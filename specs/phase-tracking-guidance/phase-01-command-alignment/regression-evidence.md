# Regression evidence

Command from tools; expected failing exit: 1.

Captured output below has trailing whitespace on pytest diagnostic blank lines
removed for repository whitespace checks. All diagnostic text and results are
unchanged. This normalization was explicitly approved on 2026-11-25.

```text
python -m pytest tests\test_phase_tracking_guidance.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 6 items

tests\test_phase_tracking_guidance.py FFFFFF                             [100%]

================================== FAILURES ===================================
_______ test_phase_tracking_examples_use_supported_commands[relative0] ________
tests\test_phase_tracking_guidance.py:32: in test_phase_tracking_examples_use_supported_commands
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"
E   AssertionError: skills\plan\SKILL.md: unsupported CLI examples: ['atom phase add 01 {slug} --risk high --poc-required', 'atom phase list']
E   assert ['atom phase ...m phase list'] == []
E
E     Left contains 2 more items, first extra item: 'atom phase add 01 {slug} --risk high --poc-required'
E     Use -v to get more diff
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
_______ test_phase_tracking_examples_use_supported_commands[relative1] ________
tests\test_phase_tracking_guidance.py:32: in test_phase_tracking_examples_use_supported_commands
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"
E   AssertionError: skills\build\SKILL.md: unsupported CLI examples: ['atom phase done NN']
E   assert ['atom phase done NN'] == []
E
E     Left contains one more item: 'atom phase done NN'
E     Use -v to get more diff
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
_______ test_phase_tracking_examples_use_supported_commands[relative2] ________
tests\test_phase_tracking_guidance.py:32: in test_phase_tracking_examples_use_supported_commands
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"
E   AssertionError: skills\atom\references\human-gates.md: unsupported CLI examples: ['atom phase show']
E   assert ['atom phase show'] == []
E
E     Left contains one more item: 'atom phase show'
E     Use -v to get more diff
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
_______ test_phase_tracking_examples_use_supported_commands[relative3] ________
tests\test_phase_tracking_guidance.py:32: in test_phase_tracking_examples_use_supported_commands
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"
E   AssertionError: tools\atom\assets\skills\plan\SKILL.md: unsupported CLI examples: ['atom phase add 01 {slug} --risk high --poc-required', 'atom phase list']
E   assert ['atom phase ...m phase list'] == []
E
E     Left contains 2 more items, first extra item: 'atom phase add 01 {slug} --risk high --poc-required'
E     Use -v to get more diff
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
_______ test_phase_tracking_examples_use_supported_commands[relative4] ________
tests\test_phase_tracking_guidance.py:32: in test_phase_tracking_examples_use_supported_commands
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"
E   AssertionError: tools\atom\assets\skills\build\SKILL.md: unsupported CLI examples: ['atom phase done NN']
E   assert ['atom phase done NN'] == []
E
E     Left contains one more item: 'atom phase done NN'
E     Use -v to get more diff
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
_______ test_phase_tracking_examples_use_supported_commands[relative5] ________
tests\test_phase_tracking_guidance.py:32: in test_phase_tracking_examples_use_supported_commands
    assert unsupported == [], f"{relative}: unsupported CLI examples: {unsupported}"
E   AssertionError: tools\atom\assets\skills\atom\references\human-gates.md: unsupported CLI examples: ['atom phase show']
E   assert ['atom phase show'] == []
E
E     Left contains one more item: 'atom phase show'
E     Use -v to get more diff
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: argument command: invalid choice: 'phase' (choose from 'check', 'poc', 'init', 'status', 'review', 'ship', 'setup-path')
=========================== short test summary info ===========================
FAILED tests/test_phase_tracking_guidance.py::test_phase_tracking_examples_use_supported_commands[relative0]
FAILED tests/test_phase_tracking_guidance.py::test_phase_tracking_examples_use_supported_commands[relative1]
FAILED tests/test_phase_tracking_guidance.py::test_phase_tracking_examples_use_supported_commands[relative2]
FAILED tests/test_phase_tracking_guidance.py::test_phase_tracking_examples_use_supported_commands[relative3]
FAILED tests/test_phase_tracking_guidance.py::test_phase_tracking_examples_use_supported_commands[relative4]
FAILED tests/test_phase_tracking_guidance.py::test_phase_tracking_examples_use_supported_commands[relative5]
============================== 6 failed in 2.25s ==============================
```
