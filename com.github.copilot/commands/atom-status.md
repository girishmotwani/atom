---
description: "Report where an Atom project currently stands: the active phase, which of its artifacts exist, and what is blocking the next beat. Keywords: status, where am I, what phase, progress, what is left, project state."
argument-hint: "(no arguments)"
---

# Atom status

Report where this project stands and what the developer should do next.

## Step 1 — Read the state

Run `atom status` and read its output. It names the current phase, recent
activity, and any problems it detected.

If the command is not found, the Atom Python package is not installed. Follow
[bootstrap.md](../../skills/atom/references/bootstrap.md) to install it, then
read the status.

If there is no `.atom/` directory, this is not an Atom project. Say so and
point at `/atom-init`, then stop.

## Step 2 — Explain it, do not just echo it

Do not paste raw output and leave it there. Translate it into three things:

1. **Where we are** — the active phase and the beat it is sitting in.
2. **What exists** — which of the phase's seven artifacts are present.
3. **What is missing** — the specific gap standing between here and the next beat.

The seven per-phase artifacts are `poc-brief`, `poc-report`, `design-spec`,
`test-spec`, `tdd-log`, `findings` and `decisions`.

## Step 3 — Name the next command

Finish with the single next step as a literal slash command, plus one line on
what it will do. Route to the earliest beat whose output is still missing —
never skip ahead to a later beat because it looks more interesting.

| What is missing | Next |
|---|---|
| No falsifiable question | `/atom-discover` |
| Question but no spike | `/atom-poc` |
| POC verdict but no design spec | `/atom-spec` |
| Agreed spec but no code | `/atom-tdd` |
| Code but no review | `/atom-review` |
| Everything present | `/atom-ship` |

If the project is complete and there is nothing outstanding, say that
explicitly rather than inventing work.
