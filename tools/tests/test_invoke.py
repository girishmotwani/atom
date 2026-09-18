"""Behaviour tests for model invocation (B107-B112, B129-B134, B137).

No test in this module may call a real model. Every test drives the
`CommandRunner` seam, so the suite is deterministic and free.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from atom.invoke import (
    DEFAULT_CONCURRENCY,
    DEFAULT_RUNS,
    InvocationReport,
    ModelRun,
    NoModelAvailable,
    RunOutcome,
    invoke_models,
    probe_models,
    review_command,
)
from atom.runner import CommandOutcome, CommandResult
from tests.conftest import FakeRunner, command_result

WORKDIR = Path("/repo")
PROMPT = "Review this diff."


def _script(models, *, stdout="[]", exit_code=0, outcome=CommandOutcome.COMPLETED):
    """Script both the probe and the review call for each model."""

    scripted: dict[tuple[str, ...], CommandResult] = {}
    for model in models:
        for command in (probe_command_for(model), review_command(model, PROMPT)):
            scripted[command] = command_result(
                command, WORKDIR, outcome, exit_code, stdout, ""
            )
    return FakeRunner(scripted)


def probe_command_for(model: str) -> tuple[str, ...]:
    from atom.invoke import probe_command

    return probe_command(model)


def issued(runner) -> list[tuple[str, ...]]:
    """Normalise the two fake runners' differing call logs to bare commands."""

    return [call[0] if isinstance(call[0], tuple) else call for call in runner.calls]


def reviews_only(runner, model: str) -> list[tuple[str, ...]]:
    probe = probe_command_for(model)
    return [command for command in issued(runner) if command != probe]


class SequencedRunner:
    """Return a different result for each successive call to the same command.

    `FakeRunner` keys on the command tuple, but B133 makes every run of a model
    an *identical* command. Testing "run 2 of 3 failed" therefore needs a runner
    that distinguishes calls by order rather than by content.
    """

    def __init__(self, sequences: dict[tuple[str, ...], list[CommandResult]]):
        self.sequences = sequences
        self.calls: list[tuple[str, ...]] = []
        self._lock = threading.Lock()

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        command_tuple = tuple(command)
        with self._lock:
            self.calls.append(command_tuple)
            queue = self.sequences.get(command_tuple)
            if not queue:
                return command_result(
                    command_tuple, working_directory, CommandOutcome.TOOL_MISSING,
                    None, "", "unscripted",
                )
            return queue.pop(0) if len(queue) > 1 else queue[0]


class TestMandatoryFlags:
    """B107, B108, B109 - each flag is here because a measurement demanded it."""

    def test_uses_silent_and_never_output_format_json(self):
        # B107: the JSON envelope is a schema Atom does not control.
        command = review_command("gpt-5.4", PROMPT)

        assert "--silent" in command
        assert "--output-format" not in command

    def test_always_disables_custom_instructions(self):
        # B108: without it the CLI loads AGENTS.md from the working directory
        # and the review becomes a property of the repo being reviewed.
        assert "--no-custom-instructions" in review_command("gpt-5.4", PROMPT)

    def test_always_disables_builtin_mcp_servers(self):
        # B109: measured 84s -> ~30s.
        assert "--disable-builtin-mcps" in review_command("gpt-5.4", PROMPT)

    def test_names_no_vendor_specific_mcp_servers_by_default(self):
        # The spike ran inside an enterprise environment and disabled two
        # named servers. Hard-coding those names would ship one company's
        # setup inside an open-source tool.
        command = review_command("gpt-5.4", PROMPT)

        assert "--disable-mcp-server" not in command

    def test_extra_mcp_servers_can_be_disabled_by_the_caller(self):
        command = review_command("gpt-5.4", PROMPT, disable_mcp_servers=("corp-mcp",))

        assert "--disable-mcp-server" in command
        assert "corp-mcp" in command

    def test_carries_the_prompt_and_the_model(self):
        command = review_command("claude-haiku-4.5", PROMPT)

        assert "claude-haiku-4.5" in command
        # The prompt travels on stdin now; see TestThePromptDoesNotTravelInArgv.
        assert PROMPT not in command


