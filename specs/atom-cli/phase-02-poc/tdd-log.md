# TDD Log — Phase 2: `atom poc`

A record of how the code was built, kept because the order things happened in is
itself evidence. The claim Atom makes is that running a throwaway program before
designing finds things design review does not. This log is where that claim is
either supported or not.

Five cycles. Three were planned from the spec. Two were not — they came from
running the finished tool, and they are the interesting ones.

---

## Cycle 1 — `scaffold.py` (B35–B43)

**RED.** 28 tests written against a module that did not exist. Every one failed
on import.

**GREEN.** `scaffold_spike`, `ScaffoldResult`, `SlugError`, `ScaffoldError`.

**Notes.** The fake for `go mod init` had to actually write a `go.mod`, not just
return exit `0`. With a fake that only returned an exit code, an implementation
that skipped running the command entirely would still have passed every test.
This is a recurring requirement in this project: *a test fake must reproduce the
side effect, not just the status.*

---

## Cycle 2 — `spike.py` (B44–B57)

**RED.** 32 tests. Import failure, then a long tail of genuine assertion
failures as the module took shape.

**GREEN.** `run_spike` with VET → BUILD → EXECUTE, short-circuiting on failure.

**One genuine gap caught by a failing test, not by inspection.** The verdict
mapping ignored spike kind, which let a library spike report `INCONCLUSIVE`.
`go test` exits `0` or `1` only and cannot express a third state, so that
verdict was unreachable in reality but reachable in the code. Fixed with a
separate `VERDICT_BY_EXIT_CODE_FOR_LIBRARY` mapping. Worth recording that this
was found by a test rather than by review — the code read fine.

**A fake that was wrong.** `ScriptedRunner` initially assumed `-o` was always
present in the build command. Library builds correctly omit it. The fake was
corrected, not the production code.

---

## Cycle 3 — `index.py` + CLI + renderers (B58–B66)

**RED.** 13 tests for `index.py`, 9 for the CLI surface.

**GREEN.** `list_spikes`, `SpikeSummary`, `poc new|run|list`, and the spike
renderers in `report.py`.

At the end of this cycle: **137 tests passing.** By the measure most projects
use, the phase was finished here.

---

## Cycle 4 — B67, B68, B69: found by running it

The phase was not finished. `pip install -e .`, a real Go toolchain, and a spike
written to exit `2`.

### What the tool printed

```
  PASS  vet     ok
  PASS  build   ok
  FAIL  execute exited 2          <- wrong

  Verdict: INCONCLUSIVE  (exit 2) -- the spike did not settle it
```

...and then exited `0`.

Three accounts of one event. The stage said failure, the verdict said a
considered result, the exit code said success. The spike had worked perfectly;
`2` was its *answer*. Every one of the 137 tests was green.

**RED for B67.** 8 failing tests for `StageResult.produced_an_answer`.

### The question that opened B68

Fixing the rendering required deciding what a non-zero EXECUTE code means. That
raised a question that had not come up while writing the spec: *what exit code
does a Go program use when it panics?*

Rather than reason about it, it was measured:

```powershell
$ go build -o probe.exe . ; .\probe.exe
PANICKING BINARY EXIT CODE = 2
```

**`2`.** The same code Atom reads as `INCONCLUSIVE`.

A spike that crashed would have been reported as having carefully concluded "I
could not tell" — Atom inventing a considered verdict out of a stack trace. The
exact failure mode this framework exists to prevent, in the framework itself.

**RED for B68.** 6 tests, including three controls that fail if the fix is
"always report CRASHED": a deliberate exit `2`, a spike that prints the word
*panic* in its stdout, and a spike whose stderr says `panic: is what I want to
avoid` with no stack dump.

**GREEN.** `Verdict.CRASHED`, set only when exit code is `2` **and** stderr
carries both `panic:` and a `goroutine N [running]:` dump.

**RED for B69.** A crashed spike `ran`, so B64 would have exited `0`. But a
crash is not a verdict. `SpikeResult.answered` splits the two; the CLI keys on
it.

### One old test had to change

`test_execute_failure_is_reported_as_execute_not_build` failed after the B67
fix. Before changing it, the question was whether this was a real regression or
a defective test.

It was defective. Its fake claimed to be a panic but used exit `1` and a bare
`panic: index out of range` with no stack dump — something no Go program has
ever produced. It passed while describing an impossible event. The fake was
corrected to a real panic; both assertions were kept unchanged.

*Changing a test to make it pass is usually the wrong move. It was right here
only because the test's fixture was factually false, and that was established by
measurement before anything was edited.*

---

## Cycle 5 — B70: 169 green tests, and the program would not start

With B67–B69 done and 169 tests passing, the tool was run again:

```
NameError: name '_exit_code_for_spike' is not defined
```

The new function had been appended to the bottom of `cli.py` — *below*
`if __name__ == "__main__": raise SystemExit(main())`. Importing the module
defines every name regardless of order, so all 169 tests passed. Running it as
`python -m atom.cli` stops at `SystemExit` before the definition is reached.

**No unit test could have caught this**, because the bug only exists in the
difference between importing a module and executing it.

**RED for B70.** 2 tests that invoke the CLI through `subprocess` and assert no
traceback.

**GREEN.** The function moved above the guard, with a comment explaining why
nothing may be added below it.

**This is the third time in this project that a fully green suite has sat on top
of a program that could not run.** Phase 1: `pyproject.toml` had
`readme = "../README.md"`, which setuptools rejects — 55 tests green, package
unbuildable. Phase 2: this. The pattern is consistent enough to be a rule:
**importing is not running, and a green suite is not a working program.**

---

## Final state

| Measure | Value |
|---|---|
| Tests | **171 passing** |
| Statement coverage | **93%** |
| Cycles planned from the spec | 3 |
| Cycles that came from running the tool | 2 |
| Behaviours found by running rather than reading | 4 (B67–B70) |

## What this phase says about the method

Of the four behaviours found after the code was "done", none were reachable by
reading it. B68 in particular — the panic/Inconclusive exit code collision —
would have passed any design review. The mapping is internally consistent,
clearly commented, and wrong for a reason that lives in the Go runtime rather
than in the code.

The counter-argument is worth stating: these could be read as evidence that the
spec was insufficiently careful, not that running is essential. B67 and B70 are
partly that. B68 is not — no amount of care in a document will tell you what
exit code a panicking binary uses. You have to crash one.
