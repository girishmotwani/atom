# Findings

- `atom init` previously wrote only `.atom` state and never installed the
  instructions or reference files that onboarding told the agent to read.
- The old onboarding contract pointed from the target repository into the Atom
  checkout or installed-plugin directory. Copilot path permissions treat that
  directory as external, which caused repeated prompts for
  `skills/atom/references/verification.md`.
- Existing target instruction files are preserved. A future migration may need
  to remove stale externally managed Atom blocks created by older versions;
  this change adds a local managed block without rewriting unrelated developer
  instructions.
