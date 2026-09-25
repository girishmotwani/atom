"""Spike: why `atom review`'s 300-second timeout let three calls run for 65 minutes.

What was observed
-----------------
The model-swap measurement (`poc/review-model-swap/`) set `timeout=300` on every call.
Three `claude-opus-5` calls reported durations of 3885, 3897 and 3901 seconds. The
timeout did fire -- each run is recorded as `timed_out` -- but it fired an hour late.

`atom review` uses the same construction (`runner.py`, `subprocess.run(..., timeout=)`),
so this is a production defect, not an artefact of the spike.

The mechanism
-------------
`subprocess.run` implements its timeout as:

    try:
        stdout, stderr = process.communicate(input, timeout=timeout)
    except TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()   # <-- no timeout on this one

The second `communicate` waits for end-of-file on the pipes, and end-of-file does not
arrive when the process is killed. It arrives when the last handle to the write end of
the pipe is closed. The CLI is a Node program that spawns children, and those children
inherit the pipe. Killing the parent closes the parent's handle; the children keep
theirs open, so the drain blocks until *they* exit of their own accord.

That is why the timeout appears to work in tests and fails in production: a well-behaved
child dies with its parent, and a hung agent is precisely the case where it does not.

What this spike measures
------------------------
A deliberately misbehaving process -- one that spawns a long-lived grandchild which
inherits the pipes -- and three ways of timing it out:

  `current`    what `runner.py` does now
  `tree_kill`  kill the whole process tree, so no handle to the pipe survives
  `abandon`    kill, then drain with a bounded wait and give up on the pipes

The question is not which is fastest. All three return eventually. The question is which
of them bounds the wait at the number the caller asked for, and what each costs when it
does.

Run it with: python poc/review-timeout/spike.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass

# The grandchild outlives its parent by this much. It only has to be comfortably
# longer than the timeout below for the difference between the strategies to show.
GRANDCHILD_LIFETIME_SECONDS = 45

# Small on purpose: the whole point is to see whether the wait is bounded by the
# number the caller asked for, and a small number makes an unbounded wait obvious.
TIMEOUT_SECONDS = 3

# How long a strategy may spend draining pipes after the kill before it stops caring.
DRAIN_GRACE_SECONDS = 2

# A process that writes a line, starts a child which inherits its pipes, and then
# sleeps. Killing it does not close the pipe, because the child still holds it --
# which is exactly the shape of a Node CLI that has spawned a worker.
MISBEHAVING_CHILD = (
    "import subprocess, sys, time; "
    "print('started', flush=True); "
    f"subprocess.Popen([sys.executable, '-c', 'import time; time.sleep({GRANDCHILD_LIFETIME_SECONDS})']); "
    "time.sleep(600)"
)


@dataclass
class Attempt:
    """One strategy's result against the misbehaving process."""

    strategy: str
    seconds: float
    timed_out: bool
    stdout: str
    note: str = ""

    @property
    def bounded(self) -> bool:
        """Return whether the wait respected the timeout the caller asked for."""

        return self.seconds < TIMEOUT_SECONDS + DRAIN_GRACE_SECONDS + 2


def _command() -> list[str]:
    return [sys.executable, "-c", MISBEHAVING_CHILD]


def current_behaviour() -> Attempt:
    """Reproduce what `runner.py` does today."""

    started = time.monotonic()
    try:
        subprocess.run(
            _command(),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        return Attempt("current", time.monotonic() - started, False, "", "did not time out")
    except subprocess.TimeoutExpired as expired:
        stdout = expired.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        return Attempt("current", time.monotonic() - started, True, stdout)


def _kill_tree(process: subprocess.Popen) -> str:
    """Terminate the process and everything it started.

    The pipe stays open while any descendant holds a handle to it, so killing only
    the direct child leaves the drain blocked. Windows has no process groups, so the
    tree is walked by `taskkill /T`; elsewhere the child is given its own session at
    launch and the whole group is signalled at once.
    """

    if os.name == "nt":
        result = subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            process.kill()
            return f"taskkill exited {result.returncode}; fell back to kill"
        return "killed process tree"

    try:
        os.killpg(os.getpgid(process.pid), 9)
        return "killed process group"
    except (ProcessLookupError, PermissionError) as error:
        process.kill()
        return f"killpg failed ({error}); fell back to kill"


def _popen() -> subprocess.Popen:
    """Start the misbehaving process, in its own group where the platform has them."""

    extra = {}
    if os.name != "nt":
        extra["start_new_session"] = True
    return subprocess.Popen(
        _command(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **extra,
    )


def tree_kill_strategy() -> Attempt:
    """Kill the whole tree on timeout, so nothing is left holding the pipe."""

    started = time.monotonic()
    process = _popen()
    try:
        process.communicate(input="", timeout=TIMEOUT_SECONDS)
        return Attempt("tree_kill", time.monotonic() - started, False, "", "did not time out")
    except subprocess.TimeoutExpired:
        note = _kill_tree(process)
        try:
            stdout, _ = process.communicate(timeout=DRAIN_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            stdout = ""
            note += "; drain still blocked"
        return Attempt("tree_kill", time.monotonic() - started, True, stdout or "", note)


def abandon_strategy() -> Attempt:
    """Kill only the direct child, then stop waiting for the pipes to close.

    This is the strategy that needs no platform-specific process handling. It buys a
    bounded wait by giving up on any output still in flight, which is a real cost: the
    partial reply a timed-out call did manage to produce is what tells a developer
    whether the model was slow or stuck.
    """

    started = time.monotonic()
    process = _popen()
    try:
        process.communicate(input="", timeout=TIMEOUT_SECONDS)
        return Attempt("abandon", time.monotonic() - started, False, "", "did not time out")
    except subprocess.TimeoutExpired:
        process.kill()
        note = "killed child only"
        try:
            stdout, _ = process.communicate(timeout=DRAIN_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            stdout = ""
            note += "; abandoned pipes after grace"
            # The reader threads are left running deliberately. They end when the
            # grandchild does; the caller is no longer waiting on them.
        return Attempt("abandon", time.monotonic() - started, True, stdout or "", note)


def main() -> int:
    print(f"timeout asked for:     {TIMEOUT_SECONDS}s")
    print(f"grandchild outlives:   {GRANDCHILD_LIFETIME_SECONDS}s")
    print(f"drain grace:           {DRAIN_GRACE_SECONDS}s")
    print(f"platform:              {os.name}\n")

    attempts = [current_behaviour(), tree_kill_strategy(), abandon_strategy()]

    header = f"{'strategy':<12}{'seconds':>9}{'bounded':>9}{'output':>9}  note"
    print(header)
    print("-" * len(header))
    for attempt in attempts:
        print(
            f"{attempt.strategy:<12}{attempt.seconds:>9.1f}"
            f"{'yes' if attempt.bounded else 'NO':>9}"
            f"{len(attempt.stdout.strip()):>9}  {attempt.note}"
        )

    print(
        "\n'output' is characters recovered from the killed process. A strategy that"
        "\nbounds the wait but recovers nothing has traded one problem for another."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
