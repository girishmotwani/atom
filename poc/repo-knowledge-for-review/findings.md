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
