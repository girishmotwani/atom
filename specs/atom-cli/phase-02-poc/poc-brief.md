---
project: "atom-cli"
phase: "phase-02-poc"
date: "2026-09-14"
status: "open"
---

# POC Brief — Phase 2: `atom poc`

## Context

The phase plan marked this phase's POC as *justifiably skipped*, on the grounds that the
project-level module-isolation spike already proved the mechanism. That justification is
**partly correct and partly wrong**, which is why this brief exists.

What the original spike genuinely proved:

- A nested module under `poc/<slug>/` is invisible to the parent's `./...` patterns.
- Go writes compile errors to stderr.
- `go run .` works inside a nested spike module — but **only on a spike that compiles**.

What it did not touch, and what Phase 2 depends on:

- It **hand-wrote** every `go.mod` from a string constant. `go mod init` was never run.
- It ran `go run .` on a **working** spike only. A spike that fails to compile is the
  normal case during development, and is exactly the case `atom poc run` must not
  misreport.

## Question

> When `atom poc run` shells out to `go run .` inside a nested spike module, does a spike
> that **fails to compile** report failure through a non-zero exit code with the compiler
> error on stderr — the same way `go build` does — or does `go run` behave differently?
>
> And: should `atom poc new` generate `go.mod` by shelling out to `go mod init`, or by
> writing the file directly?

## Why It Matters

`atom poc run` is the command a developer uses dozens of times while iterating on a spike.
Its single most important property is that **a broken spike looks broken**.

The Phase 1 work already produced one real instance of this failure mode: a fully green
test suite while the package was unbuildable. A `poc run` that swallowed compile errors
would be the same bug in a more damaging place — it would let a developer conclude a spike
had *confirmed* something when it never ran at all. That is a false Confirmed verdict,
which `poc-discipline.md` names as the framework's worst outcome.

The `go mod init` half matters less but is cheap to answer at the same time, and the
probe already produced a suggestive result: `go mod init` writes the **full patch
version** (`go 1.23.4`), whereas a hand-written template would likely say `go 1.23`.

## Falsifiable Predictions

| # | Prediction | Falsified if |
|---|---|---|
| P1 | `go run .` on a spike with a compile error exits **non-zero** | It exits 0 |
| P2 | That compile error appears on **stderr**, not stdout | It appears on stdout, or nowhere |
| P3 | A spike that compiles but **panics** also exits non-zero, with the panic on stderr | Exit 0, or panic text on stdout |
| P4 | A spike writing to both streams has **both** captured, neither lost | Either stream is empty or truncated |
| P5 | `go mod init` produces a `go.mod` at least as correct as a hand-written one, and pins the full patch version | It fails offline, needs network, or produces something unusable |

## Method

Build a throwaway parent module with four spikes under `poc/`:

1. `broken` — a deliberate type error.
2. `panics` — compiles, panics at runtime.
3. `noisy` — writes to stdout and stderr, exits non-zero deliberately.
4. `generated` — `go.mod` produced by `go mod init` rather than hand-written.

Run `go run .` in each, capturing stdout, stderr and exit code separately. Assert each
prediction. Print verbatim output so the report quotes evidence rather than summary.

**Control:** the `noisy` spike must also be shown to produce a non-empty stdout, otherwise
"stderr was captured" proves nothing about stream separation.

## Out Of Scope

Non-Go spikes. Auto-generating spike source. `go work` workspace mode, which is already
recorded as an untested boundary from the original spike.

## Done When

All five predictions are settled as Confirmed or Refuted, with verbatim output for each,
and the consequences for the Phase 2 design spec are written into the report.
