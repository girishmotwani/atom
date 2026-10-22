# Review repair test plan

Developer triage on 2026-10-22: fix all four findings before creating the PR. A subsequent "lets proceed" authorizes this repair pass. No further model batch is implied. This work preserves the approved public API, ownership mechanism, result precedence and wait allowance; a materially different mechanism remains a gate.

| Finding | Existing design obligations | Planned regression |
|---|---|---|
| Partial diff in timeout diagnostic | 17, visible secondary errors | Extend test_runner_failure_details_survive_diff_rejection to require native refusal but exclude partial diff for TIMED_OUT |
| Busy-pipe throttling | 8, 12, 13, fair bounded communication | Deterministic coordinator test: consecutive progress needs no sleep; idle pass sleeps; deadline is still checked under continuous progress. Real large-input/dual-output regression verifies bytes and completion without a new public throughput SLA |
| Interrupt outside inner handler | 7, 10, 11, 14 | Deterministic interrupt at normal completion receipt and inside missing-file diagnosis; retain identity handles and assert one finalization, actual exit, handle release and original exception propagation |
| Late-spawned member missing exit receipt | 7, 8, 9, 10, 15 | Real job-owned child creates a pipe-independent cwd-holding grandchild after the first identity snapshot, before termination. Do not claim verified cleanup when that identity was missed. Cover normal-completion runner_error and retained TIMED_OUT with explicit incompleteness. Existing stable-member exit-before-return cases remain unchanged |

No test is compiler/vet-redundant: Python accepts each of these silent logical failures. Native faults are injected only at the existing private boundary; fixture safety rescue cannot count as measured cleanup. One finding at a time will have recorded RED/GREEN output before its production change. Selected original TDD remains separate from this repair evidence.

A repeat member snapshot is not automatically an exit receipt for a process already removed from job accounting. The existing cumulative TotalProcesses accounting can detect an admission after capture begins: absent complete retained identity evidence, the existing failure contract requires an explicit incomplete-cleanup result rather than a guessed success. This is a fail-closed validation refinement of the approved mechanism, not a new containment backend or claim that accounting alone proves exit.

## Outcome

All four findings are addressed within the existing approved contract. The final standard full gate passed: 1002 passed, 2 skipped in 79.85s, coverage 95%. Complete repair captures, including failed attempts and fixture corrections, are in [repair evidence](review-fix-evidence.md). The [merged review](review.md) retains original severities/proposals and explains the actual conservative late-admission repair. No extra model review or supported-platform CI success is implied.
