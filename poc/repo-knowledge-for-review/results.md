# POC Results: repository knowledge for reviewing an unfamiliar pull request

Claims were registered in [claims.md](claims.md), with each claim marked as
pre-registered or formed mid-experiment. Nothing here moves a threshold that
was set there.

**Subject.** One held-out pull request in a large internal Go service: a
networking control-plane component. 12 production files, 73 KB of unified diff
with 12 lines of context per hunk. Ground truth is the 24 comment threads its
human reviewers actually wrote.

**Sanitisation.** This report is written for an open-source repository. The
subject repository, its pull request identifiers, and the verbatim text of its
review comments are deliberately omitted. Human threads are referenced by local
index only, and their substance is paraphrased at the level of category. The
full unsanitised working set stays outside this repository.

**Design.** Three stages.

*Stage 1* — four reviewing arms over a 2x2: knowledge base present/absent by
checkout present/absent, one run each.

*Stage 2* — a replication, added after stage 1's result turned out to be
unsupportable: five independent runs each of two conditions (plain diff, and
diff plus retrieved knowledge), ten arms in total.

*Stage 3* — a second replication, of the one claim stage 2 left standing: five
independent runs of the checkout condition, scored against the five plain arms
on a thread category fixed in writing beforehand.

Every arm received identical review instructions apart from the input under
test. None could read the ground truth. Arms were scored in a single blind pass
per stage by an independent judge, anonymised with attribution fields stripped.

---

## Headline

**This report has been corrected twice, each time after a replication. Read
this section before any other.**

The first version led with: *the mined knowledge base halved review coverage*.
**Withdrawn.** The second version retained one positive claim — that a
repository checkout unlocks "reuse what already exists" feedback.
**Also withdrawn.** Neither was a transcription error; the numbers were real
each time. The experiment simply could not support the inferences drawn.

| Stage | Claim it produced | What replication did to it |
|---|---|---|
| 1 | Knowledge base halves coverage (6/24 → 3/24) | Same condition re-run five times: **2, 3, 3, 4, 6**. Effect was 3; noise is 4. |
| 2 | Checkout uniquely unlocks reuse feedback (3 of 3) | Checkout re-run five times: **1 of 15** category opportunities. |

**Nothing tested in this POC produced a detectable improvement in review
coverage.** Not a mined knowledge base, in bulk or retrieved form. Not a
repository checkout.

What actually survives measurement:

- **No detectable coverage effect from a knowledge base**, in either bulk or
  retrieved delivery (p = 0.183 on per-run coverage, p = 0.190 on pooled union).
- **No detectable coverage effect from a checkout**, on totals (p = 0.603) or
  on the reuse category it was predicted to unlock (1 hit in 5 runs, and a
  plain arm arguably matched the same thread).
- **One detectable effect in the entire study**: retrieval makes the reviewer's
  output volume **3.25x more consistent** run to run (p = 0.008). It does not
  make it find more.
- **The instruction wording effect** — an 8x swing in findings volume from one
  sentence — remains far larger than any treatment, and is the only finding here
  that was never in doubt.
- **Every arm in the two replicated stages, pooled, reached 10/24 human
  threads.** Fourteen were matched by nobody — including two of the three
  "reuse what exists" threads the checkout was predicted to unlock.

Pooling across conditions is the sharpest summary of how little the inputs
mattered (stages 2 and 3, twenty arms, two scoring passes combined — which can
only flatter the ceiling):

```
checkout     8/24  [2, 4, 7, 8, 10, 17, 18, 22]
plain        7/24  [2, 4, 7, 10, 17, 21, 22]
retrieved    4/24  [2, 10, 18, 23]

reached ONLY by checkout  : [8]
reached ONLY by plain     : [21]
reached ONLY by retrieved : [23]
```

Each condition reaches exactly **one** thread no other condition ever reached.
That symmetry is what "no effect" looks like: the conditions are not finding
different things in any structured way, they are each sampling a little
differently from the same small reachable set.

