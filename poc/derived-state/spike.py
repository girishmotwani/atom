"""Spike for Phase 6 -- can phase state be DERIVED from the repo instead of declared?

This is throwaway code. It exists to answer the five questions recorded in
specs/atom-cli/phase-06-state/poc-brief.md BEFORE any design is written.

It is read-only against the real repository: anything it mutates is first
copied into a temp directory, and the clone it measures is a temp clone.

Run:  python poc/derived-state/spike.py
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPECS = REPO / "specs" / "atom-cli"

# The artifact set agreed with the developer during the discussion gate.
# poc-report.md is required even when the POC was justifiably skipped --
# the skip must be STATED, never inferred from an absent file.
REQUIRED_ARTIFACTS = (
    "poc-brief.md",
    "poc-report.md",
    "design-spec.md",
    "test-spec.md",
    "tdd-log.md",
    "findings.md",
    "decisions.md",
)

# Directories that look like a phase. Deliberately anchored so that a stray
# folder in specs/ cannot masquerade as one.
PHASE_DIR = re.compile(r"^phase-(\d{2})-([a-z0-9-]+)$")


# ---------------------------------------------------------------------------
# Candidate rules. Each answers "is this artifact DONE?" from the file alone.
# The point of the spike is to find out which of them can be fooled.
# ---------------------------------------------------------------------------

def rule_exists(path: Path) -> bool:
    """R1 -- the weakest rule: the file is on disk."""
    return path.is_file()


def rule_non_empty(path: Path) -> bool:
    """R2 -- on disk and has any content at all."""
    return path.is_file() and path.stat().st_size > 0


def rule_min_size(path: Path, floor: int = 1024) -> bool:
    """R3 -- on disk and larger than an arbitrary floor.

    Included precisely because it is arbitrary. If it grades as well as the
    structural rules, that is evidence the structural rules are not earning
    their complexity.
    """
    return path.is_file() and path.stat().st_size >= floor


def rule_has_sections(path: Path, minimum: int = 3) -> bool:
    """R4 -- carries at least `minimum` level-2 markdown headings."""
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^## ", text, re.MULTILINE)) >= minimum


def rule_no_placeholders(path: Path) -> bool:
    """R5 -- structural, and free of the markers a half-written doc carries."""
    if not rule_has_sections(path):
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return not re.search(r"\bTODO\b|\bTBD\b|\bFIXME\b|<placeholder>", text)


RULES = {
    "R1 exists": rule_exists,
    "R2 non-empty": rule_non_empty,
    "R3 >=1KB": rule_min_size,
    "R4 >=3 sections": rule_has_sections,
    "R5 sect+no TODO": rule_no_placeholders,
}


@dataclass
class PhaseReading:
    """What one rule concluded about one phase directory."""

    name: str
    present: list = field(default_factory=list)
    missing: list = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.missing


def read_phase(directory: Path, rule) -> PhaseReading:
    reading = PhaseReading(name=directory.name)
    for artifact in REQUIRED_ARTIFACTS:
        if rule(directory / artifact):
            reading.present.append(artifact)
        else:
            reading.missing.append(artifact)
    return reading


def phase_directories(specs_root: Path) -> list:
    return sorted(
        (p for p in specs_root.iterdir() if p.is_dir() and PHASE_DIR.match(p.name)),
        key=lambda p: p.name,
    )


def banner(text: str) -> None:
    print()
    print("=" * 74)
    print(text)
    print("=" * 74)


# ---------------------------------------------------------------------------
# Q1 -- grade every rule against the five phases whose answers are known.
# ---------------------------------------------------------------------------

def q1_grade_rules() -> dict:
    banner("Q1 -- how many phases derive as complete, per rule")
    dirs = phase_directories(SPECS)
    print(f"phase directories found: {[d.name for d in dirs]}")
    print()

    results = {}
    for rule_name, rule in RULES.items():
        readings = [read_phase(d, rule) for d in dirs]
        complete = [r.name for r in readings if r.complete]
        results[rule_name] = {
            "complete": complete,
            "detail": {r.name: r.missing for r in readings},
        }
        print(f"{rule_name:18s} complete {len(complete)}/{len(dirs)}")
        for reading in readings:
            if reading.missing:
                print(f"{'':20s}{reading.name}: missing {', '.join(reading.missing)}")
        print()
    return results


# ---------------------------------------------------------------------------
# Q2 -- THE decisive question. Can a half-written spec be told from a finished
# one? A real, finished design-spec.md is copied and then damaged in several
# realistic ways, and every rule is asked about each variant.
# ---------------------------------------------------------------------------

def q2_truncation(workdir: Path) -> dict:
    banner("Q2 -- is a half-written design-spec distinguishable from a finished one?")

    source = SPECS / "phase-04-review" / "design-spec.md"
    if not source.is_file():
        print(f"SKIP: no source spec at {source}")
        return {}

    original = source.read_text(encoding="utf-8")
    print(f"source: {source.relative_to(REPO)}  ({len(original)} chars)")

    headings = [m.start() for m in re.finditer(r"^## ", original, re.MULTILINE)]
    print(f"level-2 headings in source: {len(headings)}")

    variants = {"V0 untouched (control)": original}

    if len(headings) >= 5:
        # The most realistic half-written spec: the author got four sections in
        # and stopped. Nothing about it looks broken.
        variants["V1 first 4 sections"] = original[: headings[4]]
    if len(headings) >= 2:
        variants["V2 first 1 section"] = original[: headings[1]]
    if headings:
        # An outline: every heading kept, all prose removed. This is what an
        # agent produces when it scaffolds a document and then stops.
        outline = [
            line for line in original.splitlines()
            if line.startswith("#") or line.startswith("---")
        ]
        variants["V3 headings only"] = "\n".join(outline) + "\n"
    variants["V4 heading + TODO"] = "# Design Spec\n\n## Purpose\n\nTODO\n"

    scratch = workdir / "q2"
    scratch.mkdir(parents=True, exist_ok=True)

    table = {}
    for label, content in variants.items():
        target = scratch / (re.sub(r"[^a-z0-9]+", "_", label.lower()) + ".md")
        target.write_text(content, encoding="utf-8")
        table[label] = {name: rule(target) for name, rule in RULES.items()}

    width = max(len(v) for v in variants)
    print()
    print(" " * (width + 2) + "".join(f"{n:18s}" for n in RULES))
    for label in variants:
        cells = "".join(f"{('PASS' if table[label][n] else 'fail'):18s}" for n in RULES)
        print(f"{label:<{width}}  {cells} ({len(variants[label])} chars)")

    print()
    control = table["V0 untouched (control)"]
    verdicts = {}
    for name in RULES:
        if not control[name]:
            print(f"  !! {name} rejects the CONTROL -- rule is unusable")
            verdicts[name] = "rejects control"
            continue
        fooled = [
            lbl for lbl in variants
            if lbl != "V0 untouched (control)" and table[lbl][name]
        ]
        verdicts[name] = fooled
        if fooled:
            print(f"  {name}: FOOLED by {len(fooled)} damaged variant(s): {fooled}")
        else:
            print(f"  {name}: rejects every damaged variant")

    return {"table": table, "verdicts": verdicts}


# ---------------------------------------------------------------------------
# Q3 -- does mtime ordering survive a fresh clone? Unit tests would never catch
# this, because fixtures are always written in the order the test intends.
# ---------------------------------------------------------------------------

def q3_mtime_vs_lexical(workdir: Path) -> dict:
    banner("Q3 -- does 'newest phase directory' derive stably from mtime?")

    here = phase_directories(SPECS)
    lexical_here = [d.name for d in here]
    mtime_here = [d.name for d in sorted(here, key=lambda p: p.stat().st_mtime)]
    print(f"working tree  lexical: {lexical_here}")
    print(f"working tree  mtime  : {mtime_here}")
    print(f"working tree  agree  : {lexical_here == mtime_here}")

    clone_dir = workdir / "clone"
    print(f"\ncloning into {clone_dir} ...")
    completed = subprocess.run(
        ["git", "clone", "--quiet", str(REPO), str(clone_dir)],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )
    if completed.returncode != 0:
        print(f"clone failed ({completed.returncode}): {completed.stderr.strip()}")
        return {"clone": "failed", "stderr": completed.stderr.strip()}

    clone_specs = clone_dir / "specs" / "atom-cli"
    if not clone_specs.is_dir():
        print(f"clone has no {clone_specs}")
        return {"clone": "no specs"}

    clone_dirs = phase_directories(clone_specs)
    lexical_clone = [d.name for d in clone_dirs]
    mtime_clone = [d.name for d in sorted(clone_dirs, key=lambda p: p.stat().st_mtime)]
    stamps = {d.name: d.stat().st_mtime for d in clone_dirs}

    print(f"fresh clone   lexical: {lexical_clone}")
    print(f"fresh clone   mtime  : {mtime_clone}")
    print(f"fresh clone   agree  : {lexical_clone == mtime_clone}")

    distinct = len({round(v, 3) for v in stamps.values()})
    print(f"fresh clone   distinct mtimes (ms): {distinct} of {len(stamps)}")
    print()
    if lexical_clone != mtime_clone:
        print("  mtime ordering CHANGED across a clone -- mtime is unusable")
    elif distinct < len(stamps):
        print("  mtime ordering held, but mtimes are NOT distinct --")
        print("  the ordering is a sort-stability accident, not a measurement")
    else:
        print("  mtime ordering held on this clone (one observation, not a property)")

    return {
        "lexical_here": lexical_here,
        "mtime_here": mtime_here,
        "lexical_clone": lexical_clone,
        "mtime_clone": mtime_clone,
        "distinct_mtimes": distinct,
        "total": len(stamps),
        "clone_stamps": stamps,
    }


# ---------------------------------------------------------------------------
# Q4 -- do the five real specs share enough structure for a section rule?
# ---------------------------------------------------------------------------

def q4_structure() -> dict:
    banner("Q4 -- do the real design-specs share a usable structure?")
    out = {}
    for directory in phase_directories(SPECS):
        spec = directory / "design-spec.md"
        if not spec.is_file():
            print(f"{directory.name:20s} NO design-spec.md")
            out[directory.name] = None
            continue
        text = spec.read_text(encoding="utf-8", errors="replace")
        sections = re.findall(r"^## (.+)$", text, re.MULTILINE)
        out[directory.name] = sections
        print(f"{directory.name:20s} {len(sections):2d} sections, {len(text):6d} chars")
        print(f"{'':20s} {sections[:5]}")

    seen = [set(s) for s in out.values() if s]
    if seen:
        common = set.intersection(*seen)
        print(f"\nsections common to ALL specs: {sorted(common) or 'NONE'}")
        out["_common"] = sorted(common)
    return out


# ---------------------------------------------------------------------------
# Q5 -- branch name first, newest directory as fallback.
# ---------------------------------------------------------------------------

def current_branch(cwd: Path):
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def resolve_phase(branch, specs_root: Path):
    """The agreed rule: branch name first, newest phase directory as fallback."""
    dirs = phase_directories(specs_root)
    names = {d.name for d in dirs}

    if branch and PHASE_DIR.match(branch):
        if branch in names:
            return branch, "branch name (directory exists)"
        return branch, "branch name (NO matching directory)"

    if dirs:
        return dirs[-1].name, "fallback: newest phase directory (lexical)"
    return None, "nothing to resolve"


def q5_resolution() -> dict:
    banner("Q5 -- does the branch-name rule resolve, and what is the fallback?")
    branch = current_branch(REPO)
    print(f"actual current branch: {branch!r}")
    print()

    cases = [branch, "main", "phase-06-state", "phase-09-ghost", "scratch/experiment", None]
    out = {}
    for case in cases:
        resolved, why = resolve_phase(case, SPECS)
        out[str(case)] = {"resolved": resolved, "why": why}
        print(f"  branch={str(case)!r:22s} -> {str(resolved)!r:20s} via {why}")

    print()
    print("  phase-06-state currently holds ONLY poc-brief.md. What the rules")
    print("  say about it is the honest test of whether 'in progress' is")
    print("  representable at all:")
    live = SPECS / "phase-06-state"
    if live.is_dir():
        for rule_name, rule in RULES.items():
            reading = read_phase(live, rule)
            print(
                f"    {rule_name:18s} present={len(reading.present)}/"
                f"{len(REQUIRED_ARTIFACTS)}  complete={reading.complete}"
            )
    return out


def main() -> int:
    print(f"repo:    {REPO}")
    print(f"specs:   {SPECS}")
    workdir = Path(tempfile.mkdtemp(prefix="atom-p6-spike-"))
    print(f"scratch: {workdir}")

    results = {}
    try:
        results["q1"] = q1_grade_rules()
        results["q2"] = q2_truncation(workdir)
        results["q3"] = q3_mtime_vs_lexical(workdir)
        results["q4"] = q4_structure()
        results["q5"] = q5_resolution()
    finally:
        out = Path(__file__).parent / "results.json"
        out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        print(f"\nresults written to {out}")
        # Windows keeps handles on cloned .git objects; best-effort cleanup.
        shutil.rmtree(workdir, ignore_errors=True)
        print(f"scratch removed: {not workdir.exists()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
