---
project: "atom-cli"
phase: "phase-01-check"
date: "2026-09-14"
---

# Findings Log

Issues, ambiguities, and reusable learnings noticed during Phase 1 but deliberately not
fixed in this phase.

## Findings

| # | Finding | Severity | Where | Why not fixed now | Suggested action |
|---|---|---|---|---|---|
| 1 | `readme = "../README.md"` made the package fail to build — setuptools rejects a readme outside the package root. Caught only when installing for a live run, not by the test suite. | Medium | `tools/pyproject.toml:9` | Fixed in place (removed the field); recorded because the *class* of gap matters | Phase 3 should add a packaging smoke check so `pip install -e .` is verified by CI, not by chance |
| 2 | `go vet ./...` took **21.9s** on a two-file module, dominating a 26.7s run. Almost certainly cold build-cache cost. | Low | Observed in live run, `atom-demo` | Phase 1 explicitly rejected parallel gates as premature | Revisit if real-world runs stay slow; the `Gate` protocol makes parallel execution additive |
| 3 | `TestGate` infers "no test files" by scanning output text. Robust for current Go output, but it is string matching against a format Go has never promised to keep. | Low | `atom/gates.py:_reports_only_packages_without_tests` | Exit code remains ground truth, so the worst case is a `SKIPPED` shown as `PASSED` — never a failure shown as a pass | If richer parsing is ever needed, switch to `go test -json` as a deliberate phase, not a patch |
| 4 | The race detector requires cgo, and on Windows that means a working gcc. `--no-race` exists, but a user without gcc sees a gate failure rather than a helpful message. | Medium | `atom/gates.py:RaceGate` | Detecting toolchain capability is config-shaped work, which is Phase 3 | Phase 3 should auto-disable race with a `WARNING` when cgo is unavailable, rather than failing |
| 5 | `atom` was installed but not on `PATH` on this machine, so the entry point had to be invoked as `python -m atom.cli`. | Low | Environment, not code | Out of scope; a user-environment issue | `atom-init` (Phase 3+) should verify the console script is reachable and say so plainly if not |

## Ambiguities Resolved

| Ambiguity | Interpretation chosen | Why | Confidence |
|---|---|---|---|
| Should a `WARNING` gate that is `required=True` fail the check? | No — `WARNING` never fails, regardless of `required` | B20 says warnings are advisory. Letting `required` override that would make two fields fight over one verdict | High |
| Is a disabled `RaceGate` absent from the report, or present as `SKIPPED`? | Present as `SKIPPED` | A report should show what was *not* checked. Silently dropping a gate hides a coverage gap | High |
| What exit code signals "the command could not run" versus "the code failed"? | `2` for usage errors, `1` for a genuine gate failure | Callers frequently need to distinguish a broken invocation from a real failure. Follows common CLI convention | High |
| Does `find_poc_modules_without_go_mod` recurse below `poc/<slug>/`? | Only directories *directly* under `poc/` are candidates, but `.go` files are searched recursively within each | A spike is one directory; nested packages inside it are still that spike's problem | **High — confirmed by the developer at the Phase 1 gate** |

All ambiguities above are now resolved at High confidence. The `poc/` recursion question
was raised at the Phase 1 gate and the chosen interpretation was confirmed.

## Learnings

- **Injecting the command runner is what made the phase testable.** 55 tests run in 0.47s
  and pass on a machine with no Go toolchain, because only `test_runner.py` touches the OS.
  This is the single highest-leverage decision in the phase.
- **Exit codes are not a uniform interface, even within one toolchain.** `go build`, `go vet`
  and `go test` all signal by exit code; `gofmt -l` signals by stdout content and always
  exits 0. Any tool wrapping a family of commands must verify each one's convention
  individually rather than assuming the family shares one.
- **A POC's value is not limited to its headline question.** The module-isolation spike was
  asked about nested modules, but its most actionable output was an incidental observation
  that Go writes compile errors to stderr — which became a hard requirement in this design.
- **Unit tests do not prove a program runs.** All 55 tests passed while the package was
  unbuildable (finding 1). Installing and running it once against real input caught in
  seconds what the suite could not see at all.
- Promotion candidates for Atom references: the third and fourth bullets both generalise.
  Recommend adding to `poc-discipline.md` ("record incidental observations; they are often
  worth more than the answer") and to `verification.md` ("a green suite is not a working
  program — run it once against real input before claiming the phase works").

## Completeness Checklist

- [x] File exists
- [x] Each finding has severity, location, reason deferred, and suggested action
- [x] Every resolved ambiguity has confidence recorded
- [x] The one Medium-confidence ambiguity is flagged for the gate
- [x] Reusable learnings captured, with promotion candidates named
- [x] No fixed issue is listed as deferred (finding 1 states plainly that it was fixed)
- [x] No finding contradicts the POC verdict or design spec
