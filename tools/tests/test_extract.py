"""Behaviour tests for extraction and validation (B113-B117).

The spike measured exactly one deviation in 40 calls: a markdown fence. These
tests pin the deterministic handling of that case, and pin the *absence* of the
heuristic that was deliberately not shipped.
"""

from __future__ import annotations

import json

import pytest

from atom.extract import (
    ALLOWED_SEVERITIES,
    ExtractionReport,
    Finding,
    extract_all,
    extract_from_run,
    strip_fence,
)
from atom.invoke import ModelRun, RunOutcome

FILES = ("store/cache.go", "store/index.go")


def run_with(text: str, model: str = "gpt-5.4", run_index: int = 1) -> ModelRun:
    """Build a completed run carrying `text` as its response."""

    return ModelRun(
        model=model,
        run_index=run_index,
        outcome=RunOutcome.COMPLETED,
        response_text=text,
        duration_seconds=1.0,
    )


def findings_json(*findings: dict) -> str:
    return json.dumps(list(findings))


def a_finding(**overrides) -> dict:
    base = {
        "file": "store/cache.go",
        "line": 44,
        "severity": "high",
        "message": "Mutex is copied by value.",
    }
    base.update(overrides)
    return base


class TestFenceStripping:
    """B113 - one of the two model families fences unconditionally, 20/20."""

    def test_plain_json_needs_no_stripping(self):
        assert strip_fence('[{"a": 1}]') == '[{"a": 1}]'

    def test_a_json_labelled_fence_is_stripped(self):
        text = '```json\n[{"a": 1}]\n```'

        assert strip_fence(text) == '[{"a": 1}]'

    def test_an_unlabelled_fence_is_stripped(self):
        text = '```\n[{"a": 1}]\n```'

        assert strip_fence(text) == '[{"a": 1}]'

    def test_surrounding_whitespace_is_ignored(self):
        text = '\n\n```json\n[{"a": 1}]\n```\n\n'

        assert strip_fence(text) == '[{"a": 1}]'

    def test_a_json_labelled_fence_wins_over_an_earlier_unlabelled_one(self):
        # Models habitually illustrate a problem with a code sample and *then*
        # give their findings. Taking the first fence blindly loses the entire
        # run to a snippet the model only meant as an example.
        #
        # Preferring the block the model itself labelled `json` is selection
        # between delimited candidates, not the guessing B114 rejects: no
        # boundary is being invented.
        text = (
            "The problem is here:\n"
            "```go\nvar mu sync.Mutex\n```\n"
            "Findings:\n"
            "```json\n" + findings_json(a_finding()) + "\n```"
        )

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is None
        assert len(findings) == 1

    def test_an_unlabelled_fence_still_works_when_it_is_the_only_one(self):
        text = "```\n" + findings_json(a_finding()) + "\n```"

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is None
        assert len(findings) == 1

    def test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly(self):
        # Known limitation, recorded rather than fixed: a fence closes at the
        # first ``` it meets, so a message *containing* one truncates the
        # payload. Adding a greedy retry would mean shipping another
        # unobserved recovery path, which is what B114 warns against. Pinned
        # here so the behaviour is visible and any future fix is deliberate.
        text = "```json\n" + findings_json(a_finding(message="use ``` fences")) + "\n```"

        findings, failure = extract_from_run(run_with(text), FILES)

        assert findings == []
        assert failure is not None

    def test_a_fenced_response_extracts_normally(self):
        text = "```json\n" + findings_json(a_finding()) + "\n```"

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is None
        assert [f.line for f in findings] == [44]


class TestNoHeuristicSalvage:
    """B114 - the bracket scan never executed in 40 calls, so it does not exist."""

    def test_prose_around_bare_json_is_a_failure_not_a_rescue(self):
        # A bracket scan would "rescue" this. It is deliberately not shipped:
        # the path is unobserved, and its failure mode is silently capturing
        # the wrong span. A loud failure is the better trade.
        text = "Here are the issues I found:\n" + findings_json(a_finding())

        findings, failure = extract_from_run(run_with(text), FILES)

        assert findings == []
        assert failure is not None
        assert "json" in failure.reason.lower()

    def test_prose_outside_a_fence_is_still_extracted(self):
        # The fence is an unambiguous delimiter, so prose around it is safe to
        # discard - unlike a bracket scan, which guesses where the data starts.
        text = "Sure! Here you go:\n```json\n" + findings_json(a_finding()) + "\n```\nHope that helps."

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is None
        assert len(findings) == 1


