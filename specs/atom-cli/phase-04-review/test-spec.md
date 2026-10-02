---
project: "atom-cli"
phase: "phase-04-review"
date: "2026-09-18"
design_spec: "design-spec.md"
---

# Test Spec - Phase 4: `atom review`

A retrospective test spec for Phase 4: diff acquisition, repeated model
invocation, extraction, proximity merging, report rendering, and the `atom review`
CLI. The tests already exist; this document maps behaviours **B103-B137** to the
named tests that pin them.

Retrospective, as in Phases 2 and 3, because Atom builds the tests from the spec
during TDD rather than writing a separate test-design document first. The value
of this document is the mapping - it is what makes an unpinned behaviour visible.

**Suite:** 487 tests passing, 96% statement coverage.

```
python -m pytest tools/tests --cov=atom --cov-report=term-missing -q
```

## Coverage Figures

| Module | Coverage | Notes |
|---|---:|---|
| `diff.py` | 100% | Phase 4 diff-source selection, capture, and size accounting. |
| `invoke.py` | 100% | Phase 4 model probing, repeated calls, concurrency, stdin prompt delivery, and partial-run accounting. |
| `extract.py` | 100% | Phase 4 fence stripping, schema validation, file guard, and extraction failure reporting. |
| `merge.py` | 100% | Phase 4 proximity grouping, agreement fractions, severity preservation, and impossible-fraction guards. |
| `review.py` | 100% | Phase 4 pipeline bundle and usability boundary. |
| `report.py` | 97% | Uncovered lines are renderer branches not reached by the present fixture shapes. |
| `runner.py` | 95% | Phase 1 runner with Phase 4 start-failure diagnosis and stdin additions. |
| `cli.py` | 90% | Uncovered areas are argument-parsing and dispatch branches outside the Phase 4 paths exercised here. |
| **Total** | **96%** | **487 tests passing** |

---

## Coverage Summary

### Diff acquisition (B103-B106b)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B103 | `atom review` reviews exactly one explicit source: staged, branch, or working. | `test_staged_source_asks_git_for_the_index`; `test_working_source_asks_git_for_unstaged_changes`; `test_branch_source_diffs_against_the_merge_base`; `test_working_is_accepted`; `test_staged_is_accepted`; `test_branch_is_accepted` |
| B104 | With no source, or conflicting sources, the command fails with a usage error rather than guessing. | `test_selecting_no_source_names_all_three_options`; `test_selecting_two_sources_is_an_error_rather_than_a_precedence_rule`; `test_no_source_is_a_usage_error`; `test_two_sources_is_a_usage_error`; `test_review_without_a_source_exits_two_and_explains`; `test_review_with_two_sources_exits_two_and_explains` |
| B105 | An empty diff reports nothing to review and exits as a successful empty review. | `test_an_empty_diff_is_not_an_error`; `test_a_whitespace_only_diff_counts_as_empty`; `test_an_empty_diff_describes_itself_as_empty` |
| B106 | The diff is captured once and reused for every model call. | `test_capture_issues_exactly_one_git_command`; `test_the_prompt_carries_the_whole_diff_in_one_call`; `test_the_prompt_reaches_the_runner_as_stdin` |
| B106a | The whole diff goes in one call; there is no per-file chunking. | `test_a_multi_file_diff_is_captured_whole`; `test_the_prompt_carries_the_whole_diff_in_one_call`; `test_the_prompt_reaches_the_runner_as_stdin` |
| B106b | Diff size is reported; no size limit is imposed and nothing is truncated. | `test_nothing_is_truncated_however_large_the_diff`; `test_changed_lines_count_additions_and_removals`; `test_file_headers_are_not_counted_as_changed_lines`; `test_context_lines_are_not_counted`; `test_file_count_follows_the_b_side_of_a_rename`; `test_a_file_is_counted_once_however_many_hunks_it_has`; `test_size_reads_as_a_sentence_for_the_report`; `test_size_description_is_singular_for_one_file`; `test_the_report_describes_the_diff_that_was_reviewed` |

