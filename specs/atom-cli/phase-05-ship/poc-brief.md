---
project: "atom-cli"
phase: "phase-05-ship"
date: "2026-09-18"
status: "predictions recorded before the spike ran"
---

# POC Brief - Phase 5: `atom ship`

The phase plan marks Phase 5's POC "justifiably skipped - no technical
uncertainty", then challenges its own note. That phrase has been used twice in
this project and been wrong both times: it hid the largest finding in Phase 2
and two findings in Phase 3. **The score on "justifiably skipped" is 0 for 2.**
This brief exists because the entry gets no benefit of the doubt.

## Why this brief is written before the spike

A prediction recorded after the fact is not a prediction. The value of the
exercise is that the run can *disagree* with what is written here - so it is
written here first, with confidence stated honestly, including where the honest
answer is "no idea".

## Environment as found

| Fact | Value | Why it matters |
|---|---|---|
| `gh` version | 2.96.0 | Third-party tool whose exit codes nobody in this project has measured. |
| `gh` location | `AppData\Local\copilot-desktop-gh-2.96.0\gh.exe` | It is the Copilot app's **bundled** copy, not a standalone install. A developer without that app may have no `gh` on PATH at all. |
| Auth mechanism | `GH_TOKEN` environment variable | Not a `gh auth login` keyring entry. Auth can therefore vanish with an environment change rather than a logout. |
| Token scopes | `gist, project, read:org, repo, user, workflow` | Sufficient to open PRs. |
| Target repo | the project's own repository, base `main` | The spike opens throwaway PRs here and cleans them up. |

## Questions and predictions

| # | Question | Prediction | Confidence |
|---|---|---|---|
| Q1 | What does `gh pr create` do when a PR **already exists** for the branch? | Non-zero exit with a message naming the existing PR. | Medium |
| Q2a | How large an argument can `gh` be given before the **OS** refuses? | It hits the same Windows argv wall Phase 4 measured: roughly 8 KB produces "the syntax of the command is incorrect" and roughly 30 KB "the command line is too long". | High |
| Q2b | How large a body will **GitHub** accept via `--body-file`? | `--body-file` sidesteps argv entirely; GitHub then caps the body at 65,536 characters and rejects anything larger. | Medium |
| Q3 | What does `gh` do when **not authenticated**? | A clear, actionable message and a non-zero exit. | High |
| Q4 | Does `gh pr create` **hang** with no TTY and no upstream branch? | **No idea.** It either prompts and hangs forever, or detects the absence of a terminal and fails fast. | **None** |
| Q5 | Does `gh pr create` **push the branch by itself**? | Yes - it pushes when there is no upstream. | Medium-high |

## Why Q4 and Q5 carry the weight

**Q4 repeats a failure shape this project has already been bitten by.** Phase 4's
probe printed a correct answer and then timed out at 60 seconds, because the
child process inherited stdin and a non-TTY pipe never reached EOF. `gh` is a
famously interactive tool. If it behaves the same way, `atom ship` hangs in CI -
the one environment it exists to serve. The spike therefore runs the same call
twice, once with stdin inherited and once with empty stdin, because that
difference is what made Phase 4's bug invisible until it was looked for.

**Q5 would put the tool in conflict with its own acceptance criterion.** The
phase plan says `atom ship` "never pushes without an explicit instruction". If
`gh pr create` pushes as a side effect, that criterion is violated by the tool
being wrapped, and the design has to intercept the behaviour rather than
delegate to it. That is a design input, not an implementation detail.

**Q2 stopped being a curiosity when Phase 4 finished.** The premise of this
phase is assembling a PR body out of artifacts, and Phase 3's artifacts alone
exceed 35 KB. Two independent limits are stacked here - the operating system's
and GitHub's - and they fail differently. Phase 4 established that an
over-long argv arrives as a completed process with a non-zero exit and a
message about syntax, which is indistinguishable from the tool rejecting the
input on its merits. That is exactly the kind of lie this project has now
caught eight times.

## Decision rule - fixed before the data arrives

Recorded in advance so the numbers choose the design rather than the reverse.

| Outcome | Consequence for the design |
|---|---|
| Q4 hangs with inherited stdin | Every `gh` call in `atom ship` passes empty stdin, pinned by a test, as the runner already does for Phase 4. |
| Q4 hangs even with empty stdin | `gh pr create` cannot be called on an unpushed branch at all; `atom ship` must ensure the upstream exists first, or refuse. |
| Q5 pushes | `atom ship` never calls `gh pr create` on a branch without an upstream. Pushing becomes an explicit, separately authorised step. |
| Q2b caps the body | The body is assembled to fit, and what gets dropped is decided deliberately and stated in the body itself - never silently truncated. |
| Q1 exits zero on a duplicate | Re-running `atom ship` cannot be detected by exit code; the tool must query for an existing PR before creating one. |

## Cleanup contract

The spike works in a **git worktree**, never the main checkout, so a failure
cannot leave the developer's tree dirty or on the wrong branch. It closes every
PR it opens and deletes both the remote and local branch. Closed PRs remain
visible in the repository's history; that was agreed with the developer in
advance rather than discovered afterwards.
