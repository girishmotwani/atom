"""Execute external commands for Atom checks."""

from __future__ import annotations

import enum
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

# How long a timed-out command may spend handing back what it already printed,
# once its process tree has been killed. Long enough for a drain that is going to
# finish, short enough that it cannot become the unbounded wait it replaces.
_DRAIN_GRACE_SECONDS = 2.0


class CommandOutcome(enum.Enum):
    """Distinguishes tool evidence from failed execution lifecycles."""

    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    TOOL_MISSING = "tool_missing"
    RUNNER_ERROR = "runner_error"


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

        Windows runs own their descendants through a private Job Object before
        execution. Remaining owned children stop even on success; this is not a
        background-service launcher. Ownership or cleanup failures cannot become
        successful command evidence.
        """

        started_at = time.perf_counter()
        command_tuple = tuple(command)
        if os.name == "nt":
            return _run_windows(
                command_tuple, working_directory, timeout_seconds, stdin_text, started_at
            )
        try:
            process = _launch(
                _resolve_for_launch(command_tuple),
                working_directory,
            )
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

        try:
            stdout, stderr = process.communicate(
                stdin_text if stdin_text is not None else "",
                timeout=timeout_seconds,
            )
            duration_seconds = time.perf_counter() - started_at
            return CommandResult(
                command=command_tuple,
                working_directory=working_directory,
                outcome=CommandOutcome.COMPLETED,
                exit_code=process.returncode,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration_seconds,
            )
        except subprocess.TimeoutExpired:
            stdout, stderr, detail = _stop_and_collect(process)
            duration_seconds = time.perf_counter() - started_at
            timeout_message = f"Command timed out after {timeout_seconds:g} seconds."
            if detail:
                timeout_message = f"{timeout_message} ({detail})"
            stderr = f"{stderr}\n{timeout_message}" if stderr else timeout_message
            return CommandResult(
                command_tuple,
                working_directory,
                CommandOutcome.TIMED_OUT,
                None,
                stdout,
                stderr,
                duration_seconds,
            )
        except KeyboardInterrupt:
            # Ctrl-C reaches Atom but not the command: on POSIX the child was put
            # in its own session precisely so a timeout could signal the group,
            # which also takes it out of the terminal's reach. Without this the
            # prompt would come back while `go test` kept running unattended, so
            # the cleanup the new session costs is done here instead. The
            # interrupt is re-raised: the developer asked to stop, not to wait.
            detail = _kill_process_tree(process)
            if "tree" not in detail and "group" not in detail:
                # The fallback killed the direct child only, so descendants are
                # still running. There is no report to put this in -- the
                # interrupt discards the result -- and a developer who is about
                # to see their prompt return needs to know the build did not
                # stop with it. One line to stderr is the only channel left.
                print(f"atom: {detail} after interrupt", file=sys.stderr)
            raise


def _run_windows(
    command: tuple[str, ...],
    working_directory: Path,
    timeout_seconds: float,
    stdin_text: str | None,
    started_at: float,
) -> CommandResult:
    from ._windows_process import _WindowsProcess

    process = _WindowsProcess()
    outcome = CommandOutcome.COMPLETED
    diagnostic = ""
    # Keep the guard installed through receipt/diagnosis and the first cleanup
    # instruction, not only during individual native acquisitions.
    with process.defer_interrupts():
        try:
            try:
                process.start(_resolve_for_launch(command), working_directory)
                if process.interrupted:
                    raise KeyboardInterrupt
                process.communicate(
                    stdin_text if stdin_text is not None else "", timeout_seconds
                )
            except (FileNotFoundError, NotADirectoryError):
                outcome = CommandOutcome.TOOL_MISSING
                diagnostic = _diagnose_missing_file(command, working_directory)
            except subprocess.TimeoutExpired:
                outcome = CommandOutcome.TIMED_OUT
                diagnostic = f"Command timed out after {timeout_seconds:g} seconds."
            except OSError as error:
                if getattr(error, "winerror", None) == 193:
                    outcome = CommandOutcome.TOOL_MISSING
                    diagnostic = _diagnose_missing_file(command, working_directory)
                else:
                    outcome = CommandOutcome.RUNNER_ERROR
                    diagnostic = f"atom: Windows runner failure: {error}"
            primary_exit = process.returncode
        finally:
            propagating = sys.exc_info()[0] is not None
            problems = process.finalize(_DRAIN_GRACE_SECONDS)
            if propagating and problems:
                print(
                    f"atom: Windows cleanup incomplete: {'; '.join(problems)}",
                    file=sys.stderr,
                )
    if process.interrupted:
        if problems:
            print(f"atom: Windows cleanup incomplete: {'; '.join(problems)}", file=sys.stderr)
        raise KeyboardInterrupt
    if problems:
        if outcome is not CommandOutcome.TIMED_OUT:
            outcome = CommandOutcome.RUNNER_ERROR
        cleanup = f"atom: Windows cleanup incomplete: {'; '.join(problems)}"
        if primary_exit is not None:
            cleanup += f"; primary exit code {primary_exit}"
        diagnostic = f"{diagnostic}\n{cleanup}" if diagnostic else cleanup
    stderr = process.output("stderr")
    if diagnostic:
        stderr = f"{stderr}\n{diagnostic}" if stderr else diagnostic
    return CommandResult(
        command, working_directory, outcome,
        primary_exit if outcome is CommandOutcome.COMPLETED else None,
        process.output("stdout"), stderr, time.perf_counter() - started_at,
    )


def _launch(command: Sequence[str], working_directory: Path) -> subprocess.Popen:
    """Start a command with both streams captured and stdin closed immediately.

    On POSIX the child is given its own session so that a timeout can signal the
    whole group. The cost is real and deliberate: a process in its own session no
    longer receives the terminal's Ctrl-C, so an interrupted `atom check` stops
    reaching `go test` directly. That is accepted because the alternative is the
    failure this launch shape exists to prevent -- an unbounded wait on a tool
    that will not stop on its own -- and because Atom kills the group itself on
    the way out.

    This is the POSIX path. Windows uses its pre-execution Job Object owner.
    """

    platform_options: dict[str, object] = {}
    if os.name != "nt":
        platform_options["start_new_session"] = True

    return subprocess.Popen(
        list(command),
        cwd=working_directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **platform_options,
    )


def _stop_and_collect(process: subprocess.Popen) -> tuple[str, str, str]:
    """End a timed-out POSIX command without waiting forever on inherited pipes.

    Killing the process is not enough to end the wait. A pipe reaches
    end-of-file when the last handle to its write end closes, and any child the
    command started inherited that handle. `subprocess.run` drains with no
    deadline at this point, so the caller waits for the *descendants* to finish
    rather than for the timeout it asked for: measured at 65 minutes against a
    300-second limit, with the CLI's own worker processes holding the pipe.

    Killing the whole tree closes those handles, so the drain finishes at once
    and the partial output survives -- which matters, because what a stuck
    command already printed is usually the only clue to why it stuck.

    The bounded second wait is the backstop when group termination fails.
    POSIX communication reads incrementally, so TimeoutExpired carries the
    bytes already captured. Preserve them and name the incomplete drain.
    Windows has separate nonblocking I/O under its native lifetime owner.
    """

    detail = _kill_process_tree(process)
    try:
        stdout, stderr = process.communicate(timeout=_DRAIN_GRACE_SECONDS)
        return stdout or "", stderr or "", detail
    except subprocess.TimeoutExpired as expired:
        # The reader threads are left to end with the surviving processes. The
        # caller is no longer waiting on them, which is the point.
        salvaged_stdout = _normalise_stream(expired.stdout)
        salvaged_stderr = _normalise_stream(expired.stderr)
        note = f"{detail}; stopped waiting for output after {_DRAIN_GRACE_SECONDS:g}s"
        if not salvaged_stdout and not salvaged_stderr:
            note = f"{detail}; output abandoned after {_DRAIN_GRACE_SECONDS:g}s"
        return salvaged_stdout, salvaged_stderr, note


def _normalise_stream(stream: bytes | str | None) -> str:
    """Present a captured stream as text, whatever the platform handed back.

    `TimeoutExpired` carries the partial output undecoded on POSIX and not at
    all on Windows, so the three shapes -- bytes, text and nothing -- all reach
    the same caller. Decoding with replacement matches the rest of the runner:
    one bad byte must not cost the whole capture.
    """

    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", errors="replace")
    return stream


def _kill_process_tree(process: subprocess.Popen) -> str:
    """Terminate the command and every process it started, and say what happened.

    The detail is returned rather than logged because it ends up in the timeout
    message: "killed the process only" explains a truncated reply that "timed
    out" alone would not.
    """

    try:
        # The process id is used directly rather than looked up with `getpgid`,
        # because `_launch` made this child its own session leader, so the group
        # id equals the process id by construction. The lookup would add a way to
        # fail -- it raises once the direct child has been reaped -- in exchange
        # for re-deriving a number that is already known. A group outlives its
        # leader as long as any member is alive, which is exactly the case here.
        os.killpg(process.pid, signal.SIGKILL)
        return "killed the process group"
    except (ProcessLookupError, PermissionError) as error:
        process.kill()
        return f"could not signal the process group ({error}); killed the process only"


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

    if os.path.dirname(tool_name):
        return []  # An explicit path cannot be shadowed by another PATH entry.
    matches: list[str] = []
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        found = shutil.which(tool_name, path=directory)
        if found is not None:
            matches.append(found)
    return matches[1:]
