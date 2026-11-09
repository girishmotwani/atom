---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
author: "Copilot"
date: "2026-11-09"
status: "approved"
evidence_method: "approved command evidence plus changed-boundary validation"
---

# Bootstrap Normal-Environment Boundary Brief

## Problem And Known Evidence

The developer approved the [repair spec](bootstrap-repair-spec.md) and requested
this separate brief. The [accepted command proof](bootstrap-repair-report.md)
confirmed both Atom command roles, actual writer round trips and first init, but
used a private child HOME with pip/Git configuration disabled. It did not validate
the developer-selected shared location with normal user configuration.

The outcome is evidence for that changed installation boundary, not another
usability rehearsal. Preserve system Python, working packages, shell defaults
and the [original Inconclusive attempt](poc-report.md).

## The Question

Can the approved Ubuntu bootstrap recipe establish and reuse both usable Atom
command roles at $HOME/.local/share/atom-cli/venv with normal user HOME/pip/Git
configuration, while preserving named existing defaults and installations?

## Evidence Choice And Risk

Reuse the accepted venv/package/init/writer evidence and the approved spec.
Integration with the final prefix and real user configuration is the remaining
risk: the controlled proof could have hidden an install-scheme redirect or an
ordinary-user configuration failure. Do not invent a Go algorithm spike.

Alternative: implement the text now and explicitly leave this boundary unverified.
That is cheaper, but would not meet the approved spec's validation condition.
Package feasibility is already demonstrated; performance has no acceptance
threshold here. Agent route selection and newcomer ergonomics need a later live
trial, not additional models in this command check.

