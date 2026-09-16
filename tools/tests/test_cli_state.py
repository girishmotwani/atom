"""Tests for `atom init` and `atom status` (B81, B82, B93, B95-B102).

The subprocess smoke tests at the bottom are not optional decoration. Twice in
this project a fully green suite sat on top of a program that would not start:
once an unbuildable ``pyproject.toml``, once a ``NameError`` reachable only via
``python -m``. Importing a module defines every name regardless of order;
executing it stops at the first ``SystemExit``. Only a real process catches it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from atom.cli import main
from atom.state import Phase, Project, ProjectState, Status
from atom import storage


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run each command from inside a scratch project, as a developer would."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# atom init (B96)
# ---------------------------------------------------------------------------


def test_init_creates_the_project(project_root: Path, capsys: pytest.CaptureFixture) -> None:
    exit_code = main(["init", "--module", "example.com/thing"])

    assert exit_code == 0
    assert (project_root / ".atom" / "config.json").exists()
    assert (project_root / ".atom" / "state.json").exists()
    assert "example.com/thing" in capsys.readouterr().out


def test_init_starts_the_project_at_the_first_phase(project_root: Path) -> None:
    main(["init", "--module", "example.com/thing"])

    state = Project(project_root).load_state()
    assert state.phase == Phase.POC
    assert state.status == Status.NOT_STARTED


def test_init_refuses_to_overwrite_an_existing_project(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B96: silently overwriting a state file is destroying work."""
    main(["init", "--module", "example.com/thing"])
    Project(project_root).save_state(ProjectState(Phase.TDD, Status.IN_PROGRESS))

    exit_code = main(["init", "--module", "example.com/other"])

    assert exit_code != 0
    assert "--force" in capsys.readouterr().err
    # The real work is still there.
    assert Project(project_root).load_state().phase == Phase.TDD


def test_init_force_overwrites_deliberately(project_root: Path) -> None:
    main(["init", "--module", "example.com/thing"])
    Project(project_root).save_state(ProjectState(Phase.TDD, Status.IN_PROGRESS))

    exit_code = main(["init", "--module", "example.com/other", "--force"])

    assert exit_code == 0
    assert Project(project_root).load_state().phase == Phase.POC


# ---------------------------------------------------------------------------
# atom status (B93, B95, B97)
# ---------------------------------------------------------------------------


