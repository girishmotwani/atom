"""Render a CheckReport or SpikeResult as human-readable text or machine-readable JSON."""

from __future__ import annotations

import json

from atom.check import CheckReport
from atom.gates import GateStatus
from atom.index import SpikeSummary
from atom.invoke import RunOutcome
from atom.review import ReviewOutcome
from atom.spike import SpikeKind, SpikeResult, Stage, Verdict

# Each report is its own machine contract, so each carries its own version.
# A single shared number cannot be true for all of them: narrowing one report's
# semantics would either under-signal (leaving its consumers unable to detect
# the change) or over-signal a change to four reports that did not move.
#
# Bump one of these when that report's JSON shape or the *meaning* of an
# existing field changes incompatibly. Adding a field is not a bump; changing
# what an existing field answers for the same input is.
CHECK_SCHEMA_VERSION = 1
SPIKE_SCHEMA_VERSION = 1
SPIKE_LIST_SCHEMA_VERSION = 1
STATUS_SCHEMA_VERSION = 1

# 2: A21 narrowed `is_corroborated` from "several models in this group" to
# "several models on this line", so the same input now yields a different
# answer.
REVIEW_SCHEMA_VERSION = 2

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
        "schema_version": CHECK_SCHEMA_VERSION,
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
        "schema_version": SPIKE_SCHEMA_VERSION,
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
        "schema_version": SPIKE_LIST_SCHEMA_VERSION,
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


# How a resolved phase is explained in the text rendering (B177). Naming the
# source is not decoration: a typo'd branch reports as a pristine new phase
# (B163) and a lexical fallback happens silently (B162), so a developer seeing an
# unexpected answer needs to know which rule produced it.
_SOURCE_PHRASES = {
    "branch": "resolved from the git branch",
    "lexical": "newest phase directory; resolved by fallback",
}

# ASCII only, on purpose. The text rendering is printed to a console that may be
# code page 1252, where a Unicode tick would crash the whole command. `[x]` and
# `[ ]` carry the same present/absent meaning without that risk -- and, just as
# importantly, they never describe an artifact as "complete": the POC proved
# completeness is not derivable (F6-1), so presence is all Atom is allowed to say.
_PRESENT_MARK = "[x]"
_ABSENT_MARK = "[ ]"


def _present_over_required(artifacts) -> str:
    """Return the ``present/required`` count for a phase (e.g. ``6/6``, ``4/7``).

    A missing artifact is a phase in progress, not a failure (B166/B181), so this
    is a plain count and never a pass/fail verdict. The denominator is the
    *required* subset, which is six rather than seven for a phase whose POC was
    skipped (B168) -- the one place the conditional-artifact rule reaches output.
    """

    present = sum(1 for name in artifacts.required if artifacts.present[name])
    return f"{present}/{len(artifacts.required)}"


