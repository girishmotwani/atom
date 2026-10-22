"""Disposable proof of last-job-handle cleanup after an owned parent exits."""
from __future__ import annotations

import _winapi
import argparse
import base64
import ctypes
from ctypes import wintypes
import hashlib
import importlib.util
import json
import msvcrt
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "poc" / "windows-timeout-cleanup" / "spike.py"
spec = importlib.util.spec_from_file_location("archived_fixture_helpers", HELPER)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
save, load, alive, register, stop_owned = prior.save, prior.load, prior.alive, prior.register, prior.stop_owned
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
for name, arguments, result in (
    ("CreateJobObjectW", [ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
    ("SetInformationJobObject", [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
    ("QueryInformationJobObject", [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p], wintypes.BOOL),
    ("AssignProcessToJobObject", [wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
    ("IsProcessInJob", [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
    ("GetHandleInformation", [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
    ("ResumeThread", [wintypes.HANDLE], wintypes.DWORD),
    ("CloseHandle", [wintypes.HANDLE], wintypes.BOOL),
    ("GetExitCodeProcess", [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
    ("OpenProcess", [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
    ("GetCurrentProcess", [], wintypes.HANDLE),
):
    function = getattr(kernel, name)
    function.argtypes, function.restype = arguments, result


class BasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                ("flags", wintypes.DWORD), ("minimum_working_set", ctypes.c_size_t),
                ("maximum_working_set", ctypes.c_size_t), ("active_process_limit", wintypes.DWORD),
                ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", BasicLimits), ("io_counters", ctypes.c_uint64 * 6),
                ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]


class NativeRefusal(RuntimeError):
    pass


def command(mode, arguments):
    return [sys.executable, str(Path(__file__).resolve()), "--mode", mode,
            "--control", str(arguments.control), "--supervisor", str(arguments.supervisor),
            "--nonce", arguments.nonce]


def child(arguments):
    print("job_fixture_stdout_ready", flush=True)
    print("job_fixture_stderr_ready", file=sys.stderr, flush=True)
    save(arguments.control / "child-ready.json", {"pid": os.getpid(), "nonce": arguments.nonce,
         "cwd": str(Path.cwd()), "ready_at": time.perf_counter()})
    time.sleep(15)


def parent(arguments):
    save(arguments.control / "parent-started.json", {"pid": os.getpid(), "at": time.perf_counter(), "nonce": arguments.nonce})
    process = subprocess.Popen(command("child", arguments), cwd=arguments.control / "fixture-cwd",
                               stdin=subprocess.DEVNULL, stdout=sys.stdout, stderr=sys.stderr)
    register(process, "child", arguments)
    deadline = time.monotonic() + 10
    while not (arguments.control / "child-ready.json").exists():
        if time.monotonic() >= deadline:
            raise RuntimeError("child readiness was not observed")
        time.sleep(0.005)
    save(arguments.control / "parent-exiting.json", {"pid": os.getpid(), "child_pid": process.pid,
         "nonce": arguments.nonce, "at": time.perf_counter()})


def control(arguments):
    save(arguments.control / "control-ready.json", {"pid": os.getpid(), "nonce": arguments.nonce})
    time.sleep(15)


def worker(arguments):
    events = []
    measurement = {"verdict": "Inconclusive", "setup_valid": False, "rescue_job_close": False}
    job = None
    parent_handle = thread_handle = child_handle = None
    reads = []
    streams = {}
    control_process = None

    def event(operation, success, **details):
        record = {"operation": operation, "success": bool(success), "at": time.perf_counter(), **details}
        events.append(record)
        save(arguments.control / "native-events.json", events)
        return record

    def checked(operation, function, *values, refusal=False):
        ctypes.set_last_error(0)
        value = function(*values)
        error = ctypes.get_last_error() if not value else 0
        event(operation, value, result=value, error=error, error_message=ctypes.FormatError(error).strip() if error else "")
        if not value:
            if refusal:
                raise NativeRefusal(operation)
            raise ctypes.WinError(error)
        return value

    def in_job(handle, target, label):
        result = wintypes.BOOL()
        checked("IsProcessInJob:" + label, kernel.IsProcessInJob, handle, target, ctypes.byref(result))
        return bool(result.value)

    def open_child():
        paths = list(arguments.control.glob("owned-child-*.json"))
        if len(paths) != 1:
            raise RuntimeError("child registration missing or ambiguous")
        record = load(paths[0])
        if record["nonce"] != arguments.nonce or record["supervisor"] != arguments.supervisor:
            raise RuntimeError("invalid child registration")
        handle = checked("OpenProcess:child", kernel.OpenProcess, 0x00100400, False, record["pid"])
        if prior.kernel.GetProcessId(handle) != record["pid"]:
            raise RuntimeError("child handle identity mismatch")
        return handle, record

    def read_pipe(descriptor, label):
        try:
            with os.fdopen(descriptor, "rb") as pipe:
                streams[label] = {"data": pipe.read()}
        except OSError as error:
            streams[label] = {"error": repr(error)}
            print(f"fixture pipe read failed: {label}: {error}", file=sys.stderr, flush=True)

    def candidate():
        nonlocal job, parent_handle, thread_handle, child_handle, control_process
        measurement["worker_already_in_host_job"] = in_job(kernel.GetCurrentProcess(), None, "host")
        job = checked("CreateJobObjectW", kernel.CreateJobObjectW, None, None, refusal=True)
        flags = wintypes.DWORD()
        checked("GetHandleInformation:job", kernel.GetHandleInformation, job, ctypes.byref(flags))
        measurement["job_handle_inheritable"] = bool(flags.value & 1)
        if measurement["job_handle_inheritable"]:
            raise RuntimeError("candidate job handle is inheritable")
        information = ExtendedLimits()
        information.basic.flags = 0x00002000
        checked("SetInformationJobObject", kernel.SetInformationJobObject, job, 9, ctypes.byref(information), ctypes.sizeof(information), refusal=True)
        observed = ExtendedLimits()
        checked("QueryInformationJobObject", kernel.QueryInformationJobObject, job, 9, ctypes.byref(observed), ctypes.sizeof(observed), None)
        if observed.basic.flags != 0x00002000:
            raise RuntimeError("job limit readback differs from kill-on-close only")
        control_process = subprocess.Popen(command("control", arguments), cwd=arguments.control,
                                          stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        register(control_process, "control", arguments)
        stdout_read, stdout_write = os.pipe()
        stderr_read, stderr_write = os.pipe()
        reads.extend([stdout_read, stderr_read])
        stdin_read = os.open(os.devnull, os.O_RDONLY)
        try:
            handles = [msvcrt.get_osfhandle(item) for item in (stdin_read, stdout_write, stderr_write)]
            for handle in handles:
                os.set_handle_inheritable(handle, True)
            startup = subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESTDHANDLES,
                hStdInput=handles[0], hStdOutput=handles[1], hStdError=handles[2],
                lpAttributeList={"handle_list": handles})
            measurement["started_at"] = time.perf_counter()
            try:
                parent_handle, thread_handle, parent_pid, thread_pid = _winapi.CreateProcess(
                    sys.executable, subprocess.list2cmdline(command("parent", arguments)),
                    None, None, True, 0x00000004, None, str(arguments.control / "fixture-cwd"), startup)
            except OSError as error:
                event("CreateProcess:stdlib_winapi", False, error=error.winerror, error_message=error.strerror)
                raise
            event("CreateProcess:stdlib_winapi", True, flags=0x00000004, pid=parent_pid, thread_id=thread_pid)
        finally:
            for descriptor in (stdin_read, stdout_write, stderr_write):
                os.close(descriptor)
        register(SimpleNamespace(_handle=parent_handle, pid=parent_pid), "parent", arguments)
        registered_at = event("parent_identity_registered", True)["at"]
        checked("AssignProcessToJobObject", kernel.AssignProcessToJobObject, job, parent_handle, refusal=True)
        assigned_at = events[-1]["at"]
        member_before_resume = in_job(parent_handle, job, "suspended_parent")
        resume_started = time.perf_counter()
        ctypes.set_last_error(0)
        previous_count = kernel.ResumeThread(thread_handle)
        event("ResumeThread", previous_count != 0xFFFFFFFF, previous_suspend_count=previous_count,
              error=ctypes.get_last_error() if previous_count == 0xFFFFFFFF else 0)
        if previous_count != 1 or not member_before_resume:
            raise RuntimeError("suspended assignment/resume ordering was not established")
        checked("CloseHandle:primary_thread", kernel.CloseHandle, thread_handle)
        thread_handle = None
        readers = []
        for descriptor, label in ((stdout_read, "stdout"), (stderr_read, "stderr")):
            reader = threading.Thread(target=read_pipe, args=(descriptor, label), daemon=True)
            reader.start()
            readers.append(reader)
            reads.remove(descriptor)
        deadline = measurement["started_at"] + 2
        time.sleep(max(0, deadline - time.perf_counter()))
        child_handle, registration = open_child()
        ready = load(arguments.control / "child-ready.json")
        first = load(arguments.control / "parent-started.json")
        exiting = load(arguments.control / "parent-exiting.json")
        parent_exit = wintypes.DWORD()
        checked("GetExitCodeProcess:parent", kernel.GetExitCodeProcess, parent_handle, ctypes.byref(parent_exit))
        entry = {
            "parent_pid": parent_pid, "parent_exit_code": parent_exit.value,
            "child_pid": registration["pid"], "child_alive": alive(child_handle),
            "child_in_job": in_job(child_handle, job, "child"),
            "worker_in_candidate_job": in_job(kernel.GetCurrentProcess(), job, "worker"),
            "control_pid": control_process.pid, "control_alive": alive(int(control_process._handle)),
            "control_in_candidate_job": in_job(int(control_process._handle), job, "control"),
        }
        launch_order = registered_at <= assigned_at < resume_started <= first["at"]
        ready_valid = (ready["nonce"] == arguments.nonce and ready["pid"] == registration["pid"]
                       and Path(ready["cwd"]) == arguments.control / "fixture-cwd" and ready["ready_at"] <= deadline)
        parent_valid = (first["pid"] == parent_pid and first["nonce"] == arguments.nonce
                        and exiting["pid"] == parent_pid and exiting["nonce"] == arguments.nonce
                        and exiting["child_pid"] == registration["pid"] and exiting["at"] <= deadline)
        measurement.update({"entry": entry, "launch_order_valid": launch_order,
            "resume_previous_suspend_count": previous_count, "parent_member_before_resume": member_before_resume,
            "ready_valid": ready_valid, "parent_identity_valid": parent_valid,
            "cleanup_dispatch_seconds": time.perf_counter() - measurement["started_at"]})
        measurement["setup_valid"] = (launch_order and ready_valid and parent_valid and parent_exit.value == 0
            and entry["child_alive"] and entry["child_in_job"] and entry["control_alive"]
            and not entry["worker_in_candidate_job"] and not entry["control_in_candidate_job"])
        save(arguments.control / "cleanup-entry.json", measurement)
        if not measurement["setup_valid"]:
            return
        checked("CloseHandle:candidate_job", kernel.CloseHandle, job, refusal=True)
        job = None
        wait_milliseconds = max(0, int((measurement["started_at"] + 5 - time.perf_counter()) * 1000))
        child_wait = prior.kernel.WaitForSingleObject(child_handle, wait_milliseconds)
        if child_wait not in (0, 258):
            raise ctypes.WinError(ctypes.get_last_error())
        measurement["child_alive_at_return"] = alive(child_handle)
        for reader in readers:
            reader.join(timeout=max(0, measurement["started_at"] + 5 - time.perf_counter()))
        measurement["pipes_reached_eof"] = all(not reader.is_alive() for reader in readers)
        measurement["pipe_errors"] = {label: value["error"] for label, value in streams.items() if "error" in value}
        for label in ("stdout", "stderr"):
            data = streams.get(label, {}).get("data", b"")
            measurement[label + "_base64"] = base64.b64encode(data).decode("ascii")
            measurement[label + "_marker_present"] = ("job_fixture_" + label + "_ready\n").encode() in data.replace(b"\r\n", b"\n")
        measurement["control_alive_at_return"] = alive(int(control_process._handle))
        try:
            (arguments.control / "fixture-cwd").rmdir()
            measurement["directory_removed_before_rescue"] = True
        except OSError as error:
            measurement["directory_removed_before_rescue"] = False
            measurement["directory_error"] = {"winerror": error.winerror, "errno": error.errno, "message": str(error)}

    try:
        candidate()
    except NativeRefusal as error:
        measurement["native_refusal"] = str(error)
        measurement["verdict"] = "Refuted"
    finally:
        try:
            if job is not None:
                measurement["rescue_job_close"] = True
                checked("CloseHandle:rescue_job", kernel.CloseHandle, job)
            for handle in (thread_handle, parent_handle, child_handle):
                if handle is not None:
                    checked("CloseHandle:identity", kernel.CloseHandle, handle)
            for descriptor in reads:
                os.close(descriptor)
        finally:
            if "started_at" in measurement:
                measurement["elapsed_seconds"] = time.perf_counter() - measurement["started_at"]
            if measurement["setup_valid"] and not measurement["rescue_job_close"] and "child_alive_at_return" in measurement:
                if (measurement["elapsed_seconds"] > 5 or measurement["child_alive_at_return"]
                        or not measurement["control_alive_at_return"]):
                    measurement["verdict"] = "Refuted"
                elif measurement["pipe_errors"]:
                    measurement["verdict"] = "Inconclusive"
                elif not (measurement["pipes_reached_eof"] and measurement["stdout_marker_present"] and measurement["stderr_marker_present"]):
                    measurement["verdict"] = "Refuted"
                elif measurement["directory_removed_before_rescue"]:
                    measurement["verdict"] = "Confirmed"
            save(arguments.control / "measurement.json", measurement)


def collect_owned(arguments, collected):
    for path in arguments.control.glob("owned-*.json"):
        if path.name in collected:
            continue
        record = load(path)
        if (record["nonce"] != arguments.nonce or record["supervisor"] != os.getpid()
                or record["role"] not in {"parent", "child", "control"}
                or prior.kernel.GetProcessId(record["handle"]) != record["pid"]):
            raise RuntimeError("invalid retained process identity")
        collected[path.name] = record


def supervisor(arguments):
    scratch = arguments.scratch.resolve()
    if scratch.exists() or scratch.is_relative_to(ROOT) or ROOT.is_relative_to(scratch):
        raise ValueError("scratch must be a new directory outside the repository")
    scratch.mkdir(parents=True)
    overall_deadline = time.monotonic() + 120
    runner_file = Path(prior.production.__file__)
    before = hashlib.sha256(runner_file.read_bytes()).hexdigest()
    transcript = []

    def emit(text):
        print(text, flush=True)
        transcript.append(text)
        (scratch / "transcript.txt").write_text("\n".join(transcript) + "\n", encoding="utf-8")

    emit("experiment=windows_job_cleanup timeout_seconds=2 return_bound_seconds=5")
    emit("python_version=" + sys.version.split()[0] + " windows_version=" + str(tuple(sys.getwindowsversion())))
    emit("runner_sha256_before=" + before)
    emit("spike_sha256=" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    emit("archived_helper_sha256=" + hashlib.sha256(HELPER.read_bytes()).hexdigest())
    verdict, attempts = "Inconclusive", 0
    for number in range(1, 4):
        if time.monotonic() + 30 > overall_deadline:
            emit("infrastructure_error=insufficient_remaining_safety_budget")
            verdict = "Inconclusive"
            break
        attempts += 1
        folder = scratch / f"attempt-{number}"
        folder.mkdir()
        (folder / "fixture-cwd").mkdir()
        current = SimpleNamespace(control=folder, nonce=secrets.token_hex(8), supervisor=os.getpid())
        collected, safety_stops = {}, []
        watchdog = False
        with (folder / "worker-stdout.txt").open("w", encoding="utf-8") as stdout, (folder / "worker-stderr.txt").open("w", encoding="utf-8") as stderr:
            process = subprocess.Popen(command("worker", current), cwd=folder, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
            try:
                deadline = time.monotonic() + 20
                while True:
                    collect_owned(current, collected)
                    if process.poll() is not None:
                        break
                    if time.monotonic() >= deadline:
                        watchdog = True
                        break
                    time.sleep(0.01)
                collect_owned(current, collected)
                result_path = folder / "measurement.json"
                result = load(result_path) if result_path.exists() else None
                verdict = result["verdict"] if result is not None and process.poll() == 0 and not watchdog else "Inconclusive"
                emit(f"attempt={number} setup_valid={str(result is not None and result['setup_valid']).lower()} worker_watchdog={str(watchdog).lower()} worker_exit_code={process.poll()}")
                if result is not None:
                    for key in ("worker_already_in_host_job", "job_handle_inheritable", "launch_order_valid", "resume_previous_suspend_count", "parent_member_before_resume", "entry", "cleanup_dispatch_seconds", "elapsed_seconds", "child_alive_at_return", "pipes_reached_eof", "stdout_marker_present", "stderr_marker_present", "control_alive_at_return", "directory_removed_before_rescue", "rescue_job_close", "native_refusal"):
                        if key in result:
                            emit(key + "=" + json.dumps(result[key], sort_keys=True))
                    emit("directory_winerror=" + json.dumps(result.get("directory_error", {}).get("winerror")))
                else:
                    emit("infrastructure_error=measurement_missing")
                event_file = folder / "native-events.json"
                if event_file.exists():
                    emit("native_operations=" + json.dumps([{key: item[key] for key in ("operation", "success", "error", "error_message") if key in item} for item in load(event_file)], separators=(",", ":")))
            finally:
                collect_owned(current, collected)
                stopped = stop_owned(process.pid, int(process._handle), folder, overall_deadline)
                if stopped is not None:
                    safety_stops.append(stopped)
                for role in ("parent", "child", "control"):
                    collect_owned(current, collected)
                    for record in list(collected.values()):
                        if record["role"] == role:
                            stopped = stop_owned(record["pid"], record["handle"], folder, overall_deadline)
                            if stopped is not None:
                                safety_stops.append(stopped)
                process.wait(timeout=max(0.1, min(2, overall_deadline - time.monotonic())))
                exited = all(not alive(record["handle"]) for record in collected.values())
                save(folder / "safety-cleanup.json", {"stops": safety_stops, "all_registered_processes_exited": exited})
                for record in collected.values():
                    prior.kernel.CloseHandle(record["handle"])
                workdir = folder / "fixture-cwd"
                if workdir.exists():
                    workdir.rmdir()
                emit("safety_stop_results=" + json.dumps([{"pid": item["pid"], "return_code": item["return_code"]} for item in safety_stops]))
                emit("all_registered_processes_exited=" + str(exited).lower() + " fixture_directory_removed=" + str(not workdir.exists()).lower())
        emit("attempt_verdict=" + verdict)
        if verdict != "Confirmed":
            break
    after = hashlib.sha256(runner_file.read_bytes()).hexdigest()
    emit("runner_source_unchanged=" + str(before == after).lower())
    if before != after:
        verdict = "Inconclusive"
    emit(f"attempts_completed={attempts} attempts_limit=3")
    emit("verdict=" + verdict)
    save(scratch / "summary.json", {"verdict": verdict, "attempts": attempts,
         "runner_sha256_before": before, "runner_sha256_after": after,
         "elapsed_including_rescue_seconds": 120 - (overall_deadline - time.monotonic())})
    return {"Confirmed": 0, "Refuted": 3, "Inconclusive": 2}[verdict]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("supervisor", "worker", "parent", "child", "control"), default="supervisor")
    parser.add_argument("--scratch", type=Path)
    parser.add_argument("--control", type=Path)
    parser.add_argument("--supervisor", type=int)
    parser.add_argument("--nonce")
    arguments = parser.parse_args()
    if arguments.mode == "supervisor":
        return supervisor(arguments)
    {"worker": worker, "parent": parent, "child": child, "control": control}[arguments.mode](arguments)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
