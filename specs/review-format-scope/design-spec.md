---
project: "review-format-scope"
date: "2026-10-23"
status: "accepted-under-scoped-waiver"
---

# Design: changed-file formatting for review

## Established and still assumed

Established by [the executed proof](poc-report.md): real Git can identify changed paths without losing rename/Unicode/space names; working, index and committed content are distinct; formatting selected content over stdin ignores untouched defects and still detects changed-file defects; standalone FormatGate continues to fail an untouched defect. All 14 fixed observations passed, original/tooling audits matched and the owned fixture was removed.

Production assumptions to verify with regression tests: raw Git metadata and the matching patch can be captured together; immutable blob IDs identify staged/branch content; working bytes can be checked against the captured patch's Git blob identity; binary-safe blob transport is necessary to preserve UTF-8 and mixed line endings before formatting normalization. The proof did not establish general repository/filter/module orchestration, production compatibility or model quality.

## Public contract and scope

No CLI flag, run_review signature or existing JSON gate field changes. Only review formatting changes. Standalone atom check and default_gates remain module-wide. Build, vet, tests, race and optional checks keep their existing commands, working directory, required/advisory status and failures. Reading unchanged code as context remains allowed; accepted finding paths still follow the captured diff.

The review must capture its selected diff before evaluating gates so formatting has an exact scope. A Git/snapshot failure blocks review before model calls rather than guessing a scope. The new private helper is used only for a Go-module review with toolchain checks enabled. Non-module and explicit skip-toolchain paths retain their existing unchecked evidence and ordinary diff capture.

## Internal interfaces

One private helper module separates review snapshot acquisition from the unchanged general gate implementation. These are internal composition contracts, not new public CLI APIs:

```python
@dataclass(frozen=True)
class FormattingFile:
    path: str
    content: bytes

class ChangedFilesFormatGate:
    name = "fmt"
    required = True

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult: ...

def capture_review_diff(
    request: DiffRequest,
    runner: CommandRunner,
    working_directory: Path,
) -> tuple[CapturedDiff, ChangedFilesFormatGate]: ...
```

The helper returns a captured patch plus a gate owning immutable selected content and coverage information. CapturedDiff may carry an optional private canonical path tuple; its existing text/request positional construction and legacy parser remain valid. A raw Git manifest supplies complete paths for pure rename/binary entries without interpreting quoted patch filenames. The public run_review interface and result types stay unchanged.

## Independently verifiable behavior

1. Review formatting checks only surviving changed `.go` files belonging to the selected module, not untouched files. Each selected file is formatted as a whole, not just added lines.
2. Working mode checks captured working bytes; staged mode checks immutable index blob content, even when the working file differs or is absent; branch mode checks the committed content in the captured branch diff despite dirty working files.
3. Capture one canonical raw-metadata-plus-patch diff. Staged/branch bytes are read by immutable Git object ID; working bytes must match the selected patch identity. Detected movement, malformed metadata or an unavailable input fails visibly before models.
4. New and rename-destination Go files are included, including pure renames and moves from a non-Go extension. Deleted Go files are explicitly inapplicable. Untracked working files remain outside `git diff`, as before.
5. NUL-delimited metadata preserves spaces and Unicode without shell splitting. Resolve repository-relative paths correctly when invoked below the Git root. Reject unsafe/non-regular source paths rather than follow an outside-file substitution.
6. Preserve the existing selected-module boundary: files outside it or under nested Go modules are not silently treated as formatted. Coverage evidence names exclusions; the prompt's formatting exclusion is limited to checked files. This does not implement multi-module orchestration.
7. An empty diff, non-Go-only diff or deletion-only Go diff emits a SKIPPED fmt result with explicit zero-file coverage and no gofmt command. Other gates remain unchanged.
8. Format selected UTF-8 source via stdin without `-w`, normalize CRLF for the formatting comparison only, and never rewrite source/index/configuration. Preserve genuine formatting differences in CRLF or mixed-ending files. Invalid UTF-8 is a visible required formatting failure, not replacement-decoded success.
9. A completed gofmt process whose output differs from selected normalized content produces a required fmt failure naming the path. A zero exit code alone is not a pass.
10. Missing formatter, timeout, runner error and formatter syntax/process errors produce required failures with the original outcome/output diagnostic and path. Do not turn input acquisition errors or an empty response into a successful empty scope.
11. A changed-file formatting failure still stops model calls; failures from unchanged build/vet/test/race gates also still stop models. Existing optional tool semantics remain unchanged.
12. Toolchain JSON/Markdown summaries state selected-file formatting coverage and source mode. Prompts do not claim `gofmt -l .` ran or that unchecked files passed; SKIPPED fmt excludes no formatting category.
13. Source/diff capture is shared across all model invocations, not repeated per reviewer. Existing report sizes and accepted finding paths use the canonical manifest when available.
14. No existing runner contract, package dependency, global Git setting or ambient model instructions change. Standalone FormatGate/default_gates retain their exact behavior.

