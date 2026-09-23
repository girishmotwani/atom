"""Behaviour tests for `atom ship` (B138-B157).

Phase 5 is almost entirely `git` and `gh` invocation, and that is precisely the
surface every earlier phase's tests erased: a fake runner has no PATH, no argv
ceiling, and no stdin, so mocking the operating system mocks the constraint
away. These unit tests are therefore necessary but not sufficient; the real
`git` (Tier 1) and real `gh` (Tier 2) checks live elsewhere.

The fake runner below is keyed on *what each command is*, never on call order,
so a test cannot silently pass when the pipeline reorders its calls -- the exact
failure the test spec warns about. It records every argv and every `stdin_text`.

One constraint cannot be faked and shapes half the fixtures here: `run_check`
validates `go.mod` on the *real* filesystem before any gate runs, so whether the
gates are reached is a property of the `tmp_path`, not of the fake runner. A
B147 test (a failing gate refuses) must build a `tmp_path` that really holds a
`go.mod`; a B145a test (no module skips the gates) must build one that does not.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from atom.body import CheckSummary
from atom.runner import CommandOutcome, CommandResult
from atom.ship import PrAction, ShipOutcome, ShipRefused, run_ship

# A recognisable forty-character SHA so a link that pins it is unmistakable, and
# so a link that used a branch name instead would be obviously wrong.
HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"

# Sentinels that must never leak into the assembled body: an artifact's content
# (B148) and a gate's full output (B146) are both linked-to or summarised, never
# embedded.
ARTIFACT_SENTINEL = "ARTIFACT_BODY_SENTINEL_content_that_must_not_be_embedded"
GATE_OUTPUT_SENTINEL = "GATE_OUTPUT_SENTINEL_compiler_noise"

# The five gate commands `default_gates()` issues, so the fake can answer each
# without a Go toolchain once a real go.mod has let run_check reach them.
_GATE_COMMANDS = {
    ("go", "build", "./..."),
    ("go", "vet", "./..."),
    ("gofmt", "-l", "."),
    ("go", "test", "./..."),
    ("go", "test", "-race", "./..."),
}


class ShipRunner:
    """A scripted CommandRunner keyed on what each command is.

    It answers the three command families ship drives -- `gh`, `git`, and the
    check gates -- from configuration rather than from a call sequence, and
    records every argv and stdin so a test can assert on both what was asked and
    in what order.
    """

    def __init__(
        self,
        *,
        gh_present: bool = True,
        branch: str = "phase-05-ship",
        status_porcelain: str = "",
        has_upstream: bool = True,
        commits_ahead: int = 0,
        head_sha: str = HEAD_SHA,
        remote_url: str = "https://github.com/octocat/atom.git",
        subjects: tuple[str, ...] = ("[Phase 5] Add atom ship",),
        failing_gate: tuple[str, ...] | None = None,
        existing_pr_url: str | None = "https://github.com/octocat/atom/pull/7",
        create_stderr: str | None = None,
        create_duplicate: bool = False,
        branch_ok: bool = True,
        status_ok: bool = True,
        push_ok: bool = True,
        head_ok: bool = True,
        log_ok: bool = True,
        remote_ok: bool = True,
        edit_ok: bool = True,
        existing_pr_stdout: str | None = None,
        create_stdout: str | None = None,
        create_empty_fail: bool = False,
    ) -> None:
        self.gh_present = gh_present
        self.branch = branch
        self.status_porcelain = status_porcelain
        self.has_upstream = has_upstream
        self.commits_ahead = commits_ahead
        self.head_sha = head_sha
        self.remote_url = remote_url
        self.subjects = subjects
        self.failing_gate = failing_gate
        self.existing_pr_url = existing_pr_url
        self.create_stderr = create_stderr
        self.create_duplicate = create_duplicate
        self.branch_ok = branch_ok
        self.status_ok = status_ok
        self.push_ok = push_ok
        self.head_ok = head_ok
        self.log_ok = log_ok
        self.remote_ok = remote_ok
        self.edit_ok = edit_ok
        self.existing_pr_stdout = existing_pr_stdout
        self.create_stdout = create_stdout
        self.create_empty_fail = create_empty_fail

        self.commands: list[tuple[str, ...]] = []
        self.stdins: list[str | None] = []

    # -- recording helpers -------------------------------------------------

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        cmd = tuple(command)
        self.commands.append(cmd)
        self.stdins.append(stdin_text)

        def result(outcome, exit_code, stdout="", stderr=""):
            return CommandResult(
                command=cmd,
                working_directory=working_directory,
                outcome=outcome,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=0.1,
            )

        if cmd[0] == "gh":
            return self._run_gh(cmd, result)
        if cmd[0] == "git":
            return self._run_git(cmd, result)
        if cmd in _GATE_COMMANDS:
            return self._run_gate(cmd, result)

        return result(CommandOutcome.TOOL_MISSING, None, "", f"unexpected command: {cmd}")

    # -- command families --------------------------------------------------

    def _run_gh(self, cmd, result):
        if "--version" in cmd:
            if self.gh_present:
                return result(CommandOutcome.COMPLETED, 0, "gh version 2.40.0", "")
            return result(CommandOutcome.TOOL_MISSING, None, "", "gh not found on PATH")

        if cmd[1:3] == ("pr", "view"):
            if self.existing_pr_stdout is not None:
                return result(CommandOutcome.COMPLETED, 0, self.existing_pr_stdout, "")
            if self.existing_pr_url is None:
                return result(CommandOutcome.COMPLETED, 1, "", "no pull requests found for branch")
            payload = json.dumps({"url": self.existing_pr_url, "number": 7})
            return result(CommandOutcome.COMPLETED, 0, payload, "")

        if cmd[1:3] == ("pr", "create"):
            if self.create_duplicate:
                return result(
                    CommandOutcome.COMPLETED, 1, "",
                    "a pull request for branch already exists:\n"
                    "https://github.com/octocat/atom/pull/7",
                )
            if self.create_empty_fail:
                return result(CommandOutcome.COMPLETED, 1, "", "")
            if self.create_stderr is not None:
                return result(CommandOutcome.COMPLETED, 1, "", self.create_stderr)
            if self.create_stdout is not None:
                return result(CommandOutcome.COMPLETED, 0, self.create_stdout, "")
            return result(CommandOutcome.COMPLETED, 0, "https://github.com/octocat/atom/pull/9\n", "")

        if cmd[1:3] == ("pr", "edit"):
            if not self.edit_ok:
                return result(CommandOutcome.COMPLETED, 1, "", "could not update pull request")
            return result(CommandOutcome.COMPLETED, 0, "https://github.com/octocat/atom/pull/7\n", "")

        return result(CommandOutcome.TOOL_MISSING, None, "", f"unexpected gh command: {cmd}")

    def _run_git(self, cmd, result):
        if cmd == ("git", "rev-parse", "--abbrev-ref", "HEAD"):
            if not self.branch_ok:
                return result(CommandOutcome.COMPLETED, 128, "", "fatal: not a git repository")
            return result(CommandOutcome.COMPLETED, 0, self.branch, "")

        if cmd[:2] == ("git", "rev-parse") and "@{u}" in cmd:
            if self.has_upstream:
                return result(CommandOutcome.COMPLETED, 0, f"origin/{self.branch}", "")
            return result(CommandOutcome.COMPLETED, 128, "", "fatal: no upstream configured for branch")

        if cmd[:2] == ("git", "rev-list") and any("@{u}" in part for part in cmd):
            return result(CommandOutcome.COMPLETED, 0, str(self.commits_ahead), "")

        if cmd == ("git", "rev-parse", "HEAD"):
            if not self.head_ok:
                return result(CommandOutcome.COMPLETED, 128, "", "fatal: bad revision 'HEAD'")
            return result(CommandOutcome.COMPLETED, 0, self.head_sha, "")

        if cmd == ("git", "status", "--porcelain"):
            if not self.status_ok:
                return result(CommandOutcome.COMPLETED, 128, "", "fatal: not a git repository")
            return result(CommandOutcome.COMPLETED, 0, self.status_porcelain, "")

        if cmd[:2] == ("git", "log"):
            if not self.log_ok:
                return result(CommandOutcome.COMPLETED, 128, "", "fatal: bad revision 'main..HEAD'")
            return result(CommandOutcome.COMPLETED, 0, "\n".join(self.subjects), "")

        if cmd[:2] == ("git", "push"):
            if not self.push_ok:
                return result(CommandOutcome.COMPLETED, 1, "", "error: failed to push some refs")
            return result(CommandOutcome.COMPLETED, 0, "", "branch set up to track remote")

        if cmd == ("git", "remote", "get-url", "origin"):
            if not self.remote_ok:
                return result(CommandOutcome.COMPLETED, 128, "", "fatal: no such remote 'origin'")
            return result(CommandOutcome.COMPLETED, 0, self.remote_url, "")

        return result(CommandOutcome.TOOL_MISSING, None, "", f"unexpected git command: {cmd}")

    def _run_gate(self, cmd, result):
        if self.failing_gate is not None and cmd == self.failing_gate:
            return result(CommandOutcome.COMPLETED, 1, GATE_OUTPUT_SENTINEL, "build failed")
        # A passing gate. go build carries the sentinel so a body that embedded
        # gate output would reveal it; gofmt and go test must stay empty, or the
        # gates would read their stdout as "unformatted" / "has output".
        if cmd == ("go", "build", "./..."):
            return result(CommandOutcome.COMPLETED, 0, GATE_OUTPUT_SENTINEL, "")
        return result(CommandOutcome.COMPLETED, 0, "", "")


# -- fixtures --------------------------------------------------------------


def _make_tree(
    tmp_path: Path,
    *,
    go_mod: bool = False,
    project: str = "atom-cli",
    phase: str = "phase-05-ship",
    with_design_spec: bool = True,
    artifacts: tuple[str, ...] = ("design-spec.md", "poc-report.md", "test-spec.md"),
) -> Path:
    """Build a working tree with a phase directory, optionally a real go.mod."""

    phase_dir = tmp_path / "specs" / project / phase
    phase_dir.mkdir(parents=True)

    for name in artifacts:
        if name == "design-spec.md" and with_design_spec:
            (phase_dir / name).write_text(
                "# Ship the phase\n\n"
                "## Purpose\n\n"
                "Ship turns a finished phase into a pull request.\n\n"
                "A second purpose paragraph that must survive quoting.\n\n"
                "## Scope\n\n"
                f"{ARTIFACT_SENTINEL}\n",
                encoding="utf-8",
            )
        else:
            (phase_dir / name).write_text(f"{name}\n{ARTIFACT_SENTINEL}\n", encoding="utf-8")

    if go_mod:
        (tmp_path / "go.mod").write_text("module example.com/thing\n\ngo 1.22\n", encoding="utf-8")

    return tmp_path


def _ship(runner: ShipRunner, working_directory: Path, **kwargs) -> ShipOutcome:
    return run_ship(runner, working_directory, base_branch="main", **kwargs)


# ==========================================================================
# Preconditions (B138-B142)
# ==========================================================================


class TestGhPrecondition:
    """B138 - gh is located and verified before anything else runs."""

    def test_a_missing_gh_is_an_unmet_precondition_not_a_late_failure(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(gh_present=False)

        with pytest.raises(ShipRefused):
            _ship(runner, tree)

        # No git work was attempted: the precondition fired first.
        assert not any(cmd[0] == "git" for cmd in runner.commands)

    def test_gh_is_verified_before_any_git_work_begins(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        _ship(runner, tree, push=True)

        first_gh = next(i for i, c in enumerate(runner.commands) if c[0] == "gh")
        first_git = next(i for i, c in enumerate(runner.commands) if c[0] == "git")
        assert first_gh < first_git

    def test_the_missing_gh_message_names_the_install(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(gh_present=False)

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "cli.github.com" in str(excinfo.value)


class TestBranchPreconditions:
    """B139 - a detached HEAD or the base branch has nothing to ship from."""

    def test_a_detached_head_has_nothing_to_ship_from(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(branch="HEAD")

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "detached" in str(excinfo.value).lower()

    def test_shipping_the_base_branch_itself_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(branch="main")

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "main" in str(excinfo.value)


class TestDirtyTree:
    """B140 - a dirty working tree is refused, listing the modified files."""

    def test_a_dirty_working_tree_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(status_porcelain=" M tools/atom/ship.py\n")

        with pytest.raises(ShipRefused):
            _ship(runner, tree)

    def test_the_dirty_tree_refusal_lists_the_modified_files(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(status_porcelain=" M tools/atom/ship.py\n?? notes.txt\n")

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        message = str(excinfo.value)
        assert "tools/atom/ship.py" in message
        assert "notes.txt" in message

    def test_a_clean_tree_is_allowed_to_proceed(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(status_porcelain="")

        outcome = _ship(runner, tree)

        assert isinstance(outcome, ShipOutcome)


class TestUpstream:
    """B141/B142 - an upstream is required, or --push provides one."""

    def test_a_branch_with_no_upstream_and_no_push_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=False)

        with pytest.raises(ShipRefused):
            _ship(runner, tree, push=False)

    def test_the_missing_upstream_refusal_prints_the_command_that_fixes_it(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=False)

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree, push=False)

        message = str(excinfo.value)
        assert "git push" in message
        assert "phase-05-ship" in message

    def test_the_push_flag_pushes_the_branch_and_sets_the_upstream(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=False)

        _ship(runner, tree, push=True)

        push_calls = [c for c in runner.commands if c[:2] == ("git", "push")]
        assert push_calls, "expected ship to push"
        pushed = " ".join(push_calls[0])
        assert "--set-upstream" in push_calls[0] or "-u" in push_calls[0]
        assert "phase-05-ship" in pushed

    def test_the_push_is_a_git_command_never_gh(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=False)

        _ship(runner, tree, push=True)

        assert any(c[:2] == ("git", "push") for c in runner.commands)
        assert not any(c[0] == "gh" and "push" in c for c in runner.commands)


# ==========================================================================
# Resolving the phase (B143-B144)
# ==========================================================================


class TestPhaseResolution:
    """B143/B144 - the phase directory and its artifacts."""

    def test_the_phase_directory_is_derived_from_the_branch_name(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.phase_directory.name == "phase-05-ship"

    def test_the_phase_flag_overrides_the_branch_derivation(self, tmp_path):
        tree = _make_tree(tmp_path, phase="phase-99-override")
        runner = ShipRunner()

        outcome = _ship(runner, tree, phase="phase-99-override")

        assert outcome.phase_directory.name == "phase-99-override"

    def test_a_missing_phase_directory_is_refused_naming_the_path_it_tried(self, tmp_path):
        tree = _make_tree(tmp_path, phase="phase-05-ship")
        runner = ShipRunner(branch="phase-77-absent")

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "phase-77-absent" in str(excinfo.value)

    def test_the_artifacts_are_the_files_the_phase_directory_holds(self, tmp_path):
        tree = _make_tree(tmp_path, artifacts=("design-spec.md", "poc-report.md"))
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert set(outcome.artifacts) == {
            "specs/atom-cli/phase-05-ship/design-spec.md",
            "specs/atom-cli/phase-05-ship/poc-report.md",
        }

    def test_a_missing_artifact_is_omitted_rather_than_described_as_pending(self, tmp_path):
        tree = _make_tree(tmp_path, artifacts=("design-spec.md",))
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert not any("test-spec.md" in a for a in outcome.artifacts)
        assert "pending" not in outcome.body_text.lower()


# ==========================================================================
# Fresh check evidence (B145, B145a, B146, B147, B147a, B147b)
# ==========================================================================


class TestFreshCheck:
    """B145 - atom check runs fresh, as part of ship."""

    def test_the_check_runs_fresh_as_part_of_ship(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        _ship(runner, tree)

        assert ("go", "build", "./...") in runner.commands

    def test_a_recorded_check_result_is_not_accepted(self, tmp_path):
        # There is no seam to inject a stored result: the gates are re-run every
        # time, so a second ship issues the gate commands a second time.
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        _ship(runner, tree)
        first = runner.commands.count(("go", "build", "./..."))
        _ship(runner, tree)
        second = runner.commands.count(("go", "build", "./..."))

        assert second == first + 1


class TestNotAGoModule:
    """B145a - a tree with no Go module skips the gates, and that is not failure."""

    def test_a_tree_with_no_go_module_skips_the_gates(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        _ship(runner, tree)

        assert not any(cmd in _GATE_COMMANDS for cmd in runner.commands)

    def test_the_absent_module_is_recorded_as_an_absence_not_a_failure(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.check.passed is True
        assert outcome.check.absent_reason is not None
        assert "not a Go module" in outcome.check.absent_reason

    def test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        outcome = _ship(runner, tree, allow_failing_checks=False)

        assert outcome.pr_url
        assert outcome.exit_code == 0

    def test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        outcome = _ship(runner, tree, allow_failing_checks=False)

        assert outcome.check_overridden is False

    def test_the_evidence_section_states_the_absence_rather_than_omitting_it(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert "not a Go module" in outcome.body_text


class TestVerdictTable:
    """B146 - the body carries a bounded verdict table, not the full output."""

    def test_the_body_carries_one_verdict_row_per_gate(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert len(outcome.check.gate_rows) == 5
        assert outcome.check.absent_reason is None

    def test_the_verdict_table_is_bounded_at_five_rows(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert len(outcome.check.gate_rows) <= 5

    def test_the_body_does_not_embed_the_gates_full_output(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert GATE_OUTPUT_SENTINEL not in outcome.body_text

    def test_when_there_is_no_module_the_table_is_replaced_by_the_recorded_line(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert "| Gate |" not in outcome.body_text
        assert "not a Go module" in outcome.body_text

    def test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        evidence = outcome.body_text.split("## Evidence", 1)[1]
        assert "not a Go module" in evidence.split("##", 1)[0]


class TestCheckRefusal:
    """B147 - a failing check refuses; the absence path is not a loophole."""

    def test_a_failing_check_refuses_to_open_or_update_the_pr(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        with pytest.raises(ShipRefused):
            _ship(runner, tree, allow_failing_checks=False)

        assert not any(c[1:3] == ("pr", "create") for c in runner.commands if c[0] == "gh")
        assert not any(c[1:3] == ("pr", "edit") for c in runner.commands if c[0] == "gh")

    def test_the_check_refusal_names_the_failing_gates(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree, allow_failing_checks=False)

        assert "build" in str(excinfo.value)

    def test_allow_failing_checks_overrides_the_refusal(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        outcome = _ship(runner, tree, allow_failing_checks=True)

        assert outcome.pr_url

    def test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "vet", "./..."))

        with pytest.raises(ShipRefused):
            _ship(runner, tree, allow_failing_checks=False)


class TestOverride:
    """B147a/B147b - an override changes whether the PR opens, not what it claims."""

    def test_an_overridden_run_states_the_failure_in_the_body(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        outcome = _ship(runner, tree, allow_failing_checks=True)

        assert outcome.check.passed is False
        assert "did not pass" in outcome.body_text.lower()

    def test_an_overridden_body_never_asserts_green_while_red(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        outcome = _ship(runner, tree, allow_failing_checks=True)

        assert "all gates passed" not in outcome.body_text.lower()

    def test_an_overridden_run_still_exits_non_zero(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        outcome = _ship(runner, tree, allow_failing_checks=True)

        assert outcome.exit_code != 0


# ==========================================================================
# The body (B148-B151)
# ==========================================================================


class TestBody:
    """B148-B150 - the body is summary plus links, pinned to a SHA."""

    def test_the_body_is_summary_plus_links(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        for heading in ("## Why", "## What changed", "## Evidence", "## Artifacts"):
            assert heading in outcome.body_text

    def test_the_body_never_embeds_an_artifacts_content(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert ARTIFACT_SENTINEL not in outcome.body_text

    def test_the_body_title_comes_from_the_design_specs_h1(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.body_text.startswith("# Ship the phase")

    def test_a_title_flag_overrides_the_design_spec_h1(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree, title="A deliberate override")

        assert outcome.body_text.startswith("# A deliberate override")

    def test_the_body_quotes_the_design_specs_purpose_paragraph(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert "Ship turns a finished phase into a pull request." in outcome.body_text

    def test_what_changed_lists_the_commit_subjects_on_the_branch(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(subjects=("[Phase 5] First", "[Phase 5] Second"))

        outcome = _ship(runner, tree)

        assert "[Phase 5] First" in outcome.body_text
        assert "[Phase 5] Second" in outcome.body_text


class TestArtifactLinks:
    """B149 - links are pinned to the pushed commit SHA, never a branch."""

    def test_artifact_links_point_at_the_pushed_commit_sha(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert HEAD_SHA in outcome.body_text
        assert outcome.commit_sha == HEAD_SHA

    def test_no_artifact_link_uses_a_branch_name(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        artifacts_section = outcome.body_text.split("## Artifacts", 1)[1]
        assert "/blob/phase-05-ship/" not in artifacts_section

    def test_no_artifact_link_points_at_the_base_branch(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        artifacts_section = outcome.body_text.split("## Artifacts", 1)[1]
        assert "/blob/main/" not in artifacts_section

    def test_the_push_happens_before_the_body_is_assembled(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=False)

        _ship(runner, tree, push=True)

        push_index = next(i for i, c in enumerate(runner.commands) if c[:2] == ("git", "push"))
        sha_index = next(i for i, c in enumerate(runner.commands) if c == ("git", "rev-parse", "HEAD"))
        assert push_index < sha_index


class TestBodyFile:
    """B150/B151 - the file is newline-clean and travels by --body-file."""

    def test_the_body_file_contains_no_carriage_return(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert b"\r" not in outcome.body_path.read_bytes()

    def test_the_reported_size_is_the_character_count_not_the_byte_count(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.body_char_count == len(outcome.body_text)

    def test_the_body_travels_by_body_file(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url=None)

        _ship(runner, tree)

        gh_writes = [c for c in runner.commands if c[0] == "gh" and c[1:3] in {("pr", "create"), ("pr", "edit")}]
        assert gh_writes
        assert all("--body-file" in c for c in gh_writes)

    def test_the_body_flag_never_appears_in_the_argv(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        _ship(runner, tree)

        for cmd in runner.commands:
            if cmd[0] == "gh":
                assert "--body" not in cmd


# ==========================================================================
# Creating and updating (B152-B155)
# ==========================================================================


class TestCreateAndUpdate:
    """B152-B154 - query first, update on re-run, pass gh's error through."""

    def test_an_existing_pr_is_queried_before_any_create(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=False)
        runner = ShipRunner(existing_pr_url="https://github.com/octocat/atom/pull/7")

        outcome = _ship(runner, tree)

        gh_pr_calls = [c for c in runner.commands if c[0] == "gh" and c[1] == "pr"]
        assert gh_pr_calls[0][1:3] == ("pr", "view")
        assert outcome.pr_action is PrAction.UPDATED
        assert not any(c[1:3] == ("pr", "create") for c in gh_pr_calls)
        # The URL is the real one parsed out of the query, not the raw JSON blob.
        assert outcome.pr_url == "https://github.com/octocat/atom/pull/7"

    def test_the_duplicate_error_is_treated_as_a_fallback_not_the_primary_signal(self, tmp_path):
        # The query is the primary signal: an existing PR is updated without the
        # code ever depending on gh's duplicate stderr wording.
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url="https://github.com/octocat/atom/pull/7")

        outcome = _ship(runner, tree)

        assert outcome.pr_action is PrAction.UPDATED

    def test_the_duplicate_error_still_recovers_when_the_query_missed_it(self, tmp_path):
        # Fallback: the query found nothing, create hit a duplicate; ship must
        # recover by editing rather than surfacing gh's duplicate as a failure.
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url=None, create_duplicate=True)

        outcome = _ship(runner, tree)

        assert outcome.pr_action is PrAction.UPDATED
        assert any(c[1:3] == ("pr", "edit") for c in runner.commands if c[0] == "gh")

    def test_re_running_on_a_branch_with_a_pr_updates_the_body(self, tmp_path):
        # B153: a second ship on the same branch edits the open PR rather than
        # failing or opening a duplicate.
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url="https://github.com/octocat/atom/pull/7")

        outcome = _ship(runner, tree)

        assert any(c[1:3] == ("pr", "edit") for c in runner.commands if c[0] == "gh")
        assert outcome.pr_action is PrAction.UPDATED

    def test_re_running_is_not_treated_as_an_error(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url="https://github.com/octocat/atom/pull/7")

        outcome = _ship(runner, tree)

        assert outcome.exit_code == 0

    def test_ghs_error_text_is_passed_through_verbatim(self, tmp_path):
        verbatim = "HTTP 401: Bad credentials\nTry authenticating with: gh auth login -h github.com"
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url=None, create_stderr=verbatim)

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "gh auth login -h github.com" in str(excinfo.value)

    def test_every_gh_call_receives_empty_stdin(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        _ship(runner, tree)

        gh_stdins = [
            runner.stdins[i] for i, c in enumerate(runner.commands) if c[0] == "gh"
        ]
        assert gh_stdins
        assert all(text == "" for text in gh_stdins)


# ==========================================================================
# Failure handling and scope (B156-B157)
# ==========================================================================


class TestExitCodesAndScope:
    """B156/B157 - reused exit codes, and never a commit."""

    def test_ship_reuses_the_phase_one_to_three_exit_codes(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.exit_code in (0, 1)
        assert outcome.exit_code == 0

    def test_an_unmet_precondition_exits_by_the_ordinary_failure_route(self, tmp_path):
        # A precondition and a failing check refuse through the *same* exception
        # type, so there is no separate precondition exit route.
        tree_precondition = _make_tree(tmp_path / "a")
        tree_check = _make_tree(tmp_path / "b", go_mod=True)

        with pytest.raises(ShipRefused):
            _ship(ShipRunner(branch="HEAD"), tree_precondition)
        with pytest.raises(ShipRefused):
            _ship(
                ShipRunner(failing_gate=("go", "build", "./...")),
                tree_check,
                allow_failing_checks=False,
            )

    def test_there_is_no_distinct_precondition_exit_code(self, tmp_path):
        # ShipRefused carries no bespoke exit code; the CLI maps every refusal
        # through the one established failure code.
        tree = _make_tree(tmp_path)
        with pytest.raises(ShipRefused) as excinfo:
            _ship(ShipRunner(gh_present=False), tree)

        assert not hasattr(excinfo.value, "exit_code")

    def test_ship_never_issues_a_commit(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        _ship(runner, tree, push=True)

        assert not any(c[:2] == ("git", "commit") for c in runner.commands)

    def test_no_git_commit_command_is_ever_run(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=False)

        _ship(runner, tree, push=True)

        assert not any("commit" in c for c in runner.commands)


# ==========================================================================
# Outcome shape, degraded git, and edge cases
# ==========================================================================


class TestOutcomeShape:
    """The ShipOutcome the CLI wiring will read to choose a message and exit."""

    def test_a_clean_run_reports_succeeded(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.succeeded is True

    def test_an_overridden_run_reports_not_succeeded(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        outcome = _ship(runner, tree, allow_failing_checks=True)

        assert outcome.succeeded is False

    def test_a_created_pr_reports_the_created_action_and_url(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url=None)

        outcome = _ship(runner, tree)

        assert outcome.pr_action is PrAction.CREATED
        assert outcome.pr_url == "https://github.com/octocat/atom/pull/9"


class TestDegradedGit:
    """Every git command that can fail is surfaced as a refusal, never a crash."""

    def test_an_unreadable_branch_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        with pytest.raises(ShipRefused):
            _ship(ShipRunner(branch_ok=False), tree)

    def test_an_unreadable_status_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        with pytest.raises(ShipRefused):
            _ship(ShipRunner(status_ok=False), tree)

    def test_a_failed_push_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        with pytest.raises(ShipRefused):
            _ship(ShipRunner(has_upstream=False, push_ok=False), tree, push=True)

    def test_an_unresolvable_head_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        with pytest.raises(ShipRefused):
            _ship(ShipRunner(head_ok=False), tree)

    def test_a_missing_origin_remote_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        with pytest.raises(ShipRefused):
            _ship(ShipRunner(remote_ok=False), tree)

    def test_a_failed_log_leaves_the_what_changed_section_empty_not_fatal(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(log_ok=False)

        outcome = _ship(runner, tree)

        assert "No commits on the branch" in outcome.body_text

    def test_a_failed_edit_is_refused_with_ghs_text(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(
            existing_pr_url="https://github.com/octocat/atom/pull/7", edit_ok=False
        )

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "could not update pull request" in str(excinfo.value)

    def test_a_create_failure_with_no_output_still_refuses(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url=None, create_empty_fail=True)

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "no output" in str(excinfo.value)

    def test_a_create_success_without_a_url_falls_back_to_raw_stdout(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_url=None, create_stdout="opened\n")

        outcome = _ship(runner, tree)

        assert outcome.pr_action is PrAction.CREATED
        assert outcome.pr_url == "opened"


class TestPhaseResolutionEdges:
    """The phase resolver's direct-path, ambiguity, and outside-tree branches."""

    def test_a_direct_relative_path_resolves_the_phase(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner()

        outcome = _ship(runner, tree, phase="specs/atom-cli/phase-05-ship")

        assert outcome.phase_directory.name == "phase-05-ship"

    def test_an_ambiguous_phase_name_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path, project="proj-a")
        # A second project with the same phase name makes the glob ambiguous.
        (tmp_path / "specs" / "proj-b" / "phase-05-ship").mkdir(parents=True)
        runner = ShipRunner()

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "more than one" in str(excinfo.value).lower()

    def test_an_artifact_outside_the_repo_root_keeps_its_full_path(self, tmp_path):
        # A phase directory reached by an absolute path outside the working tree
        # cannot be made relative to it; the link falls back to the full path
        # rather than crashing.
        repo = _make_tree(tmp_path / "repo")
        outside = tmp_path / "outside" / "phase-05-ship"
        outside.mkdir(parents=True)
        (outside / "design-spec.md").write_text("# Outside\n\n## Purpose\n\nx\n", encoding="utf-8")
        runner = ShipRunner()

        outcome = _ship(runner, repo, phase=str(outside))

        assert outcome.artifacts == (outside.joinpath("design-spec.md").as_posix(),)


class TestBareTitleAndSlug:
    """Fallbacks: no design spec, and the SSH remote URL spelling."""

    def test_the_title_falls_back_to_the_branch_when_no_design_spec(self, tmp_path):
        tree = _make_tree(tmp_path, with_design_spec=False, artifacts=("poc-report.md",))
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.body_text.startswith("# phase-05-ship")
        assert "no Purpose section" in outcome.body_text

    def test_a_design_spec_without_an_h1_falls_back_to_the_branch_title(self, tmp_path):
        # The spec is present but headless: the title resolver scans it, finds no
        # `# ` line, and falls back to the branch name.
        tree = _make_tree(tmp_path, with_design_spec=False, artifacts=("poc-report.md",))
        phase_dir = tree / "specs" / "atom-cli" / "phase-05-ship"
        (phase_dir / "design-spec.md").write_text(
            "## Purpose\n\nNo top-level heading here.\n", encoding="utf-8"
        )
        runner = ShipRunner()

        outcome = _ship(runner, tree)

        assert outcome.body_text.startswith("# phase-05-ship")

    def test_an_ssh_remote_url_yields_the_owner_name_slug(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(remote_url="git@github.com:octocat/atom.git")

        outcome = _ship(runner, tree)

        assert "octocat/atom/blob/" in outcome.body_text

    def test_a_pr_view_with_empty_output_is_treated_as_no_existing_pr(self, tmp_path):
        # gh exits 0 but prints nothing: there is no URL, so ship creates.
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_stdout="")

        outcome = _ship(runner, tree)

        assert outcome.pr_action is PrAction.CREATED

    def test_a_pr_view_that_prints_a_bare_url_is_accepted(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(existing_pr_stdout="https://github.com/octocat/atom/pull/3")

        outcome = _ship(runner, tree)

        assert outcome.pr_action is PrAction.UPDATED
        assert outcome.pr_url == "https://github.com/octocat/atom/pull/3"


class TestDirtyTreeParsing:
    """B140 - porcelain parsing survives blank lines and renames."""

    def test_a_rename_lists_the_new_path(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(status_porcelain="R  old/name.py -> new/name.py\n\n")

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        assert "new/name.py" in str(excinfo.value)



class TestRefusalLeavesTheRemoteAlone:
    """B147 ordering -- the fresh check runs before the push, so a refusal
    cannot publish the branch on its way to declining.

    These tests exist because the reorder that introduced this guarantee was
    invisible to the other 83: every one of them passed both before and after
    the change. An ordering nothing asserts is an ordering free to regress.
    """

    def test_a_refused_ship_never_pushes_even_when_push_was_requested(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        with pytest.raises(ShipRefused):
            _ship(runner, tree, push=True, allow_failing_checks=False)

        pushes = [c for c in runner.commands if c[0] == "git" and "push" in c]
        assert pushes == [], f"a refusal mutated the remote: {pushes}"

    def test_the_check_runs_before_the_push_on_a_passing_run(self, tmp_path):
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner()

        _ship(runner, tree, push=True)

        first_gate = next(
            i for i, c in enumerate(runner.commands) if c[0] in ("go", "gofmt")
        )
        pushed_at = next(
            i for i, c in enumerate(runner.commands) if c[0] == "git" and "push" in c
        )
        assert first_gate < pushed_at

    def test_an_overridden_failing_check_still_pushes(self, tmp_path):
        # Guards the other side of the reorder: moving the check earlier must
        # not cost the push on the one failing path that is allowed to ship.
        tree = _make_tree(tmp_path, go_mod=True)
        runner = ShipRunner(failing_gate=("go", "build", "./..."))

        _ship(runner, tree, push=True, allow_failing_checks=True)

        assert any(c[0] == "git" and "push" in c for c in runner.commands)


class TestTheRemoteActuallyHasTheCommit:
    """B141, amended -- an upstream existing is not the same fact as the
    remote holding this commit.

    Found by `atom review` on this very branch, reported independently in three
    of six model runs, and missed by all 104 tests written before it. The
    original precondition asked only whether an upstream was configured. A
    branch with an upstream and three unpushed commits passed it, and then B149
    pinned every artifact link to a commit GitHub had never seen -- the exact
    404 that B149 exists to prevent.
    """

    def test_a_branch_ahead_of_its_upstream_is_refused(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=True, commits_ahead=3)

        with pytest.raises(ShipRefused):
            _ship(runner, tree)

    def test_the_refusal_says_how_far_ahead_and_how_to_fix_it(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=True, commits_ahead=3)

        with pytest.raises(ShipRefused) as excinfo:
            _ship(runner, tree)

        message = str(excinfo.value)
        assert "3" in message
        assert "--push" in message

    def test_a_branch_level_with_its_upstream_ships(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=True, commits_ahead=0)

        outcome = _ship(runner, tree)

        assert outcome.pr_url

    def test_being_ahead_is_irrelevant_when_push_was_requested(self, tmp_path):
        # --push resolves the problem rather than describing it, so the
        # ahead-count must not refuse a run that is about to push.
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=True, commits_ahead=3)

        outcome = _ship(runner, tree, push=True)

        assert outcome.pushed is True

    def test_no_pr_is_opened_when_the_commit_is_not_on_the_remote(self, tmp_path):
        tree = _make_tree(tmp_path)
        runner = ShipRunner(has_upstream=True, commits_ahead=1)

        with pytest.raises(ShipRefused):
            _ship(runner, tree)

        assert not any(c[1:3] == ("pr", "create") for c in runner.commands if c[0] == "gh")
