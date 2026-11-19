---
project: "ci-reliability"
date: "2026-11-18"
status: "review-triaged-hosted-ci-pending"
---

# CI Repair Findings

## Go Control Boundary Leaks Host Installation Into A Gate-Order Test

On current main ef7fea43119564dfabb18ab9faed68919e1500c9, CI run 44342921071's
Ubuntu Python 3.12 job reports:

```text
FAILED tests/test_review_continuation.py::test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates[False-expected_gate_calls0] - atom.review.ControlToolchainError: PATH Go 1.23.12 is below module minimum 1.27.0
================= 1 failed, 1674 passed, 52 skipped in 42.87s ==================
```

Source: tools/tests/test_review_continuation.py:285-329. The test scripts the
selected 1.26.9 distribution and build failure, sets go.mod minimum 1.27.0, and
stubs control resolution only for strict mode. In default mode production reads
the actual PATH distribution VERSION before FakeRunner probes. CI installs Go
1.23 through .github/workflows/ci.yml, so the production fail-closed check rejects
it before the gate-order test reaches its expected exception assertion.

Production boundary: tools/atom/review.py:714-788. Existing tests already cover
incompatible/missing/unverified controls; do not weaken that rejection or
upgrade CI's compiler merely to conceal a non-hermetic test. The exact targeted
regression passes both variants unchanged on native Windows locally. A controlled
CI-like failing reproduction remains to be run before a repair spec.

## Windows CI Has Additional Path-Identity Failures

The same run's Windows Python 3.12 job reports:

```text
=========== 15 failed, 1710 passed, 2 skipped in 124.63s (0:02:04) ============
```

Sampled failures include both parametrizations of
 test_pr_context_is_captured_before_preparation_from_launch_directory and
 test_cli_freezes_launch_rules_before_pr_preparation in test_cli_pr_review.py,
plus test_native_cli_uses_real_checkout_and_cleans_it in
 test_pr_checkout_integration.py and test_independent_clone_and_pinned_checkout
in test_pull_request.py. Assertions compare long C:/Users/runneradmin/... paths
with short C:/Users/RUNNER~1/... paths. The Go-control failure also appears.

These excerpts establish additional failing cases, not whether fixture assertions
or production canonicalization is wrong, nor the cause of all 15 failures.
No Windows production change, assertion normalization or skip is approved or
performed. Broader diagnosis needs the scope decision recorded in decisions.md.

## Current Limits

No CI fix exists yet. The local two-case pass does not make main green, reproduce
the CI host or justify ignoring remaining failures. No full local suite, new
remote CI execution, live model review, setup change, commit or publication ran.

## Complete Current-Main Test Failure Classification

Captured logs for all six CLI jobs of run 44342921071, then classified the exact
FAILED test summary lines. No additional CI rerun was triggered.

| Job | Go-control error | Path assertions | Other failures |
| --- | ---: | ---: | ---: |
| Python 3.10 Ubuntu | 1 | 0 | 0 |
| Python 3.12 Ubuntu | 1 | 0 | 0 |
| Python 3.10 macOS | 1 | 14 | 0 |
| Python 3.12 macOS | 1 | 14 | 0 |
| Python 3.12 Windows | 1 | 14 | 0 |
| Python 3.10 Windows | 1 | 14 | 6 |

Path assertion family affects ten distinct test names, with parametrizations
accounting for 14 cases per affected job. macOS compares /private/var/... with
/var/...; Windows compares runneradmin with RUNNER~1. Production intentionally
resolves the selected module in tools/atom/pull_request.py:270; checkout test
collaborators retain the uncanonicalized clone destination captured from mkdtemp.
Further controlled reproduction and contract review is needed before choosing
between a fixture correction and a production path change.

### Windows Python 3.10 Child Processes

Exact additional FAILED test names and messages from the captured Windows Python 3.10 job. Observed cases:

- tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent
- tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext
- tests/test_runner.py::test_environment_is_copied_before_launch
- tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings
- tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True]
- tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True]

First four report:

```text
AssertionError: Fatal Python error: _Py_HashRandomization_Init: failed to get random numbers to initialize Python
```

The timeout case reports COMPLETED rather than TIMED_OUT; the final case has a
missing child-ready file. They may share a child startup issue but this is not
proven. Do not mask them with retries/skips, weaken runner environment semantics,
or drop Python 3.10 support. Investigate only after the new scope decision.

### Go Failure Reproduced

