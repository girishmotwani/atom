---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-10-31"
---

# Decisions

## Approved Scope And Stack

The developer requested the next phase and allowed stacked PRs. After the
base-CI blocker was surfaced, the developer selected:
"Prepare the Phase 02 POC brief on a stacked branch".

Created local branch `feat/atom-v1-review-continuation` in an isolated worktree
from `2685490718c59d24b0d412fac0c5bb9e0ded9a15`. The intended eventual PR base
is `feat/atom-v1-toolchain`, not main, while girishmotwani/atom#15 remains open.
Reconcile that base explicitly if the parent is repaired or merged.

Preserve the original dirty checkout, the parent feature worktree and the
unpublished visibility plan. No branch was pushed and no PR was opened.
Stacking approval is not permission to publish automatically.

## Brief-Only Evidence And Boundaries

Read the accepted roadmap from the original checkout; it is absent from the
published parent snapshot. Do not copy unrelated local plan changes into the
stack. Phase 02 is honest continuation on tooling incompatibility.

Observed the untouched `atom check --no-race` root failure, exit 2, and recorded
it in [findings](findings.md). Since only documents change, use the existing
documentation-link check and exact artifact-byte checks; do not claim a new
source baseline or run the proposed experiment under brief-only approval.

## Proposed Choices, Not Approved Design

The initial class, nine fixtures, two serial sweeps, two installed compiler
versions and command/time caps in the [brief](poc-brief.md) are proposals for the
next gate. Expected fixture labels are grading data, not classifier inputs.
No production API, default continuation rule or CLI exit policy is selected.

Use disposable Python automation around real Go fixtures rather than a Go-only
driver: this follows the repository's Python automation convention. Native
compiler evidence must stay distinct from the explicitly simulated runner error.

No production source/tests, dependencies or machine policy change.
No model call, experiment, base-CI repair, push or PR is authorized by this
brief-only decision. The next step is developer approval of the bounded POC.

## Artifact Transport Correction

The first accepted brief write contained an extra final LF: its session draft
used native CRLF, and removing only LF before the native pipeline left CR.
Content verification caught the mismatch. Normalize the complete draft to LF
before removing its final newline and rewrite through the same artifact writer;
do not bypass a refusal or edit the accepted artifact directly.

## Approved POC Batch: 2026-11-01

After the POC was described, the developer said "approved, lets proceed".
This supersedes brief-only scope for one declared experiment: nine cases, two
sweeps, Go 1.26.9 and Go 1.27.0 already installed, at most 96 native Go/gofmt
commands, 60-second ordinary deadlines and a 15-minute overall ceiling.
No model, download, installation, retry, design, source patch, push or PR.

The driver stops dependent build/vet/test commands after an earlier failed gate
and records those commands as unrun. Controls must actually pass all bounded
checks to support degraded admission. Every failed or skipped selected check
remains labelled separately. Raw logs and fixtures stay outside Git.

Use existing selection, native runner and evidence rendering without modifying
them. The disposable classifier sees observations, not fixture labels/grading
answers. The explicitly simulated runner-error case is not native Go evidence.

## Inconclusive Stop And Next Gate

The approved batch stopped before its matrix: Go 1.26.9 verified with two
native commands; the exact Go 1.27.0 control did not match bounded installed
discovery. Preserve the driver and raw captures without changing treatment or
retrying. Classification remains unproved; no design is authorized.

After stopping, read only the known PATH distribution's VERSION file.
It declares Go 1.27.3; no extra compiler probe ran. A proposed new batch using
that patch as control needs explicit revised-treatment approval and fresh
identity verification. Do not infer an installation/change timeline from this
metadata or replace the declared control silently.

Archive complete output/events outside Git and retain their hashes. Published
captures replace only declared native profile/trial prefixes (including their
JSON-escaped forms); observations, failure reasons, ordering and counts remain.

## Revised Batch Approval

The developer selected "Approve revised control and one new batch" and then
said "lets start". A distinct full brief and driver change only the compatible
control from Go 1.27.0 to Go 1.27.3. Preserve the original driver, first brief,
Inconclusive report and captures. Source fixtures/minimums, classifier/grading,
selected compiler and all approved limits remain identical.

