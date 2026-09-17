"""Behaviour tests for the merge model (B118-B124).

Every behaviour here comes from the agreement analysis rather than from
intuition about how findings ought to combine, so the tests are written against
the shapes that analysis actually observed: the same defect reported at
adjacent lines, the same model disagreeing with itself on severity, and eight
noise findings that appeared in five runs or fewer.
"""

from __future__ import annotations

import random

import pytest

from atom.extract import ALLOWED_SEVERITIES, Finding
from atom.merge import (
    DEFAULT_PROXIMITY_WINDOW,
    MergedFinding,
    merge_findings,
)

RUNS = {"gpt-5.4": 3, "claude-haiku-4.5": 3}


def finding(
    line: int,
    model: str = "gpt-5.4",
    run_index: int = 1,
    severity: str = "high",
    message: str = "A problem.",
    file: str = "store/cache.go",
) -> Finding:
    return Finding(
        file=file, line=line, severity=severity,
        message=message, model=model, run_index=run_index,
    )


class TestGroupingByProximity:
    """B118 - exact line matching would report one defect as several."""

    def test_the_default_window_is_three_lines(self):
        # P4-5. Derived from near misses in one fixture diff: honest
        # provenance, not a tuned value.
        assert DEFAULT_PROXIMITY_WINDOW == 3

    def test_identical_lines_merge(self):
        merged = merge_findings(
            [finding(44, "gpt-5.4", 1), finding(44, "claude-haiku-4.5", 1)], RUNS
        )

        assert len(merged) == 1

    def test_nearby_lines_merge(self):
        # The measured case: Haiku's 34-35 within three of gpt-5.4's 37, and
        # gpt-5.4 itself reporting one defect at both 36 and 37.
        merged = merge_findings(
            [finding(37, "gpt-5.4", 1), finding(34, "claude-haiku-4.5", 1)], RUNS
        )

        assert len(merged) == 1

    def test_lines_beyond_the_window_stay_separate(self):
        merged = merge_findings(
            [finding(10, "gpt-5.4", 1), finding(20, "gpt-5.4", 2)], RUNS
        )

        assert len(merged) == 2

    def test_the_window_is_configurable(self):
        pair = [finding(10, "gpt-5.4", 1), finding(18, "claude-haiku-4.5", 1)]

        assert len(merge_findings(pair, RUNS, window=3)) == 2
        assert len(merge_findings(pair, RUNS, window=10)) == 1

    def test_the_same_line_in_different_files_never_merges(self):
        merged = merge_findings(
            [finding(44, file="store/cache.go"), finding(44, file="store/index.go")],
            RUNS,
        )

        assert len(merged) == 2

    def test_a_group_never_spans_more_than_the_window(self):
        # Proximity is not transitive: 10~12 and 12~14 under a window of 3,
        # but 10 and 14 are four apart. Chaining them would produce a group
        # wider than the window the developer asked for, and with enough
        # findings a single group could span an entire file - which is
        # precisely the "merges two genuinely different defects" error B119
        # warns about, arriving without anyone choosing it.
        chain = [finding(line, "gpt-5.4", 1) for line in (10, 12, 14, 16, 18)]

        merged = merge_findings(chain, RUNS, window=3)

        for group in merged:
            assert max(group.lines) - min(group.lines) <= 3

    def test_grouping_does_not_depend_on_the_order_findings_arrive_in(self):
        findings = [finding(line, "gpt-5.4", 1) for line in (10, 12, 14, 30, 31)]
        expected = [
            (group.file, group.lines) for group in merge_findings(findings, RUNS)
        ]

        shuffled = list(findings)
        random.Random(7).shuffle(shuffled)

        assert [
            (group.file, group.lines) for group in merge_findings(shuffled, RUNS)
        ] == expected


class TestNothingIsDiscarded:
    """B120 - a merged finding carries every contributing message."""

    def test_every_message_survives_the_merge(self):
        merged = merge_findings(
            [
                finding(44, "gpt-5.4", 1, message="Mutex copied by value."),
                finding(45, "claude-haiku-4.5", 1, message="Lock is not held here."),
            ],
            RUNS,
        )

        texts = [m.message for m in merged[0].messages]
        assert "Mutex copied by value." in texts
        assert "Lock is not held here." in texts

    def test_each_message_is_attributed_to_its_model_and_run(self):
        merged = merge_findings(
            [finding(44, "gpt-5.4", 2, message="Only one.")], RUNS
        )

        message = merged[0].messages[0]
        assert (message.model, message.run_index) == ("gpt-5.4", 2)

    def test_each_message_keeps_the_line_it_was_reported_at(self):
        # The group has one representative line, but a developer looking at a
        # merged finding needs to know the models named different lines.
        merged = merge_findings(
            [finding(36, "gpt-5.4", 1), finding(37, "gpt-5.4", 2)], RUNS
        )

        assert sorted(m.line for m in merged[0].messages) == [36, 37]


