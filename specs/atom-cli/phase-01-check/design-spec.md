---
project: "atom-cli"
phase: "phase-01-check"
author: "Atom (dogfooding)"
date: "2026-09-13"
status: "approved"
poc_report: "../poc-report.md"
---

# Design Spec — Phase 1: `atom check`

## Purpose

One command that decides whether a Go tree is green and prints evidence a developer can
paste directly into a gate. Every other Atom skill defers its "is this actually
working?" question to this command, which is what makes Atom's gates real rather than
asserted.

## Evidence Base

From [poc-report.md](../poc-report.md), verdict **Confirmed**:

- Nested modules under `poc/` are invisible to `./...` patterns. **Consequence:** the
  gates use plain `./...` with no exclusion logic.
- Go writes compile errors to **stderr**. **Consequence:** every gate captures both
  streams; a gate that only read stdout would report failure as success.
- `go.mod` presence is load-bearing for isolation. **Consequence:** `atom check` warns
  on any `poc/*` directory missing one.

Assumed, not proven: behaviour is consistent across Go versions and platforms. Mitigated
by always keeping raw output, and never letting a parse failure mask a real exit code.

> **Note.** This phase implements Atom's *tooling*, which is Python. The intent in
> [go-style.md](../../../skills/atom/references/go-style.md) still governs — explicit
> names, real doc comments, dependency injection — but the API below is Python.
> Recorded in `decisions.md`.

## Design Overview

Five gates run in sequence against one directory. Each produces a `GateResult`. The
results aggregate into a `CheckReport` that renders as text or JSON.

```
  cli.py ──▶ check.run_check(directory, gates, runner)
                      │
                      ▼
            ┌─────────────────────┐
            │  for each Gate:     │   build → vet → fmt → test → race
            │    gate.evaluate()  │
            │       │             │
            │       ▼             │
            │  runner.run(...)    │──▶ subprocess (stdout + stderr + exit)
            └─────────┬───────────┘
                      ▼
                 CheckReport  ──▶ report.render_text()
                                  report.render_json()
```

The runner is **injected** into gates rather than imported. That single decision is what
makes this phase testable without spawning processes.

## Public API

```python
# runner.py

class CommandOutcome(enum.Enum):
    """Why a command ended. Distinguishes 'ran and failed' from 'never ran'."""
    COMPLETED = "completed"        # process ran to completion; consult exit_code
    TIMED_OUT = "timed_out"        # exceeded the deadline and was killed
    TOOL_MISSING = "tool_missing"  # executable not found on PATH


@dataclass(frozen=True)
class CommandResult:
    """The complete record of one subprocess invocation."""
    command: tuple[str, ...]
    working_directory: Path
    outcome: CommandOutcome
    exit_code: int | None          # None unless outcome is COMPLETED
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def succeeded(self) -> bool: ...

    @property
    def combined_output(self) -> str: ...


class CommandRunner(Protocol):
    """Runs a command. Injected so tests can substitute a deterministic fake."""
    def run(self, command: Sequence[str], working_directory: Path,
            timeout_seconds: float = 300.0) -> CommandResult: ...


class SubprocessRunner:
    """The real runner. Captures stdout and stderr separately and never raises."""
    def run(self, command: Sequence[str], working_directory: Path,
            timeout_seconds: float = 300.0) -> CommandResult: ...
```

```python
# gates.py

class GateStatus(enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"    # not applicable, e.g. no test files
    WARNING = "warning"    # advisory only; never fails the check


@dataclass(frozen=True)
class GateResult:
    """One gate's verdict, together with the raw evidence that produced it."""
    name: str
    status: GateStatus
    summary: str               # one line, human-facing
    details: str               # verbatim command output
    required: bool             # False means a failure cannot fail the check
    duration_seconds: float


class Gate(Protocol):
    """Evaluates one Go quality signal against a directory."""
    name: str
    required: bool
    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult: ...


class BuildGate:     """go build ./..."""
class VetGate:       """go vet ./..."""
class FormatGate:    """gofmt -l . -- verdict comes from OUTPUT, not exit code"""
class TestGate:      """go test ./..."""
class RaceGate:      """go test -race ./..."""


def default_gates(enable_race: bool = True) -> list[Gate]: ...
```

```python
# check.py

@dataclass(frozen=True)
class CheckReport:
    """Aggregate verdict across all gates."""
    directory: Path
    gate_results: tuple[GateResult, ...]
    warnings: tuple[str, ...]      # non-gate advisories, e.g. poc/ missing go.mod
    total_duration_seconds: float

    @property
    def passed(self) -> bool: ...      # every REQUIRED gate passed or was skipped

    @property
    def exit_code(self) -> int: ...    # 0 when passed, otherwise 1


def run_check(directory: Path, gates: Sequence[Gate],
              runner: CommandRunner) -> CheckReport: ...


def find_poc_modules_without_go_mod(directory: Path) -> list[Path]: ...
```

```python
# report.py

def render_text(report: CheckReport, use_colour: bool = True) -> str: ...
def render_json(report: CheckReport) -> str: ...   # stable, versioned schema
```

## Types And Responsibilities

