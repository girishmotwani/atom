"""Single approved source-free tool-isolation proof; raw records stay private."""

from __future__ import annotations

import argparse
from collections import Counter
import ctypes
from ctypes import wintypes
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from atom.invoke import review_command
from atom.review import REVIEW_PROMPT
from atom.runner import SubprocessRunner

FIXTURE = """diff --git a/head.go b/head.go
--- a/head.go
+++ b/head.go
@@ -3,8 +3,8 @@
 import "errors"
 
 func First(values []int) (int, error) {
-    if len(values) == 0 {
+    if len(values) < 0 {
         return 0, errors.New("empty")
     }
     return values[0], nil
 }
"""


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch", type=Path, required=True)
    arguments = parser.parse_args()
    scratch = arguments.scratch.resolve()
    scratch.mkdir(exist_ok=False)
    work = scratch / "work"
    work.mkdir()
    prompt = REVIEW_PROMPT.format(toolchain="", style_rules="", diff=FIXTURE)
    command = review_command(
        "gemini-3.8-flash", prompt, ("azure-devops", "azure-mcp"),
    ) + (
        "--log-dir", str(scratch / "logs"), "--log-level", "debug",
        "--excluded-tools", "builtin:*", "custom:*", "mcp:*",
    )
    (scratch / "stdin.txt").write_text(prompt, encoding="utf-8")
    save(scratch / "invocation.json", {
        "command": command, "cwd": str(work), "timeout_seconds": 600,
        "prompt_utf8_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "implementation_source": str(ROOT / "tools"),
        "calls_authorized": 1,
    })
    if os.name != "nt":
        raise RuntimeError("This approved capture uses the existing Windows lifecycle.")
    from atom import _windows_process
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessId.argtypes = [wintypes.HANDLE]
    kernel.GetProcessId.restype = wintypes.DWORD
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    retained = {}
    cleanup = []
    native = _windows_process._Native
    original_launch = native.launch
    original_members = native.member_handles

    def retain(pid):
        if pid not in retained:
            handle = kernel.OpenProcess(0x100000 | 0x1000, False, pid)
            if not handle:
                raise ctypes.WinError(ctypes.get_last_error())
            retained[pid] = handle

    def observe_launch(self, *args, **kwargs):
        information = original_launch(self, *args, **kwargs)
        retain(kernel.GetProcessId(information[0]))
        return information

    def observe_members(self, job):
        members = original_members(self, job)
        for handle in members:
            retain(kernel.GetProcessId(handle))
        return members

    native.launch = observe_launch
    native.member_handles = observe_members
    print("Starting the single approved source-free Gemini call.", flush=True)
    try:
        result = SubprocessRunner().run(command, work, 600, stdin_text=prompt)
    finally:
        native.launch = original_launch
        native.member_handles = original_members
        for pid, handle in retained.items():
            cleanup.append({"pid": pid, "signaled_after_runner_return": kernel.WaitForSingleObject(handle, 0) == 0})
            if not kernel.CloseHandle(handle):
                raise ctypes.WinError(ctypes.get_last_error())
        save(scratch / "process-cleanup.json", cleanup)
    (scratch / "stdout.jsonl").write_text(result.stdout, encoding="utf-8")
    (scratch / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    record = asdict(result)
    record.pop("stdout")
    record.pop("stderr")
    record["outcome"] = result.outcome.value
    save(scratch / "process.json", record)
    shutil.rmtree(work)
    if work.exists():
        raise RuntimeError("Owned working directory remains.")
    events = []
    malformed = []
    for number, line in enumerate(result.stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            malformed.append(number)
    roots = [
        event for event in events
        if isinstance(event, dict) and not event.get("agentId")
        and not (event.get("data") or {}).get("parentToolCallId")
    ]
    delivered = [
        event["data"].get("content") for event in roots
        if event.get("type") == "user.message"
    ]
    request_count = sum(
        len((event.get("data") or {}).get("toolRequests", []))
        for event in roots if event.get("type") == "assistant.message"
    )
    summary = {
        "outcome": result.outcome.value,
        "exit_code": result.exit_code,
        "duration_seconds": result.duration_seconds,
        "malformed_lines": malformed,
        "child_events": len(events) - len(roots),
        "root_event_counts": dict(Counter(event.get("type") for event in roots)),
        "root_tool_requests": request_count,
        "delivered_prompt_matches": len(delivered) == 1
        and isinstance(delivered[0], str)
        and delivered[0].replace("\r\n", "\n") == prompt.replace("\r\n", "\n"),
        "owned_work_directory_absent": not work.exists(),
        "owned_observed_processes_exited": bool(cleanup)
        and all(item["signaled_after_runner_return"] for item in cleanup),
        "request_exposure_verdict": "pending inspection of private CLI-generated request metadata",
        "log_files": [
            str(path.relative_to(scratch))
            for path in scratch.rglob("*") if path.is_file()
        ],
    }
    save(scratch / "capture-summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    if not result.succeeded:
        print("Process did not succeed; no retry authorized.", flush=True)
        return 2
    print("Capture complete; do not grade the response until actual tool exposure is verified.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

