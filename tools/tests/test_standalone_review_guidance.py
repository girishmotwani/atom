"""Check shipped review entry contracts without launching reviewer processes."""

from __future__ import annotations

from pathlib import Path
import re
import shlex
from urllib.parse import unquote, urlsplit

import pytest

from atom.cli import _build_parser


REPOSITORY = Path(__file__).resolve().parents[2]
REFERENCE = Path("skills") / "atom" / "references" / "standalone-review.md"
REVIEW_SKILL = Path("skills") / "review" / "SKILL.md"
ASSETS = Path("tools") / "atom" / "assets"
DOCUMENTS = (
    REFERENCE,
    REVIEW_SKILL,
    ASSETS / REFERENCE,
    ASSETS / REVIEW_SKILL,
    Path("com.github.copilot") / "commands" / "start.md",
    Path("README.md"),
    Path("docs") / "workflow.md",
)


@pytest.mark.parametrize("relative", (REFERENCE, REVIEW_SKILL))
def test_review_entry_assets_match_canonical_bytes(relative: Path) -> None:
    canonical = REPOSITORY / relative
    assert canonical.is_file(), f"Missing canonical entry guidance: {relative}"
    assert (REPOSITORY / ASSETS / relative).read_bytes() == canonical.read_bytes()


def test_start_routes_review_before_lifecycle_inspection() -> None:
    start = (REPOSITORY / "com.github.copilot" / "commands" / "start.md").read_text(
        encoding="utf-8"
    )
    early_entry = start.split("## Step 1", 1)[0]
    assert "/atom:review" in early_entry
    assert "standalone-review.md" in early_entry


@pytest.mark.parametrize("strict_toolchain", (False, True))
def test_bounded_review_examples_parse_without_running_commands(
    strict_toolchain: bool,
) -> None:
    text = (REPOSITORY / REFERENCE).read_text(encoding="utf-8")
    examples = [
        line for line in text.splitlines()
        if line.startswith("atom review ") and "MODEL_A" in line
    ]
    assert len(examples) == 3
    selections = set()
    for example in examples:
        command = shlex.split(example)[1:]
        if strict_toolchain:
            command.append("--strict-toolchain")
        arguments = _build_parser().parse_args(command)
        assert arguments.strict_toolchain is strict_toolchain
        assert arguments.models == ["MODEL_A", "MODEL_B"]
        assert arguments.runs == 1
        assert arguments.concurrency == 1
        assert sum((arguments.working, arguments.staged, arguments.branch is not None)) == 1
        selections.add(
            "working" if arguments.working else "staged" if arguments.staged else "branch"
        )
    assert selections == {"working", "staged", "branch"}


@pytest.mark.parametrize(
    "relative",
    (REFERENCE, REVIEW_SKILL, ASSETS / REFERENCE, ASSETS / REVIEW_SKILL,
     Path("docs") / "workflow.md"),
)
def test_review_guidance_discloses_go_pin_degraded_exit_and_strict_choice(
    relative: Path,
) -> None:
    text = (REPOSITORY / relative).read_text(encoding="utf-8")
    for required in ("review_go_version", "--strict-toolchain", "degraded", "nonzero"):
        assert required in text, f"{relative}: missing Go-policy disclosure {required}"
    assert "Required-gate failures stop the bounded action." not in text
    assert "A failing required gate stops the review." not in text


@pytest.mark.parametrize("relative", DOCUMENTS)
def test_changed_review_document_links_resolve(relative: Path) -> None:
    document = REPOSITORY / relative
    text = document.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
        if urlsplit(target).scheme or target.startswith("#"):
            continue
        path = unquote(target.split("#", 1)[0])
        assert (document.parent / path).exists(), f"{relative}: broken link {target}"


@pytest.mark.parametrize("relative", DOCUMENTS)
def test_shipped_review_examples_do_not_use_unsupported_flags(relative: Path) -> None:
    text = (REPOSITORY / relative).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("atom review "):
            assert not {"--base", "--models"} & set(shlex.split(line))
