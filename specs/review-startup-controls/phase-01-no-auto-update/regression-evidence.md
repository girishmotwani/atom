# Startup control RED evidence

Command from tools:

python -m pytest tests\test_cli_review.py -q --tb=short -k no_auto_update

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 80 items / 76 deselected / 4 selected

tests\test_cli_review.py FFF.                                            [100%]

================================== FAILURES ===================================
_____ test_no_auto_update_reaches_probes_and_reviews[source0-True-False] ______
tests\test_cli_review.py:137: in test_no_auto_update_reaches_probes_and_reviews
    assert code == EXIT_PASSED
E   assert 2 == 0
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: unrecognized arguments: --no-auto-update
______ test_no_auto_update_reaches_probes_and_reviews[source1-True-True] ______
tests\test_cli_review.py:137: in test_no_auto_update_reaches_probes_and_reviews
    assert code == EXIT_PASSED
E   assert 2 == 0
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: unrecognized arguments: --no-auto-update
_____ test_no_auto_update_reaches_probes_and_reviews[source2-True-False] ______
tests\test_cli_review.py:137: in test_no_auto_update_reaches_probes_and_reviews
    assert code == EXIT_PASSED
E   assert 2 == 0
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: unrecognized arguments: --no-auto-update
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::test_no_auto_update_reaches_probes_and_reviews[source0-True-False]
FAILED tests/test_cli_review.py::test_no_auto_update_reaches_probes_and_reviews[source1-True-True]
FAILED tests/test_cli_review.py::test_no_auto_update_reaches_probes_and_reviews[source2-True-False]
================= 3 failed, 1 passed, 76 deselected in 1.60s ==================
```

Exit code: 1. Expected failures: enabled flag is rejected by the old parser; omitted flag remains passing.
