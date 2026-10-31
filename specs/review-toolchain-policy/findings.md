---
project: "review-toolchain-policy"
phase: "n/a"
date: "2026-10-30"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# Findings Log

| Finding | Severity | Where | Why deferred | Next action |
|---|---|---|---|---|
| Go gates use inherited executable/environment selection; no explicit review version policy was found | Medium | `tools/atom/gates.py:46-67`, `tools/atom/runner.py:71-119` | Discovery only; exact-selection feasibility is not proven | Run the approved toolchain POC before designing selection |
| Existing persistent selection is `go1.26.9+auto`, not an exact version constraint | Medium | Read-only `go env GOTOOLCHAIN` during discovery | Do not change user defaults | Test child-only exact selection against module/workspace inputs |
| `atom status` falls back to the unrelated artifact-writer project and reports old artifact-shape gaps | Low | Status run at discovery start | Unrelated to toolchain selection | Use explicit project artifacts for this work; investigate status separately |
| The new worktree starts at the still-open module-rule PR's source commit | Low | `741969b7704696eaadbb0325f2fb5b2c9d026871` | Keeps the already verified baseline and preserves both existing checkouts | Reconcile base before any eventual separate PR; no push is authorized now |

## Ambiguities Resolved

The developer selected portable toolchain work first and exact patch selection rather than a minimum accepting newer Go versions. Both are explicit product intent, not inferred defaults.

## Limits

No toolchain experiment has run. Windows-only future observations must not be described as cross-platform validation. The Python baseline is green; the Go-only check is not applicable to Atom's Python source root.

## Execution Branch

The prior base/approval notes are historical. Module-rule and README PRs are now merged. Execution uses a new clean branch from latest public main as requested by the developer. The exact-toolchain trial remains unrun at this point; no successful selection or compatibility result is claimed.

## First Executed Trial: Inconclusive

The first selected-toolchain `go version` failed with: `verifying module: checksum database disabled by GOSUMDB=off`. The driver chose that offline control; this is a harness/bootstrap limitation, not evidence that all exact selection is impossible. Zero of ten cases completed. The driver stopped immediately; no build/vet/test command or retry ran. Parent environment and persistent-settings checks reported unchanged. Full raw evidence and execution hashes are in `poc-report.md`.

Do not carry this result into a passing selection spec. A proposed direct-local-executable route is a new, unproven treatment requiring its own approval. Original source/log identities remain frozen.

## Approved Follow-Up Completed: Bounded Route Confirmed

The separately approved direct-local-executable run completed all ten cases, with 56 completed commands: 44 zero exits and twelve expected minimum-version rejections. Version/environment/root/hash controls agree on the existing Go 1.26.9 distribution; compatible tests/programs report that runtime. Parent settings, inputs and executable identity checks remained unchanged. The original trial stays Inconclusive.

Normal Go caches were retained: the second parent-setting pass does not show fresh vet.exe trace entries. Do not claim a fresh analyzer in every case or performance/cold-cache evidence. Tests used count=1. The full report contains unredacted local operational paths and is not public-shipping-ready; preserve its original capture and obtain a publication/sanitization decision before any push.

Unproven integration risks remain: project persistence/precedence, missing-version handling, SDK/cache discovery breadth, other platforms, Go invoked indirectly through PATH/Makefiles, gofmt, CGO and real dependencies. A design may now be proposed only after the result gate, not inferred as implemented.

## Phase 01 Design Investigation

- `tools/atom/buildsystem.py:125-185` can select make build/test, while `tools/atom/gates.py:46-55,156-165` redetect those commands. The POC did not attest recipe execution. The developer explicitly chose: "Direct Go gates first; explicitly reject pinned Makefile delegation". Preserve unpinned delegation and never silently bypass selected Makefile targets.
- `tools/atom/cli.py:641-686` already freezes module rules from the launch directory before preparing a PR checkout; review currently reads no project version policy. A proposed launch-policy snapshot needs an explicit override for reviewing a PR from an unrelated checkout.
- `tools/atom/review.py:293-304` captures formatting inputs before collecting gates. A selected runner must cover subsequent snapshot formatting without changing the snapshots or leaking the pin to model/Git execution.
- `tools/atom/runner.py:56-76,252-280` exposes no child environment argument. `tools/atom/_windows_process.py:233-274,453-470` also inherits the environment at native launch. Production environment injection remains an implementation obligation; preserve the suspended launch, Job Object assignment and cleanup protocol.
- Existing CI (`.github/workflows/ci.yml:14-23`) covers Windows, Linux and macOS with Go 1.23. This is a place for future native verification, not evidence that the new discovery implementation already passes there. No CI run or tool download was started during design.

## Documentation Observation During Design

`skills/review/SKILL.md:39-42,89-98` already contains examples using --base/--models and a claim that review models come from config, whereas current CLI uses --branch/repeated --model and defaults from review.py. This predates exact Go selection. Do not repair it incidentally here; include it in a separately scoped usage-documentation correction. The new version-policy documentation must not repeat those stale examples.

## Design Artifact Validation

Command: python tools\check_links.py

```text
checked 315 relative links across markdown files
all relative links resolve
```

A separate local consistency check parsed the spec's sole Python contract block, checked the backward-compatible runner parameter order/defaults, verified exactly twenty ordered behavior statements and unchanged hashes for both archived spike drivers. The complete staged draft matched the writer-accepted artifact before the staging file was removed. These are document checks, not evidence that production selection or cross-platform discovery is implemented.

## Phase 01 TDD In Progress

