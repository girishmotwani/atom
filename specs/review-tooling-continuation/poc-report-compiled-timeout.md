---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
poc_slug: "review-tooling-continuation-compiled-timeout"
verdict: "Confirmed"
date: "2026-11-02"
spike_path: "poc/review-tooling-continuation/spike-compiled-timeout.py"
---

# POC Report: Compiled-Timeout Classification Batch

## The Question

Can bounded controls distinguish a declared Go-minimum incompatibility from genuine or ambiguous source/check failures on the same frozen fixture, allowing only the evidenced incompatibility to reach a reviewer stub with truthful degraded evidence?

## Verdict

**Confirmed for this bounded classification matrix.** Two complete sweeps produced 18 expected observations: only the valid compatible case reached the stub as normal and only the valid higher-minimum case reached it as degraded; all source failures and ambiguous cases remained blocked. This does not resolve the earlier Go-supervised Windows timeout/cleanup failure or establish production behavior.

## Evidence of Treatment

Arms: selected Go 1.26.9 versus compatible-control Go 1.27.3, plus a clearly labelled simulated control-runner error. The revised slow-case treatment is selected-compiler test compilation followed by direct compiled-binary invocation.

**Check 1 — treatment reached a model:** no model was invoked, so model-prompt delivery is not applicable. The four in-process reviewer-stub receipts are captured with prompt bytes and hashes: normal prompts were 2,259 bytes (`46b973e804aae0a04c8ce9e58faed3fece31df09424b4bb5df36d50348b2e88f`); degraded prompts were 2,421 bytes (`db3371b2c3227588b57abcde99a1d713e0f3764908d5ae98277079dc6ce9910a`). The degraded prompt explicitly says control passes do not validate the requested compiler and lists selected build as FAILED; vet/test as skipped; and all four compatible-control checks as passed.

**Check 2 — required actions happened:** the executed event log contains 30 selected-version Go commands, 24 Go 1.27.3 control commands, 26 gofmt commands, two direct compiled-test invocations, and 82 native commands total. Both direct invocations used `warm.test.exe -test.v -test.count=1 -test.run=TestWait`; the two simulated runner-error observations were separately logged and were not counted as native Go commands. The compatible-control invocation log was inspected after the batch summary had already been read; this is a treatment-evidence ordering deviation and lowers confidence in the control comparison. The raw command records independently show the 24 Go 1.27.3 commands and their outcomes.

**Check 3 — behavior changed:** the deterministic fixture matrix yielded two normal and two degraded stub calls; the remaining 14 cases had zero stub calls. Both direct slow-test runs captured the entry marker, timed out cleanly, and retained source and binary hashes. The earlier package-mode timeout capture had incomplete output, so the difference does not establish that the direct invocation repaired or improved the underlying runner.

| Observation | Count / result |
|---|---:|
| `normal` | 2 |
| `degraded` | 2 |
| `source_or_mixed` | 6 |
| `unknown` | 8 |
| Stub receipts | 4 |
| Paid model calls | 0 |

No treatment action failed. The post-result timing of the Go-control evidence check is recorded above and in `decisions.md`; no retry was authorized or performed.

## Evidence

The approved driver was launched from the isolated worktree via a Python subprocess with `--output` directed to a fresh session-only directory. Its reproducible driver invocation is:

```text
python poc\review-tooling-continuation\spike-compiled-timeout.py --output <FRESH_OUTSIDE_GIT_DIRECTORY>
```

The process returned exit code 0. Complete captured driver stdout/stderr follows verbatim:

