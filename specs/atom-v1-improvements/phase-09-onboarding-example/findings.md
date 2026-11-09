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
