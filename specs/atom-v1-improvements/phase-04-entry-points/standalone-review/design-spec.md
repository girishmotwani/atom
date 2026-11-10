---
project: "atom-v1-improvements"
phase: "phase-04-entry-points"
author: "Copilot"
date: "2026-11-09"
status: "implemented; accepted"
poc_report: "remaining-cases-report.md"
---

# Design Spec - Standalone Review Entry Guidance

## Purpose

Make the existing `/atom:review` entry useful for one local review without adopting
Atom's phase lifecycle. Ship accurate guidance, routing, examples and packaged
references around the proven runtime. This is the standalone-review slice of
Phase 04, not completion of the whole phase or a new Python/Go review engine.

## Evidence Base

Approved [remaining-case report](remaining-cases-report.md), combined with its
explicitly reused working-tree observation, establishes the local mechanics:
working/staged/branch selection; normal required Go checks; report rendering;
required-gate failure before reviewer probes; honest missing-module evidence;
source/Git-state preservation; no Atom/phase setup required.

### Established

- Four continuation cases completed once with zero real model calls. The earlier
  complete working case was reused after frozen installed-wheel validation.
- The CLI requires an explicit diff source, supports `--branch REF` and repeated
  `--model NAME`, and emits Markdown or `--json` on stdout without a phase path.
- Build/vet/test/race examine the working module; formatting examines selected
  surviving changed Go snapshots. Missing root go.mod skips tooling rather than
  creating a module; an exit-0 review report does not establish a verified build.
- Canonical CLI code confirms explicit model flags or built-in defaults, not
  general model-role resolution from `.atom/config.json`. Existing configuration
  may still supply review Go-version policy; that independent feature remains.
- Source inspection confirms one full-diff prompt per model run, runtime severity
  labels critical/high/medium/low, and proximity grouping that retains messages
  and disagreement. It does not provide semantic defect deduplication or an
  automatic guarantee that every model received surrounding whole-file context.

### Assumptions And Limits

The synthetic trial did not prove a live agent waits for approval, respects
refusal or stops after review. These are instructions to strengthen, not new
runtime enforcement. Whether real models provide useful independent reviews,
and whether future installed guidance changes agent behavior, remains unproven.
The installed-user setup trial remains paused and Inconclusive.

## Design Overview

Reuse `/atom:review` and `atom review`. Place the shared bounded entry contract in
`skills\atom\references\standalone-review.md`. The review skill orchestrates that
contract; start routes an explicit review-only request there before lifecycle
inspection. README/workflow explain direct entry and link to the same guidance.
No new slash command, router, configuration key, CLI option or report schema.

```text
explicit local review intent
  -> review skill + shared entry contract
  -> read-only scope / concrete proposal
  -> developer approval
  -> existing atom review
  -> honest report + approved audit artifacts
  -> stop (standalone) / existing phase review gate (phase context)
```

## Public Surface

These are existing CLI shapes, not new APIs. MODEL_A and MODEL_B stand for actual
approved available identifiers, not literal provider names or hard-coded versions.
Examples illustrate alternatives; they are not instructions to execute all three.

```text
atom review --working --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
atom review --staged --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
atom review --branch main --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
```

`--json` remains an optional output selector. No exported Go/Python signatures
are introduced. Unsupported `--base` and `--models` examples are removed from
shipped review guidance, not added as compatibility aliases.

## Components And Responsibilities

| Surface | Responsibility |
| --- | --- |
| `skills\atom\references\standalone-review.md` | Shared local review-only scope, consent, evidence and stopping contract |
| `skills\review\SKILL.md` | Apply that contract, retain review discipline and distinguish phase continuation |
| `com.github.copilot\commands\start.md` | Route explicit review-only intent before phase/status discovery |
| `README.md`, `docs\workflow.md` | Explain entry, report location and limits using supported examples |
| `tools\atom\assets\skills\...` counterparts | Deliver byte-identical skill/reference content through onboarding |
| Existing Python tests | Validate CLI contracts, plugin names, packaged parity and actual bundle delivery |

## Behaviour

1. An explicit local review-only request defaults to standalone mode even when
   `.atom` happens to exist. Existing approved phase context may select phase
   review; mere file presence does not adopt a lifecycle. Clarify only genuinely
   missing intent, one question at a time.
