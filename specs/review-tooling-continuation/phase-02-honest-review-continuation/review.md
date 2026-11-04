# Phase 02 Review: Honest Review Continuation

## Scope and evidence

- Reviewed the 10 tracked implementation/test files in the working-tree snapshot (750 changed lines) with `gpt-5.3-codex` and `claude-opus-5.5`, one run each. Both returned usable responses; the merged run was complete (`is_partial: false`, no unavailable models, no unparsed responses).
- The new untracked `tools/tests/test_review_continuation.py` was excluded from the working-tree diff, so it was reviewed separately as the sole staged file with the same two models, one run each. The file was unstaged immediately afterward; `git status --short` confirmed it remained untracked and no staged changes remained. Both reviewers returned usable responses.
- The review command was run from `tools`. Its Go toolchain evidence says `was_run: false` because no `go.mod` exists there. This is Atom's Python tooling repository; the TDD gate previously recorded the full Python suite as 1683 passed, 5 skipped, 95% coverage. This review did not rerun Python tests.
- No production or test fixes were made during review. Findings below are the reviewers' merged results; severity disagreements and spec-aligned behavior are called out rather than silently resolved.

Commands:

```text
python -m atom.cli review --working --model gpt-5.3-codex --model claude-opus-5.5 --runs 1 --json
python -m atom.cli review --staged --model gpt-5.3-codex --model claude-opus-5.5 --runs 1 --concurrency 1 --json
```

The first command returned schema v3 with both models `runs_answered: 1`; the second returned one-file scope (`tools/tests/test_review_continuation.py`) with both models `runs_answered: 1`. Both report `skip_reason: No go.mod found in ...\tools` and no Go gates run.

## High findings

### 1. Control formatting is broader than selected formatting — `tools/atom/review.py:599-600`

**Agreement:** 2/2 models; severity differed (High from GPT-5.3-Codex, Medium from Claude Opus 5.5).

The selected candidate path uses the changed-file formatting gate, while `_run_control_gates` uses the default module-wide `FormatGate` (`gofmt -l .`). An unrelated pre-existing unformatted Go file can therefore fail the control and block an otherwise eligible degraded review, despite the selected changed-file format check passing.

**Disposition: Fixed after approved design amendment.** The developer approved using the same frozen changed Go-file snapshots for control formatting. `run_review` now passes the selected `ChangedFilesFormatGate` to `_run_control_gates`; the verified control runner supplies its own formatter. A regression test proves an unrelated unformatted Go file cannot block continuation.

### 2. Whole-tree fingerprint exceeds the needed review-snapshot scope — `tools/atom/review.py:359`

**Agreement:** 1/2 (Claude Opus 5.5 only; rated High).

Every continuation candidate fingerprints every regular file under the module before gates, and again after control checks. Any symlink, special file, or unreadable file blocks continuation even when the changed source and checks are otherwise valid; large vendor/data trees also increase hashing cost. The approved design explicitly requires whole-module hashing and fail-closed rejection of symlinks/special/unreadable inputs, so those behaviors match the current contract. The performance impact and usefulness of hashing unrelated files remain unmeasured assumptions.

**Disposition: Fixed after approved design amendment.** The developer approved changed-review-Go-file-only identity, and TDD now limits hashing to the frozen `ChangedFilesFormatGate` paths; the accepted blind spot for all other module files remains explicit. The developer chose to fingerprint only changed Go-file paths captured for this review and explicitly accepted that changes to other module files are not detected by this guard. The approved one-run POC confirmed selected-path mutation detection without reading unrelated files in a 1,002-file fixture (`poc-report-review-snapshot-fingerprint.md`). This does not prove whole-module input identity or production integration; the design and tests must state that limitation.

## Medium findings

### 3. `--control-go-version` can be accepted but unused — `tools/atom/cli.py:682`

**Agreement:** 2/2; severity differed (Medium/Low).

The value is validated but is only consumed after a continuation candidate exists. If there is no selected toolchain request (for example, no CLI pin and no project review pin), the control override is silently ignored.

**Suggested fix:** Reject this option when no selected toolchain request exists, or emit a clear warning that it has no effect unless continuation is eligible.

### 4. Candidate short-circuits omit downstream gate states — `tools/atom/review.py:558`

**Agreement:** 1/2 (Claude Opus 5.5 only).

