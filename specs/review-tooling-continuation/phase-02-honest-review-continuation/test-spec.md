---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
design_spec: "design-spec.md"
date: "2026-11-03"
---

# Test Spec

The implementation is Python under `tools/`; use pytest rather than the Go test commands shown in the generic template. Continuation behavior is exercised through `FakeRunner`/`ScriptedRunner` and does not invoke reviewer models, network services, or installations. The existing `test_review_formatting.py` integration coverage uses real Git and gofmt.

## Toolchain Redundancy Audit

None — no proposed case was unfailable. The implementation and tests are Python; Go compiler and vet guarantees do not prove these behaviors.

Silent-failure coverage — the Go-language examples are not applicable as stated. Python does permit silent wrong results and ignored exceptions; behavior tests below exercise decision outputs, preserved evidence, and command admission rather than duplicating language guarantees.

| Property | Applies here? | Test name or why not |
|---|---|---|
| Empty string where a value is required | Not applicable as a Go `string` rule | Module-version and CLI invalid-input tests cover empty/malformed values that Python accepts. |
| Ignored `error` return | Not applicable; Python exceptions are used | Control selection/runner failures must propagate to a blocking result (B5, B13). |
| Typed nil stored in an interface | Not applicable; no Go interfaces in this implementation | None. |
| Non-exhaustive switch over enum-like constants | Not applicable; no Go switch in this implementation | None. |
| Integer overflow wrapping silently at runtime | Not applicable to the version comparison contract | Version ordering tests cover the supported Go version tuple. |
| Nil map write / nil pointer deref / variable index or divisor | Not applicable; no Go map/pointer implementation | None. |

## Coverage Map

| Behaviour # | Test name(s) | Priority | Status |
|---|---|---|---|
| 1 | `test_pinned_review_uses_selected_gates`; `test_eligible_control_success_preserves_selected_and_control_evidence` | P0 must | passed |
| 2 | `test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates`; `test_strict_toolchain_cannot_be_combined_with_skip_toolchain`; `test_control_go_version_conflicts_fail_before_commands`; `test_control_go_version_requires_selected_toolchain_pin` | P0 must | passed |
| 3 | `test_module_minimum_version_requires_one_unambiguous_go_directive`; `test_continuation_candidate_requires_verified_lower_selection`; `test_continuation_candidate_requires_module_and_explicit_selection` | P0 must | passed |
| 4 | `test_candidate_format_failure_stops_before_build`; `test_candidate_gate_order_and_build_short_circuit`; `test_only_proven_selected_failure_shape_is_eligible`; `test_selected_build_timeout_does_not_resolve_or_run_control` | P0 must | passed |
| 5 | `test_default_control_resolves_and_verifies_direct_path_distribution`; `test_control_version_override_uses_exact_local_resolution`; `test_default_control_rejects_incompatible_path_without_searching_other_locations`; `test_default_control_missing_from_path_does_not_search_other_locations`; `test_default_control_rejects_unverified_path_executable` | P0 must | passed |
| 6 | `test_control_runs_only_bounded_gates_once`; `test_control_format_gate_uses_selected_changed_file_scope`; `test_control_gate_failure_blocks_models`; `test_skipped_control_gate_blocks_models` | P0 must | passed |
| 7 | `test_review_snapshot_identity_covers_only_selected_go_files`; `test_source_change_after_selected_checks_blocks_before_models`; `test_unrelated_source_change_does_not_block_control_review`; `test_missing_review_snapshot_scope_blocks_before_selected_checks`; `test_review_snapshot_identity_rejects_missing_selected_files`; `test_review_snapshot_identity_rejects_unreadable_selected_files`; `test_review_snapshot_identity_rejects_selected_symlinks`; `test_review_snapshot_identity_rejects_path_replaced_before_open`; `test_review_snapshot_identity_rejects_non_regular_selected_paths` | P0 must | passed |
| 8 | `test_pinned_review_uses_selected_gates`; strict-mode test confirms control resolution is not attempted | P0 must | passed |
| 9 | `test_eligible_control_success_preserves_selected_and_control_evidence` | P0 must | passed |
| 10 | `test_eligible_control_success_preserves_selected_and_control_evidence` checks the actual prompt caveats | P0 must | passed |
| 11 | `test_eligible_control_success_preserves_selected_and_control_evidence`; existing review output schema tests | P0 must | passed |
| 12 | `test_degraded_review_prints_warning_and_exits_check_failed` | P0 must | passed |
| 13 | `test_control_gate_failure_blocks_models`; `test_skipped_control_gate_blocks_models`; `test_source_change_after_selected_checks_blocks_before_models`; `test_source_identity_failure_is_stderr_only_and_nonzero` | P0 must | passed |
| 14 | `test_review_cli_captures_project_toolchain_policy`; `test_control_go_version_conflicts_fail_before_commands`; `test_control_go_version_requires_selected_toolchain_pin`; `test_selected_build_timeout_does_not_resolve_or_run_control` | P0 must | passed |

