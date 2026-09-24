---
project: "atom-cli"
phase: "phase-01-check"
date: "2026-09-14"
---

# Decisions Log

Deviations from instructions and autonomous judgement calls made during Phase 1.

## Decisions

| # | Date | Instruction or choice point | What I did instead | Why | Raised with developer? |
|---|---|---|---|---|---|
| 1 | 2026-09-13 | Atom's stated purpose is Go development, and `go-style.md` governs generated code | Implemented the tooling in **Python** | The developer specified Python for all framework scripts. `go-style.md`'s *intent* — explicit names, real doc comments, dependency injection — was applied to the Python API | Yes — original instruction |
| 2 | 2026-09-14 | Phase 1 implementation was delegated to a background subagent | Finished the work directly after the agent stalled | The agent completed `runner.py` and `gates.py` (build/vet only) then returned an empty turn after 14 tool calls. Framework guidance is not to relaunch a failed agent | Yes — reported at the time |
| 3 | 2026-09-14 | Design spec lists five gates and a `cli.py`, but numbers no CLI behaviours | Wrote 7 CLI tests against behaviour inferred from the spec's exit-code rules (B21) and error-handling table | An untested entry point would leave the phase's only user-facing surface unverified | **Yes — resolved.** Developer directed that they be written down; added to the design spec as B28–B34 and mapped in `test-spec.md` |
| 4 | 2026-09-14 | No instruction covered CI | Added `.github/workflows/ci.yml` running tests on 3 OSes × 2 Python versions, plus a job that **re-runs the module-isolation spike** | The spike was only ever run on Windows; the design rests on its result. CI is how that evidence stays true rather than becoming folklore | **Yes — kept, approved at the Phase 1 gate** |
| 5 | 2026-09-14 | No instruction covered doc-link integrity | Wrote `tools/check_links.py` and wired it into CI | Atom's skills navigate by relative link. A broken link silently drops a discipline reference an agent was told to read. Found and verified 74 links resolve | **Yes — kept, approved at the Phase 1 gate** |
| 6 | 2026-09-14 | `pyproject.toml` referenced `../README.md` | Removed the field | It made `pip install -e .` fail outright. Recorded as finding 1 rather than silently patched | Yes — shown in session |
| 7 | 2026-09-14 | Spec does not state whether `find_poc_modules_without_go_mod` recurses | Treated only directories *directly* under `poc/` as spikes, searching `.go` files recursively inside each | A spike is one directory. Recursing to find nested spikes would report a spike's own subpackages as separate offenders | **Yes — confirmed correct by the developer at the Phase 1 gate** |

## Standing Waivers

None.

## Skipped Steps

| Step | Reason | Developer informed? |
|---|---|---|
| Phase 1 POC | Deliberately waived in `phase-plan.md`. The project-level module-isolation spike already answered this phase's only open technical question, and subprocess orchestration carries no unknown feasibility risk | Yes — recorded in the approved phase plan |
| Multi-model review of the Phase 1 diff | `atom review` is Phase 4 and does not exist yet. Phase 1 cannot use a tool it is a prerequisite for | **Yes — developer directed at the Phase 1 gate that Phase 1 be re-reviewed once Phase 4 lands.** Carried as a tracked debt below, not written off |

### Tracked debt: Phase 1 re-review

| Item | Trigger | Owner | Status |
|---|---|---|---|
| Run `atom review` over the Phase 1 diff (commit `4d8dee1` onward) | Phase 4 (`atom review`) reaching a working state | Next agent working Phase 4 | Open |

This is the bootstrap gap, and it resolves itself: the first real target for `atom review`
should be the code that could not be reviewed by it. Phase 4's own gate should not close
until this has been run.

## Gate Record — Phase 1

Reviewed with the developer on 2026-09-14. All seven decisions and both skipped steps were
walked through individually.

| Item | Outcome |
|---|---|
| Decision 3 — CLI behaviours unnumbered | Write them down; added as B28–B34 |
| Decision 7 — `poc/` recursion semantics | Implementation confirmed correct |
| Decisions 4, 5 — CI and link checker | Both kept |
| Skipped — multi-model review | Deferred to Phase 4, tracked as debt above |
| Decisions 1, 2, 6 | Already surfaced during the session |

No Pending items remain for Phase 1.

## Notes On Process Honesty

The TDD log for cycles 1–2 was written by the stalled subagent; cycles 3–5 are mine. All
five record **real observed failure output**, captured before the corresponding
implementation existed. Cycles 3–5 can be independently re-verified from git history:
the test files were written and run before the modules they import existed.

One qualifier worth stating plainly: cycles 3–5 each covered a group of related behaviours
rather than one behaviour per red-green cycle. That is looser than strict per-behaviour TDD.
Every behaviour still had a failing test before its implementation existed, but the cycles
were coarser than a purist reading of `tdd-discipline.md` would prescribe.

