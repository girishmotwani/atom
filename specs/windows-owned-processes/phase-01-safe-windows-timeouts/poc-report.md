# POC report: job-owned cleanup after the parent exits

Publication-safe evidence extract; original report approved on 2026-10-20.

## Question

Can a stdlib-only Python Windows Job Object fixture assign a suspended parent before it runs and, when a two-second deadline expires after that parent has exited, return within five seconds with its recorded child stopped, both output markers recovered and its empty working directory removable before safety rescue, while an owned outside-job control stays alive?

## Verdict

**Confirmed for the synthetic fixture on this host, three of three trials.** This was a disposable Python/native exception to the usual Go spike. No production integration or supported-platform matrix was proved.

Command (only the absolute private scratch argument is omitted):

```text
python poc\windows-job-cleanup\spike.py --scratch <new-private-scratch-directory>
```

Exit code: 0. Complete source-free stdout, copied without changing its bytes inside the fenced block:

```text
experiment=windows_job_cleanup timeout_seconds=2 return_bound_seconds=5
python_version=3.13.14 windows_version=(10, 0, 26300, 2, '')
runner_sha256_before=de327227f6815bb6b1f58501d7de0699ba5ae401cdcfd24a02f5a0a7dbf04b4d
spike_sha256=38d43712ece647ebb7ef492fa6f661b045c85d04ae3f02edc99686d9e7edae2d
archived_helper_sha256=3bc7c41a41f4e78606e0552587927133686e378fcf5eda915a3163ae76289203
attempt=1 setup_valid=true worker_watchdog=false worker_exit_code=0
worker_already_in_host_job=true
job_handle_inheritable=false
launch_order_valid=true
resume_previous_suspend_count=1
parent_member_before_resume=true
entry={"child_alive": true, "child_in_job": true, "child_pid": 9764, "control_alive": true, "control_in_candidate_job": false, "control_pid": 3196, "parent_exit_code": 0, "parent_pid": 21708, "worker_in_candidate_job": false}
cleanup_dispatch_seconds=2.012674600002356
elapsed_seconds=2.026792499993462
child_alive_at_return=false
pipes_reached_eof=true
stdout_marker_present=true
stderr_marker_present=true
control_alive_at_return=true
directory_removed_before_rescue=true
rescue_job_close=false
directory_winerror=null
native_operations=[{"operation":"IsProcessInJob:host","success":true,"error":0,"error_message":""},{"operation":"CreateJobObjectW","success":true,"error":0,"error_message":""},{"operation":"GetHandleInformation:job","success":true,"error":0,"error_message":""},{"operation":"SetInformationJobObject","success":true,"error":0,"error_message":""},{"operation":"QueryInformationJobObject","success":true,"error":0,"error_message":""},{"operation":"CreateProcess:stdlib_winapi","success":true},{"operation":"parent_identity_registered","success":true},{"operation":"AssignProcessToJobObject","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:suspended_parent","success":true,"error":0,"error_message":""},{"operation":"ResumeThread","success":true,"error":0},{"operation":"CloseHandle:primary_thread","success":true,"error":0,"error_message":""},{"operation":"OpenProcess:child","success":true,"error":0,"error_message":""},{"operation":"GetExitCodeProcess:parent","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:child","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:worker","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:control","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:candidate_job","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:identity","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:identity","success":true,"error":0,"error_message":""}]
safety_stop_results=[{"pid": 3196, "return_code": 0}]
all_registered_processes_exited=true fixture_directory_removed=true
attempt_verdict=Confirmed
attempt=2 setup_valid=true worker_watchdog=false worker_exit_code=0
worker_already_in_host_job=true
job_handle_inheritable=false
launch_order_valid=true
resume_previous_suspend_count=1
parent_member_before_resume=true
entry={"child_alive": true, "child_in_job": true, "child_pid": 43148, "control_alive": true, "control_in_candidate_job": false, "control_pid": 7116, "parent_exit_code": 0, "parent_pid": 47088, "worker_in_candidate_job": false}
cleanup_dispatch_seconds=2.021060800005216
elapsed_seconds=2.0330389000009745
child_alive_at_return=false
pipes_reached_eof=true
stdout_marker_present=true
stderr_marker_present=true
control_alive_at_return=true
directory_removed_before_rescue=true
rescue_job_close=false
directory_winerror=null
native_operations=[{"operation":"IsProcessInJob:host","success":true,"error":0,"error_message":""},{"operation":"CreateJobObjectW","success":true,"error":0,"error_message":""},{"operation":"GetHandleInformation:job","success":true,"error":0,"error_message":""},{"operation":"SetInformationJobObject","success":true,"error":0,"error_message":""},{"operation":"QueryInformationJobObject","success":true,"error":0,"error_message":""},{"operation":"CreateProcess:stdlib_winapi","success":true},{"operation":"parent_identity_registered","success":true},{"operation":"AssignProcessToJobObject","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:suspended_parent","success":true,"error":0,"error_message":""},{"operation":"ResumeThread","success":true,"error":0},{"operation":"CloseHandle:primary_thread","success":true,"error":0,"error_message":""},{"operation":"OpenProcess:child","success":true,"error":0,"error_message":""},{"operation":"GetExitCodeProcess:parent","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:child","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:worker","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:control","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:candidate_job","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:identity","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:identity","success":true,"error":0,"error_message":""}]
safety_stop_results=[{"pid": 7116, "return_code": 0}]
all_registered_processes_exited=true fixture_directory_removed=true
attempt_verdict=Confirmed
attempt=3 setup_valid=true worker_watchdog=false worker_exit_code=0
worker_already_in_host_job=true
job_handle_inheritable=false
launch_order_valid=true
resume_previous_suspend_count=1
parent_member_before_resume=true
entry={"child_alive": true, "child_in_job": true, "child_pid": 21816, "control_alive": true, "control_in_candidate_job": false, "control_pid": 23464, "parent_exit_code": 0, "parent_pid": 59716, "worker_in_candidate_job": false}
cleanup_dispatch_seconds=2.024797199992463
elapsed_seconds=2.040968300017994
child_alive_at_return=false
pipes_reached_eof=true
stdout_marker_present=true
stderr_marker_present=true
control_alive_at_return=true
directory_removed_before_rescue=true
rescue_job_close=false
directory_winerror=null
native_operations=[{"operation":"IsProcessInJob:host","success":true,"error":0,"error_message":""},{"operation":"CreateJobObjectW","success":true,"error":0,"error_message":""},{"operation":"GetHandleInformation:job","success":true,"error":0,"error_message":""},{"operation":"SetInformationJobObject","success":true,"error":0,"error_message":""},{"operation":"QueryInformationJobObject","success":true,"error":0,"error_message":""},{"operation":"CreateProcess:stdlib_winapi","success":true},{"operation":"parent_identity_registered","success":true},{"operation":"AssignProcessToJobObject","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:suspended_parent","success":true,"error":0,"error_message":""},{"operation":"ResumeThread","success":true,"error":0},{"operation":"CloseHandle:primary_thread","success":true,"error":0,"error_message":""},{"operation":"OpenProcess:child","success":true,"error":0,"error_message":""},{"operation":"GetExitCodeProcess:parent","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:child","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:worker","success":true,"error":0,"error_message":""},{"operation":"IsProcessInJob:control","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:candidate_job","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:identity","success":true,"error":0,"error_message":""},{"operation":"CloseHandle:identity","success":true,"error":0,"error_message":""}]
safety_stop_results=[{"pid": 23464, "return_code": 0}]
all_registered_processes_exited=true fixture_directory_removed=true
attempt_verdict=Confirmed
runner_source_unchanged=true
attempts_completed=3 attempts_limit=3
verdict=Confirmed
```

