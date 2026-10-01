# POC brief: can a symbol lookup tool help an agent find the files a repair touches?

Written before any call in this experiment was made. Nothing below was chosen
after seeing a result.

## The question

When an agent is asked which files a repair must change, it searches for the
words in the repair request. Files that must change but never mention those
words are reached only by following the names declared in the files that do.

Two things could fix that. The agent could be **told** to work outward that way.
Or it could be **given a tool** that makes working outward cheap. This
experiment separates the two, because if the advice alone is what helps, the
tool is not worth building.

## What we already know

From the previous experiment on the same twenty repairs:

| Setup | Finds | Of its guesses, correct | Files named |
|---|---|---|---|
| One run of plain search | 0.723 | 0.648 | 21.6 |
| Three runs merged | 0.788 | 0.571 | 32.4 |
| Five runs merged | 0.824 | 0.534 | 39.2 |

Merging runs is the largest effect found so far. **That makes three-runs-merged
the number to beat, not 0.723.** Comparing a three-run treatment against a
one-run baseline would credit the merge to the tool.

Two earlier ideas were refuted on this same benchmark: predicting a repair's
reach from its description, and giving the agent a written guide to the
repository. Both are forms of preparing context in advance. This experiment
tries the opposite -- changing how the agent looks things up while it works.

## The three arms

All three get the same repair request, the same snapshot, and the same answer
format. They differ only as follows.

| Arm | Tools | Prompt |
|---|---|---|
| **A: plain** | built-in read and search | unchanged |
| **B: symbol-walk** | built-in read and search | plus a four-step instruction to work outward from the files it finds |
| **C: symbol-index** | built-in, plus a symbol lookup tool | the same four-step instruction, plus how to use the tool |

B and C share the wording of the four steps exactly. They differ only in how
steps two and three are carried out -- by opening files and searching in B, by
one command in C. Any difference between them is therefore attributable to the
tool rather than to the advice.

**A versus B** answers: does the advice alone help?
**B versus C** answers: does the tool add anything beyond the advice?

A is re-run rather than reused from the earlier experiment, because the CLI and
the model behind it move over time and a stale baseline would be unreliable.

## The tool given to arm C

A symbol index built ahead of time from the snapshot, queried by a script the
agent runs:

- `symbols-in <file>` -- what a file declares
- `neighbours <file>` -- files that use what it declares, ranked by how many
- `who-uses <symbol>` -- files mentioning a symbol
- `where-defined <symbol>` -- where a symbol is declared

It is built by parsing every Go file with Go's own parser, at syntax level only.
It does not type-check and does not resolve imports, because a snapshot of one
subtree generally will not build.

It knows one thing text search cannot: Go ties visibility to capitalisation, so
a lower-case name in a different package is a different symbol. On a sample
snapshot that rule removed about 19,500 name collisions and cut one query's
results from 40 files to 5, without losing the real callers.

**Honest limitation:** matching is still by name, not by resolved identity. Two
unrelated types with a method of the same name are indistinguishable. The tool
produces leads, not proof.

## Procedure

- The same 20 repairs, each touching 10 or more files, used in both earlier
  experiments.
- 3 arms x 3 runs each = **180 calls**.
- Arm C runs against a separate copy of each snapshot that carries the index.
  Arms A and B run against copies without it, so they cannot stumble on it.
- Scoring is unchanged from the earlier experiments: the agent's answer is
  compared against the files the real commit actually changed.

## How it is scored

Three runs per arm give a vote count for every file: how many of the three runs
named it. That makes two comparisons possible.

**Primary -- recall at a matched list length.** Rank each arm's files by vote
count and take the top 32, which is the length plain search reaches when three
runs are merged. Report the share of the real answer found. Ties in vote count
are broken by random shuffle, averaged over 20 draws with a fixed seed.

This is the primary measure because a lookup tool can inflate recall simply by
naming more files. Holding list length equal removes that explanation before it
can be offered.

**Secondary -- the merged result as a developer would receive it.** Files named
by at least one of the three runs: recall, share of guesses correct, and list
length.

## The bar, set in advance

Applied to the primary measure, arm C against arm A:

- **+0.05 or better** -- confirmed, worth building on.
- **+0.02 to +0.05** -- promising, but needs a fresh set of repairs before it
  can be believed.
- **below +0.02** -- refuted.

Why 0.05: re-drawing which three of five runs get merged moves the whole
experiment's score between 0.772 and 0.804, a spread of 0.033. A real effect
should be clearly larger than that. This spread is a floor rather than a full
estimate of noise, because those re-draws share runs with each other.

Arm B is reported against arm A on the same scale, and arm C against arm B.

## What would make this wrong

- The twenty repairs were chosen for an earlier experiment. They are all from
  one repository and all from Go. Nothing here generalises beyond that without
  a fresh test.
- The tool was built by the same person running the experiment, who could have
  tuned it to this benchmark. It was checked on one snapshot for sanity only,
  without reference to the correct answers.
- A result between +0.02 and +0.05 means the experiment did not settle the
  question, and must be reported that way rather than rounded up.
- If arms B and C both beat A by similar amounts, the advice is the whole
  effect and the tool should not be built.

## Recorded deviations

None yet. Anything that changes after the first call is made gets written here,
with the reason and the time it was decided.
