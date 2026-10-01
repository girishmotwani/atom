"""Build a repository knowledge base by sweeping it one area at a time.

This is a POC spike, not production Atom code, but it is the shape the real
Atom feature would take: rather than one shallow pass over a large codebase,
study each area separately and then write up how the areas fit together.

The experiment this feeds depends on one property above all others: the
repository handed to this script must contain NO history after the cut point,
because the repairs the knowledge base will later be tested against all happen
after it.  `assert_history_is_bounded` checks this before any work starts.

Comments are deliberately heavy.  A knowledge base that quietly contained an
answer would make the downstream measurement meaningless, so the reasoning
behind each choice is written down rather than assumed.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "gpt-5.4"
DEFAULT_WORKERS = 6
DEFAULT_TIMEOUT_SECONDS = 900.0

# Write-up length is scaled to the size of the area.  A one-file utility does not
# earn the same three hundred words as a twelve-thousand-line subsystem, and
# padding the small ones would spend the word budget where it buys least.
LARGE_AREA_LINES = 5000
MEDIUM_AREA_LINES = 1000
LARGE_AREA_WORD_TARGET = 400
MEDIUM_AREA_WORD_TARGET = 300
SMALL_AREA_WORD_TARGET = 150
SYNTHESIS_WORD_TARGET = 1200


def word_target_for(area: "Area") -> int:
    """Choose a write-up length proportional to how much code the area holds."""

    if area.lines >= LARGE_AREA_LINES:
        return LARGE_AREA_WORD_TARGET
    if area.lines >= MEDIUM_AREA_LINES:
        return MEDIUM_AREA_WORD_TARGET
    return SMALL_AREA_WORD_TARGET


@dataclass
class Area:
    """One top-level directory of the subtree under study."""

    name: str
    path: str
    source_files: int
    test_files: int
    lines: int


@dataclass
class CallResult:
    """The outcome of a single agent invocation."""

    ok: bool
    text: str
    seconds: float
    detail: str


def git(repo: Path, *args: str, timeout: float = 600.0) -> str:
    """Run a git command in the repository and return its stdout."""

    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{completed.stderr[-2000:]}")
    return completed.stdout


def assert_history_is_bounded(repo: Path, cut_date: str) -> None:
    """Refuse to run if the repository contains commits after the cut point.

    This is the control that makes the downstream measurement trustworthy, so
    it is checked here as well as when the repository is built.  A knowledge
    base built over history that includes the tested repairs would score well
    and mean nothing.
    """

    latest = git(repo, "log", "--all", "--pretty=format:%cI", "-1").strip()
    # Compare calendar dates only.  The recorded value is a full timestamp, so a
    # plain string comparison against a bare cut date would treat any commit on
    # the cut day itself as being after it.
    if latest[:10] > cut_date[:10]:
        raise SystemExit(
            f"Repository contains history at {latest}, after the cut point {cut_date}.\n"
            "Rebuild it with only pre-cut objects before building a knowledge base."
        )
    print(f"history check: latest commit anywhere is {latest}, at or before the cut {cut_date}")


def discover_areas(repo: Path, subtree: str, minimum_files: int) -> list[Area]:
    """List the top-level areas of the subtree, largest first.

    Areas below `minimum_files` are skipped rather than each consuming a study
    pass; a directory with one file rarely earns three hundred words.
    """

    listing = git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", subtree).splitlines()
    depth = len(subtree.rstrip("/").split("/"))

    grouped: dict[str, list[str]] = {}
    for path in listing:
        if not path.endswith(".go"):
            continue
        parts = path.split("/")
        name = parts[depth] if len(parts) > depth + 1 else "_root"
        grouped.setdefault(name, []).append(path)

    areas: list[Area] = []
    for name, files in grouped.items():
        sources = [f for f in files if not f.endswith("_test.go")]
        if len(sources) < minimum_files:
            continue
        lines = 0
        for path in sources:
            lines += git(repo, "show", f"HEAD:{path}", timeout=120).count("\n")
        areas.append(
            Area(
                name=name,
                path=subtree if name == "_root" else f"{subtree.rstrip('/')}/{name}",
                source_files=len(sources),
                test_files=len(files) - len(sources),
                lines=lines,
            )
        )

    areas.sort(key=lambda area: -area.lines)
    return areas


def copilot_command(model: str) -> list[str]:
    """Build the agent command, resolving npm shims to a real executable."""

    command = ["copilot", "--silent", "--model", model,
               "--no-custom-instructions", "--disable-builtin-mcps"]
    resolved = shutil.which(command[0])
    if resolved is not None:
        command[0] = resolved
    return command


def call_agent(model: str, prompt: str, cwd: Path, timeout_seconds: float) -> CallResult:
    """Invoke the agent once with the prompt on stdin."""

    started = time.perf_counter()
    try:
        process = subprocess.Popen(
            copilot_command(model),
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        return CallResult(False, "", 0.0, f"could not start the agent: {error}")

    try:
        out, err = process.communicate(prompt, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        # A timed-out call often leaves a partial answer behind.  It is returned
        # but marked failed, so a truncated write-up is never mistaken for a
        # complete one and frozen into the knowledge base.
        process.kill()
        out, err = process.communicate()
        return CallResult(False, out or "", time.perf_counter() - started,
                          f"timed out after {timeout_seconds:.0f}s")

    seconds = time.perf_counter() - started
    if process.returncode != 0:
        return CallResult(False, out or "", seconds,
                          f"agent exited {process.returncode}: {(err or '')[-400:]}")
    return CallResult(True, out or "", seconds, "ok")


def build_area_prompt(area: Area, word_target: int) -> str:
    """Ask the agent to study one area and describe it.

    The write-up must describe structure and responsibility, not list files.
    Downstream its job is to tell a repairing agent which areas are involved so
    that the agent's own search lands in the right place; handing over file
    lists would replace the very work being measured.
    """

    return f"""You are studying one area of a Go codebase so that another engineer,