## Frozen provenance and boundaries

Candidate SHA-256: 38d43712ece647ebb7ef492fa6f661b045c85d04ae3f02edc99686d9e7edae2d.

Archived helper SHA-256: 3bc7c41a41f4e78606e0552587927133686e378fcf5eda915a3163ae76289203.

Pre-repair runner SHA-256: de327227f6815bb6b1f58501d7de0699ba5ae401cdcfd24a02f5a0a7dbf04b4d.

Python 3.13.14; native Windows version (10, 0, 26300, 2, ''). Supervisor elapsed including safety rescue: 9.332281699986197 seconds. Only the outside controls required later safety stops. Child exit, EOF, both exact markers, directory release and control survival were measured before rescue. Private path-bearing raw receipts remain outside this publication; the source-free stdout is not the entirety of those records.

The candidate exercised last-handle-close termination, not production TerminateJobObject/accounting/member-wait refinement. Assignment succeeded inside this host's existing job only. Error paths, normal-success child policy, interruption, large stdin, shims, other runtimes and POSIX were not established by these three trials. Neither spike is promoted into production, and neither has been rerun for publication.

## Earlier counterexample

The unchanged runner was **Refuted** on 2026-10-20: a valid early-exiting parent left a live child and locked empty cwd after the bounded return. The experiment stopped after its first witness. Command and complete source-free stdout:

```text
python poc\windows-timeout-cleanup\spike.py --scratch <new-private-scratch-directory>
```

Exit code: 3.

```text
experiment=early_exiting_parent_cleanup timeout_seconds=2 return_bound_seconds=5
runner_sha256_before=de327227f6815bb6b1f58501d7de0699ba5ae401cdcfd24a02f5a0a7dbf04b4d
attempt=1 setup_valid=true worker_watchdog=false
runner_outcome=timed_out elapsed_seconds=4.753756600024644 child_alive_at_return=true
cleanup_entry={"child_alive_before_cleanup": true, "child_pid": 16584, "child_ready": true, "parent_actual_pid_matches": true, "parent_exit_code_before_cleanup": 0, "parent_pid": 52716}
native_return_code=128
native_stdout=""
native_stderr="ERROR: The process \"52716\" not found.\n"
directory_removed_before_rescue=false directory_winerror=32
safety_stop_results=[{"pid": 16584, "return_code": 0}]
all_registered_processes_exited=true fixture_directory_removed=true
attempt_verdict=Refuted
runner_source_unchanged=true
attempts_completed=1 attempts_limit=3
verdict=Refuted
```

The earlier spike is historical: it instrumented the pre-repair runner's Popen/tree-kill path and is not a current-runner regression command. Its frozen source remains as the candidate's read-only safety helper. Separate rescue was not credited as successful runner cleanup.
