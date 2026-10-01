"""Build a symbol index for one source snapshot.

Runs the `goextract` helper over a snapshot, then inverts its per-file output
into the two lookups the query tool needs:

    defined_by[symbol] -> files that declare it
    used_by[symbol]    -> files that mention it but do not declare it

The index is written into the snapshot itself, at `.atom-index/index.json`, so
that an agent confined to the snapshot directory can reach it.

Usage:
    python build_index.py <extractor-exe> <snapshot-dir>
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Symbols that appear in a very large share of files carry no navigational
# signal -- following them leads everywhere, which is the same as nowhere. We
# drop them from the reverse lookup only; `symbols-in` still reports them.
COMMON_SYMBOL_FILE_SHARE = 0.25


def is_exported(symbol: str) -> bool:
    """Report whether Go would let another package see this symbol.

    Go ties visibility to the first letter: `Reserve` is exported, `reserve` is
    package-private. For a qualified name such as `Pool.reserve`, the last
    segment decides.
    """

    last_segment = symbol.rsplit(".", 1)[-1]
    return bool(last_segment) and last_segment[0].isupper()


def package_directory(path: str) -> str:
    """Return the directory a file lives in, which in Go is its package."""

    return path.rsplit("/", 1)[0] if "/" in path else ""


def run_extractor(extractor: Path, snapshot: Path) -> list[dict]:
    """Invoke the Go extractor and collect its JSON-lines output."""

    completed = subprocess.run(
        [str(extractor), str(snapshot)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(f"extractor failed ({completed.returncode}): {completed.stderr[:2000]}")

    records = []
    for line in completed.stdout.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def build_index(records: list[dict]) -> dict:
    """Invert per-file records into symbol-keyed lookups."""

    files: dict[str, dict] = {}
    defined_by: dict[str, list[str]] = defaultdict(list)
    used_by: dict[str, list[str]] = defaultdict(list)

    for record in records:
        path = record["file"]
        files[path] = {
            "package": record["package"],
            "defs": record["defs"],
            "refs": record["refs"],
        }
        for symbol in record["defs"]:
            defined_by[symbol].append(path)
        for symbol in record["refs"]:
            used_by[symbol].append(path)

    # Prune symbols so common that "who uses this" would return most of the
    # repository. Recording the count keeps the pruning visible rather than
    # silent -- a caller asking about a dropped symbol is told why.
    file_count = max(len(files), 1)
    threshold = file_count * COMMON_SYMBOL_FILE_SHARE
    too_common = {
        symbol: len(users)
        for symbol, users in used_by.items()
        if len(users) > threshold
    }
    for symbol in too_common:
        del used_by[symbol]

    # An unexported symbol is invisible outside its own package, so a match in
    # another directory is a different symbol that merely shares a name. Go's
    # visibility rule lets us discard those with confidence -- this is the main
    # advantage the index holds over plain text search, which has no way to know
    # that one file's `retrier` is unrelated to another's.
    discarded_by_visibility = 0
    for symbol, users in list(used_by.items()):
        if is_exported(symbol):
            continue
        owning_directories = {
            package_directory(path) for path in defined_by.get(symbol, [])
        }
        if not owning_directories:
            # Used but never declared: a local variable or a name from an
            # external dependency. Either way it is not a navigational lead.
            discarded_by_visibility += len(users)
            del used_by[symbol]
            continue
        visible = [path for path in users if package_directory(path) in owning_directories]
        discarded_by_visibility += len(users) - len(visible)
        if visible:
            used_by[symbol] = visible
        else:
            del used_by[symbol]

    return {
        "file_count": len(files),
        "files": files,
        "defined_by": {symbol: sorted(paths) for symbol, paths in defined_by.items()},
        "used_by": {symbol: sorted(paths) for symbol, paths in used_by.items()},
        "too_common": too_common,
        "discarded_by_visibility": discarded_by_visibility,
    }


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    extractor = Path(sys.argv[1]).resolve()
    snapshot = Path(sys.argv[2]).resolve()

    records = run_extractor(extractor, snapshot)
    index = build_index(records)

    index_dir = snapshot / ".atom-index"
    index_dir.mkdir(exist_ok=True)
    index_path = index_dir / "index.json"
    index_path.write_text(json.dumps(index), encoding="utf-8")

    size_mb = index_path.stat().st_size / (1024 * 1024)
    print(
        f"{snapshot.name}: {index['file_count']} files, "
        f"{len(index['defined_by'])} declared symbols, "
        f"{len(index['used_by'])} usable symbols, "
        f"{len(index['too_common'])} pruned as too common, "
        f"{index['discarded_by_visibility']} name-collisions dropped, "
        f"{size_mb:.1f} MB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
