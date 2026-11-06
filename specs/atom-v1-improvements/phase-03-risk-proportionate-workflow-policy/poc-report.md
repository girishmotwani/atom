---
project: "atom-v1-improvements"
phase: "phase-03-risk-proportionate-workflow-policy"
poc_slug: "atom-v1-risk-proportionate-policy"
verdict: "Confirmed"
date: "2026-11-04"
spike_path: "poc/atom-v1-risk-proportionate-policy"
---

# POC Report

## The Question

With the same risk/evidence rubric and four fixed cases, will two independent models recommend the same justified next workflow step in every case, cite only supplied evidence, and leave the final choice with the developer without suggesting an unapproved gate bypass?

## Verdict

**Confirmed, narrowly.** Both available models returned valid answers for all four cases, chose the same route in every pair, cited case facts, emitted `developer_decides: true`, and suggested no gate bypass. The prompt supplied the route labels and definitions, so this confirms consistent application of that supplied rubric only; it does not validate the rubric itself or show independent discovery of risk factors. No developer was simulated; this confirms response wording only, not actual pause/accept/reject behavior.

## Evidence of Treatment

Arms compared: `gpt-5.3-codex` and `claude-opus-5.5`.

**Check 1 — the treatment reached the model.** The rubric and case were rendered once and the identical prompt string passed to both model calls for that case. The harness emitted the rendered prompt and its UTF-8 byte length and SHA-256 before any calls:

```text
prompt=case-01-risky-new-behavior bytes=1304 sha256=f1e48d7c025c4a7b1f347536950bf2a6a6255f63d3c3de7905e658b14deccf41
prompt=case-02-reproducible-understood-regression bytes=1360 sha256=97cfaf6cfa300d8badeef3313b2490ed03a1ebe7f7a2edfa98db2b05f375c876
prompt=case-03-previously-proven-wiring bytes=1344 sha256=43cacb18386af45ca326d4e50e45e9c6ea1ab1c23863308905b67bbd2c539a63
prompt=case-04-documentation-only bytes=1219 sha256=fae2aef36808a6bcd9e93b78cc343914b4ee4d5b1a21d41b448678124e980eef
```

The full rendered prompt text is included in the verbatim output below. Model-side custom instructions, built-in MCPs, and other tools were disabled for every probe and case call.

**Check 2 — any required action actually happened.** The experiment required direct Copilot CLI model calls only; each invocation, status and stdout was recorded by the Go harness. Successful-call stderr was discarded by the original implementation; the ten printed empty stderr blocks do not establish empty streams. Their historical contents are unknown. No model was asked to use an additional script, index, API, or MCP tool.

- Treatment requiring an action: None beyond the recorded Copilot CLI call.
- Invocations observed: 10 (2 availability probes and 8 case responses).
- Operations used: 2 probes; 4 cases x 2 models.
- Failed or refused attempts: 0. No retries or alternate model were needed.

**Check 3 — the models behaved consistently across the cases.** This experiment compares model routing, not treatment-caused quality improvement. The independently observed route label was the behavioral measure:

| Case | `gpt-5.3-codex` | `claude-opus-5.5` | Pair result |
|---|---|---|---|
| Risky new behavior | `POC_FIRST` | `POC_FIRST` | Match |
| Reproducible understood regression | `REGRESSION_TEST_FIRST` | `REGRESSION_TEST_FIRST` | Match |
| Previously proven wiring | `REUSE_EVIDENCE_AND_VALIDATE` | `REUSE_EVIDENCE_AND_VALIDATE` | Match |
| Documentation only | `DOCUMENTATION_REVIEW` | `DOCUMENTATION_REVIEW` | Match |

