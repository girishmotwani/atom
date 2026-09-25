---
project: "atom-cli"
phase: "phase-06-state"
date: "2026-09-23"
status: "ran"
spike: "poc/derived-state/spike.py, poc/derived-state/probe_mtime.py"
---

# POC Report — Phase 6: `state`, derived

The spike ran against the five real phase directories in this repository, where
the correct answers are already known. Predictions were recorded in
[`poc-brief.md`](poc-brief.md) before any of it executed.

## Scorecard

| # | Question | Prediction | Outcome | Verdict |
|---|---|---|---|---|
| Q1 | How many phases derive as complete before the debt is repaid? | 3 of 5 | 3 of 6 (`phase-06-state` now exists) — phases 2, 3, 4 | **Confirmed**, with a detail missed |
| Q2 | Is a half-written spec distinguishable from a finished one? | "No idea" | **No. Every rule is fooled.** | **Answered** |
| Q3 | Does mtime ordering survive a fresh clone? | No | **Yes — 5 clones out of 5** | **Refuted** |
| Q4 | Do the specs share usable structure? | Yes, all carry `## Purpose` | Yes, but only **two** sections are common to all | **Confirmed**, narrowly |
| Q5 | Does the branch rule resolve on a non-phase branch? | Falls back | Yes, and it exposed a hole the brief did not anticipate | **Confirmed**, plus a defect |

**Two of five predictions were wrong or incomplete.** The brief's whole purpose
was to make that visible rather than retrofit the reasoning afterwards.

## F6-1 — Document completeness is not derivable. *(the phase's central finding)*

A real, finished `design-spec.md` (18,024 chars, 13 sections) was copied and
damaged in four realistic ways. Every candidate rule was asked about each.

| Variant | R1 exists | R2 non-empty | R3 ≥1 KB | R4 ≥3 sections | R5 sections + no TODO | Size |
|---|---|---|---|---|---|---|
| **V0 untouched (control)** | PASS | PASS | PASS | PASS | PASS | 18,024 |
| **V1 first 4 of 13 sections** | PASS | PASS | **PASS** | **PASS** | **PASS** | 4,215 |
| V2 first 1 section | PASS | PASS | fail | fail | fail | 799 |
| **V3 headings only, no prose** | PASS | PASS | fail | **PASS** | **PASS** | 628 |
| V4 heading + `TODO` | PASS | PASS | fail | fail | fail | 32 |

**V1 passes every rule.** A spec abandoned a third of the way through — no
truncation marker, no placeholder, four complete and well-written sections —
is indistinguishable from a finished one by any rule tested.

This is the answer the brief's decision rule was written for, so the consequence
is already fixed and is not being chosen after seeing the data:

> *"Completion of a document is not derivable. The design must not claim it is —
> either the gate approval becomes the only completion signal for specs, or the
> rule reports 'present' rather than 'complete'."*

The design must therefore report **presence**, and must not use the word
*complete* about any document it has not been told is complete.

## F6-2 — The structural rules are simultaneously too weak and too strict

R4 and R5 were the sophisticated candidates. They fail in both directions at once:

- **Too weak:** fooled by V1 *and* by V3, an outline with every word of prose
  deleted. R3 — an arbitrary byte floor with no understanding of markdown at all
  — was fooled by only **one** variant. The structural rules lost to a constant.
- **Too strict:** `phase-01-check/tdd-log.md` is a **genuine, finished** 3,377-char
  document with only **two** level-2 sections. R4 and R5 both reject it. They
  report a real, complete artifact as missing.

A rule that accepts a truncated document and rejects a complete one is worse
than no rule, because it is confidently wrong in both directions. **The threshold
was not tuned badly; the quantity is not measuring the thing.**

## F6-3 — mtime: prediction refuted, conclusion confirmed, reasoning wrong

The brief predicted mtime ordering would not survive a clone. It survived **5 of
5** clones, with nanosecond-distinct timestamps in lexical order — because git
checks files out in index order, which *is* lexical. An apparent tie at 4-of-5
distinct was chased down and proved to be **float rounding in the probe itself**,
not a real tie. The prediction was simply wrong.

