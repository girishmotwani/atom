---
project: "atom-v1-improvements"
phase: "phase-04-entry-points"
scope: "new-repository-setup-slice"
author: "Copilot"
date: "2026-11-06"
status: "approved"
poc_report: "poc-report.md"
---

# Design Spec - Approved New-Repository Setup

## Purpose And Scope

Let a developer use Atom in a new Go repository without first creating `go.mod`.
The agent inspects the target, recommends minimal goal-appropriate setup, waits for
approval, performs only that setup and reports its actual readiness.

This is the first bounded slice of Phase 04, not the complete entry-point phase.
It changes instruction/orchestration guidance using existing commands. It adds no
runtime command, Go/Python API, template generator or approval enforcement engine.
Standalone review and the remaining entry paths retain separate evidence/design
obligations. Phase 09 will demonstrate the agreed setup path in its worked example.

## Evidence Base

The developer approved the [setup mechanics report](poc-report.md) on 2026-11-06.
The [entry-point inventory](entry-point-inventory.md) identifies the existing
commands and instruction surfaces.

### Established

- Real `go mod init` followed by existing `atom init` composed successfully on
  Windows with Go 1.27.0 and Python 3.13.14.
- The approved tiny standard-library CLI/test fixture had passing build, vet,
  formatting and test baseline results. Onboarding deliberately skipped race.
- Module-only setup completed but recorded failing vet/test checks because it had
  no packages. Onboarding exit 0 does not imply a passing application baseline.
- Existing fixture content survived setup; matching repeat onboarding left the
  complete file-content snapshot unchanged.
- Onboarding installs Atom files and may produce a build executable.
- `atom init --module` alone does not create `go.mod`; without it, no Go baseline
  is captured. It is not the new-project setup shortcut.
- Phase 3's approved policy requires a justified evidence recommendation and
  developer choice. Its experiment does not prove actual waiting or refusal.

### Still Assumed Or Required To Validate

- A shared recommendation/approval reference can keep existing entry points
  consistent without loops. This must be checked in the changed guidance.
- An agent will follow the approval and stopping instructions. This is a required
  behavioral contract, not a technical guarantee; validate real interaction
  separately before claiming the path works end to end.
- The minimal CLI fixture informs one setup option, not arbitrary service/library
  templates or real-user module naming.
- Linux replay, conflict/recovery behavior and complicated existing projects are
  not established by this POC. Preserve existing refusal behavior rather than
  invent a repair or portability claim.

## Public Entry Points And Flow

Use existing `/atom:init` for explicit setup. `/atom:start` recognizes an explicit
new-repository/setup goal and recommends that bounded path instead of treating a
missing module as a reason Atom cannot be used. It does not silently onboard every
repository for unrelated goals.

`/atom:build` may recommend the same setup when its explicitly requested full
workflow needs it. Setup approval does not satisfy any later proof/design gate.

```text
Inspect target and intent
          |
          v
Recommend module/files/commands/checks
          |
          v
Developer decision ---- refusal/change ----> stop or revise proposal
          |
      approval
          v
Recheck target -> agreed module/scaffold -> existing atom init
          |
          v
Report created files, baseline scope and limitations -> stop setup
```

No new slash command or CLI flag is proposed. Tool-execution permissions remain
independent of the developer's approval of the recommendation.

## Numbered Behavior Contract

1. **Enter without a module.** A setup request is accepted without `go.mod` or
   `.atom`. Establish whether Go is the intended target before proposing files;
   do not add a module to a non-Go repository just to satisfy an Atom check.

2. **Inspect before asking.** Read the relevant target files and existing module,
   source, workspace, Atom setup and instruction/ignore configuration. Use local
   repository identity only as evidence for a proposed module path, not as a
   silently approved default. Do not fetch remote content or initialize Git.
   When Atom onboarding is requested, verify working forms for both installed
   command roles through supported help checks before the final setup proposal or
   any module/scaffold writes. If unavailable, stop without setup changes and
   obtain separate prerequisite-installation consent; verify again before proposing
   setup. A Go module/scaffold-only request does not require Atom commands.

3. **Resolve meaningful choices.** Recommend the narrowest setup fitting the
   goal. If the real module identity, application kind or Go-version constraint
   is unknown, ask one focused question at a time. Do not silently use a directory
   name or `example.com` placeholder for the user's real module.

4. **Present one concrete proposal.** Name the target root, exact module path,
   installed Go/version implications, files to create or intentionally update,
   commands, baseline checks, generated build outputs and stopping point.
   Include Atom's `.atom` bundle/config/state/baseline/event files, managed
   instruction/ignore updates and `specs`/`poc` directories when onboarding is
   proposed. Disclose existing project build/test recipes rather than promise
   Go defaults if the project declares something else.

