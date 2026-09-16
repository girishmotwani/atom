"""Tests for the cross-process file lock (B86, B86a, B86b, B87, B88).

This module exists because of D1 in the Phase 3 decisions: the spike proved the
lock works *between threads*, which is weaker evidence than it looks. A lock
that works between threads but not between processes would leave every test in
this suite passing while the safety mechanism it is testing does nothing.

So the first test here runs real subprocesses. It is slower than the rest of
the suite and that is the price of the evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import threading
import time
from pathlib import Path

import pytest

from atom.filelock import FileLock, LockTimeout

# Each worker process appends this many lines. The number is chosen to be large
# enough that an unsynchronised append would almost certainly interleave -- the
# spike lost entries at 8 writers x 200 lines -- and small enough that the test
# stays quick.
LINES_PER_WORKER = 150
WORKER_COUNT = 4


WORKER_SOURCE = textwrap.dedent(
    """
    # A deliberately minimal worker: take the lock, append, release, repeat.
    # It is a separate PROCESS rather than a thread on purpose -- that is the
    # whole point of the test that runs it.
    import json
    import sys
    from pathlib import Path

    from atom.filelock import FileLock

    lock_path = Path(sys.argv[1])
    log_path = Path(sys.argv[2])
    worker_id = sys.argv[3]
    line_count = int(sys.argv[4])

    for index in range(line_count):
        payload = json.dumps({"worker": worker_id, "index": index})
        with FileLock(lock_path, timeout=60):
            with open(log_path, "a", encoding="utf-8", newline="") as handle:
                handle.write(payload + "\\n")
    """
)


def test_lock_is_exclusive_across_real_processes(tmp_path: Path) -> None:
    """D1: the lock must hold between PROCESSES, not merely between threads.

    The spike measured the fix with threads. Threads share a process, and an
    OS-level lock could plausibly be implemented in a way that only serialises
    within one. If that were true here, the design's central safety mechanism
    would be decorative -- and a thread-based test would never reveal it.
    """
    worker_script = tmp_path / "worker.py"
    worker_script.write_text(WORKER_SOURCE, encoding="utf-8")

    lock_path = tmp_path / "events.lock"
    log_path = tmp_path / "events.jsonl"

    processes = [
        subprocess.Popen(
            [
                sys.executable,
                str(worker_script),
                str(lock_path),
                str(log_path),
                f"worker-{number}",
                str(LINES_PER_WORKER),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for number in range(WORKER_COUNT)
    ]

    for process in processes:
        _, errors = process.communicate(timeout=120)
        assert process.returncode == 0, f"worker failed: {errors}"

    lines = log_path.read_text(encoding="utf-8").splitlines()

    expected_total = WORKER_COUNT * LINES_PER_WORKER
    assert len(lines) == expected_total, (
        f"expected {expected_total} lines, found {len(lines)} -- "
        "the lock did not serialise appends across processes"
    )

    # Every line must be independently parseable. A torn write usually shows up
    # as one unparseable line rather than a missing one, so counting lines
    # alone is not sufficient evidence.
    for number, line in enumerate(lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:  # pragma: no cover - failure path
            pytest.fail(f"line {number} is corrupt: {error}: {line!r}")
        assert isinstance(record, dict)

    # And every worker's full contribution must be present, which catches the
    # failure mode the spike found most alarming: entries vanishing silently
    # rather than arriving damaged.
    for number in range(WORKER_COUNT):
        written = [line for line in lines if f'"worker-{number}"' in line]
        assert len(written) == LINES_PER_WORKER


def test_lock_can_be_taken_and_released(tmp_path: Path) -> None:
    lock_path = tmp_path / "events.lock"

    with FileLock(lock_path, timeout=5):
        pass

    # Releasing must leave the lock available again for this same process.
    with FileLock(lock_path, timeout=5):
        pass


def test_lock_creates_the_lock_file_when_absent(tmp_path: Path) -> None:
    lock_path = tmp_path / "events.lock"
    assert not lock_path.exists()

    with FileLock(lock_path, timeout=5):
        assert lock_path.exists()


def test_lock_file_is_separate_from_the_file_being_appended(tmp_path: Path) -> None:
    """B87: locking a byte range of the log itself contends with the append."""
    lock_path = tmp_path / "events.lock"
    log_path = tmp_path / "events.jsonl"

    with FileLock(lock_path, timeout=5):
        # Appending to the guarded file must work while the lock is held --
        # which is only true because the lock is on a different file.
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write("written while the lock was held\n")

    assert log_path.read_text(encoding="utf-8").strip() == "written while the lock was held"


def test_lock_is_released_when_the_body_raises(tmp_path: Path) -> None:
    """The release has to be in a `finally`, or one error wedges the tool."""
    lock_path = tmp_path / "events.lock"

    with pytest.raises(ValueError):
        with FileLock(lock_path, timeout=5):
            raise ValueError("boom")

    # If the lock leaked, this second acquisition would time out.
    with FileLock(lock_path, timeout=5):
        pass


def test_lock_times_out_when_already_held(tmp_path: Path) -> None:
    """B86a: acquisition blocks with a bounded timeout, then gives up."""
    lock_path = tmp_path / "events.lock"
    holder_has_the_lock = threading.Event()
    holder_may_release = threading.Event()

    def hold_the_lock() -> None:
        with FileLock(lock_path, timeout=30):
            holder_has_the_lock.set()
            holder_may_release.wait(timeout=30)

    holder = threading.Thread(target=hold_the_lock, daemon=True)
    holder.start()
    assert holder_has_the_lock.wait(timeout=10), "holder never acquired the lock"

    try:
        started = time.monotonic()
        with pytest.raises(LockTimeout):
            with FileLock(lock_path, timeout=0.5):
                pass
        elapsed = time.monotonic() - started

        # It must actually wait rather than failing instantly -- a lock that
        # gives up immediately turns every momentary overlap into an error.
        assert elapsed >= 0.4
        # And it must not wait much beyond the timeout it was given.
        assert elapsed < 10
    finally:
        holder_may_release.set()
        holder.join(timeout=10)


def test_timeout_message_explains_how_to_recover(tmp_path: Path) -> None:
    """B86b: failing loudly is only acceptable if it says what to do next.

    B86a's decision was to refuse to append rather than append unsafely. The
    accepted cost is that a process killed while holding the lock blocks the
    tool. This message is what pays that cost back.
    """
    lock_path = tmp_path / "events.lock"
    holder_has_the_lock = threading.Event()
    holder_may_release = threading.Event()

    def hold_the_lock() -> None:
        with FileLock(lock_path, timeout=30):
            holder_has_the_lock.set()
            holder_may_release.wait(timeout=30)

    holder = threading.Thread(target=hold_the_lock, daemon=True)
    holder.start()
    assert holder_has_the_lock.wait(timeout=10)

    try:
        with pytest.raises(LockTimeout) as caught:
            with FileLock(lock_path, timeout=0.3):
                pass

        message = str(caught.value)
        assert str(lock_path) in message, "the message must name the lock file"
        assert "0.3" in message, "the message must state how long it waited"
        # The developer needs a route out, not just a diagnosis.
        assert "delete" in message.lower() or "remove" in message.lower()
    finally:
        holder_may_release.set()
        holder.join(timeout=10)


def test_lock_does_not_truncate_an_existing_lock_file(tmp_path: Path) -> None:
    """Opening in a truncating mode would destroy a concurrent holder's file."""
    lock_path = tmp_path / "events.lock"
    lock_path.write_bytes(b"x" * 16)

    with FileLock(lock_path, timeout=5):
        pass

    assert lock_path.read_bytes() == b"x" * 16
