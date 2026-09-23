---
phase: phase-06-state
artifact: findings
status: ran
---

# Findings — Phase 6: `state`, derived

## 1. A design spec is a prediction, and this one was wrong five times

Atom's whole argument is that a design document is a *prediction* and a POC is
an *observation*, which is why Atom runs code before it writes specs. Phase 6
turned that argument on its author. The POC was run, the evidence was
collected, the spec was written from it — and implementing that spec still
found **five** defects in it.

| # | Defect | How it was found |
|---|---|---|
| 1 | B172 folded `module_path` into `state.json`, silently repealing Phase 3's B73 | An implementer flagged it as "the only ambiguity" — and resolved it toward the wrong shape |
| 2 | B183 described what `Project` keeps in a way that read as exhaustive; an implementer deleted the working event log | Probing the implementation's diff |
| 3 | B168/B170 asked for *less* the more ignorant Atom was: an unrecognised status token required 7 artifacts, a wholly absent report required 6 | Printing the counts for three phases side by side |
| 4 | B158 said phases live in `specs/<project>/` but never defined how `<project>` is resolved | Writing the CLI layer and needing the actual path |
| 5 | B163 cross-referenced B172 (the approvals record) when it meant B177 (naming the resolution source) | A programmatic check of every citation |

Defects 1 and 2 matter most, because in both cases **the spec error was
becoming a code error through a competent implementer doing exactly as told.**
Defect 1 was even correctly identified as ambiguous by the person implementing
it, who then resolved the ambiguity in the spec's favour — which is the normal,
correct instinct, and here it propagated the mistake. That is the mechanism by
which specification errors reach production: not by being missed, but by being
noticed and deferred to.

The practice that follows: **when an implementer reports an ambiguity, treat it
as a defect report against the spec, not a question to answer.** Fix the
document and re-issue it. Answering in conversation leaves the wrong text in
place for the next reader.

## 2. The direction of a rule's error matters more than its frequency

Defect 3 is worth separating out, because the fix was not obvious and the
reasoning generalises.

Measured behaviour of the original rule:

| POC report says | Artifacts required |
|---|---|
| `skipped` (explicit) | 6 |
| an unrecognised token | **7** |
| *no report at all* | **6** |

The rule was monotonically backwards: the less Atom knew, the less it asked
for. A phase with no POC report — the state of a phase nobody has started
documenting — got the *lenient* treatment reserved for a deliberate,
justified skip.

The tempting analysis is "how often will this be wrong?" The useful analysis is
"which way is it wrong?" Over-requiring shows a developer a document they may
not owe; they resolve it by declaring the skip, which produces exactly the
record the framework wanted. Under-requiring hides a document they *do* owe,
and nothing ever surfaces it. One error self-corrects through normal use; the
other compounds in silence.

**Only an explicit `skipped` now excuses the brief.** Ignorance is treated as
"you still owe this", not as "never mind".

## 3. Completeness is not derivable, and the proof was a truncation

This was the POC's central finding (F6-1) and it held through implementation.
A real `design-spec.md` of 18,024 characters across 13 sections was truncated
to its first 4 sections — 4,215 characters — and **passed every candidate
completeness rule tested**. Structural rules were simultaneously too weak
(fooled by the truncation *and* by a headings-only outline) and too strict
(they rejected `phase-01-check/tdd-log.md`, a genuinely finished 3,377-character
document that happens to have two level-2 headings).

So Atom reports **presence, never completeness**, and the prohibition is
enforced at three levels: no such field on any dataclass (pinned via
`dataclasses.fields`), no such vocabulary in `repr`, and no such word in either
the text or JSON rendering.

The decision rule was fixed *before* the measurements arrived, which is what
makes it binding rather than a rationalisation of whatever the data happened to
show.

## 4. `mtime` was refuted as a prediction and condemned on other grounds

The POC predicted that cloning a repository would scramble directory mtimes and
break any mtime-based ordering. **That prediction was wrong** — ordering
survived 5 out of 5 clones, because git checks files out in index order, which
is lexical order. An apparent tie in the probe turned out to be float rounding
in the probe itself, not in git.

mtime was rejected anyway, for two reasons the clone test never touched:

- Editing a file *inside* a directory does not change that directory's mtime.
  Directory mtime tracks its entry list, not its contents. A phase can be
  worked on all week and look untouched.
- **Creating** any new artifact in an old phase makes that phase the newest
  immediately. Measured with the exact task that was about to be performed —
  writing this file into `phase-06-state/` — which is the kind of ordinary act
  that would have silently reordered the answer.

