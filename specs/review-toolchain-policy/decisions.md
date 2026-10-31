---
project: "review-toolchain-policy"
phase: "n/a"
date: "2026-10-30"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# Decisions Log

| Choice | Decision and reason | Developer visibility |
|---|---|---|
| Next requested task | Developer chose portable project-scoped Go toolchain policy before degraded review continuation | Explicitly selected in conversation |
| Version intent | Developer chose exact Go patch version for reproducible reviews | Explicitly selected in conversation |
| Worktree/base | Create separate local `feat/review-toolchain-policy` worktree from verified commit `741969b7704696eaadbb0325f2fb5b2c9d026871`; do not change the original dirty checkout or PR 12 | Surface at brief gate; base reconciliation remains necessary before a future PR |
| Baseline command | Attempted required `atom check --no-race`; it exits 2 because no root go.mod exists. Ran the repository-standard Python suite on unchanged source instead: 1504 passed, 5 skipped, 95% | Surface at brief gate; not a claim that Go gates passed |
| Spike language | Propose Python automation driving disposable Go fixtures, rather than a Go automation executable, because this repository requires its tooling/automation in Python | Explicitly approved in conversation |
| Evidence scope | Propose standard-library synthetic fixtures, existing cached toolchain only, no private target access, no downloads or model calls; actual private target dependency compatibility remains out of scope | Explicitly approved in conversation |
| Persistent format | Defer persistence location, defaults, precedence, opt-ins and error/exit semantics until selection behavior is observed | Discovery only; no implementation approved |

## Standing Waivers

None. Approval of task order and exact-version intent is not approval of this POC Brief or later design/implementation.

## Skipped Steps

No pipeline beat skipped. The root Go baseline cannot execute for this Python project; its failure and the successful Python replacement are recorded above. The spike has not been created or run.

## Execution Start: 2026-10-30

- The developer explicitly approved the original ten-case brief and now requested a new branch from latest main. Carry the unchanged question and criteria to `feat/atom-v1-toolchain`, based on public main `8b4dd51135c3836d5921414878182b16ff2fdefc`.
- The earlier pending-approval/base notes are historical. The POC is approved; the design, production configuration/selection implementation and any additional experiment are not.
- Python will generate disposable standard-library-only Go fixtures in one owned temporary directory, run the predeclared commands, and remove that directory afterward. The archived driver itself is written through the artifact writer.
- Use child-only `GOTOOLCHAIN=go1.26.9`, `GOPROXY=off`, `GOSUMDB=off`, explicit fixture GOWORK, empty GOFLAGS and `CGO_ENABLED=0` so ambient flags/network/C compiler setup cannot contaminate the synthetic standard-library fixture. Enable Go toolchain tracing as observational evidence. None of these assignments change the parent environment or user defaults.
- Snapshot the selected persistent Go environment file before the first command and verify its path with the actual `go env` output before accepting the result. If the expected configuration-file mapping is wrong, stop as Inconclusive rather than repairing the trial in flight.
- Record command argv, copied-parent selection, actual child selection, exit status, stdout and stderr. Use `-x` for build/vet/test to preserve executed-tool provenance, and explicit runtime-version assertions in the fixture program and test.
- This is not a model comparison or a performance claim. The two parent settings are controls for exact child override; no model-treatment claims are made. Normal compilation caches may be populated, but no toolchain download, dependency retrieval, persistent setting change or project source mutation is allowed.
- No automatic retries. Unexpected selection, persistent/source mutation, timeout or inability to establish provenance ends the experiment and requires a report gate.

## Stopped Trial And Required Re-Gate

The single approved run stopped on its first command because the autonomous GOSUMDB=off control prevented bootstrap checksum verification. Preserve the executed driver and log; verdict Inconclusive, zero cases completed, no retry. Do not remove the checksum control and continue under the previous approval, extend deadlines, download tools, or change global defaults.

Propose a separate ten-case offline trial using an existing Go 1.26.9 executable directly with child-only GOTOOLCHAIN=local and an explicitly controlled GOROOT. This changes selection/bootstrap treatment and is not run or implemented before approval. Production selection design remains blocked on evidence.

