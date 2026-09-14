"""Behaviour tests for `atom poc list` (B58-B61).

Written before index.py exists. The first run must fail on import -- RED.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.index import list_spikes


def _make_spike(poc_root: Path, slug: str, *, question: str | None = None, with_go_mod: bool = True) -> Path:
    directory = poc_root / slug
    directory.mkdir(parents=True)
    if with_go_mod:
        (directory / "go.mod").write_text(f"module spike/{slug}\n\ngo 1.23.4\n", encoding="utf-8")
    if question is not None:
        (directory / "README.md").write_text(
            f"# Spike: {slug}\n\n**Created:** 2026-01-01\n\n## Question\n\n{question}\n\n## Method\n",
            encoding="utf-8",
        )
    return directory


@pytest.fixture
def poc_root(tmp_path: Path) -> Path:
    root = tmp_path / "poc"
    root.mkdir()
    return root


def test_lists_every_spike(poc_root: Path) -> None:
    """B58: each direct child of poc/ is a spike."""

    _make_spike(poc_root, "alpha", question="First question?")
    _make_spike(poc_root, "beta", question="Second question?")

    assert sorted(summary.slug for summary in list_spikes(poc_root)) == ["alpha", "beta"]


def test_ignores_nested_directories(poc_root: Path) -> None:
    """B58: direct children only -- consistent with B19, confirmed in the Phase 1 gate.

    A spike's own subpackages belong to that spike. Treating them as spikes
    would report one investigation as several.
    """

    spike = _make_spike(poc_root, "alpha", question="A question?")
    (spike / "internal").mkdir()
    (spike / "internal" / "go.mod").write_text("module spike/alpha/internal\n", encoding="utf-8")

    assert [summary.slug for summary in list_spikes(poc_root)] == ["alpha"]


def test_reads_the_question_from_the_readme(poc_root: Path) -> None:
    """B59: the question is the only thing that makes a list of slugs useful."""

    _make_spike(poc_root, "alpha", question="Does streaming beat buffering?")

    assert list_spikes(poc_root)[0].question == "Does streaming beat buffering?"


def test_question_is_none_when_there_is_no_readme(poc_root: Path) -> None:
    """B59: a hand-made spike is still a spike; absence is reported, not invented."""

    _make_spike(poc_root, "alpha")

    assert list_spikes(poc_root)[0].question is None


def test_question_is_none_when_the_readme_has_no_question_section(poc_root: Path) -> None:
    """B59: a README missing its question must not yield a misleading first line."""

    spike = _make_spike(poc_root, "alpha")
    (spike / "README.md").write_text("# Spike: alpha\n\nSome notes.\n", encoding="utf-8")

    assert list_spikes(poc_root)[0].question is None


def test_reports_a_spike_that_has_a_go_mod(poc_root: Path) -> None:
    """B60: the healthy case."""

    _make_spike(poc_root, "alpha", question="A question?")

    assert list_spikes(poc_root)[0].has_go_mod is True


def test_flags_a_spike_missing_its_go_mod(poc_root: Path) -> None:
    """B60: the one state that breaks the parent build.

    `atom check` already fails on this (B20). `atom poc list` must show it too,
    because list is where a developer looks when something is wrong.
    """

    _make_spike(poc_root, "broken", with_go_mod=False)

    assert list_spikes(poc_root)[0].has_go_mod is False


def test_missing_poc_root_is_an_empty_list_not_an_error(tmp_path: Path) -> None:
    """B61: a repo with no spikes yet is normal, not broken."""

    assert list_spikes(tmp_path / "does-not-exist") == []


def test_empty_poc_root_is_an_empty_list(poc_root: Path) -> None:
    """B61: same reasoning -- nothing to report is not a failure."""

    assert list_spikes(poc_root) == []


def test_ignores_loose_files_in_poc_root(poc_root: Path) -> None:
    """A README at the top of poc/ is documentation, not a spike."""

    _make_spike(poc_root, "alpha", question="A question?")
    (poc_root / "README.md").write_text("These are the spikes.\n", encoding="utf-8")

    assert [summary.slug for summary in list_spikes(poc_root)] == ["alpha"]


def test_results_are_sorted_for_stable_output(poc_root: Path) -> None:
    """Unstable ordering makes output diffs noisy and CI comparisons useless."""

    for slug in ("zulu", "alpha", "mike"):
        _make_spike(poc_root, slug, question="A question?")

    assert [summary.slug for summary in list_spikes(poc_root)] == ["alpha", "mike", "zulu"]


def test_multiline_question_is_collapsed_to_one_line(poc_root: Path) -> None:
    """A question spanning lines must still render as a single table row."""

    spike = _make_spike(poc_root, "alpha")
    (spike / "README.md").write_text(
        "# Spike: alpha\n\n## Question\n\nDoes streaming beat\nbuffering for large payloads?\n\n## Method\n",
        encoding="utf-8",
    )

    question = list_spikes(poc_root)[0].question
    assert question is not None
    assert "\n" not in question


def test_question_skips_the_blockquote_guidance(poc_root: Path) -> None:
    """The scaffolded README carries a blockquote tip; it is not the question."""

    spike = _make_spike(poc_root, "alpha")
    (spike / "README.md").write_text(
        "# Spike: alpha\n\n## Question\n\nReal question?\n\n> A good spike question is falsifiable.\n\n## Method\n",
        encoding="utf-8",
    )

    assert list_spikes(poc_root)[0].question == "Real question?"