def render_status_text(report: "StatusReport", use_colour: bool = True) -> str:
    """Render the status report body for a person (B177/B178).

    The current phase gets full detail -- how it was resolved, every required
    artifact present or absent, and any approval recorded for it -- while every
    other phase gets a single summary line. The detail belongs to the phase you
    are working on; the rest is peripheral vision.

    Problems are deliberately **not** included here. They are rendered separately
    by ``render_status_problems`` and written to stderr, so that
    ``atom status > phase.txt`` captures the answer and lets the problems stay
    visible in the terminal. Each problem is therefore printed exactly once.
    """

    lines: list[str] = []

    def paint(text: str, colour: str) -> str:
        return f"{colour}{text}{_RESET}" if use_colour else text

    lines.append(f"Project: {report.root}")

    if report.module_path:
        lines.append(f"Module:  {report.module_path}")

    current = report.derivation.current
    if current is not None:
        source_phrase = _SOURCE_PHRASES.get(
            report.derivation.source, report.derivation.source
        )
        lines.append(f"Phase:   {paint(current.name, _GREEN)} ({source_phrase})")
        if not current.started:
            # B163: a branch can name a phase that has no directory yet. That is
            # the ordinary first move of a new phase, not an error -- so it is
            # stated plainly, in neutral styling, never as a failure.
            lines.append("         (not started -- no directory yet)")

        lines.append("Artifacts:")
        for name in current.artifacts.required:
            is_present = current.artifacts.present[name]
            # Present is affirmed in green; absent is neutral grey, never red.
            # A missing artifact is information, not a fault (B166/B181).
            mark = paint(_PRESENT_MARK, _GREEN) if is_present else paint(_ABSENT_MARK, _GREY)
            lines.append(f"  {mark} {name}")

        for approval in report.approvals:
            # Text shows only the current phase's approval (B177); JSON carries
            # all of them for a program to filter (B179).
            if approval.phase == current.name:
                lines.append(f"Approval: {approval.gate} approved on {approval.date}")
    else:
        # B164: no phase directories and the branch names none. A legitimate
        # state for a project that has not started a phase, not an error.
        lines.append(f"Phase:   {paint('none', _GREY)} (no phase directories found)")

    # B178: every *other* phase on one line -- name and present-of-required.
    # derivation.phases is already lexically ordered, so this is too.
    others = [
        phase
        for phase in report.derivation.phases
        if current is None or phase.name != current.name
    ]
    if others:
        lines.append("Other phases:")
        width = max(len(phase.name) for phase in others)
        for phase in others:
            count = _present_over_required(phase.artifacts)
            lines.append(f"  {phase.name.ljust(width)}  {count}")

    if report.last_event is not None:
        name = report.last_event.get("event", "?")
        when = report.last_event.get("at", "?")
        lines.append(f"Last:    {name} at {when}")

    if report.problems:
        # A pointer, not a repetition: someone redirecting stdout should be able
        # to tell that there was more to the story.
        count = len(report.problems)
        noun = "problem" if count == 1 else "problems"
        lines.append(f"{count} {noun} reported below.")
    else:
        lines.append(paint("No problems found.", _GREEN))

    return "\n".join(lines)


def render_status_problems(report: "StatusReport", use_colour: bool = True) -> str:
    """Render just the problems, for stderr. Empty string when there are none (B180).

    Every problem status reports is an advisory: the report was produced in
    full, and the problem is recoverable (a swept temp file, unsaved work, a
    corrupt state file whose loss did not stop derivation, a phase whose POC
    report cannot be parsed). So there is one colour and one heading.

    An earlier version reserved red for the case where Atom could not answer at
    all. That case turned out to be unreachable -- status has no ``--root``, so
    the root is the process's cwd, which necessarily exists -- and the red
    branch was therefore decoration claiming to carry a signal it never carried
    (F6-D6). Colour that never varies is not information.
    """

    if not report.problems:
        return ""

    lines = [f"{_YELLOW}Advisories:{_RESET}" if use_colour else "Advisories:"]
    for problem in report.problems:
        # Problems are multi-line by design -- they carry recovery steps.
        for index, part in enumerate(str(problem).splitlines()):
            lines.append(f"  {'-' if index == 0 else ' '} {part}")

    return "\n".join(lines)


def render_status_json(report: "StatusReport") -> str:
    """Render a status report as JSON (B179).

    Emitted even when the state could not be read, so a caller that asked for
    JSON always gets something parseable to inspect. The documented keys are a
    guaranteed subset of the object (see ``StatusReport.to_dict``).
    """

    payload = {"schema_version": STATUS_SCHEMA_VERSION, **report.to_dict()}
    return json.dumps(payload, indent=2, sort_keys=True)


# --- review output (Phase 4, B125-B131) -------------------------------------
#
# These renderers deliberately take no `use_colour` argument, unlike everything
# above. B125 makes the review report markdown, and B128 expects
# `atom review > review.md` to produce a usable file. ANSI escape codes in a
# .md file are invisible corruption -- they survive redirection and show up as
# noise in whatever reads the file next. The terminal-facing half of the output
# is `render_review_problems`, which is where colour would belong if it were
# ever wanted.


def render_review_markdown(outcome: "ReviewOutcome") -> str:
    """Render the review as markdown: what was reviewed, then what was found.

    The header comes first and is not optional. B127 exists because a report
    that omits a missing model reads exactly like a report where that model had
    no concerns, and the reader cannot tell the difference from the findings
    alone.
    """

    lines: list[str] = ["# Code review", ""]
    lines.extend(_review_header_lines(outcome))
    lines.extend(_review_toolchain_lines(outcome))
    lines.extend(_review_finding_lines(outcome))

    return "\n".join(lines).rstrip() + "\n"