The honest summary of this POC is not "repository context doesn't work". It is
**"this experiment was not powerful enough to tell, and no treatment showed a
signal large enough to escape its own noise floor"**.

**The error budget, now measured rather than assumed:**

| source of variation | size |
|---|---|
| judging, two judges over identical arm files | up to **2 threads** (97% per-decision agreement) |
| generation, same condition re-run | up to **4 threads** |

Nothing below roughly 4 threads out of 24 is measurable in this design. Every
treatment effect this POC ever reported was smaller than that.

---

## Evidence

Numbers below are derived from the blind judge's own coverage table by
`summarise_experiment.py`, not retyped by hand. Retyping is how a 3 quietly
becomes a 4.

Command:

```bash
python summarise_experiment.py
```

Output:

```text
threads parsed from scorer table: 24 (expected 24)

condition                       arm   n_findings  threads_matched
kb=no-kb  repo=repo             A     22          6/24
kb=no-kb  repo=no-repo          B     24          6/24
kb=kb     repo=no-repo          C     20          3/24
kb=kb     repo=repo             D     17          3/24

2x2 (threads matched out of 24)
             no-repo      repo
no-kb              6         6
kb                 3         3

union of no-kb arms      : 9/24 [1, 4, 6, 7, 10, 15, 18, 21, 22]
union of kb arms         : 4/24 [4, 10, 21, 22]
union of all four arms   : 9/24 [1, 4, 6, 7, 10, 15, 18, 21, 22]
threads added by kb arms : 0 []

unique to A (kb=no-kb, repo=repo): [1, 15]
unique to B (kb=no-kb, repo=no-repo): [7, 18]
unique to C (kb=kb, repo=no-repo): []
unique to D (kb=kb, repo=repo): []

matched by no arm        : 15/24 [2, 3, 5, 8, 9, 11, 12, 13, 14, 16, 17, 19, 20, 23, 24]
```

False-positive rates, from the same blind judge: A 0/22, B 1/24, C 0/20,
D 0/17. No arm was meaningfully less careful than another.

**Run context**

- Date run: 2026-09-28
- Subject: one held-out pull request, confirmed absent from the mining corpus
- Knowledge base: 224 entries, 116 KB across five markdown files, mined from
  100 randomly sampled completed pull requests over 2 years (seeded sample)
- Checkout: base commit of the pull request, 865 Go files, searchable, read-only
- Reviewing arms: 4. Independent blind judge: 1. Scoring passes: 1.
- Runs per arm: 1

---

## Stage 2 — the replication that invalidated the headline

Stage 1's arms were each run **once**. That is only sound if a single run is
representative of its condition. It is not.

### The replication check

Two arms were run in the *identical* condition — plain diff, no knowledge base,
no checkout — differing only in being separate invocations. They scored **6/24
and 3/24**.

That is the same gap stage 1 attributed to the knowledge base.

It is not judge drift. Re-scoring stage 1's four arm files inside the larger
pass reproduced 6/24, 3/24 and 3/24 exactly, with one arm moving 6 to 5. So:

| source of variation | size |
|---|---|
| judge, same findings re-scored | ±1 thread |
| **reviewer, same condition re-run** | **up to 4 threads** |

The instrument is stable. The *reviewer* is stochastic. Stage 1 measured the
reviewer's randomness and labelled it a treatment effect.

### Five runs per condition

Command:

```bash
python summarise_ten.py
```

Output:

```text
condition    n_runs  mean   min  max  spread  values
------------------------------------------------------------
plain        5       3.6    2    6    4       [2, 3, 3, 4, 6]
retrieved    5       2.2    1    3    2       [1, 2, 2, 3, 3]

widest within-condition spread (noise floor) : 4 threads
observed mean difference (retrieved - plain) : -1.4 threads
exact permutation p-value (252 splits)     : 0.183
  -> consistent with noise; no detectable effect of retrieval

union of 5 plain      runs : 7/24 [2, 4, 7, 10, 17, 21, 22]
union of 5 retrieved  runs : 4/24 [2, 10, 18, 23]
reached only by retrieved   : [18, 23]
reached only by plain       : [4, 7, 17, 21, 22]

union of all ten arms : 9/24 [2, 4, 7, 10, 17, 18, 21, 22, 23]
matched by no arm     : 15/24 [1, 3, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 19, 20, 24]
```

The union gap of 3 was tested separately rather than eyeballed, because this
report has already over-read one unreplicated comparison:

```text
union of 5 plain runs     : 7/24
union of 5 retrieved runs : 4/24
exact permutation p-value (252 splits) : 0.190
  -> union gap is consistent with noise
```

With five per group the smallest achievable p is 2/252 = 0.008, so this design
can detect a real effect — it simply did not find one in coverage.

### The one effect that did clear the noise

Findings volume needs no judge, so it is free of any matching-threshold concern:

```text
condition    runs  mean   sd     min  max  values
----------------------------------------------------------
plain        5     14.0   4.36   9    19   [9, 10, 15, 17, 19]
retrieved    5     12.6   1.34   11   14   [11, 12, 12, 14, 14]

mean volume difference (retrieved - plain) : -1.4 findings
exact permutation p-value (252 splits)   : 0.556
  -> volume difference is consistent with noise

sd ratio plain/retrieved : 3.25
one-sided permutation p  : 0.008 (252 splits)
```

Retrieval does not change how much the reviewer finds. It changes how
**consistently** it finds it — a 3.25x reduction in run-to-run spread.

Reviewing the same diff, the plain reviewer returned 9 findings on one run and
19 on another. The retrieval reviewer stayed within 11 to 14 every time.

Two caveats kept deliberately attached to this number: variance ratios are
outlier-sensitive, and plain's spread is driven by its 9 and its 19; and
p = 0.008 is this design's floor, meaning "the most extreme of 252 splits",
not a precise probability.

**Why this might matter more than coverage.** A reviewer whose thoroughness
halves at random is hard to build a workflow on, independent of its average.
But note what it costs: retrieval's pooled union (4/24 over five runs) is
*narrower* than plain's (7/24). One coherent reading is that retrieval
**anchors** the reviewer — steadier, and steadier because it explores less. For
a reviewer, exploration is much of the value. That reading is a hypothesis, not
a result; the union difference is inside noise.

**Stage 2 run context**

- Date run: 2026-09-28
- Same subject pull request, same instructions, same judge protocol
- Instructions persisted to `ARM-INSTRUCTION.md` before the runs, so these arms
  are reproducible. Stage 1's were given inline and were never saved.
- Reviewing arms: 10 (5 per condition). Scoring passes: 1. Findings scored: 133.
- Analysis: exact permutation tests over all 252 splits, validated against four
  known cases in `test_permutation.py` before use.

---

## Stage 3 — the replication that took the last claim

Stage 2 left exactly one positive claim standing: C3, that a checkout unlocks
the "this already exists" class of comment. It rested on one run, and the
report named replicating it as the top follow-up and the thing the design most
depended on.

Stage 3 ran it. Five checkout arms against the five existing plain arms, all
ten re-scored blind in one fresh pass, with the thread category and the
analysis plan fixed in writing beforehand (`CATEGORY-C3.md`) — including a
pre-registered caveat that one of the three category threads points at a
parallel unmerged change a base-commit checkout cannot contain.

Because the plain arms were re-scored by a new judge, stage 3 also produced the
study's first clean measurement of **judge-to-judge** variance. Both results
are in C2 and C3 below.

## C1 — Knowledge base improves coverage: **UNDETERMINED** (was: Refuted)
Stage 1 measured 3/24 with the knowledge base against 6/24 without, in both
checkout conditions, and I recorded C1 as Refuted.

