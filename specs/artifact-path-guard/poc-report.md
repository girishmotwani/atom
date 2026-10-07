---
project: "artifact-path-guard"
phase: "n/a"
poc_slug: "artifact-path-guard"
verdict: "Confirmed"
date: "2026-01-20"
spike_path: "poc/artifact-path-guard"
---

# POC Report

## The Question

Can a Python path guard, running on Windows, deny a write to
`specs/<junction>/escaped.md` where `<junction>` is a real directory junction pointing
outside the repository, while still allowing ordinary `specs/**`, `poc/**`, and the four
`.atom` runtime files?

## Verdict

**Confirmed.** A real `mklink /J` junction was created at `specs/junction-link` pointing
to a temp directory outside the repository, and `specs/junction-link/escaped.md` was
denied with reason `reparse-point-in-path` — the exact case that refuted the Go
implementation — while all seven ordinary artifact paths were allowed.

## Evidence

Command:

```bash
cd poc/artifact-path-guard && python spike.py
```

Output (second run; see "What We Learned" for why the first run is also reported):

```text
target='specs/demo.md' expected_allowed=True actual_allowed=True reason=allowed-artifact-directory pass=True
target='poc/demo/README.md' expected_allowed=True actual_allowed=True reason=allowed-artifact-directory pass=True
target='.atom/config.json' expected_allowed=True actual_allowed=True reason=allowed-runtime-file pass=True
target='.atom/state.json' expected_allowed=True actual_allowed=True reason=allowed-runtime-file pass=True
target='.atom/events.jsonl' expected_allowed=True actual_allowed=True reason=allowed-runtime-file pass=True
target='.atom/baseline.json' expected_allowed=True actual_allowed=True reason=allowed-runtime-file pass=True
target='specs/nested/deep/report.md' expected_allowed=True actual_allowed=True reason=allowed-artifact-directory pass=True
target='internal/main.go' expected_allowed=False actual_allowed=False reason=outside-artifact-set pass=True
target='.github/copilot-instructions.md' expected_allowed=False actual_allowed=False reason=outside-artifact-set pass=True
target='.atom/atom/AGENTS.md' expected_allowed=False actual_allowed=False reason=outside-artifact-set pass=True
target='.atom/credentials.json' expected_allowed=False actual_allowed=False reason=outside-artifact-set pass=True
target='specs/../internal/escape.go' expected_allowed=False actual_allowed=False reason=outside-artifact-set pass=True
target='specs' expected_allowed=False actual_allowed=False reason=outside-artifact-set pass=True
target='C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-guard-outside-okznjp6g\\absolute.md' expected_allowed=False actual_allowed=False reason=lexically-outside pass=True
target='specs/junction-link/escaped.md' expected_allowed=False actual_allowed=False reason=reparse-point-in-path pass=True
target='specs/inner-link/inside.md' expected_allowed=False actual_allowed=False reason=reparse-point-in-path pass=True
junction_created=True
symlink_created=False
inner_junction_created=True
platform=win32 python=3.13.14
verdict=CONFIRMED
EXIT=0
```

First run, before the `specs/inner-link` expectation was corrected:

```text
target='specs/inner-link/inside.md' expected_allowed=True actual_allowed=False reason=reparse-point-in-path pass=False
junction_created=True
symlink_created=False
inner_junction_created=True
platform=win32 python=3.13.14
verdict=REFUTED reason=1 case(s) produced the wrong decision
EXIT=1
```

Run context:

- Date/time run: 2026-01-20, two runs.
- Commit or working tree note: working tree on branch `feat/self-contained-atom-onboarding`,
  spike untracked.
- Python version: `3.13.14`, `platform=win32`.
- Relevant input size/rate: n/a — correctness matrix of 16 cases.
- Number of runs: 2.

Result summary from the pasted output only:

- Confirming observation: `specs/junction-link/escaped.md` denied, `junction_created=True`.
- Refuting observation: none in the second run.
- Inconclusive gap: `symlink_created=False` — the POSIX-style symlink arm never ran.

## What The Spike Did

The spike at `poc/artifact-path-guard/spike.py` creates two temp directories (a fake
repository and an outside directory), joins them with a real directory junction via
`cmd.exe /c mklink /J`, then runs a candidate four-stage guard over a fixed case matrix
and compares each decision to a written-down expectation.

- Real inputs or dependencies: real filesystem, real `mklink /J` junction, real
  `os.lstat` / `os.path.realpath` behaviour on this Windows machine.
