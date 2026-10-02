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

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from atom.check import NotAGoModuleError, run_check
from atom.diff import CapturedDiff, DiffRequest, capture_diff
from atom.extract import ExtractionReport, extract_all
from atom.gates import GateResult, advisory_gates, default_gates
from atom.invoke import InvocationReport, RunOutcome, invoke_models
from atom.merge import DEFAULT_PROXIMITY_WINDOW, MergedFinding, merge_findings
from atom.runner import CommandRunner
from atom.toolchain import ToolchainEvidence

# The two models Atom measured head to head, not a UI choice. The pairing is
# evidence-backed: across 70 calls against a fixture with four planted defects,
# these two were the only models that named the exact defect line reliably --
# gpt-5.4 at 98% and gemini-3.8-flash at 100%, against 15-56% for every other
# candidate tried. See phase-04-review/decisions.md A26 for the full table and
# for why claude-haiku-4.5, the previous default, was replaced.
#
# Accuracy is not the only reason. A second model earns its slot by *agreeing*
# in a way the merge step can use, and agreement is scored by line proximity:
# a model that finds the right defect but names a different line each run
# splits into separate low-support groups and reports as disagreement. Both
# models here attribute consistently, so corroboration means what it says.
#
# Known cost, recorded rather than fixed: model availability is account-specific,
# and an account without `gemini-3.8-flash` gets a *partial* review that exits
# non-zero (P4-3) until it passes `--model` explicitly. Whether the default should
# probe and substitute a fallback instead of failing is open -- see A26's Pending
# note, which explains why that is not a one-line change.
DEFAULT_REVIEW_MODELS = ("gpt-5.4", "gemini-3.8-flash")

# Reproduced verbatim from `poc/review-json/spike.py`. The compliance figures
# this phase is built on -- 100% for one model, 100%-after-fence-stripping for
# the other -- were measured with *this* wording. Rephrasing it, however
# harmlessly, would silently invalidate every number in the POC report, because
# output format compliance is exactly the thing prompt wording moves.
REVIEW_PROMPT = """You are reviewing a Go diff. Report real problems only.
{toolchain}
Respond with a JSON array. Every element must be an object with exactly these keys:
  "file": string, the path from the diff
  "line": integer, the line number in the new file
  "severity": one of "critical", "high", "medium", "low"
  "message": string, one sentence describing the problem

Respond with the JSON array and nothing else. No prose, no explanation, no headings.

Here is the diff:

{diff}
"""


class ToolchainGateFailed(Exception):
    """Raised when required Go gates fail before model review can begin."""

    def __init__(self, failures: Sequence[GateResult]) -> None:
        self.failures = tuple(failures)
        names = ", ".join(result.name for result in self.failures)
        super().__init__(f"Required toolchain gates failed: {names}")


