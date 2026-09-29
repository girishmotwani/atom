# POC Claims: does repository knowledge improve an AI code review?

**Pre-registration status is recorded per claim.** Three of these claims were
stated before the measurements that test them ran. Three were formed
mid-experiment, after earlier results forced a change of design. Claims formed
after seeing data are marked as such and carry less weight — a hypothesis
invented to explain a number it has already seen is not a prediction.

This honesty matters more than a tidy document. A POC that quietly back-dates
its hypotheses cannot refute anything.

---

## Context

The `atom review` beat is intended to review a pull request in a repository
Atom did not build. The open design question is what an AI reviewer needs
*besides the diff* in order to review like someone who knows the codebase.

Two candidate inputs were proposed:

1. A **knowledge base mined from the repository's own review history** — what
   this team has previously argued about, decided, and repeatedly corrected.
2. A **checkout of the repository** at the change's base commit, searchable,
   so the reviewer can ask "does this already exist?"

The subject is a single held-out pull request in a large internal Go service.
It was confirmed absent from the corpus the knowledge base was built from, so
any benefit measured is generalisation rather than memorisation.

Ground truth is what that repository's human reviewers actually wrote on the
pull request: 24 comment threads.

---

## C1 — A knowledge base mined from review history improves review coverage

**Pre-registered: yes.** Stated before any arm ran.

A reviewer given the mined knowledge base will match more of the 24 human
threads than an identical reviewer given only the diff.

- **Measure:** human threads matched, scored blind by an independent judge with
  the arms anonymised.
- **Threshold:** the knowledge base arm must match strictly more threads than
  the control. Equal or fewer refutes the claim.

## C2 — A searchable checkout improves review coverage

**Pre-registered: yes.** Stated before any checkout arm ran.

A reviewer given a searchable checkout of the base commit will match more
human threads than an identical reviewer given only the diff.

- **Measure:** as C1.
- **Threshold:** strictly more threads than control.

## C3 — The checkout specifically unlocks "this already exists" feedback

**Pre-registered: yes.** The mechanism was named before the checkout arm ran:
several human threads ask the author to reuse an existing client or helper
rather than write a new one, and no amount of diff-reading can answer that.

- **Measure:** of the human threads whose substance is "reuse what already
  exists", how many are matched by checkout arms versus non-checkout arms.
- **Threshold:** checkout arms match at least one such thread that no
  non-checkout arm matches.

**Replication added, and the threshold tightened, before stage 3 ran.** The
original threshold — "at least one thread no other arm matched" — is satisfiable
by a single lucky run, which stage 2 proved is not informative. Stage 3
therefore fixed the category membership in writing (`CATEGORY-C3.md`), ran five
checkout arms against five plain arms, and required the gap to survive an exact
permutation test. The category was also specified to be reported twice, with
and without one thread that a base-commit checkout may be unable to reach in
principle.

Note that tightening a threshold *before* the measurement, and recording why,
is the opposite of moving one afterwards to rescue a result.

## C4 — Knowledge base and checkout are complementary

**Formed mid-experiment**, after the first knowledge base result came back
negative but produced one unique correct finding the control had missed.

An arm given both inputs will match more threads than an arm given either
alone.

- **Measure:** as C1, across a 2x2 of (knowledge base present/absent) x
  (checkout present/absent).
- **Threshold:** the both-inputs arm strictly exceeds each single-input arm.

## C5 — Independent reviewers find different threads, so unioning them helps

**Formed mid-experiment**, after noticing that two arms with equal totals had
matched different threads.

The union of two differently-configured reviewers covers materially more
human threads than either alone.

- **Measure:** size of the union of matched threads across arms, versus the
  best single arm.
- **Threshold:** union exceeds the best single arm by at least two threads.

**Threshold retrospectively inadequate.** The +2 threshold was set before the
run-to-run noise floor was known. It was later measured at 4 threads, so a
union gain of 2 or 3 cannot be distinguished from noise. The threshold was not
moved to rescue a result — it is recorded here as having been set too low to
decide anything, which is itself a finding about how to register thresholds.

## C6 — Retrieval delivery rescues the knowledge base where bulk delivery failed

**Formed mid-experiment**, after C1 came back negative and the knowledge base
was found to be 116 KB against a 73 KB diff.

The argument: bulk injection degrades as the knowledge base grows, because an
ever-larger fraction of the reviewer's attention goes to mined prose. Retrieval
does not, because the bundle size is bounded by relevance rather than corpus
size. So retrieval is not an optimisation of bulk — it is the only delivery
that survives a knowledge base accumulating over time.

A reviewer given only the entries retrieved as relevant to the changed lines
will match more human threads than a reviewer given the whole corpus, and more
than a reviewer given only the diff.

- **Measure:** as C1.
- **Threshold, registered before the retrieval arms ran:** retrieval must
  exceed the plain-diff control. Equal or fewer refutes it.
- **Replication requirement, added before scoring:** five independent runs per
  condition, compared by exact permutation test, after a two-run replication
  check revealed that single runs of one condition differ by as much as the
  effect under test.

---

## C7 — A directed close-reading instruction improves coverage

**Pre-registered** in full before the treatment text was written, including the
confound rule, the bundling tradeoff, and an explicit declaration that the
checklist was tuned to known misses on this pull request.

Three stages had varied what the reviewer could *see*. This one varied what it
was *told to look for*, holding inputs fixed at the diff alone.

- **Primary** — total threads matched. Directed 3.6/24, plain 2.4/24, gap 1.2,
  p = 0.167. **Not supported.** The gap sits below the measured 2-thread
  judging noise floor, so it is not interpretable even setting the p-value
  aside.
- **Secondary** — the four close-reading threads the checklist targeted
  {3, 6, 14, 16}. Directed 1.0/4 in **every** run, plain 0.0/4 in every run.
  p = 0.008, the floor of this test. **Supported, and narrow.**

The secondary result is carried entirely by **one thread**: a new
package-level global in new code. Five independent directed runs flagged it, at
the same file and line, in five different phrasings. No plain run objected to
it. Three independent judges scored those plain arms across three passes and
none matched that thread on any of them — fifteen arm-judgements, zero matches.
So this is not judging drift, which is what killed C3.

The other three targeted threads were reached by nobody. The checklist has six
directives; the measurable effect traces to one.

**Confound, pre-registered:** directed arms emitted 1.46x more findings
(20.4 vs 14.0). That is under the 1.5x line fixed in advance, so the result is
not declared confounded -- but it is close enough that precision per finding is
now the measure that matters, and this design never measured it.

**Overfitting, declared in advance:** thread 6 was one of the four threads the
checklist was written to catch. This is an upper bound on what a *tuned*
instruction achieves, not evidence about an untuned one. Generalisation needs a
different, unseen pull request with the checklist frozen. Not claimed here.

**What it does establish:** instruction content changes which defects a
reviewer finds, reproducibly and with a traceable mechanism. That is more than
any context input managed across three stages.
## What would make this POC invalid

Recorded so the result cannot be rescued by adjusting the frame afterwards:

- **Contamination.** If the held-out pull request appears in the corpus the
  knowledge base was built from, any benefit is memorisation, not
  generalisation. Checked before running.
- **Instruction asymmetry.** If arms receive materially different review
  instructions beyond the input under test, differences measure the wording,
  not the input.
- **Ground-truth leakage.** If any reviewing arm can read the human comments,
  its score is meaningless.
- **Unblinded scoring.** The experimenter knows which arm is which and must not
  score them. Scoring is delegated with arms anonymised.
- **Judge drift.** If arms are scored in separate passes, the judge's matching
  threshold can move between passes, and that drift is indistinguishable from a
  treatment effect. All arms must be scored in one pass.
- **Insufficient replication.** *Added after the fact, and the reason two
  successive versions of the results were withdrawn.* If a condition is run
  once, its score conflates the condition with the reviewer's own randomness.
  Any claimed effect smaller than the within-condition spread is invalid. A
  noise floor must be measured — by running one condition at least twice —
  before any gap is interpreted.
- **Unmeasured judge-to-judge variance.** *Added after stage 3.* Single-pass
  scoring controls drift *within* a pass but says nothing about the threshold a
  *different* judge would apply. When scoring passes change, a shared subset of
  arms must be re-scored so judging noise can be separated from treatment
  effect. Stage 3 did this and found the two judges disagreed by up to 2
  threads — including on the single thread that the C3 verdict turned on.

## What this POC cannot decide

- Whether a knowledge base helps by an amount **smaller than this design can
  detect**. The measured noise floor is 4 threads out of 24; a real benefit
  below that would be invisible here. Every negative result in this POC is
  bounded by that sensitivity.
- Whether results generalise beyond one pull request in one repository.
- Whether a knowledge base grown and curated over time behaves like a freshly
  mined one. Retrieval was tested, so corpus *growth* is no longer blocked by
  the delivery mechanism — but growth itself remains untested.
- Whether a different reviewing model changes the ordering of the arms.
- Whether **matching human threads** is the right success measure at all. Every
  arm produced findings judged real that no human raised. This is baked into
  the scoring and therefore cannot be questioned from within this design.


---

## C8 — The directed checklist generalises to an unseen pull request: **NOT SUPPORTED**

**Status:** not supported on both pre-registered measures; the narrower C7
claim is **untested** rather than refuted.

Pre-registered in full before the pull request was selected: claim, measures,
run count, statistic, threshold, a hash of the frozen checklist, the selection
rule, and a decision table naming the meaning of each outcome in advance. One
amendment, recorded before any draw, excluded pull requests present in the
mined corpus.

Selection screened 375 candidates on structure alone and took the first
qualifying draw under a fixed seed. No re-rolls permitted; none taken.

| measure | directed | plain | gap | p |
|---|---|---|---|---|
| total coverage /13 | 2.2 | 2.2 | 0.0 | 1.000 |
| targeted subset /7 | 1.6 | 1.0 | 0.6 | 0.167 |
| findings emitted | 13.6 | 13.6 | 1.00x | — |

The verbosity confound present in C7 at 1.46x is absent here at 1.00x.

**Answer key defects, found and decided before scoring.** Of 28 reported
threads, ten were machine-generated review output posted under a human account
— and posted twice, five texts appearing verbatim a second time, four of them
anchored to a different line. Three were author-only acknowledgements. Two sat
on a file outside the diff. Thirteen human threads remained, above the
pre-registered minimum.

**Reported both ways, as committed before scoring:**

| answer key | directed | plain | gap | p |
|---|---|---|---|---|
| 13 human threads | 2.2 | 2.2 | 0.0 | 1.000 |
| 5 machine-authored | 3.2 | 2.2 | 1.0 | 0.127 |
| all 18, uncleaned | 5.4 | 4.4 | 1.0 | 0.079 |

The pre-scoring prediction that excluding machine threads would make a positive
result harder was correct. Without the audit this stage would have reported a
one-thread gap at p = 0.079.

**Limit on the interpretation, found after scoring.** C7's effect was one
checklist item firing on newly introduced package-level state. The held-out
diff adds 220 lines and six package-level declarations, none of them a variable
or constant. A judge-free check agrees: 0/5 directed arms raise package-level
state here, against 5/5 on the tuned pull request. The item responsible for C7
had no target, so C7 is untested here.

**What stands:** the seven-item bundle produced no general benefit on an unseen
change, and the only gap anywhere in the stage is agreement with machine-written
review text.

**What would settle C7:** a held-out pull request chosen by a mechanical
pre-scoring rule requiring new package-level declarations in the diff, with the
claim narrowed to that population.

**Flaw in the pre-registration:** the selection rule constrained structure but
not applicability, so a null is indistinguishable from a refutation.
