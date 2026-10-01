# TDD Log — Phase 6: `state`, derived

A record of how the code was built, kept because the order things happened in is
itself evidence.

Four cycles, run as two pairs. The phase's defining fact is that it produced
**seven defects in its own design spec, every one of them found by implementing
it** — none by reading it, including the two readings that went looking for
exactly this.

Suite: **618 before the phase, 727 after.**

| Cycle | File | Tests | Coverage | Commit |
|---|---|---:|---:|---|
| 1 | `phases.py` | 68 | 100% | `2615fc5` |
| 2 | `state.py` | 24 | 100% | `b92a1fd` |
| 3 | `status.py` + `report.py` renderers | 40 | 100% | working tree |
| 4 | `cli.py` | 30 | — | working tree |

---

## Cycles 1 and 2 — run in parallel on disjoint files

`phases.py` (derivation) and `state.py` (the approvals record) touch no shared
code, so they were built concurrently by two agents with an explicit file
ownership split. The split held: neither agent's commit contains a line from the
other's file.

**RED.** 68 tests for derivation, 24 for the record.

**GREEN.** `phases.py` derives the phase from the branch and the directory
listing and refuses to judge what it finds. `state.py` loses the `Phase` enum,
the `Status` enum, `phase_index`, `next_phase`, `InvalidTransition`, and the
transition logic — the phase is a net deletion of a state machine.

**The check that mattered was not a test.** Whether any dataclass still carried a
completeness field was verified by reflecting over `dataclasses.fields` for
`Phase`, `PhaseArtifacts` and `Derivation`, rather than by reading the source and
concluding it looked absent. The field genuinely does not exist, and that is now
established by something other than an assurance.

### Three defects found here, all by implementation

1. **B172 contradicted Phase 3's B73** by merging `module_path` into
   `state.json`. The implementing agent found it, called it "the only
   ambiguity", and then **resolved it toward the spec** — which was wrong. This
   is worth dwelling on: the agent did everything right, reported the conflict,
   and still produced wrong code, because a reported ambiguity that is answered
   in conversation leaves the defect in the document. The practice that came out
   of it is A-5 in `decisions.md`.
2. **B183 read as an exhaustive removal list** and an implementer deleted the
   working event log. It was not exhaustive; it was a summary. Rule adopted: a
   removal list must **name** what goes, and must never be inferable from what a
   summary happens to mention.
3. **B168/B170 leaned the wrong way** on a missing POC report. Resolved on the
   direction of the error rather than the frequency — see P6-3.

---

## Cycle 3 — `status.py` and the three renderers

**RED.** 40 tests: 22 named output tests, 2 for the B184 sweep, 1 prohibition
test, and 15 for branches, defaults and enrichment.

**GREEN.** `collect_status` assembles the report; three renderers in `report.py`
turn it into text, JSON and the stderr problem block.

**Two more defects, both found while writing the layer above:**

4. **B158 never defined how `<project>` resolves** under `specs/`. The spec said
   phases live in `specs/<project>/` and stopped. Added as **B158a**, and the
   implementing agent was told mid-flight.
5. **B163 cited B172 where it meant B177.** Found by extracting every `B`-number
   citation programmatically and checking each resolved to a definition — not by
   reading. Nothing in the repository does this check routinely, which is F6-D5.

**The JSON contract test asserts a subset, not equality.** B179 names eight keys;
B183 independently requires `last_event` and damaged-line reporting survive. An
equality assertion would have made B183 unimplementable, so the test pins the
eight as a guaranteed subset and `to_dict()` carries twelve. See A-2.

---

## Cycle 4 — `cli.py`

**RED.** 30 tests, including five that run the real program as a subprocess.

**GREEN.** `atom init` no longer claims a phase — it reports the module and the
approvals count and points at `atom status`. `atom status` exits 0 whenever it
could answer.

