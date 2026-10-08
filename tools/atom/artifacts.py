"""Write Atom's artifacts, and refuse to write anything else.

This module exists because approving a general purpose file editor for a
repository approves it for *every* file in that repository, including source
code. Atom only ever needs to write a small, known set of paths -- specs,
throwaway spikes, and three runtime files under ``.atom``. Routing those writes
through one narrow function means the broad approval is never needed.

The guard is deliberately not just a path classifier. A classifier that answers
"may I write here?" and then hands the path back to a separate writer leaves a
window in which the filesystem can change underneath the answer -- the classic
time-of-check to time-of-use race. A Windows directory junction dropped into
``specs/`` during that window is enough to send a write outside the repository,
which is exactly the escape the ``artifact-write-permissions`` spike
demonstrated against a path-matching permission hook. So validation and the
write live together here: the destination is re-validated after its directories
exist and immediately before the file is moved into place, and the content is
first written to a fresh file opened with ``O_EXCL`` inside the already
validated directory.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping
from uuid import uuid4

# Directories whose entire contents Atom may write. A bare directory name is not
# writable on its own -- only files beneath it.
ALLOWED_DIRECTORIES = ("specs", "poc")

# Individual runtime files Atom maintains. `.atom/atom/` -- the onboarded copy
# of these instructions -- is deliberately absent: the agent must not be able to
# rewrite the rules it is working under.
ALLOWED_RUNTIME_FILES = (
    Path(".atom") / "config.json",
    Path(".atom") / "state.json",
    Path(".atom") / "baseline.json",
)

_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class ArtifactWriteRefused(RuntimeError):
    """A requested write fell outside the artifact set and was not performed.

    Carries every refusal in the batch rather than only the first, so a caller
    fixing a multi-file write does not have to discover the problems one run at
    a time.
    """

    def __init__(self, refusals: Iterable["Decision"]) -> None:
        self.refusals = tuple(refusals)
        details = ", ".join(
            f"{refusal.target} ({refusal.reason})" for refusal in self.refusals
        )
        super().__init__(f"refused to write outside the artifact set: {details}")


@dataclass(frozen=True)
class Decision:
    """Why a single destination was allowed or refused.

    ``reason`` is a stable, greppable token rather than prose so that callers --
    including a future permission tool -- can branch on it and tests can assert
    on it without matching English.
    """

    target: str
    allowed: bool
    reason: str
    resolved: Path | None = None


def classify(root: Path, target: str | os.PathLike[str]) -> Decision:
    """Decide whether ``target`` is an Atom artifact inside ``root``.

    The checks run in a specific order, and the order is the point. Links are
    rejected *before* the destination is compared against the artifact set,
    because resolving a link first is what lets a junction named ``specs/x``
    masquerade as an allowed path.
    """

    repository = Path(os.path.realpath(root))
    candidate = Path(target)
    absolute = candidate if candidate.is_absolute() else repository / candidate
    lexical = Path(os.path.normpath(absolute))

    relative = _relative_to_repository(lexical, repository)
    if relative is None:
        return Decision(str(target), False, "outside-repository")

    if _contains_reparse_point(repository, lexical):
        return Decision(str(target), False, "reparse-point-in-path")

    resolved_relative = _relative_to_repository(
        Path(os.path.realpath(lexical)), repository
    )
    if resolved_relative is None:
        return Decision(str(target), False, "resolves-outside-repository")

    reason = _artifact_set_reason(resolved_relative)
    if reason is None:
        return Decision(str(target), False, "outside-artifact-set")
    return Decision(str(target), True, reason, repository / resolved_relative)


def write_artifacts(
    root: Path, contents: Mapping[str | os.PathLike[str], str]
) -> list[Path]:
    """Write every artifact in ``contents``, or write none of them.

    The whole batch is validated first. A mixed batch -- one spec file and one
    source file -- writes nothing at all, rather than landing the spec and then
    refusing the code, which is how the permission-hook experiment leaked a
    partial change.

    Each file is staged beside its destination and only then moved into place,
    so a destination is never left half written.
    """

    decisions = [classify(root, target) for target in contents]
    refusals = [decision for decision in decisions if not decision.allowed]
    if refusals:
        raise ArtifactWriteRefused(refusals)

    staged: list[tuple[Path, Path, str]] = []
    created_directories: list[Path] = []
    try:
        for decision, target in zip(decisions, contents):
            assert decision.resolved is not None  # guaranteed by `allowed`
            destination = decision.resolved
            created_directories.extend(
                _create_validated_directories(root, destination.parent)
            )
            # Creating the directories is itself a window in which a link could
            # have appeared, so the decision is confirmed against the filesystem
            # as it is now -- before any bytes are written anywhere.
            _confirm(root, destination, str(target))
            temporary = _stage(destination, contents[target])
            staged.append((temporary, destination, str(target)))

        # Staging one file is a window for a link to appear in front of
        # another, so every destination is confirmed once more with all of them
        # on disk and nothing yet moved into place.
        for _, destination, target in staged:
            _confirm(root, destination, target)
    except BaseException:
        for temporary, _, _ in staged:
            temporary.unlink(missing_ok=True)
        _remove_empty_directories(created_directories)
        raise

    written: list[Path] = []
    try:
        for temporary, destination, _ in staged:
            os.replace(temporary, destination)
            written.append(destination)
    except BaseException:
        for temporary, _, _ in staged:
            temporary.unlink(missing_ok=True)
        _remove_empty_directories(created_directories)
        raise
    return written


def _confirm(root: Path, destination: Path, target: str) -> None:
    """Re-run the decision against the filesystem as it is right now."""

    confirmed = classify(root, destination)
    if not confirmed.allowed:
        raise ArtifactWriteRefused([Decision(target, False, confirmed.reason)])


def _relative_to_repository(path: Path, repository: Path) -> Path | None:
    """Return ``path`` relative to ``repository``, or None if it escapes it."""

    try:
        relative = Path(os.path.relpath(path, repository))
    except ValueError:
        # Windows raises when the two paths are on different drives, which is
        # itself conclusive: the target is not in the repository.
        return None
    first = relative.parts[0] if relative.parts else ""
    if first == os.pardir:
        return None
    return relative


def _artifact_set_reason(relative: Path) -> str | None:
    """Name the rule that admits ``relative``, or None if no rule does."""

    normalised = os.path.normcase(str(relative))
    for runtime_file in ALLOWED_RUNTIME_FILES:
        if normalised == os.path.normcase(str(runtime_file)):
            return "allowed-runtime-file"
    parts = relative.parts
    if len(parts) > 1 and os.path.normcase(parts[0]) in {
        os.path.normcase(name) for name in ALLOWED_DIRECTORIES
    }:
        return "allowed-artifact-directory"
    return None


def _contains_reparse_point(repository: Path, target: Path) -> bool:
    """Report whether any existing component of ``target`` is a link.

    Every link is rejected, including one pointing back inside the repository.
    Proving a particular link is benign costs more than the feature is worth,
    and a rule with no exceptions is one an agent cannot talk itself around.
    """

    current = repository
    relative = _relative_to_repository(target, repository)
    if relative is None:
        return False
    for component in relative.parts:
        current = current / component
        if not os.path.lexists(current):
            return False
        if _is_reparse_point(current):
            return True
    return False


def _is_reparse_point(path: Path) -> bool:
    """Report whether ``path`` itself is a symlink or a Windows reparse point.

    ``os.path.islink`` misses directory junctions on some Python versions, so
    the Windows file attribute is checked directly as well.
    """

    try:
        entry = os.lstat(path)
    except (OSError, ValueError):
        return False
    if stat.S_ISLNK(entry.st_mode):
        return True
    return bool(getattr(entry, "st_file_attributes", 0) & _REPARSE_POINT)


def _create_validated_directories(root: Path, directory: Path) -> list[Path]:
    """Create ``directory`` one component at a time, refusing any link.

    ``Path.mkdir(parents=True)`` would happily walk through a junction. Creating
    each component separately means a link can be detected at the component
    where it appears, before anything is written beneath it.
    """

    repository = Path(os.path.realpath(root))
    relative = _relative_to_repository(directory, repository)
    if relative is None:
        raise ArtifactWriteRefused(
            [Decision(str(directory), False, "outside-repository")]
        )
    current = repository
    created: list[Path] = []
    try:
        for component in relative.parts:
            current = current / component
            if _is_reparse_point(current):
                raise ArtifactWriteRefused(
                    [Decision(str(current), False, "reparse-point-in-path")]
                )
            if os.path.lexists(current):
                if not current.is_dir():
                    raise ArtifactWriteRefused(
                        [Decision(str(current), False, "parent-is-a-file")]
                    )
                continue
            try:
                current.mkdir()
            except FileExistsError:
                # Another process populated the component between lexists and
                # mkdir. Re-check it rather than treating the race as permission.
                if _is_reparse_point(current):
                    raise ArtifactWriteRefused(
                        [Decision(str(current), False, "reparse-point-in-path")]
                    ) from None
                if not current.is_dir():
                    raise ArtifactWriteRefused(
                        [Decision(str(current), False, "parent-is-a-file")]
                    ) from None
            else:
                created.append(current)
    except BaseException:
        _remove_empty_directories(created)
        raise
    return created


def _remove_empty_directories(directories: Iterable[Path]) -> None:
    """Remove directories this write created when the write does not complete."""

    for directory in reversed(tuple(directories)):
        try:
            # Every path here was created by this write as a real directory, so
            # a link standing in its place was swapped in afterwards -- exactly
            # the race the guard refused. POSIX `rmdir` will not remove a
            # symlink, so an rmdir-only cleanup would leave the attacker's link
            # behind; Windows junctions, by contrast, need `rmdir` and reject
            # `unlink`. Both are tried so neither platform leaks one.
            if _is_reparse_point(directory):
                try:
                    os.unlink(directory)
                except OSError:
                    directory.rmdir()
            else:
                directory.rmdir()
        except OSError:
            # A non-empty directory may now belong to a concurrent successful
            # writer. Cleanup must never remove somebody else's artifact.
            pass


def _stage(destination: Path, text: str) -> Path:
    """Write ``text`` to a fresh file beside ``destination`` and return it.

    ``O_EXCL`` guarantees a brand new file rather than following an existing
    name, and ``O_NOFOLLOW`` -- where the platform has it -- refuses outright if
    that name is a symlink.
    """

    unique = f"{os.getpid()}-{uuid4().hex}"
    temporary = destination.with_name(f".{destination.name}.atom-{unique}.tmp")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_BINARY", 0)
    descriptor = os.open(temporary, flags, 0o600)
    try:
        handle = os.fdopen(descriptor, "wb")
    except BaseException:
        # fdopen did not take ownership of the descriptor, so closing it is
        # still ours to do; leaking it would hold the temporary file open.
        os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise
    try:
        with handle:
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary
