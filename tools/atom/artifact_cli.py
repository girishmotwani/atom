"""Command line boundary for writing Atom artifacts and nothing else."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from atom.artifacts import ArtifactWriteRefused, classify, write_artifacts


def main(argv: Sequence[str] | None = None) -> int:
    """Write one complete Atom artifact through the dedicated permission boundary."""

    parser = argparse.ArgumentParser(prog="atom-write-artifact")
    parser.add_argument("target")
    arguments = parser.parse_args(argv)

    root = Path.cwd()
    decision = classify(root, arguments.target)
    if not decision.allowed:
        print(
            f"atom-write-artifact: refused {arguments.target} ({decision.reason})",
            file=sys.stderr,
        )
        return 1

    try:
        content = sys.stdin.buffer.read().decode("utf-8")
    except UnicodeDecodeError:
        print("atom-write-artifact: stdin is not valid UTF-8", file=sys.stderr)
        return 1
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    # Windows PowerShell prepends a UTF-8 BOM when it pipes into a native
    # command, so a leading mark is shell framing rather than something the
    # author wrote. Only the first one is removed -- a later U+FEFF is content.
    content = content.removeprefix("\ufeff")

    try:
        written = write_artifacts(root, {arguments.target: content})
    except ArtifactWriteRefused as error:
        for refusal in error.refusals:
            print(
                f"atom-write-artifact: refused {refusal.target} ({refusal.reason})",
                file=sys.stderr,
            )
        return 1
    except OSError as error:
        print(f"atom-write-artifact: {error}", file=sys.stderr)
        return 1

    print(f"Wrote {written[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
