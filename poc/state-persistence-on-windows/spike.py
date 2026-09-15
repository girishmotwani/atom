"""Spike: is 'ordinary JSON persistence' actually safe on Windows?

Phase 3 plans to persist state with the obvious recipe -- write a temp file,
then os.replace it over the destination -- and to keep an append-only JSONL
event log. The phase plan called this "ordinary JSON persistence" with "no
technical uncertainty", which is the same sentence that was wrong about Phase 2.

This measures five predictions rather than reasoning about them. See
specs/atom-cli/phase-03-state/poc-brief.md for the predictions as recorded
BEFORE this was run.

Throwaway code. Clarity over structure; every check prints what it actually
observed so the report can quote real output rather than a summary of it.

Exit codes follow Atom's own convention:
    0  every prediction held
    1  at least one prediction was refuted  (a result, not a failure)
    2  the spike could not tell
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

# Each check appends (prediction_id, held?, one-line evidence).
RESULTS: list[tuple[str, bool, str]] = []


def record(prediction: str, held: bool, evidence: str) -> None:
    """Record an outcome and print it immediately, so a crash still leaves a trail."""
    RESULTS.append((prediction, held, evidence))
    verdict = "CONFIRMED" if held else "REFUTED"
    print(f"  {prediction}: {verdict} -- {evidence}")


# ---------------------------------------------------------------------------
# P1 -- os.replace over a destination that another process holds open
#
# The write-temp-then-replace recipe assumes the replace cannot fail. On POSIX
# that is true even with readers attached. Windows keeps files locked while
# open, and Python's open() does not pass FILE_SHARE_DELETE, so the prediction
# is that this raises PermissionError.
# ---------------------------------------------------------------------------


def check_replace_while_open(workspace: Path) -> None:
    print("\nP1: os.replace while the destination is open for reading")

    destination = workspace / "state.json"
    destination.write_text(json.dumps({"phase": "old"}), encoding="utf-8")

    temporary = workspace / "state.json.tmp"
    temporary.write_text(json.dumps({"phase": "new"}), encoding="utf-8")

    # Hold the destination open the way a concurrent `atom status` would.
    reader = open(destination, "r", encoding="utf-8")
    try:
        try:
            os.replace(temporary, destination)
        except PermissionError as error:
            record("P1", True, f"replace failed while a reader was attached: {type(error).__name__}")
            return
        except OSError as error:
            record("P1", True, f"replace failed with {type(error).__name__}: {error}")
            return
    finally:
        reader.close()

    # It succeeded. Verify the content really changed rather than assuming it.
    content = json.loads(destination.read_text(encoding="utf-8"))
    record("P1", False, f"replace SUCCEEDED with a reader attached; destination now {content}")


def check_replace_while_open_for_writing(workspace: Path) -> None:
    """Not a prediction -- a follow-up that only matters if P1 was refuted.

    A reader is the common case, but a second writer is the dangerous one. This
    is measured separately so the report can distinguish them.
    """
    print("\nP1b: os.replace while the destination is open for WRITING (follow-up)")

    destination = workspace / "state_w.json"
    destination.write_text(json.dumps({"phase": "old"}), encoding="utf-8")

    temporary = workspace / "state_w.json.tmp"
    temporary.write_text(json.dumps({"phase": "new"}), encoding="utf-8")

    writer = open(destination, "a", encoding="utf-8")
    try:
        os.replace(temporary, destination)
        record("P1b", False, "replace SUCCEEDED even with a writer attached")
    except OSError as error:
        record("P1b", True, f"replace failed with a writer attached: {type(error).__name__}")
    finally:
        writer.close()


# ---------------------------------------------------------------------------
# P2 -- concurrent appends to the JSONL event log
#
# If appends interleave, the event log silently corrupts under exactly the
# conditions Atom will create: several tools logging during one run. Threads
# within one process share a file object, so this uses SEPARATE file handles to
# model separate writers honestly.
# ---------------------------------------------------------------------------


def check_concurrent_appends(workspace: Path) -> None:
    print("\nP2: concurrent appends to a JSONL log")

    log = workspace / "events.jsonl"
    log.touch()

    writers = 8
    lines_each = 200
    # Each writer emits a distinctive fixed-width payload. A torn write shows up
    # as a line whose length or marker is wrong, which is easy to detect.
    payload_width = 300

    def append_many(writer_id: int) -> None:
        # A fresh handle per writer -- sharing one would test Python's buffer,
        # not the filesystem.
        with open(log, "a", encoding="utf-8") as handle:
            for sequence in range(lines_each):
                marker = f"{writer_id:02d}"
                body = marker * (payload_width // 2)
                handle.write(json.dumps({"w": writer_id, "n": sequence, "body": body}) + "\n")
                handle.flush()

    threads = [threading.Thread(target=append_many, args=(writer_id,)) for writer_id in range(writers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    expected = writers * lines_each
    raw_lines = log.read_text(encoding="utf-8").splitlines()

    corrupt = 0
    for line in raw_lines:
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            corrupt += 1
            continue
        # A line that parses can still be torn if two payloads merged.
        marker = f"{parsed['w']:02d}"
        if parsed["body"] != marker * (payload_width // 2):
            corrupt += 1

    if corrupt == 0 and len(raw_lines) == expected:
        record("P2", True, f"{expected} concurrent appends, 0 corrupt lines")
    else:
        record("P2", False, f"expected {expected} clean lines, got {len(raw_lines)} lines with {corrupt} corrupt")


# ---------------------------------------------------------------------------
# P2b / P2c -- follow-ups that only exist because P2 was refuted
#
# P2 failing raises two questions the design cannot proceed without:
#   P2b: is Python's text-mode encoding to blame? If so, binary mode fixes it
#        cheaply and no lock is needed.
#   P2c: if binary mode does not fix it, does an OS-level file lock?
#
# P2c matters most. "Use a lock" is a recommendation; without measuring it, the
# design would be built on a guess -- which is the failure mode this framework
# exists to prevent. A recommendation that has not been run is not evidence.
# ---------------------------------------------------------------------------


def _append_concurrently(log: Path, open_handle, encode, lock_path: Path | None = None) -> tuple[int, int]:
    """Drive 8 writers at one log and return (line_count, corrupt_count)."""
    writers, lines_each, payload_width = 8, 200, 300

    def append_many(writer_id: int) -> None:
        marker = f"{writer_id:02d}"
        body = marker * (payload_width // 2)

        def write_one(handle, sequence: int) -> None:
            line = json.dumps({"w": writer_id, "n": sequence, "body": body}) + "\n"
            handle.write(encode(line))
            handle.flush()

        if lock_path is None:
            with open_handle(log) as handle:
                for sequence in range(lines_each):
                    write_one(handle, sequence)
            return

        # The lock lives in its own file. Locking a byte range of the file being
        # appended to fights with the append itself.
        with open(lock_path, "r+b") as lock_handle:
            for sequence in range(lines_each):
                _acquire(lock_handle)
                try:
                    with open_handle(log) as handle:
                        write_one(handle, sequence)
                finally:
                    _release(lock_handle)

    threads = [threading.Thread(target=append_many, args=(writer_id,)) for writer_id in range(writers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    raw_lines = log.read_bytes().decode("utf-8", errors="replace").splitlines()
    corrupt = 0
    for line in raw_lines:
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            corrupt += 1
            continue
        if parsed["body"] != f"{parsed['w']:02d}" * (payload_width // 2):
            corrupt += 1
    return len(raw_lines), corrupt


if sys.platform == "win32":
    import msvcrt

    def _acquire(handle) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)

    def _release(handle) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _acquire(handle) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)

    def _release(handle) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def check_binary_appends(workspace: Path) -> None:
    print("\nP2b: does binary-mode single-write appending avoid the corruption?")

    log = workspace / "events_binary.jsonl"
    log.touch()
    count, corrupt = _append_concurrently(log, lambda p: open(p, "ab"), lambda s: s.encode("utf-8"))

    expected = 8 * 200
    if count == expected and corrupt == 0:
        record("P2b", True, f"binary mode was clean: {count} lines, 0 corrupt")
    else:
        record("P2b", False, f"binary mode ALSO corrupts: {count} lines ({expected - count} lost), {corrupt} corrupt")


def check_locked_appends(workspace: Path) -> None:
    print("\nP2c: does an OS-level file lock make appending safe?")

    log = workspace / "events_locked.jsonl"
    log.touch()
    lock_path = workspace / "events.lock"
    lock_path.touch()

    count, corrupt = _append_concurrently(
        log, lambda p: open(p, "ab"), lambda s: s.encode("utf-8"), lock_path=lock_path
    )

    expected = 8 * 200
    if count == expected and corrupt == 0:
        record("P2c", True, f"an OS file lock produced a clean log: {count} lines, 0 corrupt")
    else:
        record("P2c", False, f"even WITH a lock: {count} lines ({expected - count} lost), {corrupt} corrupt")


# ---------------------------------------------------------------------------
# P3 -- the shapes corruption actually takes
#
# The plan promises "a clear error rather than a stack trace". That is only one
# except clause if every corruption shape raises the same exception.
# ---------------------------------------------------------------------------


def check_corruption_shapes(workspace: Path) -> None:
    print("\nP3: what exception each corruption shape raises")

    shapes = {
        "truncated": '{"phase": "des',
        "empty": "",
        "nul_bytes": "\x00" * 64,
        "whitespace": "   \n\t ",
        "valid_json_wrong_type": "[1, 2, 3]",
    }

    exceptions_seen: dict[str, str] = {}
    for name, content in shapes.items():
        path = workspace / f"corrupt_{name}.json"
        path.write_text(content, encoding="utf-8")
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:  # noqa: BLE001 -- the point is to see what escapes
            exceptions_seen[name] = type(error).__name__
            continue
        # No exception. That is its own finding: the file is readable but wrong.
        exceptions_seen[name] = f"NO EXCEPTION, parsed as {type(loaded).__name__}"

    for name, outcome in exceptions_seen.items():
        print(f"      {name:<22} -> {outcome}")

    decode_errors = {name for name, outcome in exceptions_seen.items() if outcome == "JSONDecodeError"}
    all_names = set(shapes)

    if decode_errors == all_names:
        record("P3", True, "every corruption shape raised JSONDecodeError")
    else:
        others = {name: exceptions_seen[name] for name in all_names - decode_errors}
        record("P3", False, f"not all shapes raise JSONDecodeError: {others}")


# ---------------------------------------------------------------------------
# P4 / P5 -- a process killed mid-write
#
# This is the promise Phase 3 rests on: a crash must not destroy existing state.
# A real child process is killed rather than simulated, because simulating it
# would be assuming the answer.
# ---------------------------------------------------------------------------

WRITER_SOURCE = '''
import json, os, sys, time
from pathlib import Path

workspace = Path(sys.argv[1])
destination = workspace / "state.json"
temporary = workspace / "state.json.tmp"

# Write a large payload slowly so the parent can kill this process reliably
# while the temp file is half-written.
with open(temporary, "w", encoding="utf-8") as handle:
    handle.write('{"events": [')
    for index in range(100000):
        handle.write(json.dumps({"i": index, "pad": "x" * 200}) + ",")
        handle.flush()
        if index == 50:
            # Tell the parent we are genuinely mid-write.
            (workspace / "READY").write_text("1", encoding="utf-8")
        time.sleep(0.0005)
    handle.write("null]}")

os.replace(temporary, destination)
'''


def check_kill_mid_write(workspace: Path) -> None:
    print("\nP4/P5: a process killed while writing the temp file")

    destination = workspace / "state.json"
    original = {"phase": "design", "step": 3}
    destination.write_text(json.dumps(original), encoding="utf-8")

    writer_script = workspace / "slow_writer.py"
    writer_script.write_text(WRITER_SOURCE, encoding="utf-8")

    ready_flag = workspace / "READY"
    process = subprocess.Popen([sys.executable, str(writer_script), str(workspace)])

    # Wait until the child confirms it is mid-write, rather than sleeping and
    # hoping. A fixed sleep here would make the spike flaky and its result
    # meaningless.
    waited = 0.0
    while not ready_flag.exists() and process.poll() is None and waited < 30.0:
        import time

        time.sleep(0.01)
        waited += 0.01

    if not ready_flag.exists():
        record("P4", False, "INCONCLUSIVE: the child never reported being mid-write")
        process.kill()
        return

    process.kill()
    process.wait(timeout=10)

    # P4: is the original still intact?
    try:
        survived = json.loads(destination.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001
        record("P4", False, f"original state.json is unreadable after the kill: {type(error).__name__}")
        return

    if survived == original:
        record("P4", True, f"original survived the kill intact: {survived}")
    else:
        record("P4", False, f"original was modified: expected {original}, found {survived}")

    # P5: what did the killed process leave behind?
    temporary = workspace / "state.json.tmp"
    if temporary.exists():
        size = temporary.stat().st_size
        record("P5", True, f"a partial temp file was left behind ({size} bytes) -- cleanup is needed")
    else:
        record("P5", False, "no temp file was left behind; no cleanup needed")


def main() -> int:
    print("Spike: state persistence on Windows")
    print(f"platform: {sys.platform}  python: {sys.version.split()[0]}")
    print("-" * 70)

    with tempfile.TemporaryDirectory(prefix="atom-state-spike-") as raw:
        workspace = Path(raw)
        check_replace_while_open(workspace)
        check_replace_while_open_for_writing(workspace)
        check_concurrent_appends(workspace)
        check_binary_appends(workspace)
        check_locked_appends(workspace)
        check_corruption_shapes(workspace)
        check_kill_mid_write(workspace)

    print("\n" + "=" * 70)
    for prediction, held, evidence in RESULTS:
        print(f"  {prediction:<5} {'CONFIRMED' if held else 'REFUTED  '}  {evidence}")
    print("=" * 70)

    # This spike does not simply report; it PINS the findings that Phase 3's
    # design is built on. P2 and P3 were refuted, and P2b showed the obvious
    # fix does not work either. Those refutations are load-bearing. If a future
    # Python or Windows build changes any of this, the design documents quoting
    # it become wrong, and the right outcome is a loud failure saying so --
    # not a quiet pass.
    #
    # These expectations are WINDOWS expectations. They were measured on
    # Windows and nowhere else. Several of them are explicitly platform
    # behaviour: POSIX renames over an open file happily, and POSIX O_APPEND is
    # widely believed to be atomic for small writes. Asserting the Windows
    # numbers on Linux would be claiming a measurement that was never taken --
    # the exact failure this whole framework exists to prevent. So on non-
    # Windows the spike observes and reports without asserting, and says so.
    expected = {
        "P1": True,  # os.replace fails over an open destination
        "P1b": True,
        "P2": False,  # concurrent appends interleave
        "P2b": False,  # binary mode does not save us
        "P2c": True,  # an OS file lock does
        "P3": False,  # not every corruption shape raises JSONDecodeError
        "P4": True,  # the original survives a kill
        "P5": True,  # a partial temp file is left behind
    }

    actual = {prediction: held for prediction, held, _ in RESULTS}
    missing = sorted(set(expected) - set(actual))

    if missing:
        print(f"\nINCONCLUSIVE: these checks did not run: {', '.join(missing)}")
        return 2

    # P3 is pure Python semantics and P5 is pure logic -- those hold anywhere.
    # Everything else is filesystem behaviour and is Windows-specific until
    # someone measures it elsewhere.
    if sys.platform != "win32":
        print(f"\nOBSERVED ON {sys.platform} -- not asserted.")
        print("The recorded expectations in this spike were measured on Windows only.")
        divergent = sorted(p for p in expected if actual[p] != expected[p])
        if divergent:
            print(f"Differs from the Windows baseline at: {', '.join(divergent)}")
            print("That is informative, not a failure. See poc-report.md 'What this did not settle'.")
        else:
            print("Matches the Windows baseline at every prediction.")
        print("\nTo turn this into an assertion, record the POSIX baseline in poc-report.md first.")
        return 0

    drifted = {
        prediction: (expected[prediction], actual[prediction])
        for prediction in expected
        if actual[prediction] != expected[prediction]
    }

    if drifted:
        print("\nThe world has changed since this spike was written.")
        for prediction, (was, now) in sorted(drifted.items()):
            print(f"  {prediction}: report says {_word(was)}, this run observed {_word(now)}")
        print("\nspecs/atom-cli/phase-03-state/poc-report.md is now STALE and must be revisited.")
        print("This is a failure of the documentation, not of the spike.")
        return 1

    refuted = sorted(prediction for prediction, held in actual.items() if not held)
    print(f"\nEvidence matches the report. {len(refuted)} standing refutation(s): {', '.join(refuted)}")
    print("A refutation is a result, not a failure -- Phase 3's design accounts for each one.")
    return 0


def _word(held: bool) -> str:
    return "CONFIRMED" if held else "REFUTED"


if __name__ == "__main__":
    raise SystemExit(main())
