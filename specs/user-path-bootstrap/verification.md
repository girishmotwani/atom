# Verification: Opt-in Windows user-PATH setup

## Instruction fix already published

Commit `16ac6bccab326ac856a9a912a67f1b0a318a0073` was pushed to origin/main and verified with git ls-remote. Only the six approved onboarding instruction/test files were included.

## Red/green evidence

New behavior was observed failing before implementation: setup-path parser reachability; command execution with an isolated registry; six equivalent existing-directory forms; non-Windows rejection; unsupported registry types; absent key/value handling; registry permission failures; notification timeout/OS-error partial state; delimiter/NUL directory rejection; BMP/non-BMP UTF-16 length boundaries; discovery OS errors; literal PowerShell path quoting; and the three documentation contracts. Each corresponding targeted run became green before continuing.

Additional regression cases characterize already-working script-pair selection, default-scheme preference, HKCU-only writes, unchanged process environment, native pointer ABI, and init isolation. They were not claimed to have demanded new implementation.

## Affected suite

Command:

```text
python -m pytest tools\tests\test_pathsetup.py tools\tests\test_cli.py tools\tests\test_cli_state.py tools\tests\test_artifact_cli.py tools\tests\test_onboarding.py -q --tb=short
```

Captured result:

```text
============================ 113 passed in 15.38s =============================
```

Exit code: 0. The chained scoped git diff --check also exited 0.

## Full existing Python suite

Working directory: tools. Command:

```text
python -m pytest tests -q --cov=atom --cov-report=term-missing:skip-covered --tb=short
```

Captured coverage table and summary, verbatim:

```text
Name                   Stmts   Miss  Cover   Missing
----------------------------------------------------
atom\artifact_cli.py      35      1    97%   58
atom\artifacts.py        174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\buildsystem.py       76      5    93%   57-60, 72, 116, 180
atom\check.py             43      2    95%   117-118
atom\cli.py              298     21    93%   92-93, 328-329, 339-349, 371-381, 484, 721
atom\filelock.py          64     10    84%   69-80, 169
atom\gates.py            173     10    94%   91, 321, 407-408, 412, 462, 472, 509-512
atom\index.py             40      5    88%   66-67, 81, 86, 98
atom\onboarding.py        89      3    97%   61, 186-187
atom\report.py           329     10    97%   182, 197, 209, 223, 239, 241, 248, 752, 754, 756
atom\review.py            82      1    99%   327
atom\runner.py           126     14    89%   192, 270-272, 292-306, 323, 376
atom\scaffold.py          46      1    98%   127
atom\ship.py             252      3    99%   387, 390-391
atom\spike.py            128      4    97%   169, 265, 268-269
atom\state.py            103      1    99%   235
atom\storage.py           79      2    97%   109-110
atom\toolchain.py         53      6    89%   110, 133, 135, 137, 145, 147
----------------------------------------------------
TOTAL                   2980    118    96%
======================= 994 passed in 106.85s (0:01:46) =======================
```

Exit code: 0. Eleven source files were omitted from the missing-lines table because they had complete coverage; this does not mean any tests were skipped. The new pathsetup module was among the fully covered files.

## Remaining delivery

The production code has not yet changed the real user PATH. Complete the implementation gate and independent review, publish the feature, correct/update the installed marketplace/plugin, then run the explicitly requested real setup and verify it without printing the existing PATH contents. Existing terminals may retain their inherited environment even after notification.

## Post-review test-harness correction

The production feature remained unchanged. The isolated subprocess test was strengthened to disable site initialization and explicitly use this checkout's source. The same affected-suite command above then produced:

```text
============================ 113 passed in 25.51s =============================
```

Exit code: 0. See review.md for independent findings, the fix, and the explicitly deferred stale-variable-alias limitation.
