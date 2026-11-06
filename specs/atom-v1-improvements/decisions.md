---
project: "atom-v1-improvements"
date: "2026-11-04"
---

# Decisions

## Phase 03 Evidence Method

- The accepted Phase 03 plan defines this work as policy validation, not a performance benchmark; the developer selected independent model recommendations and approved a hard ceiling of 48 model calls.
- Use one throwaway Go command for four fixed cases. Probe each proposed model once; allow at most two retries per failed model-case, then use no more than one alternate model for that case, also with at most three total attempts. One failed availability probe permits the alternate for that model's cases. All calls count toward the 48-call ceiling. The original 39-call estimate was incorrect: the uncapped procedure can require 51 calls, so the hard cap may leave slots incomplete. The observed run used ten calls.
- Proposed models are `gpt-5.3-codex` and `claude-opus-5.5`, previously used successfully for Phase 02 review. The developer approved the retry and fallback bounds after the initial brief.
- This is a scoped deviation from treating every POC as a Go product-behavior spike: the uncertainty is model-applied policy, so the calls themselves are the experiment. No production code or policy changes are authorized by this decision.


## Phase 03 POC Result

- The approved experiment completed with 10 calls: two availability probes and one answer per model-case. No retries or alternate model were needed; all attempts were under the approved 48-call hard cap.
- The developer selected Linux as Phase 09's first replay target, chose a small standalone CLI feature, and authorized a WSL-local Copilot CLI update only after the Phase 09 POC brief is approved. Those decisions do not authorize any setup changes before that gate.

## Phase 03 Developer-Choice Evidence Limit

The POC required models to say the developer decides and emit `developer_decides: true`; it did not simulate a developer or test runtime approval/rejection behavior. Treat the confirmed result as recommendation-output consistency only. Any claim about actual human control requires a separately scoped test and approval.

## Phase 03 Rubric Evidence Boundary

The model prompts contained the route labels and their definitions. The spec treats those as candidate policy, not POC-proven risk factors. Discovery-interview and routine-validation guidance, actual human-choice behavior, and taxonomy completeness remain assumptions for the developer to review.

## Phase 03 Approved Implementation

- The developer explicitly approved drafting the spec with the reported model-evidence limitations, then approved that exact guidance-only spec for implementation. This does not authorize review-model spend, shipping, new commands or runtime routing.
- Implement on stacked branch `feat/atom-v1-risk-proportionate-policy` above Phase 02, retaining both safety stashes. No push or commit made for this phase.
- Put shared guidance in the existing POC discipline reference and link it from existing skills/start instructions. Keep canonical and packaged copies aligned; add no policy engine or separate entry point.
- Adapt the Go TDD template to semantic documentation review plus existing link/distribution tests because the approved spec has no runtime behavior. No artificial string-presence tests, production RED/GREEN claim, Go gate result, or new model calls.
- Narrow `.gitignore` only for the existing packaged build skill so its guidance is not omitted from fresh clones. The start command is plugin-only; there is no packaged start-command copy to invent.
- Preserve prior historical findings/decisions from stash rather than overwriting or applying unrelated work. Mark historical pending statuses as superseded by later evidence/approvals.
- Correct the POC transcript using recovered shell 418 output. Leave the archived experiment unchanged and disclose its always-zero exit and unvalidated timeout cleanup; repair/re-gate it before another experiment.
- Copilot's saved active model account is `gimotwan_microsoft`, with no environment token overrides. Keep repository operations on the existing `girishmotwani` account per the earlier split; no authentication change required.

## Historical Roadmap Decisions (Preserved From Stash 606d50e)

The following is the original 2026-10-30 record, not current task status.

---
project: "atom-v1-improvements"
phase: "n/a"
date: "2026-10-30"
---

# Decisions Log

| Choice | Decision and reason | Developer visibility |
|---|---|---|
| Artifact location | Write `specs/atom-v1-improvements/phase-plan.md` in the current VS Code checkout, with findings/decisions, so the requested plan is directly visible | Announced before writing; no unrelated dirty file changed |
| Roadmap before project-wide proof | Use the phase-plan format as a proposed portfolio backlog, not an execution-ready design. The user expressly requested capturing tasks before implementation; no confirmed v1.0 POC exists | Surface with the artifact; phases remain separately gated |
| Attribution scope | Describe Atom's goals, tasks and acceptance criteria in its own terms without references to another skills project | Explicit user request |
| Scope and prioritization | Include existing toolchain/degraded-review requests, discussed workflow ideas and public discovery; label Must/Should/Conditional and show real dependencies | Proposed for approval, not final release scope |
| Existing approval | Retain exact-toolchain POC approval and exact patch-version intent; do not mark the experiment passed or grant new implementation authority | Prior explicit conversation approvals |
| Phase registration | Do not register thirteen unproven roadmap items as approved execution phases or create empty phase artifacts | This is planning capture; register concrete phases after their applicable gates |
| Validation | Documentation-only change: verify persisted files, absence of prohibited references/placeholders and scope, without rerunning unchanged Python tests | Report with the artifact; do not claim a fresh code gate |