## Approved Direct-Executable Follow-Up

The developer approved the separate direct-local-executable brief after the benefit, original setup failure and changed selection treatment were explained. Write a separately named driver, retain the original driver/report/log, and execute one new ten-case trial without downloads, retries, model calls or persistent changes.

The follow-up reuses the original fixture definitions and evidence helpers by import, not by altering the archived driver. Candidate inspection is limited to configured/default Go cache/SDK locations and a configured/default Go root with a matching VERSION file; the first real command must still prove the actual executable's version. No checksum policy override is added. Child GOROOT is removed and the observed root/executable hash must match the candidate. A new wrapper preserves timeout diagnostics as text without changing the original execution source.

## Follow-Up Result And Scope

- Grade only the approved direct-local-executable route Confirmed: ten expected case outcomes and no retries. Preserve the distinct original Inconclusive report and immutable original driver.
- Do not rerun vet merely to force a new analyzer trace after the trial. Disclose cache reuse; the approved question concerns exact toolchain command behavior, not cold-cache analyzer invocation.
- Retain the complete unredacted local transcript in the follow-up report and the original session capture. Do not stage/push operational paths without a separate publication review and approved sanitization projection.
- No production schema, default Go version, download fallback, supported-platform expansion or degraded-review behavior is selected by this result. The next decision is whether this bounded evidence justifies writing the phase 01 spec.

## Follow-Up Report Gate Accepted

The developer selected: "Approve report and proceed to phase-1 design spec". This accepts the bounded Windows/local-executable result and authorizes phase 01 design only. It does not authorize implementation, installation, commit, push or expanded platform claims.

## Phase 01 Evidence Extraction Before Design

Established:
- The approved follow-up directly executed an existing Go 1.26.9 distribution with child GOTOOLCHAIN=local on Windows. Ten cases met expectations; compatible runtime assertions and all twelve higher-minimum rejections are retained verbatim in its report.
- Environment/default/input checks passed. Cached vet results are explicitly disclosed; the first trial remains Inconclusive.
- Atom's actual review pipeline delegates suitable Makefile targets, snapshots changed-file formatting, and uses the same base runner for Git and model commands. These are source facts, not experimental conclusions.

Still assumed / to validate during implementation:
- Bounded discovery beyond the observed default Windows cache layout, other architectures/platforms, a missing/corrupt candidate and explicit-path handling.
- Native child-environment plumbing in both launch paths, selected-distribution gofmt, unchanged scoped formatting, real race execution and existing optional analyzers' behavior.
- The proposed config/CLI/report contracts are product decisions, not POC measurements. Exact compiler selection is not evidence about real dependency compatibility or every child tool's compiler.

The developer approved the first-slice boundary in a structured gate: "Direct Go gates first; explicitly reject pinned Makefile delegation". That is a scope decision only, not approval of the forthcoming design or implementation.

The spec template is Go-oriented, but this phase modifies Atom's Python tooling. Use Python contracts/docstrings, the existing CommandRunner seam and the existing Python test/CI commands rather than adding Go production code, a new orchestration framework or shell scripts.

## Proposed Phase 01 Contracts (Pending Design Gate)

