---
project: "ado-pr-review"
phase: "bounded-review-execution"
design_spec: "design-spec.md"
date: "2026-10-29"
---

# Test spec: opt-in fixed-evidence review

## Toolchain redundancy audit

None - no proposed case was unfailable. This is Python tooling: Go nil/interface/overflow/vet guarantees do not apply. Do not test dataclass freezing or SHA-256 itself; test the captured packet's independence from later file/sequence changes, original UTF-8 bytes, and rejection of inconsistent caller metadata.

Silent failures worth testing: blank/NUL/invalid-encoding input, an ignored file error after an earlier valid file, wrong launch-directory resolution, incomplete command-policy propagation, silent tool-enabled fallback, child output salvaged as findings, failed output leaked as diagnostics, lost partial-run denominators and misleading clean scope. Python integers do not wrap here; no Go typed-nil, goroutine or arithmetic contract is introduced.

## Coverage map

All rows are required. Existing coverage is regression evidence, not claimed as a new RED loop.

| Design behavior | Test / existing regression | Validation state |
| --- | --- | --- |
| 1 | Existing exact probe flags, prompt/report schema; test_fixed_evidence_cli_reports_scope | verified |
| 2 | test_context_requires_opt_in_before_io; test_direct_context_requires_opt_in_before_runner | verified |
| 3 | test_context_capture_preserves_bytes_and_order; test_context_capture_rejects_invalid_input; test_context_capture_rejects_duplicate_paths | verified |
| 4 | test_context_capture_preserves_bytes_and_order; test_direct_context_rejects_inconsistent_metadata | verified |
| 5 | test_fixed_prompt_freezes_json_documents_and_preserves_diff | verified |
| 6 | test_fixed_prompt_freezes_json_documents_and_preserves_diff | verified |
| 7 | test_fixed_evidence_exclusions_reach_probes_and_reviews | verified |
| 8 | test_fixed_evidence_rejects_observable_execution | verified |
| 9 | Existing strict transport/schema tests; test_fixed_evidence_keeps_diff_file_guard | verified |
| 10 | test_fixed_evidence_cli_reports_scope | verified |
| 11 | test_fixed_prompt_freezes_json_documents_and_preserves_diff; existing full-diff capture tests | verified |
| 12 | test_run_review_blocks_before_models_when_required_gate_fails[True]; existing runner timeout/cleanup tests | verified |
| 13 | test_structured_failure_retains_raw_evidence_without_diagnostic_leak | verified |
| 14 | test_structured_failure_retains_raw_evidence_without_diagnostic_leak; test_fixed_probe_failure_is_safe_without_fallback; existing text/probe regressions | verified |
| 15 | test_fixed_evidence_rejects_observable_execution; existing empty transport excerpts | verified |
| 16 | test_fixed_evidence_cli_reports_scope | verified |
| 17 | test_fixed_evidence_cli_reports_scope | verified |
| 18 | test_pr_context_is_captured_before_preparation_from_launch_directory; existing PR report limitations | verified |
| 19 | test_fixed_evidence_execution_violation_is_incomplete; existing partial/no-usable/exit tests | verified |

## Ordered test cases and expected RED failures

1. Capture: arrange two actual temporary UTF-8 files with CRLF/non-ASCII/fences, load in caller order, change one on disk, assert labels/text/original byte counts/digests unchanged. Start with a declaration-only stub so RED is an assertion, not an import failure. Then table-drive invalid input (directory, missing, invalid UTF-8, NUL, blank, unreadable/resolution errors), including valid-first/invalid-second. Expect ContextInputError instead of a returned tuple; duplicate aliases expect ValueError. No file-I/O mocks except deterministic permission/resolution failures.
2. Invocation policy: fake the existing CommandRunner and invoke two repeated runs. Assert probes and reviews all use explicit source exclusions, stdin contains the same packet, MCP exclusions persist, ModelRun carries the mode. Expect no exclusion flag/unsupported mode until wired. Rejected probe must be safe and never fall back.
3. Structured diagnostics: arrange failed CommandResults with account-like sentinel stdout/stderr for both modes and each process outcome. Assert raw retention but no sentinel in detail or ordinary report/problem rendering. Expected RED: raw event details and discarded stdout. Preserve direct text callers and legacy probe behavior.
4. Extraction: use real JSONL framing with a valid root finding plus one tool request, tool execution, child message or child-owned otherwise-ignored event, including after the terminal result. Assert no findings, empty excerpt, static violation reason. Expected RED: valid findings salvaged/child ignored. Default ownership handling remains covered unchanged.
5. Composition/API preflight: use real run_review with fake process I/O; prove same full prompt across repeated reviewers, serialized adversarial delimiters, complete large document/diff, bytes/digest, direct sequence frozen, invalid opt-in/metadata before runner work, original file allowlist and toolchain blocking. Expected RED: no evidence snapshot or validation. No real model calls.
6. CLI/report: drive main through fake subprocess runner. Context without mode must fail before loader/runner work; invalid requested files block cleanly. Opted-in diff-only/document cases must disclose exact scope/quality and additive safe metadata in markdown/JSON, no local path or document text. Default shape must omit new metadata. Expected RED: parser rejects options, then report lacks scope.
7. PR boundary: fake only preparation/network boundary; prepare checks that capture already happened and can remove/change source before yielding a different checkout directory. Assert original launch-relative document snapshot reaches run_review, missing input prevents preparation, original provenance/limitations retained. Expected RED: wrong capture timing/location.

Commands use python -m pytest from tools, with selectors for the current behavior, then all affected files. Final project gate: python -m pytest tests -v --cov=atom. Capture actual RED/GREEN output privately and persist final verification evidence through the artifact writer. Run the existing link checker and scoped whitespace check. No dependency changes, new tooling, live inference, target PR access or automatic archive are authorized.

## Error/concurrency audit

Cancellation/timeout and Windows descendant ownership are unchanged runner obligations: existing tests remain authoritative; new failed-result translation tests cover their reporting. Evidence is synchronously captured and the immutable prompt is shared by the existing bounded executor; repeated concurrent fake calls verify identical stdin and snapshot independence. No new scheduler or mutable global capture state; Go -race is not a Python gate.

No behavior needs clarification before TDD. All 19 numbered behaviors map to new or explicit existing tests. No test is weakened to obtain green. Current verification records the applicable runtime evidence.

## Current verification and integration

The [current verification](../verification.md) covers the mapped behavior without claiming a fresh RED for inherited tests. Logical prompt disclosure remains covered by test_fixed_evidence_cli_reports_scope: Markdown names pre-transport UTF-8 identity; existing exact JSON assertions prevent schema/value drift.

test_fixed_evidence_keeps_changed_file_formatting_and_one_diff_capture verifies that untouched formatting defects do not block fixed-evidence review and that one diff feeds formatting and the caller-evidence prompt. test_pr_required_checks_still_block exercises both modes without weakening compiler-failure, no-output, no-model, or cleanup assertions.
