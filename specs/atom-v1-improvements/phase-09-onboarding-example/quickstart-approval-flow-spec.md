---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-17"
status: "approved-for-bounded-documentation-correction"
poc_report: "quickstart-final-validation.md"
---

# Quickstart Approval-Flow Correction Spec

## Purpose And Evidence Choice

Align the quickstart's brief-approval instructions with the observed interaction:
continue without another message if execution starts after approval; retain the
existing continuation message only for a session waiting for the next instruction.
Make the accepted recovered validation discoverable without adding audit narration
to the walkthrough. This is a documentation-only slice of
[Phase 09](../phase-plan.md), not a new installer or final whole-phase design.

Use the [accepted recovered validation](quickstart-final-validation.md), including
its final-close audit, for the observed approval flow and technical outcome.
Use the [earlier assisted replay](standalone-quickstart-report.md) only within its
recorded limits. The original phase poc-report.md remains Inconclusive; it is not
regraded or used as proof of this correction. The developer explicitly requested
this spec using the accepted replay evidence. No new spike is needed to describe
observed behavior or check text/links; no model-adherence guarantee is introduced.

## Established Before Design

- The exact published initial request was used. Actual human brief approval
  preceded scaffolding and Go edits; actual report approval followed execution.
  The installed skill continued after in-tool brief approval without a separate
  user continuation message. These are saved session-event observations.
- The supplied CSV produced food 20.00 and travel 3.75. Direct exits were 0, 1, 1;
  both negative cases emitted errors and no totals. Atom vet/build/run passed.
- Public plugin content matched all 665 files at 8cf34fa; Python tooling matched
  the documented 5bb33cbe source pin. Selected file/plugin fingerprints and saved
  evidence remained unchanged after normal client/recorder exit.
- The developer accepted that bounded technical result after a requested terminal
  restart, keeping Phase 09 open. Uninterrupted navigation remains Inconclusive.
- The earlier recipe supplied explicit continuation wording after a brief gate;
  retaining that existing wording as a fallback preserves the published path.

## Still Assumed Or Unproven

- The revised conditional wording will be clearer to readers; no new usability,
  setup-time or permission-prompt improvement has been measured.
- Another client/model may wait after approval. No automatic-versus-paused behavior
  is promised across versions; the reader follows the displayed session state.
- The initial terminal interruption is unexplained. Clean-OS, cold-authentication,
  unaided-newcomer and uninterrupted-run claims remain outside the evidence.

## Reader Surface And Files

The only public entry-point change is docs/quickstart.md step 3 and its existing
validation-notes link. No Go API, exported symbol, command, argument, skill,
configuration schema, type signature or runtime policy changes. Go API signature
consistency is not applicable; do not invent declarations for prose work.

| File | Responsibility in the proposed implementation |
|---|---|
| docs/quickstart.md | Conditional continuation instructions and link to the current validation report |
| quickstart-final-validation.md | Publish the already accepted evidence with its restart and navigation limits |
| quickstart-design-spec.md | Reconcile requirement 7, its continuation trade-off, and the original delivery scope with this approved correction |
| quickstart-approval-flow-spec.md | Record this bounded contract and its separate approval |
| findings.md and decisions.md | Preserve evidence, judgments and unresolved limitations |

All artifact paths above are within this phase. The older
[quickstart spec](quickstart-design-spec.md) describes the previously approved
page; this draft does not retroactively alter that approval. After approval,
reconcile its continuation requirement and affected scope statements without
changing the other technical requirements or erasing historical approvals.
README, workflow, runtime files, tools/tests, skills and trial artifacts stay unchanged.

## Numbered Reader Behaviors

1. The reader must inspect the brief against the supplied contract and explicitly
   approve it before authorizing execution. A continuation message never replaces
   approval, and tool permission is not artifact approval.
2. If execution starts after approval, the reader lets it proceed and does not send
   another continuation message. This is conditional guidance, not a promise that
   every model automatically continues.
