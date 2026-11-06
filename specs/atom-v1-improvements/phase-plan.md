---
project: "atom-v1-improvements"
date: "2026-10-30"
status: "accepted-ordering"
phase_count: 13
---

# Atom v1.0 Improvement Plan

## Goal

Make Atom a reliable, approachable Go engineering toolkit: developers can solve one concrete problem or use the full proof-first workflow. Preserve executable evidence, honest limitations, human control, readable Go and test-first implementation while reducing unnecessary ceremony. Website deployment and visibility/distribution work are deferred to a separate local plan after v1.0; they do not block the product release.

The developer accepted this roadmap ordering and then explicitly prioritized product improvements before visibility. It remains a task backlog, not a design spec or a claim that the work is proven. "v1.0" names the improvement milestone; it does not change the package version or announce a release. Implementation begins only through the applicable evidence, design and approval gates.

## Evidence, Decisions And Unproven Assumptions

| Basis | What is established | What is not established |
|---|---|---|
| Shipped review behavior | Default launch-module guidance delivery and fixed-evidence review are on public main; module-rule PR girishmotwani/atom#12 is merged | Delivery is not proof of rule compliance, real-PR recall or improved review quality |
| Verification | Public tooling matches source verified with 1504 passed, 5 skipped and 95% coverage | This is prior evidence, not a fresh validation of future changes or the dirty current checkout |
| Toolchain incident | A local Go 1.26.9+auto workaround resolved an observed incompatibility | It is not a portable project pin or an exact selection guarantee |
| Explicit product decision | Prefer a project-scoped exact Go patch version without changing machine/user defaults | Persistence format, precedence, unavailable-version handling and platform coverage remain undesigned |
| Approved experiment | Ten-case local-only exact-toolchain selection POC is approved but unrun | Its brief still has draft markers; conversation approval does not mean it passed |
| Public discovery | Repository metadata and README positioning are already published; project-account GitHub Pages was selected | No website deployment or community submission is approved; no discovery/ranking result is proven |
| Workflow proposals | Standalone skills, diagnosis, test boundaries, vocabulary and retrospectives address identified friction | Their benefit and final scope require focused evidence; this roadmap is not approval of every proposal |

There is no confirmed project-wide v1.0 POC. Each technical assumption below must be tested at the relevant phase. Existing historical Inconclusive verdicts remain unchanged. No completed item is counted again as new work.

## Delivery Principles

- Keep Go as the target language and Python as Atom's own tooling language; add no shell/PowerShell automation scripts.
- Preserve the full PROVE -> DESCRIBE -> BUILD path for unproven engineering decisions.
- Do not silently relax the current workflow. Any risk-proportionate alternative needs its own explicit policy approval.
- Ship small vertical slices, each with a concrete user outcome, appropriate verification and focused review.
- Prefer independent, public-boundary behavior tests; preserve red/green/refactor and meaningful error coverage.
- No automatic commits, pushes, toolchain installation, external publication or paid review batches.
- Keep canonical and packaged skills consistent; respect installed-version compatibility and upgrade safety.
- Make failures, skipped checks, evidence scope and uncertainty visible. Never invent enforcement.

## Ordered Task Backlog

The accepted order is a default, not an assertion that all tasks depend on those above them. Priority is Must, Should, Conditional or Deferred (post-v1). Dependencies name actual prerequisites; otherwise a task may ship independently.

| Phase | Deliverable | Priority | Risk | Depends on | Evidence needed |
|---|---|---|---|---|---|
| 01 | Reproducible review toolchain | Must | High | None | Approved exact-selection POC, then platform evidence |
| 02 | Honest continuation on tooling incompatibility | Must | High | 01 selection/provenance contract | Classification experiment and failure matrix |
| 03 | Explicit risk-proportionate workflow policy | Must | High | None | Reviewed routing cases and explicit policy approval |
| 04 | Independently useful entry points | Must | Medium | 03 for any new abbreviated path | Routing and isolation trials |
| 05 | Go-specific bug diagnosis | Must | Medium | 04 | Bounded Go defect-reproduction trial |
| 06 | Behavior-focused test boundaries | Must | Medium | None | Focused refactor/defect-detection trial |
| 07 | Shared domain vocabulary | Should | Medium | None | Scoped vocabulary/conflict trial |
| 08 | Evidence-driven retrospectives | Should | Medium | None | Frozen-session suggestion trial |
| 09 | Short onboarding and a worked Go example | Must | Medium | 04 for new entry points | Clean-environment example replay |
| 10 | Crawlable project documentation | Deferred (post-v1) | Medium | 13 and 09; fresh visibility activation | Static-path validation; live checks only after deploy approval |
| 11 | Search/agent/community distribution | Deferred (post-v1) | Medium | 13; 10 for submissions linking the site; fresh activation | Live eligibility/policy checks and measured observations |
| 12 | Real-PR context-quality validation | Conditional | High | None; compare a pinned shipped review version | Separately approved experiment with independent answer keys |
| 13 | v1.0 release readiness | Must | High | In-scope Must phases 01-06 and 09; 12 if making broader review-quality claims | Release checklist, regressions and explicit release approval |

