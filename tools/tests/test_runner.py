"""Behaviour tests for command execution."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

import pytest

from atom import runner as runner_module
from atom.runner import CommandOutcome, CommandResult, SubprocessRunner


def test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent(
    tmp_path, monkeypatch,
):
    monkeypatch.setenv("ATOM_PARENT_ONLY", "must not leak")
    parent = dict(os.environ)
    environment = {"ATOM_CHILD": "selected \u03bb \U0001f680", "PYTHONIOENCODING": "utf-8"}
    original = dict(environment)
    script = (
        "import json, os, sys; "
        "print(json.dumps([os.environ.get('ATOM_CHILD'), "
        "os.environ.get('ATOM_PARENT_ONLY'), sys.stdin.read()]))"
    )

    result = SubprocessRunner().run(
        [sys.executable, "-c", script], tmp_path, timeout_seconds=5,
        stdin_text="prompt \u03bb\n", environment=environment,
    )

    assert result.succeeded, result.stderr
    assert json.loads(result.stdout) == ["selected \u03bb \U0001f680", None, "prompt \u03bb\n"]
    assert environment == original
    assert dict(os.environ) == parent


@pytest.mark.parametrize("relative_path", [False, True])
def test_executable_lookup_uses_complete_child_path_and_windows_pathext(
    tmp_path, monkeypatch, relative_path,
):
    child_bin = tmp_path / "child-bin"
    child_bin.mkdir()
    child_path = child_bin.name if relative_path else str(child_bin)
    environment = dict(os.environ)
    if os.name == "nt":
        executable = child_bin / "atom-env-tool.ENVTOOL"
        shutil.copyfile(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe", executable)
        arguments = ["/d", "/c", "echo child-path"]
        environment = {
            key: value for key, value in environment.items()
            if key.upper() not in ("PATH", "PATHEXT")
        }
        environment.update({"pAtH": child_path, "pAtHeXt": ".ENVTOOL"})
    else:
        executable = child_bin / "atom-env-tool"
        shutil.copyfile(sys.executable, executable)
        executable.chmod(0o755)
        arguments = ["-c", "print('child-path')"]
        environment["PATH"] = child_path
    monkeypatch.setenv("PATH", str(tmp_path / "parent-empty-bin"))
    monkeypatch.setenv("PATHEXT", ".EXE")
    parent = dict(os.environ)

    result = SubprocessRunner().run(
        ["atom-env-tool", *arguments], tmp_path, timeout_seconds=5,
        environment=environment,
    )

    assert result.succeeded, result.stderr
    assert result.stdout.strip() == "child-path"
    assert dict(os.environ) == parent


@pytest.mark.parametrize("empty_path", [False, True])
def test_missing_child_tool_never_falls_back_to_parent_path(
    tmp_path, monkeypatch, empty_path,
):
    parent_bin = tmp_path / "parent-bin"
    parent_bin.mkdir()
    if os.name == "nt":
        shutil.copyfile(
            Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe",
            parent_bin / "atom-parent-only.exe",
        )
        arguments = ["/d", "/c", "echo parent-tool-ran"]
    else:
        executable = parent_bin / "atom-parent-only"
        shutil.copyfile(sys.executable, executable)
        executable.chmod(0o755)
        arguments = ["-c", "print('parent-tool-ran')"]
    monkeypatch.setenv("PATH", str(parent_bin))
    monkeypatch.chdir(parent_bin)
    environment = {
        "PATH": "" if empty_path else str(tmp_path / "child-empty-bin"),
        "PATHEXT": ".EXE",
    }

    result = SubprocessRunner().run(
        ["atom-parent-only", *arguments], tmp_path, timeout_seconds=5,
        environment=environment,
    )

    assert result.outcome is CommandOutcome.TOOL_MISSING, result
    assert result.stdout == ""
    assert result.stderr == "Executable not found on PATH: atom-parent-only"


@pytest.mark.skipif(os.name != "nt", reason="Windows stale executable diagnosis")
def test_windows_child_path_diagnostic_names_shadowed_copy(tmp_path, monkeypatch):
    broken = tmp_path / "broken"
    working = tmp_path / "working"
    broken.mkdir()
    working.mkdir()
    first = broken / "atom-shadow.ENVTOOL"
    second = working / "atom-shadow.ENVTOOL"
    first.touch()
    shutil.copyfile(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe", second)
    monkeypatch.setenv("PATH", str(tmp_path / "parent-empty-bin"))
    environment = {"pAtH": os.pathsep.join(map(str, (broken, working))),
                   "pAtHeXt": ".ENVTOOL"}

    result = SubprocessRunner().run(
        ["atom-shadow"], tmp_path, timeout_seconds=5, environment=environment,
    )

    assert result.outcome is CommandOutcome.TOOL_MISSING
    assert str(first) in result.stderr
    assert str(second) in result.stderr
    assert "shadowed by the entry above" in result.stderr
    assert "Reinstall" not in result.stderr


@pytest.mark.skipif(os.name != "nt", reason="Windows PATHEXT affects name lookup only")
def test_absolute_executable_does_not_depend_on_child_pathext(tmp_path):
    result = SubprocessRunner().run(
        [sys.executable, "-c", "print('absolute')"], tmp_path, timeout_seconds=5,
        environment={"PATHEXT": ".NOTEXE", "PYTHONIOENCODING": "utf-8"},
    )

    assert result.succeeded, result.stderr
    assert result.stdout.strip() == "absolute"


def test_environment_is_copied_before_launch(tmp_path, monkeypatch):
    environment = {"ATOM_CHILD": "before", "PYTHONIOENCODING": "utf-8"}
    launch_name = "_run_windows" if os.name == "nt" else "_launch"
    original_launch = getattr(runner_module, launch_name)

    def mutate_callers_mapping(*arguments, **keywords):
        environment["ATOM_CHILD"] = "after"
        return original_launch(*arguments, **keywords)

    monkeypatch.setattr(runner_module, launch_name, mutate_callers_mapping)

    result = SubprocessRunner().run(
        [sys.executable, "-c", "import os; print(os.environ.get('ATOM_CHILD'))"],
        tmp_path, timeout_seconds=5, environment=environment,
    )

    assert result.succeeded, result.stderr
    assert result.stdout.strip() == "before"
    assert environment["ATOM_CHILD"] == "after"


def test_concurrent_child_environments_do_not_leak_into_base_calls(tmp_path, monkeypatch):
    monkeypatch.setenv("ATOM_CHILD", "parent")
    parent = dict(os.environ)
    runner = SubprocessRunner()
    barrier = threading.Barrier(3)
    script = (
        "import json, os, sys, time; time.sleep(0.1); "
        "print(json.dumps([os.environ['ATOM_CHILD'], sys.stdin.read()]))"
    )

    def run_child(value):
        options = {}
        if value is not None:
            options["environment"] = {
                **parent, "ATOM_CHILD": value, "PYTHONIOENCODING": "utf-8",
            }
        barrier.wait(timeout=5)
        return runner.run(
            [sys.executable, "-c", script], tmp_path, timeout_seconds=5, **options,
        )

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(run_child, ("left \u03bb", "right \U0001f680", None)))

    assert all(result.succeeded for result in results), results
    assert [json.loads(result.stdout) for result in results] == [
        ["left \u03bb", ""], ["right \U0001f680", ""], ["parent", ""],
    ]
    assert dict(os.environ) == parent


def test_empty_environment_does_not_inherit_parent_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("ATOM_PARENT_ONLY", "must not leak")

    result = SubprocessRunner().run(
        [sys.executable, "-c", "import os; print(repr(os.environ.get('ATOM_PARENT_ONLY')))"],
        tmp_path, timeout_seconds=5, environment={},
    )

    assert result.succeeded, result.stderr
    assert result.stdout.strip() == "None"
    assert os.environ["ATOM_PARENT_ONLY"] == "must not leak"


@pytest.mark.parametrize("error", [
    PermissionError("selected executable is not executable"),
    OSError(8, "selected executable has invalid format"),
])
def test_posix_launch_errors_are_failed_command_evidence(tmp_path, monkeypatch, error):
    from types import SimpleNamespace
    import atom.runner as runner_module

    def failed_launch(*args, **kwargs):
        raise error

    # Fault injection exercises classification, not native POSIX ownership.
    monkeypatch.setattr(runner_module, "os", SimpleNamespace(name="posix"))
    monkeypatch.setattr(runner_module, "_resolve_for_launch", lambda command, **kwargs: list(command))
    monkeypatch.setattr(runner_module, "_launch", failed_launch)
    try:
        result = SubprocessRunner().run(
            ("selected-go", "version"), tmp_path, environment={"GOTOOLCHAIN": "local"},
        )
    except OSError:
        pytest.fail("unlaunchable selected executable escaped command evidence")
    assert result.outcome is CommandOutcome.RUNNER_ERROR
    assert result.exit_code is None
    assert str(error) in result.stderr


def test_runner_error_cannot_succeed_or_change_result_shape(tmp_path):
    outcome = next(
        (value for value in CommandOutcome if value.value == "runner_error"), None
    )
    assert outcome is not None, "lifecycle failure needs a distinct non-success outcome"
    result = CommandResult(("tool",), tmp_path, outcome, None, "reply", "failed", 0.1)

    assert result.succeeded is False
    assert tuple(asdict(result)) == (
        "command", "working_directory", "outcome", "exit_code",
        "stdout", "stderr", "duration_seconds",
    )


def test_command_result_succeeded_only_for_completed_zero(tmp_path):
    """B5: CommandResult.succeeded is true only for completed zero-exit commands."""
    successful_result = CommandResult(("tool",), tmp_path, CommandOutcome.COMPLETED, 0, "", "", 0.01)
    failing_result = CommandResult(("tool",), tmp_path, CommandOutcome.COMPLETED, 1, "", "", 0.01)
    missing_result = CommandResult(("tool",), tmp_path, CommandOutcome.TOOL_MISSING, None, "", "", 0.01)

    assert successful_result.succeeded is True
    assert failing_result.succeeded is False
    assert missing_result.succeeded is False


def test_command_result_combined_output_preserves_both_streams(tmp_path):
    """B17 support: combined_output keeps stdout and stderr available to gates."""
    result = CommandResult(("tool",), tmp_path, CommandOutcome.COMPLETED, 1, "stdout text", "stderr text", 0.01)

    assert result.combined_output == "stdout text\nstderr text"


def test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately(tmp_path):
    """B1/B4: A real subprocess failure is returned as data with both streams captured."""
    runner = SubprocessRunner()

    result = runner.run(
        [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(7)",
        ],
        tmp_path,
        timeout_seconds=5.0,
    )

    assert result.outcome is CommandOutcome.COMPLETED
    assert result.exit_code == 7
    assert result.stdout.strip() == "out"
    assert result.stderr.strip() == "err"
    assert result.succeeded is False


def test_subprocess_runner_returns_timed_out_without_raising(tmp_path):
    """B2: A command exceeding timeout_seconds is killed and reported without an exception."""
    runner = SubprocessRunner()

    result = runner.run(
        [sys.executable, "-c", "import time; time.sleep(1.0)"],
        tmp_path,
        timeout_seconds=0.1,
    )

    assert result.outcome is CommandOutcome.TIMED_OUT
    assert result.exit_code is None
    assert "timed out" in result.stderr.lower()


def test_subprocess_runner_returns_tool_missing_without_raising(tmp_path):
    """B3: A missing executable is reported as TOOL_MISSING instead of raising FileNotFoundError."""
    runner = SubprocessRunner()

    result = runner.run(["definitely-not-an-atom-test-tool"], tmp_path, timeout_seconds=1.0)

    assert result.outcome is CommandOutcome.TOOL_MISSING
    assert result.exit_code is None
    assert "definitely-not-an-atom-test-tool" in result.stderr


class TestFileNotFoundErrorIsDiagnosed:
    """The same exception has three causes; each gets its own explanation.

    A real Windows install left a zero-byte App Execution Alias on PATH after
    the package behind it was removed. shutil.which() resolved it and
    subprocess.run() refused to start it, and Atom reported 'not found on PATH'
    for an executable that was demonstrably on PATH.
    """

    def test_absent_tool_is_reported_as_missing_from_path(self, tmp_path):
        """B3: When the name resolves nowhere, PATH really is the problem."""
        result = SubprocessRunner().run(["atom-no-such-tool-anywhere"], tmp_path, timeout_seconds=5.0)

        assert result.outcome is CommandOutcome.TOOL_MISSING
        assert "Executable not found on PATH: atom-no-such-tool-anywhere" == result.stderr

    def test_unlaunchable_path_entry_is_not_blamed_on_path(self, tmp_path, monkeypatch):
        """A tool that PATH resolves but the system cannot start is a broken install."""
        monkeypatch.setattr(
            "atom.runner.shutil.which",
            lambda name, path=None: (
                r"C:\WindowsApps\stale-alias.exe" if name == "stale-alias" and path is None else None
            ),
        )

        result = SubprocessRunner().run(["stale-alias"], tmp_path, timeout_seconds=5.0)

        assert result.outcome is CommandOutcome.TOOL_MISSING
        assert "not found on PATH" not in result.stderr
        assert r"C:\WindowsApps\stale-alias.exe" in result.stderr
        assert "Reinstall the tool." in result.stderr

    def test_a_working_copy_hidden_behind_the_broken_one_is_named(self, tmp_path, monkeypatch):
        """Reinstalling cannot fix shadowing, so the shadowed copy must be named.

        Installing the Copilot CLI while a dead App Execution Alias sat earlier
        on PATH produced a working binary that was never reached. Advising a
        reinstall here would send the developer round the same loop again.
        """
        # The directories are built under tmp_path rather than hard-coded as
        # "C:\...". On POSIX os.pathsep is ":", which is also the Windows
        # drive-letter separator, so a hard-coded PATH would shred into
        # ['C', '\WindowsApps', 'C', ...], match no directory, and leave the
        # diagnostic advising a reinstall -- the exact wrong answer this test
        # exists to catch. The folder names keep the original Windows story.
        broken_directory = tmp_path / "WindowsApps"
        shadowed_directory = tmp_path / "npm"
        unrelated_directory = tmp_path / "other"
        broken_first = str(broken_directory / "tool.exe")
        working_second = str(shadowed_directory / "tool.cmd")

        def fake_which(name, path=None):
            if name != "tool":
                return None
            if path is None:
                return broken_first
            return {
                str(broken_directory): broken_first,
                str(shadowed_directory): working_second,
            }.get(path)

        monkeypatch.setattr("atom.runner.shutil.which", fake_which)
        monkeypatch.setenv(
            "PATH",
            os.pathsep.join(
                str(directory)
                for directory in (broken_directory, unrelated_directory, shadowed_directory)
            ),
        )

        result = SubprocessRunner().run(["tool"], tmp_path, timeout_seconds=5.0)

        assert working_second in result.stderr
        assert "shadowed by the entry above" in result.stderr
        assert "Reinstall" not in result.stderr

    def test_missing_working_directory_is_not_blamed_on_the_tool(self, tmp_path):
        """A directory that does not exist raises the same error as a missing tool."""
        absent_directory = tmp_path / "never-created"

        result = SubprocessRunner().run([sys.executable, "-c", "pass"], absent_directory, timeout_seconds=10.0)

        assert result.outcome is CommandOutcome.TOOL_MISSING
        assert result.stderr == f"Working directory does not exist: {absent_directory}"
        assert sys.executable not in result.stderr

class TestStdinIsNeverInherited:
    """A child that reads an inherited stdin blocks until an EOF that may never come.

    Observed for real: the availability probe printed its answer and then timed
    out after 60 seconds, because the CLI reads stdin whenever stdin is not a
    terminal and Atom was itself running from a pipe.
    """

    def test_a_child_reading_stdin_sees_end_of_input_immediately(self, tmp_path):
        reads_stdin = "import sys; sys.stdout.write(repr(sys.stdin.read()))"

        result = SubprocessRunner().run(
            [sys.executable, "-c", reads_stdin], tmp_path, timeout_seconds=30.0
        )

        assert result.outcome is CommandOutcome.COMPLETED
        assert result.stdout == "''"

    def test_supplied_text_reaches_the_child(self, tmp_path):
        reads_stdin = "import sys; sys.stdout.write(sys.stdin.read().upper())"

        result = SubprocessRunner().run(
            [sys.executable, "-c", reads_stdin], tmp_path,
            timeout_seconds=30.0, stdin_text="piped prompt",
        )

        assert result.stdout == "PIPED PROMPT"


class TestTimeoutIsBoundedEvenWhenChildrenSurvive:
    """A timeout has to bound the caller's wait, not merely be reported eventually.

    The existing B2 test uses a child that dies when it is killed, which is the one
    case where the old implementation was never at risk. Measured against a child
    that spawns a longer-lived process, `atom review` waited 65 minutes on a
    300-second timeout: the child was killed on schedule, but `subprocess.run`
    then drained the pipes with no deadline, and end-of-file does not arrive while
    any surviving descendant still holds the write end.
    """

    # Comfortably longer than the timeout below, so an unbounded drain is
    # unmistakable, and short enough that a failing test does not stall the suite.
    GRANDCHILD_LIFETIME_SECONDS = 10.0

    # Spawns a process that outlives it, then sleeps. Killing the direct child
    # leaves the grandchild holding the inherited pipe -- the shape of a Node CLI
    # that has started a worker.
    SPAWNS_A_SURVIVOR = (
        "import subprocess, sys, time; "
        "print('partial', flush=True); "
        "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)']); "
        "time.sleep(600)"
    )

    @pytest.mark.parametrize("with_environment", [False, True])
    def test_run_returns_promptly_when_the_child_leaves_a_process_behind(
        self, tmp_path, with_environment,
    ):
        started = time.monotonic()
        options = {}
        script = self.SPAWNS_A_SURVIVOR
        if with_environment:
            options["environment"] = {"ATOM_CHILD": "timeout", "PYTHONIOENCODING": "utf-8"}
            script = "import os; print(os.environ.get('ATOM_CHILD'), flush=True); " + script

        result = SubprocessRunner().run(
            [sys.executable, "-c", script], tmp_path, timeout_seconds=1.0, **options,
        )

        elapsed = time.monotonic() - started
        assert result.outcome is CommandOutcome.TIMED_OUT
        if with_environment:
            assert "timeout" in result.stdout
        assert elapsed < self.GRANDCHILD_LIFETIME_SECONDS / 2, (
            f"waited {elapsed:.1f}s for a 1s timeout; the wait is bounded by the "
            "surviving process rather than by the deadline"
        )

    def test_output_written_before_the_kill_is_still_returned(self, tmp_path):
        """Bounding the wait must not cost the partial reply.

        This is the whole reason the tree is killed rather than the pipes abandoned:
        abandoning bounds the wait just as well and returns nothing, and what a
        timed-out call already managed to say is what distinguishes a model that was
        slow from one that was stuck.
        """

        result = SubprocessRunner().run(
            [sys.executable, "-c", self.SPAWNS_A_SURVIVOR], tmp_path, timeout_seconds=1.0
        )

        assert "partial" in result.stdout

    def test_the_reported_duration_matches_the_time_actually_spent(self, tmp_path):
        """A duration that outruns the deadline is the symptom the report must show."""

        started = time.monotonic()
        result = SubprocessRunner().run(
            [sys.executable, "-c", self.SPAWNS_A_SURVIVOR], tmp_path, timeout_seconds=1.0
        )
        elapsed = time.monotonic() - started

        assert result.duration_seconds == pytest.approx(elapsed, abs=0.5)


class TestTheGuaranteesSurviveWhenTheKillDoesNot:
    """The bounded drain is a backstop, and a backstop that loses the evidence is a
    second failure rather than a recovery.

    Both cases below were raised by Atom's own review gate against the first version
    of the timeout fix. Neither is reachable when the tree kill works, which is why
    the kill is disabled explicitly here: a fallback path that is never exercised is
    a fallback path that is never checked.
    """

    @pytest.mark.skipif(os.name == "nt", reason="Popen/group fault; native equivalent in test_windows_process")
    def test_an_abandoned_drain_says_so_instead_of_reporting_silence(
        self, tmp_path, monkeypatch
    ):
        """If the evidence is lost, the report must say it was lost.

        Atom's review gate flagged this path as discarding output. It does -- and it
        has to. Windows reads each pipe with a single blocking `read()` that returns
        only at end-of-file, so bytes written before the deadline are held inside
        that call and are unreachable while a surviving process keeps the pipe open.
        Recovering them would mean Atom running its own chunked readers to fix a path
        that is entered only when the kill itself failed.

        So the guarantee is narrowed rather than faked: output survives whenever the
        tree kill works, and when it does not, the loss is stated. An empty reply
        that says nothing about why is the reading a developer cannot act on -- it is
        indistinguishable from a command that genuinely printed nothing.
        """

        monkeypatch.setattr(runner_module, "_DRAIN_GRACE_SECONDS", 0.5)

        # The stub keeps the process so the test can do the cleanup it disabled.
        # Neutering the kill is the whole point of the test, but leaving the
        # survivor running would leak a background process out of every run --
        # a test that damages the machine it runs on is not a passing test.
        real_kill = runner_module._kill_process_tree
        spared: list[subprocess.Popen] = []
        monkeypatch.setattr(
            runner_module,
            "_kill_process_tree",
            lambda process: spared.append(process) or "kill disabled",
        )

        try:
            result = SubprocessRunner().run(
                [
                    sys.executable,
                    "-c",
                    TestTimeoutIsBoundedEvenWhenChildrenSurvive.SPAWNS_A_SURVIVOR,
                ],
                tmp_path,
                timeout_seconds=1.0,
            )
        finally:
            for process in spared:
                real_kill(process)

        assert result.outcome is CommandOutcome.TIMED_OUT
        assert "abandoned" in result.stderr or "stopped waiting" in result.stderr, (
            "the output was dropped without saying so; the report reads as though "
            "the command printed nothing"
        )

    @pytest.mark.skipif(os.name == "nt", reason="Popen interrupt; native equivalent in test_windows_process")
    def test_an_interrupt_takes_the_process_tree_down_with_it(self, tmp_path, monkeypatch):
        """Ctrl-C must not leave the command running unattended.

        On POSIX the child is launched into its own session, so the terminal's
        interrupt never reaches it. That makes cleanup Atom's job: without it,
        interrupting `atom check` returns the prompt while `go test` keeps running
        invisibly. The interrupt still propagates -- the caller asked to stop.
        """

        killed: list[int] = []
        monkeypatch.setattr(
            runner_module,
            "_kill_process_tree",
            lambda process: killed.append(process.pid) or "killed for the interrupt",
        )
        monkeypatch.setattr(
            subprocess.Popen, "communicate", _raise_keyboard_interrupt, raising=True
        )

        with pytest.raises(KeyboardInterrupt):
            SubprocessRunner().run([sys.executable, "-c", "pass"], tmp_path)

        assert killed, "the interrupt left the process tree running"


def _raise_keyboard_interrupt(self, input=None, timeout=None):  # noqa: A002 - matches Popen
    """Stand in for a command still running when the developer presses Ctrl-C."""

    raise KeyboardInterrupt
