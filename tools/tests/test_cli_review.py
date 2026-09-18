"""End-to-end tests for `atom review`, including the program actually starting.

Three earlier phases shipped a green unit suite over a program that would not
run: an unbuildable package, a `NameError` at import time, and two messages
printed on top of each other. Every one of those was invisible to tests that
imported a module and called a function, because importing a module is not
running a program.

So the tests here that matter most are the ones at the bottom, which launch a
real subprocess and check what a developer would actually see.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from atom.cli import EXIT_CHECK_FAILED, EXIT_PASSED, EXIT_USAGE_ERROR, main
from atom.runner import CommandOutcome, CommandResult

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"

DIFF_TEXT = """diff --git a/store/cache.go b/store/cache.go
--- a/store/cache.go
+++ b/store/cache.go
@@ -40,0 +41,3 @@
+func Export() {}
+var x = 1
+var y = 2
"""

FINDINGS_JSON = (
    '[{"file": "store/cache.go", "line": 41, "severity": "high", '
    '"message": "Export reads without the lock."}]'
)


class ScriptedRunner:
    """A runner that answers git and the model CLI from a script.

    Deliberately keyed on what the command *is* rather than on call order, so
    a test does not silently pass when the pipeline changes the sequence of
    calls it makes.
    """

    def __init__(self, diff_text: str = DIFF_TEXT, reply: str = FINDINGS_JSON,
                 failing_models: tuple[str, ...] = (),
                 unavailable_models: tuple[str, ...] = ()):
        self.diff_text = diff_text
        self.reply = reply
        self.failing_models = failing_models
        self.unavailable_models = unavailable_models
        self.commands: list[list[str]] = []

    def run(self, command, working_directory, timeout_seconds):
        self.commands.append(list(command))

        def result(outcome, exit_code, stdout, stderr, duration):
            return CommandResult(
                command=tuple(command), working_directory=working_directory,
                outcome=outcome, exit_code=exit_code,
                stdout=stdout, stderr=stderr, duration_seconds=duration,
            )

        if command[0] == "git":
            return result(CommandOutcome.COMPLETED, 0, self.diff_text, "", 0.1)

        model = command[command.index("--model") + 1]

        if model in self.unavailable_models:
            return result(
                CommandOutcome.COMPLETED, 1, "",
                f'Error: Model "{model}" from --model flag is not available.', 0.1,
            )

        if model in self.failing_models:
            return result(CommandOutcome.TIMED_OUT, None, "", "timed out", 60.0)

        return result(CommandOutcome.COMPLETED, 0, self.reply, "", 1.0)


@pytest.fixture
def scripted(monkeypatch):
    runner = ScriptedRunner()
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)
    return runner


def review(*args: str) -> int:
    return main(["review", *args])


class TestDiffSourceSelection:
    """B104 - choosing what to review is explicit."""

    def test_no_source_is_a_usage_error(self, scripted, capsys):
        assert review() == EXIT_USAGE_ERROR
        assert "atom review" in capsys.readouterr().err

    def test_two_sources_is_a_usage_error(self, scripted, capsys):
        assert review("--working", "--staged") == EXIT_USAGE_ERROR
        assert capsys.readouterr().err

    def test_working_is_accepted(self, scripted):
        assert review("--working", "--runs", "1") == EXIT_PASSED

    def test_staged_is_accepted(self, scripted):
        assert review("--staged", "--runs", "1") == EXIT_PASSED

    def test_branch_is_accepted(self, scripted):
        assert review("--branch", "main", "--runs", "1") == EXIT_PASSED


class TestNonsensicalSettings:
    """A8 - refused, not clamped."""

    @pytest.mark.parametrize("flag,value", [("--runs", "0"), ("--concurrency", "0")])
    def test_a_setting_that_consults_nobody_is_refused(self, scripted, capsys, flag, value):
        assert review("--working", flag, value) == EXIT_USAGE_ERROR
        assert capsys.readouterr().err

    def test_a_negative_window_is_refused(self, scripted, capsys):
        assert review("--working", "--runs", "1", "--window", "-1") == EXIT_USAGE_ERROR
        assert capsys.readouterr().err


class TestExitCodes:
    """B135-B137."""

    def test_a_complete_review_exits_zero_even_with_findings(self, scripted, capsys):
        code = review("--working", "--runs", "1")
        assert code == EXIT_PASSED
        # The finding is present; it simply does not change the verdict.
        assert "Export reads without the lock." in capsys.readouterr().out

    def test_a_partial_review_exits_non_zero(self, monkeypatch, capsys):
        # P4-3: a CI job where one model fails every run would otherwise stay
        # green forever while nobody reads the banner.
        runner = ScriptedRunner(failing_models=("claude-haiku-4.5",))
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        assert "partial" in capsys.readouterr().out.lower()

    def test_no_usable_response_fails_loudly(self, monkeypatch, capsys):
        # B130. The dangerous case: an empty report reads as a clean one.
        runner = ScriptedRunner(failing_models=("gpt-5.4", "claude-haiku-4.5"))
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        code = review("--working", "--runs", "1")
        captured = capsys.readouterr()

        assert code == EXIT_CHECK_FAILED
        assert "not a clean review" in captured.err

    def test_every_model_unavailable_fails_rather_than_reporting_nothing(
        self, monkeypatch, capsys
    ):
        runner = ScriptedRunner(
            unavailable_models=("gpt-5.4", "claude-haiku-4.5")
        )
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        assert capsys.readouterr().err

    def test_a_git_failure_is_not_reported_as_a_clean_review(self, monkeypatch, capsys):
        class BrokenGit(ScriptedRunner):
            def run(self, command, working_directory, timeout_seconds):
                if command[0] == "git":
                    return CommandResult(
                        command=tuple(command), working_directory=working_directory,
                        outcome=CommandOutcome.COMPLETED, exit_code=128, stdout="",
                        stderr="fatal: not a git repository", duration_seconds=0.1,
                    )
                return super().run(command, working_directory, timeout_seconds)

        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: BrokenGit())

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        assert "atom review" in capsys.readouterr().err


class TestChannels:
    """B128 - `atom review > review.md` leaves a clean file."""

    def test_the_report_goes_to_stdout(self, scripted, capsys):
        review("--working", "--runs", "1")

        assert "# Code review" in capsys.readouterr().out

    def test_failure_detail_goes_to_stderr_only(self, monkeypatch, capsys):
        runner = ScriptedRunner(failing_models=("claude-haiku-4.5",))
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        review("--working", "--runs", "1")
        captured = capsys.readouterr()

        assert "timed out" in captured.err
        assert "timed out" not in captured.out

    def test_json_output_is_parseable(self, scripted, capsys):
        review("--working", "--runs", "1", "--json")
        payload = json.loads(capsys.readouterr().out)

        assert payload["findings"][0]["file"] == "store/cache.go"


class TestCommandsIssued:
    """What the pipeline actually asks the tools to do."""

    def test_each_model_is_asked_the_requested_number_of_times(self, scripted):
        review("--working", "--runs", "2")

        review_calls = [
            command for command in scripted.commands
            if command[0] != "git" and "-p" in command
            and "Here is the diff:" in command[command.index("-p") + 1]
        ]

        assert len(review_calls) == 4

    def test_custom_instructions_are_disabled(self, scripted):
        # Without this the CLI loads AGENTS.md from the working directory, and
        # the review silently becomes a different prompt than the one measured.
        review("--working", "--runs", "1")

        model_calls = [c for c in scripted.commands if c[0] != "git"]
        assert all("--no-custom-instructions" in c for c in model_calls)

    def test_no_vendor_specific_mcp_server_is_disabled_by_default(self, scripted):
        # A7. The spike's speed-up command named servers that existed on one
        # machine; shipping them would have put private names in an open tool.
        review("--working", "--runs", "1")

        joined = " ".join(" ".join(c) for c in scripted.commands)
        assert "azure" not in joined.lower()

    def test_the_prompt_carries_the_whole_diff_in_one_call(self, scripted):
        # P4-4. Phases keep diffs small, so chunking is unnecessary complexity
        # that would also destroy cross-hunk context.
        review("--working", "--runs", "1")

        prompts = [
            c[c.index("-p") + 1] for c in scripted.commands
            if c[0] != "git" and "-p" in c
        ]
        full = [p for p in prompts if "Here is the diff:" in p]

        assert full and all("var y = 2" in p for p in full)


class TestTheProgramActuallyRuns:
    """Subprocess tests. Unit tests cannot tell you that a program starts.

    Every assertion here would have caught a real failure shipped by an earlier
    phase, and none of them could have been caught by importing a module.
    """

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "atom.cli", *args],
            cwd=TOOLS_DIR, capture_output=True, text=True, timeout=120,
        )

    def test_the_module_can_be_executed(self):
        result = self._run("--help")

        assert result.returncode == 0
        assert "atom" in result.stdout

    def test_review_appears_in_the_top_level_help(self):
        result = self._run("--help")

        assert "review" in result.stdout

    def test_review_help_runs_without_error(self):
        result = self._run("review", "--help")

        assert result.returncode == 0
        assert "--working" in result.stdout
        assert "--json" in result.stdout

    def test_review_without_a_source_exits_two_and_explains(self):
        # The one path that needs no network and no models: it must still be a
        # clean usage error rather than a traceback.
        result = self._run("review")

        assert result.returncode == EXIT_USAGE_ERROR
        assert "Traceback" not in result.stderr
        assert result.stderr.strip()

    def test_review_with_two_sources_exits_two_and_explains(self):
        result = self._run("review", "--working", "--staged")

        assert result.returncode == EXIT_USAGE_ERROR
        assert "Traceback" not in result.stderr

    def test_a_refused_setting_does_not_produce_a_traceback(self):
        result = self._run("review", "--working", "--runs", "0")

        assert result.returncode == EXIT_USAGE_ERROR
        assert "Traceback" not in result.stderr

    def test_nothing_is_defined_below_the_main_guard(self):
        # Phase 2 shipped 169 green tests over a program that raised NameError
        # at startup, because a function had been appended below this guard.
        source = (TOOLS_DIR / "atom" / "cli.py").read_text(encoding="utf-8")
        _, _, tail = source.partition('if __name__ == "__main__":')

        assert tail.strip() == "raise SystemExit(main())"
