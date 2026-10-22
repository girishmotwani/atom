# Review repair execution evidence

Developer-directed remediation of the two independent reviews, 2026-10-22. Each output below is copied from its saved command capture. Local checkout, home and interpreter paths are explicitly redacted; remaining output and measurements are unchanged. Failed fixture attempts and full gates are retained rather than called successes. The final complete passing full gate is in [verification](verification.md).

## 01-diff-red

Intended RED.

Command from tools: `python -m pytest tests\test_diff.py -k runner_failure_details_survive_diff_rejection -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 35 items / 33 deselected / 2 selected

tests\test_diff.py .F                                                    [100%]

================================== FAILURES ===================================
_ test_runner_failure_details_survive_diff_rejection[CommandOutcome.TIMED_OUT] _
tests\test_diff.py:42: in test_runner_failure_details_survive_diff_rejection
    assert MULTI_FILE_DIFF not in str(caught.value)
E   AssertionError: assert 'diff --git ...ed comment\n' not in 'git took lo...tive refusal'
E     
E     'diff --git a/store... an added comment\n' is contained here:
E        changes. diff --git a/store/lookup.go b/store/lookup.go
E       index 1111111..2222222 100644
E       --- a/store/lookup.go
E       +++ b/store/lookup.go
E       @@ -10,7 +10,8 @@ func (s *Store) Lookup(key string) (string, bool) {...
E     
E     ...Full output truncated (28 lines hidden), use '-vv' to show
=========================== short test summary info ===========================
FAILED tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.TIMED_OUT]
================= 1 failed, 1 passed, 33 deselected in 1.05s ==================
```

## 02-diff-green

GREEN.

Command from tools: `python -m pytest tests\test_diff.py -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 35 items

tests\test_diff.py ...................................                   [100%]

============================= 35 passed in 4.90s ==============================
```

## 03-pipes-red

Intended RED, including a real large-transfer timeout.

Command from tools: `python -m pytest tests\test_windows_process.py -k 'communication_sleeps_only or busy_communication_still or large_streams_do_not' -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 34 items / 31 deselected / 3 selected

tests\test_windows_process.py FFF                                        [100%]

================================== FAILURES ===================================
______________ test_windows_communication_sleeps_only_while_idle ______________
tests\test_windows_process.py:217: in test_windows_communication_sleeps_only_while_idle
    assert sleeps == [0.005], "moving bytes must not incur a fixed polling delay"
E   AssertionError: moving bytes must not incur a fixed polling delay
E   assert [0.005, 0.005] == [0.005]
E     
E     Left contains one more item: 0.005
E     Use -v to get more diff
____________ test_windows_busy_communication_still_checks_deadline ____________
tests\test_windows_process.py:233: in test_windows_busy_communication_still_checks_deadline
    assert sleeps == [], "a busy stream should check its deadline without sleeping"
E   AssertionError: a busy stream should check its deadline without sleeping
E   assert [0.005] == []
E     
E     Left contains one more item: 0.005
E     Use -v to get more diff
________ test_windows_large_streams_do_not_spend_the_deadline_sleeping ________
tests\test_windows_process.py:251: in test_windows_large_streams_do_not_spend_the_deadline_sleeping
    assert result.succeeded, result.stderr[-500:]
E   AssertionError: Command timed out after 8 seconds.
E   assert False
E    +  where False = CommandResult(command=('<private-home>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3...oooooooooooooooooooooooooooooooooooo', stderr='Command timed out after 8 seconds.', duration_seconds=8.091154799913056).succeeded
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle
FAILED tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline
FAILED tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping
====================== 3 failed, 31 deselected in 10.62s ======================
```

## 04-pipes-green

GREEN.

Command from tools: `python -m pytest tests\test_windows_process.py -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 34 items

tests\test_windows_process.py ..................................         [100%]

============================= 34 passed in 13.49s =============================
```

## 05-interrupt-red

Intended RED.

Command from tools: `python -m pytest tests\test_windows_process.py -k 'outside_communication_still or observes_deferred_interrupt' -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 37 items / 34 deselected / 3 selected

tests\test_windows_process.py FFF                                        [100%]

================================== FAILURES ===================================
_ test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] _
tests\test_windows_process.py:401: in test_windows_interrupt_outside_communication_still_finalizes
    assert owners[0].finalizations == 1, "the completion-receipt gap skipped cleanup"
E   AssertionError: the completion-receipt gap skipped cleanup
E   assert 0 == 1
E    +  where 0 = <tests.test_windows_process.test_windows_interrupt_outside_communication_still_finalizes.<locals>.InterruptedOwner object at 0x000002938BE0D6A0>.finalizations
_ test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] _
tests\test_windows_process.py:409: in test_windows_interrupt_outside_communication_still_finalizes
    assert owners[0].finalizations == 1, "diagnostic handling skipped cleanup"
E   AssertionError: diagnostic handling skipped cleanup
E   assert 0 == 1
E    +  where 0 = <tests.test_windows_process.test_windows_interrupt_outside_communication_still_finalizes.<locals>.InterruptedOwner object at 0x000002938BE0D160>.finalizations
___________ test_windows_communication_observes_deferred_interrupt ____________
tests\test_windows_process.py:429: in test_windows_communication_observes_deferred_interrupt
    owner.communicate("", 1)
atom\_windows_process.py:504: in communicate
    progressed = self._pump()
                 ^^^^^^^^^^^^
tests\test_windows_process.py:424: in unexpected_io
    pytest.fail("communication ignored an already-deferred interrupt")
E   Failed: communication ignored an already-deferred interrupt
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt]
FAILED tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis]
FAILED tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt
====================== 3 failed, 34 deselected in 0.58s =======================
```

## 06-interrupt-green

GREEN.

Command from tools: `python -m pytest tests\test_windows_process.py tests\test_runner.py -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 54 items

tests\test_windows_process.py .....................................      [ 68%]
tests\test_runner.py ...............ss                                   [100%]

======================= 52 passed, 2 skipped in 19.45s ========================
```

## 07-late-member-red

Fixture error, NOT the intended RED: the observation handle lacked query access.

Command from tools: `python -m pytest tests\test_windows_process.py -k new_member_during_exit_capture -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 39 items / 37 deselected / 2 selected

tests\test_windows_process.py FF                                         [100%]

================================== FAILURES ===================================
____ test_windows_new_member_during_exit_capture_cannot_be_verified[False] ____
tests\test_windows_process.py:247: in test_windows_new_member_during_exit_capture_cannot_be_verified
    assert "job membership changed" in result.stderr
E   AssertionError: assert 'job membership changed' in 'atom: Windows cleanup incomplete: [WinError 5] IsProcessInJob: Access is denied.; primary exit code 0'
E    +  where 'atom: Windows cleanup incomplete: [WinError 5] IsProcessInJob: Access is denied.; primary exit code 0' = CommandResult(command=('<private-home>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3... incomplete: [WinError 5] IsProcessInJob: Access is denied.; primary exit code 0', duration_seconds=0.7086714999750257).stderr
____ test_windows_new_member_during_exit_capture_cannot_be_verified[True] _____
tests\test_windows_process.py:247: in test_windows_new_member_during_exit_capture_cannot_be_verified
    assert "job membership changed" in result.stderr
E   AssertionError: assert 'job membership changed' in 'Command timed out after 1 seconds.\natom: Windows cleanup incomplete: [WinError 5] IsProcessInJob: Access is denied.; primary exit code 0'
E    +  where 'Command timed out after 1 seconds.\natom: Windows cleanup incomplete: [WinError 5] IsProcessInJob: Access is denied.; primary exit code 0' = CommandResult(command=('<private-home>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3... incomplete: [WinError 5] IsProcessInJob: Access is denied.; primary exit code 0', duration_seconds=1.1983575000194833).stderr
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False]
FAILED tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True]
====================== 2 failed, 37 deselected in 2.46s =======================
```

## 08-late-member-red

Valid RED after correcting only fixture handle rights: missing retained identity still became completed/0, and timeout lacked incompleteness.

Command from tools: `python -m pytest tests\test_windows_process.py -k new_member_during_exit_capture -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 39 items / 37 deselected / 2 selected

tests\test_windows_process.py FF                                         [100%]

================================== FAILURES ===================================
____ test_windows_new_member_during_exit_capture_cannot_be_verified[False] ____
tests\test_windows_process.py:245: in test_windows_new_member_during_exit_capture_cannot_be_verified
    assert result.outcome is expected, "a missed identity must not become verified completion"
E   AssertionError: a missed identity must not become verified completion
E   assert <CommandOutcome.COMPLETED: 'completed'> is <CommandOutcome.RUNNER_ERROR: 'runner_error'>
E    +  where <CommandOutcome.COMPLETED: 'completed'> = CommandResult(command=('<private-home>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3...ndOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='primary-out\n', stderr='', duration_seconds=0.6600477000465617).outcome
____ test_windows_new_member_during_exit_capture_cannot_be_verified[True] _____
tests\test_windows_process.py:247: in test_windows_new_member_during_exit_capture_cannot_be_verified
    assert "job membership changed" in result.stderr
E   AssertionError: assert 'job membership changed' in 'Command timed out after 1 seconds.'
E    +  where 'Command timed out after 1 seconds.' = CommandResult(command=('<private-home>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3...it_code=None, stdout='primary-out\n', stderr='Command timed out after 1 seconds.', duration_seconds=1.2164536999771371).stderr
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False]
FAILED tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True]
====================== 2 failed, 37 deselected in 2.32s =======================
```

## 09-late-member-green

GREEN.

Command from tools: `python -m pytest tests\test_windows_process.py -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 39 items

tests\test_windows_process.py .......................................    [100%]

============================= 39 passed in 21.39s =============================
```

## 10-focused-green

GREEN focused group; the added PYTHONPATH override was subsequently removed for the full standard gate.

Command from tools: `python -m pytest tests\test_windows_process.py tests\test_runner.py tests\test_diff.py tests\test_gates.py tests\test_invoke.py tests\test_spike.py -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 228 items

tests\test_windows_process.py .......................................... [ 18%]
                                                                         [ 18%]
tests\test_runner.py ...............ss                                   [ 25%]
tests\test_diff.py ...................................                   [ 41%]
tests\test_gates.py ......................................               [ 57%]
tests\test_invoke.py .........................................           [ 75%]
tests\test_spike.py .................................................... [ 98%]
...                                                                      [100%]

======================= 226 passed, 2 skipped in 22.93s =======================
```

## 11-full-python-gate

FAILED full attempt: added PYTHONPATH exposed source metadata inside the packaging test venv. This is not passing evidence.

Command from tools: `python -m pytest tests -v --cov=atom`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <python>
cachedir: .pytest_cache
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1001 items

