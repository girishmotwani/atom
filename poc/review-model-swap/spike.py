"""Measure candidate replacements for `claude-haiku-4.5` in the default review pair.

Why this spike exists
---------------------
`DEFAULT_REVIEW_MODELS` carries a comment saying the pairing is an evidence-backed
default and that "anything else is a guess until it is measured". Finding 21 produced
evidence *against* the incumbent -- across three real reviews `claude-haiku-4.5`
contributed nine findings and zero real defects, all of them the same structural false
positive -- but no evidence *for* any particular replacement. Swapping on the strength of
a model's reputation would replace a measured default with an unmeasured one.

What is held constant
---------------------
The call is built by production's own `review_command` and the prompt is production's
own `REVIEW_PROMPT`, so this measures the thing that ships rather than a replica of it.
`FIXTURE` is imported from the Phase 4 spike, so the same defects are on offer.

Only the model name varies. `claude-haiku-4.5` is re-run rather than quoted from the
Phase 4 numbers, because a baseline measured earlier, on a different CLI build, is not a
control -- it is a memory. The two findings below are why that caution was warranted.

Two things this spike had to discover before it could measure anything
----------------------------------------------------------------------
**The Phase 4 harness no longer runs correctly.** It passes the prompt in argv (`-p`),
which the Phase 4 report named as a known deviation from production and judged harmless
for a small fixture. On CLI 1.0.89-1 it is not harmless: the call succeeds, exits zero,
and the model answers as though no diff had been supplied at all -- it searches the
working directory instead, and reports "no Go diff was provided". Both `gpt-5.4` and
`claude-sonnet-5` did this, under the Phase 4 prompt itself. Piping the identical prompt
on stdin, which is what production does, restores clean JSON from both.

Note what this does and does not invalidate. The *harness* is broken; the *numbers* it
published are not. Run over stdin, both Phase 4 models reproduce their published figures
closely -- `gpt-5.4` at 10/10 on line 24 against a published 20/20, `claude-haiku-4.5` at
6/10 on line 44 against a published 13/20. Those two controls are what license reading
anything else in this report. Production was never affected, because it pipes stdin for
an unrelated reason: argv silently corrupts large diffs on Windows.

**The answer key is committed to this repository.** Given a working directory inside
Atom's checkout, `claude-sonnet-5` ran a repository-wide search for "planted defect",
read `design-spec.md`, `decisions.md` and `findings.md`, and scored 4/4 without
reviewing the diff. Every call here therefore runs from an empty temporary directory.
That differs from production, where the model is inside the repository under review --
but in production the diff and the repository agree, and no file names the defects in
advance.

What is scored
--------------
The fixture has four planted defects, at lines 24, 36, 44 and 45. That ground truth makes
two things countable that a review of real code cannot:

* **hit rate** -- how reliably a model finds each planted defect
* **false positive rate** -- every reported line that is not one of the four

How to read the long durations in `results.json`
------------------------------------------------
Some rows record thousands of seconds against a 300-second timeout -- three
`claude-opus-5` calls near 3,890s, four `grok-4.7` calls above 22,400s. That is not
how long those models take. It is how long *this harness* took to give up, and the
reason was a defect it went on to expose in Atom itself: `subprocess.run` kills a
timed-out process and then drains its pipes with no deadline, so the wait is bounded
by whatever child the killed process left behind rather than by the timeout.

That defect is **fixed** here now, not merely explained: the timeout below uses the
same bounded process-tree kill as production, imported from `runner.py` rather than
copied. It was left explained rather than fixed for one earlier run, on the grounds
that it only moved rows the medians already excluded. It then cost six hours and
four discarded results -- see findings 31 and 32. The rows above survive as a record
of what the harness did, not as latency measurements.

The medians are taken over calls that answered, so they were never affected.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "raw"

# Production is the thing under test, so its own call builder and prompt are used
# rather than reproduced. `review_command` is where the flag choices and the
# stdin-not-argv decision are documented and justified.
sys.path.insert(0, str(HERE.parent.parent / "tools"))
from atom.extract import extract_from_run  # noqa: E402
from atom.invoke import ModelRun, RunOutcome, review_command  # noqa: E402
from atom.review import REVIEW_PROMPT  # noqa: E402
from atom.runner import (  # noqa: E402
    _DRAIN_GRACE_SECONDS,
    _kill_process_tree,
    _normalise_stream,
)

# Load the Phase 4 spike by path rather than by name. Both POCs are called
# `spike.py`, so a plain `from spike import ...` resolves to *this* module and
# fails as a circular import. Loading by path also makes it unambiguous which
# baseline is being reused. Only the fixture and the extractor are taken from it;
# its `build_command` is the broken argv path described in the module docstring.
_BASELINE_PATH = HERE.parent / "review-json" / "spike.py"
_spec = importlib.util.spec_from_file_location("review_json_spike", _BASELINE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover - environment problem
    raise RuntimeError(f"could not load the Phase 4 spike from {_BASELINE_PATH}")
_baseline = importlib.util.module_from_spec(_spec)
# `dataclass` looks the defining module up in `sys.modules`, so the module has to be
# registered there before it executes, not after.
sys.modules["review_json_spike"] = _baseline
_spec.loader.exec_module(_baseline)

FIXTURE = _baseline.FIXTURE
PROMPT = REVIEW_PROMPT

# --- experiment shape -------------------------------------------------------

# Seven candidates, measured live rather than quoted. `gpt-5.4` is measured too: it
# is the other half of the shipped pair, and the Phase 4 harness that produced its
# published figure has since been shown not to work, so that figure describes a call
# this CLI no longer makes. The Claude entries were the original question (A24); the
# gemini and grok entries are what actually answered it (A26).
MODELS = [
    "gpt-5.4",
    "claude-haiku-4.5",
    "claude-sonnet-5",
    "claude-opus-5",
    "gpt-5.6-luna",
    "gemini-3.8-flash",
    "grok-4.7",
]

# Matches the Phase 4 spike's per-cell count, which was chosen to tell 100% from 90%
# and explicitly not to tell 93% from 95%. Two candidates landing within a couple of
# points of each other is a finding in itself, not a verdict.
TRIALS_PER_MODEL = 10

PARALLEL_CALLS = 4
CALL_TIMEOUT_SECONDS = 300

# --- ground truth -----------------------------------------------------------

# The four defects deliberately planted in `fixture.diff`, recorded in the Phase 4
# design spec and findings. Everything else a model reports on this file is, by
# construction, something the fixture's author did not put there.
PLANTED_LINES = {24, 36, 44, 45}
FIXTURE_FILE = "inventory/stock.go"


@dataclass
class RunResult:
    """One call's outcome, reduced to what the comparison needs."""

    model: str
    trial: int
    seconds: float
    exit_code: int
    timed_out: bool
    readable: bool
    lines_reported: list[int] = field(default_factory=list)
    note: str = ""

    @property
    def hits(self) -> set[int]:
        """Return the planted lines this run found."""

        return {line for line in self.lines_reported if line in PLANTED_LINES}

    @property
    def false_positives(self) -> list[int]:
        """Return every reported line that was never planted."""

        return [line for line in self.lines_reported if line not in PLANTED_LINES]


