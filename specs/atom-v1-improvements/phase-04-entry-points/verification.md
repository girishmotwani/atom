# Shipping Verification - 2026-11-17

Base: `5bb33cb`, incorporating merged #23/#24. The final focused run imported
this shipping worktree's `tools/atom` package rather than the installed preview.
No runtime code, CLI flag, dependency or root Go module was added.

## Final Focused Python Checks

Command from the shipping worktree's tools directory:

```text
python -m pytest tests\test_plugin.py tests\test_onboarding.py tests\test_init_repeat.py tests\test_scaffold.py tests\test_cli_state.py tests\test_standalone_review_guidance.py tests\test_cli_review.py -q --tb=short
```

Verbatim captured output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-shipping\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 306 items

tests\test_plugin.py ...........                                         [  3%]
tests\test_onboarding.py .......................                         [ 11%]
tests\test_init_repeat.py .............................................. [ 26%]
...................................................................      [ 48%]
tests\test_scaffold.py ............................                      [ 57%]
tests\test_cli_state.py ...............................                  [ 67%]
tests\test_standalone_review_guidance.py ........................        [ 75%]
tests\test_cli_review.py ............................................... [ 90%]
.............................                                            [100%]

======================= 306 passed in 83.32s (0:01:23) ========================
```

This covers plugin commands, onboarding distribution (including installed init and
setup-reference bytes), matching repeats, scaffold/state and standalone-review/CLI
regressions. It is not the full Python suite, a coverage claim, live model review
or Go application validation.

## Documentation And Distribution

Command from repository root: `python tools\check_links.py`.
Verbatim output captured after all linked artifacts were written:

```text
checked 630 relative links across markdown files
all relative links resolve
```

Six canonical/package pairs were directly byte-compared: init, build,
repository-setup, bootstrap, standalone-review and review. Both bootstrap files
were also compared against main `5bb33cb` and remain unchanged. Working/index
whitespace checks exited 0. No excluded local audit is needed for these links.

## Initial Ordering Failure, Preserved

The first run started before the artifact-writing batch reached the new README
link target. Document-link tests therefore ran against an incomplete publication
tree. The batch subsequently completed; the complete focused suite was rerun
without weakening any assertion. The original captured failure follows verbatim:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-shipping\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 306 items

tests\test_plugin.py ...........                                         [  3%]
tests\test_onboarding.py .......................                         [ 11%]
tests\test_init_repeat.py .............................................. [ 26%]
...................................................................      [ 48%]
tests\test_scaffold.py ............................                      [ 57%]
tests\test_cli_state.py ...............................                  [ 67%]
tests\test_standalone_review_guidance.py ...............F........        [ 75%]
tests\test_cli_review.py ............................................... [ 90%]
.............................                                            [100%]

================================== FAILURES ===================================
____________ test_changed_review_document_links_resolve[relative5] ____________
tests\test_standalone_review_guidance.py:96: in test_changed_review_document_links_resolve
    assert (document.parent / path).exists(), f"{relative}: broken link {target}"
E   AssertionError: README.md: broken link specs/atom-v1-improvements/phase-04-entry-points/setup-evidence.md
E   assert False
E    +  where False = exists()
E    +    where exists = (WindowsPath('C:/Users/gimotwan/.copilot/session-state/1ec68bb0-53ec-4735-a4de-c5186a9d376f/files/phase04-setup-shipping') / 'specs/atom-v1-improvements/phase-04-entry-points/setup-evidence.md').exists
E    +      where WindowsPath('C:/Users/gimotwan/.copilot/session-state/1ec68bb0-53ec-4735-a4de-c5186a9d376f/files/phase04-setup-shipping') = WindowsPath('C:/Users/gimotwan/.copilot/session-state/1ec68bb0-53ec-4735-a4de-c5186a9d376f/files/phase04-setup-shipping/README.md').parent
=========================== short test summary info ===========================
FAILED tests/test_standalone_review_guidance.py::test_changed_review_document_links_resolve[relative5]
================== 1 failed, 305 passed in 74.19s (0:01:14) ===================
```

## Evidence Boundary

The mechanical Go spike was not rerun and historical output is not relabeled fresh.
Accepted installed-user observations cover their original frozen instructions,
not the combined #23/#24 treatment. No fresh model-review call or live setup replay
was authorized or run. Root atom-check is inapplicable to this Python tooling repo;
no fabricated Go gate, application readiness, race result or phase closure is claimed.

## Conflict Resolution Checks - 2026-11-17

Merged main `8cf34fa` into PR #25's branch. Only README required manual resolution;
the new quickstart, its reader-first introduction and workflow link are preserved.
No runtime code, canonical/package skill or dependency changed in this merge.
Fresh command from tools:

```text
python -m pytest tests\test_plugin.py tests\test_standalone_review_guidance.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\phase04-setup-shipping\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 35 items

tests\test_plugin.py ...........                                         [ 31%]
tests\test_standalone_review_guidance.py ........................        [100%]

============================= 35 passed in 1.65s ==============================
```

Fresh command from repository root: `python tools\check_links.py`.

```text
checked 646 relative links across markdown files
all relative links resolve
```

Direct comparisons confirm Try Atom matches current main and docs/quickstart.md
has identical bytes after native newline normalization. The index has no unresolved
entries. These are documentation checks, not a new live replay or model review.