The new trial uses a fresh outside-Git directory and verifies both distributions
before fixtures. The recording runner logs executable identities, command
outcomes, hashes and real stub receipts. No retry or production change is
authorized by the revised approval.

## Revised Batch Stopped: Preserve Partial Evidence

The revised driver differs from the original only in the declared control patch.
It verified Go 1.26.9/1.27.3 and executed 35 native commands, with six graded
first-sweep observations and two actual stub receipts. It stopped Inconclusive
at the missing slow-test entry-marker/timeout signal. Sweep two and the last
two first-sweep cases were not run.

Do not weaken the marker requirement, increase deadlines, substitute direct
test-binary execution, repeat the batch or call this Confirmed. The recorded
timeout includes Windows termination/output-collection failures. Preserve the
complete raw evidence and the executed revised driver without patching it.

A scoped read-only survivor check returned no matching trial process. No
name-based process termination or unrelated cleanup was performed. That result
does not override the native runner's earlier incomplete-cleanup evidence.
Windows runner diagnosis or another treatment requires the next developer gate.

## Approved Read-Only Windows Diagnosis

The developer selected "Diagnose the Windows runner cleanup failure", then
said "continue". Trace existing source and captured evidence first; no POC
retry or production patch was authorized by that decision.

Inspected native finalization, runner outcome handling, existing native tests
and public Microsoft API documentation. Reject an unsupported snapshot-handle
rights fix: the failing fallback uses the primary process handle. Treat
asynchronous termination/drain ordering as a hypothesis, not confirmed cause.

Do not infer that the earlier CI failures share this cause from an old log
search. Persist the read-only diagnosis and a proposed one-command trace
brief; native execution and any repair require the next scoped gate.

Post-compaction AGENTS and discipline references were reread after initial
source inspection and draft preparation, rather than before that work.
This was a process deviation. No native replay or production edit occurred;
the diagnosis remains explicitly unproved and the next experiment gated.

## Approved Single Instrumented Replay

The developer selected "Approve the single instrumented replay", then said
"lets go". This authorizes one Go command with the original selected compiler,
fixture and two-second command/cleanup timeouts, a 30-second diagnostic
ceiling, no automatic retry and no production patch or full POC rerun.

Use a session-only Python driver with in-memory timestamped observation of
native returns/errors, finalization and pipe pumping. Retain additional
process handles for identity-bound post-return checks/rescue. These handles
and logging introduce observer effects, so no successful run establishes
failure frequency or production repair. Do not retain a duplicate job handle:
that would change kill-on-last-job-handle-close behavior.

The trace question is copied verbatim from the approved diagnostic brief.
This is one diagnostic observation, not a timing benchmark or two-arm
comparison; do not repeat it to satisfy a general measurement-repeat rule.

## Instrumented Replay Stop And Next Gate

Executed the approved single replay once. Preserved all 2,063 raw trace events
and console output. No automatic retry, production edit or full POC rerun.
The 30-second ceiling was not reached; the driver clock begins after Python
imports/setup. The one process identity was signalled at runner return, so no
rescue termination occurred.

Grade Inconclusive because the cleanup failure did not reproduce and the
entry marker remained absent. Do not reinterpret this as a disproved timing
issue, privilege diagnosis or passing classification POC.

Propose one direct invocation of the already compiled test binary as a
separately gated entry/cleanup diagnostic, not as a silent replacement for the
approved package-mode classification fixture. No implementation repair is
authorized by the current result.

## Approved Compiled-Test Entry Probe

The developer selected "Approve one compiled-test entry probe", then said
"lets run". Run one preserved test-binary invocation with the same two-second
command/cleanup limits and 30-second diagnostic ceiling; no compiler command,
retry, installation, model call, source edit or classification POC replacement.

Prepare a distinct session-only driver from the immutable package-mode
diagnostic, preserving its observational wrappers and owned-identity rescue.
Check the fixture against the prior trace's source fingerprints, binary
before/after hashes and original full child-environment fingerprint.

