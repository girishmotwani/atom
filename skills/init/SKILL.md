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
atom init --check
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
  config.json       # module path, build/test commands, model roles, coverage target
  state.json        # pipeline + phase state
  events.jsonl      # structured event log
  baseline.json     # the pre-Atom check result
specs/              # pipeline artifacts
poc/                # throwaway spikes
```

Adds to `.gitignore`: `.atom/events.jsonl`, `.atom/state.json`.

`specs/` and `poc/` are **committed** — they are the reviewable record of how the code
came to look the way it does.

## Step 5 — Record the commands

Write the real build and test commands into `.atom/config.json`, confirmed by running
them rather than assumed from the file layout. Many repositories wrap Go in a
`Makefile` or a task runner, and guessing produces failures three skills later.

If they can't be determined, ask.

## Step 6 — Point the agent at the instructions

Ensure the repository's agent instructions reference Atom's, so every session loads
the discipline:

- `AGENTS.md`, or
- `.github/copilot-instructions.md`

Add a line pointing at Atom's [AGENTS.md](../../AGENTS.md) and its skills directory.
If the repository already has instructions, **add to them** — do not overwrite.

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
- [ ] Repository agent instructions reference Atom
- [ ] Developer briefed, including model guidance

## Next

`/atom:discover`.
