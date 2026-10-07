"""Install Atom's instructions and reference material into a target repository."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from contextlib import ExitStack
from pathlib import Path

from importlib.resources import as_file, files

ASSET_ROOT = files("atom") / "assets"
LOCAL_BUNDLE_DIRECTORY = Path(".atom") / "atom"
LOCAL_INSTRUCTIONS_PATH = Path(".github") / "copilot-instructions.md"
LOCAL_AGENTS_PATH = LOCAL_BUNDLE_DIRECTORY / "AGENTS.md"
MANIFEST_PATH = LOCAL_BUNDLE_DIRECTORY / "manifest.json"
GITIGNORE_PATH = Path(".gitignore")
MANAGED_MARKER = "<!-- Atom managed onboarding -->"
GITIGNORE_BLOCK_START = "# >>> Atom generated runtime files >>>"
GITIGNORE_BLOCK_END = "# <<< Atom generated runtime files <<<"
GITIGNORE_BLOCK_LINES = (
    GITIGNORE_BLOCK_START,
    "# Machine-local Atom runtime data; project configuration and approvals stay tracked.",
    ".atom/baseline.json",
    ".atom/events.jsonl",
    ".atom/events.lock",
    GITIGNORE_BLOCK_END,
)
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

    _install_gitignore_rules(root)

    return [
        bundle_directory / "AGENTS.md",
        bundle_directory / "skills",
        bundle_directory / "manifest.json",
        instructions_path,
    ]


def _install_gitignore_rules(root: Path) -> None:
    """Install Atom's machine-local runtime ignore rules."""

    path = root / GITIGNORE_PATH
    contents = ""
    if path.exists():
        try:
            with path.open("r", encoding="utf-8", newline="") as existing:
                contents = existing.read()
        except (OSError, UnicodeDecodeError) as error:
            raise OnboardingError(
                f"could not read {path}: {error}. Fix the file or its permissions, "
                "then run `atom init --force`."
            ) from error

    newline = "\r\n" if "\r\n" in contents else "\n"
    block = newline.join(GITIGNORE_BLOCK_LINES) + newline
    lines = contents.splitlines(keepends=True)
    start_lines = [
        index
        for index, line in enumerate(lines)
        if line.rstrip("\r\n") == GITIGNORE_BLOCK_START
    ]
    end_lines = [
        index
        for index, line in enumerate(lines)
        if line.rstrip("\r\n") == GITIGNORE_BLOCK_END
    ]

    if not start_lines and not end_lines:
        if not contents:
            updated = block
        elif contents.endswith(("\n\n", "\r\n\r\n")):
            updated = contents + block
        elif contents.endswith("\r\n") or contents.endswith("\n"):
            updated = contents + newline + block
        else:
            updated = contents + newline + newline + block
    elif (
        len(start_lines) == 1
        and len(end_lines) == 1
        and start_lines[0] < end_lines[0]
    ):
        updated = (
            "".join(lines[: start_lines[0]])
            + block
            + "".join(lines[end_lines[0] + 1 :])
        )
    else:
        raise OnboardingError(
            "Atom managed .gitignore markers are missing, duplicated, or out of order; "
            "repair the managed block and run `atom init --force`."
        )

    if updated == contents:
        return

    _replace_text_atomically(path, updated)


def _replace_text_atomically(path: Path, contents: str) -> None:
    """Replace a user-owned text file without truncating the original first."""

    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f"{path.name}.atom-",
            suffix=".tmp",
            dir=path.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as destination:
            destination.write(contents)
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise OnboardingError(
            f"could not update {path}: {error}. Fix the file permissions or close "
            "the process holding it open, then run `atom init --force`."
        ) from error


def _remove_legacy_external_lines(contents: str) -> str:
    """Remove old Atom-only lines that point outside the target repository."""

    lines = [
        line
        for line in contents.splitlines()
        if not any(marker in line for marker in LEGACY_EXTERNAL_MARKERS)
    ]
    return "\n".join(lines) + ("\n" if contents.endswith("\n") and lines else "")
