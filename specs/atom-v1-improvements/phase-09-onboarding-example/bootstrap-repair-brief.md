---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
author: "Copilot"
date: "2026-11-07"
status: "approved"
evidence_method: "accepted failure plus bounded deterministic command validation"
---

# Bootstrap Repair Brief

## Problem

The [first rehearsal](poc-report.md) stopped before onboarding because the actual
bootstrap guide prescribes bare pip installation into Ubuntu's externally managed
Python environment. The developer accepted its Inconclusive result and selected
repair of Atom's own guidance rather than a manual workaround for the expense CLI.

The desired outcome is a verified Linux bootstrap recipe that establishes both
command boundaries without overriding system protections or replacing a working
installation. The canonical and packaged reference must stay aligned.

## The Question

Can Ubuntu's existing Python 3 establish and reuse both Atom command boundaries
through an isolated installation that supports first initialization of a fresh
Go module without changing system Python, shell defaults or existing installations?

## Evidence Choice

Reuse the accepted, actual PEP 668 failure as proof of the documentation defect;
do not rerun global pip. The remaining uncertainty is whether the candidate
isolated-install command path really supplies both usable helpers and works with
onboarding. Recommend one bounded deterministic validation before a short repair
spec. This is command integration, not an invented Go algorithm spike.

Alternative: change the guide from general Python/pip documentation alone, without
executing the proposed commands. That is cheaper but leaves this exact integration
boundary unproven after an observed real failure. A manual workaround/revised
usability trial was considered and not selected.

The public first-use source is tested rather than quietly substituting an editable
install of unmerged local code. No new bootstrap framework, CLI command or runtime
policy engine is proposed. The final user-facing environment location and complete
guidance wording remain decisions for the post-evidence short spec.

## Observed Preflight And Baseline

Read-only Ubuntu checks on 2026-11-07 exited 0:

```text
python3 --version
Python 3.12.3
python3 -m pip --version
pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
go version
go version go1.22.2 linux/amd64
git --version
git version 2.43.0
```

python is absent; python3 resolves to /usr/bin/python3. venv and ensurepip are
importable; ensurepip reports bundled pip 24.0.
Import success is not proof that creating/installing into a venv works.
The proposed proof directory is absent, including a dangling-symlink check.
The home is user-owned, writable and Linux-native; the user is not root.

The canonical and packaged bootstrap references are byte-identical. Local
tools/pyproject.toml names distribution atom-cli, declares Python >=3.10 and both
entry points, and has no runtime dependencies. Its distribution version is not
the plugin's version; record the actual installed distribution separately.

