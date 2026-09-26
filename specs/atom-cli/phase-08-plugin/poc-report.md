---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
status: "ran"
spike: "../../../poc/copilot-plugin-surface/claims.md"
---

# POC Report — Phase 8: shipping Atom as a Copilot CLI plugin

## The question

Can Atom ship as a single Agent Plugins 1.0 plugin such that one install gives a
developer Atom's skills **and** `/atom-*` slash commands inside Copilot CLI —
with no bespoke injection step and no relocation of `skills/atom-*/`?

Claims and thresholds were fixed in
[claims.md](../../../poc/copilot-plugin-surface/claims.md) before the first
`copilot plugin install`. None were changed afterwards.

## Verdict: Confirmed

All four claims passed. Full evidence:
[results.md](../../../poc/copilot-plugin-surface/results.md).

| Claim | Result | Evidence |
|---|---|---|
| Plugin installs | Pass | `Plugin "atom-probe" installed successfully.` |
| Plugin-root `skills/` discovered | Pass | `Plugin skills: atom-probe-skill` |
| `commands/` registers a slash command | Pass | `/atom-probe PROBE123` → `ATOM_COMMAND_LOADED PROBE123` |
| `agents/` registers an agent | Pass | `--agent atom-probe:atom-probe-agent` → `ATOM_AGENT_LOADED` |

## What the design must now take as given

1. **Skills are already slash commands.** A skill is invokable as `/<skill-name>`
   with no command file. Atom's nine skills became `/atom-poc`, `/atom-spec`,
   `/atom-tdd` and the rest by adding one `plugin.json` — no new plumbing.
   Verified against the real repository, not only the fixture.

2. **Name collisions are silent, and the command always loses.** A command
   sharing a skill's name is shadowed by the skill; a command sharing the
   plugin's name never runs. Nothing warns you. This is now guarded by
   `tools/tests/test_plugin.py`.

3. **The plugin must not be named `atom`.** A plugin named `atom` would shadow a
   skill named `atom`. The plugin is `atom-go`; the marketplace is `atom`.

4. **`source: "."` works**, so the repository root is the plugin. Atom needed no
   restructuring: `skills/atom-*/SKILL.md` was already the Agent Plugins 1.0
   layout.

5. **Direct installs are deprecated.** The CLI warns that only
   `plugin@marketplace` installs will be supported in future, so documentation
   must not tell users to install from a repository URL.

6. **Installation is global.** The plugin answered `/atom-poc` correctly from an
   unrelated repository. Atom needs **no per-repo injection at all** — strictly
   simpler than symlinking skills into every target repo.

## Counted, not assumed

Nine skills load, not ten. `skills/atom/` holds shared `references/` and
`templates/` and has no `SKILL.md`, so it is correctly not a skill. This was
established by listing the directory rather than inferred from the count.

## Not proven

- That the model reliably picks the right beat from arbitrary free text. One
  example worked (`a rate limiter ...` → DISCOVER). That is an anecdote, not a
  measured rate, and it is the obvious candidate for the next spike.
- Installation from a GitHub remote. Every test used a local marketplace path.
- Behaviour when a second installed plugin claims the same command name.
