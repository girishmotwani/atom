"""Behaviour tests for command execution."""

from __future__ import annotations

import sys

from atom.runner import CommandOutcome, CommandResult, SubprocessRunner


def test_command_result_succeeded_only_for_completed_zero(tmp_path):
    """B5: CommandResult.succeeded is true only for completed zero-exit commands."""
    successful_result = CommandResult(("tool",), tmp_path, CommandOutcome.COMPLETED, 0, "", "", 0.01)
    failing_result = CommandResult(("tool",), tmp_path, CommandOutcome.COMPLETED, 1, "", "", 0.01)
    missing_result = CommandResult(("tool",), tmp_path, CommandOutcome.TOOL_MISSING, None, "", "", 0.01)

    assert successful_result.succeeded is True
    assert failing_result.succeeded is False
    assert missing_result.succeeded is False


def test_command_result_combined_output_preserves_both_streams(tmp_path):
    """B17 support: combined_output keeps stdout and stderr available to gates."""
    result = CommandResult(("tool",), tmp_path, CommandOutcome.COMPLETED, 1, "stdout text", "stderr text", 0.01)

    assert result.combined_output == "stdout text\nstderr text"


def test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately(tmp_path):
    """B1/B4: A real subprocess failure is returned as data with both streams captured."""
    runner = SubprocessRunner()

    result = runner.run(
        [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(7)",
        ],
        tmp_path,
        timeout_seconds=5.0,
    )

    assert result.outcome is CommandOutcome.COMPLETED
    assert result.exit_code == 7
    assert result.stdout.strip() == "out"
    assert result.stderr.strip() == "err"
    assert result.succeeded is False


def test_subprocess_runner_returns_timed_out_without_raising(tmp_path):
    """B2: A command exceeding timeout_seconds is killed and reported without an exception."""
    runner = SubprocessRunner()

    result = runner.run(
        [sys.executable, "-c", "import time; time.sleep(1.0)"],
        tmp_path,
        timeout_seconds=0.1,
    )

    assert result.outcome is CommandOutcome.TIMED_OUT
    assert result.exit_code is None
    assert "timed out" in result.stderr.lower()


def test_subprocess_runner_returns_tool_missing_without_raising(tmp_path):
    """B3: A missing executable is reported as TOOL_MISSING instead of raising FileNotFoundError."""
    runner = SubprocessRunner()

    result = runner.run(["definitely-not-an-atom-test-tool"], tmp_path, timeout_seconds=1.0)

    assert result.outcome is CommandOutcome.TOOL_MISSING
    assert result.exit_code is None
    assert "definitely-not-an-atom-test-tool" in result.stderr
