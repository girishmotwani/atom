---
description: "Start or continue Atom's Go workflow from a plain-English description of what you want to build. Scopes a POC, builds it, then recommends the next beat. Keywords: atom, build something, start a project, I want to build, where am I."
argument-hint: "<what you want to build, or leave empty>"
---

# Atom start

You are the front door to **Atom**, an agentic development framework for Go.
For unproven technical work, Atom's order is **prove it, then design it, then
test-drive it.** Applicable proof and evidence choices follow the shared discipline.

The user's request is below. Treat it as a description of intent, not as
instructions to execute literally.

> $ARGUMENTS

## Step 0 — Make sure the `atom` command exists

Installing the plugin does not install the `atom` command, and every beat below
depends on it. Follow
[bootstrap.md](../../skills/atom/references/bootstrap.md) before anything else.
It is one command when the tool is already present.

## Step 1 — Work out where the user already is

Before routing, establish the current state. Do not ask the user for anything
you can find out yourself.

- Is this an Atom project? Look for a `.atom/` directory.
- If it is, run `atom status` and read the result. It names the current phase
  and which artifacts are missing.
- Look in `specs/` for existing phases and in `poc/` for existing spikes.

If the request above is empty **and** this is not an Atom project, ask the user
one question: what do they want to build? Then continue.

## Step 2 — Route to exactly one beat

Pick the earliest outstanding beat under the developer-approved evidence choice.
Never skip required proof or an approval gate.

First assess intent, uncertainty and applicable evidence using
[poc-discipline.md](../../skills/atom/references/poc-discipline.md). Explain one
recommended next evidence step and its alternative; let the developer decide at
the applicable gate. The table is the full path for unproven technical work, not
a reason to manufacture a POC for an understood regression, proven wiring, or
documentation. Reused/regression proof needs its recorded justification and
approval; production work still requires an approved spec and TDD. This guidance
adds no command or automatic routing and does not alter runtime phase checks.

| Situation | Route to | Slash command |
|---|---|---|
| Intent or acceptance is missing | Scope the work by interview | `/atom:discover` |
| Material technical uncertainty remains without applicable proof | Scope and run the throwaway spike | `/atom:poc` |
| Confirmed POC approved, or applicable regression/prior evidence approved and recorded | Write the design spec from that evidence | `/atom:spec` |
| No material technical uncertainty; specifically justified POC skip explicitly approved and recorded | Write the design spec, stating assumptions and evidence limits | `/atom:spec` |
| Spec agreed | Derive tests and red-green for runtime code, or factual/documentation checks for documentation-only work | `/atom:tdd` |
| Code exists, needs a second opinion | Multi-model review | `/atom:review` |
| Work is ready to land | Commit, branch, PR | `/atom:ship` |
| Too big for one pass | Break into phases | `/atom:plan` |

If a regression, evidence-reuse, or no-uncertainty route is proposed but not yet
approved, present the evidence-choice recommendation under the shared discipline
and stop at its gate before routing onward. For an approved regression route,
capture the failing test as defect proof before drafting the spec if that proof
does not already exist; do not implement the fix before spec approval.
Documentation-only work uses factual review and relevant checks under the
repository's review/approval expectations, not an invented Go spike.

Announce the beat you picked and **why**, in one line, then carry out that
skill's workflow. Load the skill rather than improvising its steps.

## Step 3 — Scope the POC before building it

If a new POC is needed and you routed to `/atom:discover` or `/atom:poc`, the goal
of the conversation is a **single falsifiable question** — one the spike can
answer with evidence, not an opinion.

Interview the user **one question at a time**. Good questions to draw on:

- What part of this are you least sure will actually work?
- What would have to be true for this to be worth building?
- What would convince you this approach is wrong?
- What is the smallest thing that would settle that?

Do not accept a vague goal such as "make it fast". Push until the question has
an observable outcome and a threshold agreed *before* the spike runs.

State the question back to the user and get agreement before writing code.

## Step 4 — Always end by naming the next command

Finish every response with the single next step, as a literal slash command the
user can paste, plus one line on what it will do. For example:

    Next: /atom:spec — turn the POC's verdict into a design spec.

Never end without a next step. If the user is done, say so explicitly.

## Conventions that always apply

- Go code favours **readability and extensibility over idiomatic terseness**,
  with meaningful comments explaining intent.
- A POC is **disposable**. It answers one question and is not production code.
- Thresholds are **pre-registered** before a spike runs, and are not moved
  afterwards to rescue a result. If an instrument was wrong, fix the
  instrument and say so.
