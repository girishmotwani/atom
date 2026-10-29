"""Reproduce repeat-init preservation and partial-record overwrite behavior."""

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from atom.state import Project


def snapshot(root):
    return {
        str(path.relative_to(root)): (
            path.is_dir(),
            path.stat().st_size if path.is_file() else None,
            path.stat().st_mtime_ns,
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        )
        for path in [root, *sorted(root.rglob("*"))]
    }


def run_init(root):
    print("COMMAND: python -m atom.cli init", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "atom.cli", "init"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=180,
    )
    print(f"EXIT: {result.returncode}")
    print("STDOUT:")
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    print("STDERR:")
    print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return result.returncode


def compare(root, before):
    after = snapshot(root)
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    print(f"SNAPSHOT entries={len(before)} unchanged={not changed}")
    print(f"CHANGED: {changed}")


with tempfile.TemporaryDirectory(prefix="atom-repeat-init-") as directory:
    seed = Path(directory) / "complete"
    seed.mkdir()
    (seed / "go.mod").write_text("module example.com/repeat-init\n\ngo 1.23.0\n", encoding="utf-8")
    (seed / "target.go").write_text("package target\n\nfunc Value() string { return \"ok\" }\n", encoding="utf-8")
    print("CASE: first initialization")
    if run_init(seed) != 0:
        raise SystemExit("First initialization failed; reproduction inconclusive")
    Project(seed).record_approval(phase="phase-01-proof", gate="design-spec", date="2026-10-17")
    for attempt in (1, 2):
        print(f"CASE: valid repeat {attempt}")
        before = snapshot(seed)
        run_init(seed)
        compare(seed, before)
        print(f"APPROVALS: {len(Project(seed).load().state.approvals)}")
    for missing in ("config.json", "state.json"):
        case = Path(directory) / f"missing-{missing}"
        shutil.copytree(seed, case)
        (case / ".atom" / missing).unlink()
        print(f"CASE: missing {missing}")
        before = snapshot(case)
        run_init(case)
        compare(case, before)
        print(f"APPROVALS: {len(Project(case).load().state.approvals)}")
