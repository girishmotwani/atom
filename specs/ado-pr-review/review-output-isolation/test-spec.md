# Test Spec: ownership-aware CLI review responses

Approved design: [design-spec.md](design-spec.md). Python tooling; no live CLI/model invocation.

## Behavior-to-test map

| Design behavior | Test obligation |
|---|---|
| 1 | test_invoke: JSONL review flags; exact unchanged probes; stdin prompt, exclusions, bounds and ordering regressions |
| 2 | test_invoke: raw stdout plus copilot_jsonl metadata on completed native calls; legacy ModelRun default and unchanged failed outcomes |
| 3 | test_extract: JSONL object/type/data validation, blank lines, CRLF and unknown metadata; safe line diagnostics and no text fallback |
| 4 | test_extract: independent agentId/parentToolCallId exclusion; child before/after parent; malformed ownership; deltas/tool replies cannot answer |
| 5 | test_extract: explicit/unphased parent, commentary/tool exclusion, malformed message fields, absent/blank/multiple parent failures |
| 6 | test_extract: final unique successful root result; missing/nonzero/bool/malformed/duplicate/trailing result failures; root versus child errors/results |
| 7 | test_extract: unchanged fence/schema/file guards after selection; valid parent [] versus invalid parent/valid child; legacy text regressions |
| 8 | test_cli_review/test_review_output: completed versus readable, partial/nonzero, no false clean report, no metadata excerpt leakage, blank replies, denominators |
| 9 | Existing composition tests use format-aware synthetic CLI output, retaining deliberately invalid payloads. README explains isolation and strict failures. |

## Order and evidence

Use one behavioral red/green loop at a time: invocation output contract; response metadata; basic selection; ownership; candidate validation; record validation; terminal completion. Add boundary cases to their relevant loop before implementing the branch. Capture exact outputs in private session logs and retain them outside the source tree. Already-green legacy regression cases are not claimed as new red evidence.

## Redundancy audit

No Go compiler/vet cases apply to this Python parser. JSON fields are runtime input, so null, bool-versus-int, empty markers and wrong field types can silently alter selection and require tests. No new threads, cancellation behavior or process lifecycle are introduced; existing bounded-worker and Windows runner tests cover unchanged lifecycle rather than manufacturing a Go race gate. No candidate tests removed as compiler-proven.

## Collaborator policy

Keep direct ModelRun fixtures in default text mode. Add one shared sanitized event builder in tests/conftest.py for native CLI fakes. Fakes return framed output only when review commands request JSONL; probes remain text. Preserve supplied invalid findings payloads inside the envelope, empty process stdout as empty, and raw malformed-envelope tests as raw. Do not blanket-convert transport errors into valid responses.

## Actual implementation mapping

| Behavior | Concrete coverage |
|---|---|
| 1 | test_requests_structured_review_output_to_isolate_delegated_answers; preserved TestProbeExclusions, TestAvailabilityProbing, TestRepetition and prompt-on-stdin invocation tests |
| 2 | test_native_response_encoding_is_recorded_without_parsing_stdout; test_unsupported_response_format_does_not_fall_back_to_text; preserved per-run outcome and direct text fixtures |
| 3 | test_invalid_record_type_is_not_ignored_as_metadata; test_bad_framing_has_safe_line_diagnostics_without_fallback; test_invalid_parent_data_is_not_a_findings_schema_error; test_crlf_blank_lines_and_non_message_events_do_not_contribute_content |
| 4 | test_child_cannot_replace_parent_regardless_of_order; test_invalid_ownership_does_not_default_to_root; test_child_completion_errors_and_invalid_findings_do_not_overrule_root |
| 5 | test_commentary_and_tool_requests_are_not_answers; test_unphased_parent_is_supported; test_malformed_candidate_fields_are_transport_failures; test_missing_or_ambiguous_parent_is_not_rescued |
| 6 | test_incomplete_or_failed_stream_cannot_report_clean, including absent/failed/bool/malformed/duplicate/trailing/child-only terminal and root error cases |
| 7 | test_selects_parent_content_before_strict_findings_validation; test_selected_parent_still_obeys_strict_findings_schema; test_selected_parent_keeps_fence_handling_and_file_guard; preserved text-mode fence/schema/file-guard tests |
| 8 | test_bad_stream_does_not_discard_another_run; test_transport_failure_keeps_completion_but_not_answer_count; test_no_readable_parent_never_becomes_a_clean_review; preserved test_review_output cases for silence, file-guard overruling and denominators |
| 9 | test_only_parent_findings_reach_the_report (Markdown/JSON); test_pr_transport_failure_is_partial_and_still_cleans_checkout; existing local/PR-entry/report/style/toolchain suites; README paragraph verified on disk |

## Current verification

The [current verification](../verification.md) covers these unchanged deterministic tests. No new runtime dependency, lifecycle owner, thread, cancellation path, live-model compatibility result, or Go race result is introduced by this cleanup.
