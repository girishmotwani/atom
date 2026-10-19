# Repeat-init TDD Implementation

Approved contract: [design-spec.md](design-spec.md). Test mapping: [test-spec.md](test-spec.md).

## Outcome

Valid matching repeats now return 0 with an explicit read-only no-op message. Existing partial, corrupt, or conflicting setup returns 2 without repair. Explicit --force retains deliberate reset semantics. Configuration, approvals, baseline, events, instructions, file bytes, timestamps, and directory membership are preserved on ordinary repeats.

## RED / GREEN evidence

The following are verbatim excerpts from the named commands, not reconstructed output. Complete final gate and real-process output are retained separately below.

### Matching repeat

Command: `python -m pytest tools\tests\test_init_repeat.py -q --tb=short`

```text
E   AssertionError: assert 2 == 0
============================= 2 failed in 11.68s ==============================
```

Command: `python -m pytest tools\tests\test_init_repeat.py tools\tests\test_cli_state.py -k 'init' -q --tb=short`

```text
====================== 10 passed, 23 deselected in 5.36s ======================
```

### Partial initialization

Command: `python -m pytest tools\tests\test_init_repeat.py -k 'partial or existing_atom' -q --tb=line --show-capture=no`

```text
E   AssertionError: assert 0 == 2
======================= 4 failed, 2 deselected in 4.70s =======================
```

Three cases exposed false success; the non-directory case additionally exposed an uncaught FileExistsError. The assertion failures demanded protection before first-init writers.

Command: `python -m pytest tools\tests\test_init_repeat.py -q --tb=short`

```text
============================== 6 passed in 3.27s ==============================
```

### Record validity and module requests

Command: `python -m pytest tools\tests\test_init_repeat.py -k 'configuration or records or module_conflicts or read_failures' -q --tb=line --show-capture=no`

```text
E   AssertionError: assert 0 == 2
================ 29 failed, 16 passed, 6 deselected in 36.51s =================
```

The 16 already-passing cases are regression evidence, not claimed RED evidence.

Command: `python -m pytest tools\tests\test_init_repeat.py -q --tb=short`

```text
============================= 51 passed in 44.65s =============================
```

### Shared scaffold

Command: `python -m pytest tools\tests\test_init_repeat.py -k 'bundle or local_instruction or ignore_rules or scaffold_read_failures' -q --tb=no`

```text
===================== 57 failed, 55 deselected in 35.92s ======================
```

A focused traceback confirmed the failure was a false no-op, not broken setup:

Command: `python -m pytest tools\tests\test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest -k payload0 -q --tb=short --show-capture=no`

```text
E   AssertionError: assert 0 == 2
======================= 1 failed, 5 deselected in 2.54s =======================
```

The first integrated run found the expected intentional contract shift in the old runtime-log-only fixture:

```text
FAILED tools\tests\test_onboarding.py::test_init_ignores_only_generated_atom_runtime_files
======================= 1 failed, 161 passed in 58.06s ========================
```

That fixture now explicitly requests --force; its ignore rules and Git-index preservation assertions remain unchanged.

### Help and skill surfaces

Command: `python -m pytest tools\tests\test_init_repeat.py::test_init_help_explains_no_op_and_destructive_force tools\tests\test_onboarding.py::test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command -q --tb=short --show-capture=no`

```text
============================== 2 failed in 0.27s ==============================
```

After the help/docs edit, the integrated run exposed a test defect: argparse wrapped the words `recorded approvals` onto separate lines. Normalizing whitespace preserves the semantic assertion rather than constraining terminal wrapping. No production behavior was relaxed.

Command: `python -m pytest tools\tests\test_init_repeat.py::test_init_help_explains_no_op_and_destructive_force tools\tests\test_init_repeat.py::test_partial_initialization_is_refused_without_writes tools\tests\test_init_repeat.py::test_repeat_succeeds_as_a_real_process tools\tests\test_onboarding.py::test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command -q --tb=short --show-capture=no`

```text
============================== 5 passed in 2.33s ==============================
```

## Completion verification

From tools: `python -m pytest tests -q --cov=atom --cov-report=term-missing --tb=short` (exit 0).

[Complete verbatim gate output](verification.txt):

```text
TOTAL                   3059    116    96%
====================== 1107 passed in 129.32s (0:02:09) =======================
```

Command: `python poc\repeat-init\probe.py` (exit 0).

[Complete verbatim real CLI output](verification-probe.txt) shows both valid repeats return 0 with all 56 entries unchanged and one approval retained. Missing config and missing state each return 2 with all 55 entries unchanged. The missing-config case now retains its approval rather than erasing it. In the missing-state case the approval file was deliberately removed before the call; init does not manufacture a replacement.

Command: `python tools\check_links.py` (exit 0).

```text
checked 218 relative links across markdown files
all relative links resolve
```

## Reconciliation and limits

All eleven approved behaviors are implemented. Shared .gitignore marker parsing is reused by validation and installation. Other state readers keep their forgiving behavior. No dependencies or automation scripts were added beyond the retained Python proof driver.

There is no root Go module; the approved completion gate is the repository's Python CI command, not root-level atom check. The real Go-module experiment exercises unchanged first-init baseline handling. This does not claim concurrent-init safety, full bundle-content auditing, or Linux/macOS execution. The subsequent independent two-model review is recorded in [review.md](review.md).

Changes remain local and uncommitted. No push, plugin update, or original target-module modification was performed.
