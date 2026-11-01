---
project: "review-toolchain-policy"
phase: "n/a"
poc_slug: "review-toolchain-policy"
verdict: "Inconclusive"
date: "2026-10-30"
spike_path: "poc/review-toolchain-policy"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# POC Report

## The Question

Can child-process-only selection of Go 1.26.9 keep build, vet, and test on that exact version across conflicting inherited selection settings and compatible module/workspace toolchain suggestions, reject higher language-version requirements without upgrading, and leave persistent defaults unchanged?

## Verdict

**Inconclusive.** The offline-control choice `GOSUMDB=off` prevented the selected-toolchain bootstrap from passing checksum verification on the first `go version` command. Zero of ten cases completed, so the trial did not establish exact selection, module/workspace behavior, build/vet/test compatibility or runtime identity.

This is not evidence that exact selection is impossible. It is also not a passing selection experiment. No retry or environment repair was attempted.

## Evidence

Approved command, executed once from the worktree root:

```text
python poc\review-toolchain-policy\spike.py
```

The driver emitted the following complete JSONL stdout. Each command event preserves its actual stdout/stderr and outcome. The process exited 1. Evidence is copied from the captured log, not reconstructed; no redactions are applied to this local report.

```jsonl
{"event": "start", "question": "Can child-process-only selection of Go 1.26.9 keep build, vet, and test on that exact version across conflicting inherited selection settings and compatible module/workspace toolchain suggestions, reject higher language-version requirements without upgrading, and leave persistent defaults unchanged?", "cases": 10, "timeout_seconds": 60, "retries": 0, "toolchain_downloads_allowed": false, "configuration_sha256_before": "2965fe8072748e8473baf6f453dee6738ce335abf464576f9498cff229486106", "inherited_selection": null, "launcher": "C:\\Program Files\\Go\\bin\\go.EXE"}
{"event": "fixture-inputs", "sha256": {"module-newer-minimum\\go.mod": "340bcf5e1b6ac4631d113575aee1848ee7fb6b860ac10484e2a8ce5c9cd9533f", "module-newer-minimum\\main.go": "61d57eb485e35b7773d9844f0b0bc8778a638d262d8435e005d664ab73abcc9f", "module-newer-minimum\\main_test.go": "792b6c3da9f05693741d9ab647a33a03589c7beedd123460520efcdea67e0423", "module-newer-suggestion\\go.mod": "89b2a5003d1e3ee2069585f625b225e9d7216239e4e50f65835272276df5138d", "module-newer-suggestion\\main.go": "61d57eb485e35b7773d9844f0b0bc8778a638d262d8435e005d664ab73abcc9f", "module-newer-suggestion\\main_test.go": "792b6c3da9f05693741d9ab647a33a03589c7beedd123460520efcdea67e0423", "plain-module\\go.mod": "6ff3213c69a6da16a488cdb07416f687b609df272e8758e2762042bfef94083e", "plain-module\\main.go": "61d57eb485e35b7773d9844f0b0bc8778a638d262d8435e005d664ab73abcc9f", "plain-module\\main_test.go": "792b6c3da9f05693741d9ab647a33a03589c7beedd123460520efcdea67e0423", "workspace-newer-minimum\\go.work": "644c1b08992fe042897b1e5d6bd26df45420bb29af5756d939b1451105e7b4be", "workspace-newer-suggestion\\go.work": "768d76baaf3a96294cdcf3c8a08d891135f0694cf43174e30b558a315c4efa90", "workspace-newer-suggestion\\module\\go.mod": "e9c85559068df2ba46ac3e1f2ef88b97161c89300cdf10079ccbd7afae5fccb8", "workspace-newer-suggestion\\module\\main.go": "61d57eb485e35b7773d9844f0b0bc8778a638d262d8435e005d664ab73abcc9f", "workspace-newer-suggestion\\module\\main_test.go": "792b6c3da9f05693741d9ab647a33a03589c7beedd123460520efcdea67e0423", "workspace-newer-minimum\\module\\go.mod": "1d2f74a6a138e5566009868edbe02475d9a1fe6fd3880782890159298fd730ce", "workspace-newer-minimum\\module\\main.go": "61d57eb485e35b7773d9844f0b0bc8778a638d262d8435e005d664ab73abcc9f", "workspace-newer-minimum\\module\\main_test.go": "792b6c3da9f05693741d9ab647a33a03589c7beedd123460520efcdea67e0423"}}
{"event": "case-start", "case": "plain-module", "parent_selection": "local", "child_selection": "go1.26.9", "workspace": false, "newer_suggestion": false, "higher_minimum": false}
{"event": "command", "case": "plain-module", "parent_selection": "local", "child_selection": "go1.26.9", "argv": ["go", "version"], "outcome": "completed", "exit_code": 1, "stdout": "", "stderr": "go: default toolchain set to go1.26.9 from GOTOOLCHAIN=go1.26.9\ngo: golang.org/toolchain@v0.0.1-go1.26.9.windows-amd64: verifying module: checksum database disabled by GOSUMDB=off\n"}
{"event": "stopped", "reason": "RuntimeError: compatible fixture command failed"}
{"event": "verdict", "verdict": "Inconclusive", "reason": "RuntimeError: compatible fixture command failed", "completed_cases": 0, "command_count": 1, "parent_environment_unchanged": true, "persistent_settings_unchanged": true}
```

