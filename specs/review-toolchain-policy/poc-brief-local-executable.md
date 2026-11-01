---
project: "review-toolchain-policy"
phase: "n/a"
author: "Copilot"
date: "2026-10-30"
status: "approved"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# Follow-Up POC Brief: Direct Local Executable

## Original Result

The original trial is Inconclusive: GOSUMDB=off blocked checksum verification before any matrix case completed. Preserve its brief, driver and report unchanged. This follow-up is a separate proposal, not an automatic retry.

## The Question

Can direct invocation of an existing local Go 1.26.9 executable with child-only GOTOOLCHAIN=local keep build, vet and test on that exact version across inherited selection settings and module/workspace suggestions, reject higher language minimums without upgrading, and leave persistent defaults unchanged?

## Selection And Offline Boundary

Locate the candidate using existing configured/default Go cache or SDK locations by read-only filesystem inspection, without invoking a downloader. Record its executable hash and require the first real version probe to report go1.26.9. A path or filename is not version proof. If no complete candidate exists, stop as Inconclusive without downloading, installing, searching unrelated directories or repairing the cache.

Run the candidate directly, not the generic Go launcher. Use child-only GOTOOLCHAIN=local; remove any inherited child GOROOT override so the candidate uses its own distribution, then verify actual GOROOT/GOVERSION and executable identity with the environment probe. Keep the current user checksum policy unchanged; GOPROXY=off prevents dependency/toolchain retrieval, and no new checksum/trust bypass is introduced. Use only generated standard-library Go fixtures.

## Cases And Scoring

Use the same five fixture categories under each of two copied-parent settings (`local`, `go1.26.9+auto`): plain module; module with newer suggestion; module with higher minimum; compatible workspace with newer suggestion; workspace with higher minimum. Ten cases, at most six commands per case: version, environment, build, vet, test, and the built program for compatible cases.

Confirmed requires all compatible cases to succeed with exact version/provenance and compiled runtime assertions, all higher-minimum fixtures to reject without upgrade, and unchanged parent/settings/input snapshots. Different version, accepted incompatible minimum or persistent/source mutation refutes the bounded route. Missing candidate, failed provenance, timeouts or unrelated failures are Inconclusive. Stop immediately on unexpected output; no retries.

## Budget And Scope

One new run; ten cases maximum; 60 seconds per Go command through the existing owned-process runner, with the same separate bounded wrapper-cleanup guard. Zero model calls, downloads, dependency retrieval, private-target access or persistent setting changes. Python remains the disposable driver language. Retain the original driver; write a separately named follow-up driver only after approval.

A successful local direct-executable route would support only that route on the observed Windows environment. It would not prove generic launcher bootstrap, cross-platform discovery, portable project configuration, Makefile/gofmt selection or real dependency compatibility.

## Gate

Approval authorizes building/running this follow-up experiment only. No selection design, production implementation, model calls, installation, commit, push or release is included.

## Approval

The developer explicitly approved this follow-up in conversation on 2026-10-30 after the original failure, benefit and proposed change were explained. The question, ten-case matrix, deadlines, stop conditions and no-download/no-model boundaries above remain unchanged.
