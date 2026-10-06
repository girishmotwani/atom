---
name: plan
description: 'Break proven work into ordered, independently shippable phases based on POC evidence. Keywords: plan, phases, break down, roadmap, decompose, milestones, sequencing.'
---

# /atom:plan

Turns a **confirmed** project-level POC into an ordered set of phases, each small
enough to design, build and ship on its own.

This is a conversation with the developer, not a document you hand over. You propose a
breakdown; they reshape it.

## When to use

- The project-level POC came back **Confirmed** and was approved
- An existing plan needs re-cutting because a phase POC refuted an assumption
- Work is large enough that a single spec would be unreviewable

Small, single-concern work does not need a plan. One phase is a legitimate answer —
say so rather than manufacturing three.

## Before you start

Read:

1. [poc-discipline.md](../atom/references/poc-discipline.md)
2. [anti-rationalization.md](../atom/references/anti-rationalization.md)
3. [human-gates.md](../atom/references/human-gates.md)
4. The approved `poc-report.md` — the plan must follow from its evidence

---

## Step 1 — Ground the plan in evidence

List what the POC actually established, and list separately what is still assumed.

Every phase you propose should trace back to one or the other. A phase resting on an
assumption is fine — but it must be **labelled** as resting on an assumption, and that
assumption becomes that phase's POC question.

If you cannot trace a phase to either, you invented it. Cut it or justify it out loud.

## Step 2 — Cut the phases

A good phase is:

| Property | Test |
|---|---|
| **Independently shippable** | Could this merge on its own without breaking `main`? |
| **Vertically sliced** | Does it deliver behaviour end to end, rather than one horizontal layer? |
| **Small** | Roughly one design spec and one focused review |
| **Singly-purposed** | Can you state what it delivers without using "and"? |
| **Verifiable** | Is "done" a condition you could check by running something? |

The failure mode is horizontal slicing — "phase 1: all the types, phase 2: all the
logic, phase 3: all the tests". Nothing is shippable until phase 3, nothing is
learnable before the end, and the design never meets reality. Slice so that **phase 1
is a thin path all the way through**, then thicken it.

### Ordering

Front-load risk. The purpose of phasing is to learn early, and you only learn from the
phases that could fail. A plan that saves the hard part for last is a plan that
discovers its problem after everything has been built around it.

Then order by dependency, and prefer an order where each phase leaves the tree green.

## Step 3 — Assign POC questions

For each phase, decide: does this carry technical uncertainty?

- **Yes** → write its falsifiable POC question now, into the plan.
- **No** → record the specific reason it can be skipped.

A skip needs a checkable justification. "It seemed straightforward" is not one.
"Phase 2's POC already proved the codec round-trips, and this phase only moves the
call site" is one. Skips go in `decisions.md` and get raised at the phase gate.

Expect most phases in a well-cut plan to need a small spike. If none of them do,
either the work is genuinely mechanical — or you have not looked hard enough for what
could go wrong.

## Step 4 — Work it through with the developer

Present the cut as a proposal and ask about it. Useful things to surface:

- Which phase they would want shipped first if everything else slipped
- Whether any phase boundary cuts through something they think of as one unit
- What they would drop entirely under time pressure

Reshape the plan from the answers. **One question at a time.**

## Step 5 — Write the Phase Plan

Fill in [phase-plan.md](../atom/templates/phase-plan.md) at
`specs/{project}/phase-plan.md`.

Then create the phase directories so the structure is visible:

```
specs/{project}/phase-01-{slug}/
specs/{project}/phase-02-{slug}/
```

Register the phases so progress is trackable:

```bash
atom phase add 01 {slug} --risk high --poc-required
atom phase list
```

## Step 6 — Gate

Present per [human-gates.md](../atom/references/human-gates.md): the phase table, the
sequencing rationale, which phases need spikes, and one specific question.

**End your turn. Wait.**

Approval authorises starting **phase 1**. It does not approve phases 2..n in advance —
each phase re-gates through its own POC and spec, because what phase 1 teaches will
change them.

---

## The plan is not fixed

A phase POC that comes back **Refuted** is the plan working as intended. Return here,
re-cut the affected phases, and re-gate. A plan that never changes across a project is
a plan that stopped being consulted.

---

## Done when

- [ ] Every phase traces to POC evidence or a labelled assumption
- [ ] Each phase is independently shippable and vertically sliced
- [ ] Each phase states "done" as a verifiable condition
- [ ] Risk is front-loaded in the ordering
- [ ] Each phase has a POC question or a specific recorded justification for skipping
- [ ] Plan reshaped through conversation, not just presented
- [ ] `phase-plan.md` complete; phase directories created; phases registered
- [ ] Plan presented at a gate and explicitly approved

## Next

`/atom:poc` for phase 1 — or `/atom:spec` if phase 1's skip was justified and approved.
