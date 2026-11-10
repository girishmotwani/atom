# Standalone Review Slice - Shipping Evidence

Status: final bounded review accepted; exact staged slice verified for commit/PR.

## Authorization And Scope

The developer explicitly requested push/PR after review approval, accepted the
bounded review with its evidence limitations, and selected "Standalone-review
slice only; keep setup work local". See [decisions](decisions.md) and
[review](review.md). No additional model calls or installed preview update.

Partial staging includes only standalone README/workflow sections, early review
routing and the two standalone onboarding delivery parameters. Canonical and
packaged review skill/reference, guidance tests, standalone POC/evidence and these
slice-local audits accompany them. Earlier setup implementation, setup-specific
evidence, phase-plan edits and mixed phase-level audits stay local. All 74 working
files in the pre-staging preservation manifest remained byte-identical through
scope selection and verification. No stash, restore or checkout of working files.

The staged router puts the same review-only paragraph before the original
bootstrap instructions, avoiding accidental installation before bounded entry.
The staged onboarding test omits only the setup-reference parameter; source in
the dirty working tree still retains it. No runtime/default/API change is staged.

## Fresh Verification Of The Actual Staged Snapshot

Exported the real Git index with git checkout-index into a session-only snapshot.
Confirmed Python imported atom from that snapshot, not the installed user wheel.
From its tools directory ran:

```text
python -m pytest tests\test_standalone_review_guidance.py tests\test_onboarding.py tests\test_cli_review.py tests\test_report.py tests\test_merge.py tests\test_artifact_integration.py tests\test_plugin.py -q --tb=short
```

The first export lacked .git metadata. One existing subprocess test tried to
capture a real Git diff before rejecting --runs 0, so that run failed at its
repository prerequisite. Preserve the exact failed run instead of claiming it
passed:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\standalone-shipping-snapshot\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 209 items

tests\test_standalone_review_guidance.py ........................        [ 11%]
tests\test_onboarding.py .....................                           [ 21%]
tests\test_cli_review.py ............................................... [ 44%]
.........................F...                                            [ 57%]
tests\test_report.py ...................                                 [ 66%]
tests\test_merge.py ..............................................       [ 88%]
tests\test_artifact_integration.py ............                          [ 94%]
tests\test_plugin.py ...........                                         [100%]

================================== FAILURES ===================================
_ TestTheProgramActuallyRuns.test_a_refused_setting_does_not_produce_a_traceback _
tests\test_cli_review.py:909: in test_a_refused_setting_does_not_produce_a_traceback
    assert result.returncode == EXIT_USAGE_ERROR
E   AssertionError: assert 1 == 2
E    +  where 1 = CompletedProcess(args=['C:\\Users\\gimotwan\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3... type\n    --max-depth <depth>   maximum tree depth to recurse\n    --output <file>       output to a specific file\n').returncode
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::TestTheProgramActuallyRuns::test_a_refused_setting_does_not_produce_a_traceback
======================= 1 failed, 208 passed in 44.83s ========================
```

Initialized isolated Git metadata in the temporary snapshot only. The exact
failed test then passed (1 passed in 0.64s); no production/test source changed.
Re-ran the complete same selection:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\gimotwan\.copilot\session-state\1ec68bb0-53ec-4735-a4de-c5186a9d376f\files\standalone-shipping-snapshot\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 209 items

tests\test_standalone_review_guidance.py ........................        [ 11%]
tests\test_onboarding.py .....................                           [ 21%]
tests\test_cli_review.py ............................................... [ 44%]
.............................                                            [ 57%]
tests\test_report.py ...................                                 [ 66%]
tests\test_merge.py ..............................................       [ 88%]
tests\test_artifact_integration.py ............                          [ 94%]
tests\test_plugin.py ...........                                         [100%]

============================ 209 passed in 29.04s =============================
```

This is 209 focused cases, not the full Python suite, coverage or a Go application
atom-check baseline. The count excludes the setup-specific onboarding parameter
and includes the approved strict-mode/documentation cases. No Go module is
invented at Atom's repository root. No live reviewer transport trial was rerun.

## Publication Inspection And Preserved Historical Whitespace

Inspected staged adapters and evidence; validated six JSON files, 47 local
Markdown links and absence of setup-only references in the staged shared files.
Common GitHub/AWS credential, private-key, JWT and credential-URL pattern checks
found no matches in staged text or decoded archive content. This is publication
hygiene, not a comprehensive security review. No executable trial was rerun.

The standard staged git diff --check reported only four new-blank-at-EOF warnings:
implementation-validation.txt:18, remaining-cases-brief.md:63,
remaining-cases-report.md:442 and transport-correction-report.md:68.
These are historical evidence artifacts, including frozen validation bytes.
Preserve them rather than rewrite review evidence to silence cosmetic warnings.
The check with only blank-at-EOF disabled exited 0 with no output:

```text
git -c core.whitespace=-blank-at-eof --no-pager diff --cached --check
```

## Base And Remaining Limits

Verified against base 50622abf2b9f58bcfc2c9d538b7292cf0689ceee. During shipping,
origin/main advanced to ec605a715f53db93abd54d6e88f887cf20525940 (Linux bootstrap
fix). Its README edits are disjoint from this slice's addition. This branch is
not rebased through the dirty setup work; no claim that these local checks ran
against the newer main integration. GitHub/human review will observe that base.

Two reviewer responses used explicit different model requests, but exact runtime
identities were not independently exposed. The developer accepted that limit.
The Go-policy correction and partial-staging boundary were source/regression
checked, not sent to an additional reviewer batch. Live consent/refusal/stopping,
installed-preview delivery, paused setup work and complete Phase 04 remain open.

## Verified Production And Test Index Objects

These Git blob IDs identify the exact nine source/test inputs validated above.
Later audit-only metadata does not change them.

| Path | Git blob |
| --- | --- |
| `README.md` | `136163cd1afd14f7f8d4c97002d71388d0799838` |
| `com.github.copilot\commands\start.md` | `c94309e0833b7a9449f6d19232221f59ee8616c3` |
| `docs\workflow.md` | `817dad41e77cffc5dc0dd4d049597a126bb1bd63` |
| `skills\atom\references\standalone-review.md` | `ceb1a40585578310f3cd6279b3488a3b213aee39` |
| `skills\review\SKILL.md` | `f6a614cf72df16401fbfd3e0b536846401cab84f` |
| `tools\atom\assets\skills\atom\references\standalone-review.md` | `ceb1a40585578310f3cd6279b3488a3b213aee39` |
| `tools\atom\assets\skills\review\SKILL.md` | `f6a614cf72df16401fbfd3e0b536846401cab84f` |
| `tools\tests\test_onboarding.py` | `c1168488a856754c0df07e18aa4db9f50fef998a` |
| `tools\tests\test_standalone_review_guidance.py` | `d36526849b7d44e0aee94c0ffeff76bc0968392c` |
