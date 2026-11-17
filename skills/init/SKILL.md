---
name: init
description: 'Recommend and perform approved Go repository setup, including a missing module, then onboard Atom or confirm matching setup without changes. Keywords: init, onboard, setup, install atom, bootstrap, add atom to this repo.'
---

# /atom:init

Recommend and perform approved Go repository setup, or confirm an existing matching
setup without changes. An existing `go.mod` is not required to enter this skill.

## When to use

- Adding Atom to a repository for the first time
- Confirming that an already onboarded repository needs no changes
- Diagnosing missing or corrupt onboarding without silently repairing it
- Verifying the toolchain before starting a pipeline

## Step 1 — Inspect and establish requested prerequisites

Resolve Go's availability before invoking it. If missing, explain the prerequisite
and ask the developer to supply it; do not install Go or substitute extra checks
for the onboarding baseline.

Follow [repository-setup.md](../atom/references/repository-setup.md) first.
Confirm Go intent, inspect the target, resolve the real module identity and
establish whether Atom onboarding is requested. For module/scaffold-only setup
without onboarding, skip Atom bootstrap and continue to step 2; working Atom
commands are not a prerequisite for Go-only setup.

When onboarding is requested, check the **active session's** client identity against
the supported minimum in
[bootstrap.md](../atom/references/bootstrap.md), not the version of another
executable. If it is unknown, conflicting or unsupported, ask one focused
clarification or switch/update question and wait; do not update automatically.

Follow [bootstrap.md](../atom/references/bootstrap.md). It establishes working forms
for both `atom` and `atom-write-artifact` without replacing an installed package.
Read it **before executing discovery commands**. Reuse forms already verified for
this session/environment; otherwise check availability before help or module calls.
Missing tools are a setup decision: explain what is absent and ask before any
installation. Healthy tools outside PATH are reused, not reinstalled. A found but
broken/partial/unsafe installation is preserved and reported, not silently repaired.

Verify working forms for both roles through their permitted supported `--help`
interfaces before the final setup proposal or any module/scaffold writes.
If either role is unavailable, stop without setup changes and propose the missing
prerequisite separately. Installation needs explicit consent; after any approved
installation, verify both roles before proposing setup.

Group compatible read-only prerequisite checks into as few terminal invocations
as safely possible, while following bootstrap's order and stop conditions. If a
group cannot preserve a check's result or required decision, run it separately.

Keep actual command statuses and relevant diagnostics; never truncate help/writer
output with `head` or hide a failure behind a successful wrapper. A writer refusal
or nonzero result stops the workflow, even if the wrapper reports zero. Do not probe
an invalid writer target, continue with another write or bypass it with an editor.
Bootstrap approval does not approve later init or module-local artifact writes.

On Windows, keep working module forms when entry points are hidden; do not ask about
changing PATH during normal init. If the developer requests PATH setup, bootstrap
provides the one-time `setup-path` opt-in. After successful setup, use its printed
absolute executable commands in this session. Do not re-probe command names or ask
again to locate the same executables.

Do not locate or read Atom's Python source while onboarding another repository.
Use the command forms established by bootstrap from the target module directory;
use `--help` when an option is unclear, not the implementation in an external
checkout or installed package.

Existing `.atom/` files do not require an implementation audit. Read the named local
files in steps 4 and 5 when onboarding is approved and report any discrepancy.
If `atom init` refuses because
existing setup is conflicting, incomplete, or corrupt, preserve it and report the
named problem; do not add `--force`
without the developer's explicit approval to discard that state.

## Step 2 — Recommend setup and obtain approval

Recommend only necessary files/commands, checks and generated build outputs.
When onboarding is requested, include its effects and baseline checks using the
command forms established in step 1. Wait for explicit approval before setup changes.

If `go.mod` is missing, create the approved module and optional minimal scaffolding
through the shared reference's sequence before any approved onboarding. Do not
invent a module path or use `atom init --module` as a module-creation shortcut.
Declined setup leaves the target unchanged. Existing modules and matching Atom
state are reused.

## Step 3 — Run deterministic onboarding

If onboarding was not included in the approved setup, skip steps 3 through 5 and report
the agreed Go-only result in step 6. Do not run Atom commands or require onboarding
files to complete that setup.

For approved onboarding with a newly created
minimal module, retain the child-only local/offline settings from the shared setup
reference; do not change user defaults. Stop on a setup command failure and report
partial changes instead of proceeding or silently repairing them.

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

For a new module, "untouched" means the approved module/source scaffold before
Atom writes its own files, not the original empty directory. `go build` may create
an executable; disclose this in the setup recommendation.

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
Module-only targets may fail vet/test because they contain no packages. Report
module/Atom setup separately from application readiness; do not add unapproved
source merely to get a green baseline.

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

Only perform this step for approved Atom onboarding.

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

Only perform this step for approved Atom onboarding.

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

- Without onboarding: the agreed module/scaffold result and only the checks actually
  run; Atom onboarding was not run and no new Atom baseline or bundle was verified
- For approved first initialization: the baseline result, including every failed
  gate, and what was created
- For an approved matching repeat: setup was already valid, nothing changed, and
  no baseline was refreshed
- With onboarding: the two established command forms, once, for reuse in later beats
- With onboarding: the recommended model setup — see
  [model-guidance.md](../atom/references/model-guidance.md)
- For setup-only requests: stop after the result. CLI suggestions do not authorize
  a POC, feature work, review or publication.
- For an explicitly requested full feature: recommend the next evidence step under
  the shared POC discipline and stop at its approval gate. For an explicitly requested
  resume, use `/atom-status` if the position is unclear.

Use the appropriate skill available in the active client. If a documented alias is
unknown or rejected, disclose that rather than guessing another alias or reinstalling
the plugin. Naming the intended skill in ordinary language does not prove a slash
alias works; invoke that skill, not a silently substituted beat.

---

## Done when

- [ ] Go intent and target confirmed; module reused or created only after approval
- [ ] Proposed files, commands, checks and generated outputs explicitly approved
- [ ] If onboarding requested: both command roles verified before final proposal or setup writes
- [ ] Without onboarding: Atom bootstrap, execution and onboarding-only file checks skipped
- [ ] With onboarding: `atom init` completed, including a valid read-only repeat
- [ ] Approved first init: no-race baseline captured before any Atom file was written
- [ ] Approved first init: `.atom/`, `specs/`, `poc/` created; `.gitignore` updated
- [ ] Approved first init: config commands match the commands exercised by the baseline
- [ ] Approved repeat: valid matching setup confirmed without changes or a new baseline
- [ ] With onboarding: local Atom bundle present under `.atom/atom/`
- [ ] With onboarding: repository agent instructions reference the local bundle
- [ ] Developer briefed on actual setup/checks and, with onboarding, model guidance

## Next

Setup-only: complete, no automatic next command. Full-feature/resume requests:
recommend the appropriate next evidence step without treating setup as gate approval.
