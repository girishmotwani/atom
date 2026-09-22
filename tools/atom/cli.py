"""Command line entry point for the atom tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from atom.check import NotAGoModuleError, run_check
from atom.diff import (
    DiffUnavailable,
    NoDiffSourceSelected,
    TooManyDiffSourcesSelected,
    select_source,
)
from atom.gates import default_gates
from atom.index import list_spikes
from atom.invoke import (
    DEFAULT_CONCURRENCY,
    DEFAULT_RUNS,
    NoModelAvailable,
)
from atom.merge import DEFAULT_PROXIMITY_WINDOW
from atom.report import (
    render_json,
    render_review_json,
    render_review_markdown,
    render_review_problems,
    render_spike_json,
    render_spike_list_json,
    render_spike_list_text,
    render_spike_text,
    render_status_json,
    render_status_problems,
    render_status_text,
    render_text,
)
from atom.review import DEFAULT_REVIEW_MODELS, run_review
from atom.runner import SubprocessRunner
from atom.scaffold import ScaffoldError, SlugError, scaffold_spike
from atom.ship import DEFAULT_BASE_BRANCH, PrAction, ShipRefused, run_ship
from atom.spike import NotASpikeError, run_spike
from atom.state import Project
from atom.status import collect_status
from atom.storage import StateWriteFailed

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

    if arguments.command == "init":
        return _run_init_command(arguments)

    if arguments.command == "status":
        return _run_status_command(arguments)

    if arguments.command == "review":
        return _run_review_command(arguments)

    if arguments.command == "ship":
        return _run_ship_command(arguments)

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
    _add_state_parsers(subparsers)
    _add_review_parser(subparsers)
    _add_ship_parser(subparsers)

    return parser


def _add_review_parser(subparsers: argparse._SubParsersAction) -> None:
    review_parser = subparsers.add_parser(
        "review",
        help="Ask several models to review a diff and merge what they agree on.",
    )

    # No default source. B104 makes choosing one explicit, because each option
    # reviews genuinely different code and a wrong guess reviews the wrong
    # thing silently.
    review_parser.add_argument(
        "--working", action="store_true",
        help="Review uncommitted changes in the working tree.",
    )
    review_parser.add_argument(
        "--staged", action="store_true",
        help="Review staged changes only.",
    )
    review_parser.add_argument(
        "--branch", metavar="REF",
        help="Review this branch's changes against REF.",
    )
    review_parser.add_argument(
        "--model", action="append", dest="models", metavar="NAME",
        help="Model to consult; repeat for several (default: gpt-5.4 and claude-haiku-4.5).",
    )
    review_parser.add_argument(
        "--runs", type=int, default=DEFAULT_RUNS,
        help=(
            "Times to ask each model (default: %(default)s). Repetition is the "
            "confidence signal: compliance and findings both vary between runs."
        ),
    )
    review_parser.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help="Calls to run at once (default: %(default)s).",
    )
    review_parser.add_argument(
        "--window", type=int, default=DEFAULT_PROXIMITY_WINDOW,
        help=(
            "Lines apart that findings may be and still be treated as one "
            "problem (default: %(default)s)."
        ),
    )
    review_parser.add_argument(
        "--disable-mcp-server", action="append", dest="disable_mcp_servers",
        default=[], metavar="NAME",
        help="MCP server to disable for each call; repeat for several.",
    )
    review_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Emit machine-readable JSON instead of markdown.",
    )


def _add_state_parsers(subparsers: argparse._SubParsersAction) -> None:
    """Wire up `atom init` and `atom status`, the commands that track a project."""

    init_parser = subparsers.add_parser(
        "init",
        help="Create .atom/ and start the project at the first phase.",
    )
    init_parser.add_argument(
        "--module",
        required=True,
        dest="module_path",
        help="The Go module path this project builds, e.g. example.com/thing.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Re-initialise a project that already exists, discarding its state.",
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Show the current phase, recent activity, and any problems.",
    )
    status_parser.add_argument(
        "--json", action="store_true", dest="as_json", help="Emit machine-readable JSON."
    )
    status_parser.add_argument(
        "--no-colour", action="store_true", help="Disable colour."
    )


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


def _run_init_command(arguments: argparse.Namespace) -> int:
    """Create a new Atom project in the current directory."""

    project = Project(Path.cwd())

    # B96: overwriting an existing project silently would destroy a record of
    # work. Refusing by default costs one flag; the alternative costs progress.
    if project.is_initialised and not arguments.force:
        print(
            f"atom init: {project.state_directory} already exists.\n"
            "Re-initialising would discard the phase this project has reached.\n"
            "Pass --force if that is genuinely what you want.",
            file=sys.stderr,
        )
        return EXIT_USAGE_ERROR

    try:
        state = project.initialise(module_path=arguments.module_path)
    except StateWriteFailed as error:
        # B83/B83a: never claim success for work whose record was not saved,
        # and never report the failure without a route out of it.
        print(f"atom init: {error}", file=sys.stderr)
        return EXIT_CHECK_FAILED

    print(f"Initialised {project.state_directory}")
    print(f"  module: {arguments.module_path}")
    print(f"  phase:  {state.phase.value} ({state.status.value.replace('_', ' ')})")
    print()
    print("Atom starts by proving things, not describing them:")
    print("  atom poc new <slug> --question \"...\"")
    return EXIT_PASSED


def _run_status_command(arguments: argparse.Namespace) -> int:
    """Report where the project is, and everything wrong with it (B93)."""

    project = Project(Path.cwd())
    report = collect_status(project)

    if arguments.as_json:
        # Emitted on both paths: a caller that asked for JSON needs parseable
        # output even when the answer is "your state file is broken".
        print(render_status_json(report))
    else:
        use_colour = not arguments.no_colour and sys.stdout.isatty()
        print(render_status_text(report, use_colour=use_colour))

    # Problems go to stderr on both paths, and appear exactly once. The answer
    # belongs on stdout so `atom status > phase.txt` captures it; the problems
    # belong on stderr so they stay visible when it is redirected.
    if report.problems:
        if arguments.as_json:
            for problem in report.problems:
                print(f"atom status: {problem}", file=sys.stderr)
        else:
            use_colour = not arguments.no_colour and sys.stderr.isatty()
            print(render_status_problems(report, use_colour=use_colour), file=sys.stderr)

    # B95: a command that could not answer its question has not succeeded, even
    # though it ran without error. Same reasoning as Phase 2's crashed spike.
    return EXIT_PASSED if report.could_answer else EXIT_CHECK_FAILED


def _run_review_command(arguments: argparse.Namespace) -> int:
    """Ask several models about a diff and report what they said (B103-B137)."""

    try:
        request = select_source(
            staged=arguments.staged,
            branch=arguments.branch,
            working=arguments.working,
        )
    except (NoDiffSourceSelected, TooManyDiffSourcesSelected) as error:
        print(f"atom review: {error}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    try:
        outcome = run_review(
            request=request,
            models=arguments.models or list(DEFAULT_REVIEW_MODELS),
            runner=SubprocessRunner(),
            working_directory=Path.cwd(),
            runs=arguments.runs,
            concurrency=arguments.concurrency,
            window=arguments.window,
            disable_mcp_servers=arguments.disable_mcp_servers,
        )
    except ValueError as error:
        # Nonsensical settings are refused rather than clamped (A8): `--runs 0`
        # would otherwise produce a clean-looking review that consulted nobody.
        print(f"atom review: {error}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    except DiffUnavailable as error:
        print(f"atom review: {error}", file=sys.stderr)
        return EXIT_CHECK_FAILED
    except NoModelAvailable as error:
        # The other door to B130. Reaching the same dangerous state through a
        # different path must not produce a less clear message, so the sentence
        # that names the confusion is attached here too.
        print(
            f"atom review: {error}\n"
            "atom review: no model returned a usable response; "
            "this is not a clean review.",
            file=sys.stderr,
        )
        return EXIT_CHECK_FAILED

    # The report goes to stdout on both paths so `atom review > review.md`
    # captures it; problems go to stderr so they stay visible when it is
    # redirected, and appear exactly once (B128, P3-5).
    if arguments.as_json:
        print(render_review_json(outcome))
    else:
        print(render_review_markdown(outcome))

    problems = render_review_problems(outcome)
    if problems:
        print(problems.rstrip(), file=sys.stderr)

    if outcome.has_no_usable_response:
        # B130. Loudly, because an empty report is indistinguishable from a
        # clean one, and this is the case where that confusion is dangerous.
        print(
            "atom review: no model returned a usable response; "
            "this is not a clean review.",
            file=sys.stderr,
        )
        return EXIT_CHECK_FAILED

    # B136: findings never change the exit code, but an incomplete review does.
    # A CI job where one model failed every run would otherwise stay green
    # forever while nobody read the banner.
    return EXIT_CHECK_FAILED if outcome.is_partial else EXIT_PASSED


def _exit_code_for_spike(result) -> int:
    """Translate a spike outcome into a process exit code.

    Deliberately keyed on `answered`, not `ran`. All three verdicts --
    Confirmed, Refuted, Inconclusive -- are answers and exit 0, because a spike
    that disproves an assumption has succeeded at its job. A spike that
    crashed, timed out, or never compiled produced nothing, and that is a real
    failure worth surfacing to CI.
    """

    return EXIT_PASSED if result.answered else EXIT_CHECK_FAILED


def _add_ship_parser(subparsers: argparse._SubParsersAction) -> None:
    ship_parser = subparsers.add_parser(
        "ship",
        help="Turn the current branch's finished phase into a pull request.",
    )
    ship_parser.add_argument(
        "--base", dest="base_branch", default=DEFAULT_BASE_BRANCH, metavar="REF",
        help="Branch the pull request merges into (default: %(default)s).",
    )
    ship_parser.add_argument(
        "--phase", metavar="NAME",
        help=(
            "Phase directory name, when it cannot be read from the branch "
            "(for example phase-05-ship)."
        ),
    )
    ship_parser.add_argument(
        "--title", metavar="TEXT",
        help="Pull request title (default: taken from the design spec heading).",
    )
    ship_parser.add_argument(
        "--push", action="store_true",
        help=(
            "Push the branch and set its upstream first. Required when the "
            "branch has no upstream, because gh will not push for you."
        ),
    )
    # B147a. The override is a flag rather than a prompt because ship must be
    # runnable from CI, where there is nobody to answer a prompt. It does not
    # change a word of the body: the failure is stated either way.
    ship_parser.add_argument(
        "--allow-failing-checks", action="store_true",
        help=(
            "Open the pull request even though atom check failed. The failure "
            "is recorded in the body and the command still exits non-zero."
        ),
    )
    ship_parser.add_argument(
        "--no-race", action="store_true",
        help="Skip the race detector in the fresh check, which requires cgo.",
    )


def _run_ship_command(arguments: argparse.Namespace) -> int:
    """Assemble the pull request for the current branch's phase."""

    runner = SubprocessRunner()
    gates = default_gates(include_race=not arguments.no_race)

    try:
        outcome = run_ship(
            runner,
            Path.cwd(),
            base_branch=arguments.base_branch,
            phase=arguments.phase,
            title=arguments.title,
            push=arguments.push,
            allow_failing_checks=arguments.allow_failing_checks,
            gates=gates,
        )
    except ShipRefused as refusal:
        # B156. Every refusal -- missing gh, dirty tree, failing check -- leaves
        # by this one route, because ship reuses the existing exit scheme rather
        # than inventing a "precondition" code nobody else in the CLI speaks.
        print(f"atom ship refused: {refusal}", file=sys.stderr)
        return EXIT_CHECK_FAILED

    verb = "Opened" if outcome.pr_action is PrAction.CREATED else "Updated"
    print(f"{verb} {outcome.pr_url}")
    print(f"  phase    {outcome.phase_directory.name}")
    print(f"  commit   {outcome.commit_sha[:12]}")
    print(f"  body     {outcome.body_char_count} characters")

    if outcome.check_overridden:
        # B147b. Said plainly on stderr, and the exit code agrees with it. A run
        # that shipped over a failing gate has not passed, and neither the text
        # nor the status should let anyone believe otherwise.
        print(
            "\natom check failed and --allow-failing-checks was given. The pull "
            "request is open and states the failure; this run did not pass.",
            file=sys.stderr,
        )

    return EXIT_PASSED if outcome.succeeded else EXIT_CHECK_FAILED


# Must stay last in the module. Anything defined below this line does not exist
# yet when `python -m atom.cli` runs, because module execution reaches
# SystemExit first -- while `import atom.cli` defines everything and hides the
# problem. A whole green test suite once sat on top of exactly that bug.
if __name__ == "__main__":
    raise SystemExit(main())
