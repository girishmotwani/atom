# Decisions — Phase 2: `atom poc`

Decisions made during Phase 2, who made them, and what was given up. Includes
decisions the agent made on the developer's behalf, which are marked as such and
are the ones most worth arguing with at the gate.

---

## Decided by the developer

| # | Question | Decision | What it cost |
|---|---|---|---|
| P2-1 | Should the Phase 2 POC be skipped? The phase plan claimed it was "justifiably skipped" because the Phase 1 spike had already covered it. | **Run it.** "It's cheap and that's the point of Atom." | ~20 minutes. It returned a refuted assumption that would otherwise have been built into the tool. |
| P2-2 | How should library spikes execute — a second build, or `go test`? | **Fall back to `go test ./...`** | Library spikes can never report *Inconclusive* (see P2-5). |
| P2-3 | What exit code should `atom poc run` use when a spike reports *Refuted*? | **Exit `0` whenever the spike ran.** A Refuted spike is the method working. | CI cannot fail on a verdict without the spike itself exiting non-zero. That is deliberate: the verdict is output, not status. |
| P2-4 | Default spike timeout? | **300 seconds** | Long enough for a cold `go vet`; short enough to notice a hang. |
| P2-6 | A crashed spike — exit non-zero, or exit `0` per P2-3? | **Exit non-zero.** Reviewed at the Phase 2 gate and approved: a crash is not a verdict, so P2-3's "a verdict is not a failure of Atom" does not cover it. | CI treats a crashed spike as a failure, which is the intent. A developer who wants a crash to be tolerated must catch the panic in the spike itself. |

### P2-5 — a limitation created by P2-2, not discovered

`go test` exits `0` or `1` only. It has no third state, so a library spike
cannot express *Inconclusive*. This is a consequence of the developer's choice
in P2-2 rather than a fact about Go that was uncovered.

It is handled rather than hidden: a separate `VERDICT_BY_EXIT_CODE_FOR_LIBRARY`
mapping makes the missing state unreachable in code, a test pins it, and the
rendered output says so explicitly — so a developer writing `t.Skip` does not
silently receive `CONFIRMED`.

Worth noting the mapping gap was caught by a failing test, not by review.

---

## Decided by the agent — please review

These were not put to the developer at the time. Each is flagged because it
changes behaviour the developer had already ruled on, or resolves a case the
developer was never shown.

| # | Decision | Reasoning | How to overturn it |
|---|---|---|---|
| **A1** | **A crashed spike makes `atom poc run` exit non-zero**, refining the developer's P2-3. | P2-3's stated principle was *a verdict is not a failure of Atom*. A crash is not a verdict — the spike stopped rather than concluded. Exiting `0` would hide a broken spike behind a green tick, and in CI nobody would look. This reads as applying the developer's principle to a case they were not shown, rather than departing from it. **✅ Raised at the Phase 2 gate and approved — see P2-6. No longer an agent decision.** | Change `_exit_code_for_spike` to key on `result.ran` instead of `result.answered`. One line; two tests document the intent. |
| **A2** | **Crash detection requires two signals** — exit `2` plus `panic:` plus a `goroutine N [running]:` stack dump. | Requiring only `panic:` would misclassify a spike whose own output contains the word. Requiring only exit `2` would misclassify every deliberate *Inconclusive*. Three controls in the test suite fail if either signal is dropped. | Relax `_looks_like_a_go_panic`. The three control tests will fail and show exactly what breaks. |
| **A3** | **An EXECUTE stage that answered renders as `PASS ... answered with exit 2`**, not `FAIL`. | The stage's job is to run the spike; it did. The answer belongs on the verdict line. The previous rendering told three contradictory stories about one event. | Revert `_status_for_stage`. |
| **A4** | **A spike's output is shown even when nothing failed.** | For a spike that answered, its output *is* the evidence behind the verdict — the most useful thing on screen. Previously output was shown only for a failed stage, so a successful spike's findings were hidden. | Remove the `result.answered` branch in `render_spike_text`. |
| **A5** | **One existing test was modified** — `test_execute_failure_is_reported_as_execute_not_build`. | Its fake used exit `1` with a bare `panic:` line and no stack dump, which no Go program produces. The fixture was factually false; both assertions were kept unchanged. Established by measuring a real panic *before* editing anything. | The prior fixture is quoted verbatim in `tdd-log.md` if it needs restoring. |

> **A1 has since been approved by the developer (P2-6).** A2–A5 are renderings
> and test hygiene, and stand unless someone objects.

---

## Deviations from process

| # | What | Why |
|---|---|---|
| 1 | B67–B70 were added to the design spec **after** implementation, not before. | They were discovered by running the finished tool. Recording them beforehand was not possible. They are in a separately headed section so the distinction is visible rather than smoothed over. |
| 2 | B48's test was written after the fact and passed immediately. | It is a characterization test pinning already-correct behaviour, not a RED-GREEN cycle. Labelled as such in `findings.md` (D4) rather than presented as driven. |

---

## Gate record — Phase 2

| Item | Status |
|---|---|
| POC run and reported | ✅ `poc/go-run-failure-modes/` — one prediction refuted |
| Design spec written and reviewed with developer before implementation | ✅ Three open questions put to the developer, none assumed |
| TDD, RED confirmed before every GREEN | ✅ 5 cycles |
| Tests passing | ✅ 172 at 93% statement coverage |
| Verified end-to-end against a real Go toolchain | ✅ Both exit-`2` cases distinguished correctly |
| Agent decisions surfaced for review | ✅ A1–A5 above |
| **Developer gate review** | ✅ **Closed. A1 raised, discussed and approved — recorded as P2-6.** |

### What Phase 2 changes for the phases that follow

| # | Carried forward |
|---|---|
| 1 | **Never trust an external tool's exit code until it has been measured.** Three for three now: `gofmt -l`, `go run`, and the Go runtime's panic code. Assume the next one lies too. |
| 2 | **Every phase ends with a real end-to-end run.** Two of Phase 2's four late findings were invisible to a green test suite. |
| 3 | **Any new subcommand extends the `test_cli.py` subprocess smoke test.** Importing a module is not running it. |
| 4 | **Phase 4's POC must attack its real risk first** — whether Copilot CLI non-interactive returns schema-valid JSON reliably enough to merge programmatically. That is still unmeasured, and it is the whole phase. |
