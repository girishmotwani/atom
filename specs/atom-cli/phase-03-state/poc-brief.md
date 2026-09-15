# POC Brief — Phase 3: state persistence on Windows

**Spike:** `poc/state-persistence-on-windows/`
**Status:** predictions recorded, not yet run

## Why this spike exists

The phase plan said Phase 3's POC was *"justifiably skipped — no technical
uncertainty."* That is the same sentence, by the same author, that was used to
skip the Phase 2 POC. Running Phase 2's anyway refuted an assumption and then
surfaced the panic/exit-2 collision, which was the most consequential finding in
the project.

So the claim is being tested rather than trusted.

## The question

Phase 3 persists `.atom/state.json`, `.atom/config.json`, and an append-only
JSONL event log. The plan calls this *"ordinary JSON persistence"* whose *"only
real trap is corrupt or partially-written state."*

**Is the obvious write strategy — write to a temp file, then `os.replace` —
actually safe on Windows, and does concurrent appending to a JSONL log
corrupt it?**

Both are assumed rather than known. Both become expensive to change once
`atom review` and `atom ship` depend on the log.

## Predictions

Recorded before running. Each is falsifiable, and each is what the author
actually expects — not a hedge. A prediction nobody would be surprised to see
refuted is not worth writing down.

| # | Prediction | Confidence | If refuted |
|---|---|---|---|
| **P1** | `os.replace(tmp, dst)` **fails** with `PermissionError` when `dst` is open for reading by another process. Windows locks open files, and Python's `open()` does not pass `FILE_SHARE_DELETE`. | Medium-high | The naive recipe is fine and Phase 3 gets simpler. Good news, but it must be *observed* good news. |
| **P2** | Concurrent appends to a file opened in `"a"` mode **do not interleave** for lines under 4096 bytes. Python's `"a"` maps to `O_APPEND` → `FILE_APPEND_DATA`, which Windows serialises. | Medium | The event log needs a lock or a per-process file. This would be the finding that justifies the spike on its own. |
| **P3** | A truncated file, a zero-byte file, and a file of NUL bytes **all raise `json.JSONDecodeError`**, so one `except` clause covers every corruption shape. | Medium | The error path needs to branch, and the "clear error not a stack trace" promise costs more than one handler. |
| **P4** | If a process is killed **mid-write** while using write-temp-then-replace, the original `state.json` is left **intact and complete**. | High | The whole write strategy is unsound and Phase 3's central promise fails. |
| **P5** | A process killed mid-write leaves a **partial** temp file on disk rather than no file. Stale temp files therefore accumulate and need cleaning up. | Medium | No cleanup needed. |

## What this spike deliberately does not settle

- Network drives and UNC paths. Atom assumes a local working tree.
- POSIX behaviour. It will differ; CI runs the spike on all three platforms and
  will say so.
- Multi-writer *correctness* beyond corruption — two processes racing to advance
  the phase is a design problem, not a filesystem one.

## Success criterion

The spike succeeds if it produces evidence for or against every prediction.
Confirmed, Refuted and Inconclusive are all successes. The only failure is a
spike that does not run, or one whose result is laundered into agreement with
the prediction.
