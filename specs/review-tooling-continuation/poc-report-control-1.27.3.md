---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
poc_slug: "review-tooling-continuation"
verdict: "Inconclusive"
date: "2026-11-01"
spike_path: "poc/review-tooling-continuation"
---

# POC Report: Partial Matrix, Failed Timeout Evidence

## The Question

Can bounded controls distinguish a declared Go-minimum incompatibility from genuine or ambiguous source/check failures on the same frozen fixture, allowing only the evidenced incompatibility to reach a reviewer stub with truthful degraded evidence?

## Verdict

**Inconclusive.** Both exact distributions verified and six first-sweep cases
produced their required observations. The slow-test command timed out with
Windows process cleanup/output-collection errors and no entry marker.
The full nine-case/two-sweep acceptance criterion was not met. Do not promote
the partial subset to a confirmed classification or proceed to design.

## Evidence Of Treatment

This is native classification/control feasibility with an in-process reviewer
stub, not a paid-model comparison. Before interpreting the subset, capture
checks verified two observed distributions, actual compatible-control commands,
both logged stub receipts and their original UTF-8 bytes/hashes.

Actual distribution records:

```jsonl
{"event": "verified_distribution", "executable": "<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "go_sha256": "5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620", "gofmt_sha256": "6624039b8bc726fe310dffc7f6d42e3a70b871639f725117d166299cecfe53bb", "root": "<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64", "version": "1.26.9"}
{"event": "verified_distribution", "executable": "C:\\Program Files\\Go\\bin\\go.exe", "go_sha256": "83b7ba66215e696414fa49462d0db2da4f4cf15c7bebd42f0b189fa04866999d", "gofmt_sha256": "42f76ab97ca449d419f9cb19b0245cbd02af4b75170d27445f888722c7931ff3", "root": "C:\\Program Files\\Go", "version": "1.27.3"}
```

The valid higher-minimum fixture failed under selected Go 1.26.9 and passed
the four bounded formatter/build/vet/test controls under Go 1.27.3. Its source
hashes matched. Both normal/degraded stub calls are real receipts; only the
degraded receipt includes the explicit warning and separate control results.
Raw prompt sizes were 2259 and 2421 UTF-8 bytes,
not token estimates. These sizes/hashes apply before public path substitutions.

The mixed minimum/compile fixture also failed under the compatible control
and did not reach the stub. Treatment was exercised for this subset only;
the incomplete timeout observation and remaining cases are not passed checks.

## Command And Complete Captured Output

The wrapper invoked the separately approved driver from the worktree root;
only the output-directory path is labelled below:

```text
python poc\review-tooling-continuation\spike-control-1.27.3.py --output <REVISED_TRIAL_DIRECTORY>
```

Complete stdout/stderr capture, with declared profile/trial path substitutions:

```text
{"classification": "normal", "fixture": "compatible-valid", "prompt_bytes": 2259, "reason": "all bounded selected checks passed", "source_sha256_after": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "source_sha256_before": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "stub_calls": 1, "sweep": 1}
{"classification": "degraded", "fixture": "higher-minimum-valid", "prompt_bytes": 2421, "reason": "verified selected version is below declared minimum; identical control passes", "source_sha256_after": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "source_sha256_before": "fb422d54b17847444916815526f580a9e0d87fb2594c777323b317a2ec23d79a", "stub_calls": 1, "sweep": 1}
{"classification": "source_or_mixed", "fixture": "compile-defect", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "23ab80cc0d40760f29d3c45b11945db7a357476b17a3f2e146a737de1fce4058", "source_sha256_before": "23ab80cc0d40760f29d3c45b11945db7a357476b17a3f2e146a737de1fce4058", "stub_calls": 0, "sweep": 1}
{"classification": "source_or_mixed", "fixture": "failing-assertion", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "79c01eb8b63d2475ca30317435e2739040875804e080b07e5cb7345d741d5d8e", "source_sha256_before": "79c01eb8b63d2475ca30317435e2739040875804e080b07e5cb7345d741d5d8e", "stub_calls": 0, "sweep": 1}
{"classification": "source_or_mixed", "fixture": "higher-minimum-compile-defect", "prompt_bytes": 0, "reason": "compatible control also has failed or unchecked gates", "source_sha256_after": "894b5d63a2869de5706dbdaeeb2ee51174063c672f39636d510ba56e7252872c", "source_sha256_before": "894b5d63a2869de5706dbdaeeb2ee51174063c672f39636d510ba56e7252872c", "stub_calls": 0, "sweep": 1}
{"classification": "unknown", "fixture": "missing-requested-executable", "prompt_bytes": 0, "reason": "selection or frozen-input identity is not established", "source_sha256_after": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "source_sha256_before": "de5ed62d530741575d426e964d5264342a003fd11f3745dfcdb4c73dc34e4b43", "stub_calls": 0, "sweep": 1}
{"completed_cases": 6, "detail": "slow fixture did not reach marker then time out", "driver_sha256": "f76ecec9e14ce32fda6b3121ef17c4a7d4721451e534b659174494e42e14e67f", "elapsed_seconds": 107.29989699996077, "model_calls": 0, "native_commands": 35, "stub_receipts": 2, "verdict": "Inconclusive"}
```

