---
project: "atom-v1-improvements"
phase: "phase-03-risk-proportionate-workflow-policy"
author: "Copilot"
date: "2026-11-04"
status: "approved"
---

# POC Brief

## Problem

Atom needs to recommend a workflow proportionate to a task's uncertainty and evidence. A routine regression or documentation-only correction should not be forced into a fabricated Go experiment, while a risky change must not be mislabeled as routine to escape proof-first steps. Atom should explain its recommendation and leave the choice to the developer.

- Developer-visible outcome: A recommendation that names the next step, cites the available evidence and uncertainty, explains alternatives, and leaves the decision with the developer.
- Current failure or limitation: Phase 03 of the accepted roadmap identifies concrete task types but has no validated routing policy.
- Non-negotiable constraint: No route may silently waive a required gate or authorize an action the developer has not approved.
- Evidence already known: The accepted roadmap calls for representative cases and explicit policy approval; it identifies this as policy validation, not a performance benchmark.

## The Question

With the same risk/evidence rubric and four fixed cases, will two independent models recommend the same justified next workflow step in every case, cite only supplied evidence, and leave the final choice with the developer without suggesting an unapproved gate bypass?

## Why This Is The Riskiest Unknown

The largest uncertainty is whether a concise policy can distinguish different evidence states consistently without turning proportionality into a gate loophole. If discovered after writing canonical guidance, ambiguous routes could mislead later implementation and be expensive to unwind. This experiment tests recommendation consistency only; it cannot establish that the policy is correct for all developer needs.

- Feasibility risk considered: Whether the approved case distinctions can be expressed as a bounded routing rubric.
- Performance risk considered: Not relevant; no performance claim is being tested.
- Integration risk considered: Whether two independent models can apply the rubric to the same fixed case inputs. No product integration is tested.
- Ergonomics risk considered: Wording and presentation remain open until the policy is reviewed with the developer.
- Why this one was chosen: Inconsistent or unsupported routing would invalidate the proposed policy before it is written into guidance.

## Success Criteria

Each model must return one exact route label, cite supplied facts, explain the remaining uncertainty, give a concise rationale, and state that the developer makes the decision:

- `POC_FIRST`: material technical uncertainty remains; prove the risky behavior before design.
- `REGRESSION_TEST_FIRST`: a defect and its cause are already reproducible/understood; start with a failing regression test and implement under TDD, adding a separate POC only if a material unknown remains.
- `REUSE_EVIDENCE_AND_VALIDATE`: a prior approved POC/spec still covers the unchanged risk; explain its limits and validate the affected contract.
- `DOCUMENTATION_REVIEW`: documentation-only change with no behavior/API change; review the text and relevant documentation checks without inventing a Go experiment.

| Observation | Means |
|---|---|
| After permitted retries and fallback, both models return valid, evidence-grounded answers and the same route for all four cases; neither claims unsupported facts or bypasses a gate; each leaves the choice with the developer | Confirmed |
| After permitted retries and fallback, all compared models return valid answers, but any case has materially different routes, an unsupported rationale, or an unapproved gate bypass | Refuted |
| After permitted retries and fallback, a required model-case answer is missing, timed out, or unclassifiable | Inconclusive |

Minimum acceptable evidence:

- Number of runs: Hard ceiling of 48 model calls, including probes, retries, and alternate-model calls. Without the hard cap, the procedure below could require 51 calls; the cap is binding, so stop immediately at 48 even if some slots remain incomplete.
- Input size or rate: Four one-page-or-shorter fixed cases; every model receives identical rubric and case text.
- Environment notes that affect interpretation: Use the Copilot CLI account configured for model access, fixed-evidence mode with tools/custom instructions disabled, and the same CLI/runtime for all calls. Initial pair, previously used successfully for Phase 02 review: `gpt-5.3-codex` and `claude-opus-5.5`. Make one availability probe per model. If a probe reports unavailable, use at most one alternate model for that model's cases, with one probe. For a model-case response, allow at most two retries after the initial attempt. If all three attempts fail or are unclassifiable, use the same alternate for that case, with at most three total attempts. Do not select more than one alternate.
- Output values that must be pasted into the report: Exact command, model/case identifier, probe/attempt number, exit status, raw response, selected route, evidence cited, and any disagreement or policy violation.

