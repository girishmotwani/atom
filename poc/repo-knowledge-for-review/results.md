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

**Design.** Two stages.

*Stage 1* — four reviewing arms over a 2x2: knowledge base present/absent by
checkout present/absent, one run each.

*Stage 2* — a replication, added after stage 1's result turned out to be
unsupportable: five independent runs each of two conditions (plain diff, and
diff plus retrieved knowledge), ten arms in total.

Every arm received identical review instructions apart from the input under
test. None could read the ground truth. Arms were scored in a single blind pass
per stage by an independent judge, anonymised with attribution fields stripped.

---

## Headline

**This report was corrected after replication. Read this section before any
other.**

The first version of this report led with: *the mined knowledge base halved
review coverage*. **That claim is withdrawn.** It was not a transcription error
— the numbers were real. The experiment simply could not support the inference
drawn from them.

Stage 1 ran one arm per condition and saw 6/24 without a knowledge base against
3/24 with one. Stage 2 ran the *identical* condition five times and got
**2, 3, 3, 4 and 6** out of 24.

A single condition varies by 4 threads run to run. The "effect" was 3. It was
inside the noise the whole time.

What actually survives measurement:

- **No detectable coverage effect from a knowledge base**, in either bulk or
  retrieved delivery (p = 0.183 on per-run coverage, p = 0.190 on pooled union).
- **No detectable coverage effect from a checkout** on totals — though see C3,
  which is about *which* threads, not how many.
- **One detectable effect in the entire study**: retrieval makes the reviewer's
  output volume **3.25x more consistent** run to run (p = 0.008). It does not
  make it find more.
- **The instruction wording effect** — an 8x swing in findings volume from one
  sentence — remains far larger than any treatment, and is the only finding here
  that was never in doubt.
- **All ten replication arms pooled reached 9/24 human threads.** Fifteen were
  matched by nobody.

The honest summary of this POC is not "knowledge bases don't work". It is
**"this experiment was not powerful enough to tell, and neither treatment showed
a signal large enough to escape its own noise floor"**.

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

## C2 — Checkout improves coverage: **UNDETERMINED** (was: Refuted)

Stage 1: 6/24 with the checkout, 6/24 without — and on re-scoring, 5/24 and
6/24. Identical within the noise floor, but with one run per arm that
demonstrates nothing either way.

The totals were never the interesting part. C3 is.

## C3 — Checkout unlocks "this already exists" feedback: **SUPPORTED, NOT REPLICATED**

Three human threads share one substance: *stop writing new code, reuse what the
repository already has*. One asks the author to fold a hand-rolled client into
an existing vendor-API client that already handles retries and backoff. One
asks for a helper to move into that same client so it can be mocked. One points
at another in-flight change that already implements the same helpers.

| Thread category | Checkout arms | Non-checkout arms |
|---|---|---|
| "reuse the existing client / helper" (3 threads) | **3 matched** | **0 matched** |

The checkout arm matched all three. Every arm without a checkout matched none.
Two of them were matched by *no other arm at all*.

This is the most senior feedback on the pull request — one of these threads was
bumped by its reviewer and escalated — and it is structurally unreachable from
a diff. The checkout is the only input tested that reaches it.

**Why this is downgraded from Confirmed to Supported.** It rests on a single
checkout run, and stage 2 showed single runs to be unreliable. What protects it
is that it is not a count — it is a clean 3-for-3 against 0-for-3 on a
semantically coherent category, with an obvious mechanism: you cannot suggest
reusing a helper you cannot see. A count of 3 could be noise; *which* threads
those were is harder to explain away.

Replicating C3 specifically — five checkout runs, scoring only the
"reuse what exists" category — is the cheapest high-value follow-up available,
and it is the claim the spec most depends on.

The reason the total did not move is that the checkout arm lost two other
threads the diff-only arm caught. Repository access **redistributes** attention
rather than adding to it.

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

## What the 15 unmatched threads actually need

The reviewer's ceiling is not one thing. Categorising every thread no arm
matched:

| Cause | Threads | Reachable by any artifact we can gather? |
|---|---|---|
| **External API contract** — a vendor team's spec, not in the repository | 9, 12, 13, 17 | **No.** One thread's answer was a link to an external design document. |
| **Deep state-machine reasoning** about pending/failed/retry transitions | 8, 11, 19, 20, 23, 24 | Hard. Needs operational understanding of the running system. |
| **Close-reading misses** — wrong error constant, an unnecessary database read, a stale comment, a readability split | 2, 3, 14, 16 | **Yes.** These should have been caught. |
| **Repository context** | 1, 4, 15 | **Yes — solved by the checkout.** |

Roughly 4 of 24 threads are unreachable from any artifact `atom review` could
plausibly assemble. Another 4 were missed through inattention rather than
missing knowledge. Only 3 were the repository-context problem I had assumed
dominated.

