"""Behaviour tests for running a spike (B44-B57).

Written before spike.py exists. The first run must fail on import -- RED.

The central claim these tests defend: a broken spike must never be reportable
as a working one, and a spike's own exit code must reach the developer
unflattened. `go run` fails both, which is why the runner builds and executes
in separate stages.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from atom.runner import CommandOutcome, CommandResult
from atom.spike import (
    SpikeKind,
    Stage,
    Verdict,
    run_spike,
)

PACKAGE_MAIN_SOURCE = """package main

import "fmt"

func main() {
	fmt.Println("hello")
}
"""

LIBRARY_SOURCE = """package streaming

// Decode is the thing under investigation.
func Decode(input string) int {
	return len(input)
}
"""


def test_runner_error_cannot_confirm_a_spike(command_spike):
    failure = CommandResult(
        ("fixture",), command_spike, CommandOutcome.RUNNER_ERROR, None,
        "Confirmed-looking stdout", "atom: Windows cleanup incomplete: native refusal", 0.1,
    )
    result = run_spike(command_spike, ScriptedRunner({"execute": failure}))
    assert result.verdict is not Verdict.CONFIRMED
    assert result.failed_stage is Stage.EXECUTE
    assert not result.stages[-1].produced_an_answer
    assert "native refusal" in result.stages[-1].stderr


class ScriptedRunner:
    """Match commands by prefix, because the build path is a temp file.

    The conftest FakeRunner keys on the exact command tuple, which cannot work
    here: `go build -o <temp>` contains a path the test cannot predict, and
    executing the binary IS that path. Matching on a prefix keeps the test
    honest about the parts it actually cares about.
    """

    def __init__(self, outcomes: dict[str, CommandResult] | None = None) -> None:
        self.outcomes = outcomes or {}
        self.calls: list[tuple[tuple[str, ...], Path, float]] = []

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
        stdin_text: str | None = None,
    ) -> CommandResult:
        command_tuple = tuple(command)
        self.calls.append((command_tuple, working_directory, timeout_seconds))

        key = self._classify(command_tuple)

        # A build is only meaningful if it produces a binary, so the fake
        # creates one. Without this, "did we execute the built binary?" would
        # be unanswerable.
        #
        # A library build has no `-o`, by design -- asking Go to write an
        # executable for a non-main package fails for a reason unrelated to the
        # developer's question. So the side effect is conditional on `-o`
        # actually being there.
        if key == "build" and "-o" in command_tuple and self.outcomes.get(key, _ok()).succeeded:
            Path(command_tuple[command_tuple.index("-o") + 1]).write_text("fake binary", encoding="utf-8")

        return self.outcomes.get(key, _ok())

    @staticmethod
    def _classify(command: tuple[str, ...]) -> str:
        if command[:2] == ("go", "vet"):
            return "vet"
        if command[:2] == ("go", "build"):
            return "build"
        if command[:2] == ("go", "test"):
            return "test"
        return "execute"

    def commands_named(self, key: str) -> list[tuple[str, ...]]:
        return [call[0] for call in self.calls if self._classify(call[0]) == key]

    @property
    def stage_order(self) -> list[str]:
        return [self._classify(call[0]) for call in self.calls]


def _ok(stdout: str = "", stderr: str = "") -> CommandResult:
    return CommandResult((), Path("."), CommandOutcome.COMPLETED, 0, stdout, stderr, 0.1)


def _failed(exit_code: int = 1, stdout: str = "", stderr: str = "") -> CommandResult:
    return CommandResult((), Path("."), CommandOutcome.COMPLETED, exit_code, stdout, stderr, 0.1)


def _timed_out() -> CommandResult:
    return CommandResult((), Path("."), CommandOutcome.TIMED_OUT, None, "", "Command timed out.", 300.0)


@pytest.fixture
def command_spike(tmp_path: Path) -> Path:
    """A `package main` spike -- the kind that builds into a runnable binary."""

    directory = tmp_path / "poc" / "json-streaming"
    directory.mkdir(parents=True)
    (directory / "go.mod").write_text("module spike/json-streaming\n\ngo 1.23.4\n", encoding="utf-8")
    (directory / "main.go").write_text(PACKAGE_MAIN_SOURCE, encoding="utf-8")
    return directory


@pytest.fixture
def library_spike(tmp_path: Path) -> Path:
    """A library spike -- nothing to execute, so its evidence lives in tests."""

    directory = tmp_path / "poc" / "decoder"
    directory.mkdir(parents=True)
    (directory / "go.mod").write_text("module spike/decoder\n\ngo 1.23.4\n", encoding="utf-8")
    (directory / "streaming.go").write_text(LIBRARY_SOURCE, encoding="utf-8")
    return directory


# --------------------------------------------------------------------------
# B44 -- three ordered stages
# --------------------------------------------------------------------------


def test_runs_vet_then_build_then_execute(command_spike: Path) -> None:
    """B44: order matters -- vet is cheapest, execute is the only one with side effects."""

    runner = ScriptedRunner()
    run_spike(command_spike, runner)

    assert runner.stage_order == ["vet", "build", "execute"]


def test_reports_all_three_stages(command_spike: Path) -> None:
    """B44: the developer sees what happened at each stage, not just the end."""

    result = run_spike(command_spike, ScriptedRunner())

    assert [stage.stage for stage in result.stages] == [Stage.VET, Stage.BUILD, Stage.EXECUTE]


def test_never_uses_go_run(command_spike: Path) -> None:
    """The finding that shaped this phase: `go run` flattens exit codes to 1.

    Pinned as a test because it is the kind of thing a later refactor would
    'simplify' back in, silently reintroducing the bug.
    """

    runner = ScriptedRunner()
    run_spike(command_spike, runner)

    for command, _, _ in runner.calls:
        assert command[:2] != ("go", "run"), "go run flattens exit codes and must never be used"


# --------------------------------------------------------------------------
# B45, B46 -- short-circuit, and build/execute kept distinct
# --------------------------------------------------------------------------


def test_build_failure_skips_execute(command_spike: Path) -> None:
    """B45: you cannot execute a binary that was never produced."""

    result = run_spike(command_spike, ScriptedRunner({"build": _failed(stderr="main.go:6: cannot use...")}))

    execute_stage = next(stage for stage in result.stages if stage.stage is Stage.EXECUTE)
    assert execute_stage.skipped


def test_vet_failure_skips_build_and_execute(command_spike: Path) -> None:
    """B45: stages are causally chained, unlike check's independent gates (B17)."""

    result = run_spike(command_spike, ScriptedRunner({"vet": _failed(stderr="suspicious construct")}))

    skipped = [stage.stage for stage in result.stages if stage.skipped]
    assert skipped == [Stage.BUILD, Stage.EXECUTE]


