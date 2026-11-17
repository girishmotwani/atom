---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-16"
status: "accepted-with-limits-documentation-spec-authorized"
verdict: "Inconclusive for independent recipe navigation; technical result Confirmed"
---

# Standalone Quickstart Replay Report

## Question And Verdict

From the approved [standalone brief](standalone-quickstart-brief.md):

> Can the developer install the public Atom plugin and tooling into fresh isolated
> locations on Ubuntu WSL, then use one standalone POC to obtain the exact expense
> totals and visible input failures, without project onboarding, phase registration,
> a design/TDD cycle, or unprovided coaching?

**Technical result: Confirmed for the supplied cases.** A fresh public Atom install
and one standalone Go POC reached exact category totals and both required visible
failures, without root/project initialization, phases or a production lifecycle.
This is the concrete evidence-backed Go result sought by Phase 09.

**Full recipe-only navigation verdict: Inconclusive.** During the attempt the
developer pasted the generated gates into the setup session. This assistant
reviewed artifacts, advised how to answer, and supplied continuation wording after
the brief gate. Those interventions repeated the intended scope, but are still
outside-session assistance. We cannot establish that the frozen recipe alone
was sufficient, or that assistance was necessary. Do not call this independent
newcomer usability, and do not call the technical result a failure.

## Observed Setup And Session

The [preparation report](standalone-quickstart-preparation.md) records the approved
fresh Python venv, public marketplace/plugin and workspace on existing Ubuntu WSL.
Source: `5bb33cbe2c835382b5ccda840c5268321b24ac0b`; atom-cli 0.1.0; plugin 0.2.0;
all 658 plugin files matched the public Git tree before the run and remain unchanged.
The CLI cache is shared, as explicitly approved; neither base OS nor prerequisites
were newly provisioned. Setup was executed by the preparation agent, not a newcomer.

Frozen recipe SHA-256: `21f49124f665be3b065373f44c6d0638546c3b13507cda6643fe54d2b5a658c3`.
The exact [recipe](standalone-quickstart-recipe.md) and its private frozen copy match.

One isolated session event stream records Copilot CLI 1.0.107. Its initial automatic
model choice was claude-sonnet-5.5; managed settings selected gpt-6.1-sol at event
index 3, before the first assistant message at index 23. Recorded assistant messages
use gpt-6.1-sol. These startup metadata changes are not represented as a user model
switch or a fixed Auto-routing guarantee. Observed tools were apply_patch, ask_user,
bash, skill and view; no task/workflow agent launcher is in that tool-name set.
No new model task was launched by this audit.

The developer reported **4-5 active minutes**, excluding setup and human pauses.
This is an operator estimate, not a measured benchmark or time promise. They
reported **eight permission prompts**, answered yes with session-scoped reuse,
and clarified: **"Specific displayed commands/actions only"**. No all-tools,
unrestricted-path or persistent approval is reported. The POC brief/report
questions are not counted as tool-permission prompts.

The supplied transcript shows brief and report pauses. After being directed to
approve the report in the trial session and stop, the developer reported "done".
Record that as operator-reported completion/acceptance, not as a rewritten trial
artifact: the saved trial report and decisions still say report approval pending.
This audit deliberately does not alter that frozen workspace to reconcile status.

## Saved Execution Evidence

The audit read existing captures and exact fixture bytes; **no Go commands or model
sessions were rerun**. It checked the independent four-row fixture and the last-row
oops variant, the absent missing-file path, each Atom stage and all six direct cases.

Actual captured command: `atom poc run expense-summary --json --no-colour`.
Outer exit: 0; stderr: empty.
Its stdout, verbatim from the saved capture:

```json
{
  "schema_version": 1,
  "slug": "expense-summary",
  "kind": "command",
  "ran": true,
  "answered": true,
  "compiled": true,
  "verdict": "confirmed",
  "spike_exit_code": 0,
  "failed_stage": null,
  "stages": [
    {
      "stage": "vet",
      "exit_code": 0,
      "stdout": "",
      "stderr": "",
      "skipped": false,
      "timed_out": false
    },
    {
      "stage": "build",
      "exit_code": 0,
      "stdout": "",
      "stderr": "",
      "skipped": false,
      "timed_out": false
    },
    {
      "stage": "execute",
      "exit_code": 0,
      "stdout": "food 20.00\ntravel 3.75\n",
      "stderr": "",
      "skipped": false,
      "timed_out": false
    }
  ]
}
```

