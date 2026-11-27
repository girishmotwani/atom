# Findings

## Repaired defect

Issue #33 was reproduced in canonical and packaged planning, build, and gate
instructions. Unsupported phase-management examples are now replaced by existing
status inspection and explicit artifact-based tracking. The related unsupported
startup flag and misleading resume wording were repaired under the approved spec.
See [regression evidence](regression-evidence.md); tdd-log.md records the extended
inline-command failure and passing validation.

## Outstanding findings

No additional code/guidance findings were reported by the one responding reviewer.

## Evidence limits

This repository implements Atom in Python and has no root Go module. Python
parser/documentation checks are the relevant gates, not a fabricated Go spike.
No live model or external project replay has been run. Static guidance validation
does not establish that every agent follows the corrected instructions.

## Shipping blocked by partial independent review

The approved fixed-evidence review exited 1. gemini-3.8-flash completed 1/1 run
and reported no findings; gpt-5.4 completed 0/1 and exited 1. The runtime report
only identifies that exit code, not a more specific cause. See review.md for the
actual report and input provenance. Two independent responses are still required;
this is not a clean multi-model review. Go tooling was explicitly skipped because
there is no root module. No retry, commit, push or PR creation occurred.

## Three-round follow-up remains blocked

The approved three-pass batch exited 1. gemini-3.8-flash completed 3/3 passes
with no findings; gpt-5.4 completed 0/3 after a timeout (observed elapsed
60.156 seconds). The staged tree and logical prompt were unchanged. See
review-three-rounds.md for the actual report and review.md for combined triage.
This is not a clean multi-model review; missing responses remain an open shipping
prerequisite. No additional retry or publication occurred.

## Replacement review also remains partial

The approved Claude/Gemini three-pass batch exited 1. gemini-3.8-flash completed
3/3 with no findings; claude-sonnet-5.5 completed 0/3 after the runtime reported
a timeout at 60.155 seconds. This resembles the earlier GPT timeout duration but
does not establish a shared root cause. See review-replacement-three-rounds.md
and the combined participation/triage in review.md. The same staged tree and
logical prompt were used. Independent two-model participation remains unmet;
no additional retry, fix or publication occurred.

## Timeout boundary identified on 2026-11-26

The 60-second limit is the availability ping, not the 600-second review limit.
Installed invoke.py matches the checkout: failed probes prevent review submission,
so 0/3 denotes zero scheduled reviews for that model. Existing logs show custom
MCP startup despite fixed-evidence tool exclusions and a CLI automatic binary
update between probes. Shared startup warnings are not sufficient to diagnose
an authentication fault. The exact startup stall remains unproven. See
timeout-investigation.md for source/log provenance, five passing fake-runner
tests, and the proposed one-probe diagnostic. No additional model calls ran.
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

## Draft publication boundary on 2026-11-27

The developer approved a draft PR containing both accepted repairs and deferred
the independent-review prerequisite for draft publication only. Review remains
pending: prior guidance reviews have only one responding model, and the startup
control repair has no independent model review yet. No new paid review is
approved here. Historical timeout causality remains unproven; installed Atom
has not been refreshed. These are visible review limitations, not a clean-review
or ready-to-merge verdict. No merge is authorized.