5. **Wait for explicit approval.** Recommendations, earlier phase approval,
   ambiguous replies and an instruction merely to inspect are not setup approval.
   Before approval, do not bootstrap-install tools, create files, run checks that
   produce build outputs or initialize Atom state. Ordinary inspection is allowed.
   Existing working tools may be located through their supported help interfaces.

6. **Honor refusal and changed intent.** If declined, make no setup changes and
   report what remains unavailable. If a reply changes the module, file list or
   scope, revise the recommendation and obtain approval for the revised proposal.
   Do not reinterpret refusal as approval for a smaller unsolicited setup.

7. **Offer bounded scaffold choices.** Module-only setup is valid when that is
   the developer's goal. For a newly requested CLI, recommend at most the minimal
   standard-library command and meaningful smoke test demonstrated by the POC.
   Show their intended contents/behavior before approval. Do not add frameworks,
   dependencies, CI, licensing, Makefiles or unrelated application code by default.

8. **Recheck before executing.** Confirm the target and relevant files still
   match the approved proposal. Preserve existing modules and source. Unexpected
   state, workspace conflicts, symlinks or collisions stop setup with a named
   explanation; do not overwrite or attempt an unapproved repair.
   Approved managed instruction/ignore updates preserve existing user content.

9. **Use the existing command boundary.** When the module is missing, run
   `go mod init <approved-module-path>`, verify the resulting file/identity,
   create only agreed scaffold files, then run existing `atom init` if onboarding
   was approved. For an existing module, skip module creation. Do not substitute
   `atom init --module` for creating a usable Go module. Matching Atom setup follows
   the existing read-only repeat path; never add `--force` automatically.
   Without approved onboarding, skip Atom commands and onboarding-only file
   verification/completion requirements; report only the agreed Go setup/checks.

10. **Keep execution bounded.** Execute sequentially in the approved target.
    Record command failures and both streams. A failure or timeout stops the
    remaining setup. Report completed/partial changes; do not promise transactional
    rollback, blindly retry or delete user files. Cleanup or repair needs its own
    approval when it changes the agreed plan.

11. **Do not silently install or download.** The minimal new-module path uses
    installed tools and standard-library scaffold code. Use the POC's child-only
    local-toolchain/offline settings for this path; do not change user defaults.
    Missing tools, an unsupported requested version or dependencies that cannot
    be resolved require a separate recommendation and approval. Bootstrap's
    optional user-PATH setup retains its existing separate opt-in.
    Existing-project check requirements must be disclosed, not bypassed.

12. **Report setup separately from validation.** State whether module/scaffold
    creation and Atom onboarding succeeded, then report the captured baseline
    independently. Module-only no-package failures are expected information,
    not permission to add source or claim the application passes. For a new CLI,
    baseline evidence describes the approved scaffolded tree, not the original
    empty directory. Skipped race/analyzer checks establish nothing about their
    categories.

13. **Preserve repeat semantics.** Successful matching repeat initialization
    changes nothing and captures no fresh baseline. Explain preserved configuration
    and missing machine-local baseline files according to the existing init contract;
    do not recreate them, reset approvals or upgrade the local bundle implicitly.

14. **Stop at the requested outcome.** A setup-only request ends with the setup
    result and any actionable limitation. A printed POC suggestion from the CLI
    is not permission to continue. Do not invoke discovery, proof, implementation,
    review, commits, pushes or publication after setup without a distinct approved
    next step. For an explicitly requested full feature, recommend the next
    evidence step under Phase 3; setup approval never waives that gate.

## Content Integration

| Surface | Responsibility in this slice |
|---|---|
| New shared `skills/atom/references/repository-setup.md` | Own the inspection, proposal, approval, execution and stop contract once |
| `skills/init/SKILL.md` | Replace the pre-existing-module entry barrier with the shared approved setup path; retain existing onboarding/repeat/refusal behavior |
| `com.github.copilot/commands/start.md` | Recognize explicit setup intent and its bounded stopping point; avoid claiming every response must start another command |
| `skills/build/SKILL.md` | Reuse setup prerequisites without treating setup as permission for downstream feature work |
| `tools/atom/assets/skills` | Mirror changed canonical skills and the new shared reference in the self-contained bundle |
| README and workflow documentation | Describe missing-module entry accurately, including approval and readiness limits; keep Phase 09's new-repository example requirement |

