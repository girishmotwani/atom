"""Aggregate individual gate verdicts into a single check result."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from atom.gates import Gate, GateResult, GateStatus
from atom.runner import CommandRunner


class NotAGoModuleError(Exception):
    """Raised when a directory exists but is not the root of a Go module."""


@dataclass(frozen=True)
class CheckReport:
    """Aggregate verdict across every gate, with the evidence that produced it."""

    directory: Path
    gate_results: tuple[GateResult, ...]
    warnings: tuple[str, ...]
    total_duration_seconds: float

    @property
    def passed(self) -> bool:
        """Return true when no required gate failed.

        SKIPPED and WARNING are both non-failures by design: a tree with no tests
        has not failed, and an advisory signal must never gate a merge.
        """

        return not any(
            result.required and result.status is GateStatus.FAILED
            for result in self.gate_results
        )

    @property
    def exit_code(self) -> int:
        """Return the process exit code this report implies."""

        return 0 if self.passed else 1


def run_check(
    directory: Path,
    gates: Sequence[Gate],
    runner: CommandRunner,
) -> CheckReport:
    """Evaluate every gate against a Go module directory and aggregate the results.

    Every gate runs, including gates after a failure. Stopping at the first failure
    would force a developer to rerun the command once per problem, which is the
    behaviour this function deliberately rejects.

    Raises:
        NotADirectoryError: the path does not exist or is not a directory.
        NotAGoModuleError: the directory has no go.mod.
    """

    _validate_go_module_directory(directory)

    started_at = time.perf_counter()
    gate_results = [gate.evaluate(runner, directory) for gate in gates]
    total_duration_seconds = time.perf_counter() - started_at

    warnings = tuple(
        f"{_relative_to(offender, directory)} has .go files but no go.mod, "
        "so it is not isolated from the parent build"
        for offender in find_poc_modules_without_go_mod(directory)
    )

    return CheckReport(
        directory=directory,
        gate_results=tuple(gate_results),
        warnings=warnings,
        total_duration_seconds=total_duration_seconds,
    )


def find_poc_modules_without_go_mod(directory: Path) -> list[Path]:
    """Return each directory under poc/ holding .go files but no go.mod.

    The module-isolation spike proved that go.mod is what keeps a throwaway spike
    out of the parent's `./...` patterns. Without one, a half-finished spike breaks
    the real build -- a confusing failure well worth naming explicitly.
    """

    poc_root = directory / "poc"
    if not poc_root.is_dir():
        return []

    offenders = [
        candidate
        for candidate in sorted(poc_root.iterdir())
        if candidate.is_dir()
        and any(candidate.rglob("*.go"))
        and not (candidate / "go.mod").exists()
    ]

    return offenders


def _validate_go_module_directory(directory: Path) -> None:
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    if not (directory / "go.mod").exists():
        raise NotAGoModuleError(f"No go.mod found in {directory}")


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)
