"""Behaviour tests for the derivation engine in `atom.phases` (B158-B171).

The tests build real directory trees under pytest's `tmp_path`, because the
thing under test *is* the shape of the filesystem plus the current git branch.
There is no fake filesystem here; a fake would hide exactly the facts these
tests exist to pin (a directory that is not a file, an empty file that is still
present, an mtime that must never be consulted).

Three tests are adversarial guards, not restatements. They construct the input
that would fool the intuitive-but-wrong implementation the POC already refuted
(a truncated spec, a repaid-old-artifact, a thin real document) and assert Atom
is not fooled. Deleting any of them lets the implementation regress to the
wrong design with a fully green suite -- which is precisely what happened in
Phase 5.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from dataclasses import fields
from pathlib import Path

import pytest

from atom.phases import (
    PHASE_DIR,
    POC_STATUSES,
    REQUIRED_ARTIFACTS,
    Derivation,
    Phase,
    PhaseArtifacts,
    derive,
    discover_phases,
)
from atom.runner import SubprocessRunner
from tests.conftest import FakeRunner, command_result

# The real repository is the best fixture this phase will ever have. Locate it
# from this test file's own path, never from the current working directory --
# the suite is run from the repo root but must not depend on that.
REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_SPECS = REPO_ROOT / "specs" / "atom-cli"

GIT = shutil.which("git")


# ---------------------------------------------------------------------------
# Helpers -- a compact vocabulary for describing a specs tree and a branch.
# ---------------------------------------------------------------------------

def poc_report(status: str = "ran", quoted: bool = True, include: bool = True) -> str:
    """Render a `poc-report.md` whose frontmatter carries the given status."""

    lines = ['---', 'project: "x"', 'phase: "p"', 'date: "2026-01-01"']
    if include:
        value = f'"{status}"' if quoted else status
        lines.append(f"status: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n\nbody text\n"


def full_files(status: str = "ran", quoted: bool = True, include_status: bool = True, brief: bool = True) -> dict[str, str]:
    """Return a filename->content map holding every required artifact."""

    files = {name: f"# {name}\n\ncontent\n" for name in REQUIRED_ARTIFACTS}
    files["poc-report.md"] = poc_report(status=status, quoted=quoted, include=include_status)
    if not brief:
        del files["poc-brief.md"]
    return files


def phase_tree(specs_root: Path, tree: dict[str, dict[str, str]]) -> Path:
    """Materialise `tree` (phase dir name -> filename -> content) on disk."""

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
    # Real git output carries a trailing newline; include it so the strip is exercised.
    return FakeRunner({command: command_result(command, cwd, exit_code=0, stdout=f"{branch}\n")})


def failing_git_runner() -> FakeRunner:
    """A runner where the git call cannot run at all (unscripted -> TOOL_MISSING)."""

    return FakeRunner({})


def only_phase(specs_root: Path) -> Phase:
    """Discover a single-phase tree and return that one phase."""

    discovered = discover_phases(specs_root)
    assert len(discovered) == 1
    return discovered[0]


def is_complete(phase: Phase) -> bool:
    """Test-side notion of completeness: every *required* artifact is present.

    Deliberately computed in the test, never read from the production API --
    the whole point of the phase is that the code does not expose this.
    """

    return all(phase.artifacts.present[name] for name in phase.artifacts.required)


# ===========================================================================
# Resolving the current phase (B158-B164)
# ===========================================================================

# --- B158: a phase directory matches ^phase-(\d{2})-([a-z0-9-]+)$ -----------

def test_a_well_formed_phase_directory_is_recognised(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-check": full_files()})
    assert [p.name for p in discover_phases(specs)] == ["phase-01-check"]
    assert PHASE_DIR.match("phase-01-check")


def test_a_single_digit_phase_number_is_not_a_phase_directory(tmp_path):
    # \d{2} means exactly two digits; a one-digit prefix must not qualify.
    specs = phase_tree(tmp_path / "specs", {"phase-1-check": full_files()})
    assert discover_phases(specs) == ()
    assert PHASE_DIR.match("phase-1-check") is None


def test_an_uppercase_slug_is_not_a_phase_directory(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-Check": full_files()})
    assert discover_phases(specs) == ()
    assert PHASE_DIR.match("phase-01-Check") is None


def test_a_directory_merely_containing_a_phase_name_is_not_one(tmp_path):
    # The anchors matter: a phase name embedded in a longer name is not a phase.
    specs = phase_tree(tmp_path / "specs", {"my-phase-01-check": full_files()})
    assert discover_phases(specs) == ()
    assert PHASE_DIR.match("my-phase-01-check") is None


def test_a_file_named_like_a_phase_directory_is_not_one(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir(parents=True)
    (specs / "phase-02-poc").write_text("not a directory", encoding="utf-8")
    assert discover_phases(specs) == ()


# --- B159: non-matching directories are ignored silently --------------------

def test_a_non_phase_directory_is_ignored(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-check": full_files(), "notes": {"a.md": "x"}})
    assert [p.name for p in discover_phases(specs)] == ["phase-01-check"]


def test_a_non_phase_directory_produces_no_problem(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-check": full_files(), "scratchpad": {"a.md": "x"}})
    result = derive(specs, runner_on_branch("main", tmp_path), tmp_path)
    assert result.problems == []


def test_the_phase_plan_document_beside_the_phases_is_not_a_phase(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-check": full_files()})
    (specs / "phase-plan.md").write_text("# plan", encoding="utf-8")
    assert [p.name for p in discover_phases(specs)] == ["phase-01-check"]


# --- B160: phases ordered lexically on the full directory name --------------

def test_phases_are_ordered_lexically(tmp_path):
    specs = phase_tree(
        tmp_path / "specs",
        {"phase-03-c": full_files(), "phase-01-a": full_files(), "phase-02-b": full_files()},
    )
    assert [p.name for p in discover_phases(specs)] == ["phase-01-a", "phase-02-b", "phase-03-c"]


def test_the_two_digit_prefix_makes_lexical_order_numeric(tmp_path):
    specs = phase_tree(
        tmp_path / "specs",
        {"phase-10-j": full_files(), "phase-02-b": full_files()},
    )
    # Lexical order equals numeric order precisely because of the two-digit prefix.
    assert [p.number for p in discover_phases(specs)] == [2, 10]


def test_phase_ten_sorts_after_phase_nine(tmp_path):
    specs = phase_tree(
        tmp_path / "specs",
        {"phase-10-j": full_files(), "phase-09-i": full_files()},
    )
    assert [p.name for p in discover_phases(specs)] == ["phase-09-i", "phase-10-j"]


# --- B161: a branch matching the pattern names the current phase ------------

def test_a_phase_branch_names_the_current_phase(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, runner_on_branch("phase-01-a", tmp_path), tmp_path)
    assert result.current.name == "phase-01-a"
    assert result.source == "branch"


def test_the_branch_wins_over_the_lexically_greatest_phase(tmp_path):
    # The only configuration where precedence is observable: the two rules disagree.
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, runner_on_branch("phase-01-a", tmp_path), tmp_path)
    assert result.current.name == "phase-01-a"
    assert result.current.name != "phase-02-b"


# --- B162: otherwise the lexically greatest phase directory -----------------

def test_main_falls_back_to_the_lexically_greatest_phase(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, runner_on_branch("main", tmp_path), tmp_path)
    assert result.current.name == "phase-02-b"
    assert result.source == "lexical"


def test_a_detached_head_falls_back_to_the_lexically_greatest_phase(tmp_path):
    # A detached HEAD makes `git branch --show-current` print an empty string.
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, runner_on_branch("", tmp_path), tmp_path)
    assert result.current.name == "phase-02-b"
    assert result.source == "lexical"


def test_an_unrelated_branch_name_falls_back(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, runner_on_branch("scratch/experiment", tmp_path), tmp_path)
    assert result.current.name == "phase-02-b"
    assert result.source == "lexical"


def test_a_branch_that_cannot_be_read_falls_back(tmp_path):
    # A failed git call must fall back to lexical, never crash.
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, failing_git_runner(), tmp_path)
    assert result.current.name == "phase-02-b"
    assert result.source == "lexical"


# --- B163: a branch naming a phase with no directory is still current -------

def test_a_branch_naming_a_missing_phase_directory_is_still_current(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    result = derive(specs, runner_on_branch("phase-09-ghost", tmp_path), tmp_path)
    assert result.current.name == "phase-09-ghost"
    assert result.source == "branch"


def test_a_phase_with_no_directory_is_marked_not_started(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files()})
    result = derive(specs, runner_on_branch("phase-09-ghost", tmp_path), tmp_path)
    assert result.current.started is False
    assert result.current.directory is None


def test_a_phase_with_no_directory_reports_every_artifact_absent(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files()})
    result = derive(specs, runner_on_branch("phase-09-ghost", tmp_path), tmp_path)
    assert all(present is False for present in result.current.artifacts.present.values())
    # B163+B168: a fresh phase owes all seven, the brief included -- it is
    # absent-and-owed, not dropped from the tally.
    assert set(result.current.artifacts.required) == set(REQUIRED_ARTIFACTS)


def test_a_phase_with_no_directory_is_not_an_error(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files()})
    result = derive(specs, runner_on_branch("phase-09-ghost", tmp_path), tmp_path)
    assert result.problems == []


# --- B164: no phase directories and no matching branch -> no current --------

def test_a_project_with_no_phases_has_no_current_phase(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir(parents=True)
    result = derive(specs, runner_on_branch("main", tmp_path), tmp_path)
    assert result.current is None
    assert result.source == "none"


def test_a_project_with_no_phases_is_not_an_error(tmp_path):
    specs = tmp_path / "specs"
    specs.mkdir(parents=True)
    result = derive(specs, runner_on_branch("main", tmp_path), tmp_path)
    assert result.problems == []


def test_an_absent_specs_directory_is_not_a_crash(tmp_path):
    missing = tmp_path / "does-not-exist"
    assert discover_phases(missing) == ()
    result = derive(missing, runner_on_branch("main", tmp_path), tmp_path)
    assert result.current is None


# --- The mtime guard (B160, against the F6-3 measurement) -------------------

def test_creating_an_artifact_in_an_old_phase_does_not_make_it_current(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-03-c": full_files()})
    runner = runner_on_branch("main", tmp_path)
    assert derive(specs, runner, tmp_path).current.name == "phase-03-c"

    # F6-3: creating a file inside a directory makes that directory the newest.
    # Under an mtime rule this would flip the answer to phase-01-a; it must not.
    time.sleep(0.02)
    (specs / "phase-01-a" / "extra-note.md").write_text("new", encoding="utf-8")
    assert derive(specs, runner, tmp_path).current.name == "phase-03-c"


def test_editing_an_artifact_in_an_old_phase_does_not_make_it_current(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(), "phase-02-b": full_files()})
    runner = runner_on_branch("main", tmp_path)
    assert derive(specs, runner, tmp_path).current.name == "phase-02-b"

    time.sleep(0.02)
    (specs / "phase-01-a" / "design-spec.md").write_text("# edited later\n\nmore\n", encoding="utf-8")
    assert derive(specs, runner, tmp_path).current.name == "phase-02-b"


def test_the_current_phase_is_stable_when_every_directory_is_touched_in_reverse_order(tmp_path):
    # The decisive guard. Every phase directory's mtime is set in REVERSE of
    # lexical order (phase-01 newest, phase-03 oldest). A lexical rule is
    # unmoved; an mtime rule inverts and picks phase-01. The asymmetry is the guard.
    specs = phase_tree(
        tmp_path / "specs",
        {"phase-01-a": full_files(), "phase-02-b": full_files(), "phase-03-c": full_files()},
    )
    runner = runner_on_branch("main", tmp_path)
    assert derive(specs, runner, tmp_path).current.name == "phase-03-c"

    base = time.time()
    for index, name in enumerate(["phase-01-a", "phase-02-b", "phase-03-c"]):
        stamp = base - index * 1000  # phase-01 newest, phase-03 oldest
        os.utime(specs / name, (stamp, stamp))

    assert derive(specs, runner, tmp_path).current.name == "phase-03-c"


# ===========================================================================
# Artifact presence (B165-B171)
# ===========================================================================

# --- B165: the required set is exactly the seven named ----------------------

def test_the_required_artifacts_are_the_seven_named(tmp_path):
    assert REQUIRED_ARTIFACTS == (
        "poc-brief.md",
        "poc-report.md",
        "design-spec.md",
        "test-spec.md",
        "tdd-log.md",
        "findings.md",
        "decisions.md",
    )


def test_an_unexpected_file_in_a_phase_directory_is_not_required(tmp_path):
    files = full_files()
    files["notes.md"] = "irrelevant"
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    phase = only_phase(specs)
    assert "notes.md" not in phase.artifacts.required


def test_an_unexpected_file_does_not_appear_in_the_artifact_report(tmp_path):
    files = full_files()
    files["notes.md"] = "irrelevant"
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    phase = only_phase(specs)
    assert set(phase.artifacts.present) == set(REQUIRED_ARTIFACTS)


# --- B166: present or absent, no third state --------------------------------

def test_an_existing_artifact_is_present(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files()})
    assert only_phase(specs).artifacts.present["design-spec.md"] is True


def test_a_missing_artifact_is_absent(tmp_path):
    files = full_files()
    del files["findings.md"]
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["findings.md"] is False


def test_an_empty_artifact_file_is_still_present(tmp_path):
    files = full_files()
    files["findings.md"] = ""
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["findings.md"] is True


def test_a_directory_named_like_an_artifact_is_not_present(tmp_path):
    files = full_files()
    del files["design-spec.md"]
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    # A *directory* with the artifact's name is not the artifact (it is not a file).
    (specs / "phase-01-a" / "design-spec.md").mkdir()
    assert only_phase(specs).artifacts.present["design-spec.md"] is False


def test_the_artifact_report_has_exactly_two_states(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files()})
    values = only_phase(specs).artifacts.present.values()
    assert {type(v) for v in values} == {bool}


# --- B167: never read size, sections, headings, or content to judge ---------

def test_a_one_byte_artifact_is_present(tmp_path):
    files = full_files()
    files["tdd-log.md"] = "x"
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["tdd-log.md"] is True


def test_a_document_with_no_headings_is_present(tmp_path):
    files = full_files()
    files["findings.md"] = "just prose, no markdown headings at all\n"
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["findings.md"] is True


def test_a_document_of_only_headings_is_present(tmp_path):
    files = full_files()
    files["findings.md"] = "# a\n## b\n## c\n"
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["findings.md"] is True


def test_no_artifact_but_the_poc_report_is_ever_opened(tmp_path, monkeypatch):
    # The only artifact whose content is ever read is poc-report.md (for status).
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files()})
    reads: list[str] = []
    real_read_text = Path.read_text

    def spy_read_text(self, *args, **kwargs):
        reads.append(self.name)
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", spy_read_text)
    discover_phases(specs)

    opened_artifacts = [name for name in reads if name in REQUIRED_ARTIFACTS]
    assert set(opened_artifacts) <= {"poc-report.md"}


# --- B168: poc-brief.md required only when a POC actually ran ---------------

def test_a_ran_poc_requires_a_brief(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="ran")})
    assert "poc-brief.md" in only_phase(specs).artifacts.required


def test_a_skipped_poc_does_not_require_a_brief(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="skipped", brief=False)})
    assert "poc-brief.md" not in only_phase(specs).artifacts.required


def test_a_skipped_phase_with_no_brief_is_complete(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="skipped", brief=False)})
    phase = only_phase(specs)
    assert is_complete(phase) is True


def test_a_skipped_phase_requires_the_other_six(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="skipped", brief=False)})
    required = only_phase(specs).artifacts.required
    assert set(required) == {
        "poc-report.md",
        "design-spec.md",
        "test-spec.md",
        "tdd-log.md",
        "findings.md",
        "decisions.md",
    }


# --- B169: an unrecognised status is a problem, and requires the brief ------

def test_an_unrecognised_status_is_reported_as_a_problem(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="wibble")})
    assert only_phase(specs).artifacts.problems != []


def test_an_unrecognised_status_still_requires_the_brief(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="wibble", brief=False)})
    assert "poc-brief.md" in only_phase(specs).artifacts.required


def test_a_missing_status_field_is_reported_and_requires_the_brief(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(include_status=False, brief=False)})
    phase = only_phase(specs)
    assert phase.artifacts.problems != []
    assert "poc-brief.md" in phase.artifacts.required


def test_the_unrecognised_status_problem_names_the_value_it_found(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="wibble")})
    problems = only_phase(specs).artifacts.problems
    assert any("wibble" in problem for problem in problems)


# --- B170: an absent poc-report.md leaves the question unanswerable ---------

def test_an_absent_poc_report_makes_both_it_and_the_brief_absent(tmp_path):
    files = full_files(brief=False)
    del files["poc-report.md"]
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    present = only_phase(specs).artifacts.present
    assert present["poc-report.md"] is False
    assert present["poc-brief.md"] is False


def test_an_absent_poc_report_raises_no_problem_beyond_the_absences(tmp_path):
    files = full_files(brief=False)
    del files["poc-report.md"]
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    # The missing report already says everything; no extra status problem is raised.
    assert only_phase(specs).artifacts.problems == []


def test_a_phase_with_no_poc_report_still_requires_the_brief(tmp_path):
    # B170: an absent report does not shrink the required set. The brief is
    # absent-and-owed, not dropped -- the regression here is invisible (a smaller
    # tally looks fine), so it is pinned explicitly.
    files = full_files(brief=False)
    del files["poc-report.md"]
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    required = only_phase(specs).artifacts.required
    assert "poc-brief.md" in required
    assert set(required) == set(REQUIRED_ARTIFACTS)


# --- B171: the vocabulary is closed, exact, and case-sensitive --------------

def test_the_status_vocabulary_is_exactly_two_tokens(tmp_path):
    assert POC_STATUSES == ("ran", "skipped")


def test_a_status_containing_skipped_as_a_substring_is_not_skipped(tmp_path):
    # "skipped" as a substring of a longer value must not count as the token.
    specs = phase_tree(
        tmp_path / "specs",
        {"phase-01-a": full_files(status="skipped-because-no-time", brief=False)},
    )
    phase = only_phase(specs)
    assert "poc-brief.md" in phase.artifacts.required
    assert phase.artifacts.problems != []


def test_the_prose_status_values_this_repo_used_before_are_not_accepted(tmp_path):
    specs = phase_tree(
        tmp_path / "specs",
        {"phase-01-a": full_files(status="POC deliberately skipped - no spike was run", brief=False)},
    )
    phase = only_phase(specs)
    assert "poc-brief.md" in phase.artifacts.required
    assert phase.artifacts.problems != []


def test_status_matching_is_case_sensitive(tmp_path):
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="Ran")})
    phase = only_phase(specs)
    assert phase.artifacts.problems != []
    assert "poc-brief.md" in phase.artifacts.required


def test_an_unquoted_status_is_recognised(tmp_path):
    # YAML values may be unquoted; `status: ran` (no quotes) is still the token.
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": full_files(status="ran", quoted=False)})
    phase = only_phase(specs)
    assert phase.artifacts.problems == []
    assert "poc-brief.md" in phase.artifacts.required


# ===========================================================================
# The truncation guard and the thin-document guard (the phase's core)
# ===========================================================================

def _thirteen_section_spec() -> str:
    parts = ["# Design Spec\n"]
    for index in range(1, 14):
        parts.append(f"\n## Section {index}\n\nSubstantive prose for section {index}.\n")
    return "".join(parts)


def _truncate_to_sections(text: str, section_count: int) -> str:
    heads = [match.start() for match in re.finditer(r"(?m)^## ", text)]
    return text[: heads[section_count]]


def test_a_truncated_design_spec_is_reported_present(tmp_path):
    # The POC's V1: a real 13-section spec cut to its first 4 sections passed
    # every structural rule. Atom must report it PRESENT, never complete.
    full = _thirteen_section_spec()
    assert len(re.findall(r"(?m)^## ", full)) == 13
    truncated = _truncate_to_sections(full, 4)
    assert len(re.findall(r"(?m)^## ", truncated)) == 4

    files = full_files()
    files["design-spec.md"] = truncated
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["design-spec.md"] is True


def test_no_rendering_describes_any_artifact_as_complete(tmp_path):
    # phases.py exposes no completeness vocabulary anywhere in its derived data.
    # (Full text/JSON rendering lives in render.py, tested there; this pins the
    # derivation API, which is the source those renderings draw from.)
    files = full_files()
    files["design-spec.md"] = _truncate_to_sections(_thirteen_section_spec(), 4)
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    result = derive(specs, runner_on_branch("main", tmp_path), tmp_path)

    text = repr(result).lower()
    for word in ("complete", "valid", "sufficient", "done", "finished"):
        assert word not in text


def test_the_report_exposes_no_completeness_field(tmp_path):
    # No field on the derived types may name completeness -- F6-1 proved it is
    # not computable, so an API that offered it could only ever lie.
    field_names = {f.name for f in fields(PhaseArtifacts)} | {f.name for f in fields(Phase)}
    for name in field_names:
        for word in ("complete", "valid", "sufficient"):
            assert word not in name.lower()


def test_a_two_section_tdd_log_is_present(tmp_path):
    # A genuine document with only two level-2 sections -- the shape the POC's
    # structural rules wrongly rejected -- is present.
    files = full_files()
    files["tdd-log.md"] = "# TDD Log\n\n## Cycle 1\n\ntext\n\n## Cycle 2\n\ntext\n"
    specs = phase_tree(tmp_path / "specs", {"phase-01-a": files})
    assert only_phase(specs).artifacts.present["tdd-log.md"] is True


def test_the_real_phase_one_tdd_log_is_present():
    # Reads the ACTUAL file the POC's structural rules rejected, not a fixture,
    # so the guard cannot drift away from the thing it protects.
    phases = {phase.name: phase for phase in discover_phases(REAL_SPECS)}
    assert phases["phase-01-check"].artifacts.present["tdd-log.md"] is True


# ===========================================================================
# Tier 1 -- the real repository
# ===========================================================================

def test_the_real_repository_resolves_six_phases():
    assert len(discover_phases(REAL_SPECS)) == 6


def test_the_real_repository_orders_phases_one_through_six():
    assert [p.name for p in discover_phases(REAL_SPECS)] == [
        "phase-01-check",
        "phase-02-poc",
        "phase-03-state",
        "phase-04-review",
        "phase-05-ship",
        "phase-06-state",
    ]


def test_phases_one_through_five_have_every_required_artifact():
    phases = {phase.name: phase for phase in discover_phases(REAL_SPECS)}
    for name in ("phase-01-check", "phase-02-poc", "phase-03-state", "phase-04-review", "phase-05-ship"):
        assert is_complete(phases[name]), f"{name} should score as having every required artifact"


def test_the_real_phase_one_is_complete_despite_having_no_brief():
    phases = {phase.name: phase for phase in discover_phases(REAL_SPECS)}
    phase_one = phases["phase-01-check"]
    # Its POC was skipped, so the brief is not required and its absence is fine.
    assert phase_one.artifacts.present["poc-brief.md"] is False
    assert "poc-brief.md" not in phase_one.artifacts.required
    assert is_complete(phase_one) is True


def test_the_real_phase_six_is_missing_exactly_its_unwritten_artifacts():
    # Written to survive the phase legitimately completing: the four artifacts
    # that exist now must stay present, and anything still missing may only ever
    # be one of the three not-yet-written documents. No exact count is asserted.
    phases = {phase.name: phase for phase in discover_phases(REAL_SPECS)}
    present = phases["phase-06-state"].artifacts.present
    for name in ("poc-brief.md", "poc-report.md", "design-spec.md", "test-spec.md"):
        assert present[name] is True
    missing = {name for name, is_present in present.items() if not is_present}
    assert missing <= {"tdd-log.md", "findings.md", "decisions.md"}


# ===========================================================================
# Tier 2 -- real git in a throwaway repository
# ===========================================================================

def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([GIT, *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo_with_phases(root: Path, phase_names: list[str]) -> Path:
    specs = root / "specs" / "atom-cli"
    phase_tree(specs, {name: full_files() for name in phase_names})
    _git(["init"], root)
    _git(["config", "user.email", "atom-test@example.com"], root)
    _git(["config", "user.name", "Atom Test"], root)
    _git(["add", "-A"], root)
    _git(["commit", "-m", "phases"], root)
    return specs


@pytest.mark.skipif(GIT is None, reason="real git is not installed")
def test_a_real_detached_head_falls_back_to_lexical(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    specs = _init_repo_with_phases(root, ["phase-01-a", "phase-02-b"])
    head = _git(["rev-parse", "HEAD"], root).stdout.strip()
    _git(["checkout", head], root)  # detach HEAD

    result = derive(specs, SubprocessRunner(), root)
    assert result.source == "lexical"
    assert result.current.name == "phase-02-b"


@pytest.mark.skipif(GIT is None, reason="real git is not installed")
def test_a_real_phase_branch_resolves_to_its_directory(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    specs = _init_repo_with_phases(root, ["phase-01-a", "phase-02-b"])
    _git(["switch", "-c", "phase-01-a"], root)

    # Exercises real `git branch --show-current` output, trailing newline and all.
    result = derive(specs, SubprocessRunner(), root)
    assert result.source == "branch"
    assert result.current.name == "phase-01-a"


@pytest.mark.skipif(GIT is None, reason="real git is not installed")
def test_a_real_clone_preserves_phase_ordering(tmp_path):
    origin = tmp_path / "origin"
    origin.mkdir()
    _init_repo_with_phases(origin, ["phase-01-a", "phase-02-b", "phase-03-c"])

    clone = tmp_path / "clone"
    _git(["clone", "--quiet", str(origin), str(clone)], tmp_path)

    clone_specs = clone / "specs" / "atom-cli"
    assert [p.name for p in discover_phases(clone_specs)] == ["phase-01-a", "phase-02-b", "phase-03-c"]
