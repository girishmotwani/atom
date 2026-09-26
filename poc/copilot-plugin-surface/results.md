# Results — copilot-plugin-surface

Run against Copilot CLI on Windows, 2026-06. Claims and thresholds were fixed
in `claims.md` before the first `copilot plugin install`; none were changed
afterwards.

## Verdict: **Confirmed**

C1, C2 and C3 all pass. C4 passes as well.

| ID | Claim | Result | Evidence |
|----|-------|--------|----------|
| C1 | Plugin installs | **Pass** | `Plugin "atom-probe" installed successfully. Installed 1 skill.` |
| C2 | Plugin-root `skills/` discovered | **Pass** | `copilot skill list` → `Plugin skills: atom-probe-skill` |
| C3 | `com.github.copilot/commands/` registers a slash command | **Pass** | `/atom-probe PROBE123` → `ATOM_COMMAND_LOADED PROBE123` |
| C4 | `com.github.copilot/agents/` registers an agent | **Pass** | `--agent atom-probe:atom-probe-agent` → `ATOM_AGENT_LOADED` |

## The finding that changed the design

**Skills are already slash commands.** A skill named `atom-probe-skill` is
invokable as `/atom-probe-skill` with no command file at all. When a command
file and a skill shared a name, the **skill won**:

    /atom-probe-skill SAMENAME  ->  ATOM_SKILL_LOADED    (not ATOM_COMMAND_LOADED)

So Atom's nine existing skills become `/atom-build`, `/atom-discover`,
`/atom-init`, `/atom-plan`, `/atom-poc`, `/atom-review`, `/atom-ship`,
`/atom-spec` and `/atom-tdd` **for free**, by adding one `plugin.json`.
Command files are only needed for surfaces that are not already skills.

Verified end-to-end against the real repository, not just the fixture:

    /atom-poc  ->  "I'm the Atom PoC beat, producing ... proof-of-concept ..."

## Name collisions are real and silent

Two collisions were observed, both resolved by the *non-command* side:

1. **Command vs plugin name.** Plugin `atom-probe` + command `atom-probe` →
   the command never ran. Renaming the command to `atom-poc` fixed it
   immediately (`ATOM_COMMAND_LOADED NOCOLLIDE`).
2. **Command vs skill name.** The skill shadows the command, as above.

Design rule: **a command's name must differ from the plugin name and from
every skill name.** Nothing warns you; the wrong thing just runs.

## `source: "."` works — the repo is its own plugin

`.github/plugin/marketplace.json` may list a plugin whose `source` is `"."`,
making the repository root the plugin directory. Atom needed **no
restructuring**: its `skills/atom-*/SKILL.md` layout is already exactly the
Agent Plugins 1.0 location.

Marketplace paths must be **absolute**. A relative `./market-fixture` was
parsed as a GitHub `owner/repo` and failed with
`repository 'https://github.com/./market-fixture.git/' not found`.

## Direct installs are deprecated

The CLI warns:

> Direct plugin installs (repos, URLs, local paths) are deprecated. Only
> plugin@marketplace installs will be supported in a future release.

So `copilot plugin install girishmotwani/atom` is **not** a durable
instruction. Atom must ship a marketplace and tell users to run the two
supported commands instead.

## Installation is global, not per-repo

The installed plugin answered `/atom-poc` correctly from an unrelated
repository (a Helios worktree). Atom therefore needs **no per-repo injection
step at all** — this is strictly simpler than symlinking skills into each
target repo.

`atom init` keeps a narrower job: creating `.atom/` project state. It is no
longer an installation mechanism.

## Counted, not assumed

- 9 skills load, not 10. `skills/atom/` holds shared `references/` and
  `templates/` and contains no `SKILL.md`, so it is correctly not a skill.
  This was verified by listing the directory, not inferred from the count.

## Not proven here

- That the model reliably picks the right beat from an arbitrary free-text
  description. One example worked (`a rate limiter ...` → DISCOVER); that is
  an anecdote, not a measured rate.
- Anything about installing from a GitHub remote — every test used a local
  marketplace path.
- Behaviour when another installed plugin claims the same command name.
