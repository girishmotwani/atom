"""Run a spike and report honestly what happened.

The design of this module is dictated by one observation, recorded in
specs/atom-cli/phase-02-poc/poc-report.md:

    `go run` flattens every non-zero exit code to 1.

    spike exits   via go run .    via built binary
    2             1               2
    3             1               3
    42            1               42

Atom's POC verdicts are three-valued -- 0 Confirmed, 1 Refuted, 2 Inconclusive.
Under `go run`, a spike saying *Inconclusive* would be reported by Atom as
*Refuted*: the framework falsifying the experiment it exists to run, silently,
with no way for the developer to notice.

So this module never uses `go run`. It builds, then executes the binary as a
separate stage. That also buys a second thing worth having: "did not compile"
and "compiled, then failed" become distinct reportable outcomes, where `go run`
merges them into one exit 1.
"""

from __future__ import annotations

import enum
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .runner import CommandResult, CommandRunner

DEFAULT_TIMEOUT_SECONDS = 300

# Matches a `package main` declaration at the start of a line, ignoring
# comments and leading whitespace. A spike declaring anything else is a library
# and has no binary to run.
PACKAGE_MAIN_PATTERN = re.compile(r"^\s*package\s+main\s*$", re.MULTILINE)
FUNC_MAIN_PATTERN = re.compile(r"^\s*func\s+main\s*\(\s*\)", re.MULTILINE)


class Stage(enum.Enum):
    """The stages of running a spike, reported separately rather than merged."""

    VET = "vet"
    BUILD = "build"
    EXECUTE = "execute"


class SpikeKind(enum.Enum):
    """How a spike produces evidence, which determines the EXECUTE stage."""

    COMMAND = "command"
    LIBRARY = "library"


class Verdict(enum.Enum):
    """The spike's own answer, taken from its exit code.

    UNKNOWN exists so that an unrecognised exit code is reported as what it is
    rather than guessed at. Mapping "anything non-zero" to REFUTED would
    reintroduce, one layer up, exactly the flattening this module avoids.

    CRASHED exists because a panicking Go binary exits 2 -- the same code a
    spike uses to say INCONCLUSIVE. Without the distinction, a spike that
    crashed would be reported as having carefully concluded "I could not tell".
    """

    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"
    CRASHED = "crashed"
    UNKNOWN = "unknown"


# The Go runtime announces a panic with `panic:` followed by a goroutine stack
# dump. Requiring BOTH guards against a developer whose spike simply prints the
# word -- `panic: is what I want to avoid` is a note, not a crash.
GO_PANIC_MARKER = "panic:"
GO_STACK_DUMP_PATTERN = re.compile(r"^goroutine \d+ \[", re.MULTILINE)

# The exit code the Go runtime uses when a program dies from an unrecovered
# panic. It collides with Atom's INCONCLUSIVE, which is why the stderr
# signature has to break the tie.
GO_PANIC_EXIT_CODE = 2


# The exit-code vocabulary a spike uses to state its own result. Anything
# outside this mapping is UNKNOWN, never coerced into a neighbouring verdict.
VERDICT_BY_EXIT_CODE = {
    0: Verdict.CONFIRMED,
    1: Verdict.REFUTED,
    2: Verdict.INCONCLUSIVE,
}

# A library spike's verdict comes from `go test`, which exits 0 or 1 and has no
# third value. INCONCLUSIVE is therefore unreachable for this kind, and must
# not be inferred from an exit code that `go test` would never produce for that
# reason. Reading exit 2 as "the developer meant Inconclusive" would be a guess
# dressed up as an observation.
VERDICT_BY_EXIT_CODE_FOR_LIBRARY = {
    0: Verdict.CONFIRMED,
    1: Verdict.REFUTED,
}


class NotASpikeError(ValueError):
    """The directory is not a spike, because it has no go.mod of its own."""