The original compiler event names the preserved binary but does not contain its
hash. The new binary fingerprint proves this probe's before/after identity,
not independent byte-level provenance back to the original compilation.
Keep that limitation explicit rather than claim an unavailable original hash.

## Compiled-Test Result And Revised-POC Proposal

Executed the approved entry probe once. Retained all 2,249 native observations
and raw console output. Entry, timeout, signalled exit and both output EOFs
were observed; no rescue termination occurred. Grade Confirmed only for the
direct compiled-test question, not the package-mode failure or Phase 02.

Propose changing only the slow classification fixture's timed command to
the compiled binary, adding before/after binary identity evidence. Keep
the same question, compiler/control versions, nine cases, two sweeps, limits
and grading; preserve all earlier drivers/reports. Ordinary valid/control
fixtures still use Go build/vet/test.

The original supervised cleanup issue remains an open finding, not waived or
repaired. A new classification batch requires a new approval; no source fix,
design, full POC run or publication occurred under this diagnostic approval.


## Approved Compiled-Timeout Classification Batch

On 2026-11-02 the developer approved the revised brief after reviewing the
confirmed direct-binary entry probe. Authorization is exactly one serial batch:
two sweeps of the nine cases, Go 1.26.9 selected and Go 1.27.3 control, no more
than 96 native commands and 15 minutes. The separate driver changes only the
slow case to compile with the selected compiler and invoke the resulting test
binary directly. It records binary/source hashes, entry output and clean
cleanup evidence. No models, downloads, installations, production changes,
retries or publication. Preserve all prior drivers/reports and stop after this
batch for the POC report gate.


## Compiled-Timeout Batch Result And Evidence Ordering

The developer approved exactly one revised nine-case/two-sweep batch after the
compiled-binary diagnostic. Ran the new `spike-compiled-timeout.py` once in a
fresh outside-Git directory. It completed 18 observations with 82 native
commands in 163.3361283999402 seconds, produced four local stub receipts, and
made zero model calls. Verdict: Confirmed for the approved bounded criteria.
The original Go-supervised timeout failure remains open; no production fix,
design, retry, commit, push or PR was authorized.

Treatment-use process deviation: after the run, verified direct binary action
records and their entry/timeout/hash behavior before reading the batch summary.
However, the separate Go 1.27.3 control command count/outcomes were inspected
after the summary had already been read. The raw event log independently shows
24 completed Go 1.27.3 command invocations. Report this post-result verification
plainly and discount it; do not claim all treatment checks were confirmed
before result inspection. No retry was added to repair this ordering deviation.

## Phase 02 Design Spec Draft — Awaiting Gate

The developer approved writing the Phase 02 design spec after the bounded
compiled-timeout classification POC was confirmed. The draft is
[design-spec.md](phase-02-honest-review-continuation/design-spec.md). No
production implementation is authorized until that exact spec is approved.

The draft proposes (not records as approved decisions):

- Strict behavior by default, with an explicit continuation flag and an exact,
  already-installed compatible Go version; no automatic download or fallback.
- Continuation only for the POC-shaped selected build failure below the parsed
  module minimum, with stable input identity and passing bounded control checks.
- Selected failures remain visible; control passes do not count as selected
  passes. Race/advisory checks remain outside this POC-proven control set.
- A degraded report increments the review JSON schema to v3 and still exits
  non-zero so CI does not treat the requested toolchain as validated.

These are proposals requiring the developer's design-gate approval. The spec
also records unproven assumptions about production input fingerprinting and
module/dependency coverage; it does not claim that the POC fixed the Windows
runner issue or proved cross-platform behavior.

## Developer Direction: Default Continuation, Strict Opt-In

At the Phase 02 design gate, the developer requested default continuation for
tooling incompatibility and strict enforcement through an option. On clarification,
the developer chose to limit default continuation to the POC-proven case only;
source failures, missing tools, timeouts, and unknown/ambiguous failures remain
blocking, and strict mode blocks even the proven case.

The developer selected the verified PATH Go distribution as the default
compatible control, with an exact-version override. The revised draft proposes
`--strict-toolchain` for the strict opt-in and `--control-go-version` as the
optional override. PATH control discovery/verification and production input
fingerprinting were not demonstrated by the POC and remain labeled assumptions.
This direction authorizes revising the spec only; it does not approve the spec
or authorize TDD, implementation, publication, or a PR.
## Phase 02 Design Approval And TDD Scope

The developer explicitly approved the exact revised `phase-02-honest-review-continuation/design-spec.md` for TDD after choosing default continuation only for the POC-proven minimum-version incompatibility, strict opt-in behavior, and verified PATH Go as the default control with an exact-version override. The approval authorizes implementation of that spec only; it does not authorize a broader fallback, a Windows runner repair, commit, push, or PR.

The repository's implementation is Python under `tools/`, so the test plan uses pytest and existing scripted process/model boundaries rather than the generic Go test commands in the skill template. The continuation project has no phase-plan artifact in this worktree; the existing `specs/atom-cli/phase-plan.md` is for the original Atom CLI phases and is not applicable. This gap is recorded in `findings.md`; implementation proceeds from the approved design and its confirmed POC report without inventing phase-plan content.
## TDD Baseline And Clarification Gate

Before source changes, `python -m pytest tests -q` from `tools` completed with `================= 1615 passed, 5 skipped in 312.22s (0:05:12) =================`. The first TDD loop added the strict-toolchain CLI help option and rejected `--strict-toolchain` with `--skip-toolchain`; the focused tests passed (`2 passed, 65 deselected`).

Before implementing the selected/control gate orchestration, TDD inspection found that existing `run_check` deliberately evaluates every gate after a failure, whereas the POC continuation case had dependent selected checks skipped after build failure. The design allows only those causally skipped gates but does not specify whether production review should introduce review-specific short-circuiting or retain all-gates execution and block if later gates fail. No choice is made here; continuation implementation is paused for the developer's decision.
## Developer Choice: Candidate Gate Short-Circuit

After reviewing the TDD finding that production runs every gate after build failure, the developer chose review-specific short-circuiting for a default-mode continuation candidate: format first; after a completed non-zero selected build, record vet/test/race as skipped because of that build and do not execute them under the selected compiler. A selected build timeout, missing tool, or runner error remains blocking. Existing all-gates behavior stays in place for strict mode, unpinned reviews, and non-candidate requests. The revised design spec was explicitly approved for TDD on 2026-11-02; continuation orchestration is authorized only within that contract.
## Revised Design Re-Approved

After the selected-gate policy amendment, the developer explicitly approved the exact revised Phase 02 design spec for TDD. The approved contract runs formatting before build only for a default-mode continuation candidate, blocks on formatting failure/non-completion, and skips selected vet/test/race after a completed non-zero selected build. Build timeout, missing tool, and runner error remain blocking. Strict mode, unpinned reviews, and non-candidates preserve existing all-gates collection behavior.


## Phase 02 TDD Implementation And Verification

Implemented the approved Phase 02 design in Python under `tools/`; no production Go code was added. The work remains on the isolated `feat/atom-v1-review-continuation` worktree. No commit, push, or PR was made.

The continuation path preserves selected and control gate evidence separately, only admits the approved completed non-zero selected-build shape, fingerprints module inputs, and blocks on timeout, missing tool, runner error, source change, unverified control, or any non-passing control gate. Strict mode and `--skip-toolchain` retain their approved semantics. The review JSON schema is v3.

The first repository-wide run after schema v3 had five failures, all parameter cases of `test_cli_rule_metadata_never_serializes_policy`; the test still expected schema v2. The approved design explicitly increments review JSON to v3. Updated that stale expectation to v3 and reran those five cases: `5 passed, 33 deselected`. This was a justified test correction, not a production behavior change.

TDD process deviation: lifecycle evidence fields in `_review_format.py` and selected review JSON were added before their regression assertions were added. The control-gate lifecycle field received a clean assertion RED (`KeyError: 'command_outcome'`), then passed after the field was added. Some fail-closed edge tests (unreadable/special fingerprint inputs, unavailable/unverified control, skipped control, selected timeout, and skip-mode degradation) were also added after the implementation existed, because the coverage reconciliation exposed the gap. These tests passed without requiring additional production changes. The test-spec checklist marks this evidence limitation rather than presenting those cases as witnessed RED/GREEN loops.

