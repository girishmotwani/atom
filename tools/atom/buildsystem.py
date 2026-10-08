"""Decide whether a repository's Makefile owns the build and test commands.

A repository that ships a Makefile has already declared how it is built, and
that declaration usually carries things `go build ./...` cannot know -- build
tags, ldflags stamping a version, code generation that has to run first. Atom
running the Go command directly would check something the project never builds.

Only `build` and `test` are delegated. There is no conventional Makefile target
for vetting, formatting or the race detector, and `gofmt` in particular cannot
be delegated at all because its verdict is read from stdout rather than an exit
code -- `make fmt` would hide the filenames the format gate exists to report.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# The order GNU make itself searches, so Atom resolves the same file make would.
MAKEFILE_NAMES = ("GNUmakefile", "makefile", "Makefile")

BUILD_TARGET = "build"
TEST_TARGET = "test"

DEFAULT_BUILD_COMMAND = ("go", "build", "./...")
DEFAULT_TEST_COMMAND = ("go", "test", "./...")


@dataclass(frozen=True)
class BuildSystem:
    """The commands Atom will actually run, and why it chose them.

    The reason is carried so `atom init` can record a decision the developer can
    disagree with, rather than leaving them to infer it from a command string.
    """

    build_command: tuple[str, ...]
    test_command: tuple[str, ...]
    makefile: Path | None
    reason: str


def find_makefile(root: Path) -> Path | None:
    """Return the makefile GNU make would read in ``root``, if there is one."""

    for name in MAKEFILE_NAMES:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def makefile_targets(makefile: Path) -> set[str]:
    """Return the literal target names ``make`` could be asked to run.

    Only targets a developer could type are returned. Pattern rules and targets
    built from variables are skipped because neither can be invoked as a literal
    `make build`, and a missing file yields an empty set rather than raising --
    detection runs inside a quality gate, where an exception would be reported
    as a code failure rather than as the environment question it really is.
    """

    try:
        source = makefile.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()

    targets: set[str] = set()
    for raw_line in source.splitlines():
        # Recipe lines are tab-indented and routinely contain a colon of their
        # own -- `docker run image:tag` would otherwise invent a target named
        # "docker run image".
        if raw_line.startswith("\t"):
            continue

        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        colon = line.find(":")
        if colon == -1:
            continue

        # `:=` and `::=` assign a variable; neither declares a rule.
        remainder = line[colon + 1 :]
        if remainder.startswith("=") or remainder.startswith(":="):
            continue

        left = line[:colon]
        # `NAME = value:other` is an assignment whose value merely contains a
        # colon, so anything with an `=` to the left of the colon is not a rule.
        if "=" in left:
            continue

        for name in left.split():
            if "%" in name or "$" in name:
                continue
            # `.PHONY` and friends are directives to make, not work to run.
            if name.startswith("."):
                continue
            targets.add(name)

    return targets


def detect(
    root: Path,
    *,
    make_is_available: Callable[[], bool] | None = None,
) -> BuildSystem:
    """Choose the build and test commands for ``root``.

    Each gate is decided independently: a Makefile that defines ``build`` but
    not ``test`` delegates only the build, because inventing the missing target
    would make every check fail on "No rule to make target".
    """

    if make_is_available is None:
        make_is_available = _make_is_on_path

    makefile = find_makefile(root)
    if makefile is None:
        return BuildSystem(
            DEFAULT_BUILD_COMMAND,
            DEFAULT_TEST_COMMAND,
            None,
            "no makefile; using Go defaults",
        )

    # Preferring a command that cannot run would turn a green tree red on any
    # machine without make -- a common state on Windows, where a Go repository
    # otherwise needs no build tooling at all.
    if not make_is_available():
        return BuildSystem(
            DEFAULT_BUILD_COMMAND,
            DEFAULT_TEST_COMMAND,
            makefile,
            f"{makefile.name} found but make is not installed; using Go defaults",
        )

    targets = makefile_targets(makefile)
    build_command = (
        ("make", BUILD_TARGET) if BUILD_TARGET in targets else DEFAULT_BUILD_COMMAND
    )
    test_command = (
        ("make", TEST_TARGET) if TEST_TARGET in targets else DEFAULT_TEST_COMMAND
    )

    delegated = [
        name
        for name, command in ((BUILD_TARGET, build_command), (TEST_TARGET, test_command))
        if command[0] == "make"
    ]
    if delegated:
        reason = f"{makefile.name} defines {', '.join(delegated)}; using make"
    else:
        reason = f"{makefile.name} defines neither build nor test; using Go defaults"

    return BuildSystem(build_command, test_command, makefile, reason)


def _make_is_on_path() -> bool:
    return shutil.which("make") is not None
