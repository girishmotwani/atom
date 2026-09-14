"""Create spike directories for `atom poc new`.

This module owns exactly one invariant, and it is the one that matters:

    A spike directory ALWAYS has its own go.mod.

Without one, the spike's source is swept up by the parent module's `./...`
patterns, and a deliberately broken spike -- the normal state of a spike under
development -- breaks the parent build. That was established by
poc/module-isolation/spike.py and is why a failed scaffold rolls back entirely
rather than leaving a half-built directory behind.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .runner import CommandRunner

# A slug becomes both a directory name and part of a Go module path, so it has
# to be safe in both. Lowercase alphanumerics in hyphen-separated segments is
# the intersection: portable across filesystems, valid in a module path, and
# incapable of expressing a path traversal.
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Spikes are never published, so the module path is deliberately not a real
# domain. Anyone reading `spike/json-streaming` in a stack trace knows at once
# that they are looking at throwaway code.
MODULE_NAMESPACE = "spike"


class SlugError(ValueError):
    """The requested slug cannot be used as a directory and module path."""


class ScaffoldError(RuntimeError):
    """The spike could not be created, and anything partial has been removed."""


@dataclass(frozen=True)
class ScaffoldResult:
    """Describes the spike that was created so the CLI can point the developer at it."""

    slug: str
    directory: Path
    files_created: list[Path]
    module_path: str


def scaffold_spike(
    poc_root: Path,
    slug: str,
    question: str,
    runner: CommandRunner,
) -> ScaffoldResult:
    """Create a runnable spike directory containing go.mod, main.go and README.md.

    go.mod is produced by shelling out to `go mod init` rather than written from
    a template. The POC showed the toolchain pins the full patch version
    (`go 1.23.4`), which a hand-written template would have got wrong and which
    would then drift every time the toolchain moved.

    Raises SlugError for an unusable slug, FileExistsError if the spike already
    exists, and ScaffoldError if `go mod init` fails.
    """

    _validate_slug(slug)

    spike_directory = poc_root / slug
    if spike_directory.exists():
        raise FileExistsError(
            f"Spike '{slug}' already exists at {spike_directory}. "
            "Spikes are never overwritten -- they may hold observations that cannot be reproduced."
        )

    module_path = f"{MODULE_NAMESPACE}/{slug}"
    spike_directory.mkdir(parents=True)

    # From here on, any failure must leave the filesystem as we found it. A
    # directory containing Go source but no go.mod is the one state that breaks
    # the parent build, so a partial scaffold is worse than no scaffold at all.
    try:
        _generate_go_mod(spike_directory, module_path, runner)
        (spike_directory / "main.go").write_text(_render_main_go(question), encoding="utf-8")
        (spike_directory / "README.md").write_text(_render_readme(slug, question), encoding="utf-8")
    except Exception:
        shutil.rmtree(spike_directory, ignore_errors=True)
        raise

    files_created = [
        spike_directory / "go.mod",
        spike_directory / "main.go",
        spike_directory / "README.md",
    ]
    return ScaffoldResult(slug=slug, directory=spike_directory, files_created=files_created, module_path=module_path)


def _validate_slug(slug: str) -> None:
    if not SLUG_PATTERN.match(slug):
        raise SlugError(
            f"Invalid spike slug: {slug!r}. "
            "Use lowercase letters and digits in hyphen-separated words, for example 'json-streaming'."
        )


def _generate_go_mod(spike_directory: Path, module_path: str, runner: CommandRunner) -> None:
    """Run `go mod init`, then verify it actually produced the file.

    Checking the exit code alone would not be enough. Phase 1 established twice
    over that Go tools do not always signal through the exit code, so the
    invariant is confirmed by observing the file, not by trusting the report.
    """

    result = runner.run(["go", "mod", "init", module_path], spike_directory)

    if not result.succeeded:
        raise ScaffoldError(
            f"`go mod init {module_path}` failed and the spike was not created.\n"
            f"{result.stderr.strip() or result.stdout.strip()}"
        )

    if not (spike_directory / "go.mod").exists():
        raise ScaffoldError(
            f"`go mod init {module_path}` reported success but wrote no go.mod. "
            "Refusing to leave a spike that would break the parent build."
        )


def _render_main_go(question: str) -> str:
    """Build a spike that runs immediately and explains how to answer its question."""

    return f'''package main

// Spike: {question}
//
// This is throwaway code. It exists to answer one question, and it is deleted
// or archived once the question is answered. Do not make it good.
//
// Signal your answer with the exit code:
//
//     os.Exit(0)  Confirmed    -- the question was answered yes
//     os.Exit(1)  Refuted      -- the question was answered no
//     os.Exit(2)  Inconclusive -- the spike did not settle it
//
// A Refuted spike is a success. It cost you an hour and saved you a design.
// The only failure is recording Inconclusive as Confirmed.

import "fmt"

func main() {{
	fmt.Println("Question: {question}")
	fmt.Println("Replace this with the smallest program that answers it.")

	// Nothing has been observed yet, so nothing has been settled.
	// Change this to 0 or 1 once the spike actually answers the question.
	// os.Exit(2)
}}
'''


def _render_readme(slug: str, question: str) -> str:
    """Build the first draft of the POC report, so the write-up starts already begun."""

    return f"""# Spike: {slug}

**Created:** {date.today().isoformat()}

## Question

{question}

> A good spike question is falsifiable. If there is no observation that could
> answer it "no", it is not a question -- it is a preference.

## Method

<!-- What you actually ran. Enough detail that someone else could repeat it. -->

## Result

<!-- Verbatim output. Paste it; do not summarise it. The summary is the next
     section, and keeping them apart is what stops one becoming the other. -->

## Verdict

<!-- Confirmed / Refuted / Inconclusive, and what it means for the design.

     Inconclusive is a real verdict. Recording it honestly is the whole point;
     quietly upgrading it to Confirmed is the one thing that makes a POC
     worthless. -->
"""
