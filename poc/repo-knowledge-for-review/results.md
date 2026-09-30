# POC Results: repository knowledge for reviewing an unfamiliar pull request

Claims were registered in [claims.md](claims.md), with each claim marked as
pre-registered or formed mid-experiment. Nothing here moves a threshold that
was set there.

**Subject.** The first five stages used one held-out pull request in a large
internal Go service: a networking control-plane component. 12 production files,
73 KB of unified diff with 12 lines of context per hunk. Ground truth was the
24 comment threads its human reviewers actually wrote. Later stages used either
a second large production change to test checklist length or a synthetic Go
corpus with planted defects after the scraped-comment metric failed.

**Sanitisation.** This report is written for an open-source repository. The
subject repository, its pull request identifiers, and the verbatim text of its
review comments are deliberately omitted. Human threads are referenced by local
index only, and their substance is paraphrased at the level of category. The
full unsanitised working set stays outside this repository.

**Design.** Eight stages. The first five used scraped human review threads; the later stages moved to a synthetic seeded-defect benchmark after that metric failed.

*Stage 1* — four reviewing arms over a 2x2: knowledge base present/absent by
checkout present/absent, one run each.

*Stage 2* — a replication, added after stage 1's result turned out to be
unsupportable: five independent runs each of two conditions (plain diff, and
diff plus retrieved knowledge), ten arms in total.

*Stage 3* — a second replication, of the one claim stage 2 left standing: five
independent runs of the checkout condition, scored against the five plain arms
on a thread category fixed in writing beforehand.

Every arm received identical review instructions apart from the input under
test. None could read the ground truth. Arms were scored blind, with attribution
fields stripped; later seeded stages also verified prompt identity mechanically
so the rule block was the only intended difference.

---

## Headline

**Eight stages. Every context input tested failed. A hand-curated checklist is the only review aid that has beaten its alternatives, and the later experiments narrowed that result rather than generalising it.**

| lever | what was tested | verdict |
|---|---|---|
| context | knowledge base mined from ~100 PRs, bulk-injected | no effect detected |
| context | the same knowledge base via retrieval (82% smaller) | no effect detected |
| context | read-only checkout at the base commit | no effect detected |
| context | checkout aimed at the "already exists" category | **refuted on replication** |
| **instruction** | directed close-reading checklist, tuned pull request | no effect on total coverage; one defect class unlocked 5/5 vs 0/5 |
| **instruction** | the same checklist, unseen pull request | **no effect; gap exactly 0.0** |
| **instruction** | checklist length on scraped human threads | not decided; the answer key was mostly unreachable |
| **instruction** | checklist length on seeded defects | **longer lists lose recall** |
| **instruction** | model-picked rules versus curated rules | **model selection refuted; curation won** |
| **instruction** | extra rules added to the curated set | stopped before main run; selector overlap made the question unanswerable |

The instruction result was narrow and stage 4 said so: total coverage did not
move, and the effect traced to a single thread out of four targeted. It
reproduced 5/5 against 0/5, survived a three-judge check, and had a mechanism
readable directly in the output. Nothing in the first three stages did.

Stage 5 re-tested it on a pull request chosen by a pre-registered rule. The
gap was **exactly zero**. But the held-out change contains **no instance of the
defect class** the stage-4 effect came from, so that specific claim was not
refuted — it was untestable. What stage 5 does establish is that the checklist
as a bundle produced no general benefit, and that the only gap visible anywhere
in it appears solely when scoring against review threads that were themselves
machine-generated.

Stages 6 through 8 changed the benchmark instead of adding more context. Stage
6 showed that scraped review threads were a broken scoreboard. Stage 7 showed
on seeded defects that checklist dilution is real and that model selection does
not recover hand curation. Stage 8 was stopped before its main run because the
selector outputs made the additive critical-mass question arithmetically
unanswerable.


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

