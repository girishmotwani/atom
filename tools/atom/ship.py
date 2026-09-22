"""Assemble a finished phase into a pull request without re-typing what is on disk.

`atom ship` is the smallest command in the tool, and deliberately so. The branch,
the commits, the spec, the POC report and the review are all written down already;
ship's only job is to point at them and to attach evidence that the tree is green
*right now*. It writes nothing into the repository and creates nothing a human did
not already create -- in particular it never commits (B157), because a tool that
commits on the developer's behalf decides what a change *is*, and that is the
developer's decision.

This module is the analogue of `review.py`: a frozen `ShipOutcome` describing what
one run amounted to, plus a `run_ship(...)` function that drives `git` and `gh`
through the same `CommandRunner` seam every other command uses. The rendering of
the body lives in `body.py`; the create-or-update decision and every precondition
live here.

Two orderings in this module are behaviours, not implementation details:

*   **Preconditions are all checked before any work begins (B138-B142).** A
    failure costs a second rather than leaving a half-made pull request behind,
    and `gh`'s absence in particular is reported as an unmet precondition naming
    the install, not as a failure partway through (C15: the only `gh` on the
    development machine was the Copilot app's bundled copy).

*   **The push happens before the body is assembled (B149).** The body links to
    artifacts *at a commit SHA*, and a link to a commit the remote has never seen
    is a 404. Assembling first would produce a PR whose every link was broken
    until the moment it wasn't.

See `specs/atom-cli/phase-05-ship/design-spec.md` for B138-B157 and
`poc-report.md` for the measured consequences C10-C16 they rest on.
"""

from __future__ import annotations

import enum
import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from atom.body import (
    BodyInputs,
    CheckSummary,
    extract_purpose,
    render_body,
    write_body_file,
)
from atom.check import NotAGoModuleError, run_check
from atom.gates import Gate, GateStatus, default_gates
from atom.runner import CommandOutcome, CommandResult, CommandRunner

# The branch a pull request opens *into* by default. Named here rather than
# guessed per call so B139's "the current branch is the base branch itself"
# refusal has a single, overridable definition of what the base is.
DEFAULT_BASE_BRANCH = "main"

# The recorded line the body carries when there is no Go module to gate. Kept as
# a constant because two behaviours depend on its exact text: B145a records the
# absence as an absence, and B146 replaces the verdict table with this one line
# rather than dropping the section.
NO_MODULE_REASON = "not a Go module; no gates run"

# `git rev-parse --abbrev-ref HEAD` prints this literal string on a detached
# HEAD, where there is no branch name to print. It is the signal B139 refuses on.
_DETACHED_HEAD_MARKER = "HEAD"


class ShipRefused(Exception):
    """Raised for any unmet precondition or gating refusal.

    Deliberately one exception type for every refusal -- a missing `gh`, a dirty
    tree, a failing check -- because B156 says ship reuses the Phase 1-3 exit
    scheme and introduces no distinct "precondition" code. The caller maps every
    `ShipRefused` through the one established failure route, so this class carries
    a message and nothing else.
    """


class PrAction(enum.Enum):
    """Whether this run opened a new pull request or updated an existing one."""

    CREATED = "created"
    UPDATED = "updated"


@dataclass(frozen=True)
class ShipOutcome:
    """Everything one `atom ship` produced, and whether it should exit clean."""

    branch: str
    base_branch: str
    phase_directory: Path
    artifacts: tuple[str, ...]
    check: CheckSummary
    check_overridden: bool
    commit_sha: str
    body_text: str
    body_path: Path
    body_char_count: int
    pushed: bool
    pr_action: PrAction
    pr_url: str

    @property
    def succeeded(self) -> bool:
        """Return true only when the fresh check did not fail (B147b).

        A check that was *absent* (no Go module) passed by B145a's reading, so a
        clean ship of a non-Go tree succeeds; a check that ran and failed did not
        succeed even when `--allow-failing-checks` let the PR open anyway.
        """

        return self.check.passed

    @property
    def exit_code(self) -> int:
        """Return the process exit code this outcome implies.

        Reuses the Phase 1-3 scheme (0 pass, 1 failure) rather than inventing a
        code (B156). An overridden failing check produced a PR yet still exits
        non-zero, on B136's precedent that the artifact existing and the run
        succeeding are different facts (B147b).
        """

        return 0 if self.check.passed else 1


def run_ship(
    runner: CommandRunner,
    working_directory: Path,
    *,
    base_branch: str = DEFAULT_BASE_BRANCH,
    phase: str | None = None,
    title: str | None = None,
    push: bool = False,
    allow_failing_checks: bool = False,
    gates: Sequence[Gate] | None = None,
) -> ShipOutcome:
    """Turn the current branch's finished phase into a pull request.

    The pipeline is fixed and its order is load-bearing: preconditions, resolve
    the phase, a fresh ``atom check``, push (only with ``--push``), assemble the
    body, then create or update the PR. Push precedes assembly so the body's
    commit-pinned links reference a commit the remote already holds (B149), and
    the check precedes the push so a refusal leaves the remote untouched.

    Raises:
        ShipRefused: any unmet precondition, a missing phase directory, or a
            failing check without ``allow_failing_checks``.
    """

    # -- Preconditions (B138-B142), all before any work ---------------------

    _verify_gh_present(runner, working_directory)

    branch = _current_branch(runner, working_directory)
    _refuse_unshippable_branch(branch, base_branch)

    _refuse_dirty_tree(runner, working_directory)

    if not push:
        _require_upstream(runner, working_directory, branch)

    # -- Resolve the phase (B143-B144) --------------------------------------

    phase_directory = _resolve_phase_directory(working_directory, branch, phase)
    artifacts = _phase_artifacts(working_directory, phase_directory)

    # -- Fresh check evidence (B145-B147) -----------------------------------

    check = _run_fresh_check(runner, working_directory, gates)
    check_overridden = False
    if not check.passed:
        if not allow_failing_checks:
            raise ShipRefused(
                f"atom check failed: {_failing_gate_names(check)}. "
                "Fix the failing gates and re-run, or pass --allow-failing-checks "
                "to ship over them -- the failure is stated in the body either way."
            )
        # B147a/B147b: the override opens the PR but changes nothing the body
        # claims, and the run still exits non-zero.
        check_overridden = True

    # -- Push before the body is assembled (B142, B149) ---------------------
    #
    # The check deliberately runs *before* this point. B149 only requires that
    # the push precede body assembly -- so that every artifact link names a
    # commit the remote already holds -- and this order still satisfies that.
    # Pushing earlier would buy nothing and cost something: a run that refuses
    # on a failing gate would already have published the branch and set its
    # upstream, making a refusal a remote-mutating event. A command that
    # declines to act should leave no trace.

    pushed = False
    if push:
        _push_branch(runner, working_directory, branch)
        pushed = True

    # -- Assemble the body (B148-B151); SHA resolved only now ---------------

    commit_sha = _head_sha(runner, working_directory)
    subjects = _commit_subjects(runner, working_directory, branch, base_branch)
    repo_slug = _repo_slug(runner, working_directory)
    resolved_title = _resolve_title(title, phase_directory, branch)
    purpose = _purpose(phase_directory)

    body_text = render_body(
        BodyInputs(
            title=resolved_title,
            purpose=purpose,
            commit_subjects=subjects,
            check=check,
            artifacts=artifacts,
            repo_slug=repo_slug,
            commit_sha=commit_sha,
        )
    )
    body_path = _body_file_path()
    body_char_count = write_body_file(body_text, body_path)

    # -- Create or update the pull request (B152-B155) ----------------------

    pr_action, pr_url = _create_or_update_pull_request(
        runner,
        working_directory,
        branch=branch,
        base_branch=base_branch,
        title=resolved_title,
        body_path=body_path,
    )

    return ShipOutcome(
        branch=branch,
        base_branch=base_branch,
        phase_directory=phase_directory,
        artifacts=artifacts,
        check=check,
        check_overridden=check_overridden,
        commit_sha=commit_sha,
        body_text=body_text,
        body_path=body_path,
        body_char_count=body_char_count,
        pushed=pushed,
        pr_action=pr_action,
        pr_url=pr_url,
    )


