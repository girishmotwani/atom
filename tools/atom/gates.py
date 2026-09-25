"""Evaluate Go quality gates for Atom checks."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from atom.runner import CommandOutcome, CommandResult, CommandRunner


class GateStatus(enum.Enum):
    """Names the possible verdicts for one quality signal."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass(frozen=True)
class GateResult:
    """Carries one gate verdict together with the evidence behind it."""

    name: str
    status: GateStatus
    summary: str
    details: str
    required: bool
    duration_seconds: float


class Gate(Protocol):
    """Allows new quality checks to join run_check without changing aggregation."""

    name: str
    required: bool

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        """Evaluate this gate against a Go module directory."""


class BuildGate:
    """Confirms the Go tree compiles before other checks are trusted."""

    name = "build"
    required = True
    command = ("go", "build", "./...")

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        """Run go build ./... and preserve compiler output for failures."""

        return _evaluate_exit_code_gate(runner, directory, self.name, self.command, self.required)


class VetGate:
    """Runs Go's static analysis signal as a required quality gate."""

    name = "vet"
    required = True
    command = ("go", "vet", "./...")

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        """Run go vet ./... and return its exit-code verdict with evidence."""

        return _evaluate_exit_code_gate(runner, directory, self.name, self.command, self.required)


class FormatGate:
    """Confirms every Go file is gofmt-clean.

    This gate cannot use the exit code. `gofmt -l .` exits 0 whether or not files
    are unformatted -- it reports by printing the offending filenames to stdout.
    A gate that trusted the exit code here would pass an unformatted tree, which
    is exactly the failure this class exists to prevent.
    """

    name = "fmt"
    required = True
    command = ("gofmt", "-l", ".")

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        """Treat printed filenames, not the exit code, as the formatting verdict."""

        command_result = runner.run(self.command, directory)
        special_result = _result_for_non_completed_command(self.name, command_result, self.required)
        if special_result is not None:
            return special_result

        # A non-zero exit means gofmt itself failed (bad syntax, unreadable file),
        # which is a different problem from "these files need formatting".
        if command_result.exit_code != 0:
            return GateResult(
                self.name,
                GateStatus.FAILED,
                f"gofmt exited with code {command_result.exit_code}",
                command_result.combined_output,
                self.required,
                command_result.duration_seconds,
            )

        unformatted_files = _non_empty_lines(command_result.stdout)
        if not unformatted_files:
            return GateResult(
                self.name,
                GateStatus.PASSED,
                "gofmt -l . reported no unformatted files",
                command_result.combined_output,
                self.required,
                command_result.duration_seconds,
            )

        # Two classes of false failure are stripped out before a verdict: files
        # that belong to a nested module (not this module's code) and files whose
        # only fault is CRLF endings (not a formatting decision). Both made the
        # gate report red where nothing was wrong.
        ours = [
            path for path in unformatted_files
            if not _belongs_to_a_nested_module(path, directory)
        ]

        genuinely_unformatted: list[str] = []
        line_ending_only: list[str] = []
        for path in ours:
            if _differs_only_in_line_endings(path, directory, runner):
                line_ending_only.append(path)
            else:
                genuinely_unformatted.append(path)

        if genuinely_unformatted:
            return GateResult(
                self.name,
                GateStatus.FAILED,
                f"{len(genuinely_unformatted)} file(s) need gofmt: {', '.join(genuinely_unformatted)}",
                command_result.combined_output,
                self.required,
                command_result.duration_seconds,
            )

        if line_ending_only:
            # Passing, but never silently: the developer is told what was set
            # aside and how to stop it recurring.
            return GateResult(
                self.name,
                GateStatus.PASSED,
                (
                    f"{len(line_ending_only)} file(s) differ only in line endings, not formatting: "
                    f"{', '.join(line_ending_only)}. gofmt expects LF; set core.autocrlf=input "
                    "or commit a .gitattributes entry to stop the checkout rewriting them."
                ),
                command_result.combined_output,
                self.required,
                command_result.duration_seconds,
            )

        return GateResult(
            self.name,
            GateStatus.PASSED,
            "gofmt -l . reported no unformatted files in this module",
            command_result.combined_output,
            self.required,
            command_result.duration_seconds,
        )


class TestGate:
    """Runs the Go test suite and distinguishes 'no tests' from 'tests failed'."""

    name = "test"
    required = True
    command = ("go", "test", "./...")

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        """Run go test ./..., reporting SKIPPED only when no package has tests."""

        return _evaluate_go_test_gate(runner, directory, self.name, self.command, self.required)


class RaceGate:
    """Runs the test suite under the race detector when it is enabled.

    The race detector is separable because it needs cgo and is materially slower,
    so some environments must turn it off. A disabled gate still reports itself as
    SKIPPED rather than vanishing, so the report always shows what was not checked.
    """

    name = "race"
    required = True
    command = ("go", "test", "-race", "./...")

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        """Run the race detector, or report SKIPPED without running anything."""

        if not self.enabled:
            return GateResult(
                self.name,
                GateStatus.SKIPPED,
                "Race detector disabled for this run",
                "",
                self.required,
                0.0,
            )

        # Shares the test gate's evaluator rather than the plain exit-code one.
        # Both commands run the same suite over the same packages, so reporting
        # PASSED here while the test gate reports SKIPPED would give one tree two
        # contradictory verdicts -- and the passing one would be the lie.
        return _evaluate_go_test_gate(runner, directory, self.name, self.command, self.required)


def default_gates(enable_race: bool = True) -> list[Gate]:
    """Return the standard gate sequence: build, vet, fmt, test, race.

    Ordered cheapest-and-most-fundamental first. A tree that does not compile makes
    every later signal meaningless, so build leads.
    """

    return [BuildGate(), VetGate(), FormatGate(), TestGate(), RaceGate(enabled=enable_race)]


