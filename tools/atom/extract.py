"""Turn a model's reply into validated findings, or into a recorded failure.

Extraction is the narrowest part of `atom review`, and deliberately so. The
Phase 4 spike made 40 calls across two models and two output contracts, and
found **exactly one** deviation from the requested format: a markdown fence.
No malformed JSON, no invalid severities, no non-integer line numbers, no
truncation.

That single observation shapes the whole module:

*   The one deviation that *was* observed gets deterministic handling — strip
    the fence (B113).
*   The rescue heuristics that were *not* observed are not implemented (B114).
    Shipping an unexercised recovery path means shipping behaviour nobody has
    seen fail, and the bracket scan's failure mode is silent: it captures the
    wrong span and produces confident nonsense.
*   Everything else is validated anyway (B116), not because it failed but
    because the alternative to a clear message is a crash inside the merge
    step.

The governing rule is B115: **nothing is silently dropped.** A response that
cannot be used becomes a recorded, reportable failure. A review that quietly
loses half its input while still printing a confident report is the precise
failure this phase exists to prevent.

See `specs/atom-cli/phase-04-review/design-spec.md` for B113-B117.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from atom.invoke import ModelRun, RunOutcome

# The four severities the review prompt offers. Kept as a tuple rather than a
# set so that any future ordering logic has a canonical sequence to lean on.
ALLOWED_SEVERITIES = ("critical", "high", "medium", "low")

REQUIRED_FIELDS = ("file", "line", "severity", "message")

# Matches a fenced block carrying an explicit `json` label. Preferred over the
# generic pattern below: when a model illustrates a point with a ```go sample
# and *then* supplies its findings, taking the first fence blindly would throw
# the whole reply away.
_JSON_FENCE_PATTERN = re.compile(r"```json\s*(.*?)```", re.DOTALL)

# Matches a fenced block with or without a language tag. Non-greedy so the
# first complete fence wins rather than everything up to the last one.
_FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)

# Long enough to recognise a reply, short enough that a runaway response
# cannot flood the report.
_EXCERPT_LIMIT = 300


@dataclass(frozen=True)
class Finding:
    """One problem reported by one run of one model.

    `model` and `run_index` travel with the finding because the merge step
    counts *how many runs of which models* said the same thing — that count is
    the confidence signal, so losing its provenance would destroy it.
    """

    file: str
    line: int
    severity: str
    message: str
    model: str
    run_index: int


@dataclass(frozen=True)
class ExtractionFailure:
    """A run whose output could not be used, kept so the report can say so."""

    model: str
    run_index: int
    reason: str
    excerpt: str = ""
    # True when the reply itself parsed and only its *contents* were refused.
    # The difference matters upstream: a run that answered and was overruled
    # still answered, while a run whose reply could not be read gave nothing.
    # Only the second kind makes a review partial.
    reply_was_readable: bool = False


@dataclass(frozen=True)
class ExtractionReport:
    """Findings and failures together, because a report needs both."""

    findings: tuple[Finding, ...]
    failures: tuple[ExtractionFailure, ...]

    @property
    def has_failures(self) -> bool:
        """Return true when any run's output could not be fully used."""

        return bool(self.failures)


def strip_fence(text: str) -> str:
    """Return the payload inside a markdown fence, or the text unchanged.

    This is the only salvage Atom performs, and it is not really salvage: a
    fence is an unambiguous delimiter, so removing it is *extraction*, not
    repair. The distinction matters — it is what separates this from the
    bracket scan in B114, which has to guess where the data begins.

    One of the two model families the spike measured fenced its reply on all
    20 attempts, while being explicitly told not to. Handling it is mandatory.

    When several fences are present, a `json`-labelled one wins. That is still
    selection between delimiters the model supplied, not an invention of one.

    Known limitation: a fence closes at the first ``` it meets, so a *message*
    containing a triple backtick truncates the payload and the run fails
    loudly. Adding a greedy retry would mean shipping another unobserved
    recovery path, which is exactly what B114 argues against.
    """

    labelled = _JSON_FENCE_PATTERN.search(text)
    if labelled:
        return labelled.group(1).strip()

    match = _FENCE_PATTERN.search(text)
    if match:
        return match.group(1).strip()

    return text.strip()


