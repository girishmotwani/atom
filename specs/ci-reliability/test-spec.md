---
project: "ci-reliability"
date: "2026-11-19"
status: "verified-accepted"
design_spec: "design-spec.md"
---

# Test Spec: Hermetic CI Fixtures

The approved [design spec](design-spec.md) changes tests, not production.
Use existing failing regressions and diagnostic boundary controls rather than
inventing a production feature or adding tests of trivial helper accessors.

## Behaviour Mapping

| Spec | Cases and proof |
| --- | --- |
| 1 | Existing default gate-order arm; deterministic resolver records exactly one call and raises GoToolchainSelectionError. Check selected gofmt/build order and no models under old, missing and compatible PATH Go. |
| 2 | Existing strict arm retains forbidden-control sentinel, full exact gate ordering and no models under all three PATH conditions. |
| 3 | All 14 captured PR path cases; force a real Windows alias in the allocator's parent only. Keep exact equality against resolved expected module at the three consumer sites. Existing provenance, real Git, dirty original, cleanup and invalid-checkout tests remain. |
| 4 | Existing restricted-environment Unicode/stdin, absolute-executable, copy-on-launch and explicit-environment lifecycle tests. Run with Python 3.10.11 child to reproduce missing prerequisite, then verify the minimal Windows-only helper through those real subprocesses. No parent PATH/sentinel leakage. |
| 5 | Preserve existing mapping equality, caller-mutation, Unicode, stdin, PATHEXT and parent equality assertions. Mutate the actual supplied mapping in the launch hook. |
| 6 | Existing empty-environment case uses literal {}, native cmd.exe /d on Windows and Python on POSIX. Preserve completion, sentinel absence and unchanged-parent assertions. Do not augment this mapping. |
| 7 | Existing explicit-environment timeout/surviving-child and native identity cases retain deadlines, partial output, identity and termination assertions. Test with 3.10.11 child. |
| 8 | Run the six affected modules, including negative control-resolution, cleanup, runner/lifecycle and environment-isolation cases; then the full existing Python suite. No changed skips, broad exception acceptance or deadline increases. |

## Order And Evidence

Re-run the unchanged Go-control, parent-alias and six-child reproductions before
editing their fixtures. Capture failures separately from the already accepted
diagnosis. Apply a coherent correction per family and re-run the matching cases.
The six affected test modules and then the full suite are the broader gates.
Exact commands/output belong in implementation-evidence.md.

## Redundancy And Edge-Case Audit

No test is removed. No new trivial-helper, constant, constructor or language
behavior test is needed: the real failing subprocess and canonical-path cases
exercise the changed fixtures. This is Python test infrastructure, not Go code;
Go nil-string/compiler/race checks do not apply. Existing tests already cover
missing/unverified controls, process failure, timeout, interruption, inherited
versus empty mappings and checkout rejection/cleanup. Do not invent concurrency
in the repair or claim these checks prove unexecuted paths.

## Limits

The local parent pytest runs on Python 3.13.14; selecting Python 3.10.11 only for
child execution does not constitute a full 3.10 test run. Native macOS and all
six hosted CI combinations remain required before a restored-CI claim.