The [original Phase 09 brief](poc-brief.md#untouched-repository-baseline) records
30 onboarding/plugin tests passing before Phase 09 changes. HEAD remains
4434cdf71b3eaab869f9acf276fa85c1bb9f969c, with only specification changes observed.
Reuse that untouched Python baseline for this brief, not as Linux install proof:
the onboarding unit fixture substitutes deterministic Go gate results.
No current root Go baseline is claimed; Atom's own repository has no root go.mod.
The disposable module's real baseline will be captured by atom init during the
approved check, not manufactured now.

## Fixed Experimental Conditions

| Item | Proposed bound |
|---|---|
| Host | Existing Ubuntu WSL, ordinary user; Python 3.12.3 and Go 1.22.2 |
| Private proof root | $HOME/atom-phase09-bootstrap-proof, freshly created with mode 0700 only after approval |
| Virtual environment | .venv inside that proof root, outside the Go module and its .atom/ |
| Disposable Go module | module beneath the proof root; module path example.com/atom-bootstrap-proof |
| Public source | girishmotwani/atom at 50622abf2b9f58bcfc2c9d538b7292cf0689ceee, observed as public main now |
| Installation count | One venv, one pinned Atom pip-install invocation; no pip upgrade or automatic retry |
| Go execution | One real atom init in the empty disposable module; no Go implementation |
| Actual writer checks | Two named synthetic artifacts in that module, one through each working command form |
| Cost | No Copilot invocation, extra agents or review-model calls; estimated 10-15 minutes, 15-minute elapsed run cap |

The public commit pin identifies this new check, not the source commit of the
previously installed plugin. Dependency/build-tool versions and actual package
metadata must be recorded after installation; pinning Atom's source does not pin
all transitive build inputs.

## Planned Validation

Revalidate destination ownership/absence before creation. If it already exists,
is a symlink, needs elevation, or requires new system tooling, stop without repair.
Retain the outputs and exact execution parameters in private session evidence.

1. Snapshot resolved Python/pip/Go/git commands, the existing Copilot binaries and
   known shell profile fingerprints. Do not inspect authentication files.
2. Create only the private proof root, its empty module directory, private temp/cache
   directories and one venv with the already available python3. Use an explicit
   venv Python; do not activate it or change PATH/profile.
3. Install the pinned public package once through that interpreter. Use
   --no-cache-dir and proof-local temporary storage. Do not upgrade pip, use
   --user, sudo, a system-package override or extra package manager.
4. From the disposable Go module, verify --help for both entry points and both
   venv-Python module forms. Record installed atom-cli metadata and exact source
   identity without locating/reading Atom's Python implementation.
5. Create the approved example.com/atom-bootstrap-proof go.mod through go mod init,
   then run the established atom init form once. Read the named config, baseline,
   local bundle manifest, Copilot instructions and .gitignore to verify onboarding.
   A baseline failure on this empty module must be recorded verbatim; do not add
   a Go program to make it green. Confirmation requires the actual baseline to
   be persisted and disclosed, not to pass.
6. Write specs/bootstrap-proof/findings.md and decisions.md through the
   dedicated writer's two forms, supplying complete UTF-8 input. Compare the
   output bytes with the expected synthetic content. Help output alone is not
   evidence that artifact writing works. Obtain the new module's normal
   repo-specific writer approval; do not borrow the Atom repository's approval.
7. Repeat discovery of the already installed command/module forms, without
   invoking any installer. Compare package metadata and entry-point hashes;
   confirm known shell/default-command/Copilot fingerprints are unchanged.

Ubuntu-only illustrative command forms; the execution record will retain resolved
absolute paths and exact arguments:

```text
python3 -m venv <proof-root>/.venv
<proof-root>/.venv/bin/python -m pip install --no-cache-dir "git+https://github.com/girishmotwani/atom.git@50622abf2b9f58bcfc2c9d538b7292cf0689ceee#subdirectory=tools"
<proof-root>/.venv/bin/atom --help
<proof-root>/.venv/bin/atom-write-artifact --help
<proof-root>/.venv/bin/python -m atom.cli --help
<proof-root>/.venv/bin/python -m atom.artifact_cli --help
```

Go/pip temporary/cache changes, if any, should be directed into proof-local child
environment settings. Do not claim this is an OS sandbox or exhaustive proof of
every filesystem write. Stop if commands need unapproved tool downloads,
permissions, credentials or configuration changes. Stop at the first unexpected
failure rather than installing another fix or extending the experiment.

## Verdict Rules

| Observation | Verdict |
|---|---|
| One isolated installation supplies both usable forms; real init persists its actual baseline; both writer round trips match; reuse checks do not reinstall; known defaults/installations remain unchanged | Confirmed for this bounded command recipe |
| Under the fixed conditions the isolated route cannot supply a helper, init rejects the setup, an artifact round trip is wrong, or an existing installation/default is changed | Refuted; stop and gate the failed boundary |
| Public download/build prerequisites block the check, the cap/permissions stop it, evidence is missing, or conditions must change | Inconclusive; no spec based on assumed success |

A normal disclosed Go-baseline failure in the intentionally empty module is not
by itself a bootstrap failure. Conversely, helper success with missing onboarding
evidence cannot be relabeled complete. Any unexpected CLI/guide contract mismatch
is a finding and stop, not permission to repair public runtime code.

## Exclusions And Limits

No expense-summary module changes or rerun; the [original recipe](rehearsal-recipe.md)
and failed recording remain preserved. No plugin/CLI update, authentication changes,
Windows/macOS provisioning, system/package overwrite, pipx installation, commit,
push, release or Phase 09 final design. No source audit or production Python edits.

This does not test actual model compliance, genuinely new users, all editable
installations, every filesystem mutation, duplicate/conflicting environments,
repeat/no-op atom init, general Go correctness or a public end-to-end quickstart.
Executing a check-only reuse path does not enforce that an agent will choose it.
Later semantic review must preserve the guide's existing-working-package guard
and Windows opt-in behavior; any material new uncertainty returns to a gate.

Keep this proof separate from the original experienced-user attempt. Do not revise
its Inconclusive verdict, frozen inputs or historical recording. Retain named
experimental files for inspection; no automatic recursive cleanup.

## Artifacts And Next Gates

After the approved run, write bootstrap-repair-report.md here with the exact
question, command outputs, versions/source identity, artifact comparisons,
preservation checks and Confirmed/Refuted/Inconclusive limits.
Only an accepted applicable result permits the short bootstrap repair spec.
That spec still needs approval before editing canonical and packaged guidance.
Future checks use existing documentation/packaging tests plus semantic review;
no fake production RED/GREEN loop or new string-presence tests.

## Completeness

- [x] Accepted failure and remaining isolated-install uncertainty distinguished.
- [x] One falsifiable command-integration question and alternative named.
- [x] Ubuntu-only paths, source, one-run budget and fixture module path explicit.
- [x] Actual writer/init checks included, not just command-help proxies.
- [x] Verdicts distinguish expected empty-module baseline failure from setup failure.
- [x] Existing installations, original rehearsal and later gates preserved.
- [x] Python baseline reuse and no-Go-spike adaptation recorded.
- [x] Developer approves this bounded validation and its provisioning scope.

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
