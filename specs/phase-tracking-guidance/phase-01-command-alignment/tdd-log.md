# Guidance repair verification

## Scope and approval

The developer approved design-spec.md on 2026-11-25. This is a documentation
repair with parser-backed regression checks, not a production Go TDD cycle.
No runtime implementation, schema, dependencies, or spec behaviours changed.

## RED

Original complete defect evidence is in regression-evidence.md. After extending
the regression to inline executable examples, ran from tools:

```text
python -m pytest tests\test_phase_tracking_guidance.py -q --tb=line
```

Verbatim excerpts from the extended failing run (not its complete output):

```text
collected 9 items

tests\test_phase_tracking_guidance.py FFFFFF...                          [100%]
```

```text
E   AssertionError: skills\build\SKILL.md: unsupported CLI examples: ['atom phase done NN', 'atom status --start {project}']
```

```text
atom: error: unrecognized arguments: --start {project}
```

```text
========================= 6 failed, 3 passed in 2.31s =========================
```

The six failures are the unsupported examples in canonical and packaged guidance;
the three passing cases verify existing text parity. The new inline extraction
also exposes the unsupported startup flag before the repair.

## GREEN

After correcting the six documents, the first targeted integration run reported:

```text
============================= 44 passed in 2.12s ==============================
```

After formatting the new test comprehension, ran from tools:

```text
python -m pytest tests\test_phase_tracking_guidance.py tests\test_plugin.py tests\test_standalone_review_guidance.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 44 items

tests\test_phase_tracking_guidance.py .........                          [ 20%]
tests\test_plugin.py ...........                                         [ 45%]
tests\test_standalone_review_guidance.py ........................        [100%]

============================= 44 passed in 0.74s ==============================
```

## Links and whitespace

Ran from tools:

```text
python check_links.py
checked 654 relative links across markdown files
all relative links resolve
```

Ran git diff --check: exit 0. Git emitted this newline-normalization warning:

```text
warning: in the working copy of 'skills/atom/references/human-gates.md', CRLF will be replaced by LF the next time Git touches it
```

## Factual review

- Planning now uses named phase directories and the artifact writer, not phase
  registration. phases.py discover_phases and derive implement discovery and
  branch/lexical selection, not approval inference.
- Build setup uses supported status inspection. cli.py _run_status_command does
  not initialize a project, register a run, or record human approval.
- Completion is recorded in artifacts and the plan after human approval; no
  completion command or automatic completion claim remains in this path.
- Resume checks artifacts and recorded approval evidence. state.py ProjectState
  stores approvals, not an active phase/status state machine.
- The CI example explicitly states an unapproved gate, emits a halt message and
  exits 2. Status is information, not hidden enforcement.
- Three canonical/packaged pairs match after native newline normalization.
  Parser checks execute no documented commands.
- No new runtime error, cancellation or concurrency paths exist. The existing
  diagnostics, setup permission boundary and between-phase gates remain intact.

## Limits and completion gate

No full Python suite, Go gate, external project replay, live-agent evaluation,
paid review, commit, push or publication is claimed. Static checks do not prove
live-agent compliance. The developer accepted this implementation on 2026-11-25;
review is the next named step.


## Shipping preflight on 2026-11-25

Fresh commands from tools, immediately before review staging:

python -m pytest tests\test_phase_tracking_guidance.py tests\test_plugin.py tests\test_standalone_review_guidance.py -q --tb=short

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 44 items

tests\test_phase_tracking_guidance.py .........                          [ 20%]
tests\test_plugin.py ...........                                         [ 45%]
tests\test_standalone_review_guidance.py ........................        [100%]

============================= 44 passed in 1.18s ==============================
```

python check_links.py

```text
checked 654 relative links across markdown files
all relative links resolve
```

git diff --check: exit 0; the existing CRLF normalization warning remains.


## Staged artifact whitespace correction

Earlier git diff --check examined tracked changes only, not the then-untracked
phase artifacts. The staged check caught extra EOF blank lines and pytest's
trailing spaces on otherwise blank diagnostic lines. No model calls ran.
The developer approved whitespace-only normalization and continuation of the
same review on 2026-11-25. regression-evidence.md discloses the normalization.

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
