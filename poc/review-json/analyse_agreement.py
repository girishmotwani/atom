"""Measure how two models' findings actually relate, to inform the merge design.

D7 in the POC report says deduplication is unmeasured. It does not have to stay that
way: forty responses are already on disk. This script does not call any model. It asks
what the saved evidence says about questions the merge design has to answer:

  * How many findings does each model return for the same diff?
  * Do the two models converge on the same (file, line) pairs, or scatter?
  * When they flag the same underlying problem, do the line numbers match exactly?
  * How stable is a single model across repeated runs of the identical prompt?

That last one matters more than it looks. If one model returns a different set each
time it is asked, then "the two models disagree" is not evidence of anything, and a
merge strategy built on agreement is built on noise.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spike import (  # noqa: E402
    CONTRACTS,
    MODELS,
    TRIALS_PER_CELL,
    assistant_content_from_envelope,
    locate_json_payload,
    raw_path_for,
)


def findings_from(path: Path, contract: str) -> list[dict]:
    """Extract the findings list from one saved response, or [] if unusable."""
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    if contract == "envelope":
        _, content = assistant_content_from_envelope(raw)
    else:
        content = raw
    payload = locate_json_payload(content or "")
    if payload is None:
        return []
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def main() -> int:
    # model -> list of one findings-list per run (both contracts pooled: the POC
    # report's C1 established they are equivalent, so they are treated as repeats).
    runs_by_model: dict[str, list[list[dict]]] = defaultdict(list)
    for contract in CONTRACTS:
        for model in MODELS:
            for trial in range(1, TRIALS_PER_CELL + 1):
                findings = findings_from(raw_path_for(model, contract, trial), contract)
                if findings:
                    runs_by_model[model].append(findings)

    print("=" * 78)
    print("HOW MANY FINDINGS PER RUN")
    print("=" * 78)
    for model, runs in sorted(runs_by_model.items()):
        counts = [len(run) for run in runs]
        print(
            f"{model:<22} runs={len(runs):<3} findings per run: "
            f"min={min(counts)} max={max(counts)} mean={sum(counts)/len(counts):.1f}"
        )

    print("\n" + "=" * 78)
    print("SELF-CONSISTENCY -- same model, same prompt, repeated")
    print("=" * 78)
    print("How often each (file, line) is reported, as a fraction of that model's runs.")
    print("A model that always reports the same lines is stable; a model that scatters")
    print("makes cross-model agreement meaningless.\n")
    lines_by_model: dict[str, Counter] = {}
    for model, runs in sorted(runs_by_model.items()):
        counter: Counter = Counter()
        for run in runs:
            # A line reported twice in one run still counts once for that run.
            seen = {(f.get("file"), f.get("line")) for f in run if isinstance(f, dict)}
            counter.update(seen)
        lines_by_model[model] = counter
        print(f"{model}  ({len(runs)} runs)")
        for (file, line), count in counter.most_common(12):
            share = 100.0 * count / len(runs)
            marker = "always" if count == len(runs) else f"{share:.0f}%"
            print(f"    {str(file):<24} line {str(line):<5} {count:>3}/{len(runs)}  {marker}")
        print()

    print("=" * 78)
    print("CROSS-MODEL AGREEMENT -- do they converge on the same lines?")
    print("=" * 78)
    models = sorted(lines_by_model)
    if len(models) == 2:
        first, second = models
        lines_first = {key for key, count in lines_by_model[first].items() if count > 0}
        lines_second = {key for key, count in lines_by_model[second].items() if count > 0}
        both = lines_first & lines_second
        print(f"{first:<22} reported {len(lines_first)} distinct (file, line) pairs")
        print(f"{second:<22} reported {len(lines_second)} distinct (file, line) pairs")
        print(f"{'both':<22} {len(both)} pairs in common\n")

        print("exact (file, line) matches across models:")
        for key in sorted(both, key=lambda k: (str(k[0]), k[1] if isinstance(k[1], int) else 0)):
            print(f"    {str(key[0]):<24} line {key[1]}")

        print("\nreported by only one model:")
        for label, only in ((first, lines_first - lines_second), (second, lines_second - lines_first)):
            for key in sorted(only, key=lambda k: (str(k[0]), k[1] if isinstance(k[1], int) else 0)):
                count = lines_by_model[label][key]
                total = len(runs_by_model[label])
                print(f"    {label:<22} line {str(key[1]):<5} ({count}/{total} runs)")

        # Near misses are the crux of the merge design: if the same problem is
        # reported one or two lines apart, exact matching will double-report it.
        print("\nnear misses -- same file, line numbers within 3 of each other,")
        print("not an exact match. These are what an exact-match merge would duplicate:")
        near = []
        for file_a, line_a in lines_first - lines_second:
            for file_b, line_b in lines_second - lines_first:
                if file_a == file_b and isinstance(line_a, int) and isinstance(line_b, int):
                    if 0 < abs(line_a - line_b) <= 3:
                        near.append((file_a, line_a, line_b))
        if near:
            for file, line_a, line_b in sorted(near):
                print(f"    {str(file):<24} {first} line {line_a}  vs  {second} line {line_b}")
        else:
            print("    none")

    print("\n" + "=" * 78)
    print("SEVERITY AGREEMENT on the exact-match lines")
    print("=" * 78)
    if len(models) == 2:
        first, second = models
        for key in sorted(both, key=lambda k: (str(k[0]), k[1] if isinstance(k[1], int) else 0)):
            severities: dict[str, Counter] = {}
            for model in models:
                counter: Counter = Counter()
                for run in runs_by_model[model]:
                    for finding in run:
                        if isinstance(finding, dict) and (finding.get("file"), finding.get("line")) == key:
                            counter[finding.get("severity")] += 1
                severities[model] = counter
            rendered = "  |  ".join(
                f"{model}: {dict(severities[model])}" for model in models
            )
            print(f"  line {key[1]}:  {rendered}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
