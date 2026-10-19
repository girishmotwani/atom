# Decisions

- Developer approved the POC brief and Python-tooling deviation, the Confirmed report, the exact design for test-first implementation, and the completed implementation for independent review.
- Use a Python driver rather than a Go spike because Atom init and persistence are Python; a Go wrapper would duplicate subprocess/snapshot operations. The driver still exercises real CLI subprocesses against a disposable Go module.
- One maintenance phase rather than a separate multi-phase plan. The executed reproduction serves as its proof. Use the repository's Python pytest/coverage gate instead of inventing a root Go module for atom check.
- Adopt the approved structural validation boundary: protect any existing .atom entry, preserve legitimate custom commands and older complete bundles, and keep ignored runtime files and empty artifact directories optional. Repeat init is neither an upgrade nor silent repair.
- Update the existing tracked-runtime-log-only onboarding fixture to request --force explicitly. Its setup is intentionally partial, which the approved design now refuses without consent. Ignore-rule and Git-index assertions are unchanged; this is an intentional contract shift, not weakened protection.
- Normalize whitespace in the CLI help assertion because argparse wraps `recorded approvals` across lines. The test still requires the same warning and no-op semantics; terminal wrapping is not part of the contract.
- Successful no-op skill guidance resumes the existing workflow rather than sending a progressed project back to discovery.
- No reviewer model configuration exists in this checkout. The developer explicitly selected gpt-5.4 and gemini-3.8-flash for two independent read-only reviews. Neither is the authoring model. No persistent model configuration was changed.
- Reject the single Minor candidate demanding exact manifest/ignore-block equality: the approved boundary is structural, preserves additive data, and does not require canonical rule ordering or installed-version equality. Detailed evidence and reasoning are in review.md. No actionable finding was deferred.
- No production contract deviated from the approved design. No commit, push, plugin update, or original target-repository modification was performed.

## Publication authorization (2026-10-19)

- The developer requested `commit and create PR`, authorizing publication of the reviewed repeat-init fix on a dedicated branch. Earlier no-commit/no-push statements describe the implementation/review capture time.
- Re-ran the complete Python CI gate immediately before publication; exact output is retained in ship-verification.txt and linked by ship-report.md. No production code changed after review.
- Use `gh` for the scoped GitHub PR rather than the Go-phase-oriented `atom ship` artifact inference. Preserve all unrelated short-namespace and ADO-review work outside the commit. Do not merge, force-push, amend prior commits, or update the installed plugin.
