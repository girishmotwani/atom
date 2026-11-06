---
project: "atom-v1-improvements"
date: "2026-11-04"
---

# Findings

## Untouched Baseline

- `atom check --no-race` from `tools` exited 2 with `atom check: No go.mod found in C:\Users\gimotwan\work\atom\tools`; this repository implements Atom in Python, so the Go gate did not run.
- `python -m pytest tests -q --cov=atom` from `tools` completed with 1694 passed, 5 skipped, and 95% total coverage (419.79s).
- At discovery, no Phase 03 model calls or production changes had been made.

## Scope Limit

The approved experiment used 10 calls to test whether two models route four fixed cases consistently under the supplied rubric. It cannot establish universal policy correctness, cover every task type, or replace developer review and approval.

## Phase 03 Policy-Routing POC Confirmed

The [POC report](phase-03-risk-proportionate-workflow-policy/poc-report.md) records 10 successful model calls: two availability probes and eight case responses. `gpt-5.3-codex` and `claude-opus-5.5` agreed on all four route labels, used case facts, returned `developer_decides: true`, and proposed no gate bypass. No developer was simulated: this proves only response wording, not that an actual workflow pauses for or honors a developer decision. This confirms only the fixed rubric/case/model sample; it does not establish universal policy correctness or approve guidance changes.

## Phase 09 Existing Documentation And Linux Environment