- Propose optional review_go_version in existing config, CLI version override and per-run executable path; never store local executable paths in shared config or infer a pin from go.mod. Validate a present malformed config rather than silently ignoring a possibly intended pin.
- Freeze trusted launch policy before PR preparation, consistent with launch-module rules. Target-PR config does not replace it; reviewing from an unrelated directory needs explicit version intent. No automatic init/migration or changes to atom check/init/poc.
- Propose bounded common-location discovery with explicit-path escape hatch and actual-version/root/hash proof. Persisted custom cache layouts and unvalidated platforms are not claimed covered. Real probe failure is terminal; missing versions do not install or silently upgrade.
- Extend the existing Python runner with a copied per-call child environment, preserving native ownership and base/model isolation. This is an implementation assumption to test, not a result of the wrapper-based POC.
- Selected-root gofmt and helper-Go environments for advisory analyzers require integration tests. Do not claim optional tool binary/compiler versions or arbitrary subprocesses are pinned.
- Preserve unpinned output bytes/behavior; propose an optional selection object under existing JSON schema2 for opted-in reviews. Failures still use existing nonzero exit semantics and stderr, not invented successful report objects.
- Apply the developer-approved strict wrapper boundary: refuse detected pinned make build/test without bypassing recipes; preserve unpinned behavior. Separate degraded-review phase remains deferred.
- Use existing Python/native CI tests to validate implementation; no fresh Go experiment, installation, remote CI run or paid model batch started during design. Cross-platform support depends on actual native evidence after separate publication authorization.
- The first long shell command was rejected by Windows command transport (OS error206) before the artifact writer executed. Stage the complete UTF-8 draft in session-only storage, then pipe it through the same approved writer; this does not bypass a writer refusal. Remove the staging file after verifying accepted content.

## Phase 01 Design Gate Accepted

The developer selected: "Approve this design for TDD". Presented design SHA-256: `81f8b1b55eba8e518ae118da41c2dd2efca758eb6e80dbc0f7a98d7fb95551d2`. Only approval metadata/checklist was added after the gate. The approved direct-Go first slice, proposed contracts, test obligations and explicit platform/wrapper limits now govern TDD. Material changes re-gate; no publication, installation or paid model call is authorized.

## Phase 01 TDD Execution Decisions

- Implement through observed assertion-level RED/GREEN steps; no new dependencies, Go production code, tool downloads or model calls. Preserve complete raw test output outside Git until the final TDD evidence artifact is assembled.
- Delegate only native environment plumbing and its runner/Windows tests to one bounded agent; selection, orchestration, CLI, reports and documentation remain parent-owned. The completed agent changed only its four assigned files.
- Table-drive identical failure-boundary behavior (build/test delegation, skipped/no-module intent, required-gate failure provenance, Go/gofmt replacement/deletion). These are shared contracts with distinct inputs, not speculative production code under a green test.
- Extend the existing FakeRunner with optional copied child settings while retaining its existing calls tuple shape. Its previous ambient command scripts allow the first selected-routing test to reach the intended ignored-request assertion rather than failing for a missing fake command.
- Final identity evidence only rechecks gofmt when the formatter was actually used, matching the approved used-formatter boundary; the selected Go is always rechecked. This does not attest arbitrary child tools or prevent adversarial replacement races.
- Resumption deviation: the first resumed Makefile preflight implementation preceded the mandatory post-compaction rereads. The actual skill, AGENTS and discipline/spec files were then reloaded before further behavior work; approval and implementation scope were unchanged. Do not treat summaries as replacement discipline reads on subsequent resumptions.

## TDD Reconciliation And Validation Decisions

- Retain assertion RED/GREEN evidence and immediately passing preservation/native cases as different evidence categories. No correct expectation was weakened.
- The optional child-environment assertion initially used direct dictionary indexing and leaked KeyError for the missing value. Change only the assertion to get and retain the same exact custom-value expectation, producing the required ignored-override assertion before implementing it. The private adapter accepts the extended runner signature and copies per-call mappings while retaining selected controls.
- A test command guessed a nonexistent test_report_review.py and collected zero cases. Correct the selector to the existing test_report.py; retain both outputs rather than claiming the failed selector verified anything.
- Normalize POSIX launch-only permission/format OSError to explicit RUNNER_ERROR. This is tightly coupled to safely invoking an explicitly selected local executable and preserves the runner's failure-as-evidence contract; no general catch or successful fallback is added. Local fault injection does not count as native POSIX verification.
- Inspect meaningful coverage gaps after the full gate rather than adding trivial tests for the percentage. Actual result: 1614 passed, 5 skipped, 95% total; selection 99% and review orchestration 100%. The five skips are existing platform-specific cases, not a skipped native selected-distribution case.
- After the full gate, strengthen only the existing native test to exercise automatic PATH discovery as well as the explicit path, and print non-secret selection provenance. Production source is unchanged. Rerun that precise case: 1 passed, 62 deselected, observing installed Go 1.27.0; do not repeat the entire suite for a test-only assertion refinement.
- The test-spec staging comparison initially compared Windows CRLF bytes with the artifact writer's documented LF result. Verified that the draft had CRLF and accepted artifact did not; complete normalized content matched exactly, then removed the staging file. The writer accepted the artifact; no refusal was bypassed.
- Keep README and packaged/canonical review guidance identical without repairing unrelated stale examples. Retain all original POC drivers/logs and verify driver hashes unchanged. Keep raw local paths private until a separate publication/sanitization decision.
- No material spec change, new dependency or public command beyond the approved surface was introduced. Local implementation is ready for its gate; native Linux/macOS evidence and any paid review/publication remain separately authorized work.

