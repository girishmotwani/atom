---
project: "atom-v1-improvements"
date: "2026-11-04"
---

# Findings

## Untouched Baseline

- `atom check --no-race` from `tools` exited 2 with `atom check: No go.mod found in C:\Users\gimotwan\work\atom\tools`; this repository implements Atom in Python, so the Go gate did not run.
- `python -m pytest tests -q --cov=atom` from `tools` completed with 1694 passed, 5 skipped, and 95% total coverage (419.79s).
- At discovery, no Phase 03 model calls or production changes had been made.

## Scope Limit

The approved experiment used 10 calls to test whether two models route four fixed cases consistently under the supplied rubric. It cannot establish universal policy correctness, cover every task type, or replace developer review and approval.

## Phase 03 Policy-Routing POC Confirmed

The [POC report](phase-03-risk-proportionate-workflow-policy/poc-report.md) records 10 successful model calls: two availability probes and eight case responses. `gpt-5.3-codex` and `claude-opus-5.5` agreed on all four route labels, used case facts, returned `developer_decides: true`, and proposed no gate bypass. No developer was simulated: this proves only response wording, not that an actual workflow pauses for or honors a developer decision. This confirms only the fixed rubric/case/model sample; it does not establish universal policy correctness or approve guidance changes.

## Phase 09 Existing Documentation And Linux Environment

