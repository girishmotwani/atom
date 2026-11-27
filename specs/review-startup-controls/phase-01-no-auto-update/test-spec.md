# Test specification

Approved design: design-spec.md. The developer selected
"Approve this spec and implement" on 2026-11-27.

## Behaviour-to-test coverage

| Contract | Executed evidence |
| --- | --- |
| 1: opt-in/default | test_no_auto_update_reaches_probes_and_reviews includes an omitted-flag fixed-evidence case; test_no_auto_update_preserves_other_command_arguments covers both builders with omitted/explicit false and fixed evidence on/off. |
| 2: every call | test_no_auto_update_reaches_probes_and_reviews exercises the real CLI/pipeline with two models and two runs: six child commands, flag exactly once, stdin preserved. test_no_auto_update_preserves_probe_and_review_deadlines verifies structured responses and stdin on repeated review calls. |
| 3: composition | The CLI matrix composes named MCP exclusions and fixed evidence with the opt-in flag and verifies neither is implicitly enabled. Builder cases preserve all other arguments. |
| 4: selectors/PR | The CLI matrix selects working/staged/branch. test_pr_no_auto_update_reaches_probes_and_reviews checks enabled/omitted PR paths, both child commands, named-MCP composition and temporary checkout cleanup. Existing pipeline tests protect gates/reports. |
| 5: failure/deadlines | test_no_auto_update_probe_failure_never_retries_without_flag covers a rejected and timed-out flagged probe: exactly one call, no review/fallback, diagnostic preserved. test_no_auto_update_preserves_probe_and_review_deadlines checks actual runner records for 60/600-second deadlines. |
| 6: documentation | test_review_help_documents_no_auto_update_scope exercises parser help. README factual review checks per-run bundled-version semantics, unchanged defaults/settings and explicit non-guarantees. |

## Sequence and results

First ran the CLI/pipeline forwarding test against the old parser and observed
clean expected-success assertion failures: unknown option exits 2. Then added
the minimum forwarding path. Boundary cases for API defaults, failed probes,
deadlines and PR integration used only fake runners. All 14 new cases passed as
part of the final 457-test affected-area suite. Exact output and commands are
preserved in regression-evidence.md, tdd-log.md and verification.md.

## Redundancy audit

No tests for a boolean getter, Python argument parsing itself, or constants alone.
Assert the observable child command/runner behavior rather than declarations.
No new concurrency, I/O cleanup or cancellation implementation requires tests.
Existing bounded-runner and PR-cleanup tests remain applicable. Tests that passed
immediately after the end-to-end repair check its boundaries; they are not claimed
as separate RED cycles demanding additional production changes.

## Validation boundaries

The affected review CLI, invocation, pipeline/formatting/continuation/output/style
tests and guidance checks ran in one final pytest invocation. Existing relative
link and whitespace checks include new phase artifacts. No root Go module:
do not fabricate atom check evidence. No live model calls or installed Atom
refresh. No full-suite, coverage or cross-platform success claim is made.
