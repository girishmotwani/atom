"""Tests for the append-only JSONL event log (B85-B91).

The log is *diagnostic*, not authoritative. That distinction drives most of
what is tested here: a single damaged line must never make the rest of the log
unreadable, because the reason a developer opens the log is usually that
something has already gone wrong.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from atom.eventlog import EventLog, LogLine


def test_appending_then_reading_round_trips(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "events.jsonl")

    log.append({"event": "phase_started", "phase": "poc"})
    log.append({"event": "phase_completed", "phase": "poc"})

    events = [line.record for line in log.read() if line.record is not None]
    assert [event["event"] for event in events] == ["phase_started", "phase_completed"]


def test_appending_creates_the_log_and_its_directory(tmp_path: Path) -> None:
    log = EventLog(tmp_path / ".atom" / "events.jsonl")

    log.append({"event": "initialised"})

    assert (tmp_path / ".atom" / "events.jsonl").exists()


def test_each_event_is_one_line(tmp_path: Path) -> None:
    """JSONL's entire value is that a line is a unit. Indented JSON would
    silently destroy the format's crash-tolerance."""
    path = tmp_path / "events.jsonl"
    log = EventLog(path)

    log.append({"event": "a", "nested": {"deep": [1, 2, 3]}})
    log.append({"event": "b"})

    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_appending_never_rewrites_existing_content(tmp_path: Path) -> None:
    """B85: append-only. Nothing in this phase truncates or rewrites the log."""
    path = tmp_path / "events.jsonl"
    log = EventLog(path)

    log.append({"event": "first"})
    first_pass = path.read_text(encoding="utf-8")

    log.append({"event": "second"})
    second_pass = path.read_text(encoding="utf-8")

    assert second_pass.startswith(first_pass)


def test_a_timestamp_is_recorded_for_each_event(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "events.jsonl")

    log.append({"event": "phase_started"})

    record = log.read()[0].record
    assert record is not None
    assert "at" in record, "an event log without times is much less useful"


def test_the_caller_cannot_be_clobbered_by_the_timestamp(tmp_path: Path) -> None:
    """If a caller supplies its own `at`, that is the one that matters."""
    log = EventLog(tmp_path / "events.jsonl")

    log.append({"event": "imported", "at": "2020-01-01T00:00:00Z"})

    record = log.read()[0].record
    assert record is not None
    assert record["at"] == "2020-01-01T00:00:00Z"


def test_appending_uses_a_separate_lock_file(tmp_path: Path) -> None:
    """B87: the lock lives beside the log, not inside it."""
    path = tmp_path / "events.jsonl"
    log = EventLog(path)

    log.append({"event": "a"})

    assert (tmp_path / "events.lock").exists()
    # The lock file must not have collected any of the log's content.
    assert (tmp_path / "events.lock").read_bytes() == b""


# ---------------------------------------------------------------------------
# Damage tolerance (B90, B91)
# ---------------------------------------------------------------------------


def test_a_truncated_final_line_is_skipped_with_a_warning(tmp_path: Path) -> None:
    """B90: a crash mid-append leaves exactly this.

    Refusing to read the whole log because its last line is incomplete would
    turn a one-entry loss into a total one.
    """
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append({"event": "first"})
    log.append({"event": "second"})

    with open(path, "a", encoding="utf-8", newline="") as handle:
        handle.write('{"event": "third", "pha')  # killed mid-write

    lines = log.read()
    good = [line for line in lines if line.record is not None]
    damaged = [line for line in lines if line.record is None]

    assert [entry.record["event"] for entry in good] == ["first", "second"]
    assert len(damaged) == 1
    assert damaged[0].line_number == 3
    assert damaged[0].problem is not None


def test_a_corrupt_line_in_the_middle_does_not_hide_later_ones(tmp_path: Path) -> None:
    """B91: one bad line must not make the rest unreadable."""
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"event": "first"}\n'
        "}{ not json at all\n"
        '{"event": "third"}\n',
        encoding="utf-8",
    )

    lines = EventLog(path).read()
    good = [line.record["event"] for line in lines if line.record is not None]

    assert good == ["first", "third"]


