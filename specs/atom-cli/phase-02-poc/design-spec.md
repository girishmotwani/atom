# Design Spec — Phase 2: `atom poc`

> **Status: APPROVED.** Behaviours are numbered so tests can cite them. Phase 1
> numbered B1–B34; this phase continues at **B35** and runs to **B66**. Three open
> questions were resolved in developer review — see *Resolved In Developer Review*.

## Purpose

Make spikes a one-command operation.

Atom's central claim is that you should **run the thing before you describe it**. That
claim is only credible if running the thing is cheap. Today a developer who wants to
answer a question in Go has to create a directory, remember that it needs its own
`go.mod` or it will break the parent build, write a `main.go`, build it, run it, read
two streams, and clean up. That friction is what makes people skip the POC and write
the design doc from imagination instead.

`atom poc` removes the friction and enforces the two invariants the developer would
otherwise have to remember.

This phase also has to be **honest about failure**, because a spike under development
is usually broken. A tool that reports a broken spike as working would be worse than no
tool at all — it would manufacture false evidence, and Atom's whole value is that its
evidence is real.

## Evidence Base

Every design decision below traces to an observation, not an opinion.

| Source | What it established | Used by |
|---|---|---|
| [`poc/module-isolation/spike.py`](../../../poc/module-isolation/spike.py) | A nested dir with its own `go.mod` is invisible to the parent's `./...`. Without one, it breaks the parent build. | B35, B38, B60 |
| [`phase-02-poc/poc-report.md`](./poc-report.md) C1, C3 | `go run` conflates "did not compile" with "compiled then failed" | B44, B45, B46 |
| [`poc-report.md`](./poc-report.md) C4, C5 | On failure, stderr carries the content; stdout is usually empty. Streams stay separate. | B47, B48 |
| [`poc-report.md`](./poc-report.md) C6, C7 | `go mod init` works offline and pins the **full patch version** (`go 1.23.4`) | B36, B37 |
| [`poc-report.md`](./poc-report.md) C8 | **`go run` flattens every non-zero exit code to 1** | B49, B50, B51, B64 |
| [`poc-report.md`](./poc-report.md) C2 | A built binary left beside the source could be committed | B52 |
| Phase 1, B9 (`gofmt`) | Exit code alone is not a reliable success signal for Go tools | B45, B49 |
| Phase 1 `runner.py` | `CommandRunner` Protocol; injected, so gates are testable without Go | all of `spike.py` |
| Phase 1 gate review | `poc/` is scanned as **direct children only** — confirmed by the developer | B58 |
| Developer review, this phase | Library fallback, 300s timeout, exit `0` on Refuted | B54–B57, B53, B64–B65 |

### The observation that shaped this phase

```
spike exits   via go run .    via built binary
0             0               0
1             1               1
2             1               2
3             1               3
42            1               42
```

Atom's POC verdicts are three-valued: `0` Confirmed, `1` Refuted, `2` Inconclusive.
Under `go run`, a spike saying **Inconclusive** arrives as **Refuted**. Atom would
falsify the experiment it exists to run — and the developer would never see it happen.

**So `atom poc run` builds, then executes the binary.** That single refutation is
responsible for most of the structure below.

## Design Overview

```
                        atom poc <subcommand>
                                 |
         +-----------------+-----+-----------------+
         |                 |                       |
       new               run                     list
         |                 |                       |
   Scaffolder          SpikeRunner            SpikeIndex
         |                 |                       |
         |         +-------+-------+               |
         |         |       |       |               |
         |       vet    build     exec             |
         |         \       |       /               |
         |          +------+------+                |
         |                 |                       |
         |            SpikeResult                  |
         +-----------------+-----------------------+
                           |
                      report.py
                  (render_text / render_json)
                           |
                       exit code
```

Three independent capabilities behind one noun. They share `CommandRunner` and
`report.py` with Phase 1 and add nothing to them.

**The key structural decision:** `run` is **three separately reportable stages**, not
one. `go run` merges them; the developer needs them apart. "Your spike doesn't compile"
and "your spike compiled and then panicked" call for completely different next actions.

