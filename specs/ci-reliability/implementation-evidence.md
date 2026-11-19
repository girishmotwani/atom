---
project: "ci-reliability"
date: "2026-11-19"
status: "implementation-accepted-reviewed-ship-verified"
---

# CI Fixture Repair: Implementation Evidence

Implements the approved [design spec](design-spec.md) and
[test mapping](test-spec.md). Only seven existing test files changed. No runtime,
CI workflow, dependency, timeout or test-skip changes. No tests were removed.
No external model/ADO calls were made by the validation suite.

## Changes And Rationale

The gate-order test owns a deterministic failed-control resolver in its default
arm and checks exactly one call; strict mode retains its forbidden-control
sentinel. All selected-gate and no-model expectations remain intact. This is a
fixture boundary, not a bypass of production control rejection.

The three checkout expectations now resolve the expected module before exact
Path equality. Clone arguments and production containment/cleanup are unchanged.

The shared python_child_environment helper constructs a fresh restricted mapping
and explicitly supplies only the Windows SystemRoot prerequisite. Five Python
fixture call sites use it. Unicode, stdin, mapping-copy, parent immutability,
PATHEXT, timeout and process-identity assertions remain. The empty-environment
test still passes literal {}; it uses a native cmd.exe /d probe on Windows
and the original Python probe on POSIX. No production environment merge.

## Captured Reproduction And Corrected Runs

The diagnostic launcher is session-local ci_diagnosis.py. It runs pytest from
this worktree's tools directory with test-scoped collaborators. The paths mode
aliases only a real temporary parent and verifies cleanup. The children mode
substitutes existing Python 3.10.11 only as the child interpreter; unlike the
previous diagnosis control, it does not inject SystemRoot after these edits.
The go modes supply old, missing or compatible process-local PATH distributions.

Command form (only the absolute session prefix is abbreviated):

~~~text
python <SESSION_FILES>\ci_diagnosis.py <mode> <capture-label>
~~~

Modes and labels below are the actual arguments. Captured output follows;
absolute current/previous worktree and session-file prefixes are replaced by
<CI_WORKTREE> and <SESSION_FILES>/<PREVIOUS_SESSION_FILES> for portability.
Only eight whitespace-only pytest E filler lines are omitted to keep Markdown free of trailing spaces. All actual failure diagnostics remain; complete raw captures are retained in session files.

## go-old red-go

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests\test_review_continuation.py F.                                     [100%]

