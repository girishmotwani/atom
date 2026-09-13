---
project: "atom-cli"
phase: "n/a"
author: "Atom (dogfooding)"
date: "2026-09-13"
status: "approved"
---

# POC Brief

## Problem

Atom tells developers to write throwaway Go spikes under `poc/<slug>/` and keep them
in the repository as evidence. It also tells them `atom check` is the single green
gate for the whole project.

Those two promises collide. Spikes are deliberately low quality — they hardcode,
they `panic`, they may not even compile after the fact. If a rotten spike can break
`atom check`, then keeping spikes is actively harmful and the entire `poc/`
convention has to be redesigned.

## The Question

> **Does a nested Go module under `poc/<slug>/` stay completely invisible to the parent
> module's `go build ./...`, `go vet ./...` and `go test ./...` — such that a spike
> that does not even compile cannot fail the parent's `atom check`?**

## Why This Is The Riskiest Unknown

Ranked against feasibility > performance > integration > ergonomics, this is
**feasibility**. If the answer is no, `poc/` cannot live inside the repository, and
that changes `atom-init`, `atom-poc`, `atom-check` and `atom-ship` simultaneously — a
change to four skills and the whole artifact layout.

Other candidates considered and rejected as less urgent:

| Candidate unknown | Why not chosen |
|---|---|
| Can Python capture Go's interleaved stdout/stderr reliably? | Integration. Solvable with `subprocess` in several ways; failure is recoverable |
| Is the phase state machine's JSON schema right? | Ergonomics. Cheap to redesign later |
| Will `go test -cover` parsing be stable across versions? | Integration. Contained to one function |

Go's documented behaviour is that a directory containing its own `go.mod` is excluded
from the parent module. But "documented" and "true for `vet` and `test` as well as
`build`, on this Go version, on Windows" are different claims. The cost of being wrong
is four skills; the cost of checking is one program.

## Success Criteria

| Observation | Means |
|---|---|
| Parent `go build ./...` exits 0 with a deliberately broken spike present | Confirmed |
| Parent `go vet ./...` exits 0 with the broken spike present | Confirmed |
| Parent `go test ./...` exits 0 and reports only the parent's packages | Confirmed |
| The spike is still independently runnable in its own directory | Confirmed |
| Any parent command reports an error originating in `poc/` | Refuted |

## Scope

**Will do:**

- Build a real throwaway parent module on disk with one working package and one test
- Plant a spike under `poc/spike/` with its own `go.mod` that **does not compile**
- Run the three parent commands and capture real exit codes and output
- Confirm the spike still runs on its own

**Will not do:**

- Test more than one Go version (we test the toolchain actually installed)
- Test non-Windows platforms
- Test `go work` / workspace mode, which would change the answer and is out of scope
- Prove anything about vendoring, build tags or CI behaviour

## Approach Sketch

A single Python script that builds the whole scenario in a temp directory, shells out
to `go`, and prints a verdict table. One file, no abstractions, no error handling
beyond letting exceptions surface.

## Open Questions For The Developer

- Should Atom ever support `go work` workspaces? If yes, this POC's boundary becomes a
  known gap that needs its own spike, because workspace mode explicitly pulls nested
  modules back in.
