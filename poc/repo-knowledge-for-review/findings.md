# Findings — POC: repository knowledge for reviewing an unfamiliar pull request

Discoveries made while running this POC that outlive it. Several are defects in
the *instruments* rather than in the thing being measured, and those are the
ones most likely to bite again.

---

## 1. The file-authoring tools silently redact secrets *into* the file

The single most expensive defect of this POC. A Python file was written
containing:

```python
request.add_header("Authorization", f"Bearer {token}")
```

What landed on disk was:

```python
request.add_header("Authorization", f"******")
```

Every request then went out unauthenticated. The remote answered with an HTML
sign-in page rather than an error, so the failure surfaced as a *plausible but
entirely fabricated result* several steps downstream.

### Why it took five debugging cycles to find

**Reading the file back does not reveal it.** The viewing tool applies the same
redaction on display, so a correctly-written file and a corrupted one look
identical. Every inspection confirmed the code was right.

It was found only by asking the running interpreter what it had actually
loaded:

```python
import inspect, build_diff
print(inspect.getsource(build_diff.fetch_blob))
```

### Consequences

- **Any file containing an auth-header literal, written by the authoring tools,
  should be assumed corrupt until proven otherwise** by `inspect.getsource` or
  a shell-level content search — never by the viewing tool.
- Write such lines through the shell instead, or construct the header so no
  secret-shaped literal exists in the source: `"Bea" + "rer " + token`.
- The general rule: **when a tool both writes and displays content, its display
  cannot validate its writes.** Verify through a third channel.

## 2. A remote that answers missing resources with HTML, not 404, will fabricate results

The pull-request API returned an HTML redirect page for paths it could not
resolve. Two HTML pages diff cleanly against each other and produce a small,
tidy, completely fictional patch.

This was caught by **incoherence, not by an error**: every one of 23 files
reported exactly "+3 -3" changed lines while the output ran to 549 KB. Those
two numbers cannot both be true.

- Guard explicitly: if a response body opens with `<!DOCTYPE` or `<html`, raise,
  do not parse.
- **Sanity-check the shape of a result, not just its presence.** Identical
  statistics across heterogeneous inputs mean the pipeline is measuring itself.

## 3. Shell escaping silently changed an API request into a different one

An early probe appeared to prove the API accepted a `$format=json` parameter.
It did not. PowerShell had inserted a literal backslash, producing `\$format`,
which the server ignored — so the probe succeeded *because the parameter was
malformed*. Sending the parameter correctly returns HTML.

A probe that works for a reason you have not established is not evidence. When
a request is constructed through a shell, log the exact URL the client sent.

## 4. Suppressing "trivia" suppresses most of what reviewers actually say

Recorded in full in [results.md](results.md); repeated here because it
generalises well beyond this POC.

Instructing a reviewer not to "pad the list with trivia" cut its output from 24
findings to 3, because real review feedback is dominated by nits and one-line
questions. The effect was **8x** — far larger than either treatment the
experiment was designed to measure.

- Invite nits and questions **explicitly**, and make `question` a first-class
  severity.
- More generally: **verify the harness is not the dominant variable before
  attributing a flat result to the treatment.** A near-zero difference between
  arms is a reason to suspect the instrument.

## 5. Score every arm in one pass, or judge drift masquerades as effect

Arms scored in separate passes are scored against a threshold that can move
between passes. That drift is indistinguishable from a treatment effect.

The first scoring round here used two separate passes and produced 4-versus-5.
Re-scoring all four arms together produced a clean, replicated 3-versus-6. The
one-pass result is the trustworthy one.

- Anonymise arms, randomise labels with a recorded seed, and **strip the
  attribution fields** — a `kb_source` column identifies the treatment arm
  immediately.

## 6. Derive reported numbers from the source artifact; do not retype them

While writing the results report I transcribed one line of "verbatim" tool
output incorrectly, flipping a condition label — in a document that explicitly
warns against retyping numbers.

