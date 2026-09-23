---
project: "atom-cli"
phase: "phase-06-state"
date: "2026-09-23"
status: "predictions recorded before the spike ran"
---

# POC Brief — Phase 6: `state`, derived

The phase plan scores this phase's uncertainty as "undecided", having retired
the "justifiably skipped" column after it went **0 for 3**. This brief gets no
benefit of the doubt either: Phase 5 looked certain and produced three defects,
two of them found after the spec was written.

## Why this brief is written before the spike

A prediction recorded after the fact is not a prediction. The value is that the
run can *disagree* with what is written here — so it is written first, with
confidence stated honestly, including where the honest answer is "no idea".

## Environment as found

The decisive advantage of this phase: **the repo already contains five worked
examples whose correct answers are known.** The derivation can be graded.

| Phase | Artifacts present | Known-correct answer |
|---|---|---|
| `phase-01-check` | decisions, design-spec, findings, tdd-log, test-spec | shipped, complete |
| `phase-02-poc` | full set | shipped, complete |
| `phase-03-state` | full set | shipped, complete |
| `phase-04-review` | full set | shipped, complete |
| `phase-05-ship` | decisions, design-spec, findings, poc-brief, poc-report, test-spec | shipped, complete |

Two irregularities are already visible without running anything, and both were
put to the developer before this brief was written:

- **`phase-01-check` has no `poc-report.md`** — its POC was deliberately skipped.
  Agreed: a justified skip must still produce a `poc-report.md` that records the
  skip and its reasoning, so that absence is always *stated* and never inferred.
- **`phase-05-ship` has no `tdd-log.md`** — the orchestrator never wrote one.
  Agreed: `tdd-log.md` is required, and TDD-completion derives from it.

Both gaps are therefore **artifact debt to be repaid**, not rules to be bent.

| Fact | Value | Why it matters |
|---|---|---|
| Tests location | `tools/tests/`, flat, per-module | Tests are **not** in phase directories. "Has a test suite" is not derivable from the phase directory alone. |
| Current branch | `phase-05-ship` | The branch-name rule has exactly one real branch to resolve against. |
| `.atom/state.json` | written once by `atom init`, `.gitignore`d | The file the phase exists to fix. |

## Questions and predictions

| # | Question | Prediction | Confidence |
|---|---|---|---|
| Q1 | With the agreed required set, how many of the five phases derive as complete **before** the debt is repaid? | 3 of 5. Phase 1 fails on the missing `poc-report.md`; Phase 5 fails on the missing `tdd-log.md`. | High |
| Q2 | Is a **half-written** `design-spec.md` distinguishable on disk from a finished one? | **No idea.** File existence certainly cannot tell them apart. Whether section-presence can is the real question, and I do not know. | **None** |
| Q3 | Does "newest phase directory" derive stably from **mtime**? | No. A fresh `git clone` or branch checkout rewrites mtimes, so mtime ordering is an artefact of filesystem history, not project history. Lexical ordering on the `phase-NN-` prefix should be stable. | Medium-high |
| Q4 | Do all five `design-spec.md` files share enough structure for a section-presence rule to work? | Yes — every one should carry a `## Purpose` or equivalent heading. | Medium |
| Q5 | Does the branch-name rule resolve on a non-phase branch such as `main`? | It returns nothing and the fallback takes over. The interesting case is a branch like `phase-06-state` whose directory exists but holds only a brief. | Medium |

## Why Q2 and Q3 carry the weight

**Q2 is the phase's stated technical risk, in one sentence.** Derived state is
only better than declared state if the derivation cannot be fooled. If a
`design-spec.md` that is three headings and a TODO derives identically to a
finished one, then `atom status` has merely moved the lie from a stale JSON file
into a confident-looking computation — which is worse, because a stale file at
least looks stale. The spike therefore **truncates a copy of a real spec** and
checks whether any candidate rule notices.

**Q3 is a correctness trap that unit tests would never catch.** Every test in
this suite builds fixtures with `tmp_path`, writing files in a deliberate order
— so mtime ordering is always *correct in tests* and potentially meaningless on
a real clone. This is precisely the shape of the five previous phases' failures:
a mocked environment supplying a property the real environment does not have.
The spike measures mtime ordering on a **fresh clone** of this repo.

**Q1 is graded, not estimated.** The prediction is cheap to make because the
directory listing is already visible. Its value is different: it fixes, in
advance, that the derivation is expected to *fail* on two phases, so that a rule
set which reports 5 of 5 is treated as a **bug in the rules**, not a success.

## Decision rule — fixed before the data arrives

Recorded in advance so the numbers choose the design rather than the reverse.

| Outcome | Consequence for the design |
|---|---|
| Q2: no candidate rule distinguishes truncated from finished | Completion of a *document* is not derivable. The design must not claim it is — either the gate approval becomes the only completion signal for specs, or the rule reports "present" rather than "complete". |
| Q2: section-presence does distinguish them | The rule set uses required sections, and the required list is written into the spec rather than left implicit. |
| Q3: mtime ordering differs on a fresh clone | Ordering is lexical on the `phase-NN-` prefix, pinned by a test, and mtime is never read. |
| Q3: mtime ordering survives a clone | Still prefer lexical — but record the measurement, because "it worked once" is not a property. |
| Q1: any rule set reports 5 of 5 before the debt is repaid | The rules are too weak. Investigate before proceeding; do not accept the flattering answer. |
| Q5: a branch whose directory holds only a brief | Decide explicitly what that reports. It is the state this very phase is in right now, so the answer is checkable against a fact the developer can see. |

## Cleanup contract

The spike is read-only against the real repo: it **copies** phase directories to
a temp location before truncating anything, and clones into a temp directory for
the mtime measurement. It writes nothing into `specs/` and does not touch
`.atom/state.json`.