# ==========================================================================
# Preconditions
# ==========================================================================


def _verify_gh_present(runner: CommandRunner, working_directory: Path) -> None:
    """Refuse when `gh` cannot be launched, before any git work (B138, C15).

    `gh`'s absence is an unmet precondition, not a mid-run failure: on a machine
    without the Copilot app's bundled copy there is no `gh` at all, and the
    developer needs the install named rather than a stack trace three steps in.
    """

    result = runner.run(("gh", "--version"), working_directory, stdin_text="")
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(
            "atom ship needs the GitHub CLI (gh), which was not found. "
            "Install it from https://cli.github.com/ and authenticate with "
            "`gh auth login`, then run atom ship again."
        )


def _current_branch(runner: CommandRunner, working_directory: Path) -> str:
    """Return the checked-out branch name, or the detached-HEAD marker."""

    result = runner.run(
        ("git", "rev-parse", "--abbrev-ref", "HEAD"), working_directory, stdin_text=""
    )
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(
            "atom ship could not read the current branch. "
            f"git said: {_verbatim(result)}"
        )
    return result.stdout.strip()


def _refuse_unshippable_branch(branch: str, base_branch: str) -> None:
    """Refuse a detached HEAD or the base branch itself (B139)."""

    if branch == _DETACHED_HEAD_MARKER or not branch:
        raise ShipRefused(
            "atom ship refuses to run on a detached HEAD -- there is no branch to "
            "open a pull request from. Check out a branch and try again."
        )

    if branch == base_branch:
        raise ShipRefused(
            f"atom ship refuses to ship '{base_branch}' into itself -- the current "
            f"branch is the base branch. Ship from a phase branch instead."
        )


def _refuse_dirty_tree(runner: CommandRunner, working_directory: Path) -> None:
    """Refuse a dirty working tree, listing the modified files (B140).

    The refusal exists because the body links to artifacts *at a commit* while the
    fresh check runs against the *working tree*; when the tree is dirty those are
    different states, and the PR would present evidence gathered from files not in
    the commit it points at.
    """

    result = runner.run(("git", "status", "--porcelain"), working_directory, stdin_text="")
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(
            "atom ship could not read the working-tree status. "
            f"git said: {_verbatim(result)}"
        )

    modified = _porcelain_paths(result.stdout)
    if modified:
        listed = "\n".join(f"  {path}" for path in modified)
        raise ShipRefused(
            "atom ship refuses to run with a dirty working tree, because the body "
            "would point at a commit that does not contain these changes:\n"
            f"{listed}\n"
            "Commit or stash them first."
        )


def _require_upstream(runner: CommandRunner, working_directory: Path, branch: str) -> None:
    """Refuse a branch with no upstream, naming the command that fixes it (B141).

    Ship requires an upstream because `gh` will not push (C13); without one and
    without ``--push`` there is nothing for the PR's links to resolve against. The
    refusal prints the exact `git push` that would set the upstream, so the fix is
    a copy rather than a lookup.
    """

    result = runner.run(
        ("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"),
        working_directory,
        stdin_text="",
    )
    if result.outcome is CommandOutcome.COMPLETED and result.exit_code == 0:
        return

    raise ShipRefused(
        f"atom ship needs branch '{branch}' to have an upstream, and it has none. "
        "Either push it yourself:\n"
        f"  git push --set-upstream origin {branch}\n"
        "or re-run with --push, which does exactly that."
    )


def _push_branch(runner: CommandRunner, working_directory: Path, branch: str) -> None:
    """Push the branch and set its upstream, never delegating to `gh` (B142).

    The POC proved `gh` refuses to push -- `gh pr create` on a branch with no
    upstream aborts in 1.4s naming the missing push -- so ship does the push
    itself with `git` and treats the upstream as its own responsibility (C13).
    """

    result = runner.run(
        ("git", "push", "--set-upstream", "origin", branch), working_directory, stdin_text=""
    )
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(
            f"atom ship could not push branch '{branch}'. "
            f"git said: {_verbatim(result)}"
        )


# ==========================================================================
# Phase resolution
# ==========================================================================