It was caught by diffing the pasted block against freshly captured output
programmatically, not by proofreading.

- Any block claimed as verbatim should be **mechanically compared** against a
  fresh capture before the report is considered done.
- Summary statistics should be computed by a script that parses the source
  artifact, so the report cannot drift from the evidence.

## 7. A sample drawn by recency is not a sample of the repository

Switching from "the 100 most recent completed pull requests" to "100 sampled
uniformly at random over two years" changed the corpus materially:

| Measure | Recent 100 | Random 100 |
|---|---|---|
| Pull requests with no human review comment | 48% | 39% |
| Substantive human comments | 283 | 364 |
| Distinct human reviewers | 24 | 36 |

A recency slice over-represents whatever the team happens to be doing now and
whoever happens to be reviewing now. Sample over the window, with a recorded
seed.

## 8. Two design assumptions about the mined corpus were wrong, and only measurement showed it

- **Thread resolution status was assumed to reveal which advice the team
  accepted.** Measured: 305 of 335 threads carried the same status. No variance,
  no signal.
- **A lexical similarity threshold was built to find corroborated statements.**
  Measured: 1 of 4,186 statement pairs cleared it. The cause was an earlier
  instruction of mine — telling classifiers to write specific, self-contained
  sentences maximises precision and destroys the lexical overlap the threshold
  depends on. **An instruction given at one stage can silently disable a
  mechanism at a later stage.**
- **First-pass classification over-promoted by 38%** (35 of 92 entries re-filed
  by an independent auditor). Self-certification would have shipped all of them.

## 9. Repository-scoped search tools fail silently outside their repository

The `grep` and `glob` tools are scoped to the session's own repository and
return **empty results, not errors**, for absolute paths elsewhere. An agent
searching a checkout outside that scope concludes the code does not exist.

Delegated agents working against an external checkout must be told explicitly
to use shell-level search instead, or they will confidently report absence.

## 10. One run per condition measures the reviewer's randomness, not the treatment

This is the most important finding in the POC, and it invalidated its first
published headline.

Four arms were run once each. The gap between conditions was 3 threads out of
24, and it appeared consistently across a 2x2, which felt like replication. It
was reported as a clear negative result.

Running the **identical** condition five times then produced scores of
**2, 3, 3, 4 and 6** out of 24.

The within-condition spread was 4. The "effect" was 3. There had never been a
result to report.

What makes this trap hard to see:

- **The 2x2 looked like replication.** The same 3-versus-6 gap appeared in both
  checkout conditions, which reads as a replicated effect. It was two draws
  from the same wide distribution, twice.
- **The instrument was stable, so suspicion fell elsewhere.** Re-scoring the
  same findings files moved results by ±1. Judge variance was genuinely small.
  That made the numbers feel trustworthy — but the noise was upstream, in
  generation, not in scoring.
- **Plausible mechanisms were available.** A displacement story explained the
  apparent harm neatly: the knowledge base was 1.6x the size of the diff. A
  good mechanism makes a noise artifact feel explained.

**Rules now binding on every Atom experiment that compares agent
configurations:**

1. Run one condition at least twice **before** running many conditions once.
   The noise floor determines whether the study is worth running at all.
2. Report the noise floor next to every effect. An effect smaller than it is
   not a result.
3. Distinguish judge noise from generation noise — they need different fixes
   (single-pass scoring versus replication).
4. Test every gap before reporting it, including ones that look obvious. A
   union gap of 3 here looked convincing and tested at p = 0.190.
5. Prefer observables that need no judge. Findings volume required no scoring
   and produced the only clear effect in the study.

## 11. Persist the exact instruction given to each arm, or the experiment is not reproducible

The first two rounds were run by passing instructions inline to sub-agents.
Nothing was saved. When a later round needed to extend the comparison, the
exact treatment text no longer existed — so those arms can never be reproduced,
and newly-run arms cannot be proven to share their instructions.

