---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-07"
---

# Phase 09 Decisions

## Explicit Developer Choices

In the discovery interview the developer selected, one question at a time:

- "Summarize a CSV file".
- "Expense totals by category".
- "Build the CLI from scratch with Atom".
- "Following Atom's prompts and gates without reading the full methodology".
- "Me first; record it as an experienced-user rehearsal".

The earlier Linux target and WSL-local Copilot update permission remain scoped:
no setup changes before the Phase 09 brief is approved.

## Recommended Evidence Method, Pending Approval

Use a bounded observed workflow replay rather than a made-up Go parser POC.
The selected uncertainty is human interaction, which a parser spike cannot answer.
This adapts the Go-spike template under the shared evidence-step guidance.
The developer must approve the method and bounds; no technical or human-control
confirmation is claimed. Final Phase 09 spec/implementation gates are preserved,
as are the example's own gates during the rehearsal.

## Proposed Boundaries, Not Prior Approvals

The fixed category,amount fixture, one currency, exact two-decimal totals, negative
refund and visible invalid-amount/missing-file errors are proposed in the brief.
So are a public-marketplace snapshot, one session/attempt and a manually observed
60-minute active-time cap. They are acceptance/spend proposals, not implementation
choices, measured setup times, monetary guarantees or hidden enforcement.

No extra agents, review-model batches, automatic retries, release, commit or push
are approved. Setup/login beyond the stated WSL scope stops for a new decision.
A rehearsal can be Confirmed only for the actual participant and observed path;
newcomer usability and clean-machine installation remain separate work.

## Local Discovery Isolation And Baseline Adaptation

Created the new local branch feat/atom-v1-onboarding-example from verified Phase 03
commit 4434cdf71b3eaab869f9acf276fa85c1bb9f969c after checking the clean worktree and
other worktree ownership. This isolates new discovery artifacts from the published
Phase 03 branch; no remote branch, PR or native stack metadata changed.

The repository root has no go.mod and the tooling is Python. Ran the existing
onboarding/plugin tests as the proportionate untouched baseline: 30 passed.
Did not rerun the known inapplicable root Go gate or claim a full-suite pass.
The new example's initial no-race and final full Go gates remain required once it
exists. Prior Phase 03 outputs are not fresh Phase 09 runtime evidence.

## Draft Gate Status Before Approval

Draft brief produced; no rehearsal or final design authorized yet. No standing
waiver, additional model spend, WSL update or installation. Findings and decisions
are recorded now, not reconstructed after execution.

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

## WSL Update Verification Boundary: 2026-11-07

The developer said "lets do it" after approving the brief. Begin preparation,
not an autonomous substitute for the developer's interactive rehearsal. Ran
only the official copilot update in Ubuntu as the ordinary user; no sudo or
Windows/authentication changes. A root-owned launcher is not itself proof that
the updater needs elevation, so tested the actual approved update command.

The update reported version 1.0.107 downloaded, but the explicit no-auto-update
version probe executed 0.0.403. Treat this as a failed activation/freeze check,
not success. Preserve the actual command evidence and investigate the launcher
read-only; stop before a new installation/elevation or recipe change. No model
calls or approvals have been simulated.

## Stop At CLI Setup Scope Decision: 2026-11-07

Normal and no-auto-update invocations both failed the active-version requirement
after the official updater's download claim. Do not rerun the paid experiment,
raise privileges or silently add a second CLI installation. The internal launcher
cause remains unproven; additional binary reverse engineering is not Phase 09 work.

Recommend a pinned v1.0.107 user-owned rehearsal-tools installation, with an
explicit executable path and unchanged global launcher/PATH/authentication. The
official installer supports PREFIX/VERSION, and the stable release/archive digest
were verified read-only. This is a proposed setup/recipe change, not approval.
The alternative is separately approved privileged repair of the existing launcher.
Await the developer's choice before installation or recipe freeze.

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

## Metadata Preflight Guard Corrected: 2026-11-07

The pinned CLI 1.0.107 legitimately lists included awesome-copilot marketplace
and a disabled built-in browser-use plugin. The initial textual guard expected
old CLI wording "No marketplaces registered" and stopped before any mutation.
This was an overstrict preparation check, not an Atom installation conflict.

The new CLI's list help documents --json. Structured metadata shows only the
isDefault=true awesome-copilot marketplace and source=builtin, enabled=false
browser-use plugin; no user-registered Atom marketplace or installed Atom exists.
Use these explicit fields to distinguish built-in content from conflicting Atom
setup. No built-in plugin is enabled, removed or modified, and no approval/budget
boundary changes. Preserve the rejected textual check and structured follow-up
in session evidence; do not silently turn that failed guard into a successful run.

