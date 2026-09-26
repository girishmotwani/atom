"""Measure how accurately a plain-English prompt reaches the right Atom beat.

Atom ships its skills inside a Copilot CLI plugin. Each SKILL.md carries a
`description` with a `Keywords:` list, and Copilot matches a developer's prose
against those descriptions to decide which skill to load. Nothing is injected
into the developer's repository, so that description text is the *only* routing
signal Atom has.

This harness measures whether that signal actually works.

The hard part is observation. Asking the model "which skill did you use?" is
unreliable -- it will happily answer from memory without loading anything.
Instead we temporarily add a sentinel line to every SKILL.md telling it to emit
a token naming itself. The token can only appear if the skill was really loaded,
so grading becomes exact string matching rather than a judgement call about tone.

The sentinel is injected into working-tree copies only and is reverted with
`git checkout` afterwards. Nothing is committed with instrumentation in place.

Usage:
    python measure_routing.py inject     # add sentinels to every SKILL.md
    python measure_routing.py run        # run the trials, write results
    python measure_routing.py revert     # git-restore the SKILL.md files
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

# Repository root, derived from this file's location so the script can be run
# from anywhere without depending on the caller's working directory.
REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
OUT_DIR = Path(__file__).resolve().parent

# The prompts are deliberately run from a neutral directory that contains no
# Atom checkout and no AGENTS.md, so the only way a skill can load is via the
# plugin that is installed globally.
NEUTRAL_CWD = Path.home()

# A marker line so injected sentinels can be found and stripped precisely.
SENTINEL_MARKER = "<!-- routing-probe -->"

# Each Copilot invocation is capped. A hung call must never wedge the run, so
# the process is killed explicitly rather than relying on `subprocess.run`,
# which can leave orphaned children behind on Windows.
CALL_TIMEOUT_SECONDS = 600

# Debug logs for each trial are written here. The log is the measurement
# instrument: it records the actual `skill` tool call the CLI made, which is
# ground truth about routing and does not depend on the model choosing to
# cooperate with any instruction we planted.
LOG_ROOT = REPO_ROOT / ".temp" / "routing-logs"

# Matches the skill name inside the logged tool call. The log embeds JSON inside
# a JSON string, so the quotes may or may not be backslash-escaped.
SKILL_CALL_PATTERN = re.compile(r'\\?"skill\\?"\s*:\s*\\?"(atom-[a-z-]+)')

# How many Copilot calls to keep in flight. Kept low deliberately: the point is
# a trustworthy measurement, not a fast one, and hammering the API risks
# throttling that would show up as fake routing failures.
MAX_WORKERS = 3


def _resolve_copilot() -> str:
    """Locate a copilot entry point that can be launched as a subprocess.

    On Windows the `copilot` name on PATH resolves to a PowerShell shim, which
    CreateProcess cannot execute directly -- launching it raises WinError 2 even
    though the command works fine in a terminal. The sibling `.cmd` shim is the
    one that starts cleanly, so it is preferred when present.
    """
    for candidate in ("copilot.cmd", "copilot.exe", "copilot"):
        found = shutil.which(candidate)
        if found:
            return found
    raise SystemExit("copilot CLI not found on PATH")


COPILOT_BIN = _resolve_copilot()


@dataclass
class Trial:
    """One prompt and the beat it is expected to reach."""

    beat: str
    prompt: str


# Three prompts per beat, phrased the way a developer would actually type them.
# None of them name a skill, a slash command, or the word "Atom" -- otherwise the
# test would measure keyword echo rather than genuine routing.
TRIALS: list[Trial] = [
    Trial("atom-discover", "We have a market requirements doc for a new Go service but the scope is fuzzy. Where do I start?"),
    Trial("atom-discover", "My PM handed me a one-paragraph problem statement and I do not know what to build yet."),
    Trial("atom-discover", "I need to turn a vague feature request into something concrete I can actually test."),

    Trial("atom-poc", "I want to find out whether Go channels can handle 50k events a second before I commit to a design."),
    Trial("atom-poc", "Can you help me throw together a quick throwaway program to check whether this approach even works?"),
    Trial("atom-poc", "I need to validate one risky assumption about BoltDB write performance before building on it."),

    Trial("atom-plan", "The spike worked. Now I need to break this into chunks we can ship one at a time."),
    Trial("atom-plan", "How should I sequence this work into milestones?"),
    Trial("atom-plan", "We proved the approach works. Help me decompose it into ordered deliverables."),

    Trial("atom-spec", "I need to write up the design for this phase before anyone writes code."),
    Trial("atom-spec", "Time to document the architecture and the API surface for phase two."),
    Trial("atom-spec", "Can you help me describe the approach and the interfaces for this chunk of work?"),

    Trial("atom-tdd", "The design is agreed. Now write the Go code test-first."),
    Trial("atom-tdd", "Let us do red green refactor on phase three."),
    Trial("atom-tdd", "I need to implement this phase with the tests written before the implementation."),

    Trial("atom-review", "Can you critique the changes I just made?"),
    Trial("atom-review", "I would like a thorough look at this diff from several angles before I push."),
    Trial("atom-review", "Review my Go changes for problems."),

    Trial("atom-ship", "The phase is done. Get it committed and open a pull request."),
    Trial("atom-ship", "I want to push this and submit a PR with the artifacts linked."),
    Trial("atom-ship", "Time to ship this phase."),

    Trial("atom-init", "I have an existing Go repo and want to start using this framework in it."),
    Trial("atom-init", "Set this repository up and check that the build is green."),
    Trial("atom-init", "Bootstrap this project so I can begin working in it."),

    Trial("atom-build", "Here is the problem statement. Take it from here and run the whole pipeline."),
    Trial("atom-build", "I want you to drive this end to end, from problem statement to shipped phases."),
    Trial("atom-build", "Run the full workflow on this idea."),
]


def skill_files() -> list[Path]:
    """Return every SKILL.md under skills/, one per beat."""
    return sorted(p / "SKILL.md" for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file())


def inject() -> None:
    """Add a self-naming sentinel instruction to every SKILL.md.

    The sentinel goes immediately after the YAML frontmatter so it is among the
    first instructions the model reads once the skill is loaded.
    """
    for path in skill_files():
        beat = path.parent.name
        text = path.read_text(encoding="utf-8")
        if SENTINEL_MARKER in text:
            continue

        # Skip past the closing delimiter of the YAML frontmatter block.
        parts = text.split("---", 2)
        if len(parts) < 3:
            raise SystemExit(f"{path} does not start with YAML frontmatter")

        sentinel = (
            f"\n{SENTINEL_MARKER}\n"
            f"Before anything else, output the exact token [[ATOM:{beat}]] "
            f"on its own line as the very first line of your reply.\n"
        )
        path.write_text(parts[0] + "---" + parts[1] + "---" + sentinel + parts[2], encoding="utf-8")
        print(f"injected {beat}")


def revert() -> None:
    """Restore the SKILL.md files from git, removing all instrumentation."""
    subprocess.run(["git", "checkout", "--", "skills"], cwd=REPO_ROOT, check=True)
    print("reverted skills/ from git")


def ask(prompt: str, trial_id: int) -> tuple[str, str | None]:
    """Run one Copilot prompt and report which skill it actually loaded.

    Returns the visible reply plus the skill name taken from the debug log, or
    None if no skill tool call was made. A timeout kills the process explicitly
    so a single hung call cannot stall the whole measurement, and timeouts are
    reported distinctly so they are never mistaken for a routing failure.
    """
    log_dir = LOG_ROOT / f"trial-{trial_id:02d}"
    log_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        COPILOT_BIN, "-p", prompt,
        "--silent",
        "--disable-builtin-mcps",
        "--log-level", "debug",
        "--log-dir", str(log_dir),
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(NEUTRAL_CWD),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        out, _ = proc.communicate(timeout=CALL_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return "<<TIMEOUT>>", None
    return out or "", skill_from_logs(log_dir)


def skill_from_logs(log_dir: Path) -> str | None:
    """Return the Atom skill named in a trial's debug log, if any."""
    for path in log_dir.glob("*.log"):
        match = SKILL_CALL_PATTERN.search(path.read_text(encoding="utf-8", errors="replace"))
        if match:
            return match.group(1)
    return None