**Three tests failed against the finished code, and all three were the tests.**
Two called `record_approval(Approval(...))` when the signature is keyword-only;
one still asserted the pre-B181 non-zero exit on a corrupt state file. Fixing
tests rather than code is usually the wrong instinct, so each was checked against
the spec first: B181 is explicit that a damaged state file is a *reported
problem*, not an unreadable root, and the keyword-only signature is what the
committed `state.py` actually exposes.

---

## The measurement that ended the phase

Six phases of this project have now shown that a green suite does not prove a
program runs. Phase 1: 55 green, unbuildable. Phase 2: 169 green, `NameError`.
Phase 3: 273 green, overlapping messages. Phase 4: 482 green while `atom review`
produced no review. Phase 5: 595 green and a clean `--help`, crashing on first
real invocation.

So 727 green ended nothing. The phase ended when the program was run:

```
$ python -m atom.cli status --no-colour
Project: C:\Users\dev\work\atom
Phase:   phase-05-ship (resolved from the git branch)
Artifacts:
  [x] poc-brief.md   [x] poc-report.md   [x] design-spec.md
  [x] test-spec.md   [x] tdd-log.md      [x] findings.md   [x] decisions.md
Other phases:
  phase-01-check   6/6      phase-02-poc     7/7
  phase-03-state   7/7      phase-04-review  7/7
  phase-06-state   5/7
No problems found.
EXIT=0
```

The baseline it had to beat was `Phase: unknown`, exit 1. The JSON surface was
run separately and parsed, rather than eyeballed: 13 keys, `phase_source`
`branch`, six phases, no problems.

`phase-01-check` reading **6/6** rather than 6/7 is P6-3 working — that phase
declared its POC skipped, and the only thing that excuses a missing POC report is
that explicit declaration.

## Two defects found after the code worked

6. **The test spec never received B158a.** The amendment reached `status.py` and
   three tests and stopped. An amendment has more than one destination
   (`findings.md` §9).
7. **B181's non-zero exit is unreachable**, and so is the red problem rendering
   tied to it, because the root is always the working directory. Measured:
   `could_answer` is false only for inputs that also produce **zero** problems,
   so the red branch cannot execute. Left unfixed on purpose — the repair is a
   design fork belonging to the developer (A-6, F6-D6).

The seventh is the phase's sharpest lesson. This phase also added a framework
rule that a branch which cannot fail is decoration rather than robustness. It
was written about tests, on the same day, and the production code shipped with
an instance of exactly that shape sitting in it — found only because a
subordinate agent's report was checked instead of believed.

## Cycle 5 — three defects the review gate found

The gate ran after the phase was believed finished: two models, three runs each,
6/6 completed, over 32 files and +6415/−445 lines. Five finding groups, three of
them real. The cycle that followed was ordinary TDD, with one instructive
stumble.

**Red.** Fifteen tests written first across `test_state.py` and
`test_phases.py`. Nine failed, six passed — and the six were deliberate guards
against over-correcting (a clean tree must still report no problems; the current
phase's problem must not be double-counted; well-formed approvals must still
load). But one of the nine *intended* failures passed as well:
`test_an_outdated_state_file_is_not_called_corrupt` forbade the words
`"corrupt"` and `"unusable"`, and the pre-fix message used neither — it said
*"missing required key"*. The test named vocabulary the code never had, so it
could not fail. Rewritten to forbid the actual pre-fix wording, at which point
it failed properly. **Reading the red run for which names appear, rather than
for how many, is what caught it.**

**Green.** Three changes:

| File | Change |
|---|---|
| `state.py` | `_outdated_file_problem` recognises a version-1 file by its own fields and says to delete it, instead of reporting a missing key |
| `state.py` | An approval's `phase`, `gate` and `date` must each be present *and* a string; `{}` is a reported problem, not a blank record |
| `phases.py` | `derive` collects problems from every phase, not only the current one — safe because every message is already phase-prefixed |

