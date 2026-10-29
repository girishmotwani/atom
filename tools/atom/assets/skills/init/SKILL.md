---
name: init
description: 'Onboard a Go repository to Atom: capture its initial baseline or confirm existing setup without changes. Keywords: init, onboard, setup, install atom, bootstrap, add atom to this repo.'
---

# /atom:init

Set up a Go repository, or confirm an existing matching setup without changes.

## When to use

- Adding Atom to a repository for the first time
- Confirming that an already onboarded repository needs no changes
- Diagnosing missing or corrupt onboarding without silently repairing it
- Verifying the toolchain before starting a pipeline

## Step 1 — Confirm this is a Go repository

Atom is Go-scoped. It needs a `go.mod`.

If there isn't one, stop and ask the developer whether to create a module or whether
Atom is the wrong tool here. Do not invent a module path.

## Step 2 — Bootstrap the command

Follow [bootstrap.md](../atom/references/bootstrap.md). It establishes working forms
for both `atom` and `atom-write-artifact` without replacing an installed package.

On Windows, bootstrap offers the one-time `setup-path` opt-in when entry points are
hidden. After successful setup, use its printed absolute executable commands in this
session. Do not re-probe command names or ask again to locate the same executables.
If the developer declines, keep the working module forms instead.

Do not locate or read Atom's Python source while onboarding another repository.
Use the command forms established by bootstrap from the target module directory;
use `--help` when an option is unclear, not the implementation in an external
checkout or installed package.

Existing `.atom/` files do not require an implementation audit. Read the named local
files in steps 4 and 5 and report any discrepancy. If `atom init` refuses because
existing setup is conflicting, incomplete, or corrupt, preserve it and report the
named problem; do not add `--force`
without the developer's explicit approval to discard that state.

## Step 3 — Run deterministic onboarding

```bash
atom init
```

On a valid matching repeat, this command returns 0 with an explicit **read-only no-op**
message. It does not refresh the baseline, detect build commands again, reset approvals,
update the local bundle, append events, or change files and timestamps.

An existing `.atom/` with conflicting, incomplete, or corrupt setup returns a nonzero
error without repair. Restore or repair the named files before retrying. Explicit
`--force` deliberately resets the project record and discards recorded approvals; it
is not a workaround for a normal repeat.

On first initialization, this one command performs the operations that must agree:

- runs the untouched no-race baseline before writing Atom files;
- records the exact result in `.atom/baseline.json`, including failures;
- infers the module path and records the verified build/test commands;
- prefers the repository's own `make build` / `make test` when a Makefile defines them;
- creates the project scaffold and installs the local instruction bundle.

On first initialization it creates:

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

If the printed baseline is failing, tell the developer immediately. Do not repair the
repository during onboarding unless asked. A pre-existing failure discovered three
phases later looks like something Atom caused.

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

## Step 4 — Confirm the recorded commands

For first initialization, read `.atom/config.json` and confirm the module, build
command, and test command match the baseline that `atom init` printed. Do not rewrite
the file through a generic edit tool; a mismatch is an onboarding defect to report.

For a successful no-op, report the preserved configuration. No new baseline was run,
so do not compare commands to a newly printed baseline or claim they were reverified.

A repository with a Makefile will show `make build` and `make test` rather than the Go
defaults, and `atom init` prints the reason it chose them. This is expected, not a
defect: the project's own build usually carries tags, ldflags or generation steps that
`go build ./...` would silently skip. Targets are resolved one at a time, so a Makefile
with only `build` correctly leaves the test command Go-native. If `make` is not
installed, Atom says so and stays on the Go defaults rather than running a command that
cannot work.

## Step 5 — Confirm the local instructions

On first initialization, `atom init` copies instructions, references, templates and
skills into `.atom/atom/`. It also creates or updates
`.github/copilot-instructions.md` with a relative link to that local bundle.
Nothing in the target repository should point back to the Atom checkout or an
installed-plugin directory.

If the repository already has Copilot instructions, `atom init` preserves them and
adds the managed local reference once.

### Keep verification approval-free

After first initialization, verify onboarding by reading these named files:

- `.atom/config.json`
- `.atom/baseline.json`
- `.atom/atom/manifest.json`
- `.github/copilot-instructions.md`
- `.gitignore`

After a successful no-op, the same shared-file reads are sufficient without
`.atom/baseline.json`: machine-local baseline and event files may be absent on a clone.
Do not recreate them or require empty `specs/` and `poc/` directories to be restored.
The no-op validates shared onboarding structurally, not the installed bundle's version
or every instruction's content.

Do not run `git status`, recursive shell scans, or another Atom command on the normal
success path. The init output plus these file reads prove the contract without asking
the developer for more shell approvals. Run a follow-up command only when the init
output or one of these files exposes a specific discrepancy.

## Step 6 — Report

Tell the developer:

- For first initialization: the baseline result, including every failed gate, and
  what was created
- For a no-op: setup was already valid, nothing changed, and no baseline was refreshed
- The recommended model setup — see [model-guidance.md](../atom/references/model-guidance.md)
- For first initialization: next step `/atom:discover`; for a no-op: resume the
  existing workflow, using `/atom-status` if its position is unclear

---

## Done when

- [ ] `go.mod` confirmed
- [ ] `atom init` completed
- [ ] First init: no-race baseline captured before any Atom file was written
- [ ] First init: `.atom/`, `specs/`, `poc/` created; `.gitignore` updated
- [ ] First init: config commands match the commands exercised by the baseline
- [ ] Repeat: valid matching setup confirmed without changes or a new baseline
- [ ] Local Atom bundle present under `.atom/atom/`
- [ ] Repository agent instructions reference the local bundle
- [ ] Developer briefed, including model guidance

## Next

First initialization: `/atom:discover`. Successful no-op: resume the existing workflow.