Observed driver exit code: 2. The batch was not retried. Elapsed seconds,
counts and durations are actual captured values, not performance claims.

## Partial Observations

| First-sweep fixture | Classification | Actual stub calls |
|---|---|---|
| compatible-valid | normal | 1 |
| higher-minimum-valid | degraded | 1 |
| compile-defect | source_or_mixed | 0 |
| failing-assertion | source_or_mixed | 0 |
| higher-minimum-compile-defect | source_or_mixed | 0 |
| missing-requested-executable | unknown | 0 |

The seventh case compiled its test binary but did not finish its required
entry-marker/timeout observation. The simulated control-runner error,
changed-snapshot case and all of sweep two were unrun. Zero paid model calls.

## Timeout Failure And Safety

The timeout command's complete captured stderr:

```text
Command timed out after 2 seconds.
atom: Windows cleanup incomplete: owned job member did not signal exit; [WinError 5] TerminateProcess: Access is denied.; owned primary process did not exit; output incomplete: stdout, stderr
```

Captured stdout was empty and explicitly incomplete. Therefore we cannot tell
from this capture whether the Go test entered; neither buffering nor a failure
to enter is established as the cause. Earlier formatting/build/vet and test
compilation passed, but they do not repair this cleanup or collection failure.

A later read-only process query, scoped to the trial time window and exact
TestWait invocation, found no surviving matching process. No unrelated process
was stopped. This does not retroactively establish clean timeout handling.
Windows runner diagnosis is a separate proposed next step, not an implemented
repair or a proved explanation of the parent CI failures.

## Complete Native Command Results

All 35 native command results, including every failure and untruncated captured
stream, are retained here. JSON values are projected only for declared paths;
full original event lines, including launch environment records, stay outside Git.

