"""Behaviour tests for command execution."""

from __future__ import annotations

import os
import sys

from atom.runner import CommandOutcome, CommandResult, SubprocessRunner


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
        broken_first = r"C:\WindowsApps\tool.exe"
        working_second = r"C:\npm\tool.cmd"

        def fake_which(name, path=None):
            if name != "tool":
                return None
            if path is None:
                return broken_first
            return {r"C:\WindowsApps": broken_first, r"C:\npm": working_second}.get(path)

        monkeypatch.setattr("atom.runner.shutil.which", fake_which)
        monkeypatch.setenv("PATH", os.pathsep.join([r"C:\WindowsApps", r"C:\other", r"C:\npm"]))

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
