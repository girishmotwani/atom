"""End-to-end tests for `atom ship`, including the program actually starting.

This file exists because of a specific failure. Phase 5 shipped `ship.py` with
86 tests and a 595-test suite, all green, and `atom ship` crashed on its first
real invocation with a `TypeError`: the CLI called `default_gates(include_race=)`
and the parameter is `enable_race`. `atom ship --help` printed perfectly, because
argparse never reaches the command function.

Six phases have now ended the same way. The pattern is always the same: the
tests call the library function directly, and the thin wiring layer between
argparse and that function is the one place nobody looks. So the tests here
deliberately go *through* `main()` with the real `default_gates`, and the ones
at the bottom launch a real subprocess.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from atom.body import CheckSummary
from atom.cli import EXIT_CHECK_FAILED, EXIT_PASSED, main
from atom.ship import PrAction, ShipOutcome, ShipRefused

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"

PASSING_CHECK = CheckSummary(
    gate_rows=(("build", "PASSED"), ("vet", "PASSED")),
    absent_reason=None,
    passed=True,
)
FAILING_CHECK = CheckSummary(
    gate_rows=(("build", "FAILED"),),
    absent_reason=None,
    passed=False,
)


def _outcome(
    *,
    check: CheckSummary = PASSING_CHECK,
    check_overridden: bool = False,
    pr_action: PrAction = PrAction.CREATED,
    pr_url: str = "https://github.com/octocat/atom/pull/12",
) -> ShipOutcome:
    """Build a ShipOutcome with everything the CLI prints already populated."""

    return ShipOutcome(
        branch="phase-05-ship",
        base_branch="main",
        phase_directory=Path("specs/atom-cli/phase-05-ship"),
        artifacts=("design-spec.md",),
        check=check,
        check_overridden=check_overridden,
        commit_sha="abcdef1234567890",
        body_text="## Why\n\nBecause.\n",
        body_path=Path("body.md"),
        body_char_count=21,
        pushed=False,
        pr_action=pr_action,
        pr_url=pr_url,
    )


@pytest.fixture
def calls(monkeypatch):
    """Capture the keyword arguments the CLI hands to run_ship.

    Patching `run_ship` leaves everything *before* it real -- notably the
    `default_gates` call that the first real `atom ship` run died on.
    """

    recorded: dict = {}

    def fake_run_ship(runner, working_directory, **kwargs):
        recorded["runner"] = runner
        recorded["working_directory"] = working_directory
        recorded.update(kwargs)
        return recorded.get("_return") or _outcome()

    monkeypatch.setattr("atom.cli.run_ship", fake_run_ship)
    return recorded


class TestTheCommandFunctionIsReached:
    """The layer argparse tests cannot see.

    `--help` exercises the parser and stops. Everything below runs the command
    function itself, which is where the Phase 5 typo lived.
    """

    def test_ship_builds_its_gates_without_raising(self, calls):
        # The regression test for the shipped bug: default_gates is called for
        # real here, so a wrong keyword is a failure rather than a green run.
        assert main(["ship"]) == EXIT_PASSED

    def test_no_race_still_builds_gates(self, calls):
        assert main(["ship", "--no-race"]) == EXIT_PASSED

    def test_five_gates_are_passed_through(self, calls):
        main(["ship"])

        assert len(calls["gates"]) == 5

    def test_no_race_disables_only_the_race_gate(self, calls):
        main(["ship", "--no-race"])

        # Still five gates: the race gate is disabled, not removed, so the
        # report can say SKIPPED rather than silently omitting a row.
        assert len(calls["gates"]) == 5


class TestArgumentsReachRunShip:
    """Each flag must arrive under the name run_ship expects."""

    def test_base_defaults_to_main(self, calls):
        main(["ship"])

        assert calls["base_branch"] == "main"

    def test_base_is_forwarded(self, calls):
        main(["ship", "--base", "release"])

        assert calls["base_branch"] == "release"

    def test_phase_and_title_are_forwarded(self, calls):
        main(["ship", "--phase", "phase-09-x", "--title", "A title"])

        assert calls["phase"] == "phase-09-x"
        assert calls["title"] == "A title"

    def test_push_defaults_off_and_is_forwarded_when_given(self, calls):
        main(["ship"])
        assert calls["push"] is False

        main(["ship", "--push"])
        assert calls["push"] is True

    def test_allow_failing_checks_is_forwarded(self, calls):
        main(["ship", "--allow-failing-checks"])

        assert calls["allow_failing_checks"] is True


class TestRefusalsAndExitCodes:
    """B156/B147b - what the developer sees and what CI reads must agree."""

    def test_a_refusal_exits_one_and_prints_to_stderr(self, monkeypatch, capsys):
        def refuse(runner, working_directory, **kwargs):
            raise ShipRefused("the working tree is dirty")

        monkeypatch.setattr("atom.cli.run_ship", refuse)

        assert main(["ship"]) == EXIT_CHECK_FAILED

        captured = capsys.readouterr()
        assert "the working tree is dirty" in captured.err
        assert captured.out == ""

    def test_an_overridden_failing_check_exits_non_zero(self, calls, capsys):
        calls["_return"] = _outcome(check=FAILING_CHECK, check_overridden=True)

        assert main(["ship", "--allow-failing-checks"]) == EXIT_CHECK_FAILED

    def test_an_overridden_run_says_so_on_stderr(self, calls, capsys):
        calls["_return"] = _outcome(check=FAILING_CHECK, check_overridden=True)

        main(["ship", "--allow-failing-checks"])

        captured = capsys.readouterr()
        # The PR url still prints on stdout; the failure is stated on stderr.
        assert "did not pass" in captured.err
        assert "pull/12" in captured.out


class TestWhatIsPrinted:
    """Creating and updating must not read identically."""

    def test_a_created_pr_says_opened(self, calls, capsys):
        calls["_return"] = _outcome(pr_action=PrAction.CREATED)

        main(["ship"])

        assert "Opened https://github.com/octocat/atom/pull/12" in capsys.readouterr().out

    def test_an_updated_pr_says_updated(self, calls, capsys):
        calls["_return"] = _outcome(pr_action=PrAction.UPDATED)

        main(["ship"])

        assert "Updated https://github.com/octocat/atom/pull/12" in capsys.readouterr().out

    def test_the_commit_is_abbreviated_not_printed_whole(self, calls, capsys):
        main(["ship"])

        out = capsys.readouterr().out
        assert "abcdef123456" in out
        assert "abcdef1234567890" not in out


class TestTheProgramActuallyRuns:
    """Subprocess tests. Unit tests cannot tell you that a program starts."""

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "atom.cli", *args],
            cwd=TOOLS_DIR, capture_output=True, text=True, timeout=120,
        )

    def test_ship_appears_in_the_top_level_help(self):
        result = self._run("--help")

        assert result.returncode == 0
        assert "ship" in result.stdout

    def test_ship_help_runs_without_error(self):
        result = self._run("ship", "--help")

        assert result.returncode == 0
        assert "--push" in result.stdout
        assert "--allow-failing-checks" in result.stdout

    def test_ship_outside_a_phase_branch_refuses_without_a_traceback(self):
        # `tools/` is inside the repo but is not a phase directory, so this
        # reaches a real refusal. What matters is the shape of the failure:
        # a stated reason, not a stack trace.
        result = self._run("ship")

        assert result.returncode == EXIT_CHECK_FAILED
        assert "Traceback" not in result.stderr
        assert "atom ship refused" in result.stderr
