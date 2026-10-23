# Findings: changed-file review formatting

## Discovery and addressed defects

The old run_review evaluated module-wide formatting before capturing the selected diff. Finding extraction was already changed-path scoped; formatting was not. Default gates are also used by standalone atom check, so globally narrowing FormatGate would have weakened an unrelated command. The production correction composes a private selected-snapshot gate only for review; shared defaults and all other gate commands remain untouched.

The executed synthetic proof confirmed all 14 fixed observations. Production regression work then caught and fixed missing branch/staged selection, pure-rename destination metadata, deletion-only/empty skip semantics, outside/nested-module evidence, misleading formatting prompt/report claims, malformed/unsafe source handling, invalid UTF-8 reporting, Git type-change framing and lost formatter stderr. See tdd-log.md for the actual failing and passing outputs.

The first full Python run caught the review skill's packaged copy not matching its edited source. Synchronized the packaged skill rather than relaxing the equality test. The corrected full run passed 1059 tests with 2 existing POSIX-only skips on Windows and 95% total coverage. See verification.md.

## Scope limits and pending evidence

Other module-wide review checks remain in place and can still independently block a later review. This correction does not implement affected-package checks, multi-module orchestration, initialized rules, richer comments or PR URL resolution. It does not establish end-to-end ADO feasibility or review quality. No private target checks or model calls ran as part of the proof/TDD.

No unresolved implementation finding is known before independent review. The two authorized non-author reviewer reports and supported-platform CI remain pending; this is not a claim that review/publication is complete.

## Final local disposition after independent review

Both selected independent reviewers completed one round. Both concrete medium Opus findings were accepted and repaired after failing regressions; Gemini reported no significant issues. No finding was deferred or rejected. See review.md and the post-review TDD evidence. Fresh full Python gate: 1067 passed, 2 skipped in 126.29s, 95% total coverage; new helper 95%. No production edit followed that run. No unresolved implementation/review finding is known. Supported-platform CI is still pending publication, and the broader ADO feasibility checkpoint remains outside this correction.
