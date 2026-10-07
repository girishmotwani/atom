---
name: init
description: 'Onboard a Go repository to Atom: create .atom/, detect toolchain, verify a green baseline. Keywords: init, onboard, setup, install atom, bootstrap, add atom to this repo.'
---

# /atom:init

One-time setup for a Go repository.

## When to use

- Adding Atom to a repository for the first time
- `.atom/` is missing or corrupt
- Verifying the toolchain before starting a pipeline

## Step 1 — Confirm this is a Go repository

Atom is Go-scoped. It needs a `go.mod`.

If there isn't one, stop and ask the developer whether to create a module or whether
Atom is the wrong tool here. Do not invent a module path.

## Step 2 — Check the toolchain

The `atom` command has to exist before it can check anything else. Follow
[bootstrap.md](../atom/references/bootstrap.md) first — it installs the command
for a developer who has only installed the plugin.

```bash
atom check --no-race
```

Verifies:

| Tool | Needed for | If missing |
|---|---|---|
| `go` ≥ 1.21 | everything | hard stop |
| `gofmt` | formatting gate | hard stop (ships with Go) |
| `git` | `/atom:ship` | warn; pipeline still runs |
| `gh` | pull requests | warn; `/atom:ship` degrades to a manual push |
| `python` ≥ 3.10 | Atom's own tooling | hard stop |

Report every missing tool at once. Discovering them one hard stop at a time wastes the
developer's time.

## Step 3 — Establish a green baseline

```bash
atom check --no-race
```

**Run this before changing anything.** This initial check establishes the untouched
tree's baseline without race detection; it is not completion verification. Keep
`atom check` with race detection enabled for final verification.

If the tree is already failing, record the exact failure in `.atom/baseline.json` and
tell the developer immediately. A pre-existing failure discovered three phases later
looks like something you caused, and costs real time to disprove.

Do not fix the baseline as part of init unless the developer asks. Report it.

## Step 4 — Scaffold

```bash
atom init
```

Creates:

```
.atom/
  atom/                  # self-contained local instructions and skills
  config.json       # module path, build/test commands, model roles, coverage target
  state.json        # pipeline + phase state
  events.jsonl      # structured event log
  baseline.json     # the pre-Atom check result
specs/              # pipeline artifacts
poc/                # throwaway spikes
```

Maintains a marked block in `.gitignore` for machine-local runtime data:
`.atom/baseline.json`, `.atom/events.jsonl`, and `.atom/events.lock`. Existing ignore
rules are preserved. `.atom/config.json`, `.atom/state.json`, and `.atom/atom/**`
remain tracked because they are shared project configuration, approvals, and
instructions.

Ignore rules do not untrack files already committed. If Git already tracks one of
these generated files, tell the developer to remove that specific path from the index
with `git rm --cached <path>` after confirming it is safe; never run the command
silently or untrack the whole `.atom/` directory.

`specs/` and `poc/` are **committed** — they are the reviewable record of how the code
came to look the way it does.

## Step 5 — Record the commands

Write the real build and test commands into `.atom/config.json`, confirmed by running
them rather than assumed from the file layout. Many repositories wrap Go in a
`Makefile` or a task runner, and guessing produces failures three skills later.

If they can't be determined, ask.

## Step 6 — Install the local instructions

`atom init` copies Atom's instructions, references, templates and skills into
`.atom/atom/`. It also creates or updates
`.github/copilot-instructions.md` with a relative link to that local bundle.
Nothing in the target repository should point back to the Atom checkout or an
installed-plugin directory.

If the repository already has Copilot instructions, `atom init` preserves them and
adds the managed local reference once.

## Step 7 — Report

Tell the developer:

- Toolchain status, including anything missing
- The baseline result, stated plainly
- What was created
- The recommended model setup — see [model-guidance.md](../atom/references/model-guidance.md)
- The next step: `/atom:discover`

---

## Done when

- [ ] `go.mod` confirmed
- [ ] Toolchain checked, all gaps reported together
- [ ] `atom check --no-race` baseline captured before any change
- [ ] `.atom/`, `specs/`, `poc/` created; `.gitignore` updated
- [ ] Build and test commands confirmed by running them
- [ ] Local Atom bundle installed under `.atom/atom/`
- [ ] Repository agent instructions reference the local bundle
- [ ] Developer briefed, including model guidance

## Next

`/atom:discover`.
