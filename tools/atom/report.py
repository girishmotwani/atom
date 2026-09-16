"""Render a CheckReport or SpikeResult as human-readable text or machine-readable JSON."""

from __future__ import annotations

import json

from atom.check import CheckReport
from atom.gates import GateStatus
from atom.index import SpikeSummary
from atom.spike import SpikeKind, SpikeResult, Stage, Verdict

# Bump when the JSON shape changes incompatibly, so consumers can branch on it
# instead of guessing from the presence of fields.
SCHEMA_VERSION = 1

_RESET = "\x1b[0m"
_GREEN = "\x1b[32m"
_RED = "\x1b[31m"
_GREY = "\x1b[90m"
_YELLOW = "\x1b[33m"

_COLOURS = {
    GateStatus.PASSED: _GREEN,
    GateStatus.FAILED: _RED,
    GateStatus.SKIPPED: _GREY,
    GateStatus.WARNING: _YELLOW,
}
_SYMBOLS = {
    GateStatus.PASSED: "PASS",
    GateStatus.FAILED: "FAIL",
    GateStatus.SKIPPED: "SKIP",
    GateStatus.WARNING: "WARN",
}

# A verdict is not a pass/fail, so it is not coloured like one. Refuted is a
# perfectly good outcome -- painting it red would teach the developer to read a
# successful spike as a failure, which is the habit this whole phase fights.
_VERDICT_COLOURS = {
    Verdict.CONFIRMED: _GREEN,
    Verdict.REFUTED: _YELLOW,
    Verdict.INCONCLUSIVE: _YELLOW,
    Verdict.CRASHED: _RED,
    Verdict.UNKNOWN: _GREY,
}
_VERDICT_MEANINGS = {
    Verdict.CONFIRMED: "the question was answered yes",
    Verdict.REFUTED: "the question was answered no -- this is a result, not a failure",
    Verdict.INCONCLUSIVE: "the spike did not settle it",
    Verdict.CRASHED: "the spike crashed -- it did not answer anything",
    Verdict.UNKNOWN: "the spike used an exit code Atom does not recognise",
}


def render_text(report: CheckReport, use_colour: bool = True) -> str:
    """Render a report for a human reading a terminal.

    Passing gates show one line. Failing gates additionally show their verbatim
    output, because that is the only part a developer needs to act on.
    """

    lines = [f"atom check {report.directory}", ""]

    for result in report.gate_results:
        label = _paint(_SYMBOLS[result.status], result.status, use_colour)
        lines.append(f"  {label}  {result.name:<6} {result.summary} ({result.duration_seconds:.1f}s)")

        if result.status is GateStatus.FAILED and result.details.strip():
            lines.append("")
            lines.extend(f"        {detail_line}" for detail_line in result.details.splitlines())
            lines.append("")

    if report.warnings:
        lines.append("")
        lines.append("  Warnings:")
        lines.extend(f"    - {warning}" for warning in report.warnings)

    verdict_status = GateStatus.PASSED if report.passed else GateStatus.FAILED
    verdict_text = "PASSED" if report.passed else "FAILED"
    lines.append("")
    lines.append(f"  {_paint(verdict_text, verdict_status, use_colour)} in {report.total_duration_seconds:.1f}s")

    return "\n".join(lines)


def render_json(report: CheckReport) -> str:
    """Render a report as stable, versioned JSON for programmatic consumers."""

    payload = {
        "schema_version": SCHEMA_VERSION,
        "directory": str(report.directory),
        "passed": report.passed,
        "exit_code": report.exit_code,
        "total_duration_seconds": round(report.total_duration_seconds, 3),
        "warnings": list(report.warnings),
        "gates": [
            {
                "name": result.name,
                "status": result.status.value,
                "summary": result.summary,
                "details": result.details,
                "required": result.required,
                "duration_seconds": round(result.duration_seconds, 3),
            }
            for result in report.gate_results
        ],
    }

    return json.dumps(payload, indent=2)


def _paint(text: str, status: GateStatus, use_colour: bool) -> str:
    if not use_colour:
        return text

    return f"{_COLOURS[status]}{text}{_RESET}"


# --------------------------------------------------------------------------
# Spike rendering
# --------------------------------------------------------------------------