**That verdict is withdrawn.** Stage 2 established a within-condition noise
floor of 4 threads. A 3-thread gap cannot be distinguished from it.

Replication across five runs of retrieved-delivery against five runs of plain
diff gives means of 2.2 and 3.6 out of 24, p = 0.183 — no detectable effect,
in either direction.

What can still be said, weakly: across two scoring passes and three knowledge
arms totalling 51 findings, the knowledge base never contributed a thread that
a non-knowledge arm had not already found. That is consistent with "no effect"
and consistent with "small negative effect". It is not evidence of harm.

The knowledge arms were not careless — zero false positives between them.

### Displacement is now a hypothesis, not a mechanism

The original report explained the (apparent) harm by displacement: the bulk
knowledge base was **116 KB** against a **73 KB** diff, so the reviewer read
1.6x more mined prose than code.

That reasoning was built on an effect that has since evaporated. Retrieval cut
the bundle to 20 KB — an 82% reduction — and coverage did not improve. If
displacement by volume were the mechanism, it should have.

Displacement survives only in the weaker, more interesting form suggested by
stage 2: knowledge may narrow *what the reviewer attends to* rather than crowd
out context by sheer size. Untested.

## C2 — Checkout improves coverage: **NO EFFECT DETECTED** (was: Refuted, then Undetermined)

Stage 1 could not decide this: 6/24 with the checkout against 6/24 without, one
run each, which demonstrates nothing either way.

Stage 3 tested it properly — five checkout runs against five plain runs, scored
blind in one pass:

```
  plain     mean 2.8/24   values [2, 2, 2, 3, 5]
  checkout  mean 3.4/24   values [2, 2, 4, 4, 5]
  difference (checkout - plain) : +0.6 threads
  exact permutation p (252 splits) : 0.603
  widest within-condition spread (noise floor) : 3 threads
```

The checkout arms score slightly higher on average, and the difference is
comfortably inside run-to-run variation. This is the only claim in the study
with adequate replication behind a null result, so it carries more weight than
the "undetermined" verdicts: **a checkout does not measurably raise total
coverage**, though an effect below roughly 3-4 threads would still be invisible.

The totals were never supposed to be the interesting part. C3 was.

## C3 — Checkout unlocks "this already exists" feedback: **REFUTED ON REPLICATION** (was: Supported)

This was the last claim left standing, the one the recommended design depended
on, and the one flagged as most worth replicating. It was replicated. It did
not survive.

Three human threads share one substance: *stop writing new code, reuse what the
repository already has*. One asks the author to fold a hand-rolled client into
an existing sibling-library client that already handles retries and backoff.
One asks for a helper to move into that same client so it can be mocked. One
points at another in-flight change that already implements the same helpers.

Stage 1, one run per condition, looked decisive:

| Thread category | Checkout arm | Non-checkout arms |
|---|---|---|
| "reuse what exists" (3 threads) | **3 of 3** | **0 of 3** |

Stage 3 ran the checkout condition **five times** against the five existing
plain-diff arms, all ten re-scored blind in a single fresh pass. The category
and the analysis plan were fixed in writing *before* scoring.

```
--- PRIMARY: C3 category (threads [1, 4, 15], max 3) ---
  plain     mean 0.0/3   values [0, 0, 0, 0, 0]
  checkout  mean 0.2/3   values [0, 0, 0, 0, 1]
  difference (checkout - plain) : +0.2
  exact permutation p (252 splits) : 1.000
  union checkout [4]   union plain none
```

Across five checkout runs and three category threads — fifteen opportunities —
the checkout condition landed **one**. Stage 1's 3-of-3 became 1-of-15.

Pooled across the two *replicated* passes (stages 2 and 3, twenty arms),
threads 1 and 15 were matched by **no arm at all**. The only arm in the entire
study that ever matched them is the single stage-1 checkout run — the run whose
result this stage was testing. Thread 4, the one stage-3 hit, was matched by a
plain arm too, in the stage-2 pass.