A candidate formatting failure or non-completed build returns only the gates reached so far; later required gates are absent rather than explicitly marked not run/skipped. The design intentionally blocks without running build/control after format failure, but the report does not distinguish these unrun checks from missing evidence.

**Suggested fix:** Preserve the short-circuit behavior while recording remaining gates as skipped/not run with an explicit reason.

### 5. `go.mod` read failures escape without contextual CLI handling — `tools/atom/review.py:607`

**Agreement:** 1/2 (Claude Opus 5.5 only).

`Path.read_text` can raise `OSError` or `UnicodeDecodeError`; these are not converted to the repository's review/toolchain errors and can produce an uncaught traceback instead of an explicit blocked-review diagnostic.

**Suggested fix:** Catch those read/decode errors and raise a contextual error handled by the CLI.

### 6. Strict-mode test accepts either of two unrelated exception paths — `tools/tests/test_review_continuation.py:279`

**Agreement:** 1/2 (Claude Opus 5.5 only).

The test accepts either `ToolchainGateFailed` or `GoToolchainSelectionError`, so a regression that changes the expected failure path can still pass.

**Suggested fix:** Assert the exact expected exception for strict and default cases separately.

### 7. Control fallback test does not provide a valid alternate GOROOT — `tools/tests/test_review_continuation.py:413`

**Agreement:** 1/2 (Claude Opus 5.5 only).

The test's `GOROOT` points to a nonexistent directory. It can pass even if the resolver tries that fallback and fails, so it does not prove that a valid alternate installation is ignored.

**Suggested fix:** Create a valid compatible fixture at the alternate GOROOT and assert the incompatible PATH Go remains the only candidate.

## Low findings

### 8. Repeated gate-result serialization — `tools/atom/report.py:608`

**Agreement:** 1/2. The same gate-result mapping is copied for check, review, and control gate payloads, creating schema-drift risk. **Suggested fix:** Extract one serialization helper.

### 9. Control failure diagnostics omit the control selection — `tools/atom/review.py:409`

**Agreement:** 1/2. `ToolchainGateFailed` receives the selected selection even when control gates fail, obscuring which control distribution failed. **Suggested fix:** Include control selection in the failure evidence.

### 10. Continuation eligibility depends on duplicated summary text — `tools/atom/review.py:576, 688`

**Agreement:** 1/2. A wording change can silently disable the eligibility predicate. **Suggested fix:** Use a shared constant or structured skip reason.

### 11. Version parsing is duplicated and helper rationale is undocumented — `tools/atom/review.py:654`

**Agreement:** 1/2. The model identified duplicated parsing/regex logic and missing helper documentation. **Suggested fix:** Share the parser and document strict rejection conditions if the duplication is confirmed.

### 12. Recursive source traversal has no depth bound — `tools/atom/review.py:785`

**Agreement:** 1/2. An unusually deep tree can raise `RecursionError` outside the `SourceFingerprintError` path. **Suggested fix:** Use iterative traversal or translate recursion failure into the expected blocking error.

### 13. Red-phase callable assertions remain in tests — `tools/tests/test_review_continuation.py:40`

**Agreement:** 1/2. `getattr(..., None)` plus `callable` assertions are inconsistent with direct access elsewhere and hide typos. **Suggested fix:** Use direct calls.

### 14. Test setup relies on helper dictionary insertion order — `tools/tests/test_review_continuation.py:333`

**Agreement:** 1/2. `tuple(runner.scripted_results)` assumes the fixture's command insertion order. **Suggested fix:** Name the expected probe commands explicitly.

### 15. Similar `ScriptedGate` fakes are repeated — `tools/tests/test_review_continuation.py:464`

**Agreement:** 1/2. Local fakes have slightly different signatures across tests. **Suggested disposition:** Refactor only if a shared helper makes the cases clearer; this is a maintainability suggestion, not a behavior defect.

### 16. Test fixture setup duplicates version/environment probe overrides — `tools/tests/test_review_continuation.py:597`

**Agreement:** 1/2. Similar test setup appears in multiple locations. **Suggested disposition:** Consolidate only if it improves clarity; not a correctness issue.

### 17. Unused values in skipped-control test — `tools/tests/test_review_continuation.py:723`

**Agreement:** 1/2. `passing_results[0]` and `control_binary` are unused. **Suggested fix:** Remove them or use them to clarify the fixture.

## Triage status

