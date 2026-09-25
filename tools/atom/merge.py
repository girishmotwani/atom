"""Combine findings from many runs into one list, without losing what differed.

This is the part of `atom review` that the Phase 4 evidence changed most. The
naive design — collect findings, deduplicate identical ones, print a list — is
wrong in three separate ways that the agreement analysis made visible:

*   **The same defect is not reported at the same line.** One model reported a
    single problem at line 36 on some runs and line 37 on others; another
    model's lines 34-35 described the same defect as the first model's line 37.
    Exact matching reports one defect as four.

*   **Repetition is the confidence signal.** Across 20 runs, the four planted
    defects were reported by both models on nearly every run, while eight noise
    findings appeared in five runs or fewer and never by more than one model.
    Nothing else in the output separates them — not severity, not wording. A
    flat list throws that signal away.

*   **Severity is not a fact.** The same model gave the same line `high` on 18
    runs and `medium` on 2. The two models disagreed on all four real defects.
    Presenting one severity as *the* severity would be inventing agreement that
    the measurement says does not exist.

So merging groups by proximity (B118), counts agreement (B121), keeps every
message (B120), and reports severity as a set of claims rather than a verdict
(B123).

See `specs/atom-cli/phase-04-review/design-spec.md` for B118-B124.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from atom.extract import ALLOWED_SEVERITIES, Finding

# Three lines, per P4-5. Derived from the near misses observed in a single
# fixture diff, which is honest provenance rather than a tuned value. The
# window trades two opposite errors that are both invisible in the output: too
# wide merges genuinely different defects, too narrow reports one defect
# several times.
DEFAULT_PROXIMITY_WINDOW = 3

# Most severe first, so index order is also ordering priority.
_SEVERITY_RANK = {name: rank for rank, name in enumerate(ALLOWED_SEVERITIES)}


@dataclass(frozen=True)
class AttributedMessage:
    """One model's description of a problem, kept whole and kept attributed."""

    model: str
    run_index: int
    line: int
    severity: str
    message: str


@dataclass(frozen=True)
class ModelAgreement:
    """How many of one model's runs reported a given finding.

    Both halves of the fraction are stored. A count without its denominator
    cannot be read: "reported by 2 runs" means something very different when
    three runs completed than when twenty did.
    """

    model: str
    runs_reporting: int
    runs_total: int

    @property
    def fraction(self) -> str:
        """Render the agreement as the fraction a report should show."""

        return f"{self.runs_reporting}/{self.runs_total}"


@dataclass(frozen=True)
class MergedFinding:
    """One problem, as described by every run that reported it."""

    file: str
    line: int
    lines: tuple[int, ...]
    messages: tuple[AttributedMessage, ...]
    agreement: tuple[ModelAgreement, ...]

    @property
    def severities(self) -> tuple[str, ...]:
        """Return the distinct severities claimed, most severe first."""

        distinct = {message.severity for message in self.messages}
        return tuple(sorted(distinct, key=lambda name: _SEVERITY_RANK[name]))

    @property
    def highest_severity(self) -> str:
        """Return the most severe claim any model made (B124).

        Used for ordering only. It deliberately does not overwrite the
        individual claims, which stay visible under `severities`.
        """

        return self.severities[0]

    @property
    def has_severity_disagreement(self) -> bool:
        """Return true when the models did not agree on how bad this is."""

        return len(self.severities) > 1

    @property
    def model_count(self) -> int:
        """Return how many distinct models reported this finding."""

        return len(self.agreement)

    @property
    def is_corroborated(self) -> bool:
        """Return true when two models reported the same *line* (A21).

        On the measured data cross-model agreement separated the four real
        defects from the eight noise findings. It is a signal to display,
        never a filter — see B122.

        The line, not the group, is the unit. Proximity grouping is loose by
        design, so one entry can hold two unrelated defects a line apart;
        counting distinct models across the group would then report an
        agreement neither model expressed.
        """

        return any(len(models) > 1 for models in self._models_by_line().values())

    @property
    def has_nearby_multi_model_reports(self) -> bool:
        """Return true when several models reported *near* each other (A22).

        This is the weaker companion to `is_corroborated`, and the two are
        deliberately disjoint: a group where several models landed on
        different lines is reported here instead of being either claimed as
        agreement or silently dropped.

        Why it cannot be folded into `is_corroborated`: two models a line
        apart may be describing one defect (the shape the original analysis
        observed most often) or two unrelated ones. Line numbers cannot tell
        those apart, so a single boolean must be wrong in one direction. This
        reports what was actually measured — several models, nearby lines —
        and leaves the judgement to the reader.
        """

        if self.is_corroborated:
            return False

        return self.model_count > 1

    def _models_by_line(self) -> dict[int, set[str]]:
        """Group the contributing models by the line each one cited."""

        models_by_line: dict[int, set[str]] = {}
        for message in self.messages:
            models_by_line.setdefault(message.line, set()).add(message.model)

        return models_by_line