def test_build_failure_is_reported_as_build_not_execute(command_spike: Path) -> None:
    """B46: `go run` conflates these two; a developer cannot act on the conflated form."""

    result = run_spike(command_spike, ScriptedRunner({"build": _failed(stderr="compile error")}))

    assert result.failed_stage is Stage.BUILD
    assert result.compiled is False


def test_execute_failure_is_reported_as_execute_not_build(command_spike: Path) -> None:
    """B46: 'it compiled then crashed' is a different problem from 'it did not compile'.

    The fake here reproduces a *real* Go panic -- exit 2 with a goroutine stack
    dump -- because that is what one actually looks like (measured, see B68).
    An earlier version of this test used exit 1 and a bare `panic:` line, which
    no Go program has ever produced; it passed while describing something that
    cannot happen.
    """

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stderr=GO_PANIC_STDERR)}))

    assert result.failed_stage is Stage.EXECUTE
    assert result.compiled is True


# --------------------------------------------------------------------------
# B47 -- both streams preserved
# --------------------------------------------------------------------------


def test_captures_both_streams_from_the_spike(command_spike: Path) -> None:
    """B47: the POC proved both streams survive and stay separate. Keep both."""

    runner = ScriptedRunner({"execute": _failed(3, stdout="THIS-IS-STDOUT", stderr="THIS-IS-STDERR")})
    result = run_spike(command_spike, runner)

    execute_stage = next(stage for stage in result.stages if stage.stage is Stage.EXECUTE)
    assert execute_stage.stdout == "THIS-IS-STDOUT"
    assert execute_stage.stderr == "THIS-IS-STDERR"


def test_keeps_stdout_from_a_spike_that_failed(command_spike: Path) -> None:
    """A failing spike's stdout often holds the measurements that explain why."""

    runner = ScriptedRunner({"execute": _failed(1, stdout="throughput: 12MB/s", stderr="")})
    result = run_spike(command_spike, runner)

    execute_stage = next(stage for stage in result.stages if stage.stage is Stage.EXECUTE)
    assert "throughput" in execute_stage.stdout