High finding #1 is resolved after the developer-approved design amendment. The focused RED test demonstrated the unrelated-file failure, the implementation now formats the selected frozen snapshots with the control distribution, and the final Python suite passed: 1684 passed, 5 skipped, 95% coverage. `git diff --check` was clean.

High finding #2 has a developer-selected scope, a Confirmed bounded POC, an approved design amendment, and a passing implementation. Findings #3-17 remain untriaged. The new scope intentionally does not detect changes outside the selected changed-Go-file set.
## Follow-up review and nested-module path correction (2026-11-03)

A supplementary fixed-evidence review used `gpt-5.3-codex` and `claude-opus-5.5` (one completed response each; `--skip-toolchain` was used because the implementation is Python and the `tools` directory has no `go.mod`). The result contained no corroborated findings. It did not independently repeat the repository-relative/module-relative path mismatch identified in the earlier follow-up. Direct inspection and a real-Git regression test confirmed that `capture_review_diff` supplied `FormattingFile(name, content)` where `name` was repository-relative (for example `service/changed.go`), while `_fingerprint_review_snapshot` resolved from the selected module root (`service`). That made it probe `service/service/changed.go` and block eligible nested-module continuation.

**Disposition: Fixed after developer approval.** The new integration test first failed on the path mismatch, then passed after `FormattingFile` was given the already-computed module-relative `relative` path. `CapturedDiff.files` remains repository-relative for review presentation. The path change does not broaden the accepted fingerprint scope.

The supplementary reviewers also reported the following uncorroborated items; they are not fixed here and remain for developer triage:

- One reviewer rated uncaught `go.mod` filesystem/decoding errors High; another reported the same read path at Medium.
- Medium: candidate early returns do not record downstream gates as skipped; a selected build error may be replaced by a control-resolution error; non-UTF-8 control `VERSION` data may bypass the typed error path; and the accepted changed-Go-only fingerprint omits `go.mod`/`go.sum` (the latter is within the developer-approved blind spot).
- Low: re-bound environment clarity; `format_gate` type assumptions; an unused `--control-go-version`; repeated gate serialization; duplicated eligibility summary strings; PATH provenance in control selection; version-parser duplication/documentation; recursive traversal depth; and test fixture/assertion maintainability suggestions.

Verification for the path correction:

```text
python -m pytest tests/test_review_formatting.py -k nested_module_snapshot_paths_are_fingerprintable -q
1 passed, 66 deselected

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q
151 passed

python -m pytest tests -v --cov=atom
TOTAL                        4716    235    95%
================= 1687 passed, 5 skipped in 244.85s (0:04:04) =================

git diff --check
git diff --check: clean
```
## Fresh multi-model review of the nested-module path fix (2026-11-03)

Command:

```text
python -m atom.cli review --working --model gpt-5.3-codex --model claude-opus-5.5 --runs 1 --concurrency 1 --skip-toolchain --fixed-evidence --context-file tests/test_review_continuation.py --json
```

Both models returned usable responses (one run each); the review was complete, but no finding was corroborated. The toolchain was intentionally skipped because this is the Python tooling module. The working diff contained 801 changed lines across 11 tracked files; the untracked continuation test was supplied as fixed evidence.

### Findings requiring triage

- **Current-directory Go lookup (High, one model): rejected.** The claim was that Windows `shutil.which` could select `go.exe` from the current directory despite an explicit PATH. Reproduction on Python 3.13.14 / Windows placed a `go.exe` in the current directory and supplied a different empty directory as `path`; `shutil.which("go", path=...)` returned `None`. The implementation also passes the explicit environment PATH.
- **Baseline fingerprint does not prove captured-snapshot identity (Medium, one model): confirmed, awaiting disposition.** The initial digest reads current file bytes, not `FormattingFile.content`. A file edited after diff capture but before the initial digest can differ from the content formatted from the frozen snapshot, while the before/after live-file fingerprints remain equal. A local probe reproduced this: captured bytes differed from live bytes, yet two fingerprints of the unchanged live file were equal. This is not the accepted out-of-scope change to unselected files; it concerns a selected snapshot path.
- **`go.mod` read/decode errors escape the CLI path (Medium, one model): confirmed by source inspection, awaiting disposition.** `_read_module_minimum_version` directly calls `Path.read_text` without handling `OSError` or `UnicodeDecodeError`.
- **Control failure output omits the control selection (Medium, one model): awaiting disposition.** `ToolchainGateFailed` is constructed with `toolchain.selection` when control gates fail, so the control distribution is not included in that failure evidence.
- **Low findings (one model each):** fabricated completed lifecycle evidence for an empty/skipped format scope; validation-only `GoToolchainRequest` construction; duplicated gate serialization; ignored control-version override when continuation is ineligible; advisory analyzer work after selected build failure; duplicated eligibility summary literal; and PATH control provenance labeled as CLI.

