"""Shared test collaborators for Atom CLI behaviour tests."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from atom.runner import CommandOutcome, CommandResult


class FakeRunner:
    """Script command outcomes so gate tests never spawn subprocesses."""

    def __init__(self, scripted_results: dict[tuple[str, ...], CommandResult] | None = None) -> None:
        self.scripted_results = scripted_results or {}
        self.calls: list[tuple[tuple[str, ...], Path, float]] = []
        # Recorded separately rather than added to `calls`, whose tuple shape is
        # asserted on exactly by existing tests. A scripted value may also be a
        # callable taking the stdin text, for commands whose answer depends on
        # what was piped in (gofmt reading source on stdin).
        self.stdin_texts: list[str | None] = []

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
        stdin_text: str | None = None,
    ) -> CommandResult:
        command_tuple = tuple(command)
        self.calls.append((command_tuple, working_directory, timeout_seconds))
        self.stdin_texts.append(stdin_text)
        if command_tuple not in self.scripted_results:
            return command_result(command_tuple, working_directory, CommandOutcome.TOOL_MISSING, None, "", f"missing: {command_tuple[0]}")
        scripted = self.scripted_results[command_tuple]
        if callable(scripted):
            return scripted(stdin_text)
        return scripted


def command_result(
    command: tuple[str, ...],
    working_directory: Path,
    outcome: CommandOutcome = CommandOutcome.COMPLETED,
    exit_code: int | None = 0,
    stdout: str = "",
    stderr: str = "",
    duration_seconds: float = 0.25,
) -> CommandResult:
    """Build concise CommandResult instances for deterministic gate tests."""

    return CommandResult(command, working_directory, outcome, exit_code, stdout, stderr, duration_seconds)


@pytest.fixture
def fake_runner_factory():
    """Create FakeRunner instances without hiding command/result setup in tests."""

    return FakeRunner