Mapping notes:

- B1 and B8 preserve the existing normal selected-toolchain path; strict behavior is separately checked to retain all-gates behavior and never resolve control.
- B4 distinguishes completed non-zero builds from timeouts, missing tools, and runner errors, and verifies formatting short-circuits before build.
- B5 covers direct PATH discovery, exact local override, missing/incompatible PATH candidates, below-minimum overrides, and executable verification failure.
- B6/B13 cover each bounded gate, command lifecycle failures, skipped control evidence, source mutation, and the no-model boundary.
- B7 tests pass for selected-only reads, selected mutations, unrelated mutations, missing scope, and selected-path failure cases. The POC remains bounded evidence only and does not establish production Git capture integration.
- Behaviors 1-6 and 8-14 have passing coverage, including the approved B6 control-format scope amendment. The B7 snapshot-only amendment is approved and its tests pass. Initial strict-CLI RED evidence is retained below; some later edge-case tests were added after their implementation existed and are recorded as a TDD process deviation in `decisions.md`.

## Test Cases

For existing behaviors, the table lists implemented coverage. The B7 snapshot-only identity tests are implemented; RED/GREEN evidence is recorded below. A TDD process deviation for several cases is recorded in `decisions.md`. The first strict-CLI RED outputs are retained below. Later edge-case assertions added after implementation are called out in `decisions.md` rather than presented as witnessed RED/GREEN loops.

| Behavior | Implemented test coverage |
|---|---|
| B1/B8 normal selected checks and strict mode | `test_pinned_review_uses_selected_gates`; `test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates` |
| B2 strict option and conflicts | `test_strict_toolchain_cannot_be_combined_with_skip_toolchain`; `test_control_go_version_conflicts_fail_before_commands`; `test_control_go_version_requires_selected_toolchain_pin`; strict-mode parameter in `test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates` |
| B3 module/version eligibility | `test_module_minimum_version_requires_one_unambiguous_go_directive`; `test_continuation_candidate_requires_verified_lower_selection`; `test_continuation_candidate_requires_module_and_explicit_selection` |
| B4 selected gate shape and order | `test_candidate_format_failure_stops_before_build`; `test_candidate_gate_order_and_build_short_circuit`; `test_only_proven_selected_failure_shape_is_eligible`; `test_selected_build_timeout_does_not_resolve_or_run_control` |
| B5 control selection | `test_default_control_resolves_and_verifies_direct_path_distribution`; `test_control_version_override_uses_exact_local_resolution`; missing, incompatible, and unverified PATH control tests |
| B6 bounded controls | `test_control_runs_only_bounded_gates_once`; `test_control_format_gate_uses_selected_changed_file_scope`; `test_control_gate_failure_blocks_models`; `test_skipped_control_gate_blocks_models` |
| B7 changed-review-file identity | selected-only read/mutation tests; selected path failures including replacement between path check and open; missing-scope blocking; unrelated mutation continuation; selected-mutation integration blocking |
| B9/B10/B11 degraded evidence | `test_eligible_control_success_preserves_selected_and_control_evidence` asserts retained gate evidence, prompt caveats, Markdown, JSON v3, and command lifecycle evidence |
| B12 degraded CLI result | `test_degraded_review_prints_warning_and_exits_check_failed` |
| B13 fail closed | control command lifecycle failures, skipped control, PATH selection failures, source change, and `test_source_identity_failure_is_stderr_only_and_nonzero` |
| B14 skip semantics | `test_review_cli_captures_project_toolchain_policy` asserts no degraded/control evidence; control override conflict is rejected before commands |