## Local TDD Gate Accepted

The developer selected: "Accept local TDD result". The gate explicitly retained pending native Linux/macOS verification and did not authorize paid review, commits, pushes or remote CI. Record local acceptance only; do not mark the broader platform obligation complete or start the next beat in the same turn.

## Review And Sanitized Publication Authorization

- The developer requested: "can we complete the reviews and push the changes, create a PR".
- The developer then selected: "Proceed with reviews and sanitized publication".
- Scope: one fixed-evidence review per runtime-default reviewer, two availability
  probes, 300-second review deadlines, no retries, followed by the requested
  public push/PR only after reviews and any required triage/verification.
- The gate incorrectly called 300 seconds the existing timeout. Source inspection
  establishes an actual 600-second library default; the batch used the explicit
  stricter 300-second approved deadline. Neither failure was a timeout.
- Actual batch: three commands, no completed review. GPT's availability probe
  rejected the unavailable model; Gemini's review failed the 200000-token prompt
  budget at 203090 tokens. Preserve raw output and stop before new paid work.
- Do not change production reviewer defaults as part of the exact-Go feature.
  A replacement reviewer and deduplicated full-context input require a new gate.
- Preserve and byte-verify twelve untouched original artifacts outside Git.
  Publish labelled path-redacted copies with original/publication hash identities;
  do not silently relabel projected bytes as the original raw evidence.
- Publication draft preparation initially encountered an existing Python bytecode
  cache directory. Correct the publication inventory to the three explicitly
  named archived POC files; do not publish caches or rerun the spikes.
- First native text-pipeline verification caught one extra final LF per artifact.
  Remove exactly one LF before PowerShell adds its terminator, then use the same
  approved artifact writer. All ten written publication files then matched their
  complete prepared UTF-8 bytes exactly. No writer refusal was bypassed.
- No source/tests changed during review preparation or publication projection.
  No commit, push, PR, new experiment or installation was performed.

## Supplemental Publication Privacy Audit

- The scoped scan found 2 abbreviated profile prefixes in pytest
  exception representations; exact full-prefix replacement could not match them.
  Redact those prefixes with the same labelled profile placeholder.
- Anonymize 3 explanatory private-target references. This changes
  target labels in prose, not case definitions, commands or experimental verdicts.
- Two credential-shaped example-domain URLs in the raw test-name output are
  deliberate negative-test fixtures. Their source constructs fake user/password
  URL variants in unchanged test_pull_request.py; they are not runtime credentials.
  Keep these actual test identifiers rather than claim a real secret was found.
- Untouched originals remain outside Git. Initial-publication hashes remain the
  identifiers of that earlier projection; this supplemental privacy update is
  explicitly recorded instead of pretending the public bytes never changed.
- The developer explicitly approved the replacement reviewer batch using a
  distinct reviewer in place of the unavailable default and retaining Gemini,
  with duplicate new-file diff text removed, complete file/context retained,
  two reviews plus two probes, 300-second deadlines and no retries.

## Replacement Review Result

