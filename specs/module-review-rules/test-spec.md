# Test Spec: default module review guidance

Design: [approved design-spec.md](design-spec.md). Python implementation and pytest, matching existing project tooling. Design approval was explicit on 2026-10-30; no additional model calls or production reviewer-default changes are authorized.

## Redundancy audit

None - no proposed case was unfailable. Do not test dataclass assignments, hashing-library correctness, Python type annotations, or Go compiler properties. Test exact captured bytes/provenance, failure timing, source confinement, mode selection, and actual runner input instead.

Silent failures: empty/invalid policy and ignored filesystem errors require tests; each status must render truthfully; tuple/source metadata inconsistencies require validation. Go typed-nil/overflow/map properties do not apply. No new concurrency or cancellation mechanism is added; existing runner/concurrency tests remain regression coverage.

## Behavior coverage map

| Design behavior | Planned pytest coverage |
|---|---|
| 1 | test_cli_freezes_launch_rules_before_pr_preparation |
| 2 | test_capture_preserves_selected_order_and_original_bytes |
| 3 | test_capture_optional_sources_and_ignores_unselected_paths |
| 4 | test_capture_invalid_present_sources_fail; test_capture_read_failure_is_not_absence |
| 5 | test_capture_refuses_unsafe_targets; test_capture_refuses_resolved_escape_before_read; test_capture_refuses_duplicate_resolved_targets; test_capture_dangling_source_is_not_absence; test_capture_unreadable_traversal_is_not_absence |
| 6 | test_capture_skip_modes_do_not_access_candidates |
| 7 | test_cli_rule_error_prevents_preparation_or_execution |
| 8, 9 | test_review_delivers_frozen_guidance_to_every_run |
| 10 | test_review_delivers_frozen_guidance_to_every_run; test_cli_freezes_launch_rules_before_pr_preparation |
| 11 | test_review_delivers_frozen_guidance_to_every_run; existing partial/flags tests |
| 12 | test_capture_skip_modes_do_not_access_candidates; existing fixed-evidence CLI/PR tests |
| 13 | test_cli_rule_metadata_never_serializes_policy |
| 14 | test_cli_freezes_launch_rules_before_pr_preparation; existing PR report tests |
| 15 | report framing/limitations assertions; no test claims model obedience or quality |

## Ordered test cases

1. Capture both files: create synthetic UTF-8/CRLF guide and AGENTS, call capture, assert source order, exact text/byte counts and snapshot unaffected by subsequent writes. Initial RED: loader missing, then empty stub gives loaded/order assertion failure.
2. Optional selection: parameterize both/one/neither; place unwanted sibling/ancestor/GitHub/linked workflow sentinels and assert exclusion. Existing behavior checks may pass as regression; no new speculative implementation is justified by them alone.
3. Invalid source: parameterize empty/blank/NUL/invalid UTF-8/nonregular and injected PermissionError. Assert safe ModuleRulesInputError, not empty success. Use real files; inject only OS read denial.
4. Confinement: create escaped/dangling links and duplicate targets where supported; assert rejection without reading outside. Skip only when the OS cannot create the fixture, recording the platform limit.
5. Skip modes: monkeypatch filesystem access to fail, call disabled/fixed modes, assert status and zero reads. Fixed mode wins when both selected.
6. Fan-out: capture then mutate sources, use existing ScriptedRunner for two synthetic model names and multiple runs. Assert complete identical prompt, original text only, shared seven, review-only framing, unchanged native flags and strict extraction.
7. Invalid caller snapshots: altered hashes, source/status mismatches, and fixed-mode loaded snapshots must fail before runner work. No new filesystem reads in run_review.
8. CLI/reporting: run normal/opt-out/fixed using existing model boundary fake. Assert capture/default modes and safe metadata; policy text and absolute paths must not be serialized. Fixed evidence packet remains unchanged.
9. PR timing: use existing preparation seam; assert snapshot before preparation, destroy source, plant conflicting clone policy, verify frozen runner stdin and truthful PR limitations. Invalid local rule must prevent entry into preparation and runner work.

No network, live PR, paid model, or machine configuration is used by these tests. No new threads are added; multiple-run existing invocation exercises immutable snapshot sharing.

## Commands and evidence

Run one new behavior to RED, implement minimally, then run its targeted selection GREEN. Preserve each loop output outside Git in session logs. Run the combined module-rule/CLI/PR/review/report tests, then the existing full python -m pytest tests -v --cov=atom --cov-report=term-missing gate. Validate packaging/docs with existing tools where applicable. No new tooling is introduced.

## Gate

Mapping established before implementation; test names/status reconciled against actual results before completion. No original POC criteria or executed spike source is altered.

## Implementation reconciliation and verification

All fifteen behaviors are implemented and covered by the mapped capture, common-prompt, CLI/PR, metadata-report tests and existing lifecycle/extraction/fixed-evidence suites. Invalid direct snapshots are covered by test_review_rejects_invalid_policy_before_execution, including hashes, unknown sources, inconsistent lengths/status, empty loaded snapshots, duplicate/order violations and fixed-mode loaded policy. The fan-out test decodes the JSON-framed packet and checks both complete documents, including original CRLF, Unicode and JSON-looking content. The existing partial-review PR test now also carries local policy while preserving both requested reviewers and their denominators.

The three native symlink variants cannot run on this Windows machine (winerror 1314). They remain explicit skips; executable filesystem-boundary cases separately cover escaped/dangling resolution, duplicate targets, denied traversal and denied reads. This is not native link-integration proof. Missing-root error wrapping remains the two uncovered lines in the new loader; this CLI normally supplies its existing current directory. No coverage-percentage claim substitutes for these limits.

Full repository verification and exact output are recorded in [tdd-evidence.md](tdd-evidence.md): 1501 passed, 5 skipped, with 95% overall coverage. Two skips predate this change; three are the new privilege-limited link fixtures. No production model, deadline, MCP default, tool permission, extraction rule or Go-check gate was changed. No additional paid calls were made.

## Review regressions

Behavior 4 additionally maps to test_capture_non_directory_guide_parent_is_not_absence, with real non-directory parents at three depths. It observed three clean Windows assertion failures before the explicit intermediate-directory validation, then passed with the full loader suite. The existing test_local_reports_have_no_pr_fields now changes to tmp_path; the same controlled ambient-policy invocation changed from one failing test to one passing test, with its output assertions unchanged. These are approved review corrections, not new source-discovery behavior.