================================== FAILURES ===================================
_ test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates[False-expected_gate_calls0] _
tests\test_review_continuation.py:310: in test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates
    run_review(
atom\review.py:388: in run_review
    control_selection = _resolve_control_toolchain(
atom\review.py:775: in _resolve_control_toolchain
    return _resolve_path_control_toolchain(
atom\review.py:748: in _resolve_path_control_toolchain
    raise ControlToolchainError(
E   atom.review.ControlToolchainError: PATH Go 1.23.12 is below module minimum 1.27.0
=========================== short test summary info ===========================
FAILED tests/test_review_continuation.py::test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates[False-expected_gate_calls0]
========================= 1 failed, 1 passed in 2.39s =========================
~~~

## paths red-paths

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items

tests\test_cli_pr_review.py FFFFFFFFFFFF                                 [ 85%]
tests\test_pr_checkout_integration.py F                                  [ 92%]
tests\test_pull_request.py F                                             [100%]

================================== FAILURES ===================================
_______________ test_pr_report_provenance_and_limitations[True] _______________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:127: in test_pr_report_provenance_and_limitations
    assert invoke(*arguments) == EXIT_PASSED
           ^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-6fo6iso1/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-6fo6iso1/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-6fo6iso1/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F8104440>.checkout
______________ test_pr_report_provenance_and_limitations[False] _______________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:127: in test_pr_report_provenance_and_limitations
    assert invoke(*arguments) == EXIT_PASSED
           ^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-x2qoi6am/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-x2qoi6am/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-x2qoi6am/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82A1D10>.checkout
__________________ test_pr_review_options_and_partial_status __________________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:154: in test_pr_review_options_and_partial_status
    assert invoke(
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-7xnp4tbg/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-7xnp4tbg/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-7xnp4tbg/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82A3D90>.checkout
_______________ test_pr_no_model_available_is_not_clean_review ________________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:175: in test_pr_no_model_available_is_not_clean_review
    assert invoke(
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-49povvp6/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-49povvp6/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-49povvp6/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82FE780>.checkout
_______ test_pr_transport_failure_is_partial_and_still_cleans_checkout ________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:188: in test_pr_transport_failure_is_partial_and_still_cleans_checkout
    assert invoke(
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-7qzlbyz7/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-7qzlbyz7/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-7qzlbyz7/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82FF100>.checkout
_________________ test_pr_required_checks_still_block[False] __________________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:226: in test_pr_required_checks_still_block
    assert invoke("--pr", PR_URL, *options) == EXIT_CHECK_FAILED
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:318: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\_review_format.py:166: in capture_review_diff
    base = _git(
<CI_WORKTREE>\tools\atom\_review_format.py:113: in _git
    result = runner.run(command, directory, 60)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:222: in run
    return original_run(command, working_directory, timeout_seconds, stdin_text)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-24ym0151/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-24ym0151/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-24ym0151/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F829F650>.checkout
__________________ test_pr_required_checks_still_block[True] __________________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:226: in test_pr_required_checks_still_block
    assert invoke("--pr", PR_URL, *options) == EXIT_CHECK_FAILED
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:318: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\_review_format.py:166: in capture_review_diff
    base = _git(
<CI_WORKTREE>\tools\atom\_review_format.py:113: in _git
    result = runner.run(command, directory, 60)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:222: in run
    return original_run(command, working_directory, timeout_seconds, stdin_text)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-toc_ts98/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-toc_ts98/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-toc_ts98/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82D3BD0>.checkout
________________ test_cleanup_failure_prevents_success_output _________________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:245: in test_cleanup_failure_prevents_success_output
    assert invoke("--pr", PR_URL, "--skip-toolchain", "--runs", "1") == EXIT_CHECK_FAILED
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-s0f7ca22/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-s0f7ca22/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-s0f7ca22/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F83EC9E0>.checkout
_ test_pr_context_is_captured_before_preparation_from_launch_directory[False] _
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:294: in test_pr_context_is_captured_before_preparation_from_launch_directory
    assert invoke(*arguments) == EXIT_PASSED
           ^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-4c8blmpr/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-4c8blmpr/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-4c8blmpr/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F8304150>.checkout
_ test_pr_context_is_captured_before_preparation_from_launch_directory[True] __
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:294: in test_pr_context_is_captured_before_preparation_from_launch_directory
    assert invoke(*arguments) == EXIT_PASSED
           ^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-iyay_2qq/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-iyay_2qq/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-iyay_2qq/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F8307050>.checkout
_________ test_cli_freezes_launch_rules_before_pr_preparation[False] __________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:368: in test_cli_freezes_launch_rules_before_pr_preparation
    assert invoke("--pr", PR_URL, "--skip-toolchain", "--runs", "2", *options) == EXIT_PASSED
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-1388p3du/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-1388p3du/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-1388p3du/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82E6F30>.checkout
__________ test_cli_freezes_launch_rules_before_pr_preparation[True] __________
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:368: in test_cli_freezes_launch_rules_before_pr_preparation
    assert invoke("--pr", PR_URL, "--skip-toolchain", "--runs", "2", *options) == EXIT_PASSED
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:22: in invoke
    return main(["review", *arguments])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:320: in run_review
    diff = capture_diff(request, runner, working_directory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\diff.py:203: in capture_diff
    result = runner.run(command, working_directory, timeout_seconds)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\tests\test_cli_pr_review.py:112: in run
    assert working_directory == checkout_runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-ux3oss3e/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-ux3oss3e/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-ux3oss3e/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F82E7D40>.checkout
______________ test_native_cli_uses_real_checkout_and_cleans_it _______________
<CI_WORKTREE>\tools\tests\test_pr_checkout_integration.py:135: in test_native_cli_uses_real_checkout_and_cleans_it
    assert main(["review", "--pr", PR_URL, "--skip-toolchain", "--runs", "1", "--json"]) == 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:106: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\cli.py:710: in _run_review_command
    outcome = run_review(
<CI_WORKTREE>\tools\atom\review.py:458: in run_review
    invocation = invoke_models(
<CI_WORKTREE>\tools\atom\invoke.py:321: in invoke_models
    availability = probe_models(
<CI_WORKTREE>\tools\atom\invoke.py:297: in probe_models
    return tuple(_map_bounded(probe, list(models), concurrency))
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\invoke.py:469: in _map_bounded
    return list(pool.map(function, items))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\concurrent\futures\_base.py:625: in result_iterator
    yield _result_or_cancel(fs.pop())
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\concurrent\futures\_base.py:318: in _result_or_cancel
    return fut.result(timeout)
           ^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\concurrent\futures\_base.py:453: in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\concurrent\futures\_base.py:402: in __get_result
    raise self._exception
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\concurrent\futures\thread.py:59: in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<CI_WORKTREE>\tools\atom\invoke.py:285: in probe
    result = runner.run(
<CI_WORKTREE>\tools\tests\test_pr_checkout_integration.py:87: in run
    assert working_directory == self.checkout / "src" / "module"
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-s3f5w7yr/repository/src/module') == ((WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-s3f5w7yr/repository') / 'src') / 'module')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-s3f5w7yr/repository') = <tests.test_pr_checkout_integration.LocalTransportRunner object at 0x00000210F827B8C0>.checkout
_________________ test_independent_clone_and_pinned_checkout __________________
tests\test_pull_request.py:231: in test_independent_clone_and_pinned_checkout
    assert prepared.working_directory == runner.checkout
E   AssertionError: assert WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-8mzhmg3t/repository') == WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-8mzhmg3t/repository')
E    +  where WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/atom-pr-8mzhmg3t/repository') = PreparedPullRequest(working_directory=WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/atom-ci-alias-parent-lxftzdgl/...it='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', merge_base='cccccccccccccccccccccccccccccccccccccccc', module_path='.')).working_directory
E    +  and   WindowsPath('C:/Users/gimotwan/AppData/Local/Temp/ATOM-C~2/atom-pr-8mzhmg3t/repository') = <tests.test_pull_request.CheckoutRunner object at 0x00000210F80F5B70>.checkout
=========================== short test summary info ===========================
FAILED tests/test_cli_pr_review.py::test_pr_report_provenance_and_limitations[True]
FAILED tests/test_cli_pr_review.py::test_pr_report_provenance_and_limitations[False]
FAILED tests/test_cli_pr_review.py::test_pr_review_options_and_partial_status
FAILED tests/test_cli_pr_review.py::test_pr_no_model_available_is_not_clean_review
FAILED tests/test_cli_pr_review.py::test_pr_transport_failure_is_partial_and_still_cleans_checkout
FAILED tests/test_cli_pr_review.py::test_pr_required_checks_still_block[False]
FAILED tests/test_cli_pr_review.py::test_pr_required_checks_still_block[True]
FAILED tests/test_cli_pr_review.py::test_cleanup_failure_prevents_success_output
FAILED tests/test_cli_pr_review.py::test_pr_context_is_captured_before_preparation_from_launch_directory[False]
FAILED tests/test_cli_pr_review.py::test_pr_context_is_captured_before_preparation_from_launch_directory[True]
FAILED tests/test_cli_pr_review.py::test_cli_freezes_launch_rules_before_pr_preparation[False]
FAILED tests/test_cli_pr_review.py::test_cli_freezes_launch_rules_before_pr_preparation[True]
FAILED tests/test_pr_checkout_integration.py::test_native_cli_uses_real_checkout_and_cleans_it
FAILED tests/test_pull_request.py::test_independent_clone_and_pinned_checkout
============================= 14 failed in 7.79s ==============================
~~~

## children red-children

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests\test_runner.py FFFFF                                               [ 83%]
tests\test_windows_process.py F                                          [100%]

================================== FAILURES ===================================
__ test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent __
tests\test_runner.py:40: in test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent
    assert result.succeeded, result.stderr
E   AssertionError: Fatal Python error: _Py_HashRandomization_Init: failed to get random numbers to initialize Python
E     Python runtime state: preinitialized
E   assert False
E    +  where False = CommandResult(command=('C:\\Users\\gimotwan\\.copilot\\session-state\\b84ec6a2-70fc-4d05-90f2-ca5e0ea44cb5\\files\\ci-...get random numbers to initialize Python\nPython runtime state: preinitialized\n\n', duration_seconds=0.223434499999712).succeeded
__________ test_absolute_executable_does_not_depend_on_child_pathext __________
tests\test_runner.py:149: in test_absolute_executable_does_not_depend_on_child_pathext
    assert result.succeeded, result.stderr
E   AssertionError: Fatal Python error: _Py_HashRandomization_Init: failed to get random numbers to initialize Python
E     Python runtime state: preinitialized
E   assert False
E    +  where False = CommandResult(command=('C:\\Users\\gimotwan\\.copilot\\session-state\\b84ec6a2-70fc-4d05-90f2-ca5e0ea44cb5\\files\\ci-... random numbers to initialize Python\nPython runtime state: preinitialized\n\n', duration_seconds=0.030318000000988832).succeeded
__________________ test_environment_is_copied_before_launch ___________________
tests\test_runner.py:169: in test_environment_is_copied_before_launch
    assert result.succeeded, result.stderr
E   AssertionError: Fatal Python error: _Py_HashRandomization_Init: failed to get random numbers to initialize Python
E     Python runtime state: preinitialized
E   assert False
E    +  where False = CommandResult(command=('C:\\Users\\gimotwan\\.copilot\\session-state\\b84ec6a2-70fc-4d05-90f2-ca5e0ea44cb5\\files\\ci-...t random numbers to initialize Python\nPython runtime state: preinitialized\n\n', duration_seconds=0.03247900000133086).succeeded
___________ test_empty_environment_does_not_inherit_parent_settings ___________
tests\test_runner.py:213: in test_empty_environment_does_not_inherit_parent_settings
    assert result.succeeded, result.stderr
E   AssertionError: Fatal Python error: _Py_HashRandomization_Init: failed to get random numbers to initialize Python
E     Python runtime state: preinitialized
E   assert False
E    +  where False = CommandResult(command=('C:\\Users\\gimotwan\\.copilot\\session-state\\b84ec6a2-70fc-4d05-90f2-ca5e0ea44cb5\\files\\ci-...t random numbers to initialize Python\nPython runtime state: preinitialized\n\n', duration_seconds=0.03611599999931059).succeeded
_ TestTimeoutIsBoundedEvenWhenChildrenSurvive.test_run_returns_promptly_when_the_child_leaves_a_process_behind[True] _
tests\test_runner.py:479: in test_run_returns_promptly_when_the_child_leaves_a_process_behind
    assert result.outcome is CommandOutcome.TIMED_OUT
E   AssertionError: assert <CommandOutcome.COMPLETED: 'completed'> is <CommandOutcome.TIMED_OUT: 'timed_out'>
E    +  where <CommandOutcome.COMPLETED: 'completed'> = CommandResult(command=('C:\\Users\\gimotwan\\.copilot\\session-state\\b84ec6a2-70fc-4d05-90f2-ca5e0ea44cb5\\files\\ci-... random numbers to initialize Python\nPython runtime state: preinitialized\n\n', duration_seconds=0.029264299999340437).outcome
E    +  and   <CommandOutcome.TIMED_OUT: 'timed_out'> = CommandOutcome.TIMED_OUT
_______________ test_windows_parent_exits_before_timeout[True] ________________
tests\test_windows_process.py:239: in test_windows_parent_exits_before_timeout
    handle = _retained_identity(identities)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_windows_process.py:153: in _retained_identity
    handle = identities.get(timeout=1)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\queue.py:209: in get
    raise Empty
E   _queue.Empty

During handling of the above exception, another exception occurred:
tests\test_windows_process.py:226: in test_windows_parent_exits_before_timeout
    with _tree_fixture(tmp_path, hold_output=True) as (command, directory, identities):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\contextlib.py:162: in __exit__
    self.gen.throw(value)
tests\test_windows_process.py:141: in _tree_fixture
    raise handle
tests\test_windows_process.py:106: in register_identity
    pid = _read_ready_pid(ready, time.monotonic() + 6)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_windows_process.py:83: in _read_ready_pid
    return int(path.read_text())
               ^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:546: in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_abc.py:632: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:537: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\gimotwan\\AppData\\Local\\Temp\\pytest-of-gimotwan\\pytest-762\\test_windows_parent_exits_befo0\\child-ready'
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent
FAILED tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext
FAILED tests/test_runner.py::test_environment_is_copied_before_launch - Asser...
FAILED tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings
FAILED tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True]
FAILED tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True]
============================== 6 failed in 7.09s ==============================
~~~

## go-old green-go-old

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests\test_review_continuation.py ..                                     [100%]

============================== 2 passed in 0.26s ==============================
~~~

## go-missing green-go-missing

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests\test_review_continuation.py ..                                     [100%]

============================== 2 passed in 0.22s ==============================
~~~

## go-compatible green-go-compatible

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests\test_review_continuation.py ..                                     [100%]

============================== 2 passed in 0.17s ==============================
~~~

## paths green-paths

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items

tests\test_cli_pr_review.py ............                                 [ 85%]
tests\test_pr_checkout_integration.py .                                  [ 92%]
tests\test_pull_request.py .                                             [100%]

============================= 14 passed in 6.80s ==============================
~~~

## children green-children

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests\test_runner.py .....                                               [ 83%]
tests\test_windows_process.py .                                          [100%]

============================== 6 passed in 3.75s ==============================
~~~

## Six Affected Test Modules

Command from tools:

~~~text
python -m pytest tests\test_review_continuation.py tests\test_cli_pr_review.py tests\test_pull_request.py tests\test_pr_checkout_integration.py tests\test_runner.py tests\test_windows_process.py -q --tb=short --color=no
~~~

Verbatim capture:

~~~text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <CI_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 247 items

tests\test_review_continuation.py ...................................... [ 15%]
.............................                                            [ 27%]
tests\test_cli_pr_review.py ...........................                  [ 38%]
tests\test_pull_request.py ............................................. [ 56%]
..............................                                           [ 68%]
tests\test_pr_checkout_integration.py ..                                 [ 69%]
tests\test_runner.py ............................ss                      [ 81%]
tests\test_windows_process.py .......................................... [ 98%]
....                                                                     [100%]

======================= 245 passed, 2 skipped in 47.00s =======================
~~~

## Full Local Tooling Gate

~~~text
python -m pytest tests -v --cov=atom --cov-report=term-missing --color=no
~~~

Exit 0. Verbatim coverage table and final summary (not all individual passing
test lines; the complete log remains in session files/full-suite.txt):

~~~text
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   128, 181, 204, 213, 237, 247, 260
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   380     21    94%   111-112, 385-386, 396-406, 428-438, 709, 913
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 175      6    97%   93, 423-424, 428, 489, 501
atom\go_selection.py          220      3    99%   97, 181, 280
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                407      8    98%   199, 214, 226, 240, 256, 258, 265, 993
atom\review.py                314     14    96%   534, 595, 724, 744, 758, 801, 804-805, 816, 834, 844-845, 855, 869
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              79      2    97%   142, 208
---------------------------------------------------------
TOTAL                        4725    233    95%
================= 1722 passed, 5 skipped in 302.67s (0:05:02) =================
~~~

Verbatim skipped-case lines:

~~~text
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[outside] SKIPPED [ 48%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[dangling] SKIPPED [ 48%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[duplicate] SKIPPED [ 48%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 79%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 79%]
~~~

## Source Snapshot

SHA-256 of the seven test files at this implementation gate:

~~~json
{
  "tools/tests/conftest.py": "f44a612b53b39dae468f7913745bd724e36a04a19dc828b120ffe977da94c99d",
  "tools/tests/test_cli_pr_review.py": "ea82e5d58f608517aa49f8ae82313b6301adb586dd9adb5603fc45915558282d",
  "tools/tests/test_pr_checkout_integration.py": "e17771017e23d2007f5a353c20de75321e088cffc8eb08b62db1771b8b1a5e52",
  "tools/tests/test_pull_request.py": "60581f370182ea2ae170a36f75b2b72443014ba654c5ecf019c893d40ff852d1",
  "tools/tests/test_review_continuation.py": "552c57dbc27866bb37ca77fefeaa5e23c7ec1c9e1e84ca23704f0c6d76cafce2",
  "tools/tests/test_runner.py": "98862405157178d1736a193746cea862a6e408068584cd5183920201345be91a",
  "tools/tests/test_windows_process.py": "6c356b35cf199e3bcd17f815d1420b8515c4147d17d06d219a0b2795cbfb34c9"
}
~~~

## Scope And Limits

The complete seven-file diff was read. git diff --check exited 0 with no
whitespace diagnostics. An exact-set check confirmed that only the seven
approved test files changed and captured their hashes above. Generated coverage
is ignored tooling output, not a shipping source change.

Root atom check is inapplicable to this Python-tooling repository; the approved
full pytest/coverage gate above is the actual verification, not a claimed Go
build/vet/race pass. Local Python is 3.13.14 on Windows; the restricted-child
regressions additionally execute Python 3.10.11. This is not a full native 3.10
suite, macOS/Linux rerun or hosted six-job matrix result. CI remains unverified.

No new unresolved in-scope finding or spec-contract deviation. No paid review,
commit, push, PR or merge has occurred. Implementation acceptance and the exact
bounded atom review batch are the next developer gate.


## Fresh Pre-Commit Python Gate

After developer acceptance of the review triage, reran from tools:

~~~text
python -m pytest tests -v --cov=atom --cov-report=term-missing --color=no
~~~

Exit 0. Exact coverage table/final summary and skipped-case lines follow;
individual passing lines remain in session files/ship-full-suite.txt.
All seven accepted/reviewed source hashes remain unchanged. This fresh
Windows Python gate is not a hosted matrix or Go/race claim.

~~~text
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   128, 181, 204, 213, 237, 247, 260
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   380     21    94%   111-112, 385-386, 396-406, 428-438, 709, 913
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 175      6    97%   93, 423-424, 428, 489, 501
atom\go_selection.py          220      3    99%   97, 181, 280
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                407      8    98%   199, 214, 226, 240, 256, 258, 265, 993
atom\review.py                314     14    96%   534, 595, 724, 744, 758, 801, 804-805, 816, 834, 844-845, 855, 869
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              79      2    97%   142, 208
---------------------------------------------------------
TOTAL                        4725    233    95%
================= 1722 passed, 5 skipped in 238.54s (0:03:58) =================
~~~

~~~text
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[outside] SKIPPED [ 48%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[dangling] SKIPPED [ 48%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[duplicate] SKIPPED [ 48%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 79%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 79%]
~~~
