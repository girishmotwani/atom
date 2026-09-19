---
project: "atom"
document: "architecture"
date: "2026-09-19"
status: "draft for developer review"
related: "design-spec.md"
---

# Architecture — Atom

How Atom is built. What it is *for* is described in
[`design-spec.md`](design-spec.md).

## Shape

The CLI is arranged in layers. Each depends only on the layers beneath it, and
each module has one responsibility reachable through an interface rather than a
global — which is what makes every layer independently testable.

```
   cli.py ─────────────────────── argument parsing, dispatch, exit codes
      │
   ┌──┴───────────┬───────────┬──────────────┬─────────────┐
   │              │           │              │             │
 check.py      spike.py    review.py      status.py     ship.py
 gates.py    scaffold.py   diff.py
              index.py     invoke.py
                           extract.py
                           merge.py
   │              │           │              │             │
   └──────────────┴─────┬─────┴──────────────┴─────────────┘
                        │
                   report.py ──── every rendering, human and JSON
                        │
                   runner.py ──── the ONE place a subprocess starts
                        │
              state.py · storage.py · eventlog.py · filelock.py
                        │
                   .atom/ on disk
```

## The Two Seams

Atom has exactly two places where it touches the world outside itself. Both are
deliberately narrow, and both are the reason a problem at the boundary is fixed
once rather than everywhere.

### `runner.py` — the seam to the operating system

Every external command goes through it: `go`, `gofmt`, `git`, `gh`, and the
model CLIs. Nothing else calls `subprocess`.

Concentrating process launch in one module is what makes the following
enforceable rather than hoped for:

| Rule | Reason |
|---|---|
| Stdin is always supplied, never inherited | A tool that reads stdin blocks forever on a pipe that never reaches EOF |
| The executable is resolved before launch | `CreateProcess` searches only for the literal name and `name.exe`, so shim-based installs are invisible to a naive launch |
| A failure to *start* is reported differently from a failure to *succeed* | They have different causes and different fixes |
| Output is decoded explicitly, never by console default | A redirected stream must not depend on the terminal that launched it |

**Arguments have a size limit that belongs to the launcher, not the platform.**
A native executable is launched directly and accepts a large command line; a
shim is launched through the system shell and accepts far less. Anything that
can grow without bound — a diff, a pull request body, a prompt — therefore
travels by **stdin or a file**, never as an argument.

### `report.py` — the seam to the developer

Nothing else prints. That keeps two rules enforceable:

- **Output is ASCII-only.** A report that may be redirected to a file must not
  depend on the console's encoding, or it arrives permanently corrupted.
- **No ANSI colour reaches a file.** Styling is a property of a terminal, not
  of a result.

Every command renders in two forms — human-readable text and stable JSON — from
the same result objects, so the two can never drift.

## Modules

| Module | Responsibility |
|---|---|
| `cli.py` | Argument parsing, dispatch, exit codes |
| `check.py` | Aggregate gate verdicts into one check result |
| `gates.py` | Evaluate one Go quality gate each |
| `runner.py` | Execute external commands |
| `report.py` | Render results for humans and machines |
| `scaffold.py` | Create spike directories |
| `spike.py` | Run a spike and report what happened |
| `index.py` | List the spikes in a repository |
| `diff.py` | Obtain the diff to be reviewed |
| `invoke.py` | Call review models and record what each run did |
| `extract.py` | Turn a model reply into validated findings, or a recorded failure |
| `merge.py` | Combine findings across runs without losing what differed |
| `review.py` | Compose the review pipeline |
| `state.py` | Phase model and project layout |
| `storage.py` | Read and write state files safely |
| `eventlog.py` | The append-only event log |
| `filelock.py` | A cross-process lock |
| `status.py` | Assemble what `atom status` reports |
| `ship.py` | Assemble a pull request from phase artifacts |

## Quality Gates

`atom check` evaluates every gate and reports all failures rather than stopping
at the first, because a developer fixing one problem wants to see the others.

