---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
date: "2026-11-02"
status: "executed-confirmed"
---

# POC Brief: Honest Review Continuation

## Problem

A developer should be able to review source when a demonstrable toolchain
incompatibility prevents mechanical checks, without calling that review fully
validated. Genuine source failures and unexplained failures must still block.
This is Phase 02 of the accepted v1.0 roadmap, not permission to suppress the
failing macOS/Windows CI suites in the parent PR.

- Outcome: a narrowly evidenced incompatibility reaches a controlled reviewer
  stub with explicit degraded evidence; source and unknown failures do not.
- Current behavior: required failures raise before model invocation; selection
  failures also terminate review.
- Fixed constraints: preserve exact launch intent, child-only selection, failed
  output, passing-check scope and existing unpinned/skip behavior.
- Known evidence: Phase 01 provides selection/provenance, but its current CI is
  failing. See [findings](findings.md); this spike cannot close that blocker.

## The Question

Can bounded controls distinguish a declared Go-minimum incompatibility from genuine or ambiguous source/check failures on the same frozen fixture, allowing only the evidenced incompatibility to reach a reviewer stub with truthful degraded evidence?

## Why This Is The Riskiest Unknown

False tooling-only classification would hide defects and spend reviewers'
attention on an incorrectly described snapshot. Feasibility is the first risk:
compiler diagnostic wording alone cannot establish the cause.

Performance is not the chosen question; deadlines are spend/cleanup limits,
not benchmarks. Prompt/report integration is next, but a correct renderer
cannot rescue an incorrect classification. Default versus opt-in UX and final
exit codes remain later design decisions.

The initial incompatibility class is deliberately narrow: the module's declared
Go minimum exceeds the verified selected compiler. A passing compatible control
is evidence about that control, not proof that the requested compiler passed,
that no version-specific bug exists, or that arbitrary tool failures are safe.

## Proposed Fixture Matrix

All cases use small public, standard-library-only Go fixtures. Expected labels
are a separate grading key; the classifier must not read case names or labels.

| Fixture | Required observation |
|---|---|
| Compatible compiler and valid source/tests | Bounded checks pass; stub receives ordinary evidence scoped to the checks actually run |
| Higher declared minimum, otherwise valid fixture | Selected compiler fails; same frozen source passes build/vet/test under a verified compatible control; only this case reaches the stub as degraded |
| Compatible minimum with compile defect | Actual compile failure; blocked as source failure or conservatively unknown, never tooling-only |
| Compatible minimum with failing assertion | Actual test failure; blocked as source failure or conservatively unknown, never tooling-only |
| Higher minimum plus compile defect | Compatible control also fails; mixed/source evidence blocks the stub |
| Missing requested executable | Explicit selection failure; blocked as unknown/unverified, no automatic replacement |
| Deliberately slow Go test | Compile with selected Go, invoke that binary directly, capture entry then timeout with verified cleanup; blocked, not classified from matching stderr text |
| Compatible control cannot complete | Explicit simulated runner-error evidence; blocked as unknown, never counted as a native compiler observation |
| Source changes between selected and control attempts | Different source hashes invalidate the comparison; blocked as unknown |

## Success Criteria

| Observation | Verdict |
|---|---|
| Two complete sweeps of all nine cases; valid bounded control passes; only the higher-minimum valid fixture is admitted as degraded; zero source/unknown admissions | Confirmed for this bounded incompatibility class |
| Any defective, timed-out, missing-tool, changed-snapshot or ambiguous case reaches the stub as tooling-only, or failed/unchecked evidence is represented as passed | Refuted |
| Required installed distributions are unavailable, a fixture does not produce its intended signal, any case is unexecuted, or a limit interrupts the batch | Inconclusive; stop without redesign/retry |

Minimum evidence:

- Two serial sweeps; counts are proposed finite-case acceptance criteria, not a
  statistical reliability or cross-platform claim.
- Two already installed direct distributions: proposed Go 1.26.9 as selected
  compiler and Go 1.27.3 as compatible control. Verify their actual version,
  canonical root and hashes; if unavailable, stop rather than install/substitute.
- Same fixture source hashes and common child environment for selected/control
  attempts. Record the deliberately changed snapshot separately.
- Log every command, executable identity, child controls, outcome, exit code,
  stdout/stderr, classification, rationale, stub call count and final prompt.
- Failed selected checks remain FAILED; control passes are labelled separately.
  Failed/skipped/unavailable categories remain in scope for the reviewer.
- Preserve raw logs outside Git and publish only explicitly labelled path
  redactions. Paste actual output into the report; do not invent expected logs.

## Scope

### Will Do

- After approval, create one disposable Python driver under
  `poc\review-tooling-continuation\spike-compiled-timeout.py`, wrapping throwaway Go modules.
  Atom's production tooling is Python; the native fixtures are Go.
