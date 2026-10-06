---
project: "{project-slug}"
phase: "{n/a-or-phase-01-slug}"
date: "{yyyy-mm-dd}"
---

# Findings Log

<!-- GUIDANCE: Always produce this file, even when empty. This is where you put what you saw and chose not to act on, so the developer can audit that judgement. A missing file is ambiguous; an explicit no-findings statement is evidence the check happened. -->

This file records issues, ambiguities, and reusable learnings noticed during the work but deliberately not fixed in this phase.

Use it for auditability:

- Record observations, not guesses.
- Explain why the item was not fixed now.
- Prefer precise file paths and line numbers over broad package names.
- Keep the tone factual; this is not a blame document.
- If the item changes phase scope, raise it at the next gate instead of burying it here.

## Findings

<!-- GUIDANCE: Use the table for anything real that was observed and deferred. Severity is High, Medium, or Low. Where should be `file:line` when known, or a precise artifact path. If there is nothing to report, write **"No findings."** below this guidance and keep the file. Replace the example row when using the table. -->

{No findings.}

| # | Finding | Severity | Where | Why not fixed now | Suggested action |
|---|---|---|---|---|---|
| _example — replace_ 1 | Existing parser silently accepts empty frames | Medium | `parser.go:42` | This phase only adds framing metrics | Add a validation behaviour to the next phase design spec |
| {number} | {finding} | {High-Medium-Low} | `{file_line_or_artifact}` | {why_not_fixed_now} | {suggested_action} |
| {number_2} | {finding_2} | {High-Medium-Low} | `{file_line_or_artifact_2}` | {why_not_fixed_now_2} | {suggested_action_2} |
| {number_3} | {finding_3} | {High-Medium-Low} | `{file_line_or_artifact_3}` | {why_not_fixed_now_3} | {suggested_action_3} |

Finding quality bar:

- Specific: {specificity_check}
- Actionable: {actionability_check}
- Deferred for a reason, not ignored: {defer_reason_check}
- Safe to leave for this phase: {safety_check}

Do not include:

- Style preferences without project impact.
- Speculation without evidence.
- Work already fixed in the current change.

Severity guide:

- High: likely to break correctness, safety, data integrity, or a gate if ignored.
- Medium: likely to cause rework, confusing behaviour, or missed coverage later.
- Low: useful cleanup or documentation that does not threaten this phase.

Location guide:

- Prefer `file:line` for code.
- Use an artifact path for design, report, or plan issues.
- Use `unknown` only when the finding is real but the exact source is not available.

Suggested action guide:

- Name the next concrete action.
- Name the phase or gate where it should be handled.
- Avoid vague actions such as "look into this".

## Ambiguities Resolved

<!-- GUIDANCE: Record cases where you chose an interpretation so work could continue. Any low-confidence row must be raised at the next gate, not buried here. If none, write "None." Replace the example row when using the table. -->

| Ambiguity | Interpretation chosen | Why | Confidence |
|---|---|---|---|
| _example — replace_ Should retries include validation errors? | No | Validation errors are deterministic caller input issues | High |
| {ambiguity} | {interpretation_chosen} | {why} | {High-Medium-Low} |
| {ambiguity_2} | {interpretation_chosen_2} | {why_2} | {High-Medium-Low} |

Escalation rule:

- High confidence: record and continue.
- Medium confidence: record and mention at the next gate if it affects user-visible behaviour.
- Low confidence: record here and raise at the next gate before depending on it.

## Learnings

<!-- GUIDANCE: Capture reusable knowledge discovered during the work. If a learning generalises beyond this component, propose promoting it into the Atom references rather than leaving it here, and say so explicitly. If none, write "None." -->

- {learning_1}
- {learning_2}
- Promotion candidates for Atom references: {promotion_candidates_or_none}

Learning quality bar:

- Reusable by another agent: {reusable_check}
- Backed by code, POC output, or test output: {evidence_check}
- Scoped to this component or general to Atom: {scope_check}

## Completeness Checklist

<!-- GUIDANCE: Check these before the gate. The point is not to find problems; the point is to make deferred judgement visible. -->

- [ ] File exists even if there are no findings.
- [ ] "No findings." is written when there is nothing to report.
- [ ] Each finding has severity, location, reason deferred, and suggested action.
- [ ] Every resolved ambiguity has confidence recorded.
- [ ] Low-confidence ambiguity is raised at the next gate.
- [ ] Reusable learnings are captured or explicitly marked "None."
- [ ] General learnings include a recommendation on whether to promote them to Atom references.
- [ ] No fixed issue remains listed as deferred.
- [ ] No low-confidence ambiguity is left without a gate action.
- [ ] The file is present in the expected specs directory.
- [ ] The contents distinguish evidence from judgement.
- [ ] Severity follows the guide above.
- [ ] Suggested actions are concrete enough to schedule.
- [ ] Locations are precise or explicitly marked `unknown`.
- [ ] No finding contradicts the POC verdict or design spec.
- [ ] Items that require developer input are marked for the next gate.
- [ ] The table is removed or ignored only when "No findings." is the explicit content.
- [ ] The file can be reviewed without reading private agent notes.
- [ ] The explicit empty state is not combined with active table rows.
- [ ] Deferred work is not described as complete.