class TestSchemaValidation:
    """B116 - nothing failed this in 40 calls; it exists to replace a crash."""

    def test_a_well_formed_response_yields_findings(self):
        text = findings_json(
            a_finding(line=44), a_finding(file="store/index.go", line=12, severity="low")
        )

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is None
        assert len(findings) == 2
        assert findings[0].message == "Mutex is copied by value."

    def test_an_empty_array_is_a_clean_review_not_a_failure(self):
        # "No problems found" is a legitimate answer and must not be confused
        # with "the model did not answer".
        findings, failure = extract_from_run(run_with("[]"), FILES)

        assert findings == []
        assert failure is None

    def test_a_non_array_payload_is_rejected(self):
        findings, failure = extract_from_run(run_with('{"file": "x"}'), FILES)

        assert failure is not None
        assert "array" in failure.reason.lower()

    def test_unparseable_text_is_rejected(self):
        findings, failure = extract_from_run(run_with("not json at all"), FILES)

        assert failure is not None

    @pytest.mark.parametrize("missing", ["file", "line", "severity", "message"])
    def test_every_required_field_is_required(self, missing):
        payload = a_finding()
        del payload[missing]

        findings, failure = extract_from_run(run_with(findings_json(payload)), FILES)

        assert failure is not None
        assert missing in failure.reason

    def test_a_severity_outside_the_allowed_set_is_rejected(self):
        text = findings_json(a_finding(severity="catastrophic"))

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is not None
        assert "severity" in failure.reason.lower()

    def test_all_four_allowed_severities_are_accepted(self):
        assert set(ALLOWED_SEVERITIES) == {"critical", "high", "medium", "low"}

        for severity in ALLOWED_SEVERITIES:
            text = findings_json(a_finding(severity=severity))
            findings, failure = extract_from_run(run_with(text), FILES)

            assert failure is None, f"{severity} was rejected"

    def test_a_string_line_number_is_rejected(self):
        text = findings_json(a_finding(line="44"))

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is not None
        assert "line" in failure.reason.lower()

    def test_a_boolean_line_number_is_rejected(self):
        # `isinstance(True, int)` is True in Python, so the obvious check
        # accepts `"line": true` and produces a finding pointing at line 1.
        # The spike's own validator has this hole.
        text = findings_json(a_finding(line=True))

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is not None
        assert "line" in failure.reason.lower()

    def test_a_line_number_below_one_is_rejected(self):
        # A finding at line -5 has nowhere to point. Worse, the merge step
        # groups findings within a few lines of each other, so impossible
        # line numbers cluster together and get presented as a real location.
        text = findings_json(a_finding(line=-5))

        findings, failure = extract_from_run(run_with(text), FILES)

        assert failure is not None
        assert "line" in failure.reason.lower()

    def test_line_zero_is_rejected(self):
        # Files start at line 1. Some tools use 0 to mean "the whole file",
        # but the review prompt never offers that meaning, so a 0 here is a
        # model improvising rather than answering.
        findings, failure = extract_from_run(
            run_with(findings_json(a_finding(line=0))), FILES
        )

        assert failure is not None

    def test_line_one_is_accepted(self):
        findings, failure = extract_from_run(
            run_with(findings_json(a_finding(line=1))), FILES
        )

        assert failure is None
        assert findings[0].line == 1

    def test_an_element_that_is_not_an_object_is_rejected(self):
        findings, failure = extract_from_run(run_with('["just a string"]'), FILES)

        assert failure is not None