## Edge Cases And Error Paths


| Case | Expected | Test coverage |
|---|---|---|
| Missing module, request, observed version, malformed minimum, or selected version at/above minimum | Blocks continuation | module parser and continuation candidate parameterized tests |
| Selected format failure, build timeout/missing/runner error, or non-candidate required result | Blocks control | candidate formatting/order tests and selected timeout integration test |
| PATH control missing, incompatible, or unverifiable; exact override unavailable or below minimum | Blocks without substitution | PATH and exact override resolver tests |
| Control gate failure, timeout, missing tool, runner error, or skipped result | Blocks model invocation | parameterized control failure and skipped-control integration tests |
| Unchanged module files are unformatted while selected changed Go snapshots are formatted | Control `fmt` evaluates only the same frozen changed-file snapshots; unrelated files do not change its result | `test_control_format_gate_uses_selected_changed_file_scope` |
| Selected changed Go-file path missing, unreadable, symlinked, non-regular, changed, or replaced between path validation and open | Scoped identity unknown; blocks | `test_review_snapshot_identity_rejects_missing_selected_files`; `test_review_snapshot_identity_rejects_unreadable_selected_files`; `test_review_snapshot_identity_rejects_selected_symlinks`; `test_review_snapshot_identity_rejects_path_replaced_before_open`; `test_review_snapshot_identity_rejects_non_regular_selected_paths`; selected-mutation integration test |
| File outside the captured changed Go-file set changes | Identity unchanged; control may proceed if all other criteria pass | `test_unrelated_source_change_does_not_block_control_review` |
| `--strict-toolchain` with skip/control override, or control override with skip | Usage error before commands | CLI option-conflict tests |
| `--skip-toolchain` without control override | Preserves skip behavior and is not degraded | project toolchain policy CLI test |

Error-path audit:

- Constructor errors covered: no new public Python constructor is planned; invalid control version and CLI option parsing are covered.
- Dependency errors covered: PATH resolution, local Go probes, bounded gate runner, and filesystem reads. Whole-tree traversal is removed; selected-path read errors remain blocking.
- Context cancellation or timeout covered: control/selected command timeouts are blocking; no new async task or cancellation mechanism is introduced.
- Invalid input covered: malformed module minimum, invalid/empty exact control version, and conflicting CLI options.

## Concurrency Tests

None — no new concurrent work is introduced. Model-call concurrency remains after the selected/control decision and is governed by the existing `--concurrency` path.

## Fixtures And Helpers

- Reuse `tests.test_go_selection.distribution` and `distribution_runner` to build verified local Go fixtures.
- Reuse `FakeRunner` and the CLI's `ScriptedRunner` for process/model boundaries.
- Add focused continuation fixture helpers only when they keep setup deterministic and visible; use temporary source trees and synthetic PATH values.

## Review-Finding #2 Test Obligations (Implemented)

