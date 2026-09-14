---
project: "atom-cli"
phase: "phase-01-check"
date: "2026-09-14"
design_spec: "design-spec.md"
---

# Test Spec — Phase 1: `atom check`

Maps every numbered behaviour in [design-spec.md](design-spec.md) to the tests that
verify it. A behaviour with no test is an unverified claim.

**Suite:** 55 tests, 95% statement coverage, all passing.

```
python -m pytest tests -v --cov=atom --cov-report=term-missing
```

## Coverage Summary

| Module | Statements | Covered | Notes |
|---|---|---|---|
| `atom/runner.py` | 56 | 96% | Uncovered: bytes-decode branch in `_normalise_stream` |
| `atom/gates.py` | 102 | 94% | Uncovered: defensive fall-through branches |
| `atom/check.py` | 43 | 95% | Uncovered: `_relative_to` cross-drive fallback |
| `atom/report.py` | 33 | 100% | |
| `atom/cli.py` | 42 | 93% | Uncovered: `__main__` guard, help fall-through |
| **Total** | **277** | **95%** | |

## Behaviour Coverage

### Runner (B1–B5)

| # | Behaviour | Test | File |
|---|---|---|---|
| B1 | stdout/stderr captured separately with real exit code | `test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately` | `test_runner.py` |
| B2 | Timeout returns `TIMED_OUT`, `exit_code=None`, no raise | `test_subprocess_runner_returns_timed_out_without_raising` | `test_runner.py` |
| B3 | Missing executable returns `TOOL_MISSING`, no raise | `test_subprocess_runner_returns_tool_missing_without_raising` | `test_runner.py` |
| B4 | Never raises `CalledProcessError` | Covered by B2 and B3 — both assert no exception escapes | `test_runner.py` |
| B5 | `succeeded` true only for `COMPLETED` + exit 0 | `test_command_result_succeeded_only_for_completed_zero` | `test_runner.py` |
| — | `combined_output` preserves both streams | `test_command_result_combined_output_preserves_both_streams` | `test_runner.py` |

### Gates (B6–B17)

| # | Behaviour | Test | File |
|---|---|---|---|
| B6 | `BuildGate` passes on exit 0 | `test_go_command_gate_passes_when_command_exits_zero[build]` | `test_gates.py` |
| B7 | `BuildGate` fails with **stderr** in details | `test_build_gate_fails_with_stderr_details_when_build_exits_nonzero` | `test_gates.py` |
| B8 | `VetGate` behaves as B6–B7 | `test_go_command_gate_passes_when_command_exits_zero[vet]`, `test_vet_gate_fails_when_vet_exits_nonzero` | `test_gates.py` |
| B9 | `FormatGate` fails on printed filenames **despite exit 0** | `test_format_gate_fails_on_printed_filenames_despite_zero_exit_code` | `test_gates.py` |
| B9 | gofmt's own non-zero exit is a distinct failure | `test_format_gate_fails_when_gofmt_itself_errors` | `test_gates.py` |
| B10 | `FormatGate` passes on empty output | `test_format_gate_passes_when_gofmt_prints_nothing` | `test_gates.py` |
| B10 | Blank lines are not read as filenames | `test_format_gate_ignores_blank_lines_in_gofmt_output` | `test_gates.py` |
| B11 | Summary names the unformatted files | `test_format_gate_names_unformatted_files_in_summary` | `test_gates.py` |
| B12 | `TestGate` passes on exit 0 | `test_test_gate_passes_when_go_test_exits_zero` | `test_gates.py` |
| B13 | `TestGate` fails preserving raw output | `test_test_gate_fails_and_preserves_raw_output` | `test_gates.py` |
| B14 | `SKIPPED` when no package has tests | `test_test_gate_skips_when_go_reports_no_test_files` | `test_gates.py` |
| B14 | A real failure is never softened into `SKIPPED` | `test_test_gate_failure_wins_over_no_test_files_marker` | `test_gates.py` |
| B15 | `RaceGate` runs `go test -race ./...` | `test_race_gate_runs_go_test_with_race_flag` | `test_gates.py` |
| B15 | `SKIPPED` when disabled, and runs nothing | `test_race_gate_is_skipped_when_disabled` | `test_gates.py` |
| B16 | `TOOL_MISSING` yields `FAILED` naming the tool | `test_gate_fails_and_names_tool_when_executable_missing` | `test_gates.py` |
| B17 | Details are verbatim, never paraphrased | `test_test_gate_fails_and_preserves_raw_output` (asserts exact substring) | `test_gates.py` |
| — | `default_gates` order is build→vet→fmt→test→race | `test_default_gates_covers_all_five_signals_in_order` | `test_gates.py` |
| — | Disabling race keeps the gate visible | `test_default_gates_can_disable_race_without_removing_it` | `test_gates.py` |

### Check (B18–B23)

