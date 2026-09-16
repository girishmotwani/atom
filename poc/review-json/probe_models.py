"""Probe which --model names the Copilot CLI accepts, without paying for a full completion.

An invalid model is rejected during start-up, in about two seconds. A valid one goes
on to call the model, which takes well over a minute. So we start each candidate,
wait a short while, and classify by whether it died early and what it said.

This is a throwaway probe, not part of the spike proper.
"""

from __future__ import annotations

import subprocess
import sys

CANDIDATES = [
    "gpt-5.4",
    "gpt-5.3-codex",
    "gpt-5-mini",
    "claude-sonnet-4.5",
    "claude-sonnet-4",
    "claude-haiku-4.5",
    "gemini-2.5-pro",
    "auto",
]

# Long enough to let the start-up rejection happen, far short of a real completion.
STARTUP_GRACE_SECONDS = 20


def probe(model: str) -> str:
    """Return 'accepted', 'rejected: <reason>', or 'unclear' for one model name."""
    process = subprocess.Popen(
        ["copilot", "-p", "hi", "--silent", "--model", model],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        output, _ = process.communicate(timeout=STARTUP_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        # Still running past the start-up window means the name got through
        # validation and the model is actually being called.
        process.kill()
        process.communicate()
        return "accepted"

    first_line = (output or "").strip().splitlines()
    reason = first_line[0] if first_line else f"exit {process.returncode}, no output"
    if "not available" in reason:
        return f"rejected: {reason}"
    # Finished inside the grace window without a rejection -- unexpected, worth seeing.
    return f"unclear (exit {process.returncode}): {reason}"


def main() -> int:
    for model in CANDIDATES:
        print(f"{model:<20} {probe(model)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