The README already contains marketplace installation, prerequisites, an `/atom:init` walkthrough, command choices, and an “Atom is its own worked example” section; `docs/workflow.md` contains a conceptual, not executable, Go example. Phase 09 therefore needs to avoid duplicating the current material and add the requested small standalone Go CLI example. The developer selected Linux and authorized updating Copilot CLI in WSL only after the Phase 09 POC brief is approved. Ubuntu WSL currently has Go 1.22.2 and Python 3.12.3, but Copilot CLI 1.0.5 (below the README's stated minimum 1.0.89) and no Atom plugin. No update or plugin installation has occurred.


## Phase 03 Route Taxonomy Is Unvalidated

The case prompts supplied the exact route labels and definitions. Agreement therefore establishes consistent application of that rubric for four synthetic cases, not that the rubric is complete, correct, or independently derived by the models.

## Resumed Phase 03 Findings

- Recovered the original shell 418 output and corrected transcript omissions without new paid calls. Model answers and the narrow observed verdict are unchanged.
- The disposable harness always exits zero; an incomplete/refuted rerun could be automatically labeled Confirmed by `atom poc run`. Windows descendant termination on timeout is unvalidated. Neither path occurred in the observed run; defer instrument changes to a separately scoped experiment.
- The `build/` ignore pattern also excluded `tools/atom/assets/skills/build/SKILL.md`. Added a narrowly scoped exception so the approved packaged guidance can persist in a fresh clone; no broad build-directory exception.
- Corrected the earlier Python baseline command to `-q` and the failed Go-baseline working directory to `tools`. The earlier counts are historical, not a new verification claim.
- Preserved historical roadmap logs below. They describe the earlier planning state: subsequent toolchain/continuation proof and Phase 03 approval supersede their pending-status statements, not their original evidence limits.
- Phase 09 remains at discovery: Linux and a small CLI example are selected, but exact feature/first outcome and its POC brief still need agreement. No WSL setup or update was performed.

## Historical Roadmap Findings (Preserved From Stash 606d50e)

The following is the original 2026-10-30 record, not current task status.

---
project: "atom-v1-improvements"
phase: "n/a"
date: "2026-10-30"
---

# Findings Log

| Finding | Severity | Where | Why not fixed now | Next action |
|---|---|---|---|---|
| No confirmed project-wide v1.0 POC exists | High | `phase-plan.md`, evidence section | User requested a task roadmap, not a proven architecture | Keep the document proposed; prove each technical assumption before design |
| Exact-toolchain POC was explicitly approved but remains unrun; its brief still has a draft checkbox | Medium | Separate `review-toolchain-policy` worktree | Recording roadmap only | Carry conversation approval accurately into the next POC execution/report |
| Tooling-only review continuation has no reliable classification contract yet | High | Phase 02 of the roadmap | Requires experiment and semantics approval | Do not implement broad error-string bypasses |
| Proposed proportional workflow changes are not existing policy | High | Phases 03-04 | Discussion was not policy approval | Review concrete cases and approve guidance changes explicitly |
| Real-PR context quality remains unproven | High | Phase 12; existing pending validation task | Requires separately approved target access, budget and private answer keys | Keep review claims within current evidence |
| Pages hosting direction is selected but deployment/sample validation is not approved | Medium | Phases 10-11; separate public-search-discovery brief | No public writes requested here | Gate implementation/deployment and do not claim indexing results |
| Existing current checkout has unrelated dirty source and POC changes | Medium | Git status before roadmap creation | Preserve all work not authored for this request | Add only the requested new document directory; use isolated worktrees for implementation |

## Ambiguities Resolved

"v1.0" is a proposed improvement milestone, not an instruction to change package versions or publish. The roadmap includes existing reliability/discoverability requests alongside the discussed workflow improvements. The requested plan contains no references to another skills project.

## Learnings

Separate evidence delivery, technical validation and real-world quality/adoption claims. Each needs its own proof. No general repository rule is changed by recording this distinction here.

## Latest Sequencing

The developer accepted roadmap ordering, then explicitly deferred visibility until after v1.0 product improvements. Website and distribution work no longer block release readiness. Earlier notes about pending hosting/publication approvals remain true but are now deferred, not current product blockers. Visibility artifacts are local-only outside Git worktrees, and existing README/site drafts remain unpublished. The approved exact-toolchain POC is the next engineering action and is still unrun.

## Multi-Model Review Awaiting Triage (Historical): 2026-11-05

The [merged review](phase-03-risk-proportionate-workflow-policy/review.md) completed both approved model reviews within four calls, with no retries. Both models flagged the archived always-zero verdict. One reviewer found conflicting start/spec/build/TDD guidance, omitted required-field/probe validation, and incorrect retry arithmetic (uncapped maximum 51, cap still 48).

A newly established evidence limitation: the harness discarded stderr on successful model calls. The ten printed empty stderr records therefore do not prove empty streams; their historical contents are unavailable and must not be reconstructed. The eight complete response JSON objects still support the narrowly observed routing agreement, but claims that all stderr was captured need correction. Windows process-tree timeout cleanup remains unvalidated.

Staging exposed 57 intentional trailing-whitespace blank lines in the verbatim POC output. Earlier unstaged diff checks did not include untracked artifacts. Preserve the literal transcript and explicitly distinguish that exception from cleanliness checks on all other files; no broader whitespace waiver.

At that review gate no findings were fixed and no commit/push/PR had occurred. Triage was then pending (subsequently approved in decisions.md); proposals and rejected-as-blocker preferences are explicit in the review report.

## Start Routing Repair Verification: 2026-11-05

Review finding 2 is repaired in `com.github.copilot/commands/start.md`. The router now selects the earliest outstanding beat under the approved evidence choice rather than requiring a new spike for every missing POC artifact. Confirmed evidence/approved skips lead to spec; proposed alternatives stop at the evidence-choice gate; regression failure must exist before design; runtime implementation still requires spec approval. Documentation-only work does not invent a Go spike.

Captured validation:

```text
python tools\check_links.py
checked 415 relative links across markdown files
all relative links resolve
```

From `tools`:

```text
python -m pytest tests\test_plugin.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 11 items

tests\test_plugin.py ...........                                         [100%]

============================= 11 passed in 0.62s ==============================
```

`git diff --check -- com.github.copilot/commands/start.md` exited 0 with no whitespace errors (Git emitted a CRLF-to-LF normalization warning). These checks validate links and command discovery, not actual model routing or developer-control behavior. Semantic review confirms alignment with the approved shared policy. Other approved guidance/provenance/harness repairs remain pending; Windows lifecycle validation remains deferred. No commit, push, PR or paid review rerun occurred.


## Remaining Review Repairs Implemented: 2026-11-06

The accepted build/spec/TDD guidance conflicts and packaged copies are repaired. The archived harness now rejects missing/null decision booleans, emits specific rejection diagnostics, requires READY probes, captures successful stderr and exits nonzero for Refuted/Inconclusive. Regression failures exposed each changed behavior before repair; focused GREEN runs passed. Final combined validation is recorded in the repair verification artifact.

Corrected the uncapped maximum to 51 while retaining the approved hard cap of 48 and actual ten-call result. Corrected stale brief/review metadata. Historical successful stderr was discarded and is unknown; original transcript and raw model-review JSON are preserved unchanged. The review findings table and snapshot remain historical, not a review of repaired code.

Still deferred: Windows descendant-process cleanup and wall-clock timeout validation, actual developer-control behavior, taxonomy completeness and repeated/live model quality. No new model calls, paid rerun or installation. Publication remains pending final verification and the applicable completion gate.

## Repair Verification Complete: 2026-11-06

The [repair verification log](phase-03-risk-proportionate-workflow-policy/tdd-log.md) contains actual RED/GREEN and combined gate output. All required archive Go gates passed (build, vet, format, tests and race); 50 selected Python documentation/distribution tests passed. Seven canonical/packaged instruction pairs match after native newline normalization. The historical POC transcript and raw review JSON hashes are unchanged; exactly 57 literal indented transcript blank lines retain the already disclosed whitespace exception.

The initial byte-parity assertion exposed only native CRLF/LF differences, not content drift; the final check compares newline-normalized text. The initial incomplete-result fixture exceeded its one-minute test budget; the corrected three-minute fixture reproduced the intended assertion failure, then passed after the repair. Neither issue establishes a Windows lifecycle guarantee.

Remaining uncertainty is unchanged: Windows descendant/timeout cleanup, live model stability, taxonomy completeness and real developer-control behavior are not proven. There were no new model calls, dependency installs, commits or pushes. The repaired snapshot awaits the completion gate.

## Shipping Boundary: 2026-11-06

The repaired-snapshot completion gate was explicitly approved and the developer renewed the push/PR request. Fresh archive Go and selected documentation/distribution checks passed; their exact output is retained in the phase tdd-log. No new model calls were made.

Open findings remain Windows process-tree/wall-clock timeout validation, actual developer-control behavior, taxonomy completeness and live model stability. They are disclosed limitations, not evidence that these paths were validated. The earlier roadmap and review records are historical; publication does not implement later phases or authorize merging either stack layer.

## Phase 09 Discovery Resumed: 2026-11-07

The developer selected a CSV expense-category totals CLI built from scratch with
Atom. Their main concern is following prompts/gates without the full methodology;
they will first rehearse personally, explicitly as an experienced user. Genuine
newcomer usability and clean-machine installation remain unproven. Historical
WSL version observations have not been refreshed, and no setup or live model
session has occurred.

The [draft replay brief](phase-09-onboarding-example/poc-brief.md) proposes a
bounded observed workflow trial rather than an artificial Go parser spike.
The [phase findings](phase-09-onboarding-example/findings.md) disclose the
published-version/empty-module boundaries and the scoped 30-test local baseline.
Remote full CI remains red; the confirmed Ubuntu failure is inherited from #17
and disclosed in #18. No CI repair is part of this phase.

Earlier Phase 09 notes about an unchosen feature describe the earlier discovery
state. The proposed contract, recipe and rehearsal cap now await approval; this
does not authorize final documentation, Go code, installation or publication.

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

## Phase 09 Linux Preflight Blocker: 2026-11-07

The approved non-elevated Copilot update reported 1.0.107 downloaded, but Ubuntu's
normal launcher still runs 1.0.5 and --no-auto-update runs 0.0.403. Neither meets
the documented minimum. The phase findings preserve the actual command evidence;
this is not a completed rehearsal or evidence of newcomer usability. No plugin,
example module, authentication change or model session has been started.

A pinned user-owned CLI installation with an explicit path is proposed to avoid
changing the root-owned launcher or global defaults. It needs a developer setup
scope decision; no new installation or elevated operation has occurred.

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

## Phase 09 Bootstrap Repair Brief Prepared: 2026-11-07

Read-only Ubuntu checks confirm the missing python alias and available Python 3,
venv and ensurepip. Canonical and bundled bootstrap guides still prescribe the
same failing bare-pip route. No isolated installation has been executed.
The [bounded repair brief](phase-09-onboarding-example/bootstrap-repair-brief.md)
proposes actual helper, artifact-write and first-init validation in a private
disposable setup; it does not restart the original Inconclusive user rehearsal.

## Phase 09 Isolated Bootstrap Validation Confirmed: 2026-11-08

The [bounded report](phase-09-onboarding-example/bootstrap-repair-report.md)
records one public-source venv installation, both helper forms, byte-exact
artifact writes, first init and unchanged known defaults/installations.
The empty module's vet/test baseline failed and was captured; no Go or overall
Phase 09 completion is claimed. The first live rehearsal remains Inconclusive.
Experimental child-environment controls limit reuse claims; no source guidance
change or live rerun has started.

## Phase 09 Bootstrap Repair Spec Drafted: 2026-11-08

The [short repair spec](phase-09-onboarding-example/bootstrap-repair-spec.md)
uses the developer-selected shared user-owned Linux venv, preserves working
installations and Windows opt-in behavior, and scopes canonical/package guidance
plus a small README clarification. The selected prefix was only inspected.
Normal user configuration differs from the proven private environment; a bounded
validation run still needs separate approval. No guide implementation, provisioning,
plugin update, live retry or final Phase 09 design has started.

## Phase 09 Bootstrap Spec Approved; Boundary Run Not Approved: 2026-11-09

The developer approved the
[repair spec](phase-09-onboarding-example/bootstrap-repair-spec.md)
and requested a separate
[boundary-validation brief](phase-09-onboarding-example/bootstrap-boundary-brief.md).
The brief is prepared, not executed: one proposed Ubuntu install at the selected
shared prefix with normal user configuration, actual command/writer checks and
a 900-second cap, without models. Run/provisioning and named fixture-writer
approval remain outstanding. No source guide change or original rehearsal retry.

## Phase 09 Normal-Environment Bootstrap Result: 2026-11-09

The [boundary report](phase-09-onboarding-example/bootstrap-boundary-report.md)
confirms one approved normal-user Ubuntu installation at the selected shared
prefix, both real writer forms, init's honestly failing empty-module baseline
and named preservation/reuse checks in 13.642572425000253 seconds.
No material spec change was needed. Await result acceptance before the approved
three-document repair; original rehearsal remains Inconclusive. No source guide
edits, model calls, retry, cleanup or publication.

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

## Phase 09 Local Candidate Route Stopped: 2026-11-09

The approved zero-model [candidate check](phase-09-onboarding-example/candidate-delivery-report.md)
reported installed and external atom entries together, hitting its duplicate-plugin
stop condition. No candidate venv/install/init or new live rehearsal ran. The
installed plugin inventory and named working-installation/default/original-evidence
checks match. Retain the partial candidate; do not retry or patch the installation.
The accepted bootstrap repair still stands. Recommend scoping its normal publication
rather than further isolation work; acceptance/shipping/rehearsal remain gated.
