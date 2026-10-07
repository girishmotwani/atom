"""What an Atom project declares about itself: configuration and approvals.

Phase 6 splits a project's facts into two kinds, and this module owns the ones
that are *declared* rather than *derived*.

* **Derived facts** are read from the filesystem every time they are needed:
  which phases exist, which phase is current, which artifacts a phase has
  produced. Nothing derived is stored here, because a stored copy of a derived
  fact is a copy that can drift out of agreement with reality -- which is the
  precise failure this phase exists to end (see the phase-06 design spec).

* **Declared facts** cannot be observed from disk, so they must be written down.
  Following B73 (Phase 3), the two declarations live in two files with
  deliberately different lifetimes:
    - ``.atom/config.json`` holds the Go module path and the commands Atom
      exercised during onboarding -- configuration written once at ``init``
      and read-only in practice.
    - ``.atom/state.json`` holds the record that a human approved a gate --
      consent that leaves no other trace, and that accumulates over time.

The old ``Phase``/``Status`` state machine that used to live here is gone. Its
every fact is now derived, so the enums, the transition rules, and the
``InvalidTransition`` error have no remaining job (B182). The event log
(``.atom/events.jsonl``) is *not* removed -- it is a working Phase 3 feature
this phase does not repeal (B183).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from atom.eventlog import EventLog
from atom.storage import StateFileCorrupt, StateFileMissing, read_json, write_json

# Everything Atom persists lives here, and nothing is written outside it (B71).
STATE_DIRECTORY_NAME = ".atom"

CONFIG_FILE_NAME = "config.json"
STATE_FILE_NAME = "state.json"
EVENTS_FILE_NAME = "events.jsonl"
BASELINE_FILE_NAME = "baseline.json"

DEFAULT_BUILD_COMMAND = "go build ./..."
DEFAULT_TEST_COMMAND = "go test ./..."

# The on-disk schema version of state.json. Version 1 carried "phase" and
# "status" fields for the state machine this phase deletes; version 2 drops them
# and adds "approvals" (B172). The module path was never in state.json -- it has
# always lived in config.json (B73) -- so it plays no part in the v1->v2
# difference. We deliberately do NOT migrate a version-1 file: it was always
# gitignored, so it never survived a clone and there are no shared v1 files in
# the wild to rescue. A stray local v1 file simply lacks "approvals" and is
# reported as a problem by load() (B175), which is cheaper and more honest than
# guessing at a phase we no longer store.
STATE_FILE_VERSION = 2


@dataclass(frozen=True)
class Approval:
    """The record that a human approved one gate of one phase, on one day.

    This is a declaration: nothing on disk observes that consent was given, so
    Atom writes it down. Immutable, because an approval is a fact about the past.
    """

    phase: str
    gate: str
    date: str

    def to_dict(self) -> dict[str, str]:
        return {"phase": self.phase, "gate": self.gate, "date": self.date}


@dataclass(frozen=True)
class ProjectState:
    """A project's declared record: its module path and its approvals.

    This replaces the old phase/status record entirely (B183). It is the
    in-memory *composed* view of both declaration files -- ``module_path`` comes
    from config.json, ``approvals`` from state.json -- but only the approvals are
    ever written back to state.json (see ``to_dict``). It carries no phase and no
    status: both are derived now, so there is deliberately no attribute here that
    could hold a stale copy of either.
    """

    module_path: str = ""
    approvals: list[Approval] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        # state.json holds a version and approvals, nothing else (B172). The
        # module path is deliberately excluded: it belongs to config.json (B73),
        # and duplicating it here would be a second copy free to disagree.
        return {
            "version": STATE_FILE_VERSION,
            "approvals": [approval.to_dict() for approval in self.approvals],
        }


@dataclass(frozen=True)
class LoadedState:
    """A loaded state together with any problems found reading it.

    Loading returns this rather than raising, because B174/B175 require that a
    missing or corrupt state file never stops ``atom status`` from answering. The
    caller reports ``problems`` and still gets a usable ``state`` to work from.
    """

    state: ProjectState
    problems: list[str]


class Project:
    """An Atom project on disk: its paths, its declarations, and its event log.

    This is the seam every command goes through, so that "where do files live"
    and "what has this project declared" are each answered in exactly one place.
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.state_directory = self.root / STATE_DIRECTORY_NAME
        self.config_path = self.state_directory / CONFIG_FILE_NAME
        self.state_path = self.state_directory / STATE_FILE_NAME
        self.events_path = self.state_directory / EVENTS_FILE_NAME
        self.baseline_path = self.state_directory / BASELINE_FILE_NAME
        self.event_log = EventLog(self.events_path)

    @property
    def is_initialised(self) -> bool:
        """True when both halves of the project's record are present.

        Config and state are checked separately (B73) because one existing
        without the other is a half-finished init, not a working project. This
        is the guard behind ``atom init --force``: re-initialising over an
        existing project would discard its recorded approvals. Note it is a
        separate question from load() succeeding -- an *absent* state file is not
        an error to read (B174), but it does mean the project is not set up.
        """
        return self.config_path.exists() and self.state_path.exists()

    def initialise(self, *, module_path: str) -> ProjectState:
        """Create ``.atom/`` with a fresh config and an empty approvals record.

        Initialising is configuration, not a claim about progress (B176). It
        writes the module path and verified command defaults to config.json, and a
        state.json holding an empty approvals list -- never a phase or a status.
        """
        self.state_directory.mkdir(parents=True, exist_ok=True)

        write_json(
            self.config_path,
            {
                "module_path": module_path,
                "build_command": DEFAULT_BUILD_COMMAND,
                "test_command": DEFAULT_TEST_COMMAND,
            },
        )

        state = ProjectState(module_path=module_path, approvals=[])
        write_json(self.state_path, state.to_dict())

        self.event_log.append({"event": "initialised", "module_path": module_path})
        return state

    def load(self) -> LoadedState:
        """Read the declared state, reporting problems instead of raising.

        An absent state file is not an error -- it means nothing has been
        approved yet, so an empty record is returned with no problems (B174). A
        corrupt or wrong-shaped file returns an empty record *with* a problem, so
        the caller can report it and still produce the rest of its answer (B175).

        The module path is read from config.json best-effort to complete the
        declared view; config has its own error reporting through load_config()
        (B73), so a missing or broken config is treated as "unknown" here rather
        than folded into state's problems.
        """
        module_path = self._module_path_best_effort()
        try:
            # read_json requires "approvals": a version-1 file (or any dict that
            # forgot it) is rejected here, and the two cases are told apart below.
            payload = read_json(self.state_path, required_keys=("approvals",))
        except StateFileMissing:
            # The whole point of the phase: a missing file is a usable answer,
            # not a failure. No approvals recorded, nothing to report (B174).
            return LoadedState(state=ProjectState(module_path=module_path), problems=[])
        except StateFileCorrupt as error:
            # Valid-JSON-but-wrong-shape lands here too (e.g. a top-level array),
            # because read_json validates shape and not merely syntax (B175).
            problem = self._outdated_file_problem() or str(error)
            return LoadedState(
                state=ProjectState(module_path=module_path), problems=[problem]
            )

        return self._interpret(payload, module_path)

    def _outdated_file_problem(self) -> str | None:
        """Describe a version-1 state file, or return None if it is not one.

        A v1 file is intact, not damaged -- it is simply from before Phase 6 --
        and saying "missing required key" about it is misleading. Recognition is
        by v1's own fields rather than by a version number, because the v1 writer
        emitted no "version" key at all; B172's ``"version": 2`` only helps a
        future v2->v3 move. Nothing is migrated: v1 recorded a phase and a status,
        both of which are derived now, so there is nothing in it worth keeping.
        """

        try:
            # Re-read with no required keys so the same parser and the same
            # shape rules apply; only the key requirement is relaxed. Doing the
            # parse by hand here would be a second reader free to disagree with
            # the first about what counts as a JSON object.
            payload = read_json(self.state_path)
        except (StateFileMissing, StateFileCorrupt):
            # Unreadable, not JSON, or not an object at all: that is genuine
            # damage, and the caller's original message already says so.
            return None

        if "approvals" in payload:
            return None
        if not ("phase" in payload and "status" in payload):
            return None

        return (
            f"{self.state_path} is a version 1 state file, written before phases "
            f"and statuses were derived rather than stored. Nothing in it needs "
            f"rescuing: delete the file and Atom will treat the project as having "
            f"no recorded approvals."
        )

    def load_config(self) -> dict[str, Any]:
        """Read config.json, the module path and onboarding commands (B73).

        Kept separate from load() because config and state fail separately: a
        broken config is a different problem, reported on its own, from a broken
        or absent state file.

        Raises:
            StateFileMissing: The project is not initialised.
            StateFileCorrupt: The config is damaged or missing its module path.
        """
        return read_json(self.config_path, required_keys=("module_path",))

    def record_approval(self, *, phase: str, gate: str, date: str) -> ProjectState:
        """Append an approval and persist it, preserving those already recorded.

        Appending rather than replacing is the point: approvals are project
        history, so a new gate must never erase an earlier one. Only state.json
        is written -- config.json is untouched. Loading uses the forgiving
        reader, so recording works even against a fresh ``.atom/``.
        """
        existing = self.load().state
        updated = ProjectState(
            module_path=existing.module_path,
            approvals=[*existing.approvals, Approval(phase=phase, gate=gate, date=date)],
        )
        write_json(self.state_path, updated.to_dict())
        return updated

    def _module_path_best_effort(self) -> str:
        """Read the module path from config.json, or "" if it cannot be read.

        Config's own errors are load_config()'s to report (B73), so they are
        swallowed here: this method only completes the composed view.
        """
        try:
            value = self.load_config().get("module_path", "")
        except (StateFileMissing, StateFileCorrupt):
            return ""
        return value if isinstance(value, str) else ""

    def _interpret(self, payload: dict[str, Any], module_path: str) -> LoadedState:
        """Turn a parsed object into a state, collecting shape problems (B175).

        ``read_json`` has already guaranteed a dict with an ``approvals`` key.
        What it cannot check is that ``approvals`` is a *list of approval
        objects* -- so that check lives here, and a violation is a reported
        problem rather than an exception that would crash the report.
        """
        problems: list[str] = []

        raw_approvals = payload["approvals"]
        approvals: list[Approval] = []
        if not isinstance(raw_approvals, list):
            problems.append(
                f"{self.state_path} is not usable state: 'approvals' should be a "
                f"list, found a {type(raw_approvals).__name__}."
            )
        else:
            for index, entry in enumerate(raw_approvals):
                if not isinstance(entry, dict):
                    problems.append(
                        f"{self.state_path} has a malformed approval at position "
                        f"{index}: expected an object, found a "
                        f"{type(entry).__name__}."
                    )
                    continue
                # Every field must be present *and* a string. The previous
                # version used str(entry.get(name, "")), which turned {} into an
                # apparently valid approval with blank fields -- silently
                # manufacturing a record that asserts a human approved something.
                # Coercion is not reading: str(7) is "7", which looks like a date.
                missing = [
                    name
                    for name in ("phase", "gate", "date")
                    if not isinstance(entry.get(name), str)
                ]
                if missing:
                    problems.append(
                        f"{self.state_path} has a malformed approval at position "
                        f"{index}: {', '.join(missing)} must each be a string."
                    )
                    continue
                approvals.append(
                    Approval(
                        phase=entry["phase"],
                        gate=entry["gate"],
                        date=entry["date"],
                    )
                )

        # A wrong-shaped approvals value is corruption; do not surface a
        # half-read approvals list beside the problem, to avoid a caller acting
        # on partial data.
        if problems:
            approvals = []

        return LoadedState(
            state=ProjectState(module_path=module_path, approvals=approvals),
            problems=problems,
        )
