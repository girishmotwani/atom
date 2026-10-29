"""Call review models and record what each run actually did.

This module owns the *invocation* half of `atom review`: deciding which models
can be called, calling them, and turning every possible ending — success,
refusal, timeout, missing tool — into data the report can show.

Two ideas shape the design, and both come from the Phase 4 spike rather than
from taste:

1.  **A single call to a model is a lottery.** The spike measured one model's
    best finding appearing in 13 of 20 runs, so asking once omits real defects
    about a third of the time *and cannot say so*. Hence B132: call each model
    several times and report the fraction that agreed.

2.  **A failed call is an observation, not an emergency.** Nothing here raises
    because a model misbehaved. The single exception is "no model could be
    called at all" (B130), because an empty report reads exactly like a clean
    review, and that confusion is the dangerous one.

See `specs/atom-cli/phase-04-review/design-spec.md` for B107-B112 and
B129-B134, and `poc-report.md` for the measurements behind them.
"""

from __future__ import annotations

import enum
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from atom.runner import CommandOutcome, CommandResult, CommandRunner

# Calling each model three times is the smallest count that can distinguish
# "every run agreed" from "the model is guessing" (B132, P4-2).
DEFAULT_RUNS = 3

# Four concurrent calls is the figure the spike actually measured (C6). It is
# deliberately *not* raised to six so that two models x three runs finish in a
# single wave: six is unmeasured, and choosing a number because the arithmetic
# is tidy is precisely the habit this phase exists to refuse (A4).
DEFAULT_CONCURRENCY = 4

# Review calls were measured at 30-85 seconds when B112 was written, and that
# range no longer holds: gemini-3.8-flash, now a default model, ran 47-194
# seconds across ten calls. A 300-second limit left only 1.5x headroom over an
# already-observed value, and a timeout that fires on a healthy model is not a
# harmless one -- it is reported as "the model did not answer", which is the
# exact conflation that made a correct model look like a failing one during the
# A26 measurement (finding 31). 600 seconds keeps roughly 3x headroom.
#
# Raising it is only safe because the limit is now genuinely bounded. Before
# the phase-01 fix this value was advisory: a call could exceed it by hours,
# so a larger number would have meant a larger lie rather than a longer wait.
DEFAULT_TIMEOUT_SECONDS = 600.0

# An unavailable model is rejected in about two seconds, so the probe does not
# need the review timeout.
DEFAULT_PROBE_TIMEOUT_SECONDS = 60.0

# The cheapest prompt that still exercises model selection end to end.
_PROBE_PROMPT = "ping"

_CLI = "copilot"


class RunOutcome(enum.Enum):
    """Distinguishes the ways a single model call can end.

    `FAILED` and `TIMED_OUT` are kept apart because they mean different things
    to a developer reading the report: one is the model refusing, the other is
    the model never answering.
    """

    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    TOOL_MISSING = "tool_missing"


@dataclass(frozen=True)
class ModelAvailability:
    """Records whether one model can be called, and why not when it cannot."""

    model: str
    available: bool
    detail: str = ""


@dataclass(frozen=True)
class ModelRun:
    """One call to one model, including the calls that did not work.

    `run_index` is 1-based because it appears in human-readable output, where
    "run 0 of 3" reads as a mistake.
    `response_text` keeps raw stdout; `response_format` selects its decoder
    without making a completed process imply a readable review.
    Native failures retain raw stdout/stderr for private diagnosis, separately
    from safe operational detail.
    """

    model: str
    run_index: int
    outcome: RunOutcome
    response_text: str
    duration_seconds: float
    detail: str = ""
    response_format: Literal["text", "copilot_jsonl"] = "text"
    fixed_evidence: bool = False
    stderr_text: str = ""

    @property
    def is_usable(self) -> bool:
        """Return true when this run produced text worth trying to parse."""

        return self.outcome is RunOutcome.COMPLETED and bool(self.response_text.strip())


class NoModelAvailable(Exception):
    """Raised when not one model could be called, so there is nothing to report.

    This is the only failure in this module that stops the review, because an
    empty report is indistinguishable from a review that found no problems
    (B130).
    """


@dataclass(frozen=True)
class InvocationReport:
    """Everything that happened during invocation, including what did not happen.

    The report deliberately keeps *requested* runs alongside *completed* ones.
    A review that quietly shrinks its own denominator turns a degraded
    confidence signal into an intact-looking one (B134).
    """

    models: tuple[str, ...]
    runs_requested: int
    runs: tuple[ModelRun, ...]
    availability: tuple[ModelAvailability, ...]

    def requested_for(self, model: str) -> int:
        """Return how many runs of this model were asked for."""

        return self.runs_requested if model in self.models else 0

    def completed_for(self, model: str) -> int:
        """Return how many runs of this model produced a response."""

        return sum(1 for run in self.runs if run.model == model and run.outcome is RunOutcome.COMPLETED)

    @property
    def usable_runs(self) -> tuple[ModelRun, ...]:
        """Return only the runs whose text is worth handing to extraction."""

        return tuple(run for run in self.runs if run.is_usable)

    @property
    def is_partial(self) -> bool:
        """Return true when any requested run did not complete.

        Per A5/B137 this is strict on purpose: one missing run out of six is
        enough. The strictness is the point — a CI job where a model fails on
        every single run would otherwise stay green forever while nobody reads
        the banner. It is also the behaviour most likely to prove annoying, so
        it is pinned by a test rather than left to drift.
        """

        return any(
            self.completed_for(model) != self.runs_requested for model in self.models
        )

    def describe_participation(self) -> str:
        """Summarise completed-over-requested runs for every model asked for."""

        return "; ".join(
            f"{model}: {self.completed_for(model)}/{self.runs_requested} runs completed"
            for model in self.models
        )

    def unavailable_models(self) -> tuple[ModelAvailability, ...]:
        """Return the models that could not be called at all."""

        return tuple(entry for entry in self.availability if not entry.available)


