"""Reading and writing Atom's state files safely.

Two problems this module exists to solve, both measured rather than assumed
(see ``specs/atom-cli/phase-03-state/poc-report.md``):

1. **Valid JSON is not valid state.** The spike fed five corruption shapes to
   ``json.loads``. Four raised ``JSONDecodeError``. The fifth -- a JSON array --
   parsed perfectly and returned a ``list``. Code guarding only against
   ``JSONDecodeError`` lets that through, and the failure resurfaces later as an
   ``AttributeError`` a long way from the cause. So reads validate *shape*, not
   just syntax (B74).

2. **``os.replace`` can fail.** The write-temp-then-rename recipe is usually
   quoted as though the rename cannot fail. On Windows it raises
   ``PermissionError`` whenever any other process holds the destination open --
   including a reader. ``atom status`` running during a phase transition is
   exactly that situation. So replaces are retried (B80), and a write that
   ultimately fails keeps the developer's unsaved state and tells them where it
   is (B83a-B83c).

The three error types are distinct because they need different responses:
missing means "not initialised", corrupt means "something went wrong here is
what", and a failed write means "your work is in this other file".
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

# The suffix used while a file is being written. Swept at startup (B81).
TEMP_SUFFIX = ".tmp"

# The suffix used to preserve state that could not be written. Deliberately
# NOT the temp suffix: B81's sweep would otherwise delete the very file that
# B83a's error message has just told the developer to go and look at.
UNSAVED_SUFFIX = ".unsaved"

DEFAULT_RETRIES = 10
DEFAULT_BACKOFF_SECONDS = 0.05


class StateFileError(Exception):
    """Base class for every problem with an Atom state file."""


class StateFileMissing(StateFileError):
    """The file is not there at all -- the project is probably not initialised."""


class StateFileCorrupt(StateFileError):
    """The file exists but does not contain usable state."""


class StateWriteFailed(StateFileError):
    """The state could not be persisted. Carries recovery instructions."""


# A diagnosis without an action leaves the developer stuck. The parenthetical is
# the part that makes `--force` safe to suggest: `.atom/` holds only the project
# record, so re-creating it costs a phase marker, not any spike or spec.
_RECOVERY_ADVICE = (
    "If there is a `.unsaved` file beside it, that holds your last known state -- "
    "move it over this file.\n"
    "Otherwise run `atom init --force` to start the project record again; your "
    "spikes and specs are not touched."
)


@dataclass(frozen=True)
class SweptFile:
    """One leftover temp file removed at startup, reported so it is not silent."""

    path: Path
    size_in_bytes: int


def read_json(path: Path, *, required_keys: Sequence[str] = ()) -> dict[str, Any]:
    """Read and validate a JSON object from ``path``.

    Args:
        path: The file to read.
        required_keys: Keys that must be present. A missing one is corruption,
            not a caller's problem to discover later.

    Returns:
        The parsed object.

    Raises:
        StateFileMissing: The file does not exist.
        StateFileCorrupt: The file exists but is unparseable, is not a JSON
            object, or is missing a required key.
    """
    if not path.exists():
        raise StateFileMissing(
            f"{path} does not exist.\n"
            "This project does not look initialised -- run `atom init` first."
        )

    # Read fully and close immediately (B78). Holding this handle open would
    # make a concurrent os.replace fail on Windows, which is precisely the
    # failure B80 then has to retry around. Not holding it is the cheaper fix.
    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise StateFileCorrupt(f"{path} could not be read: {error}") from error

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise StateFileCorrupt(
            f"{path} is not valid JSON: {error}.\n"
            "It was probably damaged by a process that stopped mid-write.\n"
            f"{_RECOVERY_ADVICE}"
        ) from error

    # The check that the spike showed is not optional. `[1, 2, 3]` reaches this
    # line having parsed without complaint.
    if not isinstance(parsed, dict):
        raise StateFileCorrupt(
            f"{path} does not contain Atom state: "
            f"expected a JSON object, found a {type(parsed).__name__}.\n"
            f"{_RECOVERY_ADVICE}"
        )

    missing = [key for key in required_keys if key not in parsed]
    if missing:
        raise StateFileCorrupt(
            f"{path} is missing required {_pluralise('key', len(missing))}: "
            f"{', '.join(sorted(missing))}."
        )

    return parsed


def write_json(
    path: Path,
    payload: dict[str, Any],
    *,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF_SECONDS,
) -> None:
    """Write ``payload`` to ``path`` atomically, retrying a blocked replace.

    The sequence is: serialise fully in memory, write to a temp file, flush and
    fsync it, then ``os.replace`` it over the destination (B79). The original is
    never truncated or removed first, so a crash at any point leaves the old
    file intact (B84) -- which the spike confirmed by killing a real process
    mid-write.

    Args:
        path: Destination file.
        payload: The object to store.
        retries: How many times to retry a replace blocked by another process.
        backoff: Seconds to wait between attempts.

    Raises:
        StateWriteFailed: The replace did not succeed within ``retries``. The
            serialised state is preserved alongside the destination with an
            ``.unsaved`` suffix, and the message says where.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Serialise before touching the filesystem: a payload that cannot be
    # serialised should not leave a temp file behind.
    serialised = json.dumps(payload, indent=2, sort_keys=True) + "\n"

    temporary_path = path.with_suffix(path.suffix + TEMP_SUFFIX)
    _write_and_sync(temporary_path, serialised)

    last_error: OSError | None = None
    for attempt in range(retries):
        try:
            os.replace(temporary_path, path)
            return
        except PermissionError as error:
            # Expected on Windows whenever another process holds the
            # destination open. Retrying is the documented behaviour, not a
            # workaround -- see B80.
            last_error = error
            if attempt < retries - 1:
                time.sleep(backoff)
        except OSError as error:  # pragma: no cover - platform dependent
            last_error = error
            break

    # Every retry is spent. Preserve the work under a name the startup sweep
    # will not touch (B83b), then fail loudly with a way out (B83a).
    unsaved_path = path.with_suffix(path.suffix + UNSAVED_SUFFIX)
    rescued = True
    try:
        os.replace(temporary_path, unsaved_path)
    except OSError:
        # Whatever is blocking the destination is blocking this rename too. The
        # work still exists, but only as a `.tmp` file -- which sweep_temp_files
        # deletes on the next run. Saying "nothing was lost" here would be a
        # promise Atom cannot keep, so the message changes to match reality.
        unsaved_path = temporary_path
        rescued = False

    if rescued:
        fate = f"Your unsaved state has been kept at {unsaved_path} -- nothing was lost."
    else:
        fate = (
            f"Your unsaved state is still at {unsaved_path}, but that file will be "
            "removed the next time an `atom` command runs. Copy it somewhere else "
            "now if you want to keep it."
        )

    raise StateWriteFailed(
        f"could not save state to {path} after {retries} attempts: {last_error}.\n"
        "Another process is holding that file open.\n"
        f"{fate}\n"
        "Close whatever is holding the file (another `atom` run, an editor, or a "
        "file explorer preview), then either re-run this command or move that "
        f"file over {path} yourself."
    )