@dataclass(frozen=True)
class ReviewOutcome:
    """Everything one `atom review` produced, including what it failed to."""

    diff: CapturedDiff
    invocation: InvocationReport
    extraction: ExtractionReport
    findings: tuple[MergedFinding, ...]
    toolchain: ToolchainEvidence = field(
        default_factory=lambda: ToolchainEvidence(
            gate_results=(), was_run=False, skip_reason="toolchain evidence was not collected"
        )
    )

    @property
    def is_partial(self) -> bool:
        """Return true when any requested run did not answer (B131, A5).

        Deliberately strict: one silent run out of six is enough. Run count is
        the denominator of every agreement fraction, so a run that does not
        answer degrades the headline output of the review rather than merely
        shrinking it.

        "Did not answer" covers two different events that A5 originally treated
        as one. A run can go missing -- timeout, crash, model unavailable -- or
        it can complete and return a reply nobody could read. Two real reviews
        produced zero of the first and two of the second, and the second was
        being counted as a full answer. Both leave the same hole in the
        denominator, so both make the review partial.
        """

        return self.invocation.is_partial or bool(self._runs_that_went_silent)

    @property
    def silent_runs(self) -> tuple[tuple[str, int], ...]:
        """Return the runs that completed without contributing an opinion.

        Public because the report has to name them. A run counted in the "did
        not answer" total but absent from every list of problems leaves the
        partial banner promising an explanation that was never written -- the
        report would be accurate in its arithmetic and misleading in its prose.
        """

        return tuple(sorted(self._runs_that_went_silent))

    @property
    def _runs_that_went_silent(self) -> set[tuple[str, int]]:
        """Identify runs that finished the process but contributed no opinion.

        Based on every run that *completed*, not on `usable_runs`. The two
        differ by exactly the case the review gate caught here: a run that
        exits zero with empty or whitespace-only text is counted as completed
        by `InvocationReport`, yet dropped before extraction ever sees it. Such
        a run was therefore in neither the answered set nor the silent one, and
        a review consisting entirely of blank replies reported a denominator of
        zero while insisting it was complete.
        """

        completed = {
            (run.model, run.run_index)
            for run in self.invocation.runs
            if run.outcome is RunOutcome.COMPLETED
        }
        # A reply that parsed and was then overruled by the B117 file guard is
        # not silence. The model answered; Atom declined the answer. Counting
        # that as a missing run would redden CI for a working tool doing its
        # job. It still leaves the denominator, because it offered no opinion
        # about *this* diff -- shrinking a fraction and failing a build are
        # different penalties for different faults.
        return completed - self._runs_that_answered - self._runs_overruled

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

        An overruled reply counts as usable here. B130 asks whether Atom got a
        reply it could read, and a reply refused by the file guard was read --
        the tool and the model both worked, and saying "no model produced
        anything usable" would misdescribe a review that functioned.
        """

        return not (self._runs_that_answered | self._runs_overruled)

    @property
    def overruled_runs(self) -> tuple[tuple[str, int], ...]:
        """Return runs whose only contribution was refused by the file guard."""

        return tuple(sorted(self._runs_overruled))

    @property
    def _runs_overruled(self) -> set[tuple[str, int]]:
        """Identify runs whose reply was read and then declined by B117.

        Separate from silence on purpose. These runs produced output Atom
        understood; the file guard refused its contents. They leave the
        denominator because they said nothing about *this* diff, but they are
        evidence the tool and the model both worked.

        Runs that also contributed a good finding are excluded, so that
        answered, overruled and silent stay disjoint. A reply holding one
        in-scope finding and one out-of-scope one answered the question; only
        its surplus was refused. Counting it in both sets made the partial
        total subtract it twice and let the report file an answered run under
        a heading about replies that produced nothing.
        """

        readable_failures = {
            (failure.model, failure.run_index)
            for failure in self.extraction.failures
            if failure.reply_was_readable
        }
        return readable_failures - self._runs_that_answered

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
        """Return the answered-run count per model, as agreement denominators.

        Not the completed-run count. A run whose reply could not be read gave
        no opinion, and counting it inflates every denominator drawn against
        that model: a finding reported by both readable replies of three runs
        printed "2 of 3", inventing a dissent from a run that said nothing.
        Every model stays in the mapping even at zero, because `merge_findings`
        treats an absent model as a caller error rather than a silent one.
        """

        answered = self._runs_that_answered
        return {
            model: sum(1 for run_model, _ in answered if run_model == model)
            for model in self.invocation.models
        }


def run_review(
    request: DiffRequest,
    models: Sequence[str],
    runner: CommandRunner,
    working_directory: Path,
    runs: int,
    concurrency: int,
    window: int = DEFAULT_PROXIMITY_WINDOW,
    disable_mcp_servers: Sequence[str] = (),
    skip_toolchain: bool = False,
) -> ReviewOutcome:
    """Capture a diff, ask every model about it, and merge what comes back.

    The order is fixed and the failures are not symmetric. A diff that cannot
    be captured raises, because there is nothing to review and pretending
    otherwise would produce a confident empty report. Everything after that
    point degrades instead: a run that fails is recorded, a reply nobody can
    parse is recorded, and the review continues with whatever answered (B129).
    """

    toolchain = _collect_toolchain_evidence(
        working_directory, runner, skip_toolchain=skip_toolchain
    )
    if toolchain.blocking_failures:
        raise ToolchainGateFailed(toolchain.blocking_failures)

    diff = capture_diff(request, runner, working_directory)

    invocation = invoke_models(
        models=models,
        prompt=REVIEW_PROMPT.format(
            toolchain=_prompt_toolchain_text(toolchain),
            diff=diff.text,
        ),
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
        toolchain=toolchain,
    )

    return ReviewOutcome(
        diff=diff,
        invocation=invocation,
        extraction=extraction,
        findings=merge_findings(
            extraction.findings, outcome.runs_per_model, window=window
        ),
        toolchain=toolchain,
    )


def _collect_toolchain_evidence(
    working_directory: Path,
    runner: CommandRunner,
    skip_toolchain: bool,
) -> ToolchainEvidence:
    """Run required and advisory Go gates before model review consumes the diff."""

    if skip_toolchain:
        return ToolchainEvidence(
            gate_results=(),
            was_run=False,
            skip_reason="toolchain checks were skipped by request",
        )

    try:
        required_report = run_check(
            working_directory, default_gates(enable_race=True), runner
        )
        advisory_report = run_check(working_directory, advisory_gates(), runner)
    except NotAGoModuleError as error:
        return ToolchainEvidence(gate_results=(), was_run=False, skip_reason=str(error))

    return ToolchainEvidence(
        gate_results=required_report.gate_results + advisory_report.gate_results,
        was_run=True,
        skip_reason="",
    )


def _prompt_toolchain_text(toolchain: ToolchainEvidence) -> str:
    """Return the placeholder text while preserving empty-substitution identity."""

    block = toolchain.as_prompt_block()
    return f"{block}\n"
