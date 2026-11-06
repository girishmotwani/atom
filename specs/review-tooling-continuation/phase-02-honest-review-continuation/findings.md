---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-03"
---

# Findings

## Remaining review items

The supplementary multi-model review and its single-model findings are recorded in `review.md`. They remain untriaged except for the nested-module path mismatch, which was confirmed by a failing integration test and fixed. In particular, the report raised an uncorroborated High concern about uncaught `go.mod` read/decode errors, several uncorroborated Medium concerns about gate/error evidence, and lower-priority maintainability observations. The accepted limitation that files outside the selected changed-Go-file set are not fingerprinted is intentional and is documented in the approved design; it is not being represented as a fix.
## Fresh review findings awaiting disposition

The new review found a selected-snapshot race: the baseline digest reads live disk bytes rather than the frozen `FormattingFile.content`, so a selected Go file can change after capture but before the first digest without detection. A local reproduction confirmed that snapshot bytes can differ while repeated live-file fingerprints remain equal. This is distinct from the explicitly accepted blind spot for files outside the selected changed-Go-file set.

The review also identified unhandled `go.mod` read/decode errors and loss of control-toolchain identity in control-failure evidence. These are uncorroborated by the second model and remain open. The one-model High claim that Windows PATH lookup searches the current directory despite explicit `path=` was rejected after a Python 3.13.14 Windows reproduction returned `None` for a current-directory `go.exe` and a different empty PATH directory.
## Snapshot-baseline mismatch disposition

The selected working-tree snapshot mismatch is fixed: the initial live fingerprint must match the captured formatter bytes for `--working`, and a mismatch blocks before selected gates. Staged/branch equality remains intentionally unenforced per the approved scope decision. Other findings awaiting developer triage remain: contextual handling for unreadable/undecodable `go.mod`, control-selection identity in control failure output, and the other items listed in `review.md`.
## Latest review disposition

The working-tree snapshot baseline mismatch is fixed and covered by the working-vs-staged regression; the latest multi-model pass did not re-report it. Remaining actionable items are the unguarded `go.mod` read/decode failure path and preservation of selected/control failure provenance. The approved changed-Go-file-only fingerprint intentionally does not detect `go.mod`, `go.sum`, or unchanged package mutations. Lower-priority one-model observations and their spec-aligned dispositions are recorded in `review.md`.
## Module-minimum read-error disposition

The unguarded `go.mod` read/decode finding is fixed. Filesystem and UTF-8 failures now produce a contextual `ControlToolchainError`, which the CLI handles as a blocked review. The control-failure provenance finding and lower-priority review observations remain open; see `review.md`.

## Fresh review findings awaiting triage

The latest complete two-model pass produced an uncorroborated High about symlink replacement between validation and open at `tools/atom/review.py:852`; this is fixed by comparing the opened descriptor identity with the checked path identity, covered by a regression test. The uncorroborated Medium about invalid UTF-8 in the PATH Go `VERSION` read at `tools/atom/review.py:739` remains open for triage.

Two other Medium reports are already accepted limitations in the approved B7 design: staged/branch Git snapshots may differ from live module-check inputs, and the changed-Go-file-only fingerprint omits `go.mod`, `go.sum`, and unchanged packages. Six Low observations are detailed in `review.md`; they are not fixed. The `go.mod` read-error and working-snapshot baseline findings previously approved and fixed were not re-reported.

The snapshot replacement finding is closed by the open-handle identity check and its test-first evidence in `review.md`. The invalid-UTF-8 PATH `VERSION` finding remains open.

## Review after selected-path replacement fix

A complete two-model review included the new regression test and did not re-report the selected-path replacement High finding. Open for developer triage: the PATH Go `VERSION` invalid-UTF-8 error path (Medium) and whether `--control-go-version` should be rejected when no selected toolchain is explicitly pinned (Medium). The report also noted the one-model possibility that some Go installations lack the sibling `VERSION` file; the approved design currently requires exact distribution verification. Lower-priority findings and accepted dispositions are detailed in `review.md`.

The Go gate was not applicable to `tools/` because the repository implementation is Python; the focused and full pytest outputs are recorded in the TDD evidence. The changed-Go-file-only fingerprint's known module-input blind spots remain explicitly accepted under B7.

## PATH VERSION decode finding closed

The PATH Go distribution `VERSION` decode finding is fixed: `UnicodeDecodeError` now follows the existing contextual `ControlToolchainError` path, covered test-first by `test_path_control_version_decode_failure_is_contextual`. RED/GREEN evidence is in `review.md`. The separate one-model question about Go installations without a sibling `VERSION` file remains open, as does the CLI behavior for `--control-go-version` without an explicitly pinned selected toolchain.

## Fresh review disposition

The latest complete two-model review reported one uncorroborated High, three Medium, and five Low findings. The High staged/branch snapshot-versus-live-worktree mismatch is an accepted B7 limitation: the approved design explicitly says those modes do not establish equality. The changed-Go-file-only fingerprint blind spot is likewise approved scope, not a new issue.

The Medium control-resolution evidence item was deferred by the developer before the TDD completion gate; the exception may obscure the selected build failure and omit selection evidence. No code change was made. The duplicated skip-summary text is a fail-closed maintainability concern; the remaining Low observations are in `review.md`.

The prior PATH `VERSION` invalid-UTF-8 finding is closed by contextual `ControlToolchainError` handling and its regression test. The `--control-go-version` without an explicit selected-toolchain pin finding is closed by CLI validation and regression coverage. After both changes, `python -m pytest tests -v --cov=atom` reported `1694 passed, 5 skipped` and `95%` coverage.