2. Start routes clear review-only intent directly to `/atom:review` before asking
   for `atom status`, registered phases or project artifacts. It does not call
   init/discover/build or route back to itself. Other existing routing remains.
3. Read-only inspection establishes the local Git target and exactly one desired
   diff source. Use the existing bootstrap command-interface checks if needed;
   require no separate Atom source checkout or package-internals inspection.
   Missing tools get a proposal, not automatic installation/PATH changes. Missing
   root go.mod is disclosed, not treated as a reason to run init.
4. Before reviewer availability probes or review submissions, propose the exact
   selector/ref, concrete model identifiers, runs/concurrency, evidence scope,
   expected call budget including probes, and output/file effects. Recommend
   one run per model and concurrency 1 as a bounded starting choice, not a new
   CLI default. Obtain approval; earlier unrelated phase/setup approval is not
   review-spend approval. State dependency/toolchain side effects honestly;
   ordinary review is not promised to be offline or cache-write-free.
5. A declined proposal launches no reviewers and creates no audit/report bundle.
   Revised scope, additional models/runs, tool installation, gate bypass, fixes
   or publishing need their own approval. Never silently retry with more models,
   switch Go versions or suppress a failed gate to obtain a report.
6. Use supported flags and explicit model choices. State that CLI defaults exist
   when --model is omitted, but the skill's approved proposal must name the actual
   choices. The skill requires at least two different reviewer models, neither
   the authoring model; this is a workflow policy, not CLI enforcement. Unknown
   authorship or identities are resolved rather than assuming independence.
7. Keep normal review gates enabled. Required failures are reported and stop the
   bounded action; absent optional analyzers and missing-module tooling exclude
   nothing. Missing go.mod may yield a report only with the limitation disclosed
   in the approved proposal/result. Explain selected-snapshot formatting versus
   working-tree module checks. Preserve existing explicit Go-selection and other
   advanced options without expanding this entry into those workflows.
8. The runtime still writes its report to stdout. The skill proposes an approved
   standalone bundle, for example `specs\reviews\<slug>\review.md`, `findings.md`
   and `decisions.md`, rather than requiring a registered project/phase directory.
   Empty audit artifacts explicitly say No findings and No deviations. Use the
   dedicated writer for those allowed paths with first-use permission; refuse
   overwrite conflicts or writer errors without alternate writers. Do not create
   the bundle before consent. If audit-file consent is withheld, explain the
   skill's persistence requirement rather than silently waive it; direct CLI
   stdout behavior remains available and unchanged.
9. Report failures, unavailable/silent/unparsed runs, partial participation and
   skipped evidence as such. Zero usable responses is not a clean review. Do not
   claim the skill's multi-model obligation was fulfilled if fewer than two
   qualifying models answered. CLI exit status and participation metadata remain
   unchanged; no success-shaped replacement report or automatic model retry.
10. Describe the actual report: critical/high/medium/low, file/line locations,
    participation and retained messages/disagreement. Do not promise semantic
    deduplication, per-file model invocations, suggested fixes for every finding,
    automatic whole-file context or automatic design-spec delivery. Inspect
    surrounding code during triage as needed and name context limits honestly.
11. Standalone review ends after the report and disposition of findings, with no
    automatic fix, phase advancement, ship command, commit or push. Proposed
    fixes are separate approved work. Phase review retains its established
    report path, triage and next-beat recommendation under existing gates; no
    new lifecycle checks are added to the CLI or silently removed from phases.
12. Ship canonical and packaged review skill/reference changes together. Link
    the shared contract from the entry/docs and preserve plugin/skill names.
    Verify content parity and actual installation into a fresh onboarding bundle,
    not just that a file exists in the checkout. Do not replace the frozen user
    preview, release or change global configuration in this implementation.

## Error Handling

| Condition | Required guidance; existing runtime behavior is not replaced |
| --- | --- |
| Missing/ambiguous diff source | Ask for the missing choice; do not assume working/branch or submit paid work |
| Missing CLI or writer | Bootstrap checks, then approved install proposal if needed; no source-path workaround |
| Missing root go.mod | Explain skipped tooling; no fabricated clean gates or automatic module creation |
| Required gate failure | Surface actual stderr/result; no automatic fix, skip flag or version switch |
| No usable or insufficient independent responses | State actual participation and limitations; no clean/complete multi-model claim |
| Artifact collision/refusal/failure | Stop and expose the issue; do not overwrite or use a generic editor |
| Proposal declined | No reviewer probes, report writes or setup; no assumed consent from prior work |

