# Design Spec — Phase 4: `atom review`

**Status.** DRAFT — open questions Q1–Q4 await developer review. Not approved.
**Behaviours.** B103 onward.
**Evidence.** [`poc-report.md`](poc-report.md) (C1–C9, D6–D10) and the agreement
analysis in `poc/review-json/analyse_agreement.py`.

---

## Purpose

`atom review` sends a diff to two or more models and merges what comes back into one
report a developer can act on.

It exists because a single model reviewing a diff is a single opinion, and opinions
from a text generator vary. The premise of the phase is that **where independent
models agree, the finding is more likely to be real** — and the evidence below
supports that premise more strongly than expected.

---

## Evidence Base

Two measurements underpin this design. Both are re-runnable from committed data
without calling a model: `python poc/review-json/spike.py --analyse` and
`python poc/review-json/analyse_agreement.py`.

### From the spike (40 calls)

Compliance is **deterministic per model, not a rate**. `gpt-5.4` returned bare
schema-valid JSON 20/20; `claude-haiku-4.5` wrapped it in a markdown fence 20/20.
Zero schema violations of any other kind, zero truncations. See C1–C9.

### From the agreement analysis (the same 40 responses, re-read)

This was run specifically because D7 said deduplication was unmeasured, and writing an
unmeasured merge strategy into a spec is how Phase 3's recovery-path bug got in.

**Models are not equally stable when asked the identical question repeatedly:**

| model | distinct (file, line) pairs over 20 runs | most-reported pair | findings per run |
|---|---|---|---|
| `gpt-5.4` | 5 | line 44 — **20/20**, line 24 — **20/20** | 3–5, mean 4.0 |
| `claude-haiku-4.5` | 12 | line 44 — **13/20 (65%)** | 3–6, mean 4.2 |

**Cross-model agreement is a precision signal.** Four (file, line) pairs were reported
by both models — 24, 36, 44, 45. Those four are exactly the four real defects in the
fixture: the unguarded map read in `Lookup`, the missing stock check in `Reserve`, the
ignored `os.Create` error, and the unlocked map iteration in `Export`. Every one of
Haiku's eight solo findings was reported in 5 or fewer runs out of 20.

**Severity is unstable, within a model as well as across.** On line 44, `gpt-5.4` said
`high` 18 times and `medium` twice; `claude-haiku-4.5` said `critical` 7, `high` 10,
`medium` 1. There is no single authoritative severity to carry into a report.

**Near misses are real.** `claude-haiku-4.5` lines 34 and 35 sit within three lines of
`gpt-5.4` line 37; `gpt-5.4` itself reported the same underlying problem at both line
36 and line 37 across different runs. An exact `(file, line)` merge would present these
as separate findings.

### What this evidence overturns

The phase plan says "run a diff past two or more different models and merge the
findings". That sentence assumes **one call per model**. The stability data refutes the
assumption: with a model whose best finding appears in 65% of runs, a single call
produces a report that silently omits real defects about a third of the time, and
nothing in the output would indicate it. This is the subject of **Q1**.

---

## Scope

**In.** Diff acquisition, model invocation, extraction, schema validation, merging
across models, a markdown report, exit-code semantics.

**Out.** Posting to GitHub (Phase 5). Applying fixes. Reviewing anything that is not a
diff. Choosing which models a developer has access to.

---

## The Pipeline

```
 diff source ──▶ chunk ──▶ call each model (parallel) ──▶ extract ──▶ validate
                                                                        │
                       report ◀── rank ◀── merge across models ◀────────┘
```

Each stage is separately testable, and the boundary between *extract* and *validate*
matters: extraction is deterministic normalisation, validation is a contract check.
Conflating them is what would let a silently-wrong payload through.

---

## Diff Acquisition

**B103.** `atom review` reviews one of three sources, selected explicitly:
`--staged` (the index), `--branch <base>` (this branch against a base ref), or
`--working` (unstaged changes).

**B104.** With no source given, `atom review` **fails with a usage error** naming the
three options rather than guessing. Reviewing the wrong thing silently wastes minutes
of model time and produces a confident report about code the developer did not mean.