### Phase 01: Reproducible Review Toolchain

**Outcome:** different developers can run a review using the project's declared exact Go patch version.

Tasks:
- [ ] Run the already approved ten-case POC against inherited selection, module suggestions, module minimums and workspace requirements; preserve raw evidence and unchanged-default checks.
- [ ] After the report gate, specify project persistence, override precedence, worktree/PR behavior, missing-version policy and backward compatibility.
- [ ] Implement selection without mutating user defaults; record requested/actual versions and selection provenance in review evidence.
- [ ] Cover unavailable versions, incompatible project requirements, environment isolation and relevant Windows/POSIX behavior. Inspect formatting/build-wrapper provenance separately instead of assuming every executable follows Go selection.

**Done when:** supported environments either run the requested version and disclose it or report an actionable failure; no silent upgrade, installation or persistent-default change occurs. Selection alone is not claimed to make all build inputs reproducible.

**POC:** the approved exact-toolchain brief in the separate `review-toolchain-policy` worktree. No retries, models or downloads are authorized by that brief. **Size:** one focused CLI/config/report slice; split if platform or wrapper support expands it.

### Phase 02: Honest Review Continuation

**Outcome:** confirmed tooling incompatibility can be flagged while reviewers still run; genuine source failures remain blocking.

Tasks:
- [ ] Define demonstrable tooling incompatibility, unknown failures and source failures using structured provenance/control evidence, not broad compiler-text matching.
- [ ] Build a bounded fixture matrix covering incompatibility, source errors, missing tools, timeouts and mixed/ambiguous failures.
- [ ] Approve default/opt-in behavior, classification limits and CLI exit-status semantics before implementation.
- [ ] Propagate failed/unavailable checks and degraded status consistently into the model prompt, Markdown and JSON; preserve existing report consumers where possible.

**Done when:** a proven tooling-only fixture reaches a controlled reviewer stub with an explicit degraded report; code and unknown failures do not silently bypass gates. Existing skip behavior is not relabeled validation. Any real model call needs separate approval.

**POC question:** can the bounded controls distinguish tooling-only failure from genuine/ambiguous source failure without hiding either? **Size:** one review lifecycle slice after the classification contract is agreed.

### Phase 03: Risk-Proportionate Workflow Policy

**Outcome:** the required workflow matches the uncertainty while keeping exceptions visible and human-approved.

Tasks:
- [ ] Distinguish feasibility experiments, regression tests, routine validation and discovery interviews with concrete examples.
- [ ] Define proposed paths for new risky behavior, reproducible bugs, previously proven wiring and documentation-only changes.
- [ ] Specify what may reuse evidence and when changed assumptions require another POC/spec gate; retain findings/decisions and permission boundaries.
- [ ] Work through representative cases and contradictions with the developer, then update canonical and packaged guidance only after explicit approval.

**Done when:** each approved case names a justified next step and required evidence; a documentation correction does not require a fabricated Go experiment, and risky implementation cannot claim a routine-work exemption.

**Evidence question:** do reviewed examples produce consistent, explainable routing without weakening the proof-first boundary? This is a policy-validation exercise, not a performance benchmark. Any live model evaluation needs a separately approved budget. **Size:** one guidance/policy change, not a new workflow engine.

### Phase 04: Independently Useful Entry Points

**Outcome:** a developer can enter Atom with one immediate goal without adopting the entire project lifecycle.

