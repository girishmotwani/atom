# Decisions

## Evidence choice approved on 2026-11-24

The developer selected "Approve guidance repair and focused regression evidence".
Use a failing Python regression against the real CLI parser as proof of this
understood defect. Do not add a phase-management CLI or a throwaway Go spike.

## Scope and artifacts

One independently reviewable guidance repair needs no multi-phase project plan.
Use this single phase directory for the design, evidence, findings, and decisions.
The developer explicitly approved atom-write-artifact for this repository's
pipeline-artifact writes. Tests use the ordinary editing tools.

## Design approval on 2026-11-25

The developer selected "Approve implementation of this spec" for design-spec.md.
This authorizes the bounded guidance/test repair, including the related build
startup/resume corrections, not runtime changes or publication.

## Documentation verification adaptation

Map the numbered contracts to parser-backed regression, canonical/packaged
parity and factual review as recorded in test-spec.md. The documentation-only
adaptation is explicitly allowed by tdd-discipline.md. No production Go TDD or
atom check claim applies to this Python tooling repository with no root Go module.
Extend the existing regression rather than weakening it: its original extraction
misses inline commands, including the unsupported startup option.

## Boundaries

Keep the existing filesystem-derived phase model and human approval gates.
Correct canonical instructions and their packaged counterparts together.
No runtime API, configuration schema, dependency, installation, paid model call,
push, or pull request is authorized. Completion remains subject to its human gate.

## Implementation acceptance on 2026-11-25

The developer selected "Accept implementation; proceed to review next" after
reviewing the repair summary, validation results and evidence paths. The next
named step is review; no push or publication is authorized.


## Shipping and bounded review approval on 2026-11-25

The developer requested "lets ship it" and then selected "Prepare the bounded
multi-model review proposal first", followed by "Approve this exact review plan".
Review the explicitly staged six guidance files, focused test, and six existing
phase artifacts. Use gpt-5.4 and gemini-3.8-flash, each once, concurrency 1, fixed
evidence with the design spec, tdd log, phases.py, state.py and cli.py. Both differ
from author gpt-6.1-sol. Permit up to two availability probes and two submissions;
no automatic retries, token/cost ceiling, installations, or toolchain changes.
No root Go module/config/pin exists: Go tooling is skipped, not passing. Fresh
Python/doc validation is captured in tdd-log.md. Persist the report as review.md
and update phase audit files. Failed/partial review or Blocker/Major findings
stop publication. No waiver of independent review was given. The ship request
remains pending a clean review; no merge is authorized.

## Artifact whitespace correction approved on 2026-11-25

The developer selected "Approve normalization and continue the approved review"
after the staged check caught whitespace in previously untracked artifacts.
Trim trailing spaces and extra EOF blank lines only; label the regression
output normalization explicitly. The prior unstaged whitespace check did not
cover these new files. No reviewer probes/submissions ran before this repair.
The same approved reviewer command and budget apply; no runtime fixes or new
review submissions were added.

## Halted after partial review on 2026-11-25

The approved command exited 1: gpt-5.4 did not answer (exit 1), while
 gemini-3.8-flash completed and reported no findings. Persisted the actual report
as review.md. The required two-model participation is unmet. Honor the approved
stop condition: no automatic retry, model substitution, commit, push or PR.
Further spend or an explicit review waiver requires a new developer decision.

## Three-round review batch approved on 2026-11-25

The developer requested three independent rounds with the same two reviewers,
gpt-5.4 and gemini-3.8-flash, then selected "Approve the three-round batch as
proposed". Use the same staged snapshot and five context files, runs 3 per model,
concurrency 1 and fixed evidence. Each invocation receives the same input without
other runs' findings or intervening fixes. Up to two probes and six submissions;
no retries, substitutions or token/cost ceiling. The prior gpt-5.4 failure risk
was disclosed. Save the batch as review-three-rounds.md, preserve the original
review report, and update the combined participation/triage audit. Partial or
failed participation or Blocker/Major findings stop shipping. No code fixes or
publication are authorized by this review approval.

Staged tree identifier: 7ffadd8569dae01c69100e14d76fb71927375ef7

## Halted after the approved three-round batch on 2026-11-25

The batch exited 1: gemini-3.8-flash answered 3/3 with no findings, while
gpt-5.4 answered 0/3 after the reported 60.156-second timeout. The original
staged tree and prompt hash were unchanged. Preserved the actual batch report
as review-three-rounds.md and appended participation/triage to review.md.
Honor the approved stop condition: the independent multi-model requirement
remains unmet; no further spend, substitution, commit, push or PR creation.

## Replacement three-round review approved on 2026-11-26

