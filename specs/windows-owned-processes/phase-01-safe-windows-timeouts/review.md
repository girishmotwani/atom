# Independent review: Windows owned command lifetimes

Status: **all four findings triaged to fix and addressed with regression evidence; draft publication authorized; supported CI still pending**.

## Scope and evidence

Two independent read-only reviews completed on 2026-10-22, using the developer's runtime selections claude-opus-5.5 and gpt-5.6-sol; neither is the author model gpt-6.1-sol. Each received the full phase scope, surrounding-file obligation and approved neutral contract. They did not see each other's findings. No further model batch was run or authorized.

The prerequisite [shipping gate](verification.md) passed before either review: 988 passed, 2 skipped in 183.29s on Windows/Python 3.13.14, coverage 94% overall and 92% native module. Documentation: 225 relative links resolve; git diff --check exited 0. Python 3.10/3.12 and Linux/macOS CI remain unrun. Go/race/optional lint tools ran no checks for this Python-only change and exclude nothing. Passing tests establish only the paths they exercised.

Both reviewers inspected the isolated personal-main-based phase rather than the unrelated original checkout. New native owner/test files, affected runner/diff consumers, README and synthetic evidence were included. Findings below are static review evidence, not reproduced failures. These findings describe the pre-fix review snapshot. Remediation evidence is appended below; the fixes were not independently re-reviewed.

## Merged findings

| Severity | Agreement | Location | Finding | State |
|---|---|---|---|---|
| Major | 1/2 (gpt-5.6-sol) | tools/atom/_windows_process.py:542-557 | A child spawned between the single member snapshot and job termination is absent from retained-identity exit waits | Addressed; conservative admission-change guard |
| Minor | 1/2 (claude-opus-5.5) | tools/atom/diff.py:208 | Timeout diagnostics now include the entire captured partial diff | Addressed; regression verified |
| Minor | 1/2 (claude-opus-5.5) | tools/atom/_windows_process.py:474-503 | A fixed sleep after each 16 KiB transfer caps stream throughput even while making progress | Addressed; regression verified |
| Nit (reviewer's label) | 1/2 (claude-opus-5.5) | tools/atom/runner.py:204-225 | An interrupt outside the inner try can bypass finalization entirely | Addressed; full-lifetime guard and real SIGINT regression |

### Major: late-spawned member is not waited

Finalization snapshots member identity handles once while the job is still running, then calls TerminateJobObject. A member may create a pipe-independent child between these operations. The child is terminated with the job but its identity is not among those waited. The design's own local regression evidence established that active-count zero alone can precede process-handle signaling. A late member therefore has weaker exit evidence than stable members; returning can claim verified cleanup before that member is fully exited or has released its cwd. Stable-membership tests do not exercise this window. Reviewer confidence: high.

Suggested direction: collect newly observed identities through termination and wait for them within the same deadline, with a regression that injects a cwd-holding child between snapshot and termination. **This is a reviewer suggestion, not a proved repair.** A second snapshot can itself miss an identity after accounting drops to zero; any fix must establish the required receipt rather than merely add a timing-dependent query. The finding has not been dismissed for lacking consensus. Reproduction and a defensible solution precede any completion claim; a materially different ownership mechanism requires a new gate.

### Minor: partial diff becomes timeout error payload

The new timeout branch uses combined_output, which concatenates captured stdout (possibly a very large partial patch) with stderr. The CLI prints DiffUnavailable directly, so a timeout dumps the diff body ahead of the intended lifecycle diagnostics. The new test supplies diff stdout but checks only for the cleanup message. Suggested fix: retain stderr diagnostics without embedding the partial patch, and assert the diff body is absent from the error. Confidence: high.

### Minor: unconditional communication sleeps throttle busy pipes

Each pump transfers at most 16 KiB per stream, then communicate sleeps 5 ms even if it just moved a full chunk. This creates a nominal per-stream ceiling near 3.2 MB/s (potentially lower with coarse timers), backpressuring tools and spending the existing timeout on avoidable polling delays. Current large-input coverage is too small to measure that case. Suggested fix: drain a fair bounded amount while progress is available and sleep only when idle; retain deadline fairness and add representative large-transfer evidence. Confidence: high on the cap, medium on practical frequency. No benchmark was run by the reviewer.

### Interrupt gap: reviewer's Nit label does not remove the obligation

Deferred finalization is reached only by the inner BaseException handler or the later normal-path block. KeyboardInterrupt after communicate returns but before entering that block, or within an exception handler's diagnosis, can leave the function without finalizing its native owner. Pipe-independent owned children and native handles can then remain until the host exits. This conflicts with approved behavior 14 even though the reviewer rated the narrow timing window Nit. Suggested fix: structure one outer ownership-finalization guard covering normal return and diagnostic handlers, preserving primary errors and interruption semantics. Confidence: high that the gap exists, low estimated practical impact. No timing reproduction was run.

## Triage and repair outcome

The developer selected fixing all four findings before PR creation, then explicitly said to proceed. No finding was silently rejected or deferred.

- Late admission: compare cumulative TotalProcesses before identity capture and after termination/accounting waits. If it changes, missing identities cannot be retrospectively verified by another snapshot: return explicit incomplete cleanup (runner_error outside a timeout; TIMED_OUT retained otherwise), while still attempting owned termination/waits/close. Counter query failures are likewise non-success. The native race fixture creates a real pipe-independent cwd-holding child after snapshot, verifies actual job membership/count growth and checks the truthful result. This closes the false-verification path; it does not pretend the missing identity was waited. A conservative failure is possible even if termination has already finished. The documented counter also includes failed associations.
- Diff diagnostics: use stderr only for timeout detail; negative regression requires the partial diff body to be absent while cleanup detail remains.
- Busy pipes: each fair per-stream pass reports progress; communication and final drain sleep only when idle and check their deadline every pass. Deterministic progress/deadline cases plus real 8 MiB stdin and 24 MiB per-output-stream completion exercise the former artificial throttle.
- Interruption: an outer ownership-finalization guard covers completion receipt and diagnosis, with main-thread SIGINT deferral over the whole owned lifetime. Communication observes the flag promptly. Tests verify one cleanup, original interrupt identity, actual owned-child exit/cwd release before rescue and handler restoration, including real SIGINT.

The final standard full Python gate passed: **1002 passed, 2 skipped in 79.85s**, coverage 95%. See [repair evidence](review-fix-evidence.md), [test map](test-spec.md) and [verification](verification.md). Intermediate validation environment and fixture failures are preserved and explained.

Exactly the two approved independent model runs occurred, before these repairs. No additional independent review of the fixes is claimed. Publication remains draft-only with supported CI open; this report is not a phase-completion or merge approval.
