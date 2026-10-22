# Design spec: owned Windows command lifetimes

Publication-safe extract of the design approved on 2026-10-21. The public API and all 17 numbered behavior contracts below are unchanged. Unrelated project investigation context is deliberately excluded; this extract does not claim that any broader project has been proved or completed.

## Purpose

Reclaim owned Windows descendants even after their launched parent exits. Returning to a caller must not be confused with verified cleanup or usable tool evidence. The Python tooling runner changes; the Go workflow does not.

## Evidence and limits

The [synthetic POC](poc-report.md) confirmed suspended assignment, last-job-close cleanup, output recovery, directory release and outside-control survival in three trials on Windows/Python 3.13.14. It did not establish production integration, all supported platforms, arbitrary nested-job policies or a hard real-time bound. Retaining the job for termination/accounting plus retained member-identity waits is an implementation refinement, not a POC result. Local regression evidence demonstrated that zero active count alone can precede process-handle signaling. Supported-platform CI remains separate.

The developer selected stopping remaining owned children on every Windows return, including success. This is product intent, not experimental evidence.

## Design Overview

Keep SubprocessRunner as the sole public execution entry. POSIX retains its current Popen/session path. On Windows, a private native process owner establishes job membership before any command instruction executes, captures streams, and finalizes ownership on every exit. No new runtime dependency, public configuration flag or alternative user-facing runner is introduced.

```text
CommandRunner.run
  +-- POSIX: existing Popen + session behavior
  +-- Windows: private per-run process owner
        configure private kill-on-close job
        create parent suspended + restricted inherited stdio
        assign/verify job -> resume -> communicate to existing deadline
        stop remaining members -> verify empty/exits -> drain/stop polling I/O
        close owned handles -> return result / re-raise interrupt
```

The private owner uses documented Win32 APIs through ctypes, not a subclass of Popen overriding private launch hooks and not copied spike source. Command-line construction must preserve the existing resolved executable and batch-file behavior; shell interpretation must never be introduced for ordinary executables. A narrow internal native-call boundary allows deterministic failure injection without a second public dependency-injection API.

Retain the job through termination and verification; snapshot member identity handles before termination and wait for their signaling as well as zero active count. Kill-on-last-close remains the safety backstop, not the sole success receipt: after the handle is closed, job state can no longer be queried. This refinement rests on the explicit assumption above. Never enable breakaway flags, put Atom itself into the new job, name the job for reopening, or inherit/duplicate its handle into children.

## Public API

This is the single authoritative declaration block. Ellipses mark declarations, not production implementations. The only new public value is RUNNER_ERROR; all existing fields, defaults and call shapes remain unchanged. Existing result-combination semantics remain unchanged.

```python
class CommandOutcome(enum.Enum):
    """Lets callers distinguish tool evidence from execution-lifecycle failure."""
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    TOOL_MISSING = "tool_missing"
    RUNNER_ERROR = "runner_error"

@dataclass(frozen=True)
class CommandResult:
    """Keeps command evidence available for gates without subprocess exceptions."""
    command: tuple[str, ...]
    working_directory: Path
    outcome: CommandOutcome
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def succeeded(self) -> bool:
        """Prevents failed execution lifecycles from authorizing later work."""
        ...

    @property
    def combined_output(self) -> str:
        """Lets diagnostics retain both captured streams."""
        ...

class CommandRunner(Protocol):
    """Lets consumers substitute command execution without native handles."""
    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
        stdin_text: str | None = None,
    ) -> CommandResult:
        """Gives callers bounded command communication with explicit evidence."""
        ...

class SubprocessRunner:
    """Keeps real process lifecycle management behind the existing caller contract."""
    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
        stdin_text: str | None = None,
    ) -> CommandResult:
        """Owns Windows child lifetimes so completion cannot leave workers behind."""
        ...
```

No new exception is required for callers to branch on; CommandOutcome is the result discriminant. KeyboardInterrupt still propagates after cleanup. Programmer errors remain errors rather than broad-catch RUNNER_ERROR results. This phase does not redefine validation for malformed argv or invalid timeout values.

## Types And Responsibilities

| Type or component | Responsibility | File |
|---|---|---|
| CommandRunner | Defines consumer execution boundary | tools\atom\runner.py |
| SubprocessRunner | Translates execution evidence into public results | tools\atom\runner.py |
| CommandResult / CommandOutcome | Represent caller-visible execution evidence | tools\atom\runner.py |
| Private Windows process owner | Owns one native command lifetime | tools\atom\_windows_process.py |
| Private native-call adapter | Isolates documented Windows handle operations | tools\atom\_windows_process.py |

Private helper names and function bodies are left to TDD. Do not add a generic backend registry, public process/job type, global mutable handle state or new result fields. Import/load Windows facilities only on the Windows path so other platforms can still import Atom.

## Behaviour

Each numbered item is an independent test obligation, not a claim of current implementation.