@dataclass(frozen=True)
class StageResult:
    """One stage's outcome, keeping both streams because either can carry the answer."""

    stage: Stage
    exit_code: int | None
    stdout: str
    stderr: str
    skipped: bool = False
    timed_out: bool = False

    @property
    def succeeded(self) -> bool:
        """A skipped stage has not succeeded; it has not run."""

        return not self.skipped and not self.timed_out and self.exit_code == 0

    @property
    def produced_an_answer(self) -> bool:
        """True when this stage is the spike stating its result.

        Only EXECUTE can answer the question, and it answers by exiting -- with
        any code. Exit 2 means *Inconclusive*; it does not mean the stage went
        wrong. Treating a non-zero exit here as a failure would tell the
        developer their working spike was broken, which is precisely the
        confusion this phase exists to remove.

        A stage that was skipped or killed answered nothing, so it is excluded.
        """

        return self.stage is Stage.EXECUTE and not self.skipped and not self.timed_out and self.exit_code is not None


@dataclass(frozen=True)
class SpikeResult:
    """Everything that happened when a spike ran, with nothing smoothed over."""

    slug: str
    kind: SpikeKind
    stages: list[StageResult]
    verdict: Verdict | None
    spike_exit_code: int | None

    @property
    def failed_stage(self) -> Stage | None:
        """Return the first stage that genuinely went wrong, if any.

        EXECUTE is deliberately exempt when it produced an answer: a spike
        exiting 1 or 2 is stating its verdict, not malfunctioning. Calling that
        a failed stage is what made the tool report `FAIL execute exited 2`
        directly above `Verdict: INCONCLUSIVE` -- two contradictory accounts of
        the same event. A crash is the exception: there, EXECUTE really did
        fail, so it is reported.
        """

        for stage_result in self.stages:
            if stage_result.skipped:
                continue
            if stage_result.produced_an_answer and self.verdict is not Verdict.CRASHED:
                continue
            if not stage_result.succeeded:
                return stage_result.stage
        return None

    @property
    def compiled(self) -> bool:
        """Distinguish 'did not compile' from 'compiled, then failed'."""

        return any(stage.stage is Stage.BUILD and stage.succeeded for stage in self.stages)

    @property
    def ran(self) -> bool:
        """True when the spike actually executed, whatever answer it gave.

        This drives the CLI exit code. A Refuted spike still ran -- it is the
        method working, not a malfunction -- so it must not be reported as a
        failure of Atom.
        """

        return any(stage.stage is Stage.EXECUTE and not stage.skipped and not stage.timed_out for stage in self.stages)

    @property
    def answered(self) -> bool:
        """True when the spike ran AND concluded something.

        Distinct from `ran`. All three verdicts -- Confirmed, Refuted,
        Inconclusive -- are answers, and Refuted is arguably the most valuable
        of them. A crash is not: the spike stopped rather than concluded. This
        is what the CLI exit code is derived from, so a crashed spike does not
        report success.
        """

        return self.ran and self.verdict not in (None, Verdict.CRASHED)


