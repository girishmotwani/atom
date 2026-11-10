# Configured-Go Guidance Correction And Design Addendum

Status: approved correction implemented and verified; final review acceptance pending.
This addendum follows the original [review](review.md). The developer selected
"Approve minimal documentation clarification and focused checks". No runtime,
CLI default, API, model budget or installed-preview change was made.

## Correction And Factual Basis

Canonical and packaged standalone references and review skills, plus workflow
prose, now disclose the effective launch Go pin and possible degraded continuation
before reviewer-spend approval. --strict-toolchain is an explicit proposal choice
for a requested hard stop, not an automatically added option.

The narrow exception requires a verified selected Go older than the root module
minimum, strict mode off, a proven selected build failure, passing compatible
control gates and an unchanged checked-input fingerprint. A project
review_go_version can supply that selection without CLI Go flags. Not every pin
or build failure qualifies. Preserve failure/control evidence and warning: a
degraded report exits nonzero and is not clean or gate-passed. No agent retry,
version switch or expanded spend is authorized by runtime continuation.

Factual review: tools\atom\go_selection.py:349-380;
tools\atom\review.py:379-432,647-670; tools\atom\cli.py:779-805.
No new Go experiment or production runtime RED/GREEN claim is appropriate for
this approved documentation-only correction.

## Design And Validation Reconciliation

This addendum supersedes only the inaccurate absolute-failure wording in
[design-spec.md](design-spec.md) obligation 7 and its required-gate error row.
Required failures normally block calls, subject to the narrow disclosed runtime
exception above. Obligation 4's approval proposal includes effective Go policy,
possible control checks/degraded evidence and an explicit strict-mode choice.
Other design obligations, missing-module limits and approval boundaries remain.
The original broken-source fixture still proves ordinary failure blocking, not
that every configured selected-Go failure blocks all calls.

For [test-spec.md](test-spec.md) coverage rows 4 and 7: verify these facts against
source; documentation checks require Go-pin/strict/degraded/nonzero disclosures
across all five affected shipped documents and prevent reintroduction of the old
absolute sentences. Parse all three bounded command alternatives both with and
without --strict-toolchain, without launching commands. Existing CLI cases verify
strict-option forwarding and degraded warning/nonzero results; onboarding checks
verify actual packaged delivery. Text checks are not proof of live-agent consent
or of all runtime conditions. No production runtime was changed.

## Focused Verification

From tools:

```text
python -m pytest tests\test_standalone_review_guidance.py tests\test_onboarding.py tests\test_cli_review.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 122 items

tests\test_standalone_review_guidance.py ........................        [ 19%]
tests\test_onboarding.py ......................                          [ 37%]
tests\test_cli_review.py ............................................... [ 76%]
.............................                                            [100%]

============================= 122 passed in 9.31s =============================
```

git --no-pager diff --check exited 0 with no output.
git --no-pager diff --exit-code -- tools\atom\review.py tools\atom\cli.py tools\atom\go_selection.py exited 0 with no output.

This is focused documentation/parser, delivery and CLI evidence, not a full-suite,
coverage, Go application baseline or live installed-user interaction claim.
No extra reviewer calls, model probes or installation updates occurred.

## Snapshot And Review Limits

The original review-scope.json, both raw reviewer responses and all four frozen
supporting artifacts are unchanged. Of the original 13 inputs, precisely the six
authorized source/test files below changed; seven others still match. The old
review snapshot has not been silently refreshed to suggest reviewers saw these
corrections. Current corrected-file SHA-256 values:

| Path | SHA-256 |
| --- | --- |
| `skills\atom\references\standalone-review.md` | `1f490c5bf5563e1ae171297f53b23ec00d8ecbd85441547a21ddf24d8c050f3e` |
| `skills\review\SKILL.md` | `44d2fd5c05f04e33ba9b86c85634ef35ddefa63681d4d73c8fe150d44bde0157` |
| `docs\workflow.md` | `caa04dc70e8ea96d7d5b70dbdc8a4d87fa5fe11e1793d32dbc73d3f0eec6a8ed` |
| `tools\tests\test_standalone_review_guidance.py` | `77d6b8facd044ff4aeddd9a4033d663fe92155d6c55948fe3aded082d51afbb2` |
| `tools\atom\assets\skills\atom\references\standalone-review.md` | `1f490c5bf5563e1ae171297f53b23ec00d8ecbd85441547a21ddf24d8c050f3e` |
| `tools\atom\assets\skills\review\SKILL.md` | `44d2fd5c05f04e33ba9b86c85634ef35ddefa63681d4d73c8fe150d44bde0157` |

No additional findings from this correction. The single low-severity documentation
finding is addressed, not deferred. Two responses under different explicit model
requests remain the available review evidence; exact runtime model identities
were not independently exposed and no stronger independence claim is made.
The correction itself was source-checked and regression-checked, not sent to a
new reviewer batch. Final acceptance must acknowledge these limits.

Only the standalone slice was reviewed. Earlier setup work, paused installed-user
trials and complete Phase 04 coverage remain outside this acceptance. Conditional
push/PR permission is not used before final review approval; shipping must inspect
the actual branch/PR scope rather than label all pending changes reviewed.
