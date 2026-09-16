"""Tests for the phase state machine and project layout (B71-B73, B92, B94).

The transition rules here are not bookkeeping -- they encode Atom's central
claim. You may always go *back* (a refuted POC or a gap found during TDD sends
you back, and that is the framework working as intended), but you may not skip
*forward*, because skipping forward is exactly the shortcut Atom exists to
prevent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from atom.state import (
    InvalidTransition,
    Phase,
    Project,
    ProjectState,
    Status,
    next_phase,
)
from atom.storage import StateFileCorrupt, StateFileMissing


# ---------------------------------------------------------------------------
# Project layout (B71-B73)
# ---------------------------------------------------------------------------


def test_all_state_lives_under_a_single_directory(tmp_path: Path) -> None:
    """B71: nothing is written outside .atom/."""
    project = Project(tmp_path)

    assert project.state_directory == tmp_path / ".atom"
    for path in (project.config_path, project.state_path, project.events_path):
        assert path.parent == tmp_path / ".atom"


def test_config_and_state_are_separate_files(tmp_path: Path) -> None:
    """B73: config is what the developer chose; state is what Atom observed.

    They have different rewrite frequencies and should not share a failure
    mode -- losing state costs progress, losing config costs a decision.
    """
    project = Project(tmp_path)

    assert project.config_path != project.state_path
    assert project.config_path.name == "config.json"
    assert project.state_path.name == "state.json"


def test_a_project_without_the_directory_is_not_initialised(tmp_path: Path) -> None:
    assert not Project(tmp_path).is_initialised


def test_a_project_is_initialised_once_both_files_exist(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    assert project.is_initialised
    assert project.config_path.exists()
    assert project.state_path.exists()


def test_initialising_starts_at_the_first_phase(tmp_path: Path) -> None:
    """A new project has not done its POC yet. Anything else would be a lie."""
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    state = project.load_state()
    assert state.phase == Phase.POC
    assert state.status == Status.NOT_STARTED


def test_initialising_records_an_event(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    events = project.event_log.read_valid()
    assert [event["event"] for event in events] == ["initialised"]


def test_config_records_what_the_developer_chose(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    config = json.loads(project.config_path.read_text(encoding="utf-8"))
    assert config["module_path"] == "example.com/thing"


def test_loading_state_from_an_uninitialised_project_says_so(tmp_path: Path) -> None:
    """B72: a command needing state must name the fix, not just the problem."""
    with pytest.raises(StateFileMissing) as caught:
        Project(tmp_path).load_state()

    assert "atom init" in str(caught.value)


def test_loading_corrupt_state_is_distinguishable_from_missing(tmp_path: Path) -> None:
    """B77 at the project level: two problems, two answers."""
    project = Project(tmp_path)
    project.state_directory.mkdir(parents=True)
    project.state_path.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(StateFileCorrupt):
        project.load_state()


def test_state_survives_a_save_and_load_round_trip(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    project.save_state(ProjectState(phase=Phase.TDD, status=Status.IN_PROGRESS))

    reloaded = project.load_state()
    assert reloaded.phase == Phase.TDD
    assert reloaded.status == Status.IN_PROGRESS


def test_an_unknown_phase_in_the_file_is_corruption(tmp_path: Path) -> None:
    """A phase name Atom does not recognise is not something to guess at."""
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")
    project.state_path.write_text(
        json.dumps({"phase": "deploy", "status": "in_progress"}), encoding="utf-8"
    )

    with pytest.raises(StateFileCorrupt) as caught:
        project.load_state()

    assert "deploy" in str(caught.value)


def test_an_unknown_status_in_the_file_is_corruption(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")
    project.state_path.write_text(
        json.dumps({"phase": "tdd", "status": "vibes"}), encoding="utf-8"
    )

    with pytest.raises(StateFileCorrupt) as caught:
        project.load_state()

    assert "vibes" in str(caught.value)


# ---------------------------------------------------------------------------
# Transitions (B92, B94)
# ---------------------------------------------------------------------------


def test_the_pipeline_runs_in_a_known_order() -> None:
    assert list(Phase) == [Phase.POC, Phase.SPEC, Phase.TDD, Phase.REVIEW, Phase.SHIP]


@pytest.mark.parametrize(
    "current,following",
    [
        (Phase.POC, Phase.SPEC),
        (Phase.SPEC, Phase.TDD),
        (Phase.TDD, Phase.REVIEW),
        (Phase.REVIEW, Phase.SHIP),
    ],
)
def test_moving_forward_one_phase_is_allowed(current: Phase, following: Phase) -> None:
    ProjectState(phase=current, status=Status.DONE).transition_to(following)


def test_the_last_phase_has_nothing_after_it() -> None:
    assert next_phase(Phase.SHIP) is None


@pytest.mark.parametrize(
    "current,requested",
    [
        (Phase.POC, Phase.TDD),
        (Phase.POC, Phase.SHIP),
        (Phase.SPEC, Phase.REVIEW),
    ],
)
def test_skipping_a_phase_forward_is_refused(current: Phase, requested: Phase) -> None:
    """This is the rule that makes Atom a methodology rather than a task list.

    Going POC -> TDD means building without a spec. Going SPEC -> REVIEW means
    reviewing code that was never written test-first. Both are the shortcuts
    the framework exists to make inconvenient.
    """
    state = ProjectState(phase=current, status=Status.DONE)

    with pytest.raises(InvalidTransition):
        state.transition_to(requested)


@pytest.mark.parametrize(
    "current,requested",
    [
        (Phase.SPEC, Phase.POC),
        (Phase.TDD, Phase.SPEC),
        (Phase.TDD, Phase.POC),
        (Phase.SHIP, Phase.POC),
    ],
)
def test_going_back_to_any_earlier_phase_is_allowed(
    current: Phase, requested: Phase
) -> None:
    """Rework is not failure -- it is the loop working.

    A refuted POC sends you back to the question. A gap found during TDD sends
    you back to the spec. A framework that made going back awkward would push
    people to paper over what they found, which is the opposite of the point.
    """
    ProjectState(phase=current, status=Status.IN_PROGRESS).transition_to(requested)


def test_a_refused_transition_explains_what_is_legal() -> None:
    """B94: name the current phase, the requested one, and the way out."""
    state = ProjectState(phase=Phase.POC, status=Status.DONE)

    with pytest.raises(InvalidTransition) as caught:
        state.transition_to(Phase.SHIP)

    message = str(caught.value)
    assert "poc" in message.lower()
    assert "ship" in message.lower()
    assert "spec" in message.lower(), "the message must say where you CAN go"


def test_transitioning_returns_a_new_state_rather_than_mutating() -> None:
    """Immutable state makes 'what did we save' answerable at any point."""
    before = ProjectState(phase=Phase.POC, status=Status.DONE)

    after = before.transition_to(Phase.SPEC)

    assert before.phase == Phase.POC
    assert after.phase == Phase.SPEC


def test_a_new_phase_starts_not_started() -> None:
    after = ProjectState(phase=Phase.POC, status=Status.DONE).transition_to(Phase.SPEC)

    assert after.status == Status.NOT_STARTED


def test_staying_in_the_same_phase_is_allowed() -> None:
    """Re-entering the current phase is a no-op, not an error -- it is what
    happens when a second POC is run for the same question."""
    ProjectState(phase=Phase.TDD, status=Status.IN_PROGRESS).transition_to(Phase.TDD)


def test_advancing_a_project_persists_and_logs_it(tmp_path: Path) -> None:
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    project.advance_to(Phase.SPEC)

    assert project.load_state().phase == Phase.SPEC
    events = [event["event"] for event in project.event_log.read_valid()]
    assert events == ["initialised", "phase_changed"]


def test_advancing_illegally_neither_saves_nor_logs(tmp_path: Path) -> None:
    """A refused transition must leave no trace -- half-applying it would be
    worse than refusing."""
    project = Project(tmp_path)
    project.initialise(module_path="example.com/thing")

    with pytest.raises(InvalidTransition):
        project.advance_to(Phase.SHIP)

    assert project.load_state().phase == Phase.POC
    assert [event["event"] for event in project.event_log.read_valid()] == ["initialised"]