Reuse the untouched Python baseline recorded in the
[original brief](poc-brief.md#untouched-repository-baseline): 30 scoped tests passed.
This artifact-only preparation changes no runtime behavior; do not rerun it as
installation evidence or claim a root Go baseline. Atom has no root go.mod.

## Fixed Conditions And Cost

| Item | Bound |
|---|---|
| Host | Existing Ubuntu WSL, ordinary non-root user; revalidate Python 3.12.3, Go 1.22.2 and Git 2.43.0 |
| Shared venv | $HOME/.local/share/atom-cli/venv; outside every module; retain after the run |
| Private fixture root | $HOME/atom-phase09-bootstrap-boundary-proof, absent before exclusive creation with mode 0700 |
| Disposable module | module under that root; example.com/atom-bootstrap-boundary-proof |
| Public source pin | 50622abf2b9f58bcfc2c9d538b7292cf0689ceee; do not refresh to today's main |
| Installation | At most one venv creation and one pinned Atom pip-install invocation; no retry or pip upgrade |
| Functional checks | Both entry points and module forms; one real init; two named writer round trips; check-only reuse |
| Budget | One run; estimate 10-15 minutes; 900-second elapsed cap including preflight and subprocesses |
| Model cost | No Copilot invocation, agents, review batches or model requests |

These are proposed run conditions, not claims about fresh observations today.
The prior read-only layout inspection found owned/writable .local/share ancestors
and no destination. Revalidate it after approval; do not provision during drafting.

## Planned Run

1. Before mutation, verify the approved versions and normal HOME, discover both
   command roles/current Python package, and check the named destinations. A
   newly available package, changed toolchain or existing venv/fixture destination
   changes these fixed fresh-install conditions: preserve it, stop and gate.
   Never overwrite a working, partial, symlinked or unowned installation.
   Snapshot resolved system Python/pip/Go/Git and both known Copilot binaries,
   named shell profile fingerprints and the original recipe/recording identities.
2. Verify owned, writable, non-symlink ancestors within HOME. Exclusively create
   only the absent atom-cli parent as needed, its venv destination and the private
   fixture root/module. A collision stops without deletion. Create the venv with
   the existing python3; do not install missing system capabilities.
3. Before any pip install, inspect only non-secret install-scheme controls:
   relevant target/prefix/root/user/python environment settings and their
   global/install pip configuration keys. Resolve the effective scheme using
   the selected venv's pip; verify its interpreter/prefix and pip location.
   Log only key names and safe scheme conclusions, not full config or credentials.
   An absent configuration key is expected only with its actual missing-key
   diagnostic; another error is a stop, not an absent/default setting.
   A redirect, partial interpretation or uncertain scheme stops before install.
4. With normal HOME and pip/Git configuration still in effect, invoke the pinned
   public installation once through the absolute venv Python. Do not disable
   configs, replace HOME, scrub user configuration into a clean environment or
   copy credentials. Use --no-cache-dir and --no-input; disable interactive Git
   prompts only. Do not change index/authentication settings to make it work.
5. From the disposable module, verify --help through both entry points and both
   absolute-Python module forms. Record installed distribution/build metadata,
   source identity and executable hashes, not external implementation source.
   Run go mod init for the named fixture, then atom init once. Preserve the actual
   named onboarding files and baseline output, including empty-module failures.
   No Go implementation or toolchain download is permitted.
6. With fixture-specific writer permission, send complete frozen UTF-8 inputs to
   the two forms below and compare exact output bytes/hashes. Use one synthetic
   payload containing U+00E9; freeze both expected inputs before execution.
   Recheck the successful command forms and metadata without another installer.
   Compare named defaults/profile/Copilot fingerprints and original evidence.

Ubuntu command shapes; the run record will retain resolved absolute paths and
exact argv/stdin, not execute these placeholders literally:

```text
python3 -m venv "$HOME/.local/share/atom-cli/venv"
"$HOME/.local/share/atom-cli/venv/bin/python" -m pip install --no-cache-dir --no-input "git+https://github.com/girishmotwani/atom.git@50622abf2b9f58bcfc2c9d538b7292cf0689ceee#subdirectory=tools"
"$HOME/.local/share/atom-cli/venv/bin/atom" --help
"$HOME/.local/share/atom-cli/venv/bin/atom-write-artifact" --help
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.cli --help
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.artifact_cli --help
```

Fixture-specific writer permission is limited to these forms, with working
directory $HOME/atom-phase09-bootstrap-boundary-proof/module:

```text
"$HOME/.local/share/atom-cli/venv/bin/atom-write-artifact" specs/bootstrap-boundary-proof/findings.md
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.artifact_cli specs/bootstrap-boundary-proof/decisions.md
```

Approval of this brief must explicitly include these two fixture writer forms;
the Atom repository's saved approval and the previous fixture's approval do not
transfer. No generic editor is approved as a substitute.

Temporary/build and Go cache directories may be proof-local; set GOTOOLCHAIN=local
to prohibit automatic Go downloads. Record those limited controls explicitly.
Do not use the prior executor's credential-free HOME/config overrides. Ordinary
user configuration may direct normal cache, helper or temporary writes; this is
not a filesystem sandbox or an exhaustive no-write guarantee.

## Stop Conditions And Verdicts

Stop on the first unexpected failure or elapsed cap, terminate only the run's
exact child process group, preserve diagnostics privately, and do not retry,
repair configuration or silently change the recipe. A failed install may leave
a partial environment: retain and report it, not automatically delete/recreate it.

| Observation | Verdict |
|---|---|
| Safe effective scheme; one install supplies both roles; init persists its true baseline; both writer round trips match; reuse does not reinstall; named preservation checks match | Confirmed for this observed normal-user boundary only |
| Completed fixed-condition commands demonstrate an unusable role, incorrect writer bytes, rejected init or a changed named existing installation/default | Refuted; stop and present evidence |
| Changed preconditions, unsafe/uncertain scheme, download/build prerequisite failure, permission/cap stop or incomplete evidence | Inconclusive; no assumed confirmation |

An honestly persisted failing empty-module Go baseline is expected, not bootstrap
failure. A command merely returning zero is not sufficient functional evidence.
Record exact outputs/return codes, versions, pip/build inputs, pinned source,
input/output hashes, timing and preservation results. Source pinning does not pin
all build dependencies or prove the moving public install URL remains compatible.

## Exclusions, Records And Gates

No expense-summary changes or retry, source guidance edits, runtime changes,
plugin refresh, shell defaults/authentication/system changes, upgrades, broad
configuration audit, full-filesystem claim, Windows/macOS provisioning, concurrent
installer test, arbitrary editable/unsafe-layout handling or actual agent UX test.
No commit, push or release. Retain the shared environment and named proof files;
no automatic recursive cleanup. Preserve the original frozen attempt.

Write bootstrap-boundary-report.md after the approved run, separate from the
accepted earlier report. Preserve complete raw outputs privately and redact any
credential-bearing output before repository artifacts.

Present the verdict and stop for result acceptance. A material recipe change
returns to the spec gate; only accepted applicable evidence permits the already
approved documentation repair. A Confirmed boundary result does not finish
Phase 09 or authorize a live rehearsal.

## Open Question And Completeness

Only the bounded run/provisioning/writer approval remains for the developer.

- [x] One falsifiable changed-boundary question; accepted evidence and alternative.
- [x] Named prefix, fixture, source pin, single-run budget and actual checks.
- [x] Expected failures, stop conditions, verdicts and explicit exclusions.
- [x] Command-validation adaptation; no invented Go spike or fresh baseline claim.
- [x] Separate result/spec/publication/rehearsal gates preserved.
- [x] Developer approves this run, isolated provisioning and named fixture writers.


## Run And Fixture Writers Approved: 2026-11-09

The developer selected exactly:
"Approve the bounded run and named fixture-writer forms".

This authorizes the single bounded Ubuntu check, the named shared venv and private
fixture provisioning, and only the two fixture writer forms specified above.
Keep the public source pin, normal user configuration, 900-second elapsed cap,
no-model/no-retry limits and result gate unchanged. This approval does not borrow
another repository's writer permission or authorize guide edits, live rehearsal,
publication or automatic cleanup. No run has started when recording this approval.
