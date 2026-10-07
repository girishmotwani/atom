# Test Spec: Dedicated Artifact Writer

## Behavior mapping

| Behavior | Test |
|---|---|
| B1 | `test_main_allowed_target_writes_exact_utf8_content` |
| B2 | `test_main_empty_stdin_creates_empty_artifact` |
| B3 | `test_main_invalid_utf8_writes_nothing` |
| B4 | `test_main_refused_target_does_not_read_stdin` |
| B5 | `test_main_wrong_argument_count_exits_usage_error` (missing and extra parameter cases) |
| B6 | `test_main_filesystem_failure_reports_error_without_partial_file`; `test_a_failed_stage_leaves_nothing_behind`; `test_a_failed_replace_preserves_existing_file_and_removes_temporary` |
| B7 | `test_write_replaces_an_existing_artifact`; `test_a_failed_stage_leaves_nothing_behind` |
| B8 | `test_link_appearing_after_validation_is_caught_before_the_write` |
| B9 | `test_mixed_batch_writes_nothing` |
| B10 | `test_onboarding_does_not_edit_copilot_permission_configuration`; manual Copilot first-use acceptance check |
| B11 | `test_artifact_producing_skills_use_dedicated_writer`; onboarding asset installation test |
| B12 | `test_artifact_writer_instruction_forbids_bypass_and_source_writes` |

## Additional boundaries

- Unicode outside ASCII survives stdin and disk round-trip.
- A Windows junction and a POSIX symlink are refused where the platform can create
  them.
- The built wheel installs and executes the `atom-write-artifact` console script.
- The installed dedicated script writes an allowed file and refuses a source file.
- The main `atom` parser does not expose an `artifact` subcommand.
- The source skill tree and packaged asset skill tree contain matching writer rules.

## Redundancy audit

This phase is Python, so Go compiler and `go vet` guarantees do not remove any listed
case. Python accepts missing, extra, empty, byte, and path values until runtime; each
listed behavior can silently regress while the package still imports.

No test asserts only that the console-script entry is syntactically present in
`pyproject.toml`; the packaging test builds and installs the wheel and executes the
generated command instead.

## Manual acceptance

The interactive approval UI cannot be reliably driven by the unit test runner. Before
shipping:

1. Start Copilot in a temporary onboarded repository with no saved writer grant.
2. Invoke an Atom skill that writes an artifact.
3. Approve `atom-write-artifact` for the repository.
4. Invoke a second artifact write and verify no prompt appears.
5. Invoke an adjacent `atom` command requiring shell permission and verify it still
   prompts.

## TDD evidence

The dedicated CLI began absent:

```text
E       ModuleNotFoundError: No module named 'atom.artifact_cli'
============================== 1 failed in 7.27s ==============================
```

After adding the minimum module, the allowed-write test failed on the intended missing
file:

```text
E       FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\gimotwan\\AppData\\Local\\Temp\\pytest-of-gimotwan\\pytest-238\\test_main_allowed_target_write0\\specs\\project\\design.md'
============================== 1 failed in 0.40s ==============================
```

The error-behavior batch then exposed the three missing paths:

```text
FAILED tests/test_artifact_cli.py::test_main_invalid_utf8_writes_nothing - Un...
FAILED tests/test_artifact_cli.py::test_main_refused_target_does_not_read_stdin
FAILED tests/test_artifact_cli.py::test_main_filesystem_failure_reports_error_without_partial_file
========================= 3 failed, 4 passed in 0.32s =========================
```

The replace-failure test exposed a leaked temporary file:

```text
E       AssertionError: assert ['.findings.m...'findings.md'] == ['findings.md']
======================== 1 failed, 27 passed in 0.83s =========================
```

Final verification:

```text
collected 889 items
...
TOTAL                   2705    100    96%
======================= 889 passed in 94.38s (0:01:34) ========================
```
