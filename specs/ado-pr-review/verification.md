# ADO review verification

## Runtime gate

Command from tools: `python -m pytest tests -v --cov=atom --cov-report=term-missing`.

The validated runtime/test tree produced this verbatim summary:

```text
================= 1465 passed, 2 skipped in 307.98s (0:05:07) =================
TOTAL                        4107    218    95%
```

The two skips are existing Windows-disabled Popen/group/interrupt cases with native equivalents in test_windows_process.py. The suite includes packaging, native Windows lifecycle checks, ADO checkout/error handling, both review modes, changed-file snapshot checks, and repeat-init regressions.

The artifact cleanup leaves every tracked tools file and README byte-identical to that validated tree; this is not a newly repeated full gate. The source/test/README snapshot SHA-256, over sorted Git paths and blob bytes separated by NUL, is `2357e5e912a8d41b4ffa4db51a6125c27916cf67c299315912e4fa148d76694e`.

## Maintained contracts

- [Native ADO entry](native-pr-entry/design-spec.md) and [test map](native-pr-entry/test-spec.md).
- [Ownership-aware responses](review-output-isolation/design-spec.md), [test map](review-output-isolation/test-spec.md), and [synthetic transport result](review-output-isolation/poc-report.md).
- [MCP exclusion forwarding](probe-exclusion-forwarding/design-spec.md) and [test map](probe-exclusion-forwarding/test-spec.md).
- [Fixed-evidence review](bounded-review-execution/design-spec.md), [test map](bounded-review-execution/test-spec.md), and [synthetic tool-exclusion result](bounded-review-execution/poc-report-source-exclusions.md).

The fixed-evidence/formatting regression confirms one diff capture and caller-evidence prompt without an untouched formatting defect blocking review. The PR-required-check fixture exercises both modes with compiler-failure, no-output, no-model, and owned-checkout cleanup assertions intact.

## Artifact validation

The existing documentation checker was run after pruning:

```text
checked 297 relative links across markdown files
all relative links resolve
```

The Git comparison of tools and README against the locally tested tree exited 0 with no output. The independently recomputed staged source/test/README digest matches the runtime-gate digest above.

`git diff --check public/main -- . ':(exclude)poc/bounded-review-execution/source_exclusions_spike.py'` exited 0 with no output. The only exclusion is the frozen executed spike: its existing whitespace-only fixture line and blank EOF are intentionally preserved, with SHA-256 `84711dbf5032c4016f0836074c68e35eab63a93b276f54cc0d71f9e15a7224ef` verified against its staged Git bytes.

Full execution logs remain outside the committed tree; the runtime summary above is an explicitly identified excerpt, not a reconstructed full transcript.

## Hosted CI blocker

[Hosted CI before artifact cleanup](https://github.com/girishmotwani/atom/actions/runs/40903164788) completed with failures. Failing checkout tests include temporary-path equality assertions on macOS and Windows, where resolved paths have different alias spellings. The developer explicitly selected cleanup-only publication with these failures deferred. No fixture repair or all-green cross-platform claim is included.

## Limits

This is local Windows/Python evidence, not a root Go/race result, completed cross-platform CI, real-PR context-quality evidence, or a new model review. See [findings](findings.md). No model invocation, live target checkout, dependency installation, or PR merge was performed for this artifact cleanup.