**p = 1.000 here is degenerate, and saying so matters.** With exactly one
non-zero observation in ten, *every* one of the 252 splits produces the same
mean gap. The test is not reporting "definitely no effect"; it is reporting
that this data cannot discriminate at all. Quoting 1.000 as strong evidence of
absence would be the same over-reading this POC has already had to retract
once.

### The judge disagreement that finishes the claim

The single checkout hit is thread 4. The stage-3 judge recorded a near miss it
declined to count:

> *Thread 4 vs M19: M19 identifies duplicate supported-API logic, but it does
> not raise the human's client/mockability concern directly enough.*

**M is a plain-diff arm.** And the stage-2 judge, scoring that identical file,
*had* counted it as a match for thread 4.

So the entire surviving C3 signal — one thread, one arm — is a thread two
judges disagree about on a *plain* arm. There is no effect here to measure.

### Judge variance, now measured properly

Stage 3 re-scored the five plain arms that stage 2 had already scored: same
files, different judge. That is a clean measurement of judging noise with
generation held fixed.

```
arm file              judge2  judge3  delta
control3.jsonl             4       2     -2
plain-02.jsonl             6       5     -1
plain-03.jsonl             2       2     +0
plain-04.jsonl             3       2     -1
plain-05.jsonl             3       3     +0

mean shift judge3 - judge2 : -0.8 threads
largest single-arm shift   : 2 threads
per-decision agreement     : 116/120 (97%)
```

97% agreement on individual decisions sounds strong, and the per-arm totals
still move by up to 2. Stage 2 had estimated judge noise at ±1 by re-parsing a
single judge's table — a weaker check than comparing two judges, and it
under-estimated.

**Revised error budget:** generation noise up to 4 threads, judging noise up to
2. Nothing this design measures below roughly 4 threads means anything.

### Secondary: the checkout did not move overall coverage either

```
  plain     mean 2.8/24   values [2, 2, 2, 3, 5]
  checkout  mean 3.4/24   values [2, 2, 4, 4, 5]
  difference (checkout - plain) : +0.6 threads
  exact permutation p (252 splits) : 0.603
```

Consistent with noise. The stage-1 story that a checkout *redistributes*
attention — trading the reuse threads for others — also fails to replicate;
there is no redistribution visible, because there was no reuse gain to trade.

### What was wrong with the stage-1 reasoning

Stage 1 defended C3 on the grounds that it was "not a count" — a clean 3-for-3
on a semantically coherent category, with an obvious mechanism. That argument
felt much stronger than a raw score gap, and it was wrong in a way worth
recording:

- **A coherent category does not make a small sample large.** Three threads
  matched by one run is three observations from one draw. Coherence describes
  the threads, not the evidence.
- **A good mechanism makes noise feel explained.** "You cannot suggest reusing
  a helper you cannot see" is true, and it predicts the stage-1 result
  perfectly. It also predicts a result that did not recur.
- **Naming the replication as the top follow-up was not a substitute for doing
  it.** The claim was carried into the recommendation while flagged as n=1. Had
  the spec been written before this ran, it would have been built on nothing.

The mechanism may still be real. What is now established is that if a benefit
exists, **this reviewer does not reliably realise it** — one run in five found
the thread, and a plain arm arguably found it too.

## C4 — Knowledge base and checkout are complementary: **UNDETERMINED** (was: Refuted)

The both-inputs arm scored 3/24 against the checkout's 6/24. With a 4-thread
noise floor and one run per cell, this comparison carries no information.
Nothing can be concluded about interaction from this design.

## C5 — Unioning differently-configured reviewers helps: **WEAKENED** (was: Confirmed)

Stage 1: union of the two arms without a knowledge base was 9/24 against a best
single arm of 6/24 — +3, which cleared the +2 threshold registered in
claims.md.

That threshold was set before the noise floor was known to be 4. A +3 union
gain does not clear a 4-thread noise floor.