# --------------------------------------------------------------------------
# B49, B50, B51 -- the spike's own exit code, unflattened
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "exit_code, expected_verdict",
    [
        (0, Verdict.CONFIRMED),
        (1, Verdict.REFUTED),
        (2, Verdict.INCONCLUSIVE),
    ],
)
def test_maps_exit_code_to_verdict(command_spike: Path, exit_code: int, expected_verdict: Verdict) -> None:
    """B50: the three-valued vocabulary `go run` would have destroyed."""

    outcome = _ok() if exit_code == 0 else _failed(exit_code)
    result = run_spike(command_spike, ScriptedRunner({"execute": outcome}))

    assert result.verdict is expected_verdict


def test_inconclusive_survives_as_inconclusive(command_spike: Path) -> None:
    """The single most important test in this phase.

    Under `go run`, exit 2 arrives as exit 1 and Inconclusive is reported as
    Refuted -- Atom falsifying the experiment it exists to run. If this test
    ever fails, the framework has started laundering results.
    """

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2)}))

    assert result.spike_exit_code == 2
    assert result.verdict is Verdict.INCONCLUSIVE
    assert result.verdict is not Verdict.REFUTED


@pytest.mark.parametrize("exit_code", [3, 7, 42, 127])
def test_unrecognised_exit_code_is_unknown_not_refuted(command_spike: Path, exit_code: int) -> None:
    """B51: mapping 'not 0' to Refuted would reintroduce flattening one layer up."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(exit_code)}))

    assert result.verdict is Verdict.UNKNOWN
    assert result.spike_exit_code == exit_code


def test_no_verdict_when_the_spike_never_ran(command_spike: Path) -> None:
    """B49: a spike that did not compile has not answered anything."""

    result = run_spike(command_spike, ScriptedRunner({"build": _failed()}))

    assert result.verdict is None
    assert result.spike_exit_code is None
    assert result.ran is False


# --------------------------------------------------------------------------
# B52 -- the build artefact never lands beside the source
# --------------------------------------------------------------------------


def test_binary_is_not_left_in_the_spike_directory(command_spike: Path) -> None:
    """B52: a stray binary beside the source could be committed."""

    before = {path.name for path in command_spike.iterdir()}
    run_spike(command_spike, ScriptedRunner())

    assert {path.name for path in command_spike.iterdir()} == before


def test_binary_is_removed_even_when_the_spike_fails(command_spike: Path) -> None:
    """B52: cleanup must not depend on the happy path -- failure is the normal case."""

    before = {path.name for path in command_spike.iterdir()}
    run_spike(command_spike, ScriptedRunner({"execute": _failed(1, stderr="panic")}))

    assert {path.name for path in command_spike.iterdir()} == before


def test_build_output_path_is_outside_the_spike_directory(command_spike: Path) -> None:
    """B52: verify the -o target directly, not just that cleanup happened."""

    runner = ScriptedRunner()
    run_spike(command_spike, runner)

    build_command = runner.commands_named("build")[0]
    output_path = Path(build_command[build_command.index("-o") + 1])
    assert command_spike not in output_path.parents


# --------------------------------------------------------------------------
# B53 -- timeout
# --------------------------------------------------------------------------


def test_default_timeout_is_300_seconds(command_spike: Path) -> None:
    """B53: agreed in developer review; some spikes legitimately loop or wait."""

    runner = ScriptedRunner()
    run_spike(command_spike, runner)

    execute_call = next(call for call in runner.calls if runner._classify(call[0]) == "execute")
    assert execute_call[2] == 300


def test_timeout_is_overridable(command_spike: Path) -> None:
    """B53: a developer who knows their spike is fast should be able to say so."""

    runner = ScriptedRunner()
    run_spike(command_spike, runner, timeout_seconds=5)

    execute_call = next(call for call in runner.calls if runner._classify(call[0]) == "execute")
    assert execute_call[2] == 5


def test_timed_out_spike_has_no_verdict(command_spike: Path) -> None:
    """B53: a spike that was killed did not answer its question."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _timed_out()}))

    assert result.verdict is None
    assert result.failed_stage is Stage.EXECUTE


# --------------------------------------------------------------------------
# B54-B57 -- library spikes
# --------------------------------------------------------------------------


def test_detects_a_command_spike_from_its_source(command_spike: Path) -> None:
    """B54: kind is a fact about the source, not a flag to remember."""

    result = run_spike(command_spike, ScriptedRunner())

    assert result.kind is SpikeKind.COMMAND


def test_detects_a_library_spike_from_its_source(library_spike: Path) -> None:
    """B54: no `package main`, so there is nothing to execute."""

    result = run_spike(library_spike, ScriptedRunner())

    assert result.kind is SpikeKind.LIBRARY


