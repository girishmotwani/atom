# Module review rules: decisions

## Scope and approvals

Use an isolated worktree on public main, preserving existing checkout work and installed components. The developer selected local-launch as the PR-review rule source, then clarified that initialized module-local guidance should feed review. Existing shared rules already reach reviewers; they remain in place.

The developer explicitly approved the presented bounded experiment: two synthetic review calls and up to two availability probes, no real project content, live PR access, or production changes. This approval does not authorize a design spec or production implementation.

No final rule-file discovery policy is selected. Do not remove --no-custom-instructions, import the entire workflow bundle, or silently resolve the full-guide versus curated-rule trade-off.

## Baseline and proof boundary

Atom's own implementation is Python. The source/test baseline used python -m pytest tests -v --cov=atom --cov-report=term-missing from tools, not a root Go gate for a nonexistent module. It passed: the exact excerpt is in findings.md.

The proposed disposable POC uses Python with a synthetic Go fixture because the risk lives in Atom's actual Python prompt/invocation/extraction path. This adaptation was explicit in the brief and approved with it. No production code, installed tool, dependency, machine default, real target, or gate policy changes are included.

Discovery findings and decisions were written while the already-started baseline was running. This did not strictly wait for all verification to finish before writing artifacts; tracked source, tests, and packaged assets remained unchanged. The successful result is a source/test baseline, not a claim that the entire working directory remained untouched until completion.

## Approved experiment execution choices

Use the existing fixed-evidence mode and its unchanged source-exclusion flags to keep the approved calls synthetic-only; this is not evidence about the ordinary tool-enabled mode. Retain the native 60-second probes and 600-second reviews, resolve the default pair at runtime, and never retry or substitute.

Install the actual onboarding bundle in the synthetic launch fixture, customize its Go guide, freeze it with the existing context capture helper, then mutate the source and plant conflicting checkout guidance. A temporary process-local style composition seam retains the shared seven. It is not production discovery.

Run build and vet on the tiny synthetic Go fixture separately, but skip the full review gate collection for this bounded transport proof. The prompt accurately says those full gates were skipped. Production gate policy remains unchanged; no full atom check or race/coverage claim is made for this experiment.

Before calls, declare the reservation leak in lease.go with allowed attribution at the Disable declaration (line 10) or removed reset position (new-file line 11). A matching extracted finding must mention reservation state. This deterministic fixture expectation supplements, and does not replace, manual verification of the actual messages.

After compaction, the harness was first written before reactivating the POC skill and re-reading all discipline references. Those references were reloaded before any model execution; the lapse does not justify skipping their gates. No model calls had occurred at that point.

## Result and stop

The approved experiment ended Inconclusive: two native availability probes timed out; zero of the maximum two review calls were issued. Preserve the requested pair and report the full denominator. Do not increase deadlines, retry, substitute models, or reinterpret fixture setup as native delivery evidence.

No POC quality/timing comparison is claimed and no production design starts. The report gate proposes local timeout investigation without further model calls. Any rerun needs a new, explicit bounded approval.

## Approved local-only diagnosis

The developer approved inspecting the timeout locally, explicitly without additional model calls. Only non-model version/help commands and the original probes' diagnostic logs were inspected. No configuration was repaired or mutated. Raw machine-local logs remain outside Git; public artifacts carry only source-free startup observations.

A proposed retry would additionally disable the two configured custom MCP servers using the existing invocation parameter. This changes startup conditions and requires its own bounded approval. It does not prove the diagnosis in advance or erase the original Inconclusive result.

## Controlled retry approval and preservation

The developer explicitly approved the proposed controlled retry: at most two new availability probes and two synthetic reviews, with the two custom MCP servers disabled through the existing caller-selected parameter. Models, prompt composition, guide, synthetic defect and predeclared attribution, extractor, ownership behavior, and deadlines remain unchanged; no retries or real inputs are authorized.

The first executed source was preserved outside Git as module-review-rules-native-trial/executed-spike.py, with its original SHA-256 retained in that trial's invocation record. The retry adds only caller-selected server exclusions and corresponding audit/report assertions, including a pre-call assertion that guide bytes match the original SHA-256. It does not repair production code or change model/scoring expectations. The first Inconclusive trial is retained.

## Controlled retry result and stop

The retry used two probes and one review. The default gpt-5.4 was unavailable, so the existing pipeline proceeded only with Gemini and remained partial. Preserve two requested reviewers in the denominator. The whole question remains Inconclusive; no fallback or additional request was made.

Gemini identified the synthetic defect and passed strict extraction, but its line 9 is outside the frozen expectation of 10/11. Do not edit the source or scoring to turn that result into a pass. Raw evidence and the second executed source were preserved outside Git. Return to the developer to select a supported second reviewer and revise the brief; do not start production design.