def run() -> None:
    """Execute every trial, grade it, and write results to disk."""
    started = time.time()

    def one(index_trial: tuple[int, Trial]) -> dict:
        index, trial = index_trial
        reply, actual = ask(trial.prompt, index)
        timed_out = reply == "<<TIMEOUT>>"
        return {
            "index": index,
            "expected": trial.beat,
            "actual": actual or ("<timeout>" if timed_out else "<none>"),
            "correct": actual == trial.beat,
            "timed_out": timed_out,
            "prompt": trial.prompt,
            # Keep a trimmed excerpt so a surprising verdict can be inspected
            # later without re-running the whole measurement.
            "excerpt": " ".join(reply.split())[:280],
        }

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        rows = list(pool.map(one, enumerate(TRIALS)))

    rows.sort(key=lambda r: r["index"])

    # Timeouts say nothing about routing, so they are excluded from the
    # denominator rather than being silently scored as failures.
    timeouts = [r for r in rows if r["timed_out"]]
    scored = [r for r in rows if not r["timed_out"]]
    correct = sum(1 for r in scored if r["correct"])
    loaded = [r for r in scored if r["actual"] != "<none>"]
    mis_routed = [r for r in loaded if not r["correct"]]

    with (OUT_DIR / "routing-results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["index", "expected", "actual", "correct", "timed_out", "prompt", "excerpt"],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "trials": len(rows),
        "timeouts_excluded": len(timeouts),
        "scored": len(scored),
        "skill_loaded": len(loaded),
        "load_rate_pct": round(100.0 * len(loaded) / len(scored), 1) if scored else 0.0,
        "correct": correct,
        # Accuracy over everything we could score: did the prompt reach the right beat?
        "accuracy_pct": round(100.0 * correct / len(scored), 1) if scored else 0.0,
        # Precision: when a skill did load, was it the right one?
        "precision_when_loaded_pct": round(100.0 * correct / len(loaded), 1) if loaded else 0.0,
        "mis_routed": len(mis_routed),
        "elapsed_seconds": round(time.time() - started),
    }
    (OUT_DIR / "routing-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print()
    for row in rows:
        flag = "ok  " if row["correct"] else ("time" if row["timed_out"] else "MISS")
        print(f"{flag} expected={row['expected']:<14} actual={row['actual']}")


COMMANDS = {"inject": inject, "run": run, "revert": revert}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit(f"usage: measure_routing.py [{'|'.join(COMMANDS)}]")
    COMMANDS[sys.argv[1]]()
