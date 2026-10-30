# TDD evidence: default launch-module review guidance

Design: [approved design-spec.md](design-spec.md). Coverage: [test-spec.md](test-spec.md).

Implementation captures both optional launch-local rule files before PR preparation, shares one immutable policy packet across requested runs, preserves fixed-evidence and opt-out source exclusions, and reports only policy metadata. No extra model calls, installation or publishing were performed.

## Observed RED: missing policy in native runner input

Command: python -m pytest tests\test_module_rules.py -k every_run -q --tb=short

The missing keyword was first added without composition to reach this actual assertion failure, rather than treating a TypeError as behavior proof:

```text
================================== FAILURES ===================================
______________ test_review_delivers_frozen_guidance_to_every_run ______________
tests\test_module_rules.py:162: in test_review_delivers_frozen_guidance_to_every_run
    assert "MODULE_SENTINEL" in prompts[0]
E   AssertionError: assert 'MODULE_SENTINEL' in 'You are reviewing a Go diff. Report real problems only.\nThe Go toolchain did not run before this review.\nReason: to...cache.go\n--- a/store/cache.go\n+++ b/store/cache.go\n@@ -40,0 +41,3 @@\n+func Export() {}\n+var x = 1\n+var y = 2\n\n'
=========================== short test summary info ===========================
FAILED tests/test_module_rules.py::test_review_delivers_frozen_guidance_to_every_run
====================== 1 failed, 18 deselected in 0.22s =======================
```

Subsequent RED logs outside Git cover invalid metadata/fixed-mode snapshots, dangling and denied traversal, CLI capture/failure timing, report provenance and opt-out status. GREEN outputs were captured after the corresponding implementations. The full log directory is machine-local session evidence, not a production dependency; raw absolute profile paths are not copied into this artifact.

## Targeted GREEN

Command: python -m pytest tests\test_module_rules.py tests\test_cli_review.py tests\test_cli_pr_review.py tests\test_context.py tests\test_review_output.py tests\test_review_toolchain.py tests\test_review_formatting.py -q --tb=short

```text
======================= 258 passed, 3 skipped in 48.42s =======================
```

This combined run preceded the final duplicate/order/full-JSON-packet regression additions and documentation reconciliation. The complete gate below includes those changes.

## Full repository gate

Command, from tools: python -m pytest tests -v --cov=atom --cov-report=term-missing

Exit code 0. Verbatim coverage and result excerpt; the complete unedited pytest stream is preserved outside Git as module-rules-full-tests.txt:

```text

=============================== tests coverage ================================
______________ coverage: platform win32, python 3.13.14-final-0 _______________

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      374     28    93%   187-189, 239, 293, 301, 330-334, 341-343, 346-347, 361, 370-371, 389, 398, 439-440, 464, 466, 539-540, 589, 597
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   357     21    94%   103-104, 360-361, 371-381, 403-413, 664, 846
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      7    96%   91, 321, 407-408, 412, 462, 472
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           48      2    96%   52-53
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                385     10    97%   191, 206, 218, 232, 248, 250, 257, 889, 891, 893
atom\review.py                113      0   100%
atom\runner.py                169     52    69%   117-183, 227, 233, 266-270, 303-315, 327-331, 342-353, 370, 425
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              58      5    91%   120, 145, 147, 155, 157
---------------------------------------------------------
TOTAL                        4181    220    95%
================= 1501 passed, 5 skipped in 193.56s (0:03:13) =================
```

## Documentation and diff checks

Commands: python tools\check_links.py; git --no-pager diff --check; byte-compare the canonical and packaged Go guidance.

Actual output before this final artifact update; all commands exited 0:

```text
checked 303 relative links across markdown files
all relative links resolve
Packaged Go guidance matches canonical source.
```

## Limits and gate

The five full-suite skips include two baseline skips and three Windows link fixtures denied by winerror 1314. Deterministic OS-boundary cases execute confinement, dangling resolution, duplicate targets and denied traversal/read paths; native link coverage remains platform-limited. New loader coverage is 96%; the missing-root error wrapper is not exercised by these fixtures. No new concurrency or Go module was introduced, so repository pytest is the applicable gate, not a root atom check or a new race claim.

Both original POC verdicts remain Inconclusive. Accepted one-provider delivery plus these deterministic tests do not establish causal rule influence, comprehensive compliance or improved review quality. Portable toolchain selection and degraded review on tooling incompatibility remain separate pending requests. No paid multi-model review, installation, commit or push is authorized by implementation completion.
## Post-review shipping gate

The developer approved the independent-review triage corrections and continuation to commit/push after verification. Three real non-directory-parent cases failed before the fix, then passed; the ambient-policy test reproduction now passes with unchanged output assertions. Independent review details and rejected advice are preserved in [review.md](review.md). No second paid review was performed.

Final command from tools: python -m pytest tests -v --cov=atom --cov-report=term-missing. Exit 0; verbatim coverage and result:

```text

=============================== tests coverage ================================
______________ coverage: platform win32, python 3.13.14-final-0 _______________

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      374     28    93%   187-189, 239, 293, 301, 330-334, 341-343, 346-347, 361, 370-371, 389, 398, 439-440, 464, 466, 539-540, 589, 597
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   357     21    94%   103-104, 360-361, 371-381, 403-413, 664, 846
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      7    96%   91, 321, 407-408, 412, 462, 472
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                385     10    97%   191, 206, 218, 232, 248, 250, 257, 889, 891, 893
atom\review.py                113      0   100%
atom\runner.py                169     52    69%   117-183, 227, 233, 266-270, 303-315, 327-331, 342-353, 370, 425
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              58      5    91%   120, 145, 147, 155, 157
---------------------------------------------------------
TOTAL                        4185    220    95%
================= 1504 passed, 5 skipped in 198.94s (0:03:18) =================
```

A subsequent whitespace check caught an extra blank line introduced while rewriting design-spec.md through the artifact writer. Its trailing newline was normalized using that same approved writer; no source or test changed after the final Python gate. Documentation links and final staged whitespace are checked again before commit.
