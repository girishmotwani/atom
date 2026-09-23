"""Assemble what `atom status` knows about a project, derived from the repository.

Phase 6 changed the question this module answers. It no longer reads a declared
``state.json`` to learn where a project is; it *derives* that from the ``specs/``
tree (see ``atom.phases`` and the phase-06 design spec). ``state.json`` is
reduced to the two facts that genuinely cannot be observed -- configuration and
human approvals -- and its absence or corruption no longer stops status
answering. That is the entire point of the phase (B174/B175): the question was
previously unanswerable the moment the gitignored state file failed to survive a
clone, and now it is answerable from what is on disk.

Two rules from earlier phases survive unchanged and are called out because a
rewrite is exactly where a working feature gets dropped by accident (B183/B184):

* **Report everything at once** (B93/B180). A developer running ``status`` wants
  the whole picture, not the first thing that went wrong. This module never
  raises on a problem it can describe -- it collects problems into a report and
  lets the caller decide the exit code. That also keeps the JSON path parseable
  when the answer is "your state file is broken": a traceback on stderr and
  nothing on stdout would hide the failure from the automated caller most likely
  to have asked for JSON.

* **The startup temp-file sweep** (B81/B82) and the **unsaved-work check**
  (B83c) still run, and the sweep is still reported, never silent.

The one thing this module must never do is judge whether an artifact is
*finished*. The POC proved completeness is not derivable -- a 13-section design
spec truncated to its first four sections passed every structural rule tried
(F6-1). So the report carries *presence*, and the renderings say present/absent
and never complete/valid/sufficient. There is a test that fails if that leaks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from atom.phases import PHASE_DIR, Derivation, derive
from atom.runner import CommandRunner, SubprocessRunner
from atom.state import Approval, Project
from atom.storage import (
    UNSAVED_SUFFIX,
    StateFileCorrupt,
    SweptFile,
    sweep_temp_files,
)


@dataclass
class StatusReport:
    """Everything `atom status` derived and read, problems included.

    ``derivation`` is the authoritative account of where the project is: every
    phase, which one is current, and how that was resolved. The declared facts
    -- ``module_path`` and ``approvals`` -- sit beside it, and ``problems``
    gathers everything that went wrong along the way without any of it having
    stopped the report (B180).
    """

    root: Path
    derivation: Derivation
    module_path: str | None = None
    # ALL approvals across every phase. The text rendering shows only the current
    # phase's (B177); JSON carries the whole list so a program can filter (B179).
    approvals: list[Approval] = field(default_factory=list)
    last_event: dict[str, Any] | None = None
    problems: list[str] = field(default_factory=list)
    swept: list[SweptFile] = field(default_factory=list)
    damaged_log_lines: int = 0

    @property
    def could_answer(self) -> bool:
        """Whether Atom could answer the question at all -- this decides the exit code.

        After Phase 6 the answer is nearly always yes (B181). The phase and its
        artifacts are derived from the filesystem, so a missing or corrupt
        ``state.json`` no longer stops status: those are *problems*, reported and
        recovered, but the question is still answered. Non-zero is reserved for
        the one case where nothing can be derived -- a project root that cannot be
        read at all. A directory that merely is not an Atom project still reads
        fine and still gets a (mostly empty) answer, so it exits 0.
        """
        return self.root.is_dir()

    def to_dict(self) -> dict[str, Any]:
        """The JSON contract (B179).

        The documented keys -- ``root``, ``phase``, ``phase_source``,
        ``phase_started``, ``artifacts``, ``approvals``, ``problems``,
        ``phases`` -- are a guaranteed *subset*, not the whole object. B183
        separately requires that status keeps reporting the last event and any
        damaged log lines, so ``module_path``, ``last_event``, ``swept`` and
        ``damaged_log_lines`` ride along too. The JSON contract test asserts the
        documented keys are present, never that they are the only keys.
        """
        current = self.derivation.current
        return {
            # --- the documented subset (B179) ---------------------------------
            "root": str(self.root),
            "phase": current.name if current is not None else None,
            "phase_source": self.derivation.source,
            "phase_started": current.started if current is not None else None,
            # The current phase's artifact map: every required name -> present.
            "artifacts": dict(current.artifacts.present) if current is not None else {},
            "approvals": [approval.to_dict() for approval in self.approvals],
            "problems": list(self.problems),
            # Every phase, current one included (B179). Text gets one line each;
            # JSON gets the full map plus how many artifacts the phase requires.
            "phases": [
                {
                    "name": phase.name,
                    "artifacts": dict(phase.artifacts.present),
                    "required": len(phase.artifacts.required),
                }
                for phase in self.derivation.phases
            ],
            # --- carried beyond the documented subset (B183) ------------------
            "module_path": self.module_path,
            "last_event": self.last_event,
            "swept": [
                {"path": str(entry.path), "size_in_bytes": entry.size_in_bytes}
                for entry in self.swept
            ],
            "damaged_log_lines": self.damaged_log_lines,
        }


def collect_status(
    project: Project,
    runner: CommandRunner | None = None,
    specs_root: Path | None = None,
) -> StatusReport:
    """Gather everything known about ``project`` without raising on problems.

    Args:
        project: The project to report on.
        runner: How the current git branch is read. Defaults to a real
            subprocess runner; a test injects a fake to present a chosen branch.
        specs_root: The directory whose immediate children are phase directories.
            Defaults to resolving the project directory under ``<root>/specs``
            (B158a). A test may inject a materialised tree directly.

    The order of work matters only for the sweep, which runs first because a
    leftover temp file is evidence of a previous crash and clearing it is part of
    leaving the project in a good state (B81). Everything after it is independent
    and every step contributes to a single report (B93).
    """

    runner = runner if runner is not None else SubprocessRunner()

    # The startup sweep (B81) happens before anything is read, and is reported,
    # never silent (B82). This survives Phase 6 unchanged (B184).
    swept = sweep_temp_files(project.state_directory)

    report = StatusReport(
        root=project.root,
        derivation=_empty_derivation(),
        swept=swept,
    )

    for entry in swept:
        report.problems.append(
            f"removed a leftover temp file from a previous crash: "
            f"{entry.path.name} ({entry.size_in_bytes} bytes)"
        )

    # Unsaved work is reported until the developer deals with it (B83c). It is
    # checked independently of everything else, because it is a problem the
    # developer needs even when the rest of the project reads cleanly.
    _collect_unsaved_work(project, report)

    # The heart of the phase: derive the phase and its artifacts from the
    # filesystem. This never raises -- a missing specs tree yields no phases, a
    # failing git call falls back to lexical order (see atom.phases).
    if specs_root is not None:
        resolved_specs_root = specs_root
    else:
        resolved_specs_root = _resolve_project_dir(project.root / "specs", report)
    report.derivation = derive(resolved_specs_root, runner, project.root)
    # Only the current phase's status-parsing problems are surfaced by derive();
    # a missing artifact is never a problem, only information (B166).
    report.problems.extend(report.derivation.problems)

    # The declared facts. load() never raises: an absent file means "nothing
    # approved yet" (B174) and a corrupt one is a reported problem beside a full
    # report (B175). Either way the derivation above already answered the
    # question, so these only enrich it.
    loaded = project.load()
    report.problems.extend(loaded.problems)
    report.approvals = list(loaded.state.approvals)
    report.module_path = loaded.state.module_path or None

    # config.json fails separately from state.json (B73). A missing config is
    # normal for a directory that is not a project and is not worth a problem;
    # a *corrupt* config is, because it silently robbed the report of the module
    # path it would otherwise show.
    _collect_config_problems(project, report)

    # The event log is a surviving Phase 3 feature (B183): status keeps showing
    # the last event and counting any damaged lines.
    _collect_last_event(project, report)

    return report


def _empty_derivation() -> Derivation:
    """A derivation carrying no phases, used before the real one is computed.

    StatusReport requires a derivation to exist, and building one up front keeps
    ``report`` valid for the sweep/unsaved steps that run before derivation. It
    is always replaced by the real result before the report is returned.
    """

    return Derivation(phases=(), current=None, source="none", problems=[])


def _resolve_project_dir(specs_directory: Path, report: StatusReport) -> Path:
    """Resolve which directory under ``specs/`` holds the phases (B158a).

    The project directory is the immediate subdirectory of ``specs/`` that
    contains at least one phase directory. This repository has exactly one
    (``specs/atom-cli``) beside two loose ``.md`` files, which is why the rule
    was easy to leave unwritten -- and exactly why it is written here.

    Returns the resolved directory, or ``specs_directory`` itself when nothing
    under it looks like a project. Returning the parent in that case is
    deliberate: ``derive`` then finds no phase directories and reports "no
    current phase" (B164), while a branch that names a phase still resolves
    (B163). More than one candidate is a genuine ambiguity -- reported as a
    problem naming the candidates, with the lexically first used so status still
    answers rather than refusing.
    """

    if not specs_directory.is_dir():
        # No specs/ at all: hand derive a path with no phase children so it
        # reports no phases, rather than crashing on a missing directory.
        return specs_directory

    candidates = [
        child
        for child in sorted(specs_directory.iterdir(), key=lambda path: path.name)
        if child.is_dir() and _contains_a_phase_directory(child)
    ]

    if not candidates:
        return specs_directory

    if len(candidates) > 1:
        names = ", ".join(candidate.name for candidate in candidates)
        report.problems.append(
            f"specs/ has more than one project directory ({names}); "
            f"using {candidates[0].name}. If this is intentional, Atom reports "
            "against a single project -- move the others aside or configure which "
            "one to read."
        )

    return candidates[0]


def _contains_a_phase_directory(directory: Path) -> bool:
    """Whether ``directory`` has at least one immediate phase-shaped subdirectory."""

    return any(
        entry.is_dir() and PHASE_DIR.match(entry.name)
        for entry in directory.iterdir()
    )


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


def _collect_config_problems(project: Project, report: StatusReport) -> None:
    """Report a corrupt config.json, which otherwise hides the module path (B73).

    A *missing* config is not a problem here -- a directory that is not a project
    legitimately has none, and B174's spirit is that absence is not failure. Only
    corruption is surfaced, because a broken config silently removed a fact the
    report would otherwise have shown.
    """

    try:
        project.load_config()
    except StateFileCorrupt as error:
        report.problems.append(str(error))
    except Exception:
        # A missing config (StateFileMissing) or any other read miss is not a
        # problem status needs to raise: the module path simply stays unknown.
        return


def _collect_last_event(project: Project, report: StatusReport) -> None:
    """Show the most recent event, and count any damaged lines (B183, from B90/B91)."""

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