def render_review_problems(outcome: "ReviewOutcome") -> str:
    """Render operational problems for stderr. Empty string when there are none.

    Following P3-5 and B128, this is the only place a failure's *detail* is
    printed. The markdown report states that a run is missing so a redirected
    file is still honest, but it does not carry the diagnostics -- otherwise
    every review file would accumulate transport errors that belong to the
    terminal session, not to the review.
    """

    problems: list[str] = []

    for run in outcome.invocation.runs:
        if run.outcome is not RunOutcome.COMPLETED:
            detail = run.detail or run.outcome.value
            problems.append(f"{run.model} run {run.run_index}: {detail}")

    for entry in outcome.invocation.unavailable_models():
        problems.append(f"{entry.model}: {entry.detail}")

    for failure in outcome.extraction.failures:
        problems.append(
            f"{failure.model} run {failure.run_index}: {failure.reason}"
        )

    if not problems:
        return ""

    lines = ["Problems:"]
    lines.extend(f"  - {problem}" for problem in problems)

    return "\n".join(lines) + "\n"


def render_review_json(outcome: "ReviewOutcome") -> str:
    """Render the review as the machine contract described by B126."""

    invocation = outcome.invocation

    payload = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "is_partial": outcome.is_partial,
        "has_no_usable_response": outcome.has_no_usable_response,
        "diff": {
            "source": invocation and outcome.diff.request.source.value,
            "files": list(outcome.diff.files),
            "changed_lines": outcome.diff.changed_lines,
        },
        "models": [
            {
                "model": model,
                "runs_requested": invocation.requested_for(model),
                "runs_completed": invocation.completed_for(model),
                # Two different facts, both true, deliberately both present:
                # the process finished, and the reply could be read. The
                # agreement fractions are drawn against the second.
                "runs_answered": outcome.runs_per_model[model],
            }
            for model in invocation.models
        ],
        "unavailable_models": [
            {"model": entry.model, "detail": entry.detail}
            for entry in invocation.unavailable_models()
        ],
        "unparsed_responses": [
            {
                "model": failure.model,
                "run_index": failure.run_index,
                "reason": failure.reason,
                "excerpt": failure.excerpt,
                # False means Atom could not read the reply at all; true means
                # it read it and the file guard declined the contents. Only the
                # first counts against the review's completeness.
                "reply_was_readable": failure.reply_was_readable,
            }
            for failure in outcome.extraction.failures
        ],
        "silent_runs": [
            {"model": model, "run_index": run_index}
            for model, run_index in outcome.silent_runs
        ],
        "findings": [_finding_payload(finding) for finding in outcome.findings],
    }

    return json.dumps(payload, indent=2, sort_keys=True)


