"""Install Atom's instructions and reference material into a target repository."""

from __future__ import annotations

import json
import shutil
from contextlib import ExitStack
from pathlib import Path

from importlib.resources import as_file, files

ASSET_ROOT = files("atom") / "assets"
LOCAL_BUNDLE_DIRECTORY = Path(".atom") / "atom"
LOCAL_INSTRUCTIONS_PATH = Path(".github") / "copilot-instructions.md"
LOCAL_AGENTS_PATH = LOCAL_BUNDLE_DIRECTORY / "AGENTS.md"
MANIFEST_PATH = LOCAL_BUNDLE_DIRECTORY / "manifest.json"
MANAGED_MARKER = "<!-- Atom managed onboarding -->"
LEGACY_EXTERNAL_MARKERS = (
    "..\\..\\atom\\AGENTS.md",
    "../../atom/AGENTS.md",
    "skills\\atom\\",
    "skills/atom/",
)
INSTRUCTIONS_LINE = (
    f"{MANAGED_MARKER}\n"
    "Read [Atom's local instructions](../.atom/atom/AGENTS.md) before working here. "
    "The referenced skills and discipline documents are copied into this repository."
)


class OnboardingError(RuntimeError):
    """The local Atom instruction bundle could not be installed."""


def install_local_bundle(root: Path) -> list[Path]:
    """Copy Atom's instructions and skills into ``root``.

    The bundle is deliberately inside ``.atom`` so all references resolve
    within the onboarded repository, while the generated Copilot instruction
    file remains a small, stable pointer to that local source of truth.
    """

    bundle_directory = root / LOCAL_BUNDLE_DIRECTORY
    with ExitStack() as resources:
        source_agents = resources.enter_context(as_file(ASSET_ROOT / "AGENTS.md"))
        source_skills = resources.enter_context(as_file(ASSET_ROOT / "skills"))
        if not source_agents.is_file() or not source_skills.is_dir():
            raise OnboardingError(
                "The installed Atom package is missing its bundled onboarding assets."
            )

        bundle_directory.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_agents, bundle_directory / "AGENTS.md")
        shutil.copytree(source_skills, bundle_directory / "skills", dirs_exist_ok=True)
    (bundle_directory / "manifest.json").write_text(
        json.dumps(
            {
                "managed_by": "atom init",
                "source": "atom-cli package",
                "files": ["AGENTS.md", "skills/"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    instructions_path = root / LOCAL_INSTRUCTIONS_PATH
    instructions_path.parent.mkdir(parents=True, exist_ok=True)
    existing = (
        instructions_path.read_text(encoding="utf-8")
        if instructions_path.exists()
        else ""
    )
    existing = _remove_legacy_external_lines(existing)
    if MANAGED_MARKER not in existing:
        separator = "\n\n" if existing and not existing.endswith("\n\n") else ""
        instructions_path.write_text(
            existing + separator + INSTRUCTIONS_LINE + "\n",
            encoding="utf-8",
        )

    return [
        bundle_directory / "AGENTS.md",
        bundle_directory / "skills",
        bundle_directory / "manifest.json",
        instructions_path,
    ]


def _remove_legacy_external_lines(contents: str) -> str:
    """Remove old Atom-only lines that point outside the target repository."""

    lines = [
        line
        for line in contents.splitlines()
        if not any(marker in line for marker in LEGACY_EXTERNAL_MARKERS)
    ]
    return "\n".join(lines) + ("\n" if contents.endswith("\n") and lines else "")