## Standing Waivers

None. The request to capture a plan and then start implementation does not waive POC, design, review, publication or paid-work approvals.

## Skipped Steps

No implementation beat skipped. A confirmed project-level POC is not available, so this is expressly a proposed roadmap rather than a standard post-POC execution plan. No production code, existing instructions, phase state, package version, commit or remote settings were changed.

## Accepted Ordering And Product-First Clarification: 2026-10-30

The developer accepted the proposed roadmap ordering and the exact-toolchain POC as the first action. The subsequent instruction explicitly prioritizes making Atom better through v1.0 and returning to visibility afterward.

Accordingly, phases 10-11 (site deployment and distribution) are Deferred (post-v1), not release prerequisites. Phase 09 stays in scope as product usability: working installation and a real example. The local-only Atom Visibility Plan and companion audit notes are stored outside Git worktrees; do not stage or push them. The unpublished README/site drafts remain untouched.

This records an explicit sequencing decision, not a waiver of evidence, design, review, paid-work or publication gates. Resume the already approved exact-toolchain POC without broadening its scope.

## Phase 03 Implementation Completion Gate

The developer selected "Approve implementation" after receiving the guidance diff, the test-spec artifact, 50 passing targeted tests, resolved documentation links, canonical/packaged parity, and the deferred POC-harness limitation. This approves the guidance-only implementation for the next review gate, not publication or an unbounded model-review batch. No review calls or push occurred.

## Requested Draft Publication: 2026-11-05

The developer explicitly requested "show me the diff, push the change and create a PR" and "also push the plan spec upstream". Publish the Phase 03 branch to public `girishmotwani/atom`, including the restored accepted-ordering phase plan and all Phase 03 proof/design/verification artifacts. Keep the PR stacked on the still-open Phase 02 branch.

Multi-model review has not occurred. Open a draft PR to obtain review, not a ready-to-merge or fully reviewed phase claim. No new model batch is authorized or launched. This intentionally publishes the approved guidance implementation before the normal post-review ship point; it does not waive that review or future gates.

Fresh shipping validation uses the existing documentation/distribution checks for this guidance-only phase. Go `atom check` is not applicable at this Python repository root; do not fabricate its result. Format the archived spike with `gofmt` via the artifact writer and verify vet/build without executing its paid calls. The known archived verdict/timeout limitations remain disclosed, not silently repaired or reinterpreted.

## Multi-Model Review Before Publication: 2026-11-05

The developer redirected publication: "lets do the multi model review first", then selected "Approve 4-call review". Hold push/PR creation until review and developer triage. The approved bound is one availability probe and one independent full-diff review each for `gpt-5.3-codex` and `claude-opus-5.5`: four calls total, no retries or fallback. Neither is the Phase 03 implementation author (`gpt-6.1-sol`).

Use the current checkout's review implementation with fixed evidence and disabled model tools/custom instructions. Freeze the staged Phase 03 change (including the requested restored roadmap) and supply whole-file context plus the approved spec. Review existing guidance/contract drift and evidence claims, not just Go style. The source CLI reviews the full diff per call; do not infer a per-file multiplied budget from the installed skill's prose. The installed CLI lacks the checkout's newer options, so invoke `atom.cli.main` from `tools` without updating dependencies.

Documentation/distribution checks freshly passed (50 tests); all seven canonical/packaged pairs match. Archived spike vet/build passed, then `gofmt -l` caught an extra final blank line introduced by the PowerShell-to-writer pipeline. Removed that pipeline-added blank line through the artifact writer and reran vet/build/gofmt successfully, without executing the spike. Repository-root Go gates remain explicitly skipped, not passed; local checks do not prove live developer control or universal model quality.

## Review Triage Approved: 2026-11-05

Both models completed the approved four-call review (two probes plus two review calls, no retries). The developer selected "Fix guidance, provenance and deterministic harness defects; defer Windows lifecycle" after receiving the merged findings.

Authorize reconciling the start/build/spec/TDD instructions and metadata, correcting the 51-call uncapped budget arithmetic and historical successful-stderr provenance, and fixing/verifying deterministic archived-harness verdict/probe/required-field/capture defects without new paid model calls. Historical lost stderr remains unknown; do not rewrite it as captured empty output. Defer Windows process-tree timeout validation with an explicit archive warning. Do not treat the four-call review budget as permission for a rerun.

Publication remains pending repairs and appropriate verification. The earlier explicit push/PR request includes the restored roadmap and Phase 03 artifacts; it does not authorize merging or a new Windows lifecycle experiment. No commit or push has occurred.

## Start Routing Repair After Restart: 2026-11-05

The developer confirmed the saved Phase 03 branch and restart handoff, then explicitly approved the start-command repair after its scope was explained. Reconcile the existing router with approved regression proof, bounded evidence reuse and specifically justified no-uncertainty skips; retain proof, spec and implementation approvals. Documentation-only work uses factual/relevant checks. No entry point, runtime phase check, new model call, branch switch or publication is introduced by this repair.

