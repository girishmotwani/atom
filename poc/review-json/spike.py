"""Phase 4 spike: can the Copilot CLI be driven to return schema-valid review findings?

`atom review` will send a diff to two or more models and merge what comes back. Merging
is done in code, so the findings have to be structured. Nothing obliges a model to
produce structure -- it is a text generator, and valid JSON is a habit rather than a
guarantee.

This spike measures how often that habit holds, across:

  * two extraction contracts -- the CLI's own `--output-format json` envelope, versus
    plain `--silent` stdout;
  * two models from different families.

Four cells. The prompt and the diff are identical everywhere, so the only things that
vary are the transport and the model.

Read `specs/atom-cli/phase-04-review/poc-brief.md` first. It records the predictions
and, importantly, the decision rule -- fixed before this ran, so the numbers choose
the design rather than the other way round.

Usage:
    python poc/review-json/spike.py            # collect responses, then analyse
    python poc/review-json/spike.py --analyse  # re-analyse saved responses only
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "raw"
FIXTURE = HERE / "fixture.diff"

# --- experiment shape -------------------------------------------------------

MODELS = ["gpt-5.4", "claude-haiku-4.5"]
CONTRACTS = ["envelope", "plain"]
TRIALS_PER_CELL = 10

# Enough to tell 100% from 90%; not enough to tell 93% from 95%. If a cell lands
# within a couple of points of a cut-off, that is a finding in itself -- the honest
# response is more trials, not a confident verdict.

# Each call takes well over a minute, so forty of them in sequence is close to an
# hour. Four at a time keeps it manageable without pushing hard enough to make rate
# limiting a plausible confound.
PARALLEL_CALLS = 4
CALL_TIMEOUT_SECONDS = 300

# --- the contract we are asking the model to honour -------------------------

ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}
REQUIRED_FIELDS = {"file", "line", "severity", "message"}

PROMPT = """You are reviewing a Go diff. Report real problems only.

Respond with a JSON array. Every element must be an object with exactly these keys:
  "file": string, the path from the diff
  "line": integer, the line number in the new file
  "severity": one of "critical", "high", "medium", "low"
  "message": string, one sentence describing the problem

Respond with the JSON array and nothing else. No prose, no explanation, no headings.

Here is the diff:

{diff}
"""


def build_command(model: str, contract: str, prompt: str) -> list[str]:
    """Assemble the CLI invocation for one cell.

    The flags that are not about the contract are about reproducibility. Without
    `--no-custom-instructions` the CLI would read Atom's own AGENTS.md and this spike
    would measure something specific to this repository. `--disable-builtin-mcps`
    removes both a latency cost and a source of machine-to-machine variation.

    This deliberately names no individual MCP server. The authoring machine had
    vendor-specific servers configured, and an earlier revision disabled them by
    name -- which put one environment's private names into a tool meant to be
    read by anyone. A7 removed them from the shipped code for that reason, and
    the same reasoning applies to a spike that is committed as evidence.

    That removal is not free, and the cost is recorded rather than hidden: the
    committed replies under `raw/` were produced by a command that DID name two
    servers, so they show those servers disabled. Re-running this spike on a
    machine with third-party servers configured will load them, which is a
    condition the recorded run did not have. The contract question this spike
    answers -- does the envelope carry parseable JSON -- does not depend on
    which servers are loaded, so the finding stands; a rerun measuring LATENCY
    should pass its own `--disable-mcp-server` flags rather than reintroducing
    someone else's names here.
    """
    command = [
        "copilot",
        "-p",
        prompt,
        "--model",
        model,
        "--no-custom-instructions",
        "--disable-builtin-mcps",
        "--no-color",
    ]
    if contract == "envelope":
        command += ["--output-format", "json"]
    else:
        command += ["--silent"]
    return command


# --- collection -------------------------------------------------------------


@dataclass
class CallRecord:
    """One completed (or failed) call, and where its raw output was saved."""

    model: str
    contract: str
    trial: int
    exit_code: int
    seconds: float
    raw_path: Path
    timed_out: bool = False

    @property
    def cell(self) -> str:
        return f"{self.contract}/{self.model}"


def raw_path_for(model: str, contract: str, trial: int) -> Path:
    safe_model = model.replace(".", "_")
    return RAW_DIR / f"{contract}__{safe_model}__{trial:02d}.txt"


def run_one_call(model: str, contract: str, trial: int, prompt: str) -> CallRecord:
    """Make one call and save its raw output before anything tries to interpret it.

    Saving first is deliberate. Every number in the report has to be traceable back to
    a file on disk, so that the analysis can be re-run and checked rather than
    remembered. Phase 3 produced a write-up that reversed the sign of its own
    measurement because a figure was quoted from memory.
    """
    command = build_command(model, contract, prompt)
    started = time.monotonic()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CALL_TIMEOUT_SECONDS,
        )
        stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
    except subprocess.TimeoutExpired as expired:
        timed_out = True
        stdout = expired.stdout.decode("utf-8", "replace") if isinstance(expired.stdout, bytes) else (expired.stdout or "")
        stderr = expired.stderr.decode("utf-8", "replace") if isinstance(expired.stderr, bytes) else (expired.stderr or "")
        exit_code = -1

    seconds = time.monotonic() - started
    path = raw_path_for(model, contract, trial)
    # stderr is kept in a sidecar so the primary file stays byte-for-byte what the
    # extractor will see in production.
    path.write_text(stdout, encoding="utf-8")
    if stderr.strip():
        path.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")

    record = CallRecord(model, contract, trial, exit_code, seconds, path, timed_out)
    status = "TIMEOUT" if timed_out else f"exit {exit_code}"
    print(f"  {record.cell:<30} trial {trial:>2}  {seconds:>6.1f}s  {status}", flush=True)
    return record


def collect() -> list[CallRecord]:
    """Run every cell, in parallel, saving raw output as it arrives."""
    RAW_DIR.mkdir(exist_ok=True)
    prompt = PROMPT.format(diff=FIXTURE.read_text(encoding="utf-8"))

    jobs = [
        (model, contract, trial)
        for contract in CONTRACTS
        for model in MODELS
        for trial in range(1, TRIALS_PER_CELL + 1)
    ]
    print(f"making {len(jobs)} calls, {PARALLEL_CALLS} at a time\n", flush=True)

    records: list[CallRecord] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL_CALLS) as pool:
        futures = [pool.submit(run_one_call, *job, prompt) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    return records


# --- extraction -------------------------------------------------------------

FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def assistant_content_from_envelope(raw: str) -> tuple[bool, str | None]:
    """Pull the assistant's reply out of the JSONL envelope.

    Returns (transport_was_valid, content). The envelope is a stream of events; the
    final reply arrives as an `assistant.message`. Transport validity is tracked
    separately from findings validity because the two fail for different reasons and
    conflating them would hide which layer is at fault.
    """
    content: str | None = None
    saw_any_event = False
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            # A single unparseable line means the transport itself is unreliable.
            return False, content
        saw_any_event = True
        if event.get("type") == "assistant.message":
            content = event.get("data", {}).get("content")
    return saw_any_event, content


def locate_json_payload(content: str) -> str | None:
    """Find the JSON array inside a model reply that may be wrapped in prose or fences.

    This is the salvage step, and the spike measures validity *before* it is applied
    as well as after -- otherwise the repair logic would end up justifying itself.
    """
    if not content:
        return None
    fenced = FENCE_PATTERN.search(content)
    if fenced:
        return fenced.group(1).strip()
    start, end = content.find("["), content.rfind("]")
    if start != -1 and end > start:
        return content[start : end + 1]
    return None


def validate_findings(payload: str | None) -> tuple[bool, str]:
    """Check a payload against the schema. Returns (is_valid, reason_if_not)."""
    if payload is None:
        return False, "no payload found"
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as error:
        return False, f"invalid json: {str(error)[:40]}"
    if not isinstance(parsed, list):
        return False, f"not an array: {type(parsed).__name__}"
    for element in parsed:
        if not isinstance(element, dict):
            return False, "element is not an object"
        missing = REQUIRED_FIELDS - set(element)
        if missing:
            return False, f"missing field(s): {','.join(sorted(missing))}"
        if element["severity"] not in ALLOWED_SEVERITIES:
            return False, f"bad severity: {element['severity']!r}"
        if not isinstance(element["line"], int):
            return False, f"line is {type(element['line']).__name__}, not int"
    return True, ""


@dataclass
class Outcome:
    """The three independent verdicts for a single call."""

    cell: str
    transport_valid: bool
    found_payload: bool
    schema_valid: bool
    strict_valid: bool  # valid with no salvage: the raw content parsed as-is
    reason: str


def analyse_one(path: Path) -> Outcome | None:
    """Score one saved response. Returns None if the file is missing."""
    if not path.exists():
        return None
    name = path.name
    contract = name.split("__")[0]
    model = name.split("__")[1].replace("_", ".")
    raw = path.read_text(encoding="utf-8")

    if contract == "envelope":
        transport_valid, content = assistant_content_from_envelope(raw)
    else:
        # Plain stdout has no transport layer to speak of, so it cannot fail one.
        transport_valid, content = True, raw

    content = content or ""
    # Strict: did the reply parse as schema-valid JSON with no salvage at all?
    strict_valid, _ = validate_findings(content.strip() or None)
    payload = locate_json_payload(content)
    schema_valid, reason = validate_findings(payload)

    return Outcome(
        cell=f"{contract}/{model}",
        transport_valid=transport_valid,
        found_payload=payload is not None,
        schema_valid=schema_valid,
        strict_valid=strict_valid,
        reason=reason,
    )


# --- reporting --------------------------------------------------------------


@dataclass
class CellTally:
    """Running counts for one cell of the experiment."""

    total: int = 0
    transport_valid: int = 0
    found_payload: int = 0
    schema_valid: int = 0
    strict_valid: int = 0
    reasons: list[str] = field(default_factory=list)

    def percent(self, count: int) -> float:
        return 100.0 * count / self.total if self.total else 0.0


def verdict_for(rate: float) -> str:
    """Apply the decision rule fixed in the brief before any data existed."""
    if rate >= 95.0:
        return "JSON contract holds -- parse plainly"
    if rate >= 80.0:
        return "JSON contract needs an explicit repair layer"
    return "JSON contract abandoned -- use a line-oriented format"


def analyse_and_report() -> int:
    tallies: dict[str, CellTally] = {}
    for contract in CONTRACTS:
        for model in MODELS:
            for trial in range(1, TRIALS_PER_CELL + 1):
                outcome = analyse_one(raw_path_for(model, contract, trial))
                if outcome is None:
                    continue
                tally = tallies.setdefault(outcome.cell, CellTally())
                tally.total += 1
                tally.transport_valid += outcome.transport_valid
                tally.found_payload += outcome.found_payload
                tally.schema_valid += outcome.schema_valid
                tally.strict_valid += outcome.strict_valid
                if not outcome.schema_valid:
                    tally.reasons.append(outcome.reason)

    if not tallies:
        print("no saved responses found -- run without --analyse first")
        return 1

    print("\n" + "=" * 78)
    print("RESULTS -- percentages are per call, before any repair")
    print("=" * 78)
    header = f"{'cell':<28} {'n':>3} {'transport':>10} {'strict':>8} {'salvaged':>9}"
    print(header)
    print("-" * 78)
    for cell in sorted(tallies):
        tally = tallies[cell]
        print(
            f"{cell:<28} {tally.total:>3} "
            f"{tally.percent(tally.transport_valid):>9.0f}% "
            f"{tally.percent(tally.strict_valid):>7.0f}% "
            f"{tally.percent(tally.schema_valid):>8.0f}%"
        )

    print("\nfailure reasons, by cell:")
    for cell in sorted(tallies):
        reasons = tallies[cell].reasons
        if not reasons:
            print(f"  {cell:<28} none")
            continue
        counted: dict[str, int] = {}
        for reason in reasons:
            counted[reason] = counted.get(reason, 0) + 1
        summary = "; ".join(f"{reason} x{count}" for reason, count in sorted(counted.items()))
        print(f"  {cell:<28} {summary}")

    # The governing rate is the worst cell: atom review has to work with whichever
    # model the developer actually has, not with the best one available.
    worst_cell = min(tallies, key=lambda c: tallies[c].percent(tallies[c].strict_valid))
    worst_rate = tallies[worst_cell].percent(tallies[worst_cell].strict_valid)
    print("\n" + "=" * 78)
    print(f"worst cell (strict, no salvage): {worst_cell} at {worst_rate:.0f}%")
    print(f"VERDICT: {verdict_for(worst_rate)}")
    print("=" * 78)
    return 0


def main() -> int:
    global TRIALS_PER_CELL

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--analyse",
        action="store_true",
        help="skip collection and re-score the responses already saved in raw/",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=TRIALS_PER_CELL,
        help="trials per cell; lower values are for smoke-testing the harness, not for measuring",
    )
    arguments = parser.parse_args()

    TRIALS_PER_CELL = arguments.trials

    if not arguments.analyse:
        if not FIXTURE.exists():
            print(f"missing fixture diff at {FIXTURE}")
            return 1
        started = time.monotonic()
        collect()
        print(f"\ncollection took {(time.monotonic() - started) / 60:.1f} minutes")

    return analyse_and_report()


if __name__ == "__main__":
    sys.exit(main())