def _resolve_phase_directory(
    working_directory: Path, branch: str, phase: str | None
) -> Path:
    """Locate the phase directory from the branch name, or ``--phase`` (B143).

    The branch name is already the phase name under branch-per-phase, so nothing
    has to be passed or remembered. A path that does not exist is refused, naming
    what was tried, rather than being silently invented.
    """

    phase_slug = phase or branch

    # A caller may pass a full relative path (e.g. specs/atom-cli/phase-05-ship)
    # or the bare phase name; try the literal path first so both spellings work.
    direct = working_directory / phase_slug
    if direct.is_dir():
        return direct

    specs_root = working_directory / "specs"
    if specs_root.is_dir():
        matches = sorted(
            candidate
            for candidate in specs_root.glob(f"*/{phase_slug}")
            if candidate.is_dir()
        )
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            listed = ", ".join(str(match) for match in matches)
            raise ShipRefused(
                f"atom ship found more than one phase directory named '{phase_slug}': "
                f"{listed}. Pass --phase with the specific path."
            )

    raise ShipRefused(
        f"atom ship could not find a phase directory for '{phase_slug}'. "
        f"Tried {direct} and specs/*/{phase_slug}. "
        "Pass --phase with the directory to use."
    )


def _phase_artifacts(working_directory: Path, phase_directory: Path) -> tuple[str, ...]:
    """Return every file in the phase directory as a repo-relative POSIX path (B144).

    The artifacts are whatever files the directory holds; a missing one is simply
    not listed. Directories are skipped because an artifact is a file the body can
    link to, and the paths are made relative to the repository root so the body's
    links resolve from it.
    """

    files = sorted(
        child for child in phase_directory.iterdir() if child.is_file()
    )
    return tuple(_relative_posix(path, working_directory) for path in files)


# ==========================================================================
# Fresh check evidence
# ==========================================================================


def _run_fresh_check(
    runner: CommandRunner, working_directory: Path, gates: Sequence[Gate] | None
) -> CheckSummary:
    """Run `atom check` fresh and summarise it, or record a missing Go module.

    B145 makes the check fresh at ship time; a recorded earlier result is never
    accepted, so this always calls `run_check`. B145a turns the one non-failure
    `run_check` cannot express as a report -- a directory with no `go.mod`, which
    it signals by raising -- into a recorded absence rather than a failure.
    """

    resolved_gates = list(gates) if gates is not None else default_gates()

    try:
        report = run_check(working_directory, resolved_gates, runner)
    except NotAGoModuleError:
        # B145a. The Atom repository itself has no go.mod, so an unqualified B145
        # would make atom ship unable to ship Atom. Absence is not failure --
        # check.py already settles the analogous case: a tree with no tests has
        # not failed, and a tree with no Go module has not failed either.
        return CheckSummary(gate_rows=(), absent_reason=NO_MODULE_REASON, passed=True)

    gate_rows = tuple(
        (result.name, result.status.value) for result in report.gate_results
    )[:5]  # B146: bounded at five rows; the full output never enters the body.
    return CheckSummary(gate_rows=gate_rows, absent_reason=None, passed=report.passed)


def _failing_gate_names(check: CheckSummary) -> str:
    """List the gates whose recorded status is a failure, for the refusal (B147)."""

    failing = [
        name
        for name, status in check.gate_rows
        if status == GateStatus.FAILED.value
    ]
    return ", ".join(failing) if failing else "one or more gates"


# ==========================================================================
# Body assembly inputs
# ==========================================================================


def _head_sha(runner: CommandRunner, working_directory: Path) -> str:
    """Return the full HEAD SHA the artifact links are pinned to (B149)."""

    result = runner.run(("git", "rev-parse", "HEAD"), working_directory, stdin_text="")
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(
            "atom ship could not resolve HEAD to a commit SHA. "
            f"git said: {_verbatim(result)}"
        )
    return result.stdout.strip()