Tasks:
- [ ] Inventory existing commands/skills and reuse them before adding names or overlapping routers.
- [ ] Provide clear entry paths for review, diagnosis, proof experiments and full-feature delivery, with prerequisites and explicit exit conditions.
- [ ] Separate user-facing orchestration from reusable discipline references; prevent invocation loops or conflicting instructions.
- [ ] Verify missing-state behavior, installed-package parity and that no entry path silently launches paid work or publishes changes.

**Done when:** representative requests reach the intended bounded workflow; standalone review retains its evidence/permission limits; the full pipeline remains available and unchanged unless explicitly approved.

**POC question:** can the selected entry paths work in a minimal Go repository without unrelated pipeline state or automatic workflow escalation? **Size:** start with one existing standalone path and generalize only from evidence.

### Phase 05: Go-Specific Diagnosis

**Outcome:** Atom can take a reported Go defect to a narrow reproducer, tested explanation and verified fix.

Tasks:
- [ ] Define symptom capture, reproduction/minimization, falsifiable hypotheses, targeted instrumentation, regression testing and cleanup.
- [ ] Add Go-specific guidance for races, goroutine leaks, cancellation, deadlocks and performance investigation; require the appropriate observed signal rather than every diagnostic tool every time.
- [ ] Exercise one deterministic defect first, then separately scope concurrent/flaky examples; record measured reproduction rates rather than claiming determinism.
- [ ] Specify stop conditions when reproduction, target access or safe instrumentation is unavailable; redact sensitive evidence.

**Done when:** the trial identifies one runnable command that catches the original symptom and passes after the fix; no unexplained instrumentation remains. Broader defect categories are not declared supported from a single trial.

**POC question:** can a small Go cancellation/leak fixture yield a bounded repeatable failure signal and a regression that rejects the broken counterpart? **Size:** one useful diagnosis skill; defer broad tooling integration.

### Phase 06: Behavior-Focused Test Boundaries

**Outcome:** tests protect user-visible contracts without unnecessarily freezing internal structure.

Tasks:
- [ ] Extend the test-spec guidance with boundaries under test and what each catches or misses.
- [ ] Prefer public behavior through real collaborators, with fakes at genuine I/O/time/randomness boundaries.
- [ ] Include Go error contracts, context cancellation, typed-nil risks and concurrency where relevant; do not generate mandatory irrelevant cases.
- [ ] Preserve independent expected values, one red/green slice at a time and refactoring under a green suite.

**Done when:** a focused example survives a behavior-preserving refactor and fails on a deliberately broken contract; important error paths remain covered. This is not a blanket ban on justified internal tests.

**POC question:** does the proposed example demonstrate both refactor resilience and detection of a changed contract? **Size:** guidance plus a small executable example, not a rewrite of existing test suites.

### Phase 07: Shared Domain Vocabulary

**Outcome:** developer, implementation and review use consistent terms for meaningful domain behavior.

Tasks:
- [ ] Define lazy glossary use and ownership; record terms only when needed rather than scaffolding empty documents everywhere.
- [ ] Resolve overloaded terms with concrete scenarios and code evidence; keep implementation detail out of vocabulary definitions.
- [ ] Record durable, surprising trade-offs separately from ordinary task decisions; preserve existing findings/decisions responsibilities.
- [ ] Respect bounded module contexts and explicit evidence delivery. Do not silently broaden module-rule discovery or follow arbitrary linked instructions.

**Done when:** a reviewed fixture distinguishes terms such as cancellation/drain/revocation consistently and surfaces a conflict instead of guessing; any reviewer delivery path is explicit and scoped.

**POC question:** can a small scoped vocabulary resolve the chosen ambiguity without leaking another module's conventions? **Size:** one opt-in guidance slice.

### Phase 08: Evidence-Driven Retrospectives

**Outcome:** a completed session produces a short prioritized list of actionable environment improvements.

Tasks:
- [ ] Review actual session evidence for navigation friction, slow loops, missed checks and redundant instructions.
- [ ] Check existing automation before proposing a new check; separate mechanical detection from judgment.
- [ ] Propose removal/clarification as well as additions; cite evidence and likely benefit.
- [ ] Require approval before changing rules, hooks, CI or user settings; do not build a hidden enforcement mechanism.

**Done when:** a frozen-session exercise produces evidenced suggestions, recognizes an already-present check and makes no unapproved changes.

**POC question:** can the proposed review distinguish one automatable recurrence from one judgment issue without inventing incidents? **Size:** one report-producing skill, not autonomous self-modification.

