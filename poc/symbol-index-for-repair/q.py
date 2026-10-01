"""Symbol lookup for this snapshot.

Answers three questions that plain text search answers badly:

    symbols-in <file>      what does this file declare?
    who-uses <symbol>      which files mention it?
    where-defined <symbol> which file declares it?
    neighbours <file>      which files use anything this file declares?

`neighbours` is the useful one: it takes a file you already believe is involved
and returns the files that depend on it, ranked by how many of its symbols they
touch. Those files often share no vocabulary with the problem description, so no
amount of searching the description's words will surface them.

Examples:
    python .atom-index/q.py symbols-in src/ipam/pool.go
    python .atom-index/q.py neighbours src/ipam/pool.go
    python .atom-index/q.py who-uses ReservePrefix
    python .atom-index/q.py where-defined IpamPool

Matching is by name only. Two different types with a method of the same name
look identical here, so treat the output as leads to check, not as proof.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

# Long result lists are counterproductive -- they crowd out the caller's own
# reasoning. We show the strongest leads and say how many were held back.
MAX_RESULTS = 40

INDEX_PATH = Path(__file__).resolve().parent / "index.json"


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


def load_index() -> dict:
    """Read the prebuilt index that ships beside this script."""

    if not INDEX_PATH.exists():
        print(f"error: no index at {INDEX_PATH}", file=sys.stderr)
        sys.exit(1)
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def normalise(path_text: str, index: dict) -> str | None:
    """Accept a path in any reasonable form and return the indexed form."""

    candidate = path_text.replace("\\", "/").strip().lstrip("./")
    if candidate in index["files"]:
        return candidate
    # Fall back to a unique suffix match, so a caller may pass just the file
    # name when the full path is not to hand.
    matches = [path for path in index["files"] if path.endswith("/" + candidate)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"ambiguous: {candidate} matches {len(matches)} files:", file=sys.stderr)
        for path in sorted(matches)[:10]:
            print(f"  {path}", file=sys.stderr)
    return None


def show_lines(lines: list[str]) -> None:
    """Print a capped list, stating how much was withheld."""

    for line in lines[:MAX_RESULTS]:
        print(line)
    if len(lines) > MAX_RESULTS:
        print(f"... and {len(lines) - MAX_RESULTS} more (showing strongest {MAX_RESULTS})")


def command_symbols_in(index: dict, argument: str) -> int:
    path = normalise(argument, index)
    if path is None:
        print(f"not indexed: {argument}", file=sys.stderr)
        return 1
    entry = index["files"][path]
    print(f"{path}  (package {entry['package']})")
    print(f"declares {len(entry['defs'])} symbols:")
    show_lines(["  " + symbol for symbol in entry["defs"]])
    return 0


def command_who_uses(index: dict, symbol: str) -> int:
    if symbol in index["too_common"]:
        count = index["too_common"][symbol]
        print(f"'{symbol}' appears in {count} files -- too common to be a useful lead.")
        return 0
    users = index["used_by"].get(symbol, [])
    definers = index["defined_by"].get(symbol, [])
    if not users and not definers:
        print(f"'{symbol}' is not in the index.")
        return 0
    if definers:
        print(f"declared in: {', '.join(definers)}")
    if not is_exported(symbol) and len({package_directory(p) for p in definers}) > 1:
        print(
            "note: this name is package-private and several packages declare "
            "their own. Results below span all of them and are not one symbol."
        )
    print(f"used by {len(users)} files:")
    show_lines(["  " + path for path in users])
    return 0


def command_where_defined(index: dict, symbol: str) -> int:
    definers = index["defined_by"].get(symbol, [])
    if not definers:
        print(f"'{symbol}' is not declared anywhere in the index.")
        return 0
    for path in definers:
        print(path)
    return 0


def command_neighbours(index: dict, argument: str) -> int:
    """Rank files by how many of this file's declared symbols they use."""

    path = normalise(argument, index)
    if path is None:
        print(f"not indexed: {argument}", file=sys.stderr)
        return 1

    declared = index["files"][path]["defs"]
    seed_directory = package_directory(path)
    shared_symbol_counts: Counter[str] = Counter()
    example_symbols: dict[str, list[str]] = {}

    for symbol in declared:
        exported = is_exported(symbol)
        for user in index["used_by"].get(symbol, []):
            if user == path:
                continue
            # An unexported symbol cannot be seen outside its own package, so a
            # same-named use elsewhere belongs to a different symbol. Several
            # packages may each declare their own `retrier`; only this file's
            # package is a real lead.
            if not exported and package_directory(user) != seed_directory:
                continue
            shared_symbol_counts[user] += 1
            example_symbols.setdefault(user, [])
            if len(example_symbols[user]) < 3:
                example_symbols[user].append(symbol)

    if not shared_symbol_counts:
        print(f"nothing in the index uses anything declared by {path}.")
        return 0

    print(f"{path} declares {len(declared)} symbols.")
    print(f"{len(shared_symbol_counts)} files use at least one of them, strongest first:")
    ranked = shared_symbol_counts.most_common()
    show_lines(
        [
            f"  {user}  ({count} shared: {', '.join(example_symbols[user])})"
            for user, count in ranked
        ]
    )
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    command = sys.argv[1]
    argument = sys.argv[2]
    index = load_index()

    handlers = {
        "symbols-in": command_symbols_in,
        "who-uses": command_who_uses,
        "where-defined": command_where_defined,
        "neighbours": command_neighbours,
        "neighbors": command_neighbours,  # tolerate either spelling
    }
    handler = handlers.get(command)
    if handler is None:
        print(f"unknown command: {command}\n", file=sys.stderr)
        print(__doc__)
        return 2
    return handler(index, argument)


if __name__ == "__main__":
    sys.exit(main())
