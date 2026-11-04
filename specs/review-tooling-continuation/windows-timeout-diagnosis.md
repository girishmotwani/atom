---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-01"
status: "read-only-diagnosis-awaiting-trace"
---

# Windows Timeout Cleanup: Read-Only Diagnosis

## Result

The failure sequence is attributable to Windows runner finalization, not Go
version selection or the review classifier. The exact reason the process
objects stayed unsignalled is not yet established. The strongest current
hypothesis is a termination/drain ordering problem under the shared deadline;
this is not a proved root cause or an approved production fix.

No compiler command was replayed, no test was rerun and no source was patched
during this diagnosis. The two POC reports remain Inconclusive.

## Observed Evidence

The revised POC's final command was selected Go 1.26.9 running:

```text
go test -v -count=1 -run TestWait ./...
```

Formatting, build, vet and test compilation had already passed. The command
returned timed_out after a requested two-second limit; captured duration,
including cleanup, was 4.038185499957763 seconds. Stdout was empty.

Actual captured stderr:

```text
Command timed out after 2 seconds.
atom: Windows cleanup incomplete: owned job member did not signal exit; [WinError 5] TerminateProcess: Access is denied.; owned primary process did not exit; output incomplete: stdout, stderr
```

The [revised report](poc-report-control-1.27.3.md) retains all native events.
A later query found no surviving process matching this trial's time window and
TestWait command; it cannot establish that the runner itself cleaned up on time.

## Source-Level Failure Path

| Location | Observed implementation and consequence |
|---|---|
| `tools/atom/runner.py:247-260` | A communicate timeout becomes TIMED_OUT, followed by finalize using the two-second drain grace |
| `tools/atom/_windows_process.py:544-545` | Finalization creates one shared deadline for termination, exit verification and pipe draining |
| `tools/atom/_windows_process.py:573-580` | Retain job-member identities, then request job termination |
| `tools/atom/_windows_process.py:597-600` | Wait for retained process objects with the entire remaining budget; no pipe pumping in this wait loop |
| `tools/atom/_windows_process.py:601-610` | If the primary is still unsignalled, call TerminateProcess and wait with whatever budget remains |
| `tools/atom/_windows_process.py:611-619` | Only then drain pipes; an exhausted deadline can immediately report incomplete output |
| `tools/atom/runner.py:270-279` | Preserve TIMED_OUT but append cleanup failures; partial captured output is not represented as complete |

This maps every diagnostic category to an explicit branch. It does not give
the missing per-operation native timestamps, process exit status or pending-I/O
state from the failed execution.

## What Windows Documents

[TerminateProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess)
is asynchronous when terminating another process. Pending I/O must complete
or cancel before that process can exit. Microsoft also documents:

> After a process has terminated, calls to TerminateProcess with open handles
> to the process fails with ERROR_ACCESS_DENIED (5) error code.

[TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject)
terminates associated processes as if TerminateProcess were called for each.

Therefore error 5 can be a repeated-termination race, not necessarily a missing
permission, antivirus restriction or need for administrator access.
None of those host explanations is proved by the captured message.

## Hypotheses And Limits

| Hypothesis | Current evidence |
|---|---|
| Exit waits consume the grace while pipe pumping is deferred; pending I/O/EOF is not serviced in time | Source ordering and exhausted-budget diagnostics support investigation; native causality unproved |
| Fallback primary termination races with an already requested/completed job termination | Call sequence and documented error-5 semantics are consistent; native state at the failing call is missing |
| Host/native exit latency exceeds the two-second grace independently of drain order | Still possible; no operation-level trace distinguishes it |
| Go's package-mode output buffering or startup delay hides the entry marker | Still possible, but incomplete captured streams prevent a conclusion; cannot explain away the cleanup failure |
| Snapshot-member handles lack termination rights | They are used for waiting, not the failing primary TerminateProcess call; changing their access mask is not justified by this capture |

Do not raise privileges, change global settings, ignore error 5, increase the
grace, delete the marker or rewrite finalization on this evidence alone.

## Existing Coverage And CI

`tools/tests/test_windows_process.py:224-249` tests a parent that exits before
the timeout while a child holds pipes. That does not establish coverage of
this Go-supervised timeout; which descendants had started was not captured.
`tools/tests/test_windows_process.py:451-470` injects cleanup failures and checks
that TIMED_OUT retains its primary reason. Neither is evidence that this native
termination/drain ordering scenario was successfully exercised.

A bounded text search of the previously retained failed CI log found no matching
cleanup/TerminateProcess/unsignalled-process diagnostics. This is not a fresh CI
assessment, proof of absence or evidence that parent CI has the same cause.
Parent macOS/Windows CI remains unresolved.

## Recommended Next Diagnostic

Approve one instrumented replay of the recorded slow-test command using
unchanged compiler, fixture, environment controls and runner behavior.
Record job termination return, job accounting, retained process identities,
wait intervals/results, primary exit status, fallback termination error and
pipe-read/drain timing. Preserve the raw trace and perform only identity-bound
rescue if the runner leaves its own processes alive.

Instrumentation must remain local to the diagnostic process and rethrow native
errors unchanged. No production patch, full POC retry or repeated probe is
authorized yet. If the failure does not reproduce or trace changes timing enough
to prevent interpretation, report that limit rather than manufacture a cause.