1. Existing callers use the unchanged run signature and seven result fields. succeeded is true only for COMPLETED with exit_code 0; RUNNER_ERROR is never success. Original argv and requested working directory remain the reported inputs, even when launch resolves an executable path.
2. Windows launch creates a private non-inheritable kill-on-close job and a suspended parent, verifies assignment before resuming the primary thread, and grants children only the intended stdio handles. Neither Atom nor an independently owned control joins that job. No post-resume attachment or PID-tree discovery is an acceptable substitute.
3. If job setup, assignment or resumption fails, no uncontained command is resumed. Reclaim the suspended parent using its retained identity handle, finalize partial resources, and return RUNNER_ERROR with exit_code None and the failed native operation. Never launch again without ownership.
4. Ordinary Windows completion returns the primary process's real exit code and captured stdout/stderr only after communication completes and remaining job members have stopped. This includes zero and nonzero tool exits. A child with closed output pipes may not survive successful return.
5. A primary exit alone does not complete communication. If its child holds stdout/stderr open, keep the existing communication deadline; at expiry terminate the owned job, verify member exit, recover both streams, and return TIMED_OUT with exit_code None. Test the parent-exits-first fixture with a two-second deadline and return before five seconds, child stopped and empty directory removable BEFORE rescue.
6. A live-parent timeout likewise stops the primary and its ordinary job descendants. Preserve partial stdout and stderr, append the existing `Command timed out after {timeout_seconds:g} seconds.` diagnostic, and return TIMED_OUT with exit_code None when cleanup succeeds.
7. Every Windows exit path attempts owned cleanup, including successful communication, nonzero exit, expected lifecycle failure and KeyboardInterrupt. Verify the job's active-process count reaches zero before describing cleanup as verified, and release all process/thread/job/pipe handles. An expected cleanup failure returns within the bounded wait allowance with an explicit incomplete-cleanup diagnostic; it must not claim verified exit or released directories.
8. Windows finalization shares the existing two-second grace allowance for member-exit verification, remaining output drain and I/O cancellation/join waits; do not restart that allowance for each member or pipe. No subprocess-based termination utility or unbounded communicate/wait/join may run during cleanup. Native scheduling/API overhead is not a hard real-time guarantee. duration_seconds includes launch, communication and finalization.
9. For a timeout with failed termination, exit verification, output drain or handle finalization, retain TIMED_OUT and exit_code None, append every observed failure and state which cleanup/output evidence is incomplete. The primary reason remains timeout; a fallback last-handle close alone does not justify a claim of verified cleanup.
10. If Windows launch, communication or finalization fails outside a timeout, return RUNNER_ERROR with exit_code None. Preserve captured streams and any observed primary exit code in the appended diagnostic; never invent a tool exit or return COMPLETED/0 with a cleanup warning. Even primary exit 7 plus cleanup failure is RUNNER_ERROR, with 7 retained as diagnostic evidence.
11. Missing executable, broken resolved executable/alias and missing working directory retain TOOL_MISSING, exit_code None and the existing specific diagnostics when partial-launch cleanup succeeds. If partial-launch cleanup itself fails, RUNNER_ERROR takes precedence with both diagnostics. Expected other native failures (for example access denied) are RUNNER_ERROR, not missing-tool guesses.
12. With no stdin_text, the tool sees immediate EOF rather than Atom's stdin. Supplied text, including input larger than the Windows argv limit, is delivered through stdin, not moved into argv. Preserve inherited environment, Unicode paths/arguments, spaces/quoting and current PATHEXT/.cmd shim resolution. Verify ordinary .exe launch and a disposable .cmd shim; do not invoke a real review model to test plumbing.
13. Preserve UTF-8 replacement decoding, separate streams, existing newline handling and combined_output behavior. A successful owned cleanup must recover both fixture markers exactly once. On incomplete capture, retain collected bytes and explicitly name the incomplete stream; empty output must not silently imply that nothing was printed.
14. On KeyboardInterrupt during launch, communication or finalization, stop/finalize the owned Windows lifetime and re-raise KeyboardInterrupt. Emit an `atom:` stderr diagnostic if cleanup or capture could not be completed, retaining native details. Repeated interrupts must not bypass last-handle cleanup or turn the path into an unbounded wait.
15. Independent runs on the same SubprocessRunner do not share jobs, pipe buffers or native identities. Completing or interrupting one cannot stop the other's independently owned processes. A live outside-job control survives every measured termination.
16. Existing POSIX session/group cleanup, timeout results, stdin/decoding, interruption and launch diagnostics retain their current behavior; Windows modules are not loaded there. This phase's fully owned normal-success policy applies to Windows only. Do not silently broaden POSIX success cleanup.
17. Downstream gates mark RUNNER_ERROR as failed execution, model invocation does not accept it as a usable reply, diff capture rejects it, and POC-stage conversion cannot turn it into a Confirmed stage. Existing command-outcome serialization emits `runner_error` without adding/removing fields. Diagnostics remain visible through the existing result channels.

## Error Handling

Diagnostics append to captured tool stderr with a separating newline, never overwrite it. Native failures include operation name, numeric Windows error and system error text; do not use stale last-error values after unrelated calls. Include the observed primary exit when available and the original timeout/missing-tool reason. Expected lifecycle errors are caught narrowly at the native/I/O boundary; unexpected programming exceptions propagate after finally-owned cleanup.