The unchanged targeted test with process-local synthetic CI Go metadata reports:

```text
E   atom.review.ControlToolchainError: PATH Go 1.23.12 is below module minimum 1.27.0
================= 1 failed, 1 passed, 65 deselected in 14.33s =================
```

Complete diagnostic command and exact failure section are in decisions.md.

## Diagnosis Completed For The Observed Failure Families: 2026-11-19

The controlled Go failure was already reproduced. A CI-shaped parent-alias
diagnostic now reproduces all 14 path assertions; a canonical collaborator
control passes all 14. Existing Python 3.10.11 as the child reproduces all six
Windows child failures; adding only its missing SystemRoot prerequisite passes
all six unchanged assertions. A separate native Windows probe succeeds with a
truly empty mapping and no inherited parent-only sentinel.

This supersedes the earlier "remains to be run" and unproven-common-cause
statements for these bounded reproductions. See [diagnosis-report.md](diagnosis-report.md)
for exact evidence, the initial overbroad leaf-alias diagnostic, its correction,
and safe cleanup. The failed initial control is not hidden or counted as proof.

The defects are test assumptions: host control resolution in an order test,
lexical rather than canonical expected checkout paths, and Python startup
prerequisites omitted from restricted child fixtures. No production weakening
is warranted by these results. The actual empty-environment test must not be
"fixed" by adding SystemRoot to its mapping.

## Remaining Verification Limits

No repair implementation exists. [design-spec.md](design-spec.md) is draft and
awaits developer approval. No full local suite or fresh remote matrix has run.
The child experiment runs pytest on Python 3.13 with Python 3.10.11 as the
child; it is not a full Python 3.10 suite. Native Windows path reproduction is
not a fresh macOS run. Exact proposed edits still need verification.

The original captured failures are explained within these limits; this is not
proof that current main or a future repaired branch is green. No additional
unexplained failure family was discovered in the corrected reproductions.

## Spec Approval Recorded: 2026-11-19

Developer accepted the test-only spec and regression-based evidence. This
supersedes the draft/awaiting-approval statements above. The repair remains
unimplemented and all local/full-matrix verification limits still apply.

## Local Implementation Verified; Hosted CI Still Open

The approved test-only repair is implemented, superseding earlier unimplemented
status statements. All controlled failure conditions pass after the exact edits;
the six-module suite reports 245 passed, 2 skipped and the full Windows Python
3.13 suite reports 1722 passed, 5 skipped (95% measured coverage). No new in-scope
finding. See implementation-evidence.md for exact output and source hashes.

The six hosted Python/platform combinations remain unrun for these bytes.
Embedded 3.10-child checks are not a full native 3.10 suite. Local success does
not close the CI-restoration finding or establish a fresh macOS/Linux result.
Implementation acceptance, independent atom review and publication remain pending.

## Implementation Acceptance Recorded

Developer accepted the verified fixture repair and approved the explicit bounded
Atom review followed by a PR only on a clean result. This supersedes pending
implementation acceptance, not the unrun independent review or hosted matrix.
No new findings. No paid review or publication has run yet.

## Independent Review Completed; Nit Triage Gate

Actual atom review completed with two usable independent responses and no
partial/unavailable/unparsed results. Codex returned no findings; Opus returned
four low-severity comments at three locations. See review.md for every exact
message, participation, evidence hashes and individual proposed disposition.

Two comments identify wording/redundancy nits: the helper docstring overstates
the lack of parent inheritance, and the strict-arm counter is vacuous although
the original pytest.fail sentinel still enforces the contract. Proposed: defer
both without changing behavior or the reviewed snapshot.

Two further comments propose contextualizing the existing explicit SystemRoot
KeyError and supporting caller override of that prerequisite. Proposed: reject
the claimed contract violations because indexed failure meets the approved
explicit-failure contract and no caller supplies that prerequisite; parent
SystemRoot is the explicitly specified helper behavior.

These dispositions await the developer; nothing was silently discarded.
Publication is paused, not clean-path authorized by an agent's own triage.
No code changed after acceptance, no fresh ship gate or hosted matrix has run,
and no commit, push or PR exists yet.


## Developer Accepted The Review Dispositions

Two nits are explicitly deferred and two SystemRoot contract claims
rejected with the recorded reasons, now approved by the developer.
No functional review blocker remains. The fresh full Python ship gate
exited 0 with unchanged source; exact output is in implementation-evidence.md.
The deferred wording/redundancy nits and unrun hosted matrix remain open.