| Type | Responsibility | File |
|---|---|---|
| `CommandResult` | Record one subprocess invocation | `runner.py` |
| `SubprocessRunner` | Execute a command without raising | `runner.py` |
| `GateResult` | Record one gate's verdict with its evidence | `gates.py` |
| `BuildGate` / `VetGate` / `FormatGate` / `TestGate` / `RaceGate` | Evaluate one Go quality signal | `gates.py` |
| `CheckReport` | Aggregate gate results into a single verdict | `check.py` |
| `render_text` / `render_json` | Present a report in one format | `report.py` |

## Behaviour

Numbered; each becomes at least one test case.

**Runner**

1. `SubprocessRunner.run` returns a `CommandResult` with stdout and stderr captured
   **separately** and the real exit code.
2. `run` on a command exceeding `timeout_seconds` returns `outcome=TIMED_OUT` with
   `exit_code=None`, and does not raise.
3. `run` with an executable not on PATH returns `outcome=TOOL_MISSING`, and does not raise.
4. `run` never raises `CalledProcessError` — a failing command is data, not an exception.
5. `CommandResult.succeeded` is true only when `outcome is COMPLETED and exit_code == 0`.

**Gates**

6. `BuildGate` passes when `go build ./...` exits 0.
7. `BuildGate` fails when it exits non-zero, and `details` contains the **stderr** text.
8. `VetGate` behaves as 6–7 for `go vet ./...`.
9. `FormatGate` fails when `gofmt -l .` prints any filename, **even though its exit code
   is 0**. The verdict comes from stdout content, not the exit code.
10. `FormatGate` passes when `gofmt -l .` prints nothing.
11. `FormatGate` names the unformatted files in its `summary`.
12. `TestGate` passes when `go test ./...` exits 0.
13. `TestGate` fails on non-zero exit, and `details` preserves the full raw output.
14. `TestGate` returns `SKIPPED` when Go reports no test files in any package.
15. `RaceGate` runs `go test -race ./...`, and is `SKIPPED` when disabled.
16. Any gate whose command returns `TOOL_MISSING` yields `FAILED`, naming the missing tool.
17. A gate's `details` always contains verbatim command output, never a paraphrase.

**Check**

18. `run_check` evaluates **every** gate, including those after a failure. One failure
    never short-circuits the rest.
19. `CheckReport.passed` is true only when every gate with `required=True` passed or was
    skipped.
20. A `WARNING` gate never affects `passed`.
21. `CheckReport.exit_code` is 0 when `passed`, otherwise 1.
22. `find_poc_modules_without_go_mod` returns each directory directly under `poc/` that
    contains `.go` files but no `go.mod`.
23. Those directories appear in `CheckReport.warnings` and do **not** fail the check.

**Report**

24. `render_text` shows every gate with its status and duration.
25. `render_text` shows full `details` for failed gates only; passing gates show their
    summary line alone.
26. `render_json` emits a stable schema including a `schema_version` field.
27. `render_json` output parses as valid JSON for both passing and failing reports.

## Error Handling

| Condition | Behaviour | Returned |
|---|---|---|
| Executable not on PATH | Gate fails, naming the tool | `GateResult(FAILED)` |
| Command exceeds timeout | Gate fails, stating the limit | `GateResult(FAILED)` |
| Directory does not exist | Refuse before running any gate | `NotADirectoryError` |
| Directory has no `go.mod` | Refuse before running any gate | `NotAGoModuleError` |
| Test output unparseable | Verdict still follows the **exit code**; raw output preserved | `GateResult` plus a parse warning |

> Parsing never overrides an exit code. A parser that cannot read the output must not
> turn a real failure into a pass. The exit code is ground truth; the parse is a
> convenience layered on top.

## Concurrency

Phase 1 is **single-threaded and not safe for concurrent use.** Gates run in sequence.

Deliberate: Go's build cache serialises much of the work anyway, and sequential output is
far easier to read at a gate. Parallel execution is an extension point, not a phase 1
concern.

## Extension Points

- **New gates** implement the `Gate` protocol and join `default_gates()`. No existing
  gate changes.
- **New output formats** are new functions in `report.py` taking a `CheckReport`.
- **Alternative runners** implement `CommandRunner` — a recording runner for debugging,
  or a remote runner — without touching gate code.

## Trade-offs Considered

| Option | Chosen? | Why |
|---|---|---|
| Gates as classes implementing a Protocol | **Yes** | Adding a gate needs no edit to existing code |
| Gates as plain functions in a list | No | Harder to carry per-gate config such as `required` |
| Stop at the first failing gate | No | Developers want every problem in one run, not one per run |
| Raise on command failure | No | A failing command is an expected outcome here, not an exception |
| Parse `go test -json` | No | Richer, but adds a format dependency; exit codes suffice for phase 1 |
| Parallel gate execution | No | Marginal gain, interleaved output, real complexity. Deferred |

## Out Of Scope

Config loading (phase 3), phase state (phase 3), spikes (phase 2), git (phase 5),
coverage thresholds (phase 3 — phase 1 reports coverage but never fails on it).

## Completeness Checklist

- [x] Established facts and standing assumptions listed separately
- [x] Public API minimal, every symbol documented
- [x] Every signature checked for consistency at each occurrence
- [x] Behaviours numbered and independently verifiable
- [x] Error handling, concurrency and extension points specified
- [x] Concurrency safety stated explicitly (not safe — deliberate)
- [x] Trade-offs recorded including rejected options
