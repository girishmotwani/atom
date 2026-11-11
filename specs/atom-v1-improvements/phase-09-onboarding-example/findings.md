---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-07"
---

# Phase 09 Findings

## Usability Is Not Yet Proven

The developer's selected concern is following Atom's prompts and gates without
reading the whole methodology. They chose to perform the first trial themselves,
explicitly as an experienced-user rehearsal. A successful result must not be
reported as evidence that a genuine newcomer understands the workflow.

## Existing Setup Is Not A Clean Machine

Prior findings record Ubuntu WSL with Go 1.22.2, Python 3.12.3, Copilot CLI 1.0.5
and no Atom plugin. Those are historical observations, not fresh version checks.
The current README states Copilot >= 1.0.89, Go >= 1.21 and Python >= 3.10.
No WSL update, installation or live session was performed during this discovery.
The proposed first rehearsal uses a fresh module on that existing environment;
clean-machine, upgrade/uninstall and duplicate-install claims remain untested.

## Existing Documentation And Published-Version Boundary

README.md already contains setup, installation/update commands, onboarding and
command choices; docs/workflow.md remains a conceptual example. The Phase 09 work
must add a verified example rather than copy that material. The proposed public
marketplace rehearsal will test the actual installed snapshot, not unmerged local
Phase 03 guidance or a future Phase 04 shortcut.

An initially empty module may have a failing no-packages baseline. Capture it
honestly if observed; do not prefill a working implementation or silently call it
green. The actual setup/first-run behavior remains part of the unrun replay.

## Baseline And CI Boundary

