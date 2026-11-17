---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-16"
status: "approved-for-one-participant-launch"
---

# Standalone Expense POC: Frozen Replay Recipe

## Scope And Prepared Install

One experienced-user session on existing Ubuntu WSL, at most 30 active minutes,
ending at a disposable POC report. No project onboarding or production lifecycle.
Setup was executed by the preparation agent under the developer's explicit
installation approvals, not independently by a newcomer. No model session ran.
The existing CLI cache is shared, as explicitly approved; this is not a clean OS.

Fresh trial root: $HOME/atom-phase09-standalone-20261116. Its workspace is empty.
The public install was verified against commit:

```text
5bb33cbe2c835382b5ccda840c5268321b24ac0b
```

Pinned Copilot CLI 1.0.107; Go 1.22.2; Python 3.12.3; git 2.43.0;
atom-cli 0.1.0; Atom marketplace plugin 0.2.0. All 658 installed plugin files match
the selected public commit's Git blobs. Installed plugin inventory SHA-256:

```text
c0ecc02d306f0441859ac2ce0479abf9dbabd0d4e6c3b8f6b1a20dce215b4a79
```

The local unpublished discovery helper is absent. Plugin instructions and Python
commands are separate installations, both fresh and verified. Existing tool/profile
fingerprints are unchanged. See standalone-quickstart-preparation.md for evidence.
The active client's authentication and interactive /atom:poc alias remain untested;
a skill listing is not proof of either. Stop if login, a tool/client update,
unexpected permissions or an unknown command is required. Do not copy credentials,
guess another alias, update the plugin, broaden permissions or retry automatically.

## Setup Receipt: Already Executed, Do Not Repeat

The preparation created a private trial root and empty workspace/profile/evidence
locations, then ran these public installation commands with child-only isolation
settings. The variable trial below denotes the trial root:

```text
python3 -m venv "$trial/venv"
"$trial/venv/bin/python" -m pip install --no-cache-dir "git+https://github.com/girishmotwani/atom.git@5bb33cbe2c835382b5ccda840c5268321b24ac0b#subdirectory=tools"
"$HOME/.local/atom-phase09-tools/bin/copilot" --no-auto-update plugin marketplace add girishmotwani/atom
"$HOME/.local/atom-phase09-tools/bin/copilot" --no-auto-update plugin install atom@atom
```

The plugin commands used COPILOT_HOME=$trial/profile and
COPILOT_AUTO_UPDATE=false, and were run from the fresh workspace. Python temporary
files used $trial/tmp; no editable install or package cache was used. Full actual
argument arrays, outputs and exits are retained privately under $trial/evidence.
Do not confuse this receipt with a tested final end-user quickstart or repeat it
against the now-existing directories.

## Launch Once From An Ubuntu Terminal

Open Ubuntu from a separate terminal if needed:

```powershell
wsl.exe --distribution Ubuntu
```

Run the following inside Ubuntu, not PowerShell. A pre-existing recording or a
failed guard must stop the launch. The checksum command is silent on success.
The PATH/profile settings apply only to the recorder and its child session.
No global environment or shell profile is edited.

```text
trial="$HOME/atom-phase09-standalone-20261116"
if [ -e "$trial/evidence/terminal.log" ] || [ -L "$trial/evidence/terminal.log" ]; then
  echo "Recording already exists; stop."
elif [ -n "$(find "$trial/workspace" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  echo "Workspace is no longer empty; stop."
else
  cd "$trial/workspace" &&
  sha256sum --check --quiet "$trial/evidence/plugin.sha256" &&
  PATH="$trial/venv/bin:$PATH" COPILOT_HOME="$trial/profile" COPILOT_AUTO_UPDATE=false \
    script --quiet --flush --return \
      --command "\"$HOME/.local/atom-phase09-tools/bin/copilot\" --no-auto-update --log-dir \"$trial/evidence/cli-logs\"" \
      "$trial/evidence/terminal.log"
fi
```

Keep this terminal open and operate the session yourself. Record the displayed
client/model, prompts and responses; keep the default model, with no override.
Start the 30-active-minute timer before the first task; record human pauses
separately. If authentication is unavailable, stop without login or token copying.
A passed checksum before launch does not prove that the older client cannot update
plugins; verify the inventory again afterward and invalidate any changed snapshot.

## Send One Request

```text
/atom:poc I want one standalone disposable expense-summary Go POC, not a production feature or the full Atom pipeline. Prepare its brief and stop for my approval before coding. The question is: Can a Go command read the supplied expense CSV, print exact category totals including the negative refund, and reject invalid amounts and missing files with a nonzero exit and no success totals?

Read a UTF-8 CSV with header category,amount and these rows:
food,12.50
travel,5.00
food,7.50
travel,-1.25

Expected totals: food 20.00; travel 3.75. Replacing an amount with oops and using a missing file must each visibly fail with a nonzero Go process exit and no success totals. Capture exact stdout, stderr and exits, including atom poc run vet/build/run evidence and direct Go-command negative checks.

Keep this to one disposable POC under poc/expense-summary and its brief/report/findings/decisions. Use the existing Atom tools on PATH and existing Go/Python. Preserve the brief/report approval pauses. No init/start/build, phase registration, phase plan, design spec, TDD cycle, extra agents, tool installation, model review, commit, push or publication. Stop at the POC report gate.
```

If the installed skill needs discovery only to prepare the missing brief, follow
its named existing brief-preparation step, without unrelated project setup or
additional coaching. Do not invent a shortcut or force it past a required gate.
Read the actual brief before deciding whether to approve its bounded experiment.
Approval of this outer replay is not automatic approval of the generated brief.
Observe at least one actual pause before approval. A question that cannot be
resolved from this recipe or presented artifacts ends the frozen attempt.

The verified command forms available in this child session are atom and
atom-write-artifact through the prepended venv/bin PATH. No root go.mod, baseline,
.atom project state, implementation, tests or input fixtures were prewritten.
The skill should use its existing separate-module POC scaffold and runner.

## Stop And Return Evidence

Stop at the report gate, the 30-minute cap, any failure, unexpected setup/model
change, unsupported command or refusal. No retry or guide repair during the attempt.
Do not accept an unrelated full-pipeline escalation merely to reach the result.
After exiting the single session, run this in the same Ubuntu terminal:

```text
sha256sum --check --quiet "$HOME/atom-phase09-standalone-20261116/evidence/plugin.sha256"
printf 'plugin-check exit=%s\n' "$?"
```

Return the relevant redacted transcript excerpts: actual skill load/turns,
brief/report approval pauses, installed-client/model display, program totals,
invalid/missing-input commands and originating exits, elapsed active time and
permission prompts (including zero). Keep raw recordings and credentials private.
The preparation agent will also compare the full inventory for added/removed files
and check host fingerprints; checksum verification alone does not detect additions.

Correct outputs and actual approvals without pipeline escalation confirm this
specific experienced-user replay only. A workflow requiring outside coaching or
unrelated lifecycle steps refutes this frozen path. Setup/access/evidence failure,
time cap or changed conditions is Inconclusive. Stop for report review before a
final quickstart design or publication. No Go production-quality/race/coverage
claim follows from a successful throwaway POC.

## Launch Approval: 2026-11-16

Developer selected exactly: "Approve one session using the frozen recipe".
Authorize the single developer-operated default-model session with the 30-active-
minute cap and stated stop conditions. This does not preapprove the generated
brief, report, production implementation or publication. No model session is
launched by the preparation agent; the participant runs the launch block above.