```text
{"classification": "normal", "fixture": "compatible-valid", "prompt_bytes": 2259, "reason": "all bounded selected checks passed", "source_sha256_after": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "source_sha256_before": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "stub_calls": 1, "sweep": 1}
{"classification": "degraded", "fixture": "higher-minimum-valid", "prompt_bytes": 2421, "reason": "verified selected version is below declared minimum; identical control passes", "source_sha256_after": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 1, "sweep": 1}
{"classification": "source_or_mixed", "fixture": "compile-defect", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "23ab80cc0d40760f29d3c45b11945db7a357476b17a3f2e146a737de1fce4058", "source_sha256_before": "23ab80cc0d40760f29d3c45b11945db7a357476b17a3f2e146a737de1fce4058", "stub_calls": 0, "sweep": 1}
{"classification": "source_or_mixed", "fixture": "failing-assertion", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "79c01eb8b63d2475ca30317435e2739040875804e080b07e5cb7345d741d5d8e", "source_sha256_before": "79c01eb8b63d2475ca30317435e2739040875804e080b07e5cb7345d741d5d8e", "stub_calls": 0, "sweep": 1}
{"classification": "source_or_mixed", "fixture": "higher-minimum-compile-defect", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "894b5d63a2869de5706dbdaeeb2ee51174063c672f39636d510ba56e7252872c", "source_sha256_before": "894b5d63a2869de5706dbdaeeb2ee51174063c672f39636d510ba56e7252872c", "stub_calls": 0, "sweep": 1}
{"classification": "unknown", "fixture": "missing-requested-executable", "prompt_bytes": 0, "reason": "selection or frozen-input identity is not established", "source_sha256_after": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "source_sha256_before": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "stub_calls": 0, "sweep": 1}
{"classification": "unknown", "fixture": "slow-test", "prompt_bytes": 0, "reason": "a selected command did not complete", "source_sha256_after": "9ce6cb0ed07d9581043d227b5468fad3189d6500fd818f80a974f91c9278df45", "source_sha256_before": "9ce6cb0ed07d9581043d227b5468fad3189d6500fd818f80a974f91c9278df45", "stub_calls": 0, "sweep": 1}
{"classification": "unknown", "fixture": "control-runner-error", "prompt_bytes": 0, "reason": "compatible control is absent or did not complete", "source_sha256_after": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 0, "sweep": 1}
{"classification": "unknown", "fixture": "changed-source", "prompt_bytes": 0, "reason": "selection or frozen-input identity is not established", "source_sha256_after": "47531b0e6885d47cfc10e249eae64307989cf6170573359683e476571129435d", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 0, "sweep": 1}
{"classification": "normal", "fixture": "compatible-valid", "prompt_bytes": 2259, "reason": "all bounded selected checks passed", "source_sha256_after": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "source_sha256_before": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "stub_calls": 1, "sweep": 2}
{"classification": "degraded", "fixture": "higher-minimum-valid", "prompt_bytes": 2421, "reason": "verified selected version is below declared minimum; identical control passes", "source_sha256_after": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 1, "sweep": 2}
{"classification": "source_or_mixed", "fixture": "compile-defect", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "23ab80cc0d40760f29d3c45b11945db7a357476b17a3f2e146a737de1fce4058", "source_sha256_before": "23ab80cc0d40760f29d3c45b11945db7a357476b17a3f2e146a737de1fce4058", "stub_calls": 0, "sweep": 2}
{"classification": "source_or_mixed", "fixture": "failing-assertion", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "79c01eb8b63d2475ca30317435e2739040875804e080b07e5cb7345d741d5d8e", "source_sha256_before": "79c01eb8b63d2475ca30317435e2739040875804e080b07e5cb7345d741d5d8e", "stub_calls": 0, "sweep": 2}
{"classification": "source_or_mixed", "fixture": "higher-minimum-compile-defect", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "894b5d63a2869de5706dbdaeeb2ee51174063c672f39636d510ba56e7252872c", "source_sha256_before": "894b5d63a2869de5706dbdaeeb2ee51174063c672f39636d510ba56e7252872c", "stub_calls": 0, "sweep": 2}
{"classification": "unknown", "fixture": "missing-requested-executable", "prompt_bytes": 0, "reason": "selection or frozen-input identity is not established", "source_sha256_after": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "source_sha256_before": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "stub_calls": 0, "sweep": 2}
{"classification": "unknown", "fixture": "slow-test", "prompt_bytes": 0, "reason": "a selected command did not complete", "source_sha256_after": "9ce6cb0ed07d9581043d227b5468fad3189d6500fd818f80a974f91c9278df45", "source_sha256_before": "9ce6cb0ed07d9581043d227b5468fad3189d6500fd818f80a974f91c9278df45", "stub_calls": 0, "sweep": 2}
{"classification": "unknown", "fixture": "control-runner-error", "prompt_bytes": 0, "reason": "compatible control is absent or did not complete", "source_sha256_after": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 0, "sweep": 2}
{"classification": "unknown", "fixture": "changed-source", "prompt_bytes": 0, "reason": "selection or frozen-input identity is not established", "source_sha256_after": "47531b0e6885d47cfc10e249eae64307989cf6170573359683e476571129435d", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 0, "sweep": 2}
{"completed_cases": 18, "detail": "all eighteen bounded observations matched", "driver_sha256": "7a5c4ccadc496adda08a8f56850c9f5fe96455ee7b90d18ca4806bb9cc96905b", "elapsed_seconds": 163.3361283999402, "model_calls": 0, "native_commands": 82, "stub_receipts": 4, "verdict": "Confirmed"}
```

Actual direct slow-test stdout and stderr, captured independently in the native command records:

```text
=== RUN   TestWait
slow-test-entered
```

```text
Command timed out after 2 seconds.
```

The two direct invocation durations, including launch/cleanup, were 3.5989742000820115 seconds and 3.5552680999971926 seconds. Each had `timed_out` outcome, no additional cleanup/incomplete-output diagnostic, and an unchanged binary/source hash.

Verified toolchain identities:

| Distribution | Go SHA-256 | gofmt SHA-256 |
|---|---|---|
| Go 1.26.9 | 5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620 | 6624039b8bc726fe310dffc7f6d42e3a70b871639f725117d166299cecfe53bb |
| Go 1.27.3 | 83b7ba66215e696414fa49462d0db2da4f4cf15c7bebd42f0b189fa04866999d | 42f76ab97ca449d419f9cb19b0245cbd02af4b75170d27445f888722c7931ff3 |

Slow-fixture identities:

| Sweep | Test-binary SHA-256 (before = after) | Source SHA-256 (before = after) | Result |
|---|---|---|---|
| Sweep 1 | `00ce109a300611ce482a933d727dc7d2e0632a85c27c398463ebe2eec48ba411` | `9ce6cb0ed07d9581043d227b5468fad3189d6500fd818f80a974f91c9278df45` | timed_out |
| Sweep 2 | `1af11e6a90ee3dda8a82c8890f27cd69e831f915034a0e7e3743f831369a745d` | `9ce6cb0ed07d9581043d227b5468fad3189d6500fd818f80a974f91c9278df45` | timed_out |

The run used Go 1.26.9 as selected compiler and Go 1.27.3 as compatible control. The run lasted 163.3361283999402 seconds, executed 82 native commands (within the 96-command/900-second ceilings), completed 18 of 18 cases, recorded 4 stub receipts, and made 0 model calls.

Raw evidence remains outside Git:

- Event log SHA-256: `bed63295f98ef42dcc8d109414773eb226db4478abf9815fe38fc2583c87389e` (119935 bytes).
- Console capture SHA-256: `4ae16e19970419d85c19c33749697e3f7e2e87a15d03d87a97dfc5f06054c22b` (6838 bytes).
- Executed driver SHA-256: `7a5c4ccadc496adda08a8f56850c9f5fe96455ee7b90d18ca4806bb9cc96905b`.
- Trial fixtures, local compiled binaries, event log, and console output are retained under the session directory; the previous drivers and reports were not modified.

## What the Spike Did

The disposable Python driver at `poc/review-tooling-continuation/spike-compiled-timeout.py` ran two serial sweeps of nine small Go fixtures, using native gofmt/build/vet/test commands where specified. It compared selected Go 1.26.9 evidence with Go 1.27.3 control evidence, fed only normal/degraded evidence to an in-process stub, and kept simulated runner errors distinct from native commands. For the slow case, it compiled the test using selected Go and launched the resulting test binary directly; no package-mode supervisor was involved in that timed invocation.

- Real inputs: locally installed Go 1.26.9/1.27.3 executables, generated standard-library-only fixture modules, actual command outputs, and actual local stub receipts.
- Simulated input: only the separately labelled control-runner-error case.
- Main measurements: fixture classification, stub admissions/prompt bytes, command outcomes, and source/test-binary identity.

## What We Learned

- The bounded classifier admitted only the declared-minimum mismatch with valid source as degraded; actual compile/test defects and ambiguous controls remained blocked.
- Direct test-binary execution reproducibly exposed `slow-test-entered` and returned a clean timeout in both sweeps.
- The original Go-supervised timeout failure remains unexplained. This changed command path does not prove a runner repair.
- The compatible compiler's command records were independently checked after seeing the batch result; this is a process deviation, not a missing command record.
- New risk exposed: results are bounded to one Windows machine, two compiler versions, and the fixtures/commands in this matrix.

## What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| A declared Go-minimum mismatch can be separated from source failures with same-source compatible-control evidence. | Confirmed, bounded | A design may explore degraded review for this narrow class only; do not treat control passes as selected-compiler passes. |
| Defective or ambiguous cases can be conservatively blocked. | Confirmed, bounded | Keep failures/unknowns blocking, preserve failed and skipped statuses, and do not infer safety from diagnostic text alone. |
| The Go-supervised Windows timeout can be treated as clean after direct-binary timeout succeeds. | Not confirmed | Keep the prior cleanup/output-collection issue open and outside this classification result. |

## Explicitly Not Covered

- Production code, real model calls, user-facing defaults, CLI exit semantics, and report/schema compatibility.
- The original Go-supervised Windows cleanup failure, the parent PR's macOS/Windows CI failures, or any general Windows process-tree reliability claim.
- Other Go versions, operating systems, dependencies, workspaces, CGO, race detection, advisory analyzers, or statistical reliability.
- Whether a production compatible-control policy is safe or desirable; this POC tests only the bounded fixture classification.

## Recommendation

**Proceed to the phase design spec**, subject to the developer's gate. The evidence supports a narrowly scoped design discussion; it does not authorize implementation or claim the existing runner issue is fixed.

Next artifact: `specs/review-tooling-continuation/phase-02-honest-review-continuation/design-spec.md`.

Conditions before continuing:

- Keep the original Go-supervised timeout issue and Phase 01 CI failures explicitly unresolved.
- Design only the evidence-backed incompatibility class; leave default/opt-in policy, control execution permission, exit status, and compatibility decisions open for the developer.

## Completeness Checklist

- [x] Question copied verbatim from the approved brief.
- [x] Verdict is Confirmed and limited to the bounded acceptance criteria.
- [x] Actual driver output is pasted verbatim; this custom Python driver was executed directly rather than through `atom poc run`.
- [x] Spike path and run context recorded.
- [x] Treatment use and behavior evidenced; post-result control-action verification is disclosed.
- [x] Design consequences follow from the observed classifications.
- [x] Unresolved cleanup issue and other non-coverage are explicit.
- [x] No production change, model invocation, retry, or publication occurred.
