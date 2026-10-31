# Exact Go Multi-Model Review

Status: **two independent reviews completed; final unchanged Python gate passed; earlier handle-count failure retained**.

Earlier batch sections are historical. The final section records a subsequent tested author-found correction.

## First Approved Batch (Historical)

The developer approved one fixed-evidence review each from the two runtime-default
models, with availability probes, 300-second review deadlines and no retries.
The input was 780615 UTF-8 bytes, SHA-256
`4fe61a7cded1253bbe4eeaf6f17a3f0db44e8852dc9dd6f4ac114ebdff68e0d6`, covering twenty changed code/test/guidance/archived
driver files with complete current files and supporting context.

| Model | Availability | Reviews completed/requested |
|---|---|---|
| gpt-5.4 | Unavailable | 0/1 |
| gemini-3.8-flash | Available | 0/1 |

Three commands actually ran: two availability probes and the Gemini review
attempt. GPT's review was never invoked. Neither failure was a timeout.

Actual GPT availability command:

```text
copilot -p ping --silent --model gpt-5.4 --no-custom-instructions --disable-builtin-mcps --excluded-tools builtin:* custom:* mcp:*
Error: Model "gpt-5.4" from --model flag is not available.
exit code: 1
```

Actual Gemini review command and error copied from its structured stdout:

```text
copilot --output-format json --model gemini-3.8-flash --no-custom-instructions --disable-builtin-mcps --excluded-tools builtin:* custom:* mcp:*
Execution failed: Request exceeds the model's prompt budget after reserving output (203090 tokens; limit 200000). Reduce context or compact before continuing.
exit code: 1
```

No usable findings were produced. This is **not a clean review**. No source
fix, commit, push or PR has been performed. No second paid batch is authorized.
The already accepted Windows Python gate and later focused native test remain
unchanged; Linux/macOS evidence remains pending actual CI.

The review gate mistakenly described 300 seconds as the existing timeout.
The library default is actually 600 seconds. This batch explicitly used the
approved stricter 300-second limit; that did not cause either observed failure.

Proposed next batch, not executed: replace the unavailable default with a
distinct non-author reviewer and retain Gemini; remove duplicate new-file
diff text while retaining every complete changed file, tracked diff and all
supporting context. Re-gate before any further model call.

Untouched original POC/TDD artifacts and raw model captures remain outside Git.
The approved path-redacted publication copies were prepared and byte-verified;
see [publication evidence](../publication-evidence.md). Publication still waits
for successful review and triage.

## Approved Replacement Batch

Both replacement models passed their availability probes. Four commands ran:
two probes and two review attempts. Complete file/context input was retained;
only redundant new-file diff text was removed. Input: 721289
UTF-8 bytes, SHA-256 `891bd89e0334776c3568a6d6af11aeacc581ac74ca3e1329b845ed2a30d958ec`.

| Model | Review outcome | Completed/requested | Observed duration (seconds) |
|---|---|---|---|
| claude-sonnet-5.5 | Failed before query: prompt budget | 0/1 | 11.416180100059137 |
| gemini-3.8-flash | Completed, readable fixed-evidence response | 1/1 | 297.4306458000792 |

Actual failed-query diagnostic copied from structured stdout:

```text
Execution failed: Request exceeds the model's prompt budget after reserving output (226156 tokens; limit 200000). Reduce context or compact before continuing.
```

The completed Gemini response was decoded by Atom's fixed-evidence/root-response
validator and was exactly:

```json
[]
```

Gemini reported no consequential findings. That is one independent review, not
a completed two-model review. Claude's failure was not a timeout. No source bug
was reported, fixed or silently rejected; no commit, push or PR was performed.
All twenty code/test/guidance/driver snapshot hashes remain unchanged.

Proposed next step, not authorized or run: retain the completed Gemini result and
run only the pending Claude review with the CLI's larger-context setting and the
actual 600-second default deadline. This requires a fresh bounded spend gate;
do not rerun Gemini or discard either failed-batch denominator.

The pre-commit Python gate must be rerun if publication becomes unblocked.
Native Linux/macOS remains pending actual CI.

## Claude-Only Larger-Context Batch And Final Triage