The first of these new findings is rejected with reproduction evidence. The selected-snapshot baseline, `go.mod` error handling, and control-failure evidence findings remain open for developer triage. Prior review findings still marked open above also remain in scope. No additional code changes were made during this review pass.
## Snapshot-baseline finding: TDD disposition

The developer approved a working-only consistency check: for `DiffSource.WORKING`, the initial live-file fingerprint must match the captured formatter bytes. Staged and branch reviews may intentionally format Git blobs different from the live worktree, so those modes retain their prior live-file fingerprint behavior.

`test_initial_fingerprint_matches_captured_bytes_only_for_working_source` produced a clean RED: before the implementation, the working case did not raise `SourceFingerprintError` when the live file was changed after capture, while the staged case remained allowed. The implementation now hashes the live selected path and compares that digest with the captured bytes before selected checks; later control fingerprinting continues to compare live disk state against the baseline. The Windows fixture was adjusted to write exact LF bytes because `Path.write_text` translated the fixture to CRLF; this made the fixture match its declared captured snapshot rather than weakening assertions.

Verification:

```text
python -m pytest tests/test_review_continuation.py -k initial_fingerprint_matches_captured_bytes_only_for_working_source -q --tb=short
====================== 2 passed, 61 deselected in 6.26s ======================

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q --tb=short
============================ 153 passed in 48.06s ============================

python -m pytest tests -v --cov=atom
TOTAL                        4718    235    95%
================= 1689 passed, 5 skipped in 235.25s (0:03:55) =================
```
## Fresh review after working-snapshot baseline fix (2026-11-03)

Command:

```text
python -m atom.cli review --working --model gpt-5.3-codex --model claude-opus-5.5 --runs 1 --concurrency 1 --skip-toolchain --fixed-evidence --context-file tests/test_review_continuation.py --json
```

Both models returned usable responses (one run each); the review was complete and none of the findings was corroborated. The toolchain was skipped because `tools` is the Python tooling module. The diff contained 818 changed lines across 11 tracked files; the untracked continuation tests were supplied as fixed evidence. Neither model repeated the selected-snapshot baseline finding addressed by the latest TDD change.

### New findings and dispositions

- **Control resolution errors replace the selected build failure (Medium, one model): open.** If the selected build fails and control selection fails, the resolver exception can become the only reported error, hiding the selected failure evidence. A related single-model report noted that control-gate failures carry selected rather than control selection provenance.
- **`go.mod` read/decode errors escape (Medium, one model each): open.** `_read_module_minimum_version` performs unguarded `Path.read_text`; I/O or UTF-8 failures can escape without the review-specific diagnostic path.
- **Fingerprint excludes `go.mod`, `go.sum`, and unchanged packages (Medium, one model): accepted scope limitation.** This remains the developer-approved changed-Go-file-only contract, not a new implementation defect to fix within this scope.
- **Exact skip-summary text is part of candidate recognition (Medium, one model): open as a maintainability concern.** A text change would fail closed by disabling continuation; it does not turn an unsafe case into an eligible one.
- **Low findings (one model each):** control environment rebinding clarity; nested-module formatter path display differing from repo-relative diff display; ignored control-version override when no continuation candidate exists; repeated gate serialization; omitted downstream records after candidate formatting failure (the early stop matches the approved spec); and missing rationale comment for the structured eligibility predicate.

No code changes were made during this review pass. The prior current-directory PATH lookup claim remains rejected by its recorded Windows reproduction. The baseline consistency fix is implemented and its TDD evidence is recorded above; the remaining open actionable findings are available for developer triage.
## `go.mod` read-error finding: TDD disposition

The developer approved fixing the unhandled module-minimum read path. `test_module_minimum_version_read_failures_are_contextual` first failed for both injected cases because `PermissionError` and `UnicodeDecodeError` escaped. `_read_module_minimum_version` now wraps those failures in the existing `ControlToolchainError`, including the `go.mod` path; the CLI already handles that exception and returns a nonzero diagnostic. Malformed/ambiguous version directives still return `None`.