class TestAgreement:
    """B121, B122 - the single most useful output of merging."""

    def test_a_merged_finding_names_the_models_that_reported_it(self):
        merged = merge_findings(
            [finding(44, "gpt-5.4", 1), finding(44, "claude-haiku-4.5", 1)], RUNS
        )

        assert {a.model for a in merged[0].agreement} == {"gpt-5.4", "claude-haiku-4.5"}

    def test_agreement_counts_how_many_runs_of_each_model_reported_it(self):
        # The measured separation: real defects appeared in nearly every run,
        # noise in five of twenty or fewer.
        findings = [finding(44, "gpt-5.4", i) for i in (1, 2, 3)]
        findings.append(finding(44, "claude-haiku-4.5", 1))

        merged = merge_findings(findings, RUNS)
        by_model = {a.model: a for a in merged[0].agreement}

        assert by_model["gpt-5.4"].runs_reporting == 3
        assert by_model["gpt-5.4"].runs_total == 3
        assert by_model["claude-haiku-4.5"].runs_reporting == 1
        assert by_model["claude-haiku-4.5"].runs_total == 3

    def test_one_run_reporting_a_line_twice_counts_once(self):
        # Otherwise a single chatty run could manufacture the appearance of
        # corroboration, which is the number the whole phase rests on.
        findings = [
            finding(44, "gpt-5.4", 1, message="First observation."),
            finding(45, "gpt-5.4", 1, message="Second observation, same run."),
        ]

        merged = merge_findings(findings, RUNS)
        by_model = {a.model: a for a in merged[0].agreement}

        assert by_model["gpt-5.4"].runs_reporting == 1
        assert len(merged[0].messages) == 2  # but both messages are kept

    def test_a_single_model_finding_is_reported_not_suppressed(self):
        # B122: suppressing it would mean the tool quietly decides a real bug
        # is noise, on the evidence of one fixture diff.
        merged = merge_findings([finding(44, "gpt-5.4", 1)], RUNS)

        assert len(merged) == 1
        assert merged[0].model_count == 1
        assert merged[0].is_corroborated is False

    def test_a_finding_from_both_models_is_marked_corroborated(self):
        merged = merge_findings(
            [finding(44, "gpt-5.4", 1), finding(44, "claude-haiku-4.5", 1)], RUNS
        )

        assert merged[0].is_corroborated is True


class TestSeverity:
    """B123, B124 - severity is what the models said, not a verdict."""

    def test_disagreeing_severities_are_all_preserved(self):
        # Measured: the same model gave one line `high` on 18 runs and
        # `medium` on 2, and the two models disagreed on all four real defects.
        merged = merge_findings(
            [
                finding(44, "gpt-5.4", 1, severity="high"),
                finding(44, "claude-haiku-4.5", 1, severity="critical"),
            ],
            RUNS,
        )

        assert set(merged[0].severities) == {"high", "critical"}

    def test_severity_is_not_collapsed_into_one_verdict(self):
        merged = merge_findings(
            [
                finding(44, "gpt-5.4", 1, severity="low"),
                finding(44, "gpt-5.4", 2, severity="critical"),
            ],
            RUNS,
        )

        assert merged[0].has_severity_disagreement is True

    def test_agreement_on_severity_is_not_reported_as_disagreement(self):
        merged = merge_findings(
            [
                finding(44, "gpt-5.4", 1, severity="high"),
                finding(44, "claude-haiku-4.5", 1, severity="high"),
            ],
            RUNS,
        )

        assert merged[0].has_severity_disagreement is False

    def test_the_highest_claimed_severity_is_available_for_ordering(self):
        merged = merge_findings(
            [
                finding(44, "gpt-5.4", 1, severity="low"),
                finding(44, "claude-haiku-4.5", 1, severity="critical"),
            ],
            RUNS,
        )

        assert merged[0].highest_severity == "critical"


class TestOrdering:
    """B124 - the most alarming claim is never buried."""

    def test_findings_are_ordered_by_highest_severity(self):
        findings = [
            finding(10, severity="low"),
            finding(50, severity="critical"),
            finding(30, severity="medium"),
            finding(70, severity="high"),
        ]

        merged = merge_findings(findings, RUNS)

        assert [m.highest_severity for m in merged] == [
            "critical", "high", "medium", "low"
        ]

    def test_one_model_calling_it_critical_lifts_the_whole_finding(self):
        findings = [
            finding(10, "gpt-5.4", 1, severity="high"),
            finding(50, "gpt-5.4", 1, severity="low"),
            finding(50, "claude-haiku-4.5", 1, severity="critical"),
        ]

        merged = merge_findings(findings, RUNS)

        assert merged[0].line == 50

    def test_equal_severities_are_ordered_predictably(self):
        findings = [
            finding(80, file="store/index.go"),
            finding(10, file="store/index.go"),
            finding(40, file="store/cache.go"),
        ]

        merged = merge_findings(findings, RUNS)

        assert [(m.file, m.line) for m in merged] == [
            ("store/cache.go", 40),
            ("store/index.go", 10),
            ("store/index.go", 80),
        ]


