---
project: "module-review-rules"
phase: "n/a"
author: "Copilot"
date: "2026-10-30"
status: "approved"
---

# POC Brief: module-local rules reach reviewers

## Problem

Atom already sends seven shared Go review rules to every reviewer. Atom init additionally installs a module-local instruction bundle, but atom review does not consume that bundle or its local customizations. Copying guidance into a module is not the same as delivering it to a reviewer.

- Developer-visible outcome: reviewers receive the launching module's applicable local review guidance by default, rather than only package-level rules.
- Current limitation: the module-local Go guide and project review contracts do not automatically enter the review prompt.
- Non-negotiable constraints: preserve the seven shared rules, strict findings validation, attribution, current tool policy, and --no-custom-instructions. Do not solve this by importing every workflow instruction.
- Known evidence: existing explicit fixed-evidence capture freezes caller documents before PR preparation; the native pipeline already sends one common prompt to its requested reviewers. The developer selected the local launching checkout, including local edits, rather than PR-supplied policy.

## The Question

Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?

## Why This Is The Riskiest Unknown

The selected risk is integration: adding module guidance must not silently lose that guidance, switch to a different checkout's policy, or break the existing response contract. The copied Go guide is broader than the curated seven-rule block, so mere file existence is not evidence that the combined prompt remains useful.

- Feasibility: the existing shared-prompt and explicit-capture mechanisms provide a starting point, not proof of the new composition.
- Performance: record prompt size and elapsed time; this trial does not establish a size or latency budget.
- Integration: prove delivery and one rule-grounded result through the real invocation/extraction path before a production design.
- Ergonomics: filenames, configuration switches, and generalized instruction discovery can wait for evidence.
- Alternative risks not chosen: portable toolchain selection and degraded review on tooling incompatibility are separate requested changes. They are not bundled into this proof.

## Success Criteria

| Observation | Interpretation |
|---|---|
| Every actual review request contains the complete frozen local guide and its controlled project-specific addition | Delivery established for this fixture |
| Changing the local source after capture and placing a conflicting guide in the review checkout do not alter the explicit review packet | Launch-source snapshot established |
| Both native review commands retain --no-custom-instructions and the existing model/tool options | Existing invocation policy preserved |
| Both responses pass the existing ownership-aware extraction and findings schema and name the predeclared synthetic defect | Narrow integration question Confirmed |
| A review packet omits or changes the captured guidance, or a completed response fails the required integration observations | Refuted for this trial; do not silently tune and rerun |
| A requested model is unavailable, times out, or cannot complete transport | Inconclusive; report it without substitution or retry |

Minimum acceptable evidence:

- Two review calls: one run per model from Atom's existing default reviewer pair, resolved at execution. Up to two existing availability probes; no subagents.
- One small synthetic Go diff and one customized copy of the initialized module's Go-style guide. Declare the expected finding and line before model calls.
- Audit the actual logical prompt supplied to the native runner for each review, not the model's claim that it read a rule. Record rule and prompt hashes, UTF-8 counts, resolved model identities, argv policy, outcomes, findings, and elapsed time.
- Hashes identify logical pre-transport UTF-8. Do not claim exact child-stdin byte identity on Windows, where existing transport can normalize line endings.
- Use existing review deadlines without extending them; there are no automatic retries or new latency targets.

## Scope

### Will Do

- Use an owned synthetic local Go fixture, a temporary review checkout, and a Go guide copied from Atom's installed module bundle with one controlled local review contract added.
- Snapshot the launching fixture's guidance, then mutate its source and create a conflicting review-checkout copy to expose wrong-source loading.
- Add the captured guidance at a throwaway prompt-composition seam and use the real Atom invocation and extraction functions. Record that this is a prototype seam, not a shipped default loader.
- Preserve the existing shared rules, strict JSON response contract, and invocation flags; retain evidence for every requested call.

### Will Not Do

- Modify production code, installed packages, machine configuration, or any real module's instruction files.
- Send real project code or rules to models, access Azure DevOps, or run a live PR review.
- Import the complete Atom workflow bundle or select a general policy for following Markdown links and GitHub instruction files.
- Claim automatic production discovery, comprehensive rule compliance, improved review quality, cross-platform compatibility, or superiority of a longer checklist from two calls.
- Change required-gate behavior, classify tooling failures, or implement project toolchain selection.

## Approach Sketch

- Keep a small disposable Python harness at poc/module-review-rules/spike.py, with a synthetic Go fixture. The uncertain path is Atom's actual Python-to-Copilot transport, not a new Go API.
- Capture the local guide once, compose it with the unchanged shared rules and synthetic diff, and audit the prompt received by the actual command runner for every review call.
- Exercise the native invocation/extraction path; do not replace model output with canned findings or change the parser.
- Run from tools with python ..\poc\module-review-rules\spike.py.
- Stop after the predeclared two reviews or any condition that prevents the stated experiment. Capture verbatim output and return a bounded verdict, not a redesigned experiment.

Disposable shortcuts: synthetic source, temporary Git directories, a controlled extra review rule, and a temporary composition seam confined to the harness process. These do not constitute a production loader.

Invalid shortcuts: dropping a requested model from the denominator, editing the expected defect after seeing responses, disabling strict extraction, removing --no-custom-instructions, silently truncating guidance, or treating a model's self-report as delivery evidence.

## Open Questions For The Developer

The experiment does not decide the final supported rule-file formats or reconciliation of the full module-local guide with the curated shared seven. Those remain explicit design decisions after the result. Approval requested here is only for the bounded synthetic trial and its stated model-call cost.

## Completeness Checklist

- [x] One falsifiable integration question and explicit alternatives.
- [x] Observable pass/fail/inconclusive criteria and fixed call count.
- [x] Synthetic-only inputs, named spike path, and explicit exclusions.
- [x] Actual native delivery and extraction evidence, not source-file presence or model self-report.
- [x] No production design or implementation approval is assumed.
- [x] Python harness with Go fixture is an explicit repository-tooling adaptation requiring approval with this brief.

## Proposed controlled retry after the first Inconclusive trial

Explicitly approved by the developer on 2026-10-30, separately from local diagnosis. The first trial spent two availability probes and zero review calls; both probes timed out. Separately approved local diagnosis found custom MCP server startup still occurs under tool exclusions, while non-model native version execution succeeds.

Repeat the same question and all original success criteria with one explicit startup-condition change: use the existing caller-selected disable_mcp_servers parameter for the locally configured azure-devops and azure-mcp servers. Keep --no-custom-instructions, fixed-evidence source exclusions, the shared seven, the entire frozen guide, expected fixture finding/lines, default pair, and 60/600-second deadlines unchanged. This tests that named-server-isolated condition, not ordinary tool-enabled reviews.

Maximum additional calls: two existing availability probes plus two reviews, one per requested default model, with no automatic retries or substitutions. No agents, real project content, live PR access, production edits, or machine configuration changes. Preserve the original trial and both source hashes separately. If startup still prevents review, return Inconclusive without further attempts. A successful trial may support only the original narrow delivery/extraction question, not a general MCP diagnosis or quality improvement.

## Next revision: developer-selected reviewer, no new calls approved

The developer selected Claude Sonnet 5 (claude-sonnet-5) to replace the unavailable gpt-5.4 in a revised brief. Gemini remains the other requested reviewer. This is an explicit experiment selection, not a production-default change or silent fallback.

This selection does not authorize another model batch. The previous trials and their frozen attribution expectations remain unchanged and Inconclusive. Before another trial, present the revised brief with the selected pair, explicit treatment of the line-9 attribution observation, and a bounded call budget. No attribution waiver or new success criterion has been approved.