The developer requested replacing GPT and running three review rounds, then
selected "Approve Claude + Gemini, three passes each" for the exact proposal.
Use claude-sonnet-5.5 and gemini-3.8-flash, neither the author gpt-6.1-sol,
on the same staged snapshot with the same five caller context files. Runs 3
per model, concurrency 1, fixed evidence, no intervening fixes/shared findings.
Budget up to two availability probes and six submissions; no automatic retries,
substitutions, token/cost ceiling, installations, or toolchain changes.
No root Go module/config/pin: Go tooling remains skipped, not passing. Preserve
prior reports and save the actual replacement batch as
review-replacement-three-rounds.md; append combined participation/triage to
review.md and update findings.md/decisions.md. The approved scope ends at
reporting/triage: no fixes, commit, push or PR. Staged tree identifier remains
7ffadd8569dae01c69100e14d76fb71927375ef7.

## Halted after replacement batch on 2026-11-26

The exact approved Claude/Gemini command exited 1. Gemini answered 3/3 with no
findings; Claude answered 0/3 after a reported 60.155-second timeout. Persisted
the actual report as review-replacement-three-rounds.md and appended the combined
participation/triage to review.md. The staged tree and logical prompt remained
unchanged. Do not equate missing responses with a clean review. No automatic
retry, substitution, timeout change, fixes, commit, push or PR was performed.
The independent multi-model requirement remains unmet; shipping remains blocked.

## Local timeout investigation on 2026-11-26

The developer requested "lets investigate". Trace the local invocation and
installed runtime, inspect only relevant existing process/session metadata, and
run deterministic fake-runner tests plus a version-only child command. Reading
known runtime files and timestamp-bounded logs outside the checkout was necessary
to establish what the installed atom command actually launched. Do not export
raw logs/account data into repository artifacts. No model requests, settings or
source changes, package refresh, deadline increase or publication were performed.
Recorded the 60-second probe boundary, custom-MCP startup hypothesis and automatic
CLI version-change confound in timeout-investigation.md. A further diagnostic
ping requires a separately approved bounded proposal; old review spend approval
is not reused for new calls. The staged snapshot is unchanged.

## Single isolated ping approved on 2026-11-26

The developer selected "Approve the single isolated Claude ping" for the exact
proposal recorded in conversation: one claude-sonnet-5.5 ping invocation through
the installed native runner, deadline 60 seconds with existing cleanup grace,
fixed-evidence tool exclusions, both named custom MCP servers disabled and
--no-auto-update. Current bundled CLI version was verified as 1.0.117-2.
No review diff, extra model calls, retry, timeout change, source/settings edits,
installation request or publication. Preserve only safe operational evidence in
probe-isolated-result.md and update phase findings/decisions. Success establishes
availability under this configuration, not the sole cause of earlier timeouts.
## Isolated ping result on 2026-11-26

The single approved Claude ping completed successfully, exit 0 in 29.018 seconds,
with no stderr. Local session events confirm selected/responding model
claude-sonnet-5.5 and input ping. CLI version 1.0.117-2, both configured custom
MCP servers disabled and automatic updates disabled. See probe-isolated-result.md
for safe actual output and evidence limits. Availability in this configuration
is confirmed; the historical stall's individual cause is not. No additional
model request, full review, fix, timeout increase, source/settings change,
installation command or publication followed. The review requirement remains
unmet. Named MCP exclusions are supported by atom review, but it does not expose
forwarding --no-auto-update; a future plan must not silently equate these setups.

## Draft publication approved on 2026-11-27

The developer requested "lets create PR", then selected "Create one draft PR
with both changes; defer review gate for draft publication only". Publish the
accepted phase-command guidance fix and startup-control repair as two separate
commits in one draft PR on the existing branch. Rerun affected Python tests and
relative-link/whitespace checks before committing. Push this branch only.

This explicitly defers the independent-review prerequisite for draft publication;
it does not declare either phase's multi-model review complete. Keep the missing
review participation and unreviewed runtime repair prominent in the PR. No new
paid calls, installed-package refresh, saved-setting change or merge is approved.
Earlier no-publication/index-preservation boundaries are superseded only as
necessary to stage, commit, push and open this approved draft. The original
staged tree remains recorded in prior artifacts for audit.

## Draft creation command

Use gh pr create --draft with explicit repository, base and head. The existing
atom ship implementation assembles one phase and offers no draft option, so its
normal create path cannot represent this approved two-phase draft publication.
Using GitHub CLI directly preserves draft status from creation and allows both
artifact sets plus the explicit pending-review limitation in one description.
This changes publication assembly only, not implementation or review verdicts.
