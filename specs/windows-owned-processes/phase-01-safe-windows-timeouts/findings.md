# Findings after review repairs

The developer triaged all four review findings to fix before PR creation. The partial-diff diagnostic, busy-pipe delay, interrupt-finalization gap and late-admission false-completion condition are repaired and covered by focused regressions. The final standard full shipping gate passed: 1002 passed, 2 skipped in 79.85s, coverage 95%. No supported-CI, independent re-review of fixes, phase-completion or merge claim is made here.

## Validation findings, not hidden successes

- An added PYTHONPATH override exposed the source egg-info metadata inside the packaging test's clean virtual environment. pip then treated the same-version wheel as installed and did not create its writer executable. The full attempt failed (1 failed, 998 passed, 2 skipped). A read-only pip-show comparison proved the environment effect; removing the override made the unchanged packaging test pass. No packaging code or test expectation was changed.
- The next standard full attempt failed (1 failed, 998 passed, 2 skipped) because the identity observer read an existing ready file once and received PermissionError. A deterministic transient-read regression reproduced this fixture defect. Identity readiness now retries only missing/unreadable files within the original finite deadline; persistent errors remain visible. Native process-signaling and before-rescue directory assertions are unchanged. Targeted native/runner validation passed afterward.

## Remaining limits

- A cumulative job admission count change during exit-identity capture is reported as incomplete verification, not inferred success. Termination and owned-resource finalization are still attempted. This is deliberately conservative; the total includes failed associations as well as members that have already terminated.
- Required supported-platform CI has not yet run. Local Windows/Python 3.13.14 does not replace Windows/Linux/macOS Python 3.10/3.12 evidence.
- The three POC trials prove this fixture/host, not all nested-job policies, a security boundary or hard real-time kernel-call behavior. The older counterexample is archived provenance, not a current-runner regression command.
- Fixes have regression evidence but have not received another independent model review; no extra model batch was authorized or run.