### Phase 09: Short Onboarding And A Worked Go Example

**Outcome:** a new developer reaches one useful verified result before reading the whole methodology.

Tasks:
- [ ] Put supported prerequisites, installation/update/uninstall steps and a short entry-point choice near the front of the documentation.
- [ ] Build one small public Go example with real commands, outputs and failure boundaries; avoid unsupported agent/model claims.
- [ ] Explain which tasks use the full pipeline and which approved standalone paths apply.
- [ ] Replay from a clean setup and check duplication hazards between installation methods; document supported versions and limitations.

**Done when:** the documented path replays successfully in its stated environment; unverified platforms and dependencies are plainly labeled. No numerical setup-time promise without measurement.

**Evidence question:** can the exact documented commands reach the claimed first outcome on a clean supported setup? **Size:** one example and quickstart; broader compatibility is separate work.

### Phase 10: Crawlable Project Documentation

**Status:** deferred until after v1.0 and explicit visibility reactivation. Retained here for traceability only; the separate local Atom Visibility Plan owns future execution.

**Outcome:** Atom has a useful project-owned documentation site rather than only a repository landing page.

Tasks:
- [ ] Resolve the proposed local `/atom/` sample-validation brief after the workflow-policy decision; reuse it if still appropriate, not as evidence it has already run.
- [ ] Approve a minimal production publishing approach; add landing, quickstart and the verified example with ordinary HTML navigation and useful page descriptions.
- [ ] Validate project-subpath links, canonical URLs, sitemap, accessible content and factual consistency with shipped functionality.
- [ ] Obtain explicit deployment approval; only then configure Pages, verify live responses and link the repository homepage.

**Done when:** approved live pages return the expected content/links and local checks catch broken paths. Indexability is distinct from observed indexing or ranking. A project-subpath robots.txt is not claimed to control hostname-root policy.

**Evidence question:** can the sample export expose its content and links without JavaScript at the real project path? Deployment behavior is checked separately after publication approval. **Size:** minimal useful documentation site; no paid services or custom domain assumed.

### Phase 11: Search, Agent And Community Distribution

**Status:** deferred until after v1.0 and explicit visibility reactivation. Not a product-release requirement.

**Outcome:** people can encounter accurate Atom information through appropriate public discovery surfaces.

Tasks:
- [ ] Check actual live crawler access and distinguish AI search retrieval from model training policy; seek approval for policy changes.
- [ ] Evaluate supported plugin/skill directories and independently verify installation compatibility before listing them.
- [ ] Prepare useful Go problem/solution material and transparent community submission drafts; inspect current community rules before any posting.
- [ ] Define observation dates and available indexing/referral/install evidence without inventing attribution; treat llms.txt as an optional documented aid, not a guaranteed inclusion mechanism.

**Done when:** each approved submission is accurate and its result is recorded. Rejection, lack of indexing or no referral data are valid outcomes. No personal social accounts, impersonation, automated Reddit promotion or guaranteed recommendations are required.

**Evidence question:** is each selected destination eligible, permitted and technically able to consume the published material? No single POC can prove organic adoption. **Size:** one channel at a time; each external write needs approval.

### Phase 12: Real-PR Context-Quality Validation

**Outcome:** review-quality claims reflect independently verified real-PR evidence rather than prompt-delivery success.

Tasks:
- [ ] Obtain an approved experiment brief with pinned inputs, model/run budget, privacy controls and scoring boundaries.
- [ ] Audit evidence omissions; independently establish real/seeded cross-file defects and corrected counterparts without exposing answer keys to reviewers.
- [ ] Compare packaged and fuller context under controlled repeated runs; measure verified-defect recall, false positives and contract grounding.
- [ ] Publish only approved sanitized evidence; narrow claims or re-plan when results are Inconclusive or Refuted.

**Done when:** observations support only the claims the experiment actually tested. Delivery and tool isolation alone do not close this task.

**POC question:** does the pinned evidence package preserve detection of the predeclared verified defects relative to the fuller-context arm? Thresholds, run counts and costs must be approved before running. **Size:** separately budgeted research; do not block unrelated tooling releases unless their claims depend on it.

### Phase 13: v1.0 Release Readiness

**Outcome:** a versioned release has a coherent supported scope, reliable installation and defensible claims.