## Tool Preparation Verified And Recipe Frozen: 2026-11-07

The developer resumed the approved repair with "lets go". The official installer
was inspected, its bytes frozen, and run as the ordinary Ubuntu user with VERSION
v1.0.107 and PREFIX $HOME/.local/atom-phase09-tools. GitHub's release/checksum
metadata matched the Linux archive digest before installation. Installer output:

```text
Installing GitHub Copilot CLI...
Downloading from: https://github.com/github/copilot-cli/releases/download/v1.0.107/copilot-linux-x64.tar.gz
✓ Checksum validated
✓ GitHub Copilot CLI installed to /home/girish/.local/atom-phase09-tools/bin/copilot

Installation complete! Run 'copilot help' to get started.
```

The explicit pinned executable, with --no-auto-update, exited 0:

```text
GitHub Copilot CLI 1.0.107.
Run 'copilot update' to check for updates.
```

Installed CLI binary SHA-256:
985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4.
The old /usr/local/bin/copilot and shell profile fingerprints match the
pre-installation snapshots. No sudo, PATH/profile edit, Go/Python default change,
login or credential copying was performed. Public installer downloads used a
child environment without GitHub token variables; the parent environment was
not changed.

Using that exact CLI, public marketplace addition and plugin installation exited 0:

```text
Marketplace "atom" added successfully.
Plugin "atom" installed successfully. Installed 9 skills.
```

Structured metadata verifies Atom 0.2.0 enabled from marketplace atom, with source
GitHub: girishmotwani/atom. Nine SKILL.md files and three command files were verified;
skill list exposes the twelve Atom entry points. Included awesome-copilot marketplace
and disabled built-in browser-use remain unchanged; they are not Atom duplicates.

The actual installed bundle inventory has 594 files;
its sorted inventory SHA-256 is b31ce534e6ab58627ad6fb623a979c6b9061488f44cb4d1da8090b0d28f725cf.
The CLI metadata does not expose a source commit, so no exact Git commit identity
is claimed. The full per-file inventory is retained in private session evidence.
This public snapshot is not a claim to exercise the unmerged Phase 03 changes.

The terminal recorder was exercised with an unpaid printf marker, not Copilot.
Exit 0 and the marker in both stdout/log verified basic output capture. Child-only
PATH selection resolves the pinned Copilot and leaves Go/Python/git resolution
unchanged; no global shell setting changes. This is not evidence that a real
interactive conversation or all hidden tool output has already been captured.

The [frozen rehearsal recipe](rehearsal-recipe.md) SHA-256 is
69617ba5da1d9f277af92b5e1816058d625e5f57ea0c9d1ef38ec8edd9fb5052. It supersedes the generic-launcher candidate under the approved
user-owned setup amendment and specifies private transcript capture and the
same one-session/attempt, manually observed 60-minute active-effort bound.
No allow-all/autopilot flags, extra agent/model batches or automatic retry.

Authentication/model access is not yet verified; the participant must stop if
the single session asks for login or unsafe permissions. Preparation did not
start an interactive session, create the example module or write Go code.
The user, not this agent or a scripted substitute, performs the rehearsal.
No POC verdict, final Phase 09 design, runtime phase registration, commit, push,
PR or public example completion is claimed.

## Failed First Attempt Preserved; No Silent Workaround: 2026-11-07

The developer pasted the original /atom:init failure, not an approval to override
PEP 668 or install another environment. Confirm the intended Go module and
bootstrap reference read-only; do not initialize the Windows Atom repository,
read external Python implementation, create a module, use --force, or rerun pip.

Preserve the raw recording and supplied excerpt. The first attempt is Inconclusive
because bootstrap failed before the workflow could be evaluated. Do not edit the
frozen recipe or fold a venv/pipx workaround into a supposed successful first run.

Recommend scoping a real bootstrap-guidance repair, using the observed failure
as defect evidence and bounded isolation/reuse validation before the short spec
gate. A manually prepared environment/revised rehearsal is an alternative with
narrower first-use evidence. The [report](poc-report.md) awaits the developer's
result/next-action decision; no repair, new spend or second attempt is approved.

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

## Preparing The Bounded Bootstrap Brief: 2026-11-07

