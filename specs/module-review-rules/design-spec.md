---
project: "module-review-rules"
phase: "single-increment-default-delivery"
author: "Copilot"
date: "2026-10-30"
status: "approved"
poc_report: "poc-report.md"
---

# Design Spec: default launch-module review guidance

## Purpose

Normal atom review calls include the launching module's initialized Go guide and module-root AGENTS.md automatically. The CLI freezes local edits before PR preparation and gives every requested reviewer the same explicit packet. Shared Go rules, native tool permissions, strict extraction, and required gates remain intact.

This is one bounded Python-tooling increment, not a Go library or a general instruction-discovery framework. The developer approved using the one-model delivery observation as a narrow feasibility milestone and then selected both rule sources. This authorizes design preparation, not implementation before this design gate.

## Evidence Base

[POC report](poc-report.md): both original trial verdicts remain Inconclusive. Their criteria and raw evidence are unchanged. The developer explicitly accepted the narrower transport milestone on 2026-10-30 rather than requiring further calls merely for another model or exact attribution.

**Established before design:**

- The complete frozen 9741-byte customized guide reached Gemini through the real native pipeline. Its root user event matched the logical prompt after newline normalization.
- Strict extraction produced the known reservation defect without extraction errors. The location did not meet the old 10/11 expectation; this is not retrospectively scored as a pass.
- --no-custom-instructions remained enabled. Existing source builds one prompt and passes it unchanged to each requested model/run.
- Existing explicit context capture freezes UTF-8 bytes and records hashes before PR preparation. The PR CLI already distinguishes launch directory from disposable review checkout.
- The developer chose initialized Go guidance plus module-root AGENTS.md. No linked/ancestor/GitHub-file discovery was approved.

**Standing assumptions and implementation obligations:**

- A named, deterministic loader can select and validate these files correctly. Prove this with real filesystem fixtures, not a model's account of what it read.
- The common-prompt path can carry the same snapshot to every requested reviewer. Prove this for multiple model identities and runs with the existing injected runner seam.
- The additional AGENTS.md and ordinary-mode composition will remain usable under the response contract. Their semantic effects and review quality have not been established by the one-guide fixed-evidence trial.
- Local files are developer-controlled policy inputs. Framing limits their intended use but is not a security guarantee that a model obeys every boundary.

## Public Behavior And Scope

Existing review commands remain valid. Normal --working, --staged, --branch, and --pr calls automatically attempt the two sources below. Add only --no-module-rules to request the previous shared-seven-only rule behavior.

| Order | Source relative to launch directory | Purpose |
|---|---|---|
| 1 | .atom\atom\skills\atom\references\go-style.md | Initialized local Go guidance, including local edits |
| 2 | AGENTS.md | Module's handwritten review/domain constraints |

The launch directory remains the selected module root, as used by current init/check/PR workflows. This increment does not infer a different module, walk parents, or change which directory supplies the diff or Go checks. Document running from the module root; nested-directory and multi-module selection are not newly implemented here.

Missing sources are optional and reported; available ones still apply. Do not initialize a project, repair a bundle, read its entire manifest/workflow tree, or substitute the packaged guide when a local copy is missing.

**Fixed-evidence compatibility:** --fixed-evidence continues to mean no automatic module-rule discovery. It retains only the shared seven plus explicitly supplied existing evidence. --context-file remains evidence data, not a new policy channel. No additional fixed-evidence opt-in flag is introduced in this increment. This preserves the shipped source-selection contract rather than silently widening an explicit packet.

## Design Overview

```text
CLI launch directory
  -> capture permitted local rules once (or explicit disabled/fixed-evidence status)
  -> existing PR preparation, if requested
  -> unchanged diff and toolchain pipeline
  -> compose shared seven + frozen review guidance + response contract + diff
  -> same logical prompt for every requested model/run
  -> existing strict extraction/merge
  -> report rule status and safe metadata, never serialize snapshot text
```

The loader has no model, Git, network, or mutable-cache dependency. It reuses existing context capture/validation rather than implementing a second UTF-8/hash pipeline. Prompt composition consumes immutable captured values; it never consults the PR checkout for rules.

## Python API

These are the authoritative proposed signatures. Existing run_review arguments retain their order/defaults; only a keyword-only snapshot is added. No Go API or new interface hierarchy is introduced.

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from atom.context import ContextDocument