| # | Behaviour | Test | File |
|---|---|---|---|
| B18 | Every gate runs, even after a failure | `test_run_check_evaluates_every_gate_even_after_a_failure` | `test_check.py` |
| B19 | `passed` true only when required gates passed or skipped | `test_report_passes_only_when_every_required_gate_passed_or_skipped` | `test_check.py` |
| B19 | A required failure fails the check | `test_report_fails_when_a_required_gate_failed` | `test_check.py` |
| B19 | An optional failure does not | `test_optional_gate_failure_does_not_fail_the_check` | `test_check.py` |
| B20 | `WARNING` never affects `passed` | `test_warning_status_never_affects_the_verdict` | `test_check.py` |
| B21 | `exit_code` 0 when passed, else 1 | `test_exit_code_is_zero_only_when_the_check_passed[passed|failed]` | `test_check.py` |
| B22 | Finds `poc/*` with `.go` files but no `go.mod` | `test_finds_poc_directories_with_go_files_but_no_go_mod` | `test_check.py` |
| B22 | Ignores correctly scaffolded spikes | `test_ignores_poc_directories_that_have_a_go_mod` | `test_check.py` |
| B22 | Ignores non-Go spikes | `test_ignores_poc_directories_with_no_go_files` | `test_check.py` |
| B22 | No `poc/` directory is the normal case | `test_returns_empty_list_when_there_is_no_poc_directory` | `test_check.py` |
| B23 | Warnings appear without failing the check | `test_poc_warnings_appear_in_the_report_without_failing_it` | `test_check.py` |

### Report (B24–B27)

| # | Behaviour | Test | File |
|---|---|---|---|
| B24 | Shows every gate with status and duration | `test_render_text_shows_every_gate_with_status_and_duration` | `test_report.py` |
| B25 | Shows details for failed gates | `test_render_text_shows_details_for_failed_gates_only` | `test_report.py` |
| B25 | Omits details for passing gates | `test_render_text_omits_details_for_passing_gates` | `test_report.py` |
| B26 | Stable schema with `schema_version` | `test_render_json_includes_a_schema_version` | `test_report.py` |
| B26 | Every gate present with its evidence | `test_render_json_includes_every_gate_with_its_evidence` | `test_report.py` |
| B27 | Valid JSON when passing | `test_render_json_is_valid_json_for_a_passing_report` | `test_report.py` |
| B27 | Valid JSON when failing | `test_render_json_is_valid_json_for_a_failing_report` | `test_report.py` |
| — | Warnings are rendered | `test_render_text_includes_warnings` | `test_report.py` |
| — | Colour flag genuinely toggles escapes | `test_render_text_with[out]_colour_emits_escape_codes` | `test_report.py` |

### Error Handling

| Condition | Test | File |
|---|---|---|
| Directory does not exist → `NotADirectoryError` | `test_run_check_refuses_a_directory_that_does_not_exist` | `test_check.py` |
| No `go.mod` → `NotAGoModuleError` | `test_run_check_refuses_a_directory_without_go_mod` | `test_check.py` |
| Refusal happens **before** any gate runs | `test_run_check_refuses_before_running_any_gate` | `test_check.py` |

### CLI

| Behaviour | Test | File |
|---|---|---|
| Exit 0 when gates pass | `test_check_returns_zero_when_every_gate_passes` | `test_cli.py` |
| Exit 1 when a gate fails | `test_check_returns_one_when_a_gate_fails` | `test_cli.py` |
| `--json` emits parseable JSON | `test_check_json_flag_emits_parseable_json` | `test_cli.py` |
| Missing directory → exit 2, no traceback | `test_check_reports_a_missing_directory_without_a_traceback` | `test_cli.py` |
| No `go.mod` → exit 2, message names `go.mod` | `test_check_reports_a_directory_without_go_mod_clearly` | `test_cli.py` |
| Defaults to current directory | `test_check_defaults_to_the_current_directory` | `test_cli.py` |
| `--no-race` disables the race gate | `test_no_race_flag_disables_the_race_gate` | `test_cli.py` |

## Test Design Notes

**No test spawns a Go subprocess.** Every gate test injects a `FakeRunner` with scripted
`CommandResult` values. This is the payoff of the injected-runner decision: the suite runs
in **0.47 seconds** and behaves identically on a machine with no Go toolchain.

**The exceptions are deliberate.** `test_runner.py` runs real subprocesses, because
`SubprocessRunner` is the one component whose whole job is talking to the OS. Faking there
would test nothing.

**End-to-end verification is separate.** The suite proves the units. A real run against a
deliberately broken Go module verified the whole path — see `findings.md` for the observed
output.

## Completeness Checklist

- [x] Every numbered behaviour B1–B27 maps to at least one named test
- [x] Behaviours with multiple failure modes have a test per mode (B9, B10, B14, B15, B19, B22)
- [x] Error-handling table rows are covered
- [x] Test names describe behaviour, not implementation
- [x] Coverage measured and recorded, with gaps named rather than rounded away
- [x] Suite verified passing at the time of writing