Validation for this documentation-only repair uses semantic comparison with the approved design/shared POC discipline, the existing relative-link checker, the existing plugin command-surface tests and scoped diff hygiene. No artificial Go test or runtime enforcement claim. The start command has no packaged asset counterpart; none was invented. Remaining approved review repairs are still pending.

## Deterministic Harness Regression Fixture: 2026-11-06

The approved archive repair uses the compiled Go test executable as a fake Copilot CLI in a temporary directory, exercising the real harness command path without paid calls. Missing/null boolean cases failed for the intended assertions, then passed after explicit-field validation. Disagreement and gate-bypass cases exposed exit 0 instead of exit 1. The 48-invocation retry/cap fixture exceeded its original one-minute test deadline on this Windows machine; that was a fixture-time budget failure, not proof about harness verdicts. Increase only the test deadline to three minutes, preserving the expected verdict, exit, retry count and hard-cap assertions. This does not change the live harness timeout or validate Windows descendant cleanup. No test expectation was loosened.


## Approved Archive Repairs Implemented: 2026-11-06

Implement only the deterministic defects accepted at review triage: explicit required booleans and rejection reasons, exact READY availability probes, nonzero exits (1 Refuted, 2 Inconclusive), and stderr capture on successful as well as failed commands. Preserve all case facts, prompts, model choices, retry/fallback limits and the 48-call ceiling. Keep the original transcript unchanged; the ten historical empty stderr labels were placeholders produced by discarded streams, not proof of empty stderr.

The archive is not an Atom runtime component. These repairs keep the published evidence runnable without known false-success/capture defects; they do not prove the policy taxonomy or actual developer-control behavior. Fake-CLI tests exercise deterministic paths only. Windows descendant termination and a hard wall-clock timeout remain unvalidated and deferred; any live rerun still needs instrument/lifecycle review and a separately approved model-call budget. No new paid calls, runtime policy engine or production API changes.

Reconcile build/spec/TDD guidance in both canonical and packaged copies: skipping a POC needs explicit developer approval; approved no-uncertainty skips remain legitimate spec inputs; documentation-only work uses factual/distribution checks rather than fabricated runtime tests or Go gates. These are repairs to the approved guidance contract, not relaxed proof or approval requirements.

## Repair Completion Gate: 2026-11-06

Archive atom check passed every required build/vet/format/test/race gate; the selected Python documentation/distribution suite passed 50 tests. Preserve the full captured sequence in the phase tdd-log rather than asserting a new policy POC or model review. Verify packaged instruction content with native newline normalization: the first byte-level check found only pre-existing CRLF/LF differences, with identical text.

Keep the original transcript and raw model-review JSON unchanged. Do not repair unknown historical stderr by filling it in; preserve the corrected provenance note. No second model batch or live rerun is authorized. Stop at the repaired-snapshot completion gate before acting on the earlier explicit publication request.

## Repaired Snapshot Approved For Shipping: 2026-11-06

After receiving the repaired artifacts, full archive Go gate, 50 passing Python tests, 419 resolved links, unchanged original evidence and the deferred Windows lifecycle boundary, the developer selected "Approve repaired snapshot for shipping". This authorizes shipping the repaired Phase 03 snapshot under the earlier explicit request to push the change and restored plan spec and create the stacked PR. It does not authorize merging, another paid model batch, a live rerun or Windows lifecycle work. End this repair-gate turn before starting the ship beat. No commit/push/PR has yet occurred.

## Shipping The Approved Phase 03 Snapshot: 2026-11-06

The developer explicitly renewed the instruction: "lets push and create PR". Publish only the 32 approved Phase 03 guidance/archive/artifact paths, including the accepted-ordering roadmap; preserve both safety stashes and all other worktrees. The public target is girishmotwani/atom. Phase 02 PR #17 is open and standalone, with head feat/atom-v1-review-continuation at 3ca1c8f94c655e661eb2d5dcb77c8228b4c30d90, matching this branch's parent. Read-only native-stack probes succeeded and found no existing stack membership.

Create one Phase 03 commit and fast-forward-push its existing branch, then open a PR against the Phase 02 branch and register the ordered pair as a native stack after revalidating both PRs. No force push, rebase, merge or auto-merge is authorized. Open ready for review after the completed multi-model review, accepted repairs and explicit completion gate; the earlier draft plan applied before that review, not a claim that merge is authorized.

Use gh pr create with explicit repository/head/base and the actual evidence body. The installed atom ship help has no --pr option and its normal Go-root workflow does not describe this multi-project Python checkout; do not invoke a mismatched wrapper, skip gates or let fallback state select the unrelated artifact-writer project. The archive Go gate and selected documentation/distribution tests were freshly rerun before committing. These shipping records are pre-publication; the PR/commit metadata will record the completed remote action.
