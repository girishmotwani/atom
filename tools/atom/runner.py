"""Execute external commands for Atom checks."""

from __future__ import annotations

import enum
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


class CommandOutcome(enum.Enum):
    """Explains whether a command ran, timed out, or could not be started."""

    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    TOOL_MISSING = "tool_missing"


@dataclass(frozen=True)
class CommandResult:
    """Preserves complete command evidence so gates can make transparent decisions."""

    command: tuple[str, ...]
    working_directory: Path
    outcome: CommandOutcome
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def succeeded(self) -> bool:
        """Return true only for commands that completed with a zero exit code."""

        return self.outcome is CommandOutcome.COMPLETED and self.exit_code == 0

    @property
    def combined_output(self) -> str:
        """Return stdout followed by stderr without discarding either stream."""

        if self.stdout and self.stderr:
            separator = "" if self.stdout.endswith("\n") else "\n"
            return f"{self.stdout}{separator}{self.stderr}"

        return self.stdout or self.stderr


class CommandRunner(Protocol):
    """Lets tests replace process execution with a deterministic collaborator."""

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
    ) -> CommandResult:
        """Run a command in a directory without exposing subprocess exceptions."""


class SubprocessRunner:
    """Runs real subprocesses while turning expected process failures into data."""

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
    ) -> CommandResult:
        """Execute command with separate stdout/stderr capture and no check=True raises."""

        started_at = time.perf_counter()
        command_tuple = tuple(command)
        try:
            completed_process = subprocess.run(
                list(command_tuple),
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            duration_seconds = time.perf_counter() - started_at
            return CommandResult(
                command=command_tuple,
                working_directory=working_directory,
                outcome=CommandOutcome.COMPLETED,
                exit_code=completed_process.returncode,
                stdout=completed_process.stdout,
                stderr=completed_process.stderr,
                duration_seconds=duration_seconds,
            )
        except subprocess.TimeoutExpired as error:
            duration_seconds = time.perf_counter() - started_at
            stdout = _normalise_stream(error.stdout)
            stderr = _normalise_stream(error.stderr)
            timeout_message = f"Command timed out after {timeout_seconds:g} seconds."
            stderr = f"{stderr}\n{timeout_message}" if stderr else timeout_message
            return CommandResult(command_tuple, working_directory, CommandOutcome.TIMED_OUT, None, stdout, stderr, duration_seconds)
        except (FileNotFoundError, NotADirectoryError):
            # Windows raises NotADirectoryError (WinError 267) for a bad working
            # directory and FileNotFoundError for a bad executable. Both mean the
            # process never started, and both must become data rather than a crash.
            duration_seconds = time.perf_counter() - started_at
            return CommandResult(
                command_tuple,
                working_directory,
                CommandOutcome.TOOL_MISSING,
                None,
                "",
                _diagnose_missing_file(command_tuple, working_directory),
                duration_seconds,
            )


def _diagnose_missing_file(command: tuple[str, ...], working_directory: Path) -> str:
    """Explain which of the three causes of FileNotFoundError actually applies.

    The operating system raises the same exception when the tool is absent, when
    the tool is present on PATH but cannot be launched, and when the working
    directory does not exist. Reporting all three as "not on PATH" sends the
    developer hunting through their PATH for a problem that is not there.
    """

    if not working_directory.is_dir():
        return f"Working directory does not exist: {working_directory}"

    tool_name = command[0] if command else "<empty command>"
    resolved_path = shutil.which(tool_name)
    if resolved_path is None:
        return f"Executable not found on PATH: {tool_name}"

    # PATH resolved the name, yet the operating system refused to start it. On
    # Windows this is the signature of a stale App Execution Alias: a zero-byte
    # stub left behind by an uninstalled package. Reinstalling the tool is the
    # fix, so say that rather than blaming PATH.
    return (
        f"Found '{tool_name}' at {resolved_path} but the system could not start it. "
        "The entry on PATH is present but not launchable, which usually means a "
        "broken or stale install. Reinstall the tool."
    )


def _normalise_stream(stream: bytes | str | None) -> str:
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode(errors="replace")
    return stream
