---
name: atom-spec
description: 'Write the high-level design spec for one phase, grounded in that phase POC evidence. Keywords: spec, design, design doc, architecture, API design, describe the approach.'
---

# atom-spec

The **DESCRIBE** beat. Writes the design spec for exactly one phase — after that
phase's POC, never before.

The spec's job is to be precise enough that `atom-tdd` can derive tests from it
without guessing.

## When to use

- A phase POC came back **Confirmed** and was approved
- A phase's POC was justifiably skipped and the developer approved the skip

## Never use when

- No POC has been run for this phase and no skip was approved. Specifying an unproven
  design is the failure mode Atom exists to prevent. Go to `atom-poc`.

## Before you start

Read:

1. [go-style.md](../atom/references/go-style.md) — Atom deviates from idiomatic Go; do not assume you know the conventions
2. [anti-rationalization.md](../atom/references/anti-rationalization.md)
3. [human-gates.md](../atom/references/human-gates.md)
4. This phase's `poc-report.md`, and the `phase-plan.md` entry for this phase

---

## Step 1 — Extract what the POC established

Write two lists before designing anything:

- **Established** — facts the spike demonstrated, with the evidence
- **Still assumed** — everything else the design will rest on

Every significant decision in the spec must trace to the first list or be explicitly
labelled as resting on the second. An unlabelled assumption reads as a fact to the
next person, including to `atom-tdd`.

## Step 2 — Design the public surface first

Start from the outside: what does a caller write to use this?

Keep the exported surface minimal. Unexporting later is a breaking change; exporting
later is not. When unsure, leave it unexported.

Apply [go-style.md](../atom/references/go-style.md):

- Define interfaces where they are **consumed**, not where they are implemented
- Keep interfaces to one to three methods
- Return concrete types
- Take dependencies as constructor parameters so tests can substitute them
- `context.Context` first on anything that can block
- A doc comment on every exported symbol saying **why** it exists

### Signature consistency

This is the single most common defect in design specs, and it poisons the TDD step.

Every signature must be identical everywhere it appears — in the interface block, in
the implementation sketch, and in any composition or usage example in the same
document. Before the gate, walk every call site in the document and check it against
its declaration: name, parameter count, parameter types, return types.

One authoritative code block per type. Do not write a "simplified" version alongside a
"full" version — they diverge, and the reader cannot tell which one is true.

## Step 3 — Write behaviour as numbered statements

These become the test cases. Each must be independently verifiable.

```
B1. Submit returns ErrQueueFull when the queue is at capacity.
B2. Submit accepted while draining returns ErrDraining and does not enqueue.
B3. Drain blocks until every in-flight job completes or ctx is cancelled.
B4. Drain with a cancelled context returns ctx.Err() and abandons in-flight jobs.
```

> If you cannot picture the test, the statement is too vague to implement.

"Handles errors gracefully" is not a behaviour. "Returns `ErrQueueFull` without
blocking when the buffer is full" is.

## Step 4 — Specify the parts that get skipped

These sections are where under-specification actually bites:

- **Error handling** — condition, behaviour, and the exact error returned. Name the
  sentinel errors callers branch on.
- **Concurrency** — who starts each goroutine and how it stops; what each mutex
  guards; what is safe for concurrent use. If something is **not** safe for concurrent
  use, say so explicitly. Silence is not a contract.
- **Extension points** — where future behaviour is added without editing existing code.
- **Trade-offs considered** — including the options you rejected and why. Without
  them, the next reader re-litigates decisions you already settled.

## Step 5 — Diagrams

ASCII art or Mermaid only. No image files, no PlantUML.

For Mermaid, use `<br>` for line breaks in labels — never `\n`.

Include one when structure or flow is hard to hold in prose. Do not include one out of
habit.

## Step 6 — Write the spec

Fill in [design-spec.md](../atom/templates/design-spec.md) at
`specs/{project}/phase-NN-{slug}/design-spec.md`.

Keep it **high level**. This is a design spec, not the implementation transcribed into
markdown. Specify the shape, the contracts and the behaviour; leave the body of each
function to TDD. If the spec contains working implementations, you have written the
code twice and the second copy will rot.

Append ambiguities to `findings.md` as you hit them. Record every judgement call you
made on the developer's behalf in `decisions.md`.

## Step 7 — Gate

Present per [human-gates.md](../atom/references/human-gates.md): the public API, the
numbered behaviours, the trade-offs you chose between, anything resting on an
assumption rather than evidence, and one specific question.

**End your turn. Wait.**

Approval authorises implementing **this** spec. If the spec changes materially during
TDD, it re-gates.

---

## Done when

- [ ] Established facts and standing assumptions listed separately
- [ ] Public API minimal, with a doc comment on every exported symbol
- [ ] Every signature verified consistent at every occurrence in the document
- [ ] Behaviours numbered and independently verifiable
- [ ] Error handling, concurrency and extension points all specified
- [ ] Concurrency safety stated explicitly, including when the answer is "not safe"
- [ ] Trade-offs recorded, including rejected options
- [ ] Diagrams ASCII or Mermaid only
- [ ] `findings.md` and `decisions.md` updated during the work
- [ ] Spec presented at a gate and explicitly approved

## Next

`atom-tdd` — implement this phase test-first.
