"""Behaviour tests for `atom status`, rewritten against derivation (B177-B185).

Phase 6 turned `atom status` from a reader of a declared `state.json` into a
reporter of what the repository *shows*. These tests build real specs trees
under pytest's `tmp_path` and drive the current git branch through the
established `CommandRunner` seam, exactly as the derivation-engine tests do, so
that the thing under test is the shape of the filesystem plus the branch.

The output layer is where the phase's central prohibition (F6-1) can leak: a
helpful-looking "complete" column is the intuitive thing to add and the one
thing the POC proved cannot be computed. `test_no_rendering_describes_any_
artifact_as_complete` is the tripwire against that regression and is written to
be hard to satisfy accidentally.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from atom.phases import REQUIRED_ARTIFACTS
from atom.report import (
    render_status_json,
    render_status_problems,
    render_status_text,
)
from atom.state import Project
from atom.status import collect_status
from atom.storage import TEMP_SUFFIX, UNSAVED_SUFFIX
from tests.conftest import FakeRunner, command_result

# The eight documented JSON keys (B179). They are a guaranteed *subset* of the
# object, never the whole of it -- B183 adds more that ride alongside.
DOCUMENTED_JSON_KEYS = {
    "root",
    "phase",
    "phase_source",
    "phase_started",
    "artifacts",
    "approvals",
    "problems",
    "phases",
}


# ---------------------------------------------------------------------------
# Helpers -- a compact vocabulary for a specs tree, a branch, and declared state.
# ---------------------------------------------------------------------------

def poc_report(status: str = "ran") -> str:
    """Render a `poc-report.md` whose frontmatter carries the given status."""

    return (
        "---\n"
        'project: "x"\n'
        'phase: "p"\n'
        f'status: "{status}"\n'
        "---\n\nbody text\n"
    )


def full_files(status: str = "ran", brief: bool = True) -> dict[str, str]:
    """A filename->content map holding every required artifact for a phase."""

    files = {name: f"# {name}\n\ncontent\n" for name in REQUIRED_ARTIFACTS}
    files["poc-report.md"] = poc_report(status=status)
    if not brief:
        del files["poc-brief.md"]
    return files


def some_files(names: tuple[str, ...], status: str = "ran") -> dict[str, str]:
    """A phase directory holding only `names` (plus a `status` if a report is in it)."""

    files = {name: f"# {name}\n\ncontent\n" for name in names}
    if "poc-report.md" in files:
        files["poc-report.md"] = poc_report(status=status)
    return files


def materialise(specs_root: Path, tree: dict[str, dict[str, str]]) -> Path:
    """Write `tree` (phase dir name -> filename -> content) under `specs_root`."""

    specs_root.mkdir(parents=True, exist_ok=True)
    for phase_name, files in tree.items():
        directory = specs_root / phase_name
        directory.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            (directory / filename).write_text(content, encoding="utf-8")
    return specs_root


def runner_on_branch(branch: str, cwd: Path) -> FakeRunner:
    """A runner whose `git branch --show-current` prints `branch` (plus a newline)."""

    command = ("git", "branch", "--show-current")
    return FakeRunner(
        {command: command_result(command, cwd, exit_code=0, stdout=f"{branch}\n")}
    )


def write_state(root: Path, approvals: list[dict[str, str]]) -> None:
    """Write a well-formed `.atom/state.json` carrying `approvals`."""

    state_directory = root / ".atom"
    state_directory.mkdir(parents=True, exist_ok=True)
    payload = {"version": 2, "approvals": approvals}
    (state_directory / "state.json").write_text(json.dumps(payload), encoding="utf-8")


def corrupt_state(root: Path) -> None:
    """Write a `.atom/state.json` that is not valid JSON."""

    state_directory = root / ".atom"
    state_directory.mkdir(parents=True, exist_ok=True)
    (state_directory / "state.json").write_text("{ this is not json", encoding="utf-8")


def collect(
    tmp_path: Path,
    tree: dict[str, dict[str, str]] | None = None,
    branch: str = "main",
    approvals: list[dict[str, str]] | None = None,
):
    """Collect a status report for a project rooted at `tmp_path`.

    `specs_root` is injected directly at the project directory (`specs/atom-cli`)
    so the tests exercise the derivation-and-output path without depending on the
    project-directory resolution, which has no directory data to disambiguate
    here anyway.
    """

    specs_root = tmp_path / "specs" / "atom-cli"
    if tree is not None:
        materialise(specs_root, tree)
    if approvals is not None:
        write_state(tmp_path, approvals)
    project = Project(tmp_path)
    runner = runner_on_branch(branch, tmp_path)
    return collect_status(project, runner=runner, specs_root=specs_root)


# ===========================================================================
# Output -- text (B177)
# ===========================================================================

def test_the_text_rendering_names_the_project_root(tmp_path):
    report = collect(tmp_path, {"phase-01-check": full_files()})
    text = render_status_text(report, use_colour=False)
    assert str(tmp_path) in text


def test_the_text_rendering_names_the_current_phase(tmp_path):
    report = collect(tmp_path, {"phase-01-check": full_files()}, branch="main")
    text = render_status_text(report, use_colour=False)
    assert "Phase:" in text
    assert "phase-01-check" in text


def test_the_text_rendering_says_the_phase_came_from_the_branch(tmp_path):
    # Branch names the phase, so the source is the branch (B161/B177).
    report = collect(tmp_path, {"phase-01-check": full_files()}, branch="phase-01-check")
    assert report.derivation.source == "branch"
    text = render_status_text(report, use_colour=False)
    assert "resolved from the git branch" in text


def test_the_text_rendering_says_the_phase_came_from_the_fallback(tmp_path):
    # `main` names no phase, so the source is the lexical fallback (B162/B177).
    report = collect(tmp_path, {"phase-01-check": full_files()}, branch="main")
    assert report.derivation.source == "lexical"
    text = render_status_text(report, use_colour=False)
    assert "fallback" in text


def test_the_text_rendering_lists_every_required_artifact(tmp_path):
    report = collect(tmp_path, {"phase-02-poc": full_files()}, branch="phase-02-poc")
    text = render_status_text(report, use_colour=False)
    for name in REQUIRED_ARTIFACTS:
        assert name in text, f"{name} missing from the artifact table"


def test_the_text_rendering_shows_a_recorded_approval(tmp_path):
    approvals = [{"phase": "phase-02-poc", "gate": "design-spec", "date": "2026-09-24"}]
    report = collect(
        tmp_path, {"phase-02-poc": full_files()}, branch="phase-02-poc", approvals=approvals
    )
    text = render_status_text(report, use_colour=False)
    assert "design-spec" in text
    assert "2026-09-24" in text


# ===========================================================================
# Output -- the per-phase summary (B178)
# ===========================================================================

def test_every_other_phase_gets_one_summary_line(tmp_path):
    tree = {
        "phase-01-check": full_files(status="skipped", brief=False),
        "phase-02-poc": full_files(),
        "phase-03-state": full_files(),
    }
    report = collect(tmp_path, tree, branch="main")  # current is phase-03 (lexical)
    text = render_status_text(report, use_colour=False)
    summary = text.split("Other phases:", 1)[1]
    # The two non-current phases each appear exactly once in the summary block.
    assert summary.count("phase-01-check") == 1
    assert summary.count("phase-02-poc") == 1


def test_the_summary_line_reports_present_over_required(tmp_path):
    # An "other" phase holding four of its seven required artifacts summarises 4/7.
    partial = some_files(("poc-report.md", "poc-brief.md", "design-spec.md", "test-spec.md"))
    tree = {"phase-01-check": partial, "phase-05-ship": full_files()}
    report = collect(tmp_path, tree, branch="main")  # current is phase-05
    text = render_status_text(report, use_colour=False)
    assert "phase-01-check" in text
    assert "4/7" in text


def test_a_skipped_poc_phase_summarises_out_of_six(tmp_path):
    # Phase 1 skipped its POC, so it owes six artifacts, not seven. It must read
    # 6/6 -- never 6/7 (which would look permanently incomplete) and never 7/7.
    tree = {
        "phase-01-check": full_files(status="skipped", brief=False),
        "phase-02-poc": full_files(),
    }
    report = collect(tmp_path, tree, branch="main")  # current is phase-02
    text = render_status_text(report, use_colour=False)
    summary = text.split("Other phases:", 1)[1]
    assert "6/6" in summary
    assert "6/7" not in summary
    assert "7/7" not in summary


def test_the_current_phase_is_not_repeated_in_the_summary(tmp_path):
    tree = {"phase-01-check": full_files(), "phase-02-poc": full_files()}
    report = collect(tmp_path, tree, branch="phase-02-poc")  # current is phase-02
    text = render_status_text(report, use_colour=False)
    summary = text.split("Other phases:", 1)[1]
    assert "phase-02-poc" not in summary
    assert "phase-01-check" in summary


def test_the_summary_is_ordered_lexically(tmp_path):
    # Deliberately materialise out of order; the summary must still be sorted.
    tree = {
        "phase-03-state": full_files(),
        "phase-01-check": full_files(status="skipped", brief=False),
        "phase-02-poc": full_files(),
    }
    report = collect(tmp_path, tree, branch="phase-03-state")  # current is phase-03
    text = render_status_text(report, use_colour=False)
    summary = text.split("Other phases:", 1)[1]
    assert summary.index("phase-01-check") < summary.index("phase-02-poc")


# ===========================================================================
# Output -- JSON (B179)
# ===========================================================================

def test_the_json_contract_has_the_documented_keys(tmp_path):
    report = collect(tmp_path, {"phase-01-check": full_files()})
    payload = json.loads(render_status_json(report))
    # A subset assertion, not equality: B183 adds keys beyond the documented set.
    assert DOCUMENTED_JSON_KEYS.issubset(payload.keys())


def test_the_json_phases_array_covers_every_phase(tmp_path):
    tree = {
        "phase-01-check": full_files(status="skipped", brief=False),
        "phase-02-poc": full_files(),
        "phase-03-state": full_files(),
    }
    report = collect(tmp_path, tree, branch="main")
    payload = json.loads(render_status_json(report))
    names = [entry["name"] for entry in payload["phases"]]
    assert names == ["phase-01-check", "phase-02-poc", "phase-03-state"]


def test_the_json_phases_array_includes_the_current_phase(tmp_path):
    report = collect(tmp_path, {"phase-02-poc": full_files()}, branch="phase-02-poc")
    payload = json.loads(render_status_json(report))
    names = [entry["name"] for entry in payload["phases"]]
    assert payload["phase"] == "phase-02-poc"
    assert "phase-02-poc" in names


def test_the_json_artifact_map_is_name_to_boolean(tmp_path):
    report = collect(tmp_path, {"phase-02-poc": full_files()}, branch="phase-02-poc")
    payload = json.loads(render_status_json(report))
    artifacts = payload["artifacts"]
    assert set(artifacts.keys()) == set(REQUIRED_ARTIFACTS)
    assert all(isinstance(value, bool) for value in artifacts.values())


def test_the_json_is_parseable_when_problems_exist(tmp_path):
    # A corrupt state file is bad news; the JSON must still parse (B175/B179).
    materialise(tmp_path / "specs" / "atom-cli", {"phase-01-check": full_files()})
    corrupt_state(tmp_path)
    project = Project(tmp_path)
    report = collect_status(
        project,
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    payload = json.loads(render_status_json(report))  # must not raise
    assert payload["problems"], "a corrupt state file should surface a problem"
    assert payload["phase"] == "phase-01-check"


# ===========================================================================
# Output -- report everything (B180)
# ===========================================================================

def test_two_problems_are_both_reported(tmp_path):
    # Two independent problem sources: a swept temp file and unsaved work.
    state_directory = tmp_path / ".atom"
    state_directory.mkdir(parents=True)
    (state_directory / f"leftover{TEMP_SUFFIX}").write_text("junk", encoding="utf-8")
    (state_directory / f"state.json{UNSAVED_SUFFIX}").write_text("draft", encoding="utf-8")

    project = Project(tmp_path)
    report = collect_status(
        project,
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    blob = "\n".join(report.problems)
    assert "leftover" in blob
    assert "unsaved" in blob
    assert len(report.problems) >= 2


def test_a_problem_does_not_suppress_the_rest_of_the_report(tmp_path):
    # A corrupt state file is a problem, but the derived phase and artifacts must
    # still be reported in full (B175/B180) -- that is the whole point of Phase 6.
    materialise(tmp_path / "specs" / "atom-cli", {"phase-02-poc": full_files()})
    corrupt_state(tmp_path)
    project = Project(tmp_path)
    report = collect_status(
        project,
        runner=runner_on_branch("phase-02-poc", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    assert report.problems, "the corrupt state file should be reported"
    assert report.derivation.current is not None
    assert report.derivation.current.name == "phase-02-poc"
    assert all(report.derivation.current.artifacts.present.values())


# ===========================================================================
# Output -- exit code (B181, amended)
#
# B181 originally reserved a non-zero exit for "a project root that cannot be
# read at all". That condition was measured to be unreachable (F6-D6): status
# takes no --root, so the root is the process's cwd, which necessarily exists.
# The amended behaviour is simpler and honest -- `atom status` is a report, and
# a report always exits 0. These tests pin that, and the guard below pins the
# *absence* of the machinery, so it cannot quietly return.
# ===========================================================================

def test_a_phase_missing_artifacts_still_answers(tmp_path):
    # Missing artifacts are information, not failure: status still answered.
    partial = some_files(("design-spec.md",))
    report = collect(tmp_path, {"phase-02-poc": partial}, branch="phase-02-poc")
    assert report.derivation.current is not None


def test_a_project_with_no_phases_still_answers(tmp_path):
    report = collect(tmp_path, tree={}, branch="main")
    assert report.derivation.current is None
    assert report.problems == []


def test_a_corrupt_state_file_still_answers(tmp_path):
    materialise(tmp_path / "specs" / "atom-cli", {"phase-01-check": full_files()})
    corrupt_state(tmp_path)
    project = Project(tmp_path)
    report = collect_status(
        project,
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    assert report.problems
    assert report.derivation.current is not None


def test_an_unreadable_project_root_is_reported_not_raised(tmp_path):
    """The case B181 reserved a non-zero exit for still must not crash."""
    missing_root = tmp_path / "does-not-exist"
    project = Project(missing_root)
    report = collect_status(
        project,
        runner=runner_on_branch("main", missing_root),
        specs_root=missing_root / "specs" / "atom-cli",
    )
    assert report.derivation.current is None


def test_the_status_report_exposes_no_could_answer(tmp_path):
    """F6-D6: the property drove a branch that could never run. It is gone.

    Asserted by `hasattr` rather than by behaviour, because a reintroduced
    `could_answer` would otherwise sit unused and untested until someone wired
    an exit code back to it.
    """
    report = collect(tmp_path, tree={}, branch="main")
    assert not hasattr(report, "could_answer")


# ===========================================================================
# What is removed -- surviving behaviour (B184)
# ===========================================================================

def test_the_temp_file_sweep_still_runs(tmp_path):
    # B81/B82 survive the rewrite: a leftover .tmp is removed at startup.
    state_directory = tmp_path / ".atom"
    state_directory.mkdir(parents=True)
    leftover = state_directory / f"design-spec.md{TEMP_SUFFIX}"
    leftover.write_text("half a write", encoding="utf-8")

    project = Project(tmp_path)
    report = collect_status(
        project,
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    assert [entry.path.name for entry in report.swept] == [leftover.name]
    assert not leftover.exists(), "the swept temp file should be gone"


def test_the_sweep_is_still_reported_never_silent(tmp_path):
    # B82: the sweep must leave a trace, so a crash is never silently hidden.
    state_directory = tmp_path / ".atom"
    state_directory.mkdir(parents=True)
    (state_directory / f"leftover{TEMP_SUFFIX}").write_text("junk", encoding="utf-8")

    project = Project(tmp_path)
    report = collect_status(
        project,
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    assert any("leftover" in problem for problem in report.problems)


# ===========================================================================
# The prohibition -- presence, never completeness (F6-1)
# ===========================================================================

# The forbidden vocabulary, matched on WORD BOUNDARIES. The boundaries are what
# make the test meaningful rather than trivially true:
#   * It WOULD catch a real regression: a "[x] complete" column, a "valid" badge,
#     an "ok"/"done"/"finished" verdict beside an artifact -- exactly the kind of
#     completeness signal the POC proved cannot be computed (F6-1).
#   * It would NOT fire on innocent substrings: "broken"/"token"/"look" contain
#     "ok", "invalidate" contains "valid", "abandoned" contains "done" -- none of
#     which are the whole-word verdicts the prohibition targets. Word boundaries
#     let the real text through while still failing on a genuine "complete" label.
# The report deliberately carries NO problems (nothing is swept, unsaved, or
# corrupt) so the scan sees only the rendered answer, not recovery prose that
# might legitimately contain these words.
_FORBIDDEN_COMPLETENESS_WORDS = re.compile(
    r"\b(complete|valid|sufficient|done|finished|ok)\b", re.IGNORECASE
)


def test_no_rendering_describes_any_artifact_as_complete(tmp_path):
    # A phase with a deliberate mix of present and absent artifacts: the report
    # has real presence data to describe, so a completeness label would have
    # something to attach to if the code tried to emit one.
    present_subset = some_files(("poc-report.md", "design-spec.md"))
    report = collect(tmp_path, {"phase-02-poc": present_subset}, branch="phase-02-poc")

    # Sanity-check the fixture actually mixes the two states, so the test is not
    # passing merely because there was nothing to mislabel.
    presence = report.derivation.current.artifacts.present
    assert any(presence.values()) and not all(presence.values())

    text = render_status_text(report, use_colour=False)
    payload = render_status_json(report)

    for label, rendered in (("text", text), ("json", payload)):
        match = _FORBIDDEN_COMPLETENESS_WORDS.search(rendered)
        assert match is None, (
            f"{label} rendering describes an artifact with the forbidden word "
            f"{match.group(0)!r}; Atom reports presence, never completeness (F6-1)"
        )


# ===========================================================================
# The default entry point and the enrichment paths
# ---------------------------------------------------------------------------
# These exercise the parts of collect_status the behaviour tests inject around:
# the real defaults the CLI relies on (a SubprocessRunner and project-directory
# resolution under specs/), and the config/event-log enrichment that B183 keeps.
# ===========================================================================

def _collect_with_defaults(tmp_path: Path):
    """Call collect_status the way the CLI does: no injected runner, no specs_root.

    The default runner is a real SubprocessRunner. `tmp_path` is not a git
    repository, so `git branch --show-current` fails and derivation falls back to
    lexical order deterministically, regardless of whether git is installed.
    """

    return collect_status(Project(tmp_path))


def test_the_default_runner_and_project_resolution_are_used(tmp_path):
    # A real specs tree, resolved from <root>/specs with the real default runner.
    materialise(
        tmp_path / "specs" / "atom-cli",
        {"phase-01-check": full_files(status="skipped", brief=False), "phase-02-poc": full_files()},
    )
    report = _collect_with_defaults(tmp_path)
    assert report.derivation.source == "lexical"
    assert report.derivation.current is not None
    assert [phase.name for phase in report.derivation.phases] == [
        "phase-01-check",
        "phase-02-poc",
    ]


def test_the_default_path_without_a_specs_directory_reports_no_phases(tmp_path):
    # No specs/ at all: resolution returns the (absent) directory and derive
    # finds nothing, but status still answers (B164/B181).
    report = _collect_with_defaults(tmp_path)
    assert report.derivation.phases == ()
    assert report.derivation.current is None
    assert report.problems == []


def test_a_specs_directory_without_a_project_reports_no_phases(tmp_path):
    # specs/ exists but no immediate subdirectory holds a phase directory, so
    # there is no project directory to resolve (B158a) and thus no phases.
    notes = tmp_path / "specs" / "notes"
    notes.mkdir(parents=True)
    (notes / "readme.md").write_text("not a phase", encoding="utf-8")
    report = _collect_with_defaults(tmp_path)
    assert report.derivation.phases == ()
    assert report.derivation.current is None
    # B158a zero-candidate case: no phases, source "none", and -- crucially --
    # no problem reported. An empty project is legitimate, not an error (B164).
    assert report.derivation.source == "none"
    assert not any("project directory" in problem for problem in report.problems)


def test_more_than_one_project_directory_is_reported_and_the_first_used(tmp_path):
    # Two candidate project directories is a genuine ambiguity (B158a): reported
    # as a problem naming both, with the lexically first used so status answers.
    materialise(tmp_path / "specs" / "alpha", {"phase-01-check": full_files()})
    materialise(tmp_path / "specs" / "beta", {"phase-02-poc": full_files()})
    report = _collect_with_defaults(tmp_path)
    ambiguity = [problem for problem in report.problems if "more than one project" in problem]
    assert ambiguity, "the ambiguity should be reported"
    assert "alpha" in ambiguity[0] and "beta" in ambiguity[0]
    # The lexically first candidate (alpha) is the one whose phases are reported.
    assert [phase.name for phase in report.derivation.phases] == ["phase-01-check"]


def test_a_project_directory_beside_loose_phase_directories_is_reported(tmp_path):
    """F6-D10: a half-migrated layout must not drop phases in silence.

    `specs/` holding both a project directory and loose phase directories is the
    shape of an unfinished move to B158a. Resolution picks the project directory
    and the loose phases are never scanned -- which is defensible -- but saying
    nothing is not: the developer sees a phase list with entries missing and no
    indication that anything was skipped.
    """
    materialise(tmp_path / "specs" / "proj", {"phase-05-ship": full_files()})
    materialise(tmp_path / "specs", {"phase-01-check": full_files(), "phase-02-poc": full_files()})

    report = _collect_with_defaults(tmp_path)

    ignored = [problem for problem in report.problems if "phase-01-check" in problem]
    assert ignored, "the ignored loose phase directories should be reported"
    assert "phase-02-poc" in ignored[0], "every ignored phase is named, not just the first"
    assert "proj" in ignored[0], "the report says which directory won"


def test_the_mixed_layout_still_reports_the_project_directory_phases(tmp_path):
    """Reporting the ambiguity must not change which phases are used."""
    materialise(tmp_path / "specs" / "proj", {"phase-05-ship": full_files()})
    materialise(tmp_path / "specs", {"phase-01-check": full_files()})

    report = _collect_with_defaults(tmp_path)

    assert [phase.name for phase in report.derivation.phases] == ["phase-05-ship"]


def test_a_flat_layout_is_accepted_without_comment(tmp_path):
    """The deliberate other half of F6-D10: loose phases *alone* are supported.

    With no project directory to compete with, `specs/phase-NN-slug` is
    unambiguous. Atom reads it and says nothing, so the pre-B158a layout keeps
    working. This test exists to stop the mixed-layout fix above from leaking
    into the unambiguous case.
    """
    materialise(tmp_path / "specs", {"phase-01-check": full_files(), "phase-02-poc": full_files()})

    report = _collect_with_defaults(tmp_path)

    assert [phase.name for phase in report.derivation.phases] == [
        "phase-01-check",
        "phase-02-poc",
    ]
    assert report.problems == []


def test_real_repository_reports_multiple_projects_and_atom_cli_history_remains_readable():
    # The real repository now contains more than one Atom project. Resolution
    # must report that ambiguity and choose the lexically first one, while the
    # long-running atom-cli project's phase history remains directly readable.
    from atom.phases import Derivation, discover_phases
    from atom.status import StatusReport, _resolve_project_dir

    repo_root = Path(__file__).resolve().parents[2]
    real_specs = repo_root / "specs"

    report = StatusReport(
        root=repo_root,
        derivation=Derivation(phases=(), current=None, source="none", problems=[]),
    )
    resolved = _resolve_project_dir(real_specs, report)

    assert resolved == real_specs / "artifact-writer"
    ambiguity = [problem for problem in report.problems if "more than one project" in problem]
    assert ambiguity
    assert "artifact-writer" in ambiguity[0]
    assert "atom-cli" in ambiguity[0]

    names = [phase.name for phase in discover_phases(real_specs / "atom-cli")]
    for expected in (
        "phase-01-check",
        "phase-02-poc",
        "phase-03-state",
        "phase-04-review",
        "phase-05-ship",
        "phase-06-state",
    ):
        assert expected in names, f"{expected} not found under {resolved}"
    assert len(names) >= 6


def test_a_corrupt_config_is_reported_separately(tmp_path):
    # A broken config.json silently removes the module path, so it is surfaced as
    # a problem (B73). Config fails independently of state.
    state_directory = tmp_path / ".atom"
    state_directory.mkdir(parents=True)
    (state_directory / "config.json").write_text("{ not json", encoding="utf-8")

    report = collect_status(
        Project(tmp_path),
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    assert any("config.json" in problem for problem in report.problems)
    assert report.module_path is None


def test_the_last_event_and_damaged_lines_are_reported(tmp_path):
    # B183 survives: status still shows the last event and counts damaged lines.
    state_directory = tmp_path / ".atom"
    state_directory.mkdir(parents=True)
    (state_directory / "events.jsonl").write_text(
        '{"event": "initialised", "at": "2026-01-01"}\n'
        "half a line that never finished\n",
        encoding="utf-8",
    )

    report = collect_status(
        Project(tmp_path),
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    assert report.last_event == {"event": "initialised", "at": "2026-01-01"}
    assert report.damaged_log_lines == 1
    assert any("damaged" in problem for problem in report.problems)


# ===========================================================================
# Rendering branches -- the text and problem renderers end to end
# ---------------------------------------------------------------------------
# These pin the renderer branches the behaviour tests above do not reach on
# their own: the module line, a not-started phase, the no-phase project, the
# last-event line, and the stderr problem renderer in each of its colour states.
# ===========================================================================

def _write_config(root: Path, module_path: str) -> None:
    """Write a `.atom/config.json` carrying `module_path`."""

    state_directory = root / ".atom"
    state_directory.mkdir(parents=True, exist_ok=True)
    (state_directory / "config.json").write_text(
        json.dumps({"module_path": module_path}), encoding="utf-8"
    )


def test_the_text_rendering_shows_the_module_path(tmp_path):
    _write_config(tmp_path, "example.com/widgets")
    report = collect(tmp_path, {"phase-01-check": full_files()})
    text = render_status_text(report, use_colour=False)
    assert "Module:  example.com/widgets" in text


def test_the_text_rendering_marks_a_not_started_phase(tmp_path):
    # A branch naming a phase with no directory (B163): reported, not started.
    report = collect(tmp_path, {"phase-01-check": full_files()}, branch="phase-09-ghost")
    assert report.derivation.current.name == "phase-09-ghost"
    assert report.derivation.current.started is False
    text = render_status_text(report, use_colour=False)
    assert "not started" in text


def test_the_text_rendering_states_when_there_is_no_current_phase(tmp_path):
    report = collect(tmp_path, tree={}, branch="main")
    assert report.derivation.current is None
    text = render_status_text(report, use_colour=False)
    assert "none" in text
    assert "Other phases:" not in text  # nothing to summarise


def test_the_text_rendering_shows_the_last_event(tmp_path):
    state_directory = tmp_path / ".atom"
    state_directory.mkdir(parents=True)
    (state_directory / "events.jsonl").write_text(
        '{"event": "initialised", "at": "2026-01-01"}\n', encoding="utf-8"
    )
    report = collect(tmp_path, {"phase-01-check": full_files()})
    text = render_status_text(report, use_colour=False)
    assert "Last:    initialised at 2026-01-01" in text


def test_the_text_rendering_points_at_the_problems(tmp_path):
    materialise(tmp_path / "specs" / "atom-cli", {"phase-01-check": full_files()})
    corrupt_state(tmp_path)
    report = collect_status(
        Project(tmp_path),
        runner=runner_on_branch("main", tmp_path),
        specs_root=tmp_path / "specs" / "atom-cli",
    )
    text = render_status_text(report, use_colour=False)
    assert "reported below" in text


def _report_with_problems(root: Path, problems: list[str]):
    """Build a minimal StatusReport carrying `problems`, rooted at `root`."""

    from atom.phases import Derivation
    from atom.status import StatusReport

    return StatusReport(
        root=root,
        derivation=Derivation(phases=(), current=None, source="none", problems=[]),
        problems=problems,
    )


def test_the_problem_renderer_is_empty_when_there_are_no_problems(tmp_path):
    report = _report_with_problems(tmp_path, [])
    assert render_status_problems(report, use_colour=False) == ""


def test_the_problem_renderer_uses_amber_advisories(tmp_path):
    from atom.report import _YELLOW

    report = _report_with_problems(tmp_path, ["a recoverable problem\nwith a step"])
    plain = render_status_problems(report, use_colour=False)
    assert plain.startswith("Advisories:")
    assert "a recoverable problem" in plain
    assert "with a step" in plain  # the multi-line continuation is rendered too
    assert _YELLOW in render_status_problems(report, use_colour=True)


def test_the_problem_renderer_never_uses_red(tmp_path):
    """F6-D6: red was reserved for a condition that could not occur.

    The unreadable root is used deliberately -- it is the exact input the red
    branch claimed to serve -- so this fails if the branch is ever restored.
    """
    from atom.report import _RED

    report = _report_with_problems(tmp_path / "does-not-exist", ["the root is gone"])
    plain = render_status_problems(report, use_colour=False)
    assert plain.startswith("Advisories:")
    assert _RED not in render_status_problems(report, use_colour=True)