## Public API

```python
# scaffold.py
#
# Creates a spike directory. Owns exactly one invariant: a spike always has
# its own go.mod, because without one it breaks the parent build.

@dataclass(frozen=True)
class ScaffoldResult:
    """What was created, so the CLI can tell the developer where to go next."""
    slug: str
    directory: Path
    files_created: list[Path]
    module_path: str          # e.g. "spike/json-streaming"

class SlugError(ValueError):
    """The requested slug is not usable as a directory and module path."""

def scaffold_spike(
    poc_root: Path,
    slug: str,
    question: str,
    runner: CommandRunner,
) -> ScaffoldResult:
    """Create poc/<slug>/ containing go.mod, main.go and README.md.

    go.mod is produced by shelling out to `go mod init` -- never from a
    template -- because the `go` directive must carry the full patch version
    of the local toolchain (evidence: poc-report.md C6/C7).

    Raises SlugError if the slug is unusable, FileExistsError if the spike
    already exists, and ScaffoldError if `go mod init` fails.
    """


# spike.py
#
# Runs a spike. Deliberately mirrors gates.py in shape: same runner, same
# outcome vocabulary, same "never let a parse override an exit code" rule.

class Stage(Enum):
    """The three stages of running a spike, reported separately."""
    VET = "vet"
    BUILD = "build"
    EXECUTE = "execute"

class SpikeKind(Enum):
    """How the spike produces its evidence. Determines the EXECUTE stage."""
    COMMAND = "command"   # package main -- build a binary and run it
    LIBRARY = "library"   # no main -- run `go test ./...` instead

class Verdict(Enum):
    """A spike's own answer, from its exit code. Only 0/1/2 map to a verdict."""
    CONFIRMED = "confirmed"        # exit 0
    REFUTED = "refuted"            # exit 1
    INCONCLUSIVE = "inconclusive"  # exit 2
    UNKNOWN = "unknown"            # any other code -- reported, never coerced

@dataclass(frozen=True)
class StageResult:
    """One stage's outcome. Both streams kept, because both can matter."""
    stage: Stage
    exit_code: int
    stdout: str
    stderr: str
    skipped: bool = False   # a later stage is skipped when an earlier one fails

@dataclass(frozen=True)
class SpikeResult:
    """Everything that happened when a spike ran."""
    slug: str
    kind: SpikeKind
    stages: list[StageResult]
    verdict: Verdict | None     # None unless EXECUTE actually ran
    spike_exit_code: int | None # the spike's OWN code, unflattened

    @property
    def failed_stage(self) -> Stage | None: ...
    @property
    def compiled(self) -> bool: ...
    @property
    def ran(self) -> bool:
        """True if EXECUTE completed. Drives the CLI exit code (B59)."""

def run_spike(
    spike_dir: Path,
    runner: CommandRunner,
    timeout_seconds: int = 300,
) -> SpikeResult:
    """Vet, build, then execute a spike, reporting each stage separately.

    Builds to a temp binary and executes it, rather than using `go run`,
    because `go run` flattens every non-zero exit code to 1 and would
    misreport an Inconclusive spike as Refuted (evidence: poc-report.md C1/C8).

    A spike that is a library rather than `package main` has nothing to
    execute, so the EXECUTE stage becomes `go test ./...` instead.
    """


# index.py

@dataclass(frozen=True)
class SpikeSummary:
    """One row of `atom poc list`."""
    slug: str
    question: str | None     # first question line of README.md, if present
    has_go_mod: bool

def list_spikes(poc_root: Path) -> list[SpikeSummary]: ...
```

## Behaviour

### `atom poc new` — scaffolding (B35–B43)

