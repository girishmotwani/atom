---
project: "phase-tracking-guidance"
phase: "phase-01-command-alignment"
date: "2026-11-24"
status: "approved"
---

# Phase-tracking command alignment

## Purpose

Resolve #33 without adding a new CLI: planning, build, and gate instructions use
the existing artifact-derived phase model instead of unavailable commands.

## Evidence base

- [Regression evidence](regression-evidence.md): all six canonical/packaged
  document cases fail because their phase-management examples are rejected by
  the real CLI parser.
- [Existing phase derivation](../../../tools/atom/phases.py) discovers phase
  directories and reports artifact presence, never semantic completeness.
- [Existing state model](../../../tools/atom/state.py) stores configuration and
  approval declarations rather than a mutable phase/status state machine.
- [Existing CLI](../../../tools/atom/cli.py) exposes status inspection, not phase
  registration/completion or status startup.
- [Evidence choice](decisions.md) was approved before the regression.

Established: the documentation and parser disagree. Assumption not established:
corrected wording will prevent every live agent from inventing another command.
No live model-compliance or end-user usability result is claimed.

## Public surface and responsibilities

No runtime API, schema, dependencies, or Go types change. The user-facing
contract is the guidance in the plan skill, build skill, and human-gates
reference, with the corresponding packaged copies kept consistent.

## Behaviour

1. Planning writes the phase plan and creates the named phase directories under
   specs/{project}/ using the existing artifact-writer boundary. It does not
   require phase registration. Explain that phase discovery is filesystem-derived;
   artifact presence is not approval or completion.
2. Status inspection uses the supported atom status command. Do not substitute
   a writable state machine or claim status records gate approval.
3. Build setup does not require the unsupported status startup option. After a
   human-approved completion, record the accepted outcome and supporting evidence
   in the phase artifacts and update the plan; do not invoke a phase completion
   command. Preserve the existing shipping and between-phase human gates.
4. Resume inspects the actual artifacts and recorded approval evidence, using
   status as derived information. Do not imply the state file stores the active
   phase or proves a phase complete.
5. The non-interactive gate example reports the unapproved gate plainly and exits
   nonzero. It does not invent a status command output or hidden enforcement.
6. All executable Atom CLI examples in the affected documents, including inline
   startup instructions, parse against the real parser without running commands.
   Canonical and packaged text match after native newline normalization.

## Errors and permissions

Artifact-writer refusal or failure remains a blocker. A missing approval remains
a gate, not permission to proceed. No status inspection authorizes initialization,
state writes, installation, model calls, pushing, or publication. Preserve the
existing supported missing-state diagnostics; do not add fallback success.

## Concurrency and extension points

No concurrency changes, background processes, or new shared state. Extend the
focused document list only for instructions that participate in this repair;
this is not a repository-wide shell parser or a packaging generator.

## Verification obligations

- Retain the observed failing regression as defect proof.
- Extend its extraction to inline executable examples and observe the related
  startup-flag failure before repairing it.
- Validate canonical/packaged parity for the three affected pairs.
- Run the focused regression, existing plugin and standalone-entry guidance
  tests, relative-link validation, and git diff whitespace checks.
- Review the numbered guidance contracts against actual phase/status/state
  semantics. Parser acceptance alone does not prove meaningful workflow wording.
- Preserve exact validation output in the phase artifacts.

## Trade-offs

Choose correction of stale instructions over restoring a removed phase state
machine: the runtime already derives phase progress from artifacts. Choose
bounded parser-backed examples and focused parity checks over a generalized
Markdown/shell validation framework. Keep existing human gates; do not introduce
a recurring artifact-only-workaround approval prompt for ordinary planning.

## Out of scope

New CLI commands, phase persistence or selection changes, automatic completion or
approval inference, wholesale packaged-asset generation (#22), repository-wide
guidance cleanup, live model evaluation, and publishing.

## Approval

Approved by the developer in conversation on 2026-11-25. Approval authorizes only this bounded guidance/test
repair, including the directly related build startup/resume corrections.