The reviewer's ceiling is not one thing. Categorising the **14 threads no arm
in either replicated stage matched** — `[1, 3, 5, 6, 9, 11, 12, 13, 14, 15, 16,
19, 20, 24]`:

| Cause | Threads | Reachable by any artifact we can gather? |
|---|---|---|
| **External API contract** — a vendor team's spec, not in the repository | 9, 12, 13 | **No.** One thread's answer was a link to an external design document. |
| **Deep state-machine reasoning** about pending/failed/retry transitions | 11, 19, 20, 24 | Hard. Needs operational understanding of the running system. |
| **Close-reading misses** — wrong status constant, an unnecessary database read, a package-level global, a readability extraction | 3, 6, 14, 16 | **Yes, and they need no new input at all.** |
| **Repository context and convention** — reuse an existing client, follow the prevailing choice of helper | 1, 5, 15 | In principle yes. **Not in practice by simply supplying a checkout** — see C3. |

**This table was rebuilt after stage 3 and was wrong before.** Two defects, both
worth recording because both would have misdirected the next experiment:

1. It was computed against stage 1's unmatched set and never updated, so it
   described a list that three of its own rows no longer belonged to.
2. It only accounted for 17 of the 24 threads. Threads 5 and 6 were unmatched by
   every arm and appeared in no category — they had simply been dropped. A
   category table that does not partition the ground truth is not a map, and it
   was being used as one.

The corrected picture changes where effort should go. The largest *tractable*
category is not context at all — it is the four **close-reading misses**, which
need no new input, only a more careful pass:

| Thread | What the human said | Why it is tractable |
|---|---|---|
| 3 | extract this block into its own named method | visible in the diff |
| 6 | do not introduce package-level globals in new code | visible in the diff |
| 14 | this sets the wrong failure constant for the operation | visible in the diff |
| 16 | this database read is not needed | visible in the diff |

All four are answerable from the diff alone. Every arm had the diff. Every arm
missed all four.

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

## Stage 4 — the instruction experiment, and the first thing that worked

Three stages tested what the reviewer could **see**. None moved coverage. Stage
4 tested what it was **told to look for**, holding inputs fixed at the diff.

Treatment: the shared instruction plus a seven-item close-reading checklist,
phrased as standing obligations -- status and error constants, reads whose
results go unused, new package-level state, function length, duplication of
existing capability, error paths and partial failure, consistency with
neighbouring code. Control: the same five plain arms used in stages 2 and 3,
re-scored in the same fresh pass.

```
PRIMARY   total coverage /24
  directed  3.6   [2, 4, 4, 4, 4]
  plain     2.4   [4, 3, 2, 2, 1]
  gap 1.2   p = 0.167          -> NOT SUPPORTED

SECONDARY targeted close-reading threads {3, 6, 14, 16}
  directed  1.0/4 [1, 1, 1, 1, 1]
  plain     0.0/4 [0, 0, 0, 0, 0]
  gap 1.0   p = 0.008          -> SUPPORTED, narrow

CONFOUND  findings emitted per arm (judge-free)
  directed  20.4  plain 14.0   ratio 1.46x
```

**The primary measure failed, and that is the honest headline.** A 1.2-thread
gap is below the 2-thread judging noise floor. Nothing about total coverage
changed.

### The one thing that did reproduce

The entire secondary effect is **thread 6** -- a human objecting to new code
introducing a package-level global. Every directed run flagged it, at the same
file and line, in five independently-worded findings. No plain run objected.

The usual suspicion applies: stage 3 died because a single judge call on a
control arm created an apparent effect. So the plain arms were checked against
**all three** scoring passes that have now judged them:

| plain arm | judge 2 | judge 3 | judge 4 | matched thread 6? |
|---|---|---|---|---|
| control3 | 4 | 2 | 3 | no judge |
| plain-02 | 6 | 5 | 4 | no judge |
| plain-03 | 2 | 2 | 2 | no judge |
| plain-04 | 3 | 2 | 1 | no judge |
| plain-05 | 3 | 3 | 2 | no judge |