- Both replacement availability probes succeeded. All four approved commands ran.
- Gemini completed a readable fixed-evidence root response of exactly [].
  This supplies one independent review with no findings; it does not satisfy the
  two-model requirement or authorize publication by itself.
- Claude rejected 226156 input tokens against its 200000-token prompt budget.
  Its tokenizer/budget differs from Gemini's; character count is not token proof.
  This was not a timeout. Preserve the failed response and unchanged denominator.
- Production code, tests, review guidance and archived driver bytes remain unchanged.
  Supplemental artifact anonymization was separately byte-verified and audited.
- Retain the completed Gemini review. No new paid call, default change, installation,
  archived experiment, commit, push or PR is authorized or performed.
- Propose a Claude-only larger-context call with a 600-second deadline, preceded by
  a matching availability probe, only after a new developer gate.

## Completed Review And Publication Readiness

- The developer selected "Approve Claude-only long-context batch": one matching
  availability probe plus one pending review, 600-second deadline, no retries.
- Both independent reviewer responses are complete and readable. Retain Gemini's
  [] response; Claude raised two low-severity findings. Preserve both earlier
  failed batches and their denominators rather than rewriting them as successes.
- Defer empty-GOENV support because it would broaden the approved non-empty-field
  contract. Record its minimal-environment limitation and explicit GOENV=off option.
- Reject experiment-labelled version acceptance as outside the exact stable-version
  contract. No ordinary stable-release regression was established. No model
  finding is silently dropped and no lack of agreement is used as a rejection.
- No Blocker/Major finding requires a developer fix/deferral decision. Preserve
  approved source behavior; do not make either proposed policy change silently.
- Rerun the complete approved Python pre-commit gate: actual output is retained
  in TDD evidence. The source/test/guidance and immutable driver hashes remain
  exactly those supplied to both successful reviewers.
- Public artifacts contain labelled projections; untouched originals and raw
  model streams remain outside Git. No visibility plan, bytecode/cache files or
  unrelated original-checkout changes are included.
- The developer's explicit push/PR request and sanitized-publication approval
  authorize shipping this reviewed phase to the public remote. Native CI support
  remains pending; no wider platform or dependency compatibility claim is made.

## Post-Review Correction And Publication Checks

- Historical unchanged-source assertions describe the completed model-review
  snapshot. Publication inspection subsequently found a Minor behavior-7 gap:
  a different canonical GOROOT could share the selected resolved bin/go.
- Observe the focused clean assertion RED before adding a single independent
  root-equality guard. Verify 179 coupled cases and rerun the complete Python
  gate. No policy expansion, test weakening, dependency or new POC is introduced:
  the approved spec already requires the observed root to match the distribution.
- Both independent models saw the prior snapshot, not the subsequent selector
  check and regression. Record that distinction instead of claiming a final
  snapshot rereview. No further paid model invocation is authorized or performed.
- Resumption deviation: mandatory post-compaction discipline rereads occurred
  after the resumed focused RED/GREEN and fix. Reload actual AGENTS, skills and
  discipline references before publication; record the ordering deviation.
- Initial staged whitespace checking failed on prose EOF blank lines and
  trailing spaces inside verbatim pytest captures. Normalize only design/test
  prose EOFs through the artifact writer; also remove the later-authored TDD prose EOF blank line. Preserve raw capture whitespace.
- Run strict staged diff --check for every file except TDD evidence; for that
  one evidence file use per-invocation core.whitespace=-blank-at-eol. No global
  Git setting, attributes file or silent output stripping is introduced.
- The reviewed-snapshot 1614-pass gate is historical; the final corrected
  snapshot's full-gate failure and complete RED/GREEN output are separately retained.

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

## Final Staged Privacy Check

The initial userinfo-URL scan also matched six synthetic username-only URLs,
including an escaped-newline test identifier, besides the two password-shaped
fixtures. All eight were verified against unchanged test_pull_request.py:14-15,
35-44,103-111. Permit only those exact fixture strings in TDD evidence, not
arbitrary userinfo URLs or another staged file. This corrects the operational
scan's false positives; no evidence or production test was changed.

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