def test_status_reports_the_current_phase(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    main(["init", "--module", "example.com/thing"])

    exit_code = main(["status", "--no-colour"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "poc" in output.lower()


def test_status_on_an_uninitialised_project_explains_the_fix(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    exit_code = main(["status"])

    assert exit_code != 0
    # A7: the answer goes to stdout, the problems go to stderr, each exactly once.
    assert "atom init" in capsys.readouterr().err


def test_status_exits_non_zero_when_state_is_corrupt(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B95: a command that cannot answer its question has not succeeded.

    This follows the Phase 2 gate decision: `atom poc run` on a crashed spike
    exits non-zero even though the command itself ran fine. Same reasoning.
    """
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()
    (project_root / ".atom" / "state.json").write_text("[1, 2, 3]", encoding="utf-8")

    exit_code = main(["status", "--no-colour"])

    assert exit_code != 0
    assert "object" in capsys.readouterr().err.lower()


def test_status_json_is_machine_readable(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B97: human output is for people, JSON output is a contract."""
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()  # Discard init's output; in reality these are separate processes.

    main(["status", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert payload["phase"] == "poc"
    assert payload["status"] == "not_started"
    assert payload["initialised"] is True


def test_status_json_still_emits_on_corrupt_state(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """A tool consuming --json needs a parseable answer even on the bad path.

    Emitting a traceback to stderr and nothing to stdout would make the failure
    invisible to the caller that asked for JSON.
    """
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()  # Discard init's output; in reality these are separate processes.
    (project_root / ".atom" / "state.json").write_text("nonsense", encoding="utf-8")

    exit_code = main(["status", "--json"])

    assert exit_code != 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["problems"], "the problem must appear in the JSON, not only on stderr"


def test_status_reports_every_problem_at_once(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B93: a developer wants the whole picture in one run, as in Phase 1's B17."""
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()  # Discard init's output; in reality these are separate processes.
    # Two independent problems: unrecoverable state, and unsaved work waiting.
    (project_root / ".atom" / "state.json").write_text("nonsense", encoding="utf-8")
    (project_root / ".atom" / "state.json.unsaved").write_text(
        json.dumps({"phase": "tdd", "status": "in_progress"}), encoding="utf-8"
    )

    main(["status", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert len(payload["problems"]) >= 2, payload["problems"]
    assert any(".unsaved" in problem for problem in payload["problems"])


def test_status_reports_unsaved_work(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B83c: an .unsaved file is reported until the developer deals with it."""
    main(["init", "--module", "example.com/thing"])
    (project_root / ".atom" / "state.json.unsaved").write_text(
        json.dumps({"phase": "tdd", "status": "done"}), encoding="utf-8"
    )

    exit_code = main(["status", "--no-colour"])
    captured = capsys.readouterr()

    assert ".unsaved" in captured.err
    # Unsaved work is a problem worth surfacing, but the state itself is fine,
    # so this is a warning rather than a failure to answer.
    assert exit_code == 0


def test_status_shows_the_most_recent_event(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    main(["init", "--module", "example.com/thing"])
    Project(project_root).advance_to(Phase.SPEC)

    main(["status", "--no-colour"])

    assert "phase_changed" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Startup sweep (B81, B82)
# ---------------------------------------------------------------------------


def test_status_sweeps_leftover_temp_files_and_says_so(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B81/B82: a crash the developer did not notice is worth one line."""
    main(["init", "--module", "example.com/thing"])
    leftover = project_root / ".atom" / "state.json.tmp"
    leftover.write_text("x" * 900, encoding="utf-8")

    main(["status", "--no-colour"])

    assert not leftover.exists()
    problems = capsys.readouterr().err
    assert "state.json.tmp" in problems
    assert "900" in problems


def test_the_sweep_never_touches_unsaved_work(project_root: Path) -> None:
    """The B81/B83b collision, guarded at the command level too.

    Unit-testing sweep_temp_files proves the function is careful. This proves
    the command actually calls the careful version.
    """
    main(["init", "--module", "example.com/thing"])
    unsaved = project_root / ".atom" / "state.json.unsaved"
    unsaved.write_text(json.dumps({"phase": "tdd", "status": "done"}), encoding="utf-8")

    main(["status", "--no-colour"])

    assert unsaved.exists()


# ---------------------------------------------------------------------------
# Concurrency (B98, B102)
# ---------------------------------------------------------------------------


def test_status_works_while_the_event_log_lock_is_held(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B102: status must stay usable when everything else is stuck.

    It is the command a developer reaches for when they want to know why the
    tool is not responding. A diagnostic that can be blocked by the thing it
    diagnoses is not much of a diagnostic.
    """
    main(["init", "--module", "example.com/thing"])

    from atom.filelock import FileLock

    with FileLock(project_root / ".atom" / "events.lock", timeout=5):
        exit_code = main(["status", "--no-colour"])

    assert exit_code == 0
    assert "poc" in capsys.readouterr().out.lower()


def test_no_project_wide_lock_file_is_created(project_root: Path) -> None:
    """B98: Atom tolerates concurrency rather than preventing it.

    If a future change adds a whole-project lock, this test should fail and the
    decision should be revisited in the spec first -- P3-2 was a deliberate
    choice with a written-down cost (B100), not an accident.
    """
    main(["init", "--module", "example.com/thing"])
    main(["status", "--no-colour"])

    lock_files = {path.name for path in (project_root / ".atom").glob("*.lock")}
    assert lock_files == {"events.lock"}


# ---------------------------------------------------------------------------
# Smoke tests: the program actually starts (B70)
# ---------------------------------------------------------------------------


def _run_atom(*arguments: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run atom as a real process, the way a developer or CI would."""
    return subprocess.run(
        [sys.executable, "-m", "atom.cli", *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_init_runs_as_a_real_process(tmp_path: Path) -> None:
    result = _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".atom" / "state.json").exists()


def test_status_runs_as_a_real_process(tmp_path: Path) -> None:
    _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)

    result = _run_atom("status", "--no-colour", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "poc" in result.stdout.lower()


def test_status_json_runs_as_a_real_process(tmp_path: Path) -> None:
    _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)

    result = _run_atom("status", "--json", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["phase"] == "poc"


def test_status_exits_non_zero_as_a_real_process_when_corrupt(tmp_path: Path) -> None:
    """The exit code is the part CI depends on, so prove it through a process."""
    _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)
    (tmp_path / ".atom" / "state.json").write_text("[1,2,3]", encoding="utf-8")

    result = _run_atom("status", cwd=tmp_path)

    assert result.returncode != 0


def test_init_that_cannot_write_is_fatal_and_says_how_to_recover(
    project_root: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P3-4 / B83a: a failed state write is fatal AND prints a route out.

    The developer chose this over both alternatives I offered. Without this test
    the recovery instructions are a claim in a spec, not a behaviour of the
    program -- and the whole point of the decision was that the developer sees
    them at the moment things break.
    """

    def refuse_to_replace(source: str, destination: str) -> None:
        # Only the destination is blocked. The rename to `.unsaved` must still
        # work -- that is the whole point of B83b.
        if str(destination).endswith(".unsaved"):
            return _real_replace(source, destination)
        raise PermissionError(13, "the file is in use by another process")

    _real_replace = storage.os.replace
    monkeypatch.setattr(storage.os, "replace", refuse_to_replace)

    exit_code = main(["init", "--module", "example.com/thing"])

    assert exit_code != 0, "a project that was not recorded must not report success"
    message = capsys.readouterr().err
    # B83b: the unsaved work is kept under a suffix the startup sweep ignores.
    assert ".unsaved" in message, message
    assert "nothing was lost" in message, message
    # B83a: the message must contain an action, not just a diagnosis.
    assert "re-run this command" in message, message


def test_init_does_not_promise_safety_it_cannot_deliver(
    project_root: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When even the `.unsaved` rescue fails, the work sits in a `.tmp` file.

    B81 sweeps `*.tmp` on the next run, so telling the developer "nothing was
    lost" there would be false. This is the same trap that B83b exists to close
    -- it just reappears one level down when the rescue itself cannot run.
    """

    def refuse_every_replace(source: str, destination: str) -> None:
        raise PermissionError(13, "the file is in use by another process")

    monkeypatch.setattr(storage.os, "replace", refuse_every_replace)

    exit_code = main(["init", "--module", "example.com/thing"])

    assert exit_code != 0
    message = capsys.readouterr().err
    assert "nothing was lost" not in message, message
    assert "will be removed" in message, message


def test_status_reports_a_corrupt_config_separately_from_state(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B73: config and state are separate files, so they fail separately."""
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()
    (project_root / ".atom" / "config.json").write_text("not json", encoding="utf-8")

    exit_code = main(["status", "--json"])

    payload = json.loads(capsys.readouterr().out)
    # State is still readable, so status could answer its question and exits 0.
    assert exit_code == 0
    assert payload["phase"] == "poc"
    assert payload["problems"], "a broken config must still be reported"
    assert payload["module_path"] is None


def test_status_counts_damaged_event_log_lines(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B90/B91: a half-written line is skipped, counted, and never fatal.

    This is the Phase 3 spike's finding made visible: torn writes happen, and
    the log stays usable around them rather than refusing to be read.
    """
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()
    log = project_root / ".atom" / "events.jsonl"
    with open(log, "a", encoding="utf-8") as handle:
        handle.write('{"event": "torn", "at": \n')
        handle.write(json.dumps({"event": "intact", "at": "2024-01-01T00:00:00Z"}) + "\n")

    exit_code = main(["status", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0, "a damaged log line must not stop status answering"
    assert payload["damaged_log_lines"] == 1
    assert any("damaged" in problem for problem in payload["problems"])
    # The good line after the damaged one is still found -- reading does not
    # stop at the first problem.
    assert payload["last_event"]["event"] == "intact"


def test_status_tells_the_developer_how_to_recover_from_corruption(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """A diagnosis without an action leaves the developer stuck.

    P3-4 settled this for failed writes. Corruption is the more likely event --
    the Phase 3 spike proved torn writes happen -- so the same rule applies.
    """
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()
    (project_root / ".atom" / "state.json").write_text("nonsense", encoding="utf-8")

    exit_code = main(["status", "--no-colour"])

    assert exit_code != 0
    problems = capsys.readouterr().err
    assert ".unsaved" in problems, problems
    assert "atom init --force" in problems, problems


def test_status_prints_each_problem_exactly_once(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """A7: the answer goes to stdout, the problems to stderr, neither twice.

    The first implementation printed problems to both streams, which running it
    by hand showed as the same message duplicated -- with the stderr copy
    missing its newline and colliding with the report. Every test still passed,
    which is why this one exists.
    """
    main(["init", "--module", "example.com/thing"])
    capsys.readouterr()
    (project_root / ".atom" / "state.json").write_text("nonsense", encoding="utf-8")

    main(["status", "--no-colour"])

    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert combined.count("is not valid JSON") == 1, combined
    # stdout keeps the answer and a pointer, never the problem text itself.
    assert "is not valid JSON" not in captured.out
    assert "Project:" in captured.out
    assert "1 problem reported below." in captured.out