Fifteen arm-judgements by three independent judges, zero matches. Five directed
runs, five matches. This is not judge drift.

It is also the first result in this POC verified by **reading the output**
rather than by trusting a summary statistic -- and the one plain finding that
mentions the same variable turns out to be about a different concern
(nil-initialisation), which the judge correctly declined to match.

### What it does not establish

- **One of four targets.** Threads 3, 14 and 16 -- a readability extraction, a
  wrong failure constant, an unnecessary database read -- were still missed by
  every arm, directed included. The checklist named all three explicitly. Being
  told to look is not sufficient.
- **Six directives, one measurable effect.** The bundle was deliberate, to buy
  detectability against a 4-thread noise floor. The cost, stated in advance, is
  that a positive result cannot be attributed to a specific directive. Here the
  mechanism happens to be visible -- checklist item 3 maps cleanly onto thread 6
  -- but that is luck, not design.
- **The checklist was tuned to known misses on this pull request.** Declared
  before the treatment was written. This is an upper bound on a tuned
  instruction, not evidence about an arbitrary one. Generalisation requires an
  unseen PR with the checklist frozen.
- **Volume rose 1.46x.** Under the 1.5x confound line fixed in advance, so not
  declared confounded -- but close enough that precision per finding is now the
  measure that matters, and this design never measured it.

### One more thing worth recording

A single directed arm matched **thread 15** -- one of the repository-context
threads about reusing something that already exists. No checkout arm reached it
in five runs, across a stage built specifically to unlock that category.

One run out of five is nothing on its own. But the direction is worth noting:
*instructing* the reviewer to ask "does this already exist?" -- explicitly
allowing it to raise the question without being able to verify the answer --
reached a thread that *supplying the repository* did not. If that survives
replication it inverts the assumption the first three stages were built on.
## Stage 5 — the generalisation test, and what the answer key was made of

Stage 4 ended with a declaration written before the checklist was authored:
the checklist was written by someone who had read the misses it was meant to
catch, so a positive result is an optimistic upper bound and must be re-tested
on a pull request nobody had looked at. Stage 5 is that re-test.

### Everything was fixed before the pull request was chosen

In order: the claim, the two measures, the run count, the exact statistic, the
threshold, a hash of the frozen checklist, the selection rule, and a decision
table saying in advance what each possible outcome would mean. Then an
amendment, also recorded before any draw, adding a sixth selection criterion —
the pull request must not appear in the mined corpus — because summaries of
those pull requests had been read during earlier stages and that is an indirect
route by which the checklist could have been influenced by the test set.

Selection screened 375 candidates on structure only — thread counts and file
extensions, never comment text — shuffled with the pre-registered seed, and
took the first that qualified. **No re-rolls were permitted and none were
taken.** The same frozen checklist was copied into the treatment arm verbatim,
hashed before and after, with the copy refusing to proceed on any difference,
and asserted absent from the control arm.

### The answer key was not what it claimed to be

The chosen pull request reported 28 review threads. Inspection before scoring
found it was not 28 human findings.

- **Ten were machine-generated.** Uniform length, emoji severity markers,
  formulaic structure — review output posted under a person's account. Worse,
  the run had happened **twice**: five texts appeared verbatim a second time,
  and in four of the five cases the duplicate was anchored to a *different*
  line. Identical prose, different location, same pull request.
- **Three were author-only**, a one-word acknowledgement with no reviewer
  comment. The distiller filters bot accounts; it does not filter threads a
  human opened on their own change.
- **Two sat on a file outside the diff** and were unreachable by construction.

Thirteen human threads survived. That still cleared the pre-registered
minimum, so no re-roll was needed.

The exclusion decision was recorded in full before scoring, including a
prediction: three of the five machine-authored concerns map onto checklist
items, so removing them should make a positive result *harder* to obtain. That
prediction was stated in writing precisely so it could not be taken on trust,
and the stage committed to reporting the result both ways.

