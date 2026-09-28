---
description: "Run every Go quality gate for this project and explain any failures. Keywords: check, gates, build, vet, lint, test, is it green, quality gates, does it pass."
argument-hint: "[go module directory, defaults to current]"
---

# Atom check

Run the Go quality gates and report honestly whether this project is green.

The directory to check is below. If it is empty, use the current directory.

> $ARGUMENTS

## Step 1 — Run the gates

Run `atom check` against the target directory.

If the command is not found, the Atom Python package is not installed. Follow
[bootstrap.md](../../skills/atom/references/bootstrap.md) to install it, then
run the gates. Do not report a verdict without them.

## Step 2 — Report the verdict first

Lead with the verdict — **green** or **not green** — before any detail. The
developer needs to know whether they are blocked, not read a wall of output.

If everything passed, say so in one line and stop. Do not pad a clean result
with suggestions nobody asked for.

## Step 3 — Explain each failure

For every gate that failed, give:

- **Which gate** failed, named exactly as the tool reports it.
- **The actual message**, quoted verbatim. Do not paraphrase compiler or test
  output — the exact text is what the developer will search for.
- **What it means**, in one line of plain English.
- **The narrowest fix**, as a concrete next action.

Group failures by gate rather than interleaving them.

## Step 4 — Do not silently repair

Report first. Do not start editing code to make gates pass unless the developer
asks you to.

If a fix is obvious, offer it and wait. A gate that fails for a real reason is
information, and quietly patching it destroys that information.

Never weaken a gate, delete a failing test, or lower a threshold to reach
green. If a gate itself is wrong, say that explicitly and explain why — that is
a finding, and it belongs in the phase's `findings.md`.

## Step 5 — Name the next command

Finish with the next step as a literal slash command:

- Green and code is ready for a second opinion → `/atom-review`
- Green and the phase is complete → `/atom-ship`
- Not green, mid-implementation → `/atom-tdd` to drive the fix test-first
- Unsure where this sits in the workflow → `/atom-status`