```text
python -m pytest tests/test_review_continuation.py -k module_minimum_version_read_failures_are_contextual -q --tb=short
====================== 2 passed, 63 deselected in 1.42s ======================

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q --tb=short
============================ 155 passed in 52.69s ============================

python -m pytest tests -v --cov=atom
TOTAL                        4721    235    95%
================= 1691 passed, 5 skipped in 246.67s (0:04:06) =================
```

## Fresh multi-model review after contextual `go.mod` error fix

Command:

```text
python -m atom.cli review --working --model gpt-5.3-codex --model claude-opus-5.5 --runs 1 --concurrency 1 --json
```

Both distinct models returned usable responses (one run each); the review was complete with no unavailable models or unparsed responses. It covered 12 changed files and 1,780 changed lines, including the continuation regression test. The toolchain block reports `was_run: false` and `No go.mod found in ...\tools`; this repository's implementation is Python, so the Go gate was not applicable. The TDD full Python suite remains the verification evidence for the implementation.

### High

1. **`tools/atom/review.py:852` — selected-path symlink race (1/2, GPT-5.3-Codex).** Path components were checked for symlinks before the file was opened by pathname. A concurrent replacement could redirect the fingerprint read. **Disposition: Fixed after developer approval.** The opened descriptor is now required to match the final `lstat` device/inode identity. A regression test simulating a redirected open failed before the change and passed afterward; TDD evidence follows below.

### Medium

2. **`tools/atom/review.py:362` — staged/ref blob differs from live source (1/2, Claude Opus 5.5).** The control fingerprint uses live worktree bytes even when formatting consumed captured Git blobs. **Disposition: matches the explicitly approved B7 limitation.** B7 and the decisions artifact state that staged/branch snapshot equality with live worktree inputs is not established.
3. **`tools/atom/review.py:400` — unselected module inputs are not fingerprinted (1/2, Claude Opus 5.5).** Changes to `go.mod`, `go.sum`, or unchanged packages can affect module-wide gates without changing the selected changed-Go-file fingerprint. **Disposition: matches the developer-approved changed-Go-file-only scope and its documented blind spot.**
4. **`tools/atom/review.py:739` — invalid UTF-8 in the PATH Go `VERSION` file escapes typed handling (1/2, Claude Opus 5.5).** The read catches filesystem and runtime errors but not `UnicodeDecodeError`; this can bypass the contextual `ControlToolchainError` path. Open for developer triage.

### Low

5. **`tools/atom/cli.py:682-683` (1/2, Claude Opus 5.5).** `--control-go-version` may be unused without a selected-toolchain pin; the validation-only request construction may look dead to maintainers.
6. **`tools/atom/report.py:608` (1/2, Claude Opus 5.5).** Gate-result serialization is repeated in multiple payloads.
7. **`tools/atom/review.py:418` (1/2, Claude Opus 5.5).** Control gate failure evidence omits the resolved control selection.
8. **`tools/atom/review.py:547` (1/2, Claude Opus 5.5).** Advisory checks still run after a selected build failure.
9. **`tools/atom/review.py:569` (1/2, Claude Opus 5.5).** Candidate early returns do not explicitly represent downstream gates as skipped.
10. **`tools/atom/review.py:708` (1/2, Claude Opus 5.5).** Eligibility depends on matching a duplicated summary string.

No finding was corroborated by both models. The previously fixed `go.mod` read/decode finding and working-snapshot baseline finding were not re-reported. The High finding is fixed; the unaccepted Medium finding about invalid UTF-8 in the PATH Go `VERSION` file remains for developer triage. Lower-priority suggestions are recorded here and have not been changed.


## Selected-path replacement finding: TDD disposition

The developer approved fixing the uncorroborated High finding. The regression test substitutes an outside file handle at the open boundary, representing a selected path redirected after pathname validation. Before the fix, the fingerprint accepted that handle; after the fix, a device/inode mismatch raises `SourceFingerprintError` before reading.

RED:

```text
python -m pytest tests/test_review_continuation.py -k path_replaced_before_open -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\.copilot\session-state\7a134ae3-c5ed-4cc4-8f25-18c948d3df93\files\atom-v1-review-continuation\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 66 items / 65 deselected / 1 selected

tests\test_review_continuation.py F                                      [100%]

================================== FAILURES ===================================
_______ test_review_snapshot_identity_rejects_path_replaced_before_open _______
tests/test_review_continuation.py:596: in test_review_snapshot_identity_rejects_path_replaced_before_open
    with pytest.raises(review_module.SourceFingerprintError, match="between validation and opening"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE SourceFingerprintError
=========================== short test summary info ============================
FAILED tests/test_review_continuation.py::test_review_snapshot_identity_rejects_path_replaced_before_open
====================== 1 failed, 65 deselected in 3.56s =======================
```

Focused GREEN:

```text
python -m pytest tests/test_review_continuation.py -k 'path_replaced_before_open or review_snapshot_identity' -q --tb=short
============================= test session starts ==============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
collected 66 items / 60 deselected / 6 selected

tests\test_review_continuation.py ......                                 [100%]
====================== 6 passed, 60 deselected in 4.71s =======================

python -m pytest tests/test_review_formatting.py tests/test_review_continuation.py tests/test_review_toolchain.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\.copilot\session-state\7a134ae3-c5ed-4cc4-8f25-18c948d3df93\files\atom-v1-review-continuation\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 156 items

tests\test_review_formatting.py ........................................ [ 25%]
...........................                                              [ 42%]
tests\test_review_continuation.py ...................................... [ 67%]
............................                                             [ 85%]
tests\test_review_toolchain.py .......................                   [100%]

======================= 156 passed in 119.69s (0:01:59) =======================
```

The approved B7 scope remains unchanged. This check closes the selected-file pathname replacement window detected by the reviewer; it does not expand the fingerprint to other module inputs.

Full-suite verification:

```text
python -m pytest tests -v --cov=atom
TOTAL                        4723    235    95%
================= 1692 passed, 5 skipped in 539.82s (0:08:59) =================
```

## Fresh complete two-model review after selected-path race fix

Command:

```text
python -m atom.cli review --working --model gpt-5.3-codex --model claude-opus-5.5 --runs 1 --concurrency 1 --json
```

Both models returned usable responses, one run each. This complete run included the new `test_review_continuation.py` (12 files, 1,810 changed lines), unlike the earlier incomplete run that omitted the untracked test. The Go toolchain section was not run because `tools/` is Python and has no `go.mod`; Python verification is recorded in the TDD evidence above.

### Medium

- **`tools/atom/cli.py:682-683` — control override accepted but unused without selected pin (Claude Opus 5.5).** The CLI accepts `--control-go-version` without `--go-version`/`--go-executable`, but a control is only needed for a continuation candidate requiring an explicit selected toolchain. Triage against the approved public CLI contract.
- **`tools/atom/review.py:344` — module minimum read twice (Claude Opus 5.5).** `_is_continuation_candidate` and `run_review` separately read/parse `go.mod`. Considered with B7's explicit limitation that inputs outside changed Go paths are not fingerprinted; not changed in this pass.
- **`tools/atom/review.py:585` — free-text skip summary is used as eligibility state (Claude Opus 5.5).** A wording change could disable continuation; this is a maintainability concern and was not changed.
- **`tools/atom/review.py:735` — PATH Go `VERSION` decoding error escapes typed handling (Claude Opus 5.5).** `UnicodeDecodeError` is not caught with the filesystem/runtime errors and could produce a traceback instead of `ControlToolchainError`. Open for developer triage.
- **`tools/atom/review.py:735` — requiring a sibling `VERSION` file may reject some otherwise valid Go installations (GPT-5.3-Codex).** One-model report; the current approved design requires exact version/distribution verification. No change made pending triage.

### Low

- **`tools/atom/report.py:608` (Claude Opus 5.5):** repeated gate-result JSON serialization.
- **`tools/atom/review.py:387` (Claude Opus 5.5):** selected/control environment rebinding merits clarification.
- **`tools/atom/review.py:563` (Claude Opus 5.5):** early candidate gate exits omit rows for downstream skipped gates; the early-stop behavior matches the approved spec.
- **`tools/atom/review.py:617` (Claude Opus 5.5):** block comments containing a `go`-looking line may be parsed as directives.
- **`tools/atom/review.py:780` (Claude Opus 5.5):** exact control override path should explicitly confirm verified selection status.