Worth recording that the honest outcome here was "my reasoning was wrong and my
conclusion was right." Those are separate facts and the first one does not get
quietly dropped because the second is convenient.

## 5. Re-measure before recording a finding

Three times across this project a dramatic-looking result dissolved on a second
measurement: a 44.4-second `gh` call, an `atom review` "timeout" that was
really 19.5/20.6/33.0-second latency, and the mtime "tie" above. Every one of
them would have become a permanent, confidently-worded, **false** finding in a
document like this one.

The rule that now applies: a surprising measurement is a hypothesis, not a
finding. Measure it again, by a different route if possible, before writing it
down.

## 6. Behaviour numbering has drifted across four phases and has a hole

A programmatic check of every `B`-number citation in the Phase 6 spec turned up
one broken cross-reference — and, incidentally, that the repository has two
incompatible conventions for *defining* a behaviour:

| Phase | Convention |
|---|---|
| phase-02-poc | `**Bn**` |
| phase-03-state | **both** `**Bn**` and `**Bn.**` |
| phase-04-review | `**Bn.**` |
| phase-05-ship | `**Bn.**` |
| phase-06-state | `**Bn**` |

More significantly: **`phase-01-check/design-spec.md` contains no B-numbers at
all.** Behaviours B1–B34 exist only in that phase's *test* spec, where they were
assigned retroactively. Every later phase cites them (Phase 6 cites B17) as
though they were defined in a design document, and they are not.

This is the same class of problem as the `status:` frontmatter drift found
earlier in this phase, where five phases had accumulated four different header
conventions before anyone looked. Conventions decay silently because nothing
measures them. Recorded as debt below rather than fixed here — renumbering
Phase 1 is not Phase 6's job.

## 7. The event log is silent about the only decision it still has to record

Phase 6 removed phase transitions, which were the main thing the event log
recorded. What remains is `initialised` — and nothing else. In particular
`record_approval` writes **no event**, so the log says nothing about the one
human decision the project still stores.

Found by repairing a test that used to drive the log with `advance_to`. Not
fixed here, because adding an event is a design change this phase did not
specify and the phase is already a net deletion. Recorded as F6-D3.

## 8. An exit code reserved for a condition that cannot occur

**B181** says non-zero is reserved for "a project root that cannot be read at
all", and `report.py` renders problems in red on exactly that condition, amber
otherwise. Both are unreachable.

`atom status` takes no `--root`; the root is the process's current working
directory. A running process's cwd necessarily exists and is a directory, so
`root.is_dir()` is always true and `could_answer` is always true. Measured
directly rather than argued:

| Root passed to `collect_status` | `could_answer` | problems |
|---|---|---:|
| a path that does not exist | False | **0** |
| a path that is a file | False | **0** |

The second column is the surprise. The only states that clear `could_answer`
also produce *no problems*, and the stderr renderer only runs when there are
problems — so the red branch cannot execute even when constructed by hand
through the CLI. Worse, had it been reachable, the unreadable-root case would
have exited non-zero while printing **nothing at all** to explain why.

This is the same disease as the tests removed in this phase's redundancy audit:
a branch that cannot fail is not robustness, it is decoration that tells a
reader the program handles a case it does not. Colour and exit code are both
claiming to carry a signal they never carry.

Not fixed when found — the repair was a design choice between three real options
(declare `status` a report that always exits 0 and delete the dead branch; give
`could_answer` a reachable meaning; or add `--root` so a caller can name a bad
path) and that belonged to the developer, not to the implementer who found it.
Recorded as F6-D6.

**Resolved.** The developer chose the first option. `could_answer` is deleted,
the exit is unconditionally 0, and there is a single problem colour. Three
guards now pin the *absence* of the machinery rather than its behaviour — the
report exposes no `could_answer`, the renderer never emits red, and the CLI
exits 0 across four unrelated failure shapes. Pinning an absence is the only way
this stays deleted: the original branch was invisible precisely because nothing
exercised it, so a test asserting it is gone is the thing that was missing the
first time.

A detail worth keeping: the amendment's *cost* did not change. B181 always
accepted that `status` cannot be a CI gate. What changed is the pretence that it
was one for a sliver of cases it could never reach.

## 9. The test spec drifted from the design spec that amended it

B158a was added to the design spec mid-implementation (defect 4 of §1) and
propagated to `status.py`, which implements it, and to three tests, which pin
it. It was **not** propagated to the test spec, where it had zero rows until
this reconciliation.