Final verification from `tools`:

```text
python -m pytest tests -v --cov=atom
TOTAL                        4712    232    95%
================= 1683 passed, 5 skipped in 207.12s (0:03:27) =================
```

The full suite first exposed the stale schema assertion; after correcting it, the final full run passed. A final focused run after the last strict-mode assertion passed: `2 passed, 56 deselected`.


## Phase 02 Review Attempt Blocked

After the developer approved proceeding to `/atom:review`, invoked:

```text
python -m atom.cli review --working --model gpt-5.4 --model gemini-3.8-flash --runs 1 --json
atom review: No review model could be called: gpt-5.4 (Error: Model "gpt-5.4" from --model flag is not available.); gemini-3.8-flash (Error: Model "gemini-3.8-flash" from --model flag is not available.)
atom review: no model returned a usable response; this is not a clean review.
```

The account's available models did not include either default Atom reviewer. The failure occurred during model availability probes; no review prompt or source diff was delivered to a reviewer, and no review report was produced. `.atom/config.json` is absent from this worktree. A metadata-only GitHub visibility query also returned `Could not resolve to a Repository with the name 'gimotwan_microsoft/atom'`, so visibility was not established. Stop here rather than substitute unverified models or claim a completed multi-model review; request two available reviewer model IDs or account/configuration changes.


## Review Authentication Split and Retry

The developer clarified that GitHub repository operations must use `girishmotwani`, while Copilot model access must use `gimotwan_microsoft`. Switched the active `gh` account back to `girishmotwani` and authenticated Copilot CLI with the `gimotwan_microsoft` GitHub CLI token; Copilot reported `Signed in successfully as gimotwan_microsoft.` This keeps repository operations and model access on the requested accounts.

Retried the review and used only generic, no-repository-data prompts to probe supported model IDs. `auto` and `gpt-5.3-codex` returned `OK`; `gpt-5.6-sol`, `claude-sonnet-5.5`, `claude-sonnet-4.6`, `gpt-6.1-sol`, `grok-4.7`, and `gemini-4-argon` each returned `Error: Model ... from --model flag is not available.` Retrying Atom's defaults (`gpt-5.4`, `gemini-3.8-flash`) also failed availability checks. Since only one concrete reviewer model was confirmed available, do not send the source diff or claim a multi-model review. A second distinct model must be enabled or identified before continuing.


## Phase 02 Multi-Model Review Completed

The developer specified separate accounts: `girishmotwani` for GitHub repository operations and `gimotwan_microsoft` for model access. The active `gh` account is restored to `girishmotwani`; Copilot CLI is authenticated as `gimotwan_microsoft`.

Review completed using `gpt-5.3-codex` and `claude-opus-5.5`, one run each. The first working-tree snapshot covered 10 tracked code/test files (750 changed lines). Because `tools/tests/test_review_continuation.py` was untracked and absent from that diff, it was temporarily staged alone and reviewed separately with both models; it was then unstaged, and `git status --short` confirmed no staged changes remain. Both review runs were complete and produced usable findings. Go toolchain checks were not run because no `go.mod` exists under `tools`; the Python full-suite evidence remains the earlier TDD result (1683 passed, 5 skipped, 95% coverage).

An earlier review attempt timed out for one model; a retry completed. The separate test-file review initially timed out for both models, then completed with `--concurrency 1`. No code changes were made in response to review findings. The report is at `phase-02-honest-review-continuation/review.md`; High and Medium findings await developer triage.


## Review Finding #1: Design Re-Gate Required

The developer chose “Fix now” for the control-format scope finding. Matching the control formatter to the selected changed-file snapshot is a behavioral contract change, so the design/test spec is amended and presented for approval before any code/test edit. No implementation has started. The expected `specs/review-tooling-continuation/phase-plan.md` was not present; the confirmed POC report and existing approved phase design were read and remain the available evidence.


## Review Finding #1 Design Amendment Approved