- `test_review_snapshot_identity_covers_only_selected_go_files`: create a selected changed Go file plus unrelated data; prove identity reads only the selected path, ignores unrelated-file mutation, and changes when the selected file changes.
- `test_source_change_after_selected_checks_blocks_before_models`: mutate a selected changed Go path during the control run; prove the review blocks before model invocation.
- `test_unrelated_source_change_does_not_block_control_review`: mutate an unselected module file during control; prove the scoped identity remains stable and all other continuation conditions decide the result.
- Selected changed Go paths that are missing, unreadable, symlinked, non-regular, or redirected between validation and open must fail closed.
- No test should claim that unselected files remained unchanged or that the module-wide Go commands consumed the same complete source tree.

## Coverage Target

Target: all 14 numbered behaviors and all fail-closed branches in the behavior map are covered; no numeric coverage threshold. B7 obligations are implemented and covered by the tests listed above.

Rationale: control selection, exact gate shape, and file identity are safety boundaries. A percentage cannot establish that an ambiguous case is blocked.

## Completeness Checklist

- [x] Every numbered design behaviour appears in the Coverage Map.
- [x] Each P0 behaviour has at least one named test.
- [x] Each proposed test can fail on an accepted wrong result; Go compiler/vet rules do not prove Python behavior.
- [x] No case asserts a `nil` string, type mismatch, or other compiler-rejected Go property.
- [x] Redundancy and silent-failure audits are completed for this Python implementation.
- [x] Test names describe the behavior and expected outcome.
- [x] Arrange / Act / Assert is specified for each case.
- [x] Fakes are limited to filesystem/process/model boundaries.
- [x] Error paths, boundaries, and timeout outcomes are mapped for the amended B7 identity scope.
- [x] Concurrency is explicitly stated as none added.
- [x] Coverage target is behavior-based, not a percentage.
- [ ] Exact RED output is preserved for every test. Initial strict-CLI RED evidence is recorded, but several later edge-case tests were added after implementation; see the TDD deviation in `decisions.md`.
- [x] No race-enabled tests are required because no concurrent code is added.
- [x] The B7 cases preserve the approved amended design contract.
## First RED Evidence — Strict-Toolchain CLI Surface

The help-surface case is part of B2's public CLI contract. It was added before production changes and failed on the missing option, not on a broken fixture or import.

Command:

```text
python -m pytest tests/test_cli_review.py -k strict_toolchain_option -q
```

Captured output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\.copilot\session-state\7a134ae3-c5ed-4cc4-8f25-18c948d3df93\files\atom-v1-review-continuation\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 66 items / 65 deselected / 1 selected

tests\test_cli_review.py F                                               [100%]

================================== FAILURES ===================================
_____________ test_review_help_documents_strict_toolchain_option ______________

capsys = <_pytest.capture.CaptureFixture object at 0x000002DFC2811010>

    def test_review_help_documents_strict_toolchain_option(capsys):
        with pytest.raises(SystemExit) as raised:
            main(["review", "--help"])

        assert raised.value.code == 0
>       assert "--strict-toolchain" in capsys.readouterr().out
E       assert '--strict-toolchain' in 'usage: atom review [-h] [--working] [--staged] [--branch REF] [--pr ADO_URL]\n                   [--model NAME] [--ru....\n  --context-file PATH   Explicit UTF-8 evidence document; repeat with --fixed-\n                        evidence.\n'
E        +  where 'usage: atom review [-h] [--working] [--staged] [--branch REF] [--pr ADO_URL]\n                   [--model NAME] [--ru....\n  --context-file PATH   Explicit UTF-8 evidence document; repeat with --fixed-\n                        evidence.\n' = CaptureResult(out="usage: atom review [-h] [--working] [--staged] [--branch REF] [--pr ADO_URL]\n                   [-...ntext-file PATH   Explicit UTF-8 evidence document; repeat with --fixed-\n                        evidence.\n", err='').out
E        +    where CaptureResult(out="usage: atom review [-h] [--working] [--staged] [--branch REF] [--pr ADO_URL]\n                   [-...ntext-file PATH   Explicit UTF-8 evidence document; repeat with --fixed-\n                        evidence.\n", err='') = readouterr()
E        +      where readouterr = <_pytest.capture.CaptureFixture object at 0x000002DFC2811010>.readouterr

