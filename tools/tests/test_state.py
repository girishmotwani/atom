"""Tests for what an Atom project declares about itself (B172-B176, B182-B183).

Phase 6 splits a project's facts into *derived* and *declared*. Everything the
old state machine tracked -- which phase, what status -- is now derived from the
filesystem and lives elsewhere. What survives as *declared* facts are two things
that cannot be observed, kept in two files with different lifetimes (B73): the
Go module path (configuration) in ``.atom/config.json``, and the record that a
human approved a gate (an approval) in ``.atom/state.json``.

These tests pin that reduced shape and, just as importantly, pin the *absence*
of the state machine. The ``exposes_no_*`` tests assert via ``hasattr`` on the
imported module so that quietly reintroducing the ``Phase`` enum -- or any of the
transition machinery -- fails loudly rather than passing unnoticed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import atom.state as state_module
from atom.state import Approval, LoadedState, Project, ProjectState


# ---------------------------------------------------------------------------
# Project layout and initialisation (B176)
# ---------------------------------------------------------------------------


def test_all_state_lives_under_a_single_directory(tmp_path: Path) -> None:
    """B71 survives Phase 6: nothing is written outside .atom/."""
    project = Project(tmp_path)

    assert project.state_directory == tmp_path / ".atom"
    for path in (project.config_path, project.state_path, project.events_path):
        assert path.parent == tmp_path / ".atom"


def test_config_and_state_are_separate_files(tmp_path: Path) -> None:
    """B73 is not repealed by Phase 6: config is what the developer chose,
    state is what the tool tracks, and they are separate files on purpose."""
    project = Project(tmp_path)

    assert project.config_path != project.state_path
    assert project.config_path.name == "config.json"
    assert project.state_path.name == "state.json"


def test_a_project_without_a_state_file_is_not_initialised(tmp_path: Path) -> None:
    """`is_initialised` guards `--force` (B176): a half-init is not a project."""
    assert not Project(tmp_path).is_initialised


def test_a_project_is_initialised_once_both_files_exist(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    assert project.is_initialised
    assert project.config_path.exists()
    assert project.state_path.exists()


def test_init_writes_the_module_path(tmp_path: Path) -> None:
    """B176: init records the module path in config.json, where Phase 3 put it."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    stored = json.loads(project.config_path.read_text(encoding="utf-8"))
    assert stored["module_path"] == "github.com/example/thing"


def test_init_writes_an_empty_approvals_list(tmp_path: Path) -> None:
    """B176: a fresh project has approved nothing. An empty list, not a claim."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    stored = json.loads(project.state_path.read_text(encoding="utf-8"))
    assert stored["approvals"] == []


def test_init_writes_no_phase_or_status(tmp_path: Path) -> None:
    """B176: init is configuration, not a claim about progress. Phase/status
    are derived now, so writing them here would be a fact that can go stale."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    stored = json.loads(project.state_path.read_text(encoding="utf-8"))
    assert "phase" not in stored
    assert "status" not in stored


def test_init_records_an_event(tmp_path: Path) -> None:
    """The event log is a Phase 3 feature this phase does not repeal (B183)."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    events = [event["event"] for event in project.event_log.read_valid()]
    assert events == ["initialised"]


# ---------------------------------------------------------------------------
# The reduced file shape (B172)
# ---------------------------------------------------------------------------


def test_the_state_file_holds_configuration_and_approvals(tmp_path: Path) -> None:
    """B172: state.json holds a version and approvals; the configuration it
    refers to (the module path) lives beside it in config.json (B73)."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")
    project.record_approval(
        phase="phase-06-state", gate="design-spec", date="2026-09-24"
    )

    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    config = json.loads(project.config_path.read_text(encoding="utf-8"))

    assert state["version"] == 2
    assert state["approvals"] == [
        {"phase": "phase-06-state", "gate": "design-spec", "date": "2026-09-24"}
    ]
    assert config["module_path"] == "github.com/example/thing"


def test_the_module_path_stays_in_config_not_state(tmp_path: Path) -> None:
    """B172/B73: the module path is configuration, so it belongs to config.json
    and must never appear in state.json -- a second copy is free to disagree."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")
    project.record_approval(
        phase="phase-06-state", gate="design-spec", date="2026-09-24"
    )

    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    config = json.loads(project.config_path.read_text(encoding="utf-8"))

    assert "module_path" not in state
    assert config["module_path"] == "github.com/example/thing"
    assert project.config_path.exists() and project.state_path.exists()


def test_the_state_file_has_no_phase_field(tmp_path: Path) -> None:
    """B172: a file that repeats a derived fact is a file that can disagree."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")
    project.record_approval(
        phase="phase-06-state", gate="design-spec", date="2026-09-24"
    )

    stored = json.loads(project.state_path.read_text(encoding="utf-8"))
    assert "phase" not in stored


def test_the_state_file_has_no_status_field(tmp_path: Path) -> None:
    """B172: status is derived from the filesystem, never declared here."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")
    project.record_approval(
        phase="phase-06-state", gate="design-spec", date="2026-09-24"
    )

    stored = json.loads(project.state_path.read_text(encoding="utf-8"))
    assert "status" not in stored


def test_an_approval_records_phase_gate_and_date(tmp_path: Path) -> None:
    """B172: an approval is the record that a human said yes, at a gate, on a day."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    project.record_approval(
        phase="phase-06-state", gate="design-spec", date="2026-09-24"
    )

    approvals = project.load().state.approvals
    assert len(approvals) == 1
    approval = approvals[0]
    assert approval.phase == "phase-06-state"
    assert approval.gate == "design-spec"
    assert approval.date == "2026-09-24"