class TestAvailabilityProbing:
    """B110 - availability is an account property, so ask before committing."""

    def test_probes_every_model(self):
        runner = _script(["gpt-5.4", "claude-haiku-4.5"])

        report = probe_models(["gpt-5.4", "claude-haiku-4.5"], runner, WORKDIR)

        assert [entry.model for entry in report] == ["gpt-5.4", "claude-haiku-4.5"]
        assert all(entry.available for entry in report)

    def test_a_rejected_model_is_reported_unavailable_with_its_reason(self):
        model = "gemini-2.5-pro"
        probe = probe_command_for(model)
        runner = FakeRunner({
            probe: command_result(
                probe, WORKDIR, CommandOutcome.COMPLETED, 1, "",
                'Model "gemini-2.5-pro" from --model flag is not available.',
            )
        })

        entry = probe_models([model], runner, WORKDIR)[0]

        assert entry.available is False
        assert "not available" in entry.detail

    def test_no_review_call_happens_before_every_probe_has_run(self):
        # The point of B110 is ordering: discovering an unavailable model
        # after the other has already run for a minute wastes the minute.
        models = ["gpt-5.4", "claude-haiku-4.5"]
        runner = _script(models)

        invoke_models(models, PROMPT, runner, WORKDIR, runs=1)

        probes = {probe_command_for(model) for model in models}
        commands = issued(runner)
        last_probe = max(i for i, c in enumerate(commands) if c in probes)
        first_review = min(i for i, c in enumerate(commands) if c not in probes)

        assert last_probe < first_review

    def test_an_unavailable_model_is_never_asked_to_review(self):
        good, bad = "gpt-5.4", "gemini-2.5-pro"
        runner = _script([good])  # `bad` is unscripted -> TOOL_MISSING -> unavailable

        report = invoke_models([good, bad], PROMPT, runner, WORKDIR, runs=1)

        assert review_command(bad, PROMPT) not in issued(runner)
        assert report.is_partial is True

    def test_probing_no_models_returns_nothing_rather_than_failing(self):
        # `probe_models` is public and has no validation of its own; the
        # emptiness guard in the concurrency helper is what makes this safe.
        assert probe_models([], FakeRunner({}), WORKDIR) == ()

    def test_when_no_model_is_available_the_review_fails_loudly(self):
        # B130: an empty report is indistinguishable from a clean review.
        runner = FakeRunner({})  # every probe returns TOOL_MISSING

        with pytest.raises(NoModelAvailable) as error:
            invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR)

        assert "gpt-5.4" in str(error.value)


class TestRepetition:
    """B132, B133 - repetition is what turns an invisible omission visible."""

    def test_calls_each_model_three_times_by_default(self):
        assert DEFAULT_RUNS == 3

        runner = _script(["gpt-5.4"])
        report = invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR)

        reviews = reviews_only(runner, "gpt-5.4")
        assert len(reviews) == 3
        assert report.requested_for("gpt-5.4") == 3

    def test_run_count_is_overridable(self):
        runner = _script(["gpt-5.4"])

        invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR, runs=5)

        assert len(reviews_only(runner, "gpt-5.4")) == 5

    def test_runs_of_one_model_are_byte_identical_calls(self):
        # B133: the variation being measured belongs to the model. Perturbing
        # the prompt between runs would measure something else entirely.
        runner = _script(["gpt-5.4"])

        invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR, runs=3)

        assert len(set(reviews_only(runner, "gpt-5.4"))) == 1

    def test_every_model_gets_the_same_number_of_runs(self):
        models = ["gpt-5.4", "claude-haiku-4.5"]
        runner = _script(models)

        report = invoke_models(models, PROMPT, runner, WORKDIR, runs=2)

        assert report.requested_for("gpt-5.4") == 2
        assert report.requested_for("claude-haiku-4.5") == 2
        assert len(report.runs) == 4

    def test_runs_are_numbered_from_one(self):
        runner = _script(["gpt-5.4"])

        report = invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR, runs=3)

        assert sorted(r.run_index for r in report.runs) == [1, 2, 3]