Both models returned `developer_decides: true` and `gate_bypass_suggested: false` for all eight answers. Because the prompt required those values, they are evidence only that the models followed the requested response format. No developer was simulated, and the experiment did not test whether an actual workflow pauses for approval or honors rejection. Manual review found their evidence arrays drawn from the corresponding case facts. Claude's regression answer raises a possible residual risk for other empty-value inputs; it is framed as a possibility, not as an observed fact, and does not change the route. No treatment-evidence check failed.

Checks were run before reading the responses: the prompts were rendered and hashed before the first probe; invocation logging and call counting were active during every call.

## Evidence

Command:

```text
atom poc run atom-v1-risk-proportionate-policy
```

Output (verbatim; original harness output, including misleading empty stderr labels):

```text
atom poc run atom-v1-risk-proportionate-policy  (command spike)

  PASS  vet     ok
  PASS  build   ok
  PASS  execute ok

  stdout:
    Question: With the same risk/evidence rubric and four fixed cases, will two independent models recommend the same justified next workflow step in every case, cite only supplied evidence, and leave the final choice with the developer without suggesting an unapproved gate bypass?
    
    Rendered case prompts (the exact prompt string is reused for every model):
    prompt=case-01-risky-new-behavior bytes=1304 sha256=f1e48d7c025c4a7b1f347536950bf2a6a6255f63d3c3de7905e658b14deccf41
    ----- prompt begin: case-01-risky-new-behavior -----
    Recommend exactly one next workflow step for the case below. The developer makes the decision; your recommendation does not approve or perform work. Never suggest silently bypassing an applicable gate.
    
    Use these routes exactly:
    - POC_FIRST: material technical uncertainty remains; prove the risky behavior before design.
    - REGRESSION_TEST_FIRST: a defect and its cause are already reproducible and understood; start with a failing regression test and implement under TDD. Add a separate POC only if a material unknown remains.
    - REUSE_EVIDENCE_AND_VALIDATE: an approved POC/spec still covers the unchanged risk; state its limits and validate the affected contract.
    - DOCUMENTATION_REVIEW: documentation-only change with no behavior/API change; review the text and relevant documentation checks without inventing a Go experiment.
    
    Return only one JSON object with fields: route, evidence (array of exact case facts), uncertainty, rationale, developer_decides (boolean, must be true), gate_bypass_suggested (boolean, must be false).
    
    Case case-01-risky-new-behavior:
    A team proposes a new project-level Go toolchain selector. No code or experiment exists. It is not yet known how it interacts with workspace files and module version requirements; selecting the wrong compiler could change build behavior.
    
    ----- prompt end: case-01-risky-new-behavior -----
    prompt=case-02-reproducible-understood-regression bytes=1360 sha256=97cfaf6cfa300d8badeef3313b2490ed03a1ebe7f7a2edfa98db2b05f375c876
    ----- prompt begin: case-02-reproducible-understood-regression -----
    Recommend exactly one next workflow step for the case below. The developer makes the decision; your recommendation does not approve or perform work. Never suggest silently bypassing an applicable gate.
    
    Use these routes exactly:
    - POC_FIRST: material technical uncertainty remains; prove the risky behavior before design.
    - REGRESSION_TEST_FIRST: a defect and its cause are already reproducible and understood; start with a failing regression test and implement under TDD. Add a separate POC only if a material unknown remains.
    - REUSE_EVIDENCE_AND_VALIDATE: an approved POC/spec still covers the unchanged risk; state its limits and validate the affected contract.
    - DOCUMENTATION_REVIEW: documentation-only change with no behavior/API change; review the text and relevant documentation checks without inventing a Go experiment.
    
    Return only one JSON object with fields: route, evidence (array of exact case facts), uncertainty, rationale, developer_decides (boolean, must be true), gate_bypass_suggested (boolean, must be false).
    
    Case case-02-reproducible-understood-regression:
    A CLI command now rejects an input that previously worked. The failure reproduces every time, the root cause is isolated to empty-value normalization, and a failing regression test captures it. The proposed minimal fix is understood; no dependency or external behavior changes.
    
    ----- prompt end: case-02-reproducible-understood-regression -----
    prompt=case-03-previously-proven-wiring bytes=1344 sha256=43cacb18386af45ca326d4e50e45e9c6ea1ab1c23863308905b67bbd2c539a63
    ----- prompt begin: case-03-previously-proven-wiring -----
    Recommend exactly one next workflow step for the case below. The developer makes the decision; your recommendation does not approve or perform work. Never suggest silently bypassing an applicable gate.
    
    Use these routes exactly:
    - POC_FIRST: material technical uncertainty remains; prove the risky behavior before design.
    - REGRESSION_TEST_FIRST: a defect and its cause are already reproducible and understood; start with a failing regression test and implement under TDD. Add a separate POC only if a material unknown remains.
    - REUSE_EVIDENCE_AND_VALIDATE: an approved POC/spec still covers the unchanged risk; state its limits and validate the affected contract.
    - DOCUMENTATION_REVIEW: documentation-only change with no behavior/API change; review the text and relevant documentation checks without inventing a Go experiment.
    
    Return only one JSON object with fields: route, evidence (array of exact case facts), uncertainty, rationale, developer_decides (boolean, must be true), gate_bypass_suggested (boolean, must be false).
    
    Case case-03-previously-proven-wiring:
    An approved POC and spec already establish a helper's behavior and error handling. The task only connects an existing command to that helper with the same arguments; no assumptions or public behavior change. The affected caller can receive focused integration validation.
    
    ----- prompt end: case-03-previously-proven-wiring -----
    prompt=case-04-documentation-only bytes=1219 sha256=fae2aef36808a6bcd9e93b78cc343914b4ee4d5b1a21d41b448678124e980eef
    ----- prompt begin: case-04-documentation-only -----
    Recommend exactly one next workflow step for the case below. The developer makes the decision; your recommendation does not approve or perform work. Never suggest silently bypassing an applicable gate.
    
    Use these routes exactly:
    - POC_FIRST: material technical uncertainty remains; prove the risky behavior before design.
    - REGRESSION_TEST_FIRST: a defect and its cause are already reproducible and understood; start with a failing regression test and implement under TDD. Add a separate POC only if a material unknown remains.
    - REUSE_EVIDENCE_AND_VALIDATE: an approved POC/spec still covers the unchanged risk; state its limits and validate the affected contract.
    - DOCUMENTATION_REVIEW: documentation-only change with no behavior/API change; review the text and relevant documentation checks without inventing a Go experiment.
    
    Return only one JSON object with fields: route, evidence (array of exact case facts), uncertainty, rationale, developer_decides (boolean, must be true), gate_bypass_suggested (boolean, must be false).
    
    Case case-04-documentation-only:
    Correct a typo and refresh a command example whose current output has already been verified. No code, API, configuration, or supported behavior changes.
    
    ----- prompt end: case-04-documentation-only -----
    
    call=1 kind=availability-probe model=gpt-5.3-codex case=probe status="ok"
    stdout (verbatim):
    READY
    
    
    stderr (verbatim):
    
    
    call=2 kind=availability-probe model=claude-opus-5.5 case=probe status="ok"
    stdout (verbatim):
    READY
    
    
    stderr (verbatim):
    
    
    call=3 kind=case-attempt-1 model=gpt-5.3-codex case=case-01-risky-new-behavior status="ok"
    stdout (verbatim):
    {"route":"POC_FIRST","evidence":["A team proposes a new project-level Go toolchain selector.","No code or experiment exists.","It is not yet known how it interacts with workspace files and module version requirements.","Selecting the wrong compiler could change build behavior."],"uncertainty":"Material technical uncertainty remains about toolchain-selection behavior across workspace files and module version constraints, and its impact on build outcomes.","rationale":"Because the behavior is new and risk-bearing with unknown interactions and no prior experiment, the next step should be to prove the risky behavior via a focused POC before design or implementation decisions.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=4 kind=case-attempt-1 model=claude-opus-5.5 case=case-01-risky-new-behavior status="ok"
    stdout (verbatim):
    {"route":"POC_FIRST","evidence":["A team proposes a new project-level Go toolchain selector.","No code or experiment exists.","It is not yet known how it interacts with workspace files and module version requirements","selecting the wrong compiler could change build behavior."],"uncertainty":"Material and unresolved: we do not know how a project-level selector interacts with workspace files and module version requirements, or when the wrong compiler would be chosen.","rationale":"This is new behavior, not a reproducible defect, so REGRESSION_TEST_FIRST does not apply. No POC or spec exists to reuse, and the change is not documentation-only. A wrong compiler choice could change build behavior, so a focused POC should first prove how selection resolves across workspace and module version scenarios. Design and spec gates follow from that evidence and are not bypassed.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=5 kind=case-attempt-1 model=gpt-5.3-codex case=case-02-reproducible-understood-regression status="ok"
    stdout (verbatim):
    {"route":"REGRESSION_TEST_FIRST","evidence":["A CLI command now rejects an input that previously worked.","The failure reproduces every time.","The root cause is isolated to empty-value normalization.","A failing regression test captures it.","The proposed minimal fix is understood.","No dependency or external behavior changes."],"uncertainty":"No material technical uncertainty remains beyond implementing the known minimal fix against the existing failing regression test.","rationale":"Because the defect is reproducible, cause is already understood, and a failing regression test already exists, the next step is to proceed with regression-test-first TDD: keep the failing test as the guard, implement the minimal fix, and verify the contract without adding a separate POC.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=6 kind=case-attempt-1 model=claude-opus-5.5 case=case-02-reproducible-understood-regression status="ok"
    stdout (verbatim):
    {"route":"REGRESSION_TEST_FIRST","evidence":["A CLI command now rejects an input that previously worked.","The failure reproduces every time","the root cause is isolated to empty-value normalization","a failing regression test captures it","The proposed minimal fix is understood","no dependency or external behavior changes"],"uncertainty":"Low. The defect reproduces every time, its root cause is isolated, and the minimal fix is understood. No material unknown justifies a separate POC. The remaining residual risk is that the normalization fix could affect other empty-value inputs. The TDD cycle and the existing tests should cover that risk.","rationale":"The defect is reproducible and understood, and a failing regression test already captures it. This matches REGRESSION_TEST_FIRST: start from the failing test and implement the minimal fix under TDD. Then confirm that the existing suite still passes. A POC would add no information, because no dependency or external behavior changes are involved. No prior POC or spec is cited for reuse, and the change is not documentation-only. All applicable review and test gates still apply.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=7 kind=case-attempt-1 model=gpt-5.3-codex case=case-03-previously-proven-wiring status="ok"
    stdout (verbatim):
    {"route":"REUSE_EVIDENCE_AND_VALIDATE","evidence":["An approved POC and spec already establish a helper's behavior and error handling.","The task only connects an existing command to that helper with the same arguments.","No assumptions or public behavior change.","The affected caller can receive focused integration validation."],"uncertainty":"No material technical uncertainty is stated; remaining risk is limited to correct wiring at the caller boundary.","rationale":"Because prior approved evidence already covers the unchanged behavior and error path, the next step is to reuse that evidence, explicitly note it only applies while arguments/semantics remain identical, and validate the affected integration contract at the caller.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=8 kind=case-attempt-1 model=claude-opus-5.5 case=case-03-previously-proven-wiring status="ok"
    stdout (verbatim):
    {"route":"REUSE_EVIDENCE_AND_VALIDATE","evidence":["An approved POC and spec already establish a helper's behavior and error handling.","The task only connects an existing command to that helper with the same arguments.","No assumptions or public behavior change.","The affected caller can receive focused integration validation."],"uncertainty":"Low. The approved POC/spec covers the helper's behavior and error handling, but not this specific command-to-helper wiring. Validation still needs to confirm that the caller passes the same arguments and propagates the helper's errors as the spec describes.","rationale":"The risky behavior is already proven and approved, and its risk is unchanged. A new POC would add no information. The case describes no defect, so a regression test is not the starting point. This is a code change, so documentation review does not apply. The right step is to reuse the existing POC/spec evidence, note that it does not cover the new caller wiring, and run focused integration validation on the affected command contract without skipping any applicable gate.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=9 kind=case-attempt-1 model=gpt-5.3-codex case=case-04-documentation-only status="ok"
    stdout (verbatim):
    {"route":"DOCUMENTATION_REVIEW","evidence":["Correct a typo","refresh a command example whose current output has already been verified","No code, API, configuration, or supported behavior changes"],"uncertainty":"No material technical uncertainty remains because the change is documentation-only and the example output is already verified.","rationale":"This is a docs-only update with no behavior or contract change, so the next step is to review/edit the documentation text and run any relevant documentation checks rather than doing POC or regression-test-first work.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    
    call=10 kind=case-attempt-1 model=claude-opus-5.5 case=case-04-documentation-only status="ok"
    stdout (verbatim):
    {"route":"DOCUMENTATION_REVIEW","evidence":["Correct a typo and refresh a command example whose current output has already been verified.","No code, API, configuration, or supported behavior changes."],"uncertainty":"Low. The command output has already been verified, so the remaining risk is mainly wording accuracy and any applicable documentation checks.","rationale":"This is a documentation-only change with no behavior, API, or configuration impact, so a POC, regression test, or Go experiment would not add useful evidence. Review the corrected text and refreshed example, then run any relevant documentation checks.","developer_decides":true,"gate_bypass_suggested":false}
    
    
    stderr (verbatim):
    
    comparison=case-01-risky-new-behavior left_model=gpt-5.3-codex left_route=POC_FIRST right_model=claude-opus-5.5 right_route=POC_FIRST
    comparison=case-02-reproducible-understood-regression left_model=gpt-5.3-codex left_route=REGRESSION_TEST_FIRST right_model=claude-opus-5.5 right_route=REGRESSION_TEST_FIRST
    comparison=case-03-previously-proven-wiring left_model=gpt-5.3-codex left_route=REUSE_EVIDENCE_AND_VALIDATE right_model=claude-opus-5.5 right_route=REUSE_EVIDENCE_AND_VALIDATE
    comparison=case-04-documentation-only left_model=gpt-5.3-codex left_route=DOCUMENTATION_REVIEW right_model=claude-opus-5.5 right_route=DOCUMENTATION_REVIEW
    model_calls=10 hard_limit=48
    Machine verdict: candidate CONFIRMED; manually verify that every cited fact appears in its case and that each rationale is justified.

  Verdict: CONFIRMED  (exit 0) -- the question was answered yes
```

