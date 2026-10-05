# The Atom workflow

A walkthrough of what actually happens when you hand Atom a piece of work, what you
are expected to do at each point, and what ends up on disk.

For the skill reference table and installation, see the [README](../README.md). This
document is the narrative version — read it once before your first run.

---

## The idea in one paragraph

Atom never lets an agent design or implement something before it has **run a program
that proves the risky part works**. Every stage produces an artifact on disk, and
every stage ends by stopping and asking you a question. You are not reviewing a
finished result at the end; you are steering at roughly eight points along the way.

---

## The flow

```
  your problem statement
        │
        ▼
  discover ──◆── poc ──◆── plan ──◆         project level: what are we doing?
        │                                    one throwaway spike proves the
        └── refuted ──┘                      riskiest assumption before planning

        then, for each phase in the plan, in order:

  ┌──────────────────────────────────────────────────────┐
  │  poc ──◆── spec ──◆── tdd ──◆── review ── ship       │
  │   │                                                   │
  │   └── refuted ──▶ back to plan                        │
  └──────────────────────────────────────────────────────┘

  ◆ = gate. The agent presents what it did, stops, and waits for you.
```

---

## What a gate is

A gate is a full stop. The agent shows you what it produced, where it is, what it
decided and why, and asks **one** specific question. Then it ends its turn.

Three things worth knowing:

**Approval is narrow.** Approving the POC Brief authorises building *that spike* to
answer *that question*. It does not authorise designing, planning, or writing
production code. Approving the phase plan authorises **phase 1 only** — later phases
are gated individually, because phase 1 routinely changes them.

**"Looks good" is a real answer.** So is "no, do it differently", and so is "why did
you rule out X?". Gates are cheap. The expensive thing is discovering at ship time
that the agent has been building against a premise you would have corrected in one
sentence at the start.

**An interrupted gate was never approved.** If a session dies mid-gate, work resumes
*at* that gate, never past it.

---

## Step by step

### 0. Setup

`/atom:init` onboards the repository: detects your Go toolchain, creates `.atom/`, and
records the baseline before changing anything. It runs `atom check --no-race` on the
**untouched** tree, skipping race detection only for this initial baseline; this keeps
a pre-existing failure from being mistaken for one the pipeline caused. Final
verification still uses full `atom check` with race detection.

Work happens on a branch, not on `main`.

### 1. Discover — turning a problem into a question

**The agent reads your repository before it asks you anything.** Module layout,
dependencies, build and test commands, conventions already in use, and whether
something already attempts to solve this. Any question the code could have answered is
a question it should not be spending your attention on.

Then it interviews you — **one question at a time**, letting each answer shape the
next. It is working toward: what becomes possible that isn't today, who calls this,
concrete numbers for scale, fixed constraints, what you're unsure about, how you'll
judge it done, and what you explicitly do *not* want.

The question that matters most is some form of:

> **"What part of this are you least sure will work?"**

You usually know exactly where the risk is, and that answer normally *is* the POC
question.

**If your repository contradicts something you said, the agent tells you.** Quietly
designing around a wrong premise wastes the entire pipeline.

**Output:** `specs/{project}/poc-brief.md` — one falsifiable question, plus an explicit
statement of what the spike will *not* cover. Also `findings.md` and `decisions.md`,
created now and updated as work proceeds, not reconstructed at the end.

> **The falsifiability test.** The brief's question must be answerable **no** by
> running a program. "How fast is the current implementation?" fails — every run
> returns some number. "Does a lookup stay under 50 µs at the 99th percentile at
> 10,000 requests/sec with the cache 90% full?" passes, because a run can come back
> and say no. Sharpening a vague goal into a question that can fail is most of the
> value of this step.

### 2. POC — proving it before believing it

A **throwaway** Go spike, scaffolded as its own module under `poc/{slug}/` so it
cannot entangle itself with your production code. The agent builds it, **runs** it,
and records what actually happened.

**Output:** `specs/{project}/poc-report.md`, containing verbatim program output — the
real numbers, not a summary of them — and a verdict of Confirmed or Refuted.

**Refuted is a successful outcome.** It means you learned the approach doesn't work
for the price of a spike instead of the price of a release. The pipeline loops back to
discover and re-forms the plan around what you now know.