**Verified.** 742 passing (727 + 15). Then — because six phases have now shown
that a green suite does not mean a working program — all three paths were driven
through the real CLI against a scratch project holding a broken non-current
phase, a v1 state file, and a malformed approval. Each produced its intended
advisory, and the pre-existing output was unchanged on the real repository:

```
2 problems reported below.
Advisories:
  - phase-01-old: poc-report.md declares an unrecognised status 'wibble'; poc-brief.md is treated as required.
  - ...\.atom\state.json is a version 1 state file, written before phases and statuses were derived rather than stored. Nothing in it needs rescuing: delete the file and Atom will treat the project as having no recorded approvals.
```

The first line is the fix that matters most: before this cycle, `phase-01-old`
was rendered in the phase list with no indication that its report could not be
read.

## Cycle 6 — deleting the exit code that could not fire

The developer resolved F6-D6 by declaring `atom status` a report: it always
exits 0, and there is one problem colour. This is the first change in the phase
driven by a *decision* rather than a defect, and it is a deletion.

**Red.** Two new guards failed as intended — the report still exposed
`could_answer`, and the renderer still painted an unreadable root red. The
scenario tests that previously asserted `could_answer is True` were rewritten to
assert what actually matters (the report still answered), because an assertion
about a property being deleted has to move to the property's replacement, not
follow it into deletion.

**Green.** `could_answer` removed from `status.py`; `cli.py` returns
`EXIT_PASSED` unconditionally; `render_status_problems` reduced to one heading
and one colour. A fourth test, at CLI level, drives four unrelated failure
shapes through `main(["status"])` and asserts 0 each time *and* that stderr is
non-empty — exiting 0 must not become a synonym for staying quiet.

One test outside the changed files failed on the full run
(`test_the_default_path_without_a_specs_directory_reports_no_phases`, which
asserted `could_answer is True` in passing). **That is the argument for running
the whole suite rather than the files you touched**: the property had a reader
three hundred lines away from anything this cycle edited.

**Verified.** 744 passing. Then the real CLI against a scratch project holding
both a corrupt state file and an unparseable POC status:

```
2 problems reported below.
Advisories:
  - phase-01-old: poc-report.md declares an unrecognised status 'wibble'; ...
  - ...\.atom\state.json does not contain Atom state: expected a JSON object, found a list.
EXIT=0
```

Two genuine problems, an honest heading, and a zero exit — which is the whole
claim.

**The amendment had four destinations**, which is the F6-D7 lesson applied
deliberately rather than learned again: the design spec (B181, with the
correction recorded in place), the test spec (B181's row and its test names),
the code, and the tests.

## Cycle 7 -- F6-D10: the mixed `specs/` layout

**Red.** Three tests added to `test_status.py` beside the existing B158a cases:
a mixed tree must report the ignored loose phase directories *by name*; the
mixed tree must still report the project directory's phases; and two guards --
the flat tree and the nested tree must each stay at zero problems. Run: **1
failed, 43 passed**. The two guards passing immediately is correct here and was
checked rather than assumed: they pin behaviour that must not change, so a
guard that failed would have meant the fix had already leaked.

**Green.** `_resolve_project_dir` now scans `specs/` for phase-shaped
directories once a project directory has been chosen, and appends a problem
naming them and the directory that won. The zero-candidate branch is untouched
and stays silent. Full suite: **747 passed** (744 + 3).

**Verified by running it.** A scratch mixed-layout project was built in `%TEMP%`
and `python -m atom.cli status` run against it. The advisory appeared naming
both ignored directories, `phase-05-ship` was still reported with its artifact
list, and the exit code was 0 -- P6-5 holding under a new problem type. The
body goes to stdout and the advisory to stderr; the two streams interleaved on
screen, which was confirmed to be a display artifact by capturing them
separately, not assumed to be one.

**Four destinations** (F6-D7): design spec B158a amended in place, test spec
B158a row rewritten with the three new test names, findings §12 added and the
deferred row marked Resolved, decision P6-6 recorded.
