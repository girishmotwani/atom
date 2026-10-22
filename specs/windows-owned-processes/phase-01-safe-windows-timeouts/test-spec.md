# Test spec: Windows owned command lifetimes

Publication-safe extract of the pre-implementation test map, reconciled to actual test names after local TDD acceptance on 2026-10-21. The approved [design](design-spec.md) has 17 behavior obligations. This map does not substitute for fresh verification in the shipping tree.

## Coverage Map

P0 for every row. Status: passed locally unless explicitly marked POSIX-only. Tests live in tools\tests\test_windows_process.py unless another file is named. Parameterized cases distinguish native operations, primary exit codes and interruption points.

| Design # | Actual tests | Evidence / assertion |
|---|---|---|
| 1 | test_runner_error_cannot_succeed_or_change_result_shape (test_runner.py) | Distinct non-success outcome, same seven dataclass fields; original command/result compatibility retained |
| 2 | test_windows_native_job_is_private; test_windows_launch_is_suspended_until_owned; test_windows_runner_assigns_and_checks_membership_before_resume | Native kill-on-close/non-inheritance, real suspended execution, explicit stdio list, launch/assign/check/resume order |
| 3 | test_windows_setup_failure_never_executes_command | Six pre-execution refusal boundaries, no command marker, runner_error/None with WinError 5/native context |
| 4 | test_windows_success_stops_pipe_independent_child | Primary 0 and 7: real retained child signaled and exact empty cwd removable BEFORE rescue |
| 5 | test_windows_parent_exits_before_timeout | Two-second deadline, return <5 seconds, both exact markers, child signaled and directory removable BEFORE rescue |
| 6 | TestTimeoutIsBoundedEvenWhenChildrenSurvive (test_runner.py) | Live-parent timeout, partial output and measured actual duration |
| 7,8 | test_windows_timeout_keeps_primary_reason_on_cleanup_failure; test_windows_repeated_runs_release_handles_and_workers | Native termination/accounting refusal remains bounded with explicit incomplete cleanup; repeated calls leak no handles/workers |
| 9 | test_windows_timeout_keeps_primary_reason_on_cleanup_failure; test_windows_partial_capture_names_incomplete_streams | TIMED_OUT/None retained alongside secondary failure and named incomplete stdout/stderr |
| 10 | test_windows_lifecycle_failure_preserves_primary_exit | 0 and 7 plus refused job close become runner_error/None with real primary exit and stdout preserved |
| 11 | Existing missing-tool/cwd/alias cases (test_runner.py); test_windows_broken_executable_is_diagnosed_as_unlaunchable; test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles | Specific missing/unlaunchable diagnostics; full rollback attempt and original/secondary error precedence |
| 12 | Existing stdin cases (test_runner.py); test_windows_large_stdin_and_unicode_argv; test_windows_cmd_shim_preserves_arguments; test_windows_child_can_close_stdin_early | Real >64KiB stdin, exact Unicode/space/quote argv, Unicode cwd, .cmd, empty stdin EOF and early broken input |
| 13 | test_windows_large_stdin_and_unicode_argv; test_windows_partial_capture_names_incomplete_streams | UTF-8 replacement/CRLF parity, both streams, preserved partial bytes with explicit incompleteness |
| 14 | test_windows_interrupt_finalizes_owned_processes; test_windows_interrupt_during_native_launch_reclaims_suspended_parent; test_windows_sigint_during_handle_acquisition_does_not_lose_job; partial-pipe rollback primary exceptions | Communication/finalization/repeated interrupt, owner-held process receipt, actual raised SIGINT, handler restoration and original exception propagation |
| 15 | test_windows_concurrent_runs_are_isolated; test_windows_repeated_runs_release_handles_and_workers | Independent concurrent jobs, owned outside-job control survives, no native handle/thread growth |
| 16 | Existing Popen/group-fault cases (test_runner.py), retained for POSIX | Two POSIX-only tests skipped locally; other public behavior tests run through Windows. POSIX runtime remains CI obligation |
| 17 | test_runner_error_is_failed_gate_evidence (test_gates.py); test_runner_error_is_not_usable_model_evidence (test_invoke.py); test_runner_failure_details_survive_diff_rejection (test_diff.py); test_runner_error_cannot_confirm_a_spike (test_spike.py) | No false usable review, passing gate, diff or Confirmed POC; secondary timeout diagnostic preserved |

## Arrange / Act / Assert And Failure Boundaries

