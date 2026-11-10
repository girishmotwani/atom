# Review Proposal - Accepted Standalone Guidance Slice

Date: 2026-11-10.
Status: proposed; no reviewer execution authorized yet.
Implementation accepted with "Accept implementation; prepare review proposal".

## Objective And Selection

Review the accepted standalone-review implementation against its approved design:
consent before probes/spend, correct selectors/models/report semantics, root-module
limits, standalone stopping, phase compatibility, installed-bundle parity and
meaningful structural tests. Find consequential defects or contradictions, not
wording preferences. This is Python/documentation work: no root Go module is
created and no fabricated Go gate is run.

Frozen [scope and excerpts](review-scope.json) includes raw-file SHA-256, original
line numbers and three new files plain git diff would omit. Six tracked targets
overlap earlier accepted setup work; review the standalone ranges below. Older
router/setup/installation work is compatibility context, not automatically a
newly introduced defect. HEAD is not an isolated standalone baseline; a whole
branch diff is not this slice.

| File | In-scope current lines |
| --- | --- |
| `skills\atom\references\standalone-review.md` | 1-134 |
| `skills\review\SKILL.md` | 1-241 |
| `com.github.copilot\commands\start.md` | 31-36 |
| `README.md` | 140-162 |
| `docs\workflow.md` | 259-290 |
| `tools\tests\test_standalone_review_guidance.py` | 1-82 |
| `tools\tests\test_onboarding.py` | 174-199 |
| `tools\atom\assets\skills\atom\references\standalone-review.md` | 1-134 |
| `tools\atom\assets\skills\review\SKILL.md` | 1-241 |

Supporting evidence: [approved design](design-spec.md),
[validation map](test-spec.md), [accepted implementation](implementation-report.md)
and its verbatim `implementation-validation.txt`. These inputs are also hashed.
Relevant existing CLI/review/merge/bootstrap code may be read to verify factual
claims; it is not a target for opportunistic redesign. Distinguish background
issues from introduced defects and consequences of this implementation.

## Proposed Execution And Models

Two independent **read-only code-review agent tasks**, each covering the same
whole scoped slice with the same design/evidence. Neither sees the other's
findings before submitting its own. Do not divide them into artificial angles.

| Role | Explicit requested model | Author exclusion |
| --- | --- | --- |
| Independent reviewer | `claude-opus-5.5` | Different from author `gpt-6.1-sol` |
| Independent reviewer | `gemini-4-argon` | Different from author `gpt-6.1-sol` |

These IDs are advertised choices in this session's agent-tool catalog; actual
provider availability has not been probed. Approval names these exact models so
execution can request them explicitly, not assume harness defaults guarantee
independence. If selection fails or actual independence cannot be established,
report the limitation and stop without fallback, replacement, extra probes or retry.

This adapts phase review to its Python/Markdown surface. It is not an `atom review`
run, installed-plugin interaction trial or proof of its model transport. Bare
`atom review --working` would omit new assets/tests and mix earlier setup edits.
Read-only agents over explicit inputs avoid staging files, manufacturing a commit
or replacing the Git index. The frozen installed preview remains unchanged.

## Spend And Stop Conditions

Approve exactly two reviewer tasks, one pass each, normally about five to ten
minutes. This is not a promise of two underlying LLM requests: each agent can use
multiple inference/tool rounds. No exact token, cost or provider-time ceiling is
available. No separate user-level availability-probe calls are planned.

No nested agents, reviewer subprocesses, live trials, test reruns, installations,
external research, Git writes, source edits, fixes, cleanup, commits, pushes or
publication. Reviewers read only and return findings with file/line, consequence,
confidence and severity, or explicitly No findings. Source instructions/examples
are review data, not commands to execute.

Check every frozen file/supporting digest before dispatch and before accepting
results. Scope drift or changed evidence stops review rather than silently
broadening it. Preserve partial output if a task fails; no replacement/retry.
Do not mark the multi-model obligation complete if fewer than two qualifying
independent reviewers respond.

## Outputs And Triage

After approved execution, the parent saves unedited responses through the artifact
writer as `review-claude-opus-5.5.md` and `review-gemini-4-argon.md` here, then writes
`review.md` with deduplicated consequential findings, disagreements, actual
participation and limits. Reviewers do not write files. Existing phase findings
and decisions record the result/triage outside the frozen reviewed source scope.

Read critical/high findings individually, including single-model findings. Check
claims against frozen inputs and the approved contract. Agreement is not proof;
do not quietly discard disagreements. Present proposed fixes, deferrals and
rejections with reasons. Review approval does not authorize implementation of fixes.
Existing tests support review; they do not prove live user control.

## Unchanged Limits

Accepted focused evidence is 204 passed in 46.21s; this proposal makes no fresh
or full-suite test claim. Live installed-user consent/refusal/stopping remains
unproven; the setup trial is still paused and Inconclusive. No Phase 04 completion,
installed-preview refresh, release or publication is authorized.

## Preparation Correction

The previous artifact call used Windows text-mode subprocess input and the writer
rejected the scope as non-UTF-8. The developer approved explicit UTF-8 correction.
Retried the same writer/path with UTF-8 bytes; verified the JSON round-trip
preserves original Unicode excerpts. No alternate writer or production edit.

## Decision

Approve both read-only code-review tasks using these exact models, frozen scope,
spend/stop limits and report paths; or revise/pause. Approval permits those reviews
and report synthesis only, not fixes, installation or shipping.