I had characterised this ceiling as a single "repository context" problem
before measuring the categories. That was wrong, and the correction changes the
design: chasing more context would address at most 3 of 15 misses.

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
| A checkout mainly helps by giving more context around each hunk | Not supported | The totals do not move. Any value is narrow and specific. |
| A checkout uniquely enables "reuse what exists" review | Supported, not replicated | The strongest reason to ship the checkout — and the claim most worth replicating first. |
| More inputs compound | Undetermined | The design could not test interaction. Add inputs one at a time, each with a measured effect. |
| One thorough reviewer is the right shape | Partly refuted, differently than thought | Re-running the *same* reviewer adds almost nothing (7/24 union from 5 runs, best single 6/24). Variety, not repetition. |
| The reviewer's ceiling is repository knowledge | Refuted | It is four separate causes; repository knowledge is the smallest of them. |
| A single run per condition tells you what a condition does | **Refuted, and this invalidated the first version of this report** | Every future Atom experiment comparing agent configurations must replicate and report a noise floor. |

---

## The method lesson, which outlasts the result

The durable output of this POC is not a finding about knowledge bases. It is a
finding about how to measure agent configurations at all.

**An LLM reviewer re-run on identical input with identical instructions varied
by 4 threads out of 24 — larger than every treatment effect this study set out
to measure.**

Consequences now binding on Atom's own experiments:

1. **Never compare configurations on one run each.** The first version of this
   report did, and published a confident, wrong headline.
2. **Measure the noise floor before interpreting any gap.** Run one condition
   twice before running six conditions once. It is the cheapest possible
   experiment and it determines whether the rest is worth running.
3. **Separate judge noise from generation noise.** Re-scoring identical
   findings moved results by ±1; re-generating moved them by 4. Those need
   different fixes — single-pass scoring for the first, replication for the
   second.
4. **Test the gap you are about to report**, including ones that look obvious.
   The union gap of 3 looked convincing and was noise (p = 0.190).
5. **Persist the exact instructions given to each arm.** Stage 1's were inline
   and unsaved, so those arms can never be reproduced. Stage 2's live in
   `ARM-INSTRUCTION.md`.
6. **Prefer observables that need no judge.** Findings volume needed no scoring
   and produced the study's only clear effect.

---

## Explicitly not covered

- **Whether a knowledge base helps at all.** This study lacked the power to
  detect an effect smaller than roughly 4 threads out of 24. A real but modest
  benefit would have been invisible here. "Not detected" is not "not there".
- **A knowledge base grown and curated over time**, rather than mined in one
  pass. Accumulated, pruned, human-corrected entries may behave differently,
  and nothing here speaks to that.
- **Whether retrieval's consistency effect is real and useful.** It cleared
  this design's significance floor on one observable, on one pull request. It
  has not been replicated, and its cost — a narrower pooled union — is
  unmeasured.
- **C3 at adequate power.** The checkout's "reuse what exists" advantage rests
  on one run per arm, the exact weakness that invalidated the headline.
- **Generalisation.** One pull request, one repository, one language, one
  reviewing model. Fourteen arms total, all on the same diff.
- **Whether matching human threads is the right target at all.** Every arm
  produced findings judged real that the humans never raised. A reviewer that
  finds different true problems is not obviously worse than one that reproduces
  the humans. This may be the most consequential untested assumption in the
  study, because it is the one baked into the scoring.
- **Cost.** No measurement of latency or token spend per arm.
- **Write-back.** Local report only; nothing posted to any pull request.

---

## Recommendation

**Proceed to spec** — but on a much thinner evidential base than the first
version of this report claimed.

The design should be:

1. A **checkout at the base commit**, searchable, as the primary context input.
   Justified by C3, which is supported but unreplicated — so replicate C3
   before building anything expensive on it.
2. Reviewer instructions that **explicitly invite nits and questions**, with
   `question` as a first-class severity. This is the one recommendation carried
   by a large, unambiguous effect.
3. **No knowledge base in the critical path.** Not because it was shown to
   harm — that claim is withdrawn — but because two delivery mechanisms across
   fourteen arms produced no measurable benefit, and unproven machinery should
   not ship.
4. An honest statement in the output that some classes of review feedback —
   external contracts in particular — are out of reach.

Multiple unioned passes are **no longer recommended on this evidence**. Union
from repetition was measured and is nearly worthless (7/24 from five runs
against 6/24 from the best single run). Union from *variety* is untested.

Next artifact: a design spec for `atom review`, co-written with the developer.

Conditions before continuing:

- **Replicate C3** — five checkout runs, scored on the "reuse what exists"
  category. It is the only claim the recommended design depends on, and it is
  currently n=1.
- **Adopt the replication protocol** for every future Atom experiment comparing
  agent configurations. Measure the noise floor first; report it alongside any
  effect.
- Retire the mined corpus from the critical path, but **keep it** — the
  consistency observation is worth a properly powered follow-up, and the corpus
  cost real effort to build.
