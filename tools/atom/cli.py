"""Command line entry point for the atom tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from atom.check import NotAGoModuleError, run_check
from atom.gates import default_gates
from atom.report import render_json, render_text
from atom.runner import SubprocessRunner

# Exit codes are part of the contract, because `atom check` is designed to be used
# directly in a gate. 0 and 1 are verdicts about the code; 2 means the command
# itself could not run, which is a different thing a caller may want to treat
# differently from a genuine failure.
EXIT_PASSED = 0
EXIT_CHECK_FAILED = 1
EXIT_USAGE_ERROR = 2


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, run the requested command, and return an exit code."""

    parser = _build_parser()
    arguments = parser.parse_args(argv)

    if arguments.command == "check":
        return _run_check_command(arguments)

    parser.print_help()
    return EXIT_USAGE_ERROR


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atom",
        description="Atom -- prove it, describe it, then build it.",
    )
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser(
        "check",
        help="Run every Go quality gate and report the result.",
    )
    check_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Go module directory to check (default: current directory).",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit machine-readable JSON instead of text.",
    )
    check_parser.add_argument(
        "--no-race",
        action="store_true",
        help="Skip the race detector, which requires cgo and is slower.",
    )
    check_parser.add_argument(
        "--no-colour",
        action="store_true",
        help="Disable colour, for logs and pasted output.",
    )

    return parser


def _run_check_command(arguments: argparse.Namespace) -> int:
    directory = Path(arguments.directory).resolve()

    try:
        report = run_check(
            directory,
            default_gates(enable_race=not arguments.no_race),
            SubprocessRunner(),
        )
    except (NotADirectoryError, NotAGoModuleError) as error:
        # These are user mistakes, not defects. A traceback here would bury the
        # one line that actually tells the user what to do.
        print(f"atom check: {error}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    if arguments.as_json:
        print(render_json(report))
    else:
        use_colour = not arguments.no_colour and sys.stdout.isatty()
        print(render_text(report, use_colour=use_colour))

    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
