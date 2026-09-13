---
name: atom-review
description: 'Multi-model review of a Go diff, merged into one deduplicated report with severities. Keywords: review, code review, multi-model review, review my changes, review the diff, critique.'
---

# atom-review

Reviews a diff with **two or more different models** and merges their findings into one
report.

## Why more than one model

A model reviewing its own output shares its own blind spots. It will not flag the
misunderstanding that produced the code, because it still holds that
misunderstanding.

> **The reviewing model must not be the model that wrote the code.**

This is the entire point of the skill. A single-model self-review is not a substitute,
and running one instead is the rationalization this skill exists to prevent.

## When to use

- After `atom-tdd` for a phase
- Before `atom-ship`
- Any time a diff is large enough that reading it once isn't enough

## Step 1 — Establish the diff

```bash
atom review --base main          # branch diff
atom review --staged             # staged changes
atom review --working            # working tree
```

Review the diff **with** the surrounding file, not the hunks alone. Context-free hunk
review produces confident nonsense about code that is already handled ten lines up.

## Step 2 — Run the models

```bash
atom review --base main --models <model-a>,<model-b>,<model-c>
```

Each model reviews each changed file independently, in parallel. They do not see each
other's findings — shared context would collapse them into agreement, which is exactly
the diversity you are paying for.

Models are resolved from `.atom/config.json`. Never hard-code a version; see
[model-guidance.md](../atom/references/model-guidance.md).

## Step 3 — What reviewers look for

In priority order:

| Priority | Category | Examples |
|---|---|---|
| 1 | **Correctness** | Logic errors, wrong boundaries, unhandled `nil`, ignored errors |
| 2 | **Concurrency** | Races, deadlocks, unowned goroutines, leaks, misuse of context |
| 3 | **Security** | Unvalidated input, injection, leaked secrets, unsafe defaults |
| 4 | **Contract drift** | Code disagrees with the approved design spec |
| 5 | **Test quality** | Tests that can't fail, missing error paths, weakened assertions |
| 6 | **Readability** | Violations of [go-style.md](../atom/references/go-style.md) |

Formatting is **not** reviewed. `gofmt` already settled it, and review attention spent
on whitespace is attention not spent on the race condition.

## Step 4 — Merge

Findings are deduplicated by file, line and substance, then merged into one report at
`specs/{project}/phase-NN-{slug}/review.md`.

Each merged finding carries:

- **Severity** — Blocker / Major / Minor / Nit
- **Agreement** — how many models raised it
- **Location** — `file:line`
- **The finding**, and a concrete suggested fix

**Agreement is a signal, not a verdict.** Something all three models flagged is
probably real. Something one model flagged may be the one that understood the code —
single-model findings at Blocker or Major severity get read individually, never
dismissed for lacking consensus.

## Step 5 — Triage with the developer

Go through Blockers and Majors together. For each: fix now, defer to `findings.md`
with a reason, or reject with a reason.

**Reject freely, silently never.** Reviewers are often wrong about a codebase they saw
in fragments. A rejected finding with a written reason is a good outcome; a finding
quietly dropped is a lost bug.

Every fix re-runs `atom check`. Every deferral and rejection is recorded.

## Step 6 — Report

Present the merged report, the triage outcome, and what remains open.

---

## Done when

- [ ] At least two **different** models reviewed, none of them the author of the code
- [ ] Every changed file reviewed with its surrounding context
- [ ] Findings merged, deduplicated, severity-ranked
- [ ] Single-model Blockers and Majors read individually, not dismissed
- [ ] Blockers and Majors triaged with the developer
- [ ] Fixes verified by a fresh `atom check`
- [ ] Deferrals in `findings.md`, rejections recorded with reasons

## Next

`atom-ship`, or the next phase's `atom-poc`.
