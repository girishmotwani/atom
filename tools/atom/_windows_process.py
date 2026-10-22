"""Own native Windows command lifetimes without parent-PID rediscovery."""

from __future__ import annotations

import ctypes
import signal
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from ctypes import wintypes


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("process_time", ctypes.c_longlong),
        ("job_time", ctypes.c_longlong),
        ("flags", wintypes.DWORD),
        ("minimum_working_set", ctypes.c_size_t),
        ("maximum_working_set", ctypes.c_size_t),
        ("active_limit", wintypes.DWORD),
        ("affinity", ctypes.c_size_t),
        ("priority", wintypes.DWORD),
        ("scheduling", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_ulonglong)
        for name in ("reads", "writes", "other", "read_bytes", "write_bytes", "other_bytes")
    ]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("basic", _BasicLimits),
        ("io", _IoCounters),
        ("process_memory", ctypes.c_size_t),
        ("job_memory", ctypes.c_size_t),
        ("peak_process_memory", ctypes.c_size_t),
        ("peak_job_memory", ctypes.c_size_t),
    ]


class _Accounting(ctypes.Structure):
    _fields_ = [
        ("user_time", ctypes.c_longlong),
        ("kernel_time", ctypes.c_longlong),
        ("period_user_time", ctypes.c_longlong),
        ("period_kernel_time", ctypes.c_longlong),
        ("page_faults", wintypes.DWORD),
        ("total_processes", wintypes.DWORD),
        ("active_processes", wintypes.DWORD),
        ("terminated_processes", wintypes.DWORD),
    ]


class _StartupInfo(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("reserved", wintypes.LPWSTR),
        ("desktop", wintypes.LPWSTR),
        ("title", wintypes.LPWSTR),
        *[(name, wintypes.DWORD) for name in (
            "x", "y", "x_size", "y_size", "x_chars", "y_chars", "fill", "flags"
        )],
        ("show_window", wintypes.WORD),
        ("reserved_size", wintypes.WORD),
        ("reserved_bytes", wintypes.LPVOID),
        ("stdin", wintypes.HANDLE),
        ("stdout", wintypes.HANDLE),
        ("stderr", wintypes.HANDLE),
    ]


class _StartupInfoEx(ctypes.Structure):
    _fields_ = [("startup", _StartupInfo), ("attributes", wintypes.LPVOID)]


class _ProcessInfo(ctypes.Structure):
    _fields_ = [
        ("process", wintypes.HANDLE),
        ("thread", wintypes.HANDLE),
        ("process_id", wintypes.DWORD),
        ("thread_id", wintypes.DWORD),
    ]


class _SecurityAttributes(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.DWORD),
        ("descriptor", wintypes.LPVOID),
        ("inherit", wintypes.BOOL),
    ]