3. Only if the brief is already approved, POC execution has not started, and Copilot
   has stopped awaiting the next instruction with no command running or unresolved
   prompt/error, the reader sends the existing message once in the same session. Preserve
   that message byte-for-byte; do not duplicate it elsewhere in the spec.
4. Thinking/running tools, a permission question, a writer refusal, an error or
   a request to change scope are not reasons to send the fallback. Preserve normal
   displayed decisions and existing stop-on-failure guidance; add no timeout,
   automatic retry, blanket grant or instruction to bypass a gate.
5. Report review, explicit acceptance/rejection and ending the standalone task
   remain mandatory. Report acceptance does not start planning or production work.
6. The existing final validation-notes link points to quickstart-final-validation.md.
   Keep detailed versions, audit output and limitations in that report, not inline.
   Do not relabel recovered technical success as uninterrupted/newcomer proof or
   mark Phase 09 complete. Publish no raw recordings, session events or credentials.
7. Both Bash blocks, the original POC request and the existing continuation message
   remain identical to published main 8cf34fa. Preserve fixtures, exact totals,
   negative checks, prerequisite/isolation boundaries and scoped permissions.
   No setup shortening or unrelated public-text cleanup is included.

## Error Handling And Concurrency

No new error values, sentinel errors, goroutines, locks or background processes.
Existing diagnostics and writer-refusal behavior remain authoritative. If the
session fails or requests unexpected access/scope, stop rather than treating
continuation as recovery. This correction does not diagnose the earlier exit.
Use one interactive session; do not send the fallback while work is running or
run concurrent trials against the same directory. Documentation does not enforce
model pausing, serialization or safety. No new concurrency/race claim is made.

## Extension Points And Trade-offs

Future client/platform behavior belongs in separately evidenced changes, not a
new model/version switch or automation hook. Existing full-pipeline guidance is
unchanged. No diagram is needed for this two-branch reader instruction.

| Option | Decision and reason |
|---|---|
| Always send continuation after approval | Reject: contradicts the observed already-running flow and invites an unnecessary second instruction |
| Remove continuation entirely | Reject: one observed automatic continuation does not establish universal behavior; preserve the existing fallback |
| Condition the existing message on an approved, stopped session | Choose: matches observed execution while retaining a bounded manual path; no runtime adaptation |
| Add another install/model experiment or shorten setup | Reject for this change: no new behavior is required, and this result does not establish setup length as P0 |
| Put the full audit in the quickstart | Reject: keep the accepted reader-first walkthrough and link its current evidence |

## Verification After Approval

Map the numbered behaviors to factual documentation review, not manufactured Go
unit tests. Read step 3 for these cases: unapproved brief, approved/running,
approved/not-started/awaiting-next-instruction, unresolved tool/error prompt, and report gate.
Only the awaiting-next-instruction case offers the unchanged fallback.

Compare both Bash blocks and both request/continuation text blocks with the frozen
published page. Check the new link target and report's accepted verdict/limitations;
reconcile the original spec without incompatible unconditional instructions.
Run existing python tools\check_links.py and scoped git diff --check. If any
command block or behavior would change, stop and re-gate rather than expanding
this contract. No production RED/GREEN loop, root atom check or fresh replay is
claimed. No new dependencies, test tooling, installations or model calls.

## Scope And Approval Gate

This spec is a draft. Approval authorizes only the described documentation/artifact
correction and its factual/link/diff checks, then a review gate. It does not
approve another replay, runtime fix, permission change, phase completion, commit,
push, PR or merge. No public page is edited during this spec turn.

## Developer Approval: 2026-11-17

The developer selected exactly approve-bounded-documentation-spec after reviewing
the scope, seven requirements, preserved gates/blocks, unmeasured clarity claim,
replay limits and actual documentation checks. Authorize only this bounded
quickstart/artifact correction and its stated checks, followed by review.
No runtime or setup redesign, new experiment, automatic phase completion, commit,
push, PR or merge is approved. Record the decision and end this design-gate turn
before implementing. The public page and original spec remain unchanged here.