```jsonl
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "version"], "directory": "<REVISED_TRIAL_DIRECTORY>", "duration_seconds": 0.38170010002795607, "event": "command", "exit_code": 0, "index": 1, "outcome": "completed", "stderr": "", "stdout": "go version go1.26.9 windows/amd64\n"}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV"], "directory": "<REVISED_TRIAL_DIRECTORY>", "duration_seconds": 0.03680810006335378, "event": "command", "exit_code": 0, "index": 2, "outcome": "completed", "stderr": "", "stdout": "{\n\t\"GOENV\": \"<LOCAL_PROFILE>\\\\AppData\\\\Roaming\\\\go\\\\env\",\n\t\"GOROOT\": \"<LOCAL_PROFILE>\\\\go\\\\pkg\\\\mod\\\\golang.org\\\\toolchain@v0.0.1-go1.26.9.windows-amd64\",\n\t\"GOTOOLCHAIN\": \"local\",\n\t\"GOVERSION\": \"go1.26.9\"\n}\n"}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "version"], "directory": "<REVISED_TRIAL_DIRECTORY>", "duration_seconds": 0.4387396000092849, "event": "command", "exit_code": 0, "index": 3, "outcome": "completed", "stderr": "", "stdout": "go version go1.27.3 windows/amd64\n"}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV"], "directory": "<REVISED_TRIAL_DIRECTORY>", "duration_seconds": 0.06081240007188171, "event": "command", "exit_code": 0, "index": 4, "outcome": "completed", "stderr": "", "stdout": "{\n\t\"GOENV\": \"<LOCAL_PROFILE>\\\\AppData\\\\Roaming\\\\go\\\\env\",\n\t\"GOROOT\": \"C:\\\\Program Files\\\\Go\",\n\t\"GOTOOLCHAIN\": \"local\",\n\t\"GOVERSION\": \"go1.27.3\"\n}\n"}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compatible-valid", "duration_seconds": 0.052725199959240854, "event": "command", "exit_code": 0, "index": 5, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compatible-valid", "duration_seconds": 0.42000679997727275, "event": "command", "exit_code": 0, "index": 6, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "vet", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compatible-valid", "duration_seconds": 33.79947710002307, "event": "command", "exit_code": 0, "index": 7, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "test", "-count=1", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compatible-valid", "duration_seconds": 8.103122900007293, "event": "command", "exit_code": 0, "index": 8, "outcome": "completed", "stderr": "", "stdout": "ok  \texample.invalid/continuation\t2.595s\n"}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-valid", "duration_seconds": 0.04660390003118664, "event": "command", "exit_code": 0, "index": 9, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-valid", "duration_seconds": 0.0405266999732703, "event": "command", "exit_code": 1, "index": 10, "outcome": "completed", "stderr": "go: go.mod requires go >= 1.27.0 (running go 1.26.9; GOTOOLCHAIN=local)\n", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-valid", "duration_seconds": 0.07343049999326468, "event": "command", "exit_code": 0, "index": 11, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-valid", "duration_seconds": 0.5422846999717876, "event": "command", "exit_code": 0, "index": 12, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "vet", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-valid", "duration_seconds": 25.916019500000402, "event": "command", "exit_code": 0, "index": 13, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "test", "-count=1", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-valid", "duration_seconds": 6.627409400069155, "event": "command", "exit_code": 0, "index": 14, "outcome": "completed", "stderr": "", "stdout": "ok  \texample.invalid/continuation\t2.513s\n"}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compile-defect", "duration_seconds": 0.0544966000597924, "event": "command", "exit_code": 0, "index": 15, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compile-defect", "duration_seconds": 0.19321880000643432, "event": "command", "exit_code": 1, "index": 16, "outcome": "completed", "stderr": "# example.invalid/continuation\n.\\fixture.go:5:40: undefined: missingValue\n", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compile-defect", "duration_seconds": 0.04193419998046011, "event": "command", "exit_code": 0, "index": 17, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\compile-defect", "duration_seconds": 0.10086379991844296, "event": "command", "exit_code": 1, "index": 18, "outcome": "completed", "stderr": "# example.invalid/continuation\n.\\fixture.go:5:40: undefined: missingValue\n", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 0.05014840001240373, "event": "command", "exit_code": 0, "index": 19, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 0.1663840999826789, "event": "command", "exit_code": 0, "index": 20, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "vet", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 0.5617948001017794, "event": "command", "exit_code": 0, "index": 21, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "test", "-count=1", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 4.776321699959226, "event": "command", "exit_code": 1, "index": 22, "outcome": "completed", "stderr": "", "stdout": "--- FAIL: TestAdd (0.00s)\n    fixture_test.go:7: Add(2, 3) = 5; want 6\nFAIL\nFAIL\texample.invalid/continuation\t2.623s\nFAIL\n"}
{"argv": ["C:\\Program Files\\Go\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 0.02523469994775951, "event": "command", "exit_code": 0, "index": 23, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 0.16157130000647157, "event": "command", "exit_code": 0, "index": 24, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "vet", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 0.29702449997421354, "event": "command", "exit_code": 0, "index": 25, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "test", "-count=1", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\failing-assertion", "duration_seconds": 13.483362499973737, "event": "command", "exit_code": 1, "index": 26, "outcome": "completed", "stderr": "", "stdout": "--- FAIL: TestAdd (0.00s)\n    fixture_test.go:7: Add(2, 3) = 5; want 6\nFAIL\nFAIL\texample.invalid/continuation\t11.589s\nFAIL\n"}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-compile-defect", "duration_seconds": 0.0678006000816822, "event": "command", "exit_code": 0, "index": 27, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-compile-defect", "duration_seconds": 0.059104899992235005, "event": "command", "exit_code": 1, "index": 28, "outcome": "completed", "stderr": "go: go.mod requires go >= 1.27.0 (running go 1.26.9; GOTOOLCHAIN=local)\n", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-compile-defect", "duration_seconds": 0.03631859994493425, "event": "command", "exit_code": 0, "index": 29, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["C:\\Program Files\\Go\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\higher-minimum-compile-defect", "duration_seconds": 0.12962139991577715, "event": "command", "exit_code": 1, "index": 30, "outcome": "completed", "stderr": "# example.invalid/continuation\n.\\fixture.go:5:40: undefined: missingValue\n", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe", "-l", "."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\slow-test", "duration_seconds": 0.047099599963985384, "event": "command", "exit_code": 0, "index": 31, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "build", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\slow-test", "duration_seconds": 0.18666669994127005, "event": "command", "exit_code": 0, "index": 32, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "vet", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\slow-test", "duration_seconds": 0.5070663999067619, "event": "command", "exit_code": 0, "index": 33, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "test", "-c", "-o", "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\slow-test\\warm.test.exe"], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\slow-test", "duration_seconds": 4.336350300000049, "event": "command", "exit_code": 0, "index": 34, "outcome": "completed", "stderr": "", "stdout": ""}
{"argv": ["<LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe", "test", "-v", "-count=1", "-run", "TestWait", "./..."], "directory": "<REVISED_TRIAL_DIRECTORY>\\fixtures\\sweep-1\\slow-test", "duration_seconds": 4.038185499957763, "event": "command", "exit_code": null, "index": 35, "outcome": "timed_out", "stderr": "Command timed out after 2 seconds.\natom: Windows cleanup incomplete: owned job member did not signal exit; [WinError 5] TerminateProcess: Access is denied.; owned primary process did not exit; output incomplete: stdout, stderr", "stdout": ""}
```