- Use structured launch/probe/command outcomes, declared fixture metadata,
  compatible control results and snapshot identity. Diagnostic text is evidence,
  not the sole classifier.
- Run native build/vet/test and selected-root formatting where applicable.
  Compile the slow test with the selected compiler, then invoke its binary
  directly using `-test.v -test.count=1 -test.run=TestWait` and a two-second
  deadline. Record binary hashes before/after, alongside frozen source hashes.
  Missing entry, changed binary, cleanup errors or incomplete output make
  this observation Inconclusive; do not simply accept any timed_out result.
- Keep simulated runner-error/control-unavailability evidence explicitly
  separate from native results.
- Render failure-aware toolchain evidence and send it to an in-process stub.
  Log a real stub receipt, not an account claiming a model ran.

### Will Not Do

- Start another batch, retry automatically, change production, or publish under this approval.
- Change production code, existing tests, review policy, CLI defaults or exit
  semantics; add a fallback compiler; mutate machine settings; weaken a gate.
- Repair or relabel parent CI failures, or infer that those failures are tooling-only.
- Call paid models, access another target repository, download/install tools or
  dependencies, invoke Makefile recipes, or perform external publication.
- Establish native race/CGO, dependency, analyzer, workspace or all-platform
  compatibility. Record unrun checks explicitly; no full validation claim.
- Implement token-budget preflight or post-patch review repairs from
  girishmotwani/atom#14 and girishmotwani/atom#16.

## Approach And Proposed Spend

One serial batch after explicit approval: two sweeps, at most 96 native
commands including Go/gofmt probes/setup and compiled-test invocations;
60 seconds per ordinary command, two seconds for each slow-test binary
invocation with the unchanged two-second cleanup grace, and a 15-minute
overall ceiling. Zero model calls, downloads or installations. These are
proposed bounds requiring approval, not measured execution times.

Keep fixture changes inside the spike and local scratch directories. Child
settings use GOTOOLCHAIN=local, selected bin precedence, removed inherited
GOROOT, isolated fixture workspace/cache and offline standard-library inputs.
Preserve parent environment and GOENV contents; record every fixture-only
override. No global go env writes, cache clearing or original POC replay.

Stop on an invalid premise, misleading admission, missing evidence or reached
limit. Preserve the failure and gate any different treatment or repeat batch.
Archive the driver and a short report; do not promote the classifier into
production before the report and design gates.

## Existing Integration Boundaries

- [Review orchestration](../../tools/atom/review.py) currently raises before
  invocation for required failures.
- [Selection](../../tools/atom/go_selection.py) already distinguishes request,
  probes, diagnostics and failed execution.
- [Toolchain evidence](../../tools/atom/toolchain.py) excludes only categories
  whose gates passed; reuse that principle rather than blanket exclusions.
- [CLI](../../tools/atom/cli.py) currently returns failure without a review report.
  This POC does not choose the new CLI/report compatibility contract.

## Open Product Decisions

Default versus opt-in continuation, permission for compatible-control execution,
control cost, final exit statuses and report/schema compatibility remain
unapproved. The spike tests whether a conservative classification is feasible;
its disposable labels and proposed limits are not production API decisions.

## Changed Treatment And Approval Boundary

The [first report](poc-report.md), [revised-control report](poc-report-control-1.27.3.md)
and [package-mode diagnostic](windows-timeout-trace-report.md) remain
Inconclusive and immutable. The
[direct binary probe](windows-test-entry-report.md) confirmed its entry and
timeout cleanup, without reproducing or fixing the original supervisor failure.

This proposal changes only the slow-case timed command after selected-compiler
test compilation. Ordinary fixture build/vet/test, declared minimum 1.27.0,
selected Go 1.26.9, control Go 1.27.3, classifier, nine-case matrix, two sweeps
and acceptance criteria remain unchanged. Add explicit binary identity and
complete-cleanup checks; keep failed evidence and unknown cases blocking.

This POC tests conservative classification, not general Go-supervised timeout
reliability. Keep that unresolved runner failure as a separate finding and
retain the original timeout failure in published evidence. A successful new
batch must not relabel parent CI or the original runner failure as fixed.

The new disposable driver is separate; do not edit executed drivers. Use one
fresh outside-Git output directory. No model calls, downloads, installations,
production patch/design, push, PR or automatic retry.

On 2026-11-02 the developer approved exactly one revised classification
batch using this brief. This approval authorizes the described two-sweep run
only. It does not authorize automatic retries, production changes, a design,
or publication; report the evidence and stop at the POC gate.


## Executed Result

The approved batch completed both sweeps: 18/18 observations, 82 native
commands, four reviewer-stub receipts, zero model calls, and a Confirmed verdict.
See [the report](poc-report-compiled-timeout.md). This confirms only the bounded
fixture classification; the earlier Go-supervised timeout cleanup failure and
parent CI failures remain unresolved.
