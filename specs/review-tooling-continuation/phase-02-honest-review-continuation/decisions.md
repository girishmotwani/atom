---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-03"
---

# Decisions

## Nested-module snapshot path correction

The developer approved fixing the follow-up path mismatch test-first. `capture_review_diff` now stores selected `FormattingFile.path` values relative to the selected Go module, matching the root used by snapshot fingerprinting. The canonical `CapturedDiff.files` list remains repository-relative for review output. The new integration test first failed because the gate stored `service/changed.go` while fingerprinting rooted at `service`; after the one-line correction it passes and proves the fingerprint is available. This narrows path interpretation only; it does not expand the accepted fingerprint scope beyond captured changed Go files.

No other supplementary review findings were fixed in this change; they remain listed in `findings.md` and `review.md` for developer triage.
## Rejected PATH lookup finding

Rejected the fresh review's one-model High claim that Windows `shutil.which` searches the current directory ahead of the explicit PATH supplied by `_resolve_path_control_toolchain`. On the actual Python 3.13.14 Windows runtime, a current-directory `go.exe` was not selected when `shutil.which("go", path=<different empty directory>)` ran; the result was `None`. No code change is justified by that claim.

The selected-snapshot baseline mismatch, `go.mod` read/decode handling, and control-selection reporting findings are not rejected or deferred here; they await developer triage.
## Working-source snapshot baseline check

After reviewing the confirmed pre-baseline snapshot mismatch, the developer chose to require captured `FormattingFile.content` to match live selected paths only for `DiffSource.WORKING`. `--staged` and `--branch` retain their existing ability to format captured Git blobs that differ from the live worktree; their fingerprints continue to cover live worktree bytes consumed by module-wide checks. This avoids changing established staged/branch behavior, while making a working-tree edit between capture and the initial fingerprint fail closed. The design spec's B7 contract was amended before implementation.
## Snapshot-baseline implementation and fixture evidence

The working-source path now checks the live file's SHA-256 against the captured `FormattingFile.content` during the initial fingerprint. A mismatch fails before selected gates. Staged and branch requests do not apply that comparison; the source-kind decision and consequence are in the amended B7 design spec. The end-of-control fingerprint continues to compare live-file identity against the initial live baseline.

The first implementation run exposed a missing `DiffSource` import (`NameError`); the import was added and the focused test rerun green. Windows `Path.write_text` converted fixture LF bytes to CRLF, which correctly violated the new exact-byte precondition in tests that intended an unchanged baseline. Those fixtures were changed to `write_bytes` to express the captured bytes exactly; tests for deliberate post-baseline mutation still change the live file. No assertion was weakened.

Verification: RED was `1 failed, 1 passed, 61 deselected` because the working case did not raise; GREEN was `2 passed, 61 deselected`. The focused continuation/formatting/toolchain suite passed 153 tests; the full Python suite passed 1689 tests with 5 skipped and 95% coverage.
## Contextual module-minimum read failures

The developer approved fixing the unhandled `go.mod` read/decode path test-first. I will wrap filesystem and UTF-8 failures in the existing `ControlToolchainError`, which the CLI already converts to a nonzero diagnostic, without changing how malformed or ambiguous directives return `None`. The design spec's Behaviour 3 and error table were clarified before implementation.
## Module-minimum read-error fix

`_read_module_minimum_version` now catches filesystem and Unicode decode failures and raises the existing `ControlToolchainError` with the `go.mod` path and original cause. The CLI already handles that exception by printing a diagnostic to stderr and returning `EXIT_CHECK_FAILED`, so no new exception type or CLI branch was added. Parameterized tests prove both read-error classes are wrapped; malformed or ambiguous directives still return `None` as before.

## Selected-path replacement finding: TDD fix

After the fresh review reported a possible symlink replacement between path validation and open, the developer approved a test-first fix. The regression test intercepts the selected file's open and returns a handle for a different file, deterministically exercising the path-redirection boundary without depending on Windows symlink-creation privileges. RED failed because the fingerprint accepted the redirected handle. GREEN compares the opened handle's `st_dev` and `st_ino` with the final `lstat` identity before reading and raises `SourceFingerprintError` on mismatch. The focused identity tests and full focused review suite passed. Full verification: `python -m pytest tests -v --cov=atom` reported `TOTAL 4723 235 95%` and `1692 passed, 5 skipped in 539.82s (0:08:59)`. The approved changed-Go-file-only scope and its accepted module-input blind spots are unchanged.

## PATH Go VERSION decode finding: TDD approval

The developer approved fixing the review finding test-first. I will inject `UnicodeDecodeError` only for the resolved distribution's sibling `VERSION` read and require the existing `ControlToolchainError` with its path context. This remains within B5/B13's already approved fail-closed control-selection contract; no toolchain-selection behavior changes.

The first post-fix test run failed its path-context assertion because Windows canonicalized the fixture executable as `go.EXE` while the fixture `Path` displayed `go.exe`. The error itself was correctly contextual. The assertion was adjusted to require the stable parent-directory path, which still proves which distribution caused the error without imposing case-sensitive filename formatting on Windows; no behavior assertion was weakened.

## Control override requires explicit selected pin: TDD approval

The developer approved rejecting `--control-go-version` unless the caller also specifies `--go-version` or `--go-executable`. The control override has no effect unless the selected toolchain is explicitly pinned and a continuation candidate exists, so accepting it without either selected-toolchain flag silently discards user intent. The design spec now makes the option conflict explicit. The test's RED run showed the CLI returned success and invoked the model; the fix validates before any command runs. The valid forwarding test now supplies an explicit selected version and stubs the review boundary so it verifies argument propagation without invoking Go or models.

## Control-resolution evidence finding deferred

After the latest review, the developer chose to defer the Medium finding that control-toolchain resolution errors can obscure the selected build failure and selection evidence, and to proceed to the TDD completion gate. No rationale was provided. No implementation change was made; the known diagnostic-evidence gap remains visible in `findings.md` and `review.md` for follow-up.

## TDD completion verification

The full Python suite was run from `tools` after the PATH `VERSION` and CLI control-pin fixes:

```text
python -m pytest tests -v --cov=atom
TOTAL                        4725    233    95%
================= 1694 passed, 5 skipped in 238.84s (0:03:58) =================
```

`git diff --check` exited 0 with no output. `atom check` was not run: this repository implements Atom in Python, and `tools` has no `go.mod`; the Python pytest suite is the applicable full-suite verification. The review additionally completed with two distinct configured models; the deferred control-resolution evidence finding and accepted B7 limitations are recorded in `findings.md` and `review.md`.
## TDD completion gate approval

The developer approved the implementation and the recorded Medium finding deferral, authorizing the requested commit, push, and upstream PR. The PR must call out the deferred control-resolution evidence finding and the approved staged/branch snapshot limitations.
## Final pre-ship verification

A fresh run from `tools` completed after the TDD gate and before the commit:

```text
python -m pytest tests -v --cov=atom
TOTAL                        4725    233    95%
================= 1694 passed, 5 skipped in 312.38s (0:05:12) =================
```

The Go-oriented `atom check` was also attempted at the repository root and returned `atom check: No go.mod found in C:\Users\gimotwan\work\atom` (exit 2). This project implements Atom in Python; the Python full-suite run above is the applicable quality gate. No production or test files changed after the Python run.