def _commit_subjects(
    runner: CommandRunner, working_directory: Path, branch: str, base_branch: str
) -> tuple[str, ...]:
    """Return the commit subjects on this branch, for the What changed section."""

    result = runner.run(
        ("git", "log", f"{base_branch}..HEAD", "--format=%s"),
        working_directory,
        stdin_text="",
    )
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        # A missing base ref should not sink the whole ship: the section renders
        # its own emptiness rather than the command's failure becoming fatal.
        return ()
    return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())


def _repo_slug(runner: CommandRunner, working_directory: Path) -> str:
    """Return the ``owner/name`` slug the artifact links are built from."""

    result = runner.run(
        ("git", "remote", "get-url", "origin"), working_directory, stdin_text=""
    )
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(
            "atom ship could not read the origin remote URL, which the artifact "
            f"links need. git said: {_verbatim(result)}"
        )
    return _slug_from_remote_url(result.stdout.strip())


def _resolve_title(title: str | None, phase_directory: Path, branch: str) -> str:
    """Return the body title: ``--title``, else the spec H1, else the branch (B148)."""

    if title is not None:
        return title

    heading = _design_spec_h1(phase_directory)
    if heading is not None:
        return heading

    return branch


def _purpose(phase_directory: Path) -> str | None:
    """Return the design spec's Purpose prose, or None when there is none (B148)."""

    spec = _read_design_spec(phase_directory)
    if spec is None:
        return None
    return extract_purpose(spec)


# ==========================================================================
# Creating and updating the pull request
# ==========================================================================


def _create_or_update_pull_request(
    runner: CommandRunner,
    working_directory: Path,
    *,
    branch: str,
    base_branch: str,
    title: str,
    body_path: Path,
) -> tuple[PrAction, str]:
    """Update an existing PR or create a new one, querying first (B152, B153).

    The existing-PR query is the primary signal, not `gh`'s duplicate error:
    depending on stderr wording to detect the normal re-run case would make the
    tool hostage to `gh`'s phrasing (C12). The duplicate error is kept only as a
    fallback for the race where the query missed a PR another push had just made.
    """

    existing_url = _existing_pr_url(runner, working_directory)
    if existing_url is not None:
        _edit_pull_request(runner, working_directory, body_path)
        return PrAction.UPDATED, existing_url

    return _create_pull_request(
        runner,
        working_directory,
        branch=branch,
        base_branch=base_branch,
        title=title,
        body_path=body_path,
    )


def _existing_pr_url(runner: CommandRunner, working_directory: Path) -> str | None:
    """Return the current branch's open PR URL, or None when there is none (B152).

    `gh pr view` exits non-zero when the branch has no PR, which is the primary
    signal. The URL is read out of `--json` output rather than `--jq`, so the
    query does not depend on `jq` being resolvable through the same launcher
    quirks the POC measured for the tools themselves.
    """

    result = runner.run(
        ("gh", "pr", "view", "--json", "url"),
        working_directory,
        stdin_text="",
    )
    if result.outcome is CommandOutcome.COMPLETED and result.exit_code == 0:
        return _url_from_pr_view(result.stdout)
    return None


def _url_from_pr_view(stdout: str) -> str | None:
    """Pull the ``url`` field out of `gh pr view --json url` output."""

    text = stdout.strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        # A bare URL rather than JSON is still usable; treat it as the answer.
        return text or None
    url = payload.get("url") if isinstance(payload, dict) else None
    return url or None


def _edit_pull_request(
    runner: CommandRunner, working_directory: Path, body_path: Path
) -> None:
    """Refresh an existing PR's body via ``--body-file`` (B151, B153)."""

    result = runner.run(
        ("gh", "pr", "edit", "--body-file", str(body_path)),
        working_directory,
        stdin_text="",
    )
    if result.outcome is not CommandOutcome.COMPLETED or result.exit_code != 0:
        raise ShipRefused(_verbatim(result))


