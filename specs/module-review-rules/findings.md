# Module review rules: findings

## Current behavior

- Every reviewer already receives the seven shared Go rules from tools/atom/style.py. The new work is not to add those seven for the first time.
- Atom init copies a module-local workflow/style bundle and points local Copilot instructions to it. It does not infer bespoke domain rules from module source.
- Atom review does not consume module-local guidance or its customizations. It disables ambient custom instructions and builds one explicit prompt.
- The current explicit fixed-evidence loader captures caller documents before PR preparation, but calls those documents evidence data rather than executable instructions.

## Requirements clarified

The developer selected rules from the local launching checkout, including local edits, not the pinned PR checkout. The expectation is that initialized module-local guidance matters to review by default. A narrower AGENTS-only interpretation was premature; rule formats have not been approved.

## Risks and proof bounds

The module-local bundle mixes workflow orchestration with Go guidance, so blindly loading it all can change the review task. Its Go guide is also broader than the curated seven-rule prompt; adding more text must not be presented as a proven quality improvement. The proposed synthetic POC proves delivery and one narrow integration case, not a complete loader or a general quality result.

## Verification

Command from tools: python -m pytest tests -v --cov=atom --cov-report=term-missing. Verbatim source/test-baseline excerpt:

```text
TOTAL                        4107    218    95%
================= 1465 passed, 2 skipped in 185.92s (0:03:05) =================
```

Tracked source, tests, and packaged assets remain unchanged. The documentation checker previously reported all 297 relative links resolve. The approved trial has now run; its availability probes timed out before either review could start. See the POC result below.

## Separate requirements

Project-scoped reproducible toolchains and degraded review on confirmed tooling incompatibility remain additional requested work. The verified user-wide Go setting is only a local workaround, not a portable product fix.

## Approved POC result: Inconclusive

Both existing native availability probes timed out at the unchanged 60-second deadline. Counts: two probes, zero review calls, zero retries or substitutions. Both probe stdout captures are empty; stderr contains only "Command timed out after 60 seconds." The cause is not established, so this is not evidence that the models are unsupported or that module guidance broke review.

The synthetic Go fixture build/vet and local-guide snapshot succeeded, but no actual review prompt or model finding exists to validate delivery or strict extraction. Source mutation/conflicting-policy checks remain setup, not end-to-end proof. The full output and boundary are in [poc-report.md](poc-report.md).

Stop before production design. Local startup/probe investigation is the proposed next beat, not an automatically authorized additional model batch. Production code, tests, assets, installed components, real modules, and machine defaults remain unchanged.

## Approved local diagnosis: startup isolation remains unproven

No additional model calls were made. Both normal PowerShell and Atom's native runner report Copilot CLI 1.0.105; the native --version command completes successfully. The original probes' local logs show configured custom MCP servers initializing despite the fixed-evidence tool exclusions. Local help distinguishes tools unavailable to the model from disabling MCP server startup.

This explains why source exclusions alone do not isolate startup, but it does not establish that MCP caused the timeouts. Proposed next step is a separately approved bounded repeat using the existing caller-selected server exclusions, with unchanged models, inputs, extraction, and deadlines. Do not retry under the local-only diagnostic approval.

## Separately approved controlled retry: Inconclusive

Both probes completed with the existing caller-selected custom-server exclusions. gpt-5.4 exited 1 with: Error: Model "gpt-5.4" from --model flag is not available. Gemini's probe passed, then one native review completed. No model was substituted and no additional attempt was made.

The full frozen guide reached Gemini: logical prompt audit and normalized root user event matched; strict extraction returned the known reservation-leak message with no extraction failure. Gemini named line 9, outside the predeclared line 10/11 expectation. Do not silently widen that criterion or equate semantic recognition with passing attribution.

The requested two-model question remains Inconclusive. Total approved spend across the two trials was four probes and one review. The second reviewer must be explicitly selected and the brief revised before further calls. Default model-selection policy is not silently changed as part of module-rule delivery. Full evidence is in [poc-report.md](poc-report.md).

## Narrow feasibility accepted; moving to design preparation

The developer accepted the one-model delivery evidence as sufficient for the narrow transport milestone while retaining both Inconclusive trial verdicts. Additional calls solely to satisfy the original second-model/exact-location conditions are not required for this milestone. Correct automatic discovery and uniform per-reviewer delivery still need specified behavior and implementation tests.

