---
project: "atom-cli"
phase: "phase-05-ship"
date: "2026-09-18"
status: "ran"
brief: "poc-brief.md"
spike: "../../../poc/gh-ship/spike.py"
raw: "../../../poc/gh-ship/results.json"
---

# POC Report - Phase 5: `atom ship`

The phase plan rated Phase 5 "low risk - shelling out to `git` and `gh`" and marked
its POC justifiably skippable, then challenged its own note. The challenge was right.

**Four of six predictions were refuted.** "Justifiably skipped" would have been wrong
for the third phase running; the score on that phrase is now **0 for 3**.

## Results against the predictions

Predictions come from [`poc-brief.md`](poc-brief.md), written before the spike ran.

| # | Question | Predicted | Observed | Verdict |
|---|---|---|---|---|
| Q1 | PR already exists | Non-zero, names the existing PR | Exit 1, stderr gives the existing PR's URL | **Confirmed** |
| Q2a | OS argv wall for `gh` | ~8 KB, then ~30 KB, as Phase 4 measured | 32,086 bytes fine; **64,086 refused** with `WinError 206` | **Refuted** |
| Q2b | GitHub body cap | 65,536 characters, rejected above | **71,228 characters stored intact**; no cap reached | **Refuted** |
| Q3 | Unauthenticated | Clear actionable message, non-zero | Exit 1, `HTTP 401` plus `Try authenticating with: gh auth login -h github.com` | **Confirmed** |
| Q4 | Hangs with no TTY? | No idea | **Does not hang.** Fails in ~1.4 s: `aborted: you must first push the current branch to a remote, or use the --head flag` | **Answered** |
| Q5 | `gh` pushes by itself | Yes, it pushes | **It refuses to push.** Remote branch absent before and after | **Refuted** |

## The two results that had to be re-measured

Two answers arrived in the shape this project keeps getting caught by, and neither
was written down until it had been checked. [`probe_followups.py`](../../../poc/gh-ship/probe_followups.py)
exists because of them.

### An exit code of 0 is not evidence the data arrived

`gh pr edit --body-file` exited 0 for a 70,000-character body, above the cap that was
predicted. Exit 0 means `gh` was satisfied, not that GitHub stored anything -
precisely the distinction that makes `gofmt -l` exit 0 while reporting failures.

Reading the body back gave **71,228 characters**: nothing was truncated, and the
documented 65,536 limit was not enforced on this path. The prediction was wrong in
the interesting direction.

It also produced a finding nobody was looking for. The body *written* was 70,000
characters and the body *stored* was 71,228 - **1,228 more than were sent**. The
difference is exactly the number of lines: Python's text-mode write translated every
`\n` to `\r\n`, so the file on disk was larger than the string that produced it.
On Windows a body's character count and its byte count are different numbers, and any
size accounting that confuses them will be wrong by about 2%.

### One observation cannot tell a behaviour from a blip

The first `gh pr create` with *inherited* stdin took **44.4 seconds** and died with a
TCP write error, where the same call with empty stdin failed cleanly in 8.1. That is
the signature of the stall that cost Phase 4 a debugging session, and it was tempting
to record it as a second sighting.

Repeating the call three times gave **1.50 s, 1.48 s and 1.35 s**, every one exiting 1
with the same clean message. The 44 seconds was a network fault, not a stdin stall.

> **The finding here is about method, not about `gh`.** A single measurement that
> matches a hypothesis is the easiest thing in the world to believe. This project has
> already recorded one instance of fabricating evidence (finding 8 in Phase 3); this
> is the same failure caught one step earlier, by repetition rather than by
> conscience.

## What the argv wall actually is

Phase 4 measured the Copilot CLI failing at roughly 8 KB and again at 30 KB. `gh`
sailed through 32,086 bytes and failed only at 64,086. Same operating system, same
week, different walls - so one of the two measurements had to be explained rather
than averaged.

