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

## Phase 09 Discovery Choices: 2026-11-07

The developer chose CSV expense totals by category, building from scratch with
Atom, and following the prompts/gates without the full methodology as the main
uncertainty. They explicitly chose their own experienced-user rehearsal first,
not a genuine newcomer trial. Linux remains the first target; prior WSL update
permission still requires approval of this phase's brief.

The [phase decisions](phase-09-onboarding-example/decisions.md) record these exact
choices, the proposed observed-replay evidence method, scoped Python baseline
and unapproved acceptance/spend boundaries. Discovery artifacts are isolated on
new local branch feat/atom-v1-onboarding-example from 4434cdf; no existing remote
PR/stack, phase runtime state or other worktree changed.

The [replay brief](phase-09-onboarding-example/poc-brief.md) is draft. There is no
standing waiver and no WSL setup, live model session, final design, implementation,
commit or publication approval from these interview answers.

## Brief Approval Recorded: 2026-11-07

The developer selected "Approve the bounded rehearsal brief" after reviewing the
artifact path, experienced-user evidence limitation, proposed CSV/refund/error
contract, WSL-local setup scope, one interactive session and manually observed
60-minute active-effort cap. The 30-test scoped baseline and 425 resolved links
were disclosed; no full-suite, Linux runtime or newcomer-usability pass was claimed.

This approves preparation and the named bounded rehearsal under ordinary command
permissions and the example's own evidence/spec/implementation gates. It does not
approve extra provisioning/login, additional agents/model-review batches, a final
Phase 09 design, production example, commit, push, PR or release. Material recipe,
condition or budget changes stop for a new decision. No WSL update, plugin install,
live model session or Go implementation has occurred. Stop this gate turn before
starting rehearsal preparation.

## Phase 09 Preparation Paused At CLI Setup: 2026-11-07

The developer authorized preparation with "lets do it". The official Ubuntu
updater was executed without elevation and reported a download, not a verified
active-version update. Follow-up version probes failed the required minimum.
Stop before an additional CLI installation, privileged repair or material recipe
change. The phase decisions record a proposed pinned user-owned installation
versus separately authorized repair of the existing launcher. No model session,
example implementation or simulated developer approvals have occurred.

## User-Owned CLI Setup Repair Approved: 2026-11-07

The developer selected "Approve pinned user-owned installation with explicit
executable path" after the failed activation/freeze checks and installation
alternatives were presented. Authorize the official stable v1.0.107 installer
as the ordinary Ubuntu user, with a new PREFIX of $HOME/.local/atom-phase09-tools.
Stop if that destination already exists, is not a safe user-owned Linux-native
location, or needs additional privilege/provisioning. Verify the resulting
binary/version before installing Atom or starting the rehearsal.

Use $HOME/.local/atom-phase09-tools/bin/copilot explicitly for version/plugin
commands and the eventual interactive session; do not substitute the old PATH
launcher. Prevent auto-update during the frozen attempt with supported options.
This approved amendment supersedes the generic copilot launcher in the original
candidate recipe; finish and freeze the exact commands after verification.

Leave /usr/local/bin/copilot, shell PATH/profile, Windows tooling, Go/Python
defaults and existing authentication unchanged. Do not run sudo/root commands,
install Node/npm or another toolchain, log in, launch extra agents or simulate the
developer. Record the intentionally separate CLI installation and actual plugin
snapshot identity. The one-session/attempt and manually observed 60-minute
active-rehearsal bound remain unchanged.

No user-owned installer, plugin installation, example module or live model
session has been executed at this approval gate. End the gate turn before
performing this newly approved setup repair. The underlying updater cause and
actual novice usability remain unproven.

## Tool Preparation Verified And Recipe Frozen: 2026-11-07

The approved user-owned Copilot CLI 1.0.107 installation passed checksum and
explicit-version verification. Public Atom 0.2.0 is installed; all nine skills
and three command files are present. The old launcher and shell profiles retain
their captured hashes; no sudo, login, credential copying or global PATH edit.

The [phase findings](phase-09-onboarding-example/findings.md) and
[phase decisions](phase-09-onboarding-example/decisions.md) preserve the actual
installer/plugin outputs, content inventory, earlier guard correction and
verified private-recorder probe. The
[frozen recipe](phase-09-onboarding-example/rehearsal-recipe.md) SHA-256 is
69617ba5da1d9f277af92b5e1816058d625e5f57ea0c9d1ef38ec8edd9fb5052. Child-only PATH selects the pinned CLI without changing
Go/Python/git resolution. One session/attempt and the manual 60-minute active
bound remain; no additional agent/model batch or permission waiver.

