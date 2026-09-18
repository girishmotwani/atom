"""Compose the review pipeline and describe what came back from it.

`atom review` is four steps that already exist separately — capture a diff, ask
the models, extract findings, merge them — plus one job that has no home in any
of those modules: deciding what the *whole run* amounted to. Was a model
missing? Did anybody answer at all? That question spans every step, so it lives
here rather than being re-derived by the CLI and the renderers independently
and drifting apart.

The distinction this module exists to protect is B130's: "nobody answered" and
"everybody answered and found nothing" both produce an empty finding list, and
they must never produce the same outcome.

See `specs/atom-cli/phase-04-review/design-spec.md` for B129-B131.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from atom.diff import CapturedDiff, DiffRequest, capture_diff
from atom.extract import ExtractionReport, extract_all
from atom.invoke import InvocationReport, invoke_models
from atom.merge import DEFAULT_PROXIMITY_WINDOW, MergedFinding, merge_findings
from atom.runner import CommandRunner

# The two models the Phase 4 spike actually measured. Named here rather than in
# the CLI because the pairing is an evidence-backed default, not a UI choice:
# they disagreed on all four planted defects, which is the entire reason the
# review consults more than one. Anything else is a guess until it is measured.
DEFAULT_REVIEW_MODELS = ("gpt-5.4", "claude-haiku-4.5")

# Reproduced verbatim from `poc/review-json/spike.py`. The compliance figures
# this phase is built on -- 100% for one model, 100%-after-fence-stripping for
# the other -- were measured with *this* wording. Rephrasing it, however
# harmlessly, would silently invalidate every number in the POC report, because
# output format compliance is exactly the thing prompt wording moves.
REVIEW_PROMPT = """You are reviewing a Go diff. Report real problems only.

Respond with a JSON array. Every element must be an object with exactly these keys:
  "file": string, the path from the diff
  "line": integer, the line number in the new file
  "severity": one of "critical", "high", "medium", "low"
  "message": string, one sentence describing the problem

Respond with the JSON array and nothing else. No prose, no explanation, no headings.

Here is the diff:

{diff}
"""


@dataclass(frozen=True)
class ReviewOutcome:
    """Everything one `atom review` produced, including what it failed to."""

    diff: CapturedDiff
    invocation: InvocationReport
    extraction: ExtractionReport
    findings: tuple[MergedFinding, ...]

    @property
    def is_partial(self) -> bool:
        """Return true when any requested run did not answer (B131, A5).

        Deliberately strict: one failed run out of six is enough. Run count is
        the denominator of every agreement fraction, so a missing run degrades
        the headline output of the review rather than merely shrinking it.
        """

        return self.invocation.is_partial

    @property
    def has_no_usable_response(self) -> bool:
        """Return true when not one run produced a reply Atom could read (B130).

        Note what this does *not* consult: the finding list. A review where
        every model answered and reported nothing has an empty finding list and
        is a perfectly good result. Conflating the two would let a total
        infrastructure failure print as a clean bill of health, which is the
        specific confusion B130 calls dangerous.

        Note also what it *does* consult: extraction, not just the process exit.
        A model that replies "I reviewed the diff and found nothing" exits zero
        and counts as a completed run, yet contributes no opinion. Measuring
        usability at the process boundary let exactly that case report "No
        findings were reported" and exit 0 -- the same dangerous confusion,
        arriving through a door one layer further in.
        """

        return not self._runs_that_answered

    @property
    def _runs_that_answered(self) -> set[tuple[str, int]]:
        """Identify runs that survived both invocation and extraction.

        A run is excluded only when extraction failed *and* salvaged nothing.
        A reply holding two good findings and one malformed element is recorded
        as a failure yet still contributed an opinion, so it stays counted.
        """

        completed = {(run.model, run.run_index) for run in self.invocation.usable_runs}
        contributed = {
            (finding.model, finding.run_index) for finding in self.extraction.findings
        }
        unreadable = {
            (failure.model, failure.run_index) for failure in self.extraction.failures
        }
        return completed - (unreadable - contributed)

    @property
    def runs_per_model(self) -> dict[str, int]:
        """Return the completed-run count per model, as agreement denominators."""

        return {model: self.invocation.completed_for(model) for model in self.invocation.models}


def run_review(
    request: DiffRequest,
    models: Sequence[str],
    runner: CommandRunner,
    working_directory: Path,
    runs: int,
    concurrency: int,
    window: int = DEFAULT_PROXIMITY_WINDOW,
    disable_mcp_servers: Sequence[str] = (),
) -> ReviewOutcome:
    """Capture a diff, ask every model about it, and merge what comes back.

    The order is fixed and the failures are not symmetric. A diff that cannot
    be captured raises, because there is nothing to review and pretending
    otherwise would produce a confident empty report. Everything after that
    point degrades instead: a run that fails is recorded, a reply nobody can
    parse is recorded, and the review continues with whatever answered (B129).
    """

    diff = capture_diff(request, runner, working_directory)

    invocation = invoke_models(
        models=models,
        prompt=REVIEW_PROMPT.format(diff=diff.text),
        runner=runner,
        working_directory=working_directory,
        runs=runs,
        concurrency=concurrency,
        disable_mcp_servers=disable_mcp_servers,
    )

    # The diff's own file list is the allow-list (B117): a finding about a file
    # outside the diff is either a hallucination or a comment on code nobody
    # asked about, and both are noise in a review of *this* change.
    extraction = extract_all(invocation.usable_runs, allowed_files=diff.files)

    outcome = ReviewOutcome(
        diff=diff,
        invocation=invocation,
        extraction=extraction,
        findings=(),
    )

    return ReviewOutcome(
        diff=diff,
        invocation=invocation,
        extraction=extraction,
        findings=merge_findings(
            extraction.findings, outcome.runs_per_model, window=window
        ),
    )