The fix was to write `ARM-INSTRUCTION.md` and have every arm read it, with
per-arm inputs appended. A fresh control run from that file then doubled as a
replication check — which is what exposed finding 10.

**An experiment whose treatment text is not on disk is a demonstration, not an
experiment.**

## 12. A statistical test used without checking it is another way to be confidently wrong

The permutation test that carries the conclusions here was validated against
four cases with known answers before being pointed at real data: identical
groups must give p = 1.0, perfectly separated groups must give the design's
floor of 2/252, a small gap against a wide spread must not reach significance,
and a large gap against a tight spread must.

This cost one short file (`test_permutation.py`) and removed a whole class of
silent error. A wrong test does not fail loudly — it emits a plausible number
that ends an argument.

The same run revealed a design limit worth knowing in advance: with five per
group the smallest achievable p is **0.008**, so "p = 0.008" here means "the
most extreme of 252 possible splits", not a precise probability.

## 13. Fixing a retriever by inspecting its output, not by trusting its score

The first retrieval build returned a fixed top-5 per file. Inspection showed a
2-line JSON config change had been given five entries of pure noise, because
nothing relevant existed and the cutoff never bound. A relative floor — an
entry must reach 60% of the best score for its file — removed the padding.

The first de-duplication fix then created a worse failure: entries were homed to
their single best-scoring file, which left the pull request's **largest and most
important file with nothing at all**, because every one of its matches scored
higher somewhere else. Repetition wastes context; starvation loses the answer.
The resolution was one de-duplicated list with each entry naming the files it
was retrieved for.

Both defects were invisible in the summary statistics — bundle size and
reduction percentage looked excellent throughout. **Retrieval quality has to be
read, not measured.**

## 14. A coherent category is not a substitute for a sample

The knowledge-base result was withdrawn after replication. One claim survived:
that a repository checkout unlocked the "this already exists" class of comment,
scoring 3 of 3 on that category where every arm without a checkout scored 0.

It was explicitly defended on the grounds that it was **not just a count**:

> A count of 3 could be noise; *which* threads those were is harder to explain
> away.

That reasoning is wrong, and it is worth naming because it is persuasive.
Running the checkout condition five times produced **1 hit in 15 opportunities**
against the same category.

Three things made a single run feel like enough:

- **Semantic coherence was mistaken for evidential weight.** The three threads
  really did share one substance. That is a property of the threads, not of the
  sample. Three observations from one generation are still one draw.
- **The mechanism was true and obvious.** "You cannot suggest reusing a helper
  you cannot see" is correct, and it predicts the stage-1 result exactly. A
  plausible mechanism is precisely what lets a noise artifact survive scrutiny —
  it supplies the explanation that stops the questioning.
- **Naming the replication as the top follow-up felt like discharging it.** The
  claim was flagged as n=1 *and* carried into the recommendation as the primary
  design input. Had the spec been written on schedule, it would have rested on
  nothing.

**Rule: a claim is unreplicated or it is not. There is no intermediate status
that licenses building on it.**

## 15. When the judge changes, re-score a shared subset

Single-pass scoring stops the judge's threshold drifting *within* a pass. It
says nothing about whether a different judge would apply the same threshold.

Stage 3 re-scored five arm files that a previous pass had already scored. Same
files, different judge:

```
per-decision agreement     : 116/120 (97%)
largest single-arm shift   : 2 threads
mean shift                 : -0.8 threads
```

97% agreement on individual decisions, and totals still moving by 2. An earlier
estimate of judge noise at +/-1 had come from re-parsing one judge's own table —
which measures the parser, not the judge.

The overlap did more than calibrate. The deciding observation in the whole
stage — the one category thread a treatment arm matched — was a thread the
**previous judge had matched on a control arm**. Without the shared subset, a
single hit would have been reported as weak support instead of as something two
judges disagree about.

**Any experiment whose scoring pass changes must carry a shared subset across
the boundary, or its passes are not comparable.**

## 16. p = 1.000 can mean "no data", not "no effect"

