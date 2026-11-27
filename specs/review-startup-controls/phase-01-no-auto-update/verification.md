# Startup control validation

Command from tools:

python -m pytest tests\test_cli_review.py tests\test_invoke.py tests\test_cli_pr_review.py tests\test_review_toolchain.py tests\test_review_formatting.py tests\test_review_continuation.py tests\test_review_output.py tests\test_style.py tests\test_phase_tracking_guidance.py tests\test_plugin.py tests\test_standalone_review_guidance.py -q --tb=short

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 457 items

tests\test_cli_review.py ............................................... [ 10%]
..................................                                       [ 17%]
tests\test_invoke.py ................................................... [ 28%]
..................                                                       [ 32%]
tests\test_cli_pr_review.py .............................                [ 39%]
tests\test_review_toolchain.py .......................                   [ 44%]
tests\test_review_formatting.py ........................................ [ 52%]
...........................                                              [ 58%]
tests\test_review_continuation.py ...................................... [ 67%]
.............................                                            [ 73%]
tests\test_review_output.py ............................................ [ 83%]
............................                                             [ 89%]
tests\test_style.py .....                                                [ 90%]
tests\test_phase_tracking_guidance.py .........                          [ 92%]
tests\test_plugin.py ...........                                         [ 94%]
tests\test_standalone_review_guidance.py ........................        [100%]

======================= 457 passed in 67.11s (0:01:07) ========================
```

Exit code: 0. No real model calls were part of these tests.

## Relative links

Command: python tools\check_links.py

```text
checked 656 relative links across markdown files
all relative links resolve
```

Exit code: 0.

## Whitespace and staged snapshot

Checked tracked working/index diffs and every Markdown file in this phase
against NUL with git diff --no-index --check. For no-index checks, exit 1
means different files; only empty output and status 0/1 were accepted.
Checked git write-tree against the preserved staged snapshot.

```text
git diff --check: exit 0 (no output)
git diff --cached --check: exit 0 (no output)
git diff --no-index --check: 7 new phase artifacts clean
Original staged tree preserved: 7ffadd8569dae01c69100e14d76fb71927375ef7
```

Exit code: 0.

## Draft PR pre-commit verification on 2026-11-27

Fresh combined-worktree validation for both accepted changes, to be committed
as separate phases. This is affected-area Python verification, not a Go atom
check, full-suite, cross-platform or independent-model review claim.

Command from tools:

python -m pytest tests\test_cli_review.py tests\test_invoke.py tests\test_cli_pr_review.py tests\test_review_toolchain.py tests\test_review_formatting.py tests\test_review_continuation.py tests\test_review_output.py tests\test_style.py tests\test_phase_tracking_guidance.py tests\test_plugin.py tests\test_standalone_review_guidance.py -q --tb=short

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 457 items

tests\test_cli_review.py ............................................... [ 10%]
..................................                                       [ 17%]
tests\test_invoke.py ................................................... [ 28%]
..................                                                       [ 32%]
tests\test_cli_pr_review.py .............................                [ 39%]
tests\test_review_toolchain.py .......................                   [ 44%]
tests\test_review_formatting.py ........................................ [ 52%]
...........................                                              [ 58%]
tests\test_review_continuation.py ...................................... [ 67%]
.............................                                            [ 73%]
tests\test_review_output.py ............................................ [ 83%]
............................                                             [ 89%]
tests\test_style.py .....                                                [ 90%]
tests\test_phase_tracking_guidance.py .........                          [ 92%]
tests\test_plugin.py ...........                                         [ 94%]
tests\test_standalone_review_guidance.py ........................        [100%]

======================= 457 passed in 110.06s (0:01:50) =======================
```

Exit code: 0. No real model calls were part of these tests.

Fresh pre-commit relative-link command: python tools\check_links.py

```text
checked 656 relative links across markdown files
all relative links resolve
```

Exit code: 0.
