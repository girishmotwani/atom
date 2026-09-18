"""Behaviour tests for review output (B125-B131) and the ReviewOutcome bundle.

The rule these tests keep coming back to is B127: a report that does not say it
is missing a model's opinion is misleading in exactly the way this phase exists
to avoid. Most of what follows is about making absence visible -- a failed run,
an unavailable model, a response nobody could parse -- because every one of
those looks, in a naive report, exactly like "nothing was wrong there".
"""

from __future__ import annotations

import json

import pytest

from atom.diff import CapturedDiff, DiffRequest, DiffSource
from atom.extract import ExtractionFailure, ExtractionReport, Finding
from atom.invoke import InvocationReport, ModelAvailability, ModelRun, RunOutcome
from atom.merge import merge_findings
from atom.report import (
    render_review_json,
    render_review_markdown,
    render_review_problems,
)
from atom.review import ReviewOutcome

DIFF_TEXT = """diff --git a/store/cache.go b/store/cache.go
--- a/store/cache.go
+++ b/store/cache.go
@@ -40,0 +41,4 @@
+func Export() {}
+var x = 1
+var y = 2
+var z = 3
"""


def captured_diff(text: str = DIFF_TEXT) -> CapturedDiff:
    return CapturedDiff(
        text=text,
        request=DiffRequest(source=DiffSource.WORKING, base_ref=None),
    )


def run(
    model: str = "gpt-5.4",
    index: int = 1,
    outcome: RunOutcome = RunOutcome.COMPLETED,
    detail: str = "",
) -> ModelRun:
    return ModelRun(
        model=model,
        run_index=index,
        outcome=outcome,
        response_text="[]",
        duration_seconds=1.0,
        detail=detail,
    )


def invocation(
    models: tuple[str, ...] = ("gpt-5.4", "claude-haiku-4.5"),
    runs_requested: int = 2,
    runs: tuple[ModelRun, ...] | None = None,
    availability: tuple[ModelAvailability, ...] | None = None,
) -> InvocationReport:
    if runs is None:
        runs = tuple(
            run(model, index)
            for model in models
            for index in range(1, runs_requested + 1)
        )
    if availability is None:
        availability = tuple(
            ModelAvailability(model=model, available=True, detail="")
            for model in models
        )
    return InvocationReport(
        models=models,
        runs_requested=runs_requested,
        runs=runs,
        availability=availability,
    )


def finding(
    line: int,
    model: str = "gpt-5.4",
    index: int = 1,
    severity: str = "high",
    message: str = "A problem.",
    file: str = "store/cache.go",
) -> Finding:
    return Finding(
        file=file, line=line, severity=severity,
        message=message, model=model, run_index=index,
    )


def outcome(
    findings: tuple[Finding, ...] = (),
    inv: InvocationReport | None = None,
    failures: tuple[ExtractionFailure, ...] = (),
    diff: CapturedDiff | None = None,
) -> ReviewOutcome:
    inv = inv or invocation()
    runs_per_model = {model: inv.completed_for(model) for model in inv.models}
    return ReviewOutcome(
        diff=diff or captured_diff(),
        invocation=inv,
        extraction=ExtractionReport(findings=findings, failures=failures),
        findings=merge_findings(findings, runs_per_model) if findings else (),
    )


class TestWhatWasReviewed:
    """B127 - the report says what was looked at, and by whom."""

    def test_the_report_names_every_model_that_took_part(self):
        text = render_review_markdown(outcome((finding(41),)))

        assert "gpt-5.4" in text
        assert "claude-haiku-4.5" in text

    def test_the_report_states_how_many_runs_each_model_completed(self):
        text = render_review_markdown(outcome((finding(41),)))

        assert "2/2" in text

    def test_the_report_describes_the_diff_that_was_reviewed(self):
        text = render_review_markdown(outcome((finding(41),)))

        assert "store/cache.go" in text
        assert "working" in text.lower()

    def test_a_model_that_failed_every_run_is_still_named(self):
        # The dangerous case. A model that contributed nothing must not simply
        # vanish from the report, because its absence reads as agreement.
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2),
            run("claude-haiku-4.5", 1, RunOutcome.TIMED_OUT, "timed out"),
            run("claude-haiku-4.5", 2, RunOutcome.TIMED_OUT, "timed out"),
        )
        text = render_review_markdown(outcome((finding(41),), invocation(runs=runs)))

        assert "claude-haiku-4.5" in text
        assert "0/2" in text

    def test_an_unavailable_model_is_named_but_its_error_text_is_not_repeated(self):
        # A14, resolving a genuine tension between two clauses. B127 requires
        # the report to admit a model's opinion is missing; B128 forbids the
        # same operational detail appearing in both channels. Naming the model
        # satisfies the first, withholding the CLI's error string satisfies the
        # second, and stderr still carries the reason.
        availability = (
            ModelAvailability(model="gpt-5.4", available=True, detail=""),
            ModelAvailability(
                model="gemini-2.5-pro", available=False,
                detail='Model "gemini-2.5-pro" from --model flag is not available.',
            ),
        )
        inv = invocation(
            models=("gpt-5.4",),
            runs=(run("gpt-5.4", 1), run("gpt-5.4", 2)),
            availability=availability,
        )
        result = outcome((finding(41),), inv)
        text = render_review_markdown(result)

        assert "gemini-2.5-pro" in text
        assert "from --model flag is not available" not in text
        assert "from --model flag is not available" in render_review_problems(result)

    def test_responses_nobody_could_parse_are_reported(self):
        # Silently dropping an unparseable response turns a tool failure into
        # an apparently clean opinion. A14: the report names it, stderr says why.
        failures = (
            ExtractionFailure(
                model="claude-haiku-4.5", run_index=2,
                reason="no JSON array found", excerpt="I think the code is fine",
            ),
        )
        result = outcome((finding(41),), failures=failures)
        text = render_review_markdown(result)

        assert "claude-haiku-4.5" in text
        assert "could not be read" in text
        assert "no JSON array found" not in text
        assert "no JSON array found" in render_review_problems(result)