The developer selected "Approve Claude-only long-context batch". One matching
availability probe and one review ran with long_context and a 600-second owned
deadline. Claude completed in 65.40789499995299 seconds. Gemini's
already completed response was retained; it was not rerun.

Both successful reviewers received the same complete twenty-file/context prompt,
SHA-256 `891bd89e0334776c3568a6d6af11aeacc581ac74ca3e1329b845ed2a30d958ec`. Tool access was excluded and both final root
responses passed fixed-evidence validation. Reviewer models differ from the
primary authoring model. At that model-review snapshot, no source/test/guidance/archived-driver byte had changed.

| Reviewer | Completed usable reviews | Raw finding count |
|---|---|---|
| gemini-3.8-flash | 1/1 retained | 0 |
| claude-sonnet-5.5 | 1/1 larger context | 2 |

### Merged Findings

| Severity | Agreement | Location | Finding | Disposition |
|---|---|---|---|---|
| Minor (model: low) | 1/2 | tools/atom/go_selection.py:238 | Empty GOENV in minimal environments is rejected | Deferred: approved policy requires all four observed environment fields to be non-empty. Supporting empty GOENV would change that contract. Callers may explicitly use GOENV=off; no automatic setting change is introduced. |
| Minor (model: low) | 1/2 | tools/atom/go_selection.py:222 | Experiment-labelled version output is rejected | Rejected as outside scope: exact stable version output and exact GOVERSION are deliberate checks. Widening/removing the probe would change the approved stable-distribution contract; no ordinary stable-release regression was established. |

Both single-model findings were read individually, not discarded for lack of
agreement. At model triage there were no Blocker/Major findings or production changes; the subsequent correction is recorded below.
The empty-GOENV limitation is retained in findings.md and the PR notes.

Actual Claude root response, copied from the validated structured output:

```json
[
  {
    "file": "tools/atom/go_selection.py",
    "line": 238,
    "severity": "low",
    "message": "Every field in the `go env -json` output, including GOENV, must be a non-empty string. Go can report GOENV as an empty string when no user config directory resolves, for example a minimal container with neither HOME nor XDG_CONFIG_HOME set. A correct installed distribution would then fail with `verification_failed` (\"missing or malformed Go environment fields\"). Suggested fix: require GOENV to be a string but allow it to be empty, and keep the non-empty requirement for GOVERSION, GOROOT and GOTOOLCHAIN."
  },
  {
    "file": "tools/atom/go_selection.py",
    "line": 222,
    "severity": "low",
    "message": "The version probe regex `go version go<ver> \\S+\\s*` accepts exactly one platform token. A Go build whose `go version` output has an extra experiment token, such as `go1.26.9 X:foo linux/amd64`, is rejected even though the version, root and hash checks that follow would pass. The failure is explicit, not silent. Suggested fix: match `go version go<ver>(\\s+\\S+)+\\s*`, or drop this probe in favour of the exact GOVERSION check from `go env`."
  }
]
```

### Reviewed-Snapshot Pre-Commit Verification (Before Subsequent Correction)

The approved Python-project replacement for root atom check was rerun for the
reviewed snapshot alongside the final independent review. The later correction's gate follows below. Full original
bytes are retained outside Git, SHA-256 `14a0d3efde296ba70f049542bb0c7d98762b367f6f6eb898a1ab54a1430e32ab`.
The publication copy substitutes only labelled local path prefixes.

```text
python -m pytest tests -v --cov=atom --cov-report=term-missing

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   366     21    94%   107-108, 372-373, 383-393, 415-425, 684, 875
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      6    97%   91, 407-408, 412, 462, 472
atom\go_selection.py          220      3    99%   97, 181, 279
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                396     10    97%   193, 208, 220, 234, 250, 252, 259, 931, 933, 935
atom\review.py                131      0   100%
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              72      4    94%   124, 180, 188, 190
---------------------------------------------------------
TOTAL                        4508    223    95%
================= 1614 passed, 5 skipped in 209.39s (0:03:29) =================
EXIT CODE: 0
```

Complete path-redacted output is appended to [TDD evidence](tdd-evidence.md).
Native Linux/macOS, successful native Go race/CGO execution and real dependency
compatibility remain unestablished locally. Publication is explicitly authorized;
actual native CI evidence still must not be claimed before it runs.

## Subsequent Author-Found Canonical-Root Correction

