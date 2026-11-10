---
project: "atom-v1-improvements"
phase: "phase-04-entry-points"
design_spec: "design-spec.md"
date: "2026-11-09"
---

# Validation Spec - Standalone Review Guidance

The developer approved the exact design with "Approve this spec and implement it"
and then "lets proceed". This is shipped documentation plus distribution tests,
not changed review runtime. Use factual review, parser-only checks, structural
checks and the existing Python regression suite. No Go production RED/GREEN,
coverage or atom-check claim is applicable; no real reviewers are needed.

## Toolchain Redundancy Audit

None - no proposed case was unfailable. Python/Go compilation cannot prove
Markdown command validity, relative links, early routing or packaged asset parity.
Go nil/interface/overflow/cancellation tests are inapplicable because no runtime
Go API, shared state or blocking implementation is introduced. Existing CLI
runtime cases cover errors/partial responses; do not duplicate them as text tests.

## Coverage Map

| Design behaviour | Check | Evidence limit |
| --- | --- | --- |
| 1 standalone vs approved phase context | Factual review of shared reference and skill mode selection | Instructions, not live model behavior |
| 2 early direct routing | Structural start-link-before-Step-1 test; manual no-loop review | Text ordering, not agent compliance |
| 3 read-only target/bootstrap/missing module | Factual review against bootstrap and confirmed POC | No runtime/source-discovery change |
| 4 proposal and approval before probes | Shared contract review of exact selector/models/runs/cost/files | Live waiting not exercised |
| 5 refusal and revised scope | Contract review: no calls/writes on refusal; no retry or expanded scope | Not a live refusal trial |
| 6 supported flags and independent models | Parse illustrative commands using real CLI parser without invoking runner; review model source/policy distinctions | Does not establish provider availability |
| 7 real gates vs missing/skipped evidence | Existing CLI/report tests and POC; preserve exact Go selection section | No new gate behavior |
| 8 standalone audit bundle/writer/refusal | Contract review plus artifact-integration regressions | Writer runtime unchanged; no real target writes |
| 9 failures and insufficient participation | Existing CLI/report tests; guidance factual review | No new fallback/exit code |
| 10 severity/grouping/context accuracy | Existing merge/report tests plus source-backed prose review | No live quality/corroboration claim |
| 11 standalone stop and phase compatibility | Manual review of mode-specific ending, triage and next step | No agent stopping guarantee |
| 12 distribution and documented entry | Canonical/package byte parity, changed-document links, fresh onboarding delivery, plugin tests | Does not update frozen user installation |

## New Structural And Distribution Checks

`test_standalone_review_guidance.py`: both canonical/package skill/reference
pairs exist and match bytes; entry contract is linked before start's lifecycle
Step 1; each of the three bounded examples parses to its intended selector, two
placeholder models, runs=1/concurrency=1; changed shipped Markdown relative file
links resolve from canonical and packaged locations. Parser checks never call
main or spawn a reviewer. Examples with --base or --models must not survive.

Extend the existing canonical-reference onboarding test by parameterizing its
relative path: retain repository-setup.md, add standalone-review.md and the review
skill. Preserve the deterministic baseline fixture and original byte-equality
assertions; actual onboarding must copy all three into the fresh temp bundle.

Run the new structural checks and expanded onboarding selection before editing
shipped content. Expected failure is the missing standalone reference/entry or
unsupported old examples, not a harness/import error. These are documentation
regressions, not a claimed production runtime RED/GREEN loop.

## Combined Regression Selection

From `tools`, one pytest invocation covering:

```text
python -m pytest tests\test_standalone_review_guidance.py tests\test_onboarding.py tests\test_cli_review.py tests\test_report.py tests\test_merge.py tests\test_artifact_integration.py tests\test_plugin.py -q --tb=short
```

Capture exact command/output to the completion artifact. Escalate only if targeted
results indicate another affected boundary. No full-suite or global-coverage
claim follows from this focused selection. Existing test fakes are at external
command/baseline boundaries; fresh onboarding writes only pytest-owned temp paths.

## Reconciliation And Exit

Check canonical/package bytes, links, supported examples, phase compatibility,
no runtime source changes and diff whitespace. Update design status to match the
approved/implemented slice, record exact validation and remaining limitations in
implementation-report.md, findings.md and decisions.md. Gate the completed slice;
do not start a paid review, change installations, publish or close all Phase 04.