### The result

| measure | directed | plain | gap | p | verdict |
|---|---|---|---|---|---|
| total coverage /13 | 2.2 | 2.2 | **0.0** | 1.000 | not supported |
| targeted subset /7 | 1.6 | 1.0 | 0.6 | 0.167 | not supported |
| findings emitted | 13.6 | 13.6 | 1.00x | — | confound absent |

Dead flat on the pre-registered primary measure. The verbosity confound that
clouded stage 4 at 1.46x is completely absent here at 1.00x, which at least
means neither stage's number is explained by one condition simply saying more.

Across ten runs, **nine of the thirteen threads were reached by nobody.**

### Both ways, as promised

| answer key | directed | plain | gap | p |
|---|---|---|---|---|
| 13 human threads | 2.2 | 2.2 | 0.0 | 1.000 |
| 5 machine-authored threads | 3.2 | 2.2 | 1.0 | 0.127 |
| all 18, the uncleaned key | 5.4 | 4.4 | 1.0 | 0.079 |

The pre-scoring prediction held. Keeping the machine-authored threads raises
the directed condition, and raises it enough to turn a dead-flat null into the
best-looking number in the stage.

**Had the answer key not been audited, this stage would have reported a
one-thread gap at p = 0.079 and called it suggestive.** The entire apparent
effect is the treatment agreeing more closely with another model's review
output. An experiment scored against machine-written review threads is not
measuring agreement with human reviewers; it is measuring agreement with a
model, and it will flatter whichever condition writes in a more model-like
register.

### The part the pre-registration got wrong

Stage 4's effect was never "the checklist helps". It was one checklist item
firing on one thread about newly introduced package-level state, 5/5 against
0/5. So the obvious question for a null result is whether the held-out pull
request contains that defect class at all.

A mechanical check of the diff says it does not. Of 220 added lines, six
introduce package-level declarations and **none of them is a variable or
constant** — they are a type, a constructor, a method and three test functions.
A judge-free string check agrees: package-level state is raised by 0/5 directed
arms here, against 5/5 on the tuned pull request.

**The item responsible for the entire stage-4 effect had nothing to act on.**

That materially changes what this stage establishes:

- the seven-item bundle produced **no measurable benefit** on an unseen pull
  request, gap exactly zero on the pre-registered primary measure — this stands;
- the one item with a demonstrated effect was **untestable here**, so the
  stage-4 claim is neither confirmed nor refuted, it is **untested**;
- the benefit that does appear, appears **only against machine-authored text**.

The flaw is in the selection rule, and it is mine. It constrained *structure* —
thread count, language, file types, corpus membership — but not
*applicability*. A pull request can satisfy every structural criterion and
still contain nothing for a narrow treatment to act on. The resulting null is
uninformative about the treatment while being indistinguishable, in the
numbers, from a refutation.

Selecting on defect-class presence would not have been selecting on outcome. It
would have been defining the population in which the claim is made. A treatment
that catches new package-level state should be tested on changes that add some,
and its claim should be narrowed to that population rather than stated over
pull requests in general.


## Stage 6 — the checklist-length experiment, and the metric that failed

The next question came from the developer's model of how `atom review` should
improve over time: the checklist should keep accumulating rules from human
review history until it reaches enough mass to find more issues. Stage 6 tested
the first part of that claim directly. Does a checklist still work as it grows
from seven rules to thirty to one hundred?

The design used a large, old production change: 906 changed lines, a 194 KB
diff, and 24 human review threads after the answer key was audited. The seven
core rules were placed in the middle of the longer lists, not at the top or the
bottom, and the prompts were checked to be identical apart from the rule block.
There were five runs per list length, fifteen reviewing arms total.

