# Trial Amendment - Absent Advisory Tool Observation

Date: 2026-11-08.
Status: proposed; correction and rerun await approval.
Related: `poc-report.md` and the approved `poc-brief.md`.

## Unchanged Question And Conditions

Keep the approved standalone-review question, installed runtime, five cases,
real Git/Go gates, synthetic reviewers, source/state comparisons and output
criteria unchanged. No production code, optional installation or model call.

## Observer Correction

Archive the exact first observer before editing. Permit `staticcheck`, `errcheck`
and `govulncheck` availability attempts only when each is absent under the bounded
child PATH. Delegate to the existing runner and retain its actual TOOL_MISSING
result and diagnostic. A discovered optional analyzer remains a stop condition;
never run it or synthesize a pass. All other unexpected commands still stop.

Do not treat expected absent advisory tools as an execution failure of the trial.
Required command failures/timeouts retain existing stop semantics. This correction
changes the instrument, not Atom's production behavior or the success criteria.

## New Run And Preservation

Use a previously absent root:

`C:\Users\gimotwan\AppData\Local\Temp\atom-phase04-standalone-review-corrected-20261108`

Archive new raw results as `transport-correction-execution.json` and the report
as `transport-correction-report.md` beside the existing POC report. Preserve the
first observer, root and `execution.json`; no deletion, in-place retry or silent
replacement of a verdict. No more than this one corrected execution is authorized.

Same ceiling: five review calls, at most 100 local child-command attempts,
180 seconds per child, approximately five minutes. Zero model calls, subagents,
installs, remote Git operations or publication. Stop on another measurement gap,
unexpected mutation or exhausted budget and report it, without another retry.

Approval authorizes only this observer correction and the unchanged mechanical
trial in a fresh root. It does not approve a design, production changes, real
reviewers, cleanup or overall Phase 04 completion.
