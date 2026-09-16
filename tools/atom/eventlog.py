"""The append-only JSONL event log.

The log records what Atom did and when, so a developer returning to a project
can see how it got into its current state. It is **diagnostic, not
authoritative** -- the real state lives in ``state.json``. That distinction is
why a damaged line is skipped with a warning rather than treated as fatal: the
usual reason to open the log is that something has already gone wrong, and a
reader that refuses to work under exactly those conditions is useless.

Two measured facts shape this module:

* **Unlocked concurrent appends silently lose entries.** Not corrupt them --
  lose them. The spike wrote 1600 lines from eight writers and found 1545, of
  which only 3 were visibly damaged. So every append takes an OS-level lock
  (B86), on a separate lock file (B87).

* **Binary single-write appends are not a substitute for the lock.** The spike
  measured that supposed optimisation and it lost *more* lines than the naive
  version (68 versus 55). B88 forbids it explicitly, because it looks correct
  and someone would otherwise reintroduce it in good faith.

Reads deliberately do **not** take the lock. The lock serialises appends; making
readers wait for it would let one stuck writer block ``atom status``, which is
the command a developer reaches for when things are stuck.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from atom.filelock import FileLock

# Where the lock lives relative to the log. A separate file, never a byte range
# of the log itself -- locking part of the file being appended to contends with
# the append (B87).
LOCK_SUFFIX = ".lock"


@dataclass(frozen=True)
class LogLine:
    """One line of the log, whether or not it survived intact.

    A damaged line is represented rather than dropped so callers can warn about
    it. Silently skipping damage would hide the very crash the developer is
    trying to understand.
    """

    line_number: int
    raw: str
    record: dict[str, Any] | None
    problem: str | None = None

    @property
    def is_damaged(self) -> bool:
        return self.record is None


class EventLog:
    """An append-only log of what Atom did to a project."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        # `events.jsonl` -> `events.lock`, matching the directory layout in the
        # design spec. Note this REPLACES the suffix rather than appending to
        # it: `with_suffix(self.path.suffix + LOCK_SUFFIX)` would yield
        # `events.jsonl.lock` instead, which is the same idea with a name the
        # spec does not use.
        self.lock_path = self.path.with_suffix(LOCK_SUFFIX)

    def append(self, event: dict[str, Any]) -> None:
        """Append one event as a single JSON line, under an exclusive lock.

        Args:
            event: The event to record. A timestamp is added under ``at``
                unless the caller supplied one.

        Raises:
            LockTimeout: Another process held the lock for longer than the
                timeout. The event is **not** written -- see B86a. Appending
                without the lock would reintroduce silent data loss, so
                refusing is the safer failure.
        """
        # Default the timestamp without overwriting a caller's own value: an
        # imported or replayed event knows its time better than we do.
        record = {"at": _now_in_utc(), **event}

        # Serialise before taking the lock. Time spent holding the lock is time
        # every other process spends waiting, and json.dumps can raise -- doing
        # it inside would mean taking and releasing the lock for nothing.
        line = json.dumps(record, sort_keys=True) + "\n"

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with FileLock(self.lock_path):
            # Opened and closed inside the lock so the handle never outlives
            # it. newline="" keeps the separator exactly the one byte written
            # above -- on Windows, text mode would silently expand it to CRLF
            # and change the byte count of every line.
            with open(self.path, "a", encoding="utf-8", newline="") as handle:
                handle.write(line)

    def read(self) -> list[LogLine]:
        """Read every line, tolerating damage.

        A missing log is not an error -- a freshly initialised project has no
        events yet.

        Returns:
            One ``LogLine`` per non-blank line. Damaged lines have
            ``record=None`` and a populated ``problem``, so the caller can warn
            about them (B90, B91) rather than pretend the log is shorter than
            it is.
        """
        if not self.path.exists():
            return []

        # Read fully, close immediately -- the same discipline as the state
        # files (B78). A held handle breaks a concurrent replace on Windows.
        raw_text = self.path.read_text(encoding="utf-8", errors="replace")

        lines: list[LogLine] = []
        for line_number, raw in enumerate(raw_text.splitlines(), start=1):
            if not raw.strip():
                # Whitespace is not damage. Reporting it would train people to
                # ignore the warnings that do matter.
                continue
            lines.append(_parse_one_line(line_number, raw))

        return lines

    def read_valid(self) -> list[dict[str, Any]]:
        """Just the events that survived, for callers that do not warn."""
        return [line.record for line in self.read() if line.record is not None]


def _parse_one_line(line_number: int, raw: str) -> LogLine:
    """Turn one raw line into a LogLine, classifying damage rather than raising."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        # The overwhelmingly common cause is a process killed mid-append, which
        # leaves exactly one truncated line at the end of the file (B90).
        return LogLine(
            line_number=line_number,
            raw=raw,
            record=None,
            problem=f"not valid JSON: {error}",
        )

    # The same trap as the state file: `[1, 2, 3]` parses perfectly and is not
    # an event. Guarding only against JSONDecodeError would hand this to the
    # caller and fail later on the first `.get()`.
    if not isinstance(parsed, dict):
        return LogLine(
            line_number=line_number,
            raw=raw,
            record=None,
            problem=f"expected a JSON object, found a {type(parsed).__name__}",
        )

    return LogLine(line_number=line_number, raw=raw, record=parsed)


def _now_in_utc() -> str:
    """An ISO-8601 timestamp in UTC, so logs from different machines sort."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