tests\test_cli_review.py:121: AssertionError
=========================== short test summary info ============================
FAILED tests/test_cli_review.py::test_review_help_documents_strict_toolchain_option
====================== 1 failed, 65 deselected in 0.37s =======================
```
## RED Evidence — Strict Mode And Skip Conflict

Command:

```text
python -m pytest tests/test_cli_review.py -k strict_toolchain_cannot -q --tb=short --show-capture=no
```

Captured output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\.copilot\session-state\7a134ae3-c5ed-4cc4-8f25-18c948d3df93\files\atom-v1-review-continuation\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 67 items / 66 deselected / 1 selected

tests\test_cli_review.py F                                               [100%]

================================== FAILURES ===================================
________ test_strict_toolchain_cannot_be_combined_with_skip_toolchain _________
C:\Users\gimotwan\.copilot\session-state\7a134ae3-c5ed-4cc4-8f25-18c948d3df93\files\atom-v1-review-continuation\tools\tests\test_cli_review.py:129: in test_strict_toolchain_cannot_be_combined_with_skip_toolchain
    assert review("--working", "--strict-toolchain", "--skip-toolchain") == EXIT_USAGE_ERROR
E   AssertionError: assert 0 == 2
E    +  where 0 = review('--working', '--strict-toolchain', '--skip-toolchain')
=========================== short test summary info ============================
FAILED tests/test_cli_review.py::test_strict_toolchain_cannot_be_combined_with_skip_toolchain
====================== 1 failed, 66 deselected in 8.02s =======================
```






## Review-Fix TDD Evidence — Control Formatting Scope

### RED

Command:

```text
python -m pytest tests/test_review_continuation.py -k control_format_gate_uses_selected_changed_file_scope -q --tb=short
```

Captured failure excerpt:

```text
tests\test_review_continuation.py F                                      [100%]
__________ test_control_format_gate_uses_selected_changed_file_scope __________
tests\test_review_continuation.py:663: in test_control_format_gate_uses_selected_changed_file_scope
    pytest.fail(f"unrelated unformatted Go file blocked continuation: {error}")
E   Failed: unrelated unformatted Go file blocked continuation: Required toolchain gates failed: build, control fmt
====================== 1 failed, 58 deselected in 12.07s =======================
```

The assertion failed because module-wide control formatting included the unrelated unformatted file.

### GREEN

The new behavior plus the bounded-gate and skipped-gate contracts passed:

```text
python -m pytest tests/test_review_continuation.py -k 'control_format_gate_uses_selected_changed_file_scope or control_runs_only_bounded_gates_once or skipped_control_gate_blocks_models' -q --tb=short
====================== 7 passed, 52 deselected in 0.42s =======================
```

After updating the existing happy-path fixture to return the changed snapshot through the control formatter, the continuation, toolchain, and formatting regression files passed:

```text
python -m pytest tests/test_review_continuation.py tests/test_review_toolchain.py tests/test_review_formatting.py -q --tb=short
======================= 148 passed in 80.13s (0:01:20) ========================
```

### Full verification

```text
python -m pytest tests -v --cov=atom
TOTAL                        4715    233    95%
================= 1684 passed, 5 skipped in 372.14s (0:06:12) =================
```

`git diff --check` exited 0 with `git diff --check: clean`.

## Review-Fix Amendment: Control Formatting Scope

The developer approved the revised design behavior before implementation. `test_control_format_gate_uses_selected_changed_file_scope` proves the control formatter checks the frozen changed snapshot with the control Go distribution while an unrelated unformatted Go file cannot fail the gate. Empty/skipped control formatting remains fail-closed. The test passed in the full Python suite (1684 passed, 5 skipped; 95% coverage).


## Review-Snapshot TDD Evidence (2026-11-03)