who has never seen this code, can understand what it does and how it relates to the
rest of the system.

The area is: {area.path}
It contains roughly {area.source_files} source files, {area.test_files} test files,
and about {area.lines} lines of Go.

Read the code in that directory. You may also use git history in this repository to
understand how the area came to look the way it does -- `git log`, `git show` and
`git log -p` on files in that directory are all available and useful.

Write approximately {word_target} words covering:

1. **Purpose** -- what this area is responsible for, in plain language. One
   responsibility, stated plainly. If it genuinely has several, say so.
2. **Main types and interfaces** -- the handful of types that matter most, and what
   each one is for. Name them; do not paste their definitions.
3. **What it talks to** -- which other areas of the system it depends on, and which
   ones depend on it. Be specific about the direction of each relationship.
4. **How it changes** -- based on the history, what kinds of change land here, and
   what tends to have to change alongside them. This is the most valuable section,
   so favour it if you run short of room.

Rules:
- **Do not list files.** Describe structure and responsibility. Naming a type or a
  function is fine; enumerating file paths is not.
- Write what the code actually does, not what its names suggest it does.
- If something is unclear or looks inconsistent, say so plainly rather than papering
  over it. An honest gap is more useful than a confident guess.
- Prose and short headings. No code blocks.

Output only the write-up itself, starting with a `## {area.name}` heading.
"""


def build_synthesis_prompt(area_notes: str, word_target: int) -> str:
    """Ask the agent to describe how the separately studied areas fit together."""

    return f"""Below are write-ups of the individual areas of a Go system, each studied
separately. Your job is to write the part none of them could: how the system fits
together as a whole.

Write approximately {word_target} words covering:

1. **What the system does** -- its purpose, in plain language, for someone who has
   never seen it.
2. **The shape of it** -- how the areas group into layers or responsibilities, and
   what the main paths through the system are.
3. **How the areas interact** -- which areas talk to which, in which direction, and
   across which interfaces. This is the most important section.
4. **What tends to change together** -- where a change in one area usually forces a
   change in another, and why. Be concrete about the coupling.

Rules:
- Do not list files.
- Do not simply summarise each area again; the write-ups below already do that.
  Describe the relationships between them.
- Where the write-ups disagree or leave a gap, say so rather than inventing a bridge
  between them.

Output only the write-up, starting with a `# System overview` heading.

---