Publication inspection found that executable path/hash equality alone could
accept a different observed GOROOT whose bin/go resolves to the selected binary.
This is a Minor contract-enforcement gap, not a finding from either model.
Approved behavior 7 already requires the observed root to match the selected
distribution. Add one independent canonical-root equality check and one focused
regression; do not broaden the policy or weaken any existing expectation.

The regression produced the clean assertion failure `DID NOT RAISE
GoToolchainSelectionError` before production was changed. The corrected selector
and coupled review/CLI tests then passed: 179 passed. The alias is controlled
filesystem-I/O simulation, not a claimed native junction/symlink reproduction.
Complete RED/GREEN and final gate captures are in [TDD evidence](tdd-evidence.md).

The successful models reviewed the earlier snapshot, not this later check/test.
All other reviewed source, test, guidance and driver hashes remain unchanged.
No additional paid review or retry was run; this tested amendment is explicitly
distinguished from the independent model-review evidence.

Final Windows Python gate after the correction (complete capture SHA-256
`421c207d9e59b9fd520bc9cb3916182d0570b00103f74ab97710d8b36de4e9b8`; public output substitutes local path prefixes):

```text
python -m pytest tests -v --cov=atom --cov-report=term-missing
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   366     21    94%   107-108, 372-373, 383-393, 415-425, 684, 875
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      6    97%   91, 407-408, 412, 462, 472
atom\go_selection.py          220      3    99%   97, 181, 280
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                396     10    97%   193, 208, 220, 234, 250, 252, 259, 931, 933, 935
atom\review.py                131      0   100%
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              72      4    94%   124, 180, 188, 190
---------------------------------------------------------
TOTAL                        4508    223    95%
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers - AssertionError: native handles leaked across command runs
assert 330 <= 328
 +  where 330 = <function test_windows_repeated_runs_release_handles_and_workers.<locals>.handle_count at 0x00000204F8AF2DE0>()
============ 1 failed, 1614 passed, 5 skipped in 214.87s (0:03:34) ============
EXIT CODE: 1
```

Native Linux/macOS and successful native race/CGO or real dependency compatibility
remain pending actual evidence; the synthetic Windows fixture cannot prove them.

## Final Verification Blocker

The post-correction complete Python gate failed: 1 failed, 1614 passed, 5 skipped.
test_windows_repeated_runs_release_handles_and_workers observed 330 handles
against a baseline of 328 at tools/tests/test_windows_process.py:761.
Its original strict assertions passed in a separate focused run (1 passed);
that does not erase the full-suite failure or establish its cause.

No handle-cleanup assertion, tolerance, skip or production workaround was added.
Publication is paused; no commit, push or PR occurred. A bounded unchanged full
rerun versus further native-handle diagnosis requires the developer's decision.
The full failure and isolated result remain distinct evidence, not a clean gate.

## Approved Unchanged Full Rerun

After the full gate's handle-count failure and the isolated strict assertion
pass, the developer explicitly approved one unchanged full-suite rerun.
Actual result: 1615 passed, 5 skipped in 176.32s, 95% coverage, exit 0.
No production code, test assertion, tolerance or skip changed between runs.
The previously failed handle test passed in this full rerun.

The original full-suite failure remains retained, not relabelled as success.
Its cause remains unexplained; the passing rerun is not a handle-cleanup fix.
The final source gate is green. Carry the earlier failure into findings and PR
notes, alongside pending native Linux/macOS and race/CGO/dependency evidence.

Review token-budget preflight and viable plan proposal are separately tracked
in girishmotwani/atom#14. No budget implementation or additional model call
is included in this exact-Go phase.

Final full-gate excerpt (complete output in TDD evidence):

```text

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   366     21    94%   107-108, 372-373, 383-393, 415-425, 684, 875
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      6    97%   91, 407-408, 412, 462, 472
atom\go_selection.py          220      3    99%   97, 181, 280
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                396     10    97%   193, 208, 220, 234, 250, 252, 259, 931, 933, 935
atom\review.py                131      0   100%
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              72      4    94%   124, 180, 188, 190
---------------------------------------------------------
TOTAL                        4508    223    95%
================= 1615 passed, 5 skipped in 176.32s (0:02:56) =================
EXIT CODE: 0
```
