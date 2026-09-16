"""Break down *how* the salvage step succeeded, which the headline numbers hide.

`locate_json_payload` tries two strategies: strip a markdown fence, or failing that,
scan from the first '[' to the last ']'. Those are not equivalent. Stripping a fence is
deterministic -- the fence is an unambiguous delimiter. Scanning for brackets is a
heuristic that can silently capture the wrong span if the reply contains prose with
brackets in it.

A headline of "100% after salvage" means something quite different depending on which
strategy did the work, so this counts them separately. It also checks whether anything
sits outside the fence, since prose before or after it is the thing that would make a
naive parser fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spike import (  # noqa: E402
    CONTRACTS,
    FENCE_PATTERN,
    MODELS,
    TRIALS_PER_CELL,
    assistant_content_from_envelope,
    raw_path_for,
    validate_findings,
)


def classify(content: str) -> str:
    """Describe how this reply would have to be handled to yield valid findings."""
    stripped = content.strip()

    valid_as_is, _ = validate_findings(stripped or None)
    if valid_as_is:
        return "clean (no salvage needed)"

    fence = FENCE_PATTERN.search(content)
    if fence:
        valid_fenced, _ = validate_findings(fence.group(1).strip())
        if not valid_fenced:
            return "fenced but still invalid"
        # Is the fence the whole reply, or is there prose around it?
        outside = (content[: fence.start()] + content[fence.end() :]).strip()
        if outside:
            return f"fenced + prose outside ({len(outside)} chars)"
        return "fenced only (deterministic strip)"

    start, end = content.find("["), content.rfind("]")
    if start != -1 and end > start:
        valid_scanned, _ = validate_findings(content[start : end + 1])
        if valid_scanned:
            return "bracket scan needed (heuristic)"
    return "unsalvageable"


def main() -> int:
    tallies: dict[str, dict[str, int]] = {}
    for contract in CONTRACTS:
        for model in MODELS:
            cell = f"{contract}/{model}"
            for trial in range(1, TRIALS_PER_CELL + 1):
                path = raw_path_for(model, contract, trial)
                if not path.exists():
                    continue
                raw = path.read_text(encoding="utf-8")
                if contract == "envelope":
                    _, content = assistant_content_from_envelope(raw)
                else:
                    content = raw
                label = classify(content or "")
                tallies.setdefault(cell, {})
                tallies[cell][label] = tallies[cell].get(label, 0) + 1

    print(f"{'cell':<28} how the reply had to be handled")
    print("-" * 78)
    for cell in sorted(tallies):
        for label, count in sorted(tallies[cell].items(), key=lambda pair: -pair[1]):
            print(f"{cell:<28} {count:>3}x  {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