The spike stays in `poc/{slug}/`. It is documentation now, and it is frequently the
measuring instrument for every phase that follows.

### 3. Plan — breaking proven work into phases

Now that something has been *demonstrated*, the work is split into phases that are
ordered and independently shippable, each sized so it can be reviewed and merged on
its own.

**Output:** `specs/{project}/phase-plan.md`, with one directory per phase:
`specs/{project}/phase-01-{slug}/`, `phase-02-{slug}/`, and so on.

Phases run **strictly in order**. What phase 1 teaches usually changes phase 2, and
running them in parallel throws that away. Between phases the agent asks whether the
plan still holds — it often doesn't, and finding out costs one question.

### 4. Per phase — poc, spec, tdd, review, ship

| Step | What happens | Lands at |
|---|---|---|
| **poc** | Spike this phase's specific risk | `phase-NN-{slug}/poc-report.md` |
| **spec** | High-level design, grounded in that evidence | `phase-NN-{slug}/design-spec.md` |
| **tdd** | Red → green → refactor, against the approved spec | code + `test-spec.md` |
| **review** | Multi-model review, by models other than the author | `phase-NN-{slug}/review.md` |
| **ship** | Commit and open a pull request | — |

Ordering is enforced: the spec is never written before the POC, and TDD never starts
before the spec is approved. A phase POC can be skipped only with a **specific,
recorded justification** — not because it felt unnecessary at the time.

Review deliberately uses different models from the one that wrote the code, because a
model reviewing its own output mostly agrees with itself. Every fix re-runs
`atom check`; every deferral and rejection is recorded rather than dropped.

`specs/` and `poc/` are committed **alongside the code**, so the reasoning ships with
the result.

Then `atom phase done NN`, and on to the next phase.

---

## A worked example

You have an existing service and want to improve the performance of one of its core
algorithms, starting from code review plus a quick harness.

**What Atom does with that:**

1. **Discover** reads the algorithm and its tests, then asks what "performance"
   actually means here — latency, throughput, memory, behaviour under saturation —
   and at what scale. Your stated goal, *"benchmark it and find improvements"*, is not
   yet falsifiable, so it gets sharpened into a threshold a run can fail.

2. **POC** builds the harness and runs it. You get real numbers, in the report,
   verbatim.

3. **Plan** identifies improvements **from what the benchmark showed** — not from what
   looked slow while reading the code. These are routinely different, which is the
   whole point of measuring first. Each improvement becomes a phase.

4. **Each phase** re-spikes on that same harness to prove the optimisation actually
   helps *before* designing it, then specs, then TDD, then review, then ship.

Note what happened to your original request: it was two deliverables — measure, then
improve — and the pipeline separated them. What Atom resists is committing to specific
improvements before the measurement exists, because a code-review intuition about the
bottleneck is a hypothesis, not evidence.

---

## What you have at the end

- Working, reviewed, tested code, merged in independently shippable pieces
- A spike per risk, still runnable, showing what was proven and what was refuted
- A design spec per phase, reconciled against what was actually built
- `findings.md` — everything discovered that didn't fit anywhere else
- `decisions.md` — every point where the agent deviated from instructions, and why
- A verbatim `atom check` result on the final state

The last two exist even when empty, saying so explicitly. An artifact that is missing
tells you nothing; one that says "No deviations from instructions" tells you the check
was actually performed.

---

## Running it

Plain prose works:

> *"Take this from problem statement to shipped phases."*

The slash command is the certain path when you want no ambiguity about which skill
runs:

```
/atom:build
```

For a single step rather than the whole pipeline, invoke that skill directly —
`/atom:poc`, `/atom:review`, and so on.

## Resuming

State lives in `.atom/state.json`.

```bash
atom status
```

Resume from the **last completed** step. Verify the artifacts on disk match what the
state file claims before trusting it — the files are the truth, the state file is an
index.

---

## The two rules worth remembering

**Nothing gets designed before something has been run.** Not because spikes are
enjoyable, but because the expensive failures are the ones discovered after the design
is committed to.

**You are a participant, not an approver at the end.** The gates exist so your
knowledge enters the work while it is still cheap to change.
