# Findings — Phase 2: `atom poc`

Discoveries made while building Phase 2 that outlive it. Recorded here rather
than in commit messages because several of them change how later phases should
be built.

---

## 1. `go run` flattens every non-zero exit code to 1

Found by the Phase 2 spike, before any code was written.

| Spike exits | Via `go run .` | Via built binary |
|---|---|---|
| 0 | 0 | 0 |
| 1 | 1 | 1 |
| 2 | **1** | 2 |
| 3 | **1** | 3 |
| 42 | **1** | 42 |

Atom's verdicts are three-valued: `0` Confirmed, `1` Refuted, `2` Inconclusive.
Under `go run`, a spike reporting *Inconclusive* arrives as *Refuted* — the
framework falsifying the experiment it exists to run.

**Consequence:** `atom poc run` builds a binary and executes it. It never uses
`go run`. `test_never_uses_go_run` pins this against a future refactor that
would look like a simplification.

Note the `1 → 1` row. A test written only against a spike that fails with `1`
would agree with the broken implementation and miss this entirely.

---

## 2. A panicking Go binary exits 2 — the same code as *Inconclusive*

Found after the implementation was complete, by deliberately crashing a program
and reading `$LASTEXITCODE`.

```
PANICKING BINARY EXIT CODE = 2
```

Without disambiguation, a spike that crashed would be reported as having
carefully concluded "I could not tell". Atom would be inventing a considered
verdict from a stack trace.

**Consequence (B68):** exit `2` reads as `CRASHED` only when stderr carries
**both** `panic:` and a `goroutine N [running]:` stack dump. Requiring both
stops a spike that merely prints the word from being misread.

**The direction of this parse matters.** It can only escalate a report
(`INCONCLUSIVE → CRASHED`), never soften a failure into a success. That is what
makes it compatible with Phase 1's rule that a parsed stream must never override
an exit code.

**This is the strongest evidence so far for POC-first.** The ambiguous mapping
was internally consistent, clearly commented, and wrong. It would have passed
design review. The collision lives in the Go runtime, not in the code.

---

## 3. Exit codes have now lied three times

| Phase | Tool | The lie |
|---|---|---|
| 1 | `gofmt -l` | Exits `0` while printing unformatted filenames to stdout |
| 2 | `go run` | Exits `1` while the true code is hidden in a stderr string |
| 2 | Go runtime | Exits `2` for a panic, colliding with a meaningful verdict |

Three for three. **Treat every external tool's exit code as one signal among
several until measured.** `go mod init` is verified by observing that `go.mod`
appeared, not by trusting its status.

This is now frequent enough that later phases should assume it rather than
rediscover it.

---

## 4. Importing a module is not running it

`_exit_code_for_spike` was appended below `if __name__ == "__main__": raise
SystemExit(main())`. Every test imports `atom.cli`, which defines all names
regardless of order. **169 tests passed.** `python -m atom.cli` stopped at
`SystemExit` before the definition and raised `NameError`.

**Second occurrence of this class.** Phase 1 shipped a `pyproject.toml` with
`readme = "../README.md"`, which setuptools rejects — 55 tests green, package
unbuildable, caught only by running `pip install -e .`.

**Consequence (B70):** `test_cli.py` invokes the CLI through `subprocess` and
asserts no traceback. Every later phase adding a subcommand must extend it.

**A green suite is not a working program.** Every phase ends with a real
end-to-end run against real tooling. That rule has now paid for itself twice.

---

## 5. Test fakes must reproduce side effects, not just exit codes

`FakeGoModInit` writes a real `go.mod`. `ScriptedRunner` writes a real binary at
the `-o` path. Without this, an implementation that skipped running the command
entirely would pass.

It also has to be *right*. Two fakes in this phase were wrong:

- `ScriptedRunner` assumed `-o` was always present; library builds omit it.
- `test_execute_failure_is_reported_as_execute_not_build` used exit `1` with a
  bare `panic:` line and no stack dump — something no Go program produces. It
  passed while describing an impossible event.

**A fake encodes a belief about the world, and that belief can be false.** When
a test fails after a change, check the fake against reality before assuming a
regression.

---

## 6. Writing the test spec retrospectively found a real gap

B48 — *stderr is rendered before stdout on failure* — had no test. It was found
by mapping spec behaviours to tests, not by any failure.

It matters because `render_spike_text` was **edited the same day** to change
which stage's output is shown. A flipped ordering would have shipped silently.

The test passed the moment it was written. That is worth being precise about: it
pins already-correct behaviour rather than driving a fix, so it is a
characterization test and not a RED-GREEN cycle. The value is in preventing a
future regression, not in having found a present bug.

---

## Open questions carried forward

| # | Question | Why it matters |
|---|---|---|
| 1 | `go vet ./...` took **21.9s cold** on a two-file module | Parallel gates were deferred in Phase 1 on the assumption gates are fast. That assumption is shaky. |
| 2 | The race detector needs cgo and a C toolchain; absent on stock Windows | Phase 3 must auto-disable with a `WARNING`, never a silent skip. |
| 3 | `go work` workspace mode is untested | It would likely reverse the Phase 1 module-isolation result. Nobody has checked. |
| 4 | Spikes with external dependencies are untested | Only `go mod init` was proven offline-safe. `go mod tidy` has never been exercised. |
| 5 | Can Copilot CLI non-interactive return schema-valid JSON reliably enough to merge programmatically? | **This is Phase 4's entire risk**, and it is still unmeasured. Phase 4's POC must attack it first, not last. |

## Tracked debt

| # | Item | Severity | Status |
|---|---|---|---|
| D1 | `cli.py` coverage is 82%, the weakest module. Uncovered paths are argument-parsing errors and dispatch branches. | Low | Open — B70's subprocess tests cover the worst of it |
| D2 | Library spikes cannot report *Inconclusive*, because `go test` exits `0` or `1` only. | Medium | Accepted (B57). Surfaced in output so it cannot be hit silently. |
| D3 | Crash detection is Go-panic-specific. A spike killed by a signal, or one that exits `2` from a C library, is not detected. | Low | Open — no evidence yet that it occurs |
| D4 | B48's test is a characterization test, not a driven one. | Low | Accepted and labelled as such |
