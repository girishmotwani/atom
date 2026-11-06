---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
author: "Copilot"
date: "2026-11-03"
status: "executed-confirmed"
---

# POC Brief: Review-Snapshot Input Identity

## Problem

Continuation currently hashes every regular file in the module before selected checks and again after control checks. This can spend time reading unrelated files and blocks on unrelated symlinks or unreadable files. The developer chose to limit the identity contract to the selected review snapshot, accepting that changes outside that snapshot are not detected by this guard.

- Developer-visible outcome: avoid walking and hashing the whole module for degraded review continuation.
- Current limitation: `_fingerprint_source_tree` hashes every regular file and rejects unrelated special or unreadable entries.
- Non-negotiable constraint: a changed file within the selected review snapshot must still block continuation; do not describe the narrowed guard as proving the entire module tree is unchanged.
- Evidence already known: the confirmed compiled-timeout POC blocked its `changed-source` fixture using full-source identity. It did not evaluate a review-snapshot-only scope.

## The Question

Can identity checks limited to the exact changed-file paths captured for a review detect changes to those paths across selected and control checks without traversing or hashing unrelated module files?

## Why This Is The Riskiest Unknown

The main risk is whether a bounded identity check can preserve detection of review-snapshot mutations while actually avoiding unrelated tree traversal. This changes what the guard promises: unrelated module source changes may no longer be noticed, even though build, vet, and test remain module-wide. That limitation was explicitly accepted by the developer. The POC will not claim full module-input identity or benchmark production-sized trees.

- Feasibility risk considered: whether a path/content fingerprint can be scoped to the review's captured changed-file set and detect those files' mutations.
- Performance risk considered: whether the scoped method reads only the selected inputs; no production latency threshold is established.
- Integration risk considered: the POC does not integrate Git diff capture or Python gate orchestration; this is lower priority than settling the scope contract first.
- Ergonomics risk considered: internal helper shape is a later design choice.
- Why this one was chosen: implementing before proving the exact scope could either retain the costly whole-tree scan or silently remove meaningful mutation detection.

## Success Criteria

| Observation | Means |
|---|---|
| Mutating a selected review-snapshot file changes its identity result and is reported as changed | Confirmed for selected-file mutation detection |
| Adding/changing an unrelated module file does not change the scoped identity result, and the POC records that the file was not opened/read | Confirmed that unrelated inputs are outside this guard |
| The scoped method reads any unrelated file, misses a selected-file mutation, or cannot distinguish the two cases | Refuted |
| Any required case is not executed or the treatment-use log cannot establish which files were read | Inconclusive |

Minimum acceptable evidence:

- Number of runs: one deterministic run covering both mutation cases.
- Input size or rate: one selected source file plus 1,000 unrelated fixture files; count files and bytes actually read rather than claiming a general speedup.
- Environment notes that affect interpretation: Windows; standard-library-only Go POC; temporary fixture tree.
- Output values: identity before/after, detected mutation path, number of files and bytes read by the scoped arm, and proof the unrelated file was untouched.

## Scope

### Will Do

- Create one disposable Go command under `poc/review-tooling-continuation/spike-review-snapshot-fingerprint/`.
- Build a temporary fixture with one selected path and 1,000 unrelated files.
- Compute a content identity for only the selected path, mutate it and then an unrelated path in separate checks, and print the detected results plus files/bytes read.
- Instrument file reads within the POC so the result proves the unrelated files were not opened, rather than relying on the algorithm's description.

### Will Not Do

- Modify production code, tests, or the approved design spec.
- Claim module-wide selected/control input equivalence; the developer accepted that changes outside the selected review snapshot are not detected by this guard.
- Benchmark large real repositories, prove Go build/vet/test ignore unrelated files, or establish cross-platform performance.
- Change POC fixtures, run models, install/download tools, or publish/commit anything.

## Approach And Proposed Spend

One small Go program and one execution (Go vet/build/run) using only standard library and temporary files. Expected spend: a few minutes, no model calls, no network, no package installation. The source and outputs are disposable except for the archived POC and report. Any change to the selected-path contract or measurement requires another gate.

## Open Questions For The Developer

None on scope: the developer selected review-snapshot-only identity and accepted that other module files may change undetected.

## Completeness Checklist

- [x] Problem is written in the developer's terms.
- [x] The Question is one falsifiable sentence.
- [x] Riskiest unknown is ranked against feasibility, performance, integration, and ergonomics.
- [x] Success criteria are measurable observations from a running Go program.
- [x] Scope includes explicit exclusions.
- [x] Approach fits in one disposable Go command.
- [x] Open questions are listed or explicitly marked "None."
- [x] No unsupported performance threshold is asserted.
- [x] The POC can be run from the command line.
- [x] The report can yield Confirmed, Refuted, or Inconclusive without reinterpretation.
- [x] Spike path and slug are named.
- [x] No production implementation decisions are smuggled into the brief.


On 2026-11-03 the developer approved exactly the single POC described here. This approval authorizes the scoped spike only, not production edits or further experiments.


## Executed Result

The approved spike confirmed selected-path mutation detection without opening unrelated files in the bounded fixture. See [the report](poc-report-review-snapshot-fingerprint.md). This does not establish full module-input identity or production integration.