The category comparison returned an exact permutation p of 1.000. Read
carelessly, that is overwhelming evidence of no difference. It is not.

With one non-zero observation among ten, *every* one of the 252 possible splits
produces an identical mean gap. The test is not discriminating between
hypotheses; it is reporting that the data cannot discriminate at all.

A p-value at either extreme deserves an explanation of the mechanism producing
it. The same design had already shown its floor of 0.008 means "most extreme of
252 splits" rather than a precise probability. Both extremes are artifacts of a
small exact test, and both are easy to quote as though they were strong claims.

## 17. Fix the category and the analysis plan before scoring, in a file

Before stage 3 was scored, the thread category was written down, with the
reasoning for every inclusion and exclusion, and with the analysis plan and the
statistical test named.

It immediately paid for itself twice:

- Reading all 24 opening comments to build it **caught an error**: a thread
  about which of two existing clients is conventional had initially looked like
  a duplication thread. It is a convention question and was excluded, with the
  reason recorded so the exclusion is visible rather than silent.
- It pre-registered a **caveat that could only weaken the result** — one of the
  three category threads points at a parallel unmerged change that a
  base-commit checkout cannot contain, so the category was specified to be
  reported both with and without it.

Written afterwards, either decision would have looked like tuning the category
to fit the answer.

## 18. A derived table goes stale silently and then gets used as a map

The report contained a table categorising the review threads no arm had
matched, split by what each category would need to fix it. It was built after
stage 1. Stages 2 and 3 changed which threads got matched, and nothing
recomputed it.

When it was finally checked -- only because it was about to be used to target
the next experiment -- it had two defects:

- It accounted for **17 of 24 threads**. Two threads that no arm ever matched
  appeared in no category at all. They had simply been dropped when the table
  was written, and nothing noticed, because a category table has no natural
  total to check against.
- Three threads were listed as unmatched that an earlier stage had matched.

Either defect would have misdirected the follow-up experiment, and the table
looked perfectly reasonable in both states. The failure is not arithmetic; it
is that a **derived artifact was stored as prose** and then treated as data.

What makes this dangerous is that stale tables get *more* trustworthy-looking
over time. It had survived two rounds of editing, so it read as settled.

**Rules now applied:**

- A derived table gets a script that regenerates it, and the script asserts a
  completeness property -- here, that the categories plus the matched threads
  partition all 24 exactly, with no gaps and no overlaps. The check raises
  rather than printing a number someone has to notice.
- Run that script again every time the underlying data changes, not only when
  the table is about to be used.
- Prefer properties that fail loudly over totals a reader must verify. "Covers
  17" only reads as wrong if you already know the answer is 24.

For Atom: any generated artifact that summarises repository state -- a
knowledge base, a coverage map, a dependency inventory -- needs both a
regeneration command and a self-check. Without them the artifact drifts out of
agreement with the repository and stays convincing while it does.

## 19. Test the instruction before testing the inputs

Three stages and roughly twenty reviewing arms went into varying what the
reviewer could see: a mined knowledge base, the same base delivered by
retrieval, a full repository checkout. None produced a measurable change in
coverage.

One stage varied the *instruction*, holding inputs fixed at the diff, and
produced the only effect in the study that reproduced across five runs and
survived a three-judge check.

In hindsight the ordering was backwards, and the reason is worth naming. The
context experiments were attractive because they were **buildable** -- mining
PRs, building a retriever, provisioning a checkout are all satisfying
engineering. Editing a paragraph of instructions is not. So the expensive,
buildable lever got tested first and the cheap one got tested last, on
essentially no evidence that the expensive one was the bottleneck.

The signal that should have redirected this earlier was available from the
start: a **single sentence** added to the instruction had already swung output
volume eightfold and coverage from 1/24 to 6/24. That was noted as an
incidental defect rather than treated as the largest measured effect in the
experiment, because it was not the thing being studied.

**Rules now applied:**

- Before building a retrieval system, a knowledge base, or any context-assembly
  machinery for an agent, test whether **changing the instruction** achieves the
  same goal. It costs one run pair.
