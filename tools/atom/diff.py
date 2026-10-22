"""Obtaining the diff that `atom review` will send to the models.

Three design commitments live in this module, and each one exists because the
alternative fails quietly:

* **The source is always explicit (B103, B104).** There is no default and no
  precedence rule. Guessing wrong costs minutes of model time and produces a
  confident report about code the developer did not mean to review.
* **The diff is captured once (B106).** Every model call reuses the same text,
  so they are all reviewing byte-identical input. Re-running ``git diff`` per
  call would let the working tree shift underneath the review.
* **Nothing is chunked or truncated (B106a, B106b).** The whole diff goes in one
  call, because cross-file context is where a caller that no longer matches its
  callee becomes visible. Instead of imposing a size limit nobody has measured,
  the size is *reported* so that a thin review of a huge diff has a visible
  explanation.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from atom.runner import CommandOutcome, CommandRunner


class DiffSource(enum.Enum):
    """Which set of changes is under review."""

    STAGED = "staged"
    BRANCH = "branch"
    WORKING = "working"


# The flag each source is spelled as on the command line. Kept in one place so
# the error messages below and the CLI cannot drift apart.
FLAG_FOR_SOURCE = {
    DiffSource.STAGED: "--staged",
    DiffSource.BRANCH: "--branch",
    DiffSource.WORKING: "--working",
}


class NoDiffSourceSelected(Exception):
    """Raised when no source was given, rather than defaulting to one (B104)."""


class TooManyDiffSourcesSelected(Exception):
    """Raised when several sources were given, rather than picking one."""


class DiffUnavailable(Exception):
    """Raised when git could not produce a diff at all.

    Deliberately distinct from an *empty* diff (B105). An empty diff is a
    perfectly good answer; a failed git command is not, and returning empty
    text for it would turn a broken invocation into a clean review.
    """


@dataclass(frozen=True)
class DiffRequest:
    """A resolved choice of what to review."""

    source: DiffSource
    base_ref: str | None = None

    def describe(self) -> str:
        """A phrase for the report, so it says what was actually reviewed."""
        if self.source is DiffSource.STAGED:
            return "staged changes"
        if self.source is DiffSource.WORKING:
            return "unstaged working-tree changes"
        return f"this branch against {self.base_ref}"


def select_source(
    staged: bool = False,
    branch: str | None = None,
    working: bool = False,
) -> DiffRequest:
    """Turn the three CLI flags into exactly one :class:`DiffRequest`.

    Raises rather than guessing in both directions -- none given and more than
    one given. A precedence rule ("staged wins") would silently review one of
    the two things asked for, which is the same failure B104 exists to prevent.
    """

    chosen: list[DiffSource] = []
    if staged:
        chosen.append(DiffSource.STAGED)
    if branch is not None:
        chosen.append(DiffSource.BRANCH)
    if working:
        chosen.append(DiffSource.WORKING)

    if not chosen:
        options = ", ".join(
            f"{FLAG_FOR_SOURCE[source]} ({description})"
            for source, description in (
                (DiffSource.STAGED, "changes in the index"),
                (DiffSource.BRANCH, "this branch against a base ref"),
                (DiffSource.WORKING, "unstaged changes"),
            )
        )
        raise NoDiffSourceSelected(
            f"atom review needs to be told what to review. Choose one of: {options}."
        )

    if len(chosen) > 1:
        flags = " and ".join(FLAG_FOR_SOURCE[source] for source in chosen)
        raise TooManyDiffSourcesSelected(
            f"{flags} were given together, and atom review will not choose "
            "between them. Run it once for each."
        )

    return DiffRequest(source=chosen[0], base_ref=branch)


def git_command_for(request: DiffRequest) -> tuple[str, ...]:
    """Build the git command that produces the requested diff."""

    if request.source is DiffSource.STAGED:
        return ("git", "diff", "--staged")

    if request.source is DiffSource.WORKING:
        return ("git", "diff")

    # Three dots, not two. Two dots would also include everything that landed
    # on the base branch since this one forked -- code the developer never
    # wrote, handed to a model as though they had.
    return ("git", "diff", f"{request.base_ref}...HEAD")


@dataclass
class CapturedDiff:
    """The diff text, plus the size facts the report needs (B106b).

    ``files`` and ``changed_lines`` are derived from the text rather than
    stored, so they cannot disagree with it.
    """

    text: str
    request: DiffRequest | None = None

    @property
    def is_empty(self) -> bool:
        """Whether there is anything at all to review (B105)."""
        return not self.text.strip()

    @cached_property
    def files(self) -> tuple[str, ...]:
        """Every path touched by the diff, as it will exist afterwards.

        A rename is reported under its new name because that is the file the
        review's findings will refer to.
        """
        return self._parsed.files

    @cached_property
    def changed_lines(self) -> int:
        """Added and removed lines, excluding headers and context."""
        return self._parsed.changed_lines

    @cached_property
    def _parsed(self) -> _ParsedDiff:
        return _parse_diff(self.text)

    def describe_size(self) -> str:
        """A phrase for the report header, e.g. `7 changed lines across 3 files`."""

        if self.is_empty:
            return "nothing to review"

        line_word = "line" if self.changed_lines == 1 else "lines"
        file_count = len(self.files)
        file_word = "file" if file_count == 1 else "files"

        return (
            f"{self.changed_lines} changed {line_word} "
            f"across {file_count} {file_word}"
        )


def capture_diff(
    request: DiffRequest,
    runner: CommandRunner,
    working_directory: Path,
    timeout_seconds: float = 60.0,
) -> CapturedDiff:
    """Run git once and return the whole diff (B106, B106a).

    Raises :class:`DiffUnavailable` on any git failure. That is deliberate: the
    caller must not be able to confuse "git broke" with "there were no changes".
    """

    command = git_command_for(request)
    result = runner.run(command, working_directory, timeout_seconds)

    if result.outcome is CommandOutcome.TOOL_MISSING:
        raise DiffUnavailable(
            f"could not run git to get the diff: {result.stderr.strip()}"
        )

    if result.outcome is CommandOutcome.TIMED_OUT:
        detail = result.stderr.strip()
        raise DiffUnavailable(
            f"git took longer than {timeout_seconds:g} seconds to produce the diff "
            f"for {request.describe()}." + (f" {detail}" if detail else "")
        )

    if result.exit_code != 0:
        # git's own message names the bad ref; a paraphrase would lose it.
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise DiffUnavailable(
            f"git could not produce the diff for {request.describe()}: {detail}"
        )

    return CapturedDiff(text=result.stdout, request=request)


@dataclass(frozen=True)
class _ParsedDiff:
    """The two facts a single pass over the diff produces."""

    files: tuple[str, ...]
    changed_lines: int


def _parse_diff(text: str) -> _ParsedDiff:
    """Read a unified diff once, tracking whether we are inside a hunk.

    Position matters more than prefix. Every line inside a hunk carries an
    added ``+``, ``-`` or space, so *content* that already begins with ``-``
    turns into lines like ``----`` (a removed markdown rule) and content
    beginning with ``++`` turns into ``+++ something`` -- indistinguishable
    from a file header if you only look at the prefix.

    Getting this wrong is silent in both directions: the size is quietly
    understated, and ``files`` quietly gains a path that does not exist, which
    would widen B117's guard against a model naming code it was never shown.
    """

    paths: set[str] = set()
    changed_lines = 0
    inside_hunk = False
    previous_old_path: str | None = None

    for line in text.splitlines():
        if inside_hunk:
            # Checked first, because a hunk body line's real content may look
            # like any header. The prefix belongs to the diff, not the file.
            if line.startswith("+") or line.startswith("-"):
                changed_lines += 1
                continue
            if line.startswith("@@"):
                continue  # a further hunk in the same file
            if not line.startswith("diff --git "):
                continue  # context, or `\ No newline at end of file`
            # A bare `diff --git` line cannot be hunk content, because hunk
            # content always carries a prefix. So the next file has started.
            inside_hunk = False

        if line.startswith("diff --git "):
            previous_old_path = None
            continue

        if line.startswith("--- "):
            previous_old_path = _strip_diff_path_prefix(line[len("--- ") :])
            continue

        if line.startswith("+++ "):
            # `+++ /dev/null` means the file was deleted, so the only name it
            # has is the old one from the `---` line just above.
            path = _strip_diff_path_prefix(line[len("+++ ") :]) or previous_old_path
            if path:
                paths.add(path)
            continue

        if line.startswith("@@"):
            inside_hunk = True

    return _ParsedDiff(files=tuple(sorted(paths)), changed_lines=changed_lines)


def _strip_diff_path_prefix(raw_path: str) -> str | None:
    """Turn `b/store/lookup.go` into `store/lookup.go`.

    Returns ``None`` for `/dev/null`, which is not a path the review can talk
    about.
    """

    path = raw_path.strip()

    # Some diffs append a tab and a timestamp to the path.
    path = path.split("\t", 1)[0]

    if path == "/dev/null":
        return None

    if path.startswith("b/") or path.startswith("a/"):
        return path[2:]

    return path