def render_spike_text(result: SpikeResult, use_colour: bool = True) -> str:
    """Render a spike run for a human, with stderr first on failure.

    stderr comes first deliberately. The POC showed that when a spike fails,
    stdout is typically empty and stderr holds the entire explanation. Putting
    stdout first would bury the one thing worth reading.
    """

    kind_label = "command" if result.kind is SpikeKind.COMMAND else "library"
    lines = [f"atom poc run {result.slug}  ({kind_label} spike)", ""]

    crashed = result.verdict is Verdict.CRASHED
    for stage_result in result.stages:
        status = _status_for_stage(stage_result, crashed)
        label = _paint(_SYMBOLS[status], status, use_colour)
        lines.append(f"  {label}  {stage_result.stage.value:<8}{_stage_summary(stage_result, crashed)}")

    # Show the output of whichever stage the developer needs to read. For a
    # failure that is the failing stage. For a spike that answered there is no
    # failing stage -- but its output is the evidence behind the verdict, which
    # is the single most useful thing on screen, so it is shown too.
    stage_worth_reading = result.failed_stage
    if stage_worth_reading is None and result.answered:
        stage_worth_reading = Stage.EXECUTE

    if stage_worth_reading is not None:
        stage_result = next(stage for stage in result.stages if stage.stage is stage_worth_reading)
        for stream_name, stream in (("stderr", stage_result.stderr), ("stdout", stage_result.stdout)):
            if stream.strip():
                lines.append("")
                lines.append(f"  {stream_name}:")
                lines.extend(f"    {line}" for line in stream.rstrip().splitlines())

    lines.append("")
    lines.extend(_render_verdict_lines(result, use_colour))

    return "\n".join(lines)


def _render_verdict_lines(result: SpikeResult, use_colour: bool) -> list[str]:
    """Explain the outcome in words, because an exit code is not self-describing."""

    if not result.ran:
        return [
            "  No verdict -- the spike never ran, so it has not answered anything.",
            "  Fix the failure above and run it again.",
        ]

    assert result.verdict is not None  # guaranteed by result.ran
    colour = _VERDICT_COLOURS[result.verdict]
    label = result.verdict.value.upper()
    painted = f"{colour}{label}{_RESET}" if use_colour else label

    lines = [
        f"  Verdict: {painted}  (exit {result.spike_exit_code}) -- {_VERDICT_MEANINGS[result.verdict]}",
    ]

    if result.verdict is Verdict.UNKNOWN:
        lines.append("  Atom does not guess. Use 0, 1 or 2 to state a verdict.")

    # B68: exit 2 normally means Inconclusive, so a developer seeing CRASHED
    # from a 2 deserves to know why Atom read it differently this time.
    if result.verdict is Verdict.CRASHED:
        lines.append("  Exit 2 usually means Inconclusive, but the spike printed a Go panic,")
        lines.append("  so it stopped rather than concluded. Fix the panic and run it again.")

    # B57: a limitation created by the decision to run `go test` for library
    # spikes. Saying so here is what stops a developer concluding CONFIRMED
    # when what they meant was "I could not tell".
    if result.kind is SpikeKind.LIBRARY:
        lines.append("  Note: `go test` exits 0 or 1 only, so a library spike cannot report Inconclusive.")

    return lines


def _status_for_stage(stage_result, crashed: bool = False) -> GateStatus:
    """Classify a stage for display.

    An EXECUTE stage that produced an answer is PASSED: its job was to run the
    spike and it did. The answer itself lives on the verdict line, not here.
    A crash is the exception -- there the stage really did fail.
    """

    if stage_result.skipped:
        return GateStatus.SKIPPED
    if stage_result.produced_an_answer and not crashed:
        return GateStatus.PASSED
    if stage_result.timed_out or not stage_result.succeeded:
        return GateStatus.FAILED
    return GateStatus.PASSED


def _stage_summary(stage_result, crashed: bool = False) -> str:
    """Describe a stage in words that match how it is classified.

    "exited 2" invites the reading that something went wrong. "answered with
    exit 2" says what actually happened: the spike reached a conclusion.
    """

    if stage_result.skipped:
        return "skipped -- an earlier stage failed"
    if stage_result.timed_out:
        return "timed out and was killed"
    if stage_result.produced_an_answer and crashed:
        return f"crashed (exit {stage_result.exit_code})"
    if stage_result.produced_an_answer and stage_result.exit_code != 0:
        return f"answered with exit {stage_result.exit_code}"
    if stage_result.succeeded:
        return "ok"
    return f"exited {stage_result.exit_code}"