| measure | 7 rules | 30 rules | 100 rules |
|---|---:|---:|---:|
| findings per run | 3.2 | 3.2 | 4.0 |
| coverage of 24 human threads | 0.0 | 0.0 | 0.0 |
| package-state rule fired, strict argument | 0/5 | 0/5 | 0/5 |
| precision | 81% | 88% | 85% |

All pairwise coverage comparisons were gap 0.0, exact p = 1.000.

That does **not** mean longer lists are harmless. It means this stage could not
answer the checklist-length question. The rule chosen as the clean primary
measure did not fire even in the seven-rule condition. The arms often mentioned
the same topic, but they did not make the argument the rule requires. They were
not saying "make this a field or injected dependency"; they were raising a
different concern, usually concurrency.

The more important result was not the list-length result at all. It was the
answer key.

### The scraped answer key was mostly not a review benchmark

Every one of the 24 human threads was classified item by item after the null
result:

| class | n | what it was |
|---|---:|---|
| reachable | 5 | a substantive issue visible in the diff |
| local convention | 7 | repository-specific naming or import-alias preferences |
| artefact | 8 | pasted benchmark output or process negotiation |
| tooling | 4 | formatter or import-order complaints |

Only **5 of 24** threads — **21%** — were reachable by a diff-only reviewer.
That finding invalidated the metric used by the earlier stages. The reviewers
were not mostly wrong; their precision was 83% across all 52 findings. They
were finding real problems, but the scoreboard was mostly asking them to
rediscover things no diff reviewer should be expected to rediscover.

This is why the next stage stopped scoring against scraped human comments and
moved to a curated seeded-defect benchmark.

### What Stage 6 does and does not establish

It establishes that the old metric was broken and that answer keys scraped from
review history must be classified before being counted. It also records a large
change-size effect: on the 194 KB diff the reviewer produced roughly a quarter
as many findings as it had on the smaller held-out change.

It does **not** establish that longer checklists help. It does **not** establish
that longer checklists dilute. The headline question remained open because the
measurement instrument failed first.

## Stage 7 — the seeded-defect benchmark, and why model selection lost to curation

Stage 7 replaced the broken scoreboard with a synthetic Go service and a
planted-defect key. The corpus was written for the experiment, contains no
private source material, and can be published with Atom. Fourteen defects were
targeted by the curated seven-rule checklist, two additional defects were kept
as controls, and the key was blind to rule attribution.

The first run re-tested checklist length on this new benchmark:

| condition | findings per run | targeted defects found /14 | controls /2 | precision |
|---|---:|---:|---:|---:|
| curated 7 | 10.4 | **9.2** | 0.0 | 98% |
| 30 rules | 7.8 | **6.8** | 0.0 | 100% |
| 100 rules | 7.2 | **6.2** | 0.0 | 100% |

Exact two-sided permutation tests:

| comparison | gap | p |
|---|---:|---:|
| curated 7 vs 30 rules | +2.40 | **0.024** |
| curated 7 vs 100 rules | +3.00 | **0.024** |
| 30 rules vs 100 rules | +0.60 | 0.571 |

On the seeded benchmark, dilution is real. The seven-rule checklist finds about
33% more targeted defects than the thirty-rule list and about 48% more than the
hundred-rule list. Longer lists did not add false positives; they lost recall.

The controls failed as an instrument. They scored zero in every condition,
including the seven-rule baseline. A floor cannot measure crowding-out. That
failure became a rule for later work: a control or newly seeded defect must be
findable in the baseline before its decline can mean anything.

### The shippable mechanism was then tested and refuted

The mechanism Atom would actually ship is not "always send all hundred rules".
It is "grow a knowledge base, then select the few rules relevant to this change".
So the next test gave five independent selectors the diff and the full
hundred-rule checklist, asked each to pick seven rules, and then ran reviewers
with those selected lists. A random seven-rule condition was added as a count
control.

All five conditions were scored in one blind pass:

