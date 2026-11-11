---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-10"
status: "accepted-local-guidance-repair"
scope: "five shipped documentation files; no runtime or installed-plugin change"
---

# General Onboarding Guidance Repair Validation

## Result

Implemented the approved prerequisite-flow-repair-spec.md in exactly the five
shipped documents. The focused existing selector passed 34 tests. After final
semantic refinements to bootstrap/README, the four directly affected documentation
contract cases passed again. Both packaged copies match their canonical bytes;
531 relative documentation links resolve and git diff --check exits 0.

This is local guidance/packaging validation, not a successful live onboarding or
Phase 09 completion. Existing installation/boundary evidence and the newly
accepted Windows/Ubuntu discovery receipts retain their original limits. No
production RED/GREEN loop is claimed: the approved adaptation uses existing tests
and factual/semantic review because runtime source, APIs and configuration did
not change.

## Changes And Semantic Review

- Main init skill now states active-client identity, Go availability, reference-
  before-execution ordering, absent/hidden/broken choices, consent and refusal
  stops directly. It retains existing deterministic init/no-op/force behavior,
  receipt reads, actual baseline disclosure and Windows setup-path opt-in.
- Shared bootstrap resolves availability before executing roles, queries package
  presence before module help, checks the known venv safely, retains working
  forms, and separates expected absence from real errors. Git/venv/ensurepip
  prerequisites are checked before asking consent to install Atom. Existing
  isolation, configuration, collision, source and permission safeguards remain.
- README exposes existing minima and the plugin/package distinction near the
  front; corrects automatic-install and fixed-prompt expectations; qualifies
  active-client/alias discovery and preserves the historical approval ledger.
- Both packaged source pairs were synchronized. No runtime, test, schema, version,
  dependency, shell script or plugin-command file changed.

Walked all fourteen behaviors against the final canonical diff and the test-spec
mapping. In particular: already-established forms avoid rediscovery; missing
entry points never need execution; package absence is data; found-but-failing or
partial setups stop rather than trigger reinstall; unknown/unsupported client
identity needs a developer decision; a writer refusal stops even under a zero-
status wrapper. The normal receipt/no-op path and failing empty-module baseline
were preserved. This reviews what the instructions say, not agent adherence.

Final semantic refinements moved Git/venv prerequisite checks before the Atom
installation-consent question and removed README's promise that no further user
input is needed. They clarify the approved order without changing its scope.
No material spec deviation, test weakening, new fixture or installer run occurred.

## Focused Existing Tests

From tools, actual command (exit 0):

```powershell
python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

Verbatim captured output:

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

============================= 34 passed in 7.94s ==============================
```

## Final Documentation Contract Recheck

After the final bootstrap/README wording refinements, from tools (exit 0):

```powershell
python -m pytest tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

Verbatim captured output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests\test_artifact_cli.py .                                             [ 25%]
tests\test_pathsetup.py ...                                              [100%]

============================== 4 passed in 0.23s ==============================
```

## Final Parity, Links, Whitespace And Scope

At root, compared SHA-256 for each changed canonical/package pair, then ran
python tools\check_links.py and git diff --check. Checked tracked paths against
the five approved documents and existing phase-evidence directory. Actual output
(exit 0), copied verbatim:

```text
Byte parity verified: skills\init\SKILL.md (15E4169B5BE2896DD3D3802129B18D6BC81C48E9C2E956F48CD199AB23AF52F8)
Byte parity verified: skills\atom\references\bootstrap.md (E962C45C44A76A223647328F5861DA402EF4680C2771B4BEC9C8DE3FC60DEF33)
checked 531 relative links across markdown files
all relative links resolve
git diff --check: exit 0
Tracked-change scope verified: five shipped documentation files plus phase evidence only.
```

The tracked scope check was supplemented by git status --short: untracked files
are the known phase evidence, not new runtime/test/script files. No root Go module
exists; no artificial root atom check was run. Existing no-op/init tests use their
own fixtures, not the stopped participant module. No dependency installation was
needed for these validation commands.

## Remaining Findings And Delivery Boundary

Actual agent refusal/consent adherence, failing-help routing and interactive alias
acceptance were not newly exercised. The discovery check encountered no failing
commands; these tests cannot turn that into error-path or all-client proof.
Instructions are not hidden runtime enforcement. The pre-existing manual-install
platform recipes remain unchanged under the approved scope and are not newly
validated by this repair.

No existing plugin installation or local module bundle was refreshed. The stopped
Ubuntu trial, its files/baseline and its Inconclusive verdict remain unchanged.
No model calls, installs, profile/default changes, commits, pushes or merges ran.
Accepting this local implementation does not authorize delivery refresh or a new
live trial. Both need their own scoped decisions and fixed provenance.

## Local Repair Acceptance Recorded

The developer selected exactly: "Accept the local repair; keep delivery and rehearsal gated".
No publication, installed-plugin refresh, model review or new live trial is authorized.
## Subsequent Review Qualification: Semantic Repair Is Not Yet Complete

The separately approved two-model review found an unchanged automatic-install
promise in README.md:602-609. Both reviewers reported the inconsistency. The
semantic review above missed that directly coupled paragraph, so its claim that
README automatic-install expectations were corrected is incomplete; the fourteen-
behavior walkthrough must not be read as proof of full spec compliance. The
recorded test outputs, parity and link results remain real within their scope.
See prerequisite-flow-repair-review.md for merged findings, the unexecuted Minor
package-collision case and Opus's incomplete full-context reads. No source fix or
fresh live validation has occurred. Earlier local acceptance remains historical;
review triage, delivery and rehearsal are not thereby approved.
## Approved README Finding Fix: Local Validation

The developer selected "Fix the README inconsistency now", then "continue".
Corrected README's Run It paragraph to reuse healthy tools and ask before any
missing-tool installation, preserving broken/unsafe setups. The example now uses
the available discovery beat with an explicit client-registration caveat; existing
work can use the available start skill without assuming its alias works. Removed
the coupled "certain path" / "slash command is exact" promises. The recorded
25-trial result, historical correction and ledger link remain unchanged; their
conclusion is explicitly limited to that tested setup.

Only README source changed for this fix. The bootstrap query and both canonical/
packaged instruction pairs are unchanged. This implements already approved spec
behaviors 13/14; no new runtime behavior, dependency, installer or API is designed.
No new tests were added and no production RED/GREEN cycle is claimed.

From tools, actual command (exit 0):

```powershell
python -m pytest tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

Verbatim output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_pathsetup.py .                                                [100%]

============================== 1 passed in 5.40s ==============================
```

At root, ran python tools\check_links.py and git --no-pager diff --check; both
exited 0. Actual output:

```text
checked 535 relative links across markdown files
all relative links resolve
git diff --check: exit 0
```

Final README SHA-256 from Get-FileHash:

```text
1390ECFC411EB065CEA74FC41383EFA5DBA611B79E6AE47DBA3DE6F5C369B5D1
```

A direct read of README lines 599-663 confirmed the edited installation, handoff
and routing conclusion on disk. Existing broader test evidence is reused within
its original scope, not counted as newly run. No root Go check is claimed.

The Major README finding is locally fixed and validated, not independently
re-reviewed. The Minor package-detection finding and Opus full-context gap remain
open. No extra reviewer, live rehearsal, installed-content refresh or publication
occurred. This validation does not mark the overall review or Phase 09 complete.