The selected-path replacement High finding was not re-reported after the descriptor identity fix. No finding was corroborated on the exact same issue by both reviewers. The report about the changed-Go-file-only fingerprint omitting module inputs is an already accepted B7 limitation and is not reopened here. No code changes were made during this review pass.

## PATH VERSION decode finding: TDD disposition

The developer approved the Medium finding fix test-first. `_resolve_path_control_toolchain` now includes `UnicodeError` in the contextual control-distribution read handler, preserving the existing `ControlToolchainError` contract.

RED:

```text
python -m pytest tests/test_review_continuation.py -k path_control_version_decode_failure_is_contextual -q --tb=short
E   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
====================== 1 failed, 66 deselected in 3.45s =======================
```

The first GREEN attempt exposed an overly specific test expectation: Windows resolved the fixture executable as `go.EXE` while the test fixture's `Path` displayed `go.exe`. The error was already contextual; the assertion now checks the stable executable-directory context rather than filename casing. This is a fixture correction, not a weaker behavior assertion.

GREEN:

```text
python -m pytest tests/test_review_continuation.py -k 'path_control_version_decode_failure_is_contextual or default_control_resolves_and_verifies_direct_path_distribution' -q --tb=short
====================== 2 passed, 65 deselected in 21.49s ======================
```

No design change was needed: the approved contract already requires control selection failures to block with contextual diagnostics. The one-model report that some installations may lack a sibling `VERSION` file remains open for triage; it is a separate concern.

## Fresh multi-model review after PATH VERSION and CLI override fixes

The complete working-tree review used `gpt-5.3-codex` and `claude-opus-5.5`, one run each. Both returned usable responses; only Claude reported findings, so none was corroborated. The diff covered 12 files and 1,853 changed lines. The review was launched from `tools`; its Go gate reports `was_run: false` because `tools` has no `go.mod`. Python verification is recorded separately below.

The full Python suite completed after the latest CLI change:

```text
TOTAL                        4725    233    95%
================= 1694 passed, 5 skipped in 238.84s (0:03:58) =================
```

### High

1. **`tools/atom/review.py:366` — staged/branch review checks may use live worktree bytes unlike the reviewed snapshot (one model).** The snapshot consistency comparison is intentionally enabled only for `DiffSource.WORKING`; staged and branch diffs can format captured Git blobs while module-wide checks run on the working tree. This matches the explicitly approved B7 limitation in `design-spec.md`: staged/branch snapshot equality with live module-check inputs is not established. No change was made.

### Medium

2. **`tools/atom/review.py:388` — control-selection failure can hide selected build failure evidence (one model).** If no compatible control toolchain resolves, `ControlToolchainError` or `GoToolchainSelectionError` can escape before a `ToolchainGateFailed` report combines the control-selection failure with the selected build failure and selection evidence. The user-facing diagnostic may contain only the control resolution error. This remains open for developer triage.
3. **`tools/atom/review.py:403` — fingerprint omits module inputs outside changed Go files (one model).** Changes to `go.mod`, `go.sum`, unchanged packages, or test data are not fingerprinted. This is the explicitly approved changed-Go-file-only scope, not a new deviation.
4. **`tools/atom/review.py:707` — eligibility compares duplicated skip-summary text (one model).** A future wording change could disable continuation; this fails closed. A shared structured reason would reduce coupling. Open as a low-risk maintainability concern.

### Low

5. **`tools/atom/_review_format.py:258` — nested-module formatting errors may display a module-relative path while diff output uses a repository-relative path (one model).**
6. **`tools/atom/cli.py:683` — a `GoToolchainRequest` is constructed only to validate the version and discarded (one model).**
7. **`tools/atom/report.py:608` — control-gate serialization duplicates the selected-gate mapping (one model).**
8. **`tools/atom/review.py:668` — module minimum parsing occurs in candidate classification and again in `run_review` (one model).**
9. **`tools/tests/test_cli_review.py:251` — `captured = {}` appears twice consecutively (one model).**

The earlier findings for PATH `VERSION` invalid UTF-8 and a control-version override without a selected pin were not re-reported; both fixes are present and covered by the current full suite. No code change was made during this review pass.
### Triage

The developer deferred Medium finding #2 (control-selection failure can hide selected build failure evidence) and chose to proceed to the TDD completion gate. No rationale was provided; no fix was made. The accepted B7 snapshot limitations remain as specified above. The five Low findings are not fixed and remain documented for future consideration.