class TestFindingPresentation:
    """B125 plus the presentation decision recorded in A13."""

    def test_findings_are_grouped_under_their_file(self):
        findings = (finding(41, file="store/cache.go"), finding(10, file="a/other.go"))
        text = render_review_markdown(outcome(findings))

        assert "store/cache.go" in text
        assert "a/other.go" in text

    def test_a_single_line_finding_shows_that_line(self):
        text = render_review_markdown(outcome((finding(41),)))

        assert "store/cache.go:41" in text

    def test_a_finding_spanning_several_lines_shows_the_span(self):
        # A13. A merged group can cover more than one real defect, so the span
        # is shown rather than only its first line -- on the measured data a
        # group spanning 42-45 held two distinct defects.
        spanning = (
            finding(42, "gpt-5.4", 1, message="os.Create error ignored."),
            finding(45, "claude-haiku-4.5", 1, message="Export reads without the lock."),
        )
        text = render_review_markdown(outcome(spanning))

        assert "store/cache.go:42-45" in text

    def test_no_bare_finding_count_is_printed(self):
        # A13, developer decision. A headline count understates the number of
        # real defects whenever grouping merges two of them, and the reader has
        # no way to tell when that happened.
        spanning = (
            finding(42, "gpt-5.4", 1, message="os.Create error ignored."),
            finding(45, "claude-haiku-4.5", 1, message="Export reads without the lock."),
        )
        text = render_review_markdown(outcome(spanning)).lower()

        for phrase in ("1 finding", "1 issue", "findings found", "issues found"):
            assert phrase not in text

    def test_every_model_message_is_shown_with_its_author(self):
        # B120 is what makes a merged group tolerable: both defects stay
        # readable even when they share one heading.
        spanning = (
            finding(42, "gpt-5.4", 1, message="os.Create error ignored."),
            finding(45, "claude-haiku-4.5", 1, message="Export reads without the lock."),
        )
        text = render_review_markdown(outcome(spanning))

        assert "os.Create error ignored." in text
        assert "Export reads without the lock." in text
        assert "gpt-5.4" in text and "claude-haiku-4.5" in text

    def test_agreement_is_shown_as_a_fraction_per_model(self):
        text = render_review_markdown(outcome((finding(41), finding(41, "claude-haiku-4.5"))))

        assert "1/2" in text

    def test_disagreement_about_severity_is_visible(self):
        # B123. Presenting one severity as the severity would invent agreement
        # the measurement says does not exist.
        disputed = (
            finding(41, "gpt-5.4", 1, severity="critical"),
            finding(41, "claude-haiku-4.5", 1, severity="medium"),
        )
        text = render_review_markdown(outcome(disputed))

        assert "critical" in text and "medium" in text

    def test_findings_appear_in_severity_order(self):
        findings = (
            finding(10, severity="low", file="a/one.go", message="Low one."),
            finding(20, severity="critical", file="b/two.go", message="Critical one."),
        )
        text = render_review_markdown(outcome(findings))

        assert text.index("Critical one.") < text.index("Low one.")

    def test_a_review_with_no_findings_says_so_explicitly(self):
        text = render_review_markdown(outcome())

        assert "no findings" in text.lower()


class TestPartialReviews:
    """B131 - a partial review must announce itself."""

    def test_a_partial_review_is_marked_partial_in_markdown(self):
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2, RunOutcome.TIMED_OUT, "timed out"),
            run("claude-haiku-4.5", 1),
            run("claude-haiku-4.5", 2),
        )
        text = render_review_markdown(outcome((finding(41),), invocation(runs=runs)))

        assert "partial" in text.lower()

    def test_a_complete_review_is_not_marked_partial(self):
        text = render_review_markdown(outcome((finding(41),)))

        assert "partial" not in text.lower()

    def test_a_partial_review_is_marked_partial_in_json(self):
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2, RunOutcome.TIMED_OUT, "timed out"),
            run("claude-haiku-4.5", 1),
            run("claude-haiku-4.5", 2),
        )
        payload = json.loads(
            render_review_json(outcome((finding(41),), invocation(runs=runs)))
        )

        assert payload["is_partial"] is True


