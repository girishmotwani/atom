# POC Claims: does repository knowledge improve an AI code review?

**Pre-registration status is recorded per claim.** Three of these claims were
stated before the measurements that test them ran. Two were formed
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

---

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

## What this POC cannot decide

- Whether a knowledge base delivered by **retrieval** — fetching only the
  entries relevant to the hunk under review — behaves differently from one
  delivered as **bulk context**. Only bulk delivery is tested here.
- Whether results generalise beyond one pull request in one repository.
- Whether a knowledge base grown and curated over time behaves like a freshly
  mined one.
- Whether a different reviewing model changes the ordering of the arms.
