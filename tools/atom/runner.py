"""Execute external commands for Atom checks."""

from __future__ import annotations

import enum
import os
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
        stdin_text: str | None = None,
    ) -> CommandResult:
        """Run a command in a directory without exposing subprocess exceptions."""


class SubprocessRunner:
    """Runs real subprocesses while turning expected process failures into data."""

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
        stdin_text: str | None = None,
    ) -> CommandResult:
        """Execute command with separate stdout/stderr capture and no check=True raises.

        `stdin_text` exists because argv is not a safe place for large input on
        Windows: the shim layer truncates near 8,000 characters and the process
        creation call itself refuses past roughly 60,000, both without saying so.
        A pipe has no such ceiling.

        Children never inherit this process's stdin. A tool that reads stdin when
        it is not a terminal will block until EOF, and when Atom itself runs from
        a pipe or a CI job that EOF may never arrive -- the command then times out
        after producing correct output, which reads as an unreliable model rather
        than as a plumbing mistake. Passing empty input closes the pipe at once.
        A child that genuinely wants input therefore sees end-of-input rather
        than the developer's terminal, which is the right default for a
        non-interactive tool: immediate EOF is recoverable, an inherited
        never-closing pipe is not.

        Output is decoded as UTF-8 with replacement rather than in the local code
        page. Every tool Atom drives emits UTF-8, and a decode error here would
        destroy an entire review over one stray byte; replacement keeps the rest
        readable and confines the damage to the byte that caused it.
        """

        started_at = time.perf_counter()
        command_tuple = tuple(command)
        try:
            completed_process = subprocess.run(
                _resolve_for_launch(command_tuple),
                cwd=working_directory,
                input=stdin_text if stdin_text is not None else "",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
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


def _resolve_for_launch(command: tuple[str, ...]) -> list[str]:
    """Replace the program name with the path the developer's shell would pick.

    Windows CreateProcess searches PATH for the literal name and for `name.exe`
    only -- it ignores PATHEXT. Every shell honours PATHEXT, so a tool installed
    as `copilot.cmd` (the shape npm uses for all its shims) runs fine when typed
    and is invisible to subprocess.run. shutil.which applies the shell's rules,
    so resolving through it first makes Atom agree with the terminal.

    Resolution failures are left alone deliberately: passing the original name
    through lets the launch fail where the failure can be diagnosed properly.
    """

    if not command:
        return []

    resolved_program = shutil.which(command[0])
    if resolved_program is None:
        return list(command)
    return [resolved_program, *command[1:]]


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
    # stub left behind by an uninstalled package.
    problem = (
        f"Found '{tool_name}' at {resolved_path} but the system could not start it. "
        "The entry on PATH is present but not launchable."
    )

    # A dead entry earlier on PATH hides a working install behind it, so
    # reinstalling the tool does not help -- the new copy is never reached.
    # Naming the shadowed copy turns an unexplained failure into a PATH edit.
    shadowed_copies = _path_matches_after_first(tool_name)
    if shadowed_copies:
        return (
            f"{problem} A second copy is installed at {shadowed_copies[0]} but is "
            "shadowed by the entry above. Remove the broken entry from PATH, or "
            "move the working one in front of it."
        )

    return f"{problem} This usually means a broken or stale install. Reinstall the tool."


def _path_matches_after_first(tool_name: str) -> list[str]:
    """List every other place on PATH where this tool name also resolves."""

    matches: list[str] = []
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        found = shutil.which(tool_name, path=directory)
        if found is not None:
            matches.append(found)
    return matches[1:]


def _normalise_stream(stream: bytes | str | None) -> str:
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode(errors="replace")
    return stream