### Toolchain preflight (B138-B142)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B138 | Required toolchain gate failures block review before any model call. | `test_run_review_blocks_before_models_when_required_gate_fails`; `test_a_blocked_toolchain_returns_check_failed_without_reviewing` |
| B139 | `staticcheck`, `errcheck`, and `govulncheck` are advisory: missing tools skip, findings warn, clean runs pass. | `test_advisory_gate_skips_when_tool_is_missing`; `test_advisory_gate_warns_and_preserves_output_when_tool_finds_something`; `test_advisory_gate_passes_when_tool_exits_zero`; `test_advisory_gates_returns_all_optional_review_signals` |
| B140 | The prompt placeholder preserves the measured prompt byte-for-byte when empty. | `test_empty_toolchain_placeholder_preserves_original_prompt_bytes` |
| B141 | Prompt exclusions are conditional on tools that ran and passed; skipped or absent toolchains exclude nothing. | `test_prompt_block_excludes_everything_the_passing_toolchain_proved`; `test_prompt_block_does_not_exclude_ignored_errors_when_errcheck_was_skipped`; `test_prompt_block_says_nothing_is_excluded_when_toolchain_did_not_run`; `test_run_review_continues_with_no_exclusions_when_directory_is_not_go_module` |
| B142 | The markdown report records the toolchain verdicts. | `test_the_report_lists_toolchain_verdicts` |

### Model invocation (B107-B112, B132-B134)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B107 | Review calls use `--silent`, never `--output-format json`. | `test_uses_silent_and_never_output_format_json` |
| B108 | Every call disables custom instructions. | `test_always_disables_custom_instructions`; `test_custom_instructions_are_disabled` |
| B109 | Built-in MCP servers are disabled; vendor-specific server names are not hard-coded. | `test_always_disables_builtin_mcp_servers`; `test_names_no_vendor_specific_mcp_servers_by_default`; `test_extra_mcp_servers_can_be_disabled_by_the_caller`; `test_no_vendor_specific_mcp_server_is_disabled_by_default` |
| B110 | Model availability is probed before review calls are made. | `test_probes_every_model`; `test_a_rejected_model_is_reported_unavailable_with_its_reason`; `test_no_review_call_happens_before_every_probe_has_run`; `test_an_unavailable_model_is_never_asked_to_review`; `test_when_no_model_is_available_the_review_fails_loudly`; `test_unavailable_models_are_listed_with_their_reasons` |
| B111 | Calls run in parallel, bounded by a default concurrency of 4. | `test_default_concurrency_is_the_measured_four`; `test_never_exceeds_the_concurrency_limit`; `test_calls_genuinely_overlap_rather_than_merely_staying_under_the_limit`; `test_all_runs_complete_even_when_they_outnumber_the_workers` |
| B112 | A timed-out call is a recorded outcome, not an exception. Exact wall-clock timeout behaviour is not verified against a real model. | `test_a_timeout_is_a_recorded_outcome_not_a_raise`; `test_a_silent_timeout_is_named_by_its_outcome` |
| B132 | Each model is called 3 times by default and `--runs` overrides it. | `test_calls_each_model_three_times_by_default`; `test_run_count_is_overridable`; `test_each_model_is_asked_the_requested_number_of_times` |
| B133 | Runs of the same model are identical calls. | `test_runs_of_one_model_are_byte_identical_calls` |
| B134 | Each run is tracked individually and participation reports completed over requested. | `test_every_model_gets_the_same_number_of_runs`; `test_runs_are_numbered_from_one`; `test_participation_states_completed_over_requested_per_model`; `test_the_report_states_how_many_runs_each_model_completed`; `test_the_json_names_models_that_produced_nothing` |

