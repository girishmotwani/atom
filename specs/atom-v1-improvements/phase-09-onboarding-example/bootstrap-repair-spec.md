---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-08"
status: "approved"
poc_report: "bootstrap-repair-report.md"
scope: "bootstrap prerequisite repair, not the final Phase 09 example"
---

# Bootstrap Guidance Repair Spec

## Purpose And Scope

Establish both Atom commands on the observed Ubuntu setup without bare system-pip
installation, replacing a working package or changing shell defaults. This is a
documentation repair using existing Python/CLI interfaces, not a bootstrap engine.

Change only skills/atom/references/bootstrap.md, its tools/atom/assets counterpart,
and a short README clarification/link explaining that the plugin does not install
the Python commands. Retain historical approval ledgers rather than rewriting them.
Use this specifically named spec so it cannot be mistaken for the still-unproven
Phase 09 expense-summary design. No runtime API or state-schema changes.

## Evidence: Established

The accepted [bootstrap report](bootstrap-repair-report.md) establishes:

- Ubuntu has supported python3 but no python alias; the old bare-pip route failed
  with PEP 668 in the [original rehearsal](poc-report.md).
- A user-owned external venv installed pinned public atom-cli 0.1.0 and supplied
  both entry points and both Python module forms.
- Both writer forms produced the exact UTF-8 bytes. First init persisted its real
  failing empty-module baseline; that failure is not a bootstrap rejection.
- Check-only reuse preserved metadata, known binaries and profile fingerprints.

## Evidence: Choices And Remaining Assumptions

The developer chose "One user-owned environment outside repositories (recommended)"
after the proposed location and alternative were presented. The Linux default is
$HOME/.local/share/atom-cli/venv, not .atom/ or a repository-local environment.
Read-only inspection finds its existing .local/share ancestors owned/writable and
the atom-cli/venv destination absent. This proves neither creation nor installation.

The proven run used a private child HOME and disabled child pip/Git configuration.
Normal user configuration, the selected final prefix, missing/partial environments
and actual agent route selection were not validated. These are explicit boundaries,
not silently covered by the Confirmed result. Native Windows/macOS provisioning,
all editable installs and arbitrary custom install schemes are not new claims.

## Public Command Surface

All callers remain the existing skills in the target Go module. Preserve successful
entry points when available. Otherwise bind each command role to the exact verified
Python/module form and retain it throughout the session; no activation or PATH change.

For the selected Linux environment, the authoritative fallback forms are:

```text
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.cli <arguments>
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.artifact_cli <relative-path>
```

Verification uses --help for each role. Artifact content still goes through complete
UTF-8 stdin. Existing Windows python module forms, setup-path opt-in, printed absolute
commands and current-parent-process limitation remain unchanged. No exported Go
types, signatures, goroutines or new executable are introduced.

## Behavior

1. Check both entry points first. If both work, stop discovery immediately; do not
   inspect environments, install anything or disturb an editable package.
2. For missing roles on Linux, resolve supported Python 3 using python3 first,
   then python only if it is a working Python >=3.10. Preserve Windows's existing
   python fallback. Report unsupported/missing interpreters; do not provision them.
3. Run only the needed Python module help checks from the target module. Reuse
   successful forms without installation. Any working-but-incomplete Atom package,
   non-absence import failure or damaged command is a stop, not permission to mask
   it with another install. Do not equate every nonzero help result with absence.
4. Only when no working Atom boundary/package was found, check the single known
   Linux environment path. A healthy environment supplies verified module forms
   for reuse. An existing invalid, partial, unowned or symlinked destination is
   preserved and reported; never recreate it, search arbitrary layouts or delete it.
5. Only explicit package absence and an absent safe destination permit proposing
   a new install. Explain the user-owned shared location and obtain provisioning
   consent. Validate writable owned non-symlink ancestors; create the environment
   destination exclusively. A collision/permission failure stops without overwrite.
6. Create one venv outside all repositories. Before installing, check for scheme
   redirects through only relevant non-secret pip settings; if installation would
   leave the venv or its safety is uncertain, stop and ask. Do not dump
   credential-bearing config or silently disable user configuration. Only then
   install the canonical public git+https://github.com/girishmotwani/atom.git#subdirectory=tools
   through that environment's Python -m pip. Do not upgrade pip, activate the env,
   use bare pip, --user, sudo, system-protection overrides, change profiles or
   copy credentials.
7. Verify both entry-point/module boundaries after installation, record the actual
   working forms once, and use them in subsequent skill commands. Never proceed
   without both. Installation failure or partial verification stops with its exact
   diagnostic and no unchanged retry or package overwrite.
8. Keep Windows setup-path as the same one-time explicit opt-in for an already
   working package. Its printed absolute commands are authoritative in that session;
   no re-probe, registry behavior change or second install is introduced.
9. Preserve init and writer permissions, baseline disclosure and source-read limits.
   A failing Go baseline remains failing, including an empty module; do not insert
   Go code to hide it or read external Atom implementation while onboarding.
   Both canonical/package documents must be byte-identical.

## Errors And Concurrency

| Condition | Required observable response |
|---|---|
| No supported Python, missing venv/ensurepip | Show the failed capability/command; stop before system provisioning |
| Partial package, unexpected import error | Name the unavailable role/error; preserve the existing install |
| Existing unsafe or incomplete environment; creation collision | Preserve it and report the exact path/problem; no clear/force/recreate |
| Pip install redirects or uncertain scheme | Stop for explicit resolution; no silent config override or full secret-bearing config dump |
| Public download/install failure | Show actual stdout/stderr safely; stop, do not assume private-repo permissions or change authentication |
| Any boundary verification failure | No success claim or next beat; record which role failed |