def _review_header_lines(outcome: "ReviewOutcome") -> list[str]:
    """Build the "what was reviewed, and by whom" preamble (B127)."""

    invocation = outcome.invocation
    lines: list[str] = []

    request = outcome.diff.request
    scope = request.describe() if request is not None else "an unknown diff"
    lines.append(f"Reviewed {scope}: {outcome.diff.describe_size()}.")
    lines.append("")

    for path in outcome.diff.files:
        lines.append(f"- `{path}`")
    if outcome.diff.files:
        lines.append("")

    lines.append("| Model | Runs completed |")
    lines.append("| --- | --- |")
    for model in invocation.models:
        completed = invocation.completed_for(model)
        requested = invocation.requested_for(model)
        lines.append(f"| `{model}` | {completed}/{requested} |")
    lines.append("")

    unavailable = invocation.unavailable_models()
    if unavailable:
        # Named, but without the tool's error text. B127 requires the report to
        # admit that a model's opinion is missing; B128 requires operational
        # detail not to appear in both channels. The fact belongs in a file
        # someone may read months later, the diagnostic belongs to the terminal
        # session that produced it. See A14.
        lines.append("Models that could not be called:")
        lines.append("")
        for entry in unavailable:
            lines.append(f"- `{entry.model}` (see stderr for the reason)")
        lines.append("")

    failures = outcome.extraction.failures
    # Sectioned by what happened to the *run*, not to the individual failure.
    # A run that contributed a good finding answered the question even if part
    # of its reply was refused, and filing it under either heading below would
    # report an answered run as a missing one.
    unreadable = [
        failure for failure in failures
        if (failure.model, failure.run_index) in set(outcome.silent_runs)
    ]
    overruled = [
        failure for failure in failures
        if (failure.model, failure.run_index) in set(outcome.overruled_runs)
    ]
    if unreadable:
        # Named, not counted, and without the reason - same split as A14 above.
        # A response nobody could parse is an opinion that went missing, so the
        # report must admit it; why it could not be parsed is a tool problem
        # belonging to stderr.
        lines.append("Responses that could not be read:")
        lines.append("")
        for failure in unreadable:
            lines.append(
                f"- `{failure.model}` run {failure.run_index} "
                "(see stderr for the reason)"
            )
        lines.append("")

    if overruled:
        # A separate heading because this is a different event. The reply was
        # read; the file guard declined what it named. Listing it as unreadable
        # would blame the model for Atom's own scoping rule.
        lines.append("Replies that named files outside this diff:")
        lines.append("")
        for failure in overruled:
            lines.append(
                f"- `{failure.model}` run {failure.run_index} "
                "(read, but nothing it reported was in scope)"
            )
        lines.append("")

    # A run can go silent without producing an extraction failure at all: an
    # empty or whitespace-only reply is dropped before extraction ever sees it,
    # so it appears in no list above while still counting against the totals
    # below. Naming it here keeps the banner's promise honest.
    named = {(failure.model, failure.run_index) for failure in failures}
    unnamed_silence = [run for run in outcome.silent_runs if run not in named]
    if unnamed_silence:
        lines.append("Runs that returned nothing to read:")
        lines.append("")
        for model, run_index in unnamed_silence:
            lines.append(f"- `{model}` run {run_index} (empty reply)")
        lines.append("")

    if outcome.is_partial:
        # Counted as runs that produced no readable reply -- not as runs that
        # merely left the denominator. An overruled reply shrinks the fractions
        # below without being missing, so including it here would overstate how
        # much of the review failed to happen. Derived from the totals rather
        # than from `silent_runs`, which only covers runs that completed: a run
        # that timed out never completed and must still be counted here. The
        # three categories are disjoint, so subtracting both is safe.
        missing = (
            len(invocation.models) * invocation.runs_requested
            - sum(outcome.runs_per_model.values())
            - len(outcome.overruled_runs)
        )
        lines.append(
            f"> **This review is partial.** {missing} of "
            f"{len(invocation.models) * invocation.runs_requested} runs did not "
            "answer, so the agreement fractions below are out of fewer runs than "
            "were asked for. Every one of them is named above."
        )
        lines.append("")

    return lines


def _review_toolchain_lines(outcome: "ReviewOutcome") -> list[str]:
    """Record what the pre-review toolchain proved or did not check."""

    evidence = outcome.toolchain
    lines = ["## Toolchain evidence", ""]

    if not evidence.was_run:
        reason = evidence.skip_reason or "no reason was recorded"
        lines.append(f"Toolchain did not run: {reason}")
        lines.append("nothing was excluded from the review prompt.")
        lines.append("")
        return lines

    lines.append("| Command | Verdict |")
    lines.append("| --- | --- |")
    for result in evidence.gate_results:
        command = _toolchain_command_for_gate(result.name)
        verdict = _toolchain_verdict(result)
        lines.append(f"| `{command}` | {verdict} |")
    lines.append("")
    return lines


def _toolchain_command_for_gate(name: str) -> str:
    """Match report command names to the prompt's compact verdict list."""

    return {
        "build": "go build ./...",
        "vet": "go vet ./...",
        "fmt": "gofmt -l .",
        "test": "go test ./...",
        "race": "go test -race ./...",
        "staticcheck": "staticcheck ./...",
        "errcheck": "errcheck ./...",
        "govulncheck": "govulncheck ./...",
    }.get(name, name)