## Actual Reviewer-Stub Receipts

Both complete receipts are retained. Failed selected build and skipped vet/test
remain visible in the degraded prompt and do not appear among exclusions.
Compatible-control passes are separate, not validation of the requested compiler.
The stub receives toolchain evidence only; no real review or full diff/CLI
integration is claimed.

```jsonl
{"bytes": 2259, "event": "stub_receipt", "prompt": "BOUNDED POC REVIEW: not a full toolchain gate.\nRequested Go: 1.26.9 (source: cli; project version: not configured).\nGo selection: verified; observed Go: 1.26.9.\nExecutable: <LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe (source: module_cache).\nGo SHA-256: before=5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620, after=5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620.\nGOROOT: <LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\nSelected-root formatter: <LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe.\ngofmt SHA-256: before=6624039b8bc726fe310dffc7f6d42e3a70b871639f725117d166299cecfe53bb, after=6624039b8bc726fe310dffc7f6d42e3a70b871639f725117d166299cecfe53bb.\nSelection scope: direct Go/gofmt gates only. Advisory analyzer internals and arbitrary descendants are not independently attested.\n\nA Go toolchain ran over this code before review. These results are mechanical proof, not opinion.\n\n  gofmt (changed Go files)  PASSED - completed; exit=0\n\n  go build ./...            PASSED\n  go vet ./...              PASSED\n  go test ./...             PASSED\n  go test -race ./...       SKIPPED - outside bounded POC scope\n  staticcheck ./...         SKIPPED - outside bounded POC scope\n  errcheck ./...            SKIPPED - outside bounded POC scope\n  govulncheck ./...         SKIPPED - outside bounded POC scope\n\nDo not report these mechanically checked categories: formatting in the checked files only, build errors, vet diagnostics (printf verb mismatches, lost cancel, copied locks), and failing tests.\n\nWhat these tools cannot see: the race detector only observes paths the tests actually executed, so untested concurrent code is unchecked. errcheck finds discarded errors, not errors caught and handled wrongly. govulncheck finds known vulnerabilities in dependencies, not unsafe handling of input in this code. No tool here judges whether a name misleads a reader, whether a function has grown too long to follow, or whether this change will be easy to extend without editing existing behaviour.\n\nA clean tool run is not evidence a problem is absent; it is evidence that one specific tool did not see it.", "sha256": "46b973e804aae0a04c8ce9e58faed3fece31df09424b4bb5df36d50348b2e88f"}
{"bytes": 2421, "event": "stub_receipt", "prompt": "DEGRADED REVIEW: requested-compiler checks did not pass. Control passes do not validate the requested compiler.\nRequested Go: 1.26.9 (source: cli; project version: not configured).\nGo selection: verified; observed Go: 1.26.9.\nExecutable: <LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\go.exe (source: module_cache).\nGo SHA-256: before=5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620, after=5b25a4a434c7bbba11112a94c3fa9c1502c0f377bd971705ee8e07b8e3c12620.\nGOROOT: <LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\nSelected-root formatter: <LOCAL_PROFILE>\\go\\pkg\\mod\\golang.org\\toolchain@v0.0.1-go1.26.9.windows-amd64\\bin\\gofmt.exe.\ngofmt SHA-256: before=6624039b8bc726fe310dffc7f6d42e3a70b871639f725117d166299cecfe53bb, after=6624039b8bc726fe310dffc7f6d42e3a70b871639f725117d166299cecfe53bb.\nSelection scope: direct Go/gofmt gates only. Advisory analyzer internals and arbitrary descendants are not independently attested.\n\nA Go toolchain ran over this code before review. These results are mechanical proof, not opinion.\n\n  gofmt (changed Go files)  PASSED - completed; exit=0\n\n  go build ./...            FAILED - completed; exit=1\n  go vet ./...              SKIPPED - earlier bounded gate failed\n  go test ./...             SKIPPED - earlier bounded gate failed\n  go test -race ./...       SKIPPED - outside bounded POC scope\n  staticcheck ./...         SKIPPED - outside bounded POC scope\n  errcheck ./...            SKIPPED - outside bounded POC scope\n  govulncheck ./...         SKIPPED - outside bounded POC scope\n\nDo not report these mechanically checked categories: formatting in the checked files only.\n\nWhat these tools cannot see: the race detector only observes paths the tests actually executed, so untested concurrent code is unchecked. errcheck finds discarded errors, not errors caught and handled wrongly. govulncheck finds known vulnerabilities in dependencies, not unsafe handling of input in this code. No tool here judges whether a name misleads a reader, whether a function has grown too long to follow, or whether this change will be easy to extend without editing existing behaviour.\n\nA clean tool run is not evidence a problem is absent; it is evidence that one specific tool did not see it.\nCompatible control (same frozen source, not selected validation):\nfmt: passed\nbuild: passed\nvet: passed\ntest: passed", "sha256": "db3371b2c3227588b57abcde99a1d713e0f3764908d5ae98277079dc6ce9910a"}
```

