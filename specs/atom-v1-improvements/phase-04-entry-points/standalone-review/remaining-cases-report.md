---
project: "atom-v1-improvements"
phase: "phase-04-entry-points"
poc_slug: "atom-v1-standalone-review"
verdict: "Confirmed"
date: "2026-11-09"
spike_path: "poc/atom-v1-standalone-review"
---

# POC Report - Remaining Standalone Review Cases

## The Question

Original scope, copied verbatim from `poc-brief.md`:

Can the installed Atom review CLI select working, staged and branch changes in
local Go repositories without Atom or phase state, produce correctly scoped
reports, preserve source/state, and retain honest missing-module and failing-gate
behavior, with a deterministic reviewer transport instead of real model calls?

This continuation's question, copied verbatim from `remaining-cases-brief.md`:

can the same installed review entry complete staged and branch review,
block reviewers on broken Go source, and report missing-module evidence honestly,
without Atom/phase state or source/state mutation, using synthetic reviewers?

## Verdict

**Confirmed for the approved four remaining mechanical observations, combined
with the preserved working-tree observation under the validated same-runtime
boundary.** This does not change either earlier whole-run Inconclusive verdict.
The current run alone did not repeat or newly observe the working-tree case.

## Evidence

Approved command, executed once:

```powershell
python .\poc\atom-v1-standalone-review\run_trial.py
```

```text
staged: declared observation met; CLI exit 0; 4 synthetic transport calls
branch: declared observation met; CLI exit 0; 4 synthetic transport calls
broken-source: declared observation met; CLI exit 1; 0 synthetic transport calls
no-module: declared observation met; CLI exit 0; 4 synthetic transport calls
Verdict: Confirmed; real commands: 75; nested Git calls: 2; synthetic calls: 12; model calls: 0
```

Raw commands, inputs, outputs, reports and snapshots:
`remaining-cases-execution.json`.
Reused working observation: `transport-correction-execution.json`.
Original observer failure: `execution.json`. All remain separate.

Run context:

- Date: 2026-11-09; uncommitted Phase 04 work on `feat/atom-v1-entry-points`.
- Installed Go: `go version go1.27.0 windows/amd64`.
- Installed runtime: `C:\Users\gimotwan\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\atom\__init__.py`.
- Fresh root: `C:\Users\gimotwan\AppData\Local\Temp\atom-phase04-standalone-review-remaining-20261109`.
- One execution; four independent fixtures; no real reviewers/models or installs.
- Measured duration from raw evidence: `39.17636370001128` seconds.
- 75 delegated local-command attempts, including 9 actual missing-analyzer attempts,
  plus 2 nested Git invocations counted from the exact pinned helper body.
  This is 77 counted attempts within the 100-attempt ceiling, not a complete OS
  process count. Go compiler/test descendants are not independently instrumented.
- Twelve synthetic interceptions: six availability probes and six fixture answers.
  These are not twelve model calls. All Copilot invocations are intercepted.

### Results Against Criteria

| Case | Evidence | Outcome |
| --- | --- | --- |
| Working tree, reused | Earlier complete JSON report; actual required Go gates passed; only unstaged `sample.go` selected | Met, reused; not repeated |
| Staged | JSON report; only staged `sample.go`; required Go gates passed | Met, exit 0 |
| Branch against main | Markdown report; only committed `sample.go`, excluding uncommitted notes; required Go gates passed | Met, exit 0 |
| Broken Go source | Explicit required-gate failure, empty stdout, zero reviewer probes/answers | Met, expected exit 1 |
| No root module | JSON with `was_run: false`, explicit missing-go.mod reason, no gate results or new module | Met, exit 0 does not verify code |

Before/after source hashes, HEAD and staged/unstaged diff semantics compare equal
for every case. No `.atom`, `specs` or `poc` appeared. Preserved fixtures remain on
disk; Git-index timestamps/build caches are not part of this preservation claim.

### Real Go Commands And Output

The commands below are captured from the actual runner, not simulated. Empty
build/vet output with exit 0 is reported as empty, not invented success text.
Formatting used actual `gofmt` on the selected source snapshots.

#### staged

`go build ./...`; exit `0`.

stdout and stderr were empty.

`go vet ./...`; exit `0`.

stdout and stderr were empty.

`gofmt (selected source supplied on stdin)`; exit `0`.

stdout, verbatim:

```text
package sample

// Double supports a deterministic fixture smoke test.
func Double(value int) int {
	return value + value
}
```

`go test ./...`; exit `0`.

stdout, verbatim:

```text
ok  	example.com/atom-review-fixture-staged	2.431s
```

`go test -race ./...`; exit `0`.

stdout, verbatim:

```text
ok  	example.com/atom-review-fixture-staged	2.896s
```


#### branch

`go build ./...`; exit `0`.

stdout and stderr were empty.

`go vet ./...`; exit `0`.

stdout and stderr were empty.

`gofmt (selected source supplied on stdin)`; exit `0`.

