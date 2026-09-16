"""The phase state machine and the on-disk layout of an Atom project.

Atom's pipeline is POC -> SPEC -> TDD -> REVIEW -> SHIP, and the transition
rules in this module encode the framework's central claim rather than merely
tracking position:

* **You may always go back.** A refuted POC sends you back to the question; a
  gap found during TDD sends you back to the spec. That is the loop working as
  designed. Making rework awkward would push people to paper over what they
  found, which is the opposite of the point.

* **You may not skip forward.** POC -> TDD means building without a spec.
  SPEC -> REVIEW means reviewing code that was never written test-first. Those
  are precisely the shortcuts the framework exists to make inconvenient.

Position is explicit and persisted (B92). Atom never infers what phase a
project is in by looking at which files happen to exist -- inference is how a
tool ends up confidently wrong about work it did not watch happen.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any

from atom.eventlog import EventLog
from atom.storage import StateFileCorrupt, read_json, write_json

# Everything Atom persists lives here, and nothing is written outside it (B71).
STATE_DIRECTORY_NAME = ".atom"

CONFIG_FILE_NAME = "config.json"
STATE_FILE_NAME = "state.json"
EVENTS_FILE_NAME = "events.jsonl"


class Phase(str, Enum):
    """A stage of the Atom pipeline, in pipeline order.

    Declaration order is meaningful: it defines what "forward" and "back" mean
    for every transition check below.
    """

    POC = "poc"
    SPEC = "spec"
    TDD = "tdd"
    REVIEW = "review"
    SHIP = "ship"


class Status(str, Enum):
    """How far through the current phase the project is."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class InvalidTransition(Exception):
    """A requested phase change is not legal from the current phase."""


# Cached once: the ordered phase list is consulted on every transition.
PHASE_ORDER: tuple[Phase, ...] = tuple(Phase)


def phase_index(phase: Phase) -> int:
    """Position of a phase in the pipeline, used to compare forward and back."""
    return PHASE_ORDER.index(phase)


def next_phase(phase: Phase) -> Phase | None:
    """The phase that follows, or None at the end of the pipeline."""
    position = phase_index(phase)
    if position + 1 >= len(PHASE_ORDER):
        return None
    return PHASE_ORDER[position + 1]


@dataclass(frozen=True)
class ProjectState:
    """Where a project is in the pipeline.

    Immutable on purpose: transitions return a new value, so "what did we
    actually save" is answerable at any point rather than depending on when you
    happened to look.
    """

    phase: Phase
    status: Status

    def transition_to(self, requested: Phase) -> "ProjectState":
        """Move to ``requested``, refusing an illegal jump (B94).

        Args:
            requested: The phase to move to.

        Returns:
            A new state at ``requested``, reset to NOT_STARTED.

        Raises:
            InvalidTransition: The jump skips a phase forward.
        """
        if requested is self.phase:
            # Re-entering the current phase is a no-op, not an error. It is
            # what happens when a second POC is run for the same question.
            return self

        current_position = phase_index(self.phase)
        requested_position = phase_index(requested)

        # Going back any distance is always allowed; going forward is allowed
        # exactly one step at a time.
        if requested_position > current_position + 1:
            raise InvalidTransition(self._explain_refusal(requested))

        return replace(self, phase=requested, status=Status.NOT_STARTED)

    def to_dict(self) -> dict[str, Any]:
        return {"phase": self.phase.value, "status": self.status.value}

    def _explain_refusal(self, requested: Phase) -> str:
        """Say what is legal, not merely that this was not (B94)."""
        allowed_forward = next_phase(self.phase)
        options = [phase.value for phase in PHASE_ORDER[: phase_index(self.phase)]]
        if allowed_forward is not None:
            options.append(allowed_forward.value)

        return (
            f"cannot move from '{self.phase.value}' to '{requested.value}': "
            f"that skips a phase.\n"
            f"Atom's pipeline runs "
            f"{' -> '.join(phase.value for phase in PHASE_ORDER)}, and each "
            f"phase depends on the one before it.\n"
            f"From '{self.phase.value}' you can move to: {', '.join(options)}."
        )


def state_from_dict(payload: dict[str, Any], source: Path) -> ProjectState:
    """Build a ProjectState from parsed JSON, rejecting values Atom cannot use.

    An unrecognised phase or status is corruption rather than something to
    guess at -- a file saying ``"phase": "deploy"`` was written by something
    that is not this version of Atom, and proceeding would be inventing state.

    Raises:
        StateFileCorrupt: A value is not a known phase or status.
    """
    try:
        phase = Phase(payload["phase"])
    except ValueError as error:
        raise StateFileCorrupt(
            f"{source} names an unknown phase {payload['phase']!r}. "
            f"Known phases are: {', '.join(item.value for item in PHASE_ORDER)}."
        ) from error

    try:
        status = Status(payload["status"])
    except ValueError as error:
        raise StateFileCorrupt(
            f"{source} names an unknown status {payload['status']!r}. "
            f"Known statuses are: {', '.join(item.value for item in Status)}."
        ) from error

    return ProjectState(phase=phase, status=status)


class Project:
    """An Atom project on disk: its paths, its state, and its event log.

    This is the seam every command goes through, so that "where do files live"
    is answered in exactly one place.
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.state_directory = self.root / STATE_DIRECTORY_NAME
        self.config_path = self.state_directory / CONFIG_FILE_NAME
        self.state_path = self.state_directory / STATE_FILE_NAME
        self.events_path = self.state_directory / EVENTS_FILE_NAME
        self.event_log = EventLog(self.events_path)

    @property
    def is_initialised(self) -> bool:
        """True when both halves of the project's record are present.

        Config and state are checked separately (B73) because one existing
        without the other is a half-finished init, not a working project.
        """
        return self.config_path.exists() and self.state_path.exists()

    def initialise(self, *, module_path: str) -> ProjectState:
        """Create ``.atom/`` with a fresh config and state.

        A new project starts at POC/NOT_STARTED. Anything else would claim work
        that has not happened.
        """
        self.state_directory.mkdir(parents=True, exist_ok=True)

        write_json(self.config_path, {"module_path": module_path})

        state = ProjectState(phase=Phase.POC, status=Status.NOT_STARTED)
        write_json(self.state_path, state.to_dict())

        self.event_log.append({"event": "initialised", "module_path": module_path})
        return state

    def load_state(self) -> ProjectState:
        """Read the persisted state.

        Raises:
            StateFileMissing: The project is not initialised.
            StateFileCorrupt: The file is damaged or names values Atom does not
                recognise.
        """
        payload = read_json(self.state_path, required_keys=("phase", "status"))
        return state_from_dict(payload, self.state_path)

    def save_state(self, state: ProjectState) -> None:
        """Persist the state atomically."""
        write_json(self.state_path, state.to_dict())

    def load_config(self) -> dict[str, Any]:
        return read_json(self.config_path, required_keys=("module_path",))

    def advance_to(self, requested: Phase) -> ProjectState:
        """Move the project to ``requested``, persisting and logging the change.

        The transition is validated *before* anything is written, so a refused
        move leaves no trace at all -- a half-applied transition would be worse
        than a refused one.
        """
        current = self.load_state()
        updated = current.transition_to(requested)

        self.save_state(updated)
        self.event_log.append(
            {
                "event": "phase_changed",
                "from": current.phase.value,
                "to": updated.phase.value,
            }
        )
        return updated
