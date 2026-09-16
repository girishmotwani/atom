"""Tests for state file storage: validation, atomic writes, recovery.

Covers B74-B84 and B83a-B83c.

Several tests here are Windows-specific and say so. That is not a gap -- the
behaviours they cover exist *because* Windows refuses an ``os.replace`` over an
open file, which POSIX permits. On POSIX those code paths are unreachable by
construction, and a test pretending otherwise would be theatre.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from atom.storage import (
    StateFileCorrupt,
    StateFileMissing,
    StateWriteFailed,
    read_json,
    sweep_temp_files,
    write_json,
)

windows_only = pytest.mark.skipif(
    sys.platform != "win32",
    reason="POSIX allows os.replace over an open file, so this path cannot be reached",
)


# ---------------------------------------------------------------------------
# Reading: validation, not merely parsing (B74-B77)
# ---------------------------------------------------------------------------


def test_reading_a_missing_file_says_it_is_missing(tmp_path: Path) -> None:
    """B77: missing and corrupt are different problems with different answers."""
    with pytest.raises(StateFileMissing) as caught:
        read_json(tmp_path / "state.json")

    message = str(caught.value)
    assert "state.json" in message
    assert "atom init" in message, "a missing file means the project is not initialised"


def test_reading_unparseable_json_reports_corruption(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"phase": "tdd"', encoding="utf-8")  # truncated

    with pytest.raises(StateFileCorrupt) as caught:
        read_json(path)

    assert str(path) in str(caught.value)


def test_reading_valid_json_of_the_wrong_type_is_still_corruption(tmp_path: Path) -> None:
    """B74: the finding that justified validating shape, not just syntax.

    The spike fed five corruption shapes to ``json.loads``. Four raised
    JSONDecodeError. This one -- a JSON array -- parsed perfectly and returned
    a list. A ``try/except JSONDecodeError`` would have let it straight
    through, and the failure would have surfaced much later as an AttributeError
    on ``.get()``, a long way from the actual cause.
    """
    path = tmp_path / "state.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(StateFileCorrupt) as caught:
        read_json(path)

    message = str(caught.value)
    # B76: say what was expected and what was found -- never a bare KeyError.
    assert "object" in message.lower()
    assert "list" in message.lower()


@pytest.mark.parametrize(
    "contents,described_as",
    [
        ('"just a string"', "str"),
        ("42", "int"),
        ("null", "NoneType"),
        ("true", "bool"),
    ],
)
def test_other_valid_json_scalars_are_also_rejected(
    tmp_path: Path, contents: str, described_as: str
) -> None:
    """The list case is the famous one, but it is not the only one."""
    path = tmp_path / "state.json"
    path.write_text(contents, encoding="utf-8")

    with pytest.raises(StateFileCorrupt) as caught:
        read_json(path)

    assert described_as in str(caught.value)


def test_an_empty_file_is_corruption_not_emptiness(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("", encoding="utf-8")

    with pytest.raises(StateFileCorrupt):
        read_json(path)


def test_a_file_of_nul_bytes_is_corruption(tmp_path: Path) -> None:
    """A known crash artefact: the filesystem allocated the block but the
    write never landed, leaving a run of NULs."""
    path = tmp_path / "state.json"
    path.write_bytes(b"\x00" * 64)

    with pytest.raises(StateFileCorrupt):
        read_json(path)


def test_a_missing_required_key_is_corruption_and_names_the_key(tmp_path: Path) -> None:
    """B75: required keys are part of the shape, not a caller's problem."""
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"phase": "tdd"}), encoding="utf-8")

    with pytest.raises(StateFileCorrupt) as caught:
        read_json(path, required_keys=("phase", "status"))

    assert "status" in str(caught.value)


def test_reading_a_well_formed_file_returns_the_object(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    payload = {"phase": "tdd", "status": "in_progress"}
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert read_json(path, required_keys=("phase", "status")) == payload


@windows_only
def test_reading_does_not_keep_the_file_open(tmp_path: Path) -> None:
    """B78: a held handle -- even a read-only one -- breaks a concurrent replace.

    This is the behaviour that makes B80's retries likely to succeed rather
    than merely present. On Windows it is directly observable: if ``read_json``
    leaked a handle, the replace below would raise PermissionError.
    """
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"phase": "spec"}), encoding="utf-8")

    read_json(path)

    replacement = tmp_path / "other.json"
    replacement.write_text(json.dumps({"phase": "tdd"}), encoding="utf-8")
    os.replace(replacement, path)  # would raise if a handle had leaked

    assert read_json(path) == {"phase": "tdd"}


# ---------------------------------------------------------------------------
# Writing: temp, fsync, replace -- and the replace can fail (B79-B84)
# ---------------------------------------------------------------------------


def test_writing_then_reading_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    payload = {"phase": "tdd", "status": "in_progress", "step": 4}

    write_json(path, payload)

    assert read_json(path) == payload


def test_writing_creates_the_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / ".atom" / "state.json"

    write_json(path, {"phase": "poc"})

    assert path.exists()


def test_writing_leaves_no_temp_file_behind_on_success(tmp_path: Path) -> None:
    """B79's temp file is an implementation detail, not a deliverable."""
    path = tmp_path / "state.json"

    write_json(path, {"phase": "poc"})

    assert list(tmp_path.glob("*.tmp")) == []


