---
name: atom-build
description: 'End-to-end orchestrator: problem statement to shipped phases, chaining discover, POC, plan, and per-phase POC/spec/TDD/review/ship. Keywords: build, build this, end to end, full pipeline, take it from here, run atom.'
---

# atom-build

Runs the whole Atom pipeline, from a problem statement to shipped phases.

Use this when the developer hands you a problem rather than a step. For a single step,
invoke that skill directly.

## Before you start

Read:

1. [AGENTS.md](../../AGENTS.md)
2. [anti-rationalization.md](../atom/references/anti-rationalization.md)
3. [human-gates.md](../atom/references/human-gates.md)

**Re-read anti-rationalization.md at every step transition.** Not out of ritual —
context compaction genuinely erases earlier file reads, and this is the longest
workflow in the framework, so it is the one most likely to compact mid-run.

---

## The pipeline

```
  atom-discover ──▶ ◆ ──▶ atom-poc ──▶ ◆ ──▶ atom-plan ──▶ ◆
                                │
                    (refuted) ◀─┘
                                              │
  ┌─── per phase ──────────────────────────────▼─────────────┐
  │                                                          │
  │   atom-poc ──▶ ◆ ──▶ atom-spec ──▶ ◆ ──▶ atom-tdd ──▶ ◆   │
  │       │                                        │         │
  │       └─ refuted ──▶ back to atom-plan         ▼         │
  │                                          atom-review     │
  └────────────────────────────┬─────────────────────────────┘
                               ▼
                          atom-ship

  ◆ = gate: present, end turn, wait
```

## Orchestration rules

**Run one step at a time.** Do not begin the next step in the same turn as a gate.
The gate is the point.

**Invoke downstream skills properly.** Read the target `SKILL.md` and work its
checklist. Do not reconstruct a skill from memory of what it probably says — that is
how steps quietly disappear.

**Carry context forward.** Every downstream skill gets the accumulated artifacts and
the confirmed build/test commands, so nothing re-detects what is already known.

**Phases are sequential.** Phase N+1 starts after phase N ships. What phase N teaches
routinely changes phase N+1's design — running them in parallel discards that.

**Refutation is not failure.** A refuted POC loops back. That is the pipeline working.

---

## Step 0 — Set up

1. Run `atom-init` if `.atom/` is absent.
2. Work on a branch, not on `main`.
3. Create `specs/{project}/` with `findings.md` and `decisions.md`, both from their
   templates, both populated with their explicit empty statement.
4. Register the run: `atom status --start {project}`.

## Step 1 — Project scope

`atom-discover` → **gate** → `atom-poc` → **gate** → `atom-plan` → **gate**

Approving the plan authorises **phase 1 only**. Later phases re-gate individually,
because phase 1 will change them.

## Step 2 — Per phase

For each phase in order:

| Step | Skill | Gate | Notes |
|---|---|---|---|
| 1 | `atom-poc` | ◆ | Skippable only with a specific recorded justification |
| 2 | `atom-spec` | ◆ | Never before the POC |
| 3 | `atom-tdd` | ◆ | Never before the spec is approved |
| 4 | `atom-review` | — | Models other than the one that wrote the code |
| 5 | `atom-ship` | — | Push only on explicit instruction |

Then:

```bash
atom phase done NN
```

Between phases, ask the developer whether the plan still holds. It often doesn't, and
finding that out costs one question.

## Step 3 — Close out

- Reconcile every design spec against what was actually built
- Present `findings.md` and `decisions.md` in full
- Summarise: phases shipped, POCs confirmed and refuted, what remains open

---

## Resuming

State lives in `.atom/state.json`. To resume:

```bash
atom status
```

Resume from the **last completed** step. If a gate was interrupted mid-conversation,
restart at that gate — not at the step before it, and never past it. An interrupted
gate was never approved, and an unapproved gate is an open gate.

Verify the artifacts on disk match what the state file claims before trusting it.

---

## Done when

- [ ] Every phase in the plan is shipped, or explicitly deferred with a reason
- [ ] Every gate had an explicit developer response
- [ ] Every design spec matches the code that exists
- [ ] `findings.md` and `decisions.md` complete and presented
- [ ] `atom check` green on the final state, output pasted verbatim