stdout, verbatim:

```text
package sample

// Double supports a deterministic fixture smoke test.
func Double(value int) int {
	return value + value
}
```

`go test ./...`; exit `0`.

stdout, verbatim:

```text
ok  	example.com/atom-review-fixture-branch	2.782s
```

`go test -race ./...`; exit `0`.

stdout, verbatim:

```text
ok  	example.com/atom-review-fixture-branch	3.357s
```

### Branch Markdown Report, Verbatim

```markdown
# Code review

Reviewed this branch against main: 2 changed lines across 1 file.

- `sample.go`

| Model | Runs completed |
| --- | --- |
| `fixture-reviewer-one` | 1/1 |
| `fixture-reviewer-two` | 1/1 |

## Toolchain evidence

| Command | Verdict |
| --- | --- |
| `go build ./...` | PASSED |
| `go vet ./...` | PASSED |
| `gofmt (changed Go files)` | PASSED - Checked 1 changed Go file(s) from this branch against main: 'sample.go' |
| `go test ./...` | PASSED |
| `go test -race ./...` | PASSED |
| `staticcheck ./...` | not installed - not checked |
| `errcheck ./...` | not installed - not checked |
| `govulncheck ./...` | not installed - not checked |

    Formatting checks selected snapshots from this branch against main: 'sample.go'

## Module rules

Status: not-found. Provenance: local-launch.
Neither optional local source was found; only shared Go rules apply.

## Findings

### `sample.go`

#### sample.go:5 - low

Reported by: `fixture-reviewer-one` 1/1, `fixture-reviewer-two` 1/1

- `fixture-reviewer-one` run 1, line 5 (low): Synthetic transport sentinel; not a real code defect.
- `fixture-reviewer-two` run 1, line 5 (low): Synthetic transport sentinel; not a real code defect.

```

### Required-Gate Failure, Verbatim CLI stderr

```text
atom review: required Go toolchain gates failed; review was not run.
atom review: build: go build ./... failed with exit code 1
  # example.com/atom-review-fixture-broken-source
  .\sample.go:5:17: undefined: missingFixtureValue
atom review: vet: go vet ./... failed with exit code 1
  # example.com/atom-review-fixture-broken-source
  # [example.com/atom-review-fixture-broken-source]
  vet.exe: .\sample.go:5:17: undefined: missingFixtureValue
atom review: test: go test ./... failed with exit code 1
  FAIL	example.com/atom-review-fixture-broken-source [build failed]
  FAIL
  # example.com/atom-review-fixture-broken-source [example.com/atom-review-fixture-broken-source.test]
  .\sample.go:5:17: undefined: missingFixtureValue
atom review: race: go test -race ./... failed with exit code 1
  FAIL	example.com/atom-review-fixture-broken-source [build failed]
  FAIL
  # example.com/atom-review-fixture-broken-source [example.com/atom-review-fixture-broken-source.test]
  .\sample.go:5:17: undefined: missingFixtureValue
```

CLI stdout was empty and no synthetic reviewer call occurred. The intended
undefined fixture symbol was not repaired. All recorded compiler failures remain
in the raw evidence rather than being hidden as a clean review.

### Missing Module, Verbatim CLI stdout

```json
{
  "diff": {
    "changed_lines": 2,
    "files": [
      "sample.go"
    ],
    "source": "working"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "fixture-reviewer-one",
          "runs_reporting": 1,
          "runs_total": 1
        },
        {
          "model": "fixture-reviewer-two",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "sample.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": true,
      "line": 5,
      "lines": [
        5
      ],
      "messages": [
        {
          "line": 5,
          "message": "Synthetic transport sentinel; not a real code defect.",
          "model": "fixture-reviewer-one",
          "run_index": 1,
          "severity": "low"
        },
        {
          "line": 5,
          "message": "Synthetic transport sentinel; not a real code defect.",
          "model": "fixture-reviewer-two",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    }
  ],
  "has_no_usable_response": false,
  "is_partial": false,
  "models": [
    {
      "model": "fixture-reviewer-one",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    },
    {
      "model": "fixture-reviewer-two",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "not-found"
  },
  "schema_version": 3,
  "silent_runs": [],
  "toolchain": {
    "control_gates": [],
    "degraded": false,
    "gates": [],
    "skip_reason": "No go.mod found in C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-phase04-standalone-review-remaining-20261109\\no-module",
    "source_fingerprint": null,
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
```

No Go or gofmt command was attempted in this case. The runtime captures its diff
with `git diff`, not the Go-formatting path's raw Git capture. A post-run read-only
check initially assumed every case used raw capture and failed on this distinction;
inspection of the actual recorded fallback and JSON verified the declared
selection/skip criteria. No fixture, harness or result was changed or rerun.

## What The Spike Did

