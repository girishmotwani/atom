---
project: "ci-reliability"
date: "2026-11-19"
status: "diagnosis-confirmed-repair-not-implemented"
---

# CI Failure Diagnosis

## Scope And Verdict

Diagnose every FAILED test case in main CI run 44342921071 at
ef7fea43119564dfabb18ab9faed68919e1500c9. Confirmed: the captured failures fall
into three reproduced fixture/environment families. This is not a repaired
suite, a fresh six-platform-matrix run, or implementation approval.

The developer approved diagnosis of both initial families on November 18, then
selected "Investigate all observed CI failures (recommended)" on November 19.
The request "do we have the diagnosis? lets write the repair spec" authorizes
finishing this bounded diagnosis and drafting the spec, not implementing it.

| Captured job | Go control | Path assertions | Python child startup |
| --- | ---: | ---: | ---: |
| Ubuntu Python 3.10 | 1 | 0 | 0 |
| Ubuntu Python 3.12 | 1 | 0 | 0 |
| macOS Python 3.10 | 1 | 14 | 0 |
| macOS Python 3.12 | 1 | 14 | 0 |
| Windows Python 3.10 | 1 | 14 | 6 |
| Windows Python 3.12 | 1 | 14 | 0 |

Counts are exact FAILED summary cases, including parametrization, not independent
root causes. All six captured Test logs were classified; no CI rerun was triggered.

## Go-Control Host Leakage

Source: tests/test_review_continuation.py:285-329 and
atom/review.py:380-398, 714-788 (paths below tools).

The gate-order test scripts selected Go 1.26.9, a module minimum of 1.27.0,
and a selected build failure. Strict mode forbids control resolution, but the
default arm leaves control discovery bound to the real host PATH. Production
correctly rejects CI's Go 1.23.12 before reaching the intended assertion.

Both variants pass on the unmodified local host. Replacing only the test-process
PATH with synthetic Go 1.23.12 VERSION metadata reproduces the CI exception.
FakeRunner does not execute the synthetic binary. Exact command and failure
section are already preserved in [decisions.md](decisions.md).

Verbatim diagnostic failure excerpt:

~~~text
E   atom.review.ControlToolchainError: PATH Go 1.23.12 is below module minimum 1.27.0
================= 1 failed, 1 passed, 65 deselected in 14.33s =================
~~~

Conclusion: isolate this gate-order test's control boundary. Do not lower the
module minimum, upgrade CI Go, widen its exception assertion, or relax production
control verification. Existing incompatible/missing/unverified-control tests
remain the contract for actual control resolution.

## Canonical Path Versus Allocator Spelling

Source: tools/atom/pull_request.py:270-275; tools/tests/test_cli_pr_review.py:115;
tools/tests/test_pr_checkout_integration.py:88; tools/tests/test_pull_request.py:234.

Production intentionally resolves the selected module and verifies containment
within the resolved checkout. Test collaborators retain the lexical clone
destination. Their exact comparisons therefore reject valid aliases of the
same directory: /var versus /private/var on macOS, runneradmin versus RUNNER~1
on Windows.

Controlled reproduction: an autouse diagnostic plugin supplies atom-pr-
allocations through an actual Windows short-name alias of a dedicated parent
directory. The owned atom-pr- basename is unchanged, matching the CI failure
boundary. All 14 captured path cases fail at the same three comparison sites.
A diagnostic-only canonical clone-destination control makes all 14 pass without
altering production, source files, checkout safety checks or test assertions.

Exact command form, run from the isolated worktree's tools directory:

~~~text
python <SESSION_FILES>\ci_diagnosis.py paths
python <SESSION_FILES>\ci_diagnosis.py paths-canonical-fixture
~~~

Verbatim summary lines:

~~~text
============================= 14 failed in 12.08s =============================
============================= 14 passed in 9.15s ==============================
~~~

The control changes only diagnostic collaborator input, not a committed repair.
The proposed repair compares against the resolved expected module at those three
assertion sites, preserving exact canonical equality and the raw recorded clone
destination. No string lowercasing, prefix matching, or disabled assertion.

