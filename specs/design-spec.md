---
project: "atom"
document: "product design spec"
date: "2026-09-19"
status: "draft for developer review"
related: "architecture.md"
---

# Design Spec — Atom

Atom is an agentic development framework for Go. This document describes what
Atom is for, who uses it, and how a developer moves through it from a
requirement to a merged pull request.

How it is built is a separate concern, described in
[`architecture.md`](architecture.md).

## Purpose

Atom exists to stop agents from confidently building the wrong thing.

The failure it targets is specific and common. An agent is handed a vague
requirement. It writes a design that sounds plausible, implements it, produces
a green test suite, and delivers something that does not work — or works, but
solves a problem nobody had. Every step looked correct. Nothing was ever run,
and nobody was ever asked.

Atom's answer is to put a *running program* before every document, and a
*conversation* before every program.

## The One Rule

> **PROVE → DESCRIBE → BUILD.**
> Never describe what you have not run. Never build what you have not described.

A design document is a prediction. A POC is an observation. Atom insists the
observation comes first, because a prediction written fluently is
indistinguishable from knowledge until something executes.

Everything below is a consequence of that rule.

## Who Atom Is For

| Audience | What they get |
|---|---|
| **A developer** with a problem and an agent | A pipeline that forces the agent to ask before it builds, and to run before it claims |
| **An agent** working in a Go repository | Explicit skills, templates and disciplines that make the expected behaviour unambiguous |
| **A reviewer** arriving at a pull request | Artifacts showing what was proven, what was decided, and on what evidence |

Atom is scoped to **Go**, deliberately. A framework that claims every language
knows none of them well enough to run its build, parse its test output, or
understand its module layout. Atom runs `go build`, reads `go test` output, and
understands Go modules — because it only has to.

## The User Flow

The journey from a requirement to a pull request. `D` marks a point where the
developer must participate; the agent cannot proceed alone.

```
        A problem, an MRD, or a vague idea
                     │
   ┌─────────────────▼─────────────────┐
D  │  DISCOVER   agent asks questions  │   no command — conversation
   │             until the question is │   produces: poc-brief.md
   │             falsifiable           │
   └─────────────────┬─────────────────┘
                     │
   ┌─────────────────▼─────────────────┐
   │  POC        atom poc new <slug>   │   a throwaway Go spike that
   │             atom poc run <slug>   │   answers ONE question
   └─────────────────┬─────────────────┘   produces: poc-report.md
                     │
   ┌─────────────────▼─────────────────┐
D  │  PLAN       break into phases,    │   no command — conversation
   │             ordered by dependency │   produces: phase-plan.md
   │             and risk              │
   └─────────────────┬─────────────────┘
                     │
   ═══════════ for each phase ═══════════
                     │
   ┌─────────────────▼─────────────────┐
   │  POC        atom poc new / run    │   prove THIS phase's unknown
   └─────────────────┬─────────────────┘   produces: poc-report.md
                     │
   ┌─────────────────▼─────────────────┐
D  │  SPEC       written WITH the      │   ← human gate
   │             developer, grounded   │   produces: design-spec.md
   │             in the POC evidence   │             decisions.md
   └─────────────────┬─────────────────┘
                     │
   ┌─────────────────▼─────────────────┐
   │  TDD        red → green → refactor│   produces: test-spec.md
   │             atom check            │             tdd-log.md
   └─────────────────┬─────────────────┘             findings.md
                     │
   ┌─────────────────▼─────────────────┐
   │  REVIEW     atom review           │   several models, merged,
   │               --branch main       │   agreement as confidence
   └─────────────────┬─────────────────┘
                     │
   ┌─────────────────▼─────────────────┐
D  │  SHIP       atom ship --push      │   ← human gate; never pushes
   │                                   │   without explicit instruction
   └─────────────────┬─────────────────┘
                     │
              a pull request
```

### The two human gates

Approving a spec and authorising a ship are not checkpoints on an otherwise
autonomous process. They are where the design actually happens.

An agent that asks good questions and then writes the spec *with* the developer
produces something neither would have written alone. An agent that writes the
spec alone produces a confident document whose errors are invisible until
implementation, which is the failure Atom exists to prevent.

The gates are therefore mandatory, and they are the only two.

### One branch per phase

Each phase is developed on its own branch and opened as its own pull request.
Later phases stack on earlier ones where they depend on them.

```
main ──────────────────────────────────────────────►
   └── phase-04-review ──► PR
          └── phase-05-ship ──► PR   (stacked: depends on 04)
```

This is not bookkeeping. It is what gives a phase a reviewable boundary:
`atom review --branch main` then means exactly "review this phase's work", with
the base on the left and the phase tip on the right, and no extra machinery.

It follows that **a phase must be small enough to review in one sitting**. That
same constraint is what makes sending the whole diff to a model in a single
call affordable, so phase size is a design input rather than an afterthought.