The mechanism is worth naming because it is not carelessness: the design spec
was amended *while* the implementation was in flight, so the amendment reached
the code by message and the document by nobody. Every artifact that was written
before the amendment stayed at the old shape.

An amendment has more than one destination. Recorded as F6-D7.

## 10. Deferred findings

| # | Where | What | Status |
|---|---|---|---|
| F6-D1 | `phase-01-check/design-spec.md` | Contains no B-numbers; B1–B34 are defined only in its test spec, yet cited by every later phase as design behaviours | Pending |
| F6-D2 | all design specs | Two incompatible behaviour-definition conventions (`**Bn**` vs `**Bn.**`); nothing checks them | Pending |
| F6-D3 | `state.py` | `record_approval` emits no event, leaving the log silent about approvals (see §7) | Pending |
| F6-D4 | `phases.py` | B158a resolves multiple candidate project directories by taking the lexically first and reporting a problem; never exercised in a real multi-project repo | Pending |
| F6-D5 | project-wide | No check that a cited `B`-number resolves to a definition; defect 5 was found by an ad-hoc script, not by anything repeatable | Pending |
| F6-D6 | `status.py`, `report.py` | `could_answer` is unreachable from the CLI, making B181's non-zero exit and the red rendering dead (see §8) | **Resolved** — developer chose "status is a report": `could_answer` deleted, exit always 0, one problem colour; B181 amended |
| F6-D7 | `phase-06-state/test-spec.md` | B158a reached the code and the tests but not the test spec; a mid-flight amendment has more than one destination (see §9) | Fixed in this phase |
| F6-D8 | `status.py` | B179 does not say whether the `artifacts` JSON key is all seven names or only the required subset; the full map was chosen and the count put in `phases[].required` | Pending |
| F6-D9 | `status.py` | "a root that cannot be read at all" was implemented as `is_dir()`, so a permission-denied but existing directory would still report readable; not portably testable on Windows | Pending |
| F6-D10 | `status.py` | **Resolved — see §12.** Recorded as leniency about the flat layout; measurement showed the important half was elsewhere. The flat layout is now a declared, supported, silent case; a project directory *beside* loose phase directories is reported | Resolved |

## 11. The review gate found what two readings and 727 tests did not

The Phase 6 review gate ran two models three times each — 6/6 runs completed,
one reply unparseable — over a 32-file, +6415/−445 diff. It produced five
finding groups. Every one came from a single model (`gpt-5.4`); the other model
found nothing in three runs, and most findings appeared in only 1 of 3 runs.

**A 1-of-3 finding from one model is a weak signal that still has to be
checked.** Three of the five were real defects. Had the count been treated as a
confidence score and the low-agreement ones discarded, all three would have
shipped. The correct use of repetition is the opposite of a vote: it widens the
net, and the reader does the judging against source.

The three that were real:

| # | Defect | Why it was invisible before |
|---|---|---|
| 1 | A version-1 `state.json` was reported as *"missing required key"* | The code carried a recorded rationale for not migrating v1, which was correct. It answered "should we migrate?" and never asked "what do we *say*?" A defence written for one question reads as settled for a neighbouring one. |
| 2 | `{}` in `approvals` became `Approval("", "", "")` | Non-dict entries raised a problem, so the surrounding code *looked* careful. `str(entry.get(name, ""))` reads as defensive and is the opposite: it cannot fail, so it cannot report. |
| 3 | Only the *current* phase's status problems were reported | Flagged independently at two call sites. The behaviour was deliberate enough to be commented, and the comment cited B166 (missing artifacts) to justify scoping a rule that B180 (every problem is reported) governs. **A citation to a nearby behaviour is how a gap acquires the appearance of a decision.** |

Defect 2 is the same shape as §8's unreachable exit code, inverted: there, a
branch that could never run; here, a coercion that could never complain. Both
are code that performs diligence without exercising it.

### The version field does not do the job it was added for

B172 specifies `"version": 2` in `state.json`. Implementing the v1 message
showed the field cannot detect a v1 file: **the version-1 writer emitted no
version key at all** (`{"phase": ..., "status": ...}` and nothing else).
Recognition has to go by v1's own fields. The version number is useful only for
a future v2→v3 move — that is, a version field is worth nothing until the
*second* time it is needed, and the migration everyone actually has to handle is
the one from before it existed.

### A guard that passes on the first run is not yet a guard