class TestKnownLimits:
    """Behaviour that is wrong but known, pinned so it cannot drift silently.

    These are not aspirations. They record what the tool measurably does on the
    real spike responses, so that a future change to the window or the grouping
    rule has to confront the evidence rather than rediscover it.
    """

    def test_drift_lets_a_group_reach_further_than_the_window(self):
        # Measured on the 20 real spike responses. Both models described the
        # ignored os.Create error at lines 42, 43 and 44 on different runs --
        # ordinary line drift. The lowest of those anchors the group, so a
        # window of 3 reaches line 45, which is a *different* planted defect
        # (Export iterating without the lock).
        #
        # The effective reach past the true defect is therefore window + drift,
        # not window. No window value fixes this: shrinking it to 2 would split
        # the genuine 33-36 cluster instead. Proximity merging cannot separate
        # defects this close together.
        #
        # What saves it is B120 -- every message survives and stays attributed,
        # so the developer still reads both defects. Only the count is wrong.
        drifted = [
            finding(42, "gpt-5.4", 1, message="os.Create error ignored."),
            finding(43, "claude-haiku-4.5", 1, message="os.Create error ignored."),
            finding(44, "gpt-5.4", 2, message="os.Create error ignored."),
            finding(45, "claude-haiku-4.5", 2, message="Export reads without the lock."),
        ]

        merged = merge_findings(drifted, RUNS)

        assert len(merged) == 1, "two distinct defects merge; see finding #9"
        assert merged[0].lines == (42, 43, 44, 45)
        # The second defect is still readable, which is why this is tolerable.
        assert any(
            "Export" in message.message for message in merged[0].messages
        )


class TestEdges:
    def test_severity_ordering_depends_on_the_allowed_list_staying_ordered(self):
        # merge ranks severity by position in ALLOWED_SEVERITIES. If that were
        # ever changed to a set, string hash randomisation would reorder every
        # report between processes and nothing else here would catch it.
        assert ALLOWED_SEVERITIES == ("critical", "high", "medium", "low")

    def test_agreement_renders_as_the_fraction_a_report_shows(self):
        # A bare count cannot be read: "2 runs" means something very different
        # out of 3 than out of 20.
        merged = merge_findings([finding(44, "gpt-5.4", 1)], RUNS)

        assert merged[0].agreement[0].fraction == "1/3"

    def test_no_findings_merge_to_nothing(self):
        assert merge_findings([], RUNS) == ()

    def test_a_model_absent_from_the_run_counts_is_rejected(self):
        # A denominator that silently defaults would make the confidence
        # fraction wrong in the one direction nobody would notice: too high.
        with pytest.raises(KeyError):
            merge_findings([finding(44, "unknown-model", 1)], RUNS)

    def test_a_negative_window_is_rejected(self):
        with pytest.raises(ValueError, match="window"):
            merge_findings([finding(44)], RUNS, window=-1)

    def test_a_zero_window_means_exact_line_matching(self):
        merged = merge_findings(
            [finding(44, "gpt-5.4", 1), finding(45, "claude-haiku-4.5", 1)],
            RUNS, window=0,
        )

        assert len(merged) == 2


class TestImpossibleAgreementIsRefused:
    """The agreement fraction is the number this whole phase rests on.

    B121 and B122 make corroboration the signal a developer is asked to trust,
    and nothing else in the output distinguishes a real defect from noise. A
    report that prints "1/0" or "5/3" does not just show one wrong number; it
    tells the reader that none of the numbers can be relied on. So a fraction
    that cannot exist is refused at the point it would be constructed, rather
    than rendered and explained away later (A8).
    """

    def test_a_model_with_no_runs_cannot_have_reported_anything(self):
        with pytest.raises(ValueError, match="runs"):
            merge_findings([finding(44)], {"gpt-5.4": 0})

    def test_a_negative_run_count_is_rejected(self):
        with pytest.raises(ValueError, match="runs"):
            merge_findings([finding(44)], {"gpt-5.4": -1})

    def test_more_reporting_runs_than_runs_total_is_rejected(self):
        # Reachable through an ordinary caller mistake: passing the configured
        # --runs while handing over findings from a different, longer review.
        five_runs = [finding(44, "gpt-5.4", run) for run in range(1, 6)]

        with pytest.raises(ValueError, match="3"):
            merge_findings(five_runs, {"gpt-5.4": 3})

    def test_an_unrecognised_severity_names_what_is_allowed(self):
        # extract already guarantees valid severities, so this only fires for a
        # caller bug -- but a bare KeyError gives whoever hits it nothing.
        with pytest.raises(ValueError, match="critical"):
            merge_findings([finding(44, severity="catastrophic")], RUNS)
