---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-07"
status: "frozen-for-first-rehearsal"
---

# Expense CLI Rehearsal Recipe

This is your experienced-user rehearsal, not the final public quickstart.
Use this recipe and the artifacts Atom presents; do not open the full methodology
as a help manual. The agent still needs to read its own instructions.

## Prepared Environment

Ubuntu WSL: Go 1.22.2, Python 3.12.3, git 2.43.0; gcc and Python bootstrap
support are present. Copilot CLI **1.0.107** is installed in the approved user-owned
tools directory. Atom **0.2.0** is installed from public girishmotwani/atom.
All nine skills and three command files are present.

Use the pinned executable below, not the older copilot on your normal PATH.
No login or credential copying was performed. Model access is still unverified.
If startup requires login, shows broad auto-approval/autopilot, or cannot use an
available model, stop before sending a task; do not fix global settings or log in.

## Open The Recorded Session

Open a terminal and enter Ubuntu:

```powershell
wsl.exe --distribution Ubuntu
```

Run this next block **inside Ubuntu, not PowerShell**. If either directory already
exists, stop; do not reuse, overwrite or delete it. The chained commands stop at
the first error. The PATH addition applies only to the recorded child process;
it does not change your shell/profile and prevents helper calls using the old CLI.

```text
cd "$HOME" &&
mkdir -m 700 atom-phase09-rehearsal &&
mkdir -m 700 atom-phase09-evidence &&
cd atom-phase09-rehearsal &&
git init --initial-branch=rehearsal/expense-summary &&
go mod init example.com/expense-summary &&
script --quiet --flush --return --command 'env PATH="$HOME/.local/atom-phase09-tools/bin:$PATH" "$HOME/.local/atom-phase09-tools/bin/copilot" --no-auto-update --log-dir "$HOME/atom-phase09-evidence/cli-logs"' "$HOME/atom-phase09-evidence/terminal.log"
```

This creates only a blank Go module and private evidence directories, not a working
CLI. The recorder captures terminal output, not hidden password input. Keep raw
logs private; review/redact them before any publication. Do not share credentials.

## Start The Task

Start your **60-minute active-effort timer** before the first request. Record pauses
separately. One attempt and one interactive session only; no automatic retry.

Enter:

```text
/atom:init
```

Approve only this module's normal Atom bootstrap/onboarding operations when asked.
Do not authorize system-package installs or Go/Python upgrades. An empty-module
baseline may report no packages: capture the real result, do not call it green.

Then enter:

```text
/atom:start Build a Go CLI that reads an expense CSV and prints totals by category.
```

Provide this contract when asked:

```text
Read a UTF-8 CSV file named expenses.csv, with header category,amount.
Use one currency and exact two-decimal amounts, including negative refunds.
Print a total for each category.
An invalid amount or missing input file must fail visibly with a nonzero exit.
Use the existing Go/Python tools. Do not commit, push, start extra agents,
run a model-review batch, or bypass any applicable approval gate.
```

Provide this synthetic fixture:

```csv
category,amount
food,12.50
travel,5.00
food,7.50
travel,-1.25
```

Expected totals, checked independently: **food 20.00; travel 3.75**.
Do not supply a working implementation or prewritten tests.

## Follow The Prompts, Not A Guessed Pipeline

At every gate, read the named artifact and decide explicitly. A brief approval
allows only that experiment; a report approval allows the stated next beat;
a design approval allows only that implementation. Do not automatically answer yes.
Observe at least one actual pause before approval and record whether work waits.
Ask Atom to explain what is unclear using the permitted material.

If you need the full methodology, outside coaching, extra agents/model-review
spend, login/provisioning, or a changed recipe to continue, stop and preserve the
partial record. Do not quietly repair the frozen attempt.

## First Useful Result And Stop

After the example's own approved implementation, ask Atom to run its recorded
build/test commands, **full atom check with race enabled**, and:

```text
go run . expenses.csv
```

Verify both expected totals, an amount changed to oops, and a missing file.
Capture the actual commands, outputs and exits. Stop at the verified implementation
gate, before multi-model review or shipping; this is not a release-ready claim.

Record the selected model, session ID, actual approvals, clarification requests
and active elapsed time. Use /usage for reported usage, then /exit print to leave
the session with its visible history printed. Preserve the CLI's local session
history as well as the terminal log; a collapsed terminal view may omit tool details.

Do not start a second attempt. A completed rehearsal only covers you and this
environment; genuine newcomer usability, clean-machine setup, upgrade/uninstall
safety and general model reliability remain unproven.