def probe_command(
    model: str, disable_mcp_servers: Sequence[str] = (),
    *, fixed_evidence: bool = False,
) -> tuple[str, ...]:
    """Check availability with the same caller-selected isolation as reviews.

    Availability is an account property, not a fact about the CLI version: the
    spike found two models rejected on the same machine where two others were
    accepted (C7).
    """

    command = [
        _CLI,
        "-p",
        _PROBE_PROMPT,
        "--silent",
        "--model",
        model,
        "--no-custom-instructions",
        "--disable-builtin-mcps",
    ]
    for server in disable_mcp_servers:
        command.extend(("--disable-mcp-server", server))
    if fixed_evidence:
        command.extend(("--excluded-tools", "builtin:*", "custom:*", "mcp:*"))
    return tuple(command)


def review_command(
    model: str,
    prompt: str,
    disable_mcp_servers: Sequence[str] = (),
    *, fixed_evidence: bool = False,
) -> tuple[str, ...]:
    """Build one review call, with the flags that every measurement demanded.

    Each flag earns its place:

    * `--output-format json`. Silent text can concatenate delegated replies
      with the parent's findings. JSONL carries ownership so extraction can
      isolate the answer without guessing where JSON starts.
    * `--no-custom-instructions` (B108). Without it the CLI loads `AGENTS.md`
      from the working directory, and the review quietly becomes a property of
      the repository being reviewed rather than of Atom.
    * `--disable-builtin-mcps` (B109). Measured at 84 seconds down to roughly
      30. A review whose entire input is in the prompt has no use for them.

    `disable_mcp_servers` is a parameter rather than a hard-coded list on
    purpose. The spike ran inside one company's environment and disabled two
    named servers there; shipping those names would bake one organisation's
    setup into an open-source tool. Callers who have ambient servers of their
    own can name them.

    The prompt is deliberately absent. `-p <text>` puts the entire diff into
    argv, which on Windows silently corrupts the call as the diff grows: near
    8,000 characters the shim reports a syntax error and near 30,000 the command
    line is rejected outright, both surfacing as an ordinary non-zero exit that
    is indistinguishable from a model failing to answer. The CLI reads a piped
    prompt from stdin, which has no such ceiling, so `prompt` is accepted here
    only to keep one obvious place to document why it is not used.
    """

    _ = prompt

    command = [
        _CLI,
        "--output-format",
        "json",
        "--model",
        model,
        "--no-custom-instructions",
        "--disable-builtin-mcps",
    ]
    for server in disable_mcp_servers:
        command.extend(("--disable-mcp-server", server))
    if fixed_evidence:
        command.extend(("--excluded-tools", "builtin:*", "custom:*", "mcp:*"))

    return tuple(command)


def probe_models(
    models: Sequence[str],
    runner: CommandRunner,
    working_directory: Path,
    timeout_seconds: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
    concurrency: int = DEFAULT_CONCURRENCY,
    disable_mcp_servers: Sequence[str] = (),
    *, fixed_evidence: bool = False,
) -> tuple[ModelAvailability, ...]:
    """Check models with the caller's exclusions before review can spend runs.

    Probing first is worth the couple of seconds it costs: the alternative is
    discovering an unusable model after the other one has already spent a
    minute reviewing.
    """

    def probe(model: str) -> ModelAvailability:
        result = runner.run(
            probe_command(model, disable_mcp_servers, fixed_evidence=fixed_evidence),
            working_directory, timeout_seconds,
        )
        if result.succeeded:
            return ModelAvailability(model=model, available=True)
        return ModelAvailability(
            model=model,
            available=False,
            detail=_explain(result, include_output=not fixed_evidence),
        )

    return tuple(_map_bounded(probe, list(models), concurrency))