def test_a_corrupt_line_reports_its_line_number(tmp_path: Path) -> None:
    """A warning that does not say *where* is not actionable."""
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"event": "first"}\n'
        '{"event": "second"}\n'
        "garbage\n"
        '{"event": "fourth"}\n',
        encoding="utf-8",
    )

    damaged = [line for line in EventLog(path).read() if line.record is None]

    assert len(damaged) == 1
    assert damaged[0].line_number == 3


def test_a_json_array_line_is_treated_as_damaged(tmp_path: Path) -> None:
    """The same finding as the state file: valid JSON, invalid event.

    `[1,2,3]` parses without complaint. If the log reader only guarded against
    JSONDecodeError, this would be handed to callers as an event and fail on
    the first `.get()`.
    """
    path = tmp_path / "events.jsonl"
    path.write_text('{"event": "first"}\n[1, 2, 3]\n', encoding="utf-8")

    lines = EventLog(path).read()

    assert [line.record is None for line in lines] == [False, True]


def test_blank_lines_are_ignored_rather_than_reported(tmp_path: Path) -> None:
    """Whitespace is not damage -- reporting it would train people to ignore
    the warnings that matter."""
    path = tmp_path / "events.jsonl"
    path.write_text('{"event": "first"}\n\n   \n{"event": "second"}\n', encoding="utf-8")

    lines = EventLog(path).read()

    assert len(lines) == 2
    assert all(line.record is not None for line in lines)


def test_reading_a_log_that_does_not_exist_yet_is_not_an_error(tmp_path: Path) -> None:
    """A project that has just been initialised has no events. That is normal."""
    assert EventLog(tmp_path / "events.jsonl").read() == []


def test_reading_does_not_take_the_lock(tmp_path: Path) -> None:
    """B102's sibling: reading must stay possible when writing is blocked.

    The lock exists to serialise *appends*. Making readers take it too would
    mean a stuck writer could block `atom status`, which is the one command a
    developer needs when things are stuck.
    """
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append({"event": "first"})

    from atom.filelock import FileLock

    with FileLock(tmp_path / "events.lock", timeout=5):
        # Held by "another process" -- reading must still work.
        assert len(log.read()) == 1


# ---------------------------------------------------------------------------
# The reason the lock is there at all (B86, B88)
# ---------------------------------------------------------------------------


CONCURRENT_WRITER = textwrap.dedent(
    """
    import sys
    from pathlib import Path

    from atom.eventlog import EventLog

    log = EventLog(Path(sys.argv[1]))
    worker = sys.argv[2]
    for index in range(int(sys.argv[3])):
        log.append({"event": "tick", "worker": worker, "index": index})
    """
)


def test_concurrent_appends_from_real_processes_lose_nothing(tmp_path: Path) -> None:
    """B86/B88 end-to-end, at the level callers actually use.

    ``test_filelock`` proves the lock primitive serialises across processes.
    This proves ``EventLog.append`` actually uses it -- a distinction worth a
    separate test, because the primitive being correct and the caller taking it
    are independent failures.
    """
    writer_script = tmp_path / "writer.py"
    writer_script.write_text(CONCURRENT_WRITER, encoding="utf-8")
    path = tmp_path / "events.jsonl"

    workers = 4
    per_worker = 120

    processes = [
        subprocess.Popen(
            [sys.executable, str(writer_script), str(path), f"w{number}", str(per_worker)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for number in range(workers)
    ]
    for process in processes:
        _, errors = process.communicate(timeout=120)
        assert process.returncode == 0, f"writer failed: {errors}"

    lines = EventLog(path).read()
    damaged = [line for line in lines if line.record is None]

    assert damaged == [], f"{len(damaged)} damaged lines: {damaged[:3]}"
    assert len(lines) == workers * per_worker

    for number in range(workers):
        mine = [line for line in lines if line.record["worker"] == f"w{number}"]
        assert len(mine) == per_worker