class _Native:
    """Keep native failures attributable to the operation that produced them."""

    def __init__(self):
        self.library = ctypes.WinDLL("kernel32", use_last_error=True)
        self._bind("CreateJobObjectW", [wintypes.LPVOID, wintypes.LPCWSTR], wintypes.HANDLE)
        self._bind(
            "SetInformationJobObject",
            [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD],
        )
        self._bind(
            "QueryInformationJobObject",
            [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, wintypes.LPVOID],
        )
        self._bind("GetHandleInformation", [wintypes.HANDLE, wintypes.LPVOID])
        self._bind("CloseHandle", [wintypes.HANDLE])
        self._bind("AssignProcessToJobObject", [wintypes.HANDLE, wintypes.HANDLE])
        self._bind("IsProcessInJob", [wintypes.HANDLE, wintypes.HANDLE, wintypes.LPVOID])
        self._bind("ResumeThread", [wintypes.HANDLE], wintypes.DWORD)
        self._bind("WaitForSingleObject", [wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD)
        self._bind("GetExitCodeProcess", [wintypes.HANDLE, wintypes.LPVOID])
        self._bind(
            "InitializeProcThreadAttributeList",
            [wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID],
        )
        self._bind(
            "UpdateProcThreadAttribute",
            [wintypes.LPVOID, wintypes.DWORD, ctypes.c_size_t, wintypes.LPVOID,
             ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID],
        )
        self._bind("DeleteProcThreadAttributeList", [wintypes.LPVOID], None)
        self._bind(
            "CreateProcessW",
            [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.LPVOID, wintypes.LPVOID,
             wintypes.BOOL, wintypes.DWORD, wintypes.LPVOID, wintypes.LPCWSTR,
             wintypes.LPVOID, wintypes.LPVOID],
        )
        self._bind("TerminateJobObject", [wintypes.HANDLE, wintypes.UINT])
        self._bind("TerminateProcess", [wintypes.HANDLE, wintypes.UINT])
        self._bind(
            "OpenProcess",
            [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD],
            wintypes.HANDLE,
        )
        self._bind(
            "CreateNamedPipeW",
            [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
             wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID],
            wintypes.HANDLE,
        )
        self._bind(
            "CreateFileW",
            [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
             wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE],
            wintypes.HANDLE,
        )
        self._bind("ConnectNamedPipe", [wintypes.HANDLE, wintypes.LPVOID])
        for name in ("ReadFile", "WriteFile"):
            self._bind(
                name,
                [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                 wintypes.LPVOID, wintypes.LPVOID],
            )

    def _bind(self, name, arguments, result=wintypes.BOOL):
        function = getattr(self.library, name)
        function.argtypes = arguments
        function.restype = result

    def _check(self, result, operation):
        if not result:
            error = ctypes.WinError(ctypes.get_last_error())
            error.strerror = f"{operation}: {error.strerror}"
            raise error
        return result

    def create_job(self):
        job = self._check(self.library.CreateJobObjectW(None, None), "CreateJobObjectW")
        try:
            limits = _ExtendedLimits()
            limits.basic.flags = 0x2000  # Last private handle is the crash-cleanup backstop.
            self._check(
                self.library.SetInformationJobObject(
                    job, 9, ctypes.byref(limits), ctypes.sizeof(limits)
                ),
                "SetInformationJobObject",
            )
        except BaseException as error:
            self._rollback([job], error)
            raise
        return job

    def _query(self, job, information_class, value):
        self._check(
            self.library.QueryInformationJobObject(
                job, information_class, ctypes.byref(value), ctypes.sizeof(value), None
            ),
            "QueryInformationJobObject",
        )
        return value

    def handle_flags(self, handle):
        flags = wintypes.DWORD()
        self._check(
            self.library.GetHandleInformation(handle, ctypes.byref(flags)),
            "GetHandleInformation",
        )
        return flags.value

    def job_limits(self, job):
        return self._query(job, 9, _ExtendedLimits()).basic.flags

    def active_processes(self, job):
        return self._query(job, 1, _Accounting()).active_processes

    def total_processes(self, job):
        return self._query(job, 1, _Accounting()).total_processes

    def close(self, handle):
        self._check(self.library.CloseHandle(handle), "CloseHandle")

    def _rollback(self, handles, primary):
        problems = []
        for handle in handles:
            try:
                self.close(handle)
            except OSError as error:
                problems.append(str(error))
        if problems:
            detail = f"atom: Windows native rollback incomplete: {'; '.join(problems)}"
            if isinstance(primary, OSError):
                raise OSError(f"{primary}; {detail}") from primary
            print(detail, file=sys.stderr)

    def launch(self, command, working_directory, stdio, information=None):
        size = ctypes.c_size_t()
        # The first call obtains the variable-sized attribute buffer, not a launch.
        self.library.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
        if ctypes.get_last_error() != 122:
            self._check(False, "InitializeProcThreadAttributeList:size")
        attributes = ctypes.create_string_buffer(size.value)
        self._check(
            self.library.InitializeProcThreadAttributeList(
                attributes, 1, 0, ctypes.byref(size)
            ),
            "InitializeProcThreadAttributeList",
        )
        try:
            inherited = (wintypes.HANDLE * len(set(stdio)))(*dict.fromkeys(stdio))
            self._check(
                self.library.UpdateProcThreadAttribute(
                    attributes, 0, 0x20002, inherited, ctypes.sizeof(inherited), None, None
                ),
                "UpdateProcThreadAttribute:handle_list",
            )
            startup = _StartupInfoEx()
            startup.startup.cb = ctypes.sizeof(startup)
            startup.startup.flags = 0x100  # STARTF_USESTDHANDLES
            startup.startup.stdin, startup.startup.stdout, startup.startup.stderr = stdio
            startup.attributes = ctypes.cast(attributes, wintypes.LPVOID)
            if information is None:
                information = _ProcessInfo()
            command_line = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
            self._check(
                self.library.CreateProcessW(
                    None, command_line, None, None, True,
                    0x80000 | 4,  # Extended startup info; primary thread remains suspended.
                    None, str(working_directory), ctypes.byref(startup),
                    ctypes.byref(information),
                ),
                "CreateProcessW",
            )
            return information.process, information.thread
        finally:
            self.library.DeleteProcThreadAttributeList(attributes)

    def assign(self, job, process):
        self._check(
            self.library.AssignProcessToJobObject(job, process),
            "AssignProcessToJobObject",
        )

    def contains(self, job, process):
        contained = wintypes.BOOL()
        self._check(
            self.library.IsProcessInJob(process, job, ctypes.byref(contained)),
            "IsProcessInJob",
        )
        return bool(contained.value)

    def resume(self, thread):
        previous = self.library.ResumeThread(thread)
        if previous == 0xFFFFFFFF:
            self._check(False, "ResumeThread")
        return previous

    def wait(self, process, milliseconds):
        result = self.library.WaitForSingleObject(process, milliseconds)
        if result == 258:
            return False
        if result != 0:
            self._check(False, "WaitForSingleObject")
        return True

    def exit_code(self, process):
        if not self.wait(process, 0):
            return None
        code = wintypes.DWORD()
        self._check(
            self.library.GetExitCodeProcess(process, ctypes.byref(code)),
            "GetExitCodeProcess",
        )
        return code.value

    def terminate_job(self, job):
        self._check(self.library.TerminateJobObject(job, 1), "TerminateJobObject")

    def terminate_process(self, process):
        self._check(self.library.TerminateProcess(process, 1), "TerminateProcess")

    def member_handles(self, job):
        capacity = 16
        for _ in range(3):
            buffer = ctypes.create_string_buffer(8 + capacity * ctypes.sizeof(ctypes.c_size_t))
            result = self.library.QueryInformationJobObject(
                job, 3, buffer, len(buffer), None
            )
            assigned = wintypes.DWORD.from_buffer(buffer).value
            if result:
                break
            if ctypes.get_last_error() != 234:
                self._check(False, "QueryInformationJobObject:process_ids")
            capacity = max(capacity * 2, assigned)
        else:
            raise OSError("QueryInformationJobObject: process list kept growing")
        count = wintypes.DWORD.from_buffer(buffer, 4).value
        identities = []
        try:
            for pid in (ctypes.c_size_t * count).from_buffer(buffer, 8):
                handle = self.library.OpenProcess(0x100400, False, pid)
                if not handle:
                    if ctypes.get_last_error() == 87:
                        continue  # The listed member exited before OpenProcess.
                    self._check(False, "OpenProcess:job_member")
                identities.append(handle)
                if not self.contains(job, handle):
                    self.close(handle)
                    identities.pop()
            return identities
        except BaseException as error:
            self._rollback(identities, error)
            raise

    def pipe(self, reading):
        name = rf"\\.\pipe\atom-{uuid.uuid4().hex}"
        # Only the parent endpoint is nonblocking. The tool sees ordinary blocking
        # stdio; the coordinator never leaves a read/write running after return.
        parent = self.library.CreateNamedPipeW(
            name, (1 if reading else 2) | 0x80000, 1 | 8, 1, 65536, 65536, 0, None
        )
        if parent == ctypes.c_void_p(-1).value:
            self._check(False, "CreateNamedPipeW")
        child = None
        try:
            security = _SecurityAttributes(ctypes.sizeof(_SecurityAttributes), None, True)
            child = self.library.CreateFileW(
                name, 0x40000000 if reading else 0x80000000,
                0, ctypes.byref(security), 3, 0, None,
            )
            if child == ctypes.c_void_p(-1).value:
                child = None
                self._check(False, "CreateFileW:stdio")
            if not self.library.ConnectNamedPipe(parent, None):
                if ctypes.get_last_error() != 535:  # Client connected before this call.
                    self._check(False, "ConnectNamedPipe")
            return parent, child
        except BaseException as error:
            self._rollback([child, parent] if child else [parent], error)
            raise

    def read(self, handle):
        buffer = ctypes.create_string_buffer(16384)
        count = wintypes.DWORD()
        if not self.library.ReadFile(handle, buffer, len(buffer), ctypes.byref(count), None):
            error = ctypes.get_last_error()
            if error == 232:  # No bytes available yet on this nonblocking endpoint.
                return b""
            if error == 109:
                return None
            self._check(False, "ReadFile")
        return buffer.raw[:count.value]

    def write(self, handle, data):
        count = wintypes.DWORD()
        buffer = ctypes.create_string_buffer(data)
        if not self.library.WriteFile(handle, buffer, len(data), ctypes.byref(count), None):
            if ctypes.get_last_error() in (109, 232):
                return None  # Like Popen.communicate, a tool may close stdin early.
            self._check(False, "WriteFile")
        return count.value


class _WindowsProcess:
    """Serialize one job's communication so no pipe worker can outlive its run."""

    def __init__(self, native=None):
        self.native = native if native is not None else _Native()
        self.job = None
        self.information = _ProcessInfo()
        self.parents = {}
        self.children = {}
        self.buffers = {"stdout": bytearray(), "stderr": bytearray()}
        self.input = b""
        self.returncode = None
        self.interrupted = False

    @property
    def process(self):
        return self.information.process

    @process.setter
    def process(self, handle):
        self.information.process = handle

    @property
    def thread(self):
        return self.information.thread

    @thread.setter
    def thread(self, handle):
        self.information.thread = handle

    @contextmanager
    def defer_interrupts(self):
        if threading.current_thread() is not threading.main_thread():
            yield
            return
        previous = signal.getsignal(signal.SIGINT)
        if previous is signal.SIG_IGN:
            yield
            return

        def remember_interrupt(signum, frame):
            self.interrupted = True

        # Native HANDLE returns cannot be recovered if SIGINT raises between
        # acquisition and registration. Defer the raise, not the owned cleanup.
        signal.signal(signal.SIGINT, remember_interrupt)
        try:
            yield
        finally:
            signal.signal(signal.SIGINT, previous)

    def start(self, command, working_directory):
        self.job = self.native.create_job()
        for name in ("stdin", "stdout", "stderr"):
            self.parents[name], self.children[name] = self.native.pipe(name != "stdin")
        # CreateProcess fills owner-held storage even if Python is interrupted
        # before the native wrapper can hand its return value back.
        self.native.launch(
            command, working_directory, tuple(self.children.values()), self.information
        )
        self.native.assign(self.job, self.process)
        if not self.native.contains(self.job, self.process):
            raise OSError("IsProcessInJob: parent did not join the owned job")
        if self.native.resume(self.thread) != 1:
            raise OSError("ResumeThread: unexpected suspended-thread count")
        self.native.close(self.thread)
        self.thread = None
        for name in tuple(self.children):
            self.native.close(self.children[name])
            del self.children[name]

    def _close_parent(self, name):
        self.native.close(self.parents[name])
        del self.parents[name]

    def _pump(self):
        progressed = False
        for name in tuple(self.parents):
            if name == "stdin":
                if not self.input:
                    self._close_parent(name)
                    progressed = True
                    continue
                count = self.native.write(self.parents[name], self.input[:16384])
                if count is None:
                    self._close_parent(name)
                    self.input = b""
                    progressed = True
                else:
                    self.input = self.input[count:]
                    progressed = progressed or count > 0
            else:
                data = self.native.read(self.parents[name])
                if data is None:
                    self._close_parent(name)
                    progressed = True
                else:
                    self.buffers[name].extend(data)
                    progressed = progressed or bool(data)
        return progressed

    def communicate(self, input_text, timeout_seconds):
        self.input = input_text.replace("\n", "\r\n").encode("utf-8", errors="replace")
        deadline = time.monotonic() + timeout_seconds
        while True:
            if self.interrupted:
                raise KeyboardInterrupt
            progressed = self._pump()
            self.returncode = self.native.exit_code(self.process)
            if not self.parents and self.returncode is not None:
                return
            if time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired("Windows command", timeout_seconds)
            if not progressed:
                time.sleep(0.005)

    def output(self, name):
        return self.buffers[name].decode("utf-8", errors="replace").replace(
            "\r\n", "\n"
        ).replace("\r", "\n")

    def finalize(self, grace_seconds):
        deadline = time.monotonic() + grace_seconds
        problems = []
        members = []

        def attempt(function, *arguments):
            # A second Ctrl-C must not jump over the last job-handle close.
            # Retries are finite even if a handler repeatedly interrupts cleanup.
            for _ in range(3):
                try:
                    return True, function(*arguments)
                except KeyboardInterrupt:
                    self.interrupted = True
                except OSError as error:
                    problems.append(str(error))
                    return False, None
            problems.append("repeated interruption prevented a cleanup operation")
            return False, None

        def remaining_milliseconds():
            return max(0, int((deadline - time.monotonic()) * 1000))

        try:
            # Failed launch still owns the child endpoints; keeping those open
            # would make our own handles prevent EOF during rollback.
            for name in tuple(self.children):
                closed, _ = attempt(self.native.close, self.children[name])
                if closed:
                    del self.children[name]
            if self.job:
                # Accounting may reach zero before the process object is signaled.
                # Retained identities prevent that window becoming early success.
                counted_before, total_before = attempt(self.native.total_processes, self.job)
                captured, identities = attempt(self.native.member_handles, self.job)
                if captured:
                    members = identities
                attempt(self.native.terminate_job, self.job)
                while True:
                    queried, active = attempt(self.native.active_processes, self.job)
                    if not queried or not active:
                        break
                    if time.monotonic() >= deadline:
                        problems.append("owned job still has active processes")
                        break
                    attempt(time.sleep, 0.005)
                counted_after, total_after = attempt(self.native.total_processes, self.job)
                if counted_before and counted_after and total_before != total_after:
                    # A late member can disappear from accounting before another
                    # snapshot retains its exit identity. Do not guess success.
                    problems.append(
                        "job membership changed during identity capture; "
                        "exit verification incomplete"
                    )
                for member in members:
                    waited, exited = attempt(self.native.wait, member, remaining_milliseconds())
                    if waited and not exited:
                        problems.append("owned job member did not signal exit")
            if self.process:
                # An assignment failure leaves a suspended process outside the job.
                waited, exited = attempt(self.native.wait, self.process, 0)
                if not waited or not exited:
                    attempt(self.native.terminate_process, self.process)
                    waited, exited = attempt(
                        self.native.wait, self.process, remaining_milliseconds()
                    )
                    if waited and not exited:
                        problems.append("owned primary process did not exit")
            while self.parents:
                self.input = b""
                pumped, progressed = attempt(self._pump)
                if not pumped or (self.parents and time.monotonic() >= deadline):
                    problems.append("output incomplete: " + ", ".join(self.parents))
                    break
                if self.parents and not progressed:
                    attempt(time.sleep, 0.005)
        finally:
            handles = [
                *members,
                *self.children.values(), *self.parents.values(),
                self.thread, self.process, self.job,
            ]
            for handle in handles:
                if handle:
                    attempt(self.native.close, handle)
            self.children.clear()
            self.parents.clear()
            self.thread = self.process = self.job = None
        return problems
