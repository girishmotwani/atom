"""A cross-process file lock, used to make appends to the event log safe.

Why this module exists
----------------------
Phase 3's spike measured what happens when several writers append to a JSONL
log at the same time without synchronisation. The result was worse than
"occasional corruption":

    unlocked        1600 written -> 1545 present,  3 visibly corrupt
    binary, 1 write 1600 written -> 1532 present,  4 visibly corrupt
    under this lock 1600 written -> 1600 present,  0 corrupt

Fifty-five entries disappeared with no trace at all. Only three arrived
damaged. That is the dangerous shape of the bug: a test asserting "every line
in the log is valid JSON" passes while entries are being silently lost.

Note the middle row. The obvious fix -- encode once and issue a single binary
``write()``, so there is nothing for the encoder to split -- lost *more* lines
than the naive version. ``O_APPEND`` on Windows does not provide the atomicity
POSIX programmers expect from it. This is recorded as B88 in the design spec as
an explicit prohibition, because the optimisation looks correct and a future
reader would otherwise reintroduce it in good faith.

See ``specs/atom-cli/phase-03-state/poc-report.md`` for the full measurements.

Design notes
------------
* The lock is taken on a **separate** file (B87), never on a byte range of the
  file being appended to -- locking a range of the log contends with the very
  append it is meant to protect.
* Acquisition **blocks with a bounded timeout and then fails** (B86a). The
  alternative -- carry on unlocked after a timeout, so the tool always makes
  progress -- would convert a loud failure into exactly the silent one above.
* The failure message explains how to recover (B86b), because refusing to work
  is only an acceptable behaviour if the developer is told how to unblock it.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from types import TracebackType

# The platform primitives are selected once, at import time, rather than on
# every acquisition. Both calls below are non-blocking: the waiting is done by
# this module's own poll loop so that the caller's timeout is honoured exactly.
# (``msvcrt.locking`` with LK_LOCK has its own fixed ten-second retry built in,
# which would quietly override a shorter timeout.)
if sys.platform == "win32":
    import msvcrt

    def _try_acquire(file_descriptor: int) -> bool:
        """Attempt to lock one byte. Returns False if someone else holds it."""
        try:
            msvcrt.locking(file_descriptor, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _release(file_descriptor: int) -> None:
        # The file position must be back where it was when the lock was taken;
        # msvcrt locks a range starting at the *current* offset.
        os.lseek(file_descriptor, 0, os.SEEK_SET)
        msvcrt.locking(file_descriptor, msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _try_acquire(file_descriptor: int) -> bool:
        """Attempt to take an exclusive lock. Returns False if unavailable."""
        try:
            fcntl.flock(file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _release(file_descriptor: int) -> None:
        fcntl.flock(file_descriptor, fcntl.LOCK_UN)


# How often to retry while waiting. Short enough that the lock is picked up
# promptly after the holder releases it, long enough not to spin the CPU.
POLL_INTERVAL_SECONDS = 0.01

DEFAULT_TIMEOUT_SECONDS = 10.0


class LockTimeout(RuntimeError):
    """Raised when the lock could not be acquired within the timeout.

    This is deliberately an error rather than a warning. See B86a: the design
    refuses to append without the lock, because doing so reintroduces silent
    data loss.
    """


class FileLock:
    """An exclusive lock held for the duration of a ``with`` block.

    Usage::

        with FileLock(project / ".atom" / "events.lock"):
            append_one_line(...)

    The lock is always released, including when the body raises -- otherwise a
    single unexpected error would wedge the tool until the process exited.
    """

    def __init__(
        self,
        path: Path | str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        poll_interval: float = POLL_INTERVAL_SECONDS,
    ) -> None:
        self.path = Path(path)
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._file_descriptor: int | None = None

    def __enter__(self) -> "FileLock":
        self.acquire()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.release()

    def acquire(self) -> None:
        """Take the lock, waiting up to ``timeout`` seconds.

        Raises:
            LockTimeout: if the lock was still held when the timeout expired.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # O_CREAT without O_TRUNC: the lock file may already exist and may even
        # be held by someone else right now. Truncating it would be a needless
        # write to a file another process is actively depending on.
        self._file_descriptor = os.open(
            self.path, os.O_RDWR | os.O_CREAT, 0o644
        )

        deadline = time.monotonic() + self.timeout
        try:
            while True:
                if _try_acquire(self._file_descriptor):
                    return

                if time.monotonic() >= deadline:
                    raise LockTimeout(self._timeout_message())

                time.sleep(self.poll_interval)
        except BaseException:
            # Nothing is holding the descriptor open on our behalf yet, so it
            # has to be closed here or a timeout would leak one per attempt.
            os.close(self._file_descriptor)
            self._file_descriptor = None
            raise

    def release(self) -> None:
        """Release the lock and close the underlying descriptor."""
        if self._file_descriptor is None:
            return

        try:
            _release(self._file_descriptor)
        finally:
            os.close(self._file_descriptor)
            self._file_descriptor = None

    def _timeout_message(self) -> str:
        """Explain the failure and how to get out of it (B86b)."""
        return (
            f"could not acquire the lock at {self.path} "
            f"after waiting {self.timeout} seconds.\n"
            "Another atom process is probably writing to the event log.\n"
            "If you are certain no other atom process is running, this is a "
            "stale lock left by a process that was killed while holding it -- "
            f"delete {self.path} and run the command again."
        )
