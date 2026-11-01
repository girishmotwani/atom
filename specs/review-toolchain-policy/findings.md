---
project: "review-toolchain-policy"
phase: "phase-01-exact-toolchain"
date: "2026-10-31"
---

# Current Findings And Remaining Limits

Status: **local final gate passed; cross-platform CI failing**. The complete
chronological discovery/status record is archived under the provenance recorded
in [publication evidence](publication-evidence.md). Resolved preparation/base
notes are not current blockers.

## Open Findings

| Item | Evidence and disposition |
|---|---|
| CI failures | On source commit 2d42f6f, both macOS and both Windows CLI jobs failed. Both Linux CLI jobs, three existing POC jobs and docs passed. This cleanup changes no source/tests and does not fix or assign a cause to those failures. |
| Native handle-count failure | One local full run observed 330 handles versus 328 in test_windows_repeated_runs_release_handles_and_workers. Isolated and approved unchanged full reruns passed; cause remains unexplained, not repaired. |
| Empty observed GOENV | Claude Minor at go_selection.py:238. Deferred under the four-non-empty-fields contract; minimal environments may explicitly use GOENV=off. |
| Final amended code not model-rereviewed | Both independent models saw the snapshot before the canonical-root guard/test. Tests do not constitute independent approval. Post-patch review repair is girishmotwani/atom#16. |
| Prompt-budget preflight | Availability did not predict request admission; Gemini and Claude tokenizers differed. Approved deduplication/larger context completed this batch, but product preflight is not implemented. Tracked in girishmotwani/atom#14. |
| Stale review-skill examples | Existing --base/--models examples/config-default claims differ from actual --branch/repeated --model/runtime defaults. Deferred as unrelated usage-documentation repair. |
| Unavailable default reviewer | GPT default availability failure is account/catalog-specific and predates this feature. No production-default substitution introduced. |
| Evidence limits | Native fixture is standard-library-only with controlled workspace/proxy/checksum/CGO. Successful native race/CGO and real dependency compatibility are not proved. Discovery is bounded, not exhaustive SDK-manager support. |

## Actual CI Result

[CI run 41194476670](https://github.com/girishmotwani/atom/actions/runs/41194476670)
on source commit `2d42f6f18a6c0d0346f90a4cefbe5346cce9a8e3`.
These result lines are copied from the captured failed-job log, not reconstructed:

```text
atom CLI (py3.10, macos-latest)	UNKNOWN STEP	2026-10-31T10:53:21.1894330Z ================= 14 failed, 1554 passed, 52 skipped in 42.56s =================
atom CLI (py3.12, macos-latest)	UNKNOWN STEP	2026-10-31T10:53:27.6928230Z ================= 14 failed, 1554 passed, 52 skipped in 54.42s =================
atom CLI (py3.10, windows-latest)	UNKNOWN STEP	2026-10-31T10:55:32.8899015Z =========== 20 failed, 1598 passed, 2 skipped in 128.73s (0:02:08) ============
atom CLI (py3.12, windows-latest)	UNKNOWN STEP	2026-10-31T10:54:45.4458328Z =========== 14 failed, 1604 passed, 2 skipped in 110.17s (0:01:50) ============
```

Complete CI failure capture is preserved outside Git. Passing Linux/POC/docs
jobs do not turn these four failing CLI suites into cross-platform success.
Fixing or diagnosing their source cause is outside approved evidence pruning.

## Resolved Or Explicitly Rejected

The original GOSUMDB=off bootstrap trial remains Inconclusive. A separately
approved direct-executable trial Confirmed ten cases/56 commands; neither driver
was replayed or rewritten. The old branch/base was reconciled before execution.

Fixed author-found Minor: a different canonical GOROOT could share selected
bin/go and pass identity verification. Added one independent root guard and a
regression that first failed; 179 coupled cases passed afterward. The I/O alias
fake is not a native junction reproduction.

Rejected model Minor: experiment-labelled version acceptance is outside the
approved exact-stable contract; no ordinary release regression established.
Complete model messages/dispositions remain in [review](phase-01-exact-toolchain/review.md).

Latest full local result: 1615 passed, 5 skipped in 176.32s, 95%, exit 0.
All meaningful RED/GREEN and failure evidence plus the complete latest gate
remain in [TDD evidence](phase-01-exact-toolchain/tdd-evidence.md).