`poc\atom-v1-standalone-review\run_trial.py` calls installed Atom's CLI entry
function in-process. Its runner executes local Git/Go checks, admits only the
exact shipped Python/Git blob-reader invocation, and substitutes deterministic
JSONL reviewer events. Existing fixtures exercise actual Go modules and a small
meaningful Go test. The Python harness adaptation was already approved because
Atom's runtime is Python; this is not an invented Go wrapper or `atom poc run`.

Two explicitly synthetic reviewer identities each answer once per completed
report. Their identical finding is a transport sentinel, not a real defect or
independent model corroboration. Normal extraction/deduplication/rendering still
runs inside the installed distribution.

## Reused Evidence And Boundary Validation

The previous working observation's raw artifact digest remained identical before
and after this continuation. Its source/Git snapshots match and it completed the
original working-tree criterion. No result or verdict was overwritten.

Before execution, all 36 installed Python source files matched the frozen wheel,
whose SHA-256 is `05ec75a722fabc09c923e0a96a31bcfd8c069424e860e85f6f2d817c55265c0e`.
After execution those files still matched the captured preflight digests, and the
runtime import path matched the prior observation. Archive and exact source bytes:
`poc\atom-v1-standalone-review\advisory-corrected-observer-bytes.json`.

This validates reuse of that installed-runtime boundary, not arbitrary future
versions, other operating systems, a published GitHub installation, or delivery of
changed skill documentation to a live agent.

## What We Learned

The existing runtime can produce a standalone report without initializing Atom,
registering a phase or creating workflow artifacts. Runtime changes are not
required by these observations; the next work can focus on accurate entry guidance.

Staged/committed formatting intentionally uses a Python helper to preserve Git
blob bytes. Earlier observer failures were observer allow-list omissions; retain
those results rather than reinterpret them as runtime failures or successful runs.

Required Go failures stop before reviewer availability probes. By contrast,
missing root `go.mod` still permits a report with skipped toolchain evidence and
exit 0; guidance must not describe that as a verified build or application.
Absent optional analyzers are skipped, not passed.

Go build/vet/test/race run against the fixture's working tree. Formatting alone
uses the selected source snapshot. This does not prove hermetic testing of an
arbitrary staged index or committed branch tree that differs from the working tree.

## What This Changes

| Observed fact | Consequence for subsequent guidance design |
| --- | --- |
| Review works without phase state | Offer review-only entry rather than force initialization or lifecycle adoption |
| Real selectors include `--working`, `--staged`, `--branch REF` | Use actual command examples; do not retain unsupported `--base` |
| Synthetic identities were explicitly supplied with repeated `--model NAME` | State actual CLI model selection; do not invent `--models` or general role resolution |
| Gate failure blocks probes; missing module skips tooling | Distinguish blocked review, skipped tooling and complete report transport |
| Reports go to stdout without phase artifacts | Design explicit bounded report placement and review-only stopping |

The command/model discrepancies were identified in the inventory and the approved
original brief, not discovered by real paid reviewer calls in this continuation.

## Explicitly Not Covered

- Real model availability, cost, review quality, independent judgement, or whether
  a live agent waits for approval and stops at the intended review boundary.
- Published GitHub acquisition, plugin delivery of future guidance, or absence of
  every possible source-checkout dependency. This uses the frozen installed wheel.
- Universal repositories, race safety outside these tiny fixtures, coverage goals,
  same-file staged/worktree drift, renames/binary inputs or concurrent mutation.
- Detached/hostile process cleanup, complete descendant-process telemetry or timing
  benchmarks. This is one functional observation, not a performance experiment.
- Phase 04 completion, full Python-suite coverage or a production-code completion
  gate. This ran the approved review gates, not an additional `atom check` workflow.
- The installed-user setup trial remains Inconclusive and paused; no retry or
  filter workaround was attempted. This independent result does not close it.

## Recommendation

Proceed, after report approval, to a bounded standalone-review guidance spec at
`design-spec.md` in this directory. Reuse the demonstrated runtime; describe exact
selectors/model flags, approval before reviewer spend, honest tooling limits,
standalone output placement and review-only stopping while preserving phase mode.

The alternative is a separately approved live-agent trial before guidance design;
that would test interaction behavior this synthetic transport cannot establish,
but requires its own setup, model budget and gate. No such spend is authorized.

Approval of this report authorizes drafting that spec only. Implementation,
installed-preview replacement, real reviewers, cleanup and publishing remain
outside this gate. Findings/decisions preserve all earlier limitations.

## Completeness

- [x] Both questions copied verbatim; original and narrowed scopes distinguished.
- [x] One approved execution with actual terminal and child output captured.
- [x] Exact source archive and installed-runtime reuse boundary recorded.
- [x] All four remaining criteria met; earlier complete working observation reused.
- [x] Old Inconclusive results preserved; no result rewritten or silent retry.
- [x] Real dependencies distinguished from synthetic transport.
- [x] Surprises, design consequences and evidence limits explicit.
- [x] Developer selected "Approve report and draft the guidance spec" before drafting the standalone spec.