The explanation is what each tool *is*:

| Tool | Kind | Launch path | Observed limit | Matches |
|---|---|---|---|---|
| `copilot` | npm `.cmd` shim | Through `cmd.exe` | ~8 KB, then ~30 KB | `cmd.exe`'s 8,191-character command line |
| `gh` | native `.exe` | Direct `CreateProcess` | between 32 KB and 64 KB | `CreateProcess`'s 32,767-character `lpCommandLine` |

**The limit is a property of the launcher, not of Windows.** That is a far more
useful rule than any measured byte count, and it retroactively explains Phase 4's
numbers instead of leaving them as folklore about one machine.

The two failures also differ in a way that matters more than the threshold. Phase 4's
over-long argv arrived as a *completed process with a non-zero exit* - indistinguishable
from the model rejecting the input. `gh`'s arrives as an **`OSError` before the process
starts** (`WinError 206: The filename or extension is too long`), which is
unambiguous. The dangerous case is the shim, not the executable.

## Binding consequences

These constrain the Phase 5 design. Each one traces to an observation above.

| # | Consequence | Because |
|---|---|---|
| C10 | The PR body travels by `--body-file`, never `--body`. | Q2a: a body assembled from artifacts will exceed 32 KB, and Phase 3's artifacts alone exceed 35 KB. |
| C11 | Body files are written with explicit `newline="\n"`, and any size reported to the developer is the character count, not the file size. | The 1,228-character inflation above. |
| C12 | `atom ship` checks for an existing PR before creating one, and treats the duplicate error as a fallback rather than the primary signal. | Q1 works, but depending on stderr text to detect the normal re-run case makes the tool hostage to `gh`'s wording. |
| C13 | `atom ship` never relies on `gh` to push. It requires an upstream, or refuses with an instruction. | Q5: `gh` refuses to push, so the plan's "never pushes without an explicit instruction" criterion is enforceable rather than aspirational. |
| C14 | `gh`'s own error text is passed through, not paraphrased. | Q3 and Q4 both produce messages better than anything this tool would invent: they name the exact next command. |
| C15 | `gh` is located and verified before any work begins, and its absence is reported as a precondition rather than a failure partway through. | The only `gh` on this machine is the Copilot app's bundled copy; a developer without that app has none. |
| C16 | Empty stdin is still passed to every `gh` call. | **Not justified by evidence of a hang - Q4 refuted that.** Justified as defence in depth: it costs nothing and the runner already does it. Recorded honestly so a later reader does not cite Q4 as support. |

## Debt

| # | Item | Why it is being left |
|---|---|---|
| D13 | The real GitHub body cap is unmeasured above 71,228 characters. | The documented 65,536 was not enforced; finding the true ceiling would need a bisection nobody currently needs. C10 and C11 hold regardless. |
| D14 | `gh pr create --head` is untested. | Q4's error offers it as an alternative to pushing. If it can create a PR without a local upstream, C13 may be stricter than necessary. |
| D15 | Argv limits on Linux and macOS are unmeasured. | Same platform gap as Phase 4's D10. The launcher rule above predicts they will differ, which is a prediction and not a measurement. |
| D16 | Closed PR #1 remains in the repository permanently. | Agreed with the developer in advance. It is evidence, not litter. |

## Method notes

- Every git operation ran in a **throwaway worktree** beside the repository, so no
  failure could dirty the developer's checkout. Cleanup ran from a `finally` block and
  is confirmed: `git worktree list` shows only `main`, and the remote branch is gone.
- Read-only questions (Q3, Q2a) ran **before** the invasive ones, so a failure in PR
  creation could not cost the cheap answers.
- Raw output is preserved in [`results.json`](../../../poc/gh-ship/results.json) and
  [`followups.json`](../../../poc/gh-ship/followups.json) rather than summarised only
  here, on the Phase 4 precedent that saved spike responses become a free regression
  corpus.
