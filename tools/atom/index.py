"""List the spikes in a repository for `atom poc list`.

This is the view a developer reaches for when they want to know what has
already been investigated -- and, just as importantly, when something is wrong.
It therefore surfaces the one state that breaks the parent build: a spike
directory with no go.mod of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# The heading the scaffolded README puts the question under. Reading it back
# out is what turns a list of slugs into something worth looking at.
QUESTION_HEADING = "## Question"


@dataclass(frozen=True)
class SpikeSummary:
    """One row of `atom poc list`."""

    slug: str
    question: str | None
    has_go_mod: bool


def list_spikes(poc_root: Path) -> list[SpikeSummary]:
    """Return every spike under poc/, sorted by slug.

    Only direct children are considered. A spike's own subpackages belong to
    that spike, so treating them as spikes would report one investigation as
    several. This matches find_poc_modules_without_go_mod (B19).

    A missing poc/ yields an empty list rather than an error: a repository that
    has not run a spike yet is normal, not broken.
    """

    if not poc_root.is_dir():
        return []

    summaries = [
        SpikeSummary(
            slug=child.name,
            question=_read_question(child / "README.md"),
            has_go_mod=(child / "go.mod").is_file(),
        )
        for child in sorted(poc_root.iterdir())
        if child.is_dir()
    ]
    return summaries


def _read_question(readme_path: Path) -> str | None:
    """Extract the question from a spike README, or None if it does not state one.

    Returning None rather than a best guess matters here. A misleading question
    is worse than a missing one -- the developer would trust it.
    """

    if not readme_path.is_file():
        return None

    try:
        lines = readme_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None

    try:
        heading_index = next(
            index for index, line in enumerate(lines) if line.strip().lower() == QUESTION_HEADING.lower()
        )
    except StopIteration:
        return None

    question_lines: list[str] = []
    for line in lines[heading_index + 1 :]:
        stripped = line.strip()

        if stripped.startswith("#"):
            break

        # The scaffolded README puts guidance in a blockquote under the
        # question. It is advice to the developer, not part of what they asked.
        if stripped.startswith(">"):
            break

        if not stripped:
            # A blank line before any content is just spacing after the
            # heading; a blank line after content ends the question.
            if question_lines:
                break
            continue

        question_lines.append(stripped)

    if not question_lines:
        return None

    # Collapse to one line so it always renders as a single table row.
    return " ".join(question_lines)