class TestPerRunOutcomes:
    """B112, B129, B134 - a failure is data, not an exception."""

    def test_a_timeout_is_a_recorded_outcome_not_a_raise(self):
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = FakeRunner({
            probe: command_result(probe, WORKDIR),
            review: command_result(review, WORKDIR, CommandOutcome.TIMED_OUT, None, "", "timed out"),
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=1)

        assert report.runs[0].outcome is RunOutcome.TIMED_OUT
        assert report.completed_for(model) == 0

    def test_a_nonzero_exit_is_recorded_as_a_failed_run(self):
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = FakeRunner({
            probe: command_result(probe, WORKDIR),
            review: command_result(review, WORKDIR, CommandOutcome.COMPLETED, 1, "", "boom"),
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=1)

        assert report.runs[0].outcome is RunOutcome.FAILED
        assert "boom" in report.runs[0].detail

    def test_one_failing_run_does_not_stop_the_others(self):
        # B129: a failed call does not abort the review.
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = SequencedRunner({
            probe: [command_result(probe, WORKDIR)],
            review: [
                command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, "first", ""),
                command_result(review, WORKDIR, CommandOutcome.TIMED_OUT, None, "", "slow"),
                command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, "third", ""),
            ],
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=3)

        assert len(report.runs) == 3
        assert report.completed_for(model) == 2
        assert {r.outcome for r in report.runs} == {RunOutcome.COMPLETED, RunOutcome.TIMED_OUT}

    def test_response_text_is_kept_for_completed_runs(self):
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = FakeRunner({
            probe: command_result(probe, WORKDIR),
            review: command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, '[{"a": 1}]', ""),
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=1)

        assert report.runs[0].response_text == '[{"a": 1}]'


class TestPartialReviews:
    """B137 - a single missing run degrades the phase's headline number."""

    def test_a_complete_review_is_not_partial(self):
        runner = _script(["gpt-5.4", "claude-haiku-4.5"])

        report = invoke_models(
            ["gpt-5.4", "claude-haiku-4.5"], PROMPT, runner, WORKDIR, runs=1
        )

        assert report.is_partial is False

    def test_one_failed_run_out_of_six_makes_the_whole_review_partial(self):
        # Deliberately strict, per A5. Pinned so that relaxing it is a
        # visible decision rather than a drift.
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = SequencedRunner({
            probe: [command_result(probe, WORKDIR)],
            review: [
                command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, "ok", ""),
                command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, "ok", ""),
                command_result(review, WORKDIR, CommandOutcome.TIMED_OUT, None, "", "slow"),
            ],
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=3)

        assert report.completed_for(model) == 2
        assert report.is_partial is True

    def test_participation_states_completed_over_requested_per_model(self):
        # B134: a review that quietly shrinks the denominator presents a
        # degraded signal as an intact one.
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = SequencedRunner({
            probe: [command_result(probe, WORKDIR)],
            review: [
                command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, "ok", ""),
                command_result(review, WORKDIR, CommandOutcome.TIMED_OUT, None, "", "slow"),
                command_result(review, WORKDIR, CommandOutcome.COMPLETED, 0, "ok", ""),
            ],
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=3)

        assert report.describe_participation() == "gpt-5.4: 2/3 runs completed"

    def test_usable_responses_are_offered_even_when_the_review_is_partial(self):
        models = ["gpt-5.4", "gemini-2.5-pro"]
        runner = _script(["gpt-5.4"], stdout="usable")

        report = invoke_models(models, PROMPT, runner, WORKDIR, runs=1)

        assert report.is_partial is True
        assert [r.response_text for r in report.usable_runs] == ["usable"]