## Acquisition and errors

Git raw status and its patch must describe the same capture. Use full object IDs, raw NUL framing, no external diff/text conversion and no relative-path presentation. Parse status/modes strictly; an unmerged or malformed capture raises DiffUnavailable with context, not an empty diff. Branch input refs are resolved as commits safely before forming revision expressions.

Staged/branch source reads use object IDs, not moving refs/index paths. To keep CommandRunner's existing seven-field text result contract while preserving raw blob bytes, use a fixed small Python byte-to-base64 transport around read-only Git. That helper and its Git child remain descendants owned by the existing runner; there is no shell, new background process, unowned fallback or dependency. Validate framing, base64 and Git blob identity before accepting bytes. This is a production integration choice to verify in TDD, not a claim the proof tested arbitrary encodings.

Working inputs are read as bytes from validated in-module regular paths and compared to the captured Git object identity, accounting only for Git's ordinary CRLF normalization. Arbitrary transforming filters or inconsistent snapshots cannot silently pass; reject unsupported mismatches with a clear DiffUnavailable diagnostic. Go parsing/formatting errors belong to the required fmt gate. All existing per-command runner deadlines and cleanup guarantees apply; introduce no larger deadlines or silent retries.

## Concurrency and ownership

Acquisition is serial before toolchain evaluation; selected file bytes and scope are immutable for the rest of the review. No worker/thread is added. Existing model concurrency begins only after required checks pass and receives the same captured patch/evidence. Concurrent source/index changes cannot substitute different bytes into the formatter; detected inconsistency blocks. This is not a lock against other programs changing a repository, nor a promise that arbitrary checkout mutation can be made atomic.

## Trade-offs and extension

Reject globally narrowing FormatGate (it would weaken atom check), scanning the whole module then filtering only its failure list (it would still inspect unrelated files), skipping formatting entirely, patch-header-only file selection (misses pure renames/quoted names), and reading current files for every diff mode (checks the wrong snapshot). The private scoped gate composes with the existing Gate protocol; leave the general runner and shared gate defaults intact.

Build/test snapshot policy, affected-package checks, rule resolution, richer reviewer output and the ADO workflow remain out of scope. They are not implied to pass after this correction. The scoped routine-gate waiver authorizes implementing this evidence-grounded spec without another pause; it does not waive blockers or permit a material expansion.

## Validation

Test observable review behavior first through the existing public run_review/CLI with real temporary Git and gofmt, replacing only Go build/test and model boundaries in scoped integration tests. Add deterministic error/path/encoding cases and preserve standalone controls. Record a real RED before source edits, then GREEN, full Python pytest/coverage, packaging and supported-platform CI evidence using existing tooling. No target-repository check or model probe is part of this fix's proof.

## Implementation reconciliation

The implementation retains the planned private helper and gate composition. CapturedDiff carries an optional private canonical-path tuple while preserving text/request construction. ToolchainEvidence carries an internal formatting-scope flag; JSON adds a toolchain evidence object using existing gate fields without changing pre-existing fields. Raw type changes consume their deletion/addition patch pair. Capture pins --submodule=short so ambient Git submodule presentation cannot change framing; it does not change user configuration or implement submodule formatting. Basic relative manifest validation is separate from native source safety restrictions, which apply only to surviving in-module Go files that will be read. Unread non-Go/deleted/outside paths remain in canonical report scope. These details reconcile verified integration choices within behaviors 3-7 and 12-14, not a material contract expansion. Both independent review findings are fixed; fresh local full output is in verification.md.
