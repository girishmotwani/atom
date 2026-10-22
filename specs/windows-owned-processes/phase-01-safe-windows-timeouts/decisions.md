# Decisions and approvals

- 2026-10-20: developer approved a disposable Python/native POC exception because Atom's tooling, including the defect, is Python. Three candidate trials confirmed the host-specific ownership question; report approved.
- 2026-10-21: developer selected stopping remaining owned Windows children on every return, including success, and approved the fail-closed design and distinct runner_error outcome for TDD.
- 2026-10-21: developer accepted the local implementation for review, with the supported-platform CI limitation explicitly open. This was not phase completion or a claim of passing CI.
- Developer authorized exactly two independent non-author reviewers, a phase-only commit/push and separate draft PR. Concrete reviewer models are runtime selections, not repository defaults. No extra batch is implied.
- Developer requested a separate private personal destination rather than transferring the original repository. Existing personal main is used so unrelated newer commits and repeat-init work are excluded. The original checkout, history and existing PR remain unchanged.
- Publication uses a standalone neutral evidence pack. Internal investigation material and private path-bearing raw records remain local. The 17 approved behavior contracts and frozen POC source are unchanged; historical selected output is labeled rather than presented as fresh shipping-tree evidence.
- The original local investigation needed a status-test lexical-order correction, but the neutral publication project does not sort before artifact-writer. That hunk is omitted from this shipping branch to avoid an unrelated change; the original dirty checkout is preserved.
- The required Python gate replaces inapplicable root Go gates for this Python tooling repair. Unrun tools and platforms exclude no review category.

## Review gate pause (2026-10-22)

The two approved independent review runs completed after a fresh shipping-tree Python gate. One reviewer raised a Major late-spawned-member verification race; the other raised partial-diff diagnostic bloat, busy-pipe throttling and an interrupt-finalization gap. All four are recorded, including the single-model Major. No fix, rejection or deferral is assumed from model consensus or severity labels.

Work pauses for developer triage before repairs or publication. No additional model spend, changed ownership mechanism, commit, push or PR creation is authorized by this pause itself. The original repository, its existing PR and private investigation material remain untouched.

## Developer review triage accepted (2026-10-22)

The developer selected fixing all four findings before PR creation and subsequently said "lets proceed". Implement the repairs test-first against existing behavior obligations; do not silently defer any finding. No new model batch or materially different ownership mechanism is approved.

## Review repair choices and validation (2026-10-22)

- Preserve the approved mechanism and failure contract. Read cumulative TotalProcesses before collecting member identities and again after termination/accounting waits. A change means identities may have been missed: report incomplete exit verification instead of assuming a second snapshot is enough. Existing runner_error/timeout precedence handles this conservatively; no new backend, flag, deadline or dependency is introduced. Read-only admission-query failure also cannot become success.
- Remove the fixed sleep only when a fair one-chunk-per-stream pass made progress; check the deadline every pass and still sleep when idle. The same bounded pumping rule applies to final output drain. No public throughput SLA is added.
- Keep main-thread SIGINT deferral installed for the complete owned lifetime, including result receipt and diagnostics, with one outer finally. Communication observes the deferred flag promptly; worker threads do not change handlers, and the previous handler is restored. Unexpected primary exceptions remain primary after cleanup.
- Use stderr diagnostics, not diff stdout, when converting a timed-out diff into a CLI error.
- A first late-member fixture attempt used insufficient query access on its retained observation handle. Its Access Denied output is retained as a fixture failure, not credited as the intended RED. Add PROCESS_QUERY_INFORMATION without weakening any assertion; the corrected test observed false completed/0 and absent timeout incompleteness before production repair.
- Remove the validation-only PYTHONPATH override after proving it invalidates the existing clean-venv packaging test; standard cwd import still resolves this shipping source. Do not change packaging logic to accommodate the override.
- Correct the newly observed ready-record fixture race: a visible file is not a guaranteed readable identity record on Windows. Reuse a bounded reader for both identity handshakes, retry only FileNotFoundError/PermissionError under the original deadlines, and re-raise persistent failure. Add deterministic transient and persistent failure tests. Actual exit checks, output checks and before-rescue directory removal are not relaxed.

## Publication readiness after remediation (2026-10-22)

All four developer-triaged fixes have regression evidence and the final standard shipping gate is green (1002 passed, 2 skipped, 79.85s, 95% coverage). Earlier failed gates remain in the evidence; no test expectation was relaxed. The original phase's accepted local TDD gate and explicit review-fix-before-draft-PR instruction govern this bounded remediation, not a new phase or an unapproved model batch. Draft publication remains within the developer's explicit phase-only commit/push/PR authorization. Supported CI and any merge remain separate; do not mark the phase complete or claim the fixes received another independent model review.

## Evidence whitespace preservation

The first staged whitespace audit correctly flagged trailing spaces copied from pytest traceback output and the archived counterexample's original blank line at EOF. Keep those bytes: stripping captured lines would change verbatim evidence, and changing the frozen Python spike would invalidate its recorded SHA-256. Only extra document-layout blank lines outside fenced captures were removed. Apply the normal whitespace check to every other staged path; check the raw evidence with blank-at-eol exempted and the one frozen spike with blank-at-eof exempted, scoped per command/file. No repository-wide formatter or whitespace policy is disabled.