**B105.** An empty diff is not an error. `atom review` reports "nothing to review" and
exits 0. A CI job that runs `atom review` on a docs-only commit should not fail.

**B106.** The diff is captured **once** and reused for every model call, so that all
models review byte-identical input. Re-running `git diff` per model would allow the
working tree to change underneath the review.

---

## Model Invocation

Each behaviour here is forced by a measurement, not chosen for taste.

**B107.** Calls use `--silent`, not `--output-format json`. Per C1 the two are
identical at the findings level, and the envelope costs 33KB of event stream carrying
a schema Atom does not control.

**B108.** Every call passes `--no-custom-instructions`. Per C5, without it the CLI
loads `AGENTS.md` from the working directory and the review becomes a property of the
repository being reviewed.

**B109.** Every call passes `--disable-builtin-mcps` and disables ambient MCP servers.
Per C4 this took a call from **84 seconds to roughly 30**. MCP servers contribute
nothing to a review whose entire input is in the prompt.

**B110.** Model availability is probed **before** any review call is made. Per C7,
`claude-sonnet-4.5` and `gemini-2.5-pro` are rejected on hardware where `gpt-5.4` and
`claude-haiku-4.5` are accepted; availability is an account property. An unavailable
model fails in about two seconds with `Model "x" from --model flag is not available.`,
so the check is cheap and the alternative is discovering it after the other model has
already run for a minute.

**B111.** Calls run in parallel, bounded by a concurrency limit. Per C6, four
concurrent calls showed no rate limiting and no measurable interference.

**B112.** Each call has a timeout. A timed-out call is a **recorded outcome**, not an
exception — it appears in the report as a model that did not answer.

---

## Extraction and Validation

**B113.** Extraction strips a surrounding markdown fence before parsing. Per C2 this is
mandatory: one of the two available model families fences unconditionally, 20/20, while
being explicitly instructed not to.

**B114.** Extraction does **not** scan for the outermost brackets as a fallback. Per C3
that path never executed in 40 calls, so shipping it would mean shipping behaviour
nobody has observed, and its failure mode is silently capturing the wrong span.

**B115.** A response that is not schema-valid after fence-stripping is a **loud
failure** for that call — recorded, surfaced in the report, never silently dropped.
Per C9, a discarded response halves the review while the report still looks complete.

**B116.** Validation checks required fields, `severity` within the allowed set, and an
integer `line`. Per C8 nothing failed this in 40 calls; it stays because the
alternative to a clear message is a crash inside the merge step.

**B117.** A finding whose `file` is not present in the reviewed diff is rejected. A
model naming a file it was not shown is describing something it cannot have seen.

---

## The Merge Model

This is the part the evidence changed most, and the part with the most open questions.

### Identity — when are two findings the same finding?

**B118.** Findings are grouped by `file`, then by proximity of `line`, not by exact
line equality. The evidence shows the same defect reported at line 36 and line 37 by
the *same model* on different runs, and Haiku's lines 34–35 sitting within three of
gpt-5.4's line 37. Exact matching would report one defect as several.

**B119.** The proximity window is **configurable with a small default**, because the
window trades two opposite errors against each other: too wide merges two genuinely
different defects on adjacent lines into one; too narrow reports one defect repeatedly.
Neither error is detectable from the output. See **Q4**.

**B120.** Merging never discards a message. A merged finding carries every contributing
message, attributed to the model that produced it, so a developer can see that two
models described the same line differently rather than being shown one and trusting it.

### Agreement — the signal worth surfacing

**B121.** Every merged finding records **which models reported it** and **how many of
that model's runs reported it**. On the measured data this cleanly separates the four
real defects (reported by both models) from the eight noise findings (one model, ≤5
runs in 20). This is the single most useful output of merging and it is lost if the
report is a flat list.

**B122.** Agreement is **reported, never used to silently suppress**. A finding from one
model only is still shown; it is shown as lower-confidence. Suppressing it would mean
the tool quietly decides a real bug is noise, and the evidence base for that decision is
one fixture diff.

### Severity — not authoritative

**B123.** Severity is presented as **what the models said**, not as a single verdict.
Where they disagree the report shows the disagreement. The measurement is unambiguous:
the same model gave the same line two different severities across runs, and the two
models disagreed with each other on all four agreed lines.

