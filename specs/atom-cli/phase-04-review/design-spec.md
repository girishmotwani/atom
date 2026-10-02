# Design Spec — Phase 4: `atom review`

**Status.** APPROVED — Q1–Q4 resolved at the developer gate as P4-2 … P4-5.
**Behaviours.** B103–B137.
**Evidence.** [`poc-report.md`](poc-report.md) (C1–C9, D6–D10) and the agreement
analysis in `poc/review-json/analyse_agreement.py`.
**Decisions.** [`decisions.md`](decisions.md) — P4-1 … P4-5 and agent decisions A1–A6.

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
nothing in the output would indicate it. This was put to the developer as **Q1** and
answered by **P4-2**: each model is called three times, and repetition frequency becomes
the confidence signal the single-call design could not produce.

---

## Scope

**In.** Diff acquisition, model invocation, extraction, schema validation, merging
across models, a markdown report, exit-code semantics.

**Out.** Posting to GitHub (Phase 5). Applying fixes. Reviewing anything that is not a
diff. Choosing which models a developer has access to.

---

## The Pipeline

```
 toolchain ──▶ diff source ──▶ call each model, N runs each (parallel) ──▶ extract ──▶ validate
                                                                                     │
                                    report ◀── rank ◀── merge across models ◀────────┘
```

Each stage is separately testable, and the boundary between *extract* and *validate*
matters: extraction is deterministic normalisation, validation is a contract check.
Conflating them is what would let a silently-wrong payload through.

### Toolchain preflight

**B138.** Unless `--skip-toolchain` is passed, `atom review` runs the required
`atom check` gates with the race detector enabled before calling any model. A required
gate failure raises a review-blocking error, exits with the check-failed code in the
CLI, and prints the gate output. A review of code that does not compile, does not vet,
is not formatted, fails tests, or has an observed race is premature; spending model
calls there is exactly the waste this feature removes.

**B139.** The review preflight also runs three advisory gates: `staticcheck ./...`,
`errcheck ./...`, and `govulncheck ./...`. They are not required and never fail the
check. A missing advisory tool is reported as skipped, not failed. A non-zero advisory
exit is a warning whose details are preserved, because the output is evidence for the
review prompt and report.

**B140.** Toolchain evidence is inserted into the review prompt before the JSON-output
instructions without changing any existing sentence in the measured prompt. An empty
toolchain substitution reproduces the old prompt byte for byte.

**B141.** The prompt excludes only the mechanical categories whose tool actually ran
and passed. For example, ignored error returns are excluded only when `errcheck` passed;
if `errcheck` was skipped, models must still look for ignored errors. If the
toolchain did not run because the directory is not a Go module, or because
`--skip-toolchain` was passed, the prompt says nothing is excluded.

**B142.** The markdown review report records the toolchain verdicts in a compact
section so a saved report shows what the models were told not to re-report.

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

**B106a.** The **whole diff goes in a single call**. There is no per-file chunking. Per
P4-4, cross-file context is where some of the most valuable findings live — a caller that
no longer matches its callee cannot be seen one file at a time — and the reason this is
affordable is that Atom breaks work into phases before code is written, so a diff
reaching `atom review` should already be small.

**B106b.** That safety argument is an assumption about *how the framework is used*, and
the tool does not enforce it. So the report states the **size of the reviewed diff** in
lines and files. No limit is imposed and nothing is truncated: per A6, inventing a
threshold would mean picking a number nobody has measured (D8). A developer looking at a
thin review of a 2,000-line diff can at least see a plausible reason.

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

**B111.** Calls run in parallel, bounded by a concurrency limit that **defaults to 4**.
Per C6, four concurrent calls showed no rate limiting and no measurable interference.
Per A4 the default stays at the measured figure rather than being raised to 6 to make
B132's six calls finish in one wave — six is unmeasured, and choosing a number for tidy
arithmetic over evidence is the move this phase exists to refuse. The cost is two waves,
roughly 60 seconds rather than 30.

**B112.** Each call has a timeout. A timed-out call is a **recorded outcome**, not an
exception — it appears in the report as a model that did not answer.

### Repetition

**B132.** Each model is called **3 times by default**, overridable with `--runs`. Per
P4-2 this is forced by the stability measurement: `claude-haiku-4.5`'s best finding
appeared in 13 of 20 runs, so a single call to it omits real defects about a third of the
time and the output cannot say so. Repetition turns that invisible failure into a visible
confidence number.