Stage 2 gives a cleaner read on the *repetition* half of the idea: five runs of
one identical condition union to 7/24, against a best single run of 6/24. So
**re-running the same reviewer buys almost nothing** — the runs overlap heavily,
even while individual scores swing from 2 to 6.

That is a genuinely useful negative: variety between passes, not volume of
passes, is what a union strategy would have to exploit. Whether two
*differently-configured* passes beat one remains untested at adequate power,
and the original +3 observation is no longer sufficient to assume it.

---

## The instruction defect that outweighed both treatments

The first round of this experiment produced **3 findings per arm** and matched
**1/24** threads in both arms.

The cause was one sentence in my own reviewer instructions: *"do not pad the
list with trivia to make it look thorough."* Reasonable-sounding, and wrong.
The ground truth is dominated by nits and questions — one human thread opens
literally with "nit pick:", and many others are one-line questions such as "why
is this needed?" or "does it not include X?". I had explicitly suppressed the
single largest category of real reviewer behaviour.

Replacing that sentence with an instruction to report nits and questions
explicitly, and naming `question` as a severity, took both arms from 3 findings
to 24 and 20.

| Round | Instruction | Findings per arm | Threads matched |
|---|---|---|---|
| 1 | "do not pad with trivia" | 3, 3 | 1/24, 1/24 |
| 2 | nits and questions explicitly invited | 24, 20 | 6/24, 3/24 |

**An 8x swing in volume from one sentence, against a treatment effect of ±3
threads.** Had the POC stopped at round one, it would have reported the correct
conclusion about the knowledge base for entirely the wrong reason.

The general lesson: **before measuring a treatment, verify the instrument is
not the dominant variable.** A flat result across arms is a signal to suspect
the harness, not to conclude the inputs do not matter.

---

## What the unmatched threads actually need

The reviewer's ceiling is not one thing. Categorising the 15 threads no stage-1
arm matched (the pooled figure across stages 2 and 3 is 14, a nearly identical
set):

| Cause | Threads | Reachable by any artifact we can gather? |
|---|---|---|
| **External API contract** — a vendor team's spec, not in the repository | 9, 12, 13, 17 | **No.** One thread's answer was a link to an external design document. |
| **Deep state-machine reasoning** about pending/failed/retry transitions | 8, 11, 19, 20, 23, 24 | Hard. Needs operational understanding of the running system. |
| **Close-reading misses** — wrong error constant, an unnecessary database read, a stale comment, a readability split | 2, 3, 14, 16 | **Yes.** These should have been caught. |
| **Repository context** | 1, 4, 15 | **In principle yes. In practice, not by simply supplying a checkout** — see C3. |

Roughly 4 of 24 threads are unreachable from any artifact `atom review` could
plausibly assemble. Another 4 were missed through inattention rather than
missing knowledge. Only 3 were the repository-context problem I had assumed
dominated.

Two corrections have landed on this table:

1. I had characterised the whole ceiling as a "repository context" problem
   before categorising it. It is at most 3 of 15.
2. The last column originally read *"Yes — solved by the checkout"* for that
   row. Stage 3 refuted it. Supplying a checkout does not reliably convert
   those threads; across five checkout runs, threads 1 and 15 were never
   matched at all.

So the largest tractable category is not context at all — it is the four
**close-reading misses**, which need no new input, only a more careful pass.

## C6 — Retrieval delivery beats bulk delivery: **REFUTED (as stated)**
Formed after stage 1, on the argument that bulk injection scales badly with
knowledge-base size while retrieval does not — so retrieval, not bulk, is the
only delivery that survives a knowledge base growing over time.

Retrieval was built (TF-IDF over mined entries, scored per changed file,
relative floor, de-duplicated) and cut the bundle from 116 KB to 20 KB, an 82%
reduction, while keeping visibly relevant entries — the top-ranked entry for
this diff belonged to the redundant-validation convention, the same category as
one of the human threads.

