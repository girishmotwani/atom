---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-01"
status: "executed-inconclusive"
---

# Proposed Bounded Windows Timeout Trace

## Question

For one instrumented replay of the recorded slow-test command with unchanged
runner behavior, does the trace show the cleanup grace consumed by exit waits
before pipe draining and an error-5 fallback after job termination?

## Why This Probe

The [read-only diagnosis](windows-timeout-diagnosis.md) identifies the relevant
branches but cannot observe native state during the failed run. This is a
diagnostic experiment, not the nine-case POC repeated or production design.
We must not suppress genuine termination or output errors.

## Proposed Scope And Limits

One replay of the same selected Go 1.26.9 command and frozen standard-library
fixture from the preserved revised trial. Keep its two-second command timeout,
the production two-second cleanup grace and copied child-only controls.
Verify source/executable identities without installation or replacement.

Use a session-only diagnostic driver with in-process observational wrappers
around existing native methods. Record timing, results and errors for job
termination/accounting, member/primary waits, fallback termination and pipe
reads. Native calls and exceptions retain their original behavior.

No more than one Go command; no warm-up or automatic retry; 30-second overall
diagnostic ceiling including any bounded fixture rescue. Zero models,
downloads, installations, production edits, full POC reruns or publication.
These are proposed bounds awaiting approval.

Retain identities only for this private job's primary/members. Rescue, if
needed, operates only on those retained identities and is logged separately;
it never counts as runner cleanup. Do not kill by executable name, infer
ownership from an arbitrary parent PID, or touch unrelated processes.

## Interpretation

| Observation | Meaning |
|---|---|
| Failure reproduces and native trace demonstrates the suspected ordering/state | Evidence to choose a narrowly justified repair; not itself a fix |
| Failure reproduces but native trace shows a different sequence | Reject the ordering hypothesis and follow actual evidence |
| Failure does not reproduce, trace is incomplete, native precondition changes or limit is reached | Inconclusive; no retry or invented explanation |

Do not treat tracing overhead as production behavior or claim reproduction
frequency from one probe. Preserve the failed POC, this trace and any fixture
rescue as distinct records.

## Gate

Current approval covers read-only diagnosis only. Explicit approval of this
one diagnostic replay is required before execution; it does not authorize a
production patch, broad testing, another POC batch or shipping.


## Approval And Result

The developer explicitly approved the single instrumented replay, then said
"lets go". The [trace report](windows-timeout-trace-report.md) records its
Inconclusive verdict: timeout reproduced but the cleanup failure did not.
The original command and cleanup limits were not changed. No retry or repair
was performed.
