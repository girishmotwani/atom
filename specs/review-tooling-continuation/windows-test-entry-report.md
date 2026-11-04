---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-02"
status: "executed-confirmed-bounded-diagnostic"
---

# Compiled-Test Entry Probe

## Question

Does the unchanged Windows runner capture the entry marker and verify cleanup
when the already compiled TestWait binary is invoked directly with a two-second
command deadline?

## Verdict: Confirmed For Direct Compiled-Test Entry And Cleanup Only

The preserved binary printed the entry marker, timed out, signalled exit and
closed both output streams. No native error, incomplete-output diagnostic or
rescue termination occurred. The runner implementation and two-second command/
cleanup limits were unchanged.

This confirms the narrowly scoped [entry brief](windows-test-entry-brief.md),
not the nine-case classification POC or Go-supervised timeout reliability.
The original Windows cleanup failure remains unresolved; nothing was repaired.

## Execution And Evidence

The developer selected "Approve one compiled-test entry probe", then said
"lets run". Executed one native binary command, no compilation or warm-up:

```text
<PRESERVED_TEST_BINARY> -test.v -test.count=1 -test.run=TestWait
```

The same working directory, frozen fixture sources and complete original child
environment were used. Binary, source and selected-compiler fingerprints were
unchanged before/after. The command duration, including launch and cleanup, was
`2.963930599973537` seconds; the full driver execution after imports/
setup was `5.929855199996382` seconds, below its 30-second ceiling.

Actual diagnostic stdout (local trace path replaced, otherwise unchanged):

```json
{
  "outcome": "timed_out",
  "stdout": "=== RUN   TestWait\nslow-test-entered\n",
  "stderr": "Command timed out after 2 seconds.",
  "duration_seconds": 2.963930599973537,
  "events": 2249,
  "owned_identities": [
    37364
  ],
  "trace": "<SESSION_TRACE>\\events.jsonl"
}
```

Lifecycle records copied verbatim from raw JSONL; repetitive polling is omitted
from this document, not deleted from raw evidence:

```jsonl
{"event": "identity_retained", "pid": 37364, "rescue_handle": 1164, "runner_handle": 1156, "seconds": 3.892648800043389}
{"event": "finalize_started", "grace_seconds": 2.0, "parents": {"stderr": 1064, "stdout": 1056}, "primary": 1156, "seconds": 5.89288589998614}
{"arguments": [1040], "began": 5.892898799967952, "event": "native_return", "operation": "total_processes", "result": 1, "seconds": 5.892927200067788}
{"arguments": [1040], "began": 5.892932699993253, "event": "native_return", "operation": "member_handles", "result": [1052], "seconds": 5.893140300060622}
{"arguments": [1040], "began": 5.893145699985325, "event": "native_return", "operation": "terminate_job", "result": null, "seconds": 5.89318470004946}
{"arguments": [1040], "began": 5.893187800073065, "event": "native_return", "operation": "active_processes", "result": 0, "seconds": 5.893199300044216}
{"arguments": [1040], "began": 5.893202000064775, "event": "native_return", "operation": "total_processes", "result": 1, "seconds": 5.893208599998616}
{"arguments": [1052, 1999], "began": 5.893216000054963, "event": "native_return", "operation": "wait", "result": true, "seconds": 5.9051831000251696}
{"arguments": [1156, 0], "began": 5.905205299961381, "event": "native_return", "operation": "wait", "result": true, "seconds": 5.905225199996494}
{"arguments": [1056], "began": 5.905236799968407, "event": "native_return", "operation": "read", "result": {"bytes": 0, "eof": true}, "seconds": 5.905275100027211}
{"arguments": [1056], "began": 5.9052785000531, "event": "native_return", "operation": "close", "result": null, "seconds": 5.905303200008348}
{"arguments": [1064], "began": 5.905304800020531, "event": "native_return", "operation": "read", "result": {"bytes": 0, "eof": true}, "seconds": 5.905313999974169}
{"arguments": [1064], "began": 5.905315299984068, "event": "native_return", "operation": "close", "result": null, "seconds": 5.90532650006935}
{"arguments": [1052], "began": 5.905337000032887, "event": "native_return", "operation": "close", "result": null, "seconds": 5.9053396000526845}
{"arguments": [1156], "began": 5.905346899991855, "event": "native_return", "operation": "close", "result": null, "seconds": 5.9053490000078455}
{"arguments": [1040], "began": 5.905350300017744, "event": "native_return", "operation": "close", "result": null, "seconds": 5.905359899974428}
{"event": "finalize_returned", "parents": {}, "seconds": 5.905368100036867}
{"duration_seconds": 2.963930599973537, "event": "runner_return", "exit_code": null, "outcome": "timed_out", "seconds": 5.905427400022745, "stderr": "Command timed out after 2 seconds.", "stdout": "=== RUN   TestWait\nslow-test-entered\n"}
{"event": "exit_state_at_runner_return", "identities": {"37364": true}, "seconds": 5.905436099972576}
{"ceiling": false, "event": "rescue_started", "seconds": 5.905438399990089}
{"event": "rescue_not_needed", "pid": 37364, "seconds": 5.905442200019024}
{"binary_sha256": "4f294d6cefb56d09faf4595e688a1fe3eaf461940c3d7c23151d1974048259d6", "event": "input_identities_unchanged", "seconds": 5.929642200004309}
{"elapsed_seconds": 5.929855199996382, "event": "diagnostic_finished", "seconds": 5.929861400043592}
```