Core scoped-identity RED:

```text
python -m pytest tests/test_review_continuation.py -k review_snapshot_identity_covers_only_selected_go_files -q
E       AssertionError: continuation requires changed-review-file identity
E       assert False
1 failed, 59 deselected in 8.75s
```

Missing-scope RED:

```text
python -m pytest tests/test_review_continuation.py -k missing_review_snapshot_scope_blocks_before_selected_checks -q
E       AssertionError: error = AttributeError("'NoneType' object has no attribute 'files'"), want SourceFingerprintError
1 failed, 60 deselected in 1.17s
```

GREEN and final verification:

```text
python -m pytest tests/test_review_continuation.py -k missing_review_snapshot_scope_blocks_before_selected_checks -q
1 passed, 60 deselected in 0.27s

python -m pytest tests/test_review_continuation.py tests/test_review_toolchain.py -k 'review_snapshot_identity or source_change_after_selected_checks or unrelated_source_change or missing_review_snapshot_scope or pinned_review_uses_selected_gates' -q
9 passed, 75 deselected in 6.25s

python -m pytest tests -v --cov=atom
TOTAL                        4716    235    95%
1686 passed, 5 skipped in 245.95s (0:04:05)
```
## Nested-module snapshot path regression (B7)

`capture_review_diff` preserves repository-relative paths in `CapturedDiff.files`, but fingerprint paths must be relative to the selected module root. The integration case `test_nested_module_snapshot_paths_are_fingerprintable` creates a nested `service` module, captures `service/changed.go`, verifies the formatting snapshot path is `changed.go`, and verifies the scoped fingerprint succeeds.

RED:

```text
python -m pytest tests/test_review_formatting.py -k nested_module_snapshot_paths_are_fingerprintable -q
FAILED: expected ['changed.go'], got ['service/changed.go']
1 failed, 66 deselected
```

GREEN:

```text
python -m pytest tests/test_review_formatting.py -k nested_module_snapshot_paths_are_fingerprintable -q
1 passed, 66 deselected

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q
151 passed

python -m pytest tests -v --cov=atom
1687 passed, 5 skipped; TOTAL 95%
```

`git diff --check` was clean. The test maps to Behaviour 7 and does not change the approved selected-changed-Go-file-only identity scope.
## Working-tree baseline must match the captured snapshot (B7)

The approved amendment requires only `DiffSource.WORKING` to match captured `FormattingFile.content` against the live file during the initial fingerprint. `DiffSource.STAGED` and `DiffSource.BRANCH` retain their existing ability to format captured Git blobs that differ from the live worktree; their fingerprints still cover live files around module-wide checks. `test_initial_fingerprint_matches_captured_bytes_only_for_working_source` covers both outcomes.

RED:

```text
python -m pytest tests/test_review_continuation.py -k initial_fingerprint_matches_captured_bytes_only_for_working_source -q --tb=short
FAILED: working-tree case did not raise SourceFingerprintError
================= 1 failed, 1 passed, 61 deselected in 0.62s ==================
```

GREEN:

```text
python -m pytest tests/test_review_continuation.py -k initial_fingerprint_matches_captured_bytes_only_for_working_source -q --tb=short
====================== 2 passed, 61 deselected in 6.26s ======================

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q --tb=short
============================ 153 passed in 48.06s ============================

python -m pytest tests -v --cov=atom
TOTAL                        4718    235    95%
================= 1689 passed, 5 skipped in 235.25s (0:03:55) =================
```

The pinned Go fixture now writes exact bytes rather than using Windows text-mode newline translation, so the simulated captured working snapshot and live file begin byte-identical. This corrected a fixture mismatch; no expectation was weakened.
## Module-minimum read failures (B3)

`test_module_minimum_version_read_failures_are_contextual` injects both an `OSError` (`PermissionError`) and a `UnicodeDecodeError` from `go.mod` reading. Each must become a contextual `ControlToolchainError` naming the module file; the CLI already maps that exception to `EXIT_CHECK_FAILED` and stderr.