- Simulated inputs or dependencies: the repository is an empty temp tree; no file is
  actually written through the guard.
- Main measurements printed: per-case expected vs. actual decision with a reason code,
  whether each link type could be created, and a single verdict line.

## What We Learned

- The check that catches the junction is **not** path resolution — it is the explicit
  reparse-point test. `os.lstat(...).st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT`
  returns true for a junction, and it fires before any containment comparison. This is
  the specific thing the Go version lacked.
- Surprise: the guard also denies `specs/inner-link/inside.md`, a junction pointing back
  *inside* the repository. The first run scored that as a failure because the spike's
  expectation said it should be allowed. On inspection the guard is right and the
  expectation was wrong — proving a link is benign is more work than refusing all links,
  and refusing is the safe default. The expectation was corrected and the reasoning
  recorded rather than the guard being loosened.
- Expected but not observed: `os.symlink` failed, so `symlink_created=False`. Developer
  Mode is off and the shell is unprivileged. Junctions and symlinks are both reparse
  points and are caught by the same attribute test, but that is reasoning, not evidence.
- Observed but not expected: a bare `specs` directory target is denied by the allowlist
  stage (`outside-artifact-set`), because the match requires at least one path component
  below the allowed directory. That is desirable — it prevents treating a directory as a
  file target — but it was not a designed behaviour.
- New risk exposed: the guard decides, then a caller writes. Between those two moments a
  link could be introduced. This is a TOCTOU window the spike does not address.

## What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| Resolving the path and comparing prefixes is enough to prove containment | Refuted | Resolution alone is necessary but not sufficient. The design must test the reparse-point attribute on every existing component explicitly. |
| Python can detect a Windows junction without native API calls | Confirmed | No `ctypes` / `GetFinalPathNameByHandle` dependency is needed. `os.lstat` plus `stat.FILE_ATTRIBUTE_REPARSE_POINT` suffices, so the module stays pure-stdlib and testable. |
| The allowlist boundary agreed with the developer is expressible as data | Confirmed | Two allowed directory prefixes and four exact `.atom` filenames decided all 16 cases correctly with no special cases. |
| Validation is independent of writing | Confirmed, with a caveat | Safe to build the validator as a standalone module, but the eventual writer must re-check at write time or open with link-following disabled — the TOCTOU gap is real and out of scope here. |

## Explicitly Not Covered

- POSIX symlinks were never created; the symlink arm did not run.
- Linux and macOS behaviour is unproven. Only `win32` was exercised.
- Nothing was written to disk through the guard — this proves the *decision*, not the
  write, and says nothing about atomicity or partial batches.
- The TOCTOU window between decision and write is not addressed.
- Hard links, NTFS alternate data streams (`specs/demo.md:hidden`), 8.3 short names, and
  trailing-dot/space Windows path aliases were not tested.
- Case sensitivity was exercised only incidentally via `os.path.normcase`.
- No claim is made about how the guard is invoked from Copilot CLI.

## Recommendation

**Proceed to spec.** The question returned a clear yes on the exact case that killed the
previous approach, and the mechanism that produced the yes is understood rather than
incidental. The remaining unknowns (TOCTOU, non-Windows platforms, exotic path aliases)
are design concerns, not feasibility concerns.

Next artifact: `specs/artifact-path-guard/design-spec.md`

Conditions before continuing:

- The spec must state explicitly whether the guard refuses *all* reparse points or tries
  to permit benign inside-pointing ones. The spike's answer is "refuse all" and that
  should be a written decision, not an accident of implementation.
- The spec must say what the writer does about the TOCTOU window, even if the answer is
  "accepted, documented".
- The exotic Windows path aliases listed above need to become either test cases or a
  recorded non-goal before implementation, not after.

## Completeness Checklist

- [x] The question is copied verbatim from the brief.
- [x] Verdict is exactly Confirmed, Refuted, or Inconclusive.
- [x] Verbatim run output is pasted in a fenced block.
- [x] Spike path is recorded.
- [x] Surprises and non-obvious findings are captured.
- [x] Design consequences are tied to observed evidence.
- [x] Boundaries are explicit enough to prevent over-reading.
- [x] Recommendation follows from the verdict.
- [x] Run context is recorded.
- [x] Any inconclusive gap is named directly.
- [x] The report does not claim evidence outside the pasted output.
- [x] Not a comparison spike; treatment-evidence section removed.
