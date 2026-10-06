# Decisions

- Store the self-contained onboarding bundle under `.atom/atom/`, keeping all
  copied references inside the target repository.
- Package `AGENTS.md` and the complete `skills/` tree with `atom-cli` so both
  editable installs and built wheels can onboard repositories without access
  to the Atom source checkout.
- Create or update `.github/copilot-instructions.md` with one idempotent,
  relative link to `.atom/atom/AGENTS.md`; preserve existing instructions.
- Infer the module path from `go.mod` when `atom init` is called without
  `--module`, while retaining the explicit override for repositories that need
  it.
