"""Score repair-file prediction with optional repository knowledge context.

This is a deliberately readable measurement spike. The experiment asks a
Copilot CLI agent, running inside a snapshot made from one parent tree, to
predict the files that should change for a one-sentence repair request. The
script then compares those paths with curated ground truth.

The comments are intentionally heavy because the measurement is easy to bias:
snapshots must not contain version-control metadata, prompts must not reveal the
answer, and the extra-context arm must not contain file listings or repair-
specific hints.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import statistics
import subprocess
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

DEFAULT_MODEL = "gpt-5.4"
DEFAULT_TIMEOUT_SECONDS = 900.0
DEFAULT_TRIALS = 5
DEFAULT_WORKERS = 6
DRAIN_GRACE_SECONDS = 2.0
MAX_CONSECUTIVE_FAILURES = 20
VALID_ARMS = ("plain", "knowledge-base", "symbol-walk", "symbol-index")

# Arms that need the snapshot copy carrying `.atom-index/`. The other arms must
# run against snapshots without it, or they could stumble on the index and the
# comparison would mean nothing.
ARMS_WITH_INDEX = ("symbol-index",)

# The one-path-per-line fallback should not turn prose refusals into fake paths.
PATHLIKE_LINE = re.compile(
    r"(?:^[A-Za-z]:[\\/])|(?:[\\/])|(?:\.(?:go|cs|py|json|ya?ml|md|proto|thrift|txt)$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GroundTruthCase:
    """One curated repair and the truth paths used for scoring."""

    sha8: str
    sha: str
    parent_sha: str
    request: str
    truth_files: tuple[str, ...]
    excluded_files: tuple[str, ...]
    raw: dict


@dataclass(frozen=True)
class ParsedReply:
    """Machine-readable paths extracted from one raw reply."""

    readable: bool
    paths: tuple[str, ...] = ()
    reason: str = ""
    parser: str = ""


@dataclass(frozen=True)
class InvocationResult:
    """Evidence from one Copilot CLI invocation."""

    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    seconds: float


@dataclass(frozen=True)
class ScoredRun:
    """One trial after parsing and scoring."""

    sha8: str
    arm: str
    trial: int
    raw_path: str
    readable: bool
    parse_reason: str
    parser: str
    predicted: tuple[str, ...]
    truth: tuple[str, ...]
    missed: tuple[str, ...]
    recall: float | None
    precision: float | None
    seconds: float | None = None
    exit_code: int | None = None
    timed_out: bool = False


@dataclass(frozen=True)
class WorkItem:
    """One independently callable experimental unit."""

    case: GroundTruthCase
    arm: str
    trial: int
    snapshot: Path


@dataclass(frozen=True)
class TrialOutcome:
    """The scored result plus bookkeeping that is not part of scoring."""

    scored: ScoredRun
    skipped_existing_raw: bool


@dataclass(frozen=True)
class ExperimentPaths:
    """Filesystem locations supplied by the caller."""

    ground_truth: Path
    source_repo: Path
    snapshot_root: Path
    knowledge_base: Path
    out: Path

    @property
    def raw_dir(self) -> Path:
        return self.out / "raw"

    @property
    def results_path(self) -> Path:
        return self.out / "results.json"


@dataclass(frozen=True)
class ExperimentConfig:
    """Values that must be threaded through workers without globals."""

    paths: ExperimentPaths
    subtree: str
    knowledge_base_text: str


def normalise_subtree(subtree: str) -> str:
    """Return a stable forward-slash subtree value for prompts and path cleanup."""

    cleaned = subtree.strip().replace("\\", "/").strip("/")
    if not cleaned:
        raise SystemExit("--subtree must not be empty")
    return str(PurePosixPath(cleaned))


def normalise_repo_path(path_text: str, subtree: str, snapshot_dir: Path | None = None) -> str:
    """Convert emitted paths to canonical repo-relative forward-slash paths."""

    text = path_text.strip().strip("`'\"").strip()
    text = text.replace("\\", "/")
    text = re.sub(r"^file:///?", "", text, flags=re.IGNORECASE)

    if snapshot_dir is not None:
        snapshot_prefix = snapshot_dir.resolve().as_posix().rstrip("/").lower()
        lowered = text.lower()
        if lowered == snapshot_prefix:
            text = ""
        elif lowered.startswith(snapshot_prefix + "/"):
            text = text[len(snapshot_prefix) + 1 :]

    # Some replies include a host path. Keep only the configured subtree suffix
    # so local machine layout cannot affect scoring.
    marker = subtree.rstrip("/") + "/"
    marker_index = text.lower().find(marker.lower())
    if marker_index >= 0:
        text = text[marker_index:]

    while text.startswith("./"):
        text = text[2:]
    text = text.lstrip("/")
    return str(PurePosixPath(text)) if text else ""


def unique_paths(paths: Iterable[str]) -> tuple[str, ...]:
    """Deduplicate paths in first-seen order."""

    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        cleaned = path.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            ordered.append(cleaned)
    return tuple(ordered)


def load_ground_truth(directory: Path, subtree: str, selected_sha8s: set[str] | None = None) -> list[GroundTruthCase]:
    """Load curated JSON cases.

    Scoring intentionally uses `ground_truth` only. `excluded` files are loaded
    and reported, but ignored: they are neither credited nor penalised.
    """

    if not directory.is_dir():
        raise SystemExit(f"--ground-truth must be an existing directory: {directory}")

    cases: list[GroundTruthCase] = []
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        sha8 = str(data["sha8"])
        if selected_sha8s is not None and sha8 not in selected_sha8s:
            continue

        truth_files = tuple(
            sorted({normalise_repo_path(str(entry["file"]), subtree) for entry in data.get("ground_truth", [])})
        )
        excluded_files = tuple(
            sorted({normalise_repo_path(str(entry["file"]), subtree) for entry in data.get("excluded", [])})
        )
        cases.append(
            GroundTruthCase(
                sha8=sha8,
                sha=str(data["sha"]),
                parent_sha=str(data["parent_sha"]),
                request=str(data["request"]),
                truth_files=truth_files,
                excluded_files=excluded_files,
                raw=data,
            )
        )

    if selected_sha8s is not None:
        missing = sorted(selected_sha8s - {case.sha8 for case in cases})
        if missing:
            raise SystemExit(f"No ground-truth JSON found for: {', '.join(missing)}")
    if not cases:
        raise SystemExit("No ground-truth JSON cases were loaded")
    return cases


def snapshot_dir_for(case: GroundTruthCase, snapshot_root: Path) -> Path:
    """Return the stable snapshot path for a repair."""

    return snapshot_root / case.sha8


def directory_has_any_entry(path: Path) -> bool:
    """Return true when an existing directory is non-empty."""

    return path.is_dir() and any(path.iterdir())


def ensure_snapshot(case: GroundTruthCase, config: ExperimentConfig) -> Path:
    """Export the parent source tree with no version-control metadata.

    `git archive` materialises file contents from `parent_sha`; it does not copy
    metadata. The destination is skipped when already non-empty so interrupted
    or repeated runs are idempotent.
    """

    destination = snapshot_dir_for(case, config.paths.snapshot_root)
    metadata_dir = destination / ".git"
    if metadata_dir.exists():
        raise RuntimeError(f"snapshot unexpectedly contains version-control metadata: {metadata_dir}")
    if directory_has_any_entry(destination):
        return destination

    destination.mkdir(parents=True, exist_ok=True)
    git_command = [
        "git",
        "-C",
        str(config.paths.source_repo),
        "archive",
        "--format=tar",
        case.parent_sha,
        "--",
        config.subtree,
    ]
    tar_command = ["tar", "-x", "-C", str(destination)]

    git_process = subprocess.Popen(git_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
    assert git_process.stdout is not None
    tar_process = subprocess.Popen(
        tar_command,
        stdin=git_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    git_process.stdout.close()
    tar_stdout, tar_stderr = tar_process.communicate()
    git_stderr = git_process.stderr.read().decode("utf-8", errors="replace") if git_process.stderr else ""
    git_exit = git_process.wait()

    if git_exit != 0 or tar_process.returncode != 0:
        raise RuntimeError(
            "snapshot export failed\n"
            f"git exit: {git_exit}\n{git_stderr}\n"
            f"tar exit: {tar_process.returncode}\n{tar_stdout}\n{tar_stderr}"
        )
    if metadata_dir.exists():
        raise RuntimeError(f"snapshot unexpectedly contains version-control metadata: {metadata_dir}")
    return destination

def build_prompt(request: str, arm: str, subtree: str, knowledge_base_text: str = "") -> str:
    """Build the plain or extra-context prompt."""

    base = f"""You are working in a source snapshot for a repair task.