The remaining intent gap is source selection: the initialized Go guide, module AGENTS.md/domain guidance, and GitHub instruction pointers are distinct inputs. No general discovery policy has been approved. Complete that decision before claiming the default product behavior addresses module-specific rules.

## Design-source decision and compatibility boundary

The developer chose both the initialized Go guide and module-root AGENTS.md. The draft design freezes those supported sources before preparation, leaves linked/ancestor/GitHub discovery out, and keeps normal-mode source selection distinct from the existing fixed-evidence explicit packet.

Existing report.py currently says initialized rules are not applied, including PR reports; implementation must replace that blanket claim only where a snapshot was actually loaded. ContextDocument already supports exact UTF-8 capture and metadata validation and should be reused rather than duplicated. Existing Go checks and PR selection expect a launch-module root; broader root inference is not part of this bounded change.

The full AGENTS.md composition, semantic precedence, ordinary-mode effects, and review quality remain unproven assumptions even though guide transport to one reviewer was observed. The design specifies testable mechanism guarantees rather than claiming universal model compliance. No production code, tests, installed tools, or model defaults were changed while drafting.

## BUILD status and platform limitation

Implementation has begun against the explicitly approved design. Latest targeted capture/prompt/validation command: python -m pytest tests\test_module_rules.py -q --tb=short. Actual result:

```text
======================== 24 passed, 3 skipped in 0.29s ========================
```

The three skips are real symlink fixtures requiring unavailable Windows privilege (winerror 1314). Deterministic filesystem-boundary cases execute dangling, escaped-resolution, unreadable-traversal and read-error paths without that privilege; these do not substitute for native symlink integration on another platform. CLI/report integration and full-suite verification remain unfinished. Portable toolchain selection and degraded review on tooling incompatibility remain separate pending requests.

## BUILD complete, awaiting completion gate

The approved launch-local rule delivery is implemented in this isolated worktree. The CLI freezes both optional sources before preparation, fails explicitly on invalid present policy, preserves fixed-evidence and opt-out behavior, shares one complete JSON-framed packet across requested runs, and renders metadata-only provenance. Loaded PR reports no longer claim initialized rules were unapplied. Required toolchain gates, native deadlines, MCP defaults, instruction suppression, strict extraction and review denominators remain unchanged.

Exact full-suite result:

```text
TOTAL                        4181    220    95%
================= 1501 passed, 5 skipped in 193.56s (0:03:13) =================
```

The five skips are two baseline cases plus the three privilege-limited native link fixtures already disclosed. New loader coverage is 96%; the missing-root error wrapper is unexercised. Deterministic OS-boundary cases execute escaped/dangling resolution, duplicate targets, denied traversal and denied reads. Native symlink integration remains unverified on this machine, and no new provider compatibility, model-compliance or review-quality claim is made.

Verbatim output and behavior reconciliation are in [tdd-evidence.md](tdd-evidence.md) and [test-spec.md](test-spec.md). Final documentation validation after reconciliation reported:

```text
checked 308 relative links across markdown files
all relative links resolve
```

No new model calls, machine settings, installation, commits or pushes occurred. Portable toolchain selection, continuing on confirmed tooling incompatibility, and a real-PR context-quality experiment remain separate pending work. The original dirty checkout remains separate and unchanged by this increment.

## Independent review and triage gate

Both approved reviewers completed with strict extraction: Claude Sonnet 5 returned two findings; Gemini 3.8 Flash returned none. Exactly two probes and two reviews, no retries. See [review.md](review.md) for original findings and evidence. Direct validation found a Windows malformed-parent omission, confirmed one ambient-directory test-isolation issue, and found that archived POC replay now stops at its original guide pin after exposition changes. Proposed fixes/documentation await developer triage. Do not implement Sonnet's broad OSError-as-absence recommendation: it would hide required failures. Nothing committed or pushed.
## Shipping verification and remaining limitations

Both approved independent reviewers completed, all reported items were explicitly triaged with the developer, and the two approved fixes plus archived-input documentation were completed. No accepted Blocker/Major remains open. Exact final result:

```text
TOTAL                        4185    220    95%
================= 1504 passed, 5 skipped in 198.94s (0:03:18) =================
```

Remaining disclosed limits: three native symlink cases need unavailable Windows privilege; the loader's missing-root error wrapper is not exercised; archived trial replay requires its original pinned guide/bundle; real-project review quality and broader provider compatibility remain unvalidated. Original POC verdicts remain Inconclusive. Portable Go toolchain selection and continuing model review on confirmed tooling incompatibility remain separate pending requests. No additional model calls or installation occurred.
