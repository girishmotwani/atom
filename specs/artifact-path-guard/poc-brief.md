---
project: "artifact-path-guard"
phase: "n/a"
author: "Copilot CLI"
date: "2026-01-20"
status: "approved"
---

# POC Brief

## Problem

Atom wants a dedicated artifact-writing path so the developer approves one named
operation instead of a prompt per spec file. Every version of that idea stands or falls
on one thing: a validator that can say, reliably, whether a destination is inside the
approved artifact set. The previous attempt (`specs/artifact-write-permissions/`) was
refuted precisely here — a Windows directory junction at `specs/outside-link` looked
lexically like `specs/**`, passed a Go `filepath.EvalSymlinks` containment check, and a
file was really written outside the repository.

- Developer-visible outcome: artifact writes stop prompting individually, without
  widening write access to source code.
- Current failure or limitation: lexical prefix matching plus `EvalSymlinks` did not
  catch a junction on Windows.
- Non-negotiable constraint: a target that resolves outside the repository, or outside
  `specs/**`, `poc/**`, and the four `.atom` runtime files, must never be approved.
- Evidence already known: `specs/artifact-write-permissions/experiment-02-partial-artifacts/poc-report.md`
  (junction escape, verbatim).

## The Question

Can a Python path guard, running on Windows, deny a write to
`specs/<junction>/escaped.md` where `<junction>` is a real directory junction pointing
outside the repository, while still allowing ordinary `specs/**`, `poc/**`, and the four
`.atom` runtime files?

## Why This Is The Riskiest Unknown

The validator is the whole safety property. If it cannot be made to hold on Windows, no
amount of tool design, batching or atomic writing rescues the feature — and we already
have verbatim evidence of one implementation failing this exact case in another
language. Everything else about the feature is cheap to change later.

- Feasibility risk considered: can Python detect a junction at all? **Chosen.**
- Performance risk considered: negligible; a handful of `lstat` calls per write.
- Integration risk considered: how the guard is invoked (custom tool vs. CLI command) is
  real, but worthless to answer before the guard exists.
- Ergonomics risk considered: lowest; the API is one function and can be reshaped freely.
- Why this one was chosen: it is the only question whose "no" kills the feature.

## Success Criteria

| Observation | Means |
|---|---|
| A real junction is created and `specs/<junction>/escaped.md` is denied | Confirmed |
| `specs/**`, `poc/**` and the four `.atom` runtime files are allowed | Confirmed |
| Source, `.github/**`, `.atom/atom/**`, other `.atom` paths, `..` traversal and absolute outside paths are denied | Confirmed |
| The junction escape is allowed, or an ordinary artifact path is denied | Refuted |
| The junction cannot be created on this machine | Inconclusive |

Minimum acceptable evidence:

- Number of runs: 1 run covering the whole case matrix, re-run after any change.
- Input size or rate: n/a — this is a correctness question.
- Environment notes that affect interpretation: Windows, unprivileged shell.
  `os.symlink` is expected to fail without Developer Mode; `mklink /J` does not.
- Output values that must be pasted into the report: per-case expected/actual decision,
  whether the junction was created, and the verdict line.

## Scope

### Will Do

- Build a throwaway Python script that creates a temp repository and a temp directory
  outside it, joins them with a real `mklink /J` junction, and runs a candidate guard
  over a fixed case matrix.
- Print each case's expected and actual decision plus the reason code.
- Exit non-zero if any case disagrees with its expectation.

### Will Not Do

- No Copilot CLI involvement, no hooks, no permission plumbing.
- No writing of any file through the guard — this proves the decision, not the write.
- No batch/atomicity behaviour, no atomic replace, no concurrency.
- No POSIX symlink coverage beyond best effort, and no non-Windows platform claim.

## Approach Sketch

- Create `poc/artifact-path-guard/spike.py`.
- Candidate guard: lexical containment, then reject any reparse point or symlink on an
  existing component of the path, then re-check containment of the fully resolved path,
  then match the allowlist.
- Run with `python spike.py`.
- Stop as soon as the junction case produces a decision either way.

Disposable shortcuts allowed:

- Hardcoded allowlist, no configuration, no error handling.
- `subprocess` to `cmd.exe` for `mklink`.

Shortcuts not allowed because they would invalidate the result:

- Simulating the junction instead of creating one. The previous POC failed on a *real*
  junction; a mock proves nothing.

## Open Questions For The Developer

- None at brief time. One surfaced during the run and is recorded in the report.

## Completeness Checklist

- [x] Problem is written in the developer's terms.
- [x] The Question is one falsifiable sentence.
- [x] The riskiest unknown is ranked against feasibility, performance, integration, and ergonomics.
- [x] Success criteria are measurable observations from a running program.
- [x] Scope includes explicit exclusions.
- [x] Approach fits in one disposable command.
- [x] Open questions are listed.
- [x] Any threshold in the question has a source or is marked as a developer assumption.
- [x] The POC can be run from the command line.
- [x] The report will be able to answer Confirmed, Refuted, or Inconclusive without reinterpretation.
- [x] The spike path and slug are named.
- [x] No production implementation decisions are smuggled into the brief.
