"""Tests for `atom init` and `atom status` (B81, B82, B93, B177-B185).

The subprocess smoke tests at the bottom are not optional decoration. Twice in
this project a fully green suite sat on top of a program that would not start:
once an unbuildable ``pyproject.toml``, once a ``NameError`` reachable only via
``python -m``. Importing a module defines every name regardless of order;
executing it stops at the first ``SystemExit``. Only a real process catches it.

Phase 6 rewrote what these commands mean. `atom status` no longer reads a phase
out of a state file -- it derives one from ``specs/`` -- so the tests that
pinned the old state machine are **deleted** here rather than skipped (B185).
A skipped test still counts itself in the summary while measuring nothing, and
``test_no_test_in_the_suite_is_skipped`` exists precisely to make that shortcut
fail loudly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from atom.cli import main
from atom.state import Approval, Project
from atom import storage


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Run each command from inside a scratch project, as a developer would."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def make_phase(root: Path, name: str, *artifacts: str) -> Path:
    """Create a phase directory under ``specs/demo/`` with the given artifacts.

    The nesting matters: B158a resolves the project directory as the immediate
    subdirectory of ``specs/`` that holds phase directories, so phases live at
    ``specs/demo/phase-NN-slug`` and never directly under ``specs/``.

    ``tmp_path`` is not a git repository, so no branch names a phase and the
    current phase always resolves by the lexical fallback (B162). That keeps
    these tests deterministic without stubbing git.
    """
    directory = root / "specs" / "demo" / name
    directory.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts:
        (directory / artifact).write_text(f"# {artifact}\n", encoding="utf-8")
    return directory


# ---------------------------------------------------------------------------
# atom init (B96)
# ---------------------------------------------------------------------------


def test_init_creates_the_project(project_root: Path, capsys: pytest.CaptureFixture) -> None:
    exit_code = main(["init", "--module", "example.com/thing"])

    assert exit_code == 0
    assert (project_root / ".atom" / "config.json").exists()
    assert (project_root / ".atom" / "state.json").exists()
    assert "example.com/thing" in capsys.readouterr().out


def test_init_starts_the_project_with_no_approvals(project_root: Path) -> None:
    """B176: initialising is configuration, not a claim about progress.

    This replaces `test_init_starts_the_project_at_the_first_phase`, which
    asserted init wrote `phase=poc, status=not_started`. That assertion is gone
    because the thing it asserted is gone: init cannot know what phase you are
    on, and writing a guess was how the old state file drifted out of step with
    the repository in the first place.
    """
    main(["init", "--module", "example.com/thing"])

    state = Project(project_root).load().state
    assert state.module_path == "example.com/thing"
    assert state.approvals == []


def test_init_does_not_claim_a_phase(project_root: Path, capsys: pytest.CaptureFixture) -> None:
    """Init used to print `phase: poc (not started)`. It must not claim one now."""
    main(["init", "--module", "example.com/thing"])

    output = capsys.readouterr().out.lower()
    assert "phase" not in output, (
        "init must not announce a phase -- it has observed no progress, and the "
        "claim goes stale the moment a phase directory is created"
    )


def test_init_refuses_to_overwrite_an_existing_project(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B96: silently overwriting a state file is destroying work.

    What is at stake changed in Phase 6. The state file no longer holds a phase
    -- it holds recorded human approvals, which are the one thing in the project
    that genuinely cannot be re-derived from the filesystem. So this guard
    matters *more* than it did, not less.
    """
    main(["init", "--module", "example.com/thing"])
    project = Project(project_root)
    project.record_approval(phase="phase-03-state", gate="design-spec", date="2026-09-01")

    exit_code = main(["init", "--module", "example.com/other"])

    assert exit_code != 0
    assert "--force" in capsys.readouterr().err
    # The irreplaceable record is still there.
    assert [approval.phase for approval in project.load().state.approvals] == ["phase-03-state"]


def test_init_force_overwrites_deliberately(project_root: Path) -> None:
    main(["init", "--module", "example.com/thing"])
    project = Project(project_root)
    project.record_approval(phase="phase-03-state", gate="design-spec", date="2026-09-01")

    exit_code = main(["init", "--module", "example.com/other", "--force"])

    assert exit_code == 0
    assert project.load().state.approvals == []


# ---------------------------------------------------------------------------
# atom status (B93, B95, B97)
# ---------------------------------------------------------------------------