def test_library_spike_runs_go_test_instead_of_a_binary(library_spike: Path) -> None:
    """B55: a library spike's evidence naturally lives in its tests."""

    runner = ScriptedRunner()
    run_spike(library_spike, runner)

    assert runner.commands_named("test"), "library spike should run `go test`"
    assert runner.stage_order == ["vet", "build", "test"]


def test_library_spike_still_builds_first(library_spike: Path) -> None:
    """B56: tests mean nothing if the package does not compile."""

    result = run_spike(library_spike, ScriptedRunner({"build": _failed(stderr="syntax error")}))

    assert result.failed_stage is Stage.BUILD
    assert result.compiled is False


def test_library_spike_passing_tests_is_confirmed(library_spike: Path) -> None:
    """B57: go test exits 0 on success."""

    result = run_spike(library_spike, ScriptedRunner())

    assert result.verdict is Verdict.CONFIRMED


def test_library_spike_failing_tests_is_refuted(library_spike: Path) -> None:
    """B57: go test exits 1 on failure."""

    result = run_spike(library_spike, ScriptedRunner({"test": _failed(1, stdout="FAIL")}))

    assert result.verdict is Verdict.REFUTED


def test_library_spike_can_never_be_inconclusive(library_spike: Path) -> None:
    """B57: a limitation created BY the review decision, pinned so it stays visible.

    `go test` exits 0 or 1 only. A developer writing t.Skip("can't tell yet")
    and expecting Inconclusive will get Confirmed. That is documented rather
    than hidden -- and this test exists so nobody later 'fixes' it by guessing.
    """

    result = run_spike(library_spike, ScriptedRunner({"test": _failed(2)}))

    assert result.verdict is not Verdict.INCONCLUSIVE
    assert result.verdict is Verdict.UNKNOWN


def test_library_spike_does_not_build_a_binary(library_spike: Path) -> None:
    """B55: building an executable from a library would fail for the wrong reason."""

    runner = ScriptedRunner()
    run_spike(library_spike, runner)

    build_command = runner.commands_named("build")[0]
    assert "-o" not in build_command, "a library has no binary to name"


# --------------------------------------------------------------------------
# B67 -- a spike that ran did not "fail", whatever it answered
#
# Found by running the tool end-to-end, not by unit testing it. A spike
# exiting 2 was rendered `FAIL execute exited 2` while the verdict line said
# INCONCLUSIVE and the command exited 0 -- three different stories about the
# same event. The spike ran exactly as intended; 2 is its ANSWER, not a
# malfunction.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("exit_code", [0, 1, 2, 42])
def test_execute_stage_that_produced_an_answer_is_not_a_failure(command_spike: Path, exit_code: int) -> None:
    """B67: Atom's job at this stage is to run the spike. It ran."""

    outcome = _ok() if exit_code == 0 else _failed(exit_code)
    result = run_spike(command_spike, ScriptedRunner({"execute": outcome}))

    execute_stage = next(stage for stage in result.stages if stage.stage is Stage.EXECUTE)
    assert execute_stage.produced_an_answer is True


def test_execute_stage_that_timed_out_did_not_produce_an_answer(command_spike: Path) -> None:
    """B67: a killed spike answered nothing -- that is a genuine failure."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _timed_out()}))

    execute_stage = next(stage for stage in result.stages if stage.stage is Stage.EXECUTE)
    assert execute_stage.produced_an_answer is False


def test_skipped_execute_stage_did_not_produce_an_answer(command_spike: Path) -> None:
    """B67: a spike that never ran cannot have answered."""

    result = run_spike(command_spike, ScriptedRunner({"build": _failed()}))

    execute_stage = next(stage for stage in result.stages if stage.stage is Stage.EXECUTE)
    assert execute_stage.produced_an_answer is False


@pytest.mark.parametrize("stage_name", ["vet", "build"])
def test_vet_and_build_stages_never_claim_to_produce_an_answer(command_spike: Path, stage_name: str) -> None:
    """B67: only EXECUTE answers the question. vet and build are pass/fail."""

    result = run_spike(command_spike, ScriptedRunner())

    stage = next(s for s in result.stages if s.stage.value == stage_name)
    assert stage.produced_an_answer is False


# --------------------------------------------------------------------------
# B68 -- a crash is not a verdict
#
# Found by probing a real binary, not by reasoning about it: a panicking Go
# program exits 2 -- the same code Atom reads as INCONCLUSIVE. Without
# disambiguation, a spike that crashed would be reported as having carefully
# concluded "I could not tell", which is a lie the developer would believe.
#
# The signature is unambiguous: the runtime writes `panic:` and a
# `goroutine N [running]:` stack dump to stderr. Note the direction of this
# parse -- it can only make the report MORE severe, never soften a failure
# into a success. That is what keeps it compatible with Phase 1's rule that a
# parse must never override an exit code.
# --------------------------------------------------------------------------

GO_PANIC_STDERR = """panic: runtime error: index out of range [5] with length 0

