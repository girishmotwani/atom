"""Tests for the style rules that reach the reviewing models.

The rules lived in a markdown file for a long time and were delivered to
nobody. These tests exist mostly to stop that happening again: the point of
the module is that its text ends up inside the prompt, so that is what is
asserted.
"""

from __future__ import annotations

import re

from atom.diff import CapturedDiff, DiffRequest, DiffSource
from atom.invoke import InvocationReport, ModelAvailability
from atom.review import run_review
from atom.style import STYLE_RULES, style_rules_block
from tests.conftest import FakeRunner


def _fake_capture_diff(request, runner, working_directory):
    """Stand in for git so these tests only exercise prompt assembly."""
    return CapturedDiff(
        text="diff --git a/a.go b/a.go\n+++ b/a.go\n@@ -0,0 +1 @@\n+package main\n",
        request=request,
    )


def _prompt_capturing_invoker(captured: list[str]):
    """Return a fake `invoke_models` that records the prompt and answers nothing."""

    def fake_invoke_models(
        models,
        prompt,
        runner,
        working_directory,
        runs,
        concurrency,
        disable_mcp_servers=(),
        *, fixed_evidence=False,
    ):
        captured.append(prompt)
        return InvocationReport(
            models=tuple(models),
            runs_requested=runs,
            runs=(),
            availability=tuple(ModelAvailability(model, True, "") for model in models),
        )

    return fake_invoke_models


def _run_and_capture_prompt(tmp_path, monkeypatch, **kwargs) -> str:
    """Run a review with git and the models faked, and return the prompt sent."""
    captured: list[str] = []
    monkeypatch.setattr("atom.review.capture_diff", _fake_capture_diff)
    monkeypatch.setattr(
        "atom.review.invoke_models", _prompt_capturing_invoker(captured)
    )

    run_review(
        request=DiffRequest(DiffSource.WORKING, None),
        models=("gpt-5.4",),
        runner=FakeRunner({}),
        working_directory=tmp_path,
        runs=1,
        concurrency=1,
        **kwargs,
    )

    return captured[0]


def test_style_rules_reach_the_model_by_default(tmp_path, monkeypatch):
    """The whole point of the module: the rules are in the prompt, unedited."""
    prompt = _run_and_capture_prompt(tmp_path, monkeypatch)

    assert style_rules_block() in prompt


def test_style_rules_can_be_switched_off_for_measurement(tmp_path, monkeypatch):
    """Comparing delivered against not-delivered needs a genuine off state."""
    prompt = _run_and_capture_prompt(tmp_path, monkeypatch, include_style_rules=False)

    assert style_rules_block() not in prompt
    assert "no tool can check" not in prompt


def test_style_rules_sit_before_the_output_format_instruction(tmp_path, monkeypatch):
    """Format compliance was measured with the schema last; keep it last.

    The JSON schema and the "nothing else" line are the wording that produced
    the measured compliance figures, and they were measured sitting next to
    the diff. Anything inserted between them would be a change to the part of
    the prompt that is known to move format compliance.
    """
    prompt = _run_and_capture_prompt(tmp_path, monkeypatch)

    assert prompt.index("no tool can check") < prompt.index("Respond with a JSON array")


def test_every_rule_is_numbered_and_present():
    """Seven was chosen deliberately; a silent eighth or a lost rule should fail."""
    numbered = re.findall(r"^(\d+)\. ", STYLE_RULES, flags=re.MULTILINE)

    assert numbered == ["1", "2", "3", "4", "5", "6", "7"]


def test_no_rule_is_phrased_as_a_preference():
    """Preference-phrased rules were reported 0 of 3 even when handed over.

    This is the one finding the list is built on, so it is worth a test that
    fails loudly if someone later softens a rule back into advice.
    """
    lowered = STYLE_RULES.lower()

    for banned in ("prefer ", "should ", "try to ", "avoid "):
        assert banned not in lowered, f"rule text fell back to preference wording: {banned!r}"
