# Copilot Instructions

This repository uses **Atom**, an agentic development framework for Go.

**Read [`AGENTS.md`](../AGENTS.md) before doing any work here.** It defines the pipeline,
the gate protocol, and the Go conventions this project deviates toward.

## The one rule

> Nothing gets designed until something has been proven to work.

PROVE (throwaway POC) → DESCRIBE (design spec) → BUILD (TDD). In that order, for the
project and again for every phase.

## Skills

Skills live in [`skills/`](../skills/). Read the relevant `SKILL.md` and work its
checklist — do not reconstruct a skill from memory.

| Trigger | Skill |
|---|---|
| "onboard", "set up atom" | [`/atom:init`](../skills/init/SKILL.md) |
| "what should we build", a problem statement or MRD | [`/atom:discover`](../skills/discover/SKILL.md) |
| "POC", "spike", "prove it", "try it" | [`/atom:poc`](../skills/poc/SKILL.md) |
| "plan", "phases", "break this down" | [`/atom:plan`](../skills/plan/SKILL.md) |
| "spec", "design", "architecture" | [`/atom:spec`](../skills/spec/SKILL.md) |
| "implement", "TDD", "build the phase" | [`/atom:tdd`](../skills/tdd/SKILL.md) |
| "review", "code review" | [`/atom:review`](../skills/review/SKILL.md) |
| "ship", "PR", "pull request" | [`/atom:ship`](../skills/ship/SKILL.md) |
| "build this", a whole feature end to end | [`/atom:build`](../skills/build/SKILL.md) |

## Discipline references

Re-read these at every step transition, and after any context compaction — compaction
genuinely erases earlier file reads, and a summary of a rule is not the rule.

- [anti-rationalization.md](../skills/atom/references/anti-rationalization.md)
- [poc-discipline.md](../skills/atom/references/poc-discipline.md)
- [tdd-discipline.md](../skills/atom/references/tdd-discipline.md)
- [go-style.md](../skills/atom/references/go-style.md)
- [human-gates.md](../skills/atom/references/human-gates.md)
- [verification.md](../skills/atom/references/verification.md)
- [model-guidance.md](../skills/atom/references/model-guidance.md)

## Working in this repository specifically

Atom's own tooling is **Python**, under `tools/`. Atom targets **Go**, but writes no Go
itself except throwaway spikes under `poc/`.

```powershell
cd tools
python -m pip install -e ".[dev]"
python -m pytest tests -v --cov=atom
```

Never add PowerShell or shell scripts. Automation here is Python, so it runs the same
everywhere.

## Non-negotiables

- **Never invent enforcement.** Atom does not have a hidden compliance monitor, and no
  document in this repository may claim otherwise. Rules are justified by their real
  consequences or they are not stated.
- **Never push without an explicit instruction.** Committing locally is fine.
- **Always produce `findings.md` and `decisions.md`,** even when the honest content is
  "No findings." and "No deviations from instructions."
- **One question at a time** when talking to the developer.
