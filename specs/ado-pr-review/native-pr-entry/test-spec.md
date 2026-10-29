---
project: "ado-pr-review"
phase: "native-pr-entry"
design_spec: "design-spec.md"
date: "2026-10-25"
---

# Test spec: native PR entry

## Toolchain redundancy audit

None — no proposed case was unfailable.

This tooling is Python: Go compiler/vet guarantees are not applied to it. No Go nil-interface, fixed-width overflow or race-detector claim is made. Empty/malformed URLs and JSON, ignored CommandResult outcomes, wrong branch selection, path escapes and suppressed cleanup errors require runtime tests. No getter-only or annotation-only tests were added.

| Silent failure property | Coverage |
| --- | --- |
| Empty or malformed input accepted silently | Unsafe PR URLs, malformed metadata, invalid branch/source identity, invalid local scope |
| Ignored command or lifecycle failure | Metadata outcomes, clone failure, snapshot failure, zero-exit runner_error, zero-exit cleanup that leaves the directory |
| Missing dispatch case or wrong enum interpretation | Four-source CLI selection, explicit source conflicts, old local-mode regressions |
| Suppressed exception or cancellation | Setup/review/KeyboardInterrupt cleanup, cleanup interruption, preserved primary failures |
| Wrong reference or omitted files | Real diverged non-main Git history, target-only exclusion, PR changes outside selected module retained |
| Runtime indexing/type assumptions | JSON scalars, nulls, missing fields, invalid IDs and ambiguous merge bases |
| Go typed nil, fixed-width overflow, Go race detector | Not applicable to this Python increment; no new shared-state concurrency |

## Implemented behavior-to-test map

Test files: test_cli_pr_review.py, test_pull_request.py and test_pr_checkout_integration.py under tools\tests. Existing diff, local CLI, output and toolchain tests are retained without weakening.

| Design behavior | Actual tests | Contract |
| --- | --- | --- |
| 1 | test_pr_source_dispatch; test_pr_invalid_options_fail_before_preparation; test_missing_source_help_mentions_pr | Exactly one explicit source, invalid settings before preparation and discoverable --pr option |
| 2 | test_unsafe_pr_url_starts_no_command; test_metadata_failure_stops_before_clone; test_percent_encoded_names_keep_their_metadata_scope | Modern/legacy canonicalization, browser suffixes, safe percent encoding and no I/O for unsafe input |
| 3 | test_metadata_failure_stops_before_clone; test_invalid_metadata_stops_before_clone; test_malformed_metadata_stops_before_clone; test_metadata_remote_identity_is_checked | One bounded GET and explicit transport/schema/identity/status/fork/ref/remote rejection |
| 4 | test_local_scope_is_required; test_pr_module_must_still_have_go_mod_file; real Git nested-module tests | Matching local origin/module containment and valid Go module in the pinned checkout |
| 5 | test_clone_failure_is_cleaned; test_independent_clone_and_pinned_checkout | Independent HTTPS clone, accepted organization-label userinfo, no shared/filter/reference/depth shortcut |
| 6 | test_snapshot_failure_prevents_review_and_is_cleaned; test_zero_exit_with_lifecycle_error_is_not_a_snapshot; test_independent_clone_and_pinned_checkout | Full pins, unique merge base, source movement detection, detached source and verified clean tracked files |
| 7 | test_real_git_merge_base_and_dirty_original_preserved | Actual non-main target, three-dot diff, exclusion of unrelated target-only changes and retention of all PR files |
| 8 | test_native_cli_uses_real_checkout_and_cleans_it; test_pr_required_checks_still_block; report fixture checks live clone/module cwd on every model call | Existing checks/reviewer run inside the selected cloned module and required failures block all model calls |
| 9 | test_pr_review_options_and_partial_status; test_pr_no_model_available_is_not_clean_review | Option forwarding, repeated runs, unavailable/partial-model exit semantics |
| 10 | test_pr_report_provenance_and_limitations; test_local_reports_have_no_pr_fields; existing test_review_output.py | Markdown/JSON pins and limitations, selected-module check scope, unchanged local report contract |
| 11 | test_cleanup_on_failure_and_interrupt; test_cleanup_failure_preserves_primary_error; test_cleanup_interruption_names_retained_directory; test_cleanup_failure_prevents_success_output; test_cleanup_success_exit_still_requires_path_absence; test_repository_package_cannot_shadow_cleanup_worker; test_cleanup_worker_checks_ownership_and_handles_readonly_files | Bounded exact-owned-path removal on every supported outcome; explicit retained path and preserved primary errors; trusted worker launch |
| 12 | test_real_git_merge_base_and_dirty_original_preserved; test_native_cli_uses_real_checkout_and_cleans_it | Every original worktree file, HEAD/branch/index/config unchanged; temporary checkout absent |

## Arrange / act / assert and fixtures

- CLI cases invoke the real main entry with either a recording preparation boundary or the real context manager plus process-I/O fakes. Assert exit status, selected source, forwarded calls, report payloads and absence of a success report after cleanup failure.
- Metadata and setup cases use FakeRunner/LocalRunner/CheckoutRunner at the process boundary with source-free synthetic JSON and refs. Enter the public preparation context; assert errors before review, command timeouts/arguments and exact owned-path cleanup.
- Cleanup cases raise a primary error or interruption inside that context, or script a failed/interrupted/false-success worker. Assert preserved failure type, visible cleanup diagnostics and final directory state. Failed-worker test fixtures run an exact-path rescue so an intentionally retained directory is not leaked.
- Real Git cases create a deterministic synthetic origin, fork source from develop, advance develop separately, and clone a developer checkout with staged, unstaged and untracked work. Replace only HTTPS transport, ADO and model I/O; run actual Git clone/ref/checkout/merge-base/diff and the real Python cleanup worker. Snapshot every original worktree file plus HEAD/branch/index/config before/after.

## Verification

The [current verification](../verification.md) applies to the unchanged runtime/tests. Tests use synthetic inputs and real temporary Git repositories without contacting ADO or invoking reviewers.

## Concurrency, tooling and remaining scope

No new concurrent code. Existing model execution/concurrency behavior is reused. Use the existing Python pytest/coverage CI gate and Markdown link checker, not a root Go atom check or a new linter. Separately launched cleanup-process statements are not automatically traced by this coverage setup; their effects and errors are asserted through actual worker executions. No real ADO request, private target checkout, target build or model review was executed.