def _non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _reports_only_packages_without_tests(output: str) -> bool:
    """Return true when go test reported packages, and all of them lacked tests."""

    lines = _non_empty_lines(output)
    if not lines:
        return False

    return all("[no test files]" in line for line in lines)


def _evaluate_go_test_gate(
    runner: CommandRunner,
    directory: Path,
    name: str,
    command: tuple[str, ...],
    required: bool,
) -> GateResult:
    """Run a go test command, distinguishing 'no tests' from 'tests passed'.

    Shared by the test and race gates so the two cannot drift into disagreeing
    about the same tree.
    """

    command_result = runner.run(command, directory)
    special_result = _result_for_non_completed_command(name, command_result, required)
    if special_result is not None:
        return special_result

    # Exit code is ground truth. The "[no test files]" scan below is a
    # convenience layered on top, and is only consulted once we already know
    # the command succeeded -- a parse must never soften a real failure.
    if not command_result.succeeded:
        return GateResult(
            name,
            GateStatus.FAILED,
            f"{_format_command(command)} failed with exit code {command_result.exit_code}",
            command_result.combined_output,
            required,
            command_result.duration_seconds,
        )

    # stdout, not combined output. go prints per-package results to stdout and
    # progress chatter ("go: downloading ...") to stderr; scanning them merged
    # let one line of chatter make this check false, and the gate then reported
    # PASSED for a run in which no test executed. A cold module cache is the
    # normal state of CI, so that was the common case.
    if _reports_only_packages_without_tests(command_result.stdout):
        return GateResult(
            name,
            GateStatus.SKIPPED,
            "No packages contain test files",
            command_result.combined_output,
            required,
            command_result.duration_seconds,
        )

    return GateResult(
        name,
        GateStatus.PASSED,
        f"{_format_command(command)} passed",
        command_result.combined_output,
        required,
        command_result.duration_seconds,
    )


def _belongs_to_a_nested_module(relative_path: str, root: Path) -> bool:
    """Return true when a gofmt-reported path lives inside its own Go module.

    `gofmt -l .` walks the directory tree, so it crosses module boundaries that
    `go build`, `go vet` and `go test ./...` all respect. Atom's own method puts
    throwaway spikes under `poc/`, each its own module, so without this the fmt
    gate would be the one gate whose scope is the filesystem rather than the
    module under test.
    """

    parts = relative_path.replace("\\", "/").strip("/").split("/")
    # Ancestors only: the file itself cannot be a module, and the root's own
    # go.mod is what makes it the module under test rather than a nested one.
    for depth in range(1, len(parts)):
        if (root.joinpath(*parts[:depth]) / "go.mod").exists():
            return True
    return False


def _differs_only_in_line_endings(relative_path: str, root: Path, runner: CommandRunner) -> bool:
    """Return true when gofmt's only objection to a file is its CRLF endings.

    `core.autocrlf=true` is Git's default on Windows, so a checkout there holds
    CRLF even when the committed bytes are LF -- and gofmt reports every such
    file as needing formatting. Left alone that makes the gate's verdict depend
    on the checkout's line-ending policy rather than on the code, so the same
    commit fails on Windows and passes on Linux.

    The question is never "does this file contain CRLF" but "is that the *only*
    thing gofmt would change", so the file is normalised and handed back to
    gofmt on stdin: if it comes back unaltered, the endings were the whole
    complaint. Anything that cannot be determined is treated as a real
    formatting problem, because a gate must not excuse what it failed to read.
    """

    path = root / relative_path.replace("\\", "/")
    try:
        raw = path.read_bytes()
    except OSError:
        return False

    if b"\r\n" not in raw:
        return False

    try:
        normalised = raw.replace(b"\r\n", b"\n").decode("utf-8")
    except UnicodeDecodeError:
        return False

    verdict = runner.run(("gofmt",), root, stdin_text=normalised)
    if not verdict.succeeded:
        return False

    return verdict.stdout == normalised


def _evaluate_exit_code_gate(
    runner: CommandRunner,
    directory: Path,
    name: str,
    command: tuple[str, ...],
    required: bool,
) -> GateResult:
    command_result = runner.run(command, directory)
    special_result = _result_for_non_completed_command(name, command_result, required)
    if special_result is not None:
        return special_result

    if command_result.succeeded:
        return GateResult(name, GateStatus.PASSED, f"{_format_command(command)} passed", command_result.combined_output, required, command_result.duration_seconds)

    return GateResult(name, GateStatus.FAILED, f"{_format_command(command)} failed with exit code {command_result.exit_code}", command_result.combined_output, required, command_result.duration_seconds)


def _result_for_non_completed_command(name: str, command_result: CommandResult, required: bool) -> GateResult | None:
    if command_result.outcome is CommandOutcome.COMPLETED:
        return None

    if command_result.outcome is CommandOutcome.TOOL_MISSING:
        tool_name = command_result.command[0] if command_result.command else "<empty command>"
        return GateResult(name, GateStatus.FAILED, f"Required tool missing: {tool_name}", command_result.combined_output, required, command_result.duration_seconds)

    if command_result.outcome is CommandOutcome.TIMED_OUT:
        return GateResult(name, GateStatus.FAILED, "Command timed out before the gate could finish", command_result.combined_output, required, command_result.duration_seconds)

    return GateResult(name, GateStatus.FAILED, "Command did not complete", command_result.combined_output, required, command_result.duration_seconds)


def _format_command(command: tuple[str, ...]) -> str:
    return " ".join(command)