The start command remains plugin-only; do not invent a packaged counterpart.
The shared reference performs no runtime dispatch and never invokes the entry
point that called it. Bootstrap stays a prerequisite helper, not an orchestrator
that silently changes task scope. Existing lifecycle disciplines remain reusable
references rather than duplicated policy blocks.

## Error Handling And Concurrency

There are no new error types or concurrent components. Use existing command
diagnostics and exit statuses; add no parser that turns their failures into success.
The guidance requires explicit reports for missing prerequisites, conflicts,
failed commands, incomplete setup and unavailable evidence.

This slice does not make setup safe for concurrent agents. Rechecking is a
workflow safeguard, not an atomic transaction. Unexpected concurrent changes
require stopping; do not claim file locks or rollback that existing tools lack.

## Validation Obligations

- Map the numbered contract to factual/semantic guidance review and the existing
  onboarding/repeat/plugin/distribution/link checks; do not create brittle
  string-presence tests and call them proof of agent behavior.
- Verify canonical/package parity and fresh bundle inclusion of the new reference.
  Existing command surface and normal matching-repeat behavior must stay intact.
- Reuse the approved mechanical POC within its stated Windows/default-command
  limits. Re-gate if implementation needs new runtime behavior or unproven
  scaffolding rather than only the agreed orchestration.
- Separately agree and observe real approval, refusal and changed-proposal
  interactions before declaring this entry path usable end to end.
  A scripted decision flag or model's claim that it waited is insufficient.
- No model batch, Linux setup change or release publication is approved by this
  spec. Phase 09's Linux example remains a separately gated replay.

## Trade-offs

| Option | Decision and basis |
|---|---|
| Shared guidance over a new setup command | Chosen: the approved POC establishes existing command composition; no new runtime API is needed for this slice |
| Always generate an application | Rejected: module-only setup is a valid goal, and green checks must not justify unapproved files |
| New general library/service/CI templates | Deferred: the POC covers only a minimal CLI and module-only target |
| Treat onboarding exit 0 as verified readiness | Rejected by the observed failing module-only baseline |
| Approval engine or automatic routing classifier | Rejected: Phase 3 is guidance, not enforcement, and this slice should reuse its boundary |
| Modify init's runtime output or exit semantics | Not chosen: an entry path can explain the existing result and stop; changing CLI contracts requires separate scope/evidence |
| Automatically repair, force or roll back | Rejected: existing state may contain approvals and user changes; recovery is an explicit decision |

## Out Of Scope And Gate

This spec does not implement standalone review, Go diagnosis, arbitrary templates,
runtime approval enforcement, a full Phase 04 routing engine, the Phase 09 example
or release/publication work.

Approval authorizes implementing this instruction/orchestration slice, with
appropriate semantic/distribution checks. It does not authorize paid interaction
trials or claim all numbered behaviors have already been observed.
The developer selected "Approve setup design" on 2026-11-06.

## Implementation Reconciliation

The shared setup reference and init/start/build integrations are implemented as
approved, with matching packaged assets and related README/workflow explanations.
One onboarding distribution test checks canonical/package/installed byte equality.
No runtime API, command, exit status or repeat-initialization behavior changed.
Start recommends prerequisite setup only when the selected task needs it, not
merely because a root module or Atom state is absent.

See [implementation evidence](tdd-log.md) and [test mapping](test-spec.md).
Guidance/distribution implementation is awaiting its completion gate; actual
developer-interaction validation and the rest of Phase 04 remain outstanding.


## Approved Review Corrections - 2026-11-13

Developer selected 'Approve both guidance fixes' after the bounded two-reviewer
source review. Tighten readiness before final onboarding-inclusive proposals or
setup writes, and consistently condition onboarding-only execution, verification,
completion and model guidance on onboarding approval. This is a guidance amendment,
not a runtime/API change or claim of technical permission enforcement.

Reuse approved existing command-composition/help and packaging evidence; validate
changed text and distribution boundaries. No new Go spike, runtime RED/GREEN claim,
installation, live case, reviewer budget or waiver of outstanding rehearsal evidence.
The frozen pre-correction context and original raw reviews remain in setup-review/.


## Publication Context - 2026-11-17

The preceding sections preserve the dated implementation/approval history, including
then-pending gates. The setup corrections and bounded installed observations were
subsequently accepted. See [current evidence and limits](setup-evidence.md),
[review provenance](review.md), [shipping verification](verification.md) and
[publication decisions](decisions.md). References to the original setup-review
archive name local historical records, not additional files published in this PR.
The combined instructions retain newer upstream bootstrap guidance; the historical
live observations do not cover those combined bytes.
