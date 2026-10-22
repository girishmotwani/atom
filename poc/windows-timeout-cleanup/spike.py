"""Disposable observation of Windows cleanup after the launched parent exits."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

from atom import runner as production


kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel.OpenProcess.restype = wintypes.HANDLE
kernel.GetCurrentProcess.restype = wintypes.HANDLE
kernel.DuplicateHandle.argtypes = [wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel.WaitForSingleObject.restype = wintypes.DWORD
kernel.GetProcessId.argtypes = [wintypes.HANDLE]
kernel.GetProcessId.restype = wintypes.DWORD


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(path)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def alive(handle):
    state = kernel.WaitForSingleObject(handle, 0)
    if state not in (0, 258):
        raise ctypes.WinError(ctypes.get_last_error())
    return state == 258


def register(process, role, arguments):
    supervisor = kernel.OpenProcess(0x0040, False, arguments.supervisor)
    if not supervisor:
        raise ctypes.WinError(ctypes.get_last_error())
    exported = wintypes.HANDLE()
    try:
        if not kernel.DuplicateHandle(kernel.GetCurrentProcess(), int(process._handle), supervisor, ctypes.byref(exported), 0, False, 2):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(supervisor)
    save(arguments.control / f"owned-{role}-{process.pid}.json", {
        "role": role, "pid": process.pid, "handle": exported.value,
        "supervisor": arguments.supervisor, "nonce": arguments.nonce,
    })


def fixture_child(arguments):
    print("fixture_child_stdout_ready", flush=True)
    print("fixture_child_stderr_ready", file=sys.stderr, flush=True)
    save(arguments.control / "child-ready.json", {
        "pid": os.getpid(), "nonce": arguments.nonce,
        "stdout_and_stderr_written": True, "cwd": str(Path.cwd()),
    })
    time.sleep(15)


def mode_command(mode, arguments):
    return [sys.executable, str(Path(__file__).resolve()), "--mode", mode,
            "--control", str(arguments.control), "--supervisor", str(arguments.supervisor),
            "--nonce", arguments.nonce]


def fixture_parent(arguments):
    child = subprocess.Popen(mode_command("child", arguments), cwd=arguments.control / "fixture-cwd",
                             stdin=subprocess.DEVNULL, stdout=sys.stdout, stderr=sys.stderr)
    register(child, "child", arguments)
    save(arguments.control / "parent-exiting.json", {"pid": os.getpid(), "child_pid": child.pid, "nonce": arguments.nonce})


def worker(arguments):
    real_popen = subprocess.Popen
    real_run = subprocess.run
    real_kill = production._kill_process_tree
    parent = None
    child_handle = None
    entry = None

    def observed_popen(*args, **kwargs):
        nonlocal parent
        command = list(args[0] if args else kwargs["args"])
        role = "parent" if "--mode" in command and command[command.index("--mode") + 1] == "parent" else "termination"
        if role == "termination":
            if parent is None or "/PID" not in command or command[command.index("/PID") + 1] != str(parent.pid):
                raise RuntimeError("refusing native termination of an unregistered PID")
        process = real_popen(*args, **kwargs)
        register(process, role, arguments)
        if role == "parent":
            parent = process
        return process

    def observed_run(*args, **kwargs):
        result = real_run(*args, **kwargs)
        save(arguments.control / "native-result.json", {
            "command": list(result.args), "return_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
        })
        return result

    def observed_kill(process):
        nonlocal child_handle, entry
        registrations = list(arguments.control.glob("owned-child-*.json"))
        if len(registrations) != 1:
            raise RuntimeError("fixture child identity is not registered")
        child = load(registrations[0])
        child_handle = kernel.OpenProcess(0x00100000 | 0x1000, False, child["pid"])
        if not child_handle:
            raise ctypes.WinError(ctypes.get_last_error())
        ready_path = arguments.control / "child-ready.json"
        exiting_path = arguments.control / "parent-exiting.json"
        ready = load(ready_path) if ready_path.exists() else None
        exiting = load(exiting_path) if exiting_path.exists() else None
        exit_code = process.poll()
        entry = {
            "parent_pid": process.pid, "parent_exit_code_before_cleanup": exit_code,
            "parent_actual_pid_matches": exiting is not None and exiting["pid"] == process.pid,
            "child_pid": child["pid"], "child_alive_before_cleanup": alive(child_handle),
            "child_ready": ready is not None and ready["pid"] == child["pid"] and ready["nonce"] == arguments.nonce and ready["stdout_and_stderr_written"] and Path(ready["cwd"]) == arguments.control / "fixture-cwd",
        }
        save(arguments.control / "cleanup-entry.json", entry)
        return real_kill(process)

    subprocess.Popen = observed_popen
    subprocess.run = observed_run
    production._kill_process_tree = observed_kill
    try:
        started = time.perf_counter()
        result = production.SubprocessRunner().run(mode_command("parent", arguments), arguments.control / "fixture-cwd", timeout_seconds=2)
        elapsed = time.perf_counter() - started
        child_alive = alive(child_handle) if child_handle is not None else None
        directory_error = None
        try:
            (arguments.control / "fixture-cwd").rmdir()
            removed = True
        except OSError as error:
            removed = False
            directory_error = {"winerror": error.winerror, "errno": error.errno, "message": str(error)}
        native_path = arguments.control / "native-result.json"
        native = load(native_path) if native_path.exists() else None
        valid = entry is not None and entry["parent_exit_code_before_cleanup"] == 0 and entry["parent_actual_pid_matches"] and entry["child_alive_before_cleanup"] and entry["child_ready"] and native is not None
        verdict = "Inconclusive"
        if valid and result.outcome is production.CommandOutcome.TIMED_OUT:
            if elapsed > 5 or child_alive:
                verdict = "Refuted"
            elif removed:
                verdict = "Confirmed"
        save(arguments.control / "measurement.json", {
            "setup_valid": valid, "entry": entry, "outcome": result.outcome.value,
            "elapsed_seconds": elapsed, "runner_duration_seconds": result.duration_seconds,
            "stdout": result.stdout, "stderr": result.stderr,
            "child_alive_at_return": child_alive,
            "directory_removed_before_rescue": removed, "directory_error": directory_error,
            "native": native, "verdict": verdict,
        })
    finally:
        subprocess.Popen = real_popen
        subprocess.run = real_run
        production._kill_process_tree = real_kill
        if child_handle is not None:
            kernel.CloseHandle(child_handle)


def collect_owned(control, nonce, collected):
    for path in control.glob("owned-*.json"):
        if path.name in collected:
            continue
        record = load(path)
        if record["nonce"] != nonce or record["supervisor"] != os.getpid() or record["role"] not in {"parent", "child", "termination"} or kernel.GetProcessId(record["handle"]) != record["pid"]:
            raise RuntimeError("invalid owned-process identity registration")
        collected[path.name] = record


def stop_owned(pid, handle, control, deadline):
    if not alive(handle):
        return None
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise RuntimeError("safety-cleanup budget exhausted")
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", f"$ErrorActionPreference = 'Stop'; Stop-Process -Id {pid} -Force -ErrorAction Stop"],
        cwd=control, stdin=subprocess.DEVNULL, capture_output=True, text=True,
        timeout=min(5, remaining),
    )
    record = {"pid": pid, "return_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    if kernel.WaitForSingleObject(handle, 2000) != 0:
        raise RuntimeError("owned process did not exit after PID-specific safety cleanup")
    return record


def supervisor(arguments):
    scratch = arguments.scratch.resolve()
    atom_root = Path(__file__).resolve().parents[2]
    if scratch.exists() or scratch.is_relative_to(atom_root) or atom_root.is_relative_to(scratch):
        raise ValueError("scratch must be a new private directory outside the repository")
    scratch.mkdir(parents=True)
    deadline = time.monotonic() + 120
    runner_path = Path(production.__file__)
    before = hashlib.sha256(runner_path.read_bytes()).hexdigest()
    transcript = []

    def emit(text):
        print(text, flush=True)
        transcript.append(text)
        (scratch / "transcript.txt").write_text("\n".join(transcript) + "\n", encoding="utf-8")

    emit("experiment=early_exiting_parent_cleanup timeout_seconds=2 return_bound_seconds=5")
    emit("runner_sha256_before=" + before)
    verdict = "Inconclusive"
    attempts = 0
    for number in range(1, 4):
        if time.monotonic() + 30 > deadline:
            emit("infrastructure_error=insufficient_time_for_safe_attempt")
            verdict = "Inconclusive"
            break
        attempts += 1
        control = scratch / f"attempt-{number}"
        control.mkdir()
        (control / "fixture-cwd").mkdir()
        nonce = secrets.token_hex(8)
        fixture_args = argparse.Namespace(control=control, supervisor=os.getpid(), nonce=nonce)
        collected = {}
        safety_stops = []
        measurement = None
        watchdog = False
        with (control / "worker-stdout.txt").open("w", encoding="utf-8") as stdout, (control / "worker-stderr.txt").open("w", encoding="utf-8") as stderr:
            process = subprocess.Popen(mode_command("worker", fixture_args), cwd=control, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
            try:
                stop_at = time.monotonic() + 20
                while True:
                    collect_owned(control, nonce, collected)
                    if process.poll() is not None:
                        break
                    if time.monotonic() >= stop_at:
                        watchdog = True
                        break
                    time.sleep(0.01)
                collect_owned(control, nonce, collected)
                measurement_path = control / "measurement.json"
                measurement = load(measurement_path) if measurement_path.exists() else None
                verdict = measurement["verdict"] if measurement is not None and not watchdog and process.poll() == 0 else "Inconclusive"
                emit(f"attempt={number} setup_valid={str(measurement is not None and measurement['setup_valid']).lower()} worker_watchdog={str(watchdog).lower()}")
                if measurement is not None:
                    emit(f"runner_outcome={measurement['outcome']} elapsed_seconds={measurement['elapsed_seconds']} child_alive_at_return={str(measurement['child_alive_at_return']).lower()}")
                    emit("cleanup_entry=" + json.dumps(measurement["entry"], sort_keys=True))
                    native = measurement["native"]
                    if native is not None:
                        emit("native_return_code=" + str(native["return_code"]))
                        emit("native_stdout=" + json.dumps(native["stdout"]))
                        emit("native_stderr=" + json.dumps(native["stderr"]))
                    error = measurement["directory_error"]
                    emit(f"directory_removed_before_rescue={str(measurement['directory_removed_before_rescue']).lower()} directory_winerror={error['winerror'] if error else None}")
                else:
                    emit("infrastructure_error=worker_did_not_produce_a_measurement")
            finally:
                collect_owned(control, nonce, collected)
                worker_stop = stop_owned(process.pid, int(process._handle), control, deadline)
                if worker_stop is not None:
                    safety_stops.append(worker_stop)
                for role in ("parent", "termination", "child"):
                    collect_owned(control, nonce, collected)
                    for record in list(collected.values()):
                        if record["role"] == role:
                            stopped = stop_owned(record["pid"], record["handle"], control, deadline)
                            if stopped is not None:
                                safety_stops.append(stopped)
                process.wait(timeout=max(0.1, min(2, deadline - time.monotonic())))
                all_exited = all(not alive(record["handle"]) for record in collected.values())
                save(control / "safety-cleanup.json", {"stops": safety_stops, "all_registered_processes_exited": all_exited})
                for record in collected.values():
                    kernel.CloseHandle(record["handle"])
                workdir = control / "fixture-cwd"
                if workdir.exists():
                    workdir.rmdir()
                emit("safety_stop_results=" + json.dumps([{"pid": record["pid"], "return_code": record["return_code"]} for record in safety_stops]))
                emit("all_registered_processes_exited=" + str(all_exited).lower() + " fixture_directory_removed=" + str(not workdir.exists()).lower())
        emit(f"attempt_verdict={verdict}")
        if verdict != "Confirmed":
            break
    after = hashlib.sha256(runner_path.read_bytes()).hexdigest()
    emit("runner_source_unchanged=" + str(before == after).lower())
    if before != after:
        verdict = "Inconclusive"
    emit(f"attempts_completed={attempts} attempts_limit=3")
    emit("verdict=" + verdict)
    save(scratch / "summary.json", {"verdict": verdict, "attempts": attempts, "runner_sha256_before": before, "runner_sha256_after": after})
    return {"Confirmed": 0, "Refuted": 3, "Inconclusive": 2}[verdict]


def main():
    if os.name != "nt":
        raise RuntimeError("this approved fixture is Windows-only")
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("supervisor", "worker", "parent", "child"), default="supervisor")
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--control", type=Path)
    parser.add_argument("--supervisor", type=int)
    parser.add_argument("--nonce")
    arguments = parser.parse_args()
    if arguments.mode == "supervisor":
        return supervisor(arguments)
    if arguments.mode == "worker":
        worker(arguments)
    elif arguments.mode == "parent":
        fixture_parent(arguments)
    else:
        fixture_child(arguments)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