## Run Context

- Date/time run: 2026-11-04 (local environment date).
- Worktree: `feat/atom-v1-review-continuation`, with the roadmap and these artifacts untracked before this experiment.
- Go version: `go version go1.26.9 windows/amd64`.
- Relevant input size: Four independently rendered prompts of 1,304; 1,360; 1,344; and 1,219 bytes.
- Number of calls: 10 total (2 probes + 8 case calls); no retries or alternate-model calls; below the 48-call hard cap.

## What The Spike Did

The throwaway Go command rendered four fixed cases and used `copilot` with custom instructions and model-side tools disabled. It probed each proposed model once, made one call per model per case, captured raw responses, checked the response schema and route labels, and printed the paired comparison. The rationales and evidence were manually checked against the case text.

- Real inputs or dependencies: Copilot CLI 1.0.106-8; `gpt-5.3-codex`; `claude-opus-5.5`; four fixed case prompts.
- Simulated inputs or dependencies: Task descriptions are constructed examples, not observations from live Atom users or production tasks.
- Main measurements printed: Prompt byte length and hash, each model/case response, route agreement, gate-control fields, and total call count.

## What We Learned

- The two models gave matching route labels across all four cases and stated that the developer decides; no actual developer interaction was simulated.
- They distinguished uncertain new behavior, known reproducible defects, evidence-reusing wiring, and documentation-only work as intended by the supplied rubric.
- One answer surfaced a plausible residual concern about other empty-value inputs; this is a useful reasoning caveat, not evidence that such a defect exists.
- No model suggested skipping the applicable gates.
- Expected but not observed: model disagreement, unsupported concrete facts, malformed response JSON, failed probes, retries, or fallback use.
- Observed but not expected: both models explicitly explained why competing routes did not apply in several cases.
- New risk exposed: four synthetic cases and one run per model cannot establish universal policy quality or stability across model versions and task phrasing.

