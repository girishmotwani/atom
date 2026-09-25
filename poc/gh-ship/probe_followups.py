"""Phase 5 follow-up probe: two spike results that look like an API lying.

The main spike produced two answers that must not be written into the report as they
stand, because both are the shape of failure this project keeps getting caught by:

  F1  `gh pr edit --body-file` exited 0 for a 70,000-character body, above the
      65,536 cap that was predicted. Exit 0 means "gh was happy", not "GitHub stored
      it". `gofmt -l` also exits 0 while reporting failures. So the body is read back
      and measured rather than inferred from an exit code.

  F2  `gh pr create` with *inherited* stdin took 44.4 seconds and died with a TCP
      write error, where the same call with *empty* stdin failed cleanly in 8.1. That
      is either the stdin-inheritance stall Phase 4 was bitten by, or an unrelated
      network blip. One observation cannot tell those apart, so the case is repeated.

Usage:
    python poc/gh-ship/probe_followups.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

# Reuse the spike's own helpers so both runs measure things the same way.
import spike  # type: ignore[import-not-found]

PROBE_PATH = Path(__file__).resolve().parent / "followups.json"

# How many times to repeat the inherited-stdin call. Three is enough to tell a
# reproducible behaviour from a one-off network fault, which is all F2 needs.
REPEATS = 3


def measure_stored_body(gh: str) -> dict:
    """Read back the body of the PR the spike edited, and measure what GitHub kept.

    The spike wrote bodies of 30,000, then 65,536, then 70,000 characters, in that
    order, and `gh` reported success each time. If GitHub silently truncated, the
    stored length is the real cap and the exit code was a lie.
    """
    result = spike.run(
        [gh, "pr", "view", "1", "--json", "body"],
        cwd=spike.REPO_ROOT,
    )
    stored_length = None
    if result["exit_code"] == 0:
        try:
            # The spike truncates captured stdout for readability, so the body is
            # re-fetched here through a length filter rather than parsed from it.
            length_result = spike.run(
                [gh, "pr", "view", "1", "--json", "body", "--jq", ".body | length"],
                cwd=spike.REPO_ROOT,
            )
            stored_length = int(length_result["stdout"].strip())
        except (ValueError, KeyError):
            stored_length = None

    return {
        "last_body_written": 70_000,
        "stored_body_length": stored_length,
        "truncated": stored_length is not None and stored_length < 70_000,
        "raw": result,
    }


def repeat_inherited_stdin(gh: str) -> dict:
    """Run the unpushed-branch PR creation repeatedly, with stdin inherited.

    A fresh throwaway branch is needed because the condition being measured is
    "no upstream exists". The branch is never pushed, so cleanup is only local.
    """
    branch = f"spike/gh-stdin-{int(time.time())}"
    worktree = spike.create_worktree(branch)

    attempts = []
    try:
        for index in range(REPEATS):
            result = spike.run(
                [
                    gh, "pr", "create",
                    "--title", "Spike: stdin repeat",
                    "--body", "probe",
                    "--base", "main",
                ],
                cwd=worktree,
                stdin_mode="inherit",
            )
            attempts.append({"attempt": index + 1, **result})
            print(
                f"    attempt {index + 1}: "
                f"{result['duration_seconds']}s exit={result['exit_code']} "
                f"timed_out={result['timed_out']}"
            )
    finally:
        spike.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=spike.REPO_ROOT)
        spike.run(["git", "branch", "-D", branch], cwd=spike.REPO_ROOT)

    return {"branch": branch, "attempts": attempts}


def main() -> int:
    gh = spike.gh_path()
    findings: dict = {}

    print("F1  was the 70,000-character body actually stored?")
    findings["F1_body_storage"] = measure_stored_body(gh)
    stored = findings["F1_body_storage"]["stored_body_length"]
    print(f"    stored length: {stored}")

    print(f"\nF2  repeating the inherited-stdin call {REPEATS} times ...")
    findings["F2_inherited_stdin_repeats"] = repeat_inherited_stdin(gh)

    PROBE_PATH.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(f"\nwrote {PROBE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