Exact current CLI error strings/exit codes are not redefined. Existing handling
for selected-toolchain comparisons, PR preparation and fixed evidence is retained,
not extended or generalized from this local fixture evidence.

## Concurrency

No new threads, goroutines, locks or shared runtime state. Existing review
concurrency is an explicit approved parameter, not a new scheduling design.
Concurrent edits to the target or output bundle are not made safe by guidance;
report scope drift/conflicts rather than promise atomic snapshot isolation.
Real race evidence covers only fixture paths actually executed, not universal
application safety or concurrency guarantees of an arbitrary future review.

## Validation And Behaviour Coverage

This changes shipped Markdown and packaging contracts, not review runtime logic.
After approval, write `test-spec.md` mapping all twelve behaviours to factual
review, structural tests and existing relevant validation. Do not fabricate Go
runtime RED/GREEN or atom-check output for this Python/documentation repository.

- Inspect examples against the actual parser and factual claims against the CLI,
  review/report/merge code and approved POC evidence. Never execute real models
  merely to check a command example.
- Extend the existing distribution/onboarding pattern to verify canonical/package
  bytes and actual installed standalone-reference/review-skill contents. Use a
  temporary test fixture, not the frozen user preview or live repositories.
- Run a focused combined Python selection covering review CLI, report rendering,
  onboarding, artifact integration and plugin namespace. Capture actual output.
  Add the existing merge tests if modified prose makes a merge-specific claim.
- Check changed-document relative links from both canonical and packaged locations
  and verify no unsupported example flags remain in shipped entry guidance.
- Preserve the setup implementation and existing phase-review sections; use its
  relevant regression checks rather than reopening the paused live setup trial.

Text assertions and packaging tests establish documentation contracts, not
whether a real model follows consent, refusal or stopping instructions. A live
interaction trial, if wanted, remains a separate decision and spend gate.

## Extension Points

Future entry workflows may reuse the shared scope/consent/evidence structure
only after validating their own boundaries. This spec adds neither a generic
workflow engine nor new diagnosis or PR-review support. Advanced runtime feature
changes need separate proof/spec scope rather than being slipped into guidance.

## Trade-offs Considered

| Option | Chosen | Reason |
| --- | --- | --- |
| Reuse existing review CLI and document its actual boundaries | Yes | Mechanics proved; no new runtime API is needed |
| Shared reference plus small review/start adapters | Yes | One bounded contract, no copied routers or invocation loop |
| Small explicitly approved standalone audit bundle | Yes, proposed | Satisfies required findings/decisions without phase registration; direct CLI stdout remains unchanged |
| Force init/phase setup for every review | No | Contradicts observed no-state entry and Phase 04 outcome |
| Add alias flags or model-role resolver | No | Unnecessary behavior changes; correct examples instead |
| Treat all skipped evidence as a pass or block all missing-module reviews | No | Both misdescribe existing behavior; disclose and scope instead |
| Live reviewers before any guidance edit | No, not in this scope | Model quality/control is unproven but no extra paid trial was authorized |

## Out Of Scope

Runtime/API/schema changes; new Go/Python review engine; source fixes selected by
review; new skills/command names; PR/remote operations; tool installation; updating
the installed user preview; releasing, committing or publishing; setup-trial
retries; closing Phase 04 or claiming live-agent enforcement.

## Completeness And Gate

- [x] Established evidence separated from assumptions and unproven interactions.
- [x] Existing public command shapes consistent; no new exported symbols.
- [x] Twelve numbered obligations map to factual/packaging validation.
- [x] Failure, concurrency, extension and rejected alternatives specified.
- [x] Report locations and required standalone audit artifacts explicit.
- [x] Evidence/permission limits and phase compatibility retained.
- [x] Developer selected "Approve this spec and implement it" before shipped guidance/test edits.

## Implementation Reconciliation

Implemented the approved documentation/distribution scope without a runtime API
change or material spec deviation. See [implementation report](implementation-report.md)
for the twelve-obligation map and exact focused validation output. Source assets
are ready for review; the frozen installed preview and incomplete live setup
trial were not changed. Implementation acceptance and any reviewer spend remain
the developer's next decision, not an automatic continuation.
