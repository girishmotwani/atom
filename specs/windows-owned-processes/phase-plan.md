# Scoped phase plan: Windows owned command lifetimes

Publication boundary: one independently reviewable Python tooling repair. This is not a transfer of unrelated investigation material or an assertion that a broader project is complete.

1. Prove pre-execution ownership in a disposable synthetic fixture ([report](phase-01-safe-windows-timeouts/poc-report.md), approved 2026-10-20).
2. Describe the public lifecycle/error contract ([design](phase-01-safe-windows-timeouts/design-spec.md), approved 2026-10-21).
3. Implement test-first and accept the local result for review ([tests](phase-01-safe-windows-timeouts/test-spec.md), accepted 2026-10-21).
4. Independently review, triage, publish a draft PR and verify supported CI. Review and CI completion must be recorded rather than inferred.

The personal repository's existing main is the base. Unrelated newer enterprise commits and the separate repeat-init change are excluded. The original repository and its existing PR remain untouched.