The README already contains marketplace installation, prerequisites, an `/atom:init` walkthrough, command choices, and an “Atom is its own worked example” section; `docs/workflow.md` contains a conceptual, not executable, Go example. Phase 09 therefore needs to avoid duplicating the current material and add the requested small standalone Go CLI example. The developer selected Linux and authorized updating Copilot CLI in WSL only after the Phase 09 POC brief is approved. Ubuntu WSL currently has Go 1.22.2 and Python 3.12.3, but Copilot CLI 1.0.5 (below the README's stated minimum 1.0.89) and no Atom plugin. No update or plugin installation has occurred.


## Phase 03 Route Taxonomy Is Unvalidated

The case prompts supplied the exact route labels and definitions. Agreement therefore establishes consistent application of that rubric for four synthetic cases, not that the rubric is complete, correct, or independently derived by the models.

## Resumed Phase 03 Findings

- Recovered the original shell 418 output and corrected transcript omissions without new paid calls. Model answers and the narrow observed verdict are unchanged.
- The disposable harness always exits zero; an incomplete/refuted rerun could be automatically labeled Confirmed by `atom poc run`. Windows descendant termination on timeout is unvalidated. Neither path occurred in the observed run; defer instrument changes to a separately scoped experiment.
- The `build/` ignore pattern also excluded `tools/atom/assets/skills/build/SKILL.md`. Added a narrowly scoped exception so the approved packaged guidance can persist in a fresh clone; no broad build-directory exception.
- Corrected the earlier Python baseline command to `-q` and the failed Go-baseline working directory to `tools`. The earlier counts are historical, not a new verification claim.
- Preserved historical roadmap logs below. They describe the earlier planning state: subsequent toolchain/continuation proof and Phase 03 approval supersede their pending-status statements, not their original evidence limits.
- Phase 09 remains at discovery: Linux and a small CLI example are selected, but exact feature/first outcome and its POC brief still need agreement. No WSL setup or update was performed.

## Historical Roadmap Findings (Preserved From Stash 606d50e)

The following is the original 2026-10-30 record, not current task status.

---
project: "atom-v1-improvements"
phase: "n/a"
date: "2026-10-30"
---

# Findings Log

| Finding | Severity | Where | Why not fixed now | Next action |
|---|---|---|---|---|
| No confirmed project-wide v1.0 POC exists | High | `phase-plan.md`, evidence section | User requested a task roadmap, not a proven architecture | Keep the document proposed; prove each technical assumption before design |
| Exact-toolchain POC was explicitly approved but remains unrun; its brief still has a draft checkbox | Medium | Separate `review-toolchain-policy` worktree | Recording roadmap only | Carry conversation approval accurately into the next POC execution/report |
| Tooling-only review continuation has no reliable classification contract yet | High | Phase 02 of the roadmap | Requires experiment and semantics approval | Do not implement broad error-string bypasses |
| Proposed proportional workflow changes are not existing policy | High | Phases 03-04 | Discussion was not policy approval | Review concrete cases and approve guidance changes explicitly |
| Real-PR context quality remains unproven | High | Phase 12; existing pending validation task | Requires separately approved target access, budget and private answer keys | Keep review claims within current evidence |
| Pages hosting direction is selected but deployment/sample validation is not approved | Medium | Phases 10-11; separate public-search-discovery brief | No public writes requested here | Gate implementation/deployment and do not claim indexing results |
| Existing current checkout has unrelated dirty source and POC changes | Medium | Git status before roadmap creation | Preserve all work not authored for this request | Add only the requested new document directory; use isolated worktrees for implementation |

## Ambiguities Resolved

"v1.0" is a proposed improvement milestone, not an instruction to change package versions or publish. The roadmap includes existing reliability/discoverability requests alongside the discussed workflow improvements. The requested plan contains no references to another skills project.

## Learnings

Separate evidence delivery, technical validation and real-world quality/adoption claims. Each needs its own proof. No general repository rule is changed by recording this distinction here.

## Latest Sequencing

The developer accepted roadmap ordering, then explicitly deferred visibility until after v1.0 product improvements. Website and distribution work no longer block release readiness. Earlier notes about pending hosting/publication approvals remain true but are now deferred, not current product blockers. Visibility artifacts are local-only outside Git worktrees, and existing README/site drafts remain unpublished. The approved exact-toolchain POC is the next engineering action and is still unrun.

## Multi-Model Review Awaiting Triage (Historical): 2026-11-05

The [merged review](phase-03-risk-proportionate-workflow-policy/review.md) completed both approved model reviews within four calls, with no retries. Both models flagged the archived always-zero verdict. One reviewer found conflicting start/spec/build/TDD guidance, omitted required-field/probe validation, and incorrect retry arithmetic (uncapped maximum 51, cap still 48).

A newly established evidence limitation: the harness discarded stderr on successful model calls. The ten printed empty stderr records therefore do not prove empty streams; their historical contents are unavailable and must not be reconstructed. The eight complete response JSON objects still support the narrowly observed routing agreement, but claims that all stderr was captured need correction. Windows process-tree timeout cleanup remains unvalidated.

Staging exposed 57 intentional trailing-whitespace blank lines in the verbatim POC output. Earlier unstaged diff checks did not include untracked artifacts. Preserve the literal transcript and explicitly distinguish that exception from cleanliness checks on all other files; no broader whitespace waiver.

At that review gate no findings were fixed and no commit/push/PR had occurred. Triage was then pending (subsequently approved in decisions.md); proposals and rejected-as-blocker preferences are explicit in the review report.

## Start Routing Repair Verification: 2026-11-05

Review finding 2 is repaired in `com.github.copilot/commands/start.md`. The router now selects the earliest outstanding beat under the approved evidence choice rather than requiring a new spike for every missing POC artifact. Confirmed evidence/approved skips lead to spec; proposed alternatives stop at the evidence-choice gate; regression failure must exist before design; runtime implementation still requires spec approval. Documentation-only work does not invent a Go spike.

Captured validation:

```text
python tools\check_links.py
checked 415 relative links across markdown files
all relative links resolve
```

From `tools`:

```text
python -m pytest tests\test_plugin.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 11 items

tests\test_plugin.py ...........                                         [100%]

============================= 11 passed in 0.62s ==============================
```

`git diff --check -- com.github.copilot/commands/start.md` exited 0 with no whitespace errors (Git emitted a CRLF-to-LF normalization warning). These checks validate links and command discovery, not actual model routing or developer-control behavior. Semantic review confirms alignment with the approved shared policy. Other approved guidance/provenance/harness repairs remain pending; Windows lifecycle validation remains deferred. No commit, push, PR or paid review rerun occurred.


## Remaining Review Repairs Implemented: 2026-11-06

The accepted build/spec/TDD guidance conflicts and packaged copies are repaired. The archived harness now rejects missing/null decision booleans, emits specific rejection diagnostics, requires READY probes, captures successful stderr and exits nonzero for Refuted/Inconclusive. Regression failures exposed each changed behavior before repair; focused GREEN runs passed. Final combined validation is recorded in the repair verification artifact.

Corrected the uncapped maximum to 51 while retaining the approved hard cap of 48 and actual ten-call result. Corrected stale brief/review metadata. Historical successful stderr was discarded and is unknown; original transcript and raw model-review JSON are preserved unchanged. The review findings table and snapshot remain historical, not a review of repaired code.

Still deferred: Windows descendant-process cleanup and wall-clock timeout validation, actual developer-control behavior, taxonomy completeness and repeated/live model quality. No new model calls, paid rerun or installation. Publication remains pending final verification and the applicable completion gate.

## Repair Verification Complete: 2026-11-06

The [repair verification log](phase-03-risk-proportionate-workflow-policy/tdd-log.md) contains actual RED/GREEN and combined gate output. All required archive Go gates passed (build, vet, format, tests and race); 50 selected Python documentation/distribution tests passed. Seven canonical/packaged instruction pairs match after native newline normalization. The historical POC transcript and raw review JSON hashes are unchanged; exactly 57 literal indented transcript blank lines retain the already disclosed whitespace exception.

The initial byte-parity assertion exposed only native CRLF/LF differences, not content drift; the final check compares newline-normalized text. The initial incomplete-result fixture exceeded its one-minute test budget; the corrected three-minute fixture reproduced the intended assertion failure, then passed after the repair. Neither issue establishes a Windows lifecycle guarantee.

Remaining uncertainty is unchanged: Windows descendant/timeout cleanup, live model stability, taxonomy completeness and real developer-control behavior are not proven. There were no new model calls, dependency installs, commits or pushes. The repaired snapshot awaits the completion gate.

## Shipping Boundary: 2026-11-06

The repaired-snapshot completion gate was explicitly approved and the developer renewed the push/PR request. Fresh archive Go and selected documentation/distribution checks passed; their exact output is retained in the phase tdd-log. No new model calls were made.

Open findings remain Windows process-tree/wall-clock timeout validation, actual developer-control behavior, taxonomy completeness and live model stability. They are disclosed limitations, not evidence that these paths were validated. The earlier roadmap and review records are historical; publication does not implement later phases or authorize merging either stack layer.