class TestJsonContract:
    """B126 - the machine contract, consistent with `atom status --json`."""

    def test_the_json_is_valid_and_carries_a_schema_version(self):
        payload = json.loads(render_review_json(outcome((finding(41),))))

        assert payload["schema_version"] >= 1

    def test_the_json_reports_findings_with_their_line_span(self):
        spanning = (
            finding(42, "gpt-5.4", 1, message="os.Create error ignored."),
            finding(45, "claude-haiku-4.5", 1, message="Export reads without the lock."),
        )
        payload = json.loads(render_review_json(outcome(spanning)))

        assert payload["findings"][0]["lines"] == [42, 45]

    def test_the_json_reports_agreement_with_both_halves_of_the_fraction(self):
        payload = json.loads(render_review_json(outcome((finding(41),))))
        agreement = payload["findings"][0]["agreement"][0]

        assert agreement["runs_reporting"] == 1
        assert agreement["runs_total"] == 2

    def test_the_json_keeps_every_attributed_message(self):
        spanning = (
            finding(42, "gpt-5.4", 1, message="os.Create error ignored."),
            finding(45, "claude-haiku-4.5", 1, message="Export reads without the lock."),
        )
        payload = json.loads(render_review_json(outcome(spanning)))
        messages = payload["findings"][0]["messages"]

        assert len(messages) == 2
        assert {entry["model"] for entry in messages} == {"gpt-5.4", "claude-haiku-4.5"}

    def test_the_json_names_models_that_produced_nothing(self):
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2),
            run("claude-haiku-4.5", 1, RunOutcome.TIMED_OUT, "timed out"),
            run("claude-haiku-4.5", 2, RunOutcome.TIMED_OUT, "timed out"),
        )
        payload = json.loads(
            render_review_json(outcome((finding(41),), invocation(runs=runs)))
        )
        participation = {entry["model"]: entry for entry in payload["models"]}

        assert participation["claude-haiku-4.5"]["runs_completed"] == 0

    def test_the_json_reports_unparseable_responses(self):
        failures = (
            ExtractionFailure(
                model="claude-haiku-4.5", run_index=2,
                reason="no JSON array found", excerpt="I think the code is fine",
            ),
        )
        payload = json.loads(render_review_json(outcome((finding(41),), failures=failures)))

        assert payload["unparsed_responses"][0]["reason"] == "no JSON array found"


class TestChannelSeparation:
    """B128 / P3-5 - `atom review > review.md` must leave a clean file."""

    def test_operational_problems_render_separately_from_the_report(self):
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2, RunOutcome.TIMED_OUT, "timed out"),
            run("claude-haiku-4.5", 1),
            run("claude-haiku-4.5", 2),
        )
        problems = render_review_problems(outcome((finding(41),), invocation(runs=runs)))

        assert problems
        assert "timed out" in problems.lower()

    def test_a_clean_review_produces_no_problem_output(self):
        assert render_review_problems(outcome((finding(41),))) == ""

    def test_the_markdown_report_does_not_repeat_the_problem_text(self):
        # "Neither duplicated" in B128. The report states that a run is missing;
        # the stderr channel explains what went wrong. Printing the same lines
        # to both means a redirected report either loses the warning or
        # carries noise the file should not contain.
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2, RunOutcome.TIMED_OUT, "connection reset by peer"),
            run("claude-haiku-4.5", 1),
            run("claude-haiku-4.5", 2),
        )
        result = outcome((finding(41),), invocation(runs=runs))

        assert "connection reset by peer" not in render_review_markdown(result)
        assert "connection reset by peer" in render_review_problems(result)


class TestReviewOutcome:
    """The bundle the CLI hands to the renderers."""

    def test_an_outcome_knows_it_is_partial_when_a_run_failed(self):
        runs = (
            run("gpt-5.4", 1),
            run("gpt-5.4", 2, RunOutcome.TIMED_OUT, "timed out"),
            run("claude-haiku-4.5", 1),
            run("claude-haiku-4.5", 2),
        )

        assert outcome((finding(41),), invocation(runs=runs)).is_partial

    def test_an_outcome_with_every_run_answered_is_not_partial(self):
        assert not outcome((finding(41),)).is_partial

    def test_an_outcome_knows_when_no_model_produced_anything_usable(self):
        # B130. An empty report is indistinguishable from a clean review.
        runs = tuple(
            run(model, index, RunOutcome.TIMED_OUT, "timed out")
            for model in ("gpt-5.4", "claude-haiku-4.5")
            for index in (1, 2)
        )

        assert outcome(inv=invocation(runs=runs)).has_no_usable_response

    def test_a_review_that_ran_but_found_nothing_is_not_treated_as_unusable(self):
        # The distinction B130 rests on: "nobody answered" and "everybody
        # answered, nothing was wrong" produce the same empty finding list and
        # must not produce the same outcome.
        assert not outcome().has_no_usable_response
