"""Q3 follow-up -- is mtime ordering a PROPERTY of cloning, or was one clone lucky?

The main spike observed mtime ordering surviving a single fresh clone, which
REFUTED the prediction in the POC brief. This project has twice been misled by
a single observation, so the measurement is repeated, and a second question is
asked that the first run did not: does a *branch checkout* (as opposed to a
clone) preserve the ordering?

Run:  python poc/derived-state/probe_mtime.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PHASE_DIR = re.compile(r"^phase-(\d{2})-([a-z0-9-]+)$")
TRIALS = 4


def phase_dirs(specs_root: Path):
    return sorted(
        (p for p in specs_root.iterdir() if p.is_dir() and PHASE_DIR.match(p.name)),
        key=lambda p: p.name,
    )


def measure(specs_root: Path):
    dirs = phase_dirs(specs_root)
    lexical = [d.name for d in dirs]
    by_mtime = [d.name for d in sorted(dirs, key=lambda p: p.stat().st_mtime)]
    stamps = [d.stat().st_mtime for d in dirs]
    spread = max(stamps) - min(stamps) if stamps else 0.0
    return lexical, by_mtime, spread, len({round(s, 6) for s in stamps}), len(dirs)


def main() -> int:
    print(f"repo: {REPO}")
    print(f"trials: {TRIALS}\n")

    agreements = []
    for trial in range(1, TRIALS + 1):
        workdir = Path(tempfile.mkdtemp(prefix=f"atom-p6-mtime-{trial}-"))
        clone = workdir / "clone"
        completed = subprocess.run(
            ["git", "clone", "--quiet", str(REPO), str(clone)],
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        )
        if completed.returncode != 0:
            print(f"trial {trial}: clone FAILED -- {completed.stderr.strip()}")
            shutil.rmtree(workdir, ignore_errors=True)
            continue

        specs = clone / "specs" / "atom-cli"
        lexical, by_mtime, spread, distinct, total = measure(specs)
        agree = lexical == by_mtime
        agreements.append(agree)
        print(
            f"trial {trial}: agree={agree}  distinct={distinct}/{total}  "
            f"spread={spread * 1000:.1f} ms"
        )
        if not agree:
            print(f"          lexical: {lexical}")
            print(f"          mtime  : {by_mtime}")

        # Second question: does switching branches inside the clone disturb it?
        subprocess.run(
            ["git", "checkout", "--quiet", "phase-05-ship"],
            capture_output=True, text=True, cwd=str(clone), stdin=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "checkout", "--quiet", "main"],
            capture_output=True, text=True, cwd=str(clone), stdin=subprocess.DEVNULL,
        )
        lexical2, by_mtime2, spread2, distinct2, _ = measure(specs)
        print(
            f"          after branch round-trip: agree={lexical2 == by_mtime2}  "
            f"distinct={distinct2}/{total}  spread={spread2 * 1000:.1f} ms"
        )

        shutil.rmtree(workdir, ignore_errors=True)

    print()
    if agreements and all(agreements):
        print(f"mtime ordering held in {len(agreements)}/{len(agreements)} clones.")
        print("That makes it repeatable -- but repeatable is not guaranteed.")
        print("git checks files out in index order, which IS lexical, so the")
        print("agreement is a side effect of checkout order, not a contract.")
    else:
        print(f"mtime ordering held in {sum(agreements)}/{len(agreements)} clones -- UNSTABLE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