class TestConcurrency:
    """B111 - four is the measured figure, not a tidy one."""

    def test_default_concurrency_is_the_measured_four(self):
        # A4: not raised to 6 so that 2 models x 3 runs finish in one wave.
        # Six is unmeasured; picking it for arithmetic is the move this
        # phase exists to refuse.
        assert DEFAULT_CONCURRENCY == 4

    def test_never_exceeds_the_concurrency_limit(self):
        peak = 0
        live = 0
        lock = threading.Lock()

        class CountingRunner:
            def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
                nonlocal peak, live
                command_tuple = tuple(command)
                with lock:
                    live += 1
                    peak = max(peak, live)
                try:
                    return command_result(command_tuple, working_directory,
                                          CommandOutcome.COMPLETED, 0, "ok", "")
                finally:
                    with lock:
                        live -= 1

        invoke_models(["gpt-5.4", "claude-haiku-4.5"], PROMPT, CountingRunner(),
                      WORKDIR, runs=3, concurrency=2)

        assert peak <= 2

    def test_calls_genuinely_overlap_rather_than_merely_staying_under_the_limit(self):
        # The assertion above passes even if invocation is entirely serial,
        # so on its own it proves nothing. B111 exists to make reviews fast:
        # a silently sequential implementation would satisfy every other test
        # here while taking six times as long as designed.
        #
        # This runner refuses to return until a second call joins it, so the
        # test can only pass if two calls are genuinely in flight at once.
        rendezvous = threading.Barrier(2, timeout=5)
        peak = 0
        live = 0
        lock = threading.Lock()

        class RendezvousRunner:
            def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
                nonlocal peak, live
                command_tuple = tuple(command)
                if stdin_text == PROMPT:  # probes must not deadlock here
                    with lock:
                        live += 1
                        peak = max(peak, live)
                    try:
                        rendezvous.wait()
                    finally:
                        with lock:
                            live -= 1
                return command_result(command_tuple, working_directory,
                                      CommandOutcome.COMPLETED, 0, "ok", "")

        report = invoke_models(["gpt-5.4"], PROMPT, RendezvousRunner(),
                               WORKDIR, runs=2, concurrency=2)

        assert len(report.runs) == 2
        assert peak == 2

    def test_all_runs_complete_even_when_they_outnumber_the_workers(self):
        runner = _script(["gpt-5.4", "claude-haiku-4.5"], stdout="ok")

        report = invoke_models(["gpt-5.4", "claude-haiku-4.5"], PROMPT, runner,
                               WORKDIR, runs=3, concurrency=2)

        assert len(report.runs) == 6
        assert all(r.outcome is RunOutcome.COMPLETED for r in report.runs)


