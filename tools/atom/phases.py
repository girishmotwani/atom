"""Derive a project's phase state from the repository instead of a declared file.

This module answers two questions about a repository, using only what is
observable on disk plus the current git branch:

1. Which phase is current?
2. Which required artifacts does each phase have?

It is deliberately a *pure derivation engine*. It reports what exists; it never
judges whether what exists is finished. That refusal is the whole point of the
phase, and it is enforced here by three prohibitions the POC proved necessary
(`specs/atom-cli/phase-06-state/poc-report.md`):

- **Never report completeness.** A 13-section design spec truncated to its first
  4 sections passed every structural rule the POC tested (F6-1). Completeness is
  not derivable, so this module reports *presence* only and exposes no
  `complete`/`valid`/`sufficient` field.
- **Never count sections or bytes.** Those rules were fooled by a stub and
  rejected a genuine two-section document (F6-2). Presence is `Path.is_file`,
  nothing more.
- **Never read mtime.** Editing a file does not touch its directory's mtime, and
  creating a file in an *old* phase makes that phase newest immediately (F6-3).
  Ordering is lexical on the directory name, whose two-digit prefix makes lexical
  order numeric order.

The only file whose *content* is ever read is `poc-report.md`, and only for the
single frontmatter `status:` field that says whether a POC ran.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from atom.runner import CommandRunner

# A phase directory name. Anchored deliberately (B158): a stray folder must not
# masquerade as a phase. `\d{2}` is exactly two digits, so `phase-1-foo` is not a
# phase; the slug is lowercase alphanumerics and hyphens only.
PHASE_DIR = re.compile(r"^phase-(\d{2})-([a-z0-9-]+)$")

# The required artifact set (B165). This is not invented: it is the measured
# union of every file across all six existing phase directories. Order follows
# the design spec's listing.
REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "poc-brief.md",
    "poc-report.md",
    "design-spec.md",
    "test-spec.md",
    "tdd-log.md",
    "findings.md",
    "decisions.md",
)

# The closed status vocabulary (B171). Matched exactly and case-sensitively --
# never by substring -- because prose rephrasing breaks substring rules and this
# repository already accumulated four header conventions before anyone noticed.
POC_STATUSES: tuple[str, ...] = ("ran", "skipped")

# The single artifact whose requirement is conditional on a POC having run.
_CONDITIONAL_ARTIFACT = "poc-brief.md"

# The YAML frontmatter block: a `---` fence, its body, and a closing `---`, all
# at the very top of the file. We only ever look inside this block.
_FRONTMATTER_BLOCK = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---", re.DOTALL)

# A `status:` line within the frontmatter block. The value is captured raw and
# its surrounding quotes are stripped afterwards, so quoted and unquoted forms
# are treated alike before the exact-match check.
_STATUS_LINE = re.compile(r"(?m)^[ \t]*status[ \t]*:[ \t]*(.+?)[ \t]*$")


@dataclass(frozen=True)
class PhaseArtifacts:
    """The presence of each required artifact for one phase.

    Reports presence, never completeness -- see the module docstring and F6-1.
    `present` maps every required-artifact name to a boolean; `required` is the
    subset that actually counts for this phase (poc-brief.md is conditional);
    `problems` holds only status-parsing problems, never missing files (a
    missing artifact is information, not a failure).
    """

    present: dict[str, bool]
    required: tuple[str, ...]
    problems: list[str]


@dataclass(frozen=True)
class Phase:
    """One phase of a project, and the artifacts observed for it.

    `directory` is None when a branch names a phase that has no directory yet
    (B163); `started` is simply whether that directory exists.
    """

    name: str
    number: int
    slug: str
    directory: Path | None
    started: bool
    artifacts: PhaseArtifacts


@dataclass(frozen=True)
class Derivation:
    """The full derived answer: every phase, which is current, and how it was chosen.

    `source` names how `current` was resolved -- "branch", "lexical", or "none"
    -- because B163 lets a typo'd branch report as a pristine new phase and B162
    silently falls back, so a developer seeing an unexpected answer needs to know
    which rule produced it (B177).
    """

    phases: tuple[Phase, ...]
    current: Phase | None
    source: str
    problems: list[str]


def discover_phases(specs_root: Path) -> tuple[Phase, ...]:
    """Return every phase directory under `specs_root`, in lexical order.

    Non-matching entries are ignored silently (B159). An absent `specs_root` is
    not a crash -- it yields no phases (B164).
    """

    if not specs_root.is_dir():
        return ()

    phases: list[Phase] = []
    # Sort by name so the ordering is lexical (B160). mtime is never consulted,
    # for the reasons in the module docstring (F6-3).
    for entry in sorted(specs_root.iterdir(), key=lambda path: path.name):
        if entry.is_dir() and PHASE_DIR.match(entry.name):
            phases.append(_build_phase(entry.name, entry))
    return tuple(phases)


def derive(specs_root: Path, runner: CommandRunner, working_directory: Path) -> Derivation:
    """Resolve the current phase and every phase's artifacts for a repository.

    The current phase is the branch when the branch names a phase (B161), even
    when that phase has no directory (B163); otherwise it is the lexically
    greatest phase directory (B162); and when there is neither, there is no
    current phase (B164). None of these is an error.
    """

    phases = list(discover_phases(specs_root))
    phases_by_name = {phase.name: phase for phase in phases}

    branch = _current_branch(runner, working_directory)

    if branch is not None and PHASE_DIR.match(branch):
        # B161/B163: the branch names the current phase. If no directory exists
        # for it, report it as a not-started phase rather than an error -- creating
        # the branch before the directory is the ordinary first move of a phase.
        if branch in phases_by_name:
            current = phases_by_name[branch]
        else:
            current = _build_phase(branch, None)
            # Keep the full phase list complete and lexically ordered so callers
            # that render every phase (B179) see the new one in its right place.
            phases.append(current)
            phases.sort(key=lambda phase: phase.name)
        source = "branch"
    elif phases:
        # B162: no phase branch, so fall back to the lexically greatest directory.
        current = phases[-1]
        source = "lexical"
    else:
        # B164: nothing names a phase and none exist on disk.
        current = None
        source = "none"

    problems = list(current.artifacts.problems) if current is not None else []
    return Derivation(phases=tuple(phases), current=current, source=source, problems=problems)


def _build_phase(name: str, directory: Path | None) -> Phase:
    """Assemble a Phase from its name and (possibly absent) directory."""

    match = PHASE_DIR.match(name)
    # Callers only ever pass names that already matched PHASE_DIR.
    assert match is not None, f"not a phase name: {name!r}"
    return Phase(
        name=name,
        number=int(match.group(1)),
        slug=match.group(2),
        directory=directory,
        started=directory is not None,
        artifacts=_derive_artifacts(name, directory),
    )


def _derive_artifacts(name: str, directory: Path | None) -> PhaseArtifacts:
    """Derive artifact presence and the required subset for one phase.

    Presence is `Path.is_file` and nothing else (B166/B167): an empty file is
    present, a directory sharing an artifact's name is not.
    """

    present = {
        artifact: (directory is not None and (directory / artifact).is_file())
        for artifact in REQUIRED_ARTIFACTS
    }

    problems: list[str] = []
    # B168: only an explicit `skipped` token excuses the brief. Every other
    # condition -- `ran`, an unrecognised token, a missing `status:` line, or no
    # poc-report.md at all -- leaves it required. The rule leans toward asking
    # for more evidence: over-requiring is resolved by declaring the skip, while
    # under-requiring hides a document that is genuinely owed.
    brief_required = True
    if present["poc-report.md"]:
        # `directory` is not None here, because the report was found inside it.
        status, problem = _read_poc_status(name, directory / "poc-report.md")
        if problem is not None:
            problems.append(problem)
        if status == "skipped":
            brief_required = False
    # B170: when poc-report.md is absent the question "did a POC run?" has no
    # answer. The brief stays required -- absent is a statement about presence,
    # not about requirement, so it is reported absent-and-owed -- and no problem
    # beyond the two absences is raised. `brief_required` stays True.

    required = tuple(
        artifact
        for artifact in REQUIRED_ARTIFACTS
        if artifact != _CONDITIONAL_ARTIFACT or brief_required
    )
    return PhaseArtifacts(present=present, required=required, problems=problems)


def _read_poc_status(name: str, poc_report: Path) -> tuple[str | None, str | None]:
    """Return the recognised status token, or None plus a problem describing why.

    The token is one of POC_STATUSES when the frontmatter declares it exactly;
    otherwise the token is None and a problem is returned (B169). This is the
    only place any artifact's content is read (B167).
    """

    text = poc_report.read_text(encoding="utf-8", errors="replace")

    block_match = _FRONTMATTER_BLOCK.search(text)
    # Only the frontmatter block is searched; a `status:` line in the body is not
    # a declaration. No frontmatter means no declared status.
    block = block_match.group(1) if block_match is not None else ""

    status_match = _STATUS_LINE.search(block)
    if status_match is None:
        return None, (
            f"{name}: poc-report.md declares no status field; "
            "poc-brief.md is treated as required."
        )

    value = _strip_quotes(status_match.group(1).strip())
    # B171: exact, case-sensitive match against the closed vocabulary. A value
    # that merely contains "skipped", or rephrases it in prose, does not count.
    if value in POC_STATUSES:
        return value, None

    return None, (
        f"{name}: poc-report.md declares an unrecognised status {value!r}; "
        "poc-brief.md is treated as required."
    )


def _strip_quotes(value: str) -> str:
    """Remove a single pair of matching surrounding quotes, if present."""

    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _current_branch(runner: CommandRunner, working_directory: Path) -> str | None:
    """Return the current git branch name, or None when it cannot be determined.

    A failed git call falls back to None so the caller can use lexical ordering
    (B162) rather than crashing. Real git output carries a trailing newline, and
    a detached HEAD prints an empty string; both collapse to None-or-name here.
    """

    result = runner.run(["git", "branch", "--show-current"], working_directory)
    if not result.succeeded:
        return None
    return result.stdout.strip() or None
