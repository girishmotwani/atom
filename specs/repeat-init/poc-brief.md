# Repeat-init POC Brief

## Question

Does the current init guard reject a valid repeat call while allowing a partial initialization to be rewritten?

## Scope and method

Use a disposable Python driver and temporary minimal Go module. Invoke the real public CLI in subprocesses. Initialize once, record an approval, then snapshot paths, bytes, sizes, and nanosecond modification times. Run matching init twice and compare snapshots. In separate disposable cases, remove config.json or state.json, repeat init, and report the exit status and any changed files. Do not modify the developer's target module or Atom production code.

## Evidence and grading

Capture every command, exit code, stdout/stderr, and snapshot comparison. The defect is reproduced if complete repeats exit 2 without changes and either partial case rewrites retained project records. A different result is reported as contrary evidence, not forced into confirmation.

## Cost and limits

One local Python driver, no agents, no external repositories, and a few minutes of local Go checks. No performance or concurrent-init claims. Delete temporary modules automatically; retain the driver and report for reproduction.

## Expected fix contract to inform later design

A valid matching repeat must return 0 without checks, writes, timestamp changes, or initialization events. Conflicts and incomplete/corrupt shared onboarding must fail without repair. Only explicit --force may reset. Machine-local baseline/events files are optional on a clone. The precise shared-scaffold validation boundary will be proposed after the experiment.

## Gate

Approval authorizes this reproduction only, not implementation or publication.