## What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| A bounded rubric can route the four representative cases consistently without handing the decision to the model | Confirmed | The examples support drafting a Phase 03 policy proposal that states developer choice and preserves the evidence boundaries; actual human-control behavior remains unproven. |
| Four cases establish a complete or universally correct policy | Not tested | No universal claim; developer review, edge cases, and explicit policy approval remain required before guidance changes. |

## Explicitly Not Covered

- Whether the supplied route labels and definitions are the right risk/evidence factors, whether they cover all task types, or whether the developer prefers them.
- Model stability across repeated runs, model versions, wording changes, or other accounts.
- Whether an actual workflow pauses for developer approval, honors acceptance/rejection, or prevents later actions after rejection.
- Any production implementation, new shortcut, or policy approval; none was performed by this POC.

## Recommendation

Proceed to a Phase 03 policy-spec gate: use these examples to draft the proposed routing rules, then obtain explicit developer approval before changing canonical or packaged guidance.

Next artifact: `specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/design-spec.md`

Conditions before continuing:

- The developer approves this POC report and authorizes drafting the design spec.
- Any policy change remains subject to a separate explicit approval gate.

## Completeness Checklist

- [x] The question is copied verbatim from the brief.
- [x] Verdict is exactly Confirmed, Refuted, or Inconclusive.
- [x] Verbatim `atom poc run atom-v1-risk-proportionate-policy` output is pasted in a fenced block.
- [x] Spike path is recorded.
- [x] Surprises and non-obvious findings are captured.
- [x] Design consequences are tied to observed evidence.
- [x] Boundaries are explicit enough to prevent over-reading.
- [x] Recommendation follows from the verdict.
- [x] Run context is recorded.
- [x] Any inconclusive gap is named directly.
- [x] The report does not claim evidence outside the pasted output.
- [x] Comparison-spike prompt delivery and use were recorded before results were assessed.

## Evidence Record Corrections And Rerun Limits

The completed shell 418 output was recovered without new model calls. Restored the complete call-7 JSON, the printed empty stderr placeholders for calls 4-6, and the original capitalization in call 6; none changes the observed answers or verdict. Approval concerned the narrowly confirmed sample and guidance-only spec, not a new experiment.

The original harness printed candidate outcomes but always exited zero. Therefore the historical automatic `CONFIRMED (exit 0)` line alone cannot grade this experiment; the observed sample required manual response/rationale review. Its successful-call stderr was not captured: all ten printed empty stderr blocks are historical placeholders, with the actual streams unknown. No output has been reconstructed or substituted.

Post-review deterministic repairs now return nonzero for Refuted/Inconclusive, require exact READY probes and explicit boolean fields, and capture stderr on success/failure. The original transcript above predates these repairs and is deliberately unchanged. No live model rerun occurred. Timeout termination of Windows descendants remains unvalidated; no timeout occurred in the original experiment. Re-gate the instrument and lifecycle boundary before any future paid experiment. See [the test spec](test-spec.md) for repair evidence, not a new policy experiment.