def merge_findings(
    findings: Iterable[Finding],
    runs_per_model: Mapping[str, int],
    window: int = DEFAULT_PROXIMITY_WINDOW,
) -> tuple[MergedFinding, ...]:
    """Group nearby findings per file and summarise who reported what.

    `runs_per_model` supplies the denominator for every agreement fraction. It
    is required rather than inferred: counting only the runs that *appear in
    the findings* would silently omit runs that reported nothing, inflating
    every fraction in the one direction nobody would question.
    """

    if window < 0:
        raise ValueError(f"window must be zero or positive, got {window}.")

    for model, total in runs_per_model.items():
        if total < 0:
            raise ValueError(
                f"Model {model!r} is recorded as having completed {total} runs, "
                "which is not a possible number of runs."
            )

    collected = list(findings)
    for item in collected:
        if item.model not in runs_per_model:
            raise KeyError(
                f"No run count given for model {item.model!r}; "
                "agreement fractions would be wrong."
            )
        if item.severity not in _SEVERITY_RANK:
            raise ValueError(
                f"Unknown severity {item.severity!r}; "
                f"expected one of {', '.join(ALLOWED_SEVERITIES)}."
            )

    groups: list[list[Finding]] = []
    for file_path in sorted({item.file for item in collected}):
        in_file = [item for item in collected if item.file == file_path]
        groups.extend(_group_by_proximity(in_file, window))

    merged = [_summarise(group, runs_per_model) for group in groups]

    # Most severe first (B124), then a stable, obvious tiebreak so that two
    # runs of the same review never disagree about ordering.
    merged.sort(key=lambda item: (_SEVERITY_RANK[item.highest_severity], item.file, item.line))

    return tuple(merged)


def _group_by_proximity(findings: Sequence[Finding], window: int) -> list[list[Finding]]:
    """Group findings in one file into clusters no wider than `window`.

    Proximity is **not** transitive, and that matters. With a window of 3,
    lines 10 and 12 are near, 12 and 14 are near, but 10 and 14 are not. A
    chaining implementation would still put all three in one group, and with
    findings on consecutive lines the chain can grow without limit — a single
    group could span an entire file while every adjacent pair looks correct.

    That is exactly the "merges two genuinely different defects" error B119
    warns about, and it would arrive without anyone having chosen it. So each
    group is anchored on its lowest line and admits only findings within
    `window` of that anchor, which bounds every group to the width the
    developer actually asked for.
    """

    ordered = sorted(findings, key=lambda item: (item.line, item.model, item.run_index))
    groups: list[list[Finding]] = []

    for item in ordered:
        if groups and item.line - groups[-1][0].line <= window:
            groups[-1].append(item)
        else:
            groups.append([item])

    return groups


def _summarise(
    group: Sequence[Finding], runs_per_model: Mapping[str, int]
) -> MergedFinding:
    """Turn one cluster of findings into a single reportable finding."""

    messages = tuple(
        AttributedMessage(
            model=item.model,
            run_index=item.run_index,
            line=item.line,
            severity=item.severity,
            message=item.message,
        )
        for item in group
    )

    # Count *distinct runs*, not contributions. A single run that mentions the
    # same problem twice must not look like two runs agreeing — that number is
    # the one the whole phase rests on.
    reporting_runs: dict[str, set[int]] = {}
    for item in group:
        reporting_runs.setdefault(item.model, set()).add(item.run_index)

    agreement = tuple(
        ModelAgreement(
            model=model,
            runs_reporting=len(run_indices),
            runs_total=runs_per_model[model],
        )
        for model, run_indices in sorted(reporting_runs.items())
    )

    for entry in agreement:
        if entry.runs_reporting > entry.runs_total:
            # Usually means the caller passed the configured --runs alongside
            # findings from a different, longer review. Rendering "5/3" would
            # discredit every other number in the report.
            raise ValueError(
                f"Model {entry.model!r} reported this finding on "
                f"{entry.runs_reporting} runs but only {entry.runs_total} "
                "were recorded as completed."
            )

    lines = tuple(sorted({item.line for item in group}))

    return MergedFinding(
        file=group[0].file,
        line=lines[0],
        lines=lines,
        messages=messages,
        agreement=agreement,
    )