- Native ownership cases create an unnamed private job and disposable suspended Python command; assert real flags, membership and recorded operation order. No fake can substitute for the actual native ordering assertion.
- Lifecycle cases start a finite child holding an exact empty directory, with output inheritance varied by the test. An observer retains the child identity before acknowledging readiness to the parent. Call run once, then assert outcome, real retained-handle signaling and directory removal before finally-rescue.
- Native refusal cases replace only an I/O boundary, not command evidence or pass/fail observations. Assert native operation/error context and forbidden success/marker absence. Cleanup-failure fixtures retain their exact handles for separate safety rescue after the measured result.
- Pipe rollback cases force ConnectNamedPipe failure and a failed first close, then assert the other endpoint was still closed and primary plus secondary errors survive. ValueError/KeyboardInterrupt variants assert the identical original exception propagates and cleanup failure is printed, not hidden or substituted.
- Input cases run real Python/.cmd fixtures with exact JSON-encoded argv/input for comparison; decoding case emits invalid UTF-8 and CRLF directly. Large unused stdin tests early tool exit without blocking or misreporting failure.
- Consumer cases use existing FakeRunner/ScriptedRunner seams and plausible good stdout with runner_error/None. Assert that stdout never becomes usable evidence, diagnostics survive and no model is contacted.
- Concurrency cases run two jobs on one SubprocessRunner plus an explicitly owned external control; assert isolated outcomes/control survival. Repeated runs compare native process-handle count and live Python threads after a warm-up, not a coverage-driven getter count.

Expected REDs from the original plan were observed for each production increment. Existing behaviors and additional compatibility cases may pass on first execution; they are not misrepresented as new RED evidence. The retained success-child assertion exposed a real signaling race and was kept unchanged. See the log's failed attempts as well as subsequent passes.

## Fixtures And Safety

Ready PID records are atomically replaced before observation, and queue access uses the public Queue API. The observer retains process identity before acknowledging readiness; child fixtures self-expire after nine seconds. Empty cwd directories contain no script/evidence. Finally-rescue uses only those retained handles, never process-name/global scans. It does not make a failed before-rescue assertion pass.

An already-terminating process can refuse TerminateProcess with Access Denied; rescue still requires its retained identity to signal in a finite wait. This fixture correction did not relax the measured exit assertion. Faulty-close tests retain exact handles and restore the monkeypatch before safety release.

## Error-path And Concurrency Audit

Setup/refusal, partial construction, invalid native image, terminated/already-exited parent, communication timeout, incomplete drain, early stdin closure, cleanup error after exit 0/7, interrupted acquisition/finalization and programmer-error precedence have concrete coverage. Remaining low-level native ABI failure branches and unseen host policies are not universally proved by mocks or three POC trials.

There are zero I/O workers/pending overlapped requests: parent-only PIPE_NOWAIT calls let the coordinator stop polling at its deadline. Main-thread SIGINT deferral during acquisition/finalization restores the previous handler and propagates interruption after owned cleanup; worker-thread runs do not install signal handlers. Python has no Go race detector; no -race result is claimed.

## Evidence boundary

Original local TDD used Windows/Python 3.13.14. Focused regression output was 259 passed, 2 skipped in 19.91s. The original full tree included unrelated work and reported 1142 passed, 2 skipped in 138.78s; its count must not be reported as the shipping-tree count. Full private logs, including failed attempts, remain in the original local ledger. Selected exact RED/GREEN output is retained in [TDD evidence](tdd-evidence.md); fresh shipping output belongs in [verification](verification.md). Two original Popen fault hooks are POSIX-only, with native Windows equivalents. Unrun CI excludes nothing.

## Review repair coverage (2026-10-22)

| Contract | Regression | Receipt |
|---|---|---|
| 17 | test_runner_failure_details_survive_diff_rejection | Native stderr remains visible; timed-out partial diff is absent |
| 8, 12, 13 | test_windows_communication_sleeps_only_while_idle; test_windows_busy_communication_still_checks_deadline; test_windows_large_streams_do_not_spend_the_deadline_sleeping | No fixed delay during progress, idle sleep retained, deadline checked, exact large stdin/stdout/stderr |
| 7, 10, 11, 14 | test_windows_interrupt_outside_communication_still_finalizes; test_windows_communication_observes_deferred_interrupt; test_windows_sigint_during_communication_is_prompt_and_reclaims_children | One finally for receipt/diagnosis, original interrupt, real prompt SIGINT and actual child exit/cwd release before rescue, handler restoration |
| 7, 8, 9, 10, 15 | test_windows_new_member_during_exit_capture_cannot_be_verified; test_windows_admission_query_failure_cannot_verify_cleanup | Real late job member produces explicit incomplete verification; timeout remains primary; failed admission queries cannot become success |
| Fixture validity, not weaker cleanup | test_windows_fixture_waits_for_readable_identity_record; test_windows_fixture_readiness_deadline_preserves_read_failure | Transient unreadable record retried within original deadline; persistent permission/missing errors remain the original errors |

The 17 original obligations remain mapped above. Added fixture readiness waiting does not alter any process-signaling, output, timeout or before-rescue directory assertion. The status-test correction from the unrelated original investigation is omitted from this neutral shipping branch; production status and its shipping baseline tests are unchanged.

Final standard command from tools: `python -m pytest tests -v --cov=atom`; 1002 passed, 2 skipped in 79.85s (0:01:19), coverage 95%. Full captured output and failed intermediate attempts are linked in [verification](verification.md) and [repair evidence](review-fix-evidence.md). Supported-platform CI remains separate and pending.
