---
project: "{project-slug}"
phase: "{n/a-or-phase-01-slug}"
author: "{agent-or-developer-name}"
date: "{yyyy-mm-dd}"
status: "draft"
---

# POC Brief

<!-- GUIDANCE: Copy this template before building the spike. Keep the brief short enough that the POC can be implemented as one disposable Go program. Link relevant references such as ../references/poc-discipline.md only when they clarify the experiment. -->

## Problem

<!-- GUIDANCE: Write 2-4 sentences in the developer's language. Good answers describe the real job to be done and the constraint that makes it hard. Bad answers describe an imagined implementation before evidence exists. -->

{problem_statement}

Capture these facts before narrowing the question:

- Developer-visible outcome: {developer_visible_outcome}
- Current failure or limitation: {current_failure_or_limitation}
- Non-negotiable constraint: {non_negotiable_constraint}
- Evidence already known: {known_evidence_or_none}

## The Question

<!-- GUIDANCE: State exactly one falsifiable sentence. The POC passes or fails by answering this sentence, not by producing interesting side observations. Weak: "will this design work?" Strong: "can a single goroutine drain this channel fast enough to hold p99 under 10ms at 50k msg/s?" -->

{one_falsifiable_question}

## Why This Is The Riskiest Unknown

<!-- GUIDANCE: Rank uncertainties in this order: feasibility > performance > integration > ergonomics. Explain why this question would be expensive to discover late. Also name the uncertainties not chosen and why they are lower risk right now. -->

{risk_rationale}

- Feasibility risk considered: {feasibility_risk}
- Performance risk considered: {performance_risk}
- Integration risk considered: {integration_risk}
- Ergonomics risk considered: {ergonomics_risk}
- Why this one was chosen: {chosen_risk_reason}

## Success Criteria

<!-- GUIDANCE: Use concrete observations the running program can produce. "Works" is not measurable. Each row must say how the observation confirms or refutes the question. Replace the example row. -->

| Observation | Means |
|---|---|
| _example — replace_ p99 latency stays below 10ms for 50k messages/s for three 60s runs | Confirmed |
| {measurable_observation_1} | {Confirmed-or-Refuted} |
| {measurable_observation_2} | {Confirmed-or-Refuted} |
| {measurable_observation_3} | {Confirmed-or-Refuted} |

Minimum acceptable evidence:

- Number of runs: {run_count}
- Input size or rate: {input_size_or_rate}
- Environment notes that affect interpretation: {environment_notes}
- Output values that must be pasted into the report: {required_output_values}

## Scope

<!-- GUIDANCE: The exclusions matter as much as the included work. Future readers will use this section to avoid over-reading the report. If the POC proves one happy path, say which unhappy paths it does not prove. -->

### Will Do

<!-- GUIDANCE: List only the actions needed to answer the question. Good scope fits in one main.go or very close to it. Bad scope starts becoming a prototype. -->

- {included_action_1}
- {included_action_2}
- {included_action_3}

### Will Not Do

<!-- GUIDANCE: Explicitly exclude production hardening, broad test coverage, polished APIs, and unrelated risks. These exclusions protect the design from claiming evidence the POC did not generate. -->

- {excluded_action_1}
- {excluded_action_2}
- {excluded_action_3}

## Approach Sketch

<!-- GUIDANCE: Give a few bullets on how the spike will be built. If this exceeds one main.go worth of work, the question is too broad; narrow it before coding. Mention only disposable implementation choices. -->

- Create {poc_path} with a small Go command.
- Simulate or connect to {dependency_or_input}.
- Print {measurements_or_observations}.
- Run with `{command_to_run}`.
- Stop as soon as {stop_condition} is observed.
- Archive the spike under `poc/{poc_slug}` after it runs.

Disposable shortcuts allowed:

- {shortcut_1}
- {shortcut_2}

Shortcuts not allowed because they would invalidate the result:

- {invalidating_shortcut_1}

## Open Questions For The Developer

<!-- GUIDANCE: Capture unresolved product intent, acceptable thresholds, or constraints the repository cannot answer. Do not ask implementation questions the POC itself can answer. If there are none, write "None." -->

- {open_question_1}
- {open_question_2}

## Completeness Checklist

<!-- GUIDANCE: Check every item before handing this brief to the developer gate. Leave unchecked items visible rather than silently weakening the brief. -->

- [ ] Problem is written in the developer's terms.
- [ ] The Question is one falsifiable sentence.
- [ ] The riskiest unknown is ranked against feasibility, performance, integration, and ergonomics.
- [ ] Success criteria are measurable observations from a running Go program.
- [ ] Scope includes explicit exclusions.
- [ ] Approach fits in one disposable Go command or the question has been narrowed.
- [ ] Open questions are listed or explicitly marked "None."
- [ ] Any threshold in the question has a source or is marked as a developer assumption.
- [ ] The POC can be run from the command line.
- [ ] The report will be able to answer Confirmed, Refuted, or Inconclusive without reinterpretation.
- [ ] The spike path and slug are named.
- [ ] No production implementation decisions are smuggled into the brief.