| # | Behaviour |
|---|---|
| **B35** | Creates `poc/<slug>/` containing exactly three files: `go.mod`, `main.go`, `README.md`. |
| **B36** | `go.mod` is generated by running **`go mod init <module-path>`** in the new directory. Atom never writes `go.mod` from a template. |
| **B37** | The module path is `spike/<slug>`. It is deliberately not a real domain — a spike is never published. |
| **B38** | If `go mod init` fails, the **entire scaffold is rolled back** and `ScaffoldError` is raised. A spike directory without a `go.mod` breaks the parent build, so a half-created spike is worse than none. |
| **B39** | `main.go` is a runnable `package main` that prints the question and exits `0`. A freshly scaffolded spike always runs. |
| **B40** | `main.go` carries the exit-code convention as a comment: `0` Confirmed, `1` Refuted, `2` Inconclusive. |
| **B41** | `README.md` records the question, the date, and empty Method / Result / Verdict sections. It is the draft of the POC report. |
| **B42** | A slug must match `^[a-z0-9]+(-[a-z0-9]+)*$`. Anything else raises `SlugError` naming the rule. |
| **B43** | If `poc/<slug>/` already exists, raise `FileExistsError`. Never overwrite — a spike may hold unrepeatable observations. |

### `atom poc run` — the three stages (B44–B52)

| # | Behaviour |
|---|---|
| **B44** | Runs three stages **in order**: `go vet .` → `go build -o <tmp> .` → execute. |
| **B45** | Stages **short-circuit**. A failed stage marks the remainder `skipped`. This is the deliberate opposite of `run_check` (B17), which runs every gate. Rationale below. |
| **B46** | BUILD failing and EXECUTE failing are **distinct reported outcomes**. `go run` conflates them; a developer cannot act on the conflated form. |
| **B47** | Both streams are captured for every stage and **neither is discarded**, even when empty. |
| **B48** | On failure, **stderr is rendered first**. On failure stdout is typically empty and stderr holds the message. |
| **B49** | The spike's **own exit code** is reported verbatim as `spike_exit_code`. It is never flattened. |
| **B50** | Exit codes `0`/`1`/`2` map to `CONFIRMED`/`REFUTED`/`INCONCLUSIVE`. |
| **B51** | Any other exit code maps to `UNKNOWN` and is shown numerically. Atom does not guess what `42` meant. |
| **B52** | The build artefact is written to a temp location outside the repo, and removed afterwards even when execution fails. A stray binary beside the source could be committed. |
| **B53** | A spike that runs longer than **300 seconds** is killed. `EXECUTE` is reported as timed out and the run exits `1`. Atom never hangs. The limit is overridable per run. |

### Library spikes (B54–B57)

A spike that is a library rather than `package main` has nothing to execute. Its
evidence lives in its tests instead.

| # | Behaviour |
|---|---|
| **B54** | Spike kind is detected by whether the package declares `package main` with a `main` function. Detection is a **fact about the source**, never a flag the developer has to remember to pass. |
| **B55** | For a `LIBRARY` spike, the EXECUTE stage runs **`go test ./...`** instead of building and running a binary. |
| **B56** | The BUILD stage still runs for a library spike — it must compile before its tests mean anything. |
| **B57** | A library spike can only be `CONFIRMED` or `REFUTED`, because `go test` exits `0` or `1` and has no third value. `INCONCLUSIVE` is **unreachable** for this kind, and the renderer says so explicitly rather than leaving the developer to wonder why their `t.Skip` did not produce it. |

### `atom poc list` (B58–B61)

| # | Behaviour |
|---|---|
| **B58** | Lists **direct children** of `poc/` only — consistent with `find_poc_modules_without_go_mod` (B19), which the developer confirmed in the Phase 1 gate. |
| **B59** | Each row shows slug, the question from `README.md`, and whether a `go.mod` is present. |
| **B60** | A spike **missing `go.mod` is flagged loudly**. That is the one state that breaks the parent build, and `atom check` already fails on it (B20). |
| **B61** | A missing or unreadable `poc/` yields an empty list, not an error. A repo with no spikes yet is normal. |

### CLI surface (B62–B66)