## Run Context And Identity

- Branch: `feat/atom-v1-toolchain`, created at the developer's request from latest public main `8b4dd51135c3836d5921414878182b16ff2fdefc`.
- Environment: Windows; real Go launcher with generated standard-library-only Go fixtures; Python automation and the existing owned-process runner.
- Attempted selection: child-only `GOTOOLCHAIN=go1.26.9`, with `GOPROXY=off` and `GOSUMDB=off`.
- Captured commands: one attempted `go version`, completed with exit 1. Build, vet, test and generated executable were never invoked.
- Runs: one; retries: zero; completed matrix cases: zero; model calls: zero.
- Parent environment and persistent Go settings comparisons reported unchanged. Owned temporary fixtures were cleaned up by the driver.
- Captured JSONL file SHA-256: `21b4c29dbc99b1adbed094925f07cb301f14b14b703e9b98df87cebb93a1ce36`.
- Executed driver SHA-256: `c4053f08e473fefb756712137717b040c65940c4cc512f3050cc786cb14cd73e`.

## What The Spike Did

The archived driver generates five isolated module/workspace fixtures, then intends to run them under two copied-parent selection settings with an exact child override. Version/environment probes, `-x` build/vet/test traces, runtime assertions and settings/input snapshots were predeclared. Only the first version command executed; all later stages remain unobserved.

The original Python/Go-fixture approach was approved in the brief, so no standalone Go-root scaffold or `atom poc run` invocation is claimed. This was not a model comparison or a performance experiment.

## What We Learned

The first command's toolchain trace shows that the exact override reached the Go launcher. The launcher then rejected checksum verification because the driver disabled the checksum database. That diagnostic is the observed blocker; we did not independently verify every cache component or establish whether a complete runnable selected executable is present.

The experiment's autonomous offline-control choice was too restrictive for this bootstrap path. Disabling checksums is not a suitable way to prove a selected cached toolchain can execute. No product-level compiler-failure classifier or automatic fallback is justified by this observation.

## What This Changes

| Assumption | Status | Consequence |
|---|---|---|
| `GOSUMDB=off` is a harmless offline control for this selected-toolchain bootstrap | Contradicted by the recorded first-command error | Do not silently repeat this setup or change user defaults |
| The ten module/workspace cases establish exact selection | Unobserved | No selection design or production implementation yet |
| The Go selection attempt changed persistent defaults | Not observed; snapshot comparison is unchanged | Preserve this boundary in any follow-up trial |
| An existing exact executable can be invoked directly without bootstrap verification | Unproven | A separately approved local-executable trial can isolate this route |

## Explicitly Not Covered

- All ten case outcomes, build/vet/test/runtime identity and tool provenance after successful selection.
- Whether a complete usable local Go 1.26.9 executable exists independently of the launcher bootstrap.
- Linux/macOS, absent-toolchain acquisition, downloads, real dependencies, private target, real PR evidence or model reviews.
- Production persistence/precedence, missing-version policy, Go formatting/build wrappers or degraded-review exit/status semantics.
- Any guarantee of reproducible build inputs beyond a selected compiler version.

## Recommendation And Gate

Do not proceed to spec. Preserve this original Inconclusive trial and obtain approval for a separate offline direct-executable trial, described in `poc-brief-local-executable.md`. That proposal changes how the toolchain is selected and therefore needs explicit approval before code or execution. It does not repair or relabel this trial.

## Completeness

- [x] Question copied verbatim; original driver and complete command evidence preserved.
- [x] Stop-on-first-unexpected-failure honored; no retry or deadline increase.
- [x] Inconclusive gap and unchanged-default observations stated explicitly.
- [x] No claims about unexecuted cases or permission for production design.
- [ ] Developer disposition of the result and proposed follow-up experiment.
