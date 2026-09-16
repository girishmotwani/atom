# POC Report — Phase 4: getting structured review findings out of a model

**Ran.** 2026-09-16. 40 calls, all completed, none timed out.
**Harness.** `poc/review-json/spike.py`, `poc/review-json/analyse_salvage.py`.
**Evidence.** Every raw response is saved under `poc/review-json/raw/`. Re-score without
re-calling: `python poc/review-json/spike.py --analyse`.

> **This file is the authoritative source for every Phase 4 number.** Do not cite a
> figure from memory. Phase 3 produced a write-up that reversed the sign of its own
> measurement, and only a disagreement with another document caught it.

---

## Results

Percentages are per call. **strict** means the reply parsed as schema-valid JSON with
no processing at all; **salvaged** means after the extractor looked for a payload.

| cell | n | transport valid | strict | salvaged |
|---|---|---|---|---|
| `envelope` / gpt-5.4 | 10 | 100% | **100%** | 100% |
| `plain` / gpt-5.4 | 10 | 100% | **100%** | 100% |
| `envelope` / claude-haiku-4.5 | 10 | 100% | **0%** | 100% |
| `plain` / claude-haiku-4.5 | 10 | 100% | **0%** | 100% |

### How the replies had to be handled

The headline "100% salvaged" hides the thing that matters, so it was broken down
separately. Stripping a fence is a delimiter operation; scanning for the outermost
brackets is a heuristic that can capture the wrong span.

| cell | n | handling required |
|---|---|---|
| `envelope` / gpt-5.4 | 10 | clean — no processing needed |
| `plain` / gpt-5.4 | 10 | clean — no processing needed |
| `envelope` / claude-haiku-4.5 | 10 | fenced only — deterministic strip, **no prose outside the fence** |
| `plain` / claude-haiku-4.5 | 10 | fenced only — deterministic strip, **no prose outside the fence** |

**The bracket-scan heuristic never fired.** In 40 calls it was never needed.

### What did not go wrong, in 40 calls

Worth stating explicitly, because it is the most surprising part of the result:

- zero missing fields
- zero `severity` values outside the allowed set
- zero non-integer `line` values
- zero truncations, zero timeouts, zero non-zero exit codes
- zero malformed transport lines

**The only deviation observed in the entire experiment was a markdown fence.**

---

## Predictions, scored

Recorded in `poc-brief.md` before the spike ran.

| # | Prediction | Outcome |
|---|---|---|
| P1 | Transport valid on 100% of completed calls | **Confirmed.** 40/40. |
| P2 | Schema-valid rate materially below transport; 70–90% for the plain contract | **Refuted.** It is not a rate at all. It is 100% or 0%, fixed by model. |
| P3 | Dominant failure will be prose or fences, not bad field values | **Confirmed, and more sharply than expected.** Fences were the *only* failure. |
| P4 | The two contracts will not differ much at the findings level | **Confirmed.** They are identical — 20/20 agreement per model. This was my lowest-confidence prediction. |
| P5 | The two models differ by more than 10 percentage points | **Confirmed, and badly understated.** They differ by 100 points. |
| P6 | At least one call in forty truncates or times out | **Refuted.** 40/40 completed cleanly. |

Two refutations. P2 is the important one: it refuted not just a number but the *shape*
of the answer, which is what forced the decision rule to be revisited.

---

## The decision rule was amended, after seeing the data

This needs stating plainly rather than being folded in quietly, because amending a
rule after seeing the result is exactly the move the rule existed to prevent.

**The rule, as fixed in advance:** below 80% strict, abandon the JSON contract. The
worst cell scored 0% strict. Read literally: abandon.

**Why it was put to the developer instead of applied.** The rule encoded an assumption
that the data refuted. It assumed unreliability is a *rate* — that a model complies on
some unpredictable fraction of calls, so you can never trust any single response. Under
that assumption, "repair" means guessing, and a design built on guessing is unsound.

What actually happens is not a rate. It is **deterministic per model**: one model
emits bare JSON every time, the other wraps it in a fence every time. There is nothing
probabilistic to defend against, and the "repair" is removing a delimiter whose
presence is unambiguous.

**Developer decision (P4-1).** Deterministic normalisation is part of *extraction*, not
*repair*. Fence-stripping does not count against the contract. The JSON contract holds.

**What would have made this rationalisation rather than reasoning.** If the fence had
appeared on only some of Haiku's calls; if there had been prose around it; if the
bracket-scan had been needed even once; or if any schema violation had occurred. None
of those happened. The amendment is recorded here so that a future reader can judge it
rather than inherit it.