class TestFileGuard:
    """B117 - a model naming a file it was not shown describes what it cannot see.

    Recorded as A2 as the weakest behaviour in the spec: it never fired in 40
    calls. It is kept because its failure mode is loud and bounded. These tests
    are written so that striking it is a small, obvious edit.
    """

    def test_a_finding_naming_a_file_outside_the_diff_is_rejected(self):
        text = findings_json(a_finding(file="somewhere/else.go"))

        findings, failure = extract_from_run(run_with(text), FILES)

        assert findings == []
        assert failure is not None
        assert "somewhere/else.go" in failure.reason

    def test_rejecting_one_finding_does_not_discard_its_siblings(self):
        # B115's principle: never silently drop. The good findings survive and
        # the rejection is recorded, rather than the whole response being lost.
        text = findings_json(
            a_finding(file="store/cache.go", line=44),
            a_finding(file="invented/ghost.go", line=7),
            a_finding(file="store/index.go", line=12),
        )

        findings, failure = extract_from_run(run_with(text), FILES)

        assert [f.file for f in findings] == ["store/cache.go", "store/index.go"]
        assert failure is not None
        assert "invented/ghost.go" in failure.reason

    def test_the_guard_is_skipped_when_no_file_list_is_given(self):
        text = findings_json(a_finding(file="anything/at/all.go"))

        findings, failure = extract_from_run(run_with(text), allowed_files=None)

        assert failure is None
        assert len(findings) == 1


class TestFailuresAreLoud:
    """B115 - a discarded response halves the review while the report looks whole."""

    def test_a_failure_records_which_model_and_which_run(self):
        findings, failure = extract_from_run(
            run_with("garbage", model="claude-haiku-4.5", run_index=2), FILES
        )

        assert failure.model == "claude-haiku-4.5"
        assert failure.run_index == 2

    def test_a_failure_keeps_an_excerpt_of_what_was_returned(self):
        findings, failure = extract_from_run(run_with("garbage in here"), FILES)

        assert "garbage" in failure.excerpt

    def test_the_excerpt_is_bounded_so_a_huge_reply_cannot_flood_the_report(self):
        findings, failure = extract_from_run(run_with("x" * 10_000), FILES)

        assert len(failure.excerpt) < 500

    def test_an_unusable_run_is_not_silently_ignored(self):
        timed_out = ModelRun(
            model="gpt-5.4", run_index=1, outcome=RunOutcome.TIMED_OUT,
            response_text="", duration_seconds=1.0, detail="timed out",
        )

        report = extract_all([timed_out], FILES)

        assert report.findings == ()
        assert len(report.failures) == 1
        assert "timed out" in report.failures[0].reason


class TestAcrossRuns:
    """Extraction must preserve which model and run each finding came from."""

    def test_findings_carry_their_model_and_run(self):
        text = findings_json(a_finding())
        runs = [run_with(text, "gpt-5.4", 1), run_with(text, "claude-haiku-4.5", 3)]

        report = extract_all(runs, FILES)

        assert {(f.model, f.run_index) for f in report.findings} == {
            ("gpt-5.4", 1), ("claude-haiku-4.5", 3)
        }

    def test_one_bad_run_does_not_lose_the_good_ones(self):
        runs = [
            run_with(findings_json(a_finding()), "gpt-5.4", 1),
            run_with("garbage", "gpt-5.4", 2),
            run_with(findings_json(a_finding(line=12)), "gpt-5.4", 3),
        ]

        report = extract_all(runs, FILES)

        assert len(report.findings) == 2
        assert len(report.failures) == 1

    def test_a_report_knows_whether_anything_failed(self):
        good = extract_all([run_with(findings_json(a_finding()))], FILES)
        bad = extract_all([run_with("garbage")], FILES)

        assert good.has_failures is False
        assert bad.has_failures is True

    def test_duplicate_findings_are_preserved_for_the_merge_step_to_count(self):
        # Extraction must not deduplicate: repetition frequency is the
        # confidence signal the whole phase is built on (B132).
        text = findings_json(a_finding())
        runs = [run_with(text, "gpt-5.4", i) for i in (1, 2, 3)]

        report = extract_all(runs, FILES)

        assert len(report.findings) == 3