The first version of `test_an_outdated_state_file_is_not_called_corrupt`
asserted the message contained neither `"corrupt"` nor `"unusable"`. It passed
before the fix, because the pre-fix message said neither — it said *"missing
required key"*. The test named words the code never used, so it could not fail,
and it was caught only because the red run was read for *which* tests failed
rather than for the count. **In TDD the red run is the assertion about the test;
a new test that passes immediately has told you something, and it is not good
news.** Rewritten to name the actual pre-fix wording.

### What was fixed and what was not

| Finding | Verdict | Action |
|---|---|---|
| v1 file called corrupt | Real, mis-stated | Fixed — `_outdated_file_problem` names it and says to delete it |
| `{}` becomes a blank approval | Real | Fixed — every field must be present *and* a string |
| Problems scoped to the current phase | Real (two sites) | Fixed — `derive` collects across all phases, which is safe because every message is already phase-prefixed |
| `specs/` fallback when no project dir | Low | Deferred as F6-D10 — later measured and resolved, see §12 |



- **When an implementer reports an ambiguity, fix the document, not the
  conversation.** An ambiguity resolved in discussion leaves the defective text
  in place for the next reader. Two of this phase's five spec defects reached
  code that way.
- **A removal list must name what goes.** It must never be inferable from what
  a summary happens to mention, because a reader will reasonably treat the
  summary as exhaustive and delete the remainder.
- **Ask which way a rule fails, not how often.** Prefer the error that
  self-corrects through ordinary use over the error that hides.
- **Fix the decision rule before the data arrives.** It is the only thing
  separating a finding from a rationalisation.
- **A surprising measurement is a hypothesis.** Measure again before recording.
- **Conventions decay silently.** Anything not mechanically checked will
  accumulate variants — four `status:` header styles, two behaviour-numbering
  styles, one phase with no numbers at all.
- **"My reasoning was wrong and my conclusion was right" is a normal result.**
  Record both halves; dropping the first is how a lucky guess becomes received
  wisdom.
- **Read the red run for names, not for a count.** A new test that passes on its
  first run is not a guard yet — it is a sentence about words the code never
  said.
- **Agreement between reviewers is not confidence.** A finding one model raised
  once in three runs was a real defect three times over. Repetition widens the
  net; it does not rank what the net catches.
- **A recorded rationale settles the question it was written for and no other.**
  The v1 comment correctly argued against migrating and was silently read as
  having also decided what to *say* about a v1 file.
- **A citation to a nearby behaviour is how a gap acquires the look of a
  decision.** Scoping problems to the current phase cited B166, which is about
  missing artifacts, while B180 actually governed it.
- **Code can perform diligence without exercising it.** A branch that cannot run
  and a coercion that cannot complain are the same defect facing opposite ways.

## 12. F6-D10: the recorded half of a finding was the less important half

F6-D10 was filed as leniency: `_resolve_project_dir` falls back to `specs/`
itself when no child holds a phase, so the pre-B158a flat layout is accepted
without comment. Rather than argue about whether that leniency was wanted, four
layouts were built and measured:

| Layout | Resolves to | Phases found | Problems |
|---|---|---|---:|
| A -- flat `specs/phase-01-a`, `phase-02-b` | `specs/` | both | 0 |
| B -- nested `specs/proj/phase-*` | `proj` | both | 0 |
| **C -- mixed: `specs/proj/phase-05-e` plus loose `phase-01-a`, `phase-02-b`** | `proj` | **only `phase-05-e`** | **0** |
| D -- two project directories | `alpha` | alpha's only | 1 |

Row A is the filed finding, and on inspection it is fine: with nothing to be
ambiguous with, a flat tree has exactly one reading. Row C is the defect. Two
phases vanish from the report and nothing is said -- not leniency but silent
data loss. It is also inconsistent with row D, where the code already treats
"I had to choose" as reportable; a candidate beside loose phases is the same
ambiguity wearing different clothes. And a mixed tree is precisely what a
half-finished migration to B158a looks like, which is the moment a developer
most needs to be told what is being ignored.

Resolution: the mixed layout is reported as a problem naming every ignored
directory and what to do about it, with the project directory still used so
`status` still answers; the flat layout is now declared supported and stays
silent. B158a amended in the design spec and the test spec; three tests added,
two of them guards that the flat and nested cases stay quiet.

**Learning.** *A finding is a report of a symptom, not a description of the
defect.* This one named a real behaviour, explained it accurately, and pointed
at the least interesting instance of it. Building the neighbouring cases cost
ten minutes and moved the finding from "developer decision about a preference"
to "two phases disappear without a word."
