---
project: "atom-cli"
phase: "phase-03-state"
date: "2026-09-16"
design_spec: "design-spec.md"
---

# Test Spec — Phase 3: `atom state`

A retrospective test spec for Phase 3: `.atom/`, the phase state machine, the
event log, and `atom init` / `atom status`. The tests already exist; this document
maps behaviours **B71–B102** to the named tests that pin them.

Retrospective, as in Phase 2, because Atom builds the tests from the spec during
TDD rather than writing a separate test-design document first. The value of this
document is the mapping — it is what makes an unpinned behaviour visible.

**Suite:** 275 tests passing, 94% statement coverage.

```
python -m pytest tools/tests -q --cov=atom --cov-report=term-missing
```

## Coverage Figures

| Module | Coverage | Notes |
|---|---:|---|
| `check.py` | 95% | Phase 1. |
| `cli.py` | 87% | Uncovered areas are argument-parsing error paths and command dispatch branches. Up from 82% in Phase 2. |
| `eventlog.py` | 100% | |
| `filelock.py` | 84% | The uncovered lines are the POSIX `fcntl` branch, which cannot execute on Windows. Tracked as **D2**. |
| `gates.py` | 94% | Phase 1. |
| `index.py` | 88% | Phase 2. |
| `report.py` | 95% | |
| `runner.py` | 96% | Phase 2. |
| `scaffold.py` | 98% | Phase 2. |
| `spike.py` | 97% | Phase 2. |
| `state.py` | 100% | |
| `status.py` | 100% | |
| `storage.py` | 97% | |
| **Total** | **94%** | **275 tests passing** |

---

## Coverage Summary

### Layout and separation (B71–B73)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B71 | All state lives under `.atom/` in the project root. | `test_all_state_lives_under_a_single_directory` |
| B72 | `.atom/` is created by `atom init` and nothing else. | `test_a_project_without_the_directory_is_not_initialised`; `test_loading_state_from_an_uninitialised_project_says_so`; `test_status_on_an_uninitialised_project_explains_the_fix` |
| B73 | `config.json` and `state.json` are separate files on purpose. | `test_config_and_state_are_separate_files`; `test_config_records_what_the_developer_chose`; `test_status_reports_a_corrupt_config_separately_from_state` |

### Validation (B74–B77)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B74 | Loading validates **shape**, not just syntax. | `test_reading_valid_json_of_the_wrong_type_is_still_corruption`; `test_other_valid_json_scalars_are_also_rejected`; `test_an_unknown_phase_in_the_file_is_corruption`; `test_an_unknown_status_in_the_file_is_corruption` |
| B75 | Checks run in order: parses → is a `dict` → required keys present. | `test_reading_unparseable_json_reports_corruption`; `test_a_missing_required_key_is_corruption_and_names_the_key`; `test_an_empty_file_is_corruption_not_emptiness`; `test_a_file_of_nul_bytes_is_corruption` |
| B76 | A validation failure states what was expected and what was found. | `test_a_missing_required_key_is_corruption_and_names_the_key`; `test_status_exits_non_zero_when_state_is_corrupt` |
| B77 | Missing and corrupt produce **different** errors. | `test_reading_a_missing_file_says_it_is_missing`; `test_loading_corrupt_state_is_distinguishable_from_missing` |