It made no difference to coverage: 2.2/24 mean against plain diff's 3.6/24,
p = 0.183. Pooled over five runs it reached 4/24 against plain's 7/24,
p = 0.190.

**The registered claim is refuted: better delivery did not rescue the knowledge
base.** But note what that does and does not license. It does not show mined
knowledge is worthless; it shows this corpus, delivered this way, on this pull
request, produced no measurable coverage gain — in a design whose noise floor
is 4 threads out of 24.

The unregistered surprise sits here: retrieval's effect was on **consistency**,
not coverage. That was not predicted and is reported as an observation for a
future claim, not as a confirmed result.

---

## What this changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| Mining review history is the primary lever for reviewing an unfamiliar repository | No measurable support, in bulk or retrieved form | Keep the knowledge base out of the `atom review` critical path — on grounds of "unproven", not "harmful". |
| A checkout mainly helps by giving more context around each hunk | Not supported | The totals do not move (p = 0.603 over five runs per condition). |
| A checkout uniquely enables "reuse what exists" review | **Refuted on replication** | The last remaining reason to put a checkout in the critical path is gone. Ship it as an *option*, not as the design's foundation. |
| More inputs compound | Undetermined | The design could not test interaction. Add inputs one at a time, each with a measured effect. |
| One thorough reviewer is the right shape | Partly refuted, differently than thought | Re-running the *same* reviewer adds almost nothing (7/24 union from 5 runs, best single 6/24). Variety, not repetition. |
| The reviewer's ceiling is repository knowledge | Refuted | It is four separate causes; repository knowledge is the smallest of them. |
| A single run per condition tells you what a condition does | **Refuted twice, and this invalidated two successive versions of this report** | Every future Atom experiment comparing agent configurations must replicate and report a noise floor. |
| A clean result on a coherent category is safer than a raw count | **Refuted** | C3 was defended on exactly this reasoning and still failed to replicate. Coherence describes the threads, not the strength of the evidence. |

---

## The method lesson, which outlasts the result

The durable output of this POC is not a finding about knowledge bases. It is a
finding about how to measure agent configurations at all.

**An LLM reviewer re-run on identical input with identical instructions varied
by 4 threads out of 24 — larger than every treatment effect this study set out
to measure.**

Consequences now binding on Atom's own experiments:

1. **Never compare configurations on one run each.** The first version of this
   report did, and published a confident, wrong headline. The second version
   did it again for C3, on one run, and was wrong again.
2. **Measure the noise floor before interpreting any gap.** Run one condition
   twice before running six conditions once. It is the cheapest possible
   experiment and it determines whether the rest is worth running.
3. **Separate judge noise from generation noise.** Two judges scoring identical
   arm files disagreed by up to 2 threads; re-generating moved results by 4.
   Those need different fixes — single-pass scoring for the first, replication
   for the second.
4. **Test the gap you are about to report**, including ones that look obvious.
   The union gap of 3 looked convincing and was noise (p = 0.190).
5. **Persist the exact instructions given to each arm.** Stage 1's were inline
   and unsaved, so those arms can never be reproduced. Stages 2 and 3 read from
   `ARM-INSTRUCTION.md`.
6. **Prefer observables that need no judge.** Findings volume needed no scoring
   and produced the study's only clear effect.
7. **A mechanism that explains the result is not evidence for it.** "You cannot
   suggest reusing a helper you cannot see" is true, obvious, and predicted a
   result that did not recur. Plausibility is what makes a noise artifact
   survive scrutiny.
8. **Fix the category and the analysis plan in writing before scoring.** Stage 3
   did this in `CATEGORY-C3.md`, including a caveat that one of the three
   threads might be unreachable in principle. Without it, the single hit could
   have been written up as partial support.
9. **Re-score a shared subset when judges change.** Stage 3 re-scored stage 2's
   plain arms, which is the only reason judging noise could be separated from
   the treatment — and it revealed that the deciding thread was one the two
   judges disagreed about.