Authentication/model access remains unverified. No interactive rehearsal,
example module, Go implementation, final Phase 09 design, commit or publication
has occurred. The developer performs the next step; this is tool preparation,
not a POC verdict or evidence of genuine newcomer usability.

## Phase 09 First Rehearsal Inconclusive: 2026-11-07

The participant's /atom:init attempt stopped because Atom's prescribed bare pip
bootstrap is rejected by Ubuntu's externally managed Python environment.
The intended Go module exists, but no .atom/ initialization or baseline was
captured. The frozen bootstrap reference is unchanged; it lacks explicit Linux
python3 handling and an isolated-install recipe.

The [rehearsal report](phase-09-onboarding-example/poc-report.md) preserves
the supplied excerpt, private recording identity and independent file observations.
Grade Inconclusive under the approved setup-failure rule, not a passing first-use
path or a failing Go baseline. Model identity/usage/active-time and final history
remain unestablished. No venv/pipx workaround, system override or retry was run.

Recommend fixing/validating actual bootstrap guidance before a revised rehearsal;
manual environment preparation is a separately approved alternative with narrower
evidence. Keep final Phase 09 design/implementation and further live spend gated.

## Inconclusive Report Accepted; Bootstrap Repair Scoped: 2026-11-07

The developer selected exactly:
"Accept Inconclusive report; scope the bootstrap-guidance repair".

Accept the first rehearsal's Inconclusive verdict and scope repair of the
canonical and bundled bootstrap guidance rather than a manual workaround.
The observed PEP 668 failure is accepted defect evidence, not proof of a working
isolated installation or of the overall onboarding experience.

Next: prepare the bounded repair/evidence brief, covering Linux interpreter
selection, isolated installation, both command boundaries and preservation of
existing working packages. Its validation conditions and provisioning scope
still need approval; retain the short repair-spec and implementation gates.
No environment location, installation, bootstrap edit, new rehearsal, model
batch, final Phase 09 design or publication is authorized at this gate.

## Phase 09 Bootstrap Evidence Scope Drafted: 2026-11-07

The developer's "lets do it" continues preparation of the promised bounded
bootstrap brief. Reuse the accepted failure; propose one deterministic isolated
command validation before the short repair spec, not an invented Go spike or
unapproved installation. The [brief](phase-09-onboarding-example/bootstrap-repair-brief.md)
awaits run/provisioning approval. Existing first-rehearsal and later gates remain.

## Bounded Bootstrap Validation Approved: 2026-11-08

The developer selected "Approve the bounded Ubuntu validation" at the preceding
brief gate, then requested "continue" on 2026-11-08. The approved source pin remains
50622abf2b9f58bcfc2c9d538b7292cf0689ceee; do not refresh it to today's main.
Fresh read-only checks match the approved Python/Go/default commands, profile
fingerprints and Copilot binaries. The private proof destination remains absent.

Before the timed run, the developer separately selected:
"Approve the named artifact-writer forms for this fixture".
This permits only the proof environment's atom-write-artifact entry point and
equivalent Python module form for the two named findings/decisions fixtures.
It does not reuse the Atom repository's permission or approve a generic editor.

Run only the single private-venv/public-install validation under the brief's
15-minute cap and normal command permissions. No live rehearsal, source edits,
system override, retries, new tool provisioning, spec or publication is approved.
Stop at unexpected failure and present the result before the repair spec.

## Phase 09 Bootstrap Result Gate: 2026-11-08

The approved deterministic validation completed without another installation,
model calls, system override or original-trial changes. Record its bounded
Confirmed result and real failing empty-module baseline in the
[repair report](phase-09-onboarding-example/bootstrap-repair-report.md).
Stop for acceptance before the short repair spec; preserve implementation and
revised-rehearsal gates. No production executor or new enforcement was added.

## Bootstrap Result Accepted; Short Spec Authorized: 2026-11-08

The developer selected exactly:
"Accept the result; proceed to the short repair spec".

Accept the Confirmed result only for the bounded isolated Ubuntu command recipe,
including the honestly failing empty-module baseline and named preservation
checks. The original experienced-user rehearsal remains Inconclusive.

Authorize the short bootstrap-guidance repair spec next, with the final
user-environment boundary and applicable validation made explicit. This is not
approval to edit canonical/package guidance, choose untested material changes,
run another experiment, restart the live rehearsal or publish. The spec still
needs its own implementation gate.

## Phase 09 Bootstrap Repair Spec Drafted: 2026-11-08