| condition | rules | targeted defects found /14 | precision |
|---|---:|---:|---:|
| hand-curated | 7 | **9.2** | 98% |
| model-selected | 7 | **6.8** | 90% |
| 30 rules | 30 | 6.8 | 100% |
| 100 rules | 100 | 6.2 | 100% |
| random | 7 | **5.2** | 90% |

Pre-registered comparisons:

| comparison | gap | p |
|---|---:|---:|
| model-selected vs hand-curated | -2.40 | **0.048** |
| model-selected vs 100 rules | +0.60 | 0.643 |
| random vs hand-curated | -4.00 | **0.008** |
| random vs 100 rules | -1.00 | 0.286 |
| model-selected vs random | +1.60 | 0.087 |

Model selection was **refuted**. It was significantly worse than the curated
seven and indistinguishable from sending all one hundred rules. Random seven
rules also performed like the hundred-rule list, so the short-list advantage was
not caused by brevity alone. Count was not the lever; content was.

The selector was not random. It recovered curated rules at 6.9x chance and was
stable across runs. The failure was systematic: it picked rules with obvious
lexical cues in the diff and missed rules about shape and comparison with
neighbouring code. Those are exactly the rules a reviewer most needs prompting
to apply, because nothing in the changed text points to them.

Curation won. The result supports a small standing checklist more strongly than
a per-change selector, at least for this corpus and this selector.

### What Stage 7 still cannot decide

Seeded defects may not behave like organic defects. Purpose-written synthetic
code makes precision easier and may make some planted problems more salient.
Everything measured here should be treated as an upper bound until checked
against real defects.

Stage 7 also does not decide whether selection helps as an addition to the
curated seven. The selected race and timeout rules were genuinely relevant;
they were harmful only because buying them meant dropping curated rules that
mattered more. That additive version became the next experiment.

## Stage 8 — the extra-rules experiment, stopped before the main run

Stage 8 tested the developer's critical-mass hypothesis in its additive form:
keep the curated seven, then add a few change-specific rules from the larger
rule base. The seeded benchmark was extended so there was something for
non-curated rules to find.

The design planted six new defects targeted by non-curated rules, in addition
to the fourteen old defects targeted by the curated seven. The planned main run
had four conditions, five runs each: curated seven; curated seven plus three
model-selected rules; curated seven plus three random rules; and all one hundred
rules. The three-rule additions make ten-rule checklists; the data artifacts and
pre-registration agree on that point.

The target rules were chosen mechanically. The procedure shuffled the
non-curated rules with a fixed seed, walked the list in order, and accepted the
first six that could be instantiated as plausible defects in the synthetic
corpus. The accepted rules covered log severity, omitted empty fields, stale
documentation, repeated literals, exhaustive status handling, and renamed
exported methods. The accepted checklist positions were 11, 12, 15, 54, 90 and
92. The whole walk was recorded before selector runs.

### The findability gate did its job

Before spending the twenty main runs, the six new defects were tested with a
checklist containing only their six targeting rules. That gate was there because
Stage 7's controls had failed at the floor.

Round 1 found four of six defects 3/3 and two defects 0/3. The two failures were
purely stylistic: an omitted-field encoding detail and a repeated literal. Each
was repaired once, under a rule fixed before repair, to give it an observable
consequence.

Round 2 produced:

| defect slug | runs detecting |
|---|---:|
| backoff-cap-broken | 3/3 |
| cancelled-task-still-runs | 3/3 |
| renamed-without-deprecation | 3/3 |
| repeated-literal | 3/3 |
| shutdown-logged-as-failure | 2/3 |
| omitempty-hides-zero | 1/3 |

That gate prevented a repeat of the failed-control problem. It also produced a
finding that matters outside this experiment: reviewers report consequences,
not rule violations. A rule whose violation changes nothing observable goes
unreported even when the reviewer is handed that exact rule.

The repair creates a declared limitation. Two of the six new defects were made
more consequential after being observed unfindable, so the six-defect headroom
set is biased toward defects a reviewer can see. Any measured headroom would be
an upper bound, not a typical value.

