---
project: "atom-v1-improvements"
phase: "phase-03-risk-proportionate-workflow-policy"
author: "Copilot"
date: "2026-11-04"
status: "approved"
poc_report: "poc-report.md"
---

# Phase 03 Design Spec: Risk-Proportionate Workflow Policy

## Purpose

Give Atom a plain-language way to recommend the next evidence step in proportion to a task's uncertainty, while leaving the decision with the developer and preserving existing approval gates. The change is guidance only: it adds no command, workflow engine, risk score, automatic classifier, or hidden enforcement.

## Evidence Base

Phase POC report: [Risk-Proportionate Workflow POC](poc-report.md)

### Established

- Two independent models applied the same supplied route definitions consistently to four fixed cases in 10 successful calls; all four route pairs matched.
- Responses cited facts from the cases, marked the developer as decision-maker, and suggested no gate bypass.
- The prompt itself supplied the route names and definitions. The result establishes consistency under that prompt, not correctness/completeness of the policy or independent discovery of risk factors.
- No developer interaction was simulated. No actual pause, acceptance, rejection, or post-rejection behavior was observed.

### Still Assumed

- These four cases are useful anchors but do not cover every task type or edge case.
- The proposed distinctions for discovery interviews and routine validation are reasonable; neither was exercised in the POC.
- Written recommendation guidance will help preserve developer choice, but it is not a technical guarantee that a model will wait or obey a rejection.
- A failing regression test can serve as the proof for a known, reproducible defect when it directly answers the risk question; no separate regression case was exercised against the real workflow.

## Policy Contract

For a task where the developer's goal or acceptance criteria are missing, Atom asks a focused discovery question before recommending technical work. Once enough intent is known, Atom assesses the available evidence and material unknowns, recommends one next step, explains why and names the limits or consequence of alternatives. The developer chooses whether to proceed.

Recommendations use ordinary language, not risk scores or opaque route codes. A recommendation is not approval. It does not authorize implementation, toolchain installation, paid work, publication, or skipping a gate. Existing human-gate instructions remain the only approval protocol; this guidance claims no hidden enforcement.

The recommendation should state:

1. **Evidence observed:** task facts and the source of any reused approved evidence.
2. **Assessment:** what remains unknown, or why no material technical uncertainty is identified.
3. **Recommended next step:** one bounded action and the reason it fits the evidence.
4. **Alternative considered:** the relevant other path and what it would or would not establish.
5. **Decision needed:** one specific question when a gate or developer preference is involved; do not begin the gated work before approval.

## Proposed Routing Rules

These are candidate rules for developer review. The POC, regression, evidence-reuse, and documentation rules each have one prompt-supplied case. The discovery and routine-validation rules remain untested proposals.

1. **Intent or acceptance is missing:** continue discovery by asking one question at a time. An interview clarifies the desired outcome; it does not prove technical feasibility.
2. **Material technical uncertainty remains and no applicable evidence covers it:** recommend a bounded, falsifiable POC before design. Name what result would confirm, refute, or leave the question inconclusive.
3. **A defect is reproducible and its cause/fix scope is understood:** recommend beginning with a failing regression test. The test may be the proof for that defect; do not add a separate Go spike unless another material technical unknown remains. This route does not skip the design-spec or implementation approval gates: any production change still follows the currently approved spec and TDD process.
4. **An approved POC/spec covers the same assumptions and behavior:** recommend reusing it only after naming its source and limits, then validating the changed boundary. If assumptions or behavior differ, return to a new POC/spec decision rather than stretching old evidence.
5. **Work is already specified and introduces no new uncertainty:** recommend only the relevant routine validation for the changed contract. Do not manufacture a separate POC solely to repeat known checks.
6. **The change is documentation-only and does not change behavior, API, or configuration:** recommend reviewing factual claims against verified behavior and running relevant documentation checks; do not invent a Go experiment.

### Case Anchors From The POC

| Case facts | Candidate next step | Boundary to preserve |
|---|---|---|
| New behavior, no code/experiment, unresolved workspace and version interactions | Prove the risky behavior with a POC | Do not design from the recommendation alone |
| Reproducible defect, cause isolated, failing test captures it, minimal fix understood | Begin with the regression test | The POC did not establish that the policy may bypass the spec gate |
| Approved POC/spec covers unchanged helper behavior; call-site wiring is new | Reuse bounded evidence and validate the caller contract | Prior evidence does not prove the changed wiring |
| Verified documentation correction with no behavior/API/configuration change | Documentation review and relevant checks | Do not imply this establishes code correctness |

