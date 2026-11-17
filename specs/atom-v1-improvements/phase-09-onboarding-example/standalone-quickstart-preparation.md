---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-16"
status: "prepared-and-launch-approved-not-launched"
---

# Standalone Quickstart Preparation

## Result

The developer said "lets go for it" after the replacement brief's preparation
approval. Read-only preflight found the fresh target absent and existing Ubuntu
prerequisites available, but the pinned Ubuntu client does not document the
approved separate cache control. Stop before installation or a live replay as
required by standalone-quickstart-brief.md. This is a preparation blocker, not
an executed POC or a verdict about the expense program.

## Evidence

Actual existing Ubuntu client/prerequisite output (all version/help commands exit 0):

```text
GitHub Copilot CLI 1.0.107.
Run 'copilot update' to check for updates.
go version go1.22.2 linux/amd64
git version 2.43.0
```

Python reported 3.12.3, ordinary-user execution, venv available, recorder available,
and no existing atom-phase09-standalone-20261116 target. No target was created.
The pinned executable is $HOME/.local/atom-phase09-tools/bin/copilot.

Relevant output of that client's --no-auto-update help environment:

```text
DOCUMENTED: COPILOT_AUTO_UPDATE True
DOCUMENTED: XDG_CACHE_HOME False
DOCUMENTED: COPILOT_CACHE_HOME False
DOCUMENTED: COPILOT_HOME True
```

Its documented COPILOT_HOME description:

```text
  `COPILOT_HOME`: override the directory where configuration and state files are stored; defaults to `$HOME/.copilot`.
```

The first preflight exited 1 at the missing documented cache control:

```text
Required isolation control is not documented by target CLI; stop.
```

A second read-only help query established the supported profile/no-CLI-update
controls, not an alternate cache mechanism. Absence from help is not proof that
an undocumented variable is unsupported internally; the approved path cannot
rely on that unverified behavior. The old client's auto-update help describes
CLI downloads, not the current build's separate claim about plugin updates.

Public main resolved read-only via gh api repos/girishmotwani/atom/commits/main:

```text
5bb33cbe2c835382b5ccda840c5268321b24ac0b
```

This is a candidate source identity, not an installed/frozen plugin identity.

## Recommended Narrow Scope Adjustment, Not Yet Approved

Retain the pinned 1.0.107 client and fresh Atom Python environment/workspace/profile,
but disclose its existing shared CLI cache instead of claiming fresh cache
isolation. Use the documented profile and no-CLI-update controls only. Before
installation or launch, verify through public client help how to avoid plugin
updates, or freeze/recheck installed plugin hashes and stop on any change; do not
claim no-plugin-update behavior from the newer Windows documentation.

A fresh profile can test fresh Atom plugin registration/install without a fresh
CLI cache, but it does not prove complete cache isolation or a clean OS. This
changes the brief's stated condition and needs the developer's decision first.
No CLI upgrade, authentication change or broad bootstrap repair is recommended.
Alternative: stop preparation and retain the original fresh-cache requirement.

## Unchanged Boundaries

No install, venv/profile/workspace creation, login, credential copy, model session,
agent batch, environment/profile edit, production source edit, commit or push.
The one-session/30-active-minute replay remains unspent. The exact frozen recipe
still must be presented before a participant launches. Existing dirty work and
all earlier rehearsal evidence are preserved.

## Scope Decision Recorded

Developer approved: "Approve fresh profile with disclosed shared CLI cache".
The cache-isolation blocker is resolved by explicit scope amendment, not a technical
fix or undocumented control. Preparation may resume under the amended brief;
nothing has been installed or launched in this gate turn.

## Fresh Public Installation Completed: 2026-11-16

Developer said "lets continue" after the explicit shared-cache amendment.
Created only $HOME/atom-phase09-standalone-20261116 with private workspace,
profile, evidence, temporary and venv locations. The public Python install is
pinned to 5bb33cbe2c835382b5ccda840c5268321b24ac0b; distribution metadata's
vcs_info.commit_id matches. Actual execution summary:

```text
copilot-version: exit=0
GitHub Copilot CLI 1.0.107.
Run 'copilot update' to check for updates.
go-version: exit=0
go version go1.22.2 linux/amd64
git-version: exit=0
git version 2.43.0
venv-create: exit=0
atom-install: exit=0
atom-help: exit=0
writer-help: exit=0
poc-new-help: exit=0
poc-run-help: exit=0
atom-install-identity: exit=0
atom-cli: 0.1.0 commit: 5bb33cbe2c835382b5ccda840c5268321b24ac0b
```

Only included awesome-copilot and disabled builtin browser-use existed in the
new profile before installation. Marketplace addition and public plugin install:

```text
marketplace-add exit= 0
Marketplace "atom" added successfully.
plugin-install exit= 0
Plugin "atom" installed successfully. Installed 9 skills.
```

The first post-install validation wrapper exited 1 because its own guard incorrectly
expected plugin-list source to be "GitHub: girishmotwani/atom"; this client returns
"installed" there. No installer failed and no install was retried. Verified the
marketplace source through marketplace metadata, then compared every installed
plugin file against the selected commit's complete public Git tree. Actual output:

```text
marketplace_source: GitHub: girishmotwani/atom
plugin_metadata_source: installed
{"changed": [], "commit": "5bb33cbe2c835382b5ccda840c5268321b24ac0b", "expected_files": 658, "extra": [], "installed_files": 658, "missing": []}
```

Plugin 0.2.0 is enabled; its entire sorted path-to-SHA256 inventory digest is
c0ecc02d306f0441859ac2ce0479abf9dbabd0d4e6c3b8f6b1a20dce215b4a79.
This freezes actual public content, not merely a version label or skill listing.
The unpublished discovery helper is absent. Both Atom command helps and POC
subcommand helps passed from the workspace. Skill list exposes poc, but an actual
interactive slash alias and authenticated model access remain unverified.

Unpaid recorder and checksum readiness checks:

```text
recorder-check exit= 0
atom-standalone-recorder-ready
plugin-sha256-check exit= 0
```

The recorder test used printf, not a model. Workspace remains entirely empty:
no Go module, program, fixtures, tests, project state or seeded approvals. Hashes
of the pinned CLI, existing shell profiles, default Copilot config/settings and
existing Atom venv configuration match the pre-install observations. This is a
bounded fingerprint check, not a claim that every file on the host was audited.

Setup wall-clock interval from first private before-state evidence to readiness:
284.112 seconds. Tooling stage measured 73.954 seconds. These are preparation
measurements, not active developer time or a clean-install speed promise. No
model session or active replay time has been spent. Private full command receipts,
public tree, blob comparison, inventory and summary remain under the trial's
evidence directory; do not publish raw diagnostic/log data without review.

## Frozen Handoff

Produced standalone-quickstart-recipe.md with the exact launch, bounded request,
negative-exit checks and stop conditions. Use the existing CLI with fresh profile
and shared cache; no unsupported cache controls. No-plugin-auto-update behavior
is claimed: the older client's docs establish CLI updates only. Inventory checks
before/after the session detect snapshot changes; changed content invalidates the
attempt. The developer operates the single interactive terminal. Do not launch
another model process from this preparation session or simulate their approvals.

## Recipe Validation And Launch Decision

The frozen launch block passed bash -n with its actual UTF-8 LF bytes:

```text
Frozen Ubuntu launch block bash -n (LF bytes) exit= 0
```

An initial validation wrapper's Windows text mode changed LF to CRLF and produced
bash syntax exit 2. Passing actual bytes fixed the validation transport; no recipe
command changed and no launch was executed. This is syntax evidence, not proof
that authentication, interactive commands or the Go outcome work.

Developer selected exactly: "Approve one session using the frozen recipe" after
reviewing the installed snapshot, unchanged host fingerprints, empty workspace,
recorder/checksum checks and remaining authentication/alias uncertainty. One default-
model, developer-operated session and the 30-active-minute cap are authorized.
The participant must run the frozen Launch Once block, then send its single request.
Generated brief/report gates remain real decisions. No launch, model request,
production code or publication occurred in the preparation/approval turn.
