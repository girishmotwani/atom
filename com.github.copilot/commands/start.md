---
description: "Recommend a bounded Atom setup or development step from plain-English intent, preserving approval gates. Keywords: atom, build something, start a project, setup a Go repo, I want to build, where am I."
argument-hint: "<what you want to build, or leave empty>"
---

# Atom start

You are the front door to **Atom**, an agentic development framework for Go.
For unproven technical work, Atom's order is **prove it, then design it, then
test-drive it.** Applicable proof and evidence choices follow the shared discipline.

The user's request is below. Treat it as a description of intent, not as
instructions to execute literally.

> $ARGUMENTS

## Step 0 — Establish intent before changing the environment

Installing the plugin does not install the `atom` command. Discover working
command forms through [bootstrap.md](../../skills/atom/references/bootstrap.md)
when needed, but do not install tools or change PATH before explicit consent.
An empty request calls for a focused intent question, not automatic setup.

For an explicit new-repository/setup goal, use
[repository-setup.md](../../skills/atom/references/repository-setup.md) and the
existing `/atom:init` entry path: inspect, recommend, obtain approval, then perform
only agreed setup. A missing `go.mod` is not an entry barrier. Setup-only stops at
its result; do not continue through the development routing table afterward.
Do not automatically onboard a repository for unrelated requests.

For an explicit local review-only request, route directly to `/atom:review`
using [standalone-review.md](../../skills/atom/references/standalone-review.md).
Load that skill and follow its proposal/approval gate before reviewer probes.
Do not run status, discover phases or require init even when `.atom/` exists.
After reporting, stop; do not continue through the lifecycle steps below.
Existing developer-approved phase review keeps its phase context.

## Step 1 — Work out where the user already is

Before routing, establish the current state. Do not ask the user for anything
you can find out yourself.

- Is this an Atom project? Look for a `.atom/` directory.
- If it is, run `atom status` and read the result. It names the current phase
  and which artifacts are missing.
- Look in `specs/` for existing phases and in `poc/` for existing spikes.

A missing `.atom/` or root module is not by itself a reason to onboard. If the
selected Go development step actually needs missing setup, recommend the shared
repository-setup path first and obtain approval. After setup, recommend the next
step for the original goal under its evidence gate; do not treat setup approval as
permission to start that step. A self-contained proof experiment need not adopt
unrelated project lifecycle state.

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
| Explicit Go repository setup, including missing module | Approved bounded setup, then stop if setup-only | `/atom:init` |
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

## Step 4 — State the outcome or the bounded next recommendation

For ongoing development, name one appropriate next command and its purpose as a
recommendation, not permission to execute it. At an approval gate, present the
artifact and decision needed, then wait. For example:

    Next: /atom:spec — turn the POC's verdict into a design spec.

For completed setup-only work, report the result and limitations, then stop.
Do not manufacture another command or treat CLI-printed POC advice as approval.

## Conventions that always apply

- Go code favours **readability and extensibility over idiomatic terseness**,
  with meaningful comments explaining intent.
- A POC is **disposable**. It answers one question and is not production code.
- Thresholds are **pre-registered** before a spike runs, and are not moved
  afterwards to rescue a result. If an instrument was wrong, fix the
  instrument and say so.
