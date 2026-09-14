"""
Throwaway link checker for the Atom docs.

Not part of the atom package -- this is a one-off verification script, kept because
re-running it is cheaper than re-deriving it.

Checks that every relative markdown link in the repo resolves to a real file.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

broken = []
checked = 0

for md in sorted(REPO.rglob("*.md")):
    if ".git" in md.parts:
        continue
    for label, target in LINK.findall(md.read_text(encoding="utf-8")):
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