def extract_from_run(
    run: ModelRun,
    allowed_files: Sequence[str] | None = (),
) -> tuple[list[Finding], ExtractionFailure | None]:
    """Parse one run's reply into findings plus at most one recorded failure.

    Returns both halves rather than raising, because a bad reply from one run
    must not stop the other five. A rejected *finding* does not discard its
    siblings either: the good findings are returned and the rejection is
    recorded, so the report shows exactly what was dropped and why.

    `allowed_files` of `None` disables the B117 file guard. Passing an empty
    sequence is *not* the same thing — that would reject everything.
    """

    if run.outcome is not RunOutcome.COMPLETED:
        return [], ExtractionFailure(
            model=run.model,
            run_index=run.run_index,
            reason=run.detail or f"run did not complete ({run.outcome.value})",
        )

    payload = strip_fence(run.response_text)
    excerpt = _excerpt(run.response_text)

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as error:
        return [], _failure(run, f"reply is not valid json: {error}", excerpt)

    if not isinstance(parsed, list):
        return [], _failure(
            run, f"reply is not a json array (got {type(parsed).__name__})", excerpt
        )

    findings: list[Finding] = []
    rejections: list[str] = []
    # A reply counts as readable only if *every* rejection was the file guard.
    # One malformed element means part of the reply could not be understood,
    # and a reply Atom could not understand is silence no matter how much
    # well-formed JSON surrounded it.
    only_the_file_guard_objected = True

    for position, element in enumerate(parsed):
        problem = _reject_reason(element, allowed_files=None)
        if problem:
            only_the_file_guard_objected = False
        else:
            problem = _file_guard_reason(element, allowed_files)
        if problem:
            rejections.append(f"finding {position + 1}: {problem}")
            continue
        findings.append(
            Finding(
                file=element["file"],
                line=element["line"],
                severity=element["severity"],
                message=element["message"],
                model=run.model,
                run_index=run.run_index,
            )
        )

    if rejections:
        return findings, _failure(
            run,
            "; ".join(rejections),
            excerpt,
            reply_was_readable=only_the_file_guard_objected,
        )

    return findings, None


def extract_all(
    runs: Iterable[ModelRun],
    allowed_files: Sequence[str] | None = (),
) -> ExtractionReport:
    """Extract findings from every run, keeping every failure visible."""

    findings: list[Finding] = []
    failures: list[ExtractionFailure] = []

    for run in runs:
        run_findings, failure = extract_from_run(run, allowed_files)
        findings.extend(run_findings)
        if failure is not None:
            failures.append(failure)

    return ExtractionReport(findings=tuple(findings), failures=tuple(failures))


def _reject_reason(element: object, allowed_files: Sequence[str] | None) -> str:
    """Return why this element is unusable, or an empty string if it is fine."""

    if not isinstance(element, dict):
        return f"element is not an object (got {type(element).__name__})"

    missing = [field for field in REQUIRED_FIELDS if field not in element]
    if missing:
        return f"missing field(s): {', '.join(missing)}"

    if element["severity"] not in ALLOWED_SEVERITIES:
        return (
            f"severity {element['severity']!r} is not one of "
            f"{', '.join(ALLOWED_SEVERITIES)}"
        )

    # `isinstance(True, int)` is True in Python, so a plain int check accepts
    # `"line": true` and silently yields a finding pointing at line 1. The
    # bool test has to come first.
    line = element["line"]
    if isinstance(line, bool) or not isinstance(line, int):
        return f"line is {type(line).__name__}, not an integer"

    # Files start at line 1. A finding at line 0 or below has nowhere to
    # point, and because the merge step groups nearby lines together,
    # impossible line numbers would cluster into something that looks like a
    # real location.
    if line < 1:
        return f"line {line} is not a real line number (files start at line 1)"

    # B117. Deliberately last, so that striking it (per A2) leaves the rest of
    # the validation untouched.
    return _file_guard_reason(element, allowed_files)


def _file_guard_reason(element: dict, allowed_files: Sequence[str] | None) -> str:
    """Return why B117 refuses this element, or an empty string if it passes.

    Split out from the structural checks because the two rejections mean
    different things to the caller. A malformed element means the reply could
    not be understood; a file outside the diff means it was understood and
    declined. Only the first is silence.
    """

    if allowed_files is not None and element["file"] not in allowed_files:
        return (
            f"file {element['file']!r} is not in the reviewed diff "
            "(the model named something it was not shown)"
        )

    return ""


def _failure(
    run: ModelRun, reason: str, excerpt: str, reply_was_readable: bool = False
) -> ExtractionFailure:
    return ExtractionFailure(
        model=run.model,
        run_index=run.run_index,
        reason=reason,
        excerpt=excerpt,
        reply_was_readable=reply_was_readable,
    )


def _excerpt(text: str) -> str:
    """Keep enough of a reply to recognise it, without flooding the report."""

    condensed = text.strip()
    if len(condensed) <= _EXCERPT_LIMIT:
        return condensed

    return condensed[:_EXCERPT_LIMIT] + "..."
