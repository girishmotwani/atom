---
project: "artifact-write-permissions"
phase: "n/a"
author: "Copilot"
date: "2026-10-06"
status: "draft"
---

# POC Brief

## Problem

After Atom is onboarded, Copilot repeatedly asks for approval when writing design
specs, test specs, findings, decisions, POC files, and Atom runtime state. Those
prompts interrupt the workflow even though the developer has already accepted that
Atom owns those artifact locations. Removing prompts must not grant equivalent
permission to production code, tests, repository instructions, or Atom's own bundled
rules.

- Developer-visible outcome: Atom artifact writes proceed without repeated approval prompts.
- Current failure or limitation: Copilot's saved `write` approval applies to the whole repository, not selected paths.
- Non-negotiable constraint: Source code and instruction-policy writes must continue through normal approval.
- Evidence already known: Copilot CLI repository hooks can answer `permissionRequest`; saved repository permissions cannot persist path-specific write rules.

## The Question

Can a repository-level Copilot CLI `permissionRequest` hook auto-approve every file-tool write confined to `specs/**`, `poc/**`, or the four approved `.atom` runtime files while leaving source, instruction, escaped, and mixed-target writes unapproved?

## Why This Is The Riskiest Unknown

The feasibility risk is the shape and timing of the real permission payload. A path
filter that misunderstands one tool's arguments could approve a code write, while a
hook that runs after the prompt would not solve the problem. Those failures would be
expensive to discover after shipping the hook through `atom init`.

- Feasibility risk considered: Whether actual `create`, `edit`, and `apply_patch` requests expose every target before approval.
- Performance risk considered: Negligible for a local path check and lower risk than correctness.
- Integration risk considered: Whether `permissionRequest` short-circuits prompts in Copilot CLI 1.0.92.
- Ergonomics risk considered: How users opt out or inspect the rule; deferred until feasibility is proven.
- Why this one was chosen: An incomplete path check could silently authorize production-code changes.

## Success Criteria

| Observation | Means |
|---|---|
| Real Copilot CLI writes wholly under `specs/**` and `poc/**` complete without an approval prompt | Confirmed |
| Writes to `.atom/config.json`, `.atom/state.json`, `.atom/events.jsonl`, and `.atom/baseline.json` complete without an approval prompt | Confirmed |
| Writes to source, tests, `.github/**`, `.atom/atom/**`, absolute external paths, traversal paths, symlink escapes, or a patch mixing allowed and disallowed targets are not auto-approved | Confirmed |
| Any tool payload can hide a target path from the hook, or any disallowed target is auto-approved | Refuted |
| The CLI does not expose enough deterministic evidence to distinguish an auto-approval from a normal approval path | Inconclusive |

Minimum acceptable evidence:

- Number of runs: One complete case matrix, with every allow and fall-through case reported individually.
- Input size or rate: At least one request for each available file-writing tool and every boundary category above.
- Environment notes that affect interpretation: Copilot CLI version, operating system, hook event, tool names, and captured argument keys.
- Output values that must be pasted into the report: Case name, tool name, normalized targets, hook decision, prompt observed, file created or changed, and process exit result.

## Scope

### Will Do

- Build a disposable Go driver under `poc/artifact-write-permissions/`.
- Install an isolated repository hook and capture real Copilot CLI permission payloads.
- Exercise allowed, disallowed, escaped, symlinked, and mixed-target writes.
- Treat an unknown or malformed payload as fall-through, never allow.

### Will Not Do

- Modify `atom init`, production permission logic, or the open onboarding PR.
- Auto-approve shell commands; a shell command can write outside any declared target.
- Auto-approve `.atom/atom/**`, `.github/**`, source code, tests, build files, or arbitrary `.atom` paths.
- Prove behavior for older or future Copilot CLI payload formats.

## Approach Sketch

- Create `poc/artifact-write-permissions/` with one disposable Go command.
- Use an isolated temporary repository and Copilot configuration.
- Install a temporary `permissionRequest` hook that logs each payload and returns `allow` only for the approved boundary.
- Ask Copilot CLI to perform controlled writes, then inspect prompts, hook logs, exit results, and filesystem changes.
- Print one result line per case and an overall verdict.
- Run with `atom poc run artifact-write-permissions`.
- Stop immediately if a disallowed write is auto-approved.

Disposable shortcuts allowed:

- Hardcoded fixture paths and prompts.
- A temporary repository and temporary Copilot home.

Shortcuts not allowed because they would invalidate the result:

- Reconstructing tool payloads from documentation instead of capturing real requests.
- Testing only the path predicate without testing Copilot CLI hook integration.

## Open Questions For The Developer

None.

## Completeness Checklist

- [x] Problem is written in the developer's terms.
- [x] The Question is one falsifiable sentence.
- [x] The riskiest unknown is ranked against feasibility, performance, integration, and ergonomics.
- [x] Success criteria are measurable observations from a running Go program.
- [x] Scope includes explicit exclusions.
- [x] Approach fits in one disposable Go command or the question has been narrowed.
- [x] Open questions are listed or explicitly marked "None."
- [x] Any threshold in the question has a source or is marked as a developer assumption.
- [x] The POC can be run from the command line.
- [x] The report will be able to answer Confirmed, Refuted, or Inconclusive without reinterpretation.
- [x] The spike path and slug are named.
- [x] No production implementation decisions are smuggled into the brief.
