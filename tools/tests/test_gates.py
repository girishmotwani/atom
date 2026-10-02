"""Behaviour tests for Go quality gates."""

from __future__ import annotations

import pytest

from atom.gates import (
    BuildGate,
    ErrcheckGate,
    FormatGate,
    GateStatus,
    GovulncheckGate,
    RaceGate,
    StaticcheckGate,
    TestGate,
    VetGate,
    advisory_gates,
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


# ---------------------------------------------------------------------------
# Defects found by the Phase 1 review gate, run late (see phase-01-check/review.md).
# Every one is the same failure wearing different clothes: the gate reported a
# verdict that was not true -- green when nothing was checked, red when nothing
# was wrong.
# ---------------------------------------------------------------------------


def _go_file(directory, relative_path, body, line_ending="\n"):
    """Write a Go source file with explicit line endings, returning its path.

    Line endings are a parameter because they are the subject of some of these
    tests: `core.autocrlf=true` is Git's default on Windows, so a checkout there
    holds CRLF even when the committed bytes are LF.
    """
    path = directory / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.replace("\n", line_ending).encode("utf-8"))
    return path


CLEAN_SOURCE = "package main\n\nfunc main() {}\n"
ROUGH_SOURCE = "package main\nfunc  main( ) {\n}\n"


def test_test_gate_skips_when_download_chatter_accompanies_no_test_files(tmp_path):
    """Measured: `go: downloading` goes to stderr while `[no test files]` goes to stdout.

    Scanning the two streams merged means one line of chatter makes the
    all-packages-lack-tests check false, and the gate reports PASSED for a run
    in which nothing was tested. A cold module cache is the normal state of CI,
    so this is the common case, not the exotic one.
    """
    command = ("go", "test", "./...")
    runner = FakeRunner({
        command: command_result(
            command, tmp_path, exit_code=0,
            stdout="?   \texample.com/m/pkg\t[no test files]\n",
            stderr="go: downloading github.com/google/uuid v1.6.0\n",
        )
    })

    result = TestGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.SKIPPED


def test_race_gate_skips_when_no_packages_have_tests(tmp_path):
    """The race gate must not claim PASSED for a tree the test gate calls SKIPPED.

    Both run the same suite over the same packages; reporting opposite verdicts
    for one tree means at least one of them is wrong. Observed in a real run:
    `SKIP test` printed directly above `PASS race`, twenty seconds spent
    proving nothing.
    """
    command = ("go", "test", "-race", "./...")
    runner = FakeRunner({
        command: command_result(
            command, tmp_path, exit_code=0,
            stdout="?   \texample.com/m/pkg\t[no test files]\n",
        )
    })

    result = RaceGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.SKIPPED


def test_race_gate_still_passes_when_tests_actually_ran(tmp_path):
    """Guard: teaching race to skip must not stop it reporting a genuine pass."""
    command = ("go", "test", "-race", "./...")
    runner = FakeRunner({
        command: command_result(
            command, tmp_path, exit_code=0, stdout="ok  \texample.com/m/pkg\t0.2s\n",
        )
    })

    assert RaceGate().evaluate(runner, tmp_path).status is GateStatus.PASSED


def test_format_gate_ignores_files_belonging_to_a_nested_module(tmp_path):
    """Measured: `gofmt -l .` crosses module boundaries; `go vet ./...` does not.

    Atom's own method puts throwaway spikes under `poc/`, each its own module.
    Left alone, the fmt gate is the one gate in the set whose scope is the
    directory tree rather than the module, so a deliberately rough spike fails
    the whole repository.
    """
    _go_file(tmp_path, "main.go", CLEAN_SOURCE)
    (tmp_path / "poc" / "spike").mkdir(parents=True)
    (tmp_path / "poc" / "spike" / "go.mod").write_text("module example.com/spike\n")
    _go_file(tmp_path, "poc/spike/rough.go", ROUGH_SOURCE)

    command = ("gofmt", "-l", ".")
    runner = FakeRunner({
        command: command_result(command, tmp_path, exit_code=0, stdout="poc/spike/rough.go\n"),
    })

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED


def test_format_gate_still_reports_unformatted_files_in_the_root_module(tmp_path):
    """Guard: excluding nested modules must not excuse ordinary subdirectories."""
    _go_file(tmp_path, "internal/thing/rough.go", ROUGH_SOURCE)

    command = ("gofmt", "-l", ".")
    runner = FakeRunner({
        command: command_result(
            command, tmp_path, exit_code=0, stdout="internal/thing/rough.go\n",
        ),
    })

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "internal/thing/rough.go" in result.summary


def test_format_gate_does_not_fail_for_line_ending_only_differences(tmp_path):
    """Measured: gofmt flags a correctly formatted file purely for CRLF endings.

    `core.autocrlf=true` is Git's default on Windows, so the identical commit
    fails on Windows and passes on Linux. A gate whose verdict depends on the
    checkout's line-ending policy is not measuring the code.
    """
    _go_file(tmp_path, "main.go", CLEAN_SOURCE, line_ending="\r\n")

    listing = ("gofmt", "-l", ".")
    runner = FakeRunner({
        listing: command_result(listing, tmp_path, exit_code=0, stdout="main.go\n"),
        # gofmt reading stdin echoes the formatted source: handed the same file
        # with its endings normalised, it has nothing to change.
        ("gofmt",): lambda piped: command_result(("gofmt",), tmp_path, exit_code=0, stdout=piped),
    })

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED


def test_format_gate_names_line_endings_as_the_cause(tmp_path):
    """Passing silently would hide it; the developer must be told what was ignored.

    "1 file(s) need gofmt: main.go" sends someone hunting for spacing errors
    that do not exist.
    """
    _go_file(tmp_path, "main.go", CLEAN_SOURCE, line_ending="\r\n")

    listing = ("gofmt", "-l", ".")
    runner = FakeRunner({
        listing: command_result(listing, tmp_path, exit_code=0, stdout="main.go\n"),
        ("gofmt",): lambda piped: command_result(("gofmt",), tmp_path, exit_code=0, stdout=piped),
    })

    summary = FormatGate().evaluate(runner, tmp_path).summary.lower()

    assert "line ending" in summary
    assert "main.go" in summary


def test_format_gate_still_fails_when_a_crlf_file_is_also_badly_formatted(tmp_path):
    """Guard against over-correction: CRLF must not become an amnesty.

    The question is never "does this file have CRLF" but "is that the *only*
    thing gofmt objects to".
    """
    _go_file(tmp_path, "main.go", ROUGH_SOURCE, line_ending="\r\n")

    listing = ("gofmt", "-l", ".")
    runner = FakeRunner({
        listing: command_result(listing, tmp_path, exit_code=0, stdout="main.go\n"),
        # Normalising the endings leaves real formatting work, so gofmt returns
        # something other than what it was given.
        ("gofmt",): lambda piped: command_result(
            ("gofmt",), tmp_path, exit_code=0, stdout=CLEAN_SOURCE,
        ),
    })

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "main.go" in result.summary


def test_format_gate_reports_a_genuine_problem_even_beside_a_line_ending_one(tmp_path):
    """A real failure is never softened by a file that only had CRLF."""
    _go_file(tmp_path, "clean.go", CLEAN_SOURCE, line_ending="\r\n")
    _go_file(tmp_path, "rough.go", ROUGH_SOURCE)

    listing = ("gofmt", "-l", ".")

    def piped_gofmt(piped):
        # Echo the input back only when it is already formatted, which is what
        # the real gofmt does; the rough file therefore comes back changed.
        formatted = CLEAN_SOURCE if piped != CLEAN_SOURCE else piped
        return command_result(("gofmt",), tmp_path, exit_code=0, stdout=formatted)

    runner = FakeRunner({
        listing: command_result(listing, tmp_path, exit_code=0, stdout="clean.go\nrough.go\n"),
        ("gofmt",): piped_gofmt,
    })

    result = FormatGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert "rough.go" in result.summary


def test_default_gates_covers_all_five_signals_in_order(tmp_path):
    """Design overview: build -> vet -> fmt -> test -> race."""
    assert [gate.name for gate in default_gates()] == ["build", "vet", "fmt", "test", "race"]


def test_default_gates_can_disable_race_without_removing_it(tmp_path):
    """B15: Disabling race keeps the gate present so the report still mentions it."""
    gates = default_gates(enable_race=False)

    assert [gate.name for gate in gates] == ["build", "vet", "fmt", "test", "race"]
    assert gates[-1].evaluate(FakeRunner({}), tmp_path).status is GateStatus.SKIPPED


@pytest.mark.parametrize(
    ("gate", "command", "tool_name"),
    [
        pytest.param(StaticcheckGate(), ("staticcheck", "./..."), "staticcheck", id="staticcheck"),
        pytest.param(ErrcheckGate(), ("errcheck", "./..."), "errcheck", id="errcheck"),
        pytest.param(GovulncheckGate(), ("govulncheck", "./..."), "govulncheck", id="govulncheck"),
    ],
)
def test_advisory_gate_skips_when_tool_is_missing(tmp_path, gate, command, tool_name):
    """Advisory tools are useful evidence, not required local dependencies."""
    runner = FakeRunner({})

    result = gate.evaluate(runner, tmp_path)

    assert result.status is GateStatus.SKIPPED
    assert result.required is False
    assert tool_name in result.summary
    assert "not installed" in result.summary
    assert runner.calls == [(command, tmp_path, 300.0)]


@pytest.mark.parametrize(
    ("gate", "command", "output"),
    [
        pytest.param(StaticcheckGate(), ("staticcheck", "./..."), "staticcheck finding", id="staticcheck"),
        pytest.param(ErrcheckGate(), ("errcheck", "./..."), "ignored error", id="errcheck"),
        pytest.param(GovulncheckGate(), ("govulncheck", "./..."), "CVE-0000", id="govulncheck"),
    ],
)
def test_advisory_gate_warns_and_preserves_output_when_tool_finds_something(
    tmp_path, gate, command, output
):
    """A finding from an advisory tool should inform review without blocking it."""
    runner = FakeRunner({
        command: command_result(command, tmp_path, exit_code=1, stdout=output),
    })

    result = gate.evaluate(runner, tmp_path)

    assert result.status is GateStatus.WARNING
    assert result.required is False
    assert output in result.details


@pytest.mark.parametrize(
    ("gate", "command"),
    [
        pytest.param(StaticcheckGate(), ("staticcheck", "./..."), id="staticcheck"),
        pytest.param(ErrcheckGate(), ("errcheck", "./..."), id="errcheck"),
        pytest.param(GovulncheckGate(), ("govulncheck", "./..."), id="govulncheck"),
    ],
)
def test_advisory_gate_passes_when_tool_exits_zero(tmp_path, gate, command):
    """A clean advisory command is mechanical evidence the review prompt can cite."""
    runner = FakeRunner({
        command: command_result(command, tmp_path, exit_code=0, stdout="clean\n"),
    })

    result = gate.evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED
    assert result.required is False


def test_advisory_gates_returns_all_optional_review_signals():
    """The review pipeline should ask for each advisory signal explicitly."""
    gates = advisory_gates()

    assert [gate.name for gate in gates] == ["staticcheck", "errcheck", "govulncheck"]
    assert [gate.required for gate in gates] == [False, False, False]
