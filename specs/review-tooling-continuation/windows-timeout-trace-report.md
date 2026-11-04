---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-01"
status: "executed-inconclusive"
---

# Single Windows Timeout Trace

## Question

For one instrumented replay of the recorded slow-test command with unchanged
runner behavior, does the trace show the cleanup grace consumed by exit waits
before pipe draining and an error-5 fallback after job termination?

## Verdict: Inconclusive

The original cleanup failure did not reproduce. The unchanged runner timed out
the command, verified the retained process exit, observed EOF on both pipes and
returned without a cleanup diagnostic. There was no fallback TerminateProcess,
native error or rescue termination.

This neither proves the wait-before-drain hypothesis nor refutes an intermittent
failure. No production fix is justified by this successful cleanup observation.
Both classification POC reports remain Inconclusive.

## Approval And Execution

The developer selected "Approve the single instrumented replay", then said
"lets go". Executed exactly one command with the selected Go 1.26.9:

```text
<SELECTED_GO> test -v -count=1 -run TestWait ./...
```

Reused the preserved slow fixture, trial cache and child environment controls.
The complete child-environment SHA-256 matched the original command, not just
the listed Go controls. No compilation warm-up, retry, model call, download,
installation, test-suite run or production patch was performed.

The command timeout and production cleanup grace both remained two seconds.
The diagnostic's 30-second ceiling was not reached. The driver started its
clock after Python imports/setup; its recorded execution was
`2.214235100080259` seconds. The command's own recorded duration was
`2.0312764999689534` seconds.

## What Was Observed

- Job accounting reported one total process before and after termination.
  The snapshot contained only the retained primary identity. No descendant was
  observed; this does not establish whether earlier short-lived work occurred.
- Job termination returned successfully, active accounting reached zero, and
  the retained member wait returned true well within the cleanup grace.
- The primary's zero-duration wait also returned true. No primary fallback
  termination was attempted.
- Both pipes reached EOF during the following pump. The primary was still
  signalled at runner return; fixture rescue performed no termination.
- Stdout remained empty. The required entry marker was not captured.
  This still cannot establish entry into TestWait or its ten-second sleep.

The previous capture explicitly had incomplete output; this replay's complete
empty output must not be used to reinterpret that earlier failed capture.

## Evidence

Actual diagnostic stdout follows, with only the local trace path replaced.
The path replacement is a privacy transformation, not a byte-identical capture.

```json
{
  "outcome": "timed_out",
  "stdout": "",
  "stderr": "Command timed out after 2 seconds.",
  "duration_seconds": 2.0312764999689534,
  "events": 2063,
  "owned_identities": [
    47560
  ],
  "trace": "<SESSION_TRACE>\\events.jsonl"
}
```

Lifecycle events copied verbatim from the retained JSONL trace. Repetitive
pre-timeout polling events are omitted here, not deleted from raw evidence.
Handle values and process identity are local to this one execution.

