"""Tests that Atom asks the *author* for comments, not only the reviewer.

The style rules in `atom.style` reach a model only during `atom review`, which
runs after the Go code already exists. Nothing in the BUILD beat asked for a
comment, so an implementation could satisfy every TDD instruction -- failing
test first, minimum code, green suite -- and still arrive with its reasoning
undocumented. These tests pin the instruction that closes that gap.

They assert the *presence of an instruction*, not the quality of any generated
comment. No tool in Atom's gate can judge whether a comment is worth reading,
so what is enforceable here is that the author is asked at all, in both the
copy this repository edits and the copy an onboarded repository receives.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.style import STYLE_RULES

REPOSITORY = Path(__file__).resolve().parents[2]

TDD_SKILL_COPIES = (
    REPOSITORY / "skills" / "tdd" / "SKILL.md",
    REPOSITORY / "tools" / "atom" / "assets" / "skills" / "tdd" / "SKILL.md",
)


@pytest.mark.parametrize(
    "skill_path", TDD_SKILL_COPIES, ids=("source", "packaged")
)
def test_tdd_asks_the_author_for_a_comment_pass(skill_path: Path) -> None:
    """The BUILD beat names commenting as work, not as optional polish."""
    skill = skill_path.read_text(encoding="utf-8")

    assert "Comment pass" in skill
    assert "exported symbol" in skill


@pytest.mark.parametrize(
    "skill_path", TDD_SKILL_COPIES, ids=("source", "packaged")
)
def test_tdd_scopes_comments_to_what_the_code_cannot_say(skill_path: Path) -> None:
    """Both halves of the rule are present: explain reasoning, skip the obvious.

    Asking for comments without the second half produces narration of
    assignments, which rots into a lie and is worse than silence. A test that
    checked only the first half would pass while the instruction was harmful.
    """
    skill = skill_path.read_text(encoding="utf-8")

    assert "non-obvious" in skill
    assert "Obvious code stays uncommented" in skill


@pytest.mark.parametrize(
    "skill_path", TDD_SKILL_COPIES, ids=("source", "packaged")
)
def test_the_comment_pass_is_in_the_completion_checklist(skill_path: Path) -> None:
    """The checklist is what the agent self-audits; a rule absent from it is advice."""
    skill = skill_path.read_text(encoding="utf-8")

    checklist = skill.split("## Done when", 1)[1]

    assert "doc comment" in checklist
    assert "non-obvious" in checklist


def test_the_two_tdd_skill_copies_stay_identical() -> None:
    """An onboarded repository reads the packaged copy, so drift silently
    reverts this instruction for every user while the source copy looks fixed."""
    source, packaged = (path.read_text(encoding="utf-8") for path in TDD_SKILL_COPIES)

    assert source == packaged


def test_the_review_rule_names_a_missing_comment_as_the_defect() -> None:
    """Rule 7 previously ended "or say nothing", which licensed the omission.

    A reviewer reading that sentence flags a stale comment and never flags an
    absent one, which is the failure this change exists to correct.
    """
    assert "or say nothing" not in STYLE_RULES
    assert "no doc comment" in STYLE_RULES or "carrying no doc comment" in STYLE_RULES
