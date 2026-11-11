---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-10"
status: "prepared-awaiting-start-approval"
---

# Prepared-Environment Expense CLI Rehearsal

This is one proposed additional experienced-user attempt, not a newcomer test or
final public quickstart. The original recipe and Inconclusive result stay intact.
No module, evidence directory or model session has been created for this attempt.
**Do not run the launch block until this recipe and its one-attempt budget are
explicitly approved.**

## Question From The Approved Brief

Can the developer complete one bounded Ubuntu WSL rehearsal from a fresh example
module to a tested expense-summary CLI using only the frozen candidate quickstart,
the actual Atom prompts, and the artifacts presented at its gates, without opening
the full methodology or bypassing an applicable approval?

The [original brief](poc-brief.md) supplies the evidence method and CSV contract.
This amendment changes the prerequisite/source snapshot and uses new paths;
it does not reinterpret the failed first attempt as a success.

## Disclosed Prerequisites

Ubuntu WSL already has Go 1.22.2, Python 3.12.3, git 2.43.0 and the previously
verified race-build prerequisites. Pinned Copilot CLI 1.0.107 is at
$HOME/.local/atom-phase09-tools/bin/copilot. Do not use the older PATH launcher.

The installed Atom plugin is 0.2.0, with all 607 source files matching public
commit ec605a715f53db93abd54d6e88f887cf20525940. The existing atom-cli 0.1.0
package in $HOME/.local/share/atom-cli/venv records that same commit. Both
bootstrap copies match the accepted repair, and both command roles passed help
checks; see the accepted [delivery report](public-delivery-report.md).

These are **prepared working prerequisites**, not a cold-start PEP 668 test.
There is no authorized package/plugin/CLI update or system provisioning during
the attempt. The agent should reuse the existing command forms. No PATH/profile
edit is needed; the known Linux venv remains outside the new repository.
Existing module bundles have not been refreshed. The new module's init must
produce its own bundle normally; do not copy instructions or use init --force.

Model/authentication access remains unverified until your session starts.
Record the selected model and keep it unchanged during the attempt. Stop before
sending a task if startup requires login, unsafe broad approval/autopilot, a
model/configuration change or additional provisioning. Do not copy credentials.

## Launch Only After Approval

Open Ubuntu from a terminal:

```powershell
wsl.exe --distribution Ubuntu
```

Run the following inside Ubuntu, not PowerShell. Both destination names were
absent when prepared; recheck at launch. Any collision or command failure means
stop and retain partial state. Do not reuse, overwrite, remove or rename the old
attempt, its recording, or any of the bootstrap proof directories.

```text
cd "$HOME" &&
mkdir -m 700 atom-phase09-prepared-rehearsal &&
mkdir -m 700 atom-phase09-prepared-evidence &&
cd atom-phase09-prepared-rehearsal &&
git init --initial-branch=rehearsal/expense-summary-prepared &&
go mod init example.com/expense-summary &&
script --quiet --flush --return --command 'env PATH="$HOME/.local/atom-phase09-tools/bin:$PATH" "$HOME/.local/atom-phase09-tools/bin/copilot" --no-auto-update --log-dir "$HOME/atom-phase09-prepared-evidence/cli-logs"' "$HOME/atom-phase09-prepared-evidence/terminal.log"
```

This creates only a blank Go module and private recording destinations, not an
implementation or prewritten tests. The PATH selection is child-only and pins
Copilot; it does not add the Python venv or alter shell profiles. Keep raw logs
private and review/redact them before sharing. Terminal capture alone can omit
collapsed tool detail, so retain the CLI's local session history too.

## Start And Follow The Workflow

Start your manually observed **60-minute active-effort timer** before the first
request. Record setup time and pauses separately. One additional attempt and one
interactive session only; no automatic retry. This is not a fixed API-call or
monetary guarantee and is not an automatically enforced timer.

Enter:

```text
/atom:init
```

Approve only normal onboarding and guarded artifact writes for this new module.
Approvals from the Atom repository or old proof modules do not transfer. The
existing command executables are:

```text
$HOME/.local/share/atom-cli/venv/bin/atom
$HOME/.local/share/atom-cli/venv/bin/atom-write-artifact
```

The agent must retain its actual working forms and send complete UTF-8 artifact
content through the guarded writer. Stop rather than granting blanket access or
bypassing a refusal. Capture the untouched empty-module baseline honestly; no
packages or a failing baseline is not a green Go implementation.

Then enter:

```text
/atom:start Build a Go CLI that reads an expense CSV and prints totals by category.
```

When asked, provide:

```text
Read a UTF-8 CSV file named expenses.csv, with header category,amount.
Use one currency and exact two-decimal amounts, including negative refunds.
Print a total for each category.
An invalid amount or missing input file must fail visibly with a nonzero exit.
Use the existing Go/Python tools and prepared Atom commands; do not install or update tools.
Do not commit, push, start extra agents, run a model-review batch, or bypass any applicable approval gate.
```

Provide the synthetic fixture, not a working implementation or prewritten tests:

```csv
category,amount
food,12.50
travel,5.00
food,7.50
travel,-1.25
```

Independent expected totals: **food 20.00; travel 3.75**. Presentation and
implementation choices belong to the example's own gated spec.

Use this recipe and the actual prompts/presented artifacts, not the full
methodology or outside coaching. Ask for clarification inside the recorded
session. At every gate, decide explicitly; do not automatically approve. Observe
at least one actual pause before approval and record whether work waits.
A rehearsal approval does not approve the example's POC, spec or implementation
in advance. If you cannot continue within the permitted material, stop.

## Verify And Stop

At the example's approved implementation gate, ask for its recorded build/test
commands, **full atom check with race enabled through the working command form**,
and the actual execution:

```text
go run . expenses.csv
```

Check both expected totals. Replace one amount with oops for a negative check,
and also use a genuinely missing input file. Capture each real command, output
and immediate process exit; both errors must be visible and nonzero. No skipped
race gate or failing check counts as success. Do not add code to hide the initial
empty-module baseline.

Stop at that verified implementation gate, before multi-model review or shipping.
Also stop on the effort cap, missing access, changed recipe/source/model,
additional installation or model/agent spend, ambiguous permissions, a writer
refusal or an approval boundary you cannot resolve. Preserve the partial record;
do not repair the frozen recipe or start another attempt.

Record the chosen model, session ID, active elapsed time/pauses, actual approvals,
clarification requests and any outside help. Use /usage for reported usage, then
/exit print to leave with visible history printed. Preserve private terminal and
local session history; share only reviewed/redacted evidence.

Correct totals, negative checks, full Go gate and observed approvals without
outside methodology/coaching can confirm only this prepared experienced-user
workflow. Setup/access/capture failures, the cap or changed conditions are
Inconclusive; needing outside methodology/coaching or bypassing a gate can refute
the tested path. Neither outcome completes Phase 09 or proves newcomer usability,
cold-start installation, all-platform support, general model reliability or
release readiness. Present the result before the final Phase 09 design.