## Provenance And Scope

| Preserved input/capture | Raw SHA-256 |
|---|---|
| Revised executed driver | `f76ecec9e14ce32fda6b3121ef17c4a7d4721451e534b659174494e42e14e67f` |
| Original unchanged driver | `024837611d39834073fccfe8e8bb03818abca6360aab6910741fd6031581ba24` |
| Complete outside-Git stdout/stderr | `d856f9731d103ce832a562c51961873b24a1d46b112e841e2a0803b2e0f0eaeb` |
| Complete outside-Git launch/command/receipt events | `5c50b49718fc80928f97d7c0ffaf693fead48f4a6a6c4a137d4d8a73afb10985` |
| Outside-Git summary | `1337f8b8b40231ca28a7f07ce452c002bee7a74de6ce9276e873a07300b5b5a7` |

Raw captures and generated fixtures remain outside Git. Public replacements
are `<LOCAL_PROFILE>` and `<REVISED_TRIAL_DIRECTORY>`, including escaped forms.
Stack base remains `2685490718c59d24b0d412fac0c5bb9e0ded9a15`.
The [original Inconclusive report](poc-report.md),
[revised brief](poc-brief-control-1.27.3.md) and
[executed revised driver](../../poc/review-tooling-continuation/spike-control-1.27.3.py)
remain separately inspectable. No production source/test change or publication.

## What We Learned And What Changes

The installed Go 1.27.3 control can exercise the declared Go-minimum comparison.
The completed subset demonstrates why a compatible control matters: a compiler
minimum can mask a compile defect, which the compatible control then exposes.
These observations support the narrow premise but do not close the full proof.

The new blocker is native timeout cleanup/output reliability. Do not simply
increase deadlines, remove the marker, switch to direct test-binary execution
or reinterpret partial results as success. Any changed treatment or repeat
batch needs approval; first diagnose the observed Windows runner failure.

## Explicitly Not Covered

No reliable slow-test timeout signal, control-runner-error simulation,
changed-snapshot result or repeated sweep is established. No native race/CGO,
dependencies, analyzers, cross-platform readiness, full review integration or
model-quality claim is supported. Parent macOS/Windows CI remains unresolved.

## Recommendation And Gate

Keep this POC Inconclusive. Seek approval for bounded Windows runner diagnosis
before another experiment; no design, fix, retry or paid review is authorized
by these partial results.
