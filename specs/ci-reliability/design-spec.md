---
project: "ci-reliability"
phase: "bounded-fixture-repair"
author: "GitHub Copilot"
date: "2026-11-19"
status: "implementation-accepted-review-triaged"
evidence: "diagnosis-report.md"
---

# Design Spec: Hermetic CI Fixtures

## Purpose

Restore trustworthy tests for Go-review continuation, disposable PR checkouts,
and complete child environments without changing Atom's runtime behavior or
dropping any supported CI platform or Python version.

## Evidence Base

[Diagnosis report](diagnosis-report.md) and its captured current-main CI failures
are the proof for this understood-defect repair, rather than a new Go spike.

Established:

- A process-local synthetic CI Go installation reproduces the default
  gate-order test's ControlToolchainError; strict mode passes.
- Real Windows parent-path aliases reproduce all 14 captured path assertions.
  A diagnostic canonical-expected-path control passes all 14.
- Using existing Python 3.10.11 as the child reproduces the six Windows startup,
  timeout and identity failures. Supplying only the missing SystemRoot runtime
  prerequisite makes all six original assertions pass.
- A native Windows child succeeds with an actually empty mapping and observes
  no parent-only sentinel. Production need not inherit additional variables.

Still assumed, to validate during implementation:

- The exact proposed test edits reproduce the diagnostic controls' outcomes.
- The same canonical expectation fixes the observed macOS /var alias cases;
  there is no fresh macOS implementation run yet.
- Hosted Python 3.10/3.12 environments behave like the diagnosed boundaries.
- No additional failure emerges in the full suite. CI is not green yet.

Approval of this spec also accepts the diagnosis as proportionate evidence for
these fixture corrections. It does not approve an unproven production repair.

## Public Surface And Scope

No production API, CLI option, exception, serialized report, subprocess
environment, cleanup policy, CI workflow or dependency changes.

Only these existing test files may change, plus this repair's artifacts:

- tools/tests/test_review_continuation.py
- tools/tests/test_cli_pr_review.py
- tools/tests/test_pull_request.py
- tools/tests/test_pr_checkout_integration.py
- tools/tests/test_runner.py
- tools/tests/test_windows_process.py
- tools/tests/conftest.py, only for the minimal shared child-environment helper

This is one bounded repair, not a new Atom project/phase registration. No Go
module or production Go code is introduced.

## Design Overview

Keep fixtures responsible for the boundary they own:

| Boundary | Fixture correction | Runtime invariant retained |
| --- | --- | --- |
| Gate order | Deterministic failed control resolution in default arm | Strict mode never resolves a control |
| Checkout identity | Resolve the expected module before exact comparison | Canonical selected module remains contained |
| Python child setup | Explicit minimal Windows runtime prerequisite | Child mapping fully replaces inherited mapping |
| Empty environment | Native Windows probe instead of Python | The mapping passed to Atom stays exactly empty |

Reuse the existing pinned-review fixture, synthetic distribution helpers,
monkeypatch, and runner results. Do not expand global shared fixtures when a
test-local stub suffices.

## Numbered Behaviour And Test Obligations

1. The default arm of
   test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates
   runs selected gofmt then build, resolves the control boundary exactly once
   through a test-local deterministic resolver stub, and raises a matching
   GoToolchainSelectionError from that stub. No real PATH control lookup,
   control gates or model invocation occurs. Retain the existing exception
   assertion rather than adding ControlToolchainError to it.

2. The strict arm keeps its fail-if-control-called sentinel and the exact
   existing build, vet, gofmt, test and race ordering. It never resolves a
   control and never invokes models. The two arms must behave identically
   under an absent, incompatible or compatible ambient Go installation;
   existing dedicated control-resolution tests continue to exercise real
   rejection/verification rather than this stub.

3. The prepared_cli model collaborator, real-Git LocalTransportRunner model
   boundary, and independent-clone test compare the received canonical module
   with the resolved expected checkout/module path. Keep exact Path equality.
   Preserve raw clone argv, clone independence, commit pins, module-relative
   provenance, dirty-original preservation and cleanup assertions. Every one
   of the 14 diagnosed cases must pass with a valid alias in a parent component.

4. Python-based tests that intentionally construct restricted child mappings
   explicitly include SystemRoot on Windows, in addition to their existing
   test-selected variables. A small shared test-only helper returns a fresh
   mapping per call, copies only that OS prerequisite from the parent, and
   leaves non-Windows mappings restricted to the supplied variables. It does
   not silently inherit PATH, parent sentinels, or the full parent environment.
   Missing SystemRoot on a Windows test host is an explicit fixture failure,
   not a skipped test or default value.

5. Keep the existing Unicode payload, stdin, caller-mapping immutability,
   parent immutability and absolute executable/PATHEXT assertions. Continue
   exercising the mapping-copy-before-launch test by mutating the exact
   mapping supplied to SubprocessRunner, not an unused earlier copy.

