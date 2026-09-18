"""Phase 5 spike: what does `gh` actually do when `atom ship` drives it?

`atom ship` will assemble a pull request out of the artifacts a phase has already
produced and hand it to the GitHub CLI. The phase plan called that "shelling out to
git and gh" and rated the risk low. That is the same sentence shape that described
Phase 3 as "ordinary JSON persistence", which turned out to lose 1545 of 1600 log
entries. So the claim gets measured rather than believed.

Five questions, recorded with predictions in
`specs/atom-cli/phase-05-ship/poc-brief.md` before this ran:

  Q1  What happens when a PR already exists for the branch? Re-running `atom ship`
      is the normal case, not the edge case.
  Q2a How large an argument will the operating system let `gh` receive? Phase 4
      measured a Windows argv wall; this checks whether `gh` meets the same one.
  Q2b How large a body will GitHub itself accept via `--body-file`?
  Q3  What does `gh` say when it is not authenticated?
  Q4  Does `gh pr create` hang when there is no terminal and no upstream branch?
  Q5  Does `gh pr create` push the branch by itself?

Q4 and Q5 carry the weight. Q4 repeats the exact failure shape that cost Phase 4 a
debugging session -- a child process inheriting stdin and never seeing EOF. Q5 would
put `gh` in direct conflict with this phase's acceptance criterion, which says the
tool never pushes without an explicit instruction.

Safety. Every git operation happens in a throwaway *worktree* beside the repository,
never in the developer's checkout, so a crash cannot leave their tree dirty or on the
wrong branch. Every PR opened here is closed again and both branches are deleted. The
cleanup runs in a `finally` block so it happens even when a question fails outright.

Usage:
    python poc/gh-ship/spike.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# The repository this spike operates on. Resolved from the spike's own location so
# the script does not care where it is invoked from.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Worktrees live *beside* the repository, never inside it: a worktree inside the repo
# pollutes the tree that `atom check` and `git status` report on.
WORKTREE_PARENT = REPO_ROOT.parent / f"{REPO_ROOT.name}.worktrees"

RESULTS_PATH = Path(__file__).resolve().parent / "results.json"

# Long enough that a slow network call still completes, short enough that a genuine
# hang is caught rather than waited out. Phase 4's hang showed up at 60s; a prompt
# waiting on a terminal will never return, so any value here works to detect it.
TIMEOUT_SECONDS = 45


# ---------------------------------------------------------------------------
# Process invocation
# ---------------------------------------------------------------------------


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    stdin_mode: str = "empty",
    timeout: int = TIMEOUT_SECONDS,
    env: dict[str, str] | None = None,
) -> dict:
    """Run a command and record everything that might matter, including a hang.

    `stdin_mode` is the interesting parameter. Phase 4 discovered that a tool which
    reads stdin will block forever when it inherits a pipe that never reaches EOF.
    Passing "inherit" reproduces that condition deliberately so the difference between
    the two modes is visible rather than assumed.
    """
    started = time.monotonic()
    common = {
        "cwd": str(cwd) if cwd else None,
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
        "env": env,
    }

    try:
        if stdin_mode == "empty":
            completed = subprocess.run(args, input="", **common)
        else:
            # Inherit whatever stdin this process has. This is the unsafe mode, and
            # the whole point of measuring it.
            completed = subprocess.run(args, stdin=None, **common)
    except subprocess.TimeoutExpired:
        return {
            "argv_bytes": sum(len(a) for a in args),
            "timed_out": True,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "duration_seconds": round(time.monotonic() - started, 2),
        }
    except OSError as error:
        # The operating system refused to start the process at all. Phase 4 found
        # several distinct ways this happens on Windows, so the error is recorded
        # verbatim rather than summarised.
        return {
            "argv_bytes": sum(len(a) for a in args),
            "timed_out": False,
            "exit_code": None,
            "os_error": f"{type(error).__name__}: {error}",
            "stdout": "",
            "stderr": "",
            "duration_seconds": round(time.monotonic() - started, 2),
        }

    return {
        "argv_bytes": sum(len(a) for a in args),
        "timed_out": False,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip()[:2000],
        "stderr": completed.stderr.strip()[:2000],
        "duration_seconds": round(time.monotonic() - started, 2),
    }


def gh_path() -> str:
    """Locate `gh`, failing loudly rather than letting a later call fail obscurely.

    Phase 4 learned that `shutil.which` can resolve something `subprocess.run` cannot
    launch, so resolving here and reporting the path lets the report state exactly
    which binary produced the numbers.
    """
    found = shutil.which("gh")
    if not found:
        raise SystemExit("gh is not on PATH; this spike cannot answer anything without it")
    return found


# ---------------------------------------------------------------------------
# Worktree lifecycle
# ---------------------------------------------------------------------------


def create_worktree(branch: str) -> Path:
    """Create a throwaway branch in its own worktree, with one real commit on it.

    A PR needs a diff, so the commit has to change something. It changes a scratch
    file that exists only on this branch.
    """
    WORKTREE_PARENT.mkdir(parents=True, exist_ok=True)
    worktree = WORKTREE_PARENT / branch.replace("/", "-")

    result = run(
        ["git", "worktree", "add", "-b", branch, str(worktree), "main"],
        cwd=REPO_ROOT,
    )
    if result["exit_code"] != 0:
        raise SystemExit(f"could not create worktree: {result['stderr']}")

    scratch = worktree / "poc" / "gh-ship" / "scratch.txt"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    scratch.write_text(
        "Throwaway file created by the Phase 5 gh spike.\n"
        "If you are reading this on main, the spike's cleanup failed.\n",
        encoding="utf-8",
    )

    run(["git", "add", "-A"], cwd=worktree)
    run(
        ["git", "commit", "-m", "[Spike] Throwaway commit for the Phase 5 gh spike"],
        cwd=worktree,
    )
    return worktree


def remote_branch_exists(branch: str) -> bool:
    """Ask the remote directly whether the branch is there.

    This is how Q5 is answered: check before `gh pr create`, check again after, and
    see whether the branch appeared without anyone pushing it.
    """
    result = run(["git", "ls-remote", "--heads", "origin", branch], cwd=REPO_ROOT)
    return bool(result["stdout"].strip())


def cleanup(branch: str, worktree: Path | None, gh: str) -> list[dict]:
    """Undo everything the spike did, reporting each step rather than failing silently.

    Runs from a `finally` block, so it must tolerate a half-finished spike: any of
    these objects may or may not exist by the time it is called.
    """
    steps: list[dict] = []

    # Close any PR opened against the throwaway branch.
    listing = run(
        [gh, "pr", "list", "--head", branch, "--state", "all", "--json", "number"],
        cwd=REPO_ROOT,
    )
    try:
        for pull_request in json.loads(listing["stdout"] or "[]"):
            number = str(pull_request["number"])
            closed = run([gh, "pr", "close", number], cwd=REPO_ROOT)
            steps.append({"step": f"close PR #{number}", "exit_code": closed["exit_code"]})
    except json.JSONDecodeError:
        steps.append({"step": "list PRs", "error": listing["stdout"][:200]})

    if worktree and worktree.exists():
        removed = run(["git", "worktree", "remove", "--force", str(worktree)], cwd=REPO_ROOT)
        steps.append({"step": "remove worktree", "exit_code": removed["exit_code"]})

    deleted_remote = run(["git", "push", "origin", "--delete", branch], cwd=REPO_ROOT)
    steps.append({"step": "delete remote branch", "exit_code": deleted_remote["exit_code"]})

    deleted_local = run(["git", "branch", "-D", branch], cwd=REPO_ROOT)
    steps.append({"step": "delete local branch", "exit_code": deleted_local["exit_code"]})

    return steps


# ---------------------------------------------------------------------------
# The questions
# ---------------------------------------------------------------------------


def question_4_and_5(gh: str, branch: str, worktree: Path) -> dict:
    """Does `gh pr create` hang without a terminal, and does it push by itself?

    These two share a run because they share a setup: a branch that exists locally and
    not on the remote. The first call uses inherited stdin, which is the condition
    that hung Phase 4's probe. If it hangs, the second call -- with empty stdin --
    shows whether that alone is the fix.
    """
    before = remote_branch_exists(branch)

    inherited = run(
        [gh, "pr", "create", "--title", "Spike: does gh hang", "--body", "probe", "--base", "main"],
        cwd=worktree,
        stdin_mode="inherit",
    )
    pushed_after_inherited = remote_branch_exists(branch)

    empty = run(
        [gh, "pr", "create", "--title", "Spike: does gh hang", "--body", "probe", "--base", "main"],
        cwd=worktree,
        stdin_mode="empty",
    )
    pushed_after_empty = remote_branch_exists(branch)

    return {
        "remote_branch_existed_before": before,
        "with_inherited_stdin": inherited,
        "remote_branch_after_inherited": pushed_after_inherited,
        "with_empty_stdin": empty,
        "remote_branch_after_empty": pushed_after_empty,
    }


def question_1(gh: str, branch: str, worktree: Path) -> dict:
    """What does `gh pr create` do when a PR already exists for this branch?

    The branch is pushed explicitly first, so this measures duplicate-creation alone
    rather than tangling it up with the push behaviour Q5 is about.
    """
    push = run(["git", "push", "-u", "origin", branch], cwd=worktree)

    first = run(
        [
            gh, "pr", "create",
            "--title", "Spike: first PR",
            "--body", "Created by the Phase 5 spike. It will be closed automatically.",
            "--base", "main",
        ],
        cwd=worktree,
    )
    second = run(
        [
            gh, "pr", "create",
            "--title", "Spike: duplicate PR",
            "--body", "Second attempt on the same branch.",
            "--base", "main",
        ],
        cwd=worktree,
    )

    return {"explicit_push": push, "first_create": first, "duplicate_create": second}


def question_2a(gh: str) -> list[dict]:
    """How large an argument will the operating system let `gh` receive?

    A read-only search is used as the carrier: the point is whether the process starts
    at all, which is decided before `gh` sees anything. Distinguishing an OS refusal
    from a `gh` complaint is done by reading the message, which is why the message is
    kept verbatim.
    """
    measurements = []
    for size in (1_000, 4_000, 8_000, 16_000, 32_000, 64_000):
        padding = "x" * size
        result = run([gh, "pr", "list", "--limit", "1", "--search", padding], cwd=REPO_ROOT)
        measurements.append({"requested_bytes": size, **result})
    return measurements


def question_2b(gh: str, branch: str, worktree: Path) -> list[dict]:
    """How large a body will GitHub accept, once argv is out of the picture?

    `--body-file` reads from disk, so whatever limit shows up here belongs to GitHub
    rather than to Windows. 65,536 is tested explicitly because it is the documented
    cap; the values around it show whether the boundary is inclusive.
    """
    measurements = []
    body_file = worktree / "body.txt"

    for size in (30_000, 65_536, 70_000):
        # A body of repeated text rather than one long line, so a rejection is about
        # length rather than about some unrelated formatting rule.
        line = "This line pads the pull request body to a measured size.\n"
        body = (line * (size // len(line) + 1))[:size]
        body_file.write_text(body, encoding="utf-8")

        result = run(
            [gh, "pr", "edit", "--body-file", str(body_file)],
            cwd=worktree,
        )
        measurements.append({"body_bytes": size, **result})

    body_file.unlink(missing_ok=True)
    return measurements


def question_3(gh: str) -> dict:
    """What does `gh` say when it has no credentials at all?

    Both token variables are cleared and the config directory is pointed somewhere
    empty, because either one alone would leave a way for `gh` to stay authenticated
    and quietly answer the wrong question.
    """
    env = dict(os.environ)
    env.pop("GH_TOKEN", None)
    env.pop("GITHUB_TOKEN", None)
    env["GH_CONFIG_DIR"] = str(Path(os.environ["TEMP"]) / "atom-spike-empty-gh-config")

    return run([gh, "pr", "list", "--limit", "1"], cwd=REPO_ROOT, env=env)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def main() -> int:
    gh = gh_path()
    branch = f"spike/gh-ship-{int(time.time())}"
    worktree: Path | None = None
    results: dict = {"gh_path": gh, "branch": branch, "questions": {}}

    print(f"gh:      {gh}")
    print(f"branch:  {branch}")
    print()

    try:
        # Q3 and Q2a need no branch, so they run first and cannot be lost to a
        # failure in the more invasive questions.
        print("Q3  unauthenticated ...")
        results["questions"]["Q3_unauthenticated"] = question_3(gh)

        print("Q2a argv size wall ...")
        results["questions"]["Q2a_argv_wall"] = question_2a(gh)

        worktree = create_worktree(branch)
        print(f"worktree: {worktree}")

        print("Q4/Q5 hang and implicit push ...")
        results["questions"]["Q4_Q5_hang_and_push"] = question_4_and_5(gh, branch, worktree)

        print("Q1  duplicate PR ...")
        results["questions"]["Q1_duplicate_pr"] = question_1(gh, branch, worktree)

        print("Q2b GitHub body cap ...")
        results["questions"]["Q2b_body_cap"] = question_2b(gh, branch, worktree)

    finally:
        print("cleanup ...")
        results["cleanup"] = cleanup(branch, worktree, gh)
        RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nwrote {RESULTS_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
