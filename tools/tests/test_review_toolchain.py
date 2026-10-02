"""Tests for the toolchain gate that now precedes model review."""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.diff import CapturedDiff, DiffRequest, DiffSource
from atom.extract import ExtractionReport
from atom.gates import GateResult, GateStatus
from atom.invoke import InvocationReport, ModelAvailability
from atom.review import REVIEW_PROMPT, ToolchainGateFailed, run_review
from atom.runner import CommandOutcome
from tests.conftest import FakeRunner, command_result


ORIGINAL_REVIEW_PROMPT = """You are reviewing a Go diff. Report real problems only.

Respond with a JSON array. Every element must be an object with exactly these keys:
  "file": string, the path from the diff
  "line": integer, the line number in the new file
  "severity": one of "critical", "high", "medium", "low"
  "message": string, one sentence describing the problem

Respond with the JSON array and nothing else. No prose, no explanation, no headings.

Here is the diff:

{diff}
"""


def test_empty_toolchain_placeholder_preserves_original_prompt_bytes():
    """The measured review prompt must not drift when no evidence is inserted."""
    assert REVIEW_PROMPT.format(toolchain="", diff="{diff}") == ORIGINAL_REVIEW_PROMPT


def test_run_review_blocks_before_models_when_required_gate_fails(tmp_path):
    """A tree that fails required gates is not ready to spend model calls."""
    (tmp_path / "go.mod").write_text("module example.com/toolchain\n", encoding="utf-8")
    build = ("go", "build", "./...")
    runner = FakeRunner({
        build: command_result(build, tmp_path, exit_code=1, stderr="compile failed"),
        ("go", "vet", "./..."): command_result(("go", "vet", "./..."), tmp_path),
        ("gofmt", "-l", "."): command_result(("gofmt", "-l", "."), tmp_path),
        ("go", "test", "./..."): command_result(("go", "test", "./..."), tmp_path, stdout="ok example 0.1s\n"),
        ("go", "test", "-race", "./..."): command_result(("go", "test", "-race", "./..."), tmp_path, stdout="ok example 0.1s\n"),
        ("staticcheck", "./..."): command_result(("staticcheck", "./..."), tmp_path),
        ("errcheck", "./..."): command_result(("errcheck", "./..."), tmp_path),
        ("govulncheck", "./..."): command_result(("govulncheck", "./..."), tmp_path),
    })

    with pytest.raises(ToolchainGateFailed) as raised:
        run_review(
            request=DiffRequest(DiffSource.WORKING, None),
            models=("gpt-5.4",),
            runner=runner,
            working_directory=tmp_path,
            runs=1,
            concurrency=1,
        )

    assert raised.value.failures[0].name == "build"
    assert all(command[0][0] != "copilot" for command in runner.calls)


def test_run_review_continues_with_no_exclusions_when_directory_is_not_go_module(
    tmp_path, monkeypatch
):
    """Review still works outside Go modules, but the prompt must not exclude anything."""
    captured_prompts: list[str] = []

    def fake_capture_diff(request, runner, working_directory):
        return CapturedDiff(
            text="diff --git a/a.go b/a.go\n+++ b/a.go\n@@ -0,0 +1 @@\n+package main\n",
            request=request,
        )

    def fake_invoke_models(
        models,
        prompt,
        runner,
        working_directory,
        runs,
        concurrency,
        disable_mcp_servers=(),
    ):
        captured_prompts.append(prompt)
        return InvocationReport(
            models=tuple(models),
            runs_requested=runs,
            runs=(),
            availability=tuple(ModelAvailability(model, True, "") for model in models),
        )

    monkeypatch.setattr("atom.review.capture_diff", fake_capture_diff)
    monkeypatch.setattr("atom.review.invoke_models", fake_invoke_models)

    outcome = run_review(
        request=DiffRequest(DiffSource.WORKING, None),
        models=("gpt-5.4",),
        runner=FakeRunner({}),
        working_directory=tmp_path,
        runs=1,
        concurrency=1,
    )

    assert outcome.toolchain.was_run is False
    assert "go.mod" in outcome.toolchain.skip_reason
    assert "nothing is excluded" in captured_prompts[0].lower()
    assert "ignored error returns" not in captured_prompts[0]
