---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
author: "Copilot"
date: "2026-11-09"
status: "approved"
evidence_method: "accepted bootstrap evidence plus bounded candidate-delivery validation"
---

# Isolated Candidate Delivery Brief

## Problem, Choice And Evidence

The developer selected "Prepare an isolated local-candidate validation brief
(recommended)". This authorizes this brief, not provisioning or another trial.
The [accepted source repair](bootstrap-repair-test-spec.md) has not reached the
Ubuntu plugin or atom-cli package. Read-only hashes in [findings.md](findings.md)
show the plugin and both proof modules still contain the old bootstrap.

Updating only the plugin is insufficient: atom init copies its local bundle
from atom-cli package assets. The installed init help has only --module and
--force; --force discards approvals and is not a delivery mechanism.

Reuse the accepted [normal-user bootstrap proof](bootstrap-boundary-report.md)
for venv/package/command/writer behavior, with its source pin and environment
limits. Reuse the 34 passing source-documentation checks already recorded in
the test spec; do not claim these establish candidate loading. No root Go module
or new Go algorithm warrants another root baseline or throwaway Go spike.

## The Question

Can an isolated candidate expose the repaired Atom plugin through the pinned
Ubuntu CLI's local-plugin metadata and generate the matching repaired local
instruction bundle through a separate candidate atom-cli installation, while
preserving the named working installations, defaults and original trial?

## Risk And Alternative

Integration is the material uncertainty: local plugin loading may collide with
installed atom, or packaged resources may not reach a fresh module. This matters
more than installation performance or already-proven writer mechanics. Actual
skill invocation and understandable gates require a later participant rehearsal;
metadata alone cannot establish either.

Alternative: publish first, then validate the public delivery. That needs explicit
review/shipping/push authorization and still does not prove a live workflow.
Do not silently switch to that route if candidate loading fails.

## Fixed Conditions And Cost

| Item | Bound |
|---|---|
| Host | Existing ordinary-user Ubuntu WSL; Python 3.12.3, Go 1.22.2, Git 2.43.0 |
| Copilot | Existing separate 1.0.107 binary at $HOME/.local/atom-phase09-tools/bin/copilot; no update |
| Private run root | $HOME/atom-phase09-candidate-delivery-proof; must be absent; exclusive mode 0700 creation |
| Candidate plugin | plugin under that root; copied only from the verified frozen installed-content inventory |
| Candidate package source | package-source under that root; fetch exactly 50622abf2b9f58bcfc2c9d538b7292cf0689ceee from the public Atom repository |
| Candidate venv | venv under that root; never the working $HOME/.local/share/atom-cli/venv |
| New fixture | module under that root; example.com/atom-candidate-delivery-proof |
| Provisioning | One public source fetch, one venv creation, at most one candidate pip-install invocation; no retry or pip upgrade |
| Budget | One run; estimate 10-15 minutes; 900-second elapsed cap including preflight/subprocesses |
| Model spend | Zero prompt/interactive/ACP sessions, agents or review batches; Copilot metadata commands only |

These are proposed run conditions, not claims that new preflight passed. Stop
before provisioning if the toolchain/source/snapshot changed, the destination
exists, or owned non-symlink HOME ancestry cannot be established.

## Provenance And Allowed Candidate Changes

The plugin's frozen identity is 594 files, aggregate SHA-256
b31ce534e6ab58627ad6fb623a979c6b9061488f44cb4d1da8090b0d28f725cf.
Its source commit was not exposed by CLI metadata; do not invent one. The Python
package has its separately known public source pin above. Do not equate these
provenance records or copy this branch's newer Python implementation into either.

Freeze the two accepted bootstrap inputs before execution; require byte equality
and SHA-256 ce34395eea5d7049b9ab23a594227a916afae28857ae3b873dac31255f387b3e.
In each new candidate source tree, replace only the canonical bootstrap and its
packaged mirror. All other source files must retain their respective base bytes.
The existing installed plugin and working Python package remain unchanged.

Build/install the candidate package normally from its patched public-source tools
directory; do not patch site-packages, executable wrappers or wheel RECORD files.
Record source/delta hashes, installed distribution/build metadata and candidate
inventories. Distribution versions may remain 0.2.0 and 0.1.0; those strings alone
do not identify this unpublished candidate. README publication is not simulated;
this validation delivers only the bootstrap references needed by the rehearsal.

## Planned Single Run

1. Revalidate named versions, original recipe/recording identities and the entire
   frozen plugin inventory. Hash the working venv's two launchers, installed
   distribution metadata and named packaged bootstrap asset using package-resource
   metadata, not an external implementation-source audit. Snapshot both Copilot
   binary hashes and the previously named profile fingerprints. Do not inspect
   authentication files or dump full configuration/environment.
2. Exclusively create only the absent private run root. Copy the frozen plugin
   inventory without Git/cache/runtime secrets. Fetch the exact public package
   commit once into the new package-source tree. Refuse symlinks, path escapes,
   extra/missing snapshot files or unexpected base bootstrap hashes. Apply only
   the two identical reference overlays per new source tree; record all deltas.
3. Try local-plugin metadata discovery from the otherwise empty new run root,
   with --plugin-dir pointing at the candidate. Record actual plugin-list and
   skill-list output and resolve candidate identity/path. Inspect only the named
   three command files as additional file evidence. If metadata cannot distinguish
   the candidate from installed atom, reports duplicates/shadowing, drops required
   surfaces, or cannot establish discovery, stop. Do not disable/rename installed
   atom, edit its cache, change plugin identity, or launch a model to compensate.
