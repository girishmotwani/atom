# Selected original TDD evidence

These are selected command captures from the original Windows TDD tree, not fresh shipping-tree verification. The original private ledger retains all attempts. No source-bearing/private investigation logs are published here. Only the rootdir line is explicitly redacted; remaining output is copied unchanged. The fresh shipping gate is recorded separately.

## 01-result-red.txt

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <original-private-checkout> (redacted)
configfile: pyproject.toml
plugins: cov-7.1.0
collected 17 items / 16 deselected / 1 selected

tests\test_runner.py F                                                   [100%]

================================== FAILURES ===================================
___________ test_runner_error_cannot_succeed_or_change_result_shape ___________
tests\test_runner.py:21: in test_runner_error_cannot_succeed_or_change_result_shape
    assert outcome is not None, "lifecycle failure needs a distinct non-success outcome"
E   AssertionError: lifecycle failure needs a distinct non-success outcome
E   assert None is not None
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape
====================== 1 failed, 16 deselected in 5.89s =======================
```

## 02-result-green.txt

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <original-private-checkout> (redacted)
configfile: pyproject.toml
plugins: cov-7.1.0
collected 17 items / 16 deselected / 1 selected

tests\test_runner.py .                                                   [100%]

====================== 1 passed, 16 deselected in 7.60s =======================
```

## 29-exception-precedence-green.txt

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <original-private-checkout> (redacted)
configfile: pyproject.toml
plugins: cov-7.1.0
collected 31 items / 28 deselected / 3 selected

tests\test_windows_process.py ...                                        [100%]

====================== 3 passed, 28 deselected in 0.09s =======================
```

## 30-focused-refactor-green.txt

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <original-private-checkout> (redacted)
configfile: pyproject.toml
plugins: cov-7.1.0
collected 261 items

tests\test_runner.py ...............ss                                   [  6%]
tests\test_windows_process.py ...............................            [ 18%]
tests\test_status.py ............................................        [ 35%]
tests\test_gates.py ......................................               [ 49%]
tests\test_invoke.py .........................................           [ 65%]
tests\test_diff.py ...................................                   [ 78%]
tests\test_spike.py .................................................... [ 98%]
...                                                                      [100%]

======================= 259 passed, 2 skipped in 19.91s =======================
```