| Gate | Command | Note |
|---|---|---|
| build | `go build ./...` | |
| vet | `go vet ./...` | |
| fmt | `gofmt -l .` | The exit code cannot be trusted: it reports success while *printing* the unformatted files. The gate parses stdout. |
| test | `go test ./...` | |
| race | `go test -race ./...` | Optional |

`SKIPPED` and `WARNING` are non-failures by design. A tree with no tests has
not failed, and an advisory signal must never gate a merge.

> **A gate's exit code is a claim, not a fact.** Where a tool's exit code and
> its output disagree, the output wins. The `fmt` gate is the standing example.

## Phase State

The pipeline has five phases:

```
POC ──► SPEC ──► TDD ──► REVIEW ──► SHIP
```

### State is derived, not declared

Phase state is a **function of what exists on disk**, recomputed on demand
rather than stored and maintained. A phase's position is determined by which
artifacts are present:

| Artifact present | Implies at least |
|---|---|
| `poc-brief.md` | DISCOVER done |
| `poc-report.md` | POC done |
| `design-spec.md` | SPEC drafted |
| Go source and tests | TDD underway |
| A review report | REVIEW done |

The reason is the principle it follows from: **evidence outranks authority.** A
stored phase marker can claim TDD is complete while no design spec exists.
Derived state cannot, because the claim and the evidence are the same thing.
It also cannot go stale, cannot be forgotten, and cannot disagree with a
colleague's copy.

### What is stored

Exactly one thing cannot be derived: **whether a human approved something.**
A `design-spec.md` on disk shows a spec was written, not that the developer
accepted it — and that distinction is the whole substance of a human gate.

So `.atom/state.json` records approvals only:

```json
{
  "approvals": {
    "phase-05-ship": { "spec": "2026-09-19T11:04:00Z" }
  }
}
```

Small, append-mostly, and the only thing that has to be kept honest.

### On-disk layout

| Path | Contents |
|---|---|
| `.atom/config.json` | Project identity and toolchain settings |
| `.atom/state.json` | Recorded human approvals |
| `.atom/events.jsonl` | Append-only history of what happened |
| `specs/<project>/phase-NN-<name>/` | The artifacts for one phase |
| `poc/<slug>/` | One throwaway spike |

### Writes are made safe explicitly

Two properties are enforced rather than assumed, because neither holds by
default on every platform:

- **Replacing a file retries.** A rename onto an open destination can fail, and
  a reader is enough to hold one open.
- **Appending to the event log takes a cross-process lock.** Unlocked
  concurrent appends do not merely interleave — they silently *lose* entries,
  which is worse than corruption because nothing indicates it happened.

## The Review Pipeline

`atom review` is the most involved command, and its stages are separate modules
so each is testable alone.

```
  diff.py ──► invoke.py ──► extract.py ──► merge.py ──► report.py
  obtain      call models     parse and      group by      render
  the diff    N times each    validate       proximity
```

Three decisions shape it:

**The whole diff travels in one call.** Cross-file context is where the most
valuable findings live, and keeping phases small is what makes that affordable.
There is no per-file chunking.

**Each model is called several times.** A model's compliance with a structured
output contract is bimodal rather than random, and a single call can omit a
real finding with nothing in the output to indicate the omission. Repetition
turns that into a measurable signal.

**Agreement is the confidence signal.** A finding several runs report
independently is more likely to be real than one reported once. Every message
stays attributed to the runs that produced it, so a developer can see the
disagreement rather than a synthesised consensus.

Because findings are grouped by proximity, a group is reported with its **line
span** rather than a bare count — the span is what a developer can verify, and
a count implies a precision the grouping does not have.

## Extending Atom

| To add | Do this |
|---|---|
| A quality gate | Add a `Gate` in `gates.py`; `check.py` aggregates it automatically |
| A review model | Add it to config; `invoke.py` takes model names as data |
| A CLI command | Add a subparser in `cli.py` and a module for the logic; render through `report.py` |
| A pipeline stage | Add a skill in `skills/`, and a template if it produces a new artifact |

The constraints on any addition are the two seams: if it starts a process it
goes through `runner.py`, and if it prints it goes through `report.py`.
