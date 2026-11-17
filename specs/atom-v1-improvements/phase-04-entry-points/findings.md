# Setup Findings And Limits

- This changes agent instructions, not runtime commands or approval enforcement.
  The setup contract does not complete Phase 04 or block the standalone quickstart.
- Historical Windows observations retain their original scope and Inconclusive
  protocol results. No fresh live replay or model review is claimed; no more setup
  reruns are authorized. Detailed evidence remains in the archived Git snapshot.
- General template/platform guarantees and persistent Copilot permission saving
  remain unverified. Detailed diagnosis belongs to Phase 05; review repair is #28.
- Installation-mode documentation and broader phase-plan changes are outside this
  focused PR. Their prior discussion is retained in history, not silently discarded.

## Existing CI Blocker

Main `8cf34fa` already fails the same review-continuation test as this PR:
`test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates`.
The fixture requires Go 1.27.0 while CI PATH contains Go 1.23.12. The test/runtime
files are unchanged by this PR. Selected main-CI diagnostic, verbatim:

```text
atom.review.ControlToolchainError: PATH Go 1.23.12 is below module minimum 1.27.0
```

[Main CI run](https://github.com/girishmotwani/atom/actions/runs/44118536323).
Leave that unrelated fixture/toolchain repair separate; do not weaken its test or
claim the full CI matrix is green. Fresh scoped validation is recorded below.

## Scoped Validation - 2026-11-17

Command from tools:
`python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_init_repeat.py tests\test_standalone_review_guidance.py -q --tb=short`.
Selected captured output, verbatim:

```text
============================ 171 passed in 58.39s =============================
```

Command from repository root: `python tools\check_links.py`.

```text
checked 613 relative links across markdown files
all relative links resolve
```

The eight setup behavior/delivery files are byte-unchanged from the accepted
pre-simplification commit; canonical/package pairs match. This is scoped local
validation, not a clean full CI matrix or new live behavior evidence.