| Condition | Observable result / error |
|---|---|
| Tool exits normally, including nonzero | COMPLETED, real tool exit, unmodified captured streams, only after verified finalization |
| Communication deadline expires, cleanup succeeds | TIMED_OUT, None, existing timeout message |
| Deadline expires, cleanup/capture is incomplete | TIMED_OUT, None, timeout plus `atom: Windows cleanup incomplete:` or `atom: Windows output incomplete:` and native details |
| Ownership/native/communication failure outside timeout | RUNNER_ERROR, None, `atom: Windows runner failure:` plus operation/native details |
| Cleanup failure after otherwise completed command | RUNNER_ERROR, None, `atom: Windows cleanup incomplete:` plus observed primary exit when known |
| Missing launch input with clean rollback | Existing TOOL_MISSING result and diagnostic |
| Missing launch input with incomplete rollback | RUNNER_ERROR, None, missing-input diagnostic plus cleanup failure |
| Interrupt | Re-raise KeyboardInterrupt after bounded finalization; incomplete cleanup/capture reported to sys.stderr |
| Unexpected programming exception | Propagate original exception after finalization; secondary cleanup failure reported without masking it |

A job-refusal result is not a sandbox escape detector or a request to retry with breakaway. Do not catch every Exception and return a success-shaped empty result. Do not suppress failed CloseHandle, pipe cancellation or verification calls. Best-effort last-close safety cleanup must still be attempted after a verification failure, with its own failure preserved.

## Concurrency

- Each call owns its job, process/thread identities, stdio endpoints, buffers and monotonic finalization deadline. Ownership transfers explicitly from launch to the returned private owner; partial construction has its own finally cleanup.
- The Windows owner uses nonblocking parent pipe endpoints in one coordinator, interleaving stdin/stdout/stderr without worker threads. Every native read/write completes before the next poll; shutdown stops polling and closes endpoints within the shared wait allowance. There are no reader/writer workers or pending overlapped operations to abandon.
- Do not assume closing a file object from another thread interrupts blocking I/O. Parent-only PIPE_NOWAIT polling avoids that assumption while preserving blocking child stdio. Local partial-output, large-input, early-stdin-close and repeated-resource tests exercise this choice; it was not the POC communication implementation.
- A private owner is NOT safe for concurrent lifecycle calls. One run coordinator serializes stop/finalize actions, including interruption; workers may own their individual stream buffers. No public caller receives native handles. No mutex is held across a blocking native operation.
- SubprocessRunner is safe for independent concurrent runs because it has no mutable per-instance/per-module run state. Test simultaneous owned jobs and repeated invocation for resource leaks. Windows inheritable-handle setup uses an explicit handle list and closes transient inheritance before other runs can inherit unintended handles.
- No Go goroutines or Go race command apply to this Python phase. Use real concurrent Python/process regressions plus deterministic injected native failures. Keep the existing Windows/Linux/macOS, Python 3.10/3.12 CI matrix; the POC's Python 3.13.14 result does not satisfy it.

## Extension Points

CommandRunner remains the narrow consumer-side substitution point. The private native-call adapter permits scoped test doubles for setup, termination, wait and close failures without mutating the public API. Future runner backends or cancellation APIs require their own evidence/spec; do not pre-build registries, configurable kill strategies or a background-launch service here.

## Validation and scope

See the [test map](test-spec.md). Use the existing Python/pytest suite and Windows/Linux/macOS Python 3.10/3.12 CI matrix. No Go completion gate applies to this Python-only tooling change. Native calls cannot be preempted by a Python deadline; the two-second finalization allowance bounds waits, not arbitrarily hung kernel calls. Job ownership is not a security boundary. No background-service API, configurable ownership bypass, POSIX success cleanup expansion or new dependency is introduced.

## Review repair reconciliation (2026-10-22)

The public declarations and 17 numbered behaviors are unchanged. To honor behaviors 7-10 when a member can be born during exit-identity capture, read cumulative job TotalProcesses before capture and after termination/accounting waits. A change or failed query cannot establish a complete identity receipt, so use the already-specified incomplete-cleanup failure result, not a guessed success or a second-snapshot assumption. Owned termination/finalization is still attempted. This can conservatively fail even after actual termination; the documented counter includes failed association attempts as well as terminated members. It is not a substitute for member signaling or evidence of arbitrary kernel-call boundedness.

One outer lifetime guard now covers launch, communication, completion receipt and diagnostic conversion before finalization. Main-thread SIGINT is deferred until the coordinator can clean up; communication observes the flag each pass so deferral does not wait for the command deadline. The previous handler is restored and worker-thread handlers are untouched.

Nonblocking pumping remains one bounded chunk per stream per pass for fairness, with a deadline check each pass. Only idle passes sleep. Timeout diff conversion retains stderr diagnostics, not partial diff data. These are repairs within the approved lifecycle/error contract, not a new ownership backend, public option, dependency or public throughput SLA.