The [short repair spec](phase-09-onboarding-example/bootstrap-repair-spec.md)
uses the developer-selected shared user-owned Linux venv, preserves working
installations and Windows opt-in behavior, and scopes canonical/package guidance
plus a small README clarification. The selected prefix was only inspected.
Normal user configuration differs from the proven private environment; a bounded
validation run still needs separate approval. No guide implementation, provisioning,
plugin update, live retry or final Phase 09 design has started.

## Post-Compaction Reference Reload Ordering Deviation

I executed the prepared artifact helper before re-reading AGENTS.md, the discipline
references and the helper after compaction. That reversed the required read-before-work
order. I subsequently reloaded the references, reviewed the helper and the persisted
spec, and verified branch, change scope and preserved evidence. No source guidance or
Ubuntu environment was changed. Further work remains behind the spec approval gate.

Draft verification returned:

```text
checked 458 relative links across markdown files
all relative links resolve
PASS: 10 UTF-8/LF artifacts; 9 numbered behaviors; original trial and evidence hashes unchanged
```

`git diff --check` exited 0. The draft now explicitly places install-scheme checks
before pip installation; this clarification does not claim that those checks have run.

## Phase 09 Bootstrap Spec Approved; Boundary Run Not Approved: 2026-11-09

The developer approved the
[repair spec](phase-09-onboarding-example/bootstrap-repair-spec.md)
and requested a separate
[boundary-validation brief](phase-09-onboarding-example/bootstrap-boundary-brief.md).
The brief is prepared, not executed: one proposed Ubuntu install at the selected
shared prefix with normal user configuration, actual command/writer checks and
a 900-second cap, without models. Run/provisioning and named fixture-writer
approval remain outstanding. No source guide change or original rehearsal retry.

## Normal-Environment Run And Fixture Writers Approved: 2026-11-09

The developer selected exactly:
"Approve the bounded run and named fixture-writer forms".
The [boundary brief](phase-09-onboarding-example/bootstrap-boundary-brief.md) is approved only for its single 900-second Ubuntu
run, isolated provisioning and two named fixture writer forms. Preserve its
source pin, normal-user configuration, stopping rules and separate result gate.
No execution, source guidance edit or original rehearsal retry has occurred.

## Phase 09 Normal-Environment Bootstrap Result: 2026-11-09

The [boundary report](phase-09-onboarding-example/bootstrap-boundary-report.md)
confirms one approved normal-user Ubuntu installation at the selected shared
prefix, both real writer forms, init's honestly failing empty-module baseline
and named preservation/reuse checks in 13.642572425000253 seconds.
No material spec change was needed. Await result acceptance before the approved
three-document repair; original rehearsal remains Inconclusive. No source guide
edits, model calls, retry, cleanup or publication.

## Boundary Result Accepted; Guidance Repair Authorized: 2026-11-09

The developer selected exactly:
"Accept result; proceed with approved guidance repair".
The [bounded result](phase-09-onboarding-example/bootstrap-boundary-report.md) is accepted for its observed Ubuntu conditions.
The existing three-document spec is now authorized for implementation with its
focused checks and unchanged boundaries. No new run, live retry, plugin update,
commit, push or release is approved. Source guides are still unchanged here.

## Phase 09 Bootstrap Documentation Repair Started: 2026-11-09

The developer requested "lets implement". The
[documentation test spec](phase-09-onboarding-example/bootstrap-repair-test-spec.md)
maps the approved nine behaviors before edits, using accepted command evidence
and existing documentation/packaging tests. No Go production RED/GREEN, new
runtime enforcement, new install or original rehearsal retry is implied.

## Phase 09 Bootstrap Guidance Repair Verified: 2026-11-09

The [implementation validation](phase-09-onboarding-example/bootstrap-repair-test-spec.md)
records 34 passing existing tests, semantic review of all nine approved behaviors,
matching canonical/package source bytes and preserved Windows/history blocks.
Only the two bootstrap references and the small README clarification changed
outside specification artifacts. No runtime source, schema, tests or scripts
changed, and no new install/model call/live retry ran.

Await implementation acceptance. Installed plugins/local bundles still need
separately approved delivery; the original experienced-user trial remains
Inconclusive and Phase 09 is not complete.

## Bootstrap Source Repair Accepted; Delivery Still Gated: 2026-11-09