def run_spike(
    spike_directory: Path,
    runner: CommandRunner,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> SpikeResult:
    """Vet, build, then execute a spike, reporting each stage separately.

    Stages short-circuit: a failed stage marks the rest skipped. This is the
    deliberate opposite of run_check, whose gates are independent and all worth
    running. Here the stages are causally chained -- reporting "execute failed"
    after a build failure would be noise, not information.
    """

    if not (spike_directory / "go.mod").exists():
        raise NotASpikeError(
            f"{spike_directory} has no go.mod of its own. "
            "Without one its source joins the parent module, so a broken spike breaks the parent build. "
            "`atom check` reports this too."
        )

    kind = detect_spike_kind(spike_directory)
    stages: list[StageResult] = []

    vet = _run_stage(Stage.VET, ["go", "vet", "."], spike_directory, runner, timeout_seconds)
    stages.append(vet)
    if not vet.succeeded:
        stages.extend(_skip_remaining_after(Stage.VET, kind))
        return _build_result(spike_directory, kind, stages)

    # A library has no binary to name, so `-o` is omitted. Asking Go to write an
    # executable for a non-main package fails for a reason unrelated to the
    # developer's question, which would be a confusing thing to report.
    with tempfile.TemporaryDirectory(prefix="atom-spike-") as temporary_directory:
        binary_path = Path(temporary_directory) / _binary_name(spike_directory)
        build_command = ["go", "build", "."] if kind is SpikeKind.LIBRARY else ["go", "build", "-o", str(binary_path), "."]

        build = _run_stage(Stage.BUILD, build_command, spike_directory, runner, timeout_seconds)
        stages.append(build)
        if not build.succeeded:
            stages.append(_skipped(_execute_stage_for(kind)))
            return _build_result(spike_directory, kind, stages)

        execute_command = ["go", "test", "./..."] if kind is SpikeKind.LIBRARY else [str(binary_path)]
        stages.append(_run_stage(_execute_stage_for(kind), execute_command, spike_directory, runner, timeout_seconds))

    return _build_result(spike_directory, kind, stages)


def detect_spike_kind(spike_directory: Path) -> SpikeKind:
    """Decide whether a spike is runnable from its source, not from a flag.

    Detection rather than declaration means the developer cannot get it wrong,
    and a spike that changes shape mid-investigation keeps working without
    anyone remembering to update metadata.
    """

    for source_file in sorted(spike_directory.glob("*.go")):
        if source_file.name.endswith("_test.go"):
            continue
        try:
            source = source_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if PACKAGE_MAIN_PATTERN.search(source) and FUNC_MAIN_PATTERN.search(source):
            return SpikeKind.COMMAND

    return SpikeKind.LIBRARY


def _execute_stage_for(kind: SpikeKind) -> Stage:
    """Both kinds report an EXECUTE stage; only the command behind it differs."""

    return Stage.EXECUTE


def _run_stage(
    stage: Stage,
    command: list[str],
    working_directory: Path,
    runner: CommandRunner,
    timeout_seconds: int,
) -> StageResult:
    result: CommandResult = runner.run(command, working_directory, timeout_seconds)
    return StageResult(
        stage=stage,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
        timed_out=result.outcome.name == "TIMED_OUT",
    )


def _skipped(stage: Stage) -> StageResult:
    return StageResult(stage=stage, exit_code=None, stdout="", stderr="", skipped=True)


def _skip_remaining_after(stage: Stage, kind: SpikeKind) -> list[StageResult]:
    return [_skipped(Stage.BUILD), _skipped(_execute_stage_for(kind))]


def _binary_name(spike_directory: Path) -> str:
    """Name the binary after the spike, so a stray process is identifiable."""

    import sys

    suffix = ".exe" if sys.platform == "win32" else ""
    return f"{spike_directory.name}{suffix}"


def _build_result(spike_directory: Path, kind: SpikeKind, stages: list[StageResult]) -> SpikeResult:
    """Assemble the result, deriving the verdict only from a stage that actually ran."""

    execute_stage = next(
        (stage for stage in stages if stage.stage is Stage.EXECUTE and not stage.skipped and not stage.timed_out),
        None,
    )

    # A spike that never executed has not answered anything. Leaving the verdict
    # as None is the honest representation; inventing one would be the exact
    # failure this module exists to prevent.
    if execute_stage is None or execute_stage.exit_code is None:
        return SpikeResult(spike_directory.name, kind, stages, None, None)

    exit_code = execute_stage.exit_code
    verdict_mapping = VERDICT_BY_EXIT_CODE_FOR_LIBRARY if kind is SpikeKind.LIBRARY else VERDICT_BY_EXIT_CODE
    verdict = verdict_mapping.get(exit_code, Verdict.UNKNOWN)

    # B68: exit 2 is ambiguous -- it is both "Inconclusive" and the Go runtime's
    # code for an unrecovered panic. Corroborating stderr breaks the tie. This
    # only ever escalates the report (INCONCLUSIVE -> CRASHED); it can never
    # turn a failure into a success, which is what keeps it consistent with the
    # rule that parsed output must not override an exit code.
    if _looks_like_a_go_panic(exit_code, execute_stage.stderr):
        verdict = Verdict.CRASHED

    return SpikeResult(spike_directory.name, kind, stages, verdict, exit_code)


def _looks_like_a_go_panic(exit_code: int, stderr: str) -> bool:
    """Both signals are required: the word alone is something a spike might print."""

    if exit_code != GO_PANIC_EXIT_CODE:
        return False
    return GO_PANIC_MARKER in stderr and GO_STACK_DUMP_PATTERN.search(stderr) is not None
