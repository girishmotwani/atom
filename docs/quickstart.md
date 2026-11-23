# Try Atom: build a Go expense summary

Ask Atom to write and run a small Go program that totals expenses by category.
You'll try one proof of concept (POC): a throwaway program to test an idea, not a
production application. You don't need to onboard a repository or start a project.

## Before you start

Use **Ubuntu/Linux Bash**, including Ubuntu on WSL, with Git, Go, Python with
`venv`, and an authenticated GitHub Copilot CLI already available. For prerequisites
and other platforms, see [Getting started](../README.md#getting-started).

## 1. Install Atom and open Copilot

The block below installs the Atom command tools and plugin in a separate
`~/atom-quickstart` directory, then opens Copilot in an empty workspace.
Choose an unused directory; setup will not overwrite an existing one.
Paste the whole block, including the parentheses, to keep your shell settings
unchanged when it finishes.

```bash
(
  set -e
  trial="$HOME/atom-quickstart"
  for destination in "$trial" "$trial/workspace" "$trial/profile" "$trial/tmp" "$trial/venv"; do
    if [ -e "$destination" ] || [ -L "$destination" ]; then
      printf 'Destination already exists; stop: %s\n' "$destination" >&2
      exit 1
    fi
  done
  if ! copilot_bin="$(type -P copilot)"; then
    printf 'Copilot executable not found on PATH; stop.\n' >&2
    exit 1
  fi
  if ! copilot_bin="$(readlink -f "$copilot_bin")" || ! test -x "$copilot_bin"; then
    printf 'Cannot resolve an executable Copilot; stop.\n' >&2
    exit 1
  fi
  "$copilot_bin" --no-auto-update --version
  go version
  python3 --version
  git --version
  umask 077
  mkdir "$trial"
  mkdir "$trial/workspace" "$trial/profile" "$trial/tmp"
  export TMPDIR="$trial/tmp"
  python3 -m venv "$trial/venv"
  "$trial/venv/bin/python" -m pip install --no-cache-dir "git+https://github.com/girishmotwani/atom.git@5bb33cbe2c835382b5ccda840c5268321b24ac0b#subdirectory=tools"
  export PATH="$trial/venv/bin:$PATH"
  export COPILOT_HOME="$trial/profile"
  export COPILOT_AUTO_UPDATE=false
  cd "$trial/workspace"
  "$copilot_bin" --no-auto-update plugin marketplace add girishmotwani/atom
  "$copilot_bin" --no-auto-update plugin install atom@atom
  atom --help
  atom-write-artifact --help
  "$copilot_bin" --no-auto-update
)
```

Both Atom help commands must succeed. If setup fails or asks for unexpected
permissions, stop and resolve the displayed error rather than retrying with sudo
or changing your existing tools.

## 2. Ask for the POC

Send this request in the Copilot session:

```text
/atom:poc Create a standalone, disposable Go POC that reads this UTF-8 expense
CSV and prints totals by category. Prepare a brief and wait for my approval
before coding.

category,amount
food,12.50
travel,5.00
food,7.50
travel,-1.25

Expected totals: food 20.00 and travel 3.75, including the negative refund.
Also test the final amount replaced with oops, and a missing file. Each must
fail with a visible error, a nonzero process exit, and no success totals.
Capture stdout, stderr and exits, including atom poc run vet/build/run evidence
and direct executable checks.

Keep the POC under poc/expense-summary and its brief, report, findings and
decisions under specs/expense-summary. Use the existing tools. No project
onboarding, full pipeline, extra agents, installations, reviews, commits or
publication. After execution, stop for my approval of the report.
```

Atom may ask a clarifying question before preparing the brief. You don't need
`/atom:init` or a root Go module for this example.

## 3. Approve the brief and continue

Read `specs/expense-summary/poc-brief.md`. Check that it includes the CSV, expected
totals and both failure cases above. Request corrections if needed. If it matches,
explicitly approve the brief before execution. If execution starts after approval,
let it proceed; you don't need to send another message.

Only if the brief is already approved, execution has not started, and Copilot has
stopped awaiting your next instruction, send this once in the same session. Do not
send it while Copilot is thinking or running tools, or while a permission question,
writer refusal, error or scope-change request remains unresolved:

```text
Proceed with specs/expense-summary/poc-brief.md as approved. Scaffold, write and execute the disposable POC, capture all required evidence, and write the report. Stop at the report approval gate.
```

Approve only tool commands and paths you understand, including the full displayed
`atom poc new expense-summary` and `atom poc run expense-summary` commands.
Allow `atom-write-artifact` only for the intended artifact paths, not broad access.
You don't need blanket or persistent permissions. Tool prompts are separate from
approving the brief or report.

When Atom stops, read `specs/expense-summary/poc-report.md`. Accept or reject it
explicitly, then end the task; accepting a POC does not start the full pipeline.

## 4. Check the result

The report should show successful vet/build/run checks and this output with
exit 0 and no stderr:

```text
food 20.00
travel 3.75
```

Inspect the generated source and fixtures in
`~/atom-quickstart/workspace/poc/expense-summary`. To try the command yourself,
exit Copilot, open that directory in your terminal, and run these commands
individually. After each, run `printf 'exit=%s\n' "$?"` to check its exit status:

```bash
go build -o expense-summary .
./expense-summary expenses.csv
./expense-summary invalid.csv
./expense-summary missing.csv
```

The valid CSV should print the totals above. The last two commands should
**exit 1 without printing totals**. Expect errors like:

```text
reading invalid.csv row 5: invalid amount "oops"
reading missing.csv: open missing.csv: no such file or directory
```

Error wording can vary, but incorrect totals or missing failure evidence mean the
POC is not complete. Your files remain available after you close the terminal.

For a larger project, see the [full workflow](workflow.md).
[Validation notes and limitations](../specs/atom-v1-improvements/phase-09-onboarding-example/uninterrupted-quickstart-report.md)
are kept separately from this walkthrough.