def test_recording_an_approval_appends_rather_than_replaces(tmp_path: Path) -> None:
    """A second gate does not erase the first -- approvals are project history."""
    project = Project(tmp_path)
    project.initialise(module_path="github.com/example/thing")

    project.record_approval(phase="phase-06-state", gate="design-spec", date="2026-09-24")
    project.record_approval(phase="phase-06-state", gate="test-spec", date="2026-09-25")

    gates = [approval.gate for approval in project.load().state.approvals]
    assert gates == ["design-spec", "test-spec"]


# ---------------------------------------------------------------------------
# An absent file is a usable empty record, not an error (B174)
# ---------------------------------------------------------------------------


def test_an_absent_state_file_is_not_an_error(tmp_path: Path) -> None:
    """B174: the crux of the phase. `atom status` must be answerable when the
    file that used to be the sole source of truth is simply not there."""
    loaded = Project(tmp_path).load()

    assert isinstance(loaded, LoadedState)
    assert loaded.problems == []


def test_an_absent_state_file_reports_no_approvals(tmp_path: Path) -> None:
    """B174: an absent file means nothing has been approved -- not a broken read."""
    loaded = Project(tmp_path).load()

    assert loaded.state.approvals == []


# ---------------------------------------------------------------------------
# A corrupt or wrong-shaped file is a reported problem, never a crash (B175)
# ---------------------------------------------------------------------------


def test_a_corrupt_state_file_is_reported_as_a_problem(tmp_path: Path) -> None:
    """B175: unparseable content surfaces as a problem the caller can report,
    while still returning a record so the rest of status can be produced."""
    project = Project(tmp_path)
    project.state_directory.mkdir(parents=True)
    project.state_path.write_text("{not json", encoding="utf-8")

    loaded = project.load()

    assert loaded.problems, "a corrupt file must be reported, not swallowed"
    assert loaded.state.approvals == []


def test_a_non_string_module_path_is_ignored_not_trusted(tmp_path: Path) -> None:
    """A module_path in config.json that is not text cannot be configuration, so
    the composed view drops it to the empty default rather than trusting it."""
    project = Project(tmp_path)
    project.state_directory.mkdir(parents=True)
    project.config_path.write_text('{"module_path": 42}', encoding="utf-8")
    project.state_path.write_text('{"version": 2, "approvals": []}', encoding="utf-8")

    loaded = project.load()

    assert loaded.state.module_path == ""
    assert loaded.state.approvals == []
    assert loaded.problems == []


@pytest.mark.parametrize(
    "contents",
    [
        pytest.param("[1, 2, 3]", id="json-array-at-top-level"),
        pytest.param('"just a string"', id="json-string"),
        pytest.param('{"module_path": "x"}', id="dict-missing-approvals"),
        pytest.param('{"approvals": "not-a-list"}', id="approvals-not-a-list"),
        pytest.param('{"approvals": [1, 2, 3]}', id="approval-entry-not-a-dict"),
    ],
)
def test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem(
    tmp_path: Path, contents: str
) -> None:
    """B175: `[1, 2, 3]` is valid JSON and invalid state. Parsing successfully
    is not the same as being usable, so shape is checked, not just syntax."""
    project = Project(tmp_path)
    project.state_directory.mkdir(parents=True)
    project.state_path.write_text(contents, encoding="utf-8")

    loaded = project.load()

    assert loaded.problems, f"wrong-shaped state must be a problem: {contents!r}"
    assert loaded.state.approvals == []


# ---------------------------------------------------------------------------
# ProjectState is an approvals-shaped record (B183)
# ---------------------------------------------------------------------------


def test_project_state_carries_configuration_and_approvals() -> None:
    """B183: the record holds the module path and the approvals, nothing more."""
    approval = Approval(phase="phase-06-state", gate="design-spec", date="2026-09-24")
    state = ProjectState(module_path="github.com/example/thing", approvals=[approval])

    assert state.module_path == "github.com/example/thing"
    assert state.approvals == [approval]


def test_project_state_carries_no_phase() -> None:
    """B183: the phase left the file. The record has no attribute to hold it."""
    state = ProjectState(module_path="github.com/example/thing", approvals=[])

    assert not hasattr(state, "phase")
    assert not hasattr(state, "status")


# ---------------------------------------------------------------------------
# The state machine is gone (B182)
# ---------------------------------------------------------------------------


def test_the_state_module_exposes_no_phase_enum() -> None:
    """B182: the Phase enum encoded a machine whose every fact is now derived."""
    assert not hasattr(state_module, "Phase")


def test_the_state_module_exposes_no_status_enum() -> None:
    """B182: status is derived; the Status enum has no remaining job."""
    assert not hasattr(state_module, "Status")


def test_the_state_module_exposes_no_transition_machinery() -> None:
    """B182: the transition helpers and their error type are all removed."""
    assert not hasattr(state_module, "phase_index")
    assert not hasattr(state_module, "next_phase")
    assert not hasattr(state_module, "InvalidTransition")
    assert not hasattr(ProjectState, "transition_to")
