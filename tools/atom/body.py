"""Assemble the GitHub pull request body from facts that already exist on disk.

The body is the one Atom artifact a human reads on GitHub, and the Phase 5 POC
turned two of its properties from style preferences into load-bearing
constraints:

*   **It is summary plus links, never embedded content.** Phase 4's artifacts
    total 107 KB against a body ceiling the POC could only confirm as high as
    71,228 characters and never fully measured. A body built by concatenation
    grows with the phase; a body built from links grows with the *number* of
    artifacts, which stays in single digits. Only the second design cannot
    outgrow a limit nobody has found (B148).

*   **Its links name the pushed commit, never a branch.** A link to `main`
    404s until merge because the files do not exist there yet, and a link to a
    moving branch name silently starts describing different content later. So
    every link is pinned to the forty-character SHA that was pushed (B149).

*   **Its size is counted in characters, not bytes.** The POC wrote 70,000
    characters and read back 71,228 - one `\r` per line, added by a Windows
    text-mode write. The body file is therefore written with an explicit
    `newline="\n"`, and the number reported to the developer is the character
    count, which is the only figure that stays true across platforms (B150).

This module renders and writes the body only. It never invokes `gh`; the body
travels to `gh` by `--body-file`, which is `ship.py`'s concern (B151).

See `specs/atom-cli/phase-05-ship/design-spec.md` for B144-B151.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# A heading line whose text is exactly "Purpose", at any level. The design spec
# writes it as `## Purpose`, but matching the level rather than the exact prefix
# means a spec that promotes or demotes the heading still resolves.
_PURPOSE_HEADING = re.compile(r"^#+[ \t]+Purpose[ \t]*$", re.IGNORECASE)

# Any ATX heading. Used to find where the Purpose section ends: the section runs
# until the next heading of any level, so sibling and subsection headings both
# terminate it rather than being swept into the prose.
_ANY_HEADING = re.compile(r"^#+[ \t]+\S")

# The GitHub blob URL for a single file at a specific commit. The commit SHA
# sits where a ref goes; a branch name in that position would 404 until merge
# (B149), so the caller supplies a SHA and this template never sees a branch.
_BLOB_URL = "https://github.com/{repo_slug}/blob/{commit_sha}/{path}"


@dataclass(frozen=True)
class CheckSummary:
    """What the fresh atom check found, or why it did not run."""

    gate_rows: tuple[tuple[str, str], ...]   # (gate name, status text)
    absent_reason: str | None                # e.g. "not a Go module; no gates run"
    passed: bool


@dataclass(frozen=True)
class BodyInputs:
    """Everything needed to render a body, all of it already known."""

    title: str
    purpose: str | None                      # the design spec's Purpose paragraph
    commit_subjects: tuple[str, ...]
    check: CheckSummary
    artifacts: tuple[str, ...]               # repo-relative POSIX paths
    repo_slug: str                           # "owner/name"
    commit_sha: str                          # full 40-char SHA


def extract_purpose(design_spec_markdown: str) -> str | None:
    """Return the Purpose section's prose, or None when there is no such section.

    The whole section is returned, every paragraph of it, because truncating to
    the first paragraph would silently drop content the author wrote under that
    heading - the quiet omission Atom exists to prevent. Blank lines between
    paragraphs are preserved so the caller can quote them faithfully.
    """

    lines = design_spec_markdown.splitlines()

    start = None
    for index, line in enumerate(lines):
        if _PURPOSE_HEADING.match(line):
            start = index + 1
            break

    if start is None:
        return None

    body_lines: list[str] = []
    for line in lines[start:]:
        if _ANY_HEADING.match(line):
            break
        body_lines.append(line)

    prose = "\n".join(body_lines).strip()

    # A heading with nothing under it is not a purpose. Reporting it as absent
    # is more honest than returning an empty string a caller might quote as a
    # blank blockquote.
    return prose or None


def render_body(inputs: BodyInputs) -> str:
    """Render the pull request body as Markdown.

    The parts are assembled in the fixed order B148 prescribes - Title, Why,
    What changed, Evidence, Artifacts - so a reader always finds the same fact
    in the same place. Every part is present even when its source is empty,
    because an absent section reads as though the fact were never expected,
    which is the quiet omission B145a warns against; an empty part states its
    emptiness plainly instead.
    """

    sections = [
        f"# {inputs.title}",
        _render_why(inputs.purpose),
        _render_what_changed(inputs.commit_subjects),
        _render_evidence(inputs.check),
        _render_artifacts(inputs),
    ]

    # One blank line between blocks, and a single trailing newline, so the body
    # is stable across renders and diffs cleanly when re-shipped.
    return "\n\n".join(sections).rstrip() + "\n"


def write_body_file(text: str, path: Path) -> int:
    """Write the body for --body-file and return its CHARACTER count.

    The write forces `newline="\n"`: without it, Python's text mode translates
    every `\n` to `\r\n` on Windows, and the POC measured a 70,000-character
    body arriving on disk as 71,228 bytes. The value returned is `len(text)` -
    the character count - because that is the figure a developer can trust
    across platforms, where the byte count is not.
    """

    path.write_text(text, encoding="utf-8", newline="\n")

    # Deliberately len(text), never path.stat().st_size: on a non-ASCII body the
    # byte count would exceed the character count even with newline pinned, and
    # the number the developer is shown is a count of characters.
    return len(text)


def _render_why(purpose: str | None) -> str:
    """Render the Why section, quoting the purpose prose as a blockquote."""

    if purpose is None:
        # Stated, not omitted: a missing Purpose is a fact about the spec the
        # reviewer should see, not something to paper over (B144's principle).
        return "## Why\n\n_The design spec has no Purpose section._"

    return f"## Why\n\n{_blockquote(purpose)}"


def _render_what_changed(commit_subjects: tuple[str, ...]) -> str:
    """Render the What changed section as a bullet per commit subject."""

    if not commit_subjects:
        return "## What changed\n\n_No commits on the branch._"

    bullets = "\n".join(f"- {subject}" for subject in commit_subjects)
    return f"## What changed\n\n{bullets}"


def _render_evidence(check: CheckSummary) -> str:
    """Render the Evidence section: the gate table, or the recorded absence.

    When the check did not run - no Go module - the section states the recorded
    reason as a sentence rather than dropping the section (B145a/B146). An empty
    Evidence section and one that says "no gates run" are different claims, and
    only the second is honest.
    """

    if check.absent_reason is not None:
        return f"## Evidence\n\n{check.absent_reason}"

    header = "| Gate | Status |\n| --- | --- |"
    rows = "\n".join(f"| {name} | {status} |" for name, status in check.gate_rows)

    # The verdict is stated in words as well as in the rows so that a failing
    # gate shipped under an override reads as failing (B147a), never green.
    verdict = "All gates passed." if check.passed else "One or more gates did not pass."

    return f"## Evidence\n\n{header}\n{rows}\n\n{verdict}"


def _render_artifacts(inputs: BodyInputs) -> str:
    """Render the Artifacts section as one commit-pinned link per file.

    Files that are not there are simply not listed (B144): the body never
    invents an artifact and never writes "pending" about one that is absent.
    """

    if not inputs.artifacts:
        return "## Artifacts\n\n_None._"

    links = "\n".join(
        f"- [{path}]({_blob_url(inputs.repo_slug, inputs.commit_sha, path)})"
        for path in inputs.artifacts
    )
    return f"## Artifacts\n\n{links}"


def _blob_url(repo_slug: str, commit_sha: str, path: str) -> str:
    """Build a GitHub blob link pinned to the pushed commit SHA (B149)."""

    return _BLOB_URL.format(repo_slug=repo_slug, commit_sha=commit_sha, path=path)


def _blockquote(text: str) -> str:
    """Quote multi-paragraph prose as Markdown, one '>' per line.

    Blank lines become a bare '>' so paragraph breaks survive inside the quote;
    a blockquote with an unprefixed blank line silently ends early in most
    Markdown renderers, dropping every paragraph after the first.
    """

    quoted = []
    for line in text.splitlines():
        quoted.append(f"> {line}" if line.strip() else ">")
    return "\n".join(quoted)