The runner's happy-path verdict alone is not the error-path evidence. Direct
captures below ran in the separate `poc/expense-summary` module. Streams are shown
as JSON strings generated directly from saved values; `""` denotes zero bytes.

| Command | Exit | stdout (JSON string) | stderr (JSON string) |
|---|---:|---|---|
| `gofmt -l main.go` | 0 | `""` | `""` |
| `go build -o expense-summary .` | 0 | `""` | `""` |
| `go run . expenses.csv` | 0 | `"food 20.00\ntravel 3.75\n"` | `""` |
| `go run . invalid.csv` | 1 | `""` | `"reading invalid.csv row 5: invalid amount \"oops\"\nexit status 1\n"` |
| `go run . missing.csv` | 1 | `""` | `"reading missing.csv: open missing.csv: no such file or directory\nexit status 1\n"` |
| `./expense-summary expenses.csv` | 0 | `"food 20.00\ntravel 3.75\n"` | `""` |
| `./expense-summary invalid.csv` | 1 | `""` | `"reading invalid.csv row 5: invalid amount \"oops\"\n"` |
| `./expense-summary missing.csv` | 1 | `""` | `"reading missing.csv: open missing.csv: no such file or directory\n"` |

The direct executable's negative exits are distinct from the Go wrapper exits.
No success totals appear on either failure. The invalid final row follows three
valid expense rows, so partial totals could not pass unnoticed.

## Post-Run Boundaries And Persistence

The saved audit verifies all 658 plugin paths/hashes with no additions, removals or
changes. Checked existing CLI, shell profile, default Copilot configuration/settings
and existing Atom venv fingerprints match their before-state. This is a bounded
fingerprint check, not a whole-host audit or proof about unrelated concurrent work.

Workspace root contains only poc and specs: no root go.mod or .atom project state.
The separate POC source/module, two fixtures, rerun README, brief/report/findings/
decisions and raw captures persist. The disposable executable was removed after
capture. The audit retains SHA-256 hashes of all 11 workspace files under the
private trial evidence directory.

Private evidence: the trial root is $HOME/atom-phase09-standalone-20261116;
evidence/replay-audit.json records validation and hashes, and workspace/poc/
expense-summary contains atom-evidence.json and direct-evidence.json. Keep raw
recordings/session events private; this report publishes only relevant outputs
and content-free model/lifecycle metadata. The trial is retained for inspection,
not silently promoted into production source.

## Limits And Proposed Next Step

No newcomer, clean-OS, all-platform, exhaustive numeric-format/overflow, production
readiness, race/coverage or maximum-time claim follows. The root baseline's missing
go.mod exit 2 was recorded honestly and not repaired; it is not the POC's Go gate.
The public install excludes the local unpublished discovery helper and does not
accept or publish that separate implementation.

Recommend accepting the bounded technical evidence and recording the independent-
navigation limitation. Next, draft a **small documentation-only quickstart spec**
using the verified installation/POC behavior and explicit brief-approval,
continue-execution and report-stop instructions observed here. Preserve the final
documentation approval gate. Do not use the incomplete usability isolation as
evidence for a final self-service usability or Phase 09 completion claim.

This proposes bounded reuse of verified technical evidence plus factual
documentation review, not another helper experiment, a new runtime entry point,
production Go implementation, publication or a new replay. The developer must
approve that evidence choice and next scope; no spec has been drafted in this turn.

## Evidence Gate Accepted: 2026-11-16

Developer selected exactly: "Accept evidence and limits; draft the short quickstart spec".
Accept the verified installation/Go results, operator timing/permission observations
and explicitly limited independent-navigation verdict. Authorize a small
quickstart documentation spec using that bounded evidence and explicit gate
navigation, not a usability confirmation, new experiment, runtime implementation,
publication or Phase 09 completion. Preserve the spec's own approval gate before
documentation implementation. No spec is drafted in this evidence-gate turn.