| # | Behaviour |
|---|---|
| **B62** | `atom poc new <slug> --question "..."`, `atom poc run <slug>`, `atom poc list`. |
| **B63** | Exit codes follow Phase 1's contract (B28–B34): `0` success, `1` the operation failed, `2` usage error. |
| **B64** | **`atom poc run` exits `0` whenever the spike actually ran — whatever its verdict.** A Refuted spike is a successful use of the method, not a malfunction. Non-zero means strictly *Atom could not run your spike*: it did not compile, it timed out, or `go.mod` was missing. *Refined by B69: a crash was not a case anyone had in mind here, and it is not a verdict either.* |
| **B65** | The verdict is therefore **output, not exit status**. A developer who wants CI to enforce an invariant makes the spike itself exit non-zero when the invariant breaks — as `poc/go-run-failure-modes/spike.py` already does. |
| **B66** | `--json` emits the full `SpikeResult`, reusing `SCHEMA_VERSION` from `report.py`. |

### Found by running the tool (B67–B70)

Everything above was written before the code existed. The four behaviours below
were not: each one was discovered by using the finished tool against a real Go
toolchain, and none of them would have been found by reading the code.

They are recorded separately rather than folded into the tables above, because
the distinction matters to this project's central claim. If POC-first only
surfaced things a careful reader would have caught anyway, it would not be worth
the step.

| # | Behaviour |
|---|---|
| **B67** | **A spike that answered has no failed stage.** The first end-to-end run of an exit-2 spike printed `FAIL execute exited 2` directly above `Verdict: INCONCLUSIVE`, and then exited `0` — three accounts of one event, two of them wrong. The EXECUTE stage's job is to run the spike; a non-zero exit is the spike's *answer*, not a malfunction. `StageResult.produced_an_answer` marks this, `failed_stage` exempts it, and the renderer says `answered with exit 2` rather than `exited 2`. |
| **B68** | **A crash is not a verdict.** A panicking Go binary exits `2` — byte-identical to Atom's *Inconclusive*. Measured, not assumed. Without disambiguation a spike that fell over would be reported as having carefully concluded "I could not tell". Atom reads exit `2` as `CRASHED` only when stderr carries **both** `panic:` and a `goroutine N [running]:` stack dump. Requiring both signals stops a spike that merely prints the word from being misread. Note the direction: this parse can only ever escalate the report, never soften a failure into a success, which is what keeps it compatible with Phase 1's rule that a parse must not override an exit code. |
| **B69** | **`atom poc run` exits non-zero on a crash**, refining B64. B64's principle was "a verdict is not a failure of Atom"; a crash is not a verdict, so the exit code keys on `SpikeResult.answered` rather than `ran`. All three real verdicts still exit `0`. `ran` and `answered` are both exposed in `--json`, since a crashed spike genuinely did run. |
| **B70** | **The CLI is smoke-tested in a real subprocess.** Every other test imports `atom.cli`, which defines every name regardless of ordering. `python -m atom.cli` does not: execution stops at `raise SystemExit(main())`, so anything defined below that line is missing when `main()` needs it. A `NameError` of exactly this shape shipped past 169 green tests. `test_cli.py` now invokes the CLI with `subprocess` and asserts no traceback. |

> **B68 is the strongest evidence for this framework's thesis so far.** Nothing
> about the code suggested exit `2` was overloaded. The collision exists in the
> Go runtime, is documented nowhere Atom's authors had read, and was found by
> deliberately crashing a program and looking at `$LASTEXITCODE`. A design
> review of `spike.py` would have approved the ambiguous mapping without
> comment — it is internally consistent, well-commented, and wrong.

## Error Handling

| Condition | Behaviour |
|---|---|
| Slug invalid | `SlugError` → exit `2`, one stderr line naming the rule |
| Spike already exists | `FileExistsError` → exit `2`, no overwrite |
| `go mod init` fails | Roll back the whole directory, `ScaffoldError` → exit `1` |
| Spike dir has no `go.mod` | Refuse to run; tell the developer it will also break `atom check` |
| Go not installed | Same message as Phase 1 — one cause, one message |
| Spike exceeds 300s | Kill, report `EXECUTE` as timed out, exit `1`. Never hang. |
| Spike exits non-zero | **Not an error.** A result. Reported with its verdict, exit `0`. |

That last row is the philosophical core of this phase. A Refuted spike is a *success* of
the method. Atom must never treat it as a malfunction.