### Diagnostic Harness Boundary Correction

The first diagnostic aliased the owned directory's basename itself, rather than
only an ancestor. Its canonical-fixture control still failed all 14 cases because
the unchanged cleanup guard correctly refuses a basename lacking atom-pr-.
That artificial condition does not explain the captured CI paths, whose basename
is intact. It is not counted as confirmation of the CI hypothesis or a reason
to relax cleanup. Both initial captures are retained in session evidence.

The corrected parent-alias diagnostic above isolated the actual CI condition.
All 28 marked checkouts retained by the initial control were individually
identified, inspected, and removed using the unchanged ownership-checking
cleanup routine and their exact canonical paths. The two corrected runs removed
their own checkouts and dedicated alias-parent directories. No broad deletion
or repository cleanup was performed.

## Windows Python 3.10 Startup Prerequisite

Source: tools/tests/test_runner.py:23-45, 136-164, 196-208, 465-487;
tools/tests/test_windows_process.py:223-248. Production complete-environment
behavior is in tools/atom/runner.py:113-132 and
tools/atom/_windows_process.py:264-282.

The six failing cases all launch Python with explicit environment mappings that
omit SystemRoot. Existing session-local Python 3.10.11 reproduces all six when
used only as the test child interpreter; pytest itself runs on Python 3.13.14.
No interpreter installation or production change was made during this session.

Four direct failures happen before user code executes. The timeout case returns
a completed startup failure instead of timing out; the readiness case never
creates its child identity record. Adding only SystemRoot to explicit diagnostic
child mappings makes all six reach and pass their original assertions.

Exact command form:

~~~text
python <SESSION_FILES>\ci_diagnosis.py children
python <SESSION_FILES>\ci_diagnosis.py children-systemroot
~~~

Verbatim failure and summary excerpts:

~~~text
E   AssertionError: Fatal Python error: _Py_HashRandomization_Init: failed to get random numbers to initialize Python
E     Python runtime state: preinitialized
============================== 6 failed in 7.23s ==============================
============================== 6 passed in 4.09s ==============================
~~~

The earlier direct subprocess-versus-Atom probe independently shows identical
behavior: empty mapping fails both launchers, SystemRoot-only succeeds both,
and PYTHONHASHSEED-only succeeds both. Thus there is no evidence that Atom loses
a supplied environment variable or misclassifies a successful child.

The diagnostic SystemRoot injection is NOT an acceptable repair for the true
empty-environment test: it would stop exercising an empty mapping. Instead,
a separate bounded probe verified absolute System32 cmd.exe /d /c with
environment={} can check the parent-only sentinel without needing Python startup.

Verbatim native-child probe output:

~~~json
{"case": "empty-mapping-native-child", "direct_exit": 0, "direct_stdout": "None", "direct_stderr": "", "atom_outcome": "completed", "atom_exit": 0, "atom_stdout": "None", "atom_stderr": "", "parent_unchanged": true}
~~~

Do not merge the parent environment inside production, force PYTHONHASHSEED,
suppress startup errors, extend deadlines, retry failures, or skip Python 3.10.

## Evidence Location And Limits

Session evidence under files/ in session
4902d3aa-e485-4331-a054-4c8c83754b72 includes ci_diagnosis.py,
paths.txt, paths-canonical-fixture.txt, children.txt, children-systemroot.txt,
and both paths-leaf-alias control captures. The preceding session retains all
six original CI logs and python310-startup.json under ci-diagnosis-evidence.
Commands above abbreviate only the absolute session-directory prefix as
<SESSION_FILES>; output excerpts are copied, not reconstructed.

Observed path reproduction is native Windows, not a fresh macOS run. Observed
child reproduction uses an embedded 3.10.11 child, not a full Python 3.10 pytest
environment or the exact hosted CI patch release. Diagnostic controls confirm
causes, not final repair bytes or absence of other defects. No full local suite,
production/test edit, new CI execution, model-review batch, commit, push or PR
has occurred. The existing six-job CI matrix remains required before claiming
that CI has been restored.
