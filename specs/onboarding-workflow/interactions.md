# Onboarding interaction ledger

This is the complete user-interaction ledger for the successful run. The `/exit` entry is experiment cleanup after completion, not part of onboarding.

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

## Counts

| Interaction | Count |
|---|---:|
| Workflow text entries | 1 |
| Approval selections | 3 |
| Denial selections | 0 |
| State-file write approval prompts | 0 |
| Additional workflow typing | 0 |

All three approvals were shell-command approvals: entry-point discovery, Python module fallback discovery, and the single deterministic `atom init` invocation.