### Writing (B78–B84)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B78 | Readers close the handle immediately; no handle is held across a write. | `test_reading_does_not_keep_the_file_open` |
| B79 | Writes go temp-file → fsync → `os.replace`. | `test_writing_then_reading_round_trips`; `test_writing_leaves_no_temp_file_behind_on_success`; `test_writing_creates_the_parent_directory` |
| B80 | `os.replace` is retried on `PermissionError`, bounded. | `test_writing_retries_while_the_destination_is_held_open` |
| B81 | Startup removes any `*.tmp` in `.atom/`. | `test_sweeping_removes_leftover_temp_files`; `test_sweeping_leaves_real_state_files_alone`; `test_sweeping_an_absent_directory_is_not_an_error`; `test_status_sweeps_leftover_temp_files_and_says_so` |
| B82 | The removal is reported, naming the file and its size. | `test_sweeping_reports_what_it_removed`; `test_status_sweeps_leftover_temp_files_and_says_so` |
| B83 | A write that exhausts its retries fails **loudly**. | `test_a_write_that_cannot_succeed_fails_loudly`; `test_init_that_cannot_write_is_fatal_and_says_how_to_recover` |
| B83a | A failed write prints **recovery instructions**. | `test_init_that_cannot_write_is_fatal_and_says_how_to_recover` |
| B83b | The temp file is renamed to `<name>.unsaved`. | `test_init_that_cannot_write_is_fatal_and_says_how_to_recover`; `test_init_does_not_promise_safety_it_cannot_deliver` (the branch where the rescue itself fails) |
| B83c | A `*.unsaved` file is never removed automatically, and is reported. | `test_sweeping_leaves_unsaved_recovery_files_alone`; `test_the_sweep_never_touches_unsaved_work`; `test_status_reports_unsaved_work` |
| B84 | The original file is never removed before the replace succeeds. | `test_writing_replaces_rather_than_truncating` |

### The event log and its lock (B85–B89)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B85 | `events.jsonl` is append-only, one JSON object per line. | `test_each_event_is_one_line`; `test_appending_never_rewrites_existing_content`; `test_appending_then_reading_round_trips`; `test_appending_creates_the_log_and_its_directory`; `test_a_timestamp_is_recorded_for_each_event`; `test_the_caller_cannot_be_clobbered_by_the_timestamp` |
| B86 | Every append takes an OS-level file lock first. | `test_lock_is_exclusive_across_real_processes`; `test_lock_can_be_taken_and_released`; `test_lock_is_released_when_the_body_raises`; `test_concurrent_appends_from_real_processes_lose_nothing` |
| B86a | Lock acquisition blocks with a bounded timeout, then fails. | `test_lock_times_out_when_already_held` |
| B86b | A timeout names the lock file, the wait, and how to clear it. | `test_timeout_message_explains_how_to_recover` |
| B87 | The lock is a separate zero-byte file, never the log itself. | `test_lock_file_is_separate_from_the_file_being_appended`; `test_appending_uses_a_separate_lock_file`; `test_lock_creates_the_lock_file_when_absent`; `test_lock_does_not_truncate_an_existing_lock_file` |
| B88 | Atom does **not** rely on `O_APPEND` atomicity or single-`write()` calls. | `test_concurrent_appends_from_real_processes_lose_nothing` — and the neutering check in [`tdd-log.md`](tdd-log.md) Cycle 1, which is the evidence that this test would fail if the prohibition were violated. See note below. |
| B89 | The spike is wired into CI on three operating systems. | Not a unit test. Pinned by `.github/workflows/` and re-run on every push. |

> **Note on B88.** B88 is a *prohibition*, and prohibitions are hard to pin with a
> test: no assertion catches an optimisation nobody has written yet. What pins it
> is the measurement in [`poc-report.md`](poc-report.md) showing the forbidden
> approach is **worse** than the naive one (binary mode lost 68 entries where
> text mode lost 55), plus the explicit prohibition in the spec. This is a known
> weak point, and it is deliberate rather than overlooked.

### Reading a damaged log (B90–B91)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B90 | A truncated final line is skipped with a warning, not an error. | `test_a_truncated_final_line_is_skipped_with_a_warning`; `test_status_counts_damaged_event_log_lines` |
| B91 | A corrupt line anywhere else is also skipped; later lines survive. | `test_a_corrupt_line_in_the_middle_does_not_hide_later_ones`; `test_a_corrupt_line_reports_its_line_number`; `test_a_json_array_line_is_treated_as_damaged`; `test_blank_lines_are_ignored_rather_than_reported`; `test_reading_a_log_that_does_not_exist_yet_is_not_an_error` |

