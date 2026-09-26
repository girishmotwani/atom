"""Spike A: can a model turn a vague problem document into a falsifiable question?

`atom poc new` currently demands a falsifiable POC question as input -- the
hardest artifact in the whole method -- before it will scaffold anything. The
proposal is to interview the developer instead, read a problem document, and
have a model propose the question.

That is only worth building if the proposed questions are genuinely falsifiable.
A question that merely *reads* well is worse than no help at all: every
downstream artifact inherits it, and nobody notices until the spike that was
supposed to settle something settles nothing.

    Question: Can a model reliably convert a vague problem statement into a
              falsifiable POC question -- and can the tool detect when it has
              not?

EXIT CODES
    0  Confirmed    -- the pass rate met the pre-registered bar
    1  Refuted      -- it did not
    2  Inconclusive -- not enough usable replies to say

HONESTY NOTE
    The thresholds and the rubric below were written before any model was
    called. They are not adjustable after seeing the output -- that is the
    entire point of writing them here first. The verbatim replies are printed
    and saved so the developer can overrule the mechanical score, which is a
    proxy for falsifiability rather than a measurement of it.

    Re-score saved replies without spending credits:  python spike.py --analyse
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from atom.runner import SubprocessRunner  # noqa: E402

# ---------------------------------------------------------------------------
# Pre-registered experiment design. Not to be edited after the first run.
# ---------------------------------------------------------------------------

MODEL = "gpt-5.4"

# Three runs per document, because one sample cannot distinguish a model that
# reliably produces good questions from one that got lucky once. Atom's review
# command uses repetition as its confidence signal for the same reason.
RUNS_PER_DOCUMENT = 3

# Confirmed needs four questions in five to be usable. The developer approves
# the brief at a gate, so the tool need not be perfect -- but a bar below this
# makes the feature a coin toss dressed up as assistance.
CONFIRMED_PASS_RATE = 0.80

# Below half, the developer spends more effort repairing questions than writing
# them, which is worse than the blank page this feature exists to fix.
REFUTED_PASS_RATE = 0.50

# Deliberately vague, in the register real problem statements arrive in. None
# of them contains a falsifiable question; producing one is the work.
DOCUMENTS: dict[str, str] = {
    "echo-service": """
        We need an HTTP service that echoes request bodies back to the caller.
        It should be fast and shouldn't fall over when people send big payloads.
        Some clients stream, some don't.
    """,
    "event-bus": """
        Our services talk through a shared event bus. We want topic-based
        routing so a publisher can send to a topic and only interested
        subscribers wake up. Needs to keep up with our traffic.
    """,
    "config-reload": """
        Restarting to pick up config changes is painful in production. We'd
        like the service to notice when its config file changes and apply the
        new values without dropping in-flight requests.
    """,
    "cache-layer": """
        Database reads are hammering us during peak. A caching layer in front
        would help. It has to not serve stale data in a way that breaks
        correctness, whatever that means for our workload.
    """,
    "batch-importer": """
        Customers upload CSV files that we import into the system. Files are
        getting bigger and the import sometimes times out. We want it to handle
        much larger files reliably.
    """,
}

PROMPT_TEMPLATE = """You are helping scope a proof-of-concept spike for a Go project.

Here is a problem statement:

{document}

Propose exactly ONE proof-of-concept question that a throwaway Go program could
answer. The question must be falsifiable: there must be a concrete observation
that would answer it "no".

Reply with only a JSON object, no prose and no code fence:

{{"question": "...", "refuted_when": "...", "program_sketch": "..."}}

- "question": one sentence, one subject, answerable by running a program.
- "refuted_when": the specific observation that would answer the question no.
- "program_sketch": one sentence on what the program does.
"""

# ---------------------------------------------------------------------------
# The rubric. Four binary checks, all of which must pass.
#
# These are proxies. Falsifiability is a property of meaning, and no regular
# expression measures meaning. They catch the failure modes that are
# mechanically visible and make the score reproducible; the verbatim output is
# printed so a human can disagree with any individual verdict.
# ---------------------------------------------------------------------------

# A question opening this way asks for a preference. No observation refutes
# "should we use X" -- it is settled by argument, not by running anything.
_PREFERENCE_OPENINGS = re.compile(
    r"^\s*(should|which|would|is it better|what is the best|how best|do we want)\b",
    re.IGNORECASE,
)

# Words signalling that something observable happened, rather than something
# being judged good.
_OBSERVABLE = re.compile(
    r"\b(\d+|return|returns|exceed|exceeds|below|above|within|under|over|"
    r"complete|completes|fail|fails|drop|drops|lose|loses|match|matches|"
    r"grow|grows|stay|stays|remain|remains|handle|handles|serve|serves)\b",
    re.IGNORECASE,
)

# Judgement words no program can observe.
_SUBJECTIVE = re.compile(
    r"\b(good|clean|elegant|ergonomic|readable|maintainable|nice|better|"
    r"appropriate|suitable|reasonable)\b",
    re.IGNORECASE,
)


def is_single_subject(question: str) -> bool:
    """Whether the question asks about one thing.

    A compound question cannot report which half failed, so refuting it tells
    the developer nothing actionable.
    """

    if ";" in question:
        return False
    # "and" inside a noun phrase ("read and write") is fine; "and" joining two
    # clauses is not. A verb-led clause after "and" is the signal.
    parts = re.split(r"\band\b", question, flags=re.IGNORECASE)
    if len(parts) == 1:
        return True
    return not re.search(r"\b(does|can|will|is|are|do)\b", parts[1], re.IGNORECASE)


def has_refuting_observation(question: str, refuted_when: str) -> bool:
    """Whether a distinct, non-empty refuting observation was supplied.

    A "refuted_when" that merely negates the question restates it rather than
    grounding it, and is not evidence the model found an observation.
    """

    stripped = refuted_when.strip()
    if len(stripped) < 15:
        return False
    return _content_words(stripped) != _content_words(question)


def is_not_a_preference(question: str) -> bool:
    """Whether the question is about behaviour rather than about a choice."""

    return not _PREFERENCE_OPENINGS.search(question)


def is_mechanically_checkable(question: str) -> bool:
    """Whether the question names something a program could observe."""

    if _SUBJECTIVE.search(question):
        return False
    return bool(_OBSERVABLE.search(question))


RUBRIC = {
    "single_subject": lambda q, r: is_single_subject(q),
    "refuting_observation": has_refuting_observation,
    "not_a_preference": lambda q, r: is_not_a_preference(q),
    "mechanically_checkable": lambda q, r: is_mechanically_checkable(q),
}

_STOP_WORDS = {
    "a", "an", "the", "is", "are", "does", "do", "can", "will", "of", "to",
    "in", "on", "for", "with", "without", "that", "this", "it", "its", "and",
    "or", "be", "been", "when", "than", "then", "at", "by", "from", "as",
}


def _content_words(text: str) -> frozenset[str]:
    """Lowercased words with filler removed, for comparing two sentences."""

    words = re.findall(r"[a-zA-Z]+", text.lower())
    return frozenset(w for w in words if w not in _STOP_WORDS and len(w) > 2)


def stability(questions: list[str]) -> float:
    """Mean pairwise word overlap between the questions for one document.

    Low overlap means the model picked a different risk each time, which makes
    the proposal a coin toss even when each individual question is sound.
    """

    pairs = [
        (questions[i], questions[j])
        for i in range(len(questions))
        for j in range(i + 1, len(questions))
    ]
    if not pairs:
        return 0.0

    scores = []
    for first, second in pairs:
        left, right = _content_words(first), _content_words(second)
        union = left | right
        scores.append(len(left & right) / len(union) if union else 0.0)
    return sum(scores) / len(scores)


# ---------------------------------------------------------------------------
# Calling the model
# ---------------------------------------------------------------------------

RAW_DIRECTORY = Path(__file__).parent / "raw"
RESULTS_PATH = Path(__file__).parent / "results.json"


def build_command() -> tuple[str, ...]:
    """The same flags Atom's review path uses, for the same reasons.

    The prompt is piped on stdin rather than passed with `-p`, because argv has
    a hard ceiling on Windows that surfaces as an ordinary non-zero exit.
    """

    return (
        "copilot",
        "--silent",
        "--model",
        MODEL,
        "--no-custom-instructions",
        "--disable-builtin-mcps",
    )


def call_model(name: str, document: str, run_index: int) -> dict:
    """Ask once, and record what came back whether or not it parsed."""

    prompt = PROMPT_TEMPLATE.format(document=document.strip())
    started = time.monotonic()

    result = SubprocessRunner().run(
        build_command(),
        Path(__file__).parent,
        timeout_seconds=180.0,
        stdin_text=prompt,
    )

    # Save before anything can fail. A model call costs real credits, so a bug
    # in the scoring code below must never be able to discard a paid-for reply.
    RAW_DIRECTORY.mkdir(exist_ok=True)
    (RAW_DIRECTORY / f"{name}__run{run_index}.txt").write_text(
        result.stdout or result.stderr, encoding="utf-8"
    )

    # `succeeded` is the runner's own contract: the process both ran to
    # completion *and* exited zero. COMPLETED alone only means it ran.
    return {
        "document": name,
        "run_index": run_index,
        "outcome": result.outcome.name,
        "exit_code": result.exit_code,
        "duration_seconds": round(time.monotonic() - started, 1),
        "reply": result.stdout,
        "detail": "" if result.succeeded else result.stderr,
    }


def parse_reply(reply: str) -> dict | None:
    """Pull the JSON object out of a reply that may be wrapped in prose."""

    if not reply.strip():
        return None
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) and "question" in parsed else None


# ---------------------------------------------------------------------------
# Scoring and reporting
# ---------------------------------------------------------------------------


def score(records: list[dict]) -> dict:
    """Apply the pre-registered rubric to every usable reply."""

    graded: list[dict] = []
    unusable = 0

    for record in records:
        parsed = parse_reply(record.get("reply", ""))
        if parsed is None:
            unusable += 1
            continue

        question = str(parsed.get("question", ""))
        refuted_when = str(parsed.get("refuted_when", ""))
        checks = {name: bool(check(question, refuted_when)) for name, check in RUBRIC.items()}

        graded.append(
            {
                "document": record["document"],
                "run_index": record["run_index"],
                "question": question,
                "refuted_when": refuted_when,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    by_document: dict[str, list[str]] = {}
    for item in graded:
        by_document.setdefault(item["document"], []).append(item["question"])

    passed = sum(1 for item in graded if item["passed"])
    return {
        "model": MODEL,
        "requested": len(DOCUMENTS) * RUNS_PER_DOCUMENT,
        "usable": len(graded),
        "unusable": unusable,
        "passed": passed,
        "pass_rate": (passed / len(graded)) if graded else 0.0,
        "stability": {name: round(stability(qs), 2) for name, qs in by_document.items()},
        "graded": graded,
    }


def report(summary: dict) -> int:
    """Print the evidence, then the verdict derived from it."""

    print(f"model            : {summary['model']}")
    print(f"runs requested   : {summary['requested']}")
    print(f"replies usable   : {summary['usable']}  (unparseable: {summary['unusable']})")
    print()

    for item in summary["graded"]:
        mark = "PASS" if item["passed"] else "FAIL"
        failed = [name for name, ok in item["checks"].items() if not ok]
        print(f"  [{mark}] {item['document']} run {item['run_index']}")
        print(f"         Q: {item['question']}")
        print(f"         R: {item['refuted_when']}")
        if failed:
            print(f"         failed checks: {', '.join(failed)}")
        print()

    print("stability (word overlap across runs, per document):")
    for name, value in summary["stability"].items():
        print(f"  {name:<16} {value}")
    print()

    # The denominator is printed beside the rate, so a shrunken sample cannot
    # masquerade as a clean result.
    rate = summary["pass_rate"]
    print(f"pass rate        : {summary['passed']}/{summary['usable']} = {rate:.0%}")
    print(f"confirmed at     : >= {CONFIRMED_PASS_RATE:.0%}")
    print(f"refuted below    : {REFUTED_PASS_RATE:.0%}")
    print()

    if summary["usable"] < summary["requested"] / 2:
        print("Verdict: Inconclusive -- too few replies parsed to judge the model.")
        return 2
    if rate >= CONFIRMED_PASS_RATE:
        print("Verdict: Confirmed -- questions met the pre-registered bar.")
        return 0
    if rate < REFUTED_PASS_RATE:
        print("Verdict: Refuted -- too many questions were not falsifiable.")
        return 1
    print("Verdict: Inconclusive -- between the two pre-registered thresholds.")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Spike A: falsifiable question generation.")
    parser.add_argument(
        "--analyse",
        action="store_true",
        help="Re-score the saved replies without calling the model.",
    )
    arguments = parser.parse_args()

    if arguments.analyse:
        if not RESULTS_PATH.exists():
            print("No results.json yet -- run the spike first.", file=sys.stderr)
            return 2
        records = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))["records"]
        return report(score(records))

    print(f"Question: Can {MODEL} turn a vague problem statement into a falsifiable question?")
    print(f"Calling {len(DOCUMENTS) * RUNS_PER_DOCUMENT} times...\n")

    jobs = [
        (name, document, run_index)
        for name, document in DOCUMENTS.items()
        for run_index in range(1, RUNS_PER_DOCUMENT + 1)
    ]

    records: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(call_model, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            # One unexpected failure must not discard the other calls, which
            # have already cost credits and are sitting saved in raw/.
            try:
                record = future.result()
            except Exception as error:  # noqa: BLE001 - spike records, never hides
                print(f"  !! call raised: {error!r}")
                continue
            records.append(record)
            print(
                f"  {record['document']} run {record['run_index']}: "
                f"{record['outcome']} in {record['duration_seconds']}s"
            )

    records.sort(key=lambda r: (r["document"], r["run_index"]))
    summary = score(records)

    RESULTS_PATH.write_text(
        json.dumps({"records": records, "summary": summary}, indent=2), encoding="utf-8"
    )
    print(f"\nSaved {RESULTS_PATH}\n")
    return report(summary)


if __name__ == "__main__":
    raise SystemExit(main())