## Completeness Checklist

- [x] File exists
- [x] Every autonomous choice or workaround is recorded
- [x] Every skipped step has a specific, checkable reason
- [x] Developer visibility marked Yes or Pending for every row
- [x] Every Pending item names a follow-up point
- [x] Skipped steps are separated from the general Decisions table
- [x] No decision rewrites a refuted or inconclusive POC as confirmed
- [x] Process deviations in TDD granularity are stated rather than glossed

## P1-R1. Line-ending-only differences pass the fmt gate, with the cause named

**Question.** `gofmt` reports a correctly formatted CRLF file as needing
formatting. Should `atom check` fail, or ignore it?

**Options.** (a) Fail, but say line endings are the cause. (b) Ignore
line-ending-only differences and report them in the passing summary. (c) Ignore
them silently.

**Decision: (b).**

**Why not (a).** It keeps the verdict platform-dependent: the identical commit
fails on Windows and passes on Linux, because `core.autocrlf=true` is Git's
default on Windows. A gate that disagrees with CI for reasons the developer
cannot see in the code is worse than no gate. Line endings in the working tree
are a checkout policy, not a Go formatting decision, and the committed bytes --
what CI formats -- are LF either way.

**Why not (c).** Silence would hide a genuine gofmt complaint and leave nobody
to fix the underlying `.gitattributes` gap.

**Why the check is exact rather than a heuristic.** The question is never "does
this file contain CRLF" but "is that the *only* thing gofmt would change". The
file is normalised and handed back to gofmt on stdin; only an unaltered return
counts. A file that is both CRLF and genuinely misformatted still fails, pinned
by two guard tests. Anything that cannot be read or decoded is treated as a real
formatting problem -- a gate must not excuse what it failed to examine.


## P1-R2. The fmt gate is scoped to the module, like every other gate

**Question.** `gofmt -l .` walks the directory tree and so crosses module
boundaries that `go build`, `go vet` and `go test ./...` respect.

**Decision.** Exclude files that belong to a nested module -- any file with an
ancestor directory holding its own `go.mod`.

**Why.** Atom's own method puts throwaway spikes under `poc/`, each its own
module, and a spike is *meant* to be rough. Uncorrected, `fmt` was the single
gate in the set whose scope was the filesystem rather than the module under
test, so one deliberately rough spike failed the whole repository.

**Why not `go list`.** It would scope correctly, but adds a subprocess, a new
failure mode, and an argv-length ceiling the runner already documents. Walking
ancestors for `go.mod` needs no subprocess and states the intent directly.


## P1-R3. The race gate shares the test gate's evaluator

**Question.** `RaceGate` judged on exit code alone, so it reported `PASSED` for
a tree with no tests while `TestGate` reported `SKIPPED`.

**Decision.** Both call one shared evaluator.

**Why not duplicate the no-tests check into `RaceGate`.** Two copies of a rule
are two rules that will eventually disagree, which is precisely the defect being
fixed. The inconsistency was possible only because the two gates judged the same
command by different means; sharing the evaluator removes the possibility, not
just the instance.


## P1-R4. A timed-out command has its whole process tree killed

**Question.** `run` promised to return on timeout. It did not promise to return
*soon*. A `copilot` call that hung was measured taking **65 minutes against a
300-second deadline**, because `subprocess.run` kills the direct child and then
drains its pipes with no deadline of its own. A pipe reaches EOF when the last
handle to its write end closes, and the grandchildren the agent had spawned
still held one. Killing the parent closed only the parent's.

**Decision.** On timeout, kill the entire process tree, then drain the pipes
with a fixed two-second grace and return whatever arrived.

**Measured alternatives** (`poc/review-timeout/spike.py`, 3s deadline, a child
that leaves a 45s survivor behind):

| Strategy | Took | Bounded? | Output recovered |
|---|---|---|---|
| `subprocess.run` as-is | 45.6s | no | 7 chars |
| Kill the tree, then drain | **3.7s** | **yes** | **7 chars** |
| Kill the child, abandon the pipes | 5.1s | yes | **0 chars** |

**Why not abandon the pipes.** It bounds the wait just as well and needs no
platform-specific code, and it was still rejected: it throws away everything the
command had already written. For a review that stalled halfway, that partial
reply is the whole diagnosis -- it is what separates "the model was slow" from
"the model got stuck on this file". Bounding the wait by discarding the evidence
solves the symptom the defect presented with rather than the problem it caused.

**The accepted cost.** Tree kill on POSIX needs the child in its own process
group (`start_new_session=True`), which also removes it from the terminal's
foreground group -- so **Ctrl-C no longer reaches `go test`**. This was put to
the developer explicitly and accepted: an interrupt that must be issued twice is
a smaller harm than a deadline that does not hold. Windows needs no such
trade-off; `taskkill /T` walks the tree without regrouping anything.
