---
project: "artifact-write-permissions"
phase: "experiment-02-partial-artifacts"
author: "Copilot"
date: "2026-10-06"
status: "draft"
---

# POC Brief

## Problem

The first experiment showed that artifact-path approval is applied per file rather
than atomically per patch. The developer accepts that an allowed artifact may be
written before a protected code target prompts, provided the code target itself is
never auto-approved. The remaining safety question is therefore whether every
individual request outside the approved artifact boundary stays gated.

- Developer-visible outcome: Routine Atom artifact writes proceed without prompts.
- Current failure or limitation: Every repository write currently prompts unless broad write permission is granted.
- Non-negotiable constraint: Source, tests, repository instructions, Atom's bundled rules, escaped paths, and external paths must never be auto-approved.
- Evidence already known: Isolated allowed writes succeed; isolated protected writes fall through; mixed patches can apply allowed artifact files before protected files are denied.

## The Question

Can a repository `permissionRequest` hook auto-approve individual writes to `specs/**`, `poc/**`, and the four approved `.atom` runtime files while every individual request resolving outside that boundary remains gated, accepting partial artifact writes in mixed operations?

## Why This Is The Riskiest Unknown

The first experiment proved the user-visible prompt reduction but could not execute
its symlink escape case on Windows. A lexical path under `specs/` that resolves
through a junction outside the repository is the most expensive remaining safety
risk because an incorrect allow would write outside the approved boundary.

- Feasibility risk considered: Whether Windows junction targets can be resolved and rejected before approval.
- Performance risk considered: Negligible compared with correctness.
- Integration risk considered: Whether the hook consistently receives the resolved target for each file request.
- Ergonomics risk considered: Partial artifact writes are explicitly accepted by the developer.
- Why this one was chosen: It is the remaining route by which an apparently allowed path could escape the approved boundary.

## Success Criteria

| Observation | Means |
|---|---|
| Individual `specs/**`, `poc/**`, and four named runtime-file requests are allowed without prompts | Confirmed |
| Source, `.github/**`, `.atom/atom/**`, arbitrary `.atom` files, traversal, absolute external, and Windows junction escape requests all fall through and do not write | Confirmed |
| A mixed patch writes its artifact target but does not write its code target | Confirmed under the developer-approved partial-artifact behavior |
| Any individual request resolving outside the approved boundary is allowed or writes successfully | Refuted |

Minimum acceptable evidence:

- Number of runs: One complete matrix.
- Input size or rate: Every allowed and denied category, including one Windows junction escape.
- Environment notes that affect interpretation: Copilot CLI version, Go version, operating system, and hook payload tool name.
- Output values that must be pasted into the report: Hook decision and resulting file existence for every target.

## Scope

### Will Do

- Adapt the disposable Go spike to create a Windows directory junction for the escape case.
- Re-run the real Copilot CLI boundary matrix.
- Grade the mixed case as successful when the artifact exists and the code file does not.

### Will Not Do

- Implement production onboarding behavior.
- Auto-approve shell commands.
- Require patch-level atomicity.
- Test Copilot CLI versions or operating systems other than the current environment.

## Approach Sketch

- Reuse `poc/artifact-write-permissions/` as the disposable integration driver.
- Create a junction from `specs/outside-link` to a temporary directory outside the repository.
- Run controlled real Copilot CLI `apply_patch` requests.
- Print every hook decision and filesystem result.
- Run with `atom poc run artifact-write-permissions`.
- Stop immediately if an outside-boundary request is allowed.

Disposable shortcuts allowed:

- Hardcoded prompts and temporary paths.
- Windows-specific junction creation for the one unproven case.

Shortcuts not allowed because they would invalidate the result:

- Treating lexical `specs/` membership as sufficient without resolving the junction.
- Replaying synthetic payloads instead of invoking the real CLI.

## Open Questions For The Developer

None.

## Completeness Checklist

- [x] Problem is written in the developer's terms.
- [x] The Question is one falsifiable sentence.
- [x] The riskiest unknown is ranked against feasibility, performance, integration, and ergonomics.
- [x] Success criteria are measurable observations from a running Go program.
- [x] Scope includes explicit exclusions.
- [x] Approach fits in one disposable Go command.
- [x] Open questions are explicitly marked "None."
- [x] The acceptance threshold was supplied by the developer.
- [x] The POC can be run from the command line.
- [x] The report can reach Confirmed, Refuted, or Inconclusive without reinterpretation.
- [x] The spike path and slug are named.
- [x] No production implementation decisions are smuggled into the brief.