{area_notes}
"""


def study_areas(areas: list[Area], repo: Path, out_dir: Path, model: str,
                workers: int, timeout_seconds: float) -> None:
    """Run one study pass per area, in parallel, skipping any already written."""

    out_dir.mkdir(parents=True, exist_ok=True)
    pending = [area for area in areas if not (out_dir / f"{area.name}.md").exists()]
    print(f"{len(areas)} areas, {len(areas) - len(pending)} already written, {len(pending)} to study")

    lock = threading.Lock()
    done = 0

    def study(area: Area) -> None:
        nonlocal done
        result = call_agent(model, build_area_prompt(area, word_target_for(area)), repo, timeout_seconds)
        with lock:
            done += 1
            status = "ok" if result.ok else f"FAILED ({result.detail})"
            print(f"  [{done}/{len(pending)}] {area.name:<26} {result.seconds:6.0f}s "
                  f"{len(result.text.split()):5d} words  {status}", flush=True)
        # Only a successful call is persisted.  A partial write-up left on disk
        # would be silently reused on the next run and quietly degrade the
        # knowledge base.
        if result.ok and result.text.strip():
            (out_dir / f"{area.name}.md").write_text(result.text.strip() + "\n", encoding="utf-8")

    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(study, pending))


def normalise_area_writeup(name: str, text: str) -> str:
    """Strip the model's preamble and guarantee the area has its own heading.

    Two defects show up often enough to be worth correcting here rather than
    hoping a prompt tweak fixes them.  Some write-ups open by narrating the work
    ("I'm reading the package and its history..."), which is noise.  Others omit
    a heading entirely, which is worse than untidy: without one the section is
    silently absorbed into whichever area preceded it, so a reader -- or an
    agent -- attributes its contents to the wrong part of the system.
    """

    narration = re.compile(
        r"^(I['\u2019]m|I will|I['\u2019]ll|Let me|Now I|First,? I|Reading|Looking at)\b",
        re.IGNORECASE,
    )

    lines = text.splitlines()
    # Drop leading blank or narrating lines, but stop at the first real content
    # so we never eat the body of a write-up that simply starts with a sentence.
    start = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            start = index + 1
            continue
        if narration.match(stripped):
            start = index + 1
            continue
        break
    lines = lines[start:]

    body = "\n".join(lines).strip()
    first = next((line.strip() for line in lines if line.strip()), "")
    if not first.startswith("#"):
        body = f"## {name}\n\n{body}"
    elif not first.startswith("## "):
        # Demote or promote a stray heading level so every area sits at the same
        # depth, otherwise the document's structure implies a hierarchy that the
        # areas do not actually have.
        body = re.sub(r"^#+\s*", "## ", body, count=1)

    return body


def assemble(areas: list[Area], out_dir: Path, repo: Path, cut_date: str, model: str,
             timeout_seconds: float, knowledge_base_path: Path) -> None:
    """Combine the area write-ups with a synthesis pass into one document."""

    written = [(area, out_dir / f"{area.name}.md") for area in areas]
    missing = [area.name for area, path in written if not path.exists()]
    if missing:
        raise SystemExit(
            f"Cannot assemble: {len(missing)} areas have no write-up: {', '.join(missing)}.\n"
            "Re-run to retry just those areas."
        )

    notes = "\n\n".join(
        normalise_area_writeup(area.name, path.read_text(encoding="utf-8"))
        for area, path in written
    )

    synthesis_path = out_dir / "_synthesis.md"
    if synthesis_path.exists():
        print("synthesis already written, reusing it")
        synthesis = synthesis_path.read_text(encoding="utf-8").strip()
    else:
        print("running synthesis pass...")
        result = call_agent(model, build_synthesis_prompt(notes, SYNTHESIS_WORD_TARGET),
                            repo, timeout_seconds)
        if not result.ok or not result.text.strip():
            raise SystemExit(f"Synthesis pass failed: {result.detail}")
        synthesis = result.text.strip()
        synthesis_path.write_text(synthesis + "\n", encoding="utf-8")
        print(f"synthesis written in {result.seconds:.0f}s, {len(synthesis.split())} words")

    header = (
        "# Repository knowledge base\n\n"
        f"Built from the repository as it stood at {cut_date}. It describes what the\n"
        "system does, what its areas are responsible for, how they interact, and what\n"
        "tends to change alongside what.\n\n"
        "It describes areas rather than files. A handful of central files are named\n"
        "in passing where the description would be unclear without them, but it is\n"
        "not a file listing and does not enumerate the contents of any area.\n\n---\n\n"
    )
    document = header + synthesis + "\n\n---\n\n" + notes + "\n"
    knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
    knowledge_base_path.write_text(document, encoding="utf-8")

    words = len(document.split())
    print(f"\nknowledge base written: {knowledge_base_path}")
    print(f"  {len(written)} areas plus synthesis, {words} words")
    if words > 14000:
        print("  WARNING: well above the ~10,000 word ceiling; consider trimming before use")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a repository knowledge base.")
    parser.add_argument("--repo", required=True, type=Path,
                        help="repository containing history only up to the cut point")
    parser.add_argument("--subtree", required=True,
                        help="subtree to study, for example src/example")
    parser.add_argument("--cut-date", required=True,
                        help="ISO date the repository is bounded at, for example 2025-05-30")
    parser.add_argument("--out", required=True, type=Path,
                        help="directory for the per-area write-ups")
    parser.add_argument("--knowledge-base", required=True, type=Path,
                        help="path to write the assembled knowledge base")
    parser.add_argument("--minimum-files", type=int, default=1,
                        help="skip areas with fewer source files than this")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--list-only", action="store_true",
                        help="list the areas that would be studied, then stop")
    args = parser.parse_args()

    assert_history_is_bounded(args.repo, args.cut_date)

    areas = discover_areas(args.repo, args.subtree, args.minimum_files)
    projected = sum(word_target_for(area) for area in areas) + SYNTHESIS_WORD_TARGET
    print(f"\n{len(areas)} areas to study, {sum(a.lines for a in areas)} lines of source between them")
    print(f"projected knowledge base size: about {projected} words\n")
    for area in areas:
        print(f"  {area.name:<26} {area.source_files:4d} source  {area.test_files:4d} test  "
              f"{area.lines:7d} lines  -> {word_target_for(area):3d} words")
    if args.list_only:
        return

    print()
    study_areas(areas, args.repo, args.out, args.model, args.workers, args.timeout_seconds)
    assemble(areas, args.out, args.repo, args.cut_date, args.model,
             args.timeout_seconds, args.knowledge_base)


if __name__ == "__main__":
    main()