### The phase machine (B92, B94)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B92 | State is a phase (`poc`…`ship`) plus a status. | `test_the_pipeline_runs_in_a_known_order`; `test_state_survives_a_save_and_load_round_trip`; `test_initialising_starts_at_the_first_phase`; `test_a_new_phase_starts_not_started`; `test_the_last_phase_has_nothing_after_it` |
| B94 | An invalid transition is refused, naming current, attempted, and legal. | `test_skipping_a_phase_forward_is_refused`; `test_a_refused_transition_explains_what_is_legal`; `test_moving_forward_one_phase_is_allowed`; `test_going_back_to_any_earlier_phase_is_allowed`; `test_staying_in_the_same_phase_is_allowed`; `test_transitioning_returns_a_new_state_rather_than_mutating`; `test_advancing_a_project_persists_and_logs_it`; `test_advancing_illegally_neither_saves_nor_logs` |

### The commands (B93, B95–B97)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B93 | `atom status` reports everything at once, not the first problem. | `test_status_reports_every_problem_at_once`; `test_status_reports_the_current_phase`; `test_status_shows_the_most_recent_event`; `test_status_does_not_print_the_same_problem_twice` |
| B95 | `atom status` exits non-zero when it cannot determine the state. | `test_status_exits_non_zero_when_state_is_corrupt`; `test_status_exits_non_zero_as_a_real_process_when_corrupt`; `test_status_tells_the_developer_how_to_recover_from_corruption` |
| B96 | `atom init` refuses to overwrite an initialised project without `--force`. | `test_init_refuses_to_overwrite_an_existing_project`; `test_init_force_overwrites_deliberately`; `test_init_creates_the_project`; `test_init_starts_the_project_at_the_first_phase`; `test_initialising_records_an_event` |
| B97 | `--json` emits a stable schema, on the failure path too. | `test_status_json_is_machine_readable`; `test_status_json_still_emits_on_corrupt_state`; `test_status_json_runs_as_a_real_process` |

### Concurrency (B98–B102)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B98 | Atom tolerates concurrent processes rather than excluding them. | `test_no_project_wide_lock_file_is_created`; `test_concurrent_appends_from_real_processes_lose_nothing` |
| B99 | Safety comes from the atomic replace and the log lock, not exclusion. | `test_writing_replaces_rather_than_truncating`; `test_lock_is_exclusive_across_real_processes` |
| B100 | Concurrent `state.json` writers are last-one-wins, deliberately. | Not directly pinned by a test. This is a documented *accepted consequence* of P3-2, not a mechanism. Recorded in [`decisions.md`](decisions.md). |
| B101 | Every write path assumes another process may hold the file open. | `test_writing_retries_while_the_destination_is_held_open`; `test_a_write_that_cannot_succeed_fails_loudly` |
| B102 | `atom status` is read-only and takes no lock. | `test_reading_does_not_take_the_lock`; `test_status_works_while_the_event_log_lock_is_held`; `test_no_project_wide_lock_file_is_created` |

---

## Program-level tests

Unit tests demonstrate that the code is correct. They do not demonstrate that the
*program* runs — Phase 1 shipped 55 green tests on an unbuildable package, and
Phase 2 shipped 169 green tests on a program that raised `NameError` at startup.
Every new subcommand therefore carries subprocess tests that invoke
`python -m atom.cli` for real:

| Test | What it proves that an in-process test cannot |
|---|---|
| `test_init_runs_as_a_real_process` | `atom init` starts and completes outside the test harness. |
| `test_status_runs_as_a_real_process` | `atom status` starts and produces output. |
| `test_status_json_runs_as_a_real_process` | The JSON payload is clean on stdout, uncontaminated by other output. |
| `test_status_exits_non_zero_as_a_real_process_when_corrupt` | The exit code survives the process boundary, not just the `main()` return value. |

These found nothing this phase. They are kept because they cost milliseconds and
have already caught a release-blocking bug once.

## Gaps

Three behaviours are not pinned by a direct assertion. Each is recorded here
rather than quietly omitted:

| Behaviour | Why not pinned | Mitigation |
|---|---|---|
| B88 | A prohibition on an optimisation that does not exist in the code. | Measured in `poc-report.md`; stated explicitly in the spec so a future author meets the reasoning before the temptation. |
| B89 | CI configuration, not application code. | Runs on every push across three operating systems. |
| B100 | An accepted consequence, not a mechanism. | Documented in `decisions.md` under P3-2. |