## Reviewer selected at the report gate

The developer answered "Claude Sonnet 5" when asked which supported model should replace gpt-5.4 in a revised brief. Record the intended runtime identifier as claude-sonnet-5. No additional model calls were authorized by that selection; availability is not yet verified. Production defaults, the executed sources, and the original scoring remain unchanged. The next brief still needs an explicit attribution decision and approval before execution.

## Accepted narrower feasibility milestone and scoped gate exception

On 2026-10-30 the developer accepted the recommendation with: "makes sense, recommendation accepted. lets proceed". The accepted recommendation was to use the observed one-model delivery as the narrow feasibility milestone, keep the original POC verdict Inconclusive, and make correct discovery and identical delivery to each requested reviewer implementation-test obligations.

This explicitly authorizes preparation of the bounded module-rule design despite the original two-model/attribution acceptance gap. It is not a retrospective confirmation, a general waiver, an instruction to rerun models, or permission to implement before the design gate. The earlier recommendation to rerun with a replacement reviewer is superseded for this transport milestone. Claude Sonnet 5 remains a previously selected experiment candidate, not a new production default.

Established before design: the complete frozen 9741-byte customized guide reached one native review, the CLI root user event matched the logical packet after newline normalization, strict extraction yielded the known semantic defect, and ambient custom instructions remained disabled. Existing source composes one common review prompt for requested models.

Still assumed or to be specified/tested: which local files are authoritative, how missing/malformed rules behave, safe confinement and provenance, ordinary versus fixed-evidence capture, correct pre-checkout snapshot timing, and identical delivery to every requested reviewer. The POC did not prove automatic discovery, causal rule influence, improved review quality, or another provider's compatibility.

There is no phase-plan.md for this bounded change. The developer accepted moving directly to its single-increment design; record that workflow adaptation instead of inventing an approved phase plan. Source selection remains an explicit intent decision before completing the spec.

## Source selection and proposed design

The developer selected guide_and_module_agents: the initialized local Go guide plus module-root AGENTS.md. Do not follow Markdown links or discover ancestor/GitHub instruction files in this increment. Domain guidance is distinct from Atom's copied workflow AGENTS.md, which is not imported.

Draft design-spec.md proposes a normal-mode default, a --no-module-rules opt-out, frozen pre-preparation capture, metadata-only provenance, and explicit present-file failures. It preserves fixed-evidence's no-automatic-source contract and keeps lower-level review callers explicit. These are proposed design decisions awaiting the design gate, not implemented behavior.

The selected root stays the CLI launch directory, matching existing module-root check/PR use; no nested-module/ancestor inference is added. Proposed source precedence applies only to code-review conventions; workflow/output/tool instructions are outside that policy authority. Model obedience and quality are assumptions, not guarantees. Python APIs/tests are used because Atom's implementation is Python.

## Design approval and BUILD entry

The developer explicitly approved the presented design for TDD. Status is approved; the test spec maps all 15 numbered behaviors before production edits. Python pytest is the repository-standard verification adaptation; there is no new Go concurrency or root Go module. No unfailable test cases were proposed; tests target silent omissions and actual source/prompt/report behavior. No extra model batch, installation, commit, or push is authorized.

## BUILD progress and filesystem test adaptation

The first production increment is now in progress. Frozen policy reaches the real common-prompt path for two synthetic reviewer identities and two runs each, with unchanged native instruction suppression and successful strict extraction. Opt-out/fixed-evidence paths access no candidates; invalid snapshots fail before runner work. No new native model calls have been made.

Windows refused real symlink fixtures with winerror 1314. Keep those three tests skipped rather than treating a skip as RED. Deterministic filesystem-boundary tests separately observed genuine assertion failures for outside-root resolution, dangling-source omission and unreadable traversal, then passed after confinement and per-component lstat/strict-resolution handling. Read-error messages are sanitized by existing context capture. This does not claim hardened protection against concurrent malicious path replacement.

After the latest context restoration, the next RED/GREEN loops were resumed before re-reading the actual discipline documents. Those documents and the approved design/test spec have now been reloaded. This was a process lapse, not a gate waiver; no external model calls, publication, installation, or additional product scope followed from it.

## BUILD reconciliation and completion boundary

Implemented the approved design without changing its public scope. Normal CLI capture is explicit and happens before PR preparation; lower-level omission does not discover files. Additive reporting keeps schema version 2 and never dumps snapshot text. Fixed-evidence still excludes automatic policy. No native invocation code, model default, deadline, server default or gate-exit policy changed. Canonical and packaged Go-guide exposition were updated together and verified byte-identical; README describes source scope, precedence, opt-out and limitations.

