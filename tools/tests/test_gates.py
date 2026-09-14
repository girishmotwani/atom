"""Behaviour tests for Go quality gates."""

from __future__ import annotations

import pytest

from atom.gates import (
    BuildGate,
    FormatGate,
    GateStatus,
    RaceGate,
    TestGate,
    VetGate,
    default_gates,
)
from atom.runner import CommandOutcome
from tests.conftest import FakeRunner, command_result


@pytest.mark.parametrize(
    ("gate", "command", "behaviour"),
    [
        pytest.param(BuildGate(), ("go", "build", "./..."), "B6", id="build"),
        pytest.param(VetGate(), ("go", "vet", "./..."), "B8", id="vet"),
    ],
)
def test_go_command_gate_passes_when_command_exits_zero(tmp_path, gate, command, behaviour):
    f"""{behaviour}: Build and vet gates pass when their Go command exits zero."""
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="ok\n")})

    result = gate.evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED
    assert result.required is True
    assert runner.calls == [(command, tmp_path, 300.0)]


def test_build_gate_fails_with_stderr_details_when_build_exits_nonzero(tmp_path):
    """B7: BuildGate failure details come from stderr because Go compile errors use stderr."""
    command = ("go", "build", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=1, stdout="stdout noise", stderr="compile failed on stderr")})

    result = BuildGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "compile failed on stderr" in result.details
    assert "stdout noise" in result.details


def test_vet_gate_fails_when_vet_exits_nonzero(tmp_path):
    """B8: VetGate fails when go vet ./... exits non-zero and keeps evidence."""
    command = ("go", "vet", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=1, stderr="vet failed")})

    result = VetGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "vet failed" in result.details


# ---------------------------------------------------------------------------
# FormatGate -- the subtlest gate in the phase.
#
# `gofmt -l .` exits 0 even when files ARE unformatted. It signals by printing
# filenames to stdout. A gate that trusted the exit code would pass a tree that
# is not formatted, so these tests pin the behaviour deliberately.
# ---------------------------------------------------------------------------


def test_format_gate_fails_on_printed_filenames_despite_zero_exit_code(tmp_path):
    """B9: gofmt exits 0 while listing unformatted files; the output is the verdict."""
    command = ("gofmt", "-l", ".")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="handler.go\nstore.go\n")})

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert result.required is True


def test_format_gate_passes_when_gofmt_prints_nothing(tmp_path):
    """B10: An empty gofmt listing means every file is already formatted."""
    command = ("gofmt", "-l", ".")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="")})

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED


def test_format_gate_names_unformatted_files_in_summary(tmp_path):
    """B11: The summary names offending files so the fix needs no second command."""
    command = ("gofmt", "-l", ".")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="handler.go\nstore.go\n")})

    result = FormatGate().evaluate(runner, tmp_path)

    assert "handler.go" in result.summary
    assert "store.go" in result.summary


def test_format_gate_ignores_blank_lines_in_gofmt_output(tmp_path):
    """B10: Trailing whitespace in gofmt output must not be read as a filename."""
    command = ("gofmt", "-l", ".")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="\n  \n")})

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED


def test_format_gate_fails_when_gofmt_itself_errors(tmp_path):
    """B9: A non-zero gofmt exit is a real failure, distinct from listing files."""
    command = ("gofmt", "-l", ".")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=2, stderr="gofmt: bad syntax")})

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "bad syntax" in result.details


# ---------------------------------------------------------------------------
# TestGate and RaceGate
# ---------------------------------------------------------------------------


def test_test_gate_passes_when_go_test_exits_zero(tmp_path):
    """B12: TestGate passes on a zero exit from go test ./...."""
    command = ("go", "test", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="ok  example/pkg 0.2s\n")})

    result = TestGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED


def test_test_gate_fails_and_preserves_raw_output(tmp_path):
    """B13/B17: Failure details are verbatim output, never a paraphrase."""
    command = ("go", "test", "./...")
    raw_output = "--- FAIL: TestThing (0.00s)\n    thing_test.go:12: want 3 got 4\nFAIL\n"
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=1, stdout=raw_output)})

    result = TestGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert raw_output in result.details


def test_test_gate_skips_when_go_reports_no_test_files(tmp_path):
    """B14: A tree with no tests is not a failure; it is not applicable."""
    command = ("go", "test", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0, stdout="?   example/pkg [no test files]\n")})

    result = TestGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.SKIPPED


def test_test_gate_failure_wins_over_no_test_files_marker(tmp_path):
    """B14/parse rule: A real non-zero exit is never softened into SKIPPED."""
    command = ("go", "test", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=1, stdout="?   example/a [no test files]\nFAIL example/b\n")})

    result = TestGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED


def test_race_gate_runs_go_test_with_race_flag(tmp_path):
    """B15: RaceGate shells out to go test -race ./...."""
    command = ("go", "test", "-race", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0)})

    result = RaceGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED
    assert runner.calls[0][0] == command


def test_race_gate_is_skipped_when_disabled(tmp_path):
    """B15: A disabled race gate reports SKIPPED and never runs a command."""
    runner = FakeRunner({})

    result = RaceGate(enabled=False).evaluate(runner, tmp_path)

    assert result.status is GateStatus.SKIPPED
    assert runner.calls == []


def test_gate_fails_and_names_tool_when_executable_missing(tmp_path):
    """B16: A missing executable fails the gate and names the tool."""
    runner = FakeRunner({})  # unscripted commands return TOOL_MISSING

    result = BuildGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "go" in result.summary


def test_default_gates_covers_all_five_signals_in_order(tmp_path):
    """Design overview: build -> vet -> fmt -> test -> race."""
    assert [gate.name for gate in default_gates()] == ["build", "vet", "fmt", "test", "race"]


def test_default_gates_can_disable_race_without_removing_it(tmp_path):
    """B15: Disabling race keeps the gate present so the report still mentions it."""
    gates = default_gates(enable_race=False)

    assert [gate.name for gate in gates] == ["build", "vet", "fmt", "test", "race"]
    assert gates[-1].evaluate(FakeRunner({}), tmp_path).status is GateStatus.SKIPPED