def sweep_temp_files(directory: Path) -> list[SweptFile]:
    """Remove leftover temp files from a previous crash (B81).

    A ``.tmp`` file in the state directory means a process died between writing
    the temp file and replacing the destination. The spike left a 13 KB one
    behind after a single killed process; they accumulate.

    ``.unsaved`` files are deliberately left alone (B83c) -- they hold state a
    developer has been told to go and recover.

    Returns:
        The files removed, so the caller can report them rather than being
        silent about evidence of a crash (B82).
    """
    if not directory.is_dir():
        return []

    swept: list[SweptFile] = []
    for candidate in sorted(directory.glob(f"*{TEMP_SUFFIX}")):
        try:
            size = candidate.stat().st_size
            candidate.unlink()
        except OSError:  # pragma: no cover - another process got there first
            continue
        swept.append(SweptFile(path=candidate, size_in_bytes=size))

    return swept


def _write_and_sync(path: Path, contents: str) -> None:
    """Write text and force it to disk before the caller relies on it.

    Without the fsync, the replace could succeed while the temp file's contents
    are still only in the OS cache -- so a power loss would leave a correctly
    named file full of nothing.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(contents)
        handle.flush()
        os.fsync(handle.fileno())


def _pluralise(word: str, count: int) -> str:
    return word if count == 1 else f"{word}s"
