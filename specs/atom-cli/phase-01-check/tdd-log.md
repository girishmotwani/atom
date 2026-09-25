# TDD Log — Phase 1: `atom check`

Each row records a real red-green cycle. The "Red confirmed" column holds output actually
observed before the implementation existed — not a reconstruction.

Cycles 1–2 were run by a subagent; cycles 3–5 were run directly after that agent stalled
(see `decisions.md`, decision 2).

| Cycle | Behaviour(s) | Test added | Red confirmed (failure message) | Green confirmed | Notes |
|---|---|---|---|---|---|
| 1 | B1–B5, B17 support | `tests\test_runner.py` | `ImportError while importing test module 'C:\Users\gimotwan\work\atom\tools\tests\test_runner.py'.` | `5 passed in 0.48s` | Implemented runner primitives after import red. |
| 2 | B6–B8 | `tests\conftest.py`; `tests\test_gates.py` | `ImportError while importing test module 'C:\Users\gimotwan\work\atom\tools\tests\test_gates.py'.` | `9 passed in 0.51s` | Added FakeRunner and build/vet gates. |
| 3 | B9–B16, B18–B23, B24–B27 | `tests\test_gates.py` (appended); `tests\test_check.py`; `tests\test_report.py` | `ImportError: cannot import name 'FormatGate' from 'atom.gates'` / `ModuleNotFoundError: No module named 'atom.check'` — 3 collection errors | `48 passed in 0.48s` | Implemented FormatGate, TestGate, RaceGate, `default_gates`, `check.py`, `report.py`. |
| 4 | CLI surface | `tests\test_cli.py` | `ModuleNotFoundError: No module named 'atom.cli'` | `55 passed in 0.47s` | Implemented `cli.py` with argparse, `--json`, `--no-race`, `--no-colour`. |
| 5 | End-to-end verification | — (manual run, not a unit test) | `ERROR: Failed to build 'file:///C:/Users/gimotwan/work/atom/tools' when getting requirements to build editable` | `atom check` ran against a real broken Go module and correctly reported 2 failures with exit code 1 | Suite was fully green while the package was unbuildable. Fixed `pyproject.toml`; logged as finding 1. |

## Cycle 5 — live verification output

The unit suite proves the units. This proves the program. Run against a Go module with two
deliberate defects (unformatted source, a test asserting `2+2 == 5`):

```
atom check C:\Users\gimotwan\work\atom-demo

  PASS  build  go build ./... passed (0.5s)
  PASS  vet    go vet ./... passed (21.9s)
  FAIL  fmt    2 file(s) need gofmt: math.go, math_test.go (0.1s)

        math.go
        math_test.go

  FAIL  test   go test ./... failed with exit code 1 (4.2s)

        --- FAIL: TestAdd (0.00s)
            math_test.go:7: want 5 got 4
        FAIL
        FAIL	example/demo	0.319s
        FAIL

  SKIP  race   Race detector disabled for this run (0.0s)

  FAILED in 26.7s

EXIT CODE = 1
```

### B9 verified against the real tool

The design's most important claim is that `gofmt -l .` exits 0 while reporting unformatted
files. Confirmed directly rather than taken on trust:

```
> gofmt -l .
math.go
math_test.go

gofmt's OWN exit code = 0   <-- zero, despite 2 unformatted files
```

An exit-code-only implementation would have passed this project. `FormatGate` failed it.

## Honesty note

Cycles 3 and 4 each grouped several related behaviours into one red-green cycle rather than
one behaviour per cycle. Every behaviour had a failing test before its implementation
existed, but the cycles are coarser than strict per-behaviour TDD. Stated plainly here and
in `decisions.md` rather than presented as something it was not.

## Late cycle -- the four defects the Phase 1 review gate exposed

Run on branch `gate-honesty`, long after Phase 1 shipped. All four defects are
in `gates.py` and all four are the same failure: a gate reporting a verdict that
was not true.

**Before writing anything, two mechanics were measured rather than assumed** --
the habit that has repaid itself every cycle:

- `gofmt` reading stdin echoes the formatted source, so normalised content
  returning unaltered is a sound line-ending-only detector.
- `go list -f '{{.Dir}}' ./...` returns only the root module's directory,
  confirming that module scoping genuinely excludes nested spikes.

The second measurement then went unused: walking ancestors for `go.mod` does the
same job with no subprocess (P1-R2). Measuring an option is not a commitment to
using it.

**Red.** Nine tests: five failing, four guards passing. The four that passed did
so *vacuously* -- at that point the gate failed everything, so "still fails when
genuinely misformatted" could not have failed. They were written anyway and
re-checked after the fix, which is the only moment they mean anything. A guard
that has never been at risk of failing is a guard only by intention.

**Green.** `_evaluate_go_test_gate` extracted and shared by `TestGate` and
`RaceGate`; the no-tests scan moved from `combined_output` to `stdout`;
`FormatGate` filters nested-module files and line-ending-only differences before
reaching a verdict. Full suite **747 -> 756**.

**Verified by running it**, four ways, because a green suite has never been
sufficient in this repository:

| Real-world check | Result |
|---|---|
| CRLF project, no tests, nested rough spike | `PASS fmt` naming line endings; `SKIP test`; `SKIP race`; exit 0 |
| Badly formatted *and* CRLF file in the root module | `FAIL fmt` naming the file; exit 1 -- CRLF is not an amnesty |
| Cold module cache through full `atom check` | No chatter: the build gate warms the cache first |
| Cold cache, test gate alone via the real `SubprocessRunner` | `SKIPPED`, with the gate's own captured output holding `[no test files]` on stdout *and* `go: downloading` on stderr -- the exact input that previously produced `PASSED` |

The third row is worth keeping. The obvious end-to-end repro **did not
reproduce**, because `build` runs first and downloads the dependencies before
`test` ever runs. Reporting that as a successful verification would have been
false; the fourth row is what actually exercised the fixed path. *A repro that
passes for the wrong reason is indistinguishable from a fix, until it isn't.*


## Cycle: the timeout deadline becomes a real bound (B2a-B2c)

Run after Phase 1 shipped, against a defect found by a Phase 4 measurement.

**PROVE.** `poc/review-timeout/spike.py` reproduces the hang in 45 seconds --
the original observation took 71 minutes -- and compares three strategies side
by side. See decision P1-R4 for the table; the spike is what made the choice a
measurement rather than a preference.

**RED.** Three tests written first, each using the input the old guard lacked: a
child that spawns a survivor and exits.

| Test | Expected before the fix | Observed |
|---|---|---|
| B2a bounded return | fail | **fail** -- `waited 10.5s for a 1s timeout` |
| B2b partial output kept | pass | pass -- `subprocess.run` already preserved it |
| B2c honest duration | pass | pass |

Exactly one failure, and it was the predicted one. The two passes matter as much
as the failure: B2b is what locks in tree-kill over abandoning the pipes, so it
is written to pass now and fail if the cheaper strategy is ever substituted.

**GREEN.** `SubprocessRunner.run` rewritten onto `Popen` with `_launch`,
`_stop_and_collect` and `_kill_process_tree`. 14/14 in `test_runner.py`, and the
file's own runtime fell from 35.9s to 9.6s -- the old suite had been paying the
defect on every run without anyone reading the bill.

**Suite.** 796 -> 799 passing, no regressions.

**Cleanup.** `_normalise_stream` lost its last caller in the rewrite -- it
existed to cope with `TimeoutExpired.stdout` arriving as bytes -- and was
deleted. **It came back two cycles later**, when salvaging that exact field
turned out to be the right fix for a gate finding. The deletion was still
correct at the time: a helper kept "in case" is a claim that something calls it,
and the cost of being wrong was one `git revert`-sized re-add with a caller and
a test behind it this time.

### Second cycle: the gate reviews the fix (B2d-B2e)