---

## Binding consequences

These constrain the Phase 4 design. Each one is traceable to the data above.

**C1 — The two contracts are equivalent, so use the simpler one.** `--silent` and
`--output-format json` produced identical findings-level results, 20/20 per model. The
envelope costs 33KB of event stream for a 1KB answer and creates a dependency on an
event schema Atom does not control. `atom review` uses `--silent`.
*Tradeoff recorded:* the envelope carries structured metadata — model name, usage,
a terminal `result` event — that `--silent` does not. If Atom later needs to detect
truncation structurally rather than by exit code, this decision is the thing to revisit.

**C2 — The extractor must strip a markdown fence.** Deterministic, 20/20. Not optional:
one of the two available model families fences unconditionally, and it ignored an
explicit "no prose, nothing else" instruction while doing so.

**C3 — The bracket-scan heuristic must not ship untested.** It was never exercised in
40 calls, so shipping it would mean shipping code whose behaviour has never been
observed. Either cover it explicitly in tests with deliberately malformed input, or
leave it out and fail loudly. Untested salvage that silently captures the wrong span
is worse than no salvage.

**C4 — MCP servers must be disabled on every call.** With ambient MCP servers loaded, a
one-word reply took **84 seconds**. With `--disable-builtin-mcps` and the two ambient
servers disabled, a full diff review took **23–45 seconds**. The servers contribute
nothing to a review whose input is entirely in the prompt.

**C5 — `--no-custom-instructions` is mandatory.** Without it the CLI loads `AGENTS.md`
from the working directory. `atom review` would then produce different findings
depending on whose repository it ran in, and the spike would have measured this
repository rather than the models.

**C6 — Reviews must run in parallel.** At ~30s per call, two models over five files is
ten calls and five minutes sequentially. The spike ran four at a time with no rate
limiting and no measurable interference.

**C7 — Model availability must be probed, not assumed.** `claude-sonnet-4.5`,
`claude-sonnet-4` and `gemini-2.5-pro` were all rejected on this machine, while
`gpt-5.4`, `gpt-5.3-codex`, `gpt-5-mini`, `claude-haiku-4.5` and `auto` were accepted.
Availability is an account and version property, not a constant. An unavailable model
fails fast (~2s, exit 1, `Model "x" from --model flag is not available.`), so `atom
review` can and must check before starting a long run rather than failing at the end.

**C8 — Validation stays, even though nothing failed it.** Zero schema violations in 40
calls is evidence about two models on one diff with one prompt, not a guarantee. The
validator is cheap; removing it would mean a future violation is discovered by a
crash in the merge step instead of a clear message.

**C9 — Fail loudly on an unparseable response; do not drop it.** With two models
merging, a silently-discarded response halves the review while still producing a
confident-looking report. This mirrors the Phase 3 finding that silent loss is worse
than loud failure.

---

## Out of scope — recorded as debt, not answered

Named here because an unnamed gap becomes an assumed answer.

| # | Gap | Why it matters |
|---|---|---|
| D6 | **Review quality is unmeasured.** The spike scores parseability. A model returning four schema-valid hallucinations scores 100%. | Settled at the Phase 4 *gate*, by running `atom review` over the Phase 1 diff and triaging the findings — not by this spike. |
| D7 | **Deduplication is unmeasured.** Both models independently flagged the unguarded map read, in different words with different line numbers. Whether code can tell "same finding" from "different finding" is untested and is the second real risk in this phase. | Directly shapes the merge design. |
| D8 | **Large-diff behaviour is untested.** One 48-line diff. Context-limit behaviour, truncation and chunking are all unmeasured. | P6 predicted a truncation and got none — on a small diff. That is not evidence about large ones. |
| D9 | **Fence behaviour was observed under one prompt.** Haiku fenced 20/20 despite being told not to. Whether a differently-worded prompt changes that is unknown, and it does not need to be known: C2 handles both cases. | Low risk, recorded for completeness. |
| D10 | **Non-Windows behaviour is unmeasured**, consistent with D2 from Phase 3. | Still nobody has read the POSIX numbers CI produces. |

---

## Observation outside the measurement

Both models found real defects in the fixture diff: the unguarded map read in `Lookup`
racing `Reserve`, the ignored error from `os.Create`, the unclosed file handle, and the
missing check for insufficient stock in `Reserve`. They were planted, so this is not
evidence that review quality is good — it is only evidence that the pipeline carries
signal rather than noise. D6 remains open.