### Extraction and validation (B113-B117)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B113 | Extraction strips a surrounding markdown fence before parsing. | `test_plain_json_needs_no_stripping`; `test_a_json_labelled_fence_is_stripped`; `test_an_unlabelled_fence_is_stripped`; `test_surrounding_whitespace_is_ignored`; `test_a_fenced_response_extracts_normally`; `test_a_json_labelled_fence_wins_over_an_earlier_unlabelled_one`; `test_an_unlabelled_fence_still_works_when_it_is_the_only_one` |
| B114 | Extraction does not scan for outer brackets as a fallback. | `test_prose_around_bare_json_is_a_failure_not_a_rescue`; `test_prose_outside_a_fence_is_still_extracted`; `test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly` |
| B115 | Schema-invalid or unreadable responses fail loudly for that call and are surfaced. | `test_a_non_array_payload_is_rejected`; `test_unparseable_text_is_rejected`; `test_a_failure_records_which_model_and_which_run`; `test_a_failure_keeps_an_excerpt_of_what_was_returned`; `test_the_excerpt_is_bounded_so_a_huge_reply_cannot_flood_the_report`; `test_an_unusable_run_is_not_silently_ignored`; `test_responses_nobody_could_parse_are_reported`; `test_the_json_reports_unparseable_responses` |
| B116 | Validation checks required fields, severity, and a real integer line. | `test_a_well_formed_response_yields_findings`; `test_an_empty_array_is_a_clean_review_not_a_failure`; `test_every_required_field_is_required[file]`; `test_every_required_field_is_required[line]`; `test_every_required_field_is_required[severity]`; `test_every_required_field_is_required[message]`; `test_a_severity_outside_the_allowed_set_is_rejected`; `test_all_four_allowed_severities_are_accepted`; `test_a_string_line_number_is_rejected`; `test_a_boolean_line_number_is_rejected`; `test_a_line_number_below_one_is_rejected`; `test_line_zero_is_rejected`; `test_line_one_is_accepted`; `test_an_element_that_is_not_an_object_is_rejected` |
| B117 | A finding naming a file outside the reviewed diff is rejected. The file list itself is protected from hunk-body header confusion. | `test_a_finding_naming_a_file_outside_the_diff_is_rejected`; `test_rejecting_one_finding_does_not_discard_its_siblings`; `test_the_guard_is_skipped_when_no_file_list_is_given`; `test_added_content_cannot_invent_a_file`; `test_content_that_looks_like_a_git_header_does_not_start_a_new_file`; `test_content_that_looks_like_a_hunk_header_is_counted_as_a_change` |

### The merge model (B118-B124)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B118 | Findings are grouped by file and line proximity, not exact line equality. | `test_identical_lines_merge`; `test_nearby_lines_merge`; `test_lines_beyond_the_window_stay_separate`; `test_the_same_line_in_different_files_never_merges`; `test_grouping_does_not_depend_on_the_order_findings_arrive_in` |
| B119 | The proximity window defaults to 3 and is configurable. | `test_the_default_window_is_three_lines`; `test_the_window_is_configurable`; `test_a_negative_window_is_rejected`; `test_a_zero_window_means_exact_line_matching`; `test_a_group_never_spans_more_than_the_window`; `test_drift_lets_a_group_reach_further_than_the_window`; `test_a_negative_window_is_refused` |
| B120 | Merging never discards a message; every message stays attributed. | `test_every_message_survives_the_merge`; `test_each_message_is_attributed_to_its_model_and_run`; `test_each_message_keeps_the_line_it_was_reported_at`; `test_every_model_message_is_shown_with_its_author`; `test_the_json_keeps_every_attributed_message` |
| B121 | Every merged finding records which models and how many runs reported it. | `test_a_merged_finding_names_the_models_that_reported_it`; `test_agreement_counts_how_many_runs_of_each_model_reported_it`; `test_one_run_reporting_a_line_twice_counts_once`; `test_agreement_renders_as_the_fraction_a_report_shows`; `test_agreement_is_shown_as_a_fraction_per_model`; `test_the_json_reports_agreement_with_both_halves_of_the_fraction` |
| B122 | Agreement is reported, never used to suppress solo findings. | `test_a_single_model_finding_is_reported_not_suppressed`; `test_a_finding_from_both_models_is_marked_corroborated` |
| B123 | Severity is preserved as what the models said; disagreement stays visible. | `test_disagreeing_severities_are_all_preserved`; `test_severity_is_not_collapsed_into_one_verdict`; `test_agreement_on_severity_is_not_reported_as_disagreement`; `test_disagreement_about_severity_is_visible` |
| B124 | Ordering uses the highest severity any model assigned. | `test_the_highest_claimed_severity_is_available_for_ordering`; `test_findings_are_ordered_by_highest_severity`; `test_one_model_calling_it_critical_lifts_the_whole_finding`; `test_equal_severities_are_ordered_predictably`; `test_severity_ordering_depends_on_the_allowed_list_staying_ordered`; `test_findings_appear_in_severity_order` |