The developer approved the amended control-format contract: use the same frozen changed Go-file snapshots for selected and control formatting, with the control distribution's formatter; unrelated module files do not affect control `fmt`, and an empty scope remains skipped and blocks continuation. This authorizes a focused TDD fix only. Begin with a failing test that proves unrelated unformatted files do not fail the control formatter.


## Review Finding #1 Fix Implemented

The developer-approved control-format contract was implemented test-first. The new test showed that an unrelated unformatted Go file blocked continuation through the module-wide control formatter. Control formatting now evaluates the selected `ChangedFilesFormatGate` through the verified control formatter.

The first full-suite run exposed an outdated eligible-control fixture: it scripted only the superseded `gofmt -l .` command, so the existing happy-path test failed with `control fmt`. The fixture was updated to script the frozen snapshot's control-formatter stdin/stdout; its behavior assertions were not weakened. The focused regression set passed (148 passed), and the final full Python suite passed (1684 passed, 5 skipped, 95% coverage). `git diff --check` was clean.


## Review Finding #2 Scope Chosen

On 2026-11-03 the developer chose identity checking limited to changed Go-file paths captured in the review snapshot, explicitly accepting that other module files may change without this guard detecting them. This materially narrows the approved design's whole-module identity guarantee. The developer approved the POC brief; its Confirmed, bounded report is `specs/review-tooling-continuation/poc-report-review-snapshot-fingerprint.md`. The amended design was approved on 2026-11-03 before implementation.


## Review-Snapshot Identity POC Confirmed

On 2026-11-03 the developer approved one scoped POC. `atom poc run review-snapshot-fingerprint` passed vet, build, and execution. In a 1,002-file fixture, a selected-file mutation changed the scoped identity; an unrelated-file mutation did not, and the reader opened no unrelated paths. The result supports the selected-path scope only. It does not prove complete module-input identity, production Git-source integration, failure cases, or repository-scale performance. The developer's accepted blind spot for other module files remains explicit. No implementation is authorized until the amended design is presented and approved.


## Review Finding #2 Amended Design Approved

On 2026-11-03 the developer approved the amended Phase 02 design and B7 test obligations. Implementation may now proceed test-first against the changed-review-Go-file-only identity contract; files outside the selected changed-Go-file set remain intentionally undetected by this guard.


## Review Finding #2 — TDD Implementation

The approved contract hashes only live paths in the frozen `ChangedFilesFormatGate` snapshot before selected checks and after control checks. Other module files are intentionally outside this identity guarantee; the control build, vet, and test remain module-wide. Missing formatting scope and selected-path read/identity failures block continuation.

TDD evidence:

- Core selected-only identity test RED: `_fingerprint_review_snapshot` was absent; the assertion failed as expected. GREEN passed with a selected mutation changing the identity, an unrelated mutation leaving it stable, and the open tracker observing only the selected path.
- Missing-scope integration RED: the assertion observed an `AttributeError` instead of `SourceFingerprintError`; adding an explicit pre-check made it pass before selected build or model invocation.
- The selected-path missing, unreadable, symlink, and non-regular tests and unrelated-mutation end-to-end test were adapted/added after the scoped helper first passed. Their individual RED output was not observed; this is a TDD process deviation. These assertions were not weakened.
- `pinned_review_fixture` now creates its captured `main.go` on disk. The previous fixture described a captured changed-file snapshot without a corresponding live path, which correctly fails the approved missing-path contract.

Focused verification:

```text
python -m pytest tests/test_review_continuation.py tests/test_review_toolchain.py -q
84 passed in 2.31s

python -m pytest tests/test_review_continuation.py tests/test_review_toolchain.py -k 'review_snapshot_identity or source_change_after_selected_checks or unrelated_source_change or missing_review_snapshot_scope or pinned_review_uses_selected_gates' -q
9 passed, 75 deselected in 6.25s
```

Full Python verification:

```text
python -m pytest tests -v --cov=atom
TOTAL                        4716    235    95%
1686 passed, 5 skipped in 245.95s (0:04:05)
```

`git diff --check` exited 0. No Python lint tool is configured in `tools/pyproject.toml`.
