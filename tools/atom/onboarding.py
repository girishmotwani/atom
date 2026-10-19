"""Install Atom's instructions and reference material into a target repository."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from contextlib import ExitStack
from pathlib import Path

from importlib.resources import as_file, files

from atom.storage import StateFileError, read_json

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
    """The local Atom instruction bundle could not be installed or validated."""


def validate_local_bundle(root: Path) -> None:
    """Check shared onboarding without repairing or upgrading an existing bundle."""

    manifest_path = root / MANIFEST_PATH
    if not manifest_path.is_file():
        raise OnboardingError(f"{manifest_path}: missing or not a regular file")
    try:
        manifest = read_json(manifest_path)
    except StateFileError as error:
        raise OnboardingError(str(error)) from error
    entries = manifest.get("files")
    if (
        manifest.get("managed_by") != "atom init"
        or manifest.get("source") != "atom-cli package"
        or not isinstance(entries, list)
        or not all(isinstance(entry, str) for entry in entries)
        or "AGENTS.md" not in entries
        or "skills/" not in entries
    ):
        raise OnboardingError(f"{manifest_path}: not a usable Atom bundle manifest")

    bundle = root / LOCAL_BUNDLE_DIRECTORY
    _read_required_text(root / LOCAL_AGENTS_PATH)
    # Stable entrypoints, not the installed package's current inventory: a
    # repeat must not demand a bundle upgrade when a later release adds files.
    for skill in ("init", "discover", "poc", "plan", "spec", "tdd", "review", "ship"):
        _read_required_text(bundle / "skills" / skill / "SKILL.md")
    for reference in (
        "anti-rationalization.md",
        "poc-discipline.md",
        "tdd-discipline.md",
        "go-style.md",
        "human-gates.md",
        "verification.md",
        "model-guidance.md",
    ):
        _read_required_text(bundle / "skills" / "atom" / "references" / reference)

    instructions_path = root / LOCAL_INSTRUCTIONS_PATH
    instructions = _read_required_text(instructions_path)
    local_reference = f"](../{LOCAL_AGENTS_PATH.as_posix()})"
    if MANAGED_MARKER not in instructions or local_reference not in instructions:
        raise OnboardingError(
            f"{instructions_path}: missing the managed local Atom instruction reference"
        )

    gitignore_path = root / GITIGNORE_PATH
    lines = _read_required_text(gitignore_path).splitlines()
    bounds = _managed_gitignore_bounds(lines)
    if bounds is None:
        raise OnboardingError(f"{gitignore_path}: missing the Atom managed block")
    start, end = bounds
    missing = [
        rule
        for rule in GITIGNORE_BLOCK_LINES[2:-1]
        if rule not in lines[start + 1 : end]
    ]
    if missing:
        raise OnboardingError(
            f"{gitignore_path}: Atom managed block is missing {', '.join(missing)}"
        )


def _read_required_text(path: Path) -> str:
    if not path.is_file():
        raise OnboardingError(f"{path}: missing or not a regular file")
    try:
        contents = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise OnboardingError(f"could not read {path}: {error}") from error
    if not contents.strip():
        raise OnboardingError(f"{path}: file is empty")
    return contents


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
    bounds = _managed_gitignore_bounds(lines)

    if bounds is None:
        if not contents:
            updated = block
        elif contents.endswith(("\n\n", "\r\n\r\n")):
            updated = contents + block
        elif contents.endswith("\r\n") or contents.endswith("\n"):
            updated = contents + newline + block
        else:
            updated = contents + newline + newline + block
    else:
        start, end = bounds
        updated = "".join(lines[:start]) + block + "".join(lines[end + 1 :])

    if updated == contents:
        return

    _replace_text_atomically(path, updated)


def _managed_gitignore_bounds(lines: list[str]) -> tuple[int, int] | None:
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
        return None
    if len(start_lines) == len(end_lines) == 1 and start_lines[0] < end_lines[0]:
        return start_lines[0], end_lines[0]
    raise OnboardingError(
        "Atom managed .gitignore markers are missing, duplicated, or out of order; "
        "repair the managed block and run `atom init --force`."
    )


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