def test_status_reports_the_current_phase(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """The phase comes from `specs/`, not from anything `init` wrote."""
    main(["init", "--module", "example.com/thing"])
    make_phase(project_root, "phase-01-check", "design-spec.md")
    make_phase(project_root, "phase-02-poc", "design-spec.md")
    capsys.readouterr()

    exit_code = main(["status", "--no-colour"])

    assert exit_code == 0
    output = capsys.readouterr().out
    # B162: no phase-named branch here, so the lexically greatest wins.
    assert "phase-02-poc" in output


def test_status_answers_without_any_state_file_at_all(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """The central claim of Phase 6, end to end.

    This replaces `test_status_on_an_uninitialised_project_explains_the_fix`,
    which asserted a non-zero exit and an "atom init" hint. That was the bug:
    the phase is written on the filesystem in plain sight, and refusing to read
    it because a bookkeeping file was absent made `atom status` useless in
    exactly the situation where it is most wanted -- a fresh clone.
    """
    make_phase(project_root, "phase-04-review", "design-spec.md")

    exit_code = main(["status", "--no-colour"])

    captured = capsys.readouterr()
    assert exit_code == 0, "an absent state file is not a failure (B174, B181)"
    assert "phase-04-review" in captured.out


def test_status_exits_zero_when_state_is_corrupt(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B175/B181: a corrupt state file costs the approvals, not the answer.

    This inverts `test_status_exits_non_zero_when_state_is_corrupt`. The old
    test encoded "a command that cannot answer its question has not succeeded",
    which was sound -- but the premise no longer holds. Atom *can* still answer
    the question, because the phase and its artifacts were never in that file.
    Only the approvals are lost, and that is reported as a problem.
    """
    main(["init", "--module", "example.com/thing"])
    make_phase(project_root, "phase-03-state", "design-spec.md")
    capsys.readouterr()
    (project_root / ".atom" / "state.json").write_text("[1, 2, 3]", encoding="utf-8")

    exit_code = main(["status", "--no-colour"])

    captured = capsys.readouterr()
    assert exit_code == 0
    # The answer survives ...
    assert "phase-03-state" in captured.out
    # ... and the damage is still reported, never swallowed (B180).
    assert captured.err.strip(), "a corrupt state file must still be reported"


def test_status_exits_zero_whatever_it_finds(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B181 (amended): `atom status` is a report, and a report always exits 0.

    Four unrelated shapes -- an uninitialised directory, a project with no
    phases, a corrupt state file, an unrecognised POC status -- are asserted
    together rather than one per test, because the claim being pinned is that
    *no* input produces a non-zero exit. Per-case tests would pin four points
    and leave the general rule unstated.
    """
    assert main(["status", "--no-colour"]) == 0

    main(["init", "--module", "example.com/thing"])
    assert main(["status", "--no-colour"]) == 0

    make_phase(project_root, "phase-03-state", "design-spec.md")
    (project_root / ".atom" / "state.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert main(["status", "--no-colour"]) == 0

    report = project_root / "specs" / "demo" / "phase-03-state" / "poc-report.md"
    report.write_text('---\nstatus: "wibble"\n---\n\nbody\n', encoding="utf-8")
    assert main(["status", "--no-colour"]) == 0

    captured = capsys.readouterr()
    assert captured.err.strip(), "exiting 0 must not mean staying silent"


def test_status_json_is_machine_readable(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """B179: human output is for people, JSON output is a contract."""
    main(["init", "--module", "example.com/thing"])
    make_phase(project_root, "phase-02-poc", "design-spec.md", "test-spec.md")
    capsys.readouterr()  # Discard init's output; in reality these are separate processes.

    main(["status", "--json"])

    payload = json.loads(capsys.readouterr().out)
    assert payload["phase"] == "phase-02-poc"
    assert payload["phase_source"] == "lexical"
    assert payload["artifacts"]["design-spec.md"] is True
    assert payload["artifacts"]["findings.md"] is False
    # B179: every phase appears, not only the current one.
    assert [entry["name"] for entry in payload["phases"]] == ["phase-02-poc"]


def test_status_json_still_emits_on_corrupt_state(
    project_root: Path, capsys: pytest.CaptureFixture
) -> None:
    """A tool consuming --json needs a parseable answer even on the bad path.

    Emitting a traceback to stderr and nothing to stdout would make the failure
    invisible to the caller that asked for JSON.
    """
    main(["init", "--module", "example.com/thing"])
    make_phase(project_root, "phase-02-poc", "design-spec.md")
    capsys.readouterr()  # Discard init's output; in reality these are separate processes.
    (project_root / ".atom" / "state.json").write_text("nonsense", encoding="utf-8")

    exit_code = main(["status", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["problems"], "the problem must appear in the JSON, not only on stderr"
    assert payload["phase"] == "phase-02-poc", "the answer survives the corruption"


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
    """B183: the event log is not repealed by this phase.

    This used to drive the log with `advance_to(Phase.SPEC)` and assert a
    `phase_changed` event. Phase transitions no longer exist to be logged, so
    the test now uses the one event the surviving API emits. That it had to
    change reveals something worth recording: `record_approval` writes no event
    at all, which leaves the log silent about the only human decision the
    project still stores. Noted in findings rather than fixed here -- adding an
    event is a design change this phase did not specify.
    """
    main(["init", "--module", "example.com/thing"])
    make_phase(project_root, "phase-02-poc", "design-spec.md")
    capsys.readouterr()

    main(["status", "--no-colour"])

    assert "initialised" in capsys.readouterr().out


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


def test_the_atom_package_imports_cleanly(tmp_path: Path) -> None:
    """Every module loads under a real interpreter, not just under pytest.

    Importing a module inside an already-warm test session hides ordering bugs:
    Phase 2 shipped 169 green tests on a package that raised `NameError` the
    moment it was run with `python -m`. This imports the whole package in a
    fresh process, which is the only way that class of bug surfaces.
    """
    result = subprocess.run(
        [sys.executable, "-c", "import atom.cli, atom.status, atom.phases, atom.state, atom.report"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr


def test_status_runs_as_a_subprocess_and_exits_zero(tmp_path: Path) -> None:
    """Proves argparse actually reaches the command function.

    Deliberately not a `--help` test. Phase 5 shipped 595 green tests *and* a
    clean `atom ship --help`, then crashed on first real use -- because argparse
    short-circuits on `--help` before the command function is ever called.
    """
    _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)
    make_phase(tmp_path, "phase-02-poc", "design-spec.md")

    result = _run_atom("status", "--no-colour", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "phase-02-poc" in result.stdout


def test_status_json_output_is_parseable_from_a_subprocess(tmp_path: Path) -> None:
    """The JSON path survives real stdout encoding, not just capsys."""
    _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)
    make_phase(tmp_path, "phase-02-poc", "design-spec.md")

    result = _run_atom("status", "--json", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["phase"] == "phase-02-poc"


def test_status_runs_in_a_directory_that_is_not_a_project(tmp_path: Path) -> None:
    """B164/B181: no `.atom/`, no `specs/`, nothing. Still not a crash."""
    result = _run_atom("status", "--no-colour", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "status must say something even with nothing to report"


def test_status_runs_with_no_state_file_present(tmp_path: Path) -> None:
    """The phase's central claim, proven end to end through a real process.

    A fresh clone has `specs/` but no `.atom/state.json`, because state.json is
    written by `init` and a clone never runs it. Before this phase that produced
    `Phase: unknown` and exit 1 -- the defect this whole phase exists to remove.
    """
    make_phase(tmp_path, "phase-01-check", "design-spec.md")
    make_phase(tmp_path, "phase-06-state", "design-spec.md")
    assert not (tmp_path / ".atom" / "state.json").exists()

    result = _run_atom("status", "--no-colour", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "phase-06-state" in result.stdout
    assert "unknown" not in result.stdout.lower()


def test_status_exits_zero_as_a_real_process_when_corrupt(tmp_path: Path) -> None:
    """The exit code is the part CI depends on, so prove it through a process.

    Inverted in Phase 6 (B181): a corrupt state file costs the approvals, not
    the answer, so status still succeeds and reports the damage.
    """
    _run_atom("init", "--module", "example.com/thing", cwd=tmp_path)
    make_phase(tmp_path, "phase-03-state", "design-spec.md")
    (tmp_path / ".atom" / "state.json").write_text("[1,2,3]", encoding="utf-8")

    result = _run_atom("status", "--no-colour", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "phase-03-state" in result.stdout
    assert result.stderr.strip(), "the corruption must still be reported"


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
    make_phase(project_root, "phase-05-ship", "design-spec.md")
    capsys.readouterr()
    (project_root / ".atom" / "config.json").write_text("not json", encoding="utf-8")

    exit_code = main(["status", "--json"])

    payload = json.loads(capsys.readouterr().out)
    # The phase never came from config, so a broken config cannot hide it.
    assert exit_code == 0
    assert payload["phase"] == "phase-05-ship"
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

    # B181: a damaged state file is a *reported problem*, not an unreadable
    # root. Atom answered the question -- it said which file is broken and how
    # to repair it -- so the exit code is 0. Reserving non-zero for "could not
    # answer at all" is what keeps `atom status` usable in a shell pipeline;
    # a phase in progress and a torn write are both ordinary Tuesday events.
    assert exit_code == 0
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