- When an incidental change produces a larger effect than the treatment under
  test, stop and make it the treatment. A large effect in the noise channel is
  more informative than a small effect in the signal channel.
- Rank levers by **effect per unit of work**, and note that this ranking usually
  runs opposite to how interesting the work is.

The caveat that keeps this honest: the effective instruction was written by
someone who already knew which defects had been missed. It is an upper bound on
a *tuned* instruction, not proof that instructions generally beat context. The
untested version -- freeze the checklist, run it on an unseen pull request -- is
the experiment that would settle it, and it has not been run.

---

## 20. Scraped review history contains machine-written threads, and scoring against them measures model-model agreement

The held-out pull request reported 28 review threads. Ten were machine-generated
review output, posted under a human account. Five texts appeared **twice**, and
four of those duplicates were anchored to a *different* line in the same change.

Scored against the thirteen genuinely human threads, the treatment gap was
exactly 0.0 (p = 1.000). Scored against the machine-written threads, it was 1.0
(p = 0.127). Scored against the uncleaned key, 1.0 (p = 0.079) — the most
favourable number anywhere in the stage, and the one that would have been
reported had nobody looked.

An AI reviewer scored against another AI's review output is being rewarded for
writing in a model-like register, not for finding defects. The effect is
directional: it flatters whichever condition is more systematically worded,
which is exactly the condition a checklist produces.

**Rule for Atom.** Any feature that mines pull request history — review
knowledge bases, convention extraction, answer keys for evaluation — must
detect and label machine-authored threads, not just filter bot accounts. The
detectable signals here were: uniform comment length, formulaic structure,
severity markers, and verbatim duplication at differing anchors. Author-only
threads need filtering too; a bot-account filter does not catch a human opening
a thread on their own change.

**Wider rule.** When an evaluation's ground truth is scraped rather than
constructed, audit it before scoring and record the audit before unsealing any
result. State the expected direction of bias in writing first, so the audit
cannot be a post-hoc convenience. Here that prediction was made and held.

---

## 21. A generalisation test must select for applicability, not just structure

Stage 5 pre-registered a selection rule constraining thread count, language,
file types and corpus membership. Every criterion was structural. The drawn
pull request satisfied all of them and contained **zero instances of the defect
class** the treatment had been shown to catch.

The result was a gap of exactly zero — which reads as a clean refutation and is
nothing of the kind. A treatment cannot fail to catch what is not there.

The failure mode is specific to *narrow* treatments. A broad treatment acts on
almost any change, so a structural selection rule is adequate. A treatment
whose measured effect traces to a single defect class needs a held-out case
containing that class, or the null is uninformative while being numerically
indistinguishable from a refutation.

Selecting on defect-class presence is **not** selecting on outcome. Outcome
selection picks cases where the treatment did well; applicability selection
picks cases where the treatment is claimed to apply, decided mechanically on
the input before any scoring. The distinction is the difference between
defining a population and rigging a result.

**Rule for Atom.** When pre-registering a generalisation test, add a criterion
that the held-out case contains at least one instance of the mechanism under
test, evaluated mechanically on the input. If that criterion cannot be written
down, the claim is too vague to generalise and should be narrowed first.

**Corollary.** Narrow a claim to the population where its mechanism applies at
the moment the mechanism is identified — not after a null forces it. C7 should
have been stated as a claim about changes that introduce package-level state as
soon as the single-thread mechanism was read out of the output.

---

## 22. A benchmark built from scraped human comments must be classified before it is counted

Stage 6 scored fifteen reviewing arms against 24 human review threads and got
zero coverage everywhere. That looked like a reviewer failure until the answer
key was read item by item.

Only 5 of the 24 threads were substantive issues visible in the diff. The rest
were local convention preferences, formatter complaints, pasted benchmark
output, or process discussion. Those may be useful human review comments, but
they are not all defects a diff-only reviewer should be expected to rediscover.

