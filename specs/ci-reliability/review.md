---
project: "ci-reliability"
phase: "bounded-fixture-repair"
date: "2026-11-19"
status: "review-triaged-accepted"
---

# Atom Review: Hermetic CI Fixtures

## Result And Participation

Actual Atom CLI completed with exit 0. Both independent non-author models
returned one usable response each: claude-opus-5.5 and gpt-5.3-codex.
Neither was unavailable, silent or unparsed; is_partial is false.
Codex reported no findings. Opus reported four low-severity comments at three
locations, grouped by the CLI into three findings. No high/medium finding.

This is not a two-model zero-finding result. Publication is paused for an
explicit decision because the standing clean-path authorization required
both reviews clean. No commit, push or PR has occurred. No retry or model
substitution was performed and defaults remain unchanged.

## Scope And Provenance

Reviewed the accepted working-tree diff: exactly seven existing Python test
files, 52 insertions and 12 deletions. The frozen context includes the entire
contents of every changed file plus design spec, test mapping, diagnosis and
actual implementation evidence (11 labelled documents in one bundle).

Actual arguments (one invocation):

~~~text
atom review --working --model claude-opus-5.5 --model gpt-5.3-codex --runs 1 --concurrency 2 --fixed-evidence --context-file <SESSION_FILES>\atom-review-context.txt --json
~~~

The actual installed atom.exe console entry point imported this isolated
worktree's tooling using child-only PYTHONPATH. Atom's normal per-model
availability probes preceded the two review responses. No extra review batch.
Fixed evidence requested exclusion of builtin/custom/MCP tools. The report
correctly labels the context quality unvalidated: supplied documents and prompt
hashes prove delivery/provenance, not completeness or reviewer comprehension.

| Input | UTF-8 bytes | SHA-256 |
| --- | ---: | --- |
| Frozen evidence bundle | 216860 | 6c68490f957a6f8036e6eab39ef1fe9b252dc268266094de959d447f96afcda4 |
| Complete model prompt | 238621 | 7338b5be5aa570023b71d66f1bcda0705bb8fb9816947d3701e21a3d5b13b3c8 |

All seven source hashes matched implementation-evidence.md before launch.
Session files preserve atom-review-inputs.json (per-document hashes and argv),
atom-review.json (raw report), atom-review.stderr.txt (empty), and
atom-review-exit.json. These session paths are not portable repository artifacts;
the report's complete JSON is embedded below for the committed audit trail.

## Toolchain And Verification Limits

The root has no go.mod. Atom reports its Go gate NOT RUN with a no-module
skip reason; it excludes nothing. This is not a Go/race or fresh Python pass.
The reviewers received the actual accepted Python gate output in
[implementation-evidence.md](implementation-evidence.md):
1722 passed, 5 skipped, 95% measured coverage, plus bounded regressions and
245 passed, 2 skipped across the six affected modules.

Fresh preflight: all 630 relative links resolve; git diff --check exited 0.
No source changes have followed the accepted validation snapshot. The required
fresh full Python ship gate has not yet run because publication is paused.
The unchanged hosted six-combination matrix also remains unrun for this repair.

## Individual Triage: Proposed, Awaiting Developer Decision

Every Opus comment was inspected individually against the complete helper,
strict-mode test and approved spec. Agreement is not used to dismiss anything.

### Docstring Overstates Parent-Environment Isolation

- Reviewer severity: low. Human bucket: Nit. Agreement: Opus 1/1; Codex 0/1.
- Location: tools/tests/conftest.py:16.
- Observation: "without inheriting parent settings" is too broad because the
  next lines intentionally copy the sole Windows SystemRoot prerequisite.
- Proposed disposition: accept as wording nit; defer without source change.
  Behavior is intentional and explicitly documented in the inline comment and
  spec contract 4. No parent settings beyond that prerequisite are inherited.
- Suggested follow-up: say "Return caller settings plus Windows Python's
  explicit SystemRoot prerequisite."

### Missing SystemRoot Error Lacks Fixture-Specific Context

- Reviewer severity: low. Human bucket: Minor. Agreement: Opus 1/1; Codex 0/1.
- Location: tools/tests/conftest.py:21.
- Proposed disposition: reject the claimed spec violation, not the optional
  readability improvement. Direct indexed access raises KeyError naming
  SystemRoot with the exact fixture/helper traceback; it does not skip, default,
  silently inherit, or claim success. That meets contract 4's explicit fixture
  failure requirement. The spec does not require a custom exception/message.
- Optional alternative: add a contextual assertion/error, but this is not needed
  to fix a demonstrated behavior and would change the accepted snapshot.

### Caller-Supplied SystemRoot Would Be Overwritten