### Output (B125-B128)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B125 | The default output is a markdown report grouped by file and ordered by severity. | `test_findings_are_grouped_under_their_file`; `test_a_single_line_finding_shows_that_line`; `test_a_finding_spanning_several_lines_shows_the_span`; `test_no_bare_finding_count_is_printed`; `test_findings_appear_in_severity_order`; `test_a_review_with_no_findings_says_so_explicitly`; `test_rendered_markdown_is_pure_ascii`; `test_the_report_goes_to_stdout` |
| B126 | `--json` emits merged findings as a machine contract. | `test_the_json_is_valid_and_carries_a_schema_version`; `test_the_json_reports_findings_with_their_line_span`; `test_the_json_reports_agreement_with_both_halves_of_the_fraction`; `test_the_json_keeps_every_attributed_message`; `test_the_json_names_models_that_produced_nothing`; `test_the_json_reports_unparseable_responses`; `test_json_output_is_parseable` |
| B127 | The report states what was reviewed, which models participated, and what was missing. | `test_the_report_names_every_model_that_took_part`; `test_the_report_states_how_many_runs_each_model_completed`; `test_the_report_describes_the_diff_that_was_reviewed`; `test_a_model_that_failed_every_run_is_still_named`; `test_an_unavailable_model_is_named_but_its_error_text_is_not_repeated`; `test_responses_nobody_could_parse_are_reported` |
| B128 | Reports go to stdout; operational problems go to stderr and are not duplicated. | `test_operational_problems_render_separately_from_the_report`; `test_a_clean_review_produces_no_problem_output`; `test_the_markdown_report_does_not_repeat_the_problem_text`; `test_failure_detail_goes_to_stderr_only`; `test_the_report_goes_to_stdout` |

### Failure handling and exit codes (B129-B137)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B129 | Failed, timed-out, or unusable calls do not abort the review when other usable evidence exists. | `test_one_failing_run_does_not_stop_the_others`; `test_usable_responses_are_offered_even_when_the_review_is_partial`; `test_one_bad_run_does_not_lose_the_good_ones`; `test_rejecting_one_finding_does_not_discard_its_siblings` |
| B130 | If no model returned a usable answer, `atom review` fails loudly. | `test_when_no_model_is_available_the_review_fails_loudly`; `test_an_outcome_knows_when_no_model_produced_anything_usable`; `test_a_review_that_ran_but_found_nothing_is_not_treated_as_unusable`; `test_a_completed_run_whose_reply_was_unreadable_yields_no_usable_response`; `test_such_a_review_does_not_exit_zero`; `test_no_usable_response_fails_loudly`; `test_every_model_unavailable_fails_rather_than_reporting_nothing` |
| B131 | Partial reviews are marked partial in text and JSON output. | `test_a_partial_review_is_marked_partial_in_markdown`; `test_a_complete_review_is_not_marked_partial`; `test_a_partial_review_is_marked_partial_in_json`; `test_a_partial_review_exits_non_zero` |
| B135 | `atom review` reuses the Phase 1-3 exit code scheme. | `test_a_complete_review_exits_zero_even_with_findings`; `test_no_source_is_a_usage_error`; `test_two_sources_is_a_usage_error`; `test_no_usable_response_fails_loudly`; `test_every_model_unavailable_fails_rather_than_reporting_nothing`; `test_a_git_failure_is_not_reported_as_a_clean_review`; `test_review_without_a_source_exits_two_and_explains`; `test_review_with_two_sources_exits_two_and_explains` |
| B136 | A partial review exits non-zero even though a report was produced. | `test_a_partial_review_exits_non_zero`; `test_a_partial_review_is_marked_partial_in_markdown`; `test_a_partial_review_is_marked_partial_in_json` |
| B137 | One failed run is enough to make the review partial. | `test_one_failed_run_out_of_six_makes_the_whole_review_partial`; `test_an_outcome_knows_it_is_partial_when_a_run_failed` |

---

## Program-level tests

Unit tests demonstrate that the code is correct. They do not demonstrate that the
*program* runs - Phase 1 shipped 55 green tests on an unbuildable package, Phase
2 shipped 169 green tests on a program that raised `NameError` at startup, and
Phase 3 shipped 275 green tests on output that ran two messages together. The new
subcommand therefore carries subprocess tests that invoke `python -m atom.cli` for
real on paths that do not require a model call:

| Test | What it proves that an in-process test cannot |
|---|---|
| `test_the_module_can_be_executed` | The package starts outside the test harness. |
| `test_review_appears_in_the_top_level_help` | The command is wired into the top-level parser. |
| `test_review_help_runs_without_error` | The review subparser starts and exposes its contract. |
| `test_review_without_a_source_exits_two_and_explains` | The usage-error path survives the process boundary. |
| `test_review_with_two_sources_exits_two_and_explains` | Conflicting source validation survives the process boundary. |
| `test_a_refused_setting_does_not_produce_a_traceback` | Refused settings are developer errors, not crashes. |
| `test_nothing_is_defined_below_the_main_guard` | The Phase 2 startup failure cannot reappear by appending code below the guard. |

These do not call real models. The real-model gap is deliberate and recorded
below.

## Gaps

Several behaviours are only partly pinned by unit tests, or deliberately not
covered at all. Each is recorded here rather than quietly omitted:

| Area | Why not tested | Mitigation |
|---|---|---|
| Real model calls | Unit tests do not call paid or networked model CLIs. Calling live models would make the suite slow, flaky, account-dependent, and costly. | The runner seam is unit-tested, and the extractor/merge logic was checked against the saved spike responses recorded in [findings.md](findings.md). |
| Review quality (D6) | Agreement predicted the planted defects in one fixture, but quality on real historical diffs is not a unit-test property. | Kept as gate evidence in [design-spec.md](design-spec.md) and [decisions.md](decisions.md); the Phase 4 gate must run `atom review` on the Phase 1 diff. |
| Large-diff model behaviour (D8) | Tests assert the whole diff is not truncated and does not travel in argv, but they do not measure when a model's context, latency, or quality falls off. | B106b reports diff size; Cycle 6 pins the argv-size invariant instead of a guessed threshold. |
| Non-Windows platforms (D10) | The observed failures were Windows-specific: App Execution Alias, PATHEXT, and command-line length. The suite does not prove the same symptoms on Unix. | The implementation uses platform-neutral seams where possible; D10 remains pending in [decisions.md](decisions.md). |
| Cost per review (D11) | Tests cannot measure token or credit spend, and P4-2 deliberately triples call count. | Tracked as pending in [decisions.md](decisions.md). |
| Triple backticks inside a finding message (D12) | A greedy recovery path would be an unobserved heuristic. | `test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly` pins the loud failure so any future fix is deliberate. |
| Posting review comments | Posting to GitHub is outside Phase 4. | Left to Phase 5 by [design-spec.md](design-spec.md). |

## Cycle 8 (late) — run classification (B130 amended, B131 amended, B131a-c)