## Scope

### Will Do

- Evaluate four fixed cases corresponding to risky new behavior, a reproducible understood regression, previously proven wiring, and documentation-only work.
- Send the same case and rubric independently to the proposed pair; if permitted, use one alternate model only for unavailable or repeatedly failing model-cases.
- Compare route labels and check rationales against the supplied facts and the gate boundary; record every probe and attempt verbatim.

### Will Not Do

- Claim model agreement proves the policy is universally correct or that all task types are covered.
- Modify production code, canonical skills, workflow rules, or the phase plan.
- Treat a model recommendation as developer approval or automatically perform its suggested work.
- Exceed the 48-call hard cap, retry beyond the stated per-case limit, add cases, or use more than one alternate model.

## Approach Sketch

- Create one disposable Go command under `poc/atom-v1-risk-proportionate-policy/` containing the fixed rubric and four case prompts.
- Make one availability probe per proposed model, then invoke the CLI per model-case with model-side tools and custom instructions disabled; capture raw output and exit status.
- Retry failed or unclassifiable model-case calls at most twice; after three failed attempts, use at most one alternate model for that case, with up to three total attempts. A failed availability probe also permits one alternate for the unavailable model's cases.
- Print every probe and attempt and compare route labels and rationales against the criteria; preserve verbatim output in the POC report. The uncapped maximum is 51 calls (2 primary probes + 1 alternate probe + 8 model-case slots x 6 attempts); the absolute ceiling remains 48.
- Stop at the cap, or earlier when all required cases have complete valid responses.

Disposable shortcuts allowed:

- Hardcode the four case facts and route labels in the throwaway command.
- Manually assess rationale quality against the fixed evidence; do not automate subjective scoring.

Shortcuts not allowed because they would invalidate the result:

- Different prompts or context between models, hidden repository instructions/tools, retries beyond the stated limits, a second alternate, or exceeding the hard cap.

## Open Questions For The Developer

- None for this bounded experiment. The resulting routing policy still requires the developer's review and explicit approval before guidance changes.

## Completeness Checklist

- [x] Problem is written in the developer's terms.
- [x] The Question is one falsifiable sentence.
- [x] The riskiest unknown is ranked against feasibility, performance, integration, and ergonomics.
- [x] Success criteria are measurable observations from the model-call experiment.
- [x] Scope includes explicit exclusions.
- [x] Approach fits in one disposable Go command.
- [x] Open questions are listed or explicitly marked "None."
- [x] The user-approved hard ceiling is 48 calls; the uncapped retry/fallback maximum is 51, so the 48-call cap can leave the result Inconclusive.
- [x] The POC can be run from the command line.
- [x] The report can distinguish Confirmed, Refuted, and Inconclusive without reinterpretation.
- [x] The spike path and slug are named.
- [x] No production implementation decisions are smuggled into the brief.

## Execution Annotation (Not A Retrospective Change To The Experiment)

The approved amended brief was executed before the design. Exact rendered rubric and four fixed case texts are preserved in [the POC report](poc-report.md). The harness named `gpt-5.6-sol` as its sole alternate; no alternate, retry, or fallback was used in the successful ten-call run. Removed duplicate success/refutation rows introduced during the earlier budget amendment; the remaining post-retry criteria and hard ceiling are unchanged. Developer-decision markers establish response wording only, not an actual approval/rejection interaction.


## Post-Review Arithmetic Correction: 2026-11-06

The original 39-call estimate was incorrect. Exhausting both primary and alternate attempts for all eight slots could require 51 calls without a cap. The approved 48-call hard ceiling was never changed; it takes precedence over completing retries. The historical run used ten calls, with no retries or alternate. This annotation corrects the estimate, not the experiment, prompts or observed result. The brief was approved before execution; its former draft metadata was stale.