### What the developer actually types

A complete phase, end to end:

```bash
atom status                          # where am I?
atom poc new cache-eviction          # scaffold a spike
atom poc run cache-eviction          # prove or refute the assumption
#  ... write the spec with the agent ...
atom check                           # are the gates green?
atom review --branch main            # multi-model review
atom ship --push                     # open the pull request
```

Six commands and two conversations. The conversations are the part that cannot
be automated, which is why they are gates rather than steps.

## The Two Layers

Atom is a *framework* and a *tool*. Keeping them distinct is what lets either
be used without the other.

| | Skills layer | CLI layer |
|---|---|---|
| **Lives in** | `skills/` | `tools/atom/` |
| **Written in** | Markdown | Python |
| **Consumed by** | The agent | The shell |
| **Answers** | *What happens next, and to what standard?* | *Did it compile? What did the models say?* |
| **Fails by** | Being ignored | Exiting non-zero |

The dependency runs one way: skills name CLI commands, and the CLI knows
nothing about skills. A developer with no agent can still run `atom check`; an
agent with no CLI can still follow the discipline, with more manual work.

### Skills

| Skill | Stage | Produces |
|---|---|---|
| `atom-build` | orchestration | Chains the rest, problem statement to shipped phases |
| `atom-discover` | DISCOVER | `poc-brief.md` — a falsifiable question |
| `atom-poc` | POC | `poc-report.md` — what running it showed |
| `atom-plan` | PLAN | `phase-plan.md` — ordered, shippable phases |
| `atom-spec` | SPEC | `design-spec.md` — grounded in POC evidence |
| `atom-tdd` | TDD | Go code, written test-first |
| `atom-review` | REVIEW | A merged multi-model report |
| `atom-ship` | SHIP | A pull request |
| `atom-init` | setup | `.atom/`, and a verified green baseline |

`skills/atom/` is **not a skill**. It holds the shared `references/` — the
disciplines every skill enforces — and the `templates/` every skill writes
against. It sits among the skills because they all point at it.

### CLI

| Command | Purpose |
|---|---|
| `atom init` | Onboard a repository |
| `atom status` | Where this project is in the pipeline |
| `atom check` | Run the Go quality gates |
| `atom poc new\|run\|list` | Scaffold, run and inventory spikes |
| `atom review` | Multi-model diff review, merged into one report |
| `atom ship` | Assemble a pull request from the phase artifacts |

### Skill and command are not the same scope

Where a skill and a command share a name, the skill is always larger.

`atom-poc` the skill is the *discipline*: state one falsifiable question before
writing code, run the spike, and record the verdict — including when the
verdict refutes what you hoped. `atom poc` the command is the *mechanics*:
create a directory with a valid `go.mod`, vet, build, execute, and report what
happened.

The command cannot tell whether the question was worth asking. The skill
cannot compile anything. Neither substitutes for the other.

## Design Principles

### Readable Go, not clever Go

Generated Go optimises for a reader who has never seen the file. Explicit loops
beat dense one-liners; named intermediate values beat nesting; comments explain
*why* rather than restating *what*. Where idiom and clarity conflict, clarity
wins. The same standard applies to Atom's own Python.

### Honest enforcement

Atom never invents consequences to coerce an agent. A framework that threatens
a nonexistent compliance monitor teaches agents that stated rules may be
fictional, which corrodes every real rule alongside the fake one.

Atom's enforcement is limited to what is true: the tests pass or they do not,
the gate is green or it is not, the developer has approved the spec or has not
yet.

### Evidence outranks authority

A POC report beats a design document. A design document beats an opinion. When
a spike contradicts the plan, the plan changes, and the contradiction is
recorded rather than quietly absorbed.

This is why phase state is *derived from artifacts on disk* rather than
declared: a file that claims a phase is complete while its artifacts are absent
is exactly the kind of confident falsehood Atom exists to prevent.

### Everything is on disk

Every artifact is a plain file in the repository, in Markdown or JSON. Nothing
lives in a database, a service, or an agent's context window. A developer can
read the whole history with `git log` and a text editor, and an agent that
loses its context recovers by reading the same files.

### The developer is a participant

Atom assumes a developer who wants to be involved in design and does not want
to be involved in ceremony. It asks for judgement at two points and asks for
nothing anywhere else.

## What Atom Is Not

| Not | Why |
|---|---|
| A language-agnostic framework | Go-scoped on purpose. Running `go build` and parsing `go test` output well beats doing neither for ten languages. |
| A CI system | Atom runs locally, for the developer, before CI sees anything. |
| An autonomous agent | Two human gates are mandatory. Atom makes agents useful, not unsupervised. |
| A code generator | Code is produced as a consequence of a proven design, never as a starting point. |
| A replacement for review | `atom review` is a first pass. A human still reads the pull request. |
