"""Behaviour tests for check aggregation."""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.check import (
    CheckReport,
    NotAGoModuleError,
    find_poc_modules_without_go_mod,
    run_check,
)
from atom.gates import GateResult, GateStatus
from tests.conftest import FakeRunner


class RecordingGate:
    """A gate that records that it ran, so short-circuit behaviour is observable."""

    def __init__(self, name: str, status: GateStatus, required: bool = True) -> None:
        self.name = name
        self.status = status
        self.required = required
        self.evaluated = False

    def evaluate(self, runner, directory: Path) -> GateResult:
        self.evaluated = True
        return GateResult(self.name, self.status, f"{self.name} {self.status.value}", "", self.required, 0.1)


def make_go_module(tmp_path: Path) -> Path:
    """Create the minimum tree run_check accepts: a directory with a go.mod."""
    (tmp_path / "go.mod").write_text("module example\n\ngo 1.23\n", encoding="utf-8")
    return tmp_path


def test_run_check_evaluates_every_gate_even_after_a_failure(tmp_path):
    """B18: One failure never short-circuits the rest; developers want all problems at once."""
    directory = make_go_module(tmp_path)
    failing = RecordingGate("build", GateStatus.FAILED)
    later = RecordingGate("vet", GateStatus.PASSED)

    run_check(directory, [failing, later], FakeRunner({}))

    assert failing.evaluated is True
    assert later.evaluated is True, "a gate after a failure must still run"


def test_report_passes_only_when_every_required_gate_passed_or_skipped(tmp_path):
    """B19: Required gates decide the verdict; SKIPPED is not a failure."""
    directory = make_go_module(tmp_path)
    gates = [
        RecordingGate("build", GateStatus.PASSED),
        RecordingGate("test", GateStatus.SKIPPED),
    ]

    report = run_check(directory, gates, FakeRunner({}))

    assert report.passed is True


def test_report_fails_when_a_required_gate_failed(tmp_path):
    """B19: A single required failure fails the whole check."""
    directory = make_go_module(tmp_path)
    gates = [
        RecordingGate("build", GateStatus.PASSED),
        RecordingGate("vet", GateStatus.FAILED),
    ]

    report = run_check(directory, gates, FakeRunner({}))

    assert report.passed is False


def test_optional_gate_failure_does_not_fail_the_check(tmp_path):
    """B19: required=False means a failure is informational only."""
    directory = make_go_module(tmp_path)
    gates = [RecordingGate("lint", GateStatus.FAILED, required=False)]

    report = run_check(directory, gates, FakeRunner({}))

    assert report.passed is True


def test_warning_status_never_affects_the_verdict(tmp_path):
    """B20: WARNING is advisory by definition, even on a required gate."""
    directory = make_go_module(tmp_path)
    gates = [RecordingGate("fmt", GateStatus.WARNING, required=True)]

    report = run_check(directory, gates, FakeRunner({}))

    assert report.passed is True


@pytest.mark.parametrize(
    ("status", "expected_exit_code"),
    [
        pytest.param(GateStatus.PASSED, 0, id="passed"),
        pytest.param(GateStatus.FAILED, 1, id="failed"),
    ],
)
def test_exit_code_is_zero_only_when_the_check_passed(tmp_path, status, expected_exit_code):
    """B21: exit_code is 0 when passed, otherwise 1."""
    directory = make_go_module(tmp_path)

    report = run_check(directory, [RecordingGate("build", status)], FakeRunner({}))

    assert report.exit_code == expected_exit_code


def test_run_check_refuses_a_directory_that_does_not_exist(tmp_path):
    """Error handling: refuse before running any gate."""
    missing = tmp_path / "nope"

    with pytest.raises(NotADirectoryError):
        run_check(missing, [], FakeRunner({}))


def test_run_check_refuses_a_directory_without_go_mod(tmp_path):
    """Error handling: a tree with no go.mod is not a Go module."""
    with pytest.raises(NotAGoModuleError):
        run_check(tmp_path, [], FakeRunner({}))


def test_run_check_refuses_before_running_any_gate(tmp_path):
    """Error handling: validation happens first, so no command is ever issued."""
    gate = RecordingGate("build", GateStatus.PASSED)

    with pytest.raises(NotAGoModuleError):
        run_check(tmp_path, [gate], FakeRunner({}))

    assert gate.evaluated is False


# ---------------------------------------------------------------------------
# poc/ hygiene -- the spike proved go.mod is what makes isolation work, so a
# missing one is a real (if non-fatal) problem worth surfacing.
# ---------------------------------------------------------------------------


def test_finds_poc_directories_with_go_files_but_no_go_mod(tmp_path):
    """B22: A spike with .go files and no go.mod is not isolated from the parent build."""
    spike = tmp_path / "poc" / "leaky"
    spike.mkdir(parents=True)
    (spike / "main.go").write_text("package main\n", encoding="utf-8")

    offenders = find_poc_modules_without_go_mod(tmp_path)

    assert offenders == [spike]


def test_ignores_poc_directories_that_have_a_go_mod(tmp_path):
    """B22: A correctly scaffolded spike is not reported."""
    spike = tmp_path / "poc" / "tidy"
    spike.mkdir(parents=True)
    (spike / "main.go").write_text("package main\n", encoding="utf-8")
    (spike / "go.mod").write_text("module tidy\n", encoding="utf-8")

    assert find_poc_modules_without_go_mod(tmp_path) == []


def test_ignores_poc_directories_with_no_go_files(tmp_path):
    """B22: A Python-only spike needs no go.mod."""
    spike = tmp_path / "poc" / "python-only"
    spike.mkdir(parents=True)
    (spike / "spike.py").write_text("print('hi')\n", encoding="utf-8")

    assert find_poc_modules_without_go_mod(tmp_path) == []


def test_returns_empty_list_when_there_is_no_poc_directory(tmp_path):
    """B22: Absence of poc/ is the normal case for most repositories."""
    assert find_poc_modules_without_go_mod(tmp_path) == []


def test_poc_warnings_appear_in_the_report_without_failing_it(tmp_path):
    """B23: Hygiene warnings inform; they never fail the check."""
    directory = make_go_module(tmp_path)
    spike = directory / "poc" / "leaky"
    spike.mkdir(parents=True)
    (spike / "main.go").write_text("package main\n", encoding="utf-8")

    report = run_check(directory, [RecordingGate("build", GateStatus.PASSED)], FakeRunner({}))

    assert any("leaky" in warning for warning in report.warnings)
    assert report.passed is True