Tasks:
- [ ] Reconcile the roadmap with shipped evidence; explicitly accept or defer Should/Conditional items instead of silently omitting them. Website and distribution phases 10-11 are already deferred and do not gate the product release.
- [ ] Run relevant Python quality gates and end-to-end Go examples; verify packaged/canonical skill parity and supported platform behavior.
- [ ] Review upgrade/backward compatibility, error/report semantics, release notes, installation instructions and public/private evidence boundaries.
- [ ] Obtain explicit version/tag/publication approval; do not infer it from this roadmap or a local green suite.

**Done when:** every in-scope release claim has linked evidence, known limitations are documented and publication is explicitly authorized. Prior test counts are not used as fresh release evidence.

**POC treatment:** no new broad experiment is justified merely by release aggregation; run the specific integration checks and revisit any remaining unknown separately. **Size:** release verification/documentation, not bundled new features.

## Sequencing And Approval Boundaries

Start with phase 01 because its experiment is already approved and addresses an observed failure affecting other users. Follow with phase 02 so continuation is based on trustworthy toolchain evidence rather than a blanket bypass. Phase 03 must precede any newly abbreviated workflow that changes existing discipline. Diagnosis and test-boundary work deliver the next concrete Go improvements. Vocabulary and retrospectives are independently shippable Should items, not prerequisites for onboarding or the site.

Phase 09 remains product usability work: provide a working setup and example for actual users. Phases 10-11 are deferred until after v1.0 and a fresh visibility activation decision. Preserve the existing unpublished README/site drafts without implementing or publishing them now. The separate local Atom Visibility Plan captures demonstration, documentation, directories, community contributions and measurement. Phase 12 remains an independent research track and gates only the broader review-quality claims that depend on it.

Each phase must produce its own applicable brief/report/spec/test/review evidence plus findings/decisions. Create and register an execution phase only after its scope/evidence gate is valid. Do not register this unproven portfolio as an already approved execution plan. The approved exact-toolchain POC is the immediate next action; it is not authorization for its production implementation.

## Deferred Or Excluded

- Removing human gates, invented compliance systems or automatic broadening of review evidence scope.
- Automatic toolchain downloads, user-default changes, repository rewrites or automatic publication.
- Broad all-agent/all-model compatibility claims, expensive multi-model batches or private-target experiments without explicit approval.
- Rewriting all existing tests, adding a new workflow engine, speculative interfaces or mandatory glossaries/ADRs everywhere.
- Website ranking promises, fabricated adoption metrics, social impersonation or automated promotional posting.
- A release date, universal runtime support matrix or version-number change before evidence and release approval.
- Website deployment, promotion and directory/community distribution before the product-first work is complete and visibility is explicitly reactivated.

## Open Decisions And Risks

| Risk/decision | Treatment |
|---|---|
| Exact toolchain selection may conflict with module/workspace minimums | Phase 01 must fail explicitly rather than silently upgrade |
| Tool incompatibility may be indistinguishable from source defects in some cases | Phase 02 keeps unknowns explicit; approve continuation/exit semantics before code |
| Reducing ceremony could become a loophole | Phase 03 uses concrete reviewed cases and explicit policy approval |
| Additional skills could duplicate existing behavior | Phase 04 inventories/reuses current commands before adding entry points |
| Wider context could introduce conflicting instructions or disclosures | Phase 07 keeps scopes explicit; phase 12 uses private answer keys and sanitized evidence |
| Search eligibility does not imply search or model inclusion | Phases 10-11 report actual observations, not guarantees |
| Scope may exceed a single release | Must/Should/Conditional priorities are proposals; confirm deferrals before release |
| Existing work is spread across worktrees and the current checkout is dirty | Keep this roadmap visible here; perform code in an isolated current-public-main worktree and reconcile existing artifacts deliberately |

## Plan Completeness

- [x] Requested improvements captured without referring to another skills project.
- [x] Tasks, priorities, actual dependencies, acceptance criteria and scope limits recorded.
- [x] Evidence distinguished from explicit decisions and unproven assumptions.
- [x] Existing approved toolchain experiment retained as the next action.
- [x] No implementation, release or external-publication approval invented.
- [x] Portfolio ordering accepted by the developer; subsequently clarified to deliver v1.0 product improvements before deferred visibility work.
- [ ] Each phase passes its own applicable evidence/spec/verification gates before completion.
