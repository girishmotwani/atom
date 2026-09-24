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

## The Phase 1 review gate, run late

Phase 1 shipped before `atom review` existed, so its diff was never reviewed --
a bootstrap debt carried openly since. It was paid once the Copilot CLI was
working again: `atom review --branch 2083fe5` over the 23 files and 2,514 lines
of `4d8dee1..7aae972`, from a detached worktree at Phase 1's tip so the reviewed
range was exactly Phase 1.

Result: 6/6 runs, one unparseable reply, five findings -- **all from `gpt-5.4`,
all raised in 1 of 3 runs**, with `claude-haiku-4.5` finding nothing in 3/3. The
same distribution as Phase 6, and the same conclusion: agreement is not
confidence. Every finding was checked against source.

| # | Finding | Verdict |
|---|---|---|
| 1 | `gofmt -l .` recurses into nested modules | **Real** |
| 2 | stderr chatter defeats the `[no test files]` scan | **Real** |
| 3 | `text=True` decodes with the host locale | **Real -- already fixed in Phase 4** (`341b28a`) |
| 4 | CI POC job pinned to Ubuntu | Real, low, a judgement call |
| 5 | `check_links.py` strips `#anchor` before checking | **Real**, low |

Finding 3 deserves its own note: the model named the exact line and the exact
mechanism, and the defect had already been found and fixed independently in
Phase 4 by running the program. *Two different instruments found the same
defect, one of them three phases late.* The review gate is not a substitute for
running the thing, and running the thing is not a substitute for the review
gate.

### Two defects the review did not find

Both came out of refusing to explain away a measurement artifact. While checking
finding 1, `gofmt -l .` also flagged a file I believed was clean. The tempting
reading was "my fixture is sloppy". Building the minimal case instead:

- **CRLF alone fails the fmt gate.** A byte-for-byte correctly formatted file is
  reported unformatted purely for its line endings. `core.autocrlf=true` is
  Git's default on Windows *and is set in this repository*, so every Windows
  developer would see `FAIL fmt` on every file, with a message -- "1 file(s)
  need gofmt: main.go" -- that never mentions line endings. Proven end to end
  through the real `atom check`: exit 1 on a one-file project containing no
  formatting error at all. This is the most severe finding of the set and
  neither model raised it.
- **`race` reported PASSED on zero tests while `test` reported SKIPPED.** Seen
  in the same run, printed on adjacent lines: twenty seconds spent proving
  nothing, reported green.

### What the four fixed defects have in common

Every one is the same failure wearing different clothes: **the gate reported a
verdict that was not true.** Three said green where nothing had been checked;
one said red where nothing was wrong. A quality gate's only product is a true
verdict, so each of these was a total failure of the gate's purpose, not a
rough edge on it.

**Learnings.**

- *A measurement artifact is a finding you have not read yet.* The CRLF defect
  arrived disguised as a sloppy fixture, and "my test setup is wrong" is the
  most comfortable available explanation for an inconvenient result.
- *A gate whose verdict depends on the environment is not measuring the code.*
  Platform-dependent green is worse than consistent red, because it is the
  disagreement between developer and CI that nobody can reproduce.
- *Consistency between gates is itself a testable property.* `test` and `race`
  run the same suite over the same packages; that they could disagree was
  discoverable without knowing which one was wrong.
- *Bootstrap debt keeps earning interest.* Phase 1 built the gates every later
  phase relied on, and was the one phase never reviewed. The tooling a project
  builds first is the tooling its own process cannot yet check.
