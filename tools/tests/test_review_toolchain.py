"""Tests for the toolchain gate that now precedes model review."""

from __future__ import annotations

from pathlib import Path
import json

import pytest

from atom.diff import CapturedDiff, DiffRequest, DiffSource
from atom.extract import ExtractionReport
from atom.gates import GateResult, GateStatus
from atom.invoke import InvocationReport, ModelAvailability
from atom.review import REVIEW_PROMPT, ToolchainGateFailed, run_review
from atom.runner import CommandOutcome
from atom.report import render_review_json, render_review_markdown
from tests.conftest import FakeRunner, command_result
from tests.test_go_selection import distribution, distribution_runner
from atom.go_selection import GoToolchainRequest, GoToolchainSelectionError
from atom._review_format import ChangedFilesFormatGate, FormattingFile


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
    assert (
        REVIEW_PROMPT.format(toolchain="", style_rules="", diff="{diff}")
        == ORIGINAL_REVIEW_PROMPT
    )


@pytest.mark.parametrize("fixed_evidence", [False, True])
def test_run_review_blocks_before_models_when_required_gate_fails(tmp_path, fixed_evidence):
    """A tree that fails required gates is not ready to spend model calls."""
    (tmp_path / "go.mod").write_text("module example.com/toolchain\n", encoding="utf-8")
    build = ("go", "build", "./...")
    git_root = ("git", "rev-parse", "--show-toplevel")
    git_diff = (
        "git", "diff", "--raw", "--no-abbrev", "-z", "--patch", "--full-index",
        "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative",
        "--submodule=short", "--",
    )
    runner = FakeRunner({
        git_root: command_result(git_root, tmp_path, stdout=str(tmp_path) + "\n"),
        git_diff: command_result(git_diff, tmp_path),
        build: command_result(build, tmp_path, exit_code=1, stderr="compile failed"),
        ("go", "vet", "./..."): command_result(("go", "vet", "./..."), tmp_path),
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
            fixed_evidence=fixed_evidence,
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
        *, fixed_evidence=False,
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


def pinned_review_fixture(tmp_path, monkeypatch):
    binary = distribution(tmp_path / "installed")
    (tmp_path / "go.mod").write_text("module example.com/fixture\ngo 1.26.0\n", encoding="utf-8")
    runner = distribution_runner(binary, tmp_path)
    for executable in ("go", str(binary)):
        for arguments in (("build", "./..."), ("vet", "./..."), ("test", "./..."), ("test", "-race", "./...")):
            command = (executable, *arguments)
            runner.scripted_results[command] = command_result(
                command, tmp_path, stdout="ok example.com/fixture 0.1s\n",
            )
    formatter = binary.with_name("gofmt.exe" if binary.name.endswith(".exe") else "gofmt")
    source = "package main\n"
    for executable in ("gofmt", str(formatter)):
        command = (executable,)
        runner.scripted_results[command] = command_result(command, tmp_path, stdout=source)
    request = DiffRequest(DiffSource.WORKING, None)
    diff = CapturedDiff("diff --git a/main.go b/main.go\n+++ b/main.go\n@@ -0,0 +1 @@\n+package main\n", request)
    monkeypatch.setattr("atom.review.capture_diff", lambda *args: diff)
    monkeypatch.setattr("atom.review.capture_review_diff", lambda *args: (
        diff, ChangedFilesFormatGate((FormattingFile("main.go", source.encode()),), "fixture"),
    ))
    model_calls = []

    def invoke(**kwargs):
        model_calls.append(kwargs)
        return InvocationReport(models=("fixture",), runs_requested=1, runs=(), availability=())

    monkeypatch.setattr("atom.review.invoke_models", invoke)
    return binary, runner, request, model_calls


def test_pinned_review_uses_selected_gates(tmp_path, monkeypatch):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    outcome = run_review(
        request, ("fixture",), runner, tmp_path, 1, 1,
        go_toolchain_request=GoToolchainRequest("1.26.9", "cli", executable=binary),
    )

    selection = outcome.toolchain.selection
    assert selection is not None, "review ignored its exact toolchain request"
    assert selection.status == "verified"
    assert selection.executable == binary
    assert selection.observed_version == "1.26.9"
    assert len(selection.commands) == 8
    assert model_calls[0]["runner"] is runner
    assert all(call[0][0] not in ("go", "gofmt") for call in runner.calls)
    assert all(env["GOTOOLCHAIN"] == "local" for env in runner.environments)
    assert selection.executable_sha256_after == selection.executable_sha256


@pytest.mark.parametrize("target", ["build", "test"])
def test_pinned_makefile_stops_before_probes(tmp_path, monkeypatch, target):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    (tmp_path / "Makefile").write_text(f"{target}:\n\tgo {target} ./...\n", encoding="utf-8")
    monkeypatch.setattr("atom.buildsystem._make_is_on_path", lambda: True)
    try:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest("1.26.9", "cli", executable=binary),
        )
    except Exception as error:
        assert isinstance(error, GoToolchainSelectionError), "wrapper failure was misclassified"
        assert error.reason == "unsupported_wrapper"
        assert f"make {target}" in str(error)
    else:
        pytest.fail("pinned delegated recipe was accepted")
    assert runner.calls == []
    assert model_calls == []


def test_pinned_runner_refuses_delegation_added_after_preflight(tmp_path, monkeypatch):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr("atom.buildsystem._make_is_on_path", lambda: True)
    probe = (str(binary), "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV")
    response = runner.scripted_results[probe]

    def add_makefile(stdin):
        (tmp_path / "Makefile").write_text("build:\n\tgo build ./...\n", encoding="utf-8")
        return response

    runner.scripted_results[probe] = add_makefile
    try:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest("1.26.9", "cli", executable=binary),
        )
    except Exception as error:
        assert isinstance(error, GoToolchainSelectionError), "late delegation escaped the adapter"
        assert error.reason == "unsupported_wrapper"
    else:
        pytest.fail("late delegation was accepted")
    assert all(call[0][0] != "make" for call in runner.calls)
    assert model_calls == []