goroutine 1 [running]:
main.main()
	/tmp/spike/main.go:5 +0x1d
"""


def test_panicking_spike_is_crashed_not_inconclusive(command_spike: Path) -> None:
    """B68: the discovery that a panic and Inconclusive share exit code 2."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stderr=GO_PANIC_STDERR)}))

    assert result.verdict is Verdict.CRASHED
    assert result.verdict is not Verdict.INCONCLUSIVE


def test_deliberate_exit_2_is_still_inconclusive(command_spike: Path) -> None:
    """B68: the control. Without this, 'always CRASHED' would pass the test above."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stdout="too close to call")}))

    assert result.verdict is Verdict.INCONCLUSIVE


def test_crash_detection_needs_both_the_exit_code_and_the_signature(command_spike: Path) -> None:
    """B68: a spike that merely mentions panics in its output has not crashed."""

    chatty = _failed(2, stdout="we should check whether this can panic under load")
    result = run_spike(command_spike, ScriptedRunner({"execute": chatty}))

    assert result.verdict is Verdict.INCONCLUSIVE


def test_crash_detection_requires_a_stack_dump_not_just_the_word(command_spike: Path) -> None:
    """B68: `panic:` alone could be a developer's own message on stderr."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stderr="panic: is what I want to avoid")}))

    assert result.verdict is Verdict.INCONCLUSIVE


def test_a_crashed_spike_still_reports_its_exit_code(command_spike: Path) -> None:
    """B68: the raw observation survives the interpretation."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stderr=GO_PANIC_STDERR)}))

    assert result.spike_exit_code == 2


def test_a_crashed_spike_did_not_answer(command_spike: Path) -> None:
    """B69: a crash is not a verdict, so it must not be reported as one.

    B64 made `atom poc run` exit 0 "whenever the spike ran", because a Refuted
    spike is the method working. A crash is different in kind: the spike did
    not conclude anything, it fell over. Reporting that as success would hide
    a broken spike behind a green exit code.
    """

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stderr=GO_PANIC_STDERR)}))

    assert result.ran is True, "it did run -- that is not in question"
    assert result.answered is False


@pytest.mark.parametrize("exit_code", [0, 1, 2])
def test_a_spike_that_concluded_anything_has_answered(command_spike: Path, exit_code: int) -> None:
    """B69: the control. All three verdicts are answers, including Refuted."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(exit_code)}))

    assert result.answered is True


# --------------------------------------------------------------------------
# B67 -- a spike that answered has no "failed stage"
#
# `failed_stage` feeds both the text renderer and the JSON `failed_stage`
# field. Reporting `execute` there for a spike that answered Inconclusive is
# how the tool ended up telling three different stories about one event:
# `FAIL execute exited 2`, `Verdict: INCONCLUSIVE`, and process exit 0.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("exit_code", [1, 2])
def test_a_spike_that_answered_has_no_failed_stage(command_spike: Path, exit_code: int) -> None:
    """B67: non-zero from EXECUTE is the answer, not a broken stage."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(exit_code)}))

    assert result.failed_stage is None


def test_a_crashed_spike_does_have_a_failed_stage(command_spike: Path) -> None:
    """B67/B68: the control -- a crash really is a failure of the execute stage."""

    result = run_spike(command_spike, ScriptedRunner({"execute": _failed(2, stderr=GO_PANIC_STDERR)}))

    assert result.failed_stage is Stage.EXECUTE


def test_a_build_failure_is_still_a_failed_stage(command_spike: Path) -> None:
    """B67: the control -- only EXECUTE is allowed to answer with a non-zero code."""

    result = run_spike(command_spike, ScriptedRunner({"build": _failed(1, stderr="undefined: foo")}))

    assert result.failed_stage is Stage.BUILD


def test_library_spike_panicking_is_also_crashed(command_spike: Path, library_spike: Path) -> None:
    """B68: `go test` also surfaces a panic, and it is a crash there too."""

    result = run_spike(library_spike, ScriptedRunner({"test": _failed(2, stderr=GO_PANIC_STDERR)}))

    assert result.verdict is Verdict.CRASHED