The developer said "lets do it" after selecting the bootstrap-guidance repair.
Proceed with the promised repair/evidence brief, not unapproved provisioning,
implementation or the next live rehearsal.

Reuse the accepted PEP 668 failure and unchanged-tree Python baseline, with
bounded real-command validation for the remaining integration uncertainty.
Adapt the Go-spike template to Python/CLI checks; no algorithm question exists.
The proposed private environment and module are experimental fixtures, not a
decided user-facing install layout. Pin the public source observed now rather
than silently install unmerged local code.

The [repair brief](bootstrap-repair-brief.md) awaits explicit run approval.
Normal permissions and the new fixture's writer approval remain applicable.
Preserve result/spec/implementation gates and first-attempt evidence. No source
change, extra model batch, setup override, retry or publication is authorized.

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

## Bootstrap Result Recorded; Stop Before Spec: 2026-11-08

Executed exactly the approved single isolated command validation after separate
fixture-writer permission. No retries, model calls, global setup changes or source
audit. Keep the proof environment separate from the original expense-summary
module; the first failed trial is not repaired or relabeled.

Grade Confirmed only for the bounded bootstrap command recipe. The recorded
empty-module Go baseline remains failing, as the brief explicitly allowed.
The [repair report](bootstrap-repair-report.md) awaits its result gate; recommend
the short bootstrap spec next, with any changed user-environment boundary checked.
No spec, canonical/package edit, new experiment or live rerun is approved.

The evidence method was command validation, not a generated Go spike; the
private Python observer and outputs are retained, not added to production tools
or presented as an Atom runtime compliance mechanism.

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

## Shared User-Owned Bootstrap Layout Selected: 2026-11-08

The developer selected exactly:
"One user-owned environment outside repositories (recommended)".
The presented location was $HOME/.local/share/atom-cli/venv. Use it as the Linux
default in the short spec, after higher-priority working-package discovery.
This is an installation-layout choice, not approval to create or populate it.

Draft [bootstrap-repair-spec.md](bootstrap-repair-spec.md) for this prerequisite,
not phase-09 design-spec.md: the overall example still has no confirmed rehearsal.
Keep canonical/package guidance aligned and propose only a tightly coupled README
clarification. Adapt the Go API/TDD template to documented command contracts,
semantic review and existing documentation tests; no fabricated Go types or tests.

Normal HOME/pip/Git behavior and the chosen prefix need separately approved bounded
validation before repaired-command claims. Preserve that gate, then documentation
implementation approval. Do not treat source changes as delivery to installed
plugin/local bundles, and do not retry the original first attempt.

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

## Bootstrap Repair Spec Approved; Boundary Brief Prepared: 2026-11-09

The developer selected exactly:
"Approve spec; prepare separate boundary-validation brief".
Recorded the [repair spec](bootstrap-repair-spec.md) as approved, with its normal
HOME/pip/Git evidence condition unchanged. Prepared the separate
[boundary brief](bootstrap-boundary-brief.md) using the existing accepted proof.
No new Ubuntu preflight, environment creation, install, init, writer check or
guide implementation ran. The brief needs explicit run/provisioning approval,
including its new fixture-specific writer forms; existing approvals do not transfer.
Adapted discovery/POC templates to command validation and reused the recorded
Python baseline rather than inventing a Go spike or rerunning unchanged tests.

## Normal-Environment Run And Fixture Writers Approved: 2026-11-09

The developer selected exactly:
"Approve the bounded run and named fixture-writer forms".
The [boundary brief](bootstrap-boundary-brief.md) is approved only for its single 900-second Ubuntu
run, isolated provisioning and two named fixture writer forms. Preserve its
source pin, normal-user configuration, stopping rules and separate result gate.
No execution, source guidance edit or original rehearsal retry has occurred.

## Approved Boundary Run Executed; Result Gate Preserved: 2026-11-09

Executed the [approved brief](bootstrap-boundary-brief.md) once after the
developer requested "lets proeed". Used normal HOME/pip/Git configuration, only
the declared noninteractive/Go/temp controls, one source-pinned install and the
two new fixture-specific writer approvals. No clean-HOME/config override,
unchanged retry, source audit, package overwrite or automatic cleanup.

The [report](bootstrap-boundary-report.md) is Confirmed only for this observed
boundary. Retain the approved command-validation/Go-template adaptation and
existing baseline reuse; no Go algorithm spike or production TDD was fabricated.
Stop for result acceptance before the already approved documentation repair.
No source guide edits, original live retry, model calls or publication occurred.

