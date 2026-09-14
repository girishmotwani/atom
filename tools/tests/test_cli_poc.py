"""Behaviour tests for the `atom poc` CLI surface (B62-B66).

Written before the poc subcommands exist. The first run must fail -- RED.

The behaviour these tests exist to defend is B64: `atom poc run` exits 0
whenever the spike actually ran, whatever verdict it reached. A Refuted spike
is the method working, not a malfunction, and CI must not go red for it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from atom.cli import main


@pytest.fixture
def go_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A directory that looks like a Go repo, with the CWD pointed at it."""

    (tmp_path / "go.mod").write_text("module example.com/parent\n\ngo 1.23.4\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _write_spike(poc_root: Path, slug: str, *, question: str = "A question?", with_go_mod: bool = True) -> Path:
    directory = poc_root / slug
    directory.mkdir(parents=True)
    if with_go_mod:
        (directory / "go.mod").write_text(f"module spike/{slug}\n\ngo 1.23.4\n", encoding="utf-8")
    (directory / "README.md").write_text(f"# Spike: {slug}\n\n## Question\n\n{question}\n", encoding="utf-8")
    return directory


# --------------------------------------------------------------------------
# B62 -- the three subcommands exist
# --------------------------------------------------------------------------


def test_poc_list_on_an_empty_repo_succeeds(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """B61/B63: no spikes yet is normal, so it must not be an error."""

    assert main(["poc", "list"]) == 0


def test_poc_list_shows_each_spike(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """B59: slug plus question is what makes the list worth reading."""

    _write_spike(go_repo / "poc", "json-streaming", question="Does streaming beat buffering?")

    main(["poc", "list"])

    output = capsys.readouterr().out
    assert "json-streaming" in output
    assert "Does streaming beat buffering?" in output


def test_poc_list_flags_a_spike_missing_go_mod(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """B60: this is the state that breaks the parent build, so it must be loud."""

    _write_spike(go_repo / "poc", "broken", with_go_mod=False)

    main(["poc", "list"])

    output = capsys.readouterr().out
    assert "go.mod" in output


def test_poc_list_json_is_machine_readable(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """B66: JSON output must parse, and carry the schema version."""

    _write_spike(go_repo / "poc", "alpha", question="A question?")

    main(["poc", "list", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == 1
    assert payload["spikes"][0]["slug"] == "alpha"


# --------------------------------------------------------------------------
# B62, B63 -- `atom poc new`
# --------------------------------------------------------------------------


def test_poc_new_rejects_a_bad_slug_as_a_usage_error(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """B63: exit 2 means the invocation was wrong, distinct from a real failure."""

    assert main(["poc", "new", "Bad Slug", "--question", "A question?"]) == 2


def test_poc_new_bad_slug_writes_one_line_to_stderr(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A traceback would bury the one line that says what to do instead."""

    main(["poc", "new", "Bad Slug", "--question", "A question?"])

    captured = capsys.readouterr()
    assert captured.err.strip()
    assert "Traceback" not in captured.err


def test_poc_new_refuses_an_existing_spike_as_a_usage_error(go_repo: Path) -> None:
    """B43/B63: refusing to overwrite is a usage error, not a failure of the spike."""

    _write_spike(go_repo / "poc", "alpha")

    assert main(["poc", "new", "alpha", "--question", "A question?"]) == 2


# --------------------------------------------------------------------------
# B64, B65 -- the exit code contract for `atom poc run`
# --------------------------------------------------------------------------


def test_poc_run_on_a_missing_spike_is_a_usage_error(go_repo: Path) -> None:
    """B63: naming a spike that does not exist is a mistake in the invocation."""

    assert main(["poc", "run", "nope"]) == 2


def test_poc_run_on_a_spike_without_go_mod_is_a_usage_error(go_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """B63: the directory is not a spike, so there is nothing to run."""

    _write_spike(go_repo / "poc", "broken", with_go_mod=False)

    assert main(["poc", "run", "broken"]) == 2
    assert "go.mod" in capsys.readouterr().err


# --------------------------------------------------------------------------
# B69 -- a crash is not a verdict, so it is not a success
#
# B64 made `atom poc run` exit 0 whenever the spike ran, because a Refuted
# spike is the method working rather than a malfunction. A crash was not a
# case anyone had in mind when that was decided: the spike did not conclude
# anything, it fell over. Exiting 0 would hide a broken spike behind a green
# tick, and in CI nobody would ever look.
# --------------------------------------------------------------------------

GO_PANIC_STDERR = "panic: runtime error: index out of range [5] with length 0\n\ngoroutine 1 [running]:\nmain.main()\n"


def _spike_result(execute_exit: int, verdict, stderr: str = ""):
    from atom.spike import SpikeKind, SpikeResult, Stage, StageResult

    stages = (
        StageResult(Stage.VET, 0, "", ""),
        StageResult(Stage.BUILD, 0, "", ""),
        StageResult(Stage.EXECUTE, execute_exit, "", stderr),
    )
    return SpikeResult("json-streaming", SpikeKind.COMMAND, stages, verdict, execute_exit)


def test_a_crashed_spike_makes_the_command_exit_non_zero(monkeypatch, tmp_path):
    """B69: CI must be able to notice that a spike stopped working."""
    from atom import cli
    from atom.spike import Verdict

    crashed = _spike_result(2, Verdict.CRASHED, GO_PANIC_STDERR)
    monkeypatch.setattr(cli, "run_spike", lambda *args, **kwargs: crashed)

    assert cli._exit_code_for_spike(crashed) == cli.EXIT_CHECK_FAILED


def test_every_real_verdict_makes_the_command_exit_zero():
    """B64/B69: the control -- Refuted and Inconclusive are results, not failures."""
    from atom import cli
    from atom.spike import Verdict

    for exit_code, verdict in ((0, Verdict.CONFIRMED), (1, Verdict.REFUTED), (2, Verdict.INCONCLUSIVE)):
        result = _spike_result(exit_code, verdict)
        assert cli._exit_code_for_spike(result) == cli.EXIT_PASSED, verdict
