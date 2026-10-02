---
project: "{project-slug}"
phase: "{n/a-or-phase-01-slug}"
poc_slug: "{poc-slug}"
verdict: "{Confirmed-or-Refuted-or-Inconclusive}"
date: "{yyyy-mm-dd}"
spike_path: "poc/{poc-slug}"
---

# POC Report

<!-- GUIDANCE: Write this only after the spike has been built and run. A report without verbatim terminal output is not evidence. See ../references/poc-discipline.md for the rules this report enforces. -->

## The Question

<!-- GUIDANCE: Restate the question verbatim from the brief. Do not reword it. Rewording lets a miss look like a hit and turns evidence into storytelling. -->

{exact_question_from_brief}

## Verdict

<!-- GUIDANCE: Write Confirmed, Refuted, or Inconclusive with a one-line justification. All three outcomes are successes. A refutation saved the design and should be reported with enthusiasm, not apology. An inconclusive result must not be written up as confirmed. -->

**{Confirmed-or-Refuted-or-Inconclusive}.** {one_line_justification}

## Evidence of Treatment

<!-- GUIDANCE: Comparison spikes only. Delete this whole section for a single-arm spike. See treatment-evidence.md. Fill this in BEFORE reading any result -- it establishes that each arm actually received what it was supposed to receive. A treatment that never reached the model produces a clean, confident, meaningless result that is indistinguishable from a genuine null. -->

Arms compared: {arm_names}

**Check 1 — the treatment reached the model.** Rendered prompt size per arm:

```text
{paste_verbatim_rendered_prompt_sizes_per_arm}
```

**Check 2 — any required action actually happened.** Delete if no arm required the
agent to run, query, or call anything:

- Treatment requiring an action: {treatment_requiring_action_or_none}
- How its use was recorded: {usage_record_mechanism}
- Invocations observed: {invocation_count} across {case_count} cases
- Operations used: {operations_used}
- Failed or refused attempts: {failed_attempt_count}

**Check 3 — the treated arm behaved differently at all.** A behavioural measure
compared against control, independent of whether the treatment helped:

| Arm | {behavioural_measure} | Outcome measure |
|---|---|---|
| {control_arm} | {control_behaviour} | {control_outcome} |
| {treatment_arm} | {treatment_behaviour} | {treatment_outcome} |

Interpretation: {behavioural_difference_interpretation}

Checks that failed, and what was changed: {failed_checks_and_corrections_or_none}

When the checks were run, relative to the calls: {checks_timing_before_or_after_calls}

## Evidence

<!-- GUIDANCE: Paste real command output verbatim in fenced code blocks. Never paraphrase, retype, round numbers, or reconstruct from memory. If you did not capture the output, re-run the command and paste the new output. Include the exact command used. -->

Command:

```bash
atom poc run {poc-slug}
```

Output:

```text
{paste_verbatim_atom_poc_run_output_here}
```

Additional command, if used:

```bash
{additional_command_or_remove_this_block}
```

```text
{paste_verbatim_additional_output_or_remove_this_block}
```

Run context:

- Date/time run: {run_datetime}
- Commit or working tree note: {commit_or_working_tree_note}
- Go version: `{go_version_output}`
- Relevant input size/rate: {input_size_or_rate}
- Number of runs: {run_count}

Result summary from the pasted output only:

- Confirming observation: {confirming_observation_or_none}
- Refuting observation: {refuting_observation_or_none}
- Inconclusive gap: {inconclusive_gap_or_none}

## What The Spike Did

<!-- GUIDANCE: Briefly describe what the disposable Go program did and point to the code path. Good answers distinguish what was simulated from what was real. Bad answers imply the spike is production code. -->

The spike at `{spike_path}` {brief_spike_description}.

- Real inputs or dependencies: {real_inputs}
- Simulated inputs or dependencies: {simulated_inputs}
- Main measurements printed: {measurements}

## What We Learned

<!-- GUIDANCE: Capture non-obvious findings, especially surprises. Surprises are the highest-value content because they update the design. Do not restate the success criteria unless the result changed your understanding. -->

- {learning_1}
- {learning_2}
- {surprise_or_none}
- Expected but not observed: {expected_but_not_observed_or_none}
- Observed but not expected: {observed_but_not_expected_or_none}
- New risk exposed: {new_risk_or_none}

## What This Changes

<!-- GUIDANCE: Connect evidence to design consequences. Replace the example row. If nothing changes, say which assumption was strengthened and why. -->

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| _example — replace_ one goroutine can drain all work | Refuted | The design needs bounded worker parallelism instead of a single drain loop. |
| {assumption_1} | {Confirmed-or-Refuted-or-Inconclusive} | {design_consequence_1} |
| {assumption_2} | {Confirmed-or-Refuted-or-Inconclusive} | {design_consequence_2} |

## Explicitly Not Covered

<!-- GUIDANCE: State the boundary out loud. Proving a happy path at 1k req/s says nothing about error paths at 100k req/s. Future readers must be able to tell exactly what this report does not prove. -->

- {boundary_1}
- {boundary_2}
- {boundary_3}

## Recommendation

<!-- GUIDANCE: Choose one: proceed to spec, respike with a sharper question, or return to discovery. The recommendation must follow from the verdict and evidence, not optimism. -->

{proceed-to-spec-or-respike-or-return-to-discovery}: {recommendation_reason}

Next artifact: {next_artifact_path_or_none}

Conditions before continuing:

- {condition_before_continuing_1}
- {condition_before_continuing_2}

## Completeness Checklist

<!-- GUIDANCE: Check every item before the gate. If evidence is missing, re-run the POC before filling the checklist. -->

- [ ] The question is copied verbatim from the brief.
- [ ] Verdict is exactly Confirmed, Refuted, or Inconclusive.
- [ ] Verbatim `atom poc run {poc-slug}` output is pasted in a fenced block.
- [ ] Spike path is recorded.
- [ ] Surprises and non-obvious findings are captured.
- [ ] Design consequences are tied to observed evidence.
- [ ] Boundaries are explicit enough to prevent over-reading.
- [ ] Recommendation follows from the verdict.
- [ ] Run context is recorded.
- [ ] Any inconclusive gap is named directly.
- [ ] The report does not claim evidence outside the pasted output.
- [ ] Comparison spikes only: all three treatment-evidence checks passed before results were read, and no arm's use of a treatment is asserted on the agent's own say-so.
