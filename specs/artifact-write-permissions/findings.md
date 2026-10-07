---
project: "artifact-write-permissions"
phase: "n/a"
date: "2026-10-06"
---

# Findings Log

## Findings

| # | Finding | Severity | Where | Why not fixed now | Suggested action |
|---|---|---|---|---|---|
| 1 | Saved repository `write` approval has no path field and therefore approves writes across the repository. | High | Copilot CLI `permissions-config.json` documentation | The POC is evaluating a narrower hook-based alternative. | Do not have `atom init` persist a repository-wide `write` approval. |
| 2 | Shell permission is command-based rather than destination-based, so an approved shell can write outside Atom artifact directories. | High | `copilot help permissions` | Shell auto-approval is outside the accepted boundary. | Leave shell commands under normal permission handling. |
| 3 | Repository hooks are loaded when Copilot CLI starts, so a hook installed by `atom init` cannot affect the already-running session. | Medium | Copilot CLI hooks documentation | This is lifecycle behavior, not a POC defect. | Document that artifact auto-approval begins in the next session. |
| 4 | Copilot decomposes one mixed `apply_patch` operation into per-file `edit` permission requests and applies an allowed spec file before the later code-file request is denied. | High | `poc/artifact-write-permissions` case `deny-mixed-spec-and-code` | This refutes the proposed per-file auto-approval boundary; it cannot be fixed without changing the approach. | Return to discovery and evaluate an atomic artifact-writing tool rather than per-file permission approval. |
| 5 | The active model/toolset exposes `apply_patch` as permission tool `edit`; documented `create` was unavailable in the controlled run. | Medium | Initial POC capture runs | The POC uses the available tool and records the actual payload. | Treat unknown tool names and payloads as fall-through in any future approach. |
| 6 | Windows did not permit creating the symlink fixture in the current environment. | Low | `poc/artifact-write-permissions` symlink setup | The mixed-patch result already refutes the question independently. | Re-run the symlink case in an environment with symlink privileges only if a later design depends on per-path approval. |
| 7 | A Windows directory junction under `specs/` was not resolved by the spike's normal path canonicalization; Copilot auto-approved `specs/outside-link/escaped.md` and created the file outside the repository. | High | Experiment 2 case `deny-symlink-escape` | This refutes the revised path-based approach in the current Windows environment. | Do not ship repository path auto-approval without a separately proven Windows reparse-point boundary. |

## Ambiguities Resolved

| Ambiguity | Interpretation chosen | Why | Confidence |
|---|---|---|---|
| Does “all Atom artifacts” include `.atom/atom/**`? | No; allow only the four named runtime files. | `.atom/atom/**` contains the instructions and permission policy itself. | High |
| Does POC code count as an Atom artifact? | Yes; allow `poc/**`. | The developer explicitly selected all Atom artifacts after being told `poc/` contains throwaway Go code. | High |