### Why the main run was stopped

The new defects targeted checklist positions 11, 12, 15, 54, 90 and 92.

The five model selectors chose positions 42, 95 and 90 in four runs, and 25, 42
and 95 in one run. In aggregate: 42 was chosen 5/5, 95 was chosen 5/5, 90 was
chosen 4/5, and 25 was chosen 1/5.

The overlap with the six new target rules is exactly one position: 90.

That made the headline question arithmetically unanswerable before a single
main reviewing arm ran. The model-selected additive checklist could catch at
most one of the six new defects by rule selection. Spending twenty runs would
have measured a ceiling that was already visible from the selector outputs.

Three paths were considered. Running the planned arms anyway would have spent a
main run on a question the design could no longer answer. Relabelling the stage
as a dilution test would have changed the claim after seeing a decisive planning
result. Adding a hand-picked checklist aimed at the planted defects would have
been teaching to the test: a win would prove only that rules chosen because they
match planted defects can find those planted defects.

The decision was to stop the seeded-defect version rather than spend the main
run.

### What remains open

The critical-mass hypothesis is not settled for organic defects. This stopped
experiment shows that the tested selector did not pick the non-curated rules the
new seeded defects needed, and that adding hand-picked target rules would not be
a fair test. It does not prove that a growing checklist cannot help on real
changes, and it does not prove that seeded defects represent organic defects.
Those remain open questions.

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
- **Generalisation.** The first five stages used one pull request, one
  repository, one language, and one reviewing model. The seeded stages used one
  synthetic corpus. They are stronger as controlled mechanism tests, but weaker
  as evidence about organic defects.
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

The context-input stages produced **no treatment that measurably improves
review coverage on an unseen change**. The seeded stages add a narrower result:
a small hand-curated checklist beats longer lists and model-selected lists on
planted defects. Both results should change the shape of what gets built rather
than be worked around.

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

**The instruction lever has now been tested, and the result is a narrow one.**
On the pull request whose misses had been read, a directed checklist unlocked
one defect class 5/5 against 0/5. On an unseen pull request the gap was exactly
zero — but that change contained no instance of the defect class in question,
so the narrow claim is untested rather than refuted.

Two consequences for the spec:

5. Ship the directed checklist as **opt-in, off by default**, described by the
   one defect class it has been shown to catch — newly introduced package-level
   state — and not as a general improvement. It is cheap, it did not increase
   output volume on the held-out change (1.00x), and it has a readable
   mechanism. None of that makes it a default.
6. Treat review-history mining as **unproven and hazardous**, per finding 20.
   Any such feature must detect machine-written threads before using them.

The next experiment is not another context input. It is the same checklist on a
held-out change selected by a mechanical rule requiring the defect class to be
present, with the claim narrowed to that population from the outset.
Next artifact: a design spec for `atom review`, co-written with the developer,
written in full knowledge that its context inputs are unproven and its one
instruction result is narrow and not yet shown to transfer.

Conditions before continuing:

- **Adopt the replication protocol** for every future Atom experiment comparing
  agent configurations. Five runs per condition minimum, noise floor reported
  alongside any effect, category and analysis plan fixed before scoring. This
  POC published two wrong headlines without it.
- **Pre-register generalisation tests on applicability, not just structure**
  (finding 21). A held-out case must contain an instance of the mechanism under
  test, or the null means nothing.
- **Audit any scraped ground truth before scoring** (finding 20), and record the
  expected direction of bias in writing first. Stage 5 would have reported a
  false positive without this.
- **Do not reinstate any refuted claim** into the spec's justification. If the
  spec needs C3, C3 must be re-established by a new, properly powered
  experiment — not by the stage-1 result, which is superseded.
- Retire the mined corpus from the critical path, but **keep it** — the
  consistency observation is worth a properly powered follow-up, and the corpus
  cost real effort to build.
