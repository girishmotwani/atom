# Implementation Evidence - New-Repository Setup Slice

Date: 2026-11-06. Base: `50622ab`.
The developer approved the setup design before these guidance changes.
No production runtime API was added or modified.

## Distribution Check Before Implementation

Command from `tools`:

```text
python -m pytest tests\test_onboarding.py::test_init_installs_the_canonical_repository_setup_reference -q --tb=short
```

Selected output, verbatim:

```text
tests\test_onboarding.py F                                               [100%]

================================== FAILURES ===================================
_________ test_init_installs_the_canonical_repository_setup_reference _________
tests\test_onboarding.py:181: in test_init_installs_the_canonical_repository_setup_reference
    assert canonical.is_file()
E   AssertionError: assert False
E    +  where False = is_file()
E    +    where is_file = WindowsPath('C:/Users/gimotwan/atom/skills/atom/references/repository-setup.md').is_file
```

This was an expected missing-reference failure, not evidence about human consent.

## Implementation

- Added one shared repository-setup reference with target inspection, concrete
  recommendations, explicit approval/refusal/revision, bounded execution and stop.
- Updated init, start and full-build setup prerequisites to reuse that reference.
  Start also distinguishes genuinely needed setup from unrelated missing state.
- Preserved matching-repeat, baseline capture and current command exit semantics.
- Mirrored canonical init/build/reference bytes into packaged assets.
- Updated README and workflow explanations; retained the Phase 09 example goal.
- Added one real onboarding distribution test comparing installed/package bytes
  with the canonical reference.

No runtime RED/GREEN, full Go gate or approval enforcement is claimed.

## Distribution Check After Implementation

Same command as above. Selected output, verbatim:

```text
tests\test_onboarding.py .                                               [100%]

============================== 1 passed in 0.52s ==============================
```

## Existing Behavior And Distribution Validation

Command from repository root:

```text
python -m pytest tools\tests\test_plugin.py tools\tests\test_onboarding.py tools\tests\test_init_repeat.py tools\tests\test_scaffold.py tools\tests\test_cli_state.py -q --tb=short
```

Selected output, verbatim:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 203 items
```

```text
======================= 203 passed in 71.80s (0:01:11) ========================
```

The full task-runner transcript is retained in the session files as
`phase-04-setup-tests.txt`. This is focused verification, not the full Python suite
or a live-agent setup trial.

Documentation/parity check output before the final start clarification, verbatim:

```text
checked 434 relative links across markdown files
all relative links resolve
Canonical/package bytes match: skills\init\SKILL.md
Canonical/package bytes match: skills\build\SKILL.md
Canonical/package bytes match: skills\atom\references\repository-setup.md
```

`git diff --check` exited 0 without output.

## Design Reconciliation And Remaining Gates

All fourteen numbered setup behaviors are expressed by the shared reference and
its entry integrations. The test spec distinguishes semantic guidance review,
unchanged command mechanics and distribution from unobserved live-agent behavior.
The start clarification applies the approved "selected task needs setup" boundary;
it is not an automatic missing-state router or a new command.

Actual approval/refusal/changed-proposal interaction remains pending a separately
agreed observation. Standalone review and remaining Phase 04 entry paths are not
implemented or approved by this slice. No commits, pushes, publication or paid
model calls occurred.


## Setup Integration On Merged Main - 2026-11-10

The developer approved "Approve setup integration and focused validation".
Continued in branch feat/atom-v1-setup-entry, worktree:
C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-continuation

Base: dd580342949a797acabcdbafe79e838d5ac38c00, containing merged #20 and #21.
The original checkout, all 43 pending working files and its empty index were
preserved unchanged. This worktree is intentionally retained as the continuation
workspace, not a disposable test fixture.

Applied the existing nine-file tracked setup delta using Git's three-way merge.
All files merged cleanly, including README. Transferred the two new setup
references through Git and 32 existing setup proof/audit artifacts through the
approved artifact writer. No production runtime, API, schema, command default,
new scaffolding or design behavior was added. Both upstream bootstrap references
remain unchanged. Retained #20's isolated Linux bootstrap/approval-budget wording
and #21's review-only routing and evidence disclosures.

The initial low-level reference transfer used Windows filesystem separators in
Git's internal cacheinfo path and was rejected before a file was written. Used
Git's repository-path syntax for that index operation, retaining native Windows
filesystem paths. No source was changed or lost, and no artifact-writer refusal
occurred. This was transfer plumbing, not a new experiment or a trial retry.

Fresh command from this worktree's tools directory:

```text
python -m pytest tests\test_plugin.py tests\test_onboarding.py tests\test_init_repeat.py tests\test_scaffold.py tests\test_cli_state.py tests\test_standalone_review_guidance.py tests\test_cli_review.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-continuation\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 305 items