def raw_path_for(model: str, trial: int) -> Path:
    return RAW_DIR / f"{model.replace('.', '_')}__{trial:02d}.txt"


def run_one_call(model: str, trial: int, prompt: str) -> RunResult:
    """Make one call, save the raw reply, then reduce it.

    The reply is written to disk before anything interprets it, so that every number
    below can be re-derived from a file rather than trusted.
    """

    command = list(review_command(model, prompt))

    # Windows CreateProcess searches PATH for the literal name and for `name.exe`
    # only -- it ignores PATHEXT -- so the npm shim `copilot.CMD` runs fine when
    # typed and is invisible to subprocess.run. Production resolves this in
    # `runner.py`, which explains it at length; this spike calls the CLI directly,
    # so it has to do the same thing.
    resolved = shutil.which(command[0])
    if resolved is not None:
        command[0] = resolved

    started = time.monotonic()
    timed_out = False

    # Run from an empty directory, not from Atom's own checkout.
    #
    # This is not tidiness. The fixture's four planted defects are documented by
    # line number in `specs/atom-cli/phase-04-review/`, and `claude-sonnet-5`
    # found them -- by running a repository-wide search for "planted defect" and
    # reading design-spec.md, decisions.md and findings.md. It scored 4/4 without
    # reviewing the diff. Any model able to read files can do the same, so a
    # measurement taken inside this repository scores recall of a committed answer
    # key rather than the reviewing the models are supposed to be doing.
    #
    # An empty directory also removes the AGENTS.md priming that had the same model
    # trying to open `skills/atom-review/SKILL.md` before it read anything else.
    with tempfile.TemporaryDirectory(prefix="atom-model-swap-") as neutral_directory:
        # `subprocess.run(timeout=...)` is not usable here, and this harness found
        # out the expensive way: the gemini/grok batch took 6h22m against a
        # 300-second limit, because four calls each blocked for over 22,000
        # seconds. `run` reacts to a timeout by killing the direct child and then
        # calling `communicate()` again with *no* timeout, and a pipe only reaches
        # EOF when the last handle to its write end closes. The CLI's own children
        # inherited that handle, so the second wait ran until they chose to exit.
        #
        # This is the same defect the phase-01 fix removed from production's
        # `runner.py`, which is why the kill below is imported from there rather
        # than reimplemented: a second copy would need fixing a second time.
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=neutral_directory,
            # Give the child its own process group so the kill can take the whole
            # tree with it. Windows gets the tree from `taskkill /T` instead.
            start_new_session=(os.name != "nt"),
        )
        try:
            # Production pipes the prompt rather than passing `-p`, and the
            # difference is not cosmetic: over argv this CLI answers as though
            # no diff arrived at all. See the module docstring.
            stdout, stderr = process.communicate(prompt, timeout=CALL_TIMEOUT_SECONDS)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_tree(process)
            try:
                stdout, stderr = process.communicate(timeout=_DRAIN_GRACE_SECONDS)
            except subprocess.TimeoutExpired as drain_expired:
                # Bounded means bounded, but "bounded" is not "discard". POSIX
                # reads pipes incrementally, so this exception can still be
                # carrying a complete reply; throwing it away here would re-file
                # an answered call as unanswered, which is finding 31 again.
                process.kill()
                stdout = _normalise_stream(drain_expired.stdout)
                stderr = (
                    _normalise_stream(drain_expired.stderr)
                    or "drain did not finish after the kill"
                )
            exit_code = -1

    seconds = time.monotonic() - started
    path = raw_path_for(model, trial)
    path.write_text(stdout, encoding="utf-8")
    if stderr.strip():
        path.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")

    result = _reduce(model, trial, seconds, exit_code, timed_out, stdout)
    status = "TIMEOUT" if timed_out else f"exit {exit_code}"
    summary = (
        f"{len(result.hits)}/4 planted, {len(result.false_positives)} other"
        if result.readable
        else f"unreadable ({result.note})"
    )
    print(f"  {model:<20} trial {trial:>2}  {seconds:>6.1f}s  {status:<8} {summary}", flush=True)
    return result