def render_spike_json(result: SpikeResult) -> str:
    """Render a spike run as stable, versioned JSON."""

    payload = {
        "schema_version": SCHEMA_VERSION,
        "slug": result.slug,
        "kind": result.kind.value,
        "ran": result.ran,
        "answered": result.answered,
        "compiled": result.compiled,
        "verdict": result.verdict.value if result.verdict is not None else None,
        "spike_exit_code": result.spike_exit_code,
        "failed_stage": result.failed_stage.value if result.failed_stage is not None else None,
        "stages": [
            {
                "stage": stage.stage.value,
                "exit_code": stage.exit_code,
                "stdout": stage.stdout,
                "stderr": stage.stderr,
                "skipped": stage.skipped,
                "timed_out": stage.timed_out,
            }
            for stage in result.stages
        ],
    }

    return json.dumps(payload, indent=2)


def render_spike_list_text(summaries: list[SpikeSummary], use_colour: bool = True) -> str:
    """Render the spike index, flagging any spike that would break the parent build."""

    if not summaries:
        return "No spikes yet.\n\nStart one with:\n  atom poc new <slug> --question \"...\""

    lines = [f"{len(summaries)} spike{'s' if len(summaries) != 1 else ''}", ""]
    widest_slug = max(len(summary.slug) for summary in summaries)

    for summary in summaries:
        question = summary.question or "(no question recorded)"
        lines.append(f"  {summary.slug:<{widest_slug}}  {question}")

        if not summary.has_go_mod:
            warning = "no go.mod -- this spike breaks the parent build; `atom check` will fail"
            painted = f"{_RED}{warning}{_RESET}" if use_colour else warning
            lines.append(f"  {'':<{widest_slug}}  {painted}")

    return "\n".join(lines)


def render_spike_list_json(summaries: list[SpikeSummary]) -> str:
    """Render the spike index as stable, versioned JSON."""

    payload = {
        "schema_version": SCHEMA_VERSION,
        "spikes": [
            {
                "slug": summary.slug,
                "question": summary.question,
                "has_go_mod": summary.has_go_mod,
            }
            for summary in summaries
        ],
    }

    return json.dumps(payload, indent=2)


# ---------------------------------------------------------------------------
# atom status
# ---------------------------------------------------------------------------


def render_status_text(report: "StatusReport", use_colour: bool = True) -> str:
    """Render a status report for a person.

    Everything the report found is shown in one go (B93). Problems are listed
    rather than raised, because a developer whose state file is broken still
    wants to see the module path and the last event that made it.
    """

    lines: list[str] = []

    def paint(text: str, colour: str) -> str:
        return f"{colour}{text}{_RESET}" if use_colour else text

    lines.append(f"Project: {report.root}")

    if report.module_path:
        lines.append(f"Module:  {report.module_path}")

    if report.state is not None:
        phase = report.state.phase.value
        status = report.state.status.value.replace("_", " ")
        lines.append(f"Phase:   {paint(phase, _GREEN)} ({status})")
    else:
        lines.append(f"Phase:   {paint('unknown', _RED)}")

    if report.last_event is not None:
        name = report.last_event.get("event", "?")
        when = report.last_event.get("at", "?")
        lines.append(f"Last:    {name} at {when}")

    if report.problems:
        lines.append("")
        # Amber, not red: most of these are warnings about recoverable things.
        # Reserving red for the genuine failure keeps the colour meaningful.
        heading = "Problems:" if not report.could_answer else "Warnings:"
        lines.append(paint(heading, _RED if not report.could_answer else _YELLOW))
        for problem in report.problems:
            # Problems are multi-line by design -- they carry recovery steps.
            for index, part in enumerate(str(problem).splitlines()):
                lines.append(f"  {'-' if index == 0 else ' '} {part}")

    if not report.problems and report.could_answer:
        lines.append("")
        lines.append(paint("No problems found.", _GREEN))

    return "\n".join(lines)


def render_status_json(report: "StatusReport") -> str:
    """Render a status report as JSON (B97).

    Emitted even when the state could not be read, so a caller that asked for
    JSON always gets something parseable to inspect.
    """

    payload = {"schema_version": SCHEMA_VERSION, **report.to_dict()}
    return json.dumps(payload, indent=2, sort_keys=True)
