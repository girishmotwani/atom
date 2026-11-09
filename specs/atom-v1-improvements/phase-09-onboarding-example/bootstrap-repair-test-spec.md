---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
design_spec: "bootstrap-repair-spec.md"
date: "2026-11-09"
status: "accepted"
---

# Bootstrap Repair Documentation Test Spec

## Scope And Evidence Adaptation

Implement only the [approved prerequisite spec](bootstrap-repair-spec.md), after
the [accepted boundary result](bootstrap-boundary-report.md). This is not the
final example's test-spec.md and does not complete Phase 09.

No runtime code, Go types, new tests or scripts are needed. Map each documented
behavior to semantic review, existing documentation/packaging tests and the
accepted actual command evidence. Do not claim a production RED/GREEN loop or
that string/parity tests establish agent compliance.

## Toolchain Redundancy Audit

None - no proposed case was unfailable. No existing test is removed or weakened.
Go nil/type/overflow/switch/race properties are not applicable to prose-only
changes. Silent failure matters here as a false success/absence claim: manually
check each failure branch rather than inventing Go tests of documentation.

## Coverage Map

Numbers refer to the approved spec, not new runtime enforcement.

| Behavior | Required review/check | Evidence and limit |
|---|---|---|
| 1 | Both successful entry points stop discovery; only a missing role continues | Review Step 1; reuse proof demonstrates working forms, not agent route selection |
| 2 | Supported existing Linux python3 first; supported python fallback; visible missing/unsupported stop | Review Step 2 and Python >=3.10 requirement; accepted run covers Python 3.12.3, not every fallback |
| 3 | Needed module checks precede installs; bind successful forms; partial/unexpected failure stops | Review Step 2; existing artifact/bootstrap test preserves Windows forms and source-read limits |
| 4 | Only known safe shared venv considered; verify/reuse; preserve unsafe/partial destination | Review Step 3; accepted run covers fresh install then read-only reuse, not unsafe layouts |
| 5 | Explicit absence plus consent before exclusive safe creation; collision stops | Review Step 4; creation was approved and real, not a concurrency/unsafe-path experiment |
| 6 | Venv Python pip; scheme checks precede install; no overrides/activation/system changes | Review Step 4 against accepted normal-user controls and command argv; active redirects untested |
| 7 | Both roles verified after install; exact forms retained; diagnostics/no retry on failure | Review Step 4; actual help and UTF-8 writer results, not help alone |
| 8 | Windows opt-in block unchanged; printed absolute commands authoritative; no re-probe | Existing parametrized path-setup documentation test and README session-limitation test; compare original block bytes |
| 9 | Canonical/package equality; permissions, baseline disclosure and source-read limits retained | Existing plugin/onboarding/artifact documentation tests; semantic review and original-evidence hashes |

README review: clarify plugin versus Python commands, link to the bootstrap
reference, and label the captured approval count as historical without rewriting
its table, interaction ledger or claims about that captured run.

## Edge And Error Review

Missing/unsupported interpreter, broken help command, non-absence import error,
one working/one missing role, partial package, unowned/symlinked prefix/ancestors,
creation collision, missing venv/ensurepip, install-scheme redirect/uncertainty,
download failure and post-install role failure must preserve existing state and
stop with the actual diagnostic. Missing-key exit 1 is not an unexpected pip
failure only when its diagnostic establishes that exact absence.

Preserve complete UTF-8 stdin and repository-specific writer approval. An empty
module's failing vet/test baseline must not be reclassified as passing. Concurrent
installers are unsupported; do not claim locking or broad safety enforcement.

## Existing Automated Checks

From tools:

```powershell
python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

From the repository root:

```powershell
python tools\check_links.py
git diff --check
```

Also verify canonical/package byte parity, changed-file UTF-8/LF, unchanged
Windows opt-in block and historical approval table, and original recipe/recording
hashes. These are document integrity checks, not new runtime unit tests.

## Baseline And Non-Goals

Reuse the recorded untouched Python baseline and two accepted command proofs;
do not install again. No root Go module exists, so atom check is not applicable
to this documentation-only implementation. No production RED/GREEN or coverage/
race claim is made; real initial-baseline output remains in the accepted reports.

No model review batch, live retry, installed-plugin/local-bundle refresh, commit,
push or release. Source changes alone do not deliver new instructions to the
installed plugin. Retain the original Inconclusive experienced-user trial.

## Validation Results

All nine mapped behaviors were checked against the actual canonical diff,
its byte-identical packaged copy, the approved spec and accepted command report.
The three-document implementation preserves the Windows opt-in block and
historical approval table verbatim. No material spec change was needed.

The source recipe keeps the canonical moving public URL; its command evidence
uses the recorded source pin, not a guarantee about future source versions.
Existing non-Linux working-package discovery/Windows opt-in remains intact;
no unproven native Windows/macOS fresh-install recipe is added.

All missing/partial/unsafe/error branches in the map have explicit stop/preserve/
diagnostic instructions. The known-env and fresh-env paths cannot authorize
reinstallation over a working or incomplete package. Scheme checks precede the
sole venv-Python install, and help verification binds both roles without PATH
changes. These are reviewed instructions, not proof of actual model compliance.

The focused existing checks, from tools, exited 0:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 34 items

tests\test_onboarding.py ...................                             [ 55%]
tests\test_plugin.py ...........                                         [ 88%]
tests\test_artifact_cli.py .                                             [ 91%]
tests\test_pathsetup.py ...                                              [100%]

============================= 34 passed in 8.63s ==============================
```

The first source-document link check, from the repository root, exited 0:

```text
checked 491 relative links across markdown files
all relative links resolve
```

`git diff --check` exited 0. Additional integrity checks returned:

```text
PASS: canonical and packaged bootstrap bytes identical
PASS: Windows opt-in block and historical approval table unchanged
PASS: three source documents UTF-8/LF; no production code or tests changed
PASS: original Inconclusive trial and frozen recipe/recording identities preserved
```

No Go production RED/GREEN loop, atom check success, fresh install, live retry or
model review batch is claimed. Phase 09 remains open. Installed plugins and
already-onboarded module bundles still contain their previous guidance.

## Implementation Acceptance Gate

- [x] All nine documented behaviors mapped and semantically reviewed.
- [x] Existing scoped tests passed without modification or weakening.
- [x] Canonical/package equality, Windows/history preservation and encoding checked.
- [x] Original trial and approved command evidence preserved.
- [x] No runtime source, schema, production tests or automation scripts changed.
- [x] Developer accepts this documentation repair; delivery/rehearsal remain gated.


## Documentation Repair Accepted: 2026-11-09

The developer selected exactly:
"Accept documentation repair; keep delivery and rehearsal gated".

The prerequisite source-document repair is accepted. Its final post-artifact link
check exited 0 with this output:

```text
checked 496 relative links across markdown files
all relative links resolve
```

The final whitespace check also exited 0. No material spec change, production
RED/GREEN claim or test weakening. This acceptance does not authorize delivery
or refresh of installed plugins/module bundles, a new live rehearsal, commit,
push or release. The original trial remains Inconclusive; Phase 09 is still open.

## Fresh Pre-Publication Verification: 2026-11-09

After explicit commit/push/PR authorization, repeated the same approved focused
command on independent fix/ubuntu-atom-bootstrap, based on public main after
its identical source tree was verified. Exit 0; actual output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 34 items

tests\test_onboarding.py ...................                             [ 55%]
tests\test_plugin.py ...........                                         [ 88%]
tests\test_artifact_cli.py .                                             [ 91%]
tests\test_pathsetup.py ...                                              [100%]

============================= 34 passed in 14.46s =============================
```

This is documentation/packaging verification, not a full-suite or root Go gate.
Canonical/package bytes and preserved Windows/history/original-trial identities
were rechecked before staging. All private executor/raw-terminal files remain
outside the committed set. No source implementation changed after this repeat.