def test_writing_replaces_rather_than_truncating(tmp_path: Path) -> None:
    """B79/B84: the destination must never be opened for writing directly.

    If the implementation truncated the destination and then wrote into it, a
    crash between the two would destroy the original. Writing elsewhere and
    replacing is what the spike confirmed survives a killed process.
    """
    path = tmp_path / "state.json"
    write_json(path, {"phase": "poc", "status": "done"})
    original_inode_ish = path.stat().st_mtime_ns

    time.sleep(0.01)
    write_json(path, {"phase": "spec", "status": "in_progress"})

    assert read_json(path)["phase"] == "spec"
    assert path.stat().st_mtime_ns != original_inode_ish


@windows_only
def test_writing_retries_while_the_destination_is_held_open(tmp_path: Path) -> None:
    """B80: the replace fails deterministically when a reader is attached.

    The spike confirmed this raises PermissionError on Windows. A single
    unguarded ``os.replace`` would therefore fail during ordinary use -- for
    example when ``atom status`` reads state while a phase transition writes it.
    """
    path = tmp_path / "state.json"
    write_json(path, {"phase": "poc"})

    holder_is_ready = threading.Event()
    release_the_handle = threading.Event()

    def hold_the_file_open() -> None:
        with open(path, "r", encoding="utf-8") as handle:
            handle.read()
            holder_is_ready.set()
            release_the_handle.wait(timeout=30)

    holder = threading.Thread(target=hold_the_file_open, daemon=True)
    holder.start()
    assert holder_is_ready.wait(timeout=10)

    # Let the write start and fail at least once, then release the handle.
    def release_shortly() -> None:
        time.sleep(0.3)
        release_the_handle.set()

    threading.Thread(target=release_shortly, daemon=True).start()

    write_json(path, {"phase": "spec"}, retries=100, backoff=0.02)

    holder.join(timeout=10)
    assert read_json(path)["phase"] == "spec"


@windows_only
def test_a_write_that_cannot_succeed_fails_loudly(tmp_path: Path) -> None:
    """B83: never report success for work whose record was not persisted."""
    path = tmp_path / "state.json"
    write_json(path, {"phase": "poc"})

    holder_is_ready = threading.Event()
    release_the_handle = threading.Event()

    def hold_the_file_open() -> None:
        with open(path, "r", encoding="utf-8") as handle:
            handle.read()
            holder_is_ready.set()
            release_the_handle.wait(timeout=30)

    holder = threading.Thread(target=hold_the_file_open, daemon=True)
    holder.start()
    assert holder_is_ready.wait(timeout=10)

    try:
        with pytest.raises(StateWriteFailed) as caught:
            write_json(path, {"phase": "spec"}, retries=3, backoff=0.01)

        message = str(caught.value)
        # B83a: an error that diagnoses without offering a route out is half a
        # feature. The developer's unsaved work has to be findable.
        assert str(path) in message
        assert ".unsaved" in message

        # B83b: the unsaved state is kept, under a name B81 will not sweep.
        unsaved = path.with_suffix(path.suffix + ".unsaved")
        assert unsaved.exists()
        assert json.loads(unsaved.read_text(encoding="utf-8")) == {"phase": "spec"}

        # B84: and the original is untouched.
        assert json.loads(path.read_text(encoding="utf-8")) == {"phase": "poc"}
    finally:
        release_the_handle.set()
        holder.join(timeout=10)


# ---------------------------------------------------------------------------
# Sweeping leftovers (B81, B82) -- and not sweeping the recovery file (B83c)
# ---------------------------------------------------------------------------


def test_sweeping_removes_leftover_temp_files(tmp_path: Path) -> None:
    """B81: a leftover .tmp is the fingerprint of a previous crash."""
    leftover = tmp_path / "state.json.tmp"
    leftover.write_text("partial", encoding="utf-8")

    swept = sweep_temp_files(tmp_path)

    assert not leftover.exists()
    assert [entry.path for entry in swept] == [leftover]


def test_sweeping_reports_what_it_removed(tmp_path: Path) -> None:
    """B82: a crash the developer did not notice is worth one line of output."""
    leftover = tmp_path / "state.json.tmp"
    leftover.write_text("x" * 1234, encoding="utf-8")

    swept = sweep_temp_files(tmp_path)

    assert len(swept) == 1
    assert swept[0].size_in_bytes == 1234


def test_sweeping_leaves_unsaved_recovery_files_alone(tmp_path: Path) -> None:
    """B83c -- and the reason B83b renames instead of leaving a .tmp in place.

    This is the collision the design review caught: B83a tells the developer to
    go and look at the file holding their unsaved state. If that file were a
    .tmp, the next atom invocation would sweep it away before they got there.
    Atom does not delete the only copy of someone's work on their behalf.
    """
    unsaved = tmp_path / "state.json.unsaved"
    unsaved.write_text(json.dumps({"phase": "spec"}), encoding="utf-8")

    swept = sweep_temp_files(tmp_path)

    assert unsaved.exists(), "the recovery file must survive the sweep"
    assert swept == []


def test_sweeping_leaves_real_state_files_alone(tmp_path: Path) -> None:
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"phase": "poc"}), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"module": "example"}), encoding="utf-8")

    sweep_temp_files(tmp_path)

    assert state.exists()
    assert config.exists()


def test_sweeping_an_absent_directory_is_not_an_error(tmp_path: Path) -> None:
    assert sweep_temp_files(tmp_path / "nope") == []
