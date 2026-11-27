"""Keep phase-tracking instructions within the supported CLI surface."""

from pathlib import Path
import re
import shlex

import pytest

from atom.cli import _build_parser


REPOSITORY = Path(__file__).resolve().parents[2]
ASSETS = Path("tools") / "atom" / "assets"
GUIDANCE = (
    Path("skills") / "plan" / "SKILL.md",
    Path("skills") / "build" / "SKILL.md",
    Path("skills") / "atom" / "references" / "human-gates.md",
)


@pytest.mark.parametrize("relative", GUIDANCE + tuple(ASSETS / path for path in GUIDANCE))
def test_phase_tracking_examples_use_supported_commands(relative: Path) -> None:
    text = (REPOSITORY / relative).read_text(encoding="utf-8")
    examples = [
        line.strip() for line in text.splitlines() if line.strip().startswith("atom ")
    ]
    examples.extend(re.findall(r"`(atom [^`\n]+)`", text))
    assert examples, f"{relative}: no CLI examples checked"
    unsupported = []
    for line in examples:
        try:
            _build_parser().parse_args(shlex.split(line)[1:])
        except SystemExit as error:
            if error.code != 0:
                unsupported.append(line)
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"


@pytest.mark.parametrize("relative", GUIDANCE)
def test_phase_tracking_assets_match_canonical_text(relative: Path) -> None:
    canonical = (REPOSITORY / relative).read_text(encoding="utf-8")
    packaged = (REPOSITORY / ASSETS / relative).read_text(encoding="utf-8")
    assert packaged == canonical, f"{relative}: packaged phase guidance differs"