6. test_empty_environment_does_not_inherit_parent_settings passes the literal
   empty mapping through Atom on every platform. On Windows use the absolute
   System32 cmd.exe path with /d and a noninteractive parent-sentinel probe;
   on POSIX retain the Python probe. Assert successful completion, absent
   parent-only sentinel, and unchanged parent sentinel. Do not use the
   minimal-Python-environment helper or inject SystemRoot for this case.

7. Both explicit-environment lifecycle tests retain their existing deadlines,
   exact timeout outcome, partial-output checks, retained process-identity
   assertions, owned-descendant termination and fixture-rescue distinction.
   Add the prerequisite to their Python fixture mapping, not to production.
   A child that exits before executing the fixture is still a failure.

8. Preserve all existing incompatible/missing/unverified-control rejection,
   cleanup ownership/redirected-path rejection, complete-environment lookup,
   concurrent environment isolation and lifecycle-failure tests. No broad
   exception acceptance, retries, skips, relaxed timing, deleted failing case,
   or swallowed diagnostic is an acceptable repair.

## Error Handling

| Condition | Required result |
| --- | --- |
| Selected build failure, default gate-order fixture | Test-owned GoToolchainSelectionError after exact selected gates |
| Control attempted in strict fixture | Immediate explicit pytest failure |
| Actual incompatible/missing/unverified control | Existing production rejection and dedicated tests unchanged |
| Missing Windows SystemRoot fixture prerequisite | Explicit fixture setup failure |
| Native child cannot launch or startup fails | Existing result/diagnostic assertions fail |
| Checkout identity or cleanup fails | Existing assertions/errors remain visible; no success fallback |

No exception signatures or runtime error classifications change.

## Concurrency And Ownership

There are no new production workers, locks or shared mutable state. The helper
returns a new dictionary per call; concurrent tests must not share a writable
environment mapping. Existing monkeypatch changes remain test-scoped, with
normal pytest restoration. Existing runner-owned children, readiness observers,
rescue and handle cleanup remain unchanged. No new background service, process
name-based termination or longer process lifetime is introduced.

## Extension Points

Use the existing test-only fixture seam for deterministic control resolution.
Use one minimal test helper for repeated Python child prerequisites. Keep
canonical expectations at the three consumer assertions instead of changing
the allocator, production module path, or every captured command.

No new production abstraction is warranted by the evidence.

## Trade-offs

| Option | Choice and reason |
| --- | --- |
| Fixture corrections with unchanged production | Chosen: reproduced failures concern host-dependent test assumptions |
| Upgrade CI Go to satisfy a gate-order fixture | Rejected: masks non-hermetic behavior |
| Resolve expected checkout paths | Chosen: exact canonical identity matches the existing containment contract |
| Remove production resolve or compare lexical strings | Rejected: changes intended path/containment behavior |
| Give Python fixtures only SystemRoot on Windows | Chosen: measured startup prerequisite, explicit at the caller |
| Merge os.environ into production or relax empty-mapping test | Rejected: violates complete-environment isolation |
| Force PYTHONHASHSEED or increase timeouts | Rejected: masks startup failure or changes what is measured |
| Native Windows empty-environment probe | Chosen: observed working without inventing Python prerequisites |

## Implementation And Verification Plan

These are required future checks, not results already obtained:

1. Map numbered requirements to the existing failing cases in test-spec.md.
   Preserve the recorded pre-edit failures and rerun the smallest affected
   cases before each coherent fixture edit. This is a justified fixture repair,
   not fabricated RED evidence for a production feature.
2. Apply the smallest test-only edits. Repeat the two Go-order variants under
   controlled old and missing PATH Go, the 14 path cases under parent aliases,
   and the six child cases with Python 3.10 as the child. Keep actual empty-env
   coverage separate from the diagnostic SystemRoot-injection control.
3. Run all tests in the six affected test modules together, including the
   existing negative controls. Confirm no external model or ADO call runs.
4. Run the existing full tooling gate from tools:
   python -m pytest tests -v --cov=atom --cov-report=term-missing
   Run python tools/check_links.py from the repository root and git diff --check.
   No project linter/type-checker command is configured in tools/pyproject.toml;
   do not install new tooling for this repair.
5. Present exact output, remaining limits and implementation diff for acceptance.
   Root atom check is inapplicable because this repository's tooling is Python
   and no root go.mod exists. Do not claim a fictional Go/race gate.
6. Once separately authorized to publish, require the unchanged CI matrix:
   Python 3.10 and 3.12 on Ubuntu, macOS and Windows, with existing POC/docs
   jobs intact. Do not claim restored CI from local Windows results alone.

A new failure family, necessary runtime change, or weaker guarantee stops this
repair for a new decision. Approval does not authorize model-review batches,
installation, commit, push, PR creation, merge, or unrelated dirty-checkout work.

## Out Of Scope

Review-model replacement, Phase 09 completion, bootstrap/onboarding changes,
toolchain-policy redesign, cleanup guard relaxation, dependency updates,
workflow version/platform changes and broad test refactoring.
