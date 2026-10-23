---
project: "review-format-scope"
phase: "n/a"
date: "2026-10-22"
status: "approved"
---

# POC Brief: changed-file formatting for review

## Problem and agreed scope

A review of changed files must not be blocked by formatting defects in untouched files. The developer explicitly selected **formatting only** for the first correction: build, vet, test, race and advisory check behavior stay unchanged. Standalone `atom check` remains a full-module check. Review findings remain tied to changed files, but reading unchanged callers and surrounding code for context is allowed.

The current implementation does the opposite ordering for validation: `run_review` collects full-module toolchain evidence before capturing the diff. The standard FormatGate executes `gofmt -l .`. Finding extraction already uses the diff's file allow-list. The former whole-module baseline probe was superseded before execution; it is not part of this work.

This proof uses only a disposable synthetic repository. It neither reviews the selected ADO PR nor accesses or changes its code.

## The Question

Can one selected working, staged or branch diff supply only its changed, surviving Go-file snapshots to a read-only formatting check, so untouched formatting defects do not block review while genuine formatting failures in the selected files still do?

## Why prove this first

The risk is checking the wrong scope or bytes: a clean working copy does not prove staged content is clean, and a dirty working copy must not contaminate a branch snapshot. Deleted and renamed paths and Git path quoting can also lead to false failures or silently missing files. These are correctness uncertainties, not a reason to skip all checks.

Performance is bounded locally; no model-quality or external integration claim is attempted. Production interfaces and the precise implementation are deferred until this experiment reports what worked. No PR URL, rule-loader or richer-comment architecture is selected.

## Preregistered fixture cases

| Fixture observation | Required result |
|---|---|
| A clean changed Go file sits beside an untouched badly formatted Go file, exercised for working, staged and branch modes. | Only the selected changed content is checked; scoped formatting passes in all three modes. |
| The selected changed Go content is badly formatted. | Scoped formatting fails and attributes the result to that changed path. |
| A staged file is badly formatted but its unstaged working copy is clean; then the inverse. | Each staged result follows the index snapshot, not the working copy. |
| A committed branch snapshot differs from a later unstaged edit. | Branch formatting follows the pinned committed source, not the later edit. |
| The selected change adds, renames without content edits, or deletes a Go file. | Added content and rename destinations are included; deleted content is explicitly inapplicable rather than read from a missing path. |
| A changed path contains spaces or non-ASCII characters, including a module-directory prefix when Git is invoked from the module. | The exact path is selected and its bytes are checked without shell splitting or quoted-path confusion. |
| A selected diff has no surviving Go files. | No formatter process runs; coverage is explicitly not applicable, not a claim that the module is formatted. |
| A required Git read fails or selected Go content has a formatter syntax error. | The error remains visible and cannot become an empty scope or a pass. |
| The existing standalone FormatGate checks the fixture module containing the untouched defect. | It still fails: standalone module-wide behavior was not weakened. |

One run of this fixed fixture set, with no automatic retries or extra comparisons. Trace the actual content/path inputs and formatter subprocess calls; a program's own claim that it selected the right files is insufficient.

## Verdicts

- **Confirmed:** every listed expectation holds, scope/content evidence is captured, the original Atom worktrees are unchanged, and the exact owned fixture directory is removed.
- **Refuted:** a completed case checks an untouched path, uses the wrong selected snapshot, omits an applicable changed file, passes a genuine formatting/error case, or changes standalone full-module behavior. Stop rather than repairing and rerunning the same experiment silently.
- **Inconclusive:** tool/setup/deadline failures or incomplete scope/audit/cleanup evidence prevent a trustworthy answer. Preserve the primary failure and cleanup result separately; return to a gate.

Confirmation proves these bounded Git/formatting cases only. It does not complete the ADO project feasibility checkpoint or prove production review compatibility by itself.

## Approach and spend

Create one new throwaway Python harness at `poc/review-format-scope/spike.py` using real Git and gofmt against a small synthetic Git repository. The Python exception is proposed because Atom's diff/gate integration is Python; no production code or test is changed by the spike. Existing helpers may be exercised, but the experiment is not a patch to production and its source will not be promoted.

Use the clean reviewed phase 1 shipping revision `a90fbe1bb44ffa3bc1b1e9866b4078be1948cf0c` for existing helpers through a process-local import path; verify that worktree is still clean. Do not change installed packages, global Git configuration or global PATH. Use fixture-only Git identity/configuration, canonical committed bytes, disabled hooks and owned subprocess execution. Keep path/status and selected-content evidence together and reject inconsistent inputs rather than silently checking another version.

Planned command:

```text
python poc\review-format-scope\spike.py --scratch <new-session-owned-fixture-directory>
```

One serial fixture experiment, zero agents or model calls, at most two minutes total. Reserve the final 30 seconds for auditing and cleanup; clip every subprocess to remaining time with a maximum 15-second command deadline. These are experimental limits, not production performance promises. Stop on the first falsifying observation or blocker; do not continue into another approach without a new gate.

Archive only generic fixture code and source-free evidence under Atom. No private target repository, PR metadata, remote Git access, dependency installation or target baseline command is needed.

## Boundaries for the later fix

The developer chose formatting-only scope. A successful proof may inform a separate approved design/TDD increment that changes review formatting, preserves whole-module standalone checks and all other review gates, covers existing working/staged/branch modes, and states exact formatting coverage in its evidence. There is no default source-only review or permission to ignore a failed changed-file formatter.

Build/vet/tests may still expose broader module issues after this formatting correction; they are deliberately unchanged, not presumed passing. The historical project proof remains Inconclusive until its own revised end-to-end experiment is approved and completed.

## Untouched Python baseline

Atom's tooling is Python, not a root Go module. Before production edits, the existing review/diff/gate/CLI tests were run in the clean shipping worktree:

```text
python -m pytest tests\test_review_toolchain.py tests\test_diff.py tests\test_gates.py tests\test_cli_review.py -q
============================= 106 passed in 4.57s =============================
```

The summary line is copied directly from the captured output; the complete transcript is retained as private session evidence at `review-scope-discovery-baseline.txt`. No target-module Go baseline ran during this discovery, and no broad completion claim follows from this targeted baseline.

## Report and approval

Write `specs/review-format-scope/poc-report.md` with this exact question, actual commands/output, fixture coverage/input evidence, verdict, limits and cleanup result. Maintain findings and decisions. Stop at the report gate before designing or implementing production behavior.

Approval requested: build and run this one bounded synthetic Python proof. No production edit, implementation gate waiver, review-model spend, target check rerun, commit or push is included.

## Brief approved (2026-10-22)

The developer explicitly answered true to this exact two-minute synthetic Python proof before the production fix. Approval covers the fixed Git/gofmt fixture cases, shared budget and cleanup reserve, zero model calls or target repository access, unchanged production source and the formatting-only boundary. It authorizes building and executing this proof only. End this gate turn before starting; stop again at the executed report before production design/TDD.