## Trade-offs Considered

**Build-then-execute instead of `go run`.** Costs a temp file and one more stage.
Bought: unflattened exit codes and a clean separation of compile failure from run
failure. Not a preference — `go run` is disqualified by evidence (C1, C8).

**`run` short-circuits, `check` does not.** Inconsistent on purpose. In `check`, the
gates are independent and a developer wants every problem at once. In `run`, the stages
are *causally chained* — you cannot execute a binary that did not build. Reporting
"EXECUTE failed" after a build failure would be noise. Consistency for its own sake
would make the output worse.

**Shelling out to `go mod init` rather than templating.** Slower and needs Go present.
But a template would have hard-coded `go 1.23` when the toolchain writes `go 1.23.4`
(C7). We only know that because the spike ran.

**Scaffold rolls back; spikes never do.** Asymmetric deliberately. A half-scaffolded
directory is *dangerous* — it breaks the parent build. A failed spike run is *the normal
case* and its output is the whole point.

**`UNKNOWN` verdict rather than mapping everything.** Tempting to treat "not 0" as
Refuted. That is exactly the flattening this phase exists to avoid — reintroduced one
layer up.

**Exit `0` on a Refuted spike.** Loses the ability to fail CI on a verdict directly.
Bought: non-zero keeps a single, honest meaning — *Atom could not run your spike*. A
developer who wants an invariant enforced makes the spike assert it, which is stricter
and more explicit than inferring intent from a verdict.

**Detecting spike kind instead of declaring it.** Costs a source scan and an edge case
(a spike part-way through being converted). Bought: the developer cannot get it wrong,
and a spike that changes shape does not need its metadata updated to keep working.

## Out Of Scope

- Non-Go spikes.
- Generating spike *code* from the question. Atom scaffolds; the developer thinks.
- `go mod tidy` / spikes with external dependencies. `go mod init` was proven
  offline-safe; `tidy` was not.
- Promoting a spike into production code. Spikes are throwaway by definition.

## Resolved In Developer Review

Three points the POC left unsettled. Each was put to the developer rather than
assumed, and each is now binding.

| Question | Decision | Consequence |
|---|---|---|
| **Library spikes** — B44 assumed `package main`; a library has nothing to execute. | Fall back to **`go test ./...`** as the EXECUTE stage. A library spike's evidence naturally lives in a test. | B54–B57. Kind is **detected from the source**, not declared by a flag. |
| **Timeout default** — 120s was the one invented constant in the spec. | **300 seconds.** Some spikes legitimately loop or wait; a generous ceiling still prevents a hang. | B53. Still overridable per run. |
| **Exit code for a Refuted spike** — should CI go red? | **No.** Exit `0` whenever the spike ran. Non-zero means strictly *Atom could not run it*. | B64–B65. A Refuted spike is the method succeeding, and this session's own P6 refutation is the worked example. |

### A limitation that falls out of the library decision

`go test` exits `0` or `1` only. It has no third value. So a **library spike can never
report `INCONCLUSIVE`** — that verdict is reachable only by a `COMMAND` spike exiting `2`.

This is stated in B57 and must be surfaced in the output rather than left implicit. A
developer who writes `t.Skip("can't tell yet")` expecting *Inconclusive* will get
*Confirmed*, which is precisely the laundering this phase exists to prevent. If that
proves to bite in practice, the fix is a sentinel the library spike can print — but that
is speculation, and speculation does not belong in a design until a spike has tested it.

## Completeness Checklist

- [x] Every behaviour numbered and citable (B35–B66)
- [x] Every design decision traced to evidence or named as a judgement call
- [x] Failure modes specified, including the "not an error" case
- [x] Trade-offs recorded with the losing option stated
- [x] Deliberate inconsistency with Phase 1 (B45 vs B17) justified rather than hidden
- [x] Unevidenced assumptions surfaced as open questions, not buried
- [x] **Developer review complete — all three open questions resolved and recorded**
- [x] A limitation created *by* a review decision (B57) documented rather than left to be discovered
