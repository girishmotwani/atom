---
name: atom-poc
description: 'Build, run and evaluate a throwaway Go spike that answers one falsifiable question. Produces a POC Report with verbatim evidence. Keywords: POC, proof of concept, spike, prototype, prove it, experiment, try it out.'
---

# atom-poc

The **PROVE** beat. Builds a disposable Go program that answers exactly one question,
runs it, and writes up what actually happened.

Used twice in the pipeline: once for the project, then once per phase that carries
technical risk.

## When to use

- A POC Brief exists and has been approved
- A phase in the plan has an open technical risk
- Any moment someone is about to design around an unverified assumption

## Before you start

Read, in this order:

1. [poc-discipline.md](../atom/references/poc-discipline.md) — **the authority for this skill**
2. [anti-rationalization.md](../atom/references/anti-rationalization.md)
3. [verification.md](../atom/references/verification.md)

You need an approved brief. If there isn't one, go back to `atom-discover`. Building a
spike without an agreed question produces a program nobody can grade.

---

## Step 1 — Restate the question

Copy the question out of the brief **verbatim** into your working notes.

Do not reword it. Rewording is how a miss becomes a hit: the question drifts toward
whatever the spike turned out to be good at, and the report confirms something nobody
asked.

## Step 2 — Scaffold

```bash
atom poc new {slug}
```

Creates `poc/{slug}/` with its own `go.mod`, a `main.go` stub, and a `README.md`
carrying the question. The spike is a **separate module** — it must not compile into
the production build, and it must be free to pull dependencies that production will
never take.

## Step 3 — Write the spike

Write the smallest program that can answer the question.

**This code is disposable, and should look it.** Hardcode values. Skip error handling.
`panic` on anything unexpected. Put it all in `main.go`. Time spent making a spike
elegant is time spent on code you are about to delete.

The one thing a spike must do well is **report**. It should print what it found,
clearly enough that the output alone settles the question:

```go
// The spike's entire job is to answer one question, so it prints the measurement
// the question asks about — not a generic "done".
fmt.Printf("processed=%d duration=%s p99=%s\n", processed, elapsed, p99)
```

If you find yourself building abstractions, splitting files, or adding configuration,
the question is too broad. Stop, narrow it, and check the narrowing with the developer.

### The scope trap

Spikes grow. You will be tempted to also check the adjacent thing while you're in
here. Don't. A spike that answers three questions answers none of them cleanly, and
its report cannot be graded. Note the adjacent question in `findings.md` as a
candidate for a later spike.

## Step 4 — Run it

```bash
atom poc run {slug}
```

Runs `go vet`, `go build`, then `go run`, and captures **all** output.

> **A POC that has not been executed does not exist.**

Reading the spike and concluding it would work is precisely the failure this whole
framework is built to prevent. If it doesn't run, it has proven nothing.

Capture the real output. You will paste it verbatim — never retyped, never rounded,
never reconstructed from memory. If you lost it, run it again.

If it measures something, run it more than once. A single timing sample is noise.

## Step 5 — Reach a verdict

Three outcomes. **All three are successes.**

| Verdict | Meaning | Next |
|---|---|---|
| **Confirmed** | The assumption held, and the output shows it | Proceed to `atom-spec` |
| **Refuted** | The assumption was wrong | Back to `atom-discover` with what you learned |
| **Inconclusive** | The spike didn't isolate the question | Sharpen and respike. Do **not** proceed |

Grade against the brief's success criteria, not against how you feel about the code.

**Inconclusive is not a soft confirm.** If the spike crashed, or the numbers came out
ambiguous, or you only got it working by changing what you were testing — the verdict
is Inconclusive. Writing that up as Confirmed launders a guess into the design as
evidence, and every decision downstream inherits it.

> Refuting your own plan is the highest-value outcome in this pipeline. You just saved
> the design. Report it with enthusiasm, not apology.

## Step 6 — Write the POC Report

Fill in [poc-report.md](../atom/templates/poc-report.md) at
`specs/{project}/poc-report.md`, or `specs/{project}/phase-NN-{slug}/poc-report.md`
for a phase spike.

Two sections carry most of the value:

- **Evidence** — verbatim output, in fenced blocks.
- **Explicitly Not Covered** — the boundary of what this proves. A spike showing a
  happy path at 1k req/s is not evidence about error paths at 100k req/s, and the
  report must say so, or somebody will later believe it was.

Record anything that surprised you. Surprises are the highest-value content in the
report — they are, by definition, the things the design would otherwise have got wrong.

Append to `findings.md` **as you go**, not from memory afterwards.

## Step 7 — Gate

Present per [human-gates.md](../atom/references/human-gates.md): the verdict, the
evidence, what it changes, and one specific question.

**End your turn. Wait.**

---

## After approval

Leave the spike in `poc/{slug}/`. It is documentation now — the next person who
doubts the decision can re-run it.

**Do not copy spike code into the implementation.** It earned its shortcuts by being
disposable. Production code earns its shape from the spec and the tests. Carry the
knowledge forward, not the source.

---

## Done when

- [ ] Question restated verbatim from the brief
- [ ] Spike scaffolded as its own module under `poc/{slug}/`
- [ ] Spike **executed**, with real output captured
- [ ] Verdict reached against the brief's stated success criteria
- [ ] `poc-report.md` complete, with verbatim evidence and explicit non-coverage
- [ ] `findings.md` updated during the work
- [ ] Any skipped phase POC justified in `decisions.md` with a specific, checkable reason
- [ ] Report presented at a gate and explicitly approved

## Next

- **Confirmed**, project-level → `atom-plan`
- **Confirmed**, phase-level → `atom-spec`
- **Refuted** → `atom-discover`
- **Inconclusive** → sharpen the question, respike
