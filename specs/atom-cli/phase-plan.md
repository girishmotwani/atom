---
project: "atom-cli"
date: "2026-09-13"
status: "approved"
phase_count: 5
---

# Phase Plan — Atom CLI

## Goal

A Python CLI, `atom`, that gives the Atom pipeline its runnable gates: verifying a Go
tree is green, scaffolding and running throwaway spikes, and tracking phase state. It
is the part of Atom that cannot be a markdown file, because the framework's central
claim is that evidence comes from execution.

## What The POC Proved

See [poc-report.md](poc-report.md). Verdict: **Confirmed**.

A nested Go module under `poc/<slug>/` is completely invisible to the parent module's
`go build ./...`, `go vet ./...` and `go test ./...` — a spike that fails to compile
three ways did not affect any parent command, and none of them referenced `poc/`.

Two consequences carry into this plan as hard requirements, not preferences:

1. **`atom poc new` must always write a `go.mod`.** Isolation is entirely load-bearing
   on it. A spike without one is absorbed into the parent module and will break
   `atom check`.
2. **`atom poc run` must capture stderr.** Go writes compile errors there; capturing
   stdout alone would render a failed spike as silent success — the exact laundering of
   evidence Atom exists to prevent.

Still assumed, not proven: that Go's behaviour holds on non-Windows platforms and
across Go versions other than 1.23.4, and that workspace (`go work`) mode is out of
scope.

## Phases

| # | Phase | Delivers | Risk | Needs POC? | Depends on |
|---|---|---|---|---|---|
| 1 | `check` | `atom check` — build, vet, gofmt, test, race, coverage, one verdict | M | No — see justification | — |
| 2 | `poc` | `atom poc new/run/list` — scaffold, execute and list spikes | M | No — the project POC covered the risk | 1 |
| 3 | `state` | `atom init`, `atom phase …`, `atom status` — config and phase tracking | L | No | 1 |
| 4 | `review` | `atom review` — multi-model diff review, merged report | H | **Yes** | 1, 3 |
| 5 | `ship` | `atom ship` — commit, push, PR from artifacts | L | No | 1, 3 |

## Phase Detail

### Phase 1 — `check`

**Objective.** One command that decides whether a Go tree is green, and prints evidence
a developer can paste into a gate.

**Scope in.** Running Go tooling as subprocesses; capturing both streams; parsing test
and coverage output; a stable result model; human and JSON output; correct exit codes.

**Scope out.** Config files, phase state, spikes, git. Phase 1 takes a directory and
reports on it.

**Technical risk.** Medium, and it is all in output parsing. `go test` output format
varies with cached results, no-test packages, build failures and panics. Subprocess
handling across platforms is the other half.

**POC question — justifiably skipped.** The project POC already exercised exactly this
mechanism: it shelled out to `go build`, `go vet` and `go test` from Python, captured
both streams, and asserted on exit codes across a real module tree. The remaining
uncertainty is output *parsing*, which is deterministic, cheaply testable, and
discovered by tests rather than by a spike. Recorded in `decisions.md`.

**Done when.** `atom check` runs on a real Go repo; exits 0 green and non-zero on any
failure; reports every failing gate rather than stopping at the first; `--json` emits a
stable schema.

**Size.** ~250 lines production.

### Phase 2 — `poc`

**Objective.** Make spikes a one-command operation, with the POC's two invariants
enforced by the tool rather than by the developer remembering them.

**Scope in.** `atom poc new` scaffolds `poc/<slug>/` with `go.mod`, `main.go` carrying
the question, and a `README.md`. `atom poc run` runs vet, build then run, capturing
both streams. `atom poc list` shows every spike and whether it still runs.

**Scope out.** Non-Go spikes. Auto-generating spike code.

**Technical risk.** Medium, concentrated in one place: if the generated `go.mod` is
wrong or missing, the parent build breaks. That is the one thing tests must pin down.

**POC question — justifiably skipped.** The project POC proved this exact mechanism and
produced the invariants. Nothing further is unknown.

**Done when.** A scaffolded spike always has a `go.mod`; a deliberately broken spike
does not affect `atom check` at the repo root; `atom poc run` surfaces compile errors
from stderr rather than reporting success.

**Size.** ~200 lines production.

### Phase 3 — `state`

**Objective.** Persist where a project is in the pipeline so work resumes correctly.

**Scope in.** `.atom/config.json`, `.atom/state.json`, the phase state machine, the
JSONL event log, `atom init` and `atom status`.