The job reported one total process. Its retained member and primary waits
returned true. Both stdout/stderr reads returned EOF before finalization
returned, and the retained identity was signalled at runner return.
The separately logged rescue checked identity but performed no termination.
No primary fallback TerminateProcess was needed.

## Provenance

| Input/capture | SHA-256 |
|---|---|
| Executed entry diagnostic driver | `7759240d2704c2d774be3baf20ad200671150143e37dff82504e3d73a85b8ba6` |
| Preserved test binary, before and after | `4f294d6cefb56d09faf4595e688a1fe3eaf461940c3d7c23151d1974048259d6` |
| Selected compiler, hashed but not invoked | `5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620` |
| Full child environment, matches original command | `64ff622fb11a27ef0127401bb1832a467290ad7cf9a7c637f48c2a952f4c505b` |
| Complete raw event capture | `0816ac0e2bddc9a931a10f98dd7af3a625c9ec39ca5baec696d4e25d3e51c46f` |
| Raw console capture | `2c72969ff3b03e4ff6d118b39c3b2086e0b5a790be2d9aaeb33d146e6af60232` |

Preserved fixture source fingerprints matched the prior trace:

```json
{
  "fixture.go": "e7ef43beaa2edbbfe115b861b48a44b921e904899571c1e54d8ade11f81c8393",
  "fixture_test.go": "e2637045f8a67514e53f78cb3b3820f8192d39ba7f4c220c51ff1f896d3d5928",
  "go.mod": "56072eab7af9d8c6bd9eb9b63c37ca10d6218a08b27fbf7d04274893de073b60"
}
```

All 2,249 native observation events, executed driver, console output and
preserved binary remain outside Git. The old diagnostic and both original
classification drivers/reports remain unchanged.

## Explicitly Not Covered

- The original Go-supervised cleanup failure was not reproduced or repaired.
  Removing the compiler/package supervisor changes the diagnostic target.
- The original compile event named this preserved binary but recorded no binary
  hash. This probe proves before/after stability and source identity, not an
  independently recorded binary hash from the original compile.
- Timing logging and retained process handles can perturb behavior. This is
  one bounded functional observation, not a frequency or performance claim.
- No production source/test edit, Python suite, full Go gate, cross-platform
  validation, model call, installation, download, retry or publication occurred.
  Parent CI failures remain unresolved.

## Plan Impact And Gate

There is now executed evidence that the slow fixture can enter and produce a
verifiable timeout via its compiled binary. A separately
[revised classification brief](poc-brief-compiled-timeout.md) proposes using
that narrowly defined signal for the slow case, keeping the original failures
and Go-supervised cleanup finding visible.

That change requires explicit approval before a new classification batch.
It would not silently replace the failed experiment or prove the general
runner issue fixed. No Phase 02 production design is authorized yet.