tests\test_plugin.py ...........                                         [  3%]
tests\test_onboarding.py ......................                          [ 10%]
tests\test_init_repeat.py .............................................. [ 25%]
...................................................................      [ 47%]
tests\test_scaffold.py ............................                      [ 57%]
tests\test_cli_state.py ...............................                  [ 67%]
tests\test_standalone_review_guidance.py ........................        [ 75%]
tests\test_cli_review.py ............................................... [ 90%]
.............................                                            [100%]

======================= 305 passed in 67.12s (0:01:07) ========================
```

Repository Markdown verification from this worktree's root:

```text
python tools\check_links.py
checked 561 relative links across markdown files
all relative links resolve
```

Additional direct checks:

- Canonical/package bytes match for init, build, repository-setup, bootstrap,
  standalone-review and review skill (six pairs).
- Both bootstrap references still match this worktree's merged-main HEAD.
- git diff --cached --check exited 0 with no output.
- All 43 original pending working files still match pre-integration SHA-256 values;
  the original branch/index are unchanged.

These are focused Python/documentation and distribution checks, not a full-suite,
coverage, Go application atom-check or live-agent interaction claim. The approved
mechanical setup POC is reused within its stated Windows boundary; no POC rerun,
Go module creation at Atom's root, real model call, install/update, commit or push.

The content-filtered installed trial remains Inconclusive and paused. This result
does not prove live waiting/refusal/revision/stopping, installation delivery of the
new merged guidance, or complete Phase 04. Integration is ready for developer
acceptance before any separately approved reviewer batch or interaction work.


## Approved Source-Review Corrections - 2026-11-13

Documentation-only refinement; no Go runtime RED/GREEN claim. Both guidance findings
were approved before changes. Added real init bundle-byte coverage; original reports
and pre-correction context preserved. Exact fresh checks follow.

```text
Command: python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_init_repeat.py -q --tb=short
Cwd: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-continuation\tools
Imported source: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-continuation\tools\atom\__init__.py

============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-continuation\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 147 items

tests\test_onboarding.py .......................                         [ 15%]
tests\test_plugin.py ...........                                         [ 23%]
tests\test_init_repeat.py .............................................. [ 54%]
...................................................................      [100%]

============================ 147 passed in 53.20s =============================

Exit code: 0
```

```text
Command: python tools\check_links.py

checked 561 relative links across markdown files
all relative links resolve

Exit code: 0
Canonical/package bytes match: skills\init\SKILL.md
Canonical/package bytes match: skills\atom\references\repository-setup.md
```

git diff --check exited 0. Parent flow reconciliation and limitations are in
setup-review/guidance-corrections.md; no new multi-model review, installed treatment
refresh, live case, commit or publication. Corrected outcome awaits acceptance.


## Correction Gate Accepted - 2026-11-13

Developer selected 'Accept corrections; keep Phase 04 open'. The two source-guidance
findings are accepted as addressed. This accepts the parent-verified corrections
with their recorded limits, not a clean live rehearsal or fresh multi-model review.
Phase 04 remains open; installed-preview refresh, further live trials, other entry
boundaries and shipping retain separate gates. No commit/push/PR is authorized.


## Bounded Evidence Accepted - 2026-11-17

Developer selected 'Accept bounded evidence; no more reruns'. This accepts only
the actual recorded setup behavior and limitations, not three clean protocol
passes. Module+Atom and Go-only protocol results and original aggregate remain
Inconclusive; missing-command case remains Confirmed. No historical output,
missing checkpoint or budget is rewritten. No further rerun of these cases.

Setup observation/report gate is closed with those limits. Persistent permission
saving remains unverified and parked, not an accepted proof or prerequisite for
this accepted setup evidence. Other Phase 04 entry boundaries remain open. No
commit, push, PR, source change, extra trial, publication or Phase 04 completion
was authorized by this acceptance. Existing evaluation/repair discovery stays parked.


## Publication Context - 2026-11-17

The preceding sections preserve the dated implementation/approval history, including
then-pending gates. The setup corrections and bounded installed observations were
subsequently accepted. See [current evidence and limits](setup-evidence.md),
[review provenance](review.md), [shipping verification](verification.md) and
[publication decisions](decisions.md). References to the original setup-review
archive name local historical records, not additional files published in this PR.
The combined instructions retain newer upstream bootstrap guidance; the historical
live observations do not cover those combined bytes.
