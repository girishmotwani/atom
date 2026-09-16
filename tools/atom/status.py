"""Assembling and rendering what `atom status` knows about a project.

The guiding rule is B93, inherited from Phase 1's B17: report **everything at
once**. A developer running ``status`` wants the whole picture, not the first
thing that went wrong. So this module never raises on a problem it can
describe -- it collects problems into a report and lets the caller decide the
exit code.

That has a second benefit on the JSON path: a tool that asked for JSON gets
parseable output even when the answer is "your state file is broken". Printing
a traceback to stderr and nothing to stdout would make the failure invisible to
exactly the caller most likely to be automated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from atom.state import Project, ProjectState
from atom.storage import (
    UNSAVED_SUFFIX,
    StateFileCorrupt,
    StateFileMissing,
    SweptFile,
    sweep_temp_files,
)


@dataclass
class StatusReport:
    """Everything `atom status` found, problems included."""

    root: Path
    initialised: bool
    state: ProjectState | None = None
    module_path: str | None = None
    last_event: dict[str, Any] | None = None
    problems: list[str] = field(default_factory=list)
    swept: list[SweptFile] = field(default_factory=list)
    damaged_log_lines: int = 0

    @property
    def could_answer(self) -> bool:
        """Whether Atom could actually determine where the project is.

        This -- not the presence of problems -- decides the exit code (B95). An
        ``.unsaved`` file is a problem worth reporting but does not stop status
        answering its question, so it warns and still exits 0.
        """
        return self.state is not None

    def to_dict(self) -> dict[str, Any]:
        """The JSON contract (B97)."""
        return {
            "root": str(self.root),
            "initialised": self.initialised,
            "phase": self.state.phase.value if self.state else None,
            "status": self.state.status.value if self.state else None,
            "module_path": self.module_path,
            "last_event": self.last_event,
            "problems": list(self.problems),
            "swept": [
                {"path": str(entry.path), "size_in_bytes": entry.size_in_bytes}
                for entry in self.swept
            ],
            "damaged_log_lines": self.damaged_log_lines,
        }


def collect_status(project: Project) -> StatusReport:
    """Gather everything known about ``project`` without raising on problems."""

    # The startup sweep (B81) happens before anything is read: a leftover temp
    # file is evidence of a previous crash, and clearing it is part of leaving
    # the project in a good state. It is reported, never silent (B82).
    swept = sweep_temp_files(project.state_directory)

    report = StatusReport(
        root=project.root,
        initialised=project.is_initialised,
        swept=swept,
    )

    for entry in swept:
        report.problems.append(
            f"removed a leftover temp file from a previous crash: "
            f"{entry.path.name} ({entry.size_in_bytes} bytes)"
        )

    # Unsaved work is checked even when the state itself is unreadable, because
    # those two problems are independent and the developer needs both (B93).
    _collect_unsaved_work(project, report)

    try:
        report.state = project.load_state()
    except StateFileMissing as error:
        report.problems.append(str(error))
        return report
    except StateFileCorrupt as error:
        report.problems.append(str(error))
        # Deliberately falls through: config and the event log may still be
        # readable, and a developer whose state is broken needs the log most.

    _collect_config(project, report)
    _collect_last_event(project, report)

    return report


def _collect_unsaved_work(project: Project, report: StatusReport) -> None:
    """Report any `.unsaved` file until the developer deals with it (B83c)."""
    if not project.state_directory.is_dir():
        return

    for unsaved in sorted(project.state_directory.glob(f"*{UNSAVED_SUFFIX}")):
        report.problems.append(
            f"unsaved work is waiting in {unsaved.name} -- a previous command "
            f"could not write its state. Review it, then move it over "
            f"{unsaved.name.removesuffix(UNSAVED_SUFFIX)} or delete it."
        )


def _collect_config(project: Project, report: StatusReport) -> None:
    try:
        report.module_path = project.load_config().get("module_path")
    except (StateFileMissing, StateFileCorrupt) as error:
        # Config is separate from state (B73) and fails separately too.
        report.problems.append(str(error))


def _collect_last_event(project: Project, report: StatusReport) -> None:
    """Show the most recent event, and count any damaged lines (B90, B91)."""
    lines = project.event_log.read()
    report.damaged_log_lines = sum(1 for line in lines if line.is_damaged)

    if report.damaged_log_lines:
        report.problems.append(
            f"{report.damaged_log_lines} damaged line(s) in the event log were "
            "skipped -- most likely a process stopped mid-write."
        )

    valid = [line.record for line in lines if line.record is not None]
    if valid:
        report.last_event = valid[-1]