Two further measurements then condemned mtime anyway, for reasons the brief
never considered:

| Action | Effect on directory mtime |
|---|---|
| Editing the contents of an existing artifact | **None.** `phase-02-poc` stayed in place after `findings.md` was modified. |
| **Creating** a new artifact in an old phase | **Becomes the newest phase immediately.** |

The second was measured using **the exact task this phase is about to perform**:
writing the owed `phase-01-check/poc-report.md` makes Phase 1 — the oldest,
long-shipped phase — report as the *current* phase.

So mtime is both **too insensitive** (a whole spec can be rewritten without
moving it) and **too sensitive** (repaying old documentation debt reorders
everything). It is unusable. The brief's pre-recorded rule already said prefer
lexical regardless of the clone result, so the design is unaffected — but it
would have been right **by luck**, and that is worth stating plainly.

> **Lesson:** a prediction can be refuted and still lead to the correct design.
> That is not vindication. The reasoning was wrong, and the next prediction
> built on the same reasoning would have failed.

## F6-4 — APIs have now lied twelve times

**Directory mtime does not change when a file inside it changes.** It tracks
entries — creations, deletions, renames — not content. The name says "modified
time" and it is not the time the directory's contents were last modified. Anyone
using it as "when did work last happen here" gets a wrong answer silently.

## F6-5 — Only two sections are common to all five specs

| Phase | Sections | Chars |
|---|---|---|
| `phase-01-check` | 12 | 12,882 |
| `phase-02-poc` | 10 | 21,556 |
| `phase-03-state` | 10 | 15,196 |
| `phase-04-review` | 13 | 18,024 |
| `phase-05-ship` | 13 | 15,186 |

Common to **all**: `Purpose`, `Evidence Base`. Nothing else. Any required-section
rule can demand at most those two — which V1 and V3 both satisfy. This is an
independent route to the same conclusion as F6-1.

## F6-6 — The branch rule resolves to directories that do not exist

The agreed rule is branch name first, newest phase directory as fallback.

| Branch | Resolves to | Via |
|---|---|---|
| `phase-05-ship` | `phase-05-ship` | branch name, directory exists |
| `main` | `phase-06-state` | fallback, lexical |
| `phase-06-state` | `phase-06-state` | branch name, directory exists |
| **`phase-09-ghost`** | **`phase-09-ghost`** | **branch name, no such directory** |
| `scratch/experiment` | `phase-06-state` | fallback, lexical |
| *(detached HEAD)* | `phase-06-state` | fallback, lexical |

A branch named after a phase that has no directory resolves to a phase that does
not exist. The design must decide explicitly whether that is an error or a
legitimate "not started" — it is a real state, not a hypothetical: it is the
state `phase-06-state` was in ten minutes before this spike ran.

## F6-7 — Q1's missed detail

The prediction named `phase-01-check` as failing on the missing `poc-report.md`.
It is also missing `poc-brief.md`. Repaying that debt means writing **both**: the
questions that were not asked, and the record of why they were not.

## F6-8 — The spike's own cleanup failed

`shutil.rmtree(..., ignore_errors=True)` reported `scratch removed: False` —
Windows holds handles on cloned `.git` object files. Harmless here (temp
directory), but a tool that clones and cleans up must not assume `rmtree`
succeeded just because it did not raise. `ignore_errors=True` converts a failure
into a silent one.

## What the design must now take as given

1. Report **presence**, never document "completeness" — F6-1.
2. Do not count sections or bytes as a proxy for done — F6-2.
3. Order phases **lexically** on the `phase-NN-` prefix. Never read mtime — F6-3.
4. Two required sections is the most any structural check could demand, which is
   not enough to be worth having — F6-5.
5. Decide explicitly what a phase branch with no directory reports — F6-6.
6. Repay `phase-01-check/poc-brief.md`, `phase-01-check/poc-report.md`, and
   `phase-05-ship/tdd-log.md` before deriving anything — F6-7.
