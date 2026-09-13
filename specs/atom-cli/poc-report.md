---
project: "atom-cli"
phase: "n/a"
poc_slug: "module-isolation"
verdict: "Confirmed"
date: "2026-09-13"
spike_path: "poc/module-isolation"
---

# POC Report

## The Question

> **Does a nested Go module under `poc/<slug>/` stay completely invisible to the parent
> module's `go build ./...`, `go vet ./...` and `go test ./...` — such that a spike
> that does not even compile cannot fail the parent's `atom check`?**

## Verdict

**Confirmed.** A spike that fails to compile for three separate reasons was completely
invisible to all three parent commands, which exited 0 and never referenced `poc/`.

## Evidence

Command:

```bash
python poc/module-isolation/spike.py
```

Output:

```text
========================================================================
ATOM POC: module-isolation
========================================================================
scenario built at: C:\Users\gimotwan\AppData\Local\Temp\atom-poc-isolation-ubat4n1l\parent
go version go1.23.4 windows/amd64

-- CONTROL: the spike must genuinely fail to compile --
  cmd=C:\Program Files\Go\bin\go.EXE build ./... (in poc/spike) exit=1
  stderr: # example.com/spike
  spike_is_really_broken=True

-- PARENT COMMANDS with the broken spike present --
  go build ./...  exit=0  leaked_poc_ref=False
  go vet ./...  exit=0  leaked_poc_ref=False
  go test ./...  exit=0  leaked_poc_ref=False
      | ok  	example.com/parent/calc	0.545s

-- INDEPENDENT SPIKE EXECUTION --
  cmd=C:\Program Files\Go\bin\go.EXE run . (in poc/goodspike) exit=0
  stdout: spike-ran-independently=true
  spike_still_runnable=True

========================================================================
VERDICT
========================================================================
  broken spike genuinely broken ........ True
  parent build/vet/test all exit 0 ..... True
  no parent command referenced poc/ .... True
  valid spike still runs standalone .... True

  RESULT: CONFIRMED
========================================================================

machine-readable:
{
  "confirmed": true,
  "parent_exits": {
    "build": 0,
    "vet": 0,
    "test": 0
  },
  "poc_leak": {
    "build": false,
    "vet": false,
    "test": false
  },
  "spike_runnable": true
}
```

Run context:

- Date/time run: 2026-09-13
- Go version: `go version go1.23.4 windows/amd64`
- Platform: Windows
- Number of runs: 1 (boolean outcome, not a measurement — repetition adds nothing)

## What The Spike Did

The spike at `poc/module-isolation/spike.py` builds a complete throwaway Go project in
a temp directory:

- A parent module with a real package (`calc`) and a real passing test
- `poc/spike/` — its own `go.mod`, and a `main.go` that is broken three ways: a type
  error, a call to an undefined function, and an unused import
- `poc/goodspike/` — its own `go.mod` and a valid program

It then runs the three parent commands, checks their exit codes, greps their combined
output for any `poc/` reference, and separately runs the good spike standalone.

- Real: the Go toolchain, real modules on disk, real compilation
- Simulated: nothing

### The control case matters

The spike first verifies **in `poc/spike/` itself** that the broken code really does
fail to compile (exit 1). Without that control, a parent exit code of 0 would be
worthless — it could equally mean "isolation works" or "the broken file was never
broken". The spike exits with a distinct code and refuses to report a verdict if the
control fails.

## What We Learned

- Nested-module exclusion holds for `vet` and `test`, not just `build`. This was the
  part actually worth checking — `go vet` in particular does its own package loading,
  and it would have been reasonable for it to behave differently.
- Exclusion is **total**, not merely non-fatal. No parent command so much as mentioned
  `poc/` in its output. Spikes will not add noise to `atom check`.
- **Surprise:** `go build ./...` in the *parent* exits 0 even though a nested module
  is unbuildable, but `go build ./...` inside `poc/spike/` exits 1 with a bare
  `# example.com/spike` header on stderr and the detail following. Atom's `atom poc run`
  must capture stderr as well as stdout, or POC compile failures will appear to the
  developer as silent success.

## What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| Spikes can be committed under `poc/` without risking the parent build | Confirmed | `poc/` stays inside the repository and is committed. `atom-init`, `atom-poc` and `atom-ship` keep their current shape |
| `atom check` can safely use plain `./...` patterns | Confirmed | No exclusion flags, no `-skip`, no directory filtering needed. `atom check` stays simple |
| Each spike needs its own `go.mod` | Confirmed — and it is load-bearing | `atom poc new` must **always** generate a `go.mod`. A spike without one is absorbed into the parent and will break `atom check`. This becomes an invariant, not a convenience |
| Capturing stdout is enough for `atom poc run` | Refuted | Go writes compile errors to stderr. `atom poc run` must capture and surface both streams |

## Explicitly Not Covered

- **Only one Go version was tested** (1.23.4). The behaviour is documented Go module
  semantics and is unlikely to change, but this is evidence about 1.23, not a guarantee
  about 1.21 or 1.25.
- **Only Windows was tested.** Path handling differs on Unix; the module resolution
  logic should not, but that is an inference, not a result.
- **`go work` workspace mode was not tested, and would very likely change the answer.**
  A `go.work` file that lists the spike modules would deliberately pull them back into
  the build. This is a real gap — see the recommendation below.
- Says nothing about vendoring, build tags, or how CI systems that scan for `go.mod`
  files might treat `poc/`.

## Recommendation

**Proceed to spec.** The `poc/` convention is sound and the design that depends on it
can be written.

Two things carry forward as hard requirements rather than preferences:

1. `atom poc new` must always write a `go.mod`. Treat a missing one as a bug, and have
   `atom check` warn when it finds a directory under `poc/` without one.
2. `atom poc run` must capture stderr as well as stdout.

Conditions before continuing:

- Log the `go work` gap in `findings.md` as a candidate for its own spike if Atom ever
  supports workspace mode.

Next artifact: `specs/atom-cli/phase-plan.md`