## Evidence Reuse Contract

When recommending reuse, the agent must identify the approved artifact, summarize the behavior and assumptions it covers, state what it does not cover, and name the validation for the current changed boundary. If the artifact cannot be found, was not approved, or does not cover the current assumptions, it is not valid reuse evidence. A material assumption change returns the task to discovery/POC rather than being silently treated as routine.

## Developer Decision And Gate Boundary

- A recommendation may explain consequences, but it cannot approve itself.
- When the next action is gated, present the applicable artifact and ask the existing gate question before acting.
- If the developer rejects the recommendation, stop and ask what path they prefer; do not reinterpret silence or a prior approval as consent.
- For a documentation-only change, use the repository's normal review/approval expectations; do not claim a new gate is enforced by this policy.
- This is guidance, not a compliance monitor. A model's statement that the developer decides is not evidence that runtime behavior enforces that choice.

## Content Integration

- Update canonical guidance and the installed/project-packaged copies only after this spec is explicitly approved.
- Reuse current commands and skills. This phase defines no new entry point; any new standalone path belongs to Phase 04 and its separate evidence/gate sequence.
- Keep findings and decisions current, and keep the four cases as examples rather than an exhaustive classifier.
- Validate text and canonical/package parity with the existing documentation and packaging tests. No Go API or product implementation is defined by this spec.

## Error Handling, Concurrency, And Extension Points

There is no runtime API, error path, or concurrent component in this documentation-only phase. These design sections are not applicable. Future routing categories may be added as reviewed guidance examples; they do not justify adding a workflow engine or changing existing commands in this phase.

## Trade-offs Considered

| Option | Chosen? | Why |
|---|---|---|
| Fixed categorical examples with cited evidence | Yes, provisionally | The POC only exercised four named categories; it provides no basis for a numeric score or universal classifier. |
| Numeric risk score and automatic route selection | No | The experiment did not calibrate thresholds, and automatic selection would overstate what was proven. |
| Re-run a POC for every task, including docs-only changes | No | The plan requires proportional evidence; the documentation-only case supports not inventing a Go experiment, subject to developer approval. |
| Reuse prior evidence without checking assumptions | No | The wiring case showed that prior helper evidence does not prove the new caller boundary. |
| Treat `developer_decides: true` as enforcement | No | The POC did not simulate a developer or test runtime approval/rejection. |
| Add new workflow commands in Phase 03 | No | Phase 04 owns entry-point inventory and any new standalone path. |

## Out Of Scope

- Proving that the proposed taxonomy is complete or universally correct.
- Testing actual developer acceptance/rejection behavior or guaranteeing model compliance.
- Adding new commands, automatic scoring, hidden monitoring, or a new workflow engine.
- Changing the proof-first boundary or removing existing approval gates.
- Updating canonical or packaged policy before the developer approves this spec.

## Completeness Checklist

- [x] Purpose states the new capability this phase enables.
- [x] Phase POC report is linked.
- [x] Established evidence and assumptions are separated.
- [x] Policy behaviors are independently reviewable.
- [x] No Go API is proposed because this phase is documentation-only.
- [x] Developer choice is explicitly a guidance contract, not claimed runtime enforcement.
- [x] Rejected approaches and their evidence limits are recorded.

## Implementation Reconciliation

The developer approved this guidance-only spec after accepting the stated POC limitations. The shared policy lives in `skills/atom/references/poc-discipline.md`; existing AGENTS, discovery/spec/TDD/build/start guidance and README/workflow descriptions link or defer to it. Canonical and packaged instruction copies remain aligned. A scoped ignore exception preserves the packaged build skill in fresh clones. No runtime command, API, phase-state logic, classifier, scoring or gate protocol changed.

The [test spec](test-spec.md) maps all six routing rules and cross-cutting boundaries to semantic review and existing documentation/distribution checks. No Go test is needed for the guidance itself, and no new paid model experiment is part of this implementation. Subsequent review triage separately authorized deterministic archive-harness repairs and fake-CLI tests, as recorded in decisions.md and the test spec; these do not add a production API or runtime policy behavior. Actual developer-control behavior and taxonomy correctness remain unproven, as above.
