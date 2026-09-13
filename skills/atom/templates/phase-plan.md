---
project: "{project-slug}"
date: "{yyyy-mm-dd}"
status: "draft"
phase_count: "{number-of-phases}"
---

# Phase Plan

<!-- GUIDANCE: Write this after the project-level POC succeeds. The plan decomposes proven work into independently shippable phases. It is not permission to design unproven internals. -->

## Goal

<!-- GUIDANCE: Write 2-4 sentences describing what the finished work delivers to the developer or user. Good answers describe observable capability. Bad answers list internal tasks without explaining the outcome. -->

{goal_statement}

## What The POC Proved

<!-- GUIDANCE: Summarize only what the project-level POC established and link to the report. The plan must follow from evidence, not imagination. Do not claim anything the report explicitly did not cover. -->

Project-level POC report: [{poc_report_title}]({relative_path_to_poc_report})

{short_evidence_summary}

## Phases

<!-- GUIDANCE: Each row must be independently shippable. Front-load risk. Needs POC? is Yes unless the phase has a specific recorded reason to skip. Replace the example row. -->

| # | Phase | Delivers | Risk (H/M/L) | Needs POC? | Depends on |
|---|---|---|---|---|---|
| _example — replace_ 01 | Stream parser boundary | Accepts one framed input and emits one parsed message | H | Yes | Project POC |
| {phase_number} | {phase_name} | {deliverable} | {H-M-or-L} | {Yes-or-No-with-reason} | {dependencies} |
| {phase_number_2} | {phase_name_2} | {deliverable_2} | {H-M-or-L} | {Yes-or-No-with-reason} | {dependencies} |
| {phase_number_3} | {phase_name_3} | {deliverable_3} | {H-M-or-L} | {Yes-or-No-with-reason} | {dependencies} |

Planning guardrails:

- Keep each phase small enough for one focused design spec and one focused test spec.
- Prefer a phase that removes an unknown over a phase that adds breadth.
- Do not group unrelated risky work just because it touches the same package.

## Phase Detail

<!-- GUIDANCE: Repeat this block for every phase in the table. Keep each phase small enough to review and ship on its own. -->

### Phase {NN}: {phase_slug}

<!-- GUIDANCE: The objective says what new capability exists after this phase, not what files change. -->

**Objective:** {objective}

<!-- GUIDANCE: Scope in/out must prevent phase creep. A good scope out item names work that is tempting but intentionally deferred. -->

**Scope in:**

- {scope_in_1}
- {scope_in_2}

**Scope out:**

- {scope_out_1}
- {scope_out_2}

<!-- GUIDANCE: State the technical risk plainly. If risk is low, explain why evidence already exists. -->

**Technical risk:** {technical_risk}

<!-- GUIDANCE: Provide a phase POC question unless skipping is justified by prior evidence. "It seemed straightforward" is not a justification. Good skip: "Phase 2's POC already proved the codec round-trips and this phase only moves the call site." -->

**POC question or skip justification:** {poc_question_or_skip_justification}

<!-- GUIDANCE: Done when must be concrete and verifiable by commands, tests, or observable behaviour. -->

**Done when:**

- {done_condition_1}
- {done_condition_2}

<!-- GUIDANCE: Estimate size to keep review risk controlled. Prefer small phases over broad ones. -->

**Estimated size:** {small-medium-large-or-rough-files}

**Primary artifacts:**

- POC report: `specs/{project}/phase-{NN}-{phase_slug}/poc-report.md`
- Design spec: `specs/{project}/phase-{NN}-{phase_slug}/design-spec.md`
- Test spec: `specs/{project}/phase-{NN}-{phase_slug}/test-spec.md`

**Review focus:** {what_reviewers_should_focus_on}

## Sequencing Rationale

<!-- GUIDANCE: Explain why this order front-loads risk and keeps every phase independently shippable. Bad rationale: "this is the order I thought of." Good rationale: "phase 1 proves decoding before phase 2 wires storage, so storage work is not built on an unknown parser." -->

{sequencing_rationale}

## Deferred / Out Of Scope

<!-- GUIDANCE: List work intentionally not included in this plan and give reasons. This protects the phase plan from silently expanding. -->

| Item | Reason deferred |
|---|---|
| {deferred_item_1} | {deferred_reason_1} |
| {deferred_item_2} | {deferred_reason_2} |

## Open Risks

<!-- GUIDANCE: Capture known risks that remain after the project POC. Mitigations should point to a phase, POC, test, or developer decision. -->

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| {risk_1} | {High-Medium-Low} | {High-Medium-Low} | {mitigation_1} |
| {risk_2} | {High-Medium-Low} | {High-Medium-Low} | {mitigation_2} |
| {risk_3} | {High-Medium-Low} | {High-Medium-Low} | {mitigation_3} |

Risk notes:

- Highest remaining risk: {highest_remaining_risk}
- First phase that addresses it: {phase_that_addresses_risk}
- Risk accepted until later because: {accepted_risk_reason_or_none}

## Completeness Checklist

<!-- GUIDANCE: Do not pass the gate until every item is true or explicitly called out as blocked. -->

- [ ] Goal describes the finished capability.
- [ ] Project POC report is linked.
- [ ] Every phase delivers something independently shippable.
- [ ] Every phase has either a POC question or a recorded, evidence-based justification for skipping.
- [ ] Sequencing front-loads the highest risks.
- [ ] Dependencies are explicit.
- [ ] Deferred work has reasons.
- [ ] Open risks have mitigations.
- [ ] High-risk phases appear before broad build-out phases where possible.
- [ ] No phase depends on behaviour that is still only assumed.
- [ ] Artifact paths follow `specs/{project}/phase-NN-{slug}/`.