The first cycle was run through `atom review` before committing. The gate found
four issues in it -- three real, and one that was a defect in the **spec** rather
than the code.

| Reported | Verdict | Outcome |
|---|---|---|
| Ctrl-C leaves POSIX children orphaned; `run` never cleans up the session it created | valid | `run` now kills the tree on `KeyboardInterrupt` and re-raises (B2e) |
| `os.getpgid(process.pid)` fails once the direct child is reaped, so survivors go unkilled | valid | the lookup is gone; `_launch` makes the child its own session leader, so the group id *is* the pid |
| The abandoned drain discards output the fix promised to preserve | valid, but not fixable | the promise was narrowed and the loss is now reported (B2d) |
| The spike's "median" is the upper-middle value over all runs, including ones that never answered | valid | true median over readable runs only |

**RED.** Two tests, both failing as predicted. Neither is reachable while the
tree kill works, so both disable it explicitly -- *a fallback path that is never
exercised is a fallback path that is never checked.*

**The one that could not be made to pass.** The third finding was written first
as "partial output survives an abandoned drain", and the test failed. It kept
failing because the guarantee is not achievable: Windows reads each pipe with a
single blocking `read()` that returns only at end-of-file, so bytes written
before the deadline sit inside that call, unreachable, while a surviving process
holds the pipe open. Recovering them means Atom running chunked readers on every
command to serve a path entered only after a kill has already failed.

The code had always been honest -- `_stop_and_collect` said it abandoned the
output. The false sentence was in behaviour rule 2b, which I had written as
"Any output produced before the deadline is preserved", unqualified. So the fix
was to the **spec**, and the test was retargeted to the property that is both
true and worth holding: the loss is *named*. An empty reply that does not say
why it is empty cannot be told apart from a command that printed nothing.

> *A test that will not go green is sometimes telling you the specification is
> wrong.* The temptation is to weaken the assertion until it passes; the
> difference is whether the weakened claim is still worth making. "Output is
> preserved" became "output is preserved when the kill works, and its loss is
> reported when it does not" -- narrower, and actually true.

**GREEN.** 16/16 in `test_runner.py`. Suite 799 -> 801.

### Third cycle: the gate reviews the fix to the fix

The corrected change was gated again rather than committed, because the fixes
were themselves unreviewed. Three more findings, all valid.

| Reported | Outcome |
|---|---|
| The interrupt path discards the kill detail, so a failed tree kill leaves descendants running silently | the fallback case now prints one line to stderr -- the interrupt throws the result away, so there is no report to carry it |
| The abandoned drain discards `TimeoutExpired.stdout`/`.stderr` | valid after all; salvaged where the platform provides it |
| The new B2d test neuters the kill and leaks a 600-second process on every run | the stub now records the process and the test performs the real kill in a `finally` |

**The reversal.** The second finding is the one the previous cycle had
dismissed. That dismissal was reasoned from a Windows probe -- `TimeoutExpired`
came back with `stdout=None` -- and then written up as though it were a property
of the language. It is not. POSIX reads the pipes incrementally and the
exception carries everything that had arrived; only Windows, which reads each
pipe with one blocking `read()` to end-of-file, has nothing to give. So the path
now salvages what the platform offers and names the loss when there is none, and
the docstring states the difference instead of generalising from one half of it.

> *A measurement on one platform is evidence about that platform.* The probe was
> right, the conclusion drawn from it was not, and the failure was in the step
> between them -- writing "not recoverable" where the evidence supported "not
> recoverable on Windows". The second gate run caught in minutes a claim that
> would have been wrong on every machine but this one.

**The third finding is the one worth dwelling on.** The test written to prove
the fallback path behaves correctly was itself leaving a ten-minute process
behind on every single run -- introduced while fixing a defect about processes
outliving their parent. *The guard for a defect is written in the same blind
spot that produced it.*

**GREEN.** 16/16 in `test_runner.py`, and verified directly: no surviving
`sleep(600)` process after the run.