**B133.** Runs of the same model are **identical calls** — same prompt, same diff, no
injected variation. The variation being measured belongs to the model. Perturbing the
prompt between runs would measure something else entirely and make B121's counts
meaningless.

**B134.** Each run's outcome is tracked individually, and the report states **how many
runs of each model completed**. B121's confidence signal is a fraction; a review that
quietly shrinks the denominator presents a degraded signal as an intact one.

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

> **This is the weakest behaviour in the spec.** It never happened in 40 calls, so by
> B114's own reasoning it should not exist. It is kept only because its failure mode is
> loud and bounded — at worst it rejects a finding that shows up as rejected — where the
> bracket-scan fallback's failure mode is silent. Recorded as **A2** so it can be struck.

---

## The Merge Model

This is the part the evidence changed most. Every behaviour in it is derived from the
agreement analysis rather than from intuition about how findings ought to combine.

### Identity — when are two findings the same finding?

**B118.** Findings are grouped by `file`, then by proximity of `line`, not by exact
line equality. The evidence shows the same defect reported at line 36 and line 37 by
the *same model* on different runs, and Haiku's lines 34–35 sitting within three of
gpt-5.4's line 37. Exact matching would report one defect as several.

**B119.** The proximity window **defaults to 3 lines** and is configurable, because the
window trades two opposite errors against each other: too wide merges two genuinely
different defects on adjacent lines into one; too narrow reports one defect repeatedly.
Neither error is detectable from the output. Per P4-5 the default of 3 is derived from
the near misses observed in **one fixture diff** — it is honest provenance, not a tuned
value.

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

**B131.** Partial reviews are marked as partial in both text and JSON output.

### Exit codes

**B135.** `atom review` reuses the exit codes established in Phases 1–3 rather than
inventing a scheme:

| Code | Constant | Meaning |
|---|---|---|
| 0 | `EXIT_PASSED` | The review completed. Every run of every model answered. **Findings do not change this** — `review` reports, it does not judge. |
| 1 | `EXIT_CHECK_FAILED` | The review did not complete: a run failed or timed out, no model returned anything usable (B130), or the diff could not be obtained. |
| 2 | `EXIT_USAGE_ERROR` | No diff source given (B104), or an invalid argument. |

**B136.** Per P4-3, a **partial review exits non-zero** even though a report was
produced. The reasoning is about noticing: a CI job where one model fails on every run
would otherwise stay green forever while nobody reads the banner.

**B137.** Per A5, a single failed *run* is enough to make the review partial — not only
the total failure of a model. B132 makes run count the denominator of the confidence
signal, so a missing run degrades the headline output of the phase. This is deliberately
strict, it is the behaviour most likely to prove annoying in practice, and A5 records
both that risk and the alternative.

**Severity never affects the exit code.** Gating on it was considered and rejected
(P4-3): severity is measurably unstable (B123), and a build that fails for reasons the
developer cannot see is worse than no gate.

---

## Resolved At The Developer Gate

Four questions were put to the developer, each carrying a cost the developer bears and
the agent does not. All four are answered; the full reasoning is in
[`decisions.md`](decisions.md).

| # | Question | Answer | Recorded as |
|---|---|---|---|
| Q1 | Once per model, or several times? | **3 runs per model**, `--runs` to override | P4-2 → B132–B134 |
| Q2 | Does `atom review` exit non-zero on findings? | **No.** 0 unless the tool failed — and a **partial review counts as failed** | P4-3 → B135–B137 |
| Q3 | Whole diff, or one call per file? | **Whole diff, one call.** Phase decomposition is what keeps diffs small | P4-4 → B106a, B106b |
| Q4 | How wide is the proximity window? | **Default 3 lines**, configurable | P4-5 → B119 |

Two of these went beyond picking an offered option:

- **Q2 was answered in two parts.** The developer's rule — *0 unless the tool failed* —
  left a seam in the middle: a partial review produces a real report while missing half
  the evidence. Asked separately, the developer closed it toward non-zero, on the grounds
  that a CI job silently losing a model every run would stay green forever.
- **Q3 was answered with a methodology argument rather than a technical one.** The spec
  had framed it as measurable and unmeasured. The developer's position is that it is
  neither: phases exist precisely so diffs stay small enough for one call. That is an
  assumption about how the framework is used, so B106b makes diff size visible rather than
  letting the assumption fail quietly, and D8 stays open.

---