def _toolchain_verdict(result) -> str:
    """Render skipped advisory tools as unchecked rather than clean."""

    if result.status is GateStatus.SKIPPED and "not installed" in result.summary.lower():
        return "not installed - not checked"
    if result.status is GateStatus.SKIPPED:
        return f"SKIPPED - {result.summary}"
    if result.status is GateStatus.WARNING:
        return f"WARNING - {result.summary}"
    if result.status is GateStatus.FAILED:
        return f"FAILED - {result.summary}"
    return result.status.name


def _review_finding_lines(outcome: "ReviewOutcome") -> list[str]:
    """Build the findings section, grouped by file and led by severity."""

    if not outcome.findings:
        lines = ["## Findings", ""]
        lines.append(
            "No findings were reported." if not outcome.has_no_usable_response
            else "No findings were reported, because no model answered."
        )
        return lines

    lines: list[str] = ["## Findings", ""]

    # Files are ordered by their most severe finding rather than alphabetically,
    # so the first thing on screen is the worst thing found. `outcome.findings`
    # already arrives in severity order (B124), so first appearance is enough.
    files: list[str] = []
    for finding in outcome.findings:
        if finding.file not in files:
            files.append(finding.file)

    for path in files:
        lines.append(f"### `{path}`")
        lines.append("")
        for finding in outcome.findings:
            if finding.file == path:
                lines.extend(_single_finding_lines(finding))

    return lines


def _single_finding_lines(finding) -> list[str]:
    """Render one merged finding, span first."""

    # An em dash here arrives as mojibake wherever stdout is not UTF-8, and a
    # redirected report file keeps the damage permanently. A hyphen reads the
    # same and survives every console code page.
    lines: list[str] = [f"#### {finding.file}:{_line_span(finding)} - {finding.highest_severity}", ""]

    if finding.has_severity_disagreement:
        # B123. Naming the disagreement is the point: presenting one severity
        # as the severity would invent an agreement the measurement denies.
        claimed = ", ".join(finding.severities)
        lines.append(f"Severity is disputed: {claimed}.")
        lines.append("")

    if len(finding.lines) > 1:
        # A13. A group can cover more than one real defect, so the reader is
        # told the span is a grouping rather than a single reported line.
        reported = ", ".join(str(line) for line in finding.lines)
        lines.append(
            f"Reported at lines {reported}; nearby lines are grouped, so this "
            "entry may cover more than one problem."
        )
        lines.append("")

    if finding.has_nearby_multi_model_reports:
        # A22. Several models landed in this group but never on the same line.
        # That is not agreement and must not be shown as agreement, but it is
        # also not nothing, so it is stated plainly instead of dropped.
        lines.append(
            "Several models reported problems in this group, but on different "
            "lines, so this is not recorded as agreement."
        )
        lines.append("")

    agreement = ", ".join(
        f"`{entry.model}` {entry.fraction}" for entry in finding.agreement
    )
    lines.append(f"Reported by: {agreement}")
    lines.append("")

    for message in finding.messages:
        lines.append(
            f"- `{message.model}` run {message.run_index}, line {message.line} "
            f"({message.severity}): {message.message}"
        )
    lines.append("")

    return lines


def _line_span(finding) -> str:
    """Return `41` for a single line, `42-45` for a group (A13)."""

    if len(finding.lines) <= 1:
        return str(finding.line)

    return f"{finding.lines[0]}-{finding.lines[-1]}"


def _finding_payload(finding) -> dict:
    """Convert one merged finding to its JSON form."""

    return {
        "file": finding.file,
        "line": finding.line,
        "lines": list(finding.lines),
        "highest_severity": finding.highest_severity,
        "severities": list(finding.severities),
        "is_corroborated": finding.is_corroborated,
        "has_nearby_multi_model_reports": finding.has_nearby_multi_model_reports,
        "has_severity_disagreement": finding.has_severity_disagreement,
        "agreement": [
            {
                "model": entry.model,
                "runs_reporting": entry.runs_reporting,
                "runs_total": entry.runs_total,
            }
            for entry in finding.agreement
        ],
        "messages": [
            {
                "model": message.model,
                "run_index": message.run_index,
                "line": message.line,
                "severity": message.severity,
                "message": message.message,
            }
            for message in finding.messages
        ],
    }
