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