Regression additions for duplicate/order snapshots, duplicate resolved targets, full JSON packet decoding and partial review participation passed using already-built behavior; no new speculative production code was justified by them. While extending the hash fixture to two documents, preserved its second document so the hash case still tests metadata rather than accidentally failing on a length mismatch. An initially guessed CheckoutRunner.module fixture attribute was replaced with the existing tmp_path root before executing that regression. No expectation was loosened and no correct failure was removed.

Full Python verification is green with 1501 passed, 5 skipped and 95% total coverage; exact captured output is in tdd-evidence.md. The unresolved Windows native-link fixture limitation and the loader's uncovered missing-root wrapper are disclosed, not hidden by aggregate coverage. There is no new Go concurrency; the applicable gate remains repository pytest rather than a nonexistent root Go check. Both POC verdicts remain Inconclusive, as previously agreed.

Stop at the implementation completion gate. This does not authorize paid multi-model review, installation, commit, push or publication. Keep the portable toolchain and degraded-review requests pending rather than bundling them into module-rule delivery.

## Implementation completion approved

The developer explicitly answered true to the completion gate for module-rule delivery after receiving the full-suite result and the Windows link-test limitation. Mark this bounded implementation complete. This supersedes earlier awaiting-gate status notes, not the original POC verdicts. The approval explicitly excludes paid review, installation, commit and push; no next phase starts automatically.

## Independent review required before shipping

The developer requested commit and push, then explicitly rejected waiving the separate multi-model review and requested the diff. Complete and focused patches were exported outside Git for inspection; intent-to-add makes new feature files visible to git diff without staging their contents. The original dirty checkout remains untouched. Publication, when ready, must target the public remote girishmotwani/atom, not the legacy origin.

No project reviewer config exists in this isolated worktree. The developer explicitly approved runtime selection of Claude Sonnet 5 and Gemini 3.8 Flash: one independent review each, at most two probes and two review calls, no retries, after fresh Python verification. Both reviewers differ from the authoring model. Existing native 60-second probe and 600-second review deadlines remain unchanged. Named custom startup exclusions apply to this invocation only; no production defaults or saved server configuration change.

This repository is Python tooling, so the review gate is the full repository pytest/coverage command, not nonexistent root Go checks. Supply an explicit Python-review packet containing the complete frozen diff, full current changed files, approved design and directly dependent context to both models. Use existing native invocation and strict extraction with model-side tools excluded; do not silently truncate, substitute models, fabricate reviews or fall back on failed extraction. Original POC criteria and verdicts are unaffected. Triage Blockers/Majors with the developer before shipping.

## Approved review corrections

The developer approved the review triage: reject the recommendation to ignore NotADirectoryError or broad OSError, fix Windows malformed-parent omission explicitly, isolate the ambient-dependent CLI test, document the archived guide pin, then rerun verification and continue commit/push. This is scoped continuation approval, not authorization for more paid calls.

Windows real-filesystem tests observed three clean DID NOT RAISE ModuleRulesInputError failures for non-directory entries at different guide-parent depths. Explicit directory checks now reject these inputs before attempting a child lookup, because Windows can otherwise report that child as FileNotFoundError. The approved fail-explicitly contract is preserved, rather than redefining invalid present trees as optional absence. The design wording now makes that already-approved interpretation explicit.

The existing local report test was reproduced failing from a temporary directory with blank AGENTS.md, then passed after adding tmp_path chdir. Its assertions were not weakened. No production change was made for that test-isolation correction. Current loader suite: 35 passed, 3 skipped. Native link privilege limits remain unchanged.

The archived spike retains its original source/scoring and frozen-guide assertion. Its README now explains why the changed current bundle cannot replay the historical guide unchanged. No historical hash or verdict was tuned; no POC/model call was made for this offline check. The completed independent review covers the pre-triage snapshot; these small approved corrections receive deterministic tests and final full verification, not an unapproved second paid review.
## Commit and push authorization

The developer explicitly requested commit and push, required independent review rather than waiving it, approved the bounded two-model review, and then approved its proposed fixes/documentation and continuation after fresh verification. That full Python gate passed with 1504 tests and five disclosed skips. All review dispositions are in review.md; no accepted Blocker/Major remains open. No further paid calls are authorized or made.

Commit this single bounded increment with its relevant POC/spec/review records, preserving the original dirty checkout. Push only feat/module-review-rules to the public girishmotwani/atom remote, with no force push, main-branch mutation or history rewrite. The current request is commit and push, not installation or automatic next-phase work.