RED:

```text
python -m pytest tests/test_review_continuation.py -k module_minimum_version_read_failures_are_contextual -q --tb=short
FAILED: PermissionError escaped instead of ControlToolchainError
FAILED: UnicodeDecodeError escaped instead of ControlToolchainError
====================== 2 failed, 63 deselected in 2.38s =======================
```

GREEN:

```text
python -m pytest tests/test_review_continuation.py -k module_minimum_version_read_failures_are_contextual -q --tb=short
====================== 2 passed, 63 deselected in 1.42s ======================

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q --tb=short
============================ 155 passed in 52.69s ============================

python -m pytest tests -v --cov=atom
TOTAL                        4721    235    95%
================= 1691 passed, 5 skipped in 246.67s (0:04:06) =================
```



## RED/GREEN Evidence — Selected Path Replacement

RED demonstrated that a redirected file handle was accepted before the implementation:

```text
python -m pytest tests/test_review_continuation.py -k path_replaced_before_open -q --tb=short
E   Failed: DID NOT RAISE SourceFingerprintError
====================== 1 failed, 65 deselected in 3.56s =======================
```

GREEN confirmed the regression plus snapshot identity cases:

```text
python -m pytest tests/test_review_continuation.py -k 'path_replaced_before_open or review_snapshot_identity' -q --tb=short
====================== 6 passed, 60 deselected in 4.71s =======================
```

Full-suite verification:

```text
python -m pytest tests -v --cov=atom
TOTAL                        4723    235    95%
================= 1692 passed, 5 skipped in 539.82s (0:08:59) =================
```

## PATH Control VERSION Decode Error Case

| Behaviour | Test | Expected result |
|---|---|---|
| B5 / B13 | `test_path_control_version_decode_failure_is_contextual` | An invalid UTF-8 Go distribution `VERSION` file raises the existing `ControlToolchainError` with the PATH distribution context and does not escape as `UnicodeDecodeError`. |

This test can fail because Python accepts the invalid bytes read and raises at runtime; neither type checking nor the Go toolchain proves the Python exception handling.

## RED/GREEN Evidence — PATH VERSION Decode Failure

```text
python -m pytest tests/test_review_continuation.py -k path_control_version_decode_failure_is_contextual -q --tb=short
E   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
====================== 1 failed, 66 deselected in 3.45s =======================

python -m pytest tests/test_review_continuation.py -k 'path_control_version_decode_failure_is_contextual or default_control_resolves_and_verifies_direct_path_distribution' -q --tb=short
====================== 2 passed, 65 deselected in 21.49s ======================
```

## Control Override Requires a Selected Toolchain Pin

| Behavior | Test | Expected result |
|---|---|---|
| B2 option conflict | `test_control_go_version_requires_selected_toolchain_pin` | Reject `--control-go-version` without `--go-version` or `--go-executable` as `EXIT_USAGE_ERROR` before any commands; preserve the valid pinned override path. |

This test can fail because the parser accepts the option and the CLI can silently ignore it; no static check enforces the CLI combination contract.

## RED/GREEN Evidence — Control Override Requires Selected Pin

RED before CLI validation:

```text
python -m pytest tests/test_cli_review.py -k control_go_version_conflicts_fail_before_commands -q --tb=short
FAILED test_control_go_version_conflicts_fail_before_commands[conflict0]
E   AssertionError: assert 0 == 2
================= 1 failed, 2 passed, 73 deselected in 1.75s ==================
```

GREEN, including strict/skip conflicts and the valid pinned forwarding case:

```text
python -m pytest tests/test_cli_review.py -k 'control_go_version_conflicts_fail_before_commands or control_go_version_reaches_review_pipeline' -q --tb=short
====================== 4 passed, 72 deselected in 0.26s ======================
```