def invoke_models(
    models: Sequence[str],
    prompt: str,
    runner: CommandRunner,
    working_directory: Path,
    runs: int = DEFAULT_RUNS,
    concurrency: int = DEFAULT_CONCURRENCY,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    disable_mcp_servers: Sequence[str] = (),
    *, fixed_evidence: bool = False,
) -> InvocationReport:
    """Run every available model `runs` times and record each attempt.

    Returns rather than raises for every per-run failure (B129). The one
    exception is when no model is available at all, which raises
    `NoModelAvailable` because there is then nothing to report and silence
    would read as a clean review (B130).
    """

    requested = tuple(models)
    _reject_nonsensical_settings(requested, runs, concurrency)
    availability = probe_models(
        requested, runner, working_directory, concurrency=concurrency,
        disable_mcp_servers=disable_mcp_servers,
        fixed_evidence=fixed_evidence,
    )
    usable_models = [entry.model for entry in availability if entry.available]

    if not usable_models:
        raise NoModelAvailable(
            "No review model could be called: "
            + "; ".join(
                f"{entry.model} ({entry.detail or 'unavailable'})"
                for entry in availability
            )
        )

    # Runs of the same model are identical calls (B133): the variation being
    # measured belongs to the model, so introducing any of our own would
    # measure something else and make the agreement counts meaningless.
    command_for = {
        model: review_command(
            model, prompt, disable_mcp_servers, fixed_evidence=fixed_evidence,
        )
        for model in usable_models
    }
    planned = [
        (model, run_index)
        for model in usable_models
        for run_index in range(1, runs + 1)
    ]

    def execute(plan: tuple[str, int]) -> ModelRun:
        model, run_index = plan
        result = runner.run(
            command_for[model], working_directory, timeout_seconds, stdin_text=prompt
        )
        return _to_run(
            model, run_index, result, response_format="copilot_jsonl",
            fixed_evidence=fixed_evidence,
        )

    completed = _map_bounded(execute, planned, concurrency)

    # Sort so the report is deterministic regardless of completion order.
    order = {model: position for position, model in enumerate(requested)}
    completed.sort(key=lambda run: (order.get(run.model, len(order)), run.run_index))

    return InvocationReport(
        models=requested,
        runs_requested=runs,
        runs=tuple(completed),
        availability=availability,
    )


def _reject_nonsensical_settings(
    models: tuple[str, ...], runs: int, concurrency: int
) -> None:
    """Refuse settings that would produce a review nobody was asked for.

    `--runs 0` is the interesting one. Left unguarded it makes no calls at all
    and then reports "0/0 runs completed" with `is_partial` false — a report
    that reads exactly like "no problems found" despite no model having been
    consulted. That is the same confusion B130 exists to prevent, arriving
    through a different door, so it is refused rather than corrected: silently
    clamping to 1 would hide the developer's mistake instead of showing it.
    """

    if not models:
        raise ValueError("At least one review model must be given.")
    if runs < 1:
        raise ValueError(f"runs must be at least 1, got {runs}.")
    if concurrency < 1:
        raise ValueError(f"concurrency must be at least 1, got {concurrency}.")


def _to_run(
    model: str,
    run_index: int,
    result: CommandResult,
    *,
    response_format: Literal["text", "copilot_jsonl"] = "text",
    fixed_evidence: bool = False,
) -> ModelRun:
    """Translate a command result into a run outcome without losing the reason."""

    if result.outcome is CommandOutcome.TIMED_OUT:
        outcome = RunOutcome.TIMED_OUT
    elif result.outcome is CommandOutcome.TOOL_MISSING:
        outcome = RunOutcome.TOOL_MISSING
    elif result.succeeded:
        outcome = RunOutcome.COMPLETED
    else:
        outcome = RunOutcome.FAILED

    structured = response_format == "copilot_jsonl"
    return ModelRun(
        model=model,
        run_index=run_index,
        outcome=outcome,
        response_text=result.stdout if structured or outcome is RunOutcome.COMPLETED else "",
        duration_seconds=result.duration_seconds,
        detail="" if outcome is RunOutcome.COMPLETED else _explain(
            result, include_output=not (structured or fixed_evidence),
        ),
        response_format=response_format,
        fixed_evidence=fixed_evidence,
        stderr_text=result.stderr,
    )


def _explain(result: CommandResult, *, include_output: bool = True) -> str:
    """Keep process diagnostics separate from potentially private CLI streams."""

    if not include_output:
        # Structured stdout/stderr can contain source and account-bearing events.
        if result.outcome is CommandOutcome.TIMED_OUT:
            return f"timed out (observed elapsed {result.duration_seconds:.3f} seconds)"
        if result.outcome is CommandOutcome.TOOL_MISSING:
            return "CLI not found"
        if result.outcome is CommandOutcome.RUNNER_ERROR:
            return "runner error; cleanup status not independently established"
        if result.exit_code is not None:
            return f"exited with code {result.exit_code}"
        return result.outcome.value
    message = result.combined_output.strip()
    if message:
        return message
    if result.exit_code is not None:
        return f"exited with code {result.exit_code}"
    return result.outcome.value


def _map_bounded(function, items: list, concurrency: int) -> list:
    """Apply `function` across `items` with at most `concurrency` in flight.

    Kept as a helper so the concurrency limit is enforced in exactly one place;
    B111's limit is a measured figure and should not be re-implemented per call
    site where it could drift.
    """

    if not items:
        return []

    # `max(1, ...)` matters when `items` is shorter than the limit; the
    # executor rejects a worker count of zero.
    workers = max(1, min(concurrency, len(items)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(function, items))