**Scope out.** Multi-project state. Remote state.

**Technical risk.** Low. Ordinary JSON persistence. The only real trap is corrupt or
partially-written state, which must degrade to a clear error rather than a stack trace.

**POC question — justifiably skipped.** No technical uncertainty.

**Done when.** State survives a restart; a corrupt state file produces an actionable
message; `atom status` shows the current phase and step.

**Size.** ~250 lines production.

### Phase 4 — `review`

**Objective.** Run a diff past two or more different models and merge the findings.

**Scope in.** Diff extraction, per-file parallel review, structured findings, dedupe
and merge, severity ranking, markdown report.

**Scope out.** Posting to GitHub. Automatic fixes.

**Technical risk.** High, and it is genuinely unknown — this is the only phase where a
POC is mandatory.

**POC question.** *Can a model be driven, through the Copilot CLI in non-interactive
mode, to return review findings as schema-valid JSON reliably enough to merge
programmatically — and what fraction of responses need repair?*

**Done when.** Two distinct models review a real diff; findings merge and deduplicate;
malformed model output degrades to a readable report rather than a crash. **And** the
Phase 1 diff has been run through `atom review` — see below.

**Inherited debt — the bootstrap gap.** Phase 1 shipped without a multi-model review,
because `atom review` did not exist to review it. Agreed with the developer at the Phase 1
gate on 2026-09-14: the first real target for `atom review` is the code that could not be
reviewed by it. **This phase's gate does not close until `atom review` has been run over
the Phase 1 diff (commit `4d8dee1` onward) and its findings triaged.** Recorded in
`phase-01-check/decisions.md` under Tracked debt.

**Size.** ~350 lines production.

### Phase 5 — `ship`

**Objective.** Assemble a PR from the artifacts already written.

**Scope in.** Commit message assembly, PR body from artifacts, `gh` invocation.

**Scope out.** Merging. Review response. Branch management beyond the current branch.

**Technical risk.** Low. Shelling out to `git` and `gh`.

**POC question — justifiably skipped.** No technical uncertainty.

**Done when.** A PR is opened with real `atom check` output and POC verdicts in the
body; the tool never pushes without an explicit instruction.

**Size.** ~200 lines production.

## Sequencing Rationale

Phase 1 is the walking skeleton: it establishes the subprocess layer, the result model
and the output conventions that every later phase reuses. It is also the phase most
used day to day, so it ships first and earns feedback early.

Phase 2 follows because it is the framework's signature capability and depends only on
phase 1's runner.

Phase 4 carries the only real unknown. It would be tempting to front-load it on the
"risk first" principle — but it depends on both the runner (1) and config (3) to be
testable at all, and a failure there degrades `atom review` alone rather than
invalidating the plan. Risk is front-loaded *within* what the dependency graph allows.

Phase 5 is last because it has the least uncertainty and the least value before there
is something to ship.

Every phase leaves the tree green and is independently useful: `atom check` alone is
worth installing.

## Deferred / Out Of Scope

| Item | Reason |
|---|---|
| `go work` workspace support | Would invalidate the isolation POC's finding; needs its own spike first |
| Non-Go languages | Atom is deliberately Go-scoped; generality was Helios's weakness |
| A daemon or server mode | No evidence anyone needs it |
| Editor integration | The CLI is the contract; integrations can come later |

## Open Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `go test` output format changes between versions | Low | Medium | Parse defensively; always keep raw output; never let a parse failure mask a real result |
| Copilot CLI's non-interactive interface changes | Medium | High | Isolate it behind one adapter module; phase 4's POC establishes the baseline |
| Coverage parsing differs across Go versions | Medium | Low | Treat coverage as advisory; never fail `atom check` on a parse miss alone |
| POC dirs committed without `go.mod` by hand | Medium | High | `atom check` warns on any `poc/*` directory lacking a `go.mod` |
| Platform differences (paths, signals) outside Windows | Medium | Medium | Use `pathlib` and `subprocess` portably; add CI on Linux and macOS in phase 3 |

## Completeness Checklist

- [x] Every phase traces to POC evidence or a labelled assumption
- [x] Each phase is independently shippable
- [x] Each phase states "done" as a verifiable condition
- [x] Each phase has a POC question or a specific recorded justification for skipping
- [x] Risk front-loaded as far as the dependency graph allows, with the exception argued
- [x] Deferred items recorded with reasons