Repair request:
{request}

Your job is to identify every repo-relative source file that likely must change to implement this repair.

Use ordinary search through the files in the current working directory. Be deliberately over-inclusive: recall matters more than precision, and a missed required file is the failure this experiment cares about.

Do not edit files. Do not assume git history is available. Report paths relative to the directory you are working in, using forward slashes.

Reply with a fenced ```json block containing only a JSON array of strings, for example:
```json
["{subtree}/<area>/<file>.go", "{subtree}/<area>/<file>_test.go"]
```
"""
    plain = base + "\nUse ordinary search to find every file that must change.\n"
    if arm == "plain":
        return plain
    if arm == "symbol-walk":
        return plain + build_symbol_walk_section(use_index=False)
    if arm == "symbol-index":
        return plain + build_symbol_walk_section(use_index=True)
    if arm != "knowledge-base":
        raise ValueError(f"unknown arm: {arm}")
    return plain + build_knowledge_base_section(knowledge_base_text)


def build_symbol_walk_section(use_index: bool) -> str:
    """Describe the expand-from-seed-files strategy.

    The two arms share every word of the strategy and differ only in how steps
    two and three are carried out. Keeping the wording otherwise identical is
    what lets the comparison attribute any difference to the lookup tool rather
    than to the advice.
    """

    if use_index:
        mechanism = (
            "   This snapshot carries a prebuilt symbol index. Query it with:\n"
            "\n"
            "     python .atom-index/q.py symbols-in <file>      what a file declares\n"
            "     python .atom-index/q.py neighbours <file>      files using what it declares\n"
            "     python .atom-index/q.py who-uses <symbol>      files mentioning a symbol\n"
            "     python .atom-index/q.py where-defined <symbol> where a symbol is declared\n"
            "\n"
            "   `neighbours` does steps 2 and 3 in one command and ranks results by how\n"
            "   many symbols are shared. It understands Go visibility, so a package-private\n"
            "   name in another package is correctly treated as a different symbol.\n"
            "   The index is a navigational aid built by name matching, not proof: treat\n"
            "   its output as leads to confirm by reading the files.\n"
            "   `.atom-index/` is tooling, not repository source. Never report it as an answer.\n"
        )
    else:
        mechanism = (
            "   Open each file you have found and read the names it declares -- types,\n"
            "   functions, methods. Then search for those names to find the files that\n"
            "   use them.\n"
        )

    return (
        "\nHow to search:\n"
        "Do not stop at the files that match the words of the request. Work outward:\n"
        "\n"
        " 1. Search for files that look involved, using the words in the request.\n"
        " 2. For each one, find out what it declares.\n"
        " 3. Find the files that use those declarations, and judge whether they must change too.\n"
        " 4. Repeat on anything new you find, until you stop finding new files.\n"
        "\n"
        f"{mechanism}"
        "\nFiles that must change often do not contain the words of the request anywhere.\n"
        "They are reached only by following the names declared in the files that do.\n"
    )


def build_knowledge_base_section(knowledge_base_text: str) -> str:
    """Append neutral background context without changing the base task."""

    return (
        "\nRepository knowledge base:" "\n"
        "The document below is background knowledge about this repository, gathered from an older state of the code and its history.\n"
        "It is not an answer key and does not mention this repair. It describes areas rather than files, though a few central files are named in passing.\n"
        "Still search the snapshot yourself. Use the document only to decide where to look.\n\n"
        "--- BEGIN KNOWLEDGE BASE ---\n"
        f"{knowledge_base_text.rstrip()}\n"
        "--- END KNOWLEDGE BASE ---\n"
    )


def copilot_command(model: str) -> list[str]:
    """Build the Copilot command, resolving package shims with `shutil.which()`."""

    command = ["copilot", "--silent", "--model", model, "--no-custom-instructions", "--disable-builtin-mcps"]
    resolved = shutil.which(command[0])
    if resolved is not None:
        command[0] = resolved
    return command


def normalise_timeout_stream(stream: bytes | str | None) -> str:
    """Present timeout-carried output as text."""

    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", errors="replace")
    return stream


def kill_process_tree(process: subprocess.Popen) -> str:
    """Kill a timed-out Copilot call's whole process tree."""

    if os.name == "nt":
        killed = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if killed.returncode == 0:
            return "killed the process tree"
        process.kill()
        return f"taskkill exited {killed.returncode}; killed the direct process only"
    try:
        os.killpg(process.pid, 9)
        return "killed the process group"
    except Exception as error:  # pragma: no cover - this host is usually not POSIX.
        process.kill()
        return f"could not signal process group ({error}); killed the direct process only"


def run_one_call(model: str, prompt: str, cwd: Path, timeout_seconds: float) -> InvocationResult:
    """Invoke Copilot once with the prompt on stdin and `cwd` at the snapshot."""

    command = copilot_command(model)
    started = time.perf_counter()
    platform_options: dict[str, object] = {}
    if os.name != "nt":
        platform_options["start_new_session"] = True

    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            **platform_options,
        )
    except (FileNotFoundError, NotADirectoryError) as error:
        return InvocationResult("", f"could not start Copilot CLI: {error}", None, False, time.perf_counter() - started)

    timed_out = False
    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout_seconds)
        exit_code = process.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        detail = kill_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=DRAIN_GRACE_SECONDS)
        except subprocess.TimeoutExpired as drain_expired:
            stdout = normalise_timeout_stream(drain_expired.stdout)
            stderr = normalise_timeout_stream(drain_expired.stderr)
            suffix = f"{detail}; stopped waiting for output after {DRAIN_GRACE_SECONDS:g}s"
            stderr = f"{stderr}\n{suffix}" if stderr else suffix
        exit_code = -1

    return InvocationResult(stdout or "", stderr or "", exit_code, timed_out, time.perf_counter() - started)


def raw_path_for(raw_dir: Path, sha8: str, arm: str, trial: int) -> Path:
    """Return the required raw-reply path."""

    return raw_dir / f"{sha8}__{arm}__{trial:02d}.txt"


def raw_reply_is_complete(path: Path) -> bool:
    """Return true when a previous run left a non-empty raw reply."""

    return path.is_file() and path.stat().st_size > 0


def stderr_path_for(raw_path: Path) -> Path:
    """Return the sidecar path used for stderr from the same trial."""

    return raw_path.with_suffix(".stderr.txt")


def paths_from_json(value: object, subtree: str, snapshot_dir: Path) -> tuple[str, ...] | None:
    """Accept only a JSON array of strings."""

    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return unique_paths(normalise_repo_path(item, subtree, snapshot_dir) for item in value)


def parse_fenced_json(reply: str, subtree: str, snapshot_dir: Path) -> ParsedReply | None:
    """Prefer the requested fenced JSON block."""

    for match in re.finditer(r"```(?:json)?\s*(.*?)```", reply, flags=re.IGNORECASE | re.DOTALL):
        try:
            parsed = json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue
        paths = paths_from_json(parsed, subtree, snapshot_dir)
        if paths is not None:
            return ParsedReply(True, paths, parser="fenced-json")
    return None


def parse_bracketed_json(reply: str, subtree: str, snapshot_dir: Path) -> ParsedReply | None:
    """Try any bare bracketed JSON array."""

    starts = [index for index, char in enumerate(reply) if char == "["]
    ends = [index for index, char in enumerate(reply) if char == "]"]
    for start in starts:
        for end in reversed(ends):
            if end <= start:
                continue
            try:
                parsed = json.loads(reply[start : end + 1])
            except json.JSONDecodeError:
                continue
            paths = paths_from_json(parsed, subtree, snapshot_dir)
            if paths is not None:
                return ParsedReply(True, paths, parser="bare-json-array")
    return None


def clean_line_path(line: str) -> str:
    """Remove bullets, numbering, quotes, and trailing punctuation."""

    cleaned = line.strip()
    cleaned = re.sub(r"^[-*•]\s+", "", cleaned)
    cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned)
    return cleaned.strip().rstrip(",;").strip().strip("`'\"")


def parse_line_paths(reply: str, subtree: str, snapshot_dir: Path) -> ParsedReply | None:
    """Fallback for one-path-per-line replies."""

    candidates: list[str] = []
    for raw_line in reply.splitlines():
        line = clean_line_path(raw_line)
        if not line or line.startswith("```"):
            continue
        if PATHLIKE_LINE.search(line):
            candidates.append(normalise_repo_path(line, subtree, snapshot_dir))
    paths = unique_paths(candidates)
    if not paths:
        return None
    return ParsedReply(True, paths, parser="line-paths")


def parse_reply(reply: str, subtree: str, snapshot_dir: Path) -> ParsedReply:
    """Parse a reply in the required tolerant order."""

    if not reply.strip():
        return ParsedReply(False, reason="empty reply")
    for parser in (parse_fenced_json, parse_bracketed_json, parse_line_paths):
        parsed = parser(reply, subtree, snapshot_dir)
        if parsed is not None:
            return parsed
    return ParsedReply(False, reason="no JSON array or path-like lines found")

def score_prediction(
    case: GroundTruthCase,
    arm: str,
    trial: int,
    raw_path: Path,
    parsed: ParsedReply,
    invocation: InvocationResult | None = None,
) -> ScoredRun:
    """Compute recall, precision, and missed files for one trial."""

    truth = set(case.truth_files)
    if not parsed.readable:
        return ScoredRun(
            case.sha8,
            arm,
            trial,
            str(raw_path),
            False,
            parsed.reason,
            parsed.parser,
            (),
            tuple(sorted(truth)),
            tuple(sorted(truth)),
            None,
            None,
            invocation.seconds if invocation else None,
            invocation.exit_code if invocation else None,
            invocation.timed_out if invocation else False,
        )

    predicted = set(parsed.paths)
    hits = predicted & truth
    recall = len(hits) / len(truth) if truth else 1.0
    precision = len(hits) / len(predicted) if predicted else 0.0
    return ScoredRun(
        case.sha8,
        arm,
        trial,
        str(raw_path),
        True,
        "",
        parsed.parser,
        tuple(sorted(predicted)),
        tuple(sorted(truth)),
        tuple(sorted(truth - predicted)),
        recall,
        precision,
        invocation.seconds if invocation else None,
        invocation.exit_code if invocation else None,
        invocation.timed_out if invocation else False,
    )


def mean_or_none(values: Sequence[float]) -> float | None:
    """Return a mean, or None when no readable trials exist."""

    return statistics.mean(values) if values else None


def spread(values: Sequence[float]) -> dict[str, object]:
    """Expose spread as endpoints plus raw values."""

    if not values:
        return {"min": None, "max": None, "values": []}
    return {"min": min(values), "max": max(values), "values": list(values)}


def blast_radius_bucket(truth_size: int) -> str:
    """Map truth-file count to the mandatory size stratum."""

    if truth_size <= 4:
        return "small"
    if truth_size <= 14:
        return "medium"
    return "large"


def summarise(cases: Sequence[GroundTruthCase], runs: Sequence[ScoredRun], arms: Sequence[str]) -> dict:
    """Build the JSON report requested by the brief."""

    runs_by_commit_arm: dict[tuple[str, str], list[ScoredRun]] = defaultdict(list)
    for run in runs:
        runs_by_commit_arm[(run.sha8, run.arm)].append(run)

    unreadable_counts = {arm: 0 for arm in arms}
    for run in runs:
        if not run.readable:
            unreadable_counts[run.arm] = unreadable_counts.get(run.arm, 0) + 1

    per_commit: dict[str, dict] = {}
    per_commit_means: dict[str, list[float]] = {arm: [] for arm in arms}
    stratified: dict[str, dict[str, list[float]]] = {
        bucket: {arm: [] for arm in arms} for bucket in ("small", "medium", "large")
    }

    for case in cases:
        bucket = blast_radius_bucket(len(case.truth_files))
        entry = {
            "request": case.request,
            "truth_size": len(case.truth_files),
            "blast_radius_bucket": bucket,
            "truth_files": list(case.truth_files),
            "excluded_files_ignored_by_scoring": list(case.excluded_files),
            "arms": {},
        }
        for arm in arms:
            arm_runs = sorted(runs_by_commit_arm.get((case.sha8, arm), []), key=lambda item: item.trial)
            readable = [run for run in arm_runs if run.readable]
            recall_values = [float(run.recall) for run in readable if run.recall is not None]
            precision_values = [float(run.precision) for run in readable if run.precision is not None]
            recall_mean = mean_or_none(recall_values)
            precision_mean = mean_or_none(precision_values)
            if recall_mean is not None:
                per_commit_means[arm].append(recall_mean)
                stratified[bucket][arm].append(recall_mean)

            entry["arms"][arm] = {
                "readable_trials": len(readable),
                "unreadable_trials": len(arm_runs) - len(readable),
                "mean_recall": recall_mean,
                "recall_spread": spread(recall_values),
                "mean_precision": precision_mean,
                "precision_spread": spread(precision_values),
                "missed_by_trial": [
                    {
                        "trial": run.trial,
                        "readable": run.readable,
                        "missed": list(run.missed),
                        "parse_reason": run.parse_reason,
                    }
                    for run in arm_runs
                ],
                "missed_in_every_readable_trial": sorted(
                    set.intersection(*(set(run.missed) for run in readable)) if readable else set(case.truth_files)
                ),
            }
        per_commit[case.sha8] = entry

    return {
        "metadata": {
            "runs_scored": len(runs),
            "commit_count": len(cases),
            "arms": list(arms),
            "note": "Excluded files are ignored: they are neither credited nor penalised.",
        },
        "per_commit": per_commit,
        "overall_mean_recall_by_arm": {arm: mean_or_none(per_commit_means[arm]) for arm in arms},
        "recall_stratified_by_blast_radius_size": {
            bucket: {arm: mean_or_none(values) for arm, values in arm_values.items()}
            for bucket, arm_values in stratified.items()
        },
        "unreadable_reply_counts_by_arm": unreadable_counts,
    }


def format_optional(value: float | None) -> str:
    """Format optional metrics without turning missing data into zero."""

    return "n/a" if value is None else f"{value:.3f}"


def print_report(summary: dict) -> None:
    """Print a compact report; full details are written to JSON."""

    print("\nPER-COMMIT MEANS")
    print("sha8      arm             recall mean/spread        precision mean/spread")
    for sha8, entry in summary["per_commit"].items():
        for arm, arm_entry in entry["arms"].items():
            recall = arm_entry["mean_recall"]
            precision = arm_entry["mean_precision"]
            recall_spread = arm_entry["recall_spread"]
            precision_spread = arm_entry["precision_spread"]
            print(
                f"{sha8:<9} {arm:<15} "
                f"{format_optional(recall):>6} [{format_optional(recall_spread['min'])}, {format_optional(recall_spread['max'])}]   "
                f"{format_optional(precision):>6} [{format_optional(precision_spread['min'])}, {format_optional(precision_spread['max'])}]"
            )

    print("\nOVERALL MEAN RECALL BY ARM")
    for arm, value in summary["overall_mean_recall_by_arm"].items():
        print(f"  {arm}: {format_optional(value)}")

    print("\nRECALL STRATIFIED BY BLAST-RADIUS SIZE")
    for bucket, values in summary["recall_stratified_by_blast_radius_size"].items():
        print("  " + bucket + ": " + ", ".join(f"{arm}={format_optional(value)}" for arm, value in values.items()))

    print("\nUNREADABLE REPLIES BY ARM")
    for arm, count in summary["unreadable_reply_counts_by_arm"].items():
        print(f"  {arm}: {count}")


def parse_csv_set(text: str) -> set[str] | None:
    """Parse an optional comma-separated selector."""

    values = {part.strip() for part in text.split(",") if part.strip()}
    return values or None


def parse_arms(text: str) -> tuple[str, ...]:
    """Parse the comma-separated arm list."""

    arms = tuple(part.strip() for part in text.split(",") if part.strip())
    invalid = [arm for arm in arms if arm not in VALID_ARMS]
    if invalid:
        raise SystemExit(f"Unknown arm(s): {', '.join(invalid)}. Valid arms: {', '.join(VALID_ARMS)}")
    if not arms:
        raise SystemExit("At least one arm is required")
    return arms


def execute_work_item(
    work_item: WorkItem,
    config: ExperimentConfig,
    model: str,
    timeout_seconds: float,
    force: bool,
) -> TrialOutcome:
    """Run or resume one repair-arm-trial unit.

    Resume is the default: a non-empty raw reply file is durable evidence. The
    driver re-scores it exactly as written and never makes another call for that
    trial unless `--force` is supplied.
    """

    raw_path = raw_path_for(config.paths.raw_dir, work_item.case.sha8, work_item.arm, work_item.trial)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    if not force and raw_reply_is_complete(raw_path):
        reply = raw_path.read_text(encoding="utf-8")
        parsed = parse_reply(reply, config.subtree, work_item.snapshot)
        scored = score_prediction(work_item.case, work_item.arm, work_item.trial, raw_path, parsed)
        return TrialOutcome(scored=scored, skipped_existing_raw=True)

    prompt = build_prompt(work_item.case.request, work_item.arm, config.subtree, config.knowledge_base_text)
    invocation = run_one_call(model, prompt, work_item.snapshot, timeout_seconds)

    # The raw reply is the durable evidence. Save before parsing so an
    # interrupted run can later re-score exactly what the model returned.
    raw_path.write_text(invocation.stdout, encoding="utf-8")
    stderr_path = stderr_path_for(raw_path)
    if invocation.stderr.strip():
        stderr_path.write_text(invocation.stderr, encoding="utf-8")
    elif stderr_path.exists():
        stderr_path.unlink()

    parsed = parse_reply(invocation.stdout, config.subtree, work_item.snapshot)
    scored = score_prediction(work_item.case, work_item.arm, work_item.trial, raw_path, parsed, invocation)
    return TrialOutcome(scored=scored, skipped_existing_raw=False)

def run_failed(scored: ScoredRun) -> bool:
    """Return true for the failures that should be visible and counted."""

    exit_failed = scored.exit_code is not None and scored.exit_code != 0
    return exit_failed or scored.timed_out or not scored.readable


def describe_failure(scored: ScoredRun) -> str:
    """Create a compact human-readable failure line."""

    reasons: list[str] = []
    if scored.exit_code is not None and scored.exit_code != 0:
        reasons.append(f"exit={scored.exit_code}")
    if scored.timed_out:
        reasons.append("timeout")
    if not scored.readable:
        reasons.append(f"unreadable={scored.parse_reason}")
    return ", ".join(reasons) if reasons else "ok"


def format_progress_line(index: int, total: int, outcome: TrialOutcome) -> str:
    """Build the one-line progress message for a completed work item."""

    scored = outcome.scored
    prefix = "FAIL " if run_failed(scored) else "     "
    source = "resume" if outcome.skipped_existing_raw else "call"
    status = (
        "unreadable: " + scored.parse_reason
        if not scored.readable
        else f"recall={scored.recall:.3f} precision={scored.precision:.3f}"
    )
    exit_text = "n/a" if scored.exit_code is None else str(scored.exit_code)
    seconds_text = "n/a" if scored.seconds is None else f"{scored.seconds:.1f}s"
    timeout_note = " timeout" if scored.timed_out else ""
    return (
        f"{prefix}[{index}/{total}] {scored.sha8} {scored.arm:<15} trial {scored.trial:02d} "
        f"{source:<6} exit={exit_text} {seconds_text}{timeout_note} {status}"
    )


def write_incremental_results(
    cases: Sequence[GroundTruthCase],
    scored_runs: Sequence[ScoredRun],
    arms: Sequence[str],
    results_path: Path,
) -> dict:
    """Write the current partial report atomically enough for interruption."""

    summary = summarise(cases, scored_runs, arms)
    temporary_path = results_path.with_suffix(".json.writing")
    temporary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    temporary_path.replace(results_path)
    return summary


def submit_next_work(
    pool: concurrent.futures.ThreadPoolExecutor,
    jobs: list[WorkItem],
    next_index: int,
    pending: dict[concurrent.futures.Future[TrialOutcome], WorkItem],
    config: ExperimentConfig,
    model: str,
    timeout_seconds: float,
    force: bool,
) -> int:
    """Submit one more job if any remain, returning the next unsent index."""

    if next_index >= len(jobs):
        return next_index
    work_item = jobs[next_index]
    future = pool.submit(execute_work_item, work_item, config, model, timeout_seconds, force)
    pending[future] = work_item
    return next_index + 1


def read_knowledge_base(path: Path) -> str:
    """Read the required background document."""

    if not path.is_file():
        raise SystemExit(f"--knowledge-base must be an existing file: {path}")
    return path.read_text(encoding="utf-8")


def build_config(arguments: argparse.Namespace) -> ExperimentConfig:
    """Create path and prompt configuration from CLI arguments."""

    paths = ExperimentPaths(
        ground_truth=arguments.ground_truth,
        source_repo=arguments.source_repo,
        snapshot_root=arguments.snapshot_root,
        knowledge_base=arguments.knowledge_base,
        out=arguments.out,
    )
    return ExperimentConfig(
        paths=paths,
        subtree=normalise_subtree(arguments.subtree),
        knowledge_base_text=read_knowledge_base(paths.knowledge_base),
    )


def run_dry_run(cases: Sequence[GroundTruthCase], arms: Sequence[str], config: ExperimentConfig) -> int:
    """Print prompt sizes and selected cases without creating snapshots or calls."""

    print(f"dry-run: {len(cases)} case(s)")
    print("cases: " + ", ".join(case.sha8 for case in cases))
    sample_case = cases[0]
    for arm in arms:
        prompt = build_prompt(sample_case.request, arm, config.subtree, config.knowledge_base_text)
        byte_count = len(prompt.encode("utf-8"))
        print(f"prompt bytes [{arm}]: {byte_count}")
        print(f"prompt chars [{arm}]: {len(prompt)}")
    print("no agent calls made")
    return 0


def run_experiment(arguments: argparse.Namespace) -> int:
    """Run snapshots, optional calls, scoring, and reporting."""

    config = build_config(arguments)
    selected = parse_csv_set(arguments.cases)
    cases = load_ground_truth(config.paths.ground_truth, config.subtree, selected)
    arms = parse_arms(arguments.arms)
    io_lock = threading.Lock()

    if arguments.dry_run:
        return run_dry_run(cases, arms, config)

    if arguments.snapshot_only:
        for case in cases:
            snapshot = ensure_snapshot(case, config)
            print(f"snapshot ready: {case.sha8} -> {snapshot}")
        print("snapshot-only complete; no Copilot CLI calls made")
        return 0

    config.paths.out.mkdir(parents=True, exist_ok=True)
    config.paths.raw_dir.mkdir(parents=True, exist_ok=True)

    # Serial setup happens before the pool starts. Exporting the same snapshot
    # concurrently could corrupt the directory and quietly bias both arms.
    snapshots: dict[str, Path] = {}
    for case in cases:
        snapshots[case.sha8] = ensure_snapshot(case, config)
    print(f"setup complete: {len(snapshots)} snapshots", flush=True)

    # Arms that need the symbol index run against a separate, pre-built copy of
    # each snapshot. Those copies are made outside this driver; we only verify
    # they are present, because silently falling back to an unindexed snapshot
    # would produce a result that looks valid and means nothing.
    indexed_root = (
        Path(arguments.indexed_snapshot_root) if arguments.indexed_snapshot_root else None
    )
    indexed_arms = [arm for arm in arms if arm in ARMS_WITH_INDEX]
    if indexed_arms:
        if indexed_root is None:
            raise SystemExit(
                f"arms {indexed_arms} need --indexed-snapshot-root"
            )
        for case in cases:
            index_file = indexed_root / case.sha8 / ".atom-index" / "index.json"
            if not index_file.exists():
                raise SystemExit(f"missing symbol index: {index_file}")
        print(f"indexed snapshots verified: {len(cases)} under {indexed_root}", flush=True)

    def snapshot_for(case: GroundTruthCase, arm: str) -> Path:
        """Return the snapshot an arm must run in."""

        if arm in ARMS_WITH_INDEX:
            return indexed_root / case.sha8  # type: ignore[union-attr]
        return snapshots[case.sha8]

    jobs = [
        WorkItem(case=case, arm=arm, trial=trial, snapshot=snapshot_for(case, arm))
        for case in cases
        for arm in arms
        for trial in range(1, arguments.trials + 1)
    ]
    total_jobs = len(jobs)
    scored_runs: list[ScoredRun] = []
    failures: list[ScoredRun] = []
    skipped_existing = 0
    completed = 0
    consecutive_failures = 0
    aborted = False

    max_workers = max(1, arguments.workers)
    next_job_index = 0
    pending: dict[concurrent.futures.Future[TrialOutcome], WorkItem] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for _ in range(min(max_workers, total_jobs)):
            next_job_index = submit_next_work(
                pool,
                jobs,
                next_job_index,
                pending,
                config,
                arguments.model,
                arguments.timeout_seconds,
                arguments.force,
            )

        while pending:
            done, _not_done = concurrent.futures.wait(
                pending,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            for future in done:
                work_item = pending.pop(future)
                completed += 1
                try:
                    outcome = future.result()
                except Exception as error:
                    # Unexpected worker failures are converted into scored
                    # failures so a single bad unit does not discard prior work.
                    raw_path = raw_path_for(config.paths.raw_dir, work_item.case.sha8, work_item.arm, work_item.trial)
                    parsed = ParsedReply(False, reason=f"worker exception: {error}")
                    scored = score_prediction(work_item.case, work_item.arm, work_item.trial, raw_path, parsed)
                    outcome = TrialOutcome(scored=scored, skipped_existing_raw=False)

                scored_runs.append(outcome.scored)
                if outcome.skipped_existing_raw:
                    skipped_existing += 1

                failed = run_failed(outcome.scored)
                if failed:
                    failures.append(outcome.scored)
                    consecutive_failures += 1
                else:
                    consecutive_failures = 0

                with io_lock:
                    print(format_progress_line(completed, total_jobs, outcome), flush=True)
                    write_incremental_results(cases, scored_runs, arms, config.paths.results_path)

                if consecutive_failures > MAX_CONSECUTIVE_FAILURES:
                    aborted = True
                    with io_lock:
                        print(
                            f"\nABORTING: more than {MAX_CONSECUTIVE_FAILURES} consecutive calls failed. "
                            "This suggests a systemic problem such as auth expiry or rate limiting.",
                            flush=True,
                        )
                    for pending_future in pending:
                        pending_future.cancel()
                    break

                if not aborted:
                    next_job_index = submit_next_work(
                        pool,
                        jobs,
                        next_job_index,
                        pending,
                        config,
                        arguments.model,
                        arguments.timeout_seconds,
                        arguments.force,
                    )
            if aborted:
                break

    summary = summarise(cases, scored_runs, arms)
    with io_lock:
        print_report(summary)
        write_incremental_results(cases, scored_runs, arms, config.paths.results_path)

        print("\nFAILURES")
        if not failures:
            print("  none")
        else:
            for scored in failures:
                print(f"  {scored.sha8} {scored.arm} trial {scored.trial:02d}: {describe_failure(scored)}")

        print(f"\nskipped existing raw replies: {skipped_existing}")
        if aborted:
            print("run stopped early after systemic failure guard tripped")
    print(f"\nresults: {config.paths.results_path}")
    print(f"raw replies: {config.paths.raw_dir}")
    return 2 if aborted else 0


def existing_dir(value: str) -> Path:
    """Argparse converter for required directories."""

    path = Path(value)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"directory does not exist: {value}")
    return path


def path_value(value: str) -> Path:
    """Argparse converter that keeps required paths explicit."""

    return Path(value)


def build_arg_parser() -> argparse.ArgumentParser:
    """Define the promised command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", type=existing_dir, required=True, help="Directory of ground-truth JSON files")
    parser.add_argument("--source-repo", type=existing_dir, required=True, help="Repository to take snapshots from")
    parser.add_argument("--snapshot-root", type=path_value, required=True, help="Scratch directory for snapshots")
    parser.add_argument(
        "--indexed-snapshot-root",
        type=path_value,
        default=None,
        help="Directory of pre-built snapshot copies carrying .atom-index/ (required by the symbol-index arm)",
    )
    parser.add_argument("--subtree", required=True, help="Repo-relative subtree to export and score")
    parser.add_argument("--knowledge-base", type=path_value, required=True, help="Markdown knowledge document")
    parser.add_argument("--out", type=path_value, required=True, help="Directory for raw replies and results.json")
    parser.add_argument("--trials", "--runs", dest="trials", type=int, default=DEFAULT_TRIALS, help="Independent trials per case per arm (default: 5)")
    parser.add_argument("--arms", default=",".join(VALID_ARMS), help="Comma-separated arms to run (default: both)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Copilot model id for both arms (default: {DEFAULT_MODEL})")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help=f"Concurrent subprocess calls (default: {DEFAULT_WORKERS})")
    parser.add_argument("--cases", default="", help="Optional comma-separated sha8 subset")
    parser.add_argument("--resume", action="store_true", help="Resume from non-empty parseable raw replies (default behaviour)")
    parser.add_argument("--force", action="store_true", help="Ignore existing raw replies and call every trial again")
    parser.add_argument("--dry-run", action="store_true", help="Load inputs and print prompt sizes without making calls")
    parser.add_argument("--snapshot-only", action="store_true", help="Build snapshots without making Copilot CLI calls")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"Copilot CLI timeout per trial (default: {DEFAULT_TIMEOUT_SECONDS:g})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""

    arguments = build_arg_parser().parse_args(argv)
    if arguments.trials < 1:
        raise SystemExit("--trials must be at least 1")
    if arguments.workers < 1:
        raise SystemExit("--workers must be at least 1")
    return run_experiment(arguments)


if __name__ == "__main__":
    raise SystemExit(main())