---

## Explicitly not covered

- **Whether repository context helps at all.** This study lacked the power to
  detect an effect smaller than roughly 4 threads out of 24. A real but modest
  benefit would have been invisible here. "Not detected" is not "not there",
  and that applies to the checkout as much as to the knowledge base.
- **A knowledge base grown and curated over time**, rather than mined in one
  pass. Accumulated, pruned, human-corrected entries may behave differently,
  and nothing here speaks to that.
- **Whether a better-used checkout helps.** The arms were told they had a
  checkout and left to decide how to use it. A reviewer *directed* to ask
  "does this already exist?" for every new helper is a different treatment,
  and an obvious next candidate — the instruction-wording effect is the largest
  one this study ever measured.
- **Whether retrieval's consistency effect is real and useful.** It cleared
  this design's significance floor on one observable, on one pull request. It
  has not been replicated, and its cost — a narrower pooled union — is
  unmeasured.
- **C3 under a directed instruction.** Stage 3 refuted C3 as a property of
  *having* a checkout. It says nothing about a reviewer explicitly told to
  check for duplication, which is a different and untested treatment.
- **Generalisation.** One pull request, one repository, one language, one
  reviewing model. Twenty-three reviewing arms in total, all on the same diff.
- **Whether matching human threads is the right target at all.** Every arm
  produced findings judged real that the humans never raised. A reviewer that
  finds different true problems is not obviously worse than one that reproduces
  the humans. This may be the most consequential untested assumption in the
  study, because it is the one baked into the scoring.
- **Cost.** No measurement of latency or token spend per arm.
- **Write-back.** Local report only; nothing posted to any pull request.

---

## Recommendation

**Proceed to spec — but the spec can no longer be justified by this POC's
findings, only by its constraints.**

Twenty-three reviewing arms across three stages produced **no treatment that
measurably improves review coverage**. That is a real result, and it should
change the shape of what gets built rather than be worked around.

The design should be:

1. Reviewer instructions that **explicitly invite nits and questions**, with
   `question` as a first-class severity. After three stages this is still the
   only recommendation carried by a large, unambiguous effect — an 8x swing in
   output from a single sentence.
2. A **checkout at the base commit** as an *available* input, not the
   foundation. C3 is refuted, so the checkout is no longer justified by
   evidence of benefit; it is justified by being cheap, harmless (p = 0.603 on
   totals), and a prerequisite for any future directed-duplication instruction.
3. **No knowledge base in the critical path.** Not because it was shown to
   harm — that claim is withdrawn — but because two delivery mechanisms
   produced no measurable benefit, and unproven machinery should not ship.
4. An honest statement in the output that some classes of review feedback —
   external contracts in particular — are out of reach.

Multiple unioned passes are **no longer recommended on this evidence**. Union
from repetition was measured and is nearly worthless (7/24 from five runs
against 6/24 from the best single run). Union from *variety* is untested.

**The most promising untested lever is the instruction, not the context.** Every
context treatment failed; the one instruction change tested produced the largest
effect in the study. The obvious next experiment is a *directed* reviewer —
told to ask "does this already exist?" of every new helper, with the checkout as
the means of answering — measured with five runs per condition from the start.

Next artifact: a design spec for `atom review`, co-written with the developer,
written in full knowledge that its context inputs are unproven.

Conditions before continuing:

- **Adopt the replication protocol** for every future Atom experiment comparing
  agent configurations. Five runs per condition minimum, noise floor reported
  alongside any effect, category and analysis plan fixed before scoring. This
  POC published two wrong headlines without it.
- **Do not reinstate any refuted claim** into the spec's justification. If the
  spec needs C3, C3 must be re-established by a new, properly powered
  experiment — not by the stage-1 result, which is superseded.
- Retire the mined corpus from the critical path, but **keep it** — the
  consistency observation is worth a properly powered follow-up, and the corpus
  cost real effort to build.