The developer selected exactly:
"Accept documentation repair; keep delivery and rehearsal gated".
Accepted the approved three-document source repair and its recorded evidence:
34 existing tests passed, final 496 Markdown links resolved, mirror parity and
preserved Windows/history/original-trial checks passed. No material spec change.
Installed-plugin/module-bundle delivery and a new frozen live rehearsal remain
separately gated. No publication or Phase 09 completion is implied.

## Phase 09 Candidate Delivery Route Pending: 2026-11-09

Read-only inspection confirms two stale delivery surfaces: installed plugin
instructions and module-local bundles generated from atom-cli package assets.
A plugin-only refresh is insufficient. The installed init interface offers no
bundle-source override; do not use --force to discard approvals as an update.
The original rehearsal remains untouched and Inconclusive.

Recommend scoping an isolated local candidate with both repaired surfaces before
a separately approved new rehearsal; publication first is the alternative.
Delivery/loading/build mechanics and budget still need their own bounded approval.
No install, plugin/bundle mutation, model call, publication or new rehearsal ran.

## Reference Reload Ordering Deviation During Delivery Inspection: 2026-11-09

After compaction, I performed read-only delivery inspection and appended its
findings/route recommendation before re-reading the actual AGENTS.md and
required discipline references. The retained skill text and summary did not
satisfy that explicit reload order. This repeated the earlier ordering error.
I have now re-read AGENTS.md, all seven discipline references and the active
discover SKILL.md, and reviewed the appended phase decisions. No installation,
production edit, publication or live trial occurred. The route and execution
remain unapproved; this record does not retroactively authorize that ordering.

## Phase 09 Isolated Candidate Brief Prepared: 2026-11-09

The developer chose preparation of an isolated local-candidate validation brief,
not execution. See [the draft](phase-09-onboarding-example/candidate-delivery-brief.md).
It proposes separate candidate plugin/package delivery with known provenance,
one 900-second zero-model run and new fixture writer forms. Actual pinned CLI
help supports the proposed metadata commands; loading precedence remains unproven.
No existing installation was changed and no new live trial started. Run approval,
result acceptance and rehearsal approval remain separate.

## Candidate Delivery Run Authorized After Clarification: 2026-11-09

After asking how candidate preparation relates to Phase 09 and receiving that
explanation, the developer replied exactly: "thanks!lets proceed".
Proceed only with the presented [candidate brief](phase-09-onboarding-example/candidate-delivery-brief.md):
one 900-second preparation/validation run, isolated plugin/package/venv/module
and its two named new fixture writer forms. No additional model session, existing
installation refresh, original-attempt retry or publication is authorized.
The bootstrap command-validation adaptation reuses accepted evidence; it does
not fabricate a Go spike or claim this is the live usability rehearsal.

## Phase 09 Local Candidate Route Stopped: 2026-11-09

The approved zero-model [candidate check](phase-09-onboarding-example/candidate-delivery-report.md)
reported installed and external atom entries together, hitting its duplicate-plugin
stop condition. No candidate venv/install/init or new live rehearsal ran. The
installed plugin inventory and named working-installation/default/original-evidence
checks match. Retain the partial candidate; do not retry or patch the installation.
The accepted bootstrap repair still stands. Recommend scoping its normal publication
rather than further isolation work; acceptance/shipping/rehearsal remain gated.

## Candidate Result Accepted; Bootstrap-Fix PR Authorized: 2026-11-09

The developer selected exactly:
"Accept result; commit, push and open the bootstrap-fix PR".
Accept the [stopped candidate result](phase-09-onboarding-example/candidate-delivery-report.md) and its
preservation evidence. No isolation workaround or new experiment is authorized.
Ship the accepted three-source-document bootstrap prerequisite and its supporting
Phase 09 evidence, explicitly not a completed Phase 09 example. No merge, release,
installed-plugin/package refresh or new live rehearsal is authorized.

PR #18 is merged as public main commit 50622abf2b9f58bcfc2c9d538b7292cf0689ceee.
Its tree equals local 4434cdf71b3eaab869f9acf276fa85c1bb9f969c, but their squash
ancestry differs. Create independent fix/ubuntu-atom-bootstrap from origin/main,
carrying the unchanged dirty documentation; preserve the original phase branch.
Do not rebase/amend earlier commits or submit the already-published ancestor diff.

Adapt the ship skill to this accepted documentation-only prerequisite: there is
no root go.mod, so do not claim atom check/Go coverage/race or Phase 09 completion.
Re-run the approved 34 focused checks and document/link/integrity checks now.
Use gh pr create with explicit main base rather than a state-driven phase ship
that would imply the example is complete. Self-review the source and artifact
changes; no additional model-review batch or runtime-code change is involved.