- Reviewer severity: low. Human bucket: Minor. Agreement: Opus 1/1; Codex 0/1.
- Location: tools/tests/conftest.py:21 (same grouped CLI location, distinct issue).
- Proposed disposition: reject as an unsupported hypothetical extension, not a
  current defect. None of the six repaired child fixture calls supplies its own
  SystemRoot. Contract 4 deliberately copies this one prerequisite from the
  parent; it does not promise caller override precedence for that key.
- If a future test needs to exercise an invalid/different SystemRoot, construct
  its mapping directly or separately specify helper override behavior.
  Do not silently expand this bounded repair's behavior.

### Strict-Arm Control-Call Counter Is Redundant

- Reviewer severity: low. Human bucket: Nit. Agreement: Opus 1/1; Codex 0/1.
- Location: tools/tests/test_review_continuation.py:342.
- Observation: strict mode's resolver is the separate pytest.fail sentinel,
  so this counter cannot record a strict-mode attempt. The sentinel, which
  is preserved, is the actual strict guard. The counter genuinely checks the
  default arm's required exactly-once resolution.
- Proposed disposition: accept as redundant-assertion nit; defer without source
  change. Strict mode is not unguarded and no behavior regression is identified.
- Suggested follow-up: assert the call count only under if not strict, retaining
  the existing strict sentinel and exact gate/model assertions.

Recommendation: accept the reviewed snapshot with the two wording/redundancy
nits deferred and the two unsupported behavior claims rejected as explained;
then run the fresh ship gate and create the PR. Alternatively fix the nits
before publication, which changes the reviewed snapshot and requires an explicit
updated validation/review decision. Neither alternative is self-approved.

## Complete Verbatim Atom JSON Report

~~~json
{
  "diff": {
    "changed_lines": 64,
    "files": [
      "tools/tests/conftest.py",
      "tools/tests/test_cli_pr_review.py",
      "tools/tests/test_pr_checkout_integration.py",
      "tools/tests/test_pull_request.py",
      "tools/tests/test_review_continuation.py",
      "tools/tests/test_runner.py",
      "tools/tests/test_windows_process.py"
    ],
    "source": "working"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "tools/tests/conftest.py",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 16,
      "lines": [
        16
      ],
      "messages": [
        {
          "line": 16,
          "message": "The docstring says the helper does not inherit parent settings, but it copies SystemRoot from the parent environment, so the doc misstates the one inheritance the helper exists to perform.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "tools/tests/conftest.py",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 21,
      "lines": [
        21
      ],
      "messages": [
        {
          "line": 21,
          "message": "If SystemRoot is missing on Windows, the bare os.environ[\"SystemRoot\"] lookup raises only KeyError: 'SystemRoot', with nothing naming the Python child-environment fixture prerequisite; the spec requires an explicit fixture failure, so raise a contextual error instead.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        },
        {
          "line": 21,
          "message": "The helper silently overwrites any SystemRoot the caller passed in settings, so a test that deliberately supplies a different value would get the parent's value without notice.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "tools/tests/test_review_continuation.py",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 342,
      "lines": [
        342
      ],
      "messages": [
        {
          "line": 342,
          "message": "In the strict arm, control_calls can never be non-empty because the strict stub is a separate lambda that never appends to it, so `len(control_calls) == 0` is vacuous and suggests a check that does not exist; the pytest.fail sentinel is the real guard.",
          "model": "claude-opus-5.5",
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
      "model": "claude-opus-5.5",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    },
    {
      "model": "gpt-5.3-codex",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "fixed-evidence"
  },
  "review_execution": {
    "context_quality": "unvalidated",
    "documents": [
      {
        "label": "context-1",
        "sha256": "6c68490f957a6f8036e6eab39ef1fe9b252dc268266094de959d447f96afcda4",
        "utf8_bytes": 216860
      }
    ],
    "mode": "fixed-evidence",
    "prompt_sha256": "7338b5be5aa570023b71d66f1bcda0705bb8fb9816947d3701e21a3d5b13b3c8",
    "prompt_utf8_bytes": 238621,
    "scope": "diff-plus-caller-context",
    "tool_policy": "source-exclusions-requested"
  },
  "schema_version": 3,
  "silent_runs": [],
  "toolchain": {
    "control_gates": [],
    "degraded": false,
    "gates": [],
    "skip_reason": "No go.mod found in C:\\Users\\gimotwan\\.copilot\\session-state\\b84ec6a2-70fc-4d05-90f2-ca5e0ea44cb5\\files\\ci-control-toolchain",
    "source_fingerprint": null,
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
~~~



## Developer Triage Accepted; Fresh Ship Gate Passed

Developer selected "Accept the documented triage; rerun validation and create
the PR without merging". The two nit deferrals and two evidence-backed
rejections above are now accepted, superseding pending/paused statements.
No reviewed source was changed and no additional model call was made.
The fresh full Python gate exited 0; exact output is appended to
[implementation-evidence.md](implementation-evidence.md). Hosted CI remains
pending until the branch is published and its unchanged matrix runs.
