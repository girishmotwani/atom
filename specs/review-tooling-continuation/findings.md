---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-10-31"
---

# Findings

## Parent CI Is Still Failing

The local stack base is `2685490718c59d24b0d412fac0c5bb9e0ded9a15`,
the head of girishmotwani/atom#15. Live PR inspection showed both macOS and
both Windows CLI jobs failed in
[CI run 41211435262](https://github.com/girishmotwani/atom/actions/runs/41211435262).
Both Linux CLI jobs, all three POC jobs and documentation passed.

No cause is established. The developer explicitly chose brief-only stacked
preparation rather than base repair. This does not mark Phase 01 complete,
authorize bypassing its failures or establish that they are tooling-only.

## Untouched Root Baseline Is Not A Go Gate Pass

Actual command/output, with only the native worktree prefix replaced by the
declared label `<STACKED_WORKTREE>`:

```text
atom check --no-race
atom check: No go.mod found in <STACKED_WORKTREE>
```

Observed exit code: 2. This is Atom's Python tooling repository; no Go check
ran at its root. No fresh pytest pass is claimed. For later Python source
changes, the existing repository command is
`python -m pytest tests -v --cov=atom` from `tools`.

## Classification POC Confirmed; Production Integration Unproven

Current review orchestration stops before invocation for required failures
(`tools/atom/review.py:345-346`); selection failures also terminate in the CLI
(`tools/atom/cli.py:712-717`). A failure status does not identify a tooling-only
cause. The [brief](poc-brief.md) proposes independent controls rather than
broad error-string matching.

Compatible-control success does not validate the requested compiler or prove
the absence of version-dependent bugs. Missing tools, timeouts, mixed failures
and changed snapshots must not become successful reviews.

At brief preparation, no experiment, production patch or review model call had run.

## Approved Trial Stopped: 2026-11-01

The [POC report](poc-report.md) is Inconclusive. Two native probes verified
Go 1.26.9, but bounded discovery could not verify Go 1.27.0 from PATH,
the declared SDK location or the module-cache location. Zero fixtures and
zero reviewer-stub/model calls ran; the driver exited 2 without retrying.

A read-only inspection after the stop showed PATH distribution metadata:

```text
go1.27.3
time 2026-10-19T22:20:36Z
```

This is VERSION-file metadata, not an executed version probe for Go 1.27.3.
It suggests a candidate for a separately approved control; it does not authorize
substitution or establish the POC's classification result. No source/CI repair,
download, installation, global-setting write or production implementation occurred.

## Revised Batch: Windows Timeout Cleanup Failure

The separately approved Go 1.27.3-control batch verified both distributions.
It completed six first-sweep cases before stopping at the slow-test observation:
35 native commands, two actual stub receipts, zero models, exit 2, Inconclusive.
The original driver/report/captures remain preserved.

The slow fixture formatted, built, vetted and compiled its test executable.
Its supervised `go test -v -count=1 -run TestWait ./...` returned timed_out
without the required entry marker; stdout was empty. Captured stderr:

```text
Command timed out after 2 seconds.
atom: Windows cleanup incomplete: owned job member did not signal exit; [WinError 5] TerminateProcess: Access is denied.; owned primary process did not exit; output incomplete: stdout, stderr
```

Output is explicitly incomplete, so absence of the marker does not prove that
the test never entered. The cleanup failure is not a clean timeout observation
and cannot establish the intended timeout-classification safeguard.

A subsequent read-only process query, scoped to the captured trial window and
exact TestWait invocation, found no surviving matching process. No unrelated
process was stopped. This later observation does not repair the earlier cleanup
failure or establish its cause.

Only valid-source normal/degraded cases reached the stub in the completed
subset; compile defects, a failing assertion, mixed minimum/compile failure and
missing executable were blocked. The slow case did not complete grading,
control-runner-error and changed-source cases were not reached, and sweep two
never ran. Do not turn these partial results into the nine-case/two-sweep proof.
No further POC retry, Windows runner fix or design is authorized yet.

## Read-Only Windows Diagnosis

The [source/evidence diagnosis](windows-timeout-diagnosis.md) maps the recorded
WinError 5 to primary fallback termination after the job-termination/exit-wait
path. Finalization shares one two-second deadline and defers pipe pumping
until after member and primary waits. Pending I/O or asynchronous termination
is a plausible explanation, not a proved cause.

Microsoft documents that TerminateProcess can return error 5 when called again
on a terminated process. The message alone does not establish missing rights;
the read-only member handles are not the handles passed to the failing fallback.
No permission change, source patch or native replay was performed.

The [proposed one-command trace](windows-timeout-diagnostic-brief.md) requires
new approval. Existing parent-exited/cleanup-injection tests do not establish
that the captured Go-supervised timeout state was covered.

## Single Instrumented Replay: Cleanup Failure Not Reproduced

The [one-command trace](windows-timeout-trace-report.md) returned timed_out in
2.0312764999689534 seconds with only the expected deadline diagnostic. Job
accounting recorded one total process, the retained identity signalled exit,
both pipes reached EOF and rescue performed no termination. No native error
or primary fallback termination occurred. The complete child-environment hash
matched the original command, and source/executable hashes were unchanged.

The diagnostic remains Inconclusive: the original failure did not reproduce,
and the required slow-test entry marker was still absent. Do not equate clean
cleanup here with a repair or proof that the test entered. A proposed direct
compiled-test entry probe changes the target and requires another gate.

## Compiled-Test Entry And Timeout Cleanup Confirmed

The [direct compiled-test probe](windows-test-entry-report.md) captured
`slow-test-entered`, timed out in 2.963930599973537 seconds including launch/
cleanup, verified the retained process signalled and observed both output EOFs.
No native error, primary fallback termination or rescue termination occurred.
Full child environment matched the original command; source/binary/compiler
fingerprints were unchanged. One command, no retries.

Confirmed only for this direct binary diagnostic. The original Go-supervised
cleanup failure, parent CI and full classification POC remain unresolved.
The proposed revised classification brief uses direct compiled-test timeout
as an explicitly changed fixture treatment, not a production runner repair.


## Compiled-Timeout Classification POC Confirmed, Bounded

The [compiled-timeout report](poc-report-compiled-timeout.md) records two full
sweeps and 18 expected classifications. Only valid-source normal/degraded cases
reached the local stub (four receipts total); all 14 defective/unknown cases
were blocked. Both direct slow-test runs captured the entry marker and cleanly
timed out with stable source and binary hashes. This does not reproduce or fix
the earlier Go-supervised cleanup failure, nor does it resolve parent CI.

The Go 1.27.3 control invocation evidence was verified after the batch summary
was read; the report records this ordering deviation. No retry or production
change occurred.

## Phase 02 Design Approval: Revised Gate Policy

The compiled-timeout POC confirms only its bounded fixture matrix. The developer explicitly approved the then-current Phase 02 design spec for TDD. During TDD, the selected-gate integration ambiguity surfaced; the developer chose review-specific short-circuiting for default continuation candidates. The revised design spec was explicitly approved for TDD on 2026-11-02. Continuation orchestration is authorized only within that spec; the POC limits remain unchanged.
## Revised Default Continuation Policy — Approved

The developer directed default continuation only for the POC-proven Go-minimum incompatibility; source failures, missing tools, timeouts, and unknown or ambiguous outcomes remain blocking, and strict mode blocks even that case. The verified PATH Go distribution is the default compatible control, with an exact-version override. The earlier design was approved for TDD; the short-circuit policy amendment was explicitly approved at the revised design gate. PATH control discovery/verification and production input fingerprinting were not demonstrated by the POC and remain labeled assumptions.
## Phase Plan Artifact Not Present In This Worktree

A search of this worktree found no `specs/review-tooling-continuation/phase-plan.md`; the only phase plan found is `specs/atom-cli/phase-plan.md`, which covers Atom CLI's original phases and does not define this continuation phase. The Phase 02 design spec and confirmed POC report provide the scope used for the test plan; the short-circuit amendment is approved. No unrelated or speculative phase plan was created.
## TDD Integration Gap Resolved: Selected Gate Short-Circuit Policy

The approved eligibility shape permits downstream required gates to be `SKIPPED` only when the selected build failed, matching the confirmed POC observation. Production `tools/atom/check.py::run_check` explicitly evaluates every gate after a failure, while `tools/atom/review.py::_collect_toolchain_evidence` passes the full default gate list. Thus the current production path cannot produce a build-caused downstream skip; on a below-minimum Go version, vet/test may also fail and conservatively block continuation. Changing review to short-circuit those checks would alter which selected-toolchain evidence is collected. The approved spec does not say whether to preserve current all-gates behavior or stop dependent selected checks after a failed build. The developer chose a review-specific sequence for a default-mode continuation candidate: format first; after a completed selected build failure, skip selected vet/test/race and attempt control only if the other eligibility evidence passes. The revised design spec records this choice and was explicitly approved before continuation orchestration resumed.





## Phase 02 TDD Findings

No additional unresolved production issue was identified in the TDD cycle. The confirmed POC and approved design remain bounded: the full Python suite does not prove cross-platform Go behavior or the unaddressed Go-supervised Windows timeout cleanup. The parent CI failures and runner cleanup finding above remain open; this implementation does not claim to repair either.


## Phase 02 Review Blocked By Model Availability

The approved multi-model review could not run: Atom's configured defaults `gpt-5.4` and `gemini-3.8-flash` were both unavailable to the current account. The command exited 1 before delivering the code-review prompt, so there is no review report or finding triage. The worktree has no `.atom/config.json`; two available reviewer model IDs or an account/configuration change are required to resume review.


## Review Still Blocked After Account Selection

The account split is now applied: repository operations use `girishmotwani`; Copilot CLI model access is authenticated as `gimotwan_microsoft`. Auto and `gpt-5.3-codex` are available, but all tested concrete alternatives were rejected as unavailable, including the Atom defaults. One concrete reviewer is insufficient for the required independent multi-model review. The second account's model policy/catalog needs to expose another distinct model before `review.md` can be produced. No source diff or review prompt was sent; only generic availability probes ran.


## Phase 02 Review Findings Await Triage

## Phase 02 Review Triage

The multi-model review completed with `gpt-5.3-codex` and `claude-opus-5.5` (one answered run each) across the tracked implementation diff and continuation test file. Finding #1, the mismatch between selected changed-file formatting and module-wide control formatting, was fixed after the developer approved an amended contract. The control formatter now checks the same frozen changed Go-file snapshots; a focused regression proves an unrelated unformatted Go file cannot block continuation.

Verification after the fix: `python -m pytest tests -v --cov=atom` reported `1684 passed, 5 skipped`, `95%` coverage; `git diff --check` was clean. The second High finding about whole-module fingerprint cost/scope and findings #3-17 remain open for developer triage. See `phase-02-honest-review-continuation/review.md` for the complete review and dispositions.


## Review Finding #2 — Narrowed Identity Contract Needs Evidence

At this finding-disposition point, the developer had chosen review-snapshot-only identity, accepting that changes outside the captured review inputs are not detected. The existing confirmed POC tested changed-source rejection only with full-source hashes; the approved spike then confirmed selected-path mutation detection without unrelated reads in a 1,002-file fixture. The amended design was subsequently approved, implemented, and verified; the final disposition and accepted scope limit are recorded below. See `poc-report-review-snapshot-fingerprint.md`.


## Review Finding #2 — Implemented With Accepted Scope Limit

The developer approved the changed-review-Go-file-only identity design on 2026-11-03. Changes outside the selected changed-Go-file paths remain an accepted blind spot; the module-wide control build, vet, and test still run. Implementation and verification passed: `python -m pytest tests -v --cov=atom` reported 1686 passed, 5 skipped, and 95% total coverage. The guard intentionally does not detect changes outside the selected changed-Go-file set.
