# Test spec: changed-file review formatting

The numbered behaviors in design-spec.md are the contract. Source is tools/tests/test_review_formatting.py unless another file is named. All 57 formatting regression cases passed in the captured guard run; the subsequent full Python gate passed 1059 tests with 2 platform-specific skips and 95% total coverage. Verbatim outputs are in tdd-log.md and verification.md.

| Design behavior | Executed regression evidence |
|---|---|
| 1. Only whole changed Go files | test_clean_changed_file_is_not_blocked_by_untouched_formatting; test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean; exact complete formatter stdin assertions |
| 2. Selected working/index/branch bytes | test_staged_formatting_uses_index_snapshot_not_working_file (clean/bad inverse and absent working file); test_branch_formatting_uses_committed_content_despite_dirty_working_file; all-source bad snapshot cases |
| 3. Shared canonical capture and fail-closed identity | test_working_file_movement_after_diff_capture_blocks_models; test_invalid_manifest_is_refused_without_empty_scope_success; test_snapshot_acquisition_and_blob_transport_fail_closed; test_invalid_branch_ref_fails_before_checks_or_models |
| 4. Add/rename/delete/untracked | test_pure_rename_formats_destination_and_preserves_canonical_diff_path; test_added_and_renamed_go_paths_use_nul_delimited_canonical_names; test_no_surviving_go_files_skips_formatter_with_explicit_scope; test_untracked_go_file_is_not_added_to_working_diff_scope |
| 5. Canonical names and safe paths | Unicode/space and pure rename cases; test_module_boundary_exclusions_are_explicit_without_checking_other_modules invokes below the Git root; malformed path table; test_working_file_substituted_with_non_regular_path_is_not_read; test_non_regular_selected_go_entry_is_refused_before_formatter_or_models |
| 6. Module boundary | test_module_boundary_exclusions_are_explicit_without_checking_other_modules checks exact selected stdin plus outside/nested exclusions |
| 7. Zero applicable files | test_no_surviving_go_files_skips_formatter_with_explicit_scope (empty, non-Go, deleted); prompt skip case; untracked case |
| 8. UTF-8/CRLF/immutability | test_selected_bytes_are_preserved_and_only_line_endings_are_normalized (working/index, CRLF, mixed, genuine defect, UTF-8); invalid UTF-8 required-failure cases; status/source byte preservation assertions |
| 9. Compare formatter output | bad selected snapshots and test_formatter_failures_keep_path_and_original_diagnostic (zero exit with empty output) |
| 10. Command/acquisition failures | formatter missing/timeout/runner error/syntax error table; Git failure/blob failure/malformed base64/wrong identity table; invalid manifest table |
| 11. Required failures still block | test_non_format_required_gate_commands_and_failures_remain_unchanged covers exact build/vet/test/race and advisory command lists; changed-file fmt failures assert no model calls; existing test_review_toolchain.py and test_gates.py |
| 12. Honest prompt/JSON/Markdown | test_prompt_names_selected_formatting_scope_without_claiming_module_scan; test_cli_reports_selected_file_formatting_coverage exercises public CLI success in JSON and Markdown; existing test_toolchain.py and test_review_output.py |
| 13. Capture shared across models | test_captured_content_is_reused_when_checks_change_working_tree; raw-diff command-count assertions; canonical diff.files assertions; existing invocation/extraction/report tests retain their model-sharing and changed-path guards |
| 14. Existing contracts | standalone FormatGate still fails untouched.go in first scope test; default gates/runner are unmodified; existing runner, review, non-module, explicit skip-toolchain, packaging and installed-CLI tests pass in the full suite |

## Redundancy audit and limits

These are Python runtime and real Git/gofmt integration properties, not Go compiler assertions. No language-guarantee tests were added or removed. The two skipped tests are the existing POSIX runner fault tests on Windows; native Windows equivalents ran. No new concurrency, dependency or performance claim is introduced. Real build/test/model boundaries are replaced only in scoped fixture integration tests so failures and source selection are deterministic; the real standalone format control and real Git/gofmt remain active. This does not claim a private target check or end-to-end ADO review passed.

The initial untouched targeted baseline was 106 passed in 4.57s. Tests that immediately passed are regression guards rather than fabricated RED evidence. The incorrect UTF-8 clean fixture and the pre-existing FakeRunner acquisition fixture were corrected with their original assertions retained; see decisions.md.

## Independent-review regression additions

- test_submodule_display_config_cannot_change_manifest_patch_framing: two real local Git pointer/display cases cover design behaviors 3, 4 and 13. Log mode reproduced the review finding before --submodule=short; the diff-mode fixture was already passing and is not misrepresented as RED.
- test_unread_manifest_paths_do_not_apply_native_source_path_restrictions: six cross-platform injected-manifest cases cover design behaviors 4-7 for non-Go, deleted and outside-module Go names containing colon/backslash. All six failed before the fix; all pass afterward. These are valid POSIX-name parsing cases, not a claim those checkout names were created on Windows. Existing selected-source unsafe-path cases retain their refusals.

The complete formatting regression file now has 65 passing cases (40.13s in the post-review targeted run). Earlier counts above describe pre-review evidence. Both independent reviewer findings were repaired test-first within the same approved formatting-only contract. A fresh post-fix full-suite run is recorded separately in verification.md.