## What This Phase Does Not Settle

- **D6 — review quality.** Agreement predicted the real defects on one fixture where
  the defects were planted by the person evaluating the result. That is suggestive, not
  conclusive. The Phase 4 **gate** settles this by running `atom review` over the Phase
  1 diff and triaging the findings.
- **D8 — large diffs.** Untested. P4-4 sends the whole diff in one call on the grounds
  that phase decomposition keeps diffs small; nobody has measured where that stops being
  true. B106b makes the size visible instead of guessing at a limit.
- **D10 — non-Windows behaviour.** Consistent with D2 from Phase 3.
- **Whether two models are enough.** Three would give a majority rather than a tie.
  Unmeasured.
- **D11 — cost.** Nobody has measured what a review costs in tokens or credits, and
  P4-2 tripled the call count, so the question is now three times as sharp.
- **Whether A5 is too strict.** Failing the whole review because one run of six timed
  out is the behaviour most likely to irritate in daily use. It needs real timeout-rate
  data, which does not exist yet.

---

## Size

Roughly 400 lines of production Python, larger than the plan's 350 because P4-2's
repetition and B121's agreement tracking add a layer the plan did not anticipate.

---

## Amended after the Phase 4 gate review (A5 revised, A19, A20)

These amendments replace the run-classification described above. See `decisions.md`
A5 (revised) for the measurements that drove them.

**B130 (amended).** "No usable response" means no run produced a reply Atom could *read*.
A reply refused by the B117 file guard was read, so a review consisting only of overruled
replies is reported as a review that happened and found nothing in scope — not as an
infrastructure failure.

**B131 (amended).** A review is partial when any run produced no readable reply. This
covers a run that never completed *and* a run that completed with an empty or unparseable
reply. It deliberately does not cover a reply the file guard overruled.

**B131a (new).** Every run belongs to exactly one of three categories — answered,
overruled, silent. They are disjoint by construction: a run that contributed any in-scope
finding is answered, whatever else its reply contained.

**B131b (new).** The agreement denominator for a model is its count of *answered* runs.
Overruled and silent runs leave the denominator.

**B131c (new).** Every run counted in the partial banner is named in a section above it.
The banner does not refer the reader to stderr, because a silent run produces no stderr
detail.

---

## Amended after the Phase 4 gate discussion

**B122 (amended).** Corroboration is reported when two distinct models reported the **same
line**, not merely the same merged group. Proximity grouping is intentionally loose
(B118), so a group can hold unrelated defects a line apart; counting models across the
group reports an agreement neither model expressed.

`MergedFinding.is_corroborated` buckets `messages` by `line` and is true when any single
line drew more than one distinct model.

**B122a (new).** `model_count` and the per-model agreement fractions are unchanged: they
continue to report every model that contributed to the entry. Narrowing corroboration must
not hide who spoke.

**B120 (unchanged, re-confirmed).** Every contributing message stays visible, so a reader
of an over-merged entry still sees both problems described even though the entry is no
longer marked corroborated.

**B122b (new, A22).** `has_nearby_multi_model_reports` is true when more than one distinct
model contributed to a merged entry but no single line drew two models. It is disjoint from
`is_corroborated` by construction: it returns false whenever corroboration is claimed.

Rendered as a plain statement rather than a verdict, because the data cannot distinguish
one defect described a line apart from two unrelated defects a line apart:

    Several models reported problems in this group, but on different lines,
    so this is not recorded as agreement.

Carried in the JSON payload as `has_nearby_multi_model_reports`. This field's addition is
additive on its own, but it ships alongside A21's narrowing of `is_corroborated`, so the
review contract does move — see B126 and `REVIEW_SCHEMA_VERSION` = 2.

**B126 (amended, A23).** Each report kind carries its own schema version constant rather
than sharing one. `REVIEW_SCHEMA_VERSION` is **2**, recording A21's narrowing of
`is_corroborated`; check, spike, spike-list and status remain at 1.

**Corrects** the B122b note above, which originally read "the addition is additive, so
`SCHEMA_VERSION` is unchanged". That sentence has been fixed in place rather than only
superseded here: a false statement left standing with a correction forty lines later still
reads as current to anyone who stops at the first one. The original wording and how it
happened are recorded in Finding 26.

That assessment covered
only the new field and missed that A21, in the same change, altered an existing field's
meaning.

**The rule.** Adding a field is not a bump. Changing what an existing field answers for the
same input is.
