# POC Report: Existing-repository onboarding UX

## Question

> After you have fixed this, can you spike onboarding to an existing repo and running the atom init command. Verify that the onboarding is complete and also the user is not asked for approval to write to atom's state files.

## Verdict

**Confirmed after repair.** A real Copilot CLI session onboarded a committed existing Go repository completely. The user typed `/atom:init` once and selected **Yes** on three shell-command approvals. There were no denials, no extra workflow typing, and no approval prompt for an individual Atom state-file write.

## Run context

- Date: 2026-10-07
- Copilot CLI: 1.0.93-4
- Mode: Interactive, Manual Approval, screen-reader output captured through a Windows pseudo-terminal
- Plugin: current workspace loaded with `--plugin-dir`
- Atom CLI: editable package from `tools/`, invoked through `python -m atom.cli` because console scripts were not on PATH
- Fixture: existing Git repository with a committed `go.mod`, Go source, and Go test

## Interaction evidence

```text
USER INPUT 1: typed `/atom:init` and pressed Enter (initial prompt).

APPROVAL 1: pressed Enter to select `1. Yes`.
VISIBLE PROMPT:
Check Atom command entry points
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ $atom = Get-Command atom -ErrorAction SilentlyContinue; $writer = Get-Command atom-write-artifact -ErrorAction SilentlyContinue; if ($atom) { & atom --help } else     │
│ { Write-Output 'ATOM_NOT_FOUND' }; if ($writer) { & atom-write-artifact --help } else { Write-Output 'WRITER_NOT_FOUND' }                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Do you want to run this command?

Current selection: 1. Yes
  2. No, and tell Copilot what to do differently (Esc to stop)

↑/↓ to navigate · enter to select · esc to cancel

APPROVAL 2: pressed Enter to select `1. Yes`.
VISIBLE PROMPT:
Check Atom Python module entry points
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ $python = Get-Command python -ErrorAction SilentlyContinue; if (-not $python) { Write-Output 'PYTHON_NOT_FOUND'; exit 0 }; & python -m atom.cli --help; Write-Output   │
│ "ATOM_MODULE_EXIT=$LASTEXITCODE"; & python -m atom.artifact_cli --help; Write-Output "WRITER_MODULE_EXIT=$LASTEXITCODE"                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Do you want to run this command?

Current selection: 1. Yes
  2. No, and tell Copilot what to do differently (Esc to stop)

↑/↓ to navigate · enter to select · esc to cancel

APPROVAL 3: pressed Enter to select `1. Yes`.
VISIBLE PROMPT:
& python -m atom.cli init

Run deterministic Atom onboarding
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ & python -m atom.cli init                                                                                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Do you want to run this command?

Current selection: 1. Yes
  2. No, and tell Copilot what to do differently (Esc to stop)

↑/↓ to navigate · enter to select · esc to cancel

EXPERIMENT CLEANUP: typed `/exit` after Copilot completed its onboarding response; not part of onboarding workflow.
```

The full terminal stream is preserved in [transcript.txt](transcript.txt). The compact ledger is preserved separately in [interactions.md](interactions.md).

## Independent repository verification

```text
COMMAND: python -m atom.cli status
Project: C:\Users\gimotwan\work\atom\.temp\onboarding-ux-fixture
Module:  example.com/existing
Phase:   none (no phase directories found)
Last:    initialised at 2026-10-07T22:23:15+00:00
No problems found.
--- CONFIG ---
{
  "build_command": "go build ./...",
  "module_path": "example.com/existing",
  "test_command": "go test ./..."
}
--- BASELINE SUMMARY ---
passed=True exit_code=0 gates=build:passed,vet:passed,fmt:passed,test:passed,race:skipped
--- REQUIRED PATHS ---
.atom\state.json=True
.atom\baseline.json=True
.atom\atom\AGENTS.md=True
.atom\atom\manifest.json=True
.github\copilot-instructions.md=True
specs=True
poc=True
--- IGNORE CHECK ---
.atom/baseline.json
.atom/events.jsonl
.atom/events.lock
ignored_exit=0
shared_exit=1
--- EXTERNAL REFERENCES ---
none
```

## What changed during the spike

The first real run refuted the pre-repair onboarding contract: `atom init` did not create `baseline.json`, `specs/`, or `poc/`, and the skill attempted repeated shell verification. The repair moved the baseline and complete scaffold into `atom init`, then constrained successful post-init verification to named file reads. The final run needed three approvals instead of nine.

## Explicit approval/typing result

- **Typed:** `/atom:init` once.
- **Approved:** three shell commands by pressing Enter on `1. Yes`.
- **Denied:** nothing.
- **Typed after the initial command:** nothing during onboarding.
- **State-file prompts:** none. The state files were written inside the approved `atom init` command, so Copilot never presented a separate write approval for them.
- **Experiment-only cleanup:** `/exit` after the completed response; excluded from workflow counts.

## Explicitly not covered

- Copilot CLI versions other than 1.0.93-4.
- POSIX terminals.
- A machine where the `atom` and `atom-write-artifact` entry points are already on PATH; that path should require fewer bootstrap steps.
- Permission behavior of later Atom beats when they first invoke `atom-write-artifact`.
- Choosing `No` on an approval prompt; the success workflow required no denial.
