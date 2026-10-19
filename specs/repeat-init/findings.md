# Findings

## Resolved

- Valid repeat init previously returned 2 despite requiring no changes. The real CLI experiment now shows two exit-0 repeats with all 56 snapshot entries unchanged and the approval retained.
- Partial initialization previously bypassed the guard, reran checks, rewrote six paths, and erased the retained approval when config was missing. Both partial cases now return 2 with all 55 snapshot entries unchanged; the retained approval survives the missing-config case.
- Shared onboarding validity is checked before any detection/check/write path; regression cases cover configuration/state corruption, module conflicts, scaffold anchors, and read failures.

## Review

Independent gpt-5.4 and gemini-3.8-flash reviews completed. No actionable findings remain. One Minor candidate about exact manifest/ignore-block equality was rejected with explicit contract-based reasoning in [review.md](review.md); no Blockers or Majors were reported.

## Remaining boundaries

No unresolved findings within the approved sequential-repeat scope. Concurrent initialization and exhaustive bundle-content/link auditing are not provided. Cross-platform CI has not run for this uncommitted local change.

Evidence: [full Python gate](verification.txt), [real CLI reproduction after the fix](verification-probe.txt), [TDD report](tdd-report.md).
