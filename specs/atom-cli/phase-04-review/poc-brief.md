# POC Brief — Phase 4: getting structured review findings out of a model

**Status.** Written before the spike ran. Predictions below are recorded so the
spike can refute them.

---

## Why this spike exists

Phase 4 is the only phase whose plan entry has always said a POC is *mandatory*.
Every other phase claimed "no technical uncertainty" and was wrong twice, but this
one was never in doubt: `atom review` depends on a model doing something models are
not obliged to do.

`atom review` sends a diff to two or more models and merges what comes back. Merging
means code, and code needs structure — a list of findings with a file, a line, a
severity and a message. The prompt asks for that structure. Nothing enforces it. A
model is a text generator; producing valid JSON is a behaviour it usually exhibits,
not a guarantee it offers.

If the compliance rate is high, `atom review` is a parser. If it is low, `atom review`
needs a repair layer, or a different contract entirely — and that is a difference in
the *design*, not the implementation. It has to be known before the spec is written.

---

## The question

> Can a model be driven, through the Copilot CLI in non-interactive mode, to return
> review findings as schema-valid JSON reliably enough to merge programmatically —
> and what fraction of responses need repair?

Investigating the CLI surfaced a distinction the question did not anticipate, and it
splits the question in two.

`copilot --output-format json` emits **JSONL: one JSON object per line**. That is a
*transport envelope* produced by the CLI itself. It is not the review schema. The two
layers can fail independently:

- the envelope can be flawless while the findings inside it are wrapped in a markdown
  fence, prefixed with "Here are the issues I found:", or use a `severity` value that
  is not one of the four allowed;
- and a perfectly-formed findings block is worthless if the envelope truncates.

So the spike measures **two contracts**, not one:

| Contract | How findings are requested | How they are extracted |
|---|---|---|
| **A — envelope** | `--output-format json`, prompt asks for a findings array | parse JSONL, pull assistant content, parse findings |
| **B — fenced** | `--silent`, prompt asks for a fenced ```json block | locate the fence, parse what is inside |

Crossed with **two models**, that is four cells.

### What is measured in each cell

Per call, three independent outcomes, because conflating them would hide where the
failure actually is:

1. **Transport valid** — did the CLI's own output parse at all?
2. **Findings located** — was a candidate findings payload found in the response?
3. **Schema valid** — did it parse *and* satisfy the schema (required fields present,
   `severity` within the allowed set, `line` an integer)?

The headline rate is #3, since that is the only one that can be merged.

---

## Predictions

Recorded before running. Phase 3's spike had teeth only because P1–P5 were written
down first — two of them were refuted, and one of those refutations changed the design.

| # | Prediction | Confidence |
|---|---|---|
| P1 | The **transport** layer (contract A) will be valid JSONL on 100% of completed calls. It is program-generated framing, not model output. | High |
| P2 | The **schema-valid** rate will be materially below the transport rate — I expect 70–90% for contract B. Models habitually add preamble. | Medium |
| P3 | The dominant failure mode will be **surrounding prose or markdown fences**, not bad field values. Models comply with the *shape* and fail at the *boundary*. | Medium |
| P4 | The two contracts will **not** differ much at the findings level. The envelope changes framing, not the model's content behaviour. | Low — this is the one I most expect to be wrong |
| P5 | The two models will differ by **more than 10 percentage points**. Compliance is a training artefact and is not uniform across families. | Medium |
| P6 | At least one call in forty will **truncate or time out**, and the design will have to treat that as a normal outcome rather than an error. | Medium |

P4 is deliberately a low-confidence prediction. If `--output-format json` measurably
improves findings-level compliance, that is the single most useful thing this spike
could discover, and it would make contract A the obvious foundation.

---

## Decision rule — fixed in advance

Agreed with the developer **before the spike ran**, so that the data selects the
design rather than the design selecting its evidence.

| Schema-valid rate | Verdict | What Phase 4 then builds |
|---|---|---|
| **≥ 95%** | JSON contract holds | Parse it plainly. Fail loudly on the rare bad response. |
| **80% – 95%** | JSON contract needs help | Build an explicit repair layer — de-fence, retry, salvage. |
| **< 80%** | JSON contract abandoned | Line-oriented delimited format, which parses even when partly mangled. |

The rate that counts is **per call, before any repair**. Measuring after repair would
make the repair layer justify itself.

If the four cells straddle a cut-off, the **lowest** cell governs — `atom review` has
to work with whichever model the developer actually has, not the best one.

> **This rule was subsequently amended, on the record.** The data refuted the premise
> it rests on: compliance turned out to be deterministic per model rather than a rate.
> See "The decision rule was amended, after seeing the data" in
> [`poc-report.md`](poc-report.md) for what changed and why, including the conditions
> under which the amendment would have been rationalisation instead of reasoning.

---

## What this spike deliberately does not settle

Naming these matters as much as the measurement; an unnamed gap becomes an assumed
answer.

- **Whether the findings are any good.** This measures parseability, not review
  quality. A model returning four perfectly-schema-valid hallucinations scores 100%.
  Review quality is a Phase 4 *gate* concern — the Phase 1 diff run — not a spike one.
- **Whether two models' findings can be deduplicated.** Merge quality depends on
  findings agreeing about what a "same" finding is. Unmeasured, and it is the second
  risk in this phase.
- **Cost and latency.** Relevant to adoption, not to the design fork.
- **Behaviour on large diffs.** The spike uses one modest diff. Context-limit
  behaviour is untested and is recorded as debt.
- **Non-Windows behaviour.** Consistent with D2 from Phase 3; still nobody has read
  the POSIX numbers.

---

## Method

- **10 trials per cell, 40 calls total.** Enough to distinguish 100% from 90%; not
  enough to distinguish 93% from 95%. If a cell lands within a few points of a
  cut-off, that is itself a finding, and the honest response is more trials, not a
  confident verdict.
- **Every raw response is written to disk** before it is parsed. Analysis can then be
  re-run without re-calling the models, and every number in the report is traceable
  to a file. This is a direct response to finding #8 of Phase 3, where a measurement
  was cited from memory with its sign reversed.
- **The same diff and the same prompt for all four cells.** Only the contract and the
  model vary.
- **Failures are recorded, not retried.** A retried call would measure the retry.

## Success criterion

The spike succeeds if it produces a rate per cell and a verdict against the table
above — **including** a verdict that kills the JSON contract. All three outcomes are
successes. The only failure is an inconclusive result reported as a confident one.