4. Create the separate candidate venv with existing python3. Before pip installation,
   recheck effective venv interpreter/prefix/pip and the same relevant install-scheme
   environment/config keys as the accepted boundary proof. Preserve normal HOME,
   pip and Git configuration. Unsafe/uncertain redirects or missing capabilities
   stop; no system installs, clean-HOME workaround, authentication change or override.
5. Install the candidate once through its absolute venv Python, with --no-cache-dir
   and --no-input. Record build inputs/dependencies actually used; source pinning
   does not pin every build dependency. Set only GOTOOLCHAIN=local,
   GIT_TERMINAL_PROMPT=0 and named run-local temporary/Go-cache locations as needed.
6. In the new module, verify both candidate entry points and both module --help
   forms. Use a child-only PATH prefix to confirm which resolves to the candidate;
   never edit shell startup files or activate it globally. Run go mod init for the
   named module and candidate atom init once. Compare the generated bootstrap to
   the frozen accepted bytes; retain manifest, instructions and actual baseline.
   An empty-module vet/test failure is expected and must remain visible, not
   relabeled as passing Go phase evidence. No Go application is added or downloaded.
7. Under the two new fixture-specific writer permissions below, write complete
   findings/decisions payloads frozen before execution, including a UTF-8 U+00E9
   byte-round-trip case. Compare exact output bytes/hashes. Repeat only read-only
   role/resource checks; no reinstall/re-init. Compare all named preservation
   snapshots, retain private evidence and produce candidate-delivery-report.md.

Verified pinned 1.0.107 help advertises --plugin-dir as loading a local plugin,
and plugin list as listing installed and --plugin-dir plugins. It does not
establish precedence or actual command invocation. Proposed command shapes;
record resolved absolute paths and exact argv/stdin in the report:

```text
<COPILOT> --no-auto-update --plugin-dir <ROOT>/plugin plugin list
<COPILOT> --no-auto-update --plugin-dir <ROOT>/plugin skill list
python3 -m venv <ROOT>/venv
<ROOT>/venv/bin/python -m pip install --no-cache-dir --no-input <ROOT>/package-source/tools
<ROOT>/venv/bin/atom --help
<ROOT>/venv/bin/atom-write-artifact --help
<ROOT>/venv/bin/python -m atom.cli --help
<ROOT>/venv/bin/python -m atom.artifact_cli --help
<ROOT>/venv/bin/atom init
```

ROOT is $HOME/atom-phase09-candidate-delivery-proof. Local-plugin metadata checks
run before module initialization, without discovering the generated module bundle.
Record the nine skills and three command-file names separately from any evidence
of runtime availability. If more than advertised CLI metadata is required to
answer the stated question, report Inconclusive rather than broadening the run.

Approval must explicitly include these new writer forms, each with working
directory <ROOT>/module:

```text
<ROOT>/venv/bin/atom-write-artifact specs/candidate-delivery-proof/findings.md
<ROOT>/venv/bin/python -m atom.artifact_cli specs/candidate-delivery-proof/decisions.md
```

Existing root/prior-fixture approvals do not transfer. Any writer refusal stops;
no generic editor or alternate path is a substitute.

## Verdicts And Stopping Rules

| Observation | Verdict |
|---|---|
| Unambiguous candidate plugin metadata; expected files; normally built candidate supplies both roles; init generates exact repaired bytes; writer round trips and named preservation checks match | Confirmed for candidate preparation/metadata and package-bundle delivery only |
| Fixed-condition evidence shows candidate shadowing/lost surfaces, wrong generated bytes, unusable installed role, wrong writer bytes or changed named existing installation/default | Refuted; stop and present evidence |
| Changed preconditions, uncertain metadata/scheme/provenance, download/build/permission failure, cap or incomplete evidence | Inconclusive; no assumed confirmation |

Stop at the first unexpected failure or elapsed cap. Terminate only owned exact
child processes; preserve partial files and diagnostics, with no automatic retry,
configuration repair, deletion or alternative loading mechanism. Ordinary package
builds/CLI metadata commands can write normal caches/logs; named fingerprint
checks are not an exhaustive filesystem sandbox or no-write guarantee.

## Exclusions, Records And Gates

No current installation refresh, global PATH/plugin/profile/authentication change,
package-source/runtime edits beyond the named reference overlays, force init,
original-attempt mutation, expense CLI implementation, commit, push or release.
Retain all candidate/proof files; no automatic cleanup. Preserve the first
Inconclusive attempt and frozen evidence. Redact credential-bearing output before
writing repository artifacts; retain complete raw streams privately.

A successful result would prepare an unpublished candidate, not prove cold-start
PEP 668 handling by an agent, three working command invocations, a passing Go
application, novice usability or Phase 09 completion. A later candidate rehearsal
would have working CLI prerequisites; its new recipe must disclose that boundary.

Present the report and stop for acceptance. Only then prepare a new frozen
participant recipe and seek separate live-rehearsal approval. A failed/incomplete
result needs a new decision, not an automatic revised experiment.

## Approval

After clarification of the pending run request and its relationship to Phase 09,
the developer replied exactly: "thanks!lets proceed". This authorizes this single
bounded preparation/validation run, its isolated provisioning and the two named
fixture-writer forms. It does not authorize another live rehearsal or publication.