tests/test_artifact_cli.py::test_main_allowed_target_writes_exact_utf8_content PASSED [  0%]
tests/test_artifact_cli.py::test_main_empty_stdin_creates_empty_artifact PASSED [  0%]
tests/test_artifact_cli.py::test_module_execution_runs_main_entry_point PASSED [  0%]
tests/test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback PASSED [  0%]
tests/test_artifact_cli.py::test_main_normalizes_native_shell_line_endings_to_lf PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_the_byte_order_mark_windows_shells_prepend PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_only_the_first_byte_order_mark PASSED [  0%]
tests/test_artifact_cli.py::test_main_invalid_utf8_writes_nothing PASSED [  0%]
tests/test_artifact_cli.py::test_main_refused_target_does_not_read_stdin PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments0] PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments1] PASSED [  1%]
tests/test_artifact_cli.py::test_main_filesystem_failure_reports_error_without_partial_file PASSED [  1%]
tests/test_artifact_cli.py::test_main_refusal_during_write_is_reported PASSED [  1%]
tests/test_artifact_integration.py::test_package_registers_only_the_dedicated_artifact_writer PASSED [  1%]
tests/test_artifact_integration.py::test_main_atom_cli_does_not_expose_artifact_subcommand PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[discover] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[poc] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[plan] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[spec] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[tdd] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[review] PASSED [  2%]
tests/test_artifact_integration.py::test_artifact_writer_instruction_forbids_bypass_and_source_writes PASSED [  2%]
tests/test_artifact_integration.py::test_onboarding_installs_artifact_writer_instructions PASSED [  2%]
tests/test_artifact_integration.py::test_onboarding_does_not_edit_copilot_permission_configuration PASSED [  2%]
tests/test_artifact_integration.py::test_built_package_installs_working_dedicated_console_script FAILED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[specs/project/design.md-allowed-artifact-directory] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[poc/spike/README.md-allowed-artifact-directory] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/config.json-allowed-runtime-file] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/state.json-allowed-runtime-file] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/baseline.json-allowed-runtime-file] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[internal/server.go-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[tools/atom/cli.py-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.github/copilot-instructions.md-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/atom/AGENTS.md-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/events.jsonl-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/credentials.json-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs/../internal/escape.go-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[../elsewhere/escape.md-outside-repository] PASSED [  3%]
tests/test_artifacts.py::test_absolute_path_outside_the_repository_is_refused PASSED [  3%]
tests/test_artifacts.py::test_link_inside_specs_is_refused_before_containment PASSED [  4%]
tests/test_artifacts.py::test_link_pointing_back_inside_is_still_refused PASSED [  4%]
tests/test_artifacts.py::test_write_creates_nested_artifact_directories PASSED [  4%]
tests/test_artifacts.py::test_write_replaces_an_existing_artifact PASSED [  4%]
tests/test_artifacts.py::test_write_leaves_no_temporary_files_behind PASSED [  4%]
tests/test_artifacts.py::test_mixed_batch_writes_nothing PASSED          [  4%]
tests/test_artifacts.py::test_every_refusal_in_a_batch_is_reported PASSED [  4%]
tests/test_artifacts.py::test_write_through_a_link_is_refused_and_writes_nothing PASSED [  4%]
tests/test_artifacts.py::test_link_appearing_after_validation_is_caught_before_the_write PASSED [  4%]
tests/test_artifacts.py::test_cleanup_removes_a_link_planted_where_it_created_a_directory PASSED [  4%]
tests/test_artifacts.py::test_a_file_in_place_of_a_directory_is_refused PASSED [  5%]
tests/test_artifacts.py::test_a_path_on_another_drive_is_refused PASSED  [  5%]
tests/test_artifacts.py::test_a_failed_stage_leaves_nothing_behind PASSED [  5%]
tests/test_artifacts.py::test_a_failed_replace_preserves_existing_file_and_removes_temporary PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_the_purpose_prose_is_returned PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_every_paragraph_of_the_purpose_survives PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_a_missing_purpose_section_returns_none PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_the_next_heading_ends_the_purpose_section PASSED [  5%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_title_is_the_h1 PASSED [  5%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_why_quotes_the_purpose_paragraph PASSED [  5%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_what_changed_lists_the_commit_subjects PASSED [  6%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_parts_appear_in_the_specified_order PASSED [  6%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_links_to_each_artifact_rather_than_embedding_it PASSED [  6%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_every_link_embeds_the_pushed_commit_sha PASSED [  6%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_uses_a_branch_name_as_the_ref PASSED [  6%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_points_at_the_base_branch PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_written_file_contains_no_carriage_return PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_returned_count_is_the_character_count PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_character_count_is_below_the_text_mode_byte_count PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_reported_count_matches_the_bytes_on_disk PASSED [  6%]
tests/test_body.py::TestEvidenceStatesAbsence::test_a_gate_table_carries_one_row_per_gate PASSED [  7%]
tests/test_body.py::TestEvidenceStatesAbsence::test_the_recorded_line_replaces_the_table_it_does_not_empty_the_section PASSED [  7%]
tests/test_body.py::TestEvidenceStatesAbsence::test_an_overridden_failure_is_stated_never_asserted_green PASSED [  7%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_no_artifacts_produces_no_invented_link PASSED [  7%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_the_body_never_editorialises_a_missing_artifact PASSED [  7%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_only_the_artifacts_present_are_linked PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_a_plain_rule_is_a_target PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_several_targets_on_one_rule_are_all_read PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_prerequisites_are_not_targets PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_a_double_colon_rule_is_a_target PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS := -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ::= -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ?= -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS += -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS = -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_a_recipe_line_is_never_a_target PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_pattern_and_variable_targets_are_ignored PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_special_targets_are_ignored PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_a_comment_does_not_create_a_target PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_unreadable_makefile_yields_no_targets PASSED [  8%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_a_makefile_the_go_defaults_stand PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_a_makefile_with_both_targets_takes_over PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[GNUmakefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[Makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_each_gate_is_decided_on_its_own_target PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[GNUmakefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[Makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_gnumakefile_wins_over_makefile_as_make_would PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_make_installed_the_makefile_is_not_used PASSED [ 10%]
tests/test_check.py::test_run_check_evaluates_every_gate_even_after_a_failure PASSED [ 10%]
tests/test_check.py::test_report_passes_only_when_every_required_gate_passed_or_skipped PASSED [ 10%]
tests/test_check.py::test_report_fails_when_a_required_gate_failed PASSED [ 10%]
tests/test_check.py::test_optional_gate_failure_does_not_fail_the_check PASSED [ 10%]
tests/test_check.py::test_warning_status_never_affects_the_verdict PASSED [ 10%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[passed] PASSED [ 10%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[failed] PASSED [ 10%]
tests/test_check.py::test_run_check_refuses_a_directory_that_does_not_exist PASSED [ 10%]
tests/test_check.py::test_run_check_refuses_a_directory_without_go_mod PASSED [ 10%]
tests/test_check.py::test_run_check_refuses_before_running_any_gate PASSED [ 11%]
tests/test_check.py::test_finds_poc_directories_with_go_files_but_no_go_mod PASSED [ 11%]
tests/test_check.py::test_ignores_poc_directories_that_have_a_go_mod PASSED [ 11%]
tests/test_check.py::test_ignores_poc_directories_with_no_go_files PASSED [ 11%]
tests/test_check.py::test_returns_empty_list_when_there_is_no_poc_directory PASSED [ 11%]
tests/test_check.py::test_poc_warnings_appear_in_the_report_without_failing_it PASSED [ 11%]
tests/test_cli.py::test_check_returns_zero_when_every_gate_passes PASSED [ 11%]
tests/test_cli.py::test_check_returns_one_when_a_gate_fails PASSED       [ 11%]
tests/test_cli.py::test_check_json_flag_emits_parseable_json PASSED      [ 11%]
tests/test_cli.py::test_check_reports_a_missing_directory_without_a_traceback PASSED [ 11%]
tests/test_cli.py::test_check_reports_a_directory_without_go_mod_clearly PASSED [ 12%]
tests/test_cli.py::test_check_defaults_to_the_current_directory PASSED   [ 12%]
tests/test_cli.py::test_no_race_flag_disables_the_race_gate PASSED       [ 12%]
tests/test_cli.py::test_the_cli_runs_as_a_module_without_exploding PASSED [ 12%]
tests/test_cli.py::test_every_subcommand_is_reachable_in_a_real_process PASSED [ 12%]
tests/test_cli_poc.py::test_poc_list_on_an_empty_repo_succeeds PASSED    [ 12%]
tests/test_cli_poc.py::test_poc_list_shows_each_spike PASSED             [ 12%]
tests/test_cli_poc.py::test_poc_list_flags_a_spike_missing_go_mod PASSED [ 12%]
tests/test_cli_poc.py::test_poc_list_json_is_machine_readable PASSED     [ 12%]
tests/test_cli_poc.py::test_poc_new_rejects_a_bad_slug_as_a_usage_error PASSED [ 12%]
tests/test_cli_poc.py::test_poc_new_bad_slug_writes_one_line_to_stderr PASSED [ 13%]
tests/test_cli_poc.py::test_poc_new_refuses_an_existing_spike_as_a_usage_error PASSED [ 13%]
tests/test_cli_poc.py::test_poc_run_on_a_missing_spike_is_a_usage_error PASSED [ 13%]
tests/test_cli_poc.py::test_poc_run_on_a_spike_without_go_mod_is_a_usage_error PASSED [ 13%]
tests/test_cli_poc.py::test_a_crashed_spike_makes_the_command_exit_non_zero PASSED [ 13%]
tests/test_cli_poc.py::test_every_real_verdict_makes_the_command_exit_zero PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_no_source_is_a_usage_error PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_two_sources_is_a_usage_error PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_working_is_accepted PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_staged_is_accepted PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_branch_is_accepted PASSED [ 14%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--runs-0] PASSED [ 14%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--concurrency-0] PASSED [ 14%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_negative_window_is_refused PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_complete_review_exits_zero_even_with_findings PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_partial_review_exits_non_zero PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_no_usable_response_fails_loudly PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_every_model_unavailable_fails_rather_than_reporting_nothing PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_git_failure_is_not_reported_as_a_clean_review PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_blocked_toolchain_returns_check_failed_without_reviewing PASSED [ 14%]
tests/test_cli_review.py::TestChannels::test_the_report_goes_to_stdout PASSED [ 15%]
tests/test_cli_review.py::TestChannels::test_failure_detail_goes_to_stderr_only PASSED [ 15%]
tests/test_cli_review.py::TestChannels::test_json_output_is_parseable PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_each_model_is_asked_the_requested_number_of_times PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_custom_instructions_are_disabled PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_no_named_mcp_server_is_disabled_by_default PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_the_prompt_carries_the_whole_diff_in_one_call PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_the_module_can_be_executed PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_appears_in_the_top_level_help PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_help_runs_without_error PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_without_a_source_exits_two_and_explains PASSED [ 16%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_with_two_sources_exits_two_and_explains PASSED [ 16%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_a_refused_setting_does_not_produce_a_traceback PASSED [ 16%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_nothing_is_defined_below_the_main_guard PASSED [ 16%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_default_models_are_the_two_that_scored_above_ninety_percent PASSED [ 16%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_help_text_names_the_models_it_actually_uses PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_ship_builds_its_gates_without_raising PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_still_builds_gates PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_five_gates_are_passed_through PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_disables_only_the_race_gate PASSED [ 16%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_defaults_to_main PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_is_forwarded PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_phase_and_title_are_forwarded PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_push_defaults_off_and_is_forwarded_when_given PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_allow_failing_checks_is_forwarded PASSED [ 17%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_a_refusal_exits_one_and_prints_to_stderr PASSED [ 17%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_failing_check_exits_non_zero PASSED [ 17%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_run_says_so_on_stderr PASSED [ 17%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_a_created_pr_says_opened PASSED [ 17%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_an_updated_pr_says_updated PASSED [ 17%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_the_commit_is_abbreviated_not_printed_whole PASSED [ 18%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_appears_in_the_top_level_help PASSED [ 18%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_help_runs_without_error PASSED [ 18%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_outside_a_phase_branch_refuses_without_a_traceback PASSED [ 18%]
tests/test_cli_state.py::test_init_creates_the_project PASSED            [ 18%]
tests/test_cli_state.py::test_init_starts_the_project_with_no_approvals PASSED [ 18%]
tests/test_cli_state.py::test_init_does_not_claim_a_phase PASSED         [ 18%]
tests/test_cli_state.py::test_init_refuses_to_overwrite_an_existing_project PASSED [ 18%]
tests/test_cli_state.py::test_init_force_overwrites_deliberately PASSED  [ 18%]
tests/test_cli_state.py::test_status_reports_the_current_phase PASSED    [ 18%]
tests/test_cli_state.py::test_status_answers_without_any_state_file_at_all PASSED [ 19%]
tests/test_cli_state.py::test_status_exits_zero_when_state_is_corrupt PASSED [ 19%]
tests/test_cli_state.py::test_status_exits_zero_whatever_it_finds PASSED [ 19%]
tests/test_cli_state.py::test_status_json_is_machine_readable PASSED     [ 19%]
tests/test_cli_state.py::test_status_json_still_emits_on_corrupt_state PASSED [ 19%]
tests/test_cli_state.py::test_status_reports_every_problem_at_once PASSED [ 19%]
tests/test_cli_state.py::test_status_reports_unsaved_work PASSED         [ 19%]
tests/test_cli_state.py::test_status_shows_the_most_recent_event PASSED  [ 19%]
tests/test_cli_state.py::test_status_sweeps_leftover_temp_files_and_says_so PASSED [ 19%]
tests/test_cli_state.py::test_the_sweep_never_touches_unsaved_work PASSED [ 19%]
tests/test_cli_state.py::test_status_works_while_the_event_log_lock_is_held PASSED [ 20%]
tests/test_cli_state.py::test_no_project_wide_lock_file_is_created PASSED [ 20%]
tests/test_cli_state.py::test_init_runs_as_a_real_process PASSED         [ 20%]
tests/test_cli_state.py::test_the_atom_package_imports_cleanly PASSED    [ 20%]
tests/test_cli_state.py::test_status_runs_as_a_subprocess_and_exits_zero PASSED [ 20%]
tests/test_cli_state.py::test_status_json_output_is_parseable_from_a_subprocess PASSED [ 20%]
tests/test_cli_state.py::test_status_runs_in_a_directory_that_is_not_a_project PASSED [ 20%]
tests/test_cli_state.py::test_status_runs_with_no_state_file_present PASSED [ 20%]
tests/test_cli_state.py::test_status_exits_zero_as_a_real_process_when_corrupt PASSED [ 20%]
tests/test_cli_state.py::test_init_that_cannot_write_is_fatal_and_says_how_to_recover PASSED [ 20%]
tests/test_cli_state.py::test_init_does_not_promise_safety_it_cannot_deliver PASSED [ 21%]
tests/test_cli_state.py::test_status_reports_a_corrupt_config_separately_from_state PASSED [ 21%]
tests/test_cli_state.py::test_status_counts_damaged_event_log_lines PASSED [ 21%]
tests/test_cli_state.py::test_status_tells_the_developer_how_to_recover_from_corruption PASSED [ 21%]
tests/test_cli_state.py::test_status_prints_each_problem_exactly_once PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[source] PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[packaged] PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[source] PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[packaged] PASSED [ 21%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[source] PASSED [ 21%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[packaged] PASSED [ 22%]
tests/test_comment_guidance.py::test_the_two_tdd_skill_copies_stay_identical PASSED [ 22%]
tests/test_comment_guidance.py::test_the_review_rule_names_a_missing_comment_as_the_defect PASSED [ 22%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.RUNNER_ERROR] PASSED [ 22%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.TIMED_OUT] PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_staged_source_asks_git_for_the_index PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_working_source_asks_git_for_unstaged_changes PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_branch_source_diffs_against_the_merge_base PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_selecting_no_source_names_all_three_options PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_selecting_two_sources_is_an_error_rather_than_a_precedence_rule PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_the_chosen_source_is_recorded_on_the_request PASSED [ 23%]
tests/test_diff.py::TestCapture::test_capture_issues_exactly_one_git_command PASSED [ 23%]
tests/test_diff.py::TestCapture::test_a_multi_file_diff_is_captured_whole PASSED [ 23%]
tests/test_diff.py::TestCapture::test_an_empty_diff_is_not_an_error PASSED [ 23%]
tests/test_diff.py::TestCapture::test_a_whitespace_only_diff_counts_as_empty PASSED [ 23%]
tests/test_diff.py::TestCapture::test_nothing_is_truncated_however_large_the_diff PASSED [ 23%]
tests/test_diff.py::TestGitFailure::test_a_failed_git_command_is_reported_not_swallowed PASSED [ 23%]
tests/test_diff.py::TestGitFailure::test_a_missing_git_is_reported_clearly PASSED [ 23%]
tests/test_diff.py::TestGitFailure::test_a_timed_out_git_command_is_reported PASSED [ 23%]
tests/test_diff.py::TestSize::test_changed_lines_count_additions_and_removals PASSED [ 23%]
tests/test_diff.py::TestSize::test_file_headers_are_not_counted_as_changed_lines PASSED [ 24%]
tests/test_diff.py::TestSize::test_context_lines_are_not_counted PASSED  [ 24%]
tests/test_diff.py::TestSize::test_file_count_follows_the_b_side_of_a_rename PASSED [ 24%]
tests/test_diff.py::TestSize::test_a_file_is_counted_once_however_many_hunks_it_has PASSED [ 24%]
tests/test_diff.py::TestSize::test_size_reads_as_a_sentence_for_the_report PASSED [ 24%]
tests/test_diff.py::TestSize::test_size_description_is_singular_for_one_file PASSED [ 24%]
tests/test_diff.py::TestSize::test_an_empty_diff_describes_itself_as_empty PASSED [ 24%]
tests/test_diff.py::TestDescription::test_staged_describes_itself PASSED [ 24%]
tests/test_diff.py::TestDescription::test_working_describes_itself PASSED [ 24%]
tests/test_diff.py::TestDescription::test_branch_names_the_base_ref PASSED [ 24%]
tests/test_diff.py::TestDescription::test_a_path_without_an_a_or_b_prefix_is_used_as_is PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_removing_a_markdown_rule_still_counts_as_a_changed_line PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_added_content_cannot_invent_a_file PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_git_header_does_not_start_a_new_file PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_hunk_header_is_counted_as_a_change PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_several_files_each_reset_the_header_state PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_a_deleted_file_is_named_by_its_old_path PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_a_no_newline_marker_is_not_a_changed_line PASSED [ 25%]
tests/test_eventlog.py::test_appending_then_reading_round_trips PASSED   [ 25%]
tests/test_eventlog.py::test_appending_creates_the_log_and_its_directory PASSED [ 25%]
tests/test_eventlog.py::test_each_event_is_one_line PASSED               [ 26%]
tests/test_eventlog.py::test_appending_never_rewrites_existing_content PASSED [ 26%]
tests/test_eventlog.py::test_a_timestamp_is_recorded_for_each_event PASSED [ 26%]
tests/test_eventlog.py::test_the_caller_cannot_be_clobbered_by_the_timestamp PASSED [ 26%]
tests/test_eventlog.py::test_appending_uses_a_separate_lock_file PASSED  [ 26%]
tests/test_eventlog.py::test_a_truncated_final_line_is_skipped_with_a_warning PASSED [ 26%]
tests/test_eventlog.py::test_a_corrupt_line_in_the_middle_does_not_hide_later_ones PASSED [ 26%]
tests/test_eventlog.py::test_a_corrupt_line_reports_its_line_number PASSED [ 26%]
tests/test_eventlog.py::test_a_json_array_line_is_treated_as_damaged PASSED [ 26%]
tests/test_eventlog.py::test_blank_lines_are_ignored_rather_than_reported PASSED [ 26%]
tests/test_eventlog.py::test_reading_a_log_that_does_not_exist_yet_is_not_an_error PASSED [ 27%]
tests/test_eventlog.py::test_reading_does_not_take_the_lock PASSED       [ 27%]
tests/test_eventlog.py::test_concurrent_appends_from_real_processes_lose_nothing PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_plain_json_needs_no_stripping PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_is_stripped PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_is_stripped PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_surrounding_whitespace_is_ignored PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_wins_over_an_earlier_unlabelled_one PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_still_works_when_it_is_the_only_one PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_fenced_response_extracts_normally PASSED [ 28%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_around_bare_json_is_a_failure_not_a_rescue PASSED [ 28%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_outside_a_fence_is_still_extracted PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_a_well_formed_response_yields_findings PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_an_empty_array_is_a_clean_review_not_a_failure PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_a_non_array_payload_is_rejected PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_unparseable_text_is_rejected PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[file] PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[line] PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[severity] PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[message] PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_severity_outside_the_allowed_set_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_all_four_allowed_severities_are_accepted PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_string_line_number_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_boolean_line_number_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_line_number_below_one_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_line_zero_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_line_one_is_accepted PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_an_element_that_is_not_an_object_is_rejected PASSED [ 29%]
tests/test_extract.py::TestFileGuard::test_a_finding_naming_a_file_outside_the_diff_is_rejected PASSED [ 29%]
tests/test_extract.py::TestFileGuard::test_rejecting_one_finding_does_not_discard_its_siblings PASSED [ 30%]
tests/test_extract.py::TestFileGuard::test_the_guard_is_skipped_when_no_file_list_is_given PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_records_which_model_and_which_run PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_keeps_an_excerpt_of_what_was_returned PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_the_excerpt_is_bounded_so_a_huge_reply_cannot_flood_the_report PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_an_unusable_run_is_not_silently_ignored PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_findings_carry_their_model_and_run PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_one_bad_run_does_not_lose_the_good_ones PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_a_report_knows_whether_anything_failed PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_duplicate_findings_are_preserved_for_the_merge_step_to_count PASSED [ 30%]
tests/test_filelock.py::test_lock_is_exclusive_across_real_processes PASSED [ 31%]
tests/test_filelock.py::test_lock_can_be_taken_and_released PASSED       [ 31%]
tests/test_filelock.py::test_lock_creates_the_lock_file_when_absent PASSED [ 31%]
tests/test_filelock.py::test_lock_file_is_separate_from_the_file_being_appended PASSED [ 31%]
tests/test_filelock.py::test_lock_is_released_when_the_body_raises PASSED [ 31%]
tests/test_filelock.py::test_lock_times_out_when_already_held PASSED     [ 31%]
tests/test_filelock.py::test_timeout_message_explains_how_to_recover PASSED [ 31%]
tests/test_filelock.py::test_lock_does_not_truncate_an_existing_lock_file PASSED [ 31%]
tests/test_gates.py::test_runner_error_is_failed_gate_evidence PASSED    [ 31%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[build] PASSED [ 31%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[vet] PASSED [ 32%]
tests/test_gates.py::test_build_gate_fails_with_stderr_details_when_build_exits_nonzero PASSED [ 32%]
tests/test_gates.py::test_vet_gate_fails_when_vet_exits_nonzero PASSED   [ 32%]
tests/test_gates.py::test_format_gate_fails_on_printed_filenames_despite_zero_exit_code PASSED [ 32%]
tests/test_gates.py::test_format_gate_passes_when_gofmt_prints_nothing PASSED [ 32%]
tests/test_gates.py::test_format_gate_names_unformatted_files_in_summary PASSED [ 32%]
tests/test_gates.py::test_format_gate_ignores_blank_lines_in_gofmt_output PASSED [ 32%]
tests/test_gates.py::test_format_gate_fails_when_gofmt_itself_errors PASSED [ 32%]
tests/test_gates.py::test_test_gate_passes_when_go_test_exits_zero PASSED [ 32%]
tests/test_gates.py::test_test_gate_fails_and_preserves_raw_output PASSED [ 32%]
tests/test_gates.py::test_test_gate_skips_when_go_reports_no_test_files PASSED [ 33%]
tests/test_gates.py::test_test_gate_failure_wins_over_no_test_files_marker PASSED [ 33%]
tests/test_gates.py::test_race_gate_runs_go_test_with_race_flag PASSED   [ 33%]
tests/test_gates.py::test_race_gate_is_skipped_when_disabled PASSED      [ 33%]
tests/test_gates.py::test_gate_fails_and_names_tool_when_executable_missing PASSED [ 33%]
tests/test_gates.py::test_test_gate_skips_when_download_chatter_accompanies_no_test_files PASSED [ 33%]
tests/test_gates.py::test_race_gate_skips_when_no_packages_have_tests PASSED [ 33%]
tests/test_gates.py::test_race_gate_still_passes_when_tests_actually_ran PASSED [ 33%]
tests/test_gates.py::test_format_gate_ignores_files_belonging_to_a_nested_module PASSED [ 33%]
tests/test_gates.py::test_format_gate_still_reports_unformatted_files_in_the_root_module PASSED [ 33%]
tests/test_gates.py::test_format_gate_does_not_fail_for_line_ending_only_differences PASSED [ 34%]
tests/test_gates.py::test_format_gate_names_line_endings_as_the_cause PASSED [ 34%]
tests/test_gates.py::test_format_gate_still_fails_when_a_crlf_file_is_also_badly_formatted PASSED [ 34%]
tests/test_gates.py::test_format_gate_reports_a_genuine_problem_even_beside_a_line_ending_one PASSED [ 34%]
tests/test_gates.py::test_default_gates_covers_all_five_signals_in_order PASSED [ 34%]
tests/test_gates.py::test_default_gates_can_disable_race_without_removing_it PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[staticcheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[errcheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[govulncheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[staticcheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[errcheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[govulncheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[staticcheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[errcheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[govulncheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gates_returns_all_optional_review_signals PASSED [ 35%]
tests/test_gates_makefile.py::TestBuildGate::test_a_build_target_is_preferred_over_go_build PASSED [ 35%]
tests/test_gates_makefile.py::TestBuildGate::test_without_a_build_target_go_build_still_runs PASSED [ 35%]
tests/test_gates_makefile.py::TestBuildGate::test_a_failing_make_target_fails_the_gate PASSED [ 35%]
tests/test_gates_makefile.py::TestTestGate::test_a_test_target_is_preferred_over_go_test PASSED [ 35%]
tests/test_gates_makefile.py::TestTestGate::test_a_failing_make_target_fails_the_gate PASSED [ 36%]
tests/test_gates_makefile.py::TestTestGate::test_no_test_files_is_still_reported_as_skipped_through_make PASSED [ 36%]
tests/test_gates_makefile.py::TestTestGate::test_a_real_test_run_through_make_is_not_downgraded PASSED [ 36%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_format_gate_ignores_a_makefile PASSED [ 36%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_vet_gate_ignores_a_makefile PASSED [ 36%]
tests/test_gates_makefile.py::test_a_makefile_is_ignored_when_make_is_not_installed PASSED [ 36%]
tests/test_index.py::test_lists_every_spike PASSED                       [ 36%]
tests/test_index.py::test_ignores_nested_directories PASSED              [ 36%]
tests/test_index.py::test_reads_the_question_from_the_readme PASSED      [ 36%]
tests/test_index.py::test_question_is_none_when_there_is_no_readme PASSED [ 36%]
tests/test_index.py::test_question_is_none_when_the_readme_has_no_question_section PASSED [ 37%]
tests/test_index.py::test_reports_a_spike_that_has_a_go_mod PASSED       [ 37%]
tests/test_index.py::test_flags_a_spike_missing_its_go_mod PASSED        [ 37%]
tests/test_index.py::test_missing_poc_root_is_an_empty_list_not_an_error PASSED [ 37%]
tests/test_index.py::test_empty_poc_root_is_an_empty_list PASSED         [ 37%]
tests/test_index.py::test_ignores_loose_files_in_poc_root PASSED         [ 37%]
tests/test_index.py::test_results_are_sorted_for_stable_output PASSED    [ 37%]
tests/test_index.py::test_multiline_question_is_collapsed_to_one_line PASSED [ 37%]
tests/test_index.py::test_question_skips_the_blockquote_guidance PASSED  [ 37%]
tests/test_invoke.py::test_runner_error_is_not_usable_model_evidence PASSED [ 37%]
tests/test_invoke.py::TestMandatoryFlags::test_uses_silent_and_never_output_format_json PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_custom_instructions PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_builtin_mcp_servers PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_names_no_vendor_specific_mcp_servers_by_default PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_extra_mcp_servers_can_be_disabled_by_the_caller PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_carries_the_prompt_and_the_model PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_probes_every_model PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_a_rejected_model_is_reported_unavailable_with_its_reason PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_no_review_call_happens_before_every_probe_has_run PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_an_unavailable_model_is_never_asked_to_review PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_probing_no_models_returns_nothing_rather_than_failing PASSED [ 39%]
tests/test_invoke.py::TestAvailabilityProbing::test_when_no_model_is_available_the_review_fails_loudly PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_calls_each_model_three_times_by_default PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_run_count_is_overridable PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_runs_of_one_model_are_byte_identical_calls PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_every_model_gets_the_same_number_of_runs PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_runs_are_numbered_from_one PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_timeout_is_a_recorded_outcome_not_a_raise PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_nonzero_exit_is_recorded_as_a_failed_run PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_one_failing_run_does_not_stop_the_others PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_response_text_is_kept_for_completed_runs PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_a_complete_review_is_not_partial PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_one_failed_run_out_of_six_makes_the_whole_review_partial PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_participation_states_completed_over_requested_per_model PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_usable_responses_are_offered_even_when_the_review_is_partial PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_default_concurrency_is_the_measured_four PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_never_exceeds_the_concurrency_limit PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_calls_genuinely_overlap_rather_than_merely_staying_under_the_limit PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_all_runs_complete_even_when_they_outnumber_the_workers PASSED [ 40%]
tests/test_invoke.py::TestReportingWhatFailed::test_unavailable_models_are_listed_with_their_reasons PASSED [ 40%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_missing_cli_is_reported_as_tool_missing_not_as_a_refusal PASSED [ 41%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_failure_still_gets_a_reason PASSED [ 41%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_timeout_is_named_by_its_outcome PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_runs_is_rejected_rather_than_reported_as_complete PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_negative_runs_is_rejected PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_concurrency_is_rejected_rather_than_silently_corrected PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_no_models_at_all_is_rejected PASSED [ 41%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_review_command_does_not_contain_the_prompt PASSED [ 41%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_command_length_stays_flat_as_the_prompt_grows PASSED [ 41%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_the_prompt_reaches_the_runner_as_stdin PASSED [ 41%]
tests/test_merge.py::TestGroupingByProximity::test_the_default_window_is_three_lines PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_identical_lines_merge PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_nearby_lines_merge PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_lines_beyond_the_window_stay_separate PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_the_window_is_configurable PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_the_same_line_in_different_files_never_merges PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_a_group_never_spans_more_than_the_window PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_grouping_does_not_depend_on_the_order_findings_arrive_in PASSED [ 42%]
tests/test_merge.py::TestNothingIsDiscarded::test_every_message_survives_the_merge PASSED [ 42%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_is_attributed_to_its_model_and_run PASSED [ 42%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_keeps_the_line_it_was_reported_at PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_a_merged_finding_names_the_models_that_reported_it PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_agreement_counts_how_many_runs_of_each_model_reported_it PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_one_run_reporting_a_line_twice_counts_once PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_a_single_model_finding_is_reported_not_suppressed PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_a_finding_from_both_models_is_marked_corroborated PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_different_lines_of_one_group_is_not_corroboration PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_the_same_line_is_still_corroboration PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_agreement_on_one_line_survives_an_unrelated_line_joining_the_group PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_one_model_reporting_twice_on_a_line_is_not_corroboration PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_model_count_still_reports_every_model_in_the_group PASSED [ 44%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_a_single_line_group_from_two_models_is_unaffected PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_the_same_defect_at_adjacent_lines_is_reported_as_nearby PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_same_line_agreement_is_not_also_reported_as_nearby PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_agreement_on_one_line_wins_over_a_nearby_report PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_one_model_across_several_lines_is_neither_signal PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_a_lone_finding_is_neither_signal PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_disagreeing_severities_are_all_preserved PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_severity_is_not_collapsed_into_one_verdict PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_agreement_on_severity_is_not_reported_as_disagreement PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_the_highest_claimed_severity_is_available_for_ordering PASSED [ 45%]
tests/test_merge.py::TestOrdering::test_findings_are_ordered_by_highest_severity PASSED [ 45%]
tests/test_merge.py::TestOrdering::test_one_model_calling_it_critical_lifts_the_whole_finding PASSED [ 45%]
tests/test_merge.py::TestOrdering::test_equal_severities_are_ordered_predictably PASSED [ 45%]
tests/test_merge.py::TestKnownLimits::test_drift_lets_a_group_reach_further_than_the_window PASSED [ 45%]
tests/test_merge.py::TestEdges::test_severity_ordering_depends_on_the_allowed_list_staying_ordered PASSED [ 45%]
tests/test_merge.py::TestEdges::test_agreement_renders_as_the_fraction_a_report_shows PASSED [ 45%]
tests/test_merge.py::TestEdges::test_no_findings_merge_to_nothing PASSED [ 45%]
tests/test_merge.py::TestEdges::test_a_model_absent_from_the_run_counts_is_rejected PASSED [ 45%]
tests/test_merge.py::TestEdges::test_a_negative_window_is_rejected PASSED [ 45%]
tests/test_merge.py::TestEdges::test_a_zero_window_means_exact_line_matching PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_with_no_runs_cannot_have_reported_anything PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_that_completed_no_runs_is_allowed_to_report_nothing PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_negative_run_count_is_rejected PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_more_reporting_runs_than_runs_total_is_rejected PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_an_unrecognised_severity_names_what_is_allowed PASSED [ 46%]
tests/test_onboarding.py::test_init_records_the_makefile_commands_it_will_actually_run PASSED [ 46%]
tests/test_onboarding.py::test_init_records_a_partial_makefile_one_gate_at_a_time PASSED [ 46%]
tests/test_onboarding.py::test_init_infers_module_and_installs_local_instructions PASSED [ 46%]
tests/test_onboarding.py::test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command PASSED [ 46%]
tests/test_onboarding.py::test_init_updates_existing_instructions_once PASSED [ 47%]
tests/test_onboarding.py::test_init_removes_legacy_external_atom_references PASSED [ 47%]
tests/test_onboarding.py::test_init_requires_module_when_go_mod_is_absent PASSED [ 47%]
tests/test_onboarding.py::test_init_ignores_only_generated_atom_runtime_files PASSED [ 47%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_and_updates_it_once PASSED [ 47%]
tests/test_onboarding.py::test_init_replaces_stale_atom_gitignore_block PASSED [ 47%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_newlines PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n# >>> Atom generated runtime files >>>\n.atom/second.json\n# <<< Atom generated runtime files <<<\n] PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n] PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n.atom/first.json\n] PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n# >>> Atom generated runtime files >>>\n] PASSED [ 48%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/-\n\n] PASSED [ 48%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/\n\n-] PASSED [ 48%]
tests/test_onboarding.py::test_gitignore_update_keeps_original_when_atomic_replace_fails PASSED [ 48%]
tests/test_onboarding.py::test_init_reports_an_unreadable_gitignore_without_a_traceback PASSED [ 48%]
tests/test_phases.py::test_a_well_formed_phase_directory_is_recognised PASSED [ 48%]
tests/test_phases.py::test_a_single_digit_phase_number_is_not_a_phase_directory PASSED [ 48%]
tests/test_phases.py::test_an_uppercase_slug_is_not_a_phase_directory PASSED [ 48%]
tests/test_phases.py::test_a_directory_merely_containing_a_phase_name_is_not_one PASSED [ 48%]
tests/test_phases.py::test_a_file_named_like_a_phase_directory_is_not_one PASSED [ 48%]
tests/test_phases.py::test_a_non_phase_directory_is_ignored PASSED       [ 49%]
tests/test_phases.py::test_a_non_phase_directory_produces_no_problem PASSED [ 49%]
tests/test_phases.py::test_the_phase_plan_document_beside_the_phases_is_not_a_phase PASSED [ 49%]
tests/test_phases.py::test_phases_are_ordered_lexically PASSED           [ 49%]
tests/test_phases.py::test_the_two_digit_prefix_makes_lexical_order_numeric PASSED [ 49%]
tests/test_phases.py::test_phase_ten_sorts_after_phase_nine PASSED       [ 49%]
tests/test_phases.py::test_a_phase_branch_names_the_current_phase PASSED [ 49%]
tests/test_phases.py::test_the_branch_wins_over_the_lexically_greatest_phase PASSED [ 49%]
tests/test_phases.py::test_main_falls_back_to_the_lexically_greatest_phase PASSED [ 49%]
tests/test_phases.py::test_a_detached_head_falls_back_to_the_lexically_greatest_phase PASSED [ 49%]
tests/test_phases.py::test_an_unrelated_branch_name_falls_back PASSED    [ 50%]
tests/test_phases.py::test_a_branch_that_cannot_be_read_falls_back PASSED [ 50%]
tests/test_phases.py::test_a_branch_naming_a_missing_phase_directory_is_still_current PASSED [ 50%]
tests/test_phases.py::test_a_phase_with_no_directory_is_marked_not_started PASSED [ 50%]
tests/test_phases.py::test_a_phase_with_no_directory_reports_every_artifact_absent PASSED [ 50%]
tests/test_phases.py::test_a_phase_with_no_directory_is_not_an_error PASSED [ 50%]
tests/test_phases.py::test_a_project_with_no_phases_has_no_current_phase PASSED [ 50%]
tests/test_phases.py::test_a_project_with_no_phases_is_not_an_error PASSED [ 50%]
tests/test_phases.py::test_an_absent_specs_directory_is_not_a_crash PASSED [ 50%]
tests/test_phases.py::test_creating_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 50%]
tests/test_phases.py::test_editing_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 51%]
tests/test_phases.py::test_the_current_phase_is_stable_when_every_directory_is_touched_in_reverse_order PASSED [ 51%]
tests/test_phases.py::test_the_required_artifacts_are_the_seven_named PASSED [ 51%]
tests/test_phases.py::test_an_unexpected_file_in_a_phase_directory_is_not_required PASSED [ 51%]
tests/test_phases.py::test_an_unexpected_file_does_not_appear_in_the_artifact_report PASSED [ 51%]
tests/test_phases.py::test_an_existing_artifact_is_present PASSED        [ 51%]
tests/test_phases.py::test_a_missing_artifact_is_absent PASSED           [ 51%]
tests/test_phases.py::test_an_empty_artifact_file_is_still_present PASSED [ 51%]
tests/test_phases.py::test_a_directory_named_like_an_artifact_is_not_present PASSED [ 51%]
tests/test_phases.py::test_the_artifact_report_has_exactly_two_states PASSED [ 51%]
tests/test_phases.py::test_a_one_byte_artifact_is_present PASSED         [ 52%]
tests/test_phases.py::test_a_document_with_no_headings_is_present PASSED [ 52%]
tests/test_phases.py::test_a_document_of_only_headings_is_present PASSED [ 52%]
tests/test_phases.py::test_no_artifact_but_the_poc_report_is_ever_opened PASSED [ 52%]
tests/test_phases.py::test_a_ran_poc_requires_a_brief PASSED             [ 52%]
tests/test_phases.py::test_a_skipped_poc_does_not_require_a_brief PASSED [ 52%]
tests/test_phases.py::test_a_skipped_phase_with_no_brief_is_complete PASSED [ 52%]
tests/test_phases.py::test_a_skipped_phase_requires_the_other_six PASSED [ 52%]
tests/test_phases.py::test_an_unrecognised_status_is_reported_as_a_problem PASSED [ 52%]
tests/test_phases.py::test_an_unrecognised_status_still_requires_the_brief PASSED [ 52%]
tests/test_phases.py::test_a_missing_status_field_is_reported_and_requires_the_brief PASSED [ 53%]
tests/test_phases.py::test_the_unrecognised_status_problem_names_the_value_it_found PASSED [ 53%]
tests/test_phases.py::test_an_absent_poc_report_makes_both_it_and_the_brief_absent PASSED [ 53%]
tests/test_phases.py::test_an_absent_poc_report_raises_no_problem_beyond_the_absences PASSED [ 53%]
tests/test_phases.py::test_a_phase_with_no_poc_report_still_requires_the_brief PASSED [ 53%]
tests/test_phases.py::test_the_status_vocabulary_is_exactly_two_tokens PASSED [ 53%]
tests/test_phases.py::test_a_status_containing_skipped_as_a_substring_is_not_skipped PASSED [ 53%]
tests/test_phases.py::test_the_prose_status_values_this_repo_used_before_are_not_accepted PASSED [ 53%]
tests/test_phases.py::test_status_matching_is_case_sensitive PASSED      [ 53%]
tests/test_phases.py::test_an_unquoted_status_is_recognised PASSED       [ 53%]
tests/test_phases.py::test_a_truncated_design_spec_is_reported_present PASSED [ 54%]
tests/test_phases.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 54%]
tests/test_phases.py::test_the_report_exposes_no_completeness_field PASSED [ 54%]
tests/test_phases.py::test_a_two_section_tdd_log_is_present PASSED       [ 54%]
tests/test_phases.py::test_the_real_phase_one_tdd_log_is_present PASSED  [ 54%]
tests/test_phases.py::test_the_real_repository_resolves_eight_phases PASSED [ 54%]
tests/test_phases.py::test_the_real_repository_orders_phases_one_through_eight PASSED [ 54%]
tests/test_phases.py::test_phases_one_through_five_have_every_required_artifact PASSED [ 54%]
tests/test_phases.py::test_the_real_phase_one_is_complete_despite_having_no_brief PASSED [ 54%]
tests/test_phases.py::test_the_real_phase_six_is_missing_exactly_its_unwritten_artifacts PASSED [ 54%]
tests/test_phases.py::test_a_real_detached_head_falls_back_to_lexical PASSED [ 55%]
tests/test_phases.py::test_a_real_phase_branch_resolves_to_its_directory PASSED [ 55%]
tests/test_phases.py::test_a_real_clone_preserves_phase_ordering PASSED  [ 55%]
tests/test_phases.py::test_a_problem_in_a_non_current_phase_is_still_reported PASSED [ 55%]
tests/test_phases.py::test_a_reported_problem_names_the_phase_it_came_from PASSED [ 55%]
tests/test_phases.py::test_problems_are_reported_in_phase_order PASSED   [ 55%]
tests/test_phases.py::test_the_current_phase_problem_is_reported_exactly_once PASSED [ 55%]
tests/test_phases.py::test_a_clean_tree_still_reports_no_problems PASSED [ 55%]
tests/test_plugin.py::test_the_plugin_manifest_declares_agent_plugins_1_0 PASSED [ 55%]
tests/test_plugin.py::test_the_plugin_manifest_uses_only_allowed_fields PASSED [ 55%]
tests/test_plugin.py::test_no_command_shares_a_name_with_a_skill PASSED  [ 56%]
tests/test_plugin.py::test_the_plugin_owns_the_atom_command_namespace PASSED [ 56%]
tests/test_plugin.py::test_no_command_shares_a_name_with_the_plugin PASSED [ 56%]
tests/test_plugin.py::test_the_atom_router_is_available_as_start PASSED  [ 56%]
tests/test_plugin.py::test_no_skill_shares_a_name_with_the_plugin PASSED [ 56%]
tests/test_plugin.py::test_the_plugin_exposes_exactly_the_compact_skill_names PASSED [ 56%]
tests/test_plugin.py::test_the_marketplace_lists_the_plugin_by_its_manifest_name PASSED [ 56%]
tests/test_plugin.py::test_the_marketplace_sources_the_repository_root PASSED [ 56%]
tests/test_plugin.py::test_every_atom_skill_directory_is_discoverable PASSED [ 56%]
tests/test_report.py::test_render_text_shows_every_gate_with_status_and_duration PASSED [ 56%]
tests/test_report.py::test_render_text_shows_details_for_failed_gates_only PASSED [ 57%]
tests/test_report.py::test_render_text_omits_details_for_passing_gates PASSED [ 57%]
tests/test_report.py::test_render_text_includes_warnings PASSED          [ 57%]
tests/test_report.py::test_render_text_without_colour_emits_no_escape_codes PASSED [ 57%]
tests/test_report.py::test_render_text_with_colour_emits_escape_codes PASSED [ 57%]
tests/test_report.py::test_render_json_is_valid_json_for_a_passing_report PASSED [ 57%]
tests/test_report.py::test_render_json_is_valid_json_for_a_failing_report PASSED [ 57%]
tests/test_report.py::test_render_json_includes_a_schema_version PASSED  [ 57%]
tests/test_report.py::test_render_json_includes_every_gate_with_its_evidence PASSED [ 57%]
tests/test_report.py::test_a_spike_that_answered_is_not_rendered_as_a_failed_stage PASSED [ 57%]
tests/test_report.py::test_an_answering_stage_says_it_answered_rather_than_that_it_exited PASSED [ 58%]
tests/test_report.py::test_a_refuted_spike_is_not_rendered_as_a_failure_either PASSED [ 58%]
tests/test_report.py::test_a_crashed_spike_is_still_rendered_as_a_failure PASSED [ 58%]
tests/test_report.py::test_a_crash_explains_that_exit_2_was_a_panic_not_a_verdict PASSED [ 58%]
tests/test_report.py::test_the_spike_output_is_shown_even_when_nothing_failed PASSED [ 58%]
tests/test_report.py::test_json_reports_no_failed_stage_for_a_spike_that_answered PASSED [ 58%]
tests/test_report.py::test_json_exposes_answered_separately_from_ran PASSED [ 58%]
tests/test_report.py::test_stderr_is_rendered_before_stdout PASSED       [ 58%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_names_every_model_that_took_part PASSED [ 58%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_states_how_many_runs_each_model_completed PASSED [ 58%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_describes_the_diff_that_was_reviewed PASSED [ 59%]
tests/test_review_output.py::TestWhatWasReviewed::test_a_model_that_failed_every_run_is_still_named PASSED [ 59%]
tests/test_review_output.py::TestWhatWasReviewed::test_an_unavailable_model_is_named_but_its_error_text_is_not_repeated PASSED [ 59%]
tests/test_review_output.py::TestWhatWasReviewed::test_responses_nobody_could_parse_are_reported PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_findings_are_grouped_under_their_file PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_a_single_line_finding_shows_that_line PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_a_finding_spanning_several_lines_shows_the_span PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_no_bare_finding_count_is_printed PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_every_model_message_is_shown_with_its_author PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_the_report_lists_toolchain_verdicts PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_agreement_is_shown_as_a_fraction_per_model PASSED [ 60%]
tests/test_review_output.py::TestFindingPresentation::test_disagreement_about_severity_is_visible PASSED [ 60%]
tests/test_review_output.py::TestFindingPresentation::test_findings_appear_in_severity_order PASSED [ 60%]
tests/test_review_output.py::TestFindingPresentation::test_a_review_with_no_findings_says_so_explicitly PASSED [ 60%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_markdown PASSED [ 60%]
tests/test_review_output.py::TestPartialReviews::test_a_complete_review_is_not_marked_partial PASSED [ 60%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_json PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_json_is_valid_and_carries_a_schema_version PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_review_schema_version_records_the_corroboration_narrowing PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_other_reports_did_not_change_and_keep_their_version PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_findings_with_their_line_span PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_agreement_with_both_halves_of_the_fraction PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_keeps_every_attributed_message PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_names_models_that_produced_nothing PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_unparseable_responses PASSED [ 61%]
tests/test_review_output.py::TestChannelSeparation::test_operational_problems_render_separately_from_the_report PASSED [ 61%]
tests/test_review_output.py::TestChannelSeparation::test_a_clean_review_produces_no_problem_output PASSED [ 61%]
tests/test_review_output.py::TestChannelSeparation::test_the_markdown_report_does_not_repeat_the_problem_text PASSED [ 61%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_it_is_partial_when_a_run_failed PASSED [ 61%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_with_every_run_answered_is_not_partial PASSED [ 61%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_when_no_model_produced_anything_usable PASSED [ 62%]
tests/test_review_output.py::TestReviewOutcome::test_a_review_that_ran_but_found_nothing_is_not_treated_as_unusable PASSED [ 62%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_a_completed_run_whose_reply_was_unreadable_yields_no_usable_response PASSED [ 62%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_such_a_review_does_not_exit_zero PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_left_out_of_the_denominator PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_finding_both_readable_runs_reported_is_not_shown_as_a_dissent PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_completed_without_answering_makes_the_review_partial PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_notice_counts_the_run_that_could_not_be_read PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_reports_answered_runs_alongside_completed_ones PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_that_partly_parsed_still_counts_as_an_answer PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_clean_review_still_counts_every_run_and_is_not_partial PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_model_whose_every_reply_was_unreadable_renders_without_crashing PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_missing_run_is_still_partial PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[   \n\t ] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[I reviewed it and found nothing.] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_returned_nothing_is_named_in_the_report PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[file-guard only] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[schema-invalid] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[mixed] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_not_named_twice PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_is_never_also_counted_as_overruled PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_despite_a_malformed_element_is_not_called_unreadable PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_is_not_called_a_review_that_produced_nothing PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_gets_its_own_heading PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_total_excludes_an_overruled_reply PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_banner_does_not_promise_stderr_detail PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_distinguishes_an_overruled_reply_from_an_unreadable_one PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_overruled_by_the_file_guard_does_not_make_the_review_partial PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_still_leaves_the_denominator PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unparseable_reply_is_still_silence PASSED [ 65%]
tests/test_review_output.py::TestTheReportSurvivesEveryConsoleEncoding::test_rendered_markdown_is_pure_ascii PASSED [ 65%]
tests/test_review_toolchain.py::test_empty_toolchain_placeholder_preserves_original_prompt_bytes PASSED [ 65%]
tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails PASSED [ 65%]
tests/test_review_toolchain.py::test_run_review_continues_with_no_exclusions_when_directory_is_not_go_module PASSED [ 65%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 65%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 65%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 65%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 65%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 65%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 66%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 66%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 66%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind PASSED [ 66%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 66%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 66%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 67%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 67%]
tests/test_scaffold.py::test_scaffold_creates_exactly_three_files PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_shells_out_to_go_mod_init PASSED   [ 67%]
tests/test_scaffold.py::test_scaffold_go_mod_pins_full_patch_version PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_module_path_is_namespaced_under_spike PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_rolls_back_completely_when_go_mod_init_fails PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_rollback_leaves_sibling_spikes_untouched PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_main_go_is_package_main_with_a_main_function PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_main_go_prints_the_question PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_main_go_documents_the_exit_code_convention PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_readme_has_the_report_sections PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_readme_records_the_question PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[Json-Streaming] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json_streaming] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json streaming] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[-leading] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[trailing-] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[double--hyphen] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[] PASSED    [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[../escape] PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json] PASSED   [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json-streaming] PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[http2-vs-http3] PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[a1] PASSED     [ 69%]
tests/test_scaffold.py::test_scaffold_slug_error_explains_the_rule PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_refuses_to_overwrite_an_existing_spike PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_does_not_modify_an_existing_spike_when_refusing PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_creates_poc_root_when_missing PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_reports_every_file_it_created PASSED [ 69%]
tests/test_ship.py::TestGhPrecondition::test_a_missing_gh_is_an_unmet_precondition_not_a_late_failure PASSED [ 70%]
tests/test_ship.py::TestGhPrecondition::test_gh_is_verified_before_any_git_work_begins PASSED [ 70%]
tests/test_ship.py::TestGhPrecondition::test_the_missing_gh_message_names_the_install PASSED [ 70%]
tests/test_ship.py::TestBranchPreconditions::test_a_detached_head_has_nothing_to_ship_from PASSED [ 70%]
tests/test_ship.py::TestBranchPreconditions::test_shipping_the_base_branch_itself_is_refused PASSED [ 70%]
tests/test_ship.py::TestDirtyTree::test_a_dirty_working_tree_is_refused PASSED [ 70%]
tests/test_ship.py::TestDirtyTree::test_the_dirty_tree_refusal_lists_the_modified_files PASSED [ 70%]
tests/test_ship.py::TestDirtyTree::test_a_clean_tree_is_allowed_to_proceed PASSED [ 70%]
tests/test_ship.py::TestUpstream::test_a_branch_with_no_upstream_and_no_push_is_refused PASSED [ 70%]
tests/test_ship.py::TestUpstream::test_the_missing_upstream_refusal_prints_the_command_that_fixes_it PASSED [ 70%]
tests/test_ship.py::TestUpstream::test_the_push_flag_pushes_the_branch_and_sets_the_upstream PASSED [ 71%]
tests/test_ship.py::TestUpstream::test_the_push_is_a_git_command_never_gh PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_directory_is_derived_from_the_branch_name PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_flag_overrides_the_branch_derivation PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_phase_directory_is_refused_naming_the_path_it_tried PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_the_artifacts_are_the_files_the_phase_directory_holds PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_artifact_is_omitted_rather_than_described_as_pending PASSED [ 71%]
tests/test_ship.py::TestFreshCheck::test_the_check_runs_fresh_as_part_of_ship PASSED [ 71%]
tests/test_ship.py::TestFreshCheck::test_a_recorded_check_result_is_not_accepted PASSED [ 71%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_skips_the_gates PASSED [ 71%]
tests/test_ship.py::TestNotAGoModule::test_the_absent_module_is_recorded_as_an_absence_not_a_failure PASSED [ 72%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal PASSED [ 72%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag PASSED [ 72%]
tests/test_ship.py::TestNotAGoModule::test_the_evidence_section_states_the_absence_rather_than_omitting_it PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_body_carries_one_verdict_row_per_gate PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_verdict_table_is_bounded_at_five_rows PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_body_does_not_embed_the_gates_full_output PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_when_there_is_no_module_the_table_is_replaced_by_the_recorded_line PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty PASSED [ 72%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_check_refuses_to_open_or_update_the_pr PASSED [ 72%]
tests/test_ship.py::TestCheckRefusal::test_the_check_refusal_names_the_failing_gates PASSED [ 73%]
tests/test_ship.py::TestCheckRefusal::test_allow_failing_checks_overrides_the_refusal PASSED [ 73%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent PASSED [ 73%]
tests/test_ship.py::TestOverride::test_an_overridden_run_states_the_failure_in_the_body PASSED [ 73%]
tests/test_ship.py::TestOverride::test_an_overridden_body_never_asserts_green_while_red PASSED [ 73%]
tests/test_ship.py::TestOverride::test_an_overridden_run_still_exits_non_zero PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_is_summary_plus_links PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_never_embeds_an_artifacts_content PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_title_comes_from_the_design_specs_h1 PASSED [ 73%]
tests/test_ship.py::TestBody::test_a_title_flag_overrides_the_design_spec_h1 PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_quotes_the_design_specs_purpose_paragraph PASSED [ 74%]
tests/test_ship.py::TestBody::test_what_changed_lists_the_commit_subjects_on_the_branch PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_artifact_links_point_at_the_pushed_commit_sha PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_uses_a_branch_name PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_points_at_the_base_branch PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_the_push_happens_before_the_body_is_assembled PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_body_file_contains_no_carriage_return PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_reported_size_is_the_character_count_not_the_byte_count PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_body_travels_by_body_file PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_body_flag_never_appears_in_the_argv PASSED [ 74%]
tests/test_ship.py::TestCreateAndUpdate::test_an_existing_pr_is_queried_before_any_create PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_is_treated_as_a_fallback_not_the_primary_signal PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_still_recovers_when_the_query_missed_it PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_on_a_branch_with_a_pr_updates_the_body PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_is_not_treated_as_an_error PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_ghs_error_text_is_passed_through_verbatim PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_every_gh_call_receives_empty_stdin PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_reuses_the_phase_one_to_three_exit_codes PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_an_unmet_precondition_exits_by_the_ordinary_failure_route PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_there_is_no_distinct_precondition_exit_code PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_never_issues_a_commit PASSED [ 76%]
tests/test_ship.py::TestExitCodesAndScope::test_no_git_commit_command_is_ever_run PASSED [ 76%]
tests/test_ship.py::TestOutcomeShape::test_a_clean_run_reports_succeeded PASSED [ 76%]
tests/test_ship.py::TestOutcomeShape::test_an_overridden_run_reports_not_succeeded PASSED [ 76%]
tests/test_ship.py::TestOutcomeShape::test_a_created_pr_reports_the_created_action_and_url PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_branch_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_status_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_a_failed_push_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_an_unresolvable_head_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_a_missing_origin_remote_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_a_failed_log_leaves_the_what_changed_section_empty_not_fatal PASSED [ 77%]
tests/test_ship.py::TestDegradedGit::test_a_failed_edit_is_refused_with_ghs_text PASSED [ 77%]
tests/test_ship.py::TestDegradedGit::test_a_create_failure_with_no_output_still_refuses PASSED [ 77%]
tests/test_ship.py::TestDegradedGit::test_a_create_success_without_a_url_falls_back_to_raw_stdout PASSED [ 77%]
tests/test_ship.py::TestPhaseResolutionEdges::test_a_direct_relative_path_resolves_the_phase PASSED [ 77%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_ambiguous_phase_name_is_refused PASSED [ 77%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_artifact_outside_the_repo_root_keeps_its_full_path PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_the_title_falls_back_to_the_branch_when_no_design_spec PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_design_spec_without_an_h1_falls_back_to_the_branch_title PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_an_ssh_remote_url_yields_the_owner_name_slug PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_with_empty_output_is_treated_as_no_existing_pr PASSED [ 78%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_that_prints_a_bare_url_is_accepted PASSED [ 78%]
tests/test_ship.py::TestDirtyTreeParsing::test_a_rename_lists_the_new_path PASSED [ 78%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_a_refused_ship_never_pushes_even_when_push_was_requested PASSED [ 78%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_the_check_runs_before_the_push_on_a_passing_run PASSED [ 78%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_an_overridden_failing_check_still_pushes PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_ahead_of_its_upstream_is_refused PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_the_refusal_says_how_far_ahead_and_how_to_fix_it PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_level_with_its_upstream_ships PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_being_ahead_is_irrelevant_when_push_was_requested PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_no_pr_is_opened_when_the_commit_is_not_on_the_remote PASSED [ 79%]
tests/test_spike.py::test_runner_error_cannot_confirm_a_spike PASSED     [ 79%]
tests/test_spike.py::test_runs_vet_then_build_then_execute PASSED        [ 79%]
tests/test_spike.py::test_reports_all_three_stages PASSED                [ 79%]
tests/test_spike.py::test_never_uses_go_run PASSED                       [ 79%]
tests/test_spike.py::test_build_failure_skips_execute PASSED             [ 79%]
tests/test_spike.py::test_vet_failure_skips_build_and_execute PASSED     [ 79%]
tests/test_spike.py::test_build_failure_is_reported_as_build_not_execute PASSED [ 79%]
tests/test_spike.py::test_execute_failure_is_reported_as_execute_not_build PASSED [ 79%]
tests/test_spike.py::test_captures_both_streams_from_the_spike PASSED    [ 79%]
tests/test_spike.py::test_keeps_stdout_from_a_spike_that_failed PASSED   [ 80%]
tests/test_spike.py::test_maps_exit_code_to_verdict[0-Verdict.CONFIRMED] PASSED [ 80%]
tests/test_spike.py::test_maps_exit_code_to_verdict[1-Verdict.REFUTED] PASSED [ 80%]
tests/test_spike.py::test_maps_exit_code_to_verdict[2-Verdict.INCONCLUSIVE] PASSED [ 80%]
tests/test_spike.py::test_inconclusive_survives_as_inconclusive PASSED   [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[3] PASSED [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[7] PASSED [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[42] PASSED [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[127] PASSED [ 80%]
tests/test_spike.py::test_no_verdict_when_the_spike_never_ran PASSED     [ 80%]
tests/test_spike.py::test_binary_is_not_left_in_the_spike_directory PASSED [ 81%]
tests/test_spike.py::test_binary_is_removed_even_when_the_spike_fails PASSED [ 81%]
tests/test_spike.py::test_build_output_path_is_outside_the_spike_directory PASSED [ 81%]
tests/test_spike.py::test_default_timeout_is_300_seconds PASSED          [ 81%]
tests/test_spike.py::test_timeout_is_overridable PASSED                  [ 81%]
tests/test_spike.py::test_timed_out_spike_has_no_verdict PASSED          [ 81%]
tests/test_spike.py::test_detects_a_command_spike_from_its_source PASSED [ 81%]
tests/test_spike.py::test_detects_a_library_spike_from_its_source PASSED [ 81%]
tests/test_spike.py::test_library_spike_runs_go_test_instead_of_a_binary PASSED [ 81%]
tests/test_spike.py::test_library_spike_still_builds_first PASSED        [ 81%]
tests/test_spike.py::test_library_spike_passing_tests_is_confirmed PASSED [ 82%]
tests/test_spike.py::test_library_spike_failing_tests_is_refuted PASSED  [ 82%]
tests/test_spike.py::test_library_spike_can_never_be_inconclusive PASSED [ 82%]
tests/test_spike.py::test_library_spike_does_not_build_a_binary PASSED   [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[0] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[1] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[2] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[42] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_timed_out_did_not_produce_an_answer PASSED [ 82%]
tests/test_spike.py::test_skipped_execute_stage_did_not_produce_an_answer PASSED [ 82%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[vet] PASSED [ 83%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[build] PASSED [ 83%]
tests/test_spike.py::test_panicking_spike_is_crashed_not_inconclusive PASSED [ 83%]
tests/test_spike.py::test_deliberate_exit_2_is_still_inconclusive PASSED [ 83%]
tests/test_spike.py::test_crash_detection_needs_both_the_exit_code_and_the_signature PASSED [ 83%]
tests/test_spike.py::test_crash_detection_requires_a_stack_dump_not_just_the_word PASSED [ 83%]
tests/test_spike.py::test_a_crashed_spike_still_reports_its_exit_code PASSED [ 83%]
tests/test_spike.py::test_a_crashed_spike_did_not_answer PASSED          [ 83%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[0] PASSED [ 83%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[1] PASSED [ 83%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[2] PASSED [ 84%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[1] PASSED [ 84%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[2] PASSED [ 84%]
tests/test_spike.py::test_a_crashed_spike_does_have_a_failed_stage PASSED [ 84%]
tests/test_spike.py::test_a_build_failure_is_still_a_failed_stage PASSED [ 84%]
tests/test_spike.py::test_library_spike_panicking_is_also_crashed PASSED [ 84%]
tests/test_state.py::test_all_state_lives_under_a_single_directory PASSED [ 84%]
tests/test_state.py::test_config_and_state_are_separate_files PASSED     [ 84%]
tests/test_state.py::test_a_project_without_a_state_file_is_not_initialised PASSED [ 84%]
tests/test_state.py::test_a_project_is_initialised_once_both_files_exist PASSED [ 84%]
tests/test_state.py::test_init_writes_the_module_path PASSED             [ 85%]
tests/test_state.py::test_init_writes_an_empty_approvals_list PASSED     [ 85%]
tests/test_state.py::test_init_writes_no_phase_or_status PASSED          [ 85%]
tests/test_state.py::test_init_records_an_event PASSED                   [ 85%]
tests/test_state.py::test_the_state_file_holds_configuration_and_approvals PASSED [ 85%]
tests/test_state.py::test_the_module_path_stays_in_config_not_state PASSED [ 85%]
tests/test_state.py::test_the_state_file_has_no_phase_field PASSED       [ 85%]
tests/test_state.py::test_the_state_file_has_no_status_field PASSED      [ 85%]
tests/test_state.py::test_an_approval_records_phase_gate_and_date PASSED [ 85%]
tests/test_state.py::test_recording_an_approval_appends_rather_than_replaces PASSED [ 85%]
tests/test_state.py::test_an_absent_state_file_is_not_an_error PASSED    [ 86%]
tests/test_state.py::test_an_absent_state_file_reports_no_approvals PASSED [ 86%]
tests/test_state.py::test_a_corrupt_state_file_is_reported_as_a_problem PASSED [ 86%]
tests/test_state.py::test_a_non_string_module_path_is_ignored_not_trusted PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-array-at-top-level] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-string] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[dict-missing-approvals] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approvals-not-a-list] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approval-entry-not-a-dict] PASSED [ 86%]
tests/test_state.py::test_project_state_carries_configuration_and_approvals PASSED [ 86%]
tests/test_state.py::test_project_state_carries_no_phase PASSED          [ 87%]
tests/test_state.py::test_the_state_module_exposes_no_phase_enum PASSED  [ 87%]
tests/test_state.py::test_the_state_module_exposes_no_status_enum PASSED [ 87%]
tests/test_state.py::test_the_state_module_exposes_no_transition_machinery PASSED [ 87%]
tests/test_state.py::test_a_version_one_state_file_is_reported_as_outdated PASSED [ 87%]
tests/test_state.py::test_an_outdated_state_file_is_not_called_corrupt PASSED [ 87%]
tests/test_state.py::test_an_outdated_state_file_says_what_to_do_about_it PASSED [ 87%]
tests/test_state.py::test_an_outdated_state_file_yields_no_approvals PASSED [ 87%]
tests/test_state.py::test_a_file_missing_approvals_without_the_v1_shape_is_still_corrupt PASSED [ 87%]
tests/test_state.py::test_an_approval_missing_a_field_is_a_problem PASSED [ 87%]
tests/test_state.py::test_an_empty_approval_object_is_not_a_valid_approval PASSED [ 88%]
tests/test_state.py::test_an_approval_with_a_non_string_field_is_a_problem PASSED [ 88%]
tests/test_state.py::test_a_malformed_approval_names_its_position PASSED [ 88%]
tests/test_state.py::test_well_formed_approvals_still_load PASSED        [ 88%]
tests/test_status.py::test_the_text_rendering_names_the_project_root PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_names_the_current_phase PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_branch PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_fallback PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_lists_every_required_artifact PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_shows_a_recorded_approval PASSED [ 88%]
tests/test_status.py::test_every_other_phase_gets_one_summary_line PASSED [ 89%]
tests/test_status.py::test_the_summary_line_reports_present_over_required PASSED [ 89%]
tests/test_status.py::test_a_skipped_poc_phase_summarises_out_of_six PASSED [ 89%]
tests/test_status.py::test_the_current_phase_is_not_repeated_in_the_summary PASSED [ 89%]
tests/test_status.py::test_the_summary_is_ordered_lexically PASSED       [ 89%]
tests/test_status.py::test_the_json_contract_has_the_documented_keys PASSED [ 89%]
tests/test_status.py::test_the_json_phases_array_covers_every_phase PASSED [ 89%]
tests/test_status.py::test_the_json_phases_array_includes_the_current_phase PASSED [ 89%]
tests/test_status.py::test_the_json_artifact_map_is_name_to_boolean PASSED [ 89%]
tests/test_status.py::test_the_json_is_parseable_when_problems_exist PASSED [ 89%]
tests/test_status.py::test_two_problems_are_both_reported PASSED         [ 90%]
tests/test_status.py::test_a_problem_does_not_suppress_the_rest_of_the_report PASSED [ 90%]
tests/test_status.py::test_a_phase_missing_artifacts_still_answers PASSED [ 90%]
tests/test_status.py::test_a_project_with_no_phases_still_answers PASSED [ 90%]
tests/test_status.py::test_a_corrupt_state_file_still_answers PASSED     [ 90%]
tests/test_status.py::test_an_unreadable_project_root_is_reported_not_raised PASSED [ 90%]
tests/test_status.py::test_the_status_report_exposes_no_could_answer PASSED [ 90%]
tests/test_status.py::test_the_temp_file_sweep_still_runs PASSED         [ 90%]
tests/test_status.py::test_the_sweep_is_still_reported_never_silent PASSED [ 90%]
tests/test_status.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 90%]
tests/test_status.py::test_the_default_runner_and_project_resolution_are_used PASSED [ 91%]
tests/test_status.py::test_the_default_path_without_a_specs_directory_reports_no_phases PASSED [ 91%]
tests/test_status.py::test_a_specs_directory_without_a_project_reports_no_phases PASSED [ 91%]
tests/test_status.py::test_more_than_one_project_directory_is_reported_and_the_first_used PASSED [ 91%]
tests/test_status.py::test_a_project_directory_beside_loose_phase_directories_is_reported PASSED [ 91%]
tests/test_status.py::test_the_mixed_layout_still_reports_the_project_directory_phases PASSED [ 91%]
tests/test_status.py::test_a_flat_layout_is_accepted_without_comment PASSED [ 91%]
tests/test_status.py::test_real_repository_reports_multiple_projects_and_atom_cli_history_remains_readable PASSED [ 91%]
tests/test_status.py::test_a_corrupt_config_is_reported_separately PASSED [ 91%]
tests/test_status.py::test_the_last_event_and_damaged_lines_are_reported PASSED [ 91%]
tests/test_status.py::test_the_text_rendering_shows_the_module_path PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_marks_a_not_started_phase PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_states_when_there_is_no_current_phase PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_shows_the_last_event PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_points_at_the_problems PASSED [ 92%]
tests/test_status.py::test_the_problem_renderer_is_empty_when_there_are_no_problems PASSED [ 92%]
tests/test_status.py::test_the_problem_renderer_uses_amber_advisories PASSED [ 92%]
tests/test_status.py::test_the_problem_renderer_never_uses_red PASSED    [ 92%]
tests/test_storage.py::test_reading_a_missing_file_says_it_is_missing PASSED [ 92%]
tests/test_storage.py::test_reading_unparseable_json_reports_corruption PASSED [ 92%]
tests/test_storage.py::test_reading_valid_json_of_the_wrong_type_is_still_corruption PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected["just a string"-str] PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[42-int] PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[null-NoneType] PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[true-bool] PASSED [ 93%]
tests/test_storage.py::test_an_empty_file_is_corruption_not_emptiness PASSED [ 93%]
tests/test_storage.py::test_a_file_of_nul_bytes_is_corruption PASSED     [ 93%]
tests/test_storage.py::test_a_missing_required_key_is_corruption_and_names_the_key PASSED [ 93%]
tests/test_storage.py::test_reading_a_well_formed_file_returns_the_object PASSED [ 93%]
tests/test_storage.py::test_reading_does_not_keep_the_file_open PASSED   [ 93%]
tests/test_storage.py::test_writing_then_reading_round_trips PASSED      [ 94%]
tests/test_storage.py::test_writing_creates_the_parent_directory PASSED  [ 94%]
tests/test_storage.py::test_writing_leaves_no_temp_file_behind_on_success PASSED [ 94%]
tests/test_storage.py::test_writing_replaces_rather_than_truncating PASSED [ 94%]
tests/test_storage.py::test_writing_retries_while_the_destination_is_held_open PASSED [ 94%]
tests/test_storage.py::test_a_write_that_cannot_succeed_fails_loudly PASSED [ 94%]
tests/test_storage.py::test_sweeping_removes_leftover_temp_files PASSED  [ 94%]
tests/test_storage.py::test_sweeping_reports_what_it_removed PASSED      [ 94%]
tests/test_storage.py::test_sweeping_leaves_unsaved_recovery_files_alone PASSED [ 94%]
tests/test_storage.py::test_sweeping_leaves_real_state_files_alone PASSED [ 94%]
tests/test_storage.py::test_sweeping_an_absent_directory_is_not_an_error PASSED [ 95%]
tests/test_style.py::test_style_rules_reach_the_model_by_default PASSED  [ 95%]
tests/test_style.py::test_style_rules_can_be_switched_off_for_measurement PASSED [ 95%]
tests/test_style.py::test_style_rules_sit_before_the_output_format_instruction PASSED [ 95%]
tests/test_style.py::test_every_rule_is_numbered_and_present PASSED      [ 95%]
tests/test_style.py::test_no_rule_is_phrased_as_a_preference PASSED      [ 95%]
tests/test_toolchain.py::test_prompt_block_excludes_everything_the_passing_toolchain_proved PASSED [ 95%]
tests/test_toolchain.py::test_prompt_block_does_not_exclude_ignored_errors_when_errcheck_was_skipped PASSED [ 95%]
tests/test_toolchain.py::test_prompt_block_says_nothing_is_excluded_when_toolchain_did_not_run PASSED [ 95%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 95%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 96%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] PASSED [ 96%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 96%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout PASSED [ 96%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 96%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 96%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 96%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 96%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 96%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 96%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 97%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 97%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 97%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 97%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 98%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 98%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 98%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 98%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 98%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 99%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 99%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [ 99%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 99%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 99%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 99%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 99%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

================================== FAILURES ===================================
________ test_built_package_installs_working_dedicated_console_script _________

tmp_path = WindowsPath('<private-home>/AppData/Local/Temp/pytest-of-user/pytest-390/test_built_package_installs_wo0')

    def test_built_package_installs_working_dedicated_console_script(
        tmp_path: Path,
    ) -> None:
        wheelhouse = tmp_path / "wheelhouse"
        wheelhouse.mkdir()
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--quiet",
                "--no-deps",
                "--wheel-dir",
                str(wheelhouse),
                str(REPOSITORY / "tools"),
            ],
            check=True,
        )
        wheel = next(wheelhouse.glob("atom_cli-*.whl"))
    
        environment = tmp_path / "environment"
        subprocess.run([sys.executable, "-m", "venv", str(environment)], check=True)
        environment_python = (
            environment / "Scripts" / "python.exe"
            if os.name == "nt"
            else environment / "bin" / "python"
        )
        subprocess.run(
            [
                str(environment_python),
                "-m",
                "pip",
                "install",
                "--quiet",
                "--no-deps",
                str(wheel),
            ],
            check=True,
        )
        writer = (
            environment / "Scripts" / "atom-write-artifact.exe"
            if os.name == "nt"
            else environment / "bin" / "atom-write-artifact"
        )
    
        repository = tmp_path / "repository"
        repository.mkdir()
>       allowed = subprocess.run(
            [str(writer), "specs/installed.md"],
            cwd=repository,
            input="# Installed\n".encode(),
            capture_output=True,
        )

tests\test_artifact_integration.py:155: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\subprocess.py:554: in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\subprocess.py:1039: in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <Popen: returncode: None args: ['<private-home>\\AppData\\Local\\Temp\\...>
args = '<private-home>\\AppData\\Local\\Temp\\pytest-of-user\\pytest-390\\test_built_package_installs_wo0\\environment\\Scripts\\atom-write-artifact.exe specs/installed.md'
executable = None, preexec_fn = None, close_fds = False, pass_fds = ()
cwd = '<private-home>\\AppData\\Local\\Temp\\pytest-of-user\\pytest-390\\test_built_package_installs_wo0\\repository'
env = None, startupinfo = <subprocess.STARTUPINFO object at 0x0000017F8DABA190>
creationflags = 0, shell = False, p2cread = Handle(956), p2cwrite = 11
c2pread = 12, c2pwrite = Handle(940), errread = 13, errwrite = Handle(1316)
unused_restore_signals = True, unused_gid = None, unused_gids = None
unused_uid = None, unused_umask = -1, unused_start_new_session = False
unused_process_group = -1

    def _execute_child(self, args, executable, preexec_fn, close_fds,
                       pass_fds, cwd, env,
                       startupinfo, creationflags, shell,
                       p2cread, p2cwrite,
                       c2pread, c2pwrite,
                       errread, errwrite,
                       unused_restore_signals,
                       unused_gid, unused_gids, unused_uid,
                       unused_umask,
                       unused_start_new_session, unused_process_group):
        """Execute program (MS Windows version)"""
    
        assert not pass_fds, "pass_fds not supported on Windows."
    
        if isinstance(args, str):
            pass
        elif isinstance(args, bytes):
            if shell:
                raise TypeError('bytes args is not allowed on Windows')
            args = list2cmdline([args])
        elif isinstance(args, os.PathLike):
            if shell:
                raise TypeError('path-like args is not allowed when '
                                'shell is true')
            args = list2cmdline([args])
        else:
            args = list2cmdline(args)
    
        if executable is not None:
            executable = os.fsdecode(executable)
    
        # Process startup details
        if startupinfo is None:
            startupinfo = STARTUPINFO()
        else:
            # bpo-34044: Copy STARTUPINFO since it is modified above,
            # so the caller can reuse it multiple times.
            startupinfo = startupinfo.copy()
    
        use_std_handles = -1 not in (p2cread, c2pwrite, errwrite)
        if use_std_handles:
            startupinfo.dwFlags |= _winapi.STARTF_USESTDHANDLES
            startupinfo.hStdInput = p2cread
            startupinfo.hStdOutput = c2pwrite
            startupinfo.hStdError = errwrite
    
        attribute_list = startupinfo.lpAttributeList
        have_handle_list = bool(attribute_list and
                                "handle_list" in attribute_list and
                                attribute_list["handle_list"])
    
        # If we were given an handle_list or need to create one
        if have_handle_list or (use_std_handles and close_fds):
            if attribute_list is None:
                attribute_list = startupinfo.lpAttributeList = {}
            handle_list = attribute_list["handle_list"] = \
                list(attribute_list.get("handle_list", []))
    
            if use_std_handles:
                handle_list += [int(p2cread), int(c2pwrite), int(errwrite)]
    
            handle_list[:] = self._filter_handle_list(handle_list)
    
            if handle_list:
                if not close_fds:
                    warnings.warn("startupinfo.lpAttributeList['handle_list'] "
                                  "overriding close_fds", RuntimeWarning)
    
                # When using the handle_list we always request to inherit
                # handles but the only handles that will be inherited are
                # the ones in the handle_list
                close_fds = False
    
        if shell:
            startupinfo.dwFlags |= _winapi.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = _winapi.SW_HIDE
            if not executable:
                # gh-101283: without a fully-qualified path, before Windows
                # checks the system directories, it first looks in the
                # application directory, and also the current directory if
                # NeedCurrentDirectoryForExePathW(ExeName) is true, so try
                # to avoid executing unqualified "cmd.exe".
                comspec = os.environ.get('ComSpec')
                if not comspec:
                    system_root = os.environ.get('SystemRoot', '')
                    comspec = os.path.join(system_root, 'System32', 'cmd.exe')
                    if not os.path.isabs(comspec):
                        raise FileNotFoundError('shell not found: neither %ComSpec% nor %SystemRoot% is set')
                if os.path.isabs(comspec):
                    executable = comspec
            else:
                comspec = executable
    
            args = '{} /c "{}"'.format (comspec, args)
    
        if cwd is not None:
            cwd = os.fsdecode(cwd)
    
        sys.audit("subprocess.Popen", executable, args, cwd, env)
    
        # Start the process
        try:
>           hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
                                     # no special security
                                     None, None,
                                     int(not close_fds),
                                     creationflags,
                                     env,
                                     cwd,
                                     startupinfo)
E                                    FileNotFoundError: [WinError 2] The system cannot find the file specified

C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\subprocess.py:1554: FileNotFoundError
---------------------------- Captured stderr call -----------------------------


[notice] A new release of pip is available: 26.0.1 -> 26.2.2

[notice] To update, run: <python> -m pip install --upgrade pip



[notice] A new release of pip is available: 26.1.2 -> 26.2.2

[notice] To update, run: <private-home>\AppData\Local\Temp\pytest-of-user\pytest-390\test_built_package_installs_wo0\environment\Scripts\python.exe -m pip install --upgrade pip

=============================== tests coverage ================================
______________ coverage: platform win32, python 3.13.14-final-0 _______________

Name                       Stmts   Miss  Cover
----------------------------------------------
atom\__init__.py               1      0   100%
atom\_windows_process.py     374     28    93%
atom\artifact_cli.py          35      1    97%
atom\artifacts.py            174     19    89%
atom\body.py                  71      0   100%
atom\buildsystem.py           76      5    93%
atom\check.py                 43      2    95%
atom\cli.py                  280     21    92%
atom\diff.py                 121      0   100%
atom\eventlog.py              50      0   100%
atom\extract.py              101      0   100%
atom\filelock.py              64     10    84%
atom\gates.py                173      8    95%
atom\index.py                 40      5    88%
atom\invoke.py               116      0   100%
atom\merge.py                 92      0   100%
atom\onboarding.py            89      3    97%
atom\phases.py                92      0   100%
atom\report.py               329     10    97%
atom\review.py                82      1    99%
atom\runner.py               169     52    69%
atom\scaffold.py              46      1    98%
atom\ship.py                 252      3    99%
atom\spike.py                128      4    97%
atom\state.py                103      1    99%
atom\status.py                77      0   100%
atom\storage.py               79      2    97%
atom\style.py                  4      0   100%
atom\toolchain.py             53      6    89%
----------------------------------------------
TOTAL                       3314    182    95%
=========================== short test summary info ===========================
FAILED tests/test_artifact_integration.py::test_built_package_installs_working_dedicated_console_script - FileNotFoundError: [WinError 2] The system cannot find the file specified
============= 1 failed, 998 passed, 2 skipped in 94.51s (0:01:34) =============
```

## 12-packaging-standard-env

GREEN after removing the validation-only environment override; no packaging code/test change.

Command from tools: `python -m pytest tests\test_artifact_integration.py::test_built_package_installs_working_dedicated_console_script -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_artifact_integration.py .                                     [100%]

============================= 1 passed in 24.23s ==============================
```

## 13-full-python-gate

FAILED standard full attempt: identity observer read an existing ready file once and received PermissionError. This is not passing evidence.

Command from tools: `python -m pytest tests -v --cov=atom`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <python>
cachedir: .pytest_cache
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1001 items

tests/test_artifact_cli.py::test_main_allowed_target_writes_exact_utf8_content PASSED [  0%]
tests/test_artifact_cli.py::test_main_empty_stdin_creates_empty_artifact PASSED [  0%]
tests/test_artifact_cli.py::test_module_execution_runs_main_entry_point PASSED [  0%]
tests/test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback PASSED [  0%]
tests/test_artifact_cli.py::test_main_normalizes_native_shell_line_endings_to_lf PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_the_byte_order_mark_windows_shells_prepend PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_only_the_first_byte_order_mark PASSED [  0%]
tests/test_artifact_cli.py::test_main_invalid_utf8_writes_nothing PASSED [  0%]
tests/test_artifact_cli.py::test_main_refused_target_does_not_read_stdin PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments0] PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments1] PASSED [  1%]
tests/test_artifact_cli.py::test_main_filesystem_failure_reports_error_without_partial_file PASSED [  1%]
tests/test_artifact_cli.py::test_main_refusal_during_write_is_reported PASSED [  1%]
tests/test_artifact_integration.py::test_package_registers_only_the_dedicated_artifact_writer PASSED [  1%]
tests/test_artifact_integration.py::test_main_atom_cli_does_not_expose_artifact_subcommand PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[discover] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[poc] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[plan] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[spec] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[tdd] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[review] PASSED [  2%]
tests/test_artifact_integration.py::test_artifact_writer_instruction_forbids_bypass_and_source_writes PASSED [  2%]
tests/test_artifact_integration.py::test_onboarding_installs_artifact_writer_instructions PASSED [  2%]
tests/test_artifact_integration.py::test_onboarding_does_not_edit_copilot_permission_configuration PASSED [  2%]
tests/test_artifact_integration.py::test_built_package_installs_working_dedicated_console_script PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[specs/project/design.md-allowed-artifact-directory] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[poc/spike/README.md-allowed-artifact-directory] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/config.json-allowed-runtime-file] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/state.json-allowed-runtime-file] PASSED [  2%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/baseline.json-allowed-runtime-file] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[internal/server.go-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[tools/atom/cli.py-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.github/copilot-instructions.md-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/atom/AGENTS.md-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/events.jsonl-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/credentials.json-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs/../internal/escape.go-outside-artifact-set] PASSED [  3%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[../elsewhere/escape.md-outside-repository] PASSED [  3%]
tests/test_artifacts.py::test_absolute_path_outside_the_repository_is_refused PASSED [  3%]
tests/test_artifacts.py::test_link_inside_specs_is_refused_before_containment PASSED [  4%]
tests/test_artifacts.py::test_link_pointing_back_inside_is_still_refused PASSED [  4%]
tests/test_artifacts.py::test_write_creates_nested_artifact_directories PASSED [  4%]
tests/test_artifacts.py::test_write_replaces_an_existing_artifact PASSED [  4%]
tests/test_artifacts.py::test_write_leaves_no_temporary_files_behind PASSED [  4%]
tests/test_artifacts.py::test_mixed_batch_writes_nothing PASSED          [  4%]
tests/test_artifacts.py::test_every_refusal_in_a_batch_is_reported PASSED [  4%]
tests/test_artifacts.py::test_write_through_a_link_is_refused_and_writes_nothing PASSED [  4%]
tests/test_artifacts.py::test_link_appearing_after_validation_is_caught_before_the_write PASSED [  4%]
tests/test_artifacts.py::test_cleanup_removes_a_link_planted_where_it_created_a_directory PASSED [  4%]
tests/test_artifacts.py::test_a_file_in_place_of_a_directory_is_refused PASSED [  5%]
tests/test_artifacts.py::test_a_path_on_another_drive_is_refused PASSED  [  5%]
tests/test_artifacts.py::test_a_failed_stage_leaves_nothing_behind PASSED [  5%]
tests/test_artifacts.py::test_a_failed_replace_preserves_existing_file_and_removes_temporary PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_the_purpose_prose_is_returned PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_every_paragraph_of_the_purpose_survives PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_a_missing_purpose_section_returns_none PASSED [  5%]
tests/test_body.py::TestExtractPurpose::test_the_next_heading_ends_the_purpose_section PASSED [  5%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_title_is_the_h1 PASSED [  5%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_why_quotes_the_purpose_paragraph PASSED [  5%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_what_changed_lists_the_commit_subjects PASSED [  6%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_parts_appear_in_the_specified_order PASSED [  6%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_links_to_each_artifact_rather_than_embedding_it PASSED [  6%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_every_link_embeds_the_pushed_commit_sha PASSED [  6%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_uses_a_branch_name_as_the_ref PASSED [  6%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_points_at_the_base_branch PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_written_file_contains_no_carriage_return PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_returned_count_is_the_character_count PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_character_count_is_below_the_text_mode_byte_count PASSED [  6%]
tests/test_body.py::TestWriteBodyFile::test_the_reported_count_matches_the_bytes_on_disk PASSED [  6%]
tests/test_body.py::TestEvidenceStatesAbsence::test_a_gate_table_carries_one_row_per_gate PASSED [  7%]
tests/test_body.py::TestEvidenceStatesAbsence::test_the_recorded_line_replaces_the_table_it_does_not_empty_the_section PASSED [  7%]
tests/test_body.py::TestEvidenceStatesAbsence::test_an_overridden_failure_is_stated_never_asserted_green PASSED [  7%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_no_artifacts_produces_no_invented_link PASSED [  7%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_the_body_never_editorialises_a_missing_artifact PASSED [  7%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_only_the_artifacts_present_are_linked PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_a_plain_rule_is_a_target PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_several_targets_on_one_rule_are_all_read PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_prerequisites_are_not_targets PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_a_double_colon_rule_is_a_target PASSED [  7%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS := -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ::= -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ?= -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS += -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS = -race] PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_a_recipe_line_is_never_a_target PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_pattern_and_variable_targets_are_ignored PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_special_targets_are_ignored PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_a_comment_does_not_create_a_target PASSED [  8%]
tests/test_buildsystem.py::TestReadingTargets::test_an_unreadable_makefile_yields_no_targets PASSED [  8%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_a_makefile_the_go_defaults_stand PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_a_makefile_with_both_targets_takes_over PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[GNUmakefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[Makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_each_gate_is_decided_on_its_own_target PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[GNUmakefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[Makefile] PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_gnumakefile_wins_over_makefile_as_make_would PASSED [  9%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_make_installed_the_makefile_is_not_used PASSED [ 10%]
tests/test_check.py::test_run_check_evaluates_every_gate_even_after_a_failure PASSED [ 10%]
tests/test_check.py::test_report_passes_only_when_every_required_gate_passed_or_skipped PASSED [ 10%]
tests/test_check.py::test_report_fails_when_a_required_gate_failed PASSED [ 10%]
tests/test_check.py::test_optional_gate_failure_does_not_fail_the_check PASSED [ 10%]
tests/test_check.py::test_warning_status_never_affects_the_verdict PASSED [ 10%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[passed] PASSED [ 10%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[failed] PASSED [ 10%]
tests/test_check.py::test_run_check_refuses_a_directory_that_does_not_exist PASSED [ 10%]
tests/test_check.py::test_run_check_refuses_a_directory_without_go_mod PASSED [ 10%]
tests/test_check.py::test_run_check_refuses_before_running_any_gate PASSED [ 11%]
tests/test_check.py::test_finds_poc_directories_with_go_files_but_no_go_mod PASSED [ 11%]
tests/test_check.py::test_ignores_poc_directories_that_have_a_go_mod PASSED [ 11%]
tests/test_check.py::test_ignores_poc_directories_with_no_go_files PASSED [ 11%]
tests/test_check.py::test_returns_empty_list_when_there_is_no_poc_directory PASSED [ 11%]
tests/test_check.py::test_poc_warnings_appear_in_the_report_without_failing_it PASSED [ 11%]
tests/test_cli.py::test_check_returns_zero_when_every_gate_passes PASSED [ 11%]
tests/test_cli.py::test_check_returns_one_when_a_gate_fails PASSED       [ 11%]
tests/test_cli.py::test_check_json_flag_emits_parseable_json PASSED      [ 11%]
tests/test_cli.py::test_check_reports_a_missing_directory_without_a_traceback PASSED [ 11%]
tests/test_cli.py::test_check_reports_a_directory_without_go_mod_clearly PASSED [ 12%]
tests/test_cli.py::test_check_defaults_to_the_current_directory PASSED   [ 12%]
tests/test_cli.py::test_no_race_flag_disables_the_race_gate PASSED       [ 12%]
tests/test_cli.py::test_the_cli_runs_as_a_module_without_exploding PASSED [ 12%]
tests/test_cli.py::test_every_subcommand_is_reachable_in_a_real_process PASSED [ 12%]
tests/test_cli_poc.py::test_poc_list_on_an_empty_repo_succeeds PASSED    [ 12%]
tests/test_cli_poc.py::test_poc_list_shows_each_spike PASSED             [ 12%]
tests/test_cli_poc.py::test_poc_list_flags_a_spike_missing_go_mod PASSED [ 12%]
tests/test_cli_poc.py::test_poc_list_json_is_machine_readable PASSED     [ 12%]
tests/test_cli_poc.py::test_poc_new_rejects_a_bad_slug_as_a_usage_error PASSED [ 12%]
tests/test_cli_poc.py::test_poc_new_bad_slug_writes_one_line_to_stderr PASSED [ 13%]
tests/test_cli_poc.py::test_poc_new_refuses_an_existing_spike_as_a_usage_error PASSED [ 13%]
tests/test_cli_poc.py::test_poc_run_on_a_missing_spike_is_a_usage_error PASSED [ 13%]
tests/test_cli_poc.py::test_poc_run_on_a_spike_without_go_mod_is_a_usage_error PASSED [ 13%]
tests/test_cli_poc.py::test_a_crashed_spike_makes_the_command_exit_non_zero PASSED [ 13%]
tests/test_cli_poc.py::test_every_real_verdict_makes_the_command_exit_zero PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_no_source_is_a_usage_error PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_two_sources_is_a_usage_error PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_working_is_accepted PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_staged_is_accepted PASSED [ 13%]
tests/test_cli_review.py::TestDiffSourceSelection::test_branch_is_accepted PASSED [ 14%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--runs-0] PASSED [ 14%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--concurrency-0] PASSED [ 14%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_negative_window_is_refused PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_complete_review_exits_zero_even_with_findings PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_partial_review_exits_non_zero PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_no_usable_response_fails_loudly PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_every_model_unavailable_fails_rather_than_reporting_nothing PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_git_failure_is_not_reported_as_a_clean_review PASSED [ 14%]
tests/test_cli_review.py::TestExitCodes::test_a_blocked_toolchain_returns_check_failed_without_reviewing PASSED [ 14%]
tests/test_cli_review.py::TestChannels::test_the_report_goes_to_stdout PASSED [ 15%]
tests/test_cli_review.py::TestChannels::test_failure_detail_goes_to_stderr_only PASSED [ 15%]
tests/test_cli_review.py::TestChannels::test_json_output_is_parseable PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_each_model_is_asked_the_requested_number_of_times PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_custom_instructions_are_disabled PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_no_named_mcp_server_is_disabled_by_default PASSED [ 15%]
tests/test_cli_review.py::TestCommandsIssued::test_the_prompt_carries_the_whole_diff_in_one_call PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_the_module_can_be_executed PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_appears_in_the_top_level_help PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_help_runs_without_error PASSED [ 15%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_without_a_source_exits_two_and_explains PASSED [ 16%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_with_two_sources_exits_two_and_explains PASSED [ 16%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_a_refused_setting_does_not_produce_a_traceback PASSED [ 16%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_nothing_is_defined_below_the_main_guard PASSED [ 16%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_default_models_are_the_two_that_scored_above_ninety_percent PASSED [ 16%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_help_text_names_the_models_it_actually_uses PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_ship_builds_its_gates_without_raising PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_still_builds_gates PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_five_gates_are_passed_through PASSED [ 16%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_disables_only_the_race_gate PASSED [ 16%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_defaults_to_main PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_is_forwarded PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_phase_and_title_are_forwarded PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_push_defaults_off_and_is_forwarded_when_given PASSED [ 17%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_allow_failing_checks_is_forwarded PASSED [ 17%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_a_refusal_exits_one_and_prints_to_stderr PASSED [ 17%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_failing_check_exits_non_zero PASSED [ 17%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_run_says_so_on_stderr PASSED [ 17%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_a_created_pr_says_opened PASSED [ 17%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_an_updated_pr_says_updated PASSED [ 17%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_the_commit_is_abbreviated_not_printed_whole PASSED [ 18%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_appears_in_the_top_level_help PASSED [ 18%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_help_runs_without_error PASSED [ 18%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_outside_a_phase_branch_refuses_without_a_traceback PASSED [ 18%]
tests/test_cli_state.py::test_init_creates_the_project PASSED            [ 18%]
tests/test_cli_state.py::test_init_starts_the_project_with_no_approvals PASSED [ 18%]
tests/test_cli_state.py::test_init_does_not_claim_a_phase PASSED         [ 18%]
tests/test_cli_state.py::test_init_refuses_to_overwrite_an_existing_project PASSED [ 18%]
tests/test_cli_state.py::test_init_force_overwrites_deliberately PASSED  [ 18%]
tests/test_cli_state.py::test_status_reports_the_current_phase PASSED    [ 18%]
tests/test_cli_state.py::test_status_answers_without_any_state_file_at_all PASSED [ 19%]
tests/test_cli_state.py::test_status_exits_zero_when_state_is_corrupt PASSED [ 19%]
tests/test_cli_state.py::test_status_exits_zero_whatever_it_finds PASSED [ 19%]
tests/test_cli_state.py::test_status_json_is_machine_readable PASSED     [ 19%]
tests/test_cli_state.py::test_status_json_still_emits_on_corrupt_state PASSED [ 19%]
tests/test_cli_state.py::test_status_reports_every_problem_at_once PASSED [ 19%]
tests/test_cli_state.py::test_status_reports_unsaved_work PASSED         [ 19%]
tests/test_cli_state.py::test_status_shows_the_most_recent_event PASSED  [ 19%]
tests/test_cli_state.py::test_status_sweeps_leftover_temp_files_and_says_so PASSED [ 19%]
tests/test_cli_state.py::test_the_sweep_never_touches_unsaved_work PASSED [ 19%]
tests/test_cli_state.py::test_status_works_while_the_event_log_lock_is_held PASSED [ 20%]
tests/test_cli_state.py::test_no_project_wide_lock_file_is_created PASSED [ 20%]
tests/test_cli_state.py::test_init_runs_as_a_real_process PASSED         [ 20%]
tests/test_cli_state.py::test_the_atom_package_imports_cleanly PASSED    [ 20%]
tests/test_cli_state.py::test_status_runs_as_a_subprocess_and_exits_zero PASSED [ 20%]
tests/test_cli_state.py::test_status_json_output_is_parseable_from_a_subprocess PASSED [ 20%]
tests/test_cli_state.py::test_status_runs_in_a_directory_that_is_not_a_project PASSED [ 20%]
tests/test_cli_state.py::test_status_runs_with_no_state_file_present PASSED [ 20%]
tests/test_cli_state.py::test_status_exits_zero_as_a_real_process_when_corrupt PASSED [ 20%]
tests/test_cli_state.py::test_init_that_cannot_write_is_fatal_and_says_how_to_recover PASSED [ 20%]
tests/test_cli_state.py::test_init_does_not_promise_safety_it_cannot_deliver PASSED [ 21%]
tests/test_cli_state.py::test_status_reports_a_corrupt_config_separately_from_state PASSED [ 21%]
tests/test_cli_state.py::test_status_counts_damaged_event_log_lines PASSED [ 21%]
tests/test_cli_state.py::test_status_tells_the_developer_how_to_recover_from_corruption PASSED [ 21%]
tests/test_cli_state.py::test_status_prints_each_problem_exactly_once PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[source] PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[packaged] PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[source] PASSED [ 21%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[packaged] PASSED [ 21%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[source] PASSED [ 21%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[packaged] PASSED [ 22%]
tests/test_comment_guidance.py::test_the_two_tdd_skill_copies_stay_identical PASSED [ 22%]
tests/test_comment_guidance.py::test_the_review_rule_names_a_missing_comment_as_the_defect PASSED [ 22%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.RUNNER_ERROR] PASSED [ 22%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.TIMED_OUT] PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_staged_source_asks_git_for_the_index PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_working_source_asks_git_for_unstaged_changes PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_branch_source_diffs_against_the_merge_base PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_selecting_no_source_names_all_three_options PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_selecting_two_sources_is_an_error_rather_than_a_precedence_rule PASSED [ 22%]
tests/test_diff.py::TestSourceSelection::test_the_chosen_source_is_recorded_on_the_request PASSED [ 23%]
tests/test_diff.py::TestCapture::test_capture_issues_exactly_one_git_command PASSED [ 23%]
tests/test_diff.py::TestCapture::test_a_multi_file_diff_is_captured_whole PASSED [ 23%]
tests/test_diff.py::TestCapture::test_an_empty_diff_is_not_an_error PASSED [ 23%]
tests/test_diff.py::TestCapture::test_a_whitespace_only_diff_counts_as_empty PASSED [ 23%]
tests/test_diff.py::TestCapture::test_nothing_is_truncated_however_large_the_diff PASSED [ 23%]
tests/test_diff.py::TestGitFailure::test_a_failed_git_command_is_reported_not_swallowed PASSED [ 23%]
tests/test_diff.py::TestGitFailure::test_a_missing_git_is_reported_clearly PASSED [ 23%]
tests/test_diff.py::TestGitFailure::test_a_timed_out_git_command_is_reported PASSED [ 23%]
tests/test_diff.py::TestSize::test_changed_lines_count_additions_and_removals PASSED [ 23%]
tests/test_diff.py::TestSize::test_file_headers_are_not_counted_as_changed_lines PASSED [ 24%]
tests/test_diff.py::TestSize::test_context_lines_are_not_counted PASSED  [ 24%]
tests/test_diff.py::TestSize::test_file_count_follows_the_b_side_of_a_rename PASSED [ 24%]
tests/test_diff.py::TestSize::test_a_file_is_counted_once_however_many_hunks_it_has PASSED [ 24%]
tests/test_diff.py::TestSize::test_size_reads_as_a_sentence_for_the_report PASSED [ 24%]
tests/test_diff.py::TestSize::test_size_description_is_singular_for_one_file PASSED [ 24%]
tests/test_diff.py::TestSize::test_an_empty_diff_describes_itself_as_empty PASSED [ 24%]
tests/test_diff.py::TestDescription::test_staged_describes_itself PASSED [ 24%]
tests/test_diff.py::TestDescription::test_working_describes_itself PASSED [ 24%]
tests/test_diff.py::TestDescription::test_branch_names_the_base_ref PASSED [ 24%]
tests/test_diff.py::TestDescription::test_a_path_without_an_a_or_b_prefix_is_used_as_is PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_removing_a_markdown_rule_still_counts_as_a_changed_line PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_added_content_cannot_invent_a_file PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_git_header_does_not_start_a_new_file PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_hunk_header_is_counted_as_a_change PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_several_files_each_reset_the_header_state PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_a_deleted_file_is_named_by_its_old_path PASSED [ 25%]
tests/test_diff.py::TestHeaderConfusion::test_a_no_newline_marker_is_not_a_changed_line PASSED [ 25%]
tests/test_eventlog.py::test_appending_then_reading_round_trips PASSED   [ 25%]
tests/test_eventlog.py::test_appending_creates_the_log_and_its_directory PASSED [ 25%]
tests/test_eventlog.py::test_each_event_is_one_line PASSED               [ 26%]
tests/test_eventlog.py::test_appending_never_rewrites_existing_content PASSED [ 26%]
tests/test_eventlog.py::test_a_timestamp_is_recorded_for_each_event PASSED [ 26%]
tests/test_eventlog.py::test_the_caller_cannot_be_clobbered_by_the_timestamp PASSED [ 26%]
tests/test_eventlog.py::test_appending_uses_a_separate_lock_file PASSED  [ 26%]
tests/test_eventlog.py::test_a_truncated_final_line_is_skipped_with_a_warning PASSED [ 26%]
tests/test_eventlog.py::test_a_corrupt_line_in_the_middle_does_not_hide_later_ones PASSED [ 26%]
tests/test_eventlog.py::test_a_corrupt_line_reports_its_line_number PASSED [ 26%]
tests/test_eventlog.py::test_a_json_array_line_is_treated_as_damaged PASSED [ 26%]
tests/test_eventlog.py::test_blank_lines_are_ignored_rather_than_reported PASSED [ 26%]
tests/test_eventlog.py::test_reading_a_log_that_does_not_exist_yet_is_not_an_error PASSED [ 27%]
tests/test_eventlog.py::test_reading_does_not_take_the_lock PASSED       [ 27%]
tests/test_eventlog.py::test_concurrent_appends_from_real_processes_lose_nothing PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_plain_json_needs_no_stripping PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_is_stripped PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_is_stripped PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_surrounding_whitespace_is_ignored PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_wins_over_an_earlier_unlabelled_one PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_still_works_when_it_is_the_only_one PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly PASSED [ 27%]
tests/test_extract.py::TestFenceStripping::test_a_fenced_response_extracts_normally PASSED [ 28%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_around_bare_json_is_a_failure_not_a_rescue PASSED [ 28%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_outside_a_fence_is_still_extracted PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_a_well_formed_response_yields_findings PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_an_empty_array_is_a_clean_review_not_a_failure PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_a_non_array_payload_is_rejected PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_unparseable_text_is_rejected PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[file] PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[line] PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[severity] PASSED [ 28%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[message] PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_severity_outside_the_allowed_set_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_all_four_allowed_severities_are_accepted PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_string_line_number_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_boolean_line_number_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_a_line_number_below_one_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_line_zero_is_rejected PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_line_one_is_accepted PASSED [ 29%]
tests/test_extract.py::TestSchemaValidation::test_an_element_that_is_not_an_object_is_rejected PASSED [ 29%]
tests/test_extract.py::TestFileGuard::test_a_finding_naming_a_file_outside_the_diff_is_rejected PASSED [ 29%]
tests/test_extract.py::TestFileGuard::test_rejecting_one_finding_does_not_discard_its_siblings PASSED [ 30%]
tests/test_extract.py::TestFileGuard::test_the_guard_is_skipped_when_no_file_list_is_given PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_records_which_model_and_which_run PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_keeps_an_excerpt_of_what_was_returned PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_the_excerpt_is_bounded_so_a_huge_reply_cannot_flood_the_report PASSED [ 30%]
tests/test_extract.py::TestFailuresAreLoud::test_an_unusable_run_is_not_silently_ignored PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_findings_carry_their_model_and_run PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_one_bad_run_does_not_lose_the_good_ones PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_a_report_knows_whether_anything_failed PASSED [ 30%]
tests/test_extract.py::TestAcrossRuns::test_duplicate_findings_are_preserved_for_the_merge_step_to_count PASSED [ 30%]
tests/test_filelock.py::test_lock_is_exclusive_across_real_processes PASSED [ 31%]
tests/test_filelock.py::test_lock_can_be_taken_and_released PASSED       [ 31%]
tests/test_filelock.py::test_lock_creates_the_lock_file_when_absent PASSED [ 31%]
tests/test_filelock.py::test_lock_file_is_separate_from_the_file_being_appended PASSED [ 31%]
tests/test_filelock.py::test_lock_is_released_when_the_body_raises PASSED [ 31%]
tests/test_filelock.py::test_lock_times_out_when_already_held PASSED     [ 31%]
tests/test_filelock.py::test_timeout_message_explains_how_to_recover PASSED [ 31%]
tests/test_filelock.py::test_lock_does_not_truncate_an_existing_lock_file PASSED [ 31%]
tests/test_gates.py::test_runner_error_is_failed_gate_evidence PASSED    [ 31%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[build] PASSED [ 31%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[vet] PASSED [ 32%]
tests/test_gates.py::test_build_gate_fails_with_stderr_details_when_build_exits_nonzero PASSED [ 32%]
tests/test_gates.py::test_vet_gate_fails_when_vet_exits_nonzero PASSED   [ 32%]
tests/test_gates.py::test_format_gate_fails_on_printed_filenames_despite_zero_exit_code PASSED [ 32%]
tests/test_gates.py::test_format_gate_passes_when_gofmt_prints_nothing PASSED [ 32%]
tests/test_gates.py::test_format_gate_names_unformatted_files_in_summary PASSED [ 32%]
tests/test_gates.py::test_format_gate_ignores_blank_lines_in_gofmt_output PASSED [ 32%]
tests/test_gates.py::test_format_gate_fails_when_gofmt_itself_errors PASSED [ 32%]
tests/test_gates.py::test_test_gate_passes_when_go_test_exits_zero PASSED [ 32%]
tests/test_gates.py::test_test_gate_fails_and_preserves_raw_output PASSED [ 32%]
tests/test_gates.py::test_test_gate_skips_when_go_reports_no_test_files PASSED [ 33%]
tests/test_gates.py::test_test_gate_failure_wins_over_no_test_files_marker PASSED [ 33%]
tests/test_gates.py::test_race_gate_runs_go_test_with_race_flag PASSED   [ 33%]
tests/test_gates.py::test_race_gate_is_skipped_when_disabled PASSED      [ 33%]
tests/test_gates.py::test_gate_fails_and_names_tool_when_executable_missing PASSED [ 33%]
tests/test_gates.py::test_test_gate_skips_when_download_chatter_accompanies_no_test_files PASSED [ 33%]
tests/test_gates.py::test_race_gate_skips_when_no_packages_have_tests PASSED [ 33%]
tests/test_gates.py::test_race_gate_still_passes_when_tests_actually_ran PASSED [ 33%]
tests/test_gates.py::test_format_gate_ignores_files_belonging_to_a_nested_module PASSED [ 33%]
tests/test_gates.py::test_format_gate_still_reports_unformatted_files_in_the_root_module PASSED [ 33%]
tests/test_gates.py::test_format_gate_does_not_fail_for_line_ending_only_differences PASSED [ 34%]
tests/test_gates.py::test_format_gate_names_line_endings_as_the_cause PASSED [ 34%]
tests/test_gates.py::test_format_gate_still_fails_when_a_crlf_file_is_also_badly_formatted PASSED [ 34%]
tests/test_gates.py::test_format_gate_reports_a_genuine_problem_even_beside_a_line_ending_one PASSED [ 34%]
tests/test_gates.py::test_default_gates_covers_all_five_signals_in_order PASSED [ 34%]
tests/test_gates.py::test_default_gates_can_disable_race_without_removing_it PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[staticcheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[errcheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[govulncheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[staticcheck] PASSED [ 34%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[errcheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[govulncheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[staticcheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[errcheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[govulncheck] PASSED [ 35%]
tests/test_gates.py::test_advisory_gates_returns_all_optional_review_signals PASSED [ 35%]
tests/test_gates_makefile.py::TestBuildGate::test_a_build_target_is_preferred_over_go_build PASSED [ 35%]
tests/test_gates_makefile.py::TestBuildGate::test_without_a_build_target_go_build_still_runs PASSED [ 35%]
tests/test_gates_makefile.py::TestBuildGate::test_a_failing_make_target_fails_the_gate PASSED [ 35%]
tests/test_gates_makefile.py::TestTestGate::test_a_test_target_is_preferred_over_go_test PASSED [ 35%]
tests/test_gates_makefile.py::TestTestGate::test_a_failing_make_target_fails_the_gate PASSED [ 36%]
tests/test_gates_makefile.py::TestTestGate::test_no_test_files_is_still_reported_as_skipped_through_make PASSED [ 36%]
tests/test_gates_makefile.py::TestTestGate::test_a_real_test_run_through_make_is_not_downgraded PASSED [ 36%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_format_gate_ignores_a_makefile PASSED [ 36%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_vet_gate_ignores_a_makefile PASSED [ 36%]
tests/test_gates_makefile.py::test_a_makefile_is_ignored_when_make_is_not_installed PASSED [ 36%]
tests/test_index.py::test_lists_every_spike PASSED                       [ 36%]
tests/test_index.py::test_ignores_nested_directories PASSED              [ 36%]
tests/test_index.py::test_reads_the_question_from_the_readme PASSED      [ 36%]
tests/test_index.py::test_question_is_none_when_there_is_no_readme PASSED [ 36%]
tests/test_index.py::test_question_is_none_when_the_readme_has_no_question_section PASSED [ 37%]
tests/test_index.py::test_reports_a_spike_that_has_a_go_mod PASSED       [ 37%]
tests/test_index.py::test_flags_a_spike_missing_its_go_mod PASSED        [ 37%]
tests/test_index.py::test_missing_poc_root_is_an_empty_list_not_an_error PASSED [ 37%]
tests/test_index.py::test_empty_poc_root_is_an_empty_list PASSED         [ 37%]
tests/test_index.py::test_ignores_loose_files_in_poc_root PASSED         [ 37%]
tests/test_index.py::test_results_are_sorted_for_stable_output PASSED    [ 37%]
tests/test_index.py::test_multiline_question_is_collapsed_to_one_line PASSED [ 37%]
tests/test_index.py::test_question_skips_the_blockquote_guidance PASSED  [ 37%]
tests/test_invoke.py::test_runner_error_is_not_usable_model_evidence PASSED [ 37%]
tests/test_invoke.py::TestMandatoryFlags::test_uses_silent_and_never_output_format_json PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_custom_instructions PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_builtin_mcp_servers PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_names_no_vendor_specific_mcp_servers_by_default PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_extra_mcp_servers_can_be_disabled_by_the_caller PASSED [ 38%]
tests/test_invoke.py::TestMandatoryFlags::test_carries_the_prompt_and_the_model PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_probes_every_model PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_a_rejected_model_is_reported_unavailable_with_its_reason PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_no_review_call_happens_before_every_probe_has_run PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_an_unavailable_model_is_never_asked_to_review PASSED [ 38%]
tests/test_invoke.py::TestAvailabilityProbing::test_probing_no_models_returns_nothing_rather_than_failing PASSED [ 39%]
tests/test_invoke.py::TestAvailabilityProbing::test_when_no_model_is_available_the_review_fails_loudly PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_calls_each_model_three_times_by_default PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_run_count_is_overridable PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_runs_of_one_model_are_byte_identical_calls PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_every_model_gets_the_same_number_of_runs PASSED [ 39%]
tests/test_invoke.py::TestRepetition::test_runs_are_numbered_from_one PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_timeout_is_a_recorded_outcome_not_a_raise PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_nonzero_exit_is_recorded_as_a_failed_run PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_one_failing_run_does_not_stop_the_others PASSED [ 39%]
tests/test_invoke.py::TestPerRunOutcomes::test_response_text_is_kept_for_completed_runs PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_a_complete_review_is_not_partial PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_one_failed_run_out_of_six_makes_the_whole_review_partial PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_participation_states_completed_over_requested_per_model PASSED [ 40%]
tests/test_invoke.py::TestPartialReviews::test_usable_responses_are_offered_even_when_the_review_is_partial PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_default_concurrency_is_the_measured_four PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_never_exceeds_the_concurrency_limit PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_calls_genuinely_overlap_rather_than_merely_staying_under_the_limit PASSED [ 40%]
tests/test_invoke.py::TestConcurrency::test_all_runs_complete_even_when_they_outnumber_the_workers PASSED [ 40%]
tests/test_invoke.py::TestReportingWhatFailed::test_unavailable_models_are_listed_with_their_reasons PASSED [ 40%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_missing_cli_is_reported_as_tool_missing_not_as_a_refusal PASSED [ 41%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_failure_still_gets_a_reason PASSED [ 41%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_timeout_is_named_by_its_outcome PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_runs_is_rejected_rather_than_reported_as_complete PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_negative_runs_is_rejected PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_concurrency_is_rejected_rather_than_silently_corrected PASSED [ 41%]
tests/test_invoke.py::TestNonsensicalSettings::test_no_models_at_all_is_rejected PASSED [ 41%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_review_command_does_not_contain_the_prompt PASSED [ 41%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_command_length_stays_flat_as_the_prompt_grows PASSED [ 41%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_the_prompt_reaches_the_runner_as_stdin PASSED [ 41%]
tests/test_merge.py::TestGroupingByProximity::test_the_default_window_is_three_lines PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_identical_lines_merge PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_nearby_lines_merge PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_lines_beyond_the_window_stay_separate PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_the_window_is_configurable PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_the_same_line_in_different_files_never_merges PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_a_group_never_spans_more_than_the_window PASSED [ 42%]
tests/test_merge.py::TestGroupingByProximity::test_grouping_does_not_depend_on_the_order_findings_arrive_in PASSED [ 42%]
tests/test_merge.py::TestNothingIsDiscarded::test_every_message_survives_the_merge PASSED [ 42%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_is_attributed_to_its_model_and_run PASSED [ 42%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_keeps_the_line_it_was_reported_at PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_a_merged_finding_names_the_models_that_reported_it PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_agreement_counts_how_many_runs_of_each_model_reported_it PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_one_run_reporting_a_line_twice_counts_once PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_a_single_model_finding_is_reported_not_suppressed PASSED [ 43%]
tests/test_merge.py::TestAgreement::test_a_finding_from_both_models_is_marked_corroborated PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_different_lines_of_one_group_is_not_corroboration PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_the_same_line_is_still_corroboration PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_agreement_on_one_line_survives_an_unrelated_line_joining_the_group PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_one_model_reporting_twice_on_a_line_is_not_corroboration PASSED [ 43%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_model_count_still_reports_every_model_in_the_group PASSED [ 44%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_a_single_line_group_from_two_models_is_unaffected PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_the_same_defect_at_adjacent_lines_is_reported_as_nearby PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_same_line_agreement_is_not_also_reported_as_nearby PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_agreement_on_one_line_wins_over_a_nearby_report PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_one_model_across_several_lines_is_neither_signal PASSED [ 44%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_a_lone_finding_is_neither_signal PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_disagreeing_severities_are_all_preserved PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_severity_is_not_collapsed_into_one_verdict PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_agreement_on_severity_is_not_reported_as_disagreement PASSED [ 44%]
tests/test_merge.py::TestSeverity::test_the_highest_claimed_severity_is_available_for_ordering PASSED [ 45%]
tests/test_merge.py::TestOrdering::test_findings_are_ordered_by_highest_severity PASSED [ 45%]
tests/test_merge.py::TestOrdering::test_one_model_calling_it_critical_lifts_the_whole_finding PASSED [ 45%]
tests/test_merge.py::TestOrdering::test_equal_severities_are_ordered_predictably PASSED [ 45%]
tests/test_merge.py::TestKnownLimits::test_drift_lets_a_group_reach_further_than_the_window PASSED [ 45%]
tests/test_merge.py::TestEdges::test_severity_ordering_depends_on_the_allowed_list_staying_ordered PASSED [ 45%]
tests/test_merge.py::TestEdges::test_agreement_renders_as_the_fraction_a_report_shows PASSED [ 45%]
tests/test_merge.py::TestEdges::test_no_findings_merge_to_nothing PASSED [ 45%]
tests/test_merge.py::TestEdges::test_a_model_absent_from_the_run_counts_is_rejected PASSED [ 45%]
tests/test_merge.py::TestEdges::test_a_negative_window_is_rejected PASSED [ 45%]
tests/test_merge.py::TestEdges::test_a_zero_window_means_exact_line_matching PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_with_no_runs_cannot_have_reported_anything PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_that_completed_no_runs_is_allowed_to_report_nothing PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_negative_run_count_is_rejected PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_more_reporting_runs_than_runs_total_is_rejected PASSED [ 46%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_an_unrecognised_severity_names_what_is_allowed PASSED [ 46%]
tests/test_onboarding.py::test_init_records_the_makefile_commands_it_will_actually_run PASSED [ 46%]
tests/test_onboarding.py::test_init_records_a_partial_makefile_one_gate_at_a_time PASSED [ 46%]
tests/test_onboarding.py::test_init_infers_module_and_installs_local_instructions PASSED [ 46%]
tests/test_onboarding.py::test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command PASSED [ 46%]
tests/test_onboarding.py::test_init_updates_existing_instructions_once PASSED [ 47%]
tests/test_onboarding.py::test_init_removes_legacy_external_atom_references PASSED [ 47%]
tests/test_onboarding.py::test_init_requires_module_when_go_mod_is_absent PASSED [ 47%]
tests/test_onboarding.py::test_init_ignores_only_generated_atom_runtime_files PASSED [ 47%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_and_updates_it_once PASSED [ 47%]
tests/test_onboarding.py::test_init_replaces_stale_atom_gitignore_block PASSED [ 47%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_newlines PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n# >>> Atom generated runtime files >>>\n.atom/second.json\n# <<< Atom generated runtime files <<<\n] PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n] PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n.atom/first.json\n] PASSED [ 47%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n# >>> Atom generated runtime files >>>\n] PASSED [ 48%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/-\n\n] PASSED [ 48%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/\n\n-] PASSED [ 48%]
tests/test_onboarding.py::test_gitignore_update_keeps_original_when_atomic_replace_fails PASSED [ 48%]
tests/test_onboarding.py::test_init_reports_an_unreadable_gitignore_without_a_traceback PASSED [ 48%]
tests/test_phases.py::test_a_well_formed_phase_directory_is_recognised PASSED [ 48%]
tests/test_phases.py::test_a_single_digit_phase_number_is_not_a_phase_directory PASSED [ 48%]
tests/test_phases.py::test_an_uppercase_slug_is_not_a_phase_directory PASSED [ 48%]
tests/test_phases.py::test_a_directory_merely_containing_a_phase_name_is_not_one PASSED [ 48%]
tests/test_phases.py::test_a_file_named_like_a_phase_directory_is_not_one PASSED [ 48%]
tests/test_phases.py::test_a_non_phase_directory_is_ignored PASSED       [ 49%]
tests/test_phases.py::test_a_non_phase_directory_produces_no_problem PASSED [ 49%]
tests/test_phases.py::test_the_phase_plan_document_beside_the_phases_is_not_a_phase PASSED [ 49%]
tests/test_phases.py::test_phases_are_ordered_lexically PASSED           [ 49%]
tests/test_phases.py::test_the_two_digit_prefix_makes_lexical_order_numeric PASSED [ 49%]
tests/test_phases.py::test_phase_ten_sorts_after_phase_nine PASSED       [ 49%]
tests/test_phases.py::test_a_phase_branch_names_the_current_phase PASSED [ 49%]
tests/test_phases.py::test_the_branch_wins_over_the_lexically_greatest_phase PASSED [ 49%]
tests/test_phases.py::test_main_falls_back_to_the_lexically_greatest_phase PASSED [ 49%]
tests/test_phases.py::test_a_detached_head_falls_back_to_the_lexically_greatest_phase PASSED [ 49%]
tests/test_phases.py::test_an_unrelated_branch_name_falls_back PASSED    [ 50%]
tests/test_phases.py::test_a_branch_that_cannot_be_read_falls_back PASSED [ 50%]
tests/test_phases.py::test_a_branch_naming_a_missing_phase_directory_is_still_current PASSED [ 50%]
tests/test_phases.py::test_a_phase_with_no_directory_is_marked_not_started PASSED [ 50%]
tests/test_phases.py::test_a_phase_with_no_directory_reports_every_artifact_absent PASSED [ 50%]
tests/test_phases.py::test_a_phase_with_no_directory_is_not_an_error PASSED [ 50%]
tests/test_phases.py::test_a_project_with_no_phases_has_no_current_phase PASSED [ 50%]
tests/test_phases.py::test_a_project_with_no_phases_is_not_an_error PASSED [ 50%]
tests/test_phases.py::test_an_absent_specs_directory_is_not_a_crash PASSED [ 50%]
tests/test_phases.py::test_creating_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 50%]
tests/test_phases.py::test_editing_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 51%]
tests/test_phases.py::test_the_current_phase_is_stable_when_every_directory_is_touched_in_reverse_order PASSED [ 51%]
tests/test_phases.py::test_the_required_artifacts_are_the_seven_named PASSED [ 51%]
tests/test_phases.py::test_an_unexpected_file_in_a_phase_directory_is_not_required PASSED [ 51%]
tests/test_phases.py::test_an_unexpected_file_does_not_appear_in_the_artifact_report PASSED [ 51%]
tests/test_phases.py::test_an_existing_artifact_is_present PASSED        [ 51%]
tests/test_phases.py::test_a_missing_artifact_is_absent PASSED           [ 51%]
tests/test_phases.py::test_an_empty_artifact_file_is_still_present PASSED [ 51%]
tests/test_phases.py::test_a_directory_named_like_an_artifact_is_not_present PASSED [ 51%]
tests/test_phases.py::test_the_artifact_report_has_exactly_two_states PASSED [ 51%]
tests/test_phases.py::test_a_one_byte_artifact_is_present PASSED         [ 52%]
tests/test_phases.py::test_a_document_with_no_headings_is_present PASSED [ 52%]
tests/test_phases.py::test_a_document_of_only_headings_is_present PASSED [ 52%]
tests/test_phases.py::test_no_artifact_but_the_poc_report_is_ever_opened PASSED [ 52%]
tests/test_phases.py::test_a_ran_poc_requires_a_brief PASSED             [ 52%]
tests/test_phases.py::test_a_skipped_poc_does_not_require_a_brief PASSED [ 52%]
tests/test_phases.py::test_a_skipped_phase_with_no_brief_is_complete PASSED [ 52%]
tests/test_phases.py::test_a_skipped_phase_requires_the_other_six PASSED [ 52%]
tests/test_phases.py::test_an_unrecognised_status_is_reported_as_a_problem PASSED [ 52%]
tests/test_phases.py::test_an_unrecognised_status_still_requires_the_brief PASSED [ 52%]
tests/test_phases.py::test_a_missing_status_field_is_reported_and_requires_the_brief PASSED [ 53%]
tests/test_phases.py::test_the_unrecognised_status_problem_names_the_value_it_found PASSED [ 53%]
tests/test_phases.py::test_an_absent_poc_report_makes_both_it_and_the_brief_absent PASSED [ 53%]
tests/test_phases.py::test_an_absent_poc_report_raises_no_problem_beyond_the_absences PASSED [ 53%]
tests/test_phases.py::test_a_phase_with_no_poc_report_still_requires_the_brief PASSED [ 53%]
tests/test_phases.py::test_the_status_vocabulary_is_exactly_two_tokens PASSED [ 53%]
tests/test_phases.py::test_a_status_containing_skipped_as_a_substring_is_not_skipped PASSED [ 53%]
tests/test_phases.py::test_the_prose_status_values_this_repo_used_before_are_not_accepted PASSED [ 53%]
tests/test_phases.py::test_status_matching_is_case_sensitive PASSED      [ 53%]
tests/test_phases.py::test_an_unquoted_status_is_recognised PASSED       [ 53%]
tests/test_phases.py::test_a_truncated_design_spec_is_reported_present PASSED [ 54%]
tests/test_phases.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 54%]
tests/test_phases.py::test_the_report_exposes_no_completeness_field PASSED [ 54%]
tests/test_phases.py::test_a_two_section_tdd_log_is_present PASSED       [ 54%]
tests/test_phases.py::test_the_real_phase_one_tdd_log_is_present PASSED  [ 54%]
tests/test_phases.py::test_the_real_repository_resolves_eight_phases PASSED [ 54%]
tests/test_phases.py::test_the_real_repository_orders_phases_one_through_eight PASSED [ 54%]
tests/test_phases.py::test_phases_one_through_five_have_every_required_artifact PASSED [ 54%]
tests/test_phases.py::test_the_real_phase_one_is_complete_despite_having_no_brief PASSED [ 54%]
tests/test_phases.py::test_the_real_phase_six_is_missing_exactly_its_unwritten_artifacts PASSED [ 54%]
tests/test_phases.py::test_a_real_detached_head_falls_back_to_lexical PASSED [ 55%]
tests/test_phases.py::test_a_real_phase_branch_resolves_to_its_directory PASSED [ 55%]
tests/test_phases.py::test_a_real_clone_preserves_phase_ordering PASSED  [ 55%]
tests/test_phases.py::test_a_problem_in_a_non_current_phase_is_still_reported PASSED [ 55%]
tests/test_phases.py::test_a_reported_problem_names_the_phase_it_came_from PASSED [ 55%]
tests/test_phases.py::test_problems_are_reported_in_phase_order PASSED   [ 55%]
tests/test_phases.py::test_the_current_phase_problem_is_reported_exactly_once PASSED [ 55%]
tests/test_phases.py::test_a_clean_tree_still_reports_no_problems PASSED [ 55%]
tests/test_plugin.py::test_the_plugin_manifest_declares_agent_plugins_1_0 PASSED [ 55%]
tests/test_plugin.py::test_the_plugin_manifest_uses_only_allowed_fields PASSED [ 55%]
tests/test_plugin.py::test_no_command_shares_a_name_with_a_skill PASSED  [ 56%]
tests/test_plugin.py::test_the_plugin_owns_the_atom_command_namespace PASSED [ 56%]
tests/test_plugin.py::test_no_command_shares_a_name_with_the_plugin PASSED [ 56%]
tests/test_plugin.py::test_the_atom_router_is_available_as_start PASSED  [ 56%]
tests/test_plugin.py::test_no_skill_shares_a_name_with_the_plugin PASSED [ 56%]
tests/test_plugin.py::test_the_plugin_exposes_exactly_the_compact_skill_names PASSED [ 56%]
tests/test_plugin.py::test_the_marketplace_lists_the_plugin_by_its_manifest_name PASSED [ 56%]
tests/test_plugin.py::test_the_marketplace_sources_the_repository_root PASSED [ 56%]
tests/test_plugin.py::test_every_atom_skill_directory_is_discoverable PASSED [ 56%]
tests/test_report.py::test_render_text_shows_every_gate_with_status_and_duration PASSED [ 56%]
tests/test_report.py::test_render_text_shows_details_for_failed_gates_only PASSED [ 57%]
tests/test_report.py::test_render_text_omits_details_for_passing_gates PASSED [ 57%]
tests/test_report.py::test_render_text_includes_warnings PASSED          [ 57%]
tests/test_report.py::test_render_text_without_colour_emits_no_escape_codes PASSED [ 57%]
tests/test_report.py::test_render_text_with_colour_emits_escape_codes PASSED [ 57%]
tests/test_report.py::test_render_json_is_valid_json_for_a_passing_report PASSED [ 57%]
tests/test_report.py::test_render_json_is_valid_json_for_a_failing_report PASSED [ 57%]
tests/test_report.py::test_render_json_includes_a_schema_version PASSED  [ 57%]
tests/test_report.py::test_render_json_includes_every_gate_with_its_evidence PASSED [ 57%]
tests/test_report.py::test_a_spike_that_answered_is_not_rendered_as_a_failed_stage PASSED [ 57%]
tests/test_report.py::test_an_answering_stage_says_it_answered_rather_than_that_it_exited PASSED [ 58%]
tests/test_report.py::test_a_refuted_spike_is_not_rendered_as_a_failure_either PASSED [ 58%]
tests/test_report.py::test_a_crashed_spike_is_still_rendered_as_a_failure PASSED [ 58%]
tests/test_report.py::test_a_crash_explains_that_exit_2_was_a_panic_not_a_verdict PASSED [ 58%]
tests/test_report.py::test_the_spike_output_is_shown_even_when_nothing_failed PASSED [ 58%]
tests/test_report.py::test_json_reports_no_failed_stage_for_a_spike_that_answered PASSED [ 58%]
tests/test_report.py::test_json_exposes_answered_separately_from_ran PASSED [ 58%]
tests/test_report.py::test_stderr_is_rendered_before_stdout PASSED       [ 58%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_names_every_model_that_took_part PASSED [ 58%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_states_how_many_runs_each_model_completed PASSED [ 58%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_describes_the_diff_that_was_reviewed PASSED [ 59%]
tests/test_review_output.py::TestWhatWasReviewed::test_a_model_that_failed_every_run_is_still_named PASSED [ 59%]
tests/test_review_output.py::TestWhatWasReviewed::test_an_unavailable_model_is_named_but_its_error_text_is_not_repeated PASSED [ 59%]
tests/test_review_output.py::TestWhatWasReviewed::test_responses_nobody_could_parse_are_reported PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_findings_are_grouped_under_their_file PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_a_single_line_finding_shows_that_line PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_a_finding_spanning_several_lines_shows_the_span PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_no_bare_finding_count_is_printed PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_every_model_message_is_shown_with_its_author PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_the_report_lists_toolchain_verdicts PASSED [ 59%]
tests/test_review_output.py::TestFindingPresentation::test_agreement_is_shown_as_a_fraction_per_model PASSED [ 60%]
tests/test_review_output.py::TestFindingPresentation::test_disagreement_about_severity_is_visible PASSED [ 60%]
tests/test_review_output.py::TestFindingPresentation::test_findings_appear_in_severity_order PASSED [ 60%]
tests/test_review_output.py::TestFindingPresentation::test_a_review_with_no_findings_says_so_explicitly PASSED [ 60%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_markdown PASSED [ 60%]
tests/test_review_output.py::TestPartialReviews::test_a_complete_review_is_not_marked_partial PASSED [ 60%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_json PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_json_is_valid_and_carries_a_schema_version PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_review_schema_version_records_the_corroboration_narrowing PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_other_reports_did_not_change_and_keep_their_version PASSED [ 60%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_findings_with_their_line_span PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_agreement_with_both_halves_of_the_fraction PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_keeps_every_attributed_message PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_names_models_that_produced_nothing PASSED [ 61%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_unparseable_responses PASSED [ 61%]
tests/test_review_output.py::TestChannelSeparation::test_operational_problems_render_separately_from_the_report PASSED [ 61%]
tests/test_review_output.py::TestChannelSeparation::test_a_clean_review_produces_no_problem_output PASSED [ 61%]
tests/test_review_output.py::TestChannelSeparation::test_the_markdown_report_does_not_repeat_the_problem_text PASSED [ 61%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_it_is_partial_when_a_run_failed PASSED [ 61%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_with_every_run_answered_is_not_partial PASSED [ 61%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_when_no_model_produced_anything_usable PASSED [ 62%]
tests/test_review_output.py::TestReviewOutcome::test_a_review_that_ran_but_found_nothing_is_not_treated_as_unusable PASSED [ 62%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_a_completed_run_whose_reply_was_unreadable_yields_no_usable_response PASSED [ 62%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_such_a_review_does_not_exit_zero PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_left_out_of_the_denominator PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_finding_both_readable_runs_reported_is_not_shown_as_a_dissent PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_completed_without_answering_makes_the_review_partial PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_notice_counts_the_run_that_could_not_be_read PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_reports_answered_runs_alongside_completed_ones PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_that_partly_parsed_still_counts_as_an_answer PASSED [ 62%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_clean_review_still_counts_every_run_and_is_not_partial PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_model_whose_every_reply_was_unreadable_renders_without_crashing PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_missing_run_is_still_partial PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[   \n\t ] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[I reviewed it and found nothing.] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_returned_nothing_is_named_in_the_report PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[file-guard only] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[schema-invalid] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[mixed] PASSED [ 63%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_not_named_twice PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_is_never_also_counted_as_overruled PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_despite_a_malformed_element_is_not_called_unreadable PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_is_not_called_a_review_that_produced_nothing PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_gets_its_own_heading PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_total_excludes_an_overruled_reply PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_banner_does_not_promise_stderr_detail PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_distinguishes_an_overruled_reply_from_an_unreadable_one PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_overruled_by_the_file_guard_does_not_make_the_review_partial PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_still_leaves_the_denominator PASSED [ 64%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unparseable_reply_is_still_silence PASSED [ 65%]
tests/test_review_output.py::TestTheReportSurvivesEveryConsoleEncoding::test_rendered_markdown_is_pure_ascii PASSED [ 65%]
tests/test_review_toolchain.py::test_empty_toolchain_placeholder_preserves_original_prompt_bytes PASSED [ 65%]
tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails PASSED [ 65%]
tests/test_review_toolchain.py::test_run_review_continues_with_no_exclusions_when_directory_is_not_go_module PASSED [ 65%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 65%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 65%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 65%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 65%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 65%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 66%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 66%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 66%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 66%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind PASSED [ 66%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 66%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 66%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 67%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 67%]
tests/test_scaffold.py::test_scaffold_creates_exactly_three_files PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_shells_out_to_go_mod_init PASSED   [ 67%]
tests/test_scaffold.py::test_scaffold_go_mod_pins_full_patch_version PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_module_path_is_namespaced_under_spike PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_rolls_back_completely_when_go_mod_init_fails PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_rollback_leaves_sibling_spikes_untouched PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_main_go_is_package_main_with_a_main_function PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_main_go_prints_the_question PASSED [ 67%]
tests/test_scaffold.py::test_scaffold_main_go_documents_the_exit_code_convention PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_readme_has_the_report_sections PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_readme_records_the_question PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[Json-Streaming] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json_streaming] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json streaming] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[-leading] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[trailing-] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[double--hyphen] PASSED [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[] PASSED    [ 68%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[../escape] PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json] PASSED   [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json-streaming] PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[http2-vs-http3] PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[a1] PASSED     [ 69%]
tests/test_scaffold.py::test_scaffold_slug_error_explains_the_rule PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_refuses_to_overwrite_an_existing_spike PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_does_not_modify_an_existing_spike_when_refusing PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_creates_poc_root_when_missing PASSED [ 69%]
tests/test_scaffold.py::test_scaffold_reports_every_file_it_created PASSED [ 69%]
tests/test_ship.py::TestGhPrecondition::test_a_missing_gh_is_an_unmet_precondition_not_a_late_failure PASSED [ 70%]
tests/test_ship.py::TestGhPrecondition::test_gh_is_verified_before_any_git_work_begins PASSED [ 70%]
tests/test_ship.py::TestGhPrecondition::test_the_missing_gh_message_names_the_install PASSED [ 70%]
tests/test_ship.py::TestBranchPreconditions::test_a_detached_head_has_nothing_to_ship_from PASSED [ 70%]
tests/test_ship.py::TestBranchPreconditions::test_shipping_the_base_branch_itself_is_refused PASSED [ 70%]
tests/test_ship.py::TestDirtyTree::test_a_dirty_working_tree_is_refused PASSED [ 70%]
tests/test_ship.py::TestDirtyTree::test_the_dirty_tree_refusal_lists_the_modified_files PASSED [ 70%]
tests/test_ship.py::TestDirtyTree::test_a_clean_tree_is_allowed_to_proceed PASSED [ 70%]
tests/test_ship.py::TestUpstream::test_a_branch_with_no_upstream_and_no_push_is_refused PASSED [ 70%]
tests/test_ship.py::TestUpstream::test_the_missing_upstream_refusal_prints_the_command_that_fixes_it PASSED [ 70%]
tests/test_ship.py::TestUpstream::test_the_push_flag_pushes_the_branch_and_sets_the_upstream PASSED [ 71%]
tests/test_ship.py::TestUpstream::test_the_push_is_a_git_command_never_gh PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_directory_is_derived_from_the_branch_name PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_flag_overrides_the_branch_derivation PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_phase_directory_is_refused_naming_the_path_it_tried PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_the_artifacts_are_the_files_the_phase_directory_holds PASSED [ 71%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_artifact_is_omitted_rather_than_described_as_pending PASSED [ 71%]
tests/test_ship.py::TestFreshCheck::test_the_check_runs_fresh_as_part_of_ship PASSED [ 71%]
tests/test_ship.py::TestFreshCheck::test_a_recorded_check_result_is_not_accepted PASSED [ 71%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_skips_the_gates PASSED [ 71%]
tests/test_ship.py::TestNotAGoModule::test_the_absent_module_is_recorded_as_an_absence_not_a_failure PASSED [ 72%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal PASSED [ 72%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag PASSED [ 72%]
tests/test_ship.py::TestNotAGoModule::test_the_evidence_section_states_the_absence_rather_than_omitting_it PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_body_carries_one_verdict_row_per_gate PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_verdict_table_is_bounded_at_five_rows PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_body_does_not_embed_the_gates_full_output PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_when_there_is_no_module_the_table_is_replaced_by_the_recorded_line PASSED [ 72%]
tests/test_ship.py::TestVerdictTable::test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty PASSED [ 72%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_check_refuses_to_open_or_update_the_pr PASSED [ 72%]
tests/test_ship.py::TestCheckRefusal::test_the_check_refusal_names_the_failing_gates PASSED [ 73%]
tests/test_ship.py::TestCheckRefusal::test_allow_failing_checks_overrides_the_refusal PASSED [ 73%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent PASSED [ 73%]
tests/test_ship.py::TestOverride::test_an_overridden_run_states_the_failure_in_the_body PASSED [ 73%]
tests/test_ship.py::TestOverride::test_an_overridden_body_never_asserts_green_while_red PASSED [ 73%]
tests/test_ship.py::TestOverride::test_an_overridden_run_still_exits_non_zero PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_is_summary_plus_links PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_never_embeds_an_artifacts_content PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_title_comes_from_the_design_specs_h1 PASSED [ 73%]
tests/test_ship.py::TestBody::test_a_title_flag_overrides_the_design_spec_h1 PASSED [ 73%]
tests/test_ship.py::TestBody::test_the_body_quotes_the_design_specs_purpose_paragraph PASSED [ 74%]
tests/test_ship.py::TestBody::test_what_changed_lists_the_commit_subjects_on_the_branch PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_artifact_links_point_at_the_pushed_commit_sha PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_uses_a_branch_name PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_points_at_the_base_branch PASSED [ 74%]
tests/test_ship.py::TestArtifactLinks::test_the_push_happens_before_the_body_is_assembled PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_body_file_contains_no_carriage_return PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_reported_size_is_the_character_count_not_the_byte_count PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_body_travels_by_body_file PASSED [ 74%]
tests/test_ship.py::TestBodyFile::test_the_body_flag_never_appears_in_the_argv PASSED [ 74%]
tests/test_ship.py::TestCreateAndUpdate::test_an_existing_pr_is_queried_before_any_create PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_is_treated_as_a_fallback_not_the_primary_signal PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_still_recovers_when_the_query_missed_it PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_on_a_branch_with_a_pr_updates_the_body PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_is_not_treated_as_an_error PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_ghs_error_text_is_passed_through_verbatim PASSED [ 75%]
tests/test_ship.py::TestCreateAndUpdate::test_every_gh_call_receives_empty_stdin PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_reuses_the_phase_one_to_three_exit_codes PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_an_unmet_precondition_exits_by_the_ordinary_failure_route PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_there_is_no_distinct_precondition_exit_code PASSED [ 75%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_never_issues_a_commit PASSED [ 76%]
tests/test_ship.py::TestExitCodesAndScope::test_no_git_commit_command_is_ever_run PASSED [ 76%]
tests/test_ship.py::TestOutcomeShape::test_a_clean_run_reports_succeeded PASSED [ 76%]
tests/test_ship.py::TestOutcomeShape::test_an_overridden_run_reports_not_succeeded PASSED [ 76%]
tests/test_ship.py::TestOutcomeShape::test_a_created_pr_reports_the_created_action_and_url PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_branch_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_status_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_a_failed_push_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_an_unresolvable_head_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_a_missing_origin_remote_is_refused PASSED [ 76%]
tests/test_ship.py::TestDegradedGit::test_a_failed_log_leaves_the_what_changed_section_empty_not_fatal PASSED [ 77%]
tests/test_ship.py::TestDegradedGit::test_a_failed_edit_is_refused_with_ghs_text PASSED [ 77%]
tests/test_ship.py::TestDegradedGit::test_a_create_failure_with_no_output_still_refuses PASSED [ 77%]
tests/test_ship.py::TestDegradedGit::test_a_create_success_without_a_url_falls_back_to_raw_stdout PASSED [ 77%]
tests/test_ship.py::TestPhaseResolutionEdges::test_a_direct_relative_path_resolves_the_phase PASSED [ 77%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_ambiguous_phase_name_is_refused PASSED [ 77%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_artifact_outside_the_repo_root_keeps_its_full_path PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_the_title_falls_back_to_the_branch_when_no_design_spec PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_design_spec_without_an_h1_falls_back_to_the_branch_title PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_an_ssh_remote_url_yields_the_owner_name_slug PASSED [ 77%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_with_empty_output_is_treated_as_no_existing_pr PASSED [ 78%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_that_prints_a_bare_url_is_accepted PASSED [ 78%]
tests/test_ship.py::TestDirtyTreeParsing::test_a_rename_lists_the_new_path PASSED [ 78%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_a_refused_ship_never_pushes_even_when_push_was_requested PASSED [ 78%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_the_check_runs_before_the_push_on_a_passing_run PASSED [ 78%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_an_overridden_failing_check_still_pushes PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_ahead_of_its_upstream_is_refused PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_the_refusal_says_how_far_ahead_and_how_to_fix_it PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_level_with_its_upstream_ships PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_being_ahead_is_irrelevant_when_push_was_requested PASSED [ 78%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_no_pr_is_opened_when_the_commit_is_not_on_the_remote PASSED [ 79%]
tests/test_spike.py::test_runner_error_cannot_confirm_a_spike PASSED     [ 79%]
tests/test_spike.py::test_runs_vet_then_build_then_execute PASSED        [ 79%]
tests/test_spike.py::test_reports_all_three_stages PASSED                [ 79%]
tests/test_spike.py::test_never_uses_go_run PASSED                       [ 79%]
tests/test_spike.py::test_build_failure_skips_execute PASSED             [ 79%]
tests/test_spike.py::test_vet_failure_skips_build_and_execute PASSED     [ 79%]
tests/test_spike.py::test_build_failure_is_reported_as_build_not_execute PASSED [ 79%]
tests/test_spike.py::test_execute_failure_is_reported_as_execute_not_build PASSED [ 79%]
tests/test_spike.py::test_captures_both_streams_from_the_spike PASSED    [ 79%]
tests/test_spike.py::test_keeps_stdout_from_a_spike_that_failed PASSED   [ 80%]
tests/test_spike.py::test_maps_exit_code_to_verdict[0-Verdict.CONFIRMED] PASSED [ 80%]
tests/test_spike.py::test_maps_exit_code_to_verdict[1-Verdict.REFUTED] PASSED [ 80%]
tests/test_spike.py::test_maps_exit_code_to_verdict[2-Verdict.INCONCLUSIVE] PASSED [ 80%]
tests/test_spike.py::test_inconclusive_survives_as_inconclusive PASSED   [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[3] PASSED [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[7] PASSED [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[42] PASSED [ 80%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[127] PASSED [ 80%]
tests/test_spike.py::test_no_verdict_when_the_spike_never_ran PASSED     [ 80%]
tests/test_spike.py::test_binary_is_not_left_in_the_spike_directory PASSED [ 81%]
tests/test_spike.py::test_binary_is_removed_even_when_the_spike_fails PASSED [ 81%]
tests/test_spike.py::test_build_output_path_is_outside_the_spike_directory PASSED [ 81%]
tests/test_spike.py::test_default_timeout_is_300_seconds PASSED          [ 81%]
tests/test_spike.py::test_timeout_is_overridable PASSED                  [ 81%]
tests/test_spike.py::test_timed_out_spike_has_no_verdict PASSED          [ 81%]
tests/test_spike.py::test_detects_a_command_spike_from_its_source PASSED [ 81%]
tests/test_spike.py::test_detects_a_library_spike_from_its_source PASSED [ 81%]
tests/test_spike.py::test_library_spike_runs_go_test_instead_of_a_binary PASSED [ 81%]
tests/test_spike.py::test_library_spike_still_builds_first PASSED        [ 81%]
tests/test_spike.py::test_library_spike_passing_tests_is_confirmed PASSED [ 82%]
tests/test_spike.py::test_library_spike_failing_tests_is_refuted PASSED  [ 82%]
tests/test_spike.py::test_library_spike_can_never_be_inconclusive PASSED [ 82%]
tests/test_spike.py::test_library_spike_does_not_build_a_binary PASSED   [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[0] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[1] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[2] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[42] PASSED [ 82%]
tests/test_spike.py::test_execute_stage_that_timed_out_did_not_produce_an_answer PASSED [ 82%]
tests/test_spike.py::test_skipped_execute_stage_did_not_produce_an_answer PASSED [ 82%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[vet] PASSED [ 83%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[build] PASSED [ 83%]
tests/test_spike.py::test_panicking_spike_is_crashed_not_inconclusive PASSED [ 83%]
tests/test_spike.py::test_deliberate_exit_2_is_still_inconclusive PASSED [ 83%]
tests/test_spike.py::test_crash_detection_needs_both_the_exit_code_and_the_signature PASSED [ 83%]
tests/test_spike.py::test_crash_detection_requires_a_stack_dump_not_just_the_word PASSED [ 83%]
tests/test_spike.py::test_a_crashed_spike_still_reports_its_exit_code PASSED [ 83%]
tests/test_spike.py::test_a_crashed_spike_did_not_answer PASSED          [ 83%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[0] PASSED [ 83%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[1] PASSED [ 83%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[2] PASSED [ 84%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[1] PASSED [ 84%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[2] PASSED [ 84%]
tests/test_spike.py::test_a_crashed_spike_does_have_a_failed_stage PASSED [ 84%]
tests/test_spike.py::test_a_build_failure_is_still_a_failed_stage PASSED [ 84%]
tests/test_spike.py::test_library_spike_panicking_is_also_crashed PASSED [ 84%]
tests/test_state.py::test_all_state_lives_under_a_single_directory PASSED [ 84%]
tests/test_state.py::test_config_and_state_are_separate_files PASSED     [ 84%]
tests/test_state.py::test_a_project_without_a_state_file_is_not_initialised PASSED [ 84%]
tests/test_state.py::test_a_project_is_initialised_once_both_files_exist PASSED [ 84%]
tests/test_state.py::test_init_writes_the_module_path PASSED             [ 85%]
tests/test_state.py::test_init_writes_an_empty_approvals_list PASSED     [ 85%]
tests/test_state.py::test_init_writes_no_phase_or_status PASSED          [ 85%]
tests/test_state.py::test_init_records_an_event PASSED                   [ 85%]
tests/test_state.py::test_the_state_file_holds_configuration_and_approvals PASSED [ 85%]
tests/test_state.py::test_the_module_path_stays_in_config_not_state PASSED [ 85%]
tests/test_state.py::test_the_state_file_has_no_phase_field PASSED       [ 85%]
tests/test_state.py::test_the_state_file_has_no_status_field PASSED      [ 85%]
tests/test_state.py::test_an_approval_records_phase_gate_and_date PASSED [ 85%]
tests/test_state.py::test_recording_an_approval_appends_rather_than_replaces PASSED [ 85%]
tests/test_state.py::test_an_absent_state_file_is_not_an_error PASSED    [ 86%]
tests/test_state.py::test_an_absent_state_file_reports_no_approvals PASSED [ 86%]
tests/test_state.py::test_a_corrupt_state_file_is_reported_as_a_problem PASSED [ 86%]
tests/test_state.py::test_a_non_string_module_path_is_ignored_not_trusted PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-array-at-top-level] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-string] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[dict-missing-approvals] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approvals-not-a-list] PASSED [ 86%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approval-entry-not-a-dict] PASSED [ 86%]
tests/test_state.py::test_project_state_carries_configuration_and_approvals PASSED [ 86%]
tests/test_state.py::test_project_state_carries_no_phase PASSED          [ 87%]
tests/test_state.py::test_the_state_module_exposes_no_phase_enum PASSED  [ 87%]
tests/test_state.py::test_the_state_module_exposes_no_status_enum PASSED [ 87%]
tests/test_state.py::test_the_state_module_exposes_no_transition_machinery PASSED [ 87%]
tests/test_state.py::test_a_version_one_state_file_is_reported_as_outdated PASSED [ 87%]
tests/test_state.py::test_an_outdated_state_file_is_not_called_corrupt PASSED [ 87%]
tests/test_state.py::test_an_outdated_state_file_says_what_to_do_about_it PASSED [ 87%]
tests/test_state.py::test_an_outdated_state_file_yields_no_approvals PASSED [ 87%]
tests/test_state.py::test_a_file_missing_approvals_without_the_v1_shape_is_still_corrupt PASSED [ 87%]
tests/test_state.py::test_an_approval_missing_a_field_is_a_problem PASSED [ 87%]
tests/test_state.py::test_an_empty_approval_object_is_not_a_valid_approval PASSED [ 88%]
tests/test_state.py::test_an_approval_with_a_non_string_field_is_a_problem PASSED [ 88%]
tests/test_state.py::test_a_malformed_approval_names_its_position PASSED [ 88%]
tests/test_state.py::test_well_formed_approvals_still_load PASSED        [ 88%]
tests/test_status.py::test_the_text_rendering_names_the_project_root PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_names_the_current_phase PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_branch PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_fallback PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_lists_every_required_artifact PASSED [ 88%]
tests/test_status.py::test_the_text_rendering_shows_a_recorded_approval PASSED [ 88%]
tests/test_status.py::test_every_other_phase_gets_one_summary_line PASSED [ 89%]
tests/test_status.py::test_the_summary_line_reports_present_over_required PASSED [ 89%]
tests/test_status.py::test_a_skipped_poc_phase_summarises_out_of_six PASSED [ 89%]
tests/test_status.py::test_the_current_phase_is_not_repeated_in_the_summary PASSED [ 89%]
tests/test_status.py::test_the_summary_is_ordered_lexically PASSED       [ 89%]
tests/test_status.py::test_the_json_contract_has_the_documented_keys PASSED [ 89%]
tests/test_status.py::test_the_json_phases_array_covers_every_phase PASSED [ 89%]
tests/test_status.py::test_the_json_phases_array_includes_the_current_phase PASSED [ 89%]
tests/test_status.py::test_the_json_artifact_map_is_name_to_boolean PASSED [ 89%]
tests/test_status.py::test_the_json_is_parseable_when_problems_exist PASSED [ 89%]
tests/test_status.py::test_two_problems_are_both_reported PASSED         [ 90%]
tests/test_status.py::test_a_problem_does_not_suppress_the_rest_of_the_report PASSED [ 90%]
tests/test_status.py::test_a_phase_missing_artifacts_still_answers PASSED [ 90%]
tests/test_status.py::test_a_project_with_no_phases_still_answers PASSED [ 90%]
tests/test_status.py::test_a_corrupt_state_file_still_answers PASSED     [ 90%]
tests/test_status.py::test_an_unreadable_project_root_is_reported_not_raised PASSED [ 90%]
tests/test_status.py::test_the_status_report_exposes_no_could_answer PASSED [ 90%]
tests/test_status.py::test_the_temp_file_sweep_still_runs PASSED         [ 90%]
tests/test_status.py::test_the_sweep_is_still_reported_never_silent PASSED [ 90%]
tests/test_status.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 90%]
tests/test_status.py::test_the_default_runner_and_project_resolution_are_used PASSED [ 91%]
tests/test_status.py::test_the_default_path_without_a_specs_directory_reports_no_phases PASSED [ 91%]
tests/test_status.py::test_a_specs_directory_without_a_project_reports_no_phases PASSED [ 91%]
tests/test_status.py::test_more_than_one_project_directory_is_reported_and_the_first_used PASSED [ 91%]
tests/test_status.py::test_a_project_directory_beside_loose_phase_directories_is_reported PASSED [ 91%]
tests/test_status.py::test_the_mixed_layout_still_reports_the_project_directory_phases PASSED [ 91%]
tests/test_status.py::test_a_flat_layout_is_accepted_without_comment PASSED [ 91%]
tests/test_status.py::test_real_repository_reports_multiple_projects_and_atom_cli_history_remains_readable PASSED [ 91%]
tests/test_status.py::test_a_corrupt_config_is_reported_separately PASSED [ 91%]
tests/test_status.py::test_the_last_event_and_damaged_lines_are_reported PASSED [ 91%]
tests/test_status.py::test_the_text_rendering_shows_the_module_path PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_marks_a_not_started_phase PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_states_when_there_is_no_current_phase PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_shows_the_last_event PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_points_at_the_problems PASSED [ 92%]
tests/test_status.py::test_the_problem_renderer_is_empty_when_there_are_no_problems PASSED [ 92%]
tests/test_status.py::test_the_problem_renderer_uses_amber_advisories PASSED [ 92%]
tests/test_status.py::test_the_problem_renderer_never_uses_red PASSED    [ 92%]
tests/test_storage.py::test_reading_a_missing_file_says_it_is_missing PASSED [ 92%]
tests/test_storage.py::test_reading_unparseable_json_reports_corruption PASSED [ 92%]
tests/test_storage.py::test_reading_valid_json_of_the_wrong_type_is_still_corruption PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected["just a string"-str] PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[42-int] PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[null-NoneType] PASSED [ 93%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[true-bool] PASSED [ 93%]
tests/test_storage.py::test_an_empty_file_is_corruption_not_emptiness PASSED [ 93%]
tests/test_storage.py::test_a_file_of_nul_bytes_is_corruption PASSED     [ 93%]
tests/test_storage.py::test_a_missing_required_key_is_corruption_and_names_the_key PASSED [ 93%]
tests/test_storage.py::test_reading_a_well_formed_file_returns_the_object PASSED [ 93%]
tests/test_storage.py::test_reading_does_not_keep_the_file_open PASSED   [ 93%]
tests/test_storage.py::test_writing_then_reading_round_trips PASSED      [ 94%]
tests/test_storage.py::test_writing_creates_the_parent_directory PASSED  [ 94%]
tests/test_storage.py::test_writing_leaves_no_temp_file_behind_on_success PASSED [ 94%]
tests/test_storage.py::test_writing_replaces_rather_than_truncating PASSED [ 94%]
tests/test_storage.py::test_writing_retries_while_the_destination_is_held_open PASSED [ 94%]
tests/test_storage.py::test_a_write_that_cannot_succeed_fails_loudly PASSED [ 94%]
tests/test_storage.py::test_sweeping_removes_leftover_temp_files PASSED  [ 94%]
tests/test_storage.py::test_sweeping_reports_what_it_removed PASSED      [ 94%]
tests/test_storage.py::test_sweeping_leaves_unsaved_recovery_files_alone PASSED [ 94%]
tests/test_storage.py::test_sweeping_leaves_real_state_files_alone PASSED [ 94%]
tests/test_storage.py::test_sweeping_an_absent_directory_is_not_an_error PASSED [ 95%]
tests/test_style.py::test_style_rules_reach_the_model_by_default PASSED  [ 95%]
tests/test_style.py::test_style_rules_can_be_switched_off_for_measurement PASSED [ 95%]
tests/test_style.py::test_style_rules_sit_before_the_output_format_instruction PASSED [ 95%]
tests/test_style.py::test_every_rule_is_numbered_and_present PASSED      [ 95%]
tests/test_style.py::test_no_rule_is_phrased_as_a_preference PASSED      [ 95%]
tests/test_toolchain.py::test_prompt_block_excludes_everything_the_passing_toolchain_proved PASSED [ 95%]
tests/test_toolchain.py::test_prompt_block_does_not_exclude_ignored_errors_when_errcheck_was_skipped PASSED [ 95%]
tests/test_toolchain.py::test_prompt_block_says_nothing_is_excluded_when_toolchain_did_not_run PASSED [ 95%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 95%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 96%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] FAILED [ 96%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 96%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout PASSED [ 96%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 96%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 96%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 96%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 96%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 96%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 96%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 97%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 97%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 97%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 97%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 97%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 98%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 98%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 98%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 98%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 98%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 99%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 99%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [ 99%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 99%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 99%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 99%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 99%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

================================== FAILURES ===================================
____________ test_windows_success_stops_pipe_independent_child[0] _____________

tmp_path = WindowsPath('<private-home>/AppData/Local/Temp/pytest-of-user/pytest-392/test_windows_success_stops_pip0')
exit_code = 0

    @pytest.mark.parametrize("exit_code", [0, 7])
    def test_windows_success_stops_pipe_independent_child(tmp_path, exit_code):
        native = _windows_module()._Native()
        with _tree_fixture(tmp_path, hold_output=False, exit_code=exit_code) as (command, directory, identities):
            result = SubprocessRunner().run(command, tmp_path, timeout_seconds=5)
>           handle = _retained_identity(identities)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_windows_process.py:156: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

identities = <queue.Queue object at 0x000001F49FE297F0>

    def _retained_identity(identities):
        handle = identities.get(timeout=1)
        identities.put(handle)
>       assert not isinstance(handle, BaseException), str(handle)
E       AssertionError: [Errno 13] Permission denied: '<private-home>\\AppData\\Local\\Temp\\pytest-of-user\\pytest-392\\test_windows_success_stops_pip0\\child-ready'
E       assert not True
E        +  where True = isinstance(PermissionError(13, 'Permission denied'), BaseException)

tests\test_windows_process.py:147: AssertionError

During handling of the above exception, another exception occurred:

tmp_path = WindowsPath('<private-home>/AppData/Local/Temp/pytest-of-user/pytest-392/test_windows_success_stops_pip0')
exit_code = 0

    @pytest.mark.parametrize("exit_code", [0, 7])
    def test_windows_success_stops_pipe_independent_child(tmp_path, exit_code):
        native = _windows_module()._Native()
>       with _tree_fixture(tmp_path, hold_output=False, exit_code=exit_code) as (command, directory, identities):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_windows_process.py:154: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\contextlib.py:162: in __exit__
    self.gen.throw(value)
tests\test_windows_process.py:133: in _tree_fixture
    raise handle
tests\test_windows_process.py:98: in register_identity
    pid = int(ready.read_text())
              ^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:546: in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_abc.py:632: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = WindowsPath('<private-home>/AppData/Local/Temp/pytest-of-user/pytest-392/test_windows_success_stops_pip0/child-ready')
mode = 'r', buffering = -1, encoding = 'locale', errors = None, newline = None

    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed to by this path and return a file object, as
        the built-in open() function does.
        """
        if "b" not in mode:
            encoding = io.text_encoding(encoding)
>       return io.open(self, mode, buffering, encoding, errors, newline)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       PermissionError: [Errno 13] Permission denied: '<private-home>\\AppData\\Local\\Temp\\pytest-of-user\\pytest-392\\test_windows_success_stops_pip0\\child-ready'

C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:537: PermissionError
=============================== tests coverage ================================
______________ coverage: platform win32, python 3.13.14-final-0 _______________

Name                       Stmts   Miss  Cover
----------------------------------------------
atom\__init__.py               1      0   100%
atom\_windows_process.py     374     28    93%
atom\artifact_cli.py          35      1    97%
atom\artifacts.py            174     19    89%
atom\body.py                  71      0   100%
atom\buildsystem.py           76      5    93%
atom\check.py                 43      2    95%
atom\cli.py                  280     21    92%
atom\diff.py                 121      0   100%
atom\eventlog.py              50      0   100%
atom\extract.py              101      0   100%
atom\filelock.py              64     10    84%
atom\gates.py                173      8    95%
atom\index.py                 40      5    88%
atom\invoke.py               116      0   100%
atom\merge.py                 92      0   100%
atom\onboarding.py            89      3    97%
atom\phases.py                92      0   100%
atom\report.py               329     10    97%
atom\review.py                82      1    99%
atom\runner.py               169     52    69%
atom\scaffold.py              46      1    98%
atom\ship.py                 252      3    99%
atom\spike.py                128      4    97%
atom\state.py                103      1    99%
atom\status.py                77      0   100%
atom\storage.py               79      2    97%
atom\style.py                  4      0   100%
atom\toolchain.py             53      6    89%
----------------------------------------------
TOTAL                       3314    182    95%
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] - PermissionError: [Errno 13] Permission denied: '<private-home>\\AppData\\Local\\Temp\\pytest-of-user\\pytest-392\\test_windows_success_stops_pip0\\child-ready'
============= 1 failed, 998 passed, 2 skipped in 89.04s (0:01:29) =============
```

## 14-readiness-red

Valid deterministic RED for the visible-but-unreadable identity record fixture.

Command from tools: `python -m pytest tests\test_windows_process.py -k fixture_waits_for_readable -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 43 items / 42 deselected / 1 selected

tests\test_windows_process.py F                                          [100%]

================================== FAILURES ===================================
___________ test_windows_fixture_waits_for_readable_identity_record ___________
tests\test_windows_process.py:188: in test_windows_fixture_waits_for_readable_identity_record
    assert failure is None, "temporary record sharing must not invalidate identity setup"
E   AssertionError: temporary record sharing must not invalidate identity setup
E   assert PermissionError('fixture identity record is temporarily unreadable') is None
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_fixture_waits_for_readable_identity_record
====================== 1 failed, 42 deselected in 7.83s =======================
```

## 15-readiness-green

GREEN after bounded readable-record waiting, without weakening process or cwd assertions.

Command from tools: `python -m pytest tests\test_windows_process.py tests\test_runner.py -q --tb=short`.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <shipping-tools>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 62 items

tests\test_windows_process.py .......................................... [ 67%]
...                                                                      [ 72%]
tests\test_runner.py ...............ss                                   [100%]

======================= 60 passed, 2 skipped in 21.97s ========================
```
