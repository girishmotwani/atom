Publication redaction: local Windows profile prefixes in this historical evidence were replaced with <LOCAL_PROFILE>. Original evidence remains private; this copy is not byte-identical to the captured transcript.

# Independent Review: Windows user-PATH setup

Command:

```text
python -m atom.cli review --staged --runs 1 --concurrency 2
```

The staged snapshot contained 1,075 added/removed lines across 16 feature files, including the complete new Python module, tests, POC, and approved specification. Two distinct models reviewed the same captured diff; neither was the author model. The command exited 0 with both requested runs complete.

## Tool output

```text
| Model | Runs completed |
| --- | --- |
| `gpt-5.4` | 1/1 |
| `gemini-3.8-flash` | 1/1 |

## Toolchain evidence

Toolchain did not run: No go.mod found in <LOCAL_PROFILE>\work\atom
nothing was excluded from the review prompt.

## Findings

### `tools/atom/pathsetup.py`

#### tools/atom/pathsetup.py:51 - medium

Reported by: `gpt-5.4` 1/1

- `gpt-5.4` run 1, line 51 (medium): Equivalent-entry detection expands variables from the current process environment, so a user PATH entry like `%ATOM_HOME%` is missed when this session started before that variable existed and the command can append a duplicate Scripts directory.

### `tools/tests/test_pathsetup.py`

#### tools/tests/test_pathsetup.py:61 - medium

Reported by: `gpt-5.4` 1/1

- `gpt-5.4` run 1, line 61 (medium): This subprocess test runs `python -m atom.cli` from an empty temporary directory without setting `PYTHONPATH`, so it only passes when Atom is already installed in the runner and is non-hermetic.
```

The Go gate was not represented as passing: this repository implements Python tooling and has no root Go module. The existing Python suite had already passed (994 tests); verification.md contains the real evidence. The shared review prompt is Go-oriented, so its mechanical exclusions were deliberately not treated as proof about Python.

## Triage

### Stale environment-variable aliases: deferred, medium

The finding is valid for a persisted PATH alias referencing a variable created after the current process started. Comparison currently uses the current process environment. It preserves all stored text and still makes the executable reachable, but may append a redundant literal directory when an old process cannot expand an equivalent newly created alias. Subsequent runs recognize that literal entry and do not keep appending it.

Resolving a fresh persistent user environment requires additional environment-resolution behavior beyond the isolated POC and the approved current-environment comparison. Do not improvise a registry-variable expansion engine or add unproven native token/environment APIs during publication. Record the limitation explicitly; do not claim global de-duplication against variables missing from the current process. A fresh session containing the alias variable avoids this case. No data is truncated or removed.

### Hermetic subprocess coverage: fixed

Strengthened the test to launch Python with -S and an initially empty PYTHONPATH. It reproduced the reported dependency with ModuleNotFoundError. The test now explicitly supplies this checkout's tools directory as PYTHONPATH, so it exercises source in an otherwise empty directory without relying on an installed package or editable-install hooks. This is a test-harness correction, not a weakened expectation or a production behavior change.

Post-fix command:

```text
python -m pytest tools\tests\test_pathsetup.py tools\tests\test_cli.py tools\tests\test_cli_state.py tools\tests\test_artifact_cli.py tools\tests\test_onboarding.py -q --tb=short
```

Captured result:

```text
============================ 113 passed in 25.51s =============================
```

Exit code: 0. Scoped git diff --check also exited 0. The production implementation was unchanged after the full-suite pass; only the subprocess test was strengthened.