## Boundary Result Accepted; Guidance Repair Authorized: 2026-11-09

The developer selected exactly:
"Accept result; proceed with approved guidance repair".
The [bounded result](bootstrap-boundary-report.md) is accepted for its observed Ubuntu conditions.
The existing three-document spec is now authorized for implementation with its
focused checks and unchanged boundaries. No new run, live retry, plugin update,
commit, push or release is approved. Source guides are still unchanged here.

## Bootstrap Guidance Implementation Started: 2026-11-09

The developer requested "lets implement" after accepting the boundary report.
Use the [documentation test spec](bootstrap-repair-test-spec.md) to map all nine
approved behaviors before editing. The approved adaptation is factual/semantic
review and existing documentation/packaging tests, not fabricated Go TDD or
new string-presence tests. No runtime source, public interface or state changes
are planned. Retain the three-document source scope and historical evidence.

## Bootstrap Documentation Repair Implemented And Verified: 2026-11-09

Implemented only the three source documents in the approved spec, using its
[test/semantic map](bootstrap-repair-test-spec.md). Kept existing working-package
priority and the Windows opt-in block unchanged; fresh isolated provisioning is
Linux-only rather than an invented native Windows/macOS recipe. Preserved the
canonical moving public URL and its explicit evidence-version limits.

All 34 selected existing tests passed in 8.63s; no tests were added, removed or
weakened. Documentation/packaging checks plus accepted actual command evidence
are the approved adaptation, not a Go TDD/coverage/race claim. No root Go module
exists, and no new atom check, install, experiment or model batch was run.
No material spec behavior changed. Stop at implementation acceptance; no plugin
refresh, live rehearsal retry, commit, push or release is authorized.

## Bootstrap Source Repair Accepted; Delivery Still Gated: 2026-11-09

The developer selected exactly:
"Accept documentation repair; keep delivery and rehearsal gated".
Accepted the approved three-document source repair and its recorded evidence:
34 existing tests passed, final 496 Markdown links resolved, mirror parity and
preserved Windows/history/original-trial checks passed. No material spec change.
Installed-plugin/module-bundle delivery and a new frozen live rehearsal remain
separately gated. No publication or Phase 09 completion is implied.

## Candidate Delivery Route Still Needs A Choice: 2026-11-09

The developer requested "ok. lets continue" after accepting the source repair
while explicitly keeping delivery/rehearsal gated. Investigated the two delivery
surfaces read-only; did not reinterpret continuation as installation, plugin
mutation, publication or permission to restart the original attempt.

Recommend scoping an isolated local candidate that carries the repaired plugin
instructions and package-bundled instructions, preserves the existing working
installation, and verifies the generated bundle before another live trial. Its
exact loading/build commands, collision behavior and budget still need a bounded
brief and approval; current general CLI documentation is not proof of the pinned
Ubuntu loader's behavior. Do not assume live loading overrides an installed plugin.
Alternative: publish the repair first, which needs its own review/shipping and
explicit push/release authorization. No route or provisioning is approved yet.

Reuse accepted command/source evidence for this delivery investigation; no new
Go spike, root Go baseline or unchanged Python test rerun is warranted. The next
question is the developer's local-candidate versus publication preference, not
an automatic experiment. Preserve both the original recipe and recording.

## Reference Reload Ordering Deviation During Delivery Inspection: 2026-11-09

After compaction, I performed read-only delivery inspection and appended its
findings/route recommendation before re-reading the actual AGENTS.md and
required discipline references. The retained skill text and summary did not
satisfy that explicit reload order. This repeated the earlier ordering error.
I have now re-read AGENTS.md, all seven discipline references and the active
discover SKILL.md, and reviewed the appended phase decisions. No installation,
production edit, publication or live trial occurred. The route and execution
remain unapproved; this record does not retroactively authorize that ordering.

## Isolated Candidate Brief Requested: 2026-11-09

The developer selected exactly:
"Prepare an isolated local-candidate validation brief (recommended)".
Prepared [candidate-delivery-brief.md](candidate-delivery-brief.md) only.
Pinned Ubuntu CLI help advertises local --plugin-dir loading and plugin/skill
metadata commands; precedence, collision behavior and generated candidate bundle
bytes still require execution. The brief keeps plugin content-inventory provenance
separate from the Python package's public commit pin and excludes current-branch
runtime code. It permits only bootstrap overlays in new candidate trees.
The draft proposes one 900-second, zero-model run plus new named fixture writer
forms. No provisioning, plugin refresh, install, init, source edit, publication
or live rehearsal occurred. Run/result/rehearsal gates remain separate.

