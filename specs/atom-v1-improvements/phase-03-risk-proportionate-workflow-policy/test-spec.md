---
project: "atom-v1-improvements"
phase: "phase-03-risk-proportionate-workflow-policy"
design_spec: "design-spec.md"
---

# Test Spec: Guidance Delivery And Review

## Scope And Redundancy Audit

The approved design explicitly defines a documentation-only change with no runtime API. No new Go tests, model calls, classifier, or string-presence tests are proposed for the policy guidance itself. A text assertion could check that a phrase exists, but cannot establish correct recommendations or real developer control. Use semantic review of the six proposed rules and existing documentation/packaging checks instead. This adapts the Go TDD template to the approved scope; it does not claim a RED/GREEN production-code loop.

Empty inputs, ignored errors, typed nils, non-exhaustive switches, overflow, cancellation, and concurrency are not applicable to this guidance-only implementation. No existing test is removed or weakened.

## Coverage Map

| Design routing rule | Review case and expected guidance | Delivery check |
|---|---|---|
| 1. Missing intent | Ask one discovery question; do not infer acceptance or technical feasibility | Shared policy and discovery/start instructions |
| 2. Unproven material uncertainty | Recommend a bounded falsifiable POC, with confirm/refute/inconclusive criteria, before design | Shared policy and POC/spec/build instructions |
| 3. Understood reproducible defect | A failing regression can supply defect proof; production work still needs an approved spec and TDD | Shared policy and TDD/spec instructions |
| 4. Applicable approved evidence | Name artifact, assumptions, uncovered boundary and focused validation; missing/unapproved/changed evidence is not reuse | Shared policy and POC/spec instructions |
| 5. Already specified work | Relevant changed-contract validation, without a ceremonial POC or relaxed gates | Shared policy and build/TDD instructions |
| 6. Documentation only | Verify factual claims and links/packaging; no fabricated Go experiment | Shared policy and TDD/workflow instructions |

## Cross-Cutting Review

- Separate observed evidence from assumptions, and explain uncertainty and consequences rather than assigning a risk score.
- Give one recommendation, its relevant alternative and one decision question; no work before its required approval.
- Rejection stops the proposed work; silence and earlier approval do not supply consent.
- Four model cases are illustrative only; discovery/routine validation remain untested proposals. No universal classification or runtime control claim.
- Existing entry points and runtime phase/gate state are unchanged. No paid calls, installations, push or publication are authorized.
- Canonical and packaged guidance must match so initialized repositories receive the same policy.

## Existing Validation

From repository root: `python tools\check_links.py` and `git diff --check`.
From `tools`: `python -m pytest tests\test_artifact_integration.py tests\test_comment_guidance.py tests\test_plugin.py tests\test_onboarding.py -q`.
Compare each changed canonical instruction with its corresponding packaged asset. These checks verify links, distribution and existing contracts, not model compliance. Record actual output after edits.

## Findings And Boundaries

The original POC harness always exited zero and discarded successful-call stderr. The guidance-only implementation originally deferred instrument changes. Subsequent explicit review triage separately authorized deterministic archive repairs and fake-CLI regressions, not a new paid experiment. Preserve the original observed sample/transcript and disclose that historical stderr is unknown. Windows lifecycle validation remains deferred.

## Completed Semantic Review

All six routing rules appear in the shared policy. Discovery distinguishes missing intent from uncertainty; regression proof retains spec approval; reuse rejects missing/unapproved/changed evidence and validates the boundary; routine/docs paths avoid fabricated spikes. Recommendations name observed evidence, unknowns, consequences, alternatives and the developer's decision. Existing commands and runtime gates are unchanged. README/workflow/AGENTS and existing skills defer to the same shared guidance. The four examples remain explicitly limited model evidence, not an exhaustive or enforced classifier.

## Original Guidance Verification (Historical, Before Multi-Model Review)

From repository root:

```text
python tools\check_links.py
checked 414 relative links across markdown files
all relative links resolve
```

From `tools`:

```text
python -m pytest tests\test_artifact_integration.py tests\test_comment_guidance.py tests\test_plugin.py tests\test_onboarding.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 50 items

tests\test_artifact_integration.py ............                          [ 24%]
tests\test_comment_guidance.py ........                                  [ 40%]
tests\test_plugin.py ...........                                         [ 62%]
tests\test_onboarding.py ...................                             [100%]

============================= 50 passed in 30.73s =============================
```

A validation-only Python script compared the seven changed canonical/packaged pairs (AGENTS; POC/TDD discipline; build/discover/spec/TDD skills), parsed all archived response JSON, counted stderr records, checked the corrected capitalization and deduplicated brief criteria, and ran `git diff --check`. It did not invoke models or modify files. Captured output:

```text
PASS: 7 canonical/packaged instruction pairs match
PASS: recovered transcript has eight complete JSON responses and ten stderr records
PASS: amended brief has one criterion for each verdict
PASS: git diff --check
```

No full Python suite or Go `atom check` was rerun for this documentation-only implementation. The selected tests exercise existing documentation/distribution contracts; semantic review is not empirical proof of model behavior. No review-model batch, push, installation, or Phase 09 experiment occurred. At this historical gate the implementation was ready for developer approval; multi-model review had not yet occurred. The later four-call review and its approved repairs are recorded in review.md and decisions.md.


## Separately Approved Archive Repair Checks

The developer approved these deterministic regressions after review. They repair the evidence instrument, not Atom's guidance runtime. The compiled test executable supplies fake CLI responses in a temporary directory, avoiding all paid model calls.

| Defect/contract | Regression |
|---|---|
| Missing/null booleans must not count as complete answers | Each required boolean omitted and null; explicit true/false accepted; rejection retries remain bounded |
| Refuted/Inconclusive must not report process success | Route disagreement and explicit gate bypass exit 1; invalid answers exit 2 |
| Availability requires the requested READY marker | NOT READY is rejected; unavailable primaries may use the sole alternate, but the same model cannot supply independent evidence |
| Successful stderr must actually be captured | Fake successful calls emit stderr and the real invocation log must retain it |
| Retry/fallback cannot exceed the hard cap | Invalid-answer scenario records 48 actual calls and returns Inconclusive |

Each repaired behavior was observed failing before its repair, then passing afterward. The initial incomplete-result fixture exceeded a one-minute test deadline; its time budget was corrected to three minutes without changing verdict/call-count assertions. That fixture issue is not lifecycle evidence. Preserve actual RED/GREEN output in the repair verification record.

## Post-Review Final Verification

The [repair verification log](tdd-log.md) contains verbatim RED/GREEN output, the fixture deadline correction, the combined successful archive Go build/vet/format/test/race gate, 50 passing documentation/distribution tests and the evidence-integrity checks. This is local verification of repairs, not a second paid review or a new policy experiment. The repository root remains Python; the Go gate applies only to the archived module.