def _create_pull_request(
    runner: CommandRunner,
    working_directory: Path,
    *,
    branch: str,
    base_branch: str,
    title: str,
    body_path: Path,
) -> tuple[PrAction, str]:
    """Create a PR, falling back to an edit if `gh` reports it already exists (B152)."""

    result = runner.run(
        (
            "gh", "pr", "create",
            "--base", base_branch,
            "--head", branch,
            "--title", title,
            "--body-file", str(body_path),
        ),
        working_directory,
        stdin_text="",
    )

    if result.outcome is CommandOutcome.COMPLETED and result.exit_code == 0:
        return PrAction.CREATED, _first_url(result.stdout) or result.stdout.strip()

    # Fallback only: the query said there was no PR, yet gh reports a duplicate.
    # Recover by editing the one that already exists rather than surfacing gh's
    # duplicate message as a failure (C12).
    duplicate_url = _duplicate_pr_url(result)
    if duplicate_url is not None:
        _edit_pull_request(runner, working_directory, body_path)
        return PrAction.UPDATED, duplicate_url

    # Any other failure is gh's to explain; its text names the exact next command
    # far better than a paraphrase would (B154, C14), so it is passed through.
    raise ShipRefused(_verbatim(result))


# ==========================================================================
# Small helpers
# ==========================================================================


def _porcelain_paths(porcelain_output: str) -> list[str]:
    """Turn `git status --porcelain` lines into the paths they name.

    Porcelain v1 prefixes each path with a two-character status and a space; a
    rename is written `old -> new`, and the file the developer needs named is the
    new one on the right.
    """

    paths: list[str] = []
    for line in porcelain_output.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip())
    return paths


def _slug_from_remote_url(remote_url: str) -> str:
    """Reduce an origin URL to its ``owner/name`` slug.

    Handles both the HTTPS (`https://github.com/owner/name.git`) and SSH
    (`git@github.com:owner/name.git`) spellings, and tolerates a missing `.git`
    suffix, because the slug is what the body's blob links are built from.
    """

    url = remote_url.strip()
    if url.endswith(".git"):
        url = url[: -len(".git")]

    if ":" in url and "://" not in url:
        # SSH form: git@github.com:owner/name
        url = url.split(":", 1)[1]
    else:
        # HTTPS or other URL form: keep everything after the host.
        without_scheme = url.split("://", 1)[-1]
        parts = without_scheme.split("/", 1)
        url = parts[1] if len(parts) == 2 else without_scheme

    return url.strip("/")


def _design_spec_h1(phase_directory: Path) -> str | None:
    """Return the design spec's first `# ` heading text, or None."""

    spec = _read_design_spec(phase_directory)
    if spec is None:
        return None

    for line in spec.splitlines():
        if line.startswith("# "):
            return line[len("# ") :].strip()
    return None


def _read_design_spec(phase_directory: Path) -> str | None:
    """Return the phase's design-spec.md text, or None when it is absent."""

    spec_path = phase_directory / "design-spec.md"
    if not spec_path.is_file():
        return None
    return spec_path.read_text(encoding="utf-8")


def _body_file_path() -> Path:
    """Return a fresh temp path for the body file.

    A temp file rather than a path inside the repository: ship refuses on a dirty
    tree (B140), and writing the body into the working tree would create exactly
    the untracked file that refusal exists to prevent.
    """

    handle = tempfile.NamedTemporaryFile(
        prefix="atom-ship-body-", suffix=".md", delete=False
    )
    handle.close()
    return Path(handle.name)


def _relative_posix(path: Path, root: Path) -> str:
    """Return ``path`` relative to ``root`` as a POSIX string, else its full form."""

    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _first_url(text: str) -> str | None:
    """Return the first http(s) URL in text, which is how `gh` prints a new PR."""

    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


def _duplicate_pr_url(result: CommandResult) -> str | None:
    """Return the existing PR URL from a duplicate error, or None.

    `gh pr create` on a branch that already has a PR exits non-zero and prints the
    existing PR's URL (Q1). This reads that URL out of the message so the fallback
    can edit the right PR -- without letting the *wording* of the message be the
    signal, which is B152's whole point.
    """

    combined = result.combined_output
    if "already exists" not in combined.lower():
        return None
    return _first_url(combined)


def _verbatim(result: CommandResult) -> str:
    """Return a command's own output, so `gh`'s message reaches the developer intact.

    Both `gh` failures the POC produced named the exact next command to run, and
    anything this tool invented in their place would be worse (B154, C14).
    """

    return result.combined_output.strip() or "no output"