@pytest.mark.parametrize("skip", [True, False], ids=["configured-skip", "no-module"])
def test_unexecuted_pin_retains_intent_without_observations(tmp_path, monkeypatch, skip):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    if not skip:
        (tmp_path / "go.mod").unlink()
    pin = GoToolchainRequest("1.26.9", "project", project_version="1.26.9", executable=binary)
    outcome = run_review(
        request, ("fixture",), runner, tmp_path, 1, 1,
        skip_toolchain=skip, go_toolchain_request=pin,
    )
    selection = outcome.toolchain.selection
    assert selection is not None, "unexecuted pin disappeared"
    assert selection.request == pin
    assert selection.status == "not_run"
    assert selection.reason == outcome.toolchain.skip_reason
    assert selection.observed_version is None
    assert selection.executable is None
    assert selection.probes == selection.commands == ()
    assert runner.calls == []
    assert "nothing is excluded" in model_calls[0]["prompt"].lower()


@pytest.mark.parametrize("arguments,status,exit_code,detail", [
    (("build", "./..."), CommandOutcome.COMPLETED, 1, "go.mod requires go >= 1.27.0"),
    (("build", "./..."), CommandOutcome.COMPLETED, 1, "undefined: missingSymbol"),
    (("test", "-race", "./..."), CommandOutcome.COMPLETED, 1, "WARNING: DATA RACE"),
    (("test", "./..."), CommandOutcome.TOOL_MISSING, None, "required tool is missing"),
    (("build", "./..."), CommandOutcome.COMPLETED, 2, "unknown compiler problem"),
])
def test_pinned_gate_failure_retains_selection_and_blocks_models(
    tmp_path, monkeypatch, arguments, status, exit_code, detail,
):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    command = (str(binary), *arguments)
    runner.scripted_results[command] = command_result(
        command, tmp_path, outcome=status, exit_code=exit_code, stderr=detail,
    )
    with pytest.raises(ToolchainGateFailed) as raised:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest("1.26.9", "cli", executable=binary),
        )
    assert getattr(raised.value, "selection", None) is not None, "failed gate lost its version context"
    assert raised.value.selection.observed_version == "1.26.9"
    assert detail in raised.value.failures[0].details
    assert model_calls == []


@pytest.mark.parametrize("tool", ["go", "gofmt"])
@pytest.mark.parametrize("deleted", [False, True], ids=["replaced", "deleted"])
def test_changed_selected_identity_blocks_models(tmp_path, monkeypatch, tool, deleted):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    target = binary if tool == "go" else binary.with_name(
        "gofmt.exe" if binary.name.endswith(".exe") else "gofmt"
    )
    command = (str(binary), "test", "-race", "./...")
    result = runner.scripted_results[command]

    def change_identity(stdin):
        if deleted:
            target.unlink()
        else:
            target.write_bytes(b"replaced after verification")
        return result

    runner.scripted_results[command] = change_identity
    try:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest("1.26.9", "cli", executable=binary),
        )
    except Exception as error:
        assert isinstance(error, GoToolchainSelectionError), "identity failure escaped its category"
        assert error.reason == "verification_failed"
        assert "before=" in str(error) and "after=" in str(error)
        assert error.selection.commands
        assert error.selection.executable_sha256
    else:
        pytest.fail("changed selected identity reached models")
    assert model_calls == []