The local untouched onboarding/plugin suite passed 30 tests. Exact output is in
[the brief](poc-brief.md#untouched-repository-baseline); no root Go gate or Linux
result is claimed. Remote full CI for Phase 03 is not green: the confirmed Ubuntu
failure also occurs on unchanged Phase 02 code, as disclosed in PR #18. This phase
does not repair it or waive it.

## Draft Gate Before Approval

The [replay brief](poc-brief.md) is draft. The proposed CSV/error contract, replay
recipe and spend/effort cap need approval. No Go implementation, final quickstart,
new model calls, provisioning, phase-state registration or publication occurred.

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

## WSL Preflight And CLI Activation Mismatch: 2026-11-07

Read-only Ubuntu checks observed Go 1.22.2, Python 3.12.3, git 2.43.0 and
Copilot CLI 1.0.5. gcc, curl, venv, ensurepip and pip are available. No Atom
plugin or rehearsal directory exists. The launcher at /usr/local/bin/copilot
and its parent are not writable by the ordinary Linux user.

The approved, non-elevated official updater exited 0:

```text
Checking for updates...
Copilot CLI version 1.0.107 downloaded.
```

This is a download result, not a verified active-version update. The follow-up
copilot --no-auto-update --version exited 0 but printed:

```text
GitHub Copilot CLI 0.0.403.
Run 'copilot update' to check for updates.
```

The verification assertion correctly failed. Do not count this setup as ready or
start the paid rehearsal. Marketplaces/plugins report none. No sudo, login,
plugin installation, example files or model session has occurred. Investigate
the launcher/version selection read-only before proposing any material repair.

## Preflight Blocked Before Recipe Freeze: 2026-11-07

A second read-only probe confirmed that the normal launcher still reports
Copilot CLI 1.0.5, while --no-auto-update reports 0.0.403. The known package-cache
platform directory contains only 0.0.403. The launcher is an ELF executable, not
a shell script. These observations do not establish the internal updater cause;
they establish that the claimed 1.0.107 download is not the active CLI.

Both observed active versions are below the README minimum 1.0.89. No plugin,
example module or paid model session has been started. This is a preparation
blocker, not an executed UX trial or a Refuted usability result.

The official installation documentation supports a user-owned custom PREFIX and
an explicit VERSION. Read-only release metadata confirms stable v1.0.107 and the
Linux x64 archive SHA-256 aff04181566f637010a88e68ea145ac1515ec596fae3890d06d81bb8c4be0c4e.

Proposal requiring approval: install this pinned release into a new user-owned
WSL-local rehearsal-tools prefix and invoke its binary explicitly. Leave the
root-owned launcher, shell PATH/profile, Windows tools and authentication alone.
This intentionally adds a separately identified CLI installation; do not mix
its identity with the old launcher or claim a clean-machine installation.
Alternative: explicitly authorize privileged repair of the existing WSL launcher.
No installer, sudo/root operation or path/configuration repair has been performed.

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

## First Rehearsal Blocked By Bootstrap: 2026-11-07

The developer supplied an actual /atom:init trace: entry points and Atom Python
modules were unavailable, and the guide's bare pip installation failed with
externally-managed-environment (PEP 668). Read-only verification confirmed the
rehearsal go.mod and absent .atom/config.json, baseline and local bundle.
The installed bootstrap reference still matches the frozen source inventory.

Step 3 prescribes bare pip rather than an interpreter-matched isolated install;
Step 2 uses python without explicit Linux python3 resolution. The agent did try
python3 and stopped on the failure. This is a bootstrap guidance gap, not an
Atom Go baseline failure or CSV defect. Online-interpreter speculation in the
excerpt has no matching external call; do not treat it as an observed upload.

The [report](poc-report.md) grades the first attempt Inconclusive under the
approved setup-failure rule. Raw terminal evidence is preserved privately.
Selected model, exact usage/active duration and final closed history remain gaps.
No workaround, system override, new attempt, final design or implementation.

## Bootstrap Repair Preflight: 2026-11-07

Read-only Ubuntu inspection reconfirmed Python 3.12.3, no python alias, system
pip 24.0, Go 1.22.2 and git 2.43.0. venv/ensurepip import successfully, but no
isolated install has been executed. The proposed private proof destination is
absent and the ordinary user's home is writable/Linux-native.

Canonical and packaged bootstrap references are byte-identical. The local
manifest declares atom-cli and both executable entry points; its distribution
version must not be confused with installed plugin 0.2.0. Existing onboarding
unit tests substitute Go results, so their passing baseline is not installation
proof. Public main now resolves to 50622abf2b9f58bcfc2c9d538b7292cf0689ceee; this does not
identify the original plugin snapshot's source commit.

The [repair brief](bootstrap-repair-brief.md) proposes one deterministic isolated
command check, not a live-user retry or new bootstrap framework. Only read-only
preflight ran; no venv, pip install, disposable Go module or helper run was created.

## Isolated Bootstrap Commands Confirmed: 2026-11-08

The single approved Ubuntu validation completed: one pinned public install,
both entry-point/module forms, two actual UTF-8 writer round trips and first
init succeeded. atom-cli 0.1.0 and pip 24.0 were installed in the new venv;
WHEEL metadata records setuptools 84.2.1. No installer ran during reuse.
Known Python/pip/Go/git, profile and Copilot fingerprints matched before/after.

The empty module's baseline is explicitly failing: vet/test found no packages;
race was skipped. init persisted that baseline and returned 0. This is a
Confirmed command-bootstrap result, not a passing Go check or completed example.
The [repair report](bootstrap-repair-report.md) carries verbatim commands/results.

The proof used credential-free, proof-local child HOME/temp/cache and disabled
child pip/Git configuration. Custom-environment behavior remains a changed
boundary; check-only reuse does not demonstrate actual model compliance.
No guidance edits, final spec or original-rehearsal retry. The first user trial
remains Inconclusive, with its frozen recipe and raw snapshot retained.

## Final Bootstrap Layout And Evidence Boundary: 2026-11-08

The developer selected one user-owned environment outside repositories after
$HOME/.local/share/atom-cli/venv was proposed. Read-only inspection finds safe
owned/writable .local/share ancestors and no atom-cli/venv destination; nothing
was created there. The accepted proof used a different prefix and private child
HOME/pip/Git controls, so normal-user installation is still an explicit boundary.

README describes plugin installation as the only setup step and presents a
historical three-approval trace. The [repair spec](bootstrap-repair-spec.md)
includes a small clarification/link, not a rewrite of that historical evidence.
It preserves Windows module fallback/opt-in literals required by existing tests.
No source guide change, config audit, installation or new trial has run.

## Normal-Environment Validation Pending: 2026-11-09

The [approved repair spec](bootstrap-repair-spec.md) now has a separately scoped
[boundary brief](bootstrap-boundary-brief.md). The selected shared prefix and
normal user pip/Git context remain untested. The original controlled proof and
Inconclusive rehearsal are unchanged. The new proposal retains its environment
and reports any partial install rather than silently deleting or retrying it.

## Normal-Environment Bootstrap Boundary Confirmed: 2026-11-09

The [boundary report](bootstrap-boundary-report.md) records the approved single
normal-HOME/pip/Git Ubuntu run: one shared venv/install, 34 commands,
22 exit-0 commands and 12 expected absence probes, in
13.642572425000253 elapsed seconds. Both command roles and actual UTF-8
writer round trips passed; metadata and named defaults/installations matched
on check-only reuse. No scheme redirects were present in the checked settings.

The actual empty-module baseline remains failed (vet/test: no packages; initial
race skipped), not a green Go implementation. No new bootstrap defect observed.
The shared venv and disposable proof files are retained. The original rehearsal
remains Inconclusive; result acceptance is still required before guide edits.

## Bootstrap Source Guidance Repaired; Delivery Still Pending: 2026-11-09

The [implementation validation](bootstrap-repair-test-spec.md) records 34 passing
existing tests and a direct nine-behavior semantic review. Canonical and packaged
bootstrap references are byte-identical, preserve Windows's existing opt-in and
replace bare system-pip installation with the approved Linux isolated route.
README now distinguishes plugin instructions from Python commands and qualifies
the historical approval count without rewriting its table.

No new implementation findings. Source changes have not updated the installed
plugin or already-onboarded module bundles. Candidate delivery/refresh and a new
frozen live rehearsal still require separate approval; the first attempt remains
Inconclusive. No claim that Phase 09 or the expense CLI is complete.

## Candidate Delivery Has Two Instruction Surfaces: 2026-11-09

Read-only Ubuntu checks found the installed plugin bootstrap and both named
bootstrap-proof modules' generated local bootstrap references still at SHA-256
e561e9ed5e114dd889b438e5c0c37c4ea6e64561831b1c4678b03288b4d8fa56.
The accepted repaired source is SHA-256
ce34395eea5d7049b9ab23a594227a916afae28857ae3b873dac31255f387b3e.
The original rehearsal module still has no .atom/ directory.

Atom's own tools/atom/onboarding.py:16,125-145 sources the generated bundle from
the installed atom-cli package assets, not the Copilot plugin. Consequently,
refreshing only the plugin reference would leave subsequent module-local
instructions stale. This is a delivery gap, not another runtime/source defect.
Do not fix it by editing generated bundles or an existing working package blindly.

Actual installed public command help (exit 0):

```text
usage: atom init [-h] [--module MODULE_PATH] [--force]

Capture the baseline and install Atom's complete project scaffold. A valid
matching repeat is a read-only no-op; conflicting or incomplete setup is
refused without changes.

options:
  -h, --help            show this help message and exit
  --module MODULE_PATH  The Go module path this project builds; defaults to
                        go.mod.
  --force               Re-initialise deliberately, discarding recorded
                        approvals.
```

There is no bundle-source override in that interface. --force is not an update
shortcut: its documented effect discards recorded approvals. No delivery, install,
init, model call or new live rehearsal ran during these read-only checks.

## Local Candidate Listed Alongside Installed Atom: 2026-11-09

The [candidate-delivery run](candidate-delivery-report.md) is Refuted for its
no-duplicate criterion. Pinned CLI 1.0.107 plugin-list metadata reported both
installed atom@atom and external atom enabled at version 0.2.0. Stop occurred
before venv creation, installation, module initialization or fixture writers.
This does not prove runtime precedence or invalidate the bootstrap text repair.
All eleven native commands exited zero; the observer stopped with exit 2.
The original full plugin inventory and named working-installation/default/original
trial checks match. No model request or new live rehearsal ran.

## Public Snapshot Provenance Clarified Before Shipping: 2026-11-09

The candidate run's complete 594-file public-commit inventory exactly matches
the original frozen installed-plugin inventory. GitHub confirms PR #18 merged
on 2026-11-06 as 50622abf2b9f58bcfc2c9d538b7292cf0689ceee. Earlier references
to "unmerged Phase 03" are historical scope cautions, not evidence that the
installed snapshot excluded those changes. No runtime use or compliance follows
from content equality. Preserve the frozen original recipe and observations.

## PR #20 CI Compared With Its Exact Main Baseline: 2026-11-09

PR #20 remains open and unmerged at
4ea0c7ba72b96702ef529270726fc3b433a24978, targeting main. GitHub reports
MERGEABLE but UNSTABLE, with no submitted reviews. Documentation links and
all three POC jobs passed; all six Python/OS CLI jobs failed. CI is not green.

Read-only evidence retrieval, both exit 0:

```text
gh run view 42641915538 --repo girishmotwani/atom --log-failed
gh run view 42217217981 --repo girishmotwani/atom --log-failed
```

The [PR run](https://github.com/girishmotwani/atom/actions/runs/42641915538)
is compared against the [main push run](https://github.com/girishmotwani/atom/actions/runs/42217217981)
at its exact base 50622abf2b9f58bcfc2c9d538b7292cf0689ceee. Every matrix
cell has exactly the same failed-test identity set and passed/failed/skipped
counts. No newly failing test identity was observed. This comparison uses
existing runs, not a rerun or a claim that the suite passes.

Verbatim final pytest summaries, base followed by PR:

```text
atom CLI (py3.10, macos-latest)
BASE: ================= 15 failed, 1632 passed, 52 skipped in 45.87s =================
PR:   ================= 15 failed, 1632 passed, 52 skipped in 57.61s =================

atom CLI (py3.10, ubuntu-latest)
BASE: ================= 1 failed, 1646 passed, 52 skipped in 44.33s ==================
PR:   ================= 1 failed, 1646 passed, 52 skipped in 35.53s ==================

atom CLI (py3.10, windows-latest)
BASE: =========== 21 failed, 1676 passed, 2 skipped in 130.14s (0:02:10) ============
PR:   ============ 21 failed, 1676 passed, 2 skipped in 91.66s (0:01:31) ============

atom CLI (py3.12, macos-latest)
BASE: ================= 15 failed, 1632 passed, 52 skipped in 53.68s =================
PR:   ============ 15 failed, 1632 passed, 52 skipped in 74.07s (0:01:14) ============

atom CLI (py3.12, ubuntu-latest)
BASE: ================= 1 failed, 1646 passed, 52 skipped in 42.25s ==================
PR:   ================= 1 failed, 1646 passed, 52 skipped in 31.63s ==================

atom CLI (py3.12, windows-latest)
BASE: =========== 15 failed, 1682 passed, 2 skipped in 143.53s (0:02:23) ============
PR:   =========== 15 failed, 1682 passed, 2 skipped in 139.44s (0:02:19) ============

```

The shared Ubuntu failure is:

```text
atom.review.ControlToolchainError: PATH Go 1.23.12 is below module minimum 1.27.0
```

macOS and Windows also expose path-alias comparisons; Windows Python 3.10
has additional runner/process test failures. Do not repair these inherited
runtime/test issues within the accepted documentation-only bootstrap scope
without a separate scope decision. Matching failed-test sets alone do not
establish that every failure has the same root cause or rule out hidden defects.

`atom status` exits 0 but warns about multiple specs projects and selects
artifact-writer/phase-01-dedicated-writer by fallback, not this active Phase 09.
Its unrelated missing-artifact report is not Phase 09 completion evidence.
No runtime state or unrelated project artifact was changed. The actual Phase 09
files retain its brief and Inconclusive report, findings and decisions; an
approved expense-example design, implementation and successful live rehearsal
are still missing.

## Public Fix Is Merged; Ubuntu Instructions Still Old: 2026-11-09

PR #20 merged normally as ec605a715f53db93abd54d6e88f887cf20525940.
Its public canonical and packaged bootstrap hashes match the accepted repair.
The later notes-head CI comparison also matched all six baseline failed-test
sets; this remains a failing full suite, not a Phase 09 completion claim.

Fresh read-only Ubuntu inspection confirms pinned Copilot 1.0.107 and a single
enabled installed atom@atom 0.2.0. Its plugin bootstrap and the existing shared
atom-cli 0.1.0 package asset both remain at SHA-256
e561e9ed5e114dd889b438e5c0c37c4ea6e64561831b1c4678b03288b4d8fa56.
The package still records source commit
50622abf2b9f58bcfc2c9d538b7292cf0689ceee. Nothing was refreshed.

Actual pinned CLI help, exit 0:

```text
Usage: copilot plugin update [OPTIONS] [name]

Update a plugin to the latest version, or update all installed plugins.

Fetches and installs the latest version of previously installed plugins.
```

The named form accepts plugin-name@marketplace-name. A successful update
message or unchanged version number alone will not prove repaired content
was delivered; verify actual source/content. No external duplicate plugin,
manual installed-file patch, forced module init or original-trial retry is
proposed. The remaining gap is delivery to these two existing instruction
surfaces, followed by a separately gated user-run workflow rehearsal.

## Public Ubuntu Delivery Verified: 2026-11-10

The [public delivery report](public-delivery-report.md) records the approved
named plugin update and pinned existing-venv package refresh, each once, in
16.81284103100188 seconds. All 607 installed plugin source files
match the merged commit; plugin and packaged bootstrap hashes match the accepted
repair. Both entry points and module help forms passed. All 20 commands are
accounted for: 10 exit 0 and 10 expected pip missing-key diagnostics.

The updater reports v0.2.0 "already at latest" while delivering the repaired
content; atom-cli also retains version 0.1.0. Version labels alone are not update
evidence. Named installation/default/original-trial preservation checks match,
and non-Atom distribution versions are unchanged. No new source defect found.

The package asset is repaired, but no new module/init or generated instruction
bundle was exercised in this maintenance run. Existing generated bundles were
not changed. No live rehearsal occurred; the original trial remains Inconclusive.
The remaining Phase 09 question is the user-run workflow, not more installation
mechanics. A new prepared-environment recipe and live attempt remain gated.

## Prepared Rehearsal Recipe Ready For Its Start Gate: 2026-11-10

The developer accepted the delivery result. The [new recipe](prepared-rehearsal-recipe.md)
discloses the repaired preinstalled plugin/CLI and uses separate module/evidence
paths. Read-only inspection verified current tooling/source and absent targets.
No new preparation defect found. No module/init or live session was launched.
The original attempt and recipe remain unchanged. Actual model access, new-module
bundle generation and workflow usability still need the user-run attempt.

## Prepared Attempt Stopped At A Manual Permission Request: 2026-11-10

The [prepared rehearsal report](prepared-rehearsal-report.md) is Inconclusive:
the developer stopped before a useful CLI result or completed onboarding. Exact
session events show the ownership-check permission requested at
2026-11-10T10:42:31.621Z and cancelled at 2026-11-10T10:46:08.992Z with
reason "Session aborted". No execution result exists for that command, and
no atom init call is recorded. This was not an observed Python/ownership error.

Read-only diagnosis from the new module confirms safe owned venv ancestors and
exit 0 from both existing venv module help forms. No config, baseline, bundle or
managed instructions exist yet. Earlier PATH/system-Python failures were expected
fallback probes, not proof the prepared package was missing. No source repair or
reinstallation is indicated. The participant subsequently selected exactly:
"I saw the permission prompt". Prompt visibility is confirmed by their report;
understanding and the reason approval did not complete remain unestablished.
Do not infer a UI defect from event timing or treat this answer as retry approval.
## Existing Rehearsal Handed Back As An Assisted Continuation: 2026-11-10

The developer requested continuation after the outside diagnosis. The frozen
recipe and pinned CLI binary remain unchanged; the saved session and original
recording exist, the separate continuation capture is unused, and the five named
onboarding files remain absent. No new installation defect found. Actual pinned
CLI help supports resuming the exact existing session. No model session or init
was launched by this observer. Further user-run work is assisted evidence, not
an independent confirmation of the frozen recipe's no-outside-coaching question.
The original remaining active-effort cap and all example gates remain in force.

## Participant Requested Prerequisite Prompts Instead Of Expected Failures: 2026-11-10

The developer said exactly: "I think we should simplify the flow by prompting
the user to install the relevant tools instead of showing failures".
The current bootstrap begins with bare entry-point help calls, then module help
calls, before checking the known Linux venv. These expected absence diagnostics
can look like broken onboarding. Step 4 already requires install consent; the
missing UX distinction is absence versus hidden or broken existing tooling.

This rehearsal's tools were already installed and healthy outside PATH. Asking
to reinstall them would misdiagnose the observed case. A clearer prerequisite
flow should reuse healthy installations, ask before installing actually absent
tools, and retain real execution failures rather than hiding them. Scope remains
to be clarified: general onboarding or only the example quickstart. No changed
flow or new participant outcome has been proven by this feedback. The frozen
recipe and installed rehearsal source remain unchanged by this discussion.

## Assisted Continuation Has A Persisted Onboarding Receipt: 2026-11-10

The participant supplied completed-init output. Read-only inspection of go.mod
and the five named Ubuntu onboarding files confirms the module/config commands,
local relative instruction link, generated manifest and managed ignore entries.
The baseline is persisted with exit_code 1 and passed=false: build/fmt passed,
vet/test failed because there are no Go packages, race skipped for the initial
baseline. Do not turn this into a green Go implementation or rerun init to hide it.
The prepared report retains the actual receipt and failing baseline verbatim.

The transcript also shows bootstrap friction: a premature unestablished module
command, a wrong reference-path read, repeated expected-absence probes and head
pipelines that can mask exit codes/truncate diagnostics. It does not show the
prescribed venv ancestor validation or all required post-init file reads. Earlier
observer ownership checks and the new receipt reads must not be credited as
independent participant-agent compliance. No unsafe path or broken installation
was observed. This is an instruction-following/UX finding, not evidence that the
installation is missing or that the whole workflow is confirmed.

The developer selected "General /atom:init onboarding" for the prerequisite UX
change. Scope is now clarified; implementation and evidence choice remain gated.
No general onboarding changes have been applied to the frozen rehearsal source.

## Namespaced Start Handoff Rejected Despite Skill Discovery: 2026-11-10

The developer reported "atom:start is unknown command". This observer had
recommended /atom:start without verifying that interactive alias. Read-only
pinned CLI plugin/skill lists exit 0: atom@atom 0.2.0 is installed and start and
discover are both discovered plugin skills. The canonical start command file also
exists. Neither installation inventory nor skill discovery proves that exact
slash invocation works in the participant's active session. Precise rejection
cause remains unknown without the actual UI input/error or registration evidence.

Do not repair this with a blind reinstall, update, guessed alternate slash name,
or a changed frozen recipe. A plain-language request to invoke the listed start
skill is the minimal assisted handoff; success has not yet been observed. Preserve
this as a concrete quickstart/command-surface finding, not participant confusion
or confirmation that the original recipe can be followed as written.

## Plain-Language Start Request Substituted Discover: 2026-11-10

The participant's next excerpt shows skill(discover) after requesting start in
ordinary language. Discovery has been reached, but start invocation and the
reported rejected slash command remain unverified. The excerpt ends with an
atom check --no-race request and no result. The saved empty-module baseline is
already known to fail vet/test for no packages; do not describe it as clean or
credit an uncompleted check as passing. No new installation defect is observed.

## Draft Brief And Discovery Completion Do Not Satisfy The POC Gate: 2026-11-10

The supplied excerpt shows a generic Create for specs/poc-brief.md rather than
the guarded writer, an invalid question-tool request, a subsequent multi-field
clarification and a completion summary without an explicit brief-approval question.
Read-only inspection confirms the draft describes the whole CLI feature checklist,
not one risky unknown, and lacks bounded execution/evaluation details. Its manual-
spreadsheet/shell-workflow claim differs from the stated learning example. Exact
clarification choices remain partly unavailable; do not assume their approval.

The summary adds "100% test coverage" while the actual saved criterion is only
tests for the happy path and each failure case. The numeric target is not supported
by the original recipe or saved artifact. Both named companion journal paths,
specs/findings.md and specs/decisions.md, are absent alongside the brief. The draft's
existence and prior clarification answers do not constitute approval to run a POC.
Return to the brief gate or stop the assisted rehearsal; do not silently repair,
run a spike, manufacture a green baseline or count this as successful adherence.

## Invalid Writer Probe And Arithmetic Claims Need Clarification: 2026-11-10

The participant explicitly chose float64 and standard rounding. A bounded POC
must test that candidate against independent expected cent totals, not claim all
cases are exact merely because output has two decimals. Preserve the original
input precision requirements; clarify any proposed relaxation before approval.
The offered decimal.Decimal option is not a Go standard-library package.

The agent invoked the guarded writer on /dev/null through a head pipeline and
continued after two collapsed output lines. That target is outside the writer's
allowed artifact paths; exact refusal/error remains unobserved, and the pipeline
can conceal its status. Obtain the actual diagnostic and honor any refusal stop.
Subsequent temporary-file staging and a still-pending decisions.md operation do
not establish either final artifact success or an alternate-tool bypass.

## Revised Gate Is Visible But Precision Claims And Writer Evidence Remain Open: 2026-11-10

The three named revised artifacts under poc/ now exist and the participant agent
asks approval and waits. The function-only six-case experiment does not establish
exact expense aggregation, and a literal Go 0.1 + 0.2 can be constant-folded rather
than exercising runtime addition. The saved float64 sufficiency claim is unproven;
no dependency or universal precision guarantee follows. Journals omit the earlier
generic-write and invalid-target-probe issues, and the canonical specs/ brief
needs reconciliation with the new poc/ revision before downstream use.

The requested two writer-probe output lines are still absent. The previously
identified session and four logs in the named rehearsal capture directory do
not contain that probe; their last logged activity does not establish the current
session. This is an evidence/identity gap, not proof the participant fabricated
execution or changed tools. Obtain the active session ID and inspect only its
relevant result; no broad private-history scan or invalid probe replay.

## Active Session Used CLI 1.0.5; Writer Refusal Was Masked: 2026-11-10

The participant identified session 1c8557f2-0e15-49fd-a35b-2c094364572f. Its start
metadata reports copilotVersion 1.0.5 at 11:23:46.812Z in the target module. The
original session reports 1.0.107, and the existing pinned executable still reports
1.0.107 with updates disabled. This materially differs from the frozen client/
one-session conditions. Earlier pinned-client skill discovery did not establish
the active older client's command surface. Exact start-command rejection cause,
launcher selection and any model effect remain unproven.

The actual writer probe returned refused /dev/null (outside-repository), while
the head-ended pipeline displayed exit 0. The guard held, but the agent ignored
the required stop and continued. The next three artifact writes genuinely used
the guarded writer and succeeded; they were not generic-editor substitutions.
Both that positive evidence and the procedural violation must remain explicit.
No runtime guard escape is established. Hold the POC gate and preserve the record;
no automatic reinstall, restart, source change or new independent trial.

## Rehearsal Stopped And Assessed: 2026-11-10

The developer selected "Stop and assess the rehearsal findings". Overall result
for the approved prepared attempt remains Inconclusive: the client/session changed
and the path required outside coaching; no tested expense CLI, negative checks or
final full Go gate were established. Concrete entry-flow and instruction-following
failures are still useful evidence, not a passing rehearsal or general claim
about every Atom user/model. Active-effort and usage totals remain unestablished.

Positive evidence must also survive: the venv works, first-init receipts exist,
the failing empty-module baseline is honestly recorded, the writer guard refused
its invalid target, three subsequent guarded writes succeeded, and the last brief
was presented at an actual wait-for-approval gate. No guard escape was observed.
The current pending spike is not approved by stopping or accepting this assessment.

Prioritize a scoped general onboarding prerequisite/client/handoff repair before
another live attempt; preserve writer-stop and gate findings as requirements and
validation concerns. Neither instructions alone nor fixing only a rounding helper
proves the broader flow repaired. No repair or further run is authorized yet.

## General Onboarding Repair Scoped Before Implementation: 2026-11-10

The developer requested a repair with issue/approach summary first. Source review
confirms bootstrap starts by invoking entry points and module forms before finding
the known venv; init delegates these critical details to the reference. README
already distinguishes plugin/Python commands and has a documented client minimum,
but some onboarding/manual-install wording assumes discovery/installation steps
rather than an explicit prerequisite decision. Keep historical approval ledgers
historical. Existing tests cover asset parity, command literals, Windows setup-path
and manifest/file namespace contracts; they do not prove active interactive alias
acceptance or agent adherence. The prior namespace POC is explicitly limited to
its client/setup and does not settle the observed older client's rejection.

Recommend a five-minute, no-model, no-install discovery-boundary check in the two
existing environments, reusing accepted install evidence and recorded failures.
No shipped guidance or stopped participant environment has changed. A new named
repair brief distinguishes this proposal from the prior approved bootstrap spec
and still-unproven final Phase 09 expense example.

## Availability-First Discovery Boundary Observed: 2026-11-10

After explicit approval, two non-installing observer invocations established both
command roles without running any known-missing Atom command/module. Windows
entry points both returned help exit 0. Ubuntu presence queries established both
PATH entries absent and system-Python Atom absent; six safe ancestor checks and
a prefix/package query preceded the healthy known-venv module helps, both exit 0.
The new prerequisite-flow-repair-report.md contains the full original receipts.
No diagnostics were truncated, no provisioning ran and no participant files were
written. Active-client identity, actual failure-path handling and agent adherence
were not newly exercised. These limits prevent calling this a complete onboarding
repair or a successful final Phase 09 rehearsal.

## Repair Spec Drafted After Accepted Discovery Evidence: 2026-11-10

The developer accepted the discovery report before spec drafting. The scoped spec
retains observed versus assumed facts and makes no live-repair claim. Main init
and shared bootstrap need consistent availability-first ordering, active-session
identity, explicit missing-tool consent, two retained forms and real-error stops.
README's current automatic-install wording and generic approval-count narrative
need qualification, while historical ledgers stay unchanged. Native-platform
manual-install redesign and new command aliases are outside scope. Failure-path
adherence still needs observed evidence before any compliance claim.

## General Onboarding Guidance Repair Implemented Locally: 2026-11-10

The approved five-file repair is implemented and its validation artifact preserves
34 passing focused tests, four passing final documentation cases, two byte-identical
packaged pairs, 531 resolving relative links and clean whitespace/scope checks.
All fourteen instruction behaviors were semantically reviewed; no runtime behavior,
tests or installer changed. No claim is made that this proves agent compliance.
The original manual platform-install recipes remain unchanged, not newly validated;
future platform/installer work requires separate scope. Existing installed plugins
and module bundles still contain their prior delivered content. Do not retry the
stopped rehearsal expecting local source edits to have updated those installations.

## Deferred Single-Source Skill Packaging Repair: Issue #22

The developer asked why skill mirrors exist under tools and requested a repair
issue for later rather than implementation. Verified tools\pyproject.toml bundles
assets/**/* and tools\atom\onboarding.py loads those resources through
importlib.resources, then copies AGENTS.md/skills into the self-contained target
bundle. The package resources and target snapshots are required delivery copies;
a second human-maintained source tree is the avoidable duplication.

Created and read back https://github.com/girishmotwani/atom/issues/22,
"Repair: generate packaged skill assets from one canonical source". It proposes
canonical root authoring and build-generated package resources, with an explicit
proof obligation for wheel, sdist, wheel-from-sdist, clean installed resources,
editable development and additions/deletions. The tools subdirectory build context
and existing #subdirectory=tools VCS URL are important compatibility boundaries.
No particular build hook is proven or approved. Current mirrors remain intact.
## Pre-PR Review Boundary And Remaining Validation Limits

The approved repair is entering one independent review per developer-selected
model: claude-opus-5.5 and gpt-6.1-terra, neither the author gpt-6.1-sol. Findings
are pending, not a clean-review claim. The standard runner adds model ping probes,
so the explicitly approved alternative uses exactly two read-only reviewer agents
without probes, extra agents or retries. No runtime review-runner repair is in
scope. Its existing behavior is an execution-boundary constraint, not a new
onboarding defect or permission to broaden this patch.

Current SHA-256 receipts retain both accepted canonical/package pair hashes;
README is frozen as 76935B30C29D1AA1BB88A6CC1DC9136EDD8CC9246AE1C22C9A075E238906E5E7.
Whitespace checks exit 0. Existing focused documentation/Python test evidence is
reused, not represented as a newly run suite or root Go gate. The stopped live
rehearsal and its unproven client/error/adherence paths remain unchanged.
## Bounded Pre-PR Review Returned Two Findings; Triage Pending

prerequisite-flow-repair-review.md preserves both original model responses and
the merged findings. Both selected reviewers returned; exactly two reviewer
agents were invoked, without probes, retries, extra model turns or source edits.

Major: README.md:602-609 still promises automatic installation in Run It despite
spec behavior 14. Both reviewers found the promise (2/2; severity differed);
Opus also flagged the adjacent unqualified start handoff (1/2). Parent targeted
reads confirm the missed paragraph. This is an incomplete directly coupled
repair, not permission to redesign manual platform recipes. No fix is applied.

Minor: canonical/bootstrap packaged copies at lines 84-90 use a generic top-level
atom presence signal that can match a colliding package or namespace. Opus alone
reported this (1/2). It has not been reproduced; desired collision/error routing
needs a decision before changing the approved query or weakening safe stops.

Review-completion limitation: Opus explicitly did not read the full README or
discovery report. Terra reported full requested context. Do not mark the full-
context-per-reviewer checklist complete, silently credit author verification as
an independent pass, or spend beyond the approved two-invocation budget. The
review awaits developer triage, with no fixes, publication, refresh or rehearsal.
## README Major Finding Locally Fixed; Minor And Review Coverage Still Open

Under the developer's explicit fix approval, corrected Run It tooling consent,
healthy-tool reuse and available discovery/start handoffs. Qualified the directly
coupled certainty/routing conclusion, preserving historical experiment numbers
and the ledger. README SHA-256 is now
1390ECFC411EB065CEA74FC41383EFA5DBA611B79E6AE47DBA3DE6F5C369B5D1.
The existing README documentation case passed (1 passed in 5.40s); 535 links resolve
and git diff --check exits 0. Exact output is in the validation artifact.

The Major is locally fixed, not independently re-reviewed. The Minor collision
finding remains open and unexecuted; no bootstrap/package detection text changed.
Opus's full-context gap is still open, and no new model invocation was made.
The review report proposes a separately gated, five-minute/two-command local
Python collision check with temporary fixtures and no installs or model calls.
No new detector design/implementation, refresh, publication or rehearsal follows
from the README fix approval. Overall review/Phase 09 completion is not claimed.
## Package-Name Collision Reproduced In Approved Bounded Local Check

The approved five-minute/two-probe-command check used one terminal invocation,
finishing in 0.023066100024152547 seconds. Both controlled layouts (namespace-only
atom and a synthetic unrelated atom package) return top-level presence True but
have no own CLI/writer modules or atom-cli distribution. The existing-install
positive control resolves both role modules and the distribution. No package
was imported, no missing help was executed and no installs/models/participant
writes occurred. Fixtures were removed; the process search path was restored.
The review report preserves the complete captured JSON receipts.

This confirms only a name-discrimination gap, not live Linux fallback behavior,
a universal metadata-based replacement or intended collision handling. The Minor
remains open for a scoped repair/deferral decision; no bootstrap source changed.
Retain safe import-error/partial-install stops and working editable/module forms.
Opus's review-context gap and post-fix review remain separately open; no new model
invocation or broad Phase 09 completion is implied by these Python observations.
## Detection Repair Spec Drafted; Read-Only Ambiguity Policy Needs Approval

Accepted collision evidence supports replacing generic-name-only detection, but
not distribution-only identity, arbitrary importer support or automatic absence
classification. The new package-detection-repair-spec.md records expected role
candidates, metadata, explicit ambiguity and preserved partial/error stops.
It proposes read-only reuse of the single known safe Linux venv from ambiguity
only when neither role is verified. That is a deliberate narrow change to the
old Step 3 absence prerequisite, not a measured runtime result or install waiver.
If no healthy known venv exists, ambiguity still stops for developer resolution.

Source-only/editable/mixed routing and custom-loader limits require the stated
boundary validation before shipped edits; no such new validation ran while
writing this draft. Main init/README already delegate the right policy and are
outside these two planned reference edits. Prior partial review coverage, no
post-fix independent README pass and the stopped Inconclusive rehearsal remain
open. No model call, source edit, install or publishing action occurred.
## Detection Guidance Repair Implemented And Locally Validated

The approved canonical/bootstrap packaged references now distinguish own metadata,
module candidates, ordinary absence and same-name ambiguity. Partial/verified
unresolved roles stop, source-only/mixed candidates retain actual help checks,
and ambiguity permits only read-only known-venv reuse, never installation. Query
exceptions and actual help failures retain stop rules. Both reference files have
SHA-256 1A2211645E8981D735C6C99E0C78D11E38437A5168B66B3367E8DBF90B06E96E.
README and both init hashes are unchanged.

Ten pre-edit candidate observations matched; the actual rendered query matched
and executed in the second probe. The combined window was 37.654308 seconds, with
no atom import, missing help, model call or installation. Fixtures were removed
and process sys.path restored. Fourteen existing documentation/plugin cases pass.
The named validation artifact preserves actual outputs and all twelve claim checks.

The Minor is locally addressed, not independently re-reviewed or accepted as live
Linux/agent proof. Custom-loader/editable variants, actual metadata/help-error
routing and the new live ambiguity-to-venv path remain unexercised. Existing model
context and post-fix review gaps remain open, with no reviewer budget left. No
publication, installed-content refresh or rehearsal ran; Phase 09 is incomplete.
## Final-Persistence Instruction Reload Order

The post-compaction evidence-persistence continuation relied on the handoff before
reloading the actual required instructions. Recorded the deviation in decisions.md
and completed the actual instruction/spec/mapping/final-reference reads before
the acceptance gate. No shipped edit or new experiment occurred during the lapse.
This is a process deviation, not a passing compliance claim or a new runtime fix.
## Local Detection Repair Accepted; Remaining Gaps Preserved

The developer accepted the bounded local repair with the explicit selection
"Accept the local detection repair; keep further work gated". The package-name
collision finding is locally addressed/accepted. Original independent-review
coverage gaps, post-fix review and unexercised live Linux/agent behavior remain
open. Acceptance does not complete Phase 09 or authorize delivery/refresh/rehearsal.
## Post-Fix Independent Review Gap Being Addressed

The developer approved a fresh two-agent post-fix review, one read-only invocation
each with claude-opus-5.5 and gpt-6.1-terra. Reviewers must cover the current five
shipped files with complete applicable spec/evidence context. The prior review
remains partial historical evidence; it is not retroactively made complete.
No reviewer has returned for this new snapshot yet. Further work remains gated.
## Post-Fix Review Returned Two Minor Findings

Both approved independent reviewers returned with full required context reported;
mirrors and frozen hashes match. No Blocker/Major was reported. Opus found the
README blanket installation-question promise at 482-483 (related wording 25/603/
673), which overstates the Linux-only Atom installation recipe and system-tool
supply requirement. Parent targeted reads confirm the directly coupled mismatch.
Terra found the optional Windows handoff at bootstrap:189-193 can replace verified
forms with unchecked executable paths. pathsetup.py:90-108 checks file existence,
not help. The optional paragraph is unchanged from HEAD: valid pre-existing
adjacent risk, not a new detection regression. No experiment was run for it.

Each finding has 1/2 agreement and an actionable scope proposal in
prerequisite-flow-repair-post-fix-review.md, with original responses preserved.
Recommend fixing README wording and explicitly deferring the Windows repair;
both dispositions remain pending developer triage. No automatic fix, issue,
new review turn, publication, refresh or rehearsal is authorized.
## Windows Printed-Command Handoff Repair Explicitly Deferred

The developer selected "Fix README wording and record the Windows issue for
separate repair". Deferred Minor: bootstrap.md:189-193 and its packaged mirror
switch a working session to printed Windows executables without help verification;
pathsetup.py:90-108 selects existing files, not healthy commands. A stale wrapper
can therefore break a previously verified module/mixed-form session. The paragraph
is unchanged from HEAD and outside this README correction's scope.

Separate repair direction: preserve established forms until replacements are
verified, retain real-error stops and normal PATH consent, and establish bounded
stale/mismatched-wrapper evidence before changing the contract. No PATH mutation,
new experiment, runtime edit, issue publication or implementation is approved.
The README Minor is approved for the four-passage factual correction now.
## Reviewed README Claim Corrected; Windows Risk Remains Deferred

The four approved README passages now accurately distinguish developer-supplied
system prerequisites, Linux-only consent-gated Atom installation and other-platform
setup decisions. Final text was read against init/bootstrap policy. The affected
existing README case passed 1 test in 4.61s, all 545 links resolve and whitespace
checks pass. README hash is
64E6120B27F05EF224B56C4A8CD6D239A331E420FC09D46687E987630E07D68D;
all four init/bootstrap hashes retain the reviewed snapshot.

The in-scope Minor is locally corrected, pending local acceptance, not independent
re-review of the new README bytes. The Windows handoff Minor remains explicitly
deferred with no implementation or issue publication. Both fresh reviewers report
complete context for their old README snapshot; that does not prove live agent
behavior or carry their review over to later bytes. No additional reviewer spend,
publication, installed refresh or rehearsal occurred.
## Post-Fix Correction Accepted Locally

The developer selected "Accept the correction; keep delivery, refresh and
rehearsal gated". The README claim finding is locally corrected/accepted; the
Windows printed-executable handoff risk remains the explicitly deferred Minor.
No Blocker/Major was reported. Evidence and limits remain in the post-fix report;
no new README independent review, publication/refresh or observed rehearsal ran.
## Publication Scope And Remaining Risk

Publication audit found no unrelated shipped change: five documentation files,
with canonical/package parity, plus their required phase evidence. Historical
records are retained; the PR summary should not repeat the audit chronology.
The Windows printed-executable handoff Minor remains explicitly deferred. Latest
README correction is locally validated, not independently re-reviewed. No live
agent/Linux fallback or completed Phase 09 outcome is claimed. Installed refresh,
new rehearsal and merging remain outside publication authorization.