| ID | Behaviour | Test | Priority |
| --- | --- | --- | --- |
| B131b-1 | Unreadable reply leaves the denominator | `test_an_unreadable_reply_is_left_out_of_the_denominator` | High |
| B131b-2 | Both readable runs agreeing is not shown as a dissent | `test_a_finding_both_readable_runs_reported_is_not_shown_as_a_dissent` | High |
| B131-1 | Completed run that did not answer makes the review partial | `test_a_run_that_completed_without_answering_makes_the_review_partial` | High |
| B131c-1 | Partial notice counts the unreadable run | `test_the_partial_notice_counts_the_run_that_could_not_be_read` | Medium |
| B131b-3 | Payload reports answered runs alongside completed ones | `test_the_payload_reports_answered_runs_alongside_completed_ones` | Medium |
| B131-2 | A partly-parsed reply still counts as an answer | `test_a_reply_that_partly_parsed_still_counts_as_an_answer` | High |
| B131-3 | A clean review counts every run and is not partial | `test_a_clean_review_still_counts_every_run_and_is_not_partial` | High |
| B131-4 | A model with every reply unreadable renders without crashing | `test_a_model_whose_every_reply_was_unreadable_renders_without_crashing` | Medium |
| B131-5 | A missing run is still partial | `test_a_missing_run_is_still_partial` | High |
| B131-6 | Empty, whitespace and prose replies all count as silence | `test_a_reply_with_no_findings_in_it_counts_as_silence` | High |
| B131c-2 | A run that returned nothing is named in the report | `test_a_run_that_returned_nothing_is_named_in_the_report` | Medium |
| B131c-3 | An unreadable reply is not named twice | `test_an_unreadable_reply_is_not_named_twice` | Low |
| A19-1 | Only a pure file-guard rejection counts as an answer | `test_only_a_pure_file_guard_rejection_counts_as_an_answer` | High |
| A5-1 | An overruled reply does not make the review partial | `test_a_reply_overruled_by_the_file_guard_does_not_make_the_review_partial` | High |
| A5-2 | An overruled reply still leaves the denominator | `test_an_overruled_reply_still_leaves_the_denominator` | High |
| A5-3 | An unparseable reply is still silence | `test_an_unparseable_reply_is_still_silence` | High |
| B130-1 | An overruled reply is not "no usable response" | `test_an_overruled_reply_is_not_called_a_review_that_produced_nothing` | High |
| A20-1 | An overruled reply gets its own heading | `test_an_overruled_reply_gets_its_own_heading` | Medium |
| A20-2 | Partial total excludes an overruled reply | `test_the_partial_total_excludes_an_overruled_reply` | High |
| B131c-4 | The banner does not promise stderr detail | `test_the_banner_does_not_promise_stderr_detail` | Medium |
| A19-2 | Payload distinguishes overruled from unreadable | `test_the_payload_distinguishes_an_overruled_reply_from_an_unreadable_one` | Medium |
| B131a-1 | A run that answered is never also counted as overruled | `test_a_run_that_answered_is_never_also_counted_as_overruled` | High |
| B131a-2 | A run answering despite a malformed element is not called unreadable | `test_a_run_that_answered_despite_a_malformed_element_is_not_called_unreadable` | High |

## A21 — corroboration is a same-line claim

| ID | Behaviour | Test | Priority |
| --- | --- | --- | --- |
| A21-1 | Two models on different lines of one group is not corroboration | `test_two_models_on_different_lines_of_one_group_is_not_corroboration` | High |
| A21-2 | Two models on the same line is still corroboration | `test_two_models_on_the_same_line_is_still_corroboration` | High |
| A21-3 | Real agreement survives an unrelated line joining the group | `test_agreement_on_one_line_survives_an_unrelated_line_joining_the_group` | High |
| A21-4 | One model reporting twice is not corroboration | `test_one_model_reporting_twice_on_a_line_is_not_corroboration` | Medium |
| A21-5 | `model_count` still reports every model in the group | `test_model_count_still_reports_every_model_in_the_group` | High |
| A21-6 | A single-line group from two models is unaffected | `test_a_single_line_group_from_two_models_is_unaffected` | Medium |

## A22 — nearby multi-model reports

| ID | Behaviour | Test | Priority |
| --- | --- | --- | --- |
| A22-1 | The same defect at adjacent lines is reported as nearby | `test_the_same_defect_at_adjacent_lines_is_reported_as_nearby` | High |
| A22-2 | Same-line agreement is not also reported as nearby | `test_same_line_agreement_is_not_also_reported_as_nearby` | High |
| A22-3 | Agreement on one line wins over a nearby report | `test_agreement_on_one_line_wins_over_a_nearby_report` | High |
| A22-4 | One model across several lines is neither signal | `test_one_model_across_several_lines_is_neither_signal` | Medium |
| A22-5 | A lone finding is neither signal | `test_a_lone_finding_is_neither_signal` | Medium |

## A23 — per-report schema versions

| ID | Behaviour | Test | Priority |
| --- | --- | --- | --- |
| A23-1 | The review payload carries the bumped review version | `test_the_review_schema_version_records_the_corroboration_narrowing` | High |
| A23-2 | The four unaffected reports keep version 1 | `test_the_other_reports_did_not_change_and_keep_their_version` | High |

## A26 — the default model pair is pinned to the measured one

Until A26 nothing asserted which models `atom review` consults by default. Every
other test passes its models in explicitly, so the tuple could be edited to try a
candidate and ship with the suite fully green. These two make that a deliberate act.

| ID | Case | Test | Priority |
|---|---|---|---|
| A26-1 | The default pair is the two models that scored above 90% | `test_the_default_models_are_the_two_that_scored_above_ninety_percent` | High |
| A26-2 | `--help` names the models the CLI actually uses | `test_the_help_text_names_the_models_it_actually_uses` | Medium |