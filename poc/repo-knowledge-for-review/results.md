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

**Design.** Four reviewing arms over a 2x2: knowledge base present/absent by
checkout present/absent. All four received identical review instructions apart
from the input under test. None could read the ground truth. All four were
scored in a single blind pass by an independent judge with the arms anonymised
and the attribution fields stripped.

---

## Headline

The mined knowledge base **halved** review coverage, identically in both
checkout conditions, and contributed **zero** threads that the arms without it
did not already find.

The largest effect measured in this POC was not either treatment. It was a
single sentence of my own instruction wording, which cost an 8x difference in
findings volume before any treatment was compared.

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

## C1 — Knowledge base improves coverage: **REFUTED**

3/24 with the knowledge base against 6/24 without, and the same 3-versus-6 gap
appears in both checkout conditions. The effect is negative, large, and
replicated within the design.

An earlier, cruder round pointed the same way (4 with, 5 without), so this is
the second independent observation of the same direction.

The knowledge base arms were not careless — zero false positives between them.
They were simply looking at different things.

### The mechanism is probably displacement, and that is a confound

The knowledge base is **116 KB**. The diff under review is **73 KB**. The
reviewer was asked to read 1.6x more mined prose than actual code before it
saw a single line of the change.

The knowledge base arms also produced the fewest findings overall — 20 and 17,
against 24 and 22 for the arms without it. The both-inputs arm is the clearest
case: it cited repository evidence in 17 of 17 findings and the knowledge base
in only 2, meaning it had largely *set the knowledge base aside*, and it still
finished last on volume.

**This refutes bulk injection of a mined knowledge base. It does not refute the
idea of a repository knowledge base.** Retrieval — selecting the handful of
entries relevant to the hunk in front of you — is a materially different
delivery mechanism and is untested here. That distinction is recorded in
claims.md as out of scope, and it is the obvious next experiment.

## C2 — Checkout improves coverage: **REFUTED**

6/24 with the checkout, 6/24 without. Identical totals.

But the totals conceal the real result, which is C3.

## C3 — Checkout unlocks "this already exists" feedback: **CONFIRMED**

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

The reason the total did not move is that the checkout arm lost two other
threads the diff-only arm caught. Repository access **redistributes** attention
rather than adding to it.

## C4 — Knowledge base and checkout are complementary: **REFUTED**

The both-inputs arm scored 3/24 — worse than the checkout alone (6/24) and
equal to the knowledge base alone. Combining the inputs did not combine their
strengths; the knowledge base's negative effect dominated.

## C5 — Unioning differently-configured reviewers helps: **CONFIRMED**

Union of the two arms without a knowledge base: **9/24**, against a best single
arm of 6/24. That is +3 threads, clearing the +2 threshold.

Adding both knowledge base arms to that union changes it by **zero**.

Two reviewers, one diff-focused and one repository-focused, cover 50% more
human feedback than either alone, for the cost of one extra pass. This is the
largest genuine improvement found in this POC.

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

---

## What this changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| Mining review history is the primary lever for reviewing an unfamiliar repository | Refuted | Drop bulk knowledge-base injection from the `atom review` critical path. Revisit only as retrieval. |
| A checkout mainly helps by giving more context around each hunk | Refuted | The totals do not move. Its value is narrow and specific. |
| A checkout uniquely enables "reuse what exists" review | Confirmed | Ship the checkout. It is the only input that reaches the most senior class of feedback. |
| More inputs compound | Refuted | They interfere. Add inputs one at a time, each with a measured effect. |
| One thorough reviewer is the right shape | Refuted | Two differently-configured passes, unioned, is worth +50% coverage. |
| The reviewer's ceiling is repository knowledge | Refuted | It is four separate causes; repository knowledge is the smallest of them. |

---

## Explicitly not covered

- **Retrieval-based knowledge base delivery.** Only bulk injection was tested,
  at 1.6x the size of the diff. This is the single most important untested
  variant and the most likely way a knowledge base becomes useful.
- **A knowledge base grown and curated over time**, rather than mined in one
  pass. Accumulated, pruned, human-corrected entries may behave differently.
- **Generalisation.** One pull request, one repository, one language, one
  reviewing model, one run per arm. The 3-versus-6 gap replicated across two
  checkout conditions and directionally across two rounds, but n is small.
- **Whether matching human threads is the right target at all.** Every arm
  produced 11 to 14 findings judged real that the humans never raised. A
  reviewer that finds different true problems is not obviously worse than one
  that reproduces the humans.
- **Cost.** No measurement of latency or token spend per arm.
- **Write-back.** Local report only; nothing posted to any pull request.

---

## Recommendation

**Proceed to spec**, with the knowledge base removed from the critical path.

The design should be:

1. A **checkout at the base commit**, searchable, as the primary context input.
2. **Two review passes** — one diff-focused, one repository-focused — with
   findings unioned and de-duplicated.
3. Reviewer instructions that **explicitly invite nits and questions**, with
   `question` as a first-class severity. This is not a detail; it was the
   largest effect in the POC.
4. An honest statement in the output that some classes of review feedback —
   external contracts in particular — are out of reach.

Next artifact: a design spec for `atom review`, co-written with the developer.

Conditions before continuing:

- Re-run C1 with **retrieval-based** knowledge base delivery before discarding
  the mined corpus permanently. The corpus already exists; the experiment is
  cheap, and the bulk-versus-retrieval confound is the weakest point in this
  report.
- Confirm the union approach on at least one further pull request before
  building it into the spec. C5 rests on a single observation.
