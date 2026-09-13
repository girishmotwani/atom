# Atom

**An agentic development framework for Go.**

Atom exists to stop AI agents from writing large amounts of confident code against an
imagined design.

---

## The one rule

> **Nothing gets designed until something has been proven to work.**

Every unit of work — the project, and then each phase within it — runs the same three
beats:

```
   PROVE  ──────────▶  DESCRIBE  ──────────▶  BUILD
   (POC)               (spec)                 (TDD)
```

1. **PROVE** — a throwaway Go program that answers one uncomfortable question. Run it.
2. **DESCRIBE** — *now* write the design spec, informed by what actually happened.
3. **BUILD** — red, green, refactor, with the developer in the loop.

Most agent frameworks start at step 2. The design reads beautifully, the code gets
written, and the assumption underneath it turns out to be wrong three days later. Atom
front-loads that discovery into an hour of disposable code.

---

## Why the POC comes first

A design document is a prediction. A POC is an observation.

When you design first, every later artifact inherits the design's assumptions — the
spec elaborates them, the tests encode them, the implementation hardens them. By the
time reality disagrees, disagreeing is expensive.

A POC has three possible outcomes, and **all three are wins**:

| Outcome | What it means | What it saved you |
|---|---|---|
| **Confirmed** | The assumption held | You can now design on evidence instead of hope |
| **Refuted** | The assumption was wrong | The entire design you were about to write |
| **Inconclusive** | The spike missed the question | A false confidence you were about to bake in |

Atom's most valuable moment is an agent reporting *"I was wrong, here's the output."*

---

## Pipeline

```
  problem statement / MRD
        │
        ▼
  atom-discover   interview the developer → POC Brief
        │  ◆
        ▼
  atom-poc        throwaway Go spike, executed → POC Report
        │  ◆
        ▼
  atom-plan       phase breakdown → Phase Plan
        │  ◆
        ▼
  ┌─ per phase ────────────────────────────────┐
  │   atom-poc     spike this phase's risk     │
  │        ◆                                   │
  │   atom-spec    high-level design spec      │
  │        ◆                                   │
  │   atom-tdd     red → green → refactor      │
  │        ◆                                   │
  │   atom-review  multi-model review          │
  └────────────────────────────────────────────┘
        │
        ▼
  atom-ship       commit + pull request

  ◆ = gate: the agent presents, stops, and waits for you
```

| Skill | Purpose |
|---|---|
| `atom-init` | Onboard a Go repository |
| `atom-discover` | Vague problem → concrete, falsifiable POC Brief |
| `atom-poc` | Build, run and evaluate a throwaway spike |
| `atom-plan` | Break proven work into independently shippable phases |
| `atom-spec` | High-level design spec for one phase |
| `atom-tdd` | Implement one phase test-first |
| `atom-review` | Multi-model review |
| `atom-ship` | Commit and open a pull request |
| `atom-build` | End-to-end orchestrator |

---

## Design principles

### Readable Go, not clever Go

Atom deliberately prefers **readable and extensible** Go over maximally idiomatic Go.
When the two conflict, readability wins.

```go
// Idiomatic — fine if you already know this file.
for i, v := range s {
    if v.t > d { r = append(r, i) }
}

// Atom — obvious to someone who has never seen it.
for index, session := range activeSessions {
    if session.idleTime > idleTimeout {
        expiredIndexes = append(expiredIndexes, index)
    }
}
```

Real names, explicit control flow, a doc comment on every exported symbol explaining
*why* it exists, and inline comments wherever a competent Go developer would pause and
ask "why?". `gofmt` is still absolute — the deviations are about naming, structure and
commentary. Full rules in [go-style.md](skills/atom/references/go-style.md).

### Honest enforcement

Atom has **no hidden compliance monitor**, no fabricated consequences, no invented
authority. Frameworks that coerce agents with fictional surveillance teach them that
stated rules may be bluffs — and an agent that learns to discount one rule discounts
the rest.

Atom's gates are real and local: commands you can run, artifacts on disk, and a human
in the conversation.

```bash
atom check     # build + vet + gofmt + test + race + coverage
```

### The developer is a participant

Gates are conversations, not approvals of finished work. The agent asks **one question
at a time**, explores the code before asking anything, and stops at every gate — it
presents, ends its turn, and waits.

### Everything is on disk

```
.atom/          state, config, event log
specs/          briefs, POC reports, plans, design specs, test specs, findings, decisions
poc/            every spike ever run, kept as re-runnable evidence
```

Two artifacts are always written, even when empty: `findings.md` (what you saw and
chose not to fix) and `decisions.md` (every time your judgement replaced the
developer's). They exist so that judgement can be audited.

---

## Getting started

```bash
pip install -e ./tools        # the atom CLI
cd your-go-project
atom init                     # scaffold, check toolchain, capture a green baseline
```

Then point your agent at a problem:

```
Build a feature: add topic-based routing to the event bus
```

The agent reads [AGENTS.md](AGENTS.md), picks up `atom-build`, and starts by asking you
what the riskiest part is.

### Recommended model

Atom's loop is heavy on judgement — deciding whether a POC actually answered its
question, whether a design follows from evidence, whether a test failure is a code
defect or a test defect.

**HydraFusion** in GitHub Copilot CLI suits this well. It is not a single model but a
multi-model orchestration layer that routes each task through single, cascade or
critique workflows across providers.

```
/update
/experimental on
/model          → HydraFusion (Research Preview)
```

Fallbacks and role guidance in
[model-guidance.md](skills/atom/references/model-guidance.md).

---

## Requirements

| Tool | Version | For |
|---|---|---|
| Go | ≥ 1.21 | everything |
| Python | ≥ 3.10 | the `atom` CLI |
| git | any | `atom-ship` |
| gh | any | pull requests (optional) |

Go is the **target** language. Python is the **tooling** language. Atom never asks you
to write or run PowerShell.

---

## Atom is its own worked example

The `atom` CLI was built with Atom.

`specs/atom-cli/` contains the real POC brief, the real POC report with verbatim
terminal output, the phase plan and the design specs. `poc/module-isolation/` contains
the actual spike — and you can still run it.

That spike asked whether a throwaway module under `poc/` could break the parent build.
The answer was no, which validated the design. It also **refuted** a smaller assumption
along the way: Go writes compile errors to stderr, so capturing stdout alone would have
shown POC failures to developers as silent success. That is a bug that never shipped,
because a disposable program found it before a design was written around it.

---

## License

MIT — see [LICENSE](LICENSE).