@pytest.mark.parametrize("skip", [False, True])
def test_pinned_evidence_is_consistent_across_outputs(tmp_path, monkeypatch, skip):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    monkeypatch.setenv("SELECTION_PRIVATE_VALUE", "must-not-appear-in-reports")
    outcome = run_review(
        request, ("fixture",), runner, tmp_path, 1, 1, skip_toolchain=skip,
        go_toolchain_request=GoToolchainRequest(
            "1.26.9", "cli", project_version="1.25.0", executable=binary,
        ),
    )
    serialized = render_review_json(outcome)
    payload = json.loads(serialized)
    assert "selection" in payload["toolchain"], "report omitted requested selection"
    selection = payload["toolchain"]["selection"]
    assert payload["schema_version"] == 2
    assert set(selection) == {
        "status", "requested_version", "request_source", "project_version",
        "selection_source", "executable", "executable_sha256", "executable_sha256_after",
        "goroot", "observed_version", "gofmt_executable", "gofmt_sha256",
        "gofmt_sha256_after", "reason", "discovery_diagnostics", "probes", "commands",
    }
    assert selection["status"] == ("not_run" if skip else "verified")
    assert selection["requested_version"] == "1.26.9"
    assert selection["request_source"] == "cli"
    assert selection["project_version"] == "1.25.0"
    if skip:
        assert selection["observed_version"] is selection["executable"] is None
        assert selection["commands"] == selection["probes"] == []
        assert selection["reason"] == outcome.toolchain.skip_reason
    else:
        assert selection["observed_version"] == "1.26.9"
        assert selection["executable"] == str(binary)
        assert selection["executable_sha256_after"] == selection["executable_sha256"]
        record = selection["commands"][0]
        assert record == {
            "command": [str(binary), "build", "./..."], "working_directory": str(tmp_path),
            "outcome": "completed", "exit_code": 0,
            "stdout": "ok example.com/fixture 0.1s\n", "stderr": "",
            "duration_seconds": 0.25,
        }
    for text in (render_review_markdown(outcome), model_calls[0]["prompt"]):
        assert "Requested Go: 1.26.9" in text
        assert "project version: 1.25.0" in text
        assert ("observed Go: not observed" if skip else "observed Go: 1.26.9") in text
        assert "not independently attested" in text
        assert "must-not-appear-in-reports" not in text
    assert "must-not-appear-in-reports" not in serialized


def test_unconfigured_review_preserves_legacy_evidence(tmp_path, monkeypatch):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    outcome = run_review(request, ("fixture",), runner, tmp_path, 1, 1)
    assert outcome.toolchain.selection is None
    assert "selection" not in json.loads(render_review_json(outcome))["toolchain"]
    assert "Requested Go:" not in render_review_markdown(outcome)
    assert "Requested Go:" not in model_calls[0]["prompt"]
    assert all(environment is None for environment in runner.environments)
    assert all(call[0][0] != str(binary) for call in runner.calls)


def test_advisory_commands_receive_environment_only_scope(tmp_path, monkeypatch):
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    warning = ("staticcheck", "./...")
    passing = ("govulncheck", "./...")
    runner.scripted_results[warning] = command_result(
        warning, tmp_path, exit_code=1, stderr="analyzer-specific diagnostic",
    )
    runner.scripted_results[passing] = command_result(passing, tmp_path)
    outcome = run_review(
        request, ("fixture",), runner, tmp_path, 1, 1,
        go_toolchain_request=GoToolchainRequest("1.26.9", "cli", executable=binary),
    )
    statuses = {result.name: result.status for result in outcome.toolchain.gate_results}
    assert statuses["staticcheck"] is GateStatus.WARNING
    assert statuses["errcheck"] is GateStatus.SKIPPED
    assert statuses["govulncheck"] is GateStatus.PASSED
    advisory = outcome.toolchain.selection.commands[-3:]
    assert [result.command[0] for result in advisory] == ["staticcheck", "errcheck", "govulncheck"]
    assert all(environment["GOTOOLCHAIN"] == "local" for environment in runner.environments[-3:])
    assert "not independently attested" in model_calls[0]["prompt"]