## Candidate Delivery Run Authorized After Clarification: 2026-11-09

After asking how candidate preparation relates to Phase 09 and receiving that
explanation, the developer replied exactly: "thanks!lets proceed".
Proceed only with the presented [candidate brief](candidate-delivery-brief.md):
one 900-second preparation/validation run, isolated plugin/package/venv/module
and its two named new fixture writer forms. No additional model session, existing
installation refresh, original-attempt retry or publication is authorized.
The bootstrap command-validation adaptation reuses accepted evidence; it does
not fabricate a Go spike or claim this is the live usability rehearsal.

## Candidate Run Stopped At Approved Duplicate Condition: 2026-11-09

Executed the approved brief once. Actual local-plugin metadata exposed two enabled
atom identities, so stopped without a workaround, additional skill command,
venv/install/init, fixture writes or automatic retry. See the
[candidate report](candidate-delivery-report.md) for all eleven command streams,
exact timing, source overlays and preservation checks. Retain the partial proof.

The observation refutes this brief's no-duplicate route, not the bootstrap repair
or Copilot runtime correctness. Do not infer skill-selection behavior from a
plugin listing. Recommend scoping normal publication next to avoid turning the
Phase 09 onboarding example into an isolation-tooling project. This is a
recommendation only: result acceptance, shipping authorization and a new live
rehearsal remain separate. No runtime/source production edit was made.

## Candidate Result Accepted; Bootstrap-Fix PR Authorized: 2026-11-09

The developer selected exactly:
"Accept result; commit, push and open the bootstrap-fix PR".
Accept the [stopped candidate result](candidate-delivery-report.md) and its
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

## Continuation Stops At Inherited CI / Merge Decision: 2026-11-09

The developer requested "lets continue." after publication of PR #20. Re-read
AGENTS.md and all seven discipline references. Read the actual atom-status
workflow and loaded pr-stack before preparing the potential landing gate.
Performed only read-only GitHub/local status inspection and existing-run CI
comparison, plus these findings/decision updates through atom-write-artifact.
No model agent, CI rerun, production edit or new Go experiment was needed to
compare existing evidence. The docs-only verification adaptation remains valid.

The six failing CLI jobs match their exact main baseline's failed-test IDs and
aggregate results. See [the findings](findings.md). This is an inherited red
baseline, not passing CI. Keep the bootstrap PR focused: recommend obtaining
explicit permission to land it with that disclosed limitation if normal GitHub
protections allow; do not bypass protections. Fixing inherited CI instead is a
separate scope choice and does not become authorized by this recommendation.

The earlier permission covers commit/push/PR creation only. Generic continuation
does not authorize merge, auto-merge, a protection override, environment refresh,
release or another participant rehearsal. No such action has occurred. These
new CI notes are local pending the next publication decision; do not amend the
published commit. Phase 09 remains blocked on public delivery and a separately
approved, newly frozen user-run attempt. Preserve the original Inconclusive
attempt and the stopped local-candidate evidence.

## CI Evidence Publication And Scoped Merge Authorized: 2026-11-09

The developer selected exactly:
"Publish notes and merge #20 without bypassing protections".
The subsequent "lets continue" resumes that explicit permission. Publish only
these Phase 09 CI evidence/decision updates, then merge the accepted bootstrap
fix if GitHub permits it normally. The inherited failing CI baseline is disclosed
and accepted for this merge, not waived or represented as a passing suite.
No inherited runtime/test repair, release, installed-tool update, new participant
recipe or live rehearsal is authorized.

Fresh read-only preflight confirms PR #20 is standalone, open and non-draft at
4ea0c7ba72b96702ef529270726fc3b433a24978, against unchanged main
50622abf2b9f58bcfc2c9d538b7292cf0689ceee. Main is unprotected, its effective
branch-rules response is empty, and merge/squash/rebase methods are allowed.
No stack creation, rewrite, auto-merge, queue or protection bypass is needed.
Revalidate the pushed head, membership and protections immediately before merge.

Retain the approved documentation-only ship adaptation: this repository's
tooling is Python and this update changes two Markdown journals only. Review
the complete diff and run the existing documentation-link and whitespace checks;
do not manufacture root Go/atom-check evidence or rerun unchanged Python tests
merely to publish CI observations. Preserve the published commit and use a new
notes commit with the required trailers.
