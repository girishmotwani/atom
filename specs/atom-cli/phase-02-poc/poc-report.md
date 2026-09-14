# POC Report — Go run failure modes

| | |
|---|---|
| **Phase** | 2 — `atom poc` |
| **Brief** | [`poc-brief.md`](./poc-brief.md) |
| **Spike** | [`poc/go-run-failure-modes/spike.py`](../../../poc/go-run-failure-modes/spike.py) |
| **Toolchain** | `go version go1.23.4 windows/amd64` |
| **Verdict** | **CONFIRMED with one REFUTATION** — and the refutation changes the design |

---

## The question

`atom poc run` will execute a developer's spike and report what happened. The
original module-isolation spike only ever ran `go run .` on a spike that
**compiled and worked**. But a spike under development is usually broken — that is
the entire point of a spike.

> Does `go run .` report a broken spike in a way `atom poc run` can trust?

## Result at a glance

| | Prediction | Outcome |
|---|---|---|
| **P1** | Compile error → non-zero exit | ✅ Confirmed |
| **P2** | Compile error appears on stderr | ✅ Confirmed |
| **P3** | Panic → non-zero exit, panic on stderr | ✅ Confirmed |
| **P4** | Both streams captured, not crossed | ✅ Confirmed |
| **P5** | `go mod init` works offline, pins full patch version | ✅ Confirmed |
| **P6** | `go run .` preserves the spike's own exit code | ❌ **REFUTED** |
| **INV** | Parent still builds with 4 spikes present, 3 broken | ✅ Confirmed |

P6 was not in the original brief. It was added mid-spike because P4 produced an
incidental observation that mattered more than the prediction it was testing.

---

## P6 — the refutation, and why it matters

While checking that both streams survive (P4), the noisy spike called `os.Exit(3)`
and the run came back as exit **1**. That was not what P4 was measuring, so rather
than mention it in passing it was promoted to its own prediction and measured
directly across five exit codes, two ways:

```
spike exits   via go run .    via built binary
0             0               0
1             1               1
2             1               2
3             1               3
42            1               42

  go run .      preserves exit codes: False
  built binary  preserves exit codes: True
```

**`go run` flattens every non-zero exit code to 1.** It does report the real code —
but only as the human-readable stderr line `exit status 3`, after the program's own
output. The process exit code itself is lost.

Note the `1 → 1` row. `go run` *appears* to work there. Any test written only
against a failing-with-1 spike would have missed this entirely.

### Why this is not a detail

Atom's POC verdicts are three-valued, per `poc-discipline.md`:

| Exit | Verdict |
|---|---|
| `0` | Confirmed |
| `1` | Refuted |
| `2` | Inconclusive |

Under `go run`, a spike that exits **2 to say *Inconclusive*** is reported by Atom as
exit **1 — *Refuted***.

That is the exact anti-pattern Atom's own discipline document names as the cardinal
sin — except here the framework commits it on the developer's behalf, silently, with
no way for them to notice. Atom would be a tool that quietly falsifies the results of
the experiments it exists to run.

This is also the second time in this project that **reading only the exit code has
been wrong**. `gofmt -l` (Phase 1, B9) signals by printing to stdout while exiting 0;
`go run` signals by exiting 1 while printing the truth to stderr. Same lesson, opposite
direction.

---

## Consequences for the Phase 2 design

These are binding. Each one is traceable to evidence above.

| # | Consequence | Evidence |
|---|---|---|
| C1 | **`atom poc run` MUST NOT use `go run .`.** It must `go build -o <binary> .`, then execute the binary as a separate step. | P6 |
| C2 | The built binary must go to a temp path or an ignored name — never left beside the source where it could be committed. | C1 |
| C3 | The build step and the run step are **distinct reportable outcomes**. "Did not compile" and "compiled, then failed" are different things a developer needs told apart. `go run` conflates them into one exit 1. | P1 + P3 |
| C4 | `atom poc run` must surface **stderr** prominently. On failure the useful content is always there and stdout is usually empty. | P2, P3 |
| C5 | Both streams must be captured **separately** and both shown. Neither may be dropped. | P4 |
| C6 | `atom poc new` MUST shell out to `go mod init`, not write a `go.mod` from a template. | P5 |
| C7 | Atom must **not** hard-code the `go` directive. `go mod init` pins the full patch version (`go 1.23.4`), which a template would have got wrong. | P5 |
| C8 | The spike's exit code must be reported **verbatim**, and mapped to Confirmed / Refuted / Inconclusive only when it is one of 0/1/2. Any other code is reported as-is, not coerced. | P6 |
| C9 | Adding spikes — including broken ones — must keep leaving the parent module alone. This is now a regression test, not an assumption. | INV |

---

## What this spike did not settle

Stated so the design does not quietly assume them:

- **Non-`main` packages.** Every spike here was `package main`. A spike that is a
  library has nothing to run. `atom poc run` needs a defined behaviour for that; it
  is not derivable from this evidence.
- **Long-running or interactive spikes.** Everything here terminated immediately. No
  timeout behaviour was exercised.
- **Spikes with external dependencies.** All fixtures were dependency-free, so
  `go mod tidy` and the network path are untested. This matters for C6 —
  `go mod init` was proven offline-safe, `go mod tidy` was not.
- **Non-Windows.** Single platform. The CI job added for this spike runs it on Linux
  and macOS too, which converts this gap into evidence on the next push.

---

## Reproducing

```
python poc/go-run-failure-modes/spike.py
```

Exit `0` means the evidence still matches this report. The spike deliberately
expects P6 to be **refuted** — if Go ever changes and P6 starts confirming, the spike
fails loudly and tells you this report has gone stale. It does not silently pass.