class TestReportingWhatFailed:
    """The report has to be able to say *why*, not just that something broke."""

    def test_unavailable_models_are_listed_with_their_reasons(self):
        good, bad = "gpt-5.4", "gemini-2.5-pro"
        runner = _script([good])  # `bad` is unscripted

        report = invoke_models([good, bad], PROMPT, runner, WORKDIR, runs=1)
        unavailable = report.unavailable_models()

        assert [entry.model for entry in unavailable] == [bad]
        assert unavailable[0].detail != ""

    def test_a_missing_cli_is_reported_as_tool_missing_not_as_a_refusal(self):
        # Distinguishing these matters to whoever reads the report: one means
        # "install the CLI", the other means "the model said no".
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = FakeRunner({
            probe: command_result(probe, WORKDIR),
            review: command_result(review, WORKDIR, CommandOutcome.TOOL_MISSING,
                                   None, "", "Executable not found on PATH: copilot"),
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=1)

        assert report.runs[0].outcome is RunOutcome.TOOL_MISSING
        assert "not found" in report.runs[0].detail

    def test_a_silent_failure_still_gets_a_reason(self):
        # A model that fails with no output at all would otherwise produce a
        # blank explanation in the report.
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = FakeRunner({
            probe: command_result(probe, WORKDIR),
            review: command_result(review, WORKDIR, CommandOutcome.COMPLETED, 7, "", ""),
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=1)

        assert report.runs[0].detail == "exited with code 7"

    def test_a_silent_timeout_is_named_by_its_outcome(self):
        model = "gpt-5.4"
        probe, review = probe_command_for(model), review_command(model, PROMPT)
        runner = FakeRunner({
            probe: command_result(probe, WORKDIR),
            review: command_result(review, WORKDIR, CommandOutcome.TIMED_OUT, None, "", ""),
        })

        report = invoke_models([model], PROMPT, runner, WORKDIR, runs=1)

        assert report.runs[0].detail == "timed_out"


class TestNonsensicalSettings:
    """A review that asks nobody anything must not look like a clean review."""

    def test_zero_runs_is_rejected_rather_than_reported_as_complete(self):
        # Without this guard `--runs 0` makes no calls at all, reports
        # is_partial=False and prints "0/0 runs completed" - a report
        # indistinguishable from "no problems found", which is precisely the
        # confusion B130 exists to prevent, arriving through a different door.
        runner = _script(["gpt-5.4"])

        with pytest.raises(ValueError, match="runs"):
            invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR, runs=0)

    def test_negative_runs_is_rejected(self):
        runner = _script(["gpt-5.4"])

        with pytest.raises(ValueError, match="runs"):
            invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR, runs=-1)

    def test_zero_concurrency_is_rejected_rather_than_silently_corrected(self):
        runner = _script(["gpt-5.4"])

        with pytest.raises(ValueError, match="concurrency"):
            invoke_models(["gpt-5.4"], PROMPT, runner, WORKDIR, concurrency=0)

    def test_no_models_at_all_is_rejected(self):
        runner = _script([])

        with pytest.raises(ValueError, match="model"):
            invoke_models([], PROMPT, runner, WORKDIR)


class TestThePromptDoesNotTravelInArgv:
    """A diff on the command line breaks silently once it grows.

    Measured on Windows with the npm-installed CLI: a prompt near 8,000
    characters fails with "The syntax of the command is incorrect", near 30,000
    with "The command line is too long", and past roughly 60,000 CreateProcess
    itself refuses to start. The first two arrive as COMPLETED with a non-zero
    exit, so they are indistinguishable from a model that answered badly.
    """

    def test_review_command_does_not_contain_the_prompt(self):
        """The prompt is delivered on stdin, so argv must not carry it."""
        prompt = "REVIEW-THIS-DIFF-MARKER"

        command = review_command("gpt-5.4", prompt)

        assert prompt not in command
        assert "-p" not in command

    def test_command_length_stays_flat_as_the_prompt_grows(self):
        """Argv size must not depend on diff size, which is the whole defect."""
        small = review_command("gpt-5.4", "x" * 100)
        enormous = review_command("gpt-5.4", "x" * 500_000)

        assert small == enormous

    def test_the_prompt_reaches_the_runner_as_stdin(self, tmp_path):
        """B106: the review still has to receive the diff -- just not via argv."""
        recorder = _StdinRecordingRunner()

        invoke_models(
            models=["gpt-5.4"],
            prompt="the diff text",
            runner=recorder,
            working_directory=tmp_path,
            runs=1,
        )

        assert recorder.stdin_texts == ["the diff text"]


class _StdinRecordingRunner:
    """Records what each call would have written to the child's stdin."""

    def __init__(self):
        self.stdin_texts = []

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        if "--version" in command or "ping" in command:
            return CommandResult(tuple(command), working_directory, CommandOutcome.COMPLETED, 0, "ok", "", 0.01)
        self.stdin_texts.append(stdin_text)
        return CommandResult(tuple(command), working_directory, CommandOutcome.COMPLETED, 0, "[]", "", 0.01)


