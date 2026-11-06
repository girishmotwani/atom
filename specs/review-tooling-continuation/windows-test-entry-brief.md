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

## Motivation And Changed Target

The [single package-mode trace](windows-timeout-trace-report.md) timed out
without cleanup errors but never produced the entry marker. It observed one
total job process. It did not demonstrate a sleeping Go test had been reached.

This proposed probe removes the Go build/package supervisor from the command.
That is an explicit changed diagnostic target, not a substitute result for the
classification POC or evidence that the earlier supervisor cleanup is fixed.

## One Approved Batch, If Authorized

Use the existing preserved `warm.test.exe` compiled by the original batch.
Hash the binary before/after and confirm the preserved fixture source hashes.
Run exactly one native command:

```text
<PRESERVED_TEST_BINARY> -test.v -test.count=1 -test.run=TestWait
```

Use the same working directory and original selected child environment.
Keep the production runner unchanged, with a two-second command timeout and
two-second cleanup grace. Retain the same native timing/identity observations
as the prior diagnostic, explicitly acknowledging their observer effects.

Maximum: one binary invocation, 30 seconds overall including bounded
identity-based rescue, zero Go compiler/warm-up commands, models, downloads,
installations, source edits, retries or publication.

Preserve raw evidence. Rescue only identities retained from this command's
private job; log rescue separately and never credit it as runner cleanup.
Do not retain a duplicate job handle that postpones kill-on-last-close.

## Interpretation And Stop

| Observation | Verdict for this question |
|---|---|
| Marker captured, timed_out outcome, verified exits and complete output without rescue | Confirmed only for direct compiled-test entry/cleanup |
| Marker captured but native cleanup/stream verification fails | Refuted for direct compiled-test cleanup; inspect the actual native trace |
| Marker absent, binary unavailable/changed, instrumentation invalid, or ceiling reached | Inconclusive; stop without retry |

A successful result authorizes no production repair and does not confirm the
original classification POC. Replacing that POC's command or timing model
requires a separate decision and a preserved revised driver/report.


## Result: Confirmed For This Direct-Binary Diagnostic Only

The developer approved one invocation of the preserved test binary. It printed
`slow-test-entered`, returned `timed_out` at the two-second deadline, signalled
the retained process identity, and reached EOF on both output streams. No native
error, incomplete-output diagnostic, or rescue termination occurred. The
observed runner duration including launch and cleanup was 2.963930599973537
seconds; the diagnostic finished within its 30-second ceiling.

This confirms the direct-binary entry/cleanup question only. It does not
reproduce or repair the earlier Go-supervised timeout failure, confirm the
classification POC, or authorize a production change. See the
[probe report](windows-test-entry-report.md). The revised classification batch
has a separate approval gate in
[poc-brief-compiled-timeout.md](poc-brief-compiled-timeout.md).
