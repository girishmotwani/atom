# Standalone Review Guidance - Implementation Result

Date: 2026-11-09.
Status: implemented, validated and accepted; review proposal preparation approved.
Design: [approved spec](design-spec.md).
Coverage: [validation map](test-spec.md).

## Production Changes

Added the canonical shared standalone-review entry contract and its byte-identical
packaged reference. Updated the canonical/packaged review skill to use that
contract, supported selector/model flags, actual report severities/proximity
semantics and honest context/participation limits. Start now routes explicit local
review-only intent before phase/status inspection. README/workflow document the
bounded entry and approved review/findings/decisions bundle.

Standalone review does not require init or registered phase state, even in an
existing Atom project. Missing root go.mod is disclosed as skipped tooling.
Proposal approval covers reviewer probes, review submissions, normal checks and
file effects; review-only ends without automatic fixes, progression or publishing.
Phase mode retains its established path, project audits and next-beat gate.

No CLI/runtime/prompt/schema, plugin name, default model/runs/concurrency, install,
configuration or publication change. Earlier setup work was retained, not reverted.
The frozen installed user preview was not refreshed; source changes require a
separate approved installation/update step before live installed-user validation.

## Documentation Regression Evidence

Before shipped-content edits, ran the new structural checks and expanded
onboarding cases. Verbatim excerpts from that run:

```text
__________ test_review_entry_assets_match_canonical_bytes[relative0] __________
tests\test_standalone_review_guidance.py:33: in test_review_entry_assets_match_canonical_bytes
    assert canonical.is_file(), f"Missing canonical entry guidance: {relative}"
E   AssertionError: Missing canonical entry guidance: skills\atom\references\standalone-review.md
```

```text
____________ test_start_routes_review_before_lifecycle_inspection _____________
tests\test_standalone_review_guidance.py:42: in test_start_routes_review_before_lifecycle_inspection
    assert "/atom:review" in early_entry
```

```text
================ 10 failed, 11 passed, 19 deselected in 2.11s =================
```

Other initial failures were the same absent reference in canonical/packaged
readers and onboarding, and unsupported --base/--models examples. These were
documentation/distribution regressions, not production runtime Go RED/GREEN.
Existing setup-reference and review-skill delivery cases were retained. No test
was weakened: the old canonical setup case was parameterized with two additional
assets while preserving the original byte-equality/install assertions.

## Final Focused Regression Evidence

Command from `tools`:

```text
python -m pytest tests\test_standalone_review_guidance.py tests\test_onboarding.py tests\test_cli_review.py tests\test_report.py tests\test_merge.py tests\test_artifact_integration.py tests\test_plugin.py -q --tb=short
```

The full captured output follows, not a reconstruction:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 204 items

tests\test_standalone_review_guidance.py ..................              [  8%]
tests\test_onboarding.py ......................                          [ 19%]
tests\test_cli_review.py ............................................... [ 42%]
.............................                                            [ 56%]
tests\test_report.py ...................                                 [ 66%]
tests\test_merge.py ..............................................       [ 88%]
tests\test_artifact_integration.py ............                          [ 94%]
tests\test_plugin.py ...........                                         [100%]

============================ 204 passed in 46.21s =============================
```

Raw captured output is also saved in `implementation-validation.txt`.
The new module contributes 18 checks for canonical/package bytes, three examples
parsed by the real CLI parser without invoking its runner, early routing and
relative file links from all seven changed shipped document locations. The
expanded onboarding cases actually install the setup reference, new review
reference and review skill into fresh pytest-owned bundles using the existing
deterministic baseline fixture. This is not a real Go baseline claim.

## Reconciliation To The Twelve Obligations

| Design obligations | Implemented/checked |
| --- | --- |
| 1-3 mode, early routing, prerequisites | Shared contract/skill/start review; early-route and link checks; no automatic init |
| 4-6 proposal, refusal, models/flags | Explicit contract and caller guidance; parser checks; actual CLI/model-source factual review |
| 7 gate evidence | Root-module/skipped-tooling and working-tree vs selected-formatting disclosure; existing CLI/report regressions |
| 8 approved report/audit persistence | Small standalone bundle and phase-path distinction; writer collision/refusal stop; artifact integration regressions |
| 9 failures/participation | Explicit limits/no retry/no clean empty transport; existing CLI/report regressions |
| 10 report/context truthfulness | Correct severity/grouping/retained messages; merge/report regressions; no automatic context guarantee |
| 11 bounded ending/phase compatibility | Separate standalone stop and phase recommendation; existing phase guidance retained |
| 12 distribution/docs | Matching canonical/package bytes, fresh bundle installation, links and plugin namespace regressions |

No material spec changes were necessary. Clarified implementation wording to keep
all three CLI examples illustrative alternatives and make direct CLI stdout
behavior distinct from the skill's required persisted audits. These follow the
approved design rather than introduce new behavior or waive a gate.

Additional inspection: `git diff --check` exited 0 with empty output. A scoped
search found no old --base/--models examples, model-role-resolution claim,
Blocker/Major severity enumeration, per-file invocation promise or semantic
merge promise in the changed review skill/reference surfaces.

## Remaining Limits And Findings

No newly discovered runtime defect. Live-agent consent/refusal/stopping is not
proven by prose/parser/distribution tests. The installed setup trial remains
Inconclusive and paused. This result completes the approved standalone guidance
implementation slice, not all Phase 04 entry paths, full-suite coverage, a Go
atom-check gate, a multi-model review or a release. No real reviewer batch ran.

## Completion Gate

Accept this implemented slice as ready for a separately scoped review proposal,
or request changes. No commit/push, installed-preview replacement, additional
model spend, cleanup or broader phase completion is authorized by implementation.
