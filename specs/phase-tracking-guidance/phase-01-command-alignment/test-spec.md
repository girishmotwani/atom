# Test specification

Approved design: [design-spec.md](design-spec.md), approved in conversation on 2026-11-25.

| Design behaviour | Verification |
|---|---|
| 1: filesystem-derived planning | Review plan instructions against discover_phases; parser regression rejects removed registration examples. |
| 2: read-only status | Parse documented status commands; review against _run_status_command. |
| 3: setup and accepted completion | Extend parser regression to inline commands, observe startup-flag failure, then review artifact-based completion and unchanged gates. |
| 4: resume from evidence | Review build resume wording against state.py and phases.py; artifact presence must not imply approval. |
| 5: non-interactive gate | Review explicit halt message and nonzero exit; parser regression rejects removed phase command. |
| 6: supported examples and parity | Parser-backed fenced/inline examples in six documents; normalized canonical/packaged parity for three pairs. |

## Adaptation and redundancy audit

This is documentation-only work with no runtime changes. Follow the documentation adaptation in tdd-discipline.md: parser regression plus factual review, not fabricated Go tests or a production RED/GREEN claim. Parity checks protect distribution of the same corrected guidance. Existing plugin, standalone entry-path and relative-link checks cover integration. No new error-handling, cancellation, concurrency or runtime input cases apply. No compiler-redundant tests were proposed.

## Limits

Parser acceptance does not prove workflow wording or live-agent compliance. Factual review checks the first; no live-agent claim is made.
