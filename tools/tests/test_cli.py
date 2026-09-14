"""Behaviour tests for the atom command line entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from atom.check import CheckReport
from atom.cli import main
from atom.gates import GateResult, GateStatus


def make_go_module(tmp_path: Path) -> Path:
    (tmp_path / "go.mod").write_text("module example\n\ngo 1.23\n", encoding="utf-8")
    return tmp_path


class StubGate:
    """A gate with a fixed verdict, so CLI wiring is tested without running Go."""

    def __init__(self, name: str, status: GateStatus) -> None:
        self.name = name
        self.status = status
        self.required = True

    def evaluate(self, runner, directory: Path) -> GateResult:
        return GateResult(self.name, self.status, f"{self.name} stub", "stub details", True, 0.1)


@pytest.fixture
def passing_gates(monkeypatch):
    monkeypatch.setattr("atom.cli.default_gates", lambda enable_race=True: [StubGate("build", GateStatus.PASSED)])


@pytest.fixture
def failing_gates(monkeypatch):
    monkeypatch.setattr("atom.cli.default_gates", lambda enable_race=True: [StubGate("build", GateStatus.FAILED)])


def test_check_returns_zero_when_every_gate_passes(tmp_path, capsys, passing_gates):
    """B21: A green tree exits 0 so the command works directly in a gate."""
    exit_code = main(["check", str(make_go_module(tmp_path))])

    assert exit_code == 0


def test_check_returns_one_when_a_gate_fails(tmp_path, capsys, failing_gates):
    """B21: A failing check must be detectable by exit code alone."""
    exit_code = main(["check", str(make_go_module(tmp_path))])

    assert exit_code == 1


def test_check_json_flag_emits_parseable_json(tmp_path, capsys, passing_gates):
    """B26/B27: --json is the contract for programmatic consumers."""
    main(["check", str(make_go_module(tmp_path)), "--json"])

    parsed = json.loads(capsys.readouterr().out)
    assert parsed["schema_version"] == 1


def test_check_reports_a_missing_directory_without_a_traceback(tmp_path, capsys):
    """A user error should read as a message, not a stack trace."""
    exit_code = main(["check", str(tmp_path / "nope")])

    assert exit_code == 2
    assert "Traceback" not in capsys.readouterr().err


def test_check_reports_a_directory_without_go_mod_clearly(tmp_path, capsys):
    """The most likely user mistake is running from the wrong directory."""
    exit_code = main(["check", str(tmp_path)])

    assert exit_code == 2
    assert "go.mod" in capsys.readouterr().err


def test_check_defaults_to_the_current_directory(tmp_path, monkeypatch, passing_gates):
    """Running `atom check` with no path is the common interactive case."""
    monkeypatch.chdir(make_go_module(tmp_path))

    assert main(["check"]) == 0


def test_no_race_flag_disables_the_race_gate(tmp_path, monkeypatch):
    """The race detector needs cgo, so it must be possible to turn it off."""
    recorded: dict[str, bool] = {}

    def record_gates(enable_race: bool = True):
        recorded["enable_race"] = enable_race
        return [StubGate("build", GateStatus.PASSED)]

    monkeypatch.setattr("atom.cli.default_gates", record_gates)
    main(["check", str(make_go_module(tmp_path)), "--no-race"])

    assert recorded["enable_race"] is False


# --------------------------------------------------------------------------
# B70 -- the module must actually run, not merely import
#
# Every test above imports `atom.cli`, which defines every name in the module
# regardless of ordering. Running it as `python -m atom.cli` does not: module
# execution stops at `raise SystemExit(main())`, so anything defined below
# that line is missing when main() needs it.
#
# This is the third time in this project that a fully green suite has sat on
# top of a program that could not run -- Phase 1's unbuildable pyproject.toml,
# then a NameError reachable only via `-m`. Importing is not running, and only
# a subprocess can tell the difference.
# --------------------------------------------------------------------------

import subprocess
import sys


def _run_cli(*arguments: str) -> subprocess.CompletedProcess:
    """Invoke the CLI the way a developer does, in a real process."""
    return subprocess.run(
        [sys.executable, "-m", "atom.cli", *arguments],
        capture_output=True,
        text=True,
    )


def test_the_cli_runs_as_a_module_without_exploding():
    """B70: catches names defined after the __main__ guard, which imports hide."""
    completed = _run_cli("--help")

    assert "Traceback" not in completed.stderr
    assert completed.returncode == 0


def test_every_subcommand_is_reachable_in_a_real_process():
    """B70: --help per subcommand executes the parser wiring for each one."""
    for subcommand in (["check", "--help"], ["poc", "--help"], ["poc", "new", "--help"], ["poc", "run", "--help"]):
        completed = _run_cli(*subcommand)

        assert "Traceback" not in completed.stderr, subcommand
        assert completed.returncode == 0, subcommand
