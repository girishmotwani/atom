# Findings

- The missing `__main__` guard made `python -m atom.artifact_cli` exit 0 without writing. The module fallback now executes `main()` and has subprocess regression coverage.
- The prior `/atom:init` contract was impossible for the CLI to satisfy: `atom init` did not capture `.atom/baseline.json`, create `specs/` and `poc/`, or record the build/test commands it exercised.
- Moving those operations into `atom init` removed separate state-file writes from the agent workflow. The final interactive transcript contains zero state-file write approval prompts.
- The first repaired run still required nine shell approvals because the skill performed redundant post-init shell verification and retried recursive path scans. Restricting successful verification to named file reads reduced the final run to three approvals.
- The remaining three approvals are for shell commands, not files. Two exist because this machine's Python Scripts directory is not on PATH; the third authorizes `atom init` itself.
- The final repository contained no reference to the Atom checkout or installed-plugin directory, so repeated reads of `verification.md` stay inside the onboarded repository.
