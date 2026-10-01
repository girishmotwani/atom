"""Create the indexed snapshot set used by the symbol-index arm.

Copies each plain snapshot, drops the query tool beside a freshly built index,
and leaves the originals untouched -- the arms without the tool must run against
snapshots that do not contain it, or they could stumble on the index and the
comparison would mean nothing.

Usage:
    python build_all_indexed.py <source-snapshot-root> <target-root>
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent


def build_one(source: Path, target: Path) -> str:
    """Copy one snapshot, then build the index inside the copy."""

    # Copying is the slow part, so an existing index means we can skip it. This
    # makes the script safe to re-run after an interruption.
    if not (target / ".atom-index" / "index.json").exists():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)

    index_dir = target / ".atom-index"
    index_dir.mkdir(exist_ok=True)
    shutil.copy2(TOOL_DIR / "q.py", index_dir / "q.py")

    completed = subprocess.run(
        [
            sys.executable,
            str(TOOL_DIR / "build_index.py"),
            str(TOOL_DIR / "goextract" / "goextract.exe"),
            str(target),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip() or completed.stderr.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path, help="Directory of plain snapshots")
    parser.add_argument("target_root", type=Path, help="Directory to write indexed copies into")
    arguments = parser.parse_args()

    started = time.time()
    sources = sorted(path for path in arguments.source_root.iterdir() if path.is_dir())
    for source in sources:
        print(build_one(source, arguments.target_root / source.name), flush=True)
    print(f"done: {len(sources)} snapshots in {time.time() - started:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