```jsonl
{"event": "identity_retained", "pid": 47560, "rescue_handle": 1232, "runner_handle": 1224, "seconds": 0.1766164000146091}
{"event": "finalize_started", "grace_seconds": 2.0, "parents": {"stderr": 1108, "stdout": 1072}, "primary": 1224, "seconds": 2.181149800075218}
{"arguments": [1052], "began": 2.1811821000883356, "event": "native_return", "operation": "total_processes", "result": 1, "seconds": 2.181286000064574}
{"arguments": [1052], "began": 2.1813192000845447, "event": "native_return", "operation": "member_handles", "result": [1040], "seconds": 2.181732900091447}
{"arguments": [1052], "began": 2.1817478000884876, "event": "native_return", "operation": "terminate_job", "result": null, "seconds": 2.1825899000978097}
{"arguments": [1052], "began": 2.182607700000517, "event": "native_return", "operation": "active_processes", "result": 0, "seconds": 2.182655100012198}
{"arguments": [1052], "began": 2.182662600069307, "event": "native_return", "operation": "total_processes", "result": 1, "seconds": 2.182680300087668}
{"arguments": [1040, 1998], "began": 2.1826958000892773, "event": "native_return", "operation": "wait", "result": true, "seconds": 2.1910436000907794}
{"arguments": [1224, 0], "began": 2.1910700000589713, "event": "native_return", "operation": "wait", "result": true, "seconds": 2.1910935000050813}
{"arguments": [1072], "began": 2.191107999999076, "event": "native_return", "operation": "read", "result": {"bytes": 0, "eof": true}, "seconds": 2.191159600042738}
{"arguments": [1072], "began": 2.191164500080049, "event": "native_return", "operation": "close", "result": null, "seconds": 2.191199599998072}
{"arguments": [1108], "began": 2.1912024000193924, "event": "native_return", "operation": "read", "result": {"bytes": 0, "eof": true}, "seconds": 2.191219300031662}
{"arguments": [1108], "began": 2.191221100045368, "event": "native_return", "operation": "close", "result": null, "seconds": 2.1912371000507846}
{"arguments": [1040], "began": 2.1912617000052705, "event": "native_return", "operation": "close", "result": null, "seconds": 2.191266900044866}
{"arguments": [1224], "began": 2.191269800066948, "event": "native_return", "operation": "close", "result": null, "seconds": 2.191273800097406}
{"arguments": [1052], "began": 2.191275699995458, "event": "native_return", "operation": "close", "result": null, "seconds": 2.1912913999985904}
{"event": "finalize_returned", "parents": {}, "seconds": 2.191304000094533}
{"duration_seconds": 2.0312764999689534, "event": "runner_return", "exit_code": null, "outcome": "timed_out", "seconds": 2.191386100021191, "stderr": "Command timed out after 2 seconds.", "stdout": ""}
{"event": "exit_state_at_runner_return", "identities": {"47560": true}, "seconds": 2.19140090001747}
{"ceiling": false, "event": "rescue_started", "seconds": 2.191403500037268}
{"event": "rescue_not_needed", "pid": 47560, "seconds": 2.1914101000875235}
{"event": "input_identities_unchanged", "seconds": 2.2139689000323415}
{"elapsed_seconds": 2.214235100080259, "event": "diagnostic_finished", "seconds": 2.214245600043796}
```

## Provenance And Validation

| Retained input/capture | SHA-256 |
|---|---|
| Session diagnostic driver | `c6fd7800b611ed39fb1ebe514417418cbeffac6c48d02deb42d1c460b5cf3270` |
| Selected executable | `5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620` |
| Complete child environment | `64ff622fb11a27ef0127401bb1832a467290ad7cf9a7c637f48c2a952f4c505b` |
| Original command child environment | `64ff622fb11a27ef0127401bb1832a467290ad7cf9a7c637f48c2a952f4c505b` |
| Raw event capture | `7ccb58baceccceed358fb6b8225bde8699e6516386184348c5b669908d923fb9` |
| Raw console capture | `536454881908e9c8899bf20df109e8318c9b22572eb8823f949bc8ac7a1f39b1` |

Frozen fixture identities, unchanged before/after execution:

```json
{
  "fixture.go": "e7ef43beaa2edbbfe115b861b48a44b921e904899571c1e54d8ade11f81c8393",
  "fixture_test.go": "e2637045f8a67514e53f78cb3b3820f8192d39ba7f4c220c51ff1f896d3d5928",
  "go.mod": "56072eab7af9d8c6bd9eb9b63c37ca10d6218a08b27fbf7d04274893de073b60"
}
```

The executed driver, all 2,063 events, console capture and original POC
fixtures/captures remain outside Git. The original two POC drivers are unchanged.
No claim of a fresh Go gate or Python test-suite pass is made.

## Observer Effects And Limits

The session-only driver wrapped native calls, finalization and pipe pumping
with in-memory timestamp collection; it rethrew native OSErrors unchanged.
It retained additional process handles with synchronization/query/termination
rights, checked exit state after return, and would rescue only owned retained
identities. No duplicate job handle was retained, so kill-on-last-job-handle-close
was not intentionally postponed.

Instrumentation and additional process handles can perturb timing. The trace
cannot establish uninstrumented reliability or why the earlier failure happened.
Its primary diagnostic question is unresolved. A single observation is not a
frequency measurement or benchmark.

No evidence links this result to parent macOS/Windows CI failures.

## Next Gate

Do not silently extend the deadline, remove the entry marker or replace the
package-mode command in the classification POC.

A separate [compiled-test entry probe](windows-test-entry-brief.md) would isolate
whether this runner can capture entry and cleanly time out the already compiled
Go test process, avoiding package-mode startup. That is a changed diagnostic
target requiring approval; it would not prove package-mode cleanup repaired.