No new error type or runtime diagnostic text is specified: report the actual
command's error, not a reconstructed standard message. Keep raw credential-bearing
output private and redact before public artifacts.

Bootstrap is sequential. Concurrent installers into the shared environment are
unsupported: exclusive creation is a collision check, not a new lock service.
Do not update an environment used by another session. Read-only reuse assumes a
stable existing install; existing init/writer concurrency contracts are unchanged.

## Trade-offs

| Choice | Reason |
|---|---|
| One user-owned external venv | Developer-selected reuse; no project Git pollution or partial .atom/ collision |
| Per-project venv rejected | Duplicate installs and additional project ignore/lifecycle decisions |
| Explicit Python/module forms | Proven, no activation/profile edits or executable search beyond the known path |
| pipx/new bootstrap command rejected | Extra dependency/runtime surface unsupported by this proof |
| Existing packages first | Preserve working/editable installs; a failed command is not authorization to replace them |
| Canonical public source retained | Same installation source as before; evidence pin is provenance, not a mandatory user version pin |

Future platform/layout support extends the existing reference only after relevant
evidence and approval. This spec adds no automatic classifier, configuration field,
updater, migration, package manager, monitor or shell/PowerShell script.

## Validation And Delivery Gate

Map the numbered behavior to semantic documentation review and existing tests,
not new constant/string-presence tests or a fictitious production RED/GREEN loop.
From tools, the scoped existing selector is:

```powershell
python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

At repository root, run python tools\check_links.py and git diff --check.
Retain Windows fallback literals required by its existing tests; these tests prove
parity/document contracts, not agent compliance or Linux installation.

Before presenting the guidance as validated, obtain separate pre-run approval for
one bounded check of the exact candidate recipe at the selected prefix with normal
user HOME/pip/Git context. Scope it to non-secret install-scheme checks, one safe
isolated install if absent, both command roles, named synthetic writer fixtures,
check-only reuse and known preservation fingerprints. No general configuration
audit, live Copilot trial, automatic fixes, upgrade or original-module mutation.
Use the recorded public pin for comparable evidence and disclose that the user
recipe's moving public source is not a version-compatibility guarantee.

If that boundary needs a materially different recipe, stop and re-gate this spec
before implementing it. The existing proof must not be relabeled as normal-HOME
validation. No new check or environment creation ran while drafting this spec.

Existing plugin installs/local bundles will not acquire changed guidance merely
because these source documents change. A later separately approved publication or
candidate-content refresh and re-frozen live rehearsal are required for user-path
claims. Preserve the original Inconclusive recording and recipe throughout.

## Approval Boundary

Approval accepts this three-document scope and permits its documentation
implementation after the stated boundary evidence is addressed. It does not
authorize the new install/validation run, runtime changes, model spend, final
Phase 09 design, original-module repair, plugin update, commit, push or release.
The next validation brief must make provisioning and its cost explicit.

## Completeness

- [x] Accepted evidence, developer layout choice and assumptions separated.
- [x] Public command roles consistent; no invented Go API or implementation.
- [x] Numbered behavior, actual errors, concurrency and rejected options explicit.
- [x] Scope and command-preservation/documentation checks specified.
- [x] Changed normal-user environment boundary and separate run approval explicit.
- [x] Developer approves the short repair spec.


## Spec Approval Recorded: 2026-11-09

The developer selected exactly:
"Approve spec; prepare separate boundary-validation brief".

Accept this spec with its stated conditions. Prepare the separate
[boundary-validation brief](bootstrap-boundary-brief.md); do not run it or create
the selected environment on this approval. Documentation implementation remains
conditional on addressing the normal-user boundary and accepting the result.
Material recipe changes require re-gating this spec. No live retry, publication,
commit or push is authorized.

## Boundary Evidence Reported: 2026-11-09

The [normal-user boundary report](bootstrap-boundary-report.md) is Confirmed for
the selected shared prefix and observed HOME/pip/Git context. No material recipe
change was needed. The report still awaits explicit result acceptance before
implementing this approved spec. Source guidance has not changed.

## Boundary Result Accepted; Implementation Authorized: 2026-11-09

The developer accepted the [boundary report](bootstrap-boundary-report.md) and
selected "Accept result; proceed with approved guidance repair". Its evidence
condition is addressed for the observed Ubuntu setup; implement this approved
three-document spec and run its existing focused checks. No material recipe
change or broader environment/UX claim is authorized.

## Implementation Recorded: 2026-11-09

The three source documents now implement this approved spec. The
[documentation test spec](bootstrap-repair-test-spec.md) records the nine-behavior
semantic review, 34 passing existing tests, parity and preserved Windows/history
checks. No material behavior or source scope changed. This records a source
repair, not delivery to installed plugins or successful completion of the
original rehearsal. Implementation acceptance remains pending.

## Source Implementation Accepted: 2026-11-09

The developer accepted the documentation repair and explicitly kept delivery
and rehearsal gated. The three-document source implementation and recorded
checks satisfy this prerequisite spec without material changes. No installed
plugin or existing module bundle was refreshed, and the original experienced-user
rehearsal remains Inconclusive. Phase 09 itself is not complete.
