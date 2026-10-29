# Test spec: probe exclusion forwarding

Approved design: design-spec.md. The developer approved implementation and related README changes on 2026-10-27.

| Behavior | Cases |
| --- | --- |
| 1: unchanged default flags and no implicit server exclusions | Existing TestCommandsIssued.test_no_named_mcp_server_is_disabled_by_default; new exact-empty probe-command compatibility case |
| 2: ordered repeated exclusions, input unchanged | TestProbeExclusions.test_probe_command_preserves_exclusions_and_caller_input |
| 3: every probe, cwd/timeout and positional compatibility | TestProbeExclusions.test_probe_models_forwards_exclusions_and_preserves_call_settings |
| 4: same exclusions to probes/reviews, existing ordering/stdin | TestCommandsIssued.test_named_mcp_exclusions_reach_probes_and_reviews plus existing TestAvailabilityProbing ordering and stdin/whole-diff cases |
| 5: rejection, timeout, no review and partial reporting | New excluded-probe failure parameter cases plus existing TestAvailabilityProbing and TestPartialReviews cases |
| 6: CLI integration and docs | TestCommandsIssued.test_named_mcp_exclusions_reach_probes_and_reviews; existing CLI and PR CLI suites; README/link check |

Run the three new forwarding behaviors in separate red/green loops. New API absence may first raise TypeError; add only its empty parameter scaffold and rerun to a clean behavioral assertion failure before implementing forwarding. Existing compatibility and error semantics are regression obligations, not claims that pre-existing behavior is newly red. Supplementary cases may pass immediately after a loop establishes their behavior; disclose that rather than simulate test-first history.

All tests replace model execution through CommandRunner. No real model, clone or network call belongs in this TDD run. Preserve pre-existing test edits. Python's compiler does not prove argument forwarding, argv content, input nonmutation or failure diagnostics, so no case is removed under Go-only compiler/vet rules. Go nil/interface/overflow cases are not relevant to these string-sequence helpers; no tests are removed as redundant. No new synchronization or cancellation surface is introduced; existing bounded runner/concurrency tests retain those responsibilities.

Validation: smallest red/green selectors, then invocation, CLI review, PR CLI and review-composition suites together; existing Markdown link checker and scoped whitespace check. No dependency or gate-tool additions. Full-suite repetition is not needed absent targeted failures or unresolved integration concerns.

## Final mapping and result

- Exact-empty compatibility: TestProbeExclusions.test_empty_exclusions_preserve_the_exact_probe_command (omitted, tuple and list cases).
- Failure diagnostics and no review: TestProbeExclusions.test_failed_excluded_probe_keeps_diagnostic_and_prevents_review (rejection and timeout cases).
- Partial-result preservation: TestProbeExclusions.test_excluded_probes_preserve_partial_review_reporting.
- The three originally named forwarding tests all reached assertion RED before their production forwarding implementation.

The [current verification](../verification.md) applies to these unchanged tests. No live model invocation or new TDD loop is claimed by this artifact cleanup.
