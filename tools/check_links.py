"""
Throwaway link checker for the Atom docs.

Not part of the atom package -- this is a one-off verification script, kept because
re-running it is cheaper than re-deriving it.

Checks that every relative markdown link in the repo resolves to a real file.

Links inside code -- fenced blocks and inline spans -- are deliberately ignored.
Documentation about links has to quote link syntax, and a quoted example is not a
navigational link. Treating one as a link made this script fail on a review
finding that described this script's own limitation.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Fenced blocks first: an inline-span pass would otherwise pair up the fence
# markers themselves.
FENCED_BLOCK = re.compile(r"(?m)^[ \t]*(`{3,}|~{3,}).*?^[ \t]*\1[ \t]*$", re.DOTALL)

# Inline spans deliberately do NOT cross lines. With DOTALL this pattern pairs a
# backtick with another one paragraphs away and blanks everything between them.
INLINE_CODE = re.compile(r"(`+).+?\1")


def _blank(match: re.Match[str]) -> str:
    """Replace a code region with spaces, keeping its length and its newlines.

    Deleting the region instead would be wrong in a way that hides work rather
    than reporting it. The common idiom [`AGENTS.md`](../AGENTS.md) puts code in
    the link LABEL; delete the span and `[](../AGENTS.md)` no longer matches a
    link pattern that requires a non-empty label, so the link is never checked
    and never reported. That silently dropped 62 of 136 links while still
    printing success. Spaces keep the label non-empty and the line intact.
    """
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_code(markdown: str) -> str:
    """Blank out every code region so its contents cannot be read as markup."""
    without_blocks = FENCED_BLOCK.sub(_blank, markdown)
    return INLINE_CODE.sub(_blank, without_blocks)


broken = []
checked = 0

for md in sorted(REPO.rglob("*.md")):
    if ".git" in md.parts:
        continue
    source = md.read_text(encoding="utf-8")
    prose = strip_code(source)
    # Matching happens on the blanked text, but the report quotes the original.
    # Blanking preserves length exactly, so a span found in one is the same span
    # in the other -- without that, a code label would be reported as a run of
    # spaces and the reader could not find the link being complained about.
    for match in LINK.finditer(prose):
        target = match.group(2)
        start, end = match.span(1)
        label = source[start:end]
        # Skip absolute URLs, anchors and mail links -- only relative paths are ours.
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        # Templates contain {placeholder} tokens that are filled in at use time.
        # They are not links yet, so they cannot be resolved.
        if "{" in path_part:
            continue
        checked += 1
        resolved = (md.parent / path_part).resolve()
        if not resolved.exists():
            broken.append((md.relative_to(REPO), label, target))

print(f"checked {checked} relative links across markdown files")
if broken:
    print(f"\nBROKEN: {len(broken)}")
    for source, label, target in broken:
        print(f"  {source}")
        print(f"      [{label}] -> {target}")
    sys.exit(1)

print("all relative links resolve")