The approved implementation is underway, not complete. Selection tests cover launch policy, bounded discovery, strict actual probes and child settings. Review tests now cover selected direct gates, preflight and late Makefile refusal, explicitly unexecuted intent, required failures and final executable replacement/deletion. Raw RED/GREEN output is retained in the session's toolchain-selection-tdd.txt; final evidence will be copied into the phase artifact before the implementation gate.

The independently delegated native environment change reports 72 passed and 2 skipped on Windows; its full output is retained in runner-environment-tdd.txt. This does not close native POSIX validation. CLI/report/documentation integration and final suite validation remain unfinished. No installation, model call, commit or push occurred.

## Final Local Implementation Findings

The earlier entries are chronological discovery/design snapshots, superseded by this implementation result. Optional config/CLI capture, strict local verification, isolated native child settings, selected Go/gofmt gates, wrapper refusal, identity checks and consistent reports/prompts are implemented and covered. The full Windows Python gate reports 1614 passed, 5 skipped, 95% coverage; complete output is in phase-01-exact-toolchain/tdd-evidence.md.

The native integration test also verifies actual automatic PATH discovery and explicit-path selection of installed Go 1.27.0, runtime-version assertions, selected-root formatting and a higher-minimum rejection. That additional test-only refinement passed after the full gate; no production source changed afterward. The archived Go 1.26.9 drivers retain their original SHA-256 identities and were not replayed.

During integrated source inspection, POSIX Popen permission/format failures could escape the new selected-executable route instead of becoming failed command evidence. A narrow launch-only OSError handler now records RUNNER_ERROR with original diagnostics; observed fault-injection RED/GREEN is retained. It does not turn failure into success or attest native POSIX ownership.

Remaining limitations: native Linux/macOS execution needs CI; the synthetic native fixture does not establish successful race/CGO execution or third-party dependency compatibility. Bounded discovery is not exhaustive SDK-manager support. Five full-suite skips are existing Windows-inapplicable module-rule symlink (three) and POSIX process cleanup/interrupt (two) cases. Selection's unexecuted coverage paths are internal misuse, duplicate suppression and a POSIX environment fallback, not missing version/output failure tests.

README and canonical/packaged review guidance document the new opt-in policy and limits. The unrelated stale review-skill examples noted above remain deferred. Evidence contains local operational paths and still requires separate publication review. No installation, paid model call, commit, push or remote CI trigger occurred; the implementation gate is pending.

## Final Documentation And Persistence Check

All five full transcripts were verified present in the writer-accepted TDD artifact after documented newline normalization. The staging draft was removed; driver hashes and packaged guidance agree. Final documentation output:

```text
COMMAND: python tools\check_links.py
checked 322 relative links across markdown files
all relative links resolve
EXIT CODE: 0

```


## Local Gate Status

The developer accepted the local TDD result. Native Linux/macOS verification and the separately scoped review/publication work remain pending. Acceptance does not change the limitations or authorize paid calls, commits, pushes or remote CI.

## Review Publication Blocker

The approved two-model batch yielded zero completed reviews: the runtime-default
GPT model is unavailable under the current account/catalog, and Gemini rejected
the 203090-token input against its 200000-token budget. These are invocation
failures, not timeout evidence or code findings. Full raw captures are preserved
outside Git; [review report](phase-01-exact-toolchain/review.md) carries actual
safe error output and the unchanged denominator.

Publication is blocked pending an approved replacement/deduplicated batch and
successful review/triage. No retries or degraded-review publication occurred.
The unavailable production default is pre-existing and is not changed here.

## Replacement Review Update

The larger deduplicated prompt yielded one completed independent Gemini review,
whose validated fixed-evidence response is []. Claude passed availability but
rejected 226156 tokens against its 200000-token prompt budget. Neither model
timed out; publishing still waits for a second completed independent review.
Reuse Gemini rather than spending another run on an already completed review.
The [review report](phase-01-exact-toolchain/review.md) preserves both batches
and their actual denominators; no further paid run has been approved.

## Final Review Triage And Remaining Scope

Two independent reviews completed. Gemini returned []; Claude returned two
low-severity findings. No Blocker/Major finding remains.

Deferred minor: tools/atom/go_selection.py:238 rejects an empty observed GOENV,
which can affect minimal environments without a user config directory. This is
the approved non-empty-field policy, not a silent ambient fallback. Such callers
can explicitly supply GOENV=off. Accepting empty GOENV needs a separate contract
decision; no automatic default/environment rewrite is introduced here.

The proposed acceptance of experiment-labelled version output is rejected as
outside the approved exact-stable contract. Full reasons and original model
messages are in [review report](phase-01-exact-toolchain/review.md).

Earlier invocation blockers are now resolved for this review, not erased from
history. The pre-existing unavailable default reviewer remains unchanged.
Native Linux/macOS CI, successful native race/CGO execution and actual dependency
compatibility remain separate evidence obligations, not inferred from Windows.

## Post-Review Publication Inspection

Fixed Minor: observed GOROOT was not independently compared with the inspected
distribution root when bin/go resolved to the same executable. The new
test_different_observed_root_is_rejected_even_when_binary_identity_matches
failed with DID NOT RAISE before the minimal guard, then passed with 179 coupled
cases. The final full Windows gate failed; see the verification blocker below.

The test uses a controlled filesystem-resolution fake; no real native alias
reproduction is claimed. The two model reviews apply to the preceding snapshot,
not this final check/test. Their two original Minor dispositions remain unchanged.
Full corrected-snapshot output is in phase-01-exact-toolchain/tdd-evidence.md.

Native Linux/macOS, successful native race/CGO and real dependency compatibility
remain open. Verbatim pytest trailing spaces are preserved with an explicit,
TDD-evidence-only whitespace-check exception; all other staged files are strict.

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
