"""Command line entry point for the atom tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from atom.check import NotAGoModuleError, run_check
from atom.gates import default_gates
from atom.index import list_spikes
from atom.report import (
    render_json,
    render_spike_json,
    render_spike_list_json,
    render_spike_list_text,
    render_spike_text,
    render_text,
)
from atom.runner import SubprocessRunner
from atom.scaffold import ScaffoldError, SlugError, scaffold_spike
from atom.spike import NotASpikeError, run_spike

# Exit codes are part of the contract, because `atom check` is designed to be used
# directly in a gate. 0 and 1 are verdicts about the code; 2 means the command
# itself could not run, which is a different thing a caller may want to treat
# differently from a genuine failure.
EXIT_PASSED = 0
EXIT_CHECK_FAILED = 1
EXIT_USAGE_ERROR = 2

# Where spikes live, relative to the repository root.
POC_DIRECTORY_NAME = "poc"


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, run the requested command, and return an exit code."""

    parser = _build_parser()
    arguments = parser.parse_args(argv)

    if arguments.command == "check":
        return _run_check_command(arguments)

    if arguments.command == "poc":
        return _run_poc_command(arguments, parser)

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

    _add_poc_parser(subparsers)

    return parser


def _add_poc_parser(subparsers: argparse._SubParsersAction) -> None:
    """Wire up `atom poc new|run|list`, the commands that make spiking cheap."""

    poc_parser = subparsers.add_parser(
        "poc",
        help="Create, run and list throwaway spikes.",
        description="Run the thing before you describe it.",
    )
    poc_subparsers = poc_parser.add_subparsers(dest="poc_command")

    new_parser = poc_subparsers.add_parser("new", help="Scaffold a new spike.")
    new_parser.add_argument("slug", help="Spike name in lowercase-hyphenated form, e.g. json-streaming.")
    new_parser.add_argument(
        "--question",
        required=True,
        help="The falsifiable question this spike will answer.",
    )

    run_parser = poc_subparsers.add_parser("run", help="Vet, build and run a spike.")
    run_parser.add_argument("slug", help="Which spike to run.")
    run_parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON.")
    run_parser.add_argument("--no-colour", action="store_true", help="Disable colour.")
    run_parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Seconds before the spike is killed (default: 300).",
    )

    list_parser = poc_subparsers.add_parser("list", help="Show every spike and its question.")
    list_parser.add_argument("--json", action="store_true", dest="as_json", help="Emit machine-readable JSON.")
    list_parser.add_argument("--no-colour", action="store_true", help="Disable colour.")


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


def _run_poc_command(arguments: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """Dispatch to the poc subcommands, or show help if none was given."""

    poc_root = Path.cwd() / POC_DIRECTORY_NAME

    if arguments.poc_command == "new":
        return _run_poc_new(arguments, poc_root)
    if arguments.poc_command == "run":
        return _run_poc_run(arguments, poc_root)
    if arguments.poc_command == "list":
        return _run_poc_list(arguments, poc_root)

    parser.parse_args(["poc", "--help"])
    return EXIT_USAGE_ERROR


def _run_poc_new(arguments: argparse.Namespace, poc_root: Path) -> int:
    try:
        result = scaffold_spike(poc_root, arguments.slug, arguments.question, SubprocessRunner())
    except (SlugError, FileExistsError) as error:
        # The invocation was wrong, not the code. One line, no traceback.
        print(f"atom poc new: {error}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    except ScaffoldError as error:
        print(f"atom poc new: {error}", file=sys.stderr)
        return EXIT_CHECK_FAILED

    print(f"Created spike '{result.slug}' at {result.directory}")
    for path in result.files_created:
        print(f"  {path.name}")
    print()
    print("Write the smallest program that answers the question, then:")
    print(f"  atom poc run {result.slug}")
    return EXIT_PASSED


def _run_poc_run(arguments: argparse.Namespace, poc_root: Path) -> int:
    spike_directory = poc_root / arguments.slug

    if not spike_directory.is_dir():
        print(
            f"atom poc run: no spike named '{arguments.slug}' in {poc_root}. "
            "Run `atom poc list` to see what exists.",
            file=sys.stderr,
        )
        return EXIT_USAGE_ERROR

    timeout_arguments = {} if arguments.timeout is None else {"timeout_seconds": arguments.timeout}

    try:
        result = run_spike(spike_directory, SubprocessRunner(), **timeout_arguments)
    except NotASpikeError as error:
        print(f"atom poc run: {error}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    if arguments.as_json:
        print(render_spike_json(result))
    else:
        use_colour = not arguments.no_colour and sys.stdout.isatty()
        print(render_spike_text(result, use_colour=use_colour))

    # B64/B69: a spike that reached a conclusion has done its job, whatever
    # that conclusion was. A Refuted spike is the method working. Non-zero here
    # means strictly "Atom could not get an answer out of your spike" -- it did
    # not compile, it timed out, or it crashed.
    return _exit_code_for_spike(result)


def _run_poc_list(arguments: argparse.Namespace, poc_root: Path) -> int:
    summaries = list_spikes(poc_root)

    if arguments.as_json:
        print(render_spike_list_json(summaries))
    else:
        use_colour = not arguments.no_colour and sys.stdout.isatty()
        print(render_spike_list_text(summaries, use_colour=use_colour))

    # An empty list is not a failure, and neither is a broken spike showing up
    # here -- `atom check` is what fails on that. This command only reports.
    return EXIT_PASSED


def _exit_code_for_spike(result) -> int:
    """Translate a spike outcome into a process exit code.

    Deliberately keyed on `answered`, not `ran`. All three verdicts --
    Confirmed, Refuted, Inconclusive -- are answers and exit 0, because a spike
    that disproves an assumption has succeeded at its job. A spike that
    crashed, timed out, or never compiled produced nothing, and that is a real
    failure worth surfacing to CI.
    """

    return EXIT_PASSED if result.answered else EXIT_CHECK_FAILED


# Must stay last in the module. Anything defined below this line does not exist
# yet when `python -m atom.cli` runs, because module execution reaches
# SystemExit first -- while `import atom.cli` defines everything and hides the
# problem. A whole green test suite once sat on top of exactly that bug.
if __name__ == "__main__":
    raise SystemExit(main())
