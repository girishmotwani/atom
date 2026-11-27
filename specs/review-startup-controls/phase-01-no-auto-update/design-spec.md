# Opt-in review CLI startup control

Date: 2026-11-27. Status: approved in conversation on 2026-11-27.

## Evidence and limits

The developer approved reusing the isolated diagnostic and focused regressions.
The [approved ping result](../../phase-tracking-guidance/phase-01-command-alignment/probe-isolated-result.md)
shows that Copilot CLI 1.0.117-2 accepted --no-auto-update and answered Claude
within the existing deadline when named custom MCP servers were also disabled.
The historical individual timeout cause remains unproven; no latency guarantee
or claim that argument forwarding alone fixes every startup issue is made.

Existing [invocation code](../../../tools/atom/invoke.py) already carries
caller-selected MCP exclusions to probes and reviews. The uncovered boundary is
the new opt-in choice from Atom's parser through the pipeline into both child
commands. Fake-runner regressions must establish that wiring.

## Public surface and implementation boundary

Add atom review --no-auto-update as a store-true option, default false. It applies
to all supported diff selectors, including PR mode. Describe it in CLI help and
the README beside existing per-run MCP startup exclusions.

Carry a keyword-only no_auto_update: bool = False through run_review,
invoke_models, probe_models, probe_command and review_command. Preserve existing
positional parameters and call patterns. Both command builders append Copilot's
--no-auto-update exactly once only when opted in. No persistence, environment
mutation, launcher replacement or subprocess-runner change is required.

## Behaviours

1. With the new flag omitted, probe/review argv and default behavior remain
   unchanged, including fixed-evidence mode. False is not silently overridden.
2. With the flag enabled, every availability probe and every scheduled review
   submission receives --no-auto-update exactly once. Cover multiple models and
   repeated runs; preserve prompt-on-stdin and structured review output.
3. The flag composes with existing named custom-MCP exclusions and fixed evidence.
   Neither automatically enables the other. Do not hard-code local server names
   or disable arbitrary user configuration by default.
4. CLI forwarding works for local working/staged/branch selections and PR mode.
   Existing parser validation, PR preparation/cleanup, toolchain gates, response
   extraction, report formats and exit semantics remain intact.
5. Probe/review deadlines remain 60/600 seconds. A failed probe still prevents
   that model's review submissions and remains explicit failure/partial evidence.
   There is no retry, fallback model, timeout increase or automatic flag removal.
6. Help and README state that this controls child CLI updates for this run and
   uses the version bundled in the launched executable. It is not an arbitrary
   version pin, offline mode, MCP-disable switch or guarantee of availability.

## Errors, concurrency and extension

No new error type or error-suppression path. If an older child CLI rejects the
flag, existing invocation failure reporting applies; do not retry without it.
The option is immutable per invocation and used by the existing bounded
executor, with no new shared state or background work. Existing CommandRunner
and fake-runner seams remain the extension points.

## Test and validation obligations

- Focused red/green tests in existing invocation and CLI test files, with no
  actual Copilot model calls. Test the enabled behavior, omitted default,
  composition, failure boundary and propagation to PR mode.
- Reuse existing named-MCP and command-preservation tests, plus a small matrix
  for enabled/disabled new option. Do not add trivial boolean-accessor tests.
- Update directly dependent strict-signature test doubles for the optional
  keyword rather than introducing broad mocks or weakening assertions.
- Run the focused tests first, then the directly related review pipeline tests
  and existing guidance checks. Run relative-link and whitespace checks including
  new artifacts. No Go check claim applies to this Python tooling repository.
- Preserve actual test output in phase artifacts. No full-suite or live-review
  completion claim without running the corresponding command.

## Trade-offs and exclusions

Choose explicit per-run forwarding rather than changing defaults or saved
configuration. Reuse existing named-server exclusions rather than broadening
fixed-evidence semantics. Keep the subprocess runner and Go-policy behavior out
of scope. Do not add a generic startup-options abstraction for this one boolean.

No paid model calls, probe/review reruns, installed-package refresh, persistent
settings changes, commits, pushes, PR creation or merges are authorized here.
No new phase-selection or phase-registration behavior is introduced.

Keep the existing #33 staged snapshot untouched on the current branch; this
runtime repair is tracked separately in specs/review-startup-controls. Its
earlier design excluded runtime changes and is not retroactively broadened.

## Approval

Approval authorizes only this bounded Python implementation, focused tests and
README/help updates. Completion still requires its own developer gate.

## Implementation reconciliation

Implemented the approved flag, keyword-only forwarding chain and help/README
updates without changing the numbered behaviors or boundaries. Fake-runner
regressions cover all six contracts as mapped in test-spec.md. Actual RED,
GREEN and final affected-area results are preserved in regression-evidence.md,
tdd-log.md and verification.md. Completion approval is recorded in decisions.md; this does
not declare the historical timeout cause proven or the installed CLI updated.
