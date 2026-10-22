"""Native lifecycle regressions; fixture rescue never counts as runner cleanup."""

from __future__ import annotations

import gc
import importlib
import importlib.util
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from types import SimpleNamespace

from atom.runner import CommandOutcome, SubprocessRunner

import pytest


pytestmark = pytest.mark.skipif(os.name != "nt", reason="real Windows ownership")


def _windows_module():
    assert importlib.util.find_spec("atom._windows_process") is not None, (
        "Windows commands need a pre-execution native process owner"
    )
    return importlib.import_module("atom._windows_process")


def test_windows_native_job_is_private():
    native = _windows_module()._Native()
    job = native.create_job()
    try:
        assert native.handle_flags(job) & 1 == 0
        assert native.job_limits(job) == 0x2000
        assert native.active_processes(job) == 0
    finally:
        native.close(job)


def test_windows_launch_is_suspended_until_owned(tmp_path):
    import msvcrt

    native = _windows_module()._Native()
    assert hasattr(native, "launch"), "native launch must retain the suspended thread"
    marker = tmp_path / "executed"
    job = native.create_job()
    process = thread = None
    with open(os.devnull, "r+b") as stdio:
        handle = msvcrt.get_osfhandle(stdio.fileno())
        os.set_handle_inheritable(handle, True)
        try:
            process, thread = native.launch(
                [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"],
                tmp_path,
                (handle, handle, handle),
            )
            time.sleep(0.05)
            assert not marker.exists(), "the command executed before assignment"
            native.assign(job, process)
            assert native.contains(job, process)
            assert native.resume(thread) == 1
            assert native.wait(process, 5000)
            assert native.exit_code(process) == 0
            assert marker.exists()
        finally:
            native.close(job)
            if process:
                native.wait(process, 5000)
                native.close(process)
            if thread:
                native.close(thread)


def _read_ready_pid(path, deadline):
    while True:
        try:
            return int(path.read_text())
        except (FileNotFoundError, PermissionError):
            # A visible Windows record can still have a transient sharing denial.
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


@contextmanager
def _tree_fixture(tmp_path, *, hold_output, exit_code=0):
    from ctypes import wintypes

    native = _windows_module()._Native()
    native._bind("OpenProcess", [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE)
    native._bind("TerminateProcess", [wintypes.HANDLE, wintypes.UINT])
    ready = tmp_path / "child-ready"
    acknowledged = tmp_path / "identity-retained"
    empty_directory = tmp_path / "child-cwd"
    empty_directory.mkdir()
    identities = queue.Queue()

    def register_identity():
        try:
            pid = _read_ready_pid(ready, time.monotonic() + 6)
            handle = native._check(
                native.library.OpenProcess(0x100001, False, pid), "OpenProcess:fixture"
            )
            identities.put(handle)
            acknowledged.touch()
        except (OSError, ValueError) as error:
            identities.put(error)

    observer = threading.Thread(target=register_identity)
    observer.start()
    child = (
        "import os, pathlib, sys, time; "
        f"record=pathlib.Path({str(ready)!r}); temporary=record.with_suffix('.tmp'); "
        "temporary.write_text(str(os.getpid())); temporary.replace(record); "
        "print('child-out', flush=True); print('child-err', file=sys.stderr, flush=True); "
        "time.sleep(9)"
    )
    parent = (
        "import pathlib, subprocess, sys, time; "
        f"subprocess.Popen([sys.executable, '-c', {child!r}], cwd={str(empty_directory)!r}"
        + ("); " if hold_output else ", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); ")
        + f"ack=pathlib.Path({str(acknowledged)!r}); deadline=time.monotonic()+5; "
        + "\nwhile not ack.exists() and time.monotonic()<deadline: time.sleep(0.01)\n"
        + f"sys.exit({exit_code} if ack.exists() else 83)"
    )
    handle = None
    try:
        yield [sys.executable, "-c", parent], empty_directory, identities
    finally:
        observer.join(7)
        assert not observer.is_alive(), "fixture identity observer did not finish"
        if not identities.empty():
            handle = identities.get()
            if isinstance(handle, BaseException):
                raise handle
            try:
                if not native.wait(handle, 0):
                    stopped = native.library.TerminateProcess(handle, 91)
                    if not stopped and not native.wait(handle, 5000):
                        native._check(stopped, "TerminateProcess:rescue")
                assert native.wait(handle, 5000), "fixture rescue failed"
            finally:
                native.close(handle)


def _retained_identity(identities):
    handle = identities.get(timeout=1)
    identities.put(handle)
    assert not isinstance(handle, BaseException), str(handle)
    return handle


@pytest.mark.parametrize("exit_code", [0, 7])
def test_windows_success_stops_pipe_independent_child(tmp_path, exit_code):
    native = _windows_module()._Native()
    with _tree_fixture(tmp_path, hold_output=False, exit_code=exit_code) as (command, directory, identities):
        result = SubprocessRunner().run(command, tmp_path, timeout_seconds=5)
        handle = _retained_identity(identities)
        assert result.outcome is CommandOutcome.COMPLETED, result.stderr
        assert result.exit_code == exit_code, result.stderr
        assert native.wait(handle, 0), "a child survived successful command return"
        directory.rmdir()


def test_windows_fixture_waits_for_readable_identity_record(tmp_path, monkeypatch):
    ready = tmp_path / "child-ready"
    original_read = type(ready).read_text
    reads = 0

    def temporarily_unreadable(path, *arguments, **keywords):
        nonlocal reads
        if path == ready and path.exists():
            reads += 1
            if reads == 1:
                raise PermissionError("fixture identity record is temporarily unreadable")
        return original_read(path, *arguments, **keywords)

    monkeypatch.setattr(type(ready), "read_text", temporarily_unreadable)
    native = _windows_module()._Native()
    failure = None
    try:
        with _tree_fixture(tmp_path, hold_output=False) as (command, directory, identities):
            result = SubprocessRunner().run(command, tmp_path, timeout_seconds=5)
            assert result.succeeded, result.stderr
            assert native.wait(_retained_identity(identities), 0)
            directory.rmdir()
    except PermissionError as error:
        failure = error

    assert failure is None, "temporary record sharing must not invalidate identity setup"
    assert reads >= 2, "the injected unreadable-record condition was not exercised"


@pytest.mark.parametrize("error_type", [PermissionError, FileNotFoundError])
def test_windows_fixture_readiness_deadline_preserves_read_failure(
    tmp_path, monkeypatch, error_type,
):
    record = tmp_path / "missing-identity"
    denied = error_type("fixture record is unavailable")
    clocks = iter((0, 1))
    sleeps = []

    def refuse_read(*arguments, **keywords):
        raise denied

    monkeypatch.setattr(type(record), "read_text", refuse_read)
    monkeypatch.setattr(time, "monotonic", lambda: next(clocks))
    monkeypatch.setattr(time, "sleep", sleeps.append)

    with pytest.raises(error_type) as caught:
        _read_ready_pid(record, 1)

    assert caught.value is denied
    assert sleeps == [0.01]


def test_windows_parent_exits_before_timeout(tmp_path):
    native = _windows_module()._Native()
    with _tree_fixture(tmp_path, hold_output=True) as (command, directory, identities):
        started = time.monotonic()
        result = SubprocessRunner().run(command, tmp_path, timeout_seconds=2)
        elapsed = time.monotonic() - started
        handle = _retained_identity(identities)
        assert result.outcome is CommandOutcome.TIMED_OUT, result.stderr
        assert elapsed < 5
        assert result.stdout == "child-out\n"
        assert result.stderr.startswith("child-err\n")
        assert "timed out after 2 seconds" in result.stderr
        assert native.wait(handle, 0), "a child survived timed-out command return"
        directory.rmdir()


@pytest.mark.parametrize("timed_out", [False, True])
def test_windows_new_member_during_exit_capture_cannot_be_verified(
    tmp_path, monkeypatch, timed_out,
):
    module = _windows_module()
    native = module._Native()
    ready = tmp_path / "spawner-ready"
    trigger = tmp_path / "spawn-after-snapshot"
    registered = tmp_path / "late-child"
    directory = tmp_path / "late-child-cwd"
    directory.mkdir()
    grandchild = "import time; time.sleep(9)"
    spawner = (
        "import pathlib, subprocess, sys, time; "
        f"pathlib.Path({str(ready)!r}).touch(); "
        f"trigger=pathlib.Path({str(trigger)!r}); deadline=time.monotonic()+6; "
        "\nwhile not trigger.exists() and time.monotonic()<deadline: time.sleep(0.005)\n"
        "assert trigger.exists(), 'no snapshot trigger'\n"
        f"child=subprocess.Popen([sys.executable, '-c', {grandchild!r}], "
        f"cwd={str(directory)!r}, stdin=subprocess.DEVNULL, "
        "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
        f"record=pathlib.Path({str(registered)!r}); temporary=record.with_suffix('.tmp'); "
        "temporary.write_text(str(child.pid)); temporary.replace(record); time.sleep(9)"
    )
    parent = (
        "import pathlib, subprocess, sys, time; "
        f"subprocess.Popen([sys.executable, '-c', {spawner!r}], stdin=subprocess.DEVNULL"
        + ("); " if timed_out else ", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); ")
        + f"ready=pathlib.Path({str(ready)!r}); deadline=time.monotonic()+5; "
        + "\nwhile not ready.exists() and time.monotonic()<deadline: time.sleep(0.005)\n"
        + "assert ready.exists(), 'spawner never ready'\n"
        + "print('primary-out', flush=True)"
    )
    original_members = module._Native.member_handles
    late_identities = []

    def capture_then_spawn(self, job):
        identities = original_members(self, job)
        if late_identities:
            return identities
        try:
            before = self._query(job, 1, module._Accounting()).total_processes
            trigger.touch()
            pid = _read_ready_pid(registered, time.monotonic() + 2)
            identity = self._check(
                self.library.OpenProcess(0x100401, False, pid), "OpenProcess:late-fixture"
            )
            late_identities.append(identity)
            assert self.contains(job, identity), "the fixture child was outside the owned job"
            assert self._query(job, 1, module._Accounting()).total_processes == before + 1
            return identities
        except BaseException:
            for identity in identities:
                self.close(identity)
            raise

    monkeypatch.setattr(module._Native, "member_handles", capture_then_spawn)
    try:
        result = SubprocessRunner().run(
            [sys.executable, "-c", parent], tmp_path, timeout_seconds=1,
        )
        assert late_identities, "the intended snapshot/termination race was not reached"
        expected = CommandOutcome.TIMED_OUT if timed_out else CommandOutcome.RUNNER_ERROR
        assert result.outcome is expected, "a missed identity must not become verified completion"
        assert result.exit_code is None
        assert "job membership changed" in result.stderr
        assert "exit verification incomplete" in result.stderr
        assert result.stdout == "primary-out\n"
        assert result.duration_seconds < 5
    finally:
        for identity in late_identities:
            try:
                if not native.wait(identity, 0):
                    stopped = native.library.TerminateProcess(identity, 91)
                    if not stopped and not native.wait(identity, 5000):
                        native._check(stopped, "TerminateProcess:late-rescue")
                assert native.wait(identity, 5000), "late fixture rescue failed"
            finally:
                native.close(identity)
        directory.rmdir()


def test_windows_large_stdin_and_unicode_argv(tmp_path):
    directory = tmp_path / "space \u03bb"
    directory.mkdir()
    text = "large \u03bb input\n" * 20000
    arguments = ["", "two words", 'embedded"quote', "\u03bb"]
    script = (
        "import json, sys; "
        "print(json.dumps([sys.argv[1:], sys.stdin.read()])); "
        "sys.stderr.buffer.write(b'bad\\xff\\r\\nlast\\r')"
    )
    result = SubprocessRunner().run(
        [sys.executable, "-X", "utf8", "-c", script, *arguments],
        directory, timeout_seconds=5, stdin_text=text,
    )
    assert result.succeeded, result.stderr
    assert json.loads(result.stdout) == [arguments, text]
    assert result.stderr == "bad\ufffd\nlast\n"


def test_windows_communication_sleeps_only_while_idle(monkeypatch):
    module = _windows_module()
    owner = module._WindowsProcess(native=SimpleNamespace(exit_code=lambda process: 0))
    owner.parents["stdout"] = 1
    progress = iter((True, False, None))
    sleeps = []

    def pump():
        moved = next(progress)
        if moved is None:
            owner.parents.clear()
            return True
        return moved

    monkeypatch.setattr(owner, "_pump", pump)
    monkeypatch.setattr(module.time, "sleep", sleeps.append)

    owner.communicate("", 1)

    assert sleeps == [0.005], "moving bytes must not incur a fixed polling delay"


def test_windows_busy_communication_still_checks_deadline(monkeypatch):
    module = _windows_module()
    owner = module._WindowsProcess(native=SimpleNamespace(exit_code=lambda process: None))
    owner.parents["stdout"] = 1
    clocks = iter((0, 0.25, 1))
    sleeps = []
    monkeypatch.setattr(owner, "_pump", lambda: True)
    monkeypatch.setattr(module.time, "monotonic", lambda: next(clocks))
    monkeypatch.setattr(module.time, "sleep", sleeps.append)

    with pytest.raises(subprocess.TimeoutExpired):
        owner.communicate("", 1)

    assert sleeps == [], "a busy stream should check its deadline without sleeping"


def test_windows_large_streams_do_not_spend_the_deadline_sleeping(tmp_path):
    input_size = 8 * 1024 * 1024
    output_size = 24 * 1024 * 1024
    script = (
        "import sys; "
        f"assert sys.stdin.buffer.read() == b'i' * {input_size}; "
        f"sys.stdout.buffer.write(b'o' * {output_size}); "
        f"sys.stderr.buffer.write(b'e' * {output_size})"
    )

    result = SubprocessRunner().run(
        [sys.executable, "-c", script], tmp_path,
        timeout_seconds=8, stdin_text="i" * input_size,
    )

    assert result.succeeded, result.stderr[-500:]
    assert result.stdout == "o" * output_size
    assert result.stderr == "e" * output_size


def test_windows_cmd_shim_preserves_arguments(tmp_path):
    script = tmp_path / "echo.py"
    script.write_text("import json,sys; print(json.dumps(sys.argv[1:]))")
    shim = tmp_path / "echo.cmd"
    shim.write_text(f'@"{sys.executable}" "%~dp0echo.py" %*\n')
    arguments = ["two words", "\u03bb"]

    result = SubprocessRunner().run([str(shim), *arguments], tmp_path, timeout_seconds=5)

    assert result.succeeded, result.stderr
    assert json.loads(result.stdout) == arguments


def _native_failure(operation):
    import ctypes

    error = ctypes.WinError(5)
    error.strerror = f"{operation}: {error.strerror}"
    return error


@pytest.mark.parametrize("operation", ["create_job", "pipe", "launch", "assign", "contains", "resume"])
def test_windows_setup_failure_never_executes_command(tmp_path, monkeypatch, operation):
    module = _windows_module()
    marker = tmp_path / "must-not-run"

    def refuse(*args, **kwargs):
        raise _native_failure(operation)

    monkeypatch.setattr(module._Native, operation, refuse)
    result = SubprocessRunner().run(
        [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"],
        tmp_path, timeout_seconds=1,
    )
    assert result.outcome is CommandOutcome.RUNNER_ERROR
    assert result.exit_code is None
    assert operation in result.stderr
    assert "WinError 5" in result.stderr
    assert not marker.exists()


@pytest.mark.parametrize("operation", ["terminate_job", "active_processes"])
def test_windows_timeout_keeps_primary_reason_on_cleanup_failure(
    tmp_path, monkeypatch, operation,
):
    module = _windows_module()

    def refuse(*args):
        raise _native_failure(operation)

    monkeypatch.setattr(module._Native, operation, refuse)
    with _tree_fixture(tmp_path, hold_output=True) as (command, directory, identities):
        started = time.monotonic()
        result = SubprocessRunner().run(command, tmp_path, timeout_seconds=1)
        assert time.monotonic() - started < 4
        assert result.outcome is CommandOutcome.TIMED_OUT
        assert result.exit_code is None
        assert "timed out" in result.stderr
        assert "cleanup incomplete" in result.stderr
        assert operation in result.stderr


@pytest.mark.parametrize("failed_query", [1, 2])
def test_windows_admission_query_failure_cannot_verify_cleanup(
    tmp_path, monkeypatch, failed_query,
):
    module = _windows_module()
    original = module._Native.total_processes
    calls = 0

    def fail_query(self, job):
        nonlocal calls
        calls += 1
        if calls == failed_query:
            raise _native_failure("QueryInformationJobObject:total_processes")
        return original(self, job)

    monkeypatch.setattr(module._Native, "total_processes", fail_query)
    result = SubprocessRunner().run([sys.executable, "-c", "print('reply')"], tmp_path)

    assert calls == 2
    assert result.outcome is CommandOutcome.RUNNER_ERROR
    assert result.exit_code is None
    assert result.stdout == "reply\n"
    assert "QueryInformationJobObject:total_processes" in result.stderr
    assert "cleanup incomplete" in result.stderr


@pytest.mark.parametrize("during_finalization", [0, 1, 2])
def test_windows_interrupt_finalizes_owned_processes(tmp_path, monkeypatch, during_finalization):
    module = _windows_module()
    if during_finalization:
        original = module._Native.active_processes
        interrupted = 0

        def interrupt_once(self, job):
            nonlocal interrupted
            if interrupted < during_finalization:
                interrupted += 1
                raise KeyboardInterrupt
            return original(self, job)

        monkeypatch.setattr(module._Native, "active_processes", interrupt_once)
    else:
        def interrupt_after_readiness(self, input_text, timeout_seconds):
            deadline = time.monotonic() + 5
            while not (tmp_path / "identity-retained").exists():
                self._pump()
                assert time.monotonic() < deadline, "fixture never became ready"
                time.sleep(0.01)
            raise KeyboardInterrupt

        monkeypatch.setattr(module._WindowsProcess, "communicate", interrupt_after_readiness)

    native = module._Native()
    with _tree_fixture(tmp_path, hold_output=False) as (command, directory, identities):
        with pytest.raises(KeyboardInterrupt):
            SubprocessRunner().run(command, tmp_path, timeout_seconds=5)
        handle = _retained_identity(identities)
        assert native.wait(handle, 0), "interrupt returned before the owned child exited"
        directory.rmdir()


@pytest.mark.parametrize("stage", ["completion_receipt", "missing_file_diagnosis"])
def test_windows_interrupt_outside_communication_still_finalizes(
    tmp_path, monkeypatch, stage,
):
    from atom import runner as runner_module

    module = _windows_module()
    original_owner = module._WindowsProcess
    interrupted = KeyboardInterrupt()
    owners = []

    class InterruptedOwner(original_owner):
        def __init__(self):
            super().__init__()
            self.interrupt_receipt = False
            self.finalizations = 0
            owners.append(self)

        @property
        def returncode(self):
            if self.interrupt_receipt:
                self.interrupt_receipt = False
                raise interrupted
            return self.saved_returncode

        @returncode.setter
        def returncode(self, value):
            self.saved_returncode = value

        def communicate(self, *arguments):
            super().communicate(*arguments)
            self.interrupt_receipt = True

        def finalize(self, *arguments):
            self.finalizations += 1
            return super().finalize(*arguments)

    def interrupt_diagnosis(*arguments):
        raise interrupted

    monkeypatch.setattr(module, "_WindowsProcess", InterruptedOwner)
    try:
        if stage == "completion_receipt":
            native = module._Native()
            with _tree_fixture(tmp_path, hold_output=False) as (command, directory, identities):
                with pytest.raises(KeyboardInterrupt) as caught:
                    SubprocessRunner().run(command, tmp_path, timeout_seconds=5)
                assert caught.value is interrupted
                assert owners[0].finalizations == 1, "the completion-receipt gap skipped cleanup"
                assert native.wait(_retained_identity(identities), 0)
                directory.rmdir()
        else:
            monkeypatch.setattr(runner_module, "_diagnose_missing_file", interrupt_diagnosis)
            with pytest.raises(KeyboardInterrupt) as caught:
                SubprocessRunner().run(["missing-review-fixture.exe"], tmp_path)
            assert caught.value is interrupted
            assert owners[0].finalizations == 1, "diagnostic handling skipped cleanup"
        assert not owners[0].job
        assert not owners[0].parents
    finally:
        for owner in owners:
            if owner.job:
                original_owner.finalize(owner, 2)


def test_windows_communication_observes_deferred_interrupt(monkeypatch):
    module = _windows_module()
    owner = module._WindowsProcess(native=SimpleNamespace(exit_code=lambda process: None))
    owner.interrupted = True

    def unexpected_io():
        pytest.fail("communication ignored an already-deferred interrupt")

    monkeypatch.setattr(owner, "_pump", unexpected_io)

    with pytest.raises(KeyboardInterrupt):
        owner.communicate("", 1)


def test_windows_sigint_during_communication_is_prompt_and_reclaims_children(
    tmp_path, monkeypatch,
):
    module = _windows_module()
    original = module._WindowsProcess.communicate
    previous_handler = signal.getsignal(signal.SIGINT)

    def interrupt_after_readiness(self, input_text, timeout_seconds):
        deadline = time.monotonic() + 5
        while not (tmp_path / "identity-retained").exists():
            self._pump()
            assert time.monotonic() < deadline, "fixture never became ready"
            time.sleep(0.005)
        signal.raise_signal(signal.SIGINT)
        original(self, input_text, timeout_seconds)

    monkeypatch.setattr(module._WindowsProcess, "communicate", interrupt_after_readiness)
    native = module._Native()
    with _tree_fixture(tmp_path, hold_output=True) as (command, directory, identities):
        started = time.monotonic()
        with pytest.raises(KeyboardInterrupt):
            SubprocessRunner().run(command, tmp_path, timeout_seconds=10)
        assert time.monotonic() - started < 4
        assert native.wait(_retained_identity(identities), 0)
        directory.rmdir()
    assert signal.getsignal(signal.SIGINT) is previous_handler


@pytest.mark.parametrize("exit_code", [0, 7])
def test_windows_lifecycle_failure_preserves_primary_exit(tmp_path, monkeypatch, exit_code):
    module = _windows_module()
    original_create = module._Native.create_job
    original_close = module._Native.close
    jobs = []

    def capture_job(self):
        job = original_create(self)
        jobs.append(job)
        return job

    def refuse_job_close(self, handle):
        if handle in jobs:
            raise _native_failure("CloseHandle:job")
        return original_close(self, handle)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(module._Native, "create_job", capture_job)
            patch.setattr(module._Native, "close", refuse_job_close)
            result = SubprocessRunner().run(
                [sys.executable, "-c", f"import sys; print('reply'); sys.exit({exit_code})"],
                tmp_path, timeout_seconds=2,
            )
        assert result.outcome is CommandOutcome.RUNNER_ERROR
        assert result.exit_code is None
        assert result.stdout == "reply\n"
        assert f"primary exit code {exit_code}" in result.stderr
        assert "CloseHandle:job" in result.stderr
        assert "WinError 5" in result.stderr
    finally:
        native = module._Native()
        for job in jobs:
            original_close(native, job)


def test_windows_partial_capture_names_incomplete_streams(tmp_path, monkeypatch):
    module = _windows_module()
    original_read = module._Native.read
    refuse_reads = False

    def read(self, handle):
        if refuse_reads:
            raise _native_failure("ReadFile:injected")
        return original_read(self, handle)

    def timeout_after_markers(self, input_text, timeout_seconds):
        nonlocal refuse_reads
        deadline = time.monotonic() + 5
        while not all(self.buffers.values()):
            self._pump()
            assert time.monotonic() < deadline, "fixture did not print both markers"
            time.sleep(0.005)
        refuse_reads = True
        raise subprocess.TimeoutExpired("injected command", timeout_seconds)

    monkeypatch.setattr(module._Native, "read", read)
    monkeypatch.setattr(module._WindowsProcess, "communicate", timeout_after_markers)
    result = SubprocessRunner().run(
        [sys.executable, "-c", "import sys,time; print('out',flush=True); print('err',file=sys.stderr,flush=True); time.sleep(9)"],
        tmp_path, timeout_seconds=1,
    )
    assert result.outcome is CommandOutcome.TIMED_OUT
    assert result.stdout == "out\n"
    assert result.stderr.startswith("err\n")
    assert "ReadFile:injected" in result.stderr
    assert "output incomplete: stdout, stderr" in result.stderr


def test_windows_concurrent_runs_are_isolated(tmp_path):
    runner = SubprocessRunner()
    control = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(9)"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            slow = executor.submit(
                runner.run,
                [sys.executable, "-c", "import time; print('slow'); time.sleep(0.5)"],
                tmp_path,
            )
            fast = executor.submit(
                runner.run, [sys.executable, "-c", "print('fast')"], tmp_path,
            )
            assert fast.result(timeout=5).stdout == "fast\n"
            assert control.poll() is None
            slow_result = slow.result(timeout=5)
            assert slow_result.succeeded, slow_result.stderr
            assert slow_result.stdout == "slow\n"
            assert control.poll() is None
    finally:
        control.terminate()
        control.wait(timeout=5)


def test_windows_repeated_runs_release_handles_and_workers(tmp_path):
    import ctypes
    from ctypes import wintypes

    native = _windows_module()._Native()
    native._bind("GetProcessHandleCount", [wintypes.HANDLE, wintypes.LPVOID])

    def handle_count():
        count = wintypes.DWORD()
        native._check(
            native.library.GetProcessHandleCount(wintypes.HANDLE(-1), ctypes.byref(count)),
            "GetProcessHandleCount:fixture",
        )
        return count.value

    runner = SubprocessRunner()
    assert runner.run([sys.executable, "-c", "pass"], tmp_path).succeeded
    gc.collect()
    baseline = handle_count()
    threads = set(threading.enumerate())
    for _ in range(12):
        result = runner.run([sys.executable, "-c", "print('done')"], tmp_path)
        assert result.succeeded, result.stderr
    gc.collect()
    assert handle_count() <= baseline, "native handles leaked across command runs"
    assert set(threading.enumerate()) == threads


def test_windows_interrupt_during_native_launch_reclaims_suspended_parent(tmp_path, monkeypatch):
    import ctypes
    from ctypes import wintypes

    module = _windows_module()
    native = module._Native()
    native._bind(
        "DuplicateHandle",
        [wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE, wintypes.LPVOID,
         wintypes.DWORD, wintypes.BOOL, wintypes.DWORD],
    )
    retained = wintypes.HANDLE()
    original_launch = module._Native.launch
    original_close = module._Native.close
    launched = []
    closed = set()

    def interrupt_launch(self, *arguments):
        process, thread = original_launch(self, *arguments)
        launched.extend((process, thread))
        native._check(
            native.library.DuplicateHandle(
                wintypes.HANDLE(-1), process, wintypes.HANDLE(-1),
                ctypes.byref(retained), 0, False, 2,
            ),
            "DuplicateHandle:fixture",
        )
        raise KeyboardInterrupt

    def record_close(self, handle):
        original_close(self, handle)
        closed.add(handle)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(module._Native, "launch", interrupt_launch)
            patch.setattr(module._Native, "close", record_close)
            with pytest.raises(KeyboardInterrupt):
                SubprocessRunner().run([sys.executable, "-c", "pass"], tmp_path)
        assert retained.value
        assert native.wait(retained, 0), "interrupted launch left a suspended parent alive"
    finally:
        if retained.value:
            if not native.wait(retained, 0):
                native.terminate_process(retained)
            assert native.wait(retained, 5000)
            native.close(retained)
        for handle in launched:
            if handle not in closed:
                original_close(native, handle)


def test_windows_sigint_during_handle_acquisition_does_not_lose_job(tmp_path, monkeypatch):
    module = _windows_module()
    original_create = module._Native.create_job
    original_close = module._Native.close
    created = []
    closed = set()
    previous_handler = signal.getsignal(signal.SIGINT)

    def create_then_interrupt(self):
        job = original_create(self)
        created.append(job)
        signal.raise_signal(signal.SIGINT)
        return job

    def record_close(self, handle):
        original_close(self, handle)
        closed.add(handle)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(module._Native, "create_job", create_then_interrupt)
            patch.setattr(module._Native, "close", record_close)
            with pytest.raises(KeyboardInterrupt):
                SubprocessRunner().run([sys.executable, "-c", "pass"], tmp_path)
        assert signal.getsignal(signal.SIGINT) is previous_handler
        assert created and created[0] in closed, "SIGINT lost the newly acquired job"
    finally:
        native = module._Native()
        for job in created:
            if job not in closed:
                original_close(native, job)


def test_windows_broken_executable_is_diagnosed_as_unlaunchable(tmp_path):
    executable = tmp_path / "broken.exe"
    executable.touch()
    result = SubprocessRunner().run([str(executable)], tmp_path, timeout_seconds=1)
    assert result.outcome is CommandOutcome.TOOL_MISSING, result.stderr
    assert "not launchable" in result.stderr
    assert "Reinstall the tool" in result.stderr


def test_windows_runner_assigns_and_checks_membership_before_resume(tmp_path, monkeypatch):
    module = _windows_module()
    events = []
    child_handles = []
    originals = {name: getattr(module._Native, name) for name in ("pipe", "launch", "assign", "contains", "resume")}

    def pipe(self, reading):
        parent, child = originals["pipe"](self, reading)
        assert self.handle_flags(parent) & 1 == 0
        assert self.handle_flags(child) & 1 == 1
        child_handles.append(child)
        return parent, child

    def launch(self, command, directory, stdio, information=None):
        assert tuple(stdio) == tuple(child_handles)
        events.append("launch")
        return originals["launch"](self, command, directory, stdio, information)

    monkeypatch.setattr(module._Native, "pipe", pipe)
    monkeypatch.setattr(module._Native, "launch", launch)
    for name in ("assign", "contains", "resume"):
        def record(self, *arguments, operation=name):
            events.append(operation)
            return originals[operation](self, *arguments)
        monkeypatch.setattr(module._Native, name, record)

    result = SubprocessRunner().run([sys.executable, "-c", "pass"], tmp_path)
    assert result.succeeded, result.stderr
    assert events[:4] == ["launch", "assign", "contains", "resume"]


def test_windows_child_can_close_stdin_early(tmp_path):
    result = SubprocessRunner().run(
        [sys.executable, "-c", "print('no input needed')"],
        tmp_path, timeout_seconds=2, stdin_text="unused\n" * 100000,
    )
    assert result.succeeded, result.stderr
    assert result.stdout == "no input needed\n"


@pytest.mark.parametrize("primary", [None, ValueError("fixture bug"), KeyboardInterrupt()])
def test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles(
    monkeypatch, capsys, primary,
):
    import ctypes

    native = _windows_module()._Native()
    created = []
    closed = set()
    original_close = native.close
    failed_close = False

    for name in ("CreateNamedPipeW", "CreateFileW"):
        original = getattr(native.library, name)

        def capture(*arguments, function=original):
            handle = function(*arguments)
            created.append(handle)
            return handle

        monkeypatch.setattr(native.library, name, capture)

    def refuse_connect(*arguments):
        if primary is not None:
            raise primary
        ctypes.set_last_error(5)
        return False

    def refuse_first_close(handle):
        nonlocal failed_close
        if not failed_close:
            failed_close = True
            raise _native_failure("CloseHandle:rollback")
        original_close(handle)
        closed.add(handle)

    monkeypatch.setattr(native.library, "ConnectNamedPipe", refuse_connect)
    monkeypatch.setattr(native, "close", refuse_first_close)
    try:
        with pytest.raises(type(primary) if primary is not None else OSError) as caught:
            native.pipe(True)
        if primary is None:
            assert "ConnectNamedPipe" in str(caught.value), "rollback hid the primary error"
            assert "CloseHandle:rollback" in str(caught.value)
        else:
            assert caught.value is primary
            assert "CloseHandle:rollback" in capsys.readouterr().err
        assert created[0] in closed, "one failed close skipped the other owned endpoint"
    finally:
        for handle in created:
            if handle not in closed:
                original_close(handle)
