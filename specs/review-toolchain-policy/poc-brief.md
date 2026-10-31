---
project: "review-toolchain-policy"
phase: "n/a"
author: "Copilot"
date: "2026-10-30"
status: "approved"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# POC Brief

## Problem

Atom review gates currently invoke Go from the inherited environment. A locally approved Go 1.26.9+auto workaround resolved an observed dependency/compiler incompatibility, but does not make another developer's review reproducible. The developer selected a portable project-scoped policy as the next task and explicitly wants an exact Go patch version rather than a minimum accepting newer installations.

- Outcome: reviews can use a project-declared exact Go version without changing machine or user defaults.
- Constraint: preserve real code-failure gates; do not skip checks or claim unsupported compatibility.
- Existing evidence: inherited `go version` is `go1.26.9 windows/amd64`; `go env GOTOOLCHAIN` is `go1.26.9+auto`. This does not prove exact selection.
- No production configuration format or precedence has been approved.

## The Question

Can child-process-only selection of Go 1.26.9 keep build, vet, and test on that exact version across conflicting inherited selection settings and compatible module/workspace toolchain suggestions, reject higher language-version requirements without upgrading, and leave persistent defaults unchanged?

## Why This Is The Riskiest Unknown

The integration risk is that selecting a preferred toolchain is mistaken for pinning an exact one: module or workspace requirements may select something newer, or a child override may leak into persistent defaults. A configuration design is premature until the process boundary is proven.

- Feasibility: selecting an available exact executable without installing tools.
- Integration, chosen: actual Go selection under environment, module and workspace inputs.
- Performance: lower priority; this experiment is not a timing benchmark.
- Ergonomics: storage location, CLI flags and precedence follow evidence, not this brief.
- Deferred alternative: classifying tooling failures to continue model reviews is separate; no compiler-error string matching is proposed.

## Success Criteria

Use standard-library-only disposable Go fixtures and the already available go1.26.9 toolchain. A Python driver copies its environment for each child and explicitly requests `GOTOOLCHAIN=go1.26.9`, without `+auto`. Disable proxy/network retrieval for the fixture commands and do not install missing versions.

| Observation | Interpretation |
|---|---|
| Every compatible case reports exact `go1.26.9`; build, vet and test succeed, and the fixture program/test observes that runtime version | Supports Confirmed |
| A compatible fixture silently selects a different version | Refuted |
| A fixture requiring Go 1.27.0 fails without a newer toolchain being launched | Supports Confirmed; incompatible project remains a failure |
| User Go settings or parent environment change | Refuted |
| Exact toolchain cannot be selected locally, execution times out, or controls do not establish which executable ran | Inconclusive; stop, report, and re-gate |

Minimum evidence is one complete pass over five fixture cases, each under two parent selection settings (`local` and `go1.26.9+auto`): ten bounded cases, no retries. Compatible cases run version/build/vet/test and a fixture executable; incompatible cases capture version/build/vet/test results and verify no upgrade. The driver reports command argv, exit status, stdout, stderr, child selection, runtime observations, and unchanged-default checks. Record actual toolchain executable/provenance where observable; do not infer it from success alone.

## Scope

### Will Do

1. Plain module with Go 1.26.0 minimum.
2. Same minimum with a newer `toolchain go1.27.0` suggestion.
3. Module requiring Go 1.27.0.
4. Workspace containing a compatible module, compatible Go minimum and newer toolchain suggestion.
5. Workspace whose Go minimum requires 1.27.0.

Use explicit fixture-local `GOWORK` selection to avoid ambient workspaces contaminating the comparison. Observe inherited settings without exposing unrelated environment contents. Snapshot parent selection variables and persistent Go settings existence/hash before and after; never run `go env -w`. Preserve complete raw output in the POC report. Check fixture sources/manifests for unwanted modifications; disregard only explicitly created build outputs.

### Will Not Do

- Access private target, any private repository, real PR evidence, or its dependencies.
- Call models, MCP servers, or paid agents.
- Download Go toolchains, fetch dependencies, or modify user/machine settings.
- Implement production selection, choose a persistence schema, modify go.mod/go.work in a user's project, or automatically repair incompatibility.
- Prove dependency compatibility generally, classify arbitrary compiler diagnostics, or implement degraded reviews.
- Claim cross-platform proof from one Windows run; Linux/macOS coverage remains separate.
- Claim an exact Go version alone makes every build input reproducible, or pins external Makefile executables/gofmt.

## Approach Sketch

After approval, create `poc/review-toolchain-policy/spike.py` with small disposable Go module/workspace fixtures. Python is Atom's automation language; Go fixtures exercise the actual target toolchain rather than simulating selection.

Run from this worktree using `python poc\review-toolchain-policy\spike.py`. Each external command has a 60-second timeout; stop at the first unexpected selection, persistent change, or inconclusive execution. Upper bound: ten cases, at most six commands per case; no model calls or downloads. Archive source and verbatim observations; do not promote spike code to production.

## Baseline

Untouched source commit: `741969b7704696eaadbb0325f2fb5b2c9d026871`.

`atom check --no-race` exits 2 because Atom's own root is not a Go module:

```text
atom check: No go.mod found in <SESSION_FILES>\module-review-rules
```

The repository-standard Python replacement ran against the identical unchanged source before creating this discovery worktree:

```text
python -m pytest tests -q --cov=atom --cov-report=term-missing
TOTAL                        4185    220    95%
================= 1504 passed, 5 skipped in 335.42s (0:05:35) =================
```

This is an output excerpt, not the complete log. Full output remains in session PowerShell execution 367. Three skips are native symlink fixtures unavailable on this Windows setup; two predate module-rule delivery. No new implementation has been written.

## Open Questions For The Developer

Approve this local-only experiment and its Python-driver/Go-fixture scope before any spike is created or run. Missing-toolchain acquisition, production storage/precedence, and cross-platform validation require later decisions.

## Completeness Checklist

- [x] One falsifiable question, with exact-version intent explicitly selected by the developer.
- [x] Existing implementation and untouched-tree baseline inspected.
- [x] Integration risk ranked against feasibility, performance and ergonomics.
- [x] Concrete observations and Confirmed/Refuted/Inconclusive boundaries.
- [x] Ten bounded cases, timeouts, no retries and zero model calls.
- [x] Explicit exclusions, unchanged-default control and original-checkout isolation.
- [x] No production design or implementation included.
- [x] Developer explicitly approved this bounded spike in conversation before execution.

## Execution Approval And Branch

The developer explicitly approved the bounded ten-case local-only experiment and later approved starting v1.0 with it. The draft marker above is reconciled without changing the question, cases, success criteria, deadlines or no-download/no-model limits. Design and production implementation are not approved by this consent.

At the developer's request, execution moves to a clean `feat/atom-v1-toolchain` worktree based on latest public main `8b4dd51135c3836d5921414878182b16ff2fdefc`. The historical baseline evidence above remains labeled as historical. No POC inputs or scoring change with this documentation-only base update.