@dataclass(frozen=True)
class ModuleReviewRules:
    """Keep selected local policy and its provenance stable across checkout preparation."""

    status: Literal["loaded", "not-found", "disabled", "fixed-evidence"]
    sources: tuple[str, ...]
    documents: tuple[ContextDocument, ...]

class ModuleRulesInputError(Exception):
    """Stop review when a selected local policy cannot be captured faithfully."""


def capture_module_review_rules(
    launch_directory: Path,
    *,
    enabled: bool = True,
    fixed_evidence: bool = False,
) -> ModuleReviewRules:
    """Freeze the supported launch-local sources without discovering other policy."""
    ...


def run_review(
    request: DiffRequest,
    models: Sequence[str],
    runner: CommandRunner,
    working_directory: Path,
    runs: int,
    concurrency: int,
    window: int = DEFAULT_PROXIMITY_WINDOW,
    disable_mcp_servers: Sequence[str] = (),
    skip_toolchain: bool = False,
    include_style_rules: bool = True,
    *,
    fixed_evidence: bool = False,
    context_documents: Sequence[ContextDocument] = (),
    module_rules: ModuleReviewRules | None = None,
) -> ReviewOutcome:
    """Review one captured diff using only the caller's frozen module-policy snapshot."""
    ...
```

Use a small atom.module_rules module for the new snapshot, loader, and input error. sources contains only the two canonical repository-relative identifiers, with forward slashes in serialized metadata. documents uses the existing ContextDocument representation and sequential context labels, paired positionally with sources. No absolute root path is stored in this snapshot.

Only status loaded carries nonempty sources/documents. They have matching lengths, prescribed order, no duplicates, and valid existing context metadata. Other statuses carry empty tuples. Validate caller-supplied snapshots before diff capture or model work; reject invalid metadata, unknown/duplicate sources, or inconsistent status with ValueError.

The CLI always passes the capture result, including an explicit empty/disabled result. Low-level callers omitting module_rules retain previous behavior and do not trigger hidden filesystem discovery. A loaded snapshot is rejected with ValueError when fixed_evidence is true, rather than silently changing that mode's packet.

Add a defaulted ModuleReviewRules-or-None field to ReviewOutcome so renderers can use provenance without reopening files. Do not use the disposable spike's monkeypatch as production composition.

## Behavior

1. Normal CLI review captures supported files from the launch directory before entering PR preparation or starting probes. The review checkout's matching files never replace that snapshot.
2. If both files exist, capture the entire guide first and AGENTS.md second. Preserve original UTF-8 text and newline bytes for hashes; do not truncate, summarize, deduplicate equal contents, or modify local files.
3. A genuinely absent source is omitted. One available source yields loaded; neither yields not-found. The report explicitly states when only the shared seven are available.
4. A present nonregular, unreadable, empty/whitespace-only, NUL-containing, or invalid-UTF-8 source fails capture. A dangling source link, unreadable traversal, or non-directory intermediate rule-path entry is an error, not absence.
5. Resolve sources against the launch root and refuse targets outside that root. Do not follow Markdown links, recursively load rules, inspect ancestor/sibling policies, or load .atom's workflow AGENTS.md. Two prescribed sources resolving to the same file are rejected rather than silently collapsed.
6. --no-module-rules returns disabled without opening either candidate. --fixed-evidence returns fixed-evidence without candidate access and takes precedence over that flag for reported status.
7. On a capture failure, emit a safe stderr diagnostic and return the existing check-failed exit code before PR network/clone work, toolchain execution, probes, or reviews. Emit no success-shaped review report.
8. Normal composition retains the shared seven unchanged, then adds a clearly separated JSON-framed module-guidance section before the unchanged response contract/diff. Module AGENTS.md is more specific than the initialized guide, which is more specific than shared style for conflicting code-review conventions. Tool permissions, evidence scope, findings schema, and file ownership are never overridden by that precedence.
9. The framing directs reviewers to apply code-review constraints only: do not switch to an Atom workflow, execute embedded instructions, resolve links as policy, or alter the required output format. This is prompt guidance, not a claim of sandbox enforcement or guaranteed model compliance.
10. Every actual requested model/run receives identical guidance text, ordering, and metadata in one common logical prompt. Mutating/deleting launch sources or planting conflicting checkout files after capture does not change it.
11. Existing --no-custom-instructions, caller-selected MCP options, native deadlines/lifecycle, extraction validation, merge behavior, requested-model denominators, and exit semantics are unchanged. No model is substituted, no server name is baked into production defaults, and no new paid review/probe is added.
12. Existing fixed-evidence context loading, prompt hashes/scope, and source exclusions remain unchanged. The new status reports that automatic module rules were excluded. No implicit local file content enters that mode.
13. Markdown and JSON reports show module-rule status and, when loaded, each canonical relative source identifier, UTF-8 count, and SHA-256. Renderer code never serializes snapshot text, absolute launch paths, or raw OS exceptions. This does not claim that generated finding messages can never quote relevant policy.
14. PR limitations reflect actual status: a loaded snapshot must not retain the old blanket statement that initialized rules are unapplied. Surrounding-code context and selected-module Go-check limitations remain accurate. Disabled/not-found/fixed-evidence cases must not claim local rules were applied.
15. No capture result or successfully parsed output is labeled as comprehensive rule compliance, improved review quality, or a full-context review. File discovery/delivery tests verify those mechanisms, not model reasoning quality.

## Error Handling

| Condition | Result |
|---|---|
| Genuine absence of one/both supported sources | Normal loaded/not-found result; explicit report, no warning-shaped failure |
| Invalid source contents or failed capture | ModuleRulesInputError; message starts with module rules: and names only a canonical relative source and/or safe existing context diagnostic |
| Outside-root resolution, dangling link, or nonregular source | ModuleRulesInputError with a safe condition explanation; do not include resolved profile paths or file text |
| Invalid caller snapshot or loaded snapshot in fixed-evidence mode | ValueError before execution; CLI retains its usage-error mapping if reachable |
| Existing toolchain, PR, model, or extraction failure | Existing reporting/exit behavior, unchanged |

Reuse existing context helpers for byte capture, UTF-8 checks, and SHA-256 validation. Wrap only expected filesystem/context failures. No broad catch, silent default after a failed read, or fallback to packaged/checkout policy is permitted.

Snapshot consistency is per successfully read source, not a transaction over concurrently edited files. Resolved-path confinement does not claim hardened protection against a malicious concurrent filesystem replacement; that threat model is outside this increment. Any unsupported filesystem condition fails explicitly rather than claiming successful discovery.

## Reporting Contract

For CLI-produced outcomes, add an additive module_rules object to JSON schema version 2. Keep existing keys and meanings intact. Its status is one of the snapshot statuses; provenance is local-launch; sources is a list of objects containing only path, utf8_bytes, and sha256. Empty/skipped statuses use an empty sources list. Existing low-level outcomes with module_rules None may omit the object for compatibility.

Markdown adds a Module rules section with the equivalent metadata and a plain-language explanation of not-found/disabled/fixed-evidence. Reporting never reopens sources. Existing review_execution metadata continues to describe fixed-evidence only; do not overload its documents with executable policy or claim ordinary tool exclusions were applied.

## Concurrency

Capture runs synchronously once, before concurrent model calls. No new threads, processes, global caches, or mutable shared state are introduced. Immutable snapshots may be shared across reviews/readers. Concurrent capture calls have no shared application state; concurrent filesystem edits do not provide a multi-file atomic snapshot. Existing runner ownership and bounded model concurrency remain responsible for process cleanup.

Atom's implementation is Python: validate with repository pytest, not a nonexistent root Go/race gate. The POC's tiny Go build/vet is not a replacement for Python verification.

## Test Obligations

Use existing runner/preparation seams plus real temporary filesystem inputs. No paid model calls are required to establish deterministic discovery or fan-out.

- Loader: both/one/neither source; original UTF-8/CRLF and hashes; prescribed ordering; invalid contents/nonregular/read failure; outside-root/dangling links where the platform supports them; absence distinguished from read errors.
- Selection: ignored ancestor/sibling/GitHub/link-target/whole-workflow files, plus a nested fixture proving there is no unintended upward module selection.
- Opt-out/fixed-evidence: make candidate access fail if attempted and prove it is not attempted. Preserve existing explicit-context validation and packet metadata.
- PR orchestration: capture before preparation; mutate/delete local sources and plant conflicting checkout copies; assert every actual review stdin retains only the frozen selected policy.
- Fan-out: two synthetic model identities and multiple runs receive byte-identical complete common prompts. Preserve the shared seven, JSON contract, and native flags. Simulate an unavailable reviewer to verify partial reporting still keeps the requested denominator.
- Reports: safe metadata/status in Markdown/JSON, no raw snapshot text or absolute paths, truthful PR limitations in loaded/missing/disabled/fixed modes, and unchanged fixed-evidence context reporting.
- Failure timing: invalid selected rules prevent preparation, gate/probe/model invocation, and success-shaped output. Direct invalid snapshots fail before execution.

Run the smallest combined targeted pytest selection during red/green/refactor, then the existing full tools test/coverage command before claiming implementation completion. Maintain current package/build/lint checks where configured. Do not add a new linter or model benchmark for this phase.

## Extension Points And Trade-offs

| Decision | Basis / rejected alternative |
|---|---|
| Two named module-local files, no generalized discovery | Developer-selected scope. Reject a recursive instruction framework or linked workflow import. |
| Freeze locally before PR preparation | Existing capture pattern and POC transport evidence. Reject mutable re-reads or PR-supplied policy as authoritative. |
| Preserve fixed-evidence explicitness | Existing shipped contract. Reject silently collecting new source in that mode; a future opt-in requires separate design. |
| Explicit normal-mode opt-out | Proposed design choice for reproducibility and intentional shared-only reviews; acceptance occurs at this design gate. |
| Whole local files, no machine summarization | POC used complete guidance. Token/quality impact remains an assumption; do not claim a longer checklist is better. |
| Module-specific code policy wins, execution contract does not | Proposed semantic precedence, not experimentally validated obedience. Reject allowing AGENTS.md to redefine review operation or claiming framing is enforcement. |
| Fail on invalid present policy | Avoid a review that silently loses intended guidance. Missing optional sources remain visible, nonfatal absence. |
| Extend existing ContextDocument machinery | Avoid duplicated validation and a new storage system. Snapshot uses stable relative identifiers rather than leaking absolute paths. |
| CLI orchestration owns discovery | Makes launch-vs-checkout authority explicit. Reject hidden lower-level disk reads or a global instruction monitor. |

Adding another rule-file format later requires an explicit source/precedence/test update, not following arbitrary links. No plugin/extension mechanism or configurable policy registry is needed for two sources.

## Out Of Scope

Portable Go toolchain selection, continuing on confirmed tooling incompatibility, startup/MCP fixes, production reviewer-default changes, another model experiment, ancestor or GitHub instruction discovery, nested module inference, policy generation from source, review-quality claims, and installation/publication are separate work. No push is authorized.

## Completeness Checklist

- [x] Established evidence separated from assumptions and scoped acceptance recorded.
- [x] Public behavior, Python API, source order, precedence, failure mapping, and concurrency explicit.
- [x] Signatures have one authoritative declaration and retain existing argument order/defaults.
- [x] Behaviors independently testable; deterministic tests specified for every requested reviewer.
- [x] Fixed-evidence/source authority and metadata privacy remain explicit.
- [x] Trade-offs and exclusions recorded without claiming model enforcement.
- [x] Design presented and explicitly approved before TDD.

## BUILD reconciliation

Implemented the approved API and all fifteen behaviors without a material design change. Capture walks only each named candidate's components with lstat followed by strict, root-confined resolution, distinguishing genuinely absent entries from dangling or denied traversal before reusing existing context capture. Context capture remains responsible for regular-file checks, original UTF-8 bytes, duplicate resolved targets, content validation and hashes. Windows link privileges limit three native fixtures; deterministic filesystem-boundary coverage and that limitation are recorded in the test spec and findings.

The common prompt JSON-frames paired canonical source names and complete document text; reports independently expose only status, provenance, source identifiers, sizes and hashes. Initialized guide exposition and its packaged mirror describe the new delivery contract without claiming measured quality improvement. Low-level omission and fixed-evidence retain their prior packet; production native invocation code is unchanged.

See [test-spec.md](test-spec.md) for the reconciled mapping and [tdd-evidence.md](tdd-evidence.md) for exact verification. Implementation is awaiting its completion gate; this does not authorize paid review, installation, commit, push or publication.