This invalidates any metric that treats "human thread count" as "defect count"
without classification. It also explains why the arms could have high precision
and zero coverage at the same time: they were finding real issues that were not
on the scraped scoreboard.

**Rule for Atom.** Before scoring against review-history output, classify each
key item by reachability and by kind. If the benchmark contains process chat,
tooling requests, local convention preferences, or copied diagnostic output,
report those classes separately. Do not mix them into a defect-recall measure.

---

## 23. A judge-free proxy must be validated against the construct before it is trusted

Stage 6 had a judge-free check that appeared to say a checklist rule fired in
12 of 15 runs. The strict judge said it fired in 0 of 15. Both were right about
what they measured.

The proxy detected the topic: arms used words like package-level or global. The
rule required a specific argument: that new state should be a field or injected
dependency. The arms raised the same syntax for different reasons, usually
concurrency safety, so the topic was present and the rule was absent.

Finding 19 remains right: prefer observables that do not require a judge. The
addition is that the observable must be checked against the construct once
before it becomes a metric. Otherwise a precise, reproducible proxy can measure
something adjacent with complete confidence.

---

## 24. A control or new defect must be findable before its absence can measure anything

Stage 7 included two controls intended to test whether longer checklists crowd
out unguided attention. They scored zero in every condition, including the
seven-rule baseline. A floor cannot discriminate. Their decline could never
have been observed, because there was nowhere lower to go.

Stage 8 added a findability gate before the main run: give reviewers only the
rules that target the new defects, then require each new defect to be found in
at least two of three runs. The gate caught two unfindable defects before the
main run and forced the limitation into the record.

**Rule for Atom.** Before using a control, planted defect, or newly introduced
answer-key item to measure a treatment, prove that it is detectable under a
condition where it should be detected. If it is not findable there, it cannot be
used to interpret a null elsewhere.

---

## 25. Per-change rule selection favours lexical cues, not necessarily useful rules

The model selector in Stage 7 was better than random. It recovered curated rules
at 6.9x chance and made stable choices across five independent runs. That makes
the failure more informative, not less.

It consistently chose rules whose trigger was visible as text in the diff: a
shared data structure, an outbound call, a status switch. It consistently missed
rules about shape and comparison with neighbouring code: function size, single
responsibility, and local consistency. Those missed rules are exactly the ones a
reviewer needs prompting to apply, because no token in the changed text points
to them.

The result refutes the cheap design "grow the rule base, then ask the model to
choose seven". The selector is drawn toward what it can already see. Curation is
still doing real work by keeping non-lexical review obligations in front of the
reviewer.

---

## 26. Reviewers report consequences, not rule violations

The extra-rules findability gate initially failed on two defects even though the
reviewers were handed the exact rules those defects violated. Both failures were
stylistic: an encoding tag and a repeated literal. Neither produced a visible
behavioural consequence. Four defects with visible consequences passed.

After one bounded repair gave the two failures real consequences, one became
strong and the other became weakly findable. That is the lesson: the reviewer is
not a checklist compliance engine. It silently applies a consequence filter.

**Rule for Atom.** Phrase checklist rules around the observable failure they
prevent, not around style alone. A rule whose violation changes nothing the
reviewer can explain is unlikely to be reported, even when explicitly present in
the checklist.

---

## 27. Stop when the arithmetic makes the experiment unable to answer its question

The extra-rules main run was stopped before twenty reviewing arms were spent.
The reason was not cost or inconvenience. The selectors had already made the
headline question impossible to answer: the six new defects targeted six
non-curated rules, and the model-selected additions overlapped them on exactly
one rule.

Running anyway would have produced a numeric result with an interpretation that
was already capped by the setup. Adding a hand-picked target arm would have been
worse: it would teach to the test by choosing rules because they match defects
that were planted for them.

A pre-run planning result can be decisive evidence. When it shows that the
measurement cannot move enough to answer the registered question, the correct
response is to stop and write that down, not to spend the main run for the sake
of having a table.

