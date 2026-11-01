"""End-to-end tests for `atom review`, including the program actually starting.

Three earlier phases shipped a green unit suite over a program that would not
run: an unbuildable package, a `NameError` at import time, and two messages
printed on top of each other. Every one of those was invisible to tests that
imported a module and called a function, because importing a module is not
running a program.

So the tests here that matter most are the ones at the bottom, which launch a
real subprocess and check what a developer would actually see.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import replace
import subprocess
import sys
from pathlib import Path

import pytest

from atom.cli import EXIT_CHECK_FAILED, EXIT_PASSED, EXIT_USAGE_ERROR, main
from atom.gates import GateResult, GateStatus
from atom.go_selection import (
    GoToolchainConfigError, GoToolchainRequest, GoToolchainSelection, GoToolchainSelectionError,
)
from atom.review import DEFAULT_REVIEW_MODELS
from atom.review import ToolchainGateFailed
from atom.runner import CommandOutcome, CommandResult
from tests.conftest import cli_review_events, cli_review_response
from tests.test_go_selection import write_policy

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"

DIFF_TEXT = """diff --git a/store/cache.go b/store/cache.go
--- a/store/cache.go
+++ b/store/cache.go
@@ -40,0 +41,3 @@
+func Export() {}
+var x = 1
+var y = 2
"""

FINDINGS_JSON = (
    '[{"file": "store/cache.go", "line": 41, "severity": "high", '
    '"message": "Export reads without the lock."}]'
)


class ScriptedRunner:
    """A runner that answers git and the model CLI from a script.

    Deliberately keyed on what the command *is* rather than on call order, so
    a test does not silently pass when the pipeline changes the sequence of
    calls it makes.
    """

    def __init__(self, diff_text: str = DIFF_TEXT, reply: str = FINDINGS_JSON,
                 failing_models: tuple[str, ...] = (),
                 unavailable_models: tuple[str, ...] = (),
                 transport_replies: dict[str, str] | None = None):
        self.diff_text = diff_text
        self.reply = reply
        self.failing_models = failing_models
        self.unavailable_models = unavailable_models
        self.transport_replies = transport_replies or {}
        self.commands: list[list[str]] = []
        self.stdin_texts: list[str | None] = []

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        self.commands.append(list(command))
        self.stdin_texts.append(stdin_text)

        def result(outcome, exit_code, stdout, stderr, duration):
            return CommandResult(
                command=tuple(command), working_directory=working_directory,
                outcome=outcome, exit_code=exit_code,
                stdout=stdout, stderr=stderr, duration_seconds=duration,
            )

        if command[0] == "git":
            return result(CommandOutcome.COMPLETED, 0, self.diff_text, "", 0.1)

        model = command[command.index("--model") + 1]

        if model in self.unavailable_models:
            return result(
                CommandOutcome.COMPLETED, 1, "",
                f'Error: Model "{model}" from --model flag is not available.', 0.1,
            )

        if model in self.failing_models:
            return result(CommandOutcome.TIMED_OUT, None, "", "timed out", 60.0)

        reply = self.reply
        if "--output-format" in command:
            reply = cli_review_response(reply) if reply.strip() else reply
            reply = self.transport_replies.get(model, reply)
        return result(CommandOutcome.COMPLETED, 0, reply, "", 1.0)


@pytest.fixture
def scripted(monkeypatch):
    runner = ScriptedRunner()
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)
    return runner


def review(*args: str) -> int:
    return main(["review", *args])


def test_review_cli_captures_project_toolchain_policy(scripted, monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    policy = write_policy(tmp_path)
    original = policy.read_bytes()
    assert review("--working", "--skip-toolchain", "--runs", "1", "--json") == EXIT_PASSED
    payload = json.loads(capsys.readouterr().out)
    assert "selection" in payload["toolchain"], "CLI did not capture launch policy"
    assert payload["toolchain"]["selection"]["requested_version"] == "1.26.9"
    assert payload["toolchain"]["selection"]["status"] == "not_run"
    assert policy.read_bytes() == original


@pytest.mark.parametrize("configured", [False, True])
def test_review_cli_version_and_executable_override(
    scripted, monkeypatch, tmp_path, capsys, configured,
):
    import atom.cli as cli

    monkeypatch.chdir(tmp_path)
    if configured:
        write_policy(tmp_path)
    captured = []
    original = cli.run_review

    def recording(**kwargs):
        captured.append(kwargs.get("go_toolchain_request"))
        return original(**kwargs)

    monkeypatch.setattr(cli, "run_review", recording)
    relative = Path("sdk") / "bin" / "go"
    assert review(
        "--working", "--go-version", "1.25.0", "--go-executable", str(relative),
        "--runs", "1", "--json",
    ) == EXIT_PASSED
    assert captured[0] is not None, "explicit toolchain request was ignored"
    assert captured[0].version == "1.25.0"
    assert captured[0].source == "cli"
    assert captured[0].project_version == ("1.26.9" if configured else None)
    assert captured[0].executable == (tmp_path / relative).resolve()
    assert json.loads(capsys.readouterr().out)["toolchain"]["selection"]["status"] == "not_run"


@pytest.mark.parametrize("option", [
    ("--go-version", "1.26.9"), ("--go-executable", "sdk"),
])
def test_explicit_go_options_conflict_with_skip_toolchain(
    scripted, monkeypatch, tmp_path, capsys, option,
):
    monkeypatch.chdir(tmp_path)
    write_policy(tmp_path)
    assert review("--working", "--skip-toolchain", *option, "--json") == EXIT_USAGE_ERROR
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--skip-toolchain" in captured.err
    assert scripted.commands == []


@pytest.mark.parametrize("kind", ["configuration", "selection", "required"])
def test_toolchain_setup_failures_are_stderr_only(
    scripted, monkeypatch, tmp_path, capsys, kind,
):
    monkeypatch.chdir(tmp_path)
    pin = GoToolchainRequest("1.26.9", "cli")
    if kind == "configuration":
        error = GoToolchainConfigError("config.json: invalid review_go_version")
        expected = ("review_go_version",)
    elif kind == "selection":
        command = ("fixture-go", "version")
        error = GoToolchainSelectionError(
            pin, "execution_failed", "probe failed",
            probes=(CommandResult(
                command, tmp_path, CommandOutcome.TIMED_OUT, None, "",
                "probe-specific stderr", 60,
            ),),
        )
        expected = ("Go 1.26.9", "probe-specific stderr")
    else:
        failure = GateResult(
            "build", GateStatus.FAILED, "build failed", "original compiler output", True, 0.1,
        )
        error = ToolchainGateFailed(
            (failure,), selection=GoToolchainSelection(
                pin, status="verified", observed_version="1.26.9", executable=tmp_path / "go",
            ),
        )
        expected = ("Requested Go: 1.26.9", "observed Go: 1.26.9", "original compiler output")

    def blocked(**kwargs):
        raise error

    monkeypatch.setattr("atom.cli.run_review", blocked)
    try:
        code = review("--working", "--json")
    except Exception as escaped:
        pytest.fail(f"typed setup error escaped CLI diagnostics: {type(escaped).__name__}")
    assert code == EXIT_CHECK_FAILED
    captured = capsys.readouterr()
    assert captured.out == ""
    assert all(text in captured.err for text in expected)
    assert scripted.commands == []


@pytest.mark.parametrize("options,code,diagnostic", [
    (("--go-version", "auto"), EXIT_USAGE_ERROR, "exact stable Go"),
    (("--go-executable", "installed"), EXIT_USAGE_ERROR, "requires"),
    (("--go-version", "1.26.9"), EXIT_CHECK_FAILED, "review_go_version"),
])
def test_invalid_go_policy_fails_before_runner_commands(
    scripted, monkeypatch, tmp_path, capsys, options, code, diagnostic,
):
    monkeypatch.chdir(tmp_path)
    if code == EXIT_CHECK_FAILED:
        write_policy(tmp_path, "invalid")
    assert review("--working", "--json", *options) == code
    captured = capsys.readouterr()
    assert captured.out == ""
    assert diagnostic in captured.err
    assert scripted.commands == []


def test_context_requires_opt_in_before_io(scripted, monkeypatch, capsys):
    def forbidden(*args):
        pytest.fail("context must not be read before validating opt-in")

    monkeypatch.setattr("atom.cli.load_context_documents", forbidden)
    assert review("--working", "--context-file", "unread.md") == EXIT_USAGE_ERROR
    assert "context-file requires --fixed-evidence" in capsys.readouterr().err
    assert scripted.commands == []


@pytest.mark.parametrize("kind,code,reason", [
    ("missing", EXIT_CHECK_FAILED, "could not be read"),
    ("blank", EXIT_CHECK_FAILED, "empty content"),
    ("duplicate", EXIT_USAGE_ERROR, "duplicate context-file"),
])
def test_context_cli_failure_blocks_runner(
    scripted, tmp_path, monkeypatch, capsys, kind, code, reason,
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "valid").write_text("first contract", encoding="utf-8")
    (tmp_path / "blank").write_text(" \n", encoding="utf-8")
    invalid = "valid" if kind == "duplicate" else kind
    assert review(
        "--working", "--fixed-evidence", "--context-file", "valid",
        "--context-file", invalid,
    ) == code
    output = capsys.readouterr()
    assert reason in output.err
    assert output.out == ""
    assert scripted.commands == []


def test_fixed_evidence_cli_uses_mode(scripted, tmp_path, capsys):
    source = tmp_path / "contract.md"
    source.write_text("Caller contract.", encoding="utf-8")
    assert review(
        "--working", "--fixed-evidence", "--context-file", str(source),
        "--skip-toolchain", "--runs", "1",
    ) == EXIT_PASSED
    for command in scripted.commands:
        if command[0] == "copilot":
            assert "--excluded-tools" in command
    prompts = [text for text in scripted.stdin_texts if text is not None]
    assert len(prompts) == 2
    assert all("Caller contract." in text for text in prompts)


@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("with_context", [False, True])
def test_fixed_evidence_cli_reports_scope(
    scripted, tmp_path, capsys, as_json, with_context,
):
    scripted.reply = "[]"
    documents = [b"private-first-contract\r\n", "private-\u03bb-contract\n".encode("utf-8")]
    arguments = ["--working", "--fixed-evidence", "--skip-toolchain", "--runs", "1"]
    if as_json:
        arguments.append("--json")
    if with_context:
        for index, content in enumerate(documents):
            source = tmp_path / f"private-path-{index}.md"
            source.write_bytes(content)
            arguments.extend(("--context-file", str(source)))

    assert review(*arguments) == EXIT_PASSED
    captured = capsys.readouterr()
    assert captured.err == ""
    text = captured.out
    assert "private" not in text
    prompt = next(text for text in scripted.stdin_texts if text is not None).encode("utf-8")
    scope = "diff-plus-caller-context" if with_context else "diff-only"
    if as_json:
        payload = json.loads(text)
        metadata = payload.get("review_execution")
        assert metadata is not None
        assert metadata == {
            "mode": "fixed-evidence",
            "tool_policy": "source-exclusions-requested",
            "scope": scope,
            "context_quality": "unvalidated",
            "prompt_utf8_bytes": len(prompt),
            "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
            "documents": [
                {"label": f"context-{index}", "utf8_bytes": len(content),
                 "sha256": hashlib.sha256(content).hexdigest()}
                for index, content in enumerate(documents, 1)
            ] if with_context else [],
        }
        assert not payload["is_partial"]
        assert not payload["has_no_usable_response"]
    else:
        assert "## Review evidence" in text
        assert scope in text
        assert "unvalidated" in text
        assert str(len(prompt)) in text
        assert hashlib.sha256(prompt).hexdigest() in text
        assert (
            f"Logical prompt (before platform stdin normalization): {len(prompt)} "
            f"UTF-8 bytes; SHA-256 `{hashlib.sha256(prompt).hexdigest()}`."
        ) in text
        assert "No findings were reported in the supplied evidence." in text
        assert "not automatically included" in text
        if with_context:
            assert "caller-supplied/unverified" in text
            for index, content in enumerate(documents, 1):
                assert f"context-{index}" in text
                assert hashlib.sha256(content).hexdigest() in text
                assert str(len(content)) in text


@pytest.mark.parametrize("with_good_model", [False, True])
def test_fixed_evidence_execution_violation_is_incomplete(
    monkeypatch, capsys, with_good_model,
):
    events = cli_review_events(FINDINGS_JSON)
    events.insert(0, {"type": "tool.execution_start", "data": {"private": "events"}})
    runner = ScriptedRunner(
        reply="[]", transport_replies={"bad": "\n".join(map(json.dumps, events))},
    )
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)
    arguments = [
        "--working", "--fixed-evidence", "--skip-toolchain",
        "--model", "bad", "--runs", "2", "--json",
    ]
    if with_good_model:
        arguments.extend(("--model", "good"))
    assert review(*arguments) == EXIT_CHECK_FAILED
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["is_partial"]
    assert payload["has_no_usable_response"] is not with_good_model
    assert payload["findings"] == []
    assert all(failure["excerpt"] == "" for failure in payload["unparsed_responses"])
    assert {entry["model"]: entry["runs_answered"] for entry in payload["models"]} == (
        {"bad": 0, "good": 2} if with_good_model else {"bad": 0}
    )
    assert all(entry["runs_requested"] == 2 for entry in payload["models"])
    assert "CLI fixed-evidence contract violated" in captured.err
    assert "private" not in captured.out + captured.err


@pytest.mark.parametrize("fixed", [False, True])
@pytest.mark.parametrize("as_json", [False, True])
def test_structured_failure_streams_never_reach_cli_reports(
    monkeypatch, capsys, fixed, as_json,
):
    class FailedReviews(ScriptedRunner):
        def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
            result = super().run(command, working_directory, timeout_seconds, stdin_text)
            if "--output-format" in command:
                return replace(
                    result, outcome=CommandOutcome.TIMED_OUT, exit_code=None,
                    stdout="private-native-stdout", stderr="private-native-stderr",
                )
            return result

    monkeypatch.setattr("atom.cli.SubprocessRunner", FailedReviews)
    arguments = ["--working", "--skip-toolchain", "--runs", "1"]
    if fixed:
        arguments.append("--fixed-evidence")
    if as_json:
        arguments.append("--json")
    assert review(*arguments) == EXIT_CHECK_FAILED
    captured = capsys.readouterr()
    assert "private" not in captured.out + captured.err
    assert "timed out (observed elapsed" in captured.err


class TestDiffSourceSelection:
    """B104 - choosing what to review is explicit."""

    def test_no_source_is_a_usage_error(self, scripted, capsys):
        assert review() == EXIT_USAGE_ERROR
        assert "atom review" in capsys.readouterr().err

    def test_two_sources_is_a_usage_error(self, scripted, capsys):
        assert review("--working", "--staged") == EXIT_USAGE_ERROR
        assert capsys.readouterr().err

    def test_working_is_accepted(self, scripted):
        assert review("--working", "--runs", "1") == EXIT_PASSED

    def test_staged_is_accepted(self, scripted):
        assert review("--staged", "--runs", "1") == EXIT_PASSED

    def test_branch_is_accepted(self, scripted):
        assert review("--branch", "main", "--runs", "1") == EXIT_PASSED


class TestNonsensicalSettings:
    """A8 - refused, not clamped."""

    @pytest.mark.parametrize("flag,value", [("--runs", "0"), ("--concurrency", "0")])
    def test_a_setting_that_consults_nobody_is_refused(self, scripted, capsys, flag, value):
        assert review("--working", flag, value) == EXIT_USAGE_ERROR
        assert capsys.readouterr().err

    def test_a_negative_window_is_refused(self, scripted, capsys):
        assert review("--working", "--runs", "1", "--window", "-1") == EXIT_USAGE_ERROR
        assert capsys.readouterr().err


class TestExitCodes:
    """B135-B137."""

    def test_a_complete_review_exits_zero_even_with_findings(self, scripted, capsys):
        code = review("--working", "--runs", "1")
        assert code == EXIT_PASSED
        # The finding is present; it simply does not change the verdict.
        assert "Export reads without the lock." in capsys.readouterr().out

    def test_a_partial_review_exits_non_zero(self, monkeypatch, capsys):
        # P4-3: a CI job where one model fails every run would otherwise stay
        # green forever while nobody reads the banner.
        runner = ScriptedRunner(failing_models=(DEFAULT_REVIEW_MODELS[1],))
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        assert "partial" in capsys.readouterr().out.lower()

    def test_no_usable_response_fails_loudly(self, monkeypatch, capsys):
        # B130. The dangerous case: an empty report reads as a clean one.
        runner = ScriptedRunner(failing_models=DEFAULT_REVIEW_MODELS)
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        code = review("--working", "--runs", "1")
        captured = capsys.readouterr()

        assert code == EXIT_CHECK_FAILED
        assert "not a clean review" in captured.err

    def test_every_model_unavailable_fails_rather_than_reporting_nothing(
        self, monkeypatch, capsys
    ):
        runner = ScriptedRunner(
            unavailable_models=DEFAULT_REVIEW_MODELS
        )
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        assert capsys.readouterr().err

    def test_a_git_failure_is_not_reported_as_a_clean_review(self, monkeypatch, capsys):
        class BrokenGit(ScriptedRunner):
            def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
                if command[0] == "git":
                    return CommandResult(
                        command=tuple(command), working_directory=working_directory,
                        outcome=CommandOutcome.COMPLETED, exit_code=128, stdout="",
                        stderr="fatal: not a git repository", duration_seconds=0.1,
                    )
                return super().run(command, working_directory, timeout_seconds)

        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: BrokenGit())

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        assert "atom review" in capsys.readouterr().err

    def test_a_blocked_toolchain_returns_check_failed_without_reviewing(
        self, monkeypatch, capsys
    ):
        """A failed required toolchain gate is a failed review setup, not a clean review."""
        failure = GateResult(
            "vet",
            GateStatus.FAILED,
            "go vet ./... failed with exit code 1",
            "vet: printf mismatch",
            True,
            0.1,
        )

        def blocked_review(*args, **kwargs):
            raise ToolchainGateFailed((failure,))

        monkeypatch.setattr("atom.cli.run_review", blocked_review)

        assert review("--working", "--runs", "1") == EXIT_CHECK_FAILED
        captured = capsys.readouterr()
        assert "review was not run" in captured.err
        assert "vet" in captured.err
        assert "printf mismatch" in captured.err


class TestStructuredResponses:
    @pytest.mark.parametrize("as_json", [False, True])
    def test_only_parent_findings_reach_the_report(self, monkeypatch, capsys, as_json):
        events = cli_review_events(FINDINGS_JSON)
        del events[0]["data"]["phase"]
        events.insert(0, {
            "type": "assistant.message", "agentId": "child",
            "data": {"content": "DELEGATED_SENTINEL"},
        })
        events.insert(2, {
            "type": "assistant.message",
            "data": {"content": "COMMENTARY_SENTINEL", "phase": "commentary"},
        })
        raw = "\n".join(json.dumps(event) for event in events)
        runner = ScriptedRunner(
            transport_replies={model: raw for model in DEFAULT_REVIEW_MODELS},
        )
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)
        arguments = ["--working", "--runs", "1"]
        if as_json:
            arguments.append("--json")

        assert review(*arguments) == EXIT_PASSED
        captured = capsys.readouterr()

        assert "Export reads without the lock." in captured.out
        assert "SENTINEL" not in captured.out + captured.err
        if as_json:
            payload = json.loads(captured.out)
            assert not payload["is_partial"]
            assert not payload["has_no_usable_response"]
            assert all(model["runs_answered"] == 1 for model in payload["models"])

    def test_transport_failure_keeps_completion_but_not_answer_count(self, monkeypatch, capsys):
        good, bad = DEFAULT_REVIEW_MODELS
        raw = json.dumps({
            "type": "assistant.message", "account": "PRIVATE_ACCOUNT",
            "data": {"content": "[]", "phase": "final_answer"},
        })
        runner = ScriptedRunner(transport_replies={bad: raw})
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        assert review("--working", "--runs", "1", "--json") == EXIT_CHECK_FAILED
        captured = capsys.readouterr()
        payload = json.loads(captured.out)

        assert payload["is_partial"]
        assert not payload["has_no_usable_response"]
        models = {entry["model"]: entry for entry in payload["models"]}
        assert models[good]["runs_answered"] == 1
        assert models[bad]["runs_completed"] == 1
        assert models[bad]["runs_answered"] == 0
        assert payload["silent_runs"] == [{"model": bad, "run_index": 1}]
        assert len(payload["unparsed_responses"]) == 1
        failure = payload["unparsed_responses"][0]
        assert failure["model"] == bad
        assert failure["excerpt"] == ""
        assert failure["reason"].startswith("CLI response transport:")
        assert "PRIVATE_ACCOUNT" not in captured.out + captured.err

    @pytest.mark.parametrize("raw", [
        "", " \n\t", "[]", "not JSONL",
        json.dumps({"type": "result", "exitCode": 0, "sessionId": "fixture"}),
    ])
    def test_no_readable_parent_never_becomes_a_clean_review(self, monkeypatch, capsys, raw):
        runner = ScriptedRunner(
            transport_replies={model: raw for model in DEFAULT_REVIEW_MODELS},
        )
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        assert review("--working", "--runs", "1", "--json") == EXIT_CHECK_FAILED
        captured = capsys.readouterr()
        payload = json.loads(captured.out)

        assert payload["is_partial"]
        assert payload["has_no_usable_response"]
        assert all(model["runs_completed"] == 1 for model in payload["models"])
        assert all(model["runs_answered"] == 0 for model in payload["models"])
        assert "not a clean review" in captured.err


class TestChannels:
    """B128 - `atom review > review.md` leaves a clean file."""

    def test_the_report_goes_to_stdout(self, scripted, capsys):
        review("--working", "--runs", "1")

        assert "# Code review" in capsys.readouterr().out

    def test_failure_detail_goes_to_stderr_only(self, monkeypatch, capsys):
        runner = ScriptedRunner(failing_models=(DEFAULT_REVIEW_MODELS[1],))
        monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)

        review("--working", "--runs", "1")
        captured = capsys.readouterr()

        assert "timed out" in captured.err
        assert "timed out" not in captured.out

    def test_json_output_is_parseable(self, scripted, capsys):
        review("--working", "--runs", "1", "--json")
        payload = json.loads(capsys.readouterr().out)

        assert payload["findings"][0]["file"] == "store/cache.go"


class TestCommandsIssued:
    """What the pipeline actually asks the tools to do."""

    def test_each_model_is_asked_the_requested_number_of_times(self, scripted):
        review("--working", "--runs", "2")

        review_calls = [
            text for text in scripted.stdin_texts
            if text is not None and "Here is the diff:" in text
        ]

        assert len(review_calls) == 4

    def test_custom_instructions_are_disabled(self, scripted):
        # Without this the CLI loads AGENTS.md from the working directory, and
        # the review silently becomes a different prompt than the one measured.
        review("--working", "--runs", "1")

        model_calls = [c for c in scripted.commands if c[0] != "git"]
        assert all("--no-custom-instructions" in c for c in model_calls)

    def test_named_mcp_exclusions_reach_probes_and_reviews(self, scripted):
        code = review(
            "--working", "--runs", "1", "--skip-toolchain",
            "--model", "first-model", "--model", "second-model",
            "--disable-mcp-server", "first-mcp",
            "--disable-mcp-server", "second-mcp",
        )

        assert code == EXIT_PASSED
        calls = [
            (command, text)
            for command, text in zip(scripted.commands, scripted.stdin_texts)
            if command[0] == "copilot"
        ]
        assert len(calls) == 4
        for command, text in calls:
            excluded = [
                command[index + 1]
                for index, argument in enumerate(command)
                if argument == "--disable-mcp-server"
            ]
            assert excluded == ["first-mcp", "second-mcp"]
            if "-p" in command:
                assert text is None
            else:
                assert text is not None and DIFF_TEXT in text
        probe_indices = [index for index, (command, _) in enumerate(calls) if "-p" in command]
        review_indices = [index for index, (command, _) in enumerate(calls) if "-p" not in command]
        assert max(probe_indices) < min(review_indices)

    def test_no_named_mcp_server_is_disabled_by_default(self, scripted):
        # A7. The spike's speed-up command named servers that existed on one
        # machine; shipping them would have put private names in an open tool.
        # Asserting the flag itself is absent is stronger than asserting one
        # vendor's name is absent -- it cannot be satisfied by a different
        # vendor's name, and it does not require this test to carry the very
        # names the decision exists to keep out of the repository.
        review("--working", "--runs", "1")

        model_calls = [c for c in scripted.commands if c[0] != "git"]
        assert all("--disable-mcp-server" not in c for c in model_calls)

    def test_the_prompt_carries_the_whole_diff_in_one_call(self, scripted):
        # P4-4. Phases keep diffs small, so chunking is unnecessary complexity
        # that would also destroy cross-hunk context.
        review("--working", "--runs", "1")

        full = [
            text for text in scripted.stdin_texts
            if text is not None and "Here is the diff:" in text
        ]

        assert full and all("var y = 2" in p for p in full)


class TestTheProgramActuallyRuns:
    """Subprocess tests. Unit tests cannot tell you that a program starts.

    Every assertion here would have caught a real failure shipped by an earlier
    phase, and none of them could have been caught by importing a module.
    """

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "atom.cli", *args],
            cwd=TOOLS_DIR, capture_output=True, text=True, timeout=120,
        )

    def test_the_module_can_be_executed(self):
        result = self._run("--help")

        assert result.returncode == 0
        assert "atom" in result.stdout

    def test_review_appears_in_the_top_level_help(self):
        result = self._run("--help")

        assert "review" in result.stdout

    def test_review_help_runs_without_error(self):
        result = self._run("review", "--help")

        assert result.returncode == 0
        assert "--working" in result.stdout
        assert "--json" in result.stdout

    def test_review_without_a_source_exits_two_and_explains(self):
        # The one path that needs no network and no models: it must still be a
        # clean usage error rather than a traceback.
        result = self._run("review")

        assert result.returncode == EXIT_USAGE_ERROR
        assert "Traceback" not in result.stderr
        assert result.stderr.strip()

    def test_review_with_two_sources_exits_two_and_explains(self):
        result = self._run("review", "--working", "--staged")

        assert result.returncode == EXIT_USAGE_ERROR
        assert "Traceback" not in result.stderr

    def test_a_refused_setting_does_not_produce_a_traceback(self):
        result = self._run("review", "--working", "--runs", "0")

        assert result.returncode == EXIT_USAGE_ERROR
        assert "Traceback" not in result.stderr

    def test_nothing_is_defined_below_the_main_guard(self):
        # Phase 2 shipped 169 green tests over a program that raised NameError
        # at startup, because a function had been appended below this guard.
        source = (TOOLS_DIR / "atom" / "cli.py").read_text(encoding="utf-8")
        _, _, tail = source.partition('if __name__ == "__main__":')

        assert tail.strip() == "raise SystemExit(main())"



class TestTheDefaultModelPairIsTheMeasuredOne:
    """The default pair is a measurement result, so it is pinned like one.

    Until A23 nothing asserted which models `atom review` consults by default.
    That is how a default drifts: someone edits the tuple to try a model, the
    whole suite stays green because every other test passes its models in
    explicitly, and the edit ships. These tests do not judge the choice -- they
    make changing it a deliberate act that has to update a stated reason.
    """

    def test_the_default_models_are_the_two_that_scored_above_ninety_percent(self):
        # gpt-5.4 named the exact defect line on 98% of planted defects and
        # gemini-3.8-flash on 100%. No other candidate measured above 56%.
        assert DEFAULT_REVIEW_MODELS == ("gpt-5.4", "gemini-3.8-flash")

    def test_the_help_text_names_the_models_it_actually_uses(self):
        # The help string is written by hand, so it can disagree with the
        # tuple. A developer who is told the wrong default cannot tell that
        # the review they ran was not the review that was measured.
        result = self._help()

        for model in DEFAULT_REVIEW_MODELS:
            assert model in result

    @staticmethod
    def _help() -> str:
        completed = subprocess.run(
            [sys.executable, "-m", "atom.cli", "review", "--help"],
            capture_output=True,
            text=True,
            cwd=TOOLS_DIR,
            timeout=60,
        )
        return completed.stdout