**B124.** Ordering uses the **highest** severity any model assigned, so the most alarming
claim is never buried. Ordering is a presentation choice; it does not overwrite B123.

---

## Output

**B125.** The default output is a markdown report: findings grouped by file, ordered by
severity, each showing agreement and per-model messages.

**B126.** `--json` emits the merged findings as a machine contract, consistent with
`atom status` in Phase 3.

**B127.** The report states **what was reviewed and by which models**, including any
model that failed or timed out. A report that does not say it is missing a model's
opinion is misleading in exactly the way this phase exists to avoid.

**B128.** Following P3-5 from Phase 3: the report goes to **stdout**, operational
problems go to **stderr**, neither duplicated. `atom review > review.md` must produce a
clean report file while the developer still sees that a model failed.

---

## Failure Handling

**B129.** A call that fails, times out, or returns an unusable response does not abort
the review. It is recorded and reported.

**B130.** If **no** model returned a usable response, `atom review` fails loudly. An
empty report is indistinguishable from a clean review, and that confusion is dangerous.

**B131.** Partial reviews are marked as partial in both text and JSON output — see
**Q2** for whether a partial review should also change the exit code.

---

## Open Questions For Developer Review

These are genuinely open. Each has a cost the developer bears and I do not.

### Q1 — Does each model get called once, or several times?

The stability data makes this the most consequential question in the phase.

| Approach | Cost | Consequence |
|---|---|---|
| **Once per model** | ~2 calls, ~30s | Matches the plan. With a 65%-stable model, real defects are missed about a third of the time, and the report cannot tell you it happened. |
| **N times per model** | 2N calls, ~30s wall-clock if parallel | Repetition frequency becomes a confidence signal. On the measured data this is what separates signal from noise. Costs N× the model spend. |
| **Once, but only stable models** | ~2 calls | Requires knowing which models are stable, which requires measuring them, which is the N-times approach anyway. |

My inclination is N=3 as a default with `--runs` to override, because the measurement
says a single run of the weaker model is close to a coin toss on its own findings. But
this is a direct spend decision and it is yours.

### Q2 — Does `atom review` exit non-zero when it finds problems?

- **Always 0 unless the tool itself failed.** `review` reports; it does not judge.
  Composes cleanly; useless as a CI gate on its own.
- **Non-zero at or above a severity threshold.** Usable as a gate. But severity is
  measurably unstable (B123) — gating on an unstable signal makes builds flaky.
- **Configurable, defaulting to 0.**

The severity instability is the thing I would weigh most heavily here, and it is an
argument I only have because the spike was run twenty times per cell rather than once.

### Q3 — Whole diff in one call, or one call per file?

The spike used a 48-line single-file diff, so this is **unmeasured** (D8). Per-file
bounds context and parallelises; whole-diff preserves cross-file context, which is
where some of the most valuable findings live — a caller that no longer matches its
callee. Guessing here would be exactly the move that "justifiably skipped" made twice.

If this matters to you, the honest answer is a second short spike rather than a
decision in this document.

### Q4 — How wide is the proximity window, and who sets it?

Both failure modes are silent (B119). I propose a default of 3 lines based on the
observed near misses, with an override — but that default is derived from one fixture
diff and should be labelled as such rather than presented as a tuned value.

---

## What This Phase Does Not Settle

- **D6 — review quality.** Agreement predicted the real defects on one fixture where
  the defects were planted by the person evaluating the result. That is suggestive, not
  conclusive. The Phase 4 **gate** settles this by running `atom review` over the Phase
  1 diff and triaging the findings.
- **D8 — large diffs.** Untested. See Q3.
- **D10 — non-Windows behaviour.** Consistent with D2 from Phase 3.
- **Whether two models are enough.** Three would give a majority rather than a tie.
  Unmeasured.
- **Cost.** Nobody has measured what a review costs in tokens or credits, and Q1 makes
  that question sharper.

---

## Size

Roughly 400 lines of production Python, larger than the plan's 350 because Q1's
repetition and B121's agreement tracking add a layer the plan did not anticipate.