def _reduce(
    model: str, trial: int, seconds: float, exit_code: int, timed_out: bool, stdout: str
) -> RunResult:
    """Turn one raw reply into the lines it named, or record why it could not be read.

    Production's own extractor does the work, so "readable" here means exactly what
    it means to `atom review`: fences stripped, severities validated, and the B117
    file guard applied against the files the diff actually touches. Re-implementing
    a looser parser would flatter every model by accepting replies that would be
    discarded in practice.
    """

    result = RunResult(model, trial, seconds, exit_code, timed_out, readable=False)

    run = ModelRun(
        model=model,
        run_index=trial,
        # Deliberately *not* `TIMED_OUT if timed_out`. That reading cost this
        # experiment its second-best result: four grok-4.7 calls exceeded the
        # harness's clock, but every one of them had already written a complete,
        # correct reply, and the extractor discards a TIMED_OUT run without
        # looking at it. Grok published as 6/10 when it had answered 10/10.
        #
        # "The harness stopped waiting" and "the model did not answer" are
        # different facts. A reply that arrived is scored on what it says; the
        # expired clock stays on the result as a latency note, where it is
        # already excluded from the median.
        outcome=RunOutcome.COMPLETED if stdout.strip() else RunOutcome.TIMED_OUT,
        response_text=stdout,
        duration_seconds=seconds,
    )
    findings, failure = extract_from_run(run, allowed_files=[FIXTURE_FILE])

    if failure is not None and not findings:
        result.note = failure.reason
        return result

    result.readable = True
    result.lines_reported = [finding.line for finding in findings]
    if failure is not None:
        result.note = f"partially salvaged: {failure.reason}"
    return result


def collect(models: list[str], trials: int) -> list[RunResult]:
    """Run each named model the given number of times, saving output as it arrives."""

    RAW_DIR.mkdir(exist_ok=True)
    prompt = PROMPT.format(diff=FIXTURE.read_text(encoding="utf-8"))

    jobs = [(model, trial) for model in models for trial in range(1, trials + 1)]
    print(f"making {len(jobs)} calls, {PARALLEL_CALLS} at a time")
    print(f"planted defects: {sorted(PLANTED_LINES)} in {FIXTURE_FILE}\n", flush=True)

    results: list[RunResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL_CALLS) as pool:
        futures = [pool.submit(run_one_call, model, trial, prompt) for model, trial in jobs]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    return results


def _models_present(by_model: dict[str, list[RunResult]]) -> list[str]:
    """Report the configured models in their declared order, then any others.

    The sidecar accumulates across runs, so a report may cover models that this
    invocation did not call. Ordering by `MODELS` first keeps the published table
    stable while still showing a newcomer rather than silently dropping it.
    """

    ordered = [model for model in MODELS if model in by_model]
    return ordered + sorted(model for model in by_model if model not in ordered)


def _median(ordered: list[float]) -> float:
    """Middle value, averaging the two middle values for an even count."""

    if not ordered:
        return 0.0
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2


def report(results: list[RunResult]) -> None:
    """Print the three tables the decision actually needs."""

    by_model: dict[str, list[RunResult]] = defaultdict(list)
    for result in results:
        by_model[result.model].append(result)

    print("\n" + "=" * 78)
    print("PER MODEL")
    print("=" * 78)
    header = (
        f"{'model':<20} {'readable':>9} {'findings':>9} {'planted':>9} "
        f"{'false+':>8} {'median s':>9}"
    )
    print(header)
    print("-" * len(header))

    for model in _models_present(by_model):
        runs = by_model.get(model, [])
        readable = [run for run in runs if run.readable]

        # Latency is measured over calls that answered *within the clock*, which
        # since finding 31 is a narrower set than "readable". A run whose clock
        # expired still has its reply scored -- the model did answer -- but its
        # recorded duration is the harness's cleanup time, not the model's
        # response time, so it says nothing about latency and is left out here.
        #
        # This filter and the readable filter used to be the same test. Splitting
        # "did it answer" from "did the clock expire" is what made them different,
        # and missing that would have put 22,000-second cleanups into a median.
        timely = [run for run in readable if not run.timed_out]
        # An empty `timely` set is not a latency of zero, and `_median` returns
        # 0.0 for an empty list. Printing that would claim the fastest possible
        # model for one that never answered inside the clock -- the same class of
        # error as finding 31, arriving through the formatter this time.
        median = f"{_median(sorted(run.seconds for run in timely)):.1f}" if timely else "n/a"

        if not readable:
            print(f"{model:<20} {0:>4}/{len(runs):<4} {'-':>9} {'-':>9} {'-':>8} {median:>9}")
            continue

        findings = sum(len(run.lines_reported) for run in readable) / len(readable)
        planted = sum(len(run.hits) for run in readable) / len(readable)
        false_positives = sum(len(run.false_positives) for run in readable) / len(readable)

        print(
            f"{model:<20} {len(readable):>4}/{len(runs):<4} {findings:>9.1f} "
            f"{planted:>9.1f} {false_positives:>8.1f} {median:>9}"
        )

    print("\n(findings, planted and false+ are means per readable run; 4 defects were planted)")

    print("\n" + "=" * 78)
    print("PER PLANTED DEFECT -- how often each model found it")
    print("=" * 78)
    print(f"{'model':<20} " + "".join(f"line {line:<7}" for line in sorted(PLANTED_LINES)))
    print("-" * 78)
    for model in _models_present(by_model):
        readable = [run for run in by_model.get(model, []) if run.readable]
        if not readable:
            print(f"{model:<20} (no readable runs)")
            continue
        cells = []
        for line in sorted(PLANTED_LINES):
            found = sum(1 for run in readable if line in run.hits)
            cells.append(f"{found:>2}/{len(readable):<9}")
        print(f"{model:<20} " + "".join(cells))

    print("\n" + "=" * 78)
    print("FALSE POSITIVES -- lines reported that were never planted")
    print("=" * 78)
    for model in _models_present(by_model):
        readable = [run for run in by_model.get(model, []) if run.readable]
        if not readable:
            continue
        # Counted per report, not per run: a single reply sometimes names the same
        # line twice, so these counts can exceed the number of runs. Reporting them
        # as "13/10" would read as a rate, and a rate above one is a wrong number.
        counts = Counter(line for run in readable for line in run.false_positives)
        total = sum(counts.values())
        if not counts:
            print(f"{model:<20} none")
            continue
        listed = ", ".join(
            f"line {line} x{count}" for line, count in counts.most_common(8)
        )
        print(
            f"{model:<20} {len(counts)} distinct lines, {total} reports "
            f"across {len(readable)} runs: {listed}"
        )

    unreadable = [run for run in results if not run.readable]
    if unreadable:
        print("\n" + "=" * 78)
        print("UNREADABLE REPLIES")
        print("=" * 78)
        for run in sorted(unreadable, key=lambda item: (item.model, item.trial)):
            print(f"  {run.model:<20} trial {run.trial:>2}  {run.note}")


def _load_previous(summary_path: Path) -> list[RunResult]:
    """Read results banked by earlier invocations.

    Adding a fifth model should not mean re-paying for the first forty calls, and
    re-running them would change the comparison as well as its cost -- the models
    themselves move between releases. Reloading is only sound because every run in
    the file was produced by the same fixture, the same prompt and the same
    production call shape; the moment any of those changes, this file has to be
    deleted rather than appended to.
    """

    if not summary_path.exists():
        return []

    banked = []
    for row in json.loads(summary_path.read_text(encoding="utf-8")):
        result = RunResult(
            model=row["model"],
            trial=row["trial"],
            seconds=row["seconds"],
            exit_code=row["exit_code"],
            timed_out=row["timed_out"],
            readable=row["readable"],
            lines_reported=row["lines_reported"],
            note=row["note"],
        )
        banked.append(result)
    return banked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        nargs="+",
        default=MODELS,
        help="Models to call now. Models already in results.json are reported without "
        "being re-called, so a new candidate can be measured on its own.",
    )
    parser.add_argument("--trials", type=int, default=TRIALS_PER_MODEL)
    parser.add_argument(
        "--rescore",
        action="store_true",
        help="Make no calls. Re-derive every banked result from the saved replies "
        "in raw/, which is how a scoring bug is repaired without re-paying for "
        "the calls it mis-scored.",
    )
    arguments = parser.parse_args()

    summary_path = HERE / "results.json"

    if arguments.rescore:
        # The raw replies are the evidence; results.json is a view of them. When the
        # reducer was wrong -- as it was for four grok-4.7 replies that had answered
        # correctly and were filed as unreadable (finding 31) -- the replies were
        # still on disk and only the view needed rebuilding.
        results = []
        for run in _load_previous(summary_path):
            reply_path = raw_path_for(run.model, run.trial)
            if not reply_path.exists():
                results.append(run)
                continue
            results.append(
                _reduce(
                    run.model,
                    run.trial,
                    run.seconds,
                    run.exit_code,
                    run.timed_out,
                    reply_path.read_text(encoding="utf-8"),
                )
            )
        print(f"re-scored {len(results)} banked replies; no calls made\n", flush=True)
    else:
        fresh = collect(arguments.models, arguments.trials)

        # Fresh results win: a model called again is being re-measured, not topped up.
        recalled = {(run.model, run.trial) for run in fresh}
        results = fresh + [
            run
            for run in _load_previous(summary_path)
            if (run.model, run.trial) not in recalled
        ]

    report(results)

    # A JSON sidecar so the write-up can quote figures from a file rather than from
    # scrollback, which is how a Phase 3 report once reversed the sign of its own result.
    summary_path.write_text(
        json.dumps(
            [
                {
                    "model": run.model,
                    "trial": run.trial,
                    "seconds": round(run.seconds, 1),
                    "exit_code": run.exit_code,
                    "timed_out": run.timed_out,
                    "readable": run.readable,
                    "note": run.note,
                    "lines_reported": run.lines_reported,
                    "hits": sorted(run.hits),
                    "false_positives": run.false_positives,
                }
                for run in sorted(results, key=lambda item: (item.model, item.trial))
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nraw replies: {RAW_DIR}")
    print(f"summary:     {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
