---
project: "{project-slug}"
phase: "{n/a-or-phase-01-slug}"
date: "{yyyy-mm-dd}"
---

# Decisions Log

<!-- GUIDANCE: Always produce this file, even when empty. Every time you skipped, deferred, worked around, or chose between two valid options on your own, it goes here so the developer can see where your judgement replaced theirs. -->

This file records deviations from instructions and autonomous judgement calls made during the work.

Use it for traceability:

- Record deviations even when they were reasonable.
- Record choices made without developer input when two valid paths existed.
- Record skipped, deferred, or narrowed work.
- Do not use this file to justify ignoring a failed POC or blocked step.
- If nothing happened, keep the file and state that explicitly.

## Decisions

<!-- GUIDANCE: Use this table for instruction deviations, deferred choices, workarounds, or autonomous choices between valid options. Raised with developer? is Yes, No, or Pending. If there is nothing to report, write **"No deviations from instructions."** below this guidance and keep the file. Replace the example row when using the table. -->

{No deviations from instructions.}

| # | Date | Instruction or choice point | What I did instead | Why | Raised with developer? |
|---|---|---|---|---|---|
| _example — replace_ 1 | 2026-01-20 | Phase POC expected a real network peer | Used an in-process fake peer | The external peer was unavailable and the question was codec round-trip behaviour | Pending |
| {number} | {yyyy-mm-dd} | {instruction_or_choice_point} | {what_i_did_instead} | {why} | {Yes-No-or-Pending} |
| {number_2} | {yyyy-mm-dd} | {instruction_or_choice_point_2} | {what_i_did_instead_2} | {why_2} | {Yes-No-or-Pending} |
| {number_3} | {yyyy-mm-dd} | {instruction_or_choice_point_3} | {what_i_did_instead_3} | {why_3} | {Yes-No-or-Pending} |

Decision quality bar:

- Choice point was real: {choice_point_check}
- Alternatives were plausible: {alternatives_check}
- Reason is specific and checkable: {reason_check}
- Developer visibility is recorded: {visibility_check}

Do not include:

- Normal execution of the approved plan.
- Mechanical edits that follow directly from the spec.
- Personal preference when no decision affected the work.

Raised with developer values:

- Yes: the developer has already seen and accepted or rejected the decision.
- No: the decision was made and has not yet been surfaced.
- Pending: the decision must be raised at the next gate before depending on it further.

Decision severity hints:

- Record even low-impact deviations; absence of a row means no deviation happened.
- Escalate any decision that changes user-visible behaviour.
- Escalate any decision that narrows POC evidence, phase scope, or test coverage.

## Standing Waivers

<!-- GUIDANCE: Record developer-granted waivers such as "stop asking me about X". A waiver covers continuing the plan, never changing it. A refuted POC or blocked step is always surfaced regardless of any waiver. If none, write "None." Replace the example row when using the table. -->

| Waiver | Granted by | Date | Scope | Still surface if... |
|---|---|---|---|---|
| _example — replace_ Do not ask before updating generated fixtures | {developer_name} | 2026-01-20 | Fixture files under `testdata/` for this phase | Fixture schema changes or generated output changes behaviour |
| {waiver} | {granted_by} | {yyyy-mm-dd} | {scope} | {surface_condition} |
| {waiver_2} | {granted_by_2} | {yyyy-mm-dd} | {scope_2} | {surface_condition_2} |

Waiver rules:

- A waiver must have a named grantor.
- A waiver must have a bounded scope.
- A waiver never permits continuing after a refuted POC without surfacing it.
- A waiver never permits changing the plan silently.

## Skipped Steps

<!-- GUIDANCE: Record every skipped process step. The reason must be specific and checkable; "it seemed straightforward" is not one. Skips should be rare and developer-visible. If none, write "None." -->

| Step | Reason | Developer informed? |
|---|---|---|
| {step_or_none} | {specific_checkable_reason} | {Yes-No-or-Pending} |
| {step_2_or_none} | {specific_checkable_reason_2} | {Yes-No-or-Pending} |

Skip quality bar:

- Reason points to evidence, not convenience: {evidence_for_skip}
- Risk of skipping is understood: {skip_risk}
- Next opportunity to revisit is recorded: {revisit_point}

## Completeness Checklist

<!-- GUIDANCE: Check these before the gate. The goal is honest traceability, not a clean-looking log. -->

- [ ] File exists even if there are no deviations.
- [ ] "No deviations from instructions." is written when there is nothing to report.
- [ ] Every autonomous choice or workaround is recorded.
- [ ] Every skipped step has a specific, checkable reason.
- [ ] Developer visibility is marked Yes, No, or Pending.
- [ ] Standing waivers are scoped and include conditions that still require surfacing.
- [ ] Refuted POCs and blocked steps are never hidden by waivers.
- [ ] Each waiver has a named grantor and bounded scope.
- [ ] Every Pending item has a next gate or follow-up point.
- [ ] The file is present in the expected specs directory.
- [ ] The log separates deviations from normal plan execution.
- [ ] No Pending decision lacks a named follow-up point.
- [ ] Decisions that changed scope are visible before the next build step.
- [ ] Skipped steps are not hidden inside the general Decisions table.
- [ ] Each decision says what happened instead, not just what did not happen.
- [ ] Each reason can be checked against code, artifacts, or developer input.
- [ ] Waivers are not treated as permission to skip evidence.
- [ ] The log is understandable without private agent context.
- [ ] Dates use the same format as the frontmatter date.
- [ ] Empty state text is present when all tables are intentionally unused.
- [ ] No decision rewrites a refuted or inconclusive POC as confirmed.
- [ ] The explicit empty state is not combined with active table rows.
- [ ] Scope changes are visible before implementation continues.
