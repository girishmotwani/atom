---
project: "atom-v1-improvements"
phase: "phase-04-entry-points"
date: "2026-11-06"
status: "approved"
---

# POC Brief - New-Repository Setup Mechanics

## Problem

A developer should be able to start using Atom without first creating `go.mod`.
Atom should recommend the module and minimal task-appropriate files, obtain
approval, create only those files and report what is actually ready.
Existing onboarding assumes a module, while `atom init --module` alone does not
create one and omits the Go baseline when it is absent.

The developer-visible requirement is approved setup, not an automatic feature
pipeline or a general template generator.

## The Question

Can the existing Go module-initialization and Atom onboarding commands compose
into a locally usable setup from a repository without `go.mod`, preserving
pre-existing files and reporting empty-module validation honestly?

## Evidence And Remaining Uncertainty

The current source and existing tests establish module onboarding, read-only
repeat initialization and isolated spike scaffolding. Phase 3 supplies approved
evidence-choice guidance, not proof of this new boundary.

This experiment targets integration uncertainty: which minimum approved files
make the composed setup usable, and how onboarding reports a module without
packages. Discovering that after writing new entry-point guidance could cause
Atom to claim a setup is verified when it has not exercised any application.

Actual agent approval/refusal behavior is another material unknown. This local
command trial deliberately cannot establish it. Model routing quality, performance,
project templates and standalone review are separate questions.

## Bounded Trial

Write one disposable Go command under `poc/atom-v1-new-repo-setup`.
Use temporary target directories, never initialize this Python repository.
All module paths are fixed fixture values under `example.com`, not inferred user
choices or proposed production defaults.

Run each case once; repeat only after a separately explained harness defect.

| Fixture | Action | Required observations |
|---|---|---|
| New repository containing only a README | Run real `go mod init` for the fixed fixture identity, then real `atom init`, without adding Go source | `go.mod` exists; README bytes are unchanged; Atom config records the identity; any failing/skipped/no-package baseline remains visible rather than being called a verified application |
| New repository with a pre-agreed tiny standard-library CLI and test in the approved fixture file list | Run module initialization, add exactly those fixture files, then real `atom init` | Recorded build/test commands exercise the CLI; baseline results and command exits are captured; initial README remains unchanged |
| Existing matching module with a tiny CLI/test and README | Do not reinitialize or overwrite the module; run onboarding, then its matching repeat | Existing source/module/README bytes survive; repeat initialization leaves a complete file-content snapshot unchanged |
| Setup declined | Record a fixed declined decision and perform no setup | Before/after file snapshots are identical; no `go.mod` or `.atom` is created |

The last row tests only the harness's no-action branch. It does not show that an
agent asks, waits, interprets a refusal correctly or respects a real developer.
That must be assessed in a separate developer-observed interaction.

## Verdict Rules

- **Confirmed, mechanically only:** all fixtures reach their declared observations,
  the tiny CLI has a real successful build/test baseline, and empty-module results
  are represented honestly even if that fixture's gates fail.
- **Refuted:** an existing command cannot deliver the usable CLI setup, silently
  loses existing content, reports failed/no-package validation as a clean
  application, or matching repeat onboarding changes the content snapshot.
- **Inconclusive:** missing prerequisites, environmental failures, incomplete
  output or a defective harness prevent attribution to the integration.

Capture subprocess arguments, cwd, exit status, stdout and stderr separately,
baseline gate details, files created and preservation checks. Nonzero setup
commands are failures to analyze, not permission to continue silently.
Return a nonzero harness status for Refuted or Inconclusive.

## Approach And Limits

- Reuse installed Go and the working editable Atom CLI through an absolute command
  boundary. Record their versions and the source commit.
- Use only standard-library fixture code. Set child-only `GOTOOLCHAIN=local`,
  `GOPROXY=off` and `GOSUMDB=off`; install nothing and change no user defaults.
- Keep optional network-capable analyzers outside the child PATH. Record resulting
  skipped checks; do not label them passed. Do not invoke real reviewers.
- Bound each subprocess by a timeout; capture both streams on errors. Stop and
  report timeout as Inconclusive rather than claim unverified process-tree cleanup.
- Preserve commands and raw results under the POC directory; clean up only the
  exact temporary fixture directories the harness created.
- Do not edit production code, command/skill guidance, target policies or phase
  registrations during the trial.
- Do not commit, push, publish, download dependencies, modify machine settings or
  run additional model/agent batches.

Estimated scope: four local fixtures, zero model calls, zero paid-review calls.
Allow several minutes for cold Go compilation; this is not a performance benchmark.
Windows is the only proposed environment. Phase 09's Linux replay remains separate.

## Alternative

Edit guidance using existing onboarding tests alone. This is cheaper but leaves
the missing-module composition and empty-module baseline assumption unmeasured.
The recommendation is the bounded mechanical trial above, followed by its report
gate before any design.

## Approval Boundary

Approval authorizes writing and running this local trial only. It does not approve
production changes, a particular scaffolding interface, real-agent/model spend or
the rest of Phase 04. Present its result and limitations before proposing the next
experiment or design step.

The developer selected "Approve local trial" on 2026-11-06.
