# Decisions: changed-file review formatting

## Scope choice (2026-10-22)

The developer requested changed-file review scope and explicitly chose "formatting-only" when asked whether the immediate fix should also change package-based build/vet/test scope. Limit the first correction to review formatting; preserve all other review checks and standalone full-module atom check. Reading unchanged context is not prohibited by a changed-file finding/check scope.

The formerly approved whole-module baseline probe was superseded before execution. Its approval does not authorize this different experiment. Use a new, small synthetic Git/gofmt proof rather than spending on the private PR or reviewers.

A Python harness and two-minute fixed-fixture budget are proposed for approval. Production APIs/design and implementation remain pending proof. Existing runner/helper knowledge is reused, but no POC source will be promoted into production.

The initial tooling baseline uses existing Python tests because this repository's implementation is Python; no root Go baseline is claimed. Relevant captured output is cited in the brief. No deviations are silently waived and no broader gate policy is relaxed.

## Brief approved (2026-10-22)

The developer explicitly answered true to this exact two-minute synthetic Python proof before the production fix. Approval covers the fixed Git/gofmt fixture cases, shared budget and cleanup reserve, zero model calls or target repository access, unchanged production source and the formatting-only boundary. It authorizes building and executing this proof only. End this gate turn before starting; stop again at the executed report before production design/TDD.

## Standing gate waiver: formatting-only correction through draft PR (2026-10-22)

The developer requested continuation until a PR is published, then explicitly answered true to proceeding without routine gate pauses through the approved proof, spec, test-first implementation, two independent non-author model reviews, fixes and a draft PR in girishmotwani/atom. The developer subsequently said "continue".

Scope: this changed-file formatting correction only; other review checks and standalone module-wide atom check stay unchanged. Spend: at most two independent non-author reviewer calls, one review round; local fixed-fixture proof and existing Python checks. The approved two-minute proof retains its exact cases and budget. Publish/push permission is explicit; do not merge or mark ready automatically.

Limits: stop for Refuted/Inconclusive proof, a material scope change, or an unresolved validation/privacy blocker. No other project phase, private ADO review/check rerun, extra model batch or broader validation-policy change is authorized. Record artifacts and evidence at each beat even though routine pauses are waived.

## Executed proof (2026-10-22)

The single fixed synthetic attempt completed all 14 observations with exact input hashes, unchanged original/tooling checkout audits and owned fixture removal. Verdict Confirmed; see poc-report.md for actual output and limitations. Pure rename status and selected snapshot identity must be preserved in production. No private target checks or models ran. Under the explicit scoped routine-gate waiver, proceed to the formatting-only design/TDD increment, not another project phase.

## Publication-safe worktree and design (2026-10-23)

Use branch fix/review-changed-file-formatting in a separate clean worktree based on merged personal main 93fa0eef5e20117dc41420066f689b7580a97683. Its tools tree is byte-identical to the verified discovery baseline's a90fbe1 revision. Copy only this correction's generic proof and neutral specs/review-format-scope artifacts; change the publication bundle's project label, not its question or captured evidence. Do not copy the private ADO parent investigation or its inputs/logs.

The spec is accepted under the developer's explicit scoped routine-gate waiver. Production must preserve exact snapshot bytes and truthful formatting coverage; binary-safe owned Git transport and raw-manifest parsing are integration assumptions to cover with regression tests. No general runner/result schema or default module-wide check changes are permitted.

## Personal repository made public (2026-10-23)

The developer explicitly requested public visibility for girishmotwani/atom. Before the change, inspected 15 reachable branch/PR-head refs, 1,652 objects / 813 blobs (21,300,427 blob bytes), 121 commit messages, seven PRs, one review and all 28 retained workflow log archives for known private ADO markers and credential patterns; none were flagged. No releases, Actions artifacts or initialized wiki existed. Published refs were unchanged at the visibility change. GitHub then verified visibility PUBLIC and isPrivate false. This is a bounded publication-readiness check, not a universal secret-detection guarantee. The original enterprise repository and checkout were not made public or modified.


## Test-first integration and fixture corrections (2026-10-23)

Observed each new production behavior fail before implementing it: working-file scope, immutable staged bytes, committed branch bytes, pure rename canonical paths, zero-file skip, module exclusions, honest prompt coverage, non-regular Git entries, strict manifests, invalid UTF-8 and working-path substitution. Additional fault/encoding/path guards exercise behavior already present; their immediate passes are not claimed as RED evidence.

The initial UTF-8 clean-source fixture was not actually gofmt-clean: gofmt inserts a blank line between a variable declaration and the trailing comment. The exact command output in the session showed that inserted newline. Corrected the fixture by adding that blank line, retaining exact stdin/byte-preservation and clean-verdict assertions; production code was unchanged for this fixture correction.

The pre-existing build-failure unit fixture had no Git responses because checks formerly ran before diff acquisition. Added explicit repository-root and empty raw-diff responses to its FakeRunner and removed the unused module-wide gofmt response. Its original required build-failure and no-model assertions remain unchanged. Real Git integration tests separately cover all new acquisition behavior.

Canonical finding/report paths stay repository-relative, matching the raw manifest and --no-relative patch even when invoked from a module below the Git root. Formatting scope explicitly records outside-module and nested-module exclusions. Standalone default_gates and FormatGate are unchanged. No general CommandRunner/CommandResult change, dependency, global Git setting or private-target access was introduced.

## Full-gate integration corrections (2026-10-23)

The first full Python gate reported 1 failed, 1058 passed and 2 skipped. Its single failure was the existing skill source/package equality contract: the formatting documentation update also belongs in tools/atom/assets/skills/review/SKILL.md. Applied the same edits to that packaged skill; did not weaken the equality assertion. A fresh full gate is required before independent review.

CLI coverage is additive JSON toolchain evidence using existing gate fields; all pre-existing JSON fields and schema version remain unchanged. Markdown and reviewer prompts name changed-file formatting instead of claiming gofmt -l . ran. A Git type change has one raw record but two patch blocks; account for that real framing before selecting the surviving content. These are integration fixes within the approved canonical-path/snapshot contract, not new check policy.

## Independent reviewers selected (2026-10-23)

No .atom model-role configuration exists in the clean publication worktree or original tooling checkout. Before spending the two authorized calls, asked the developer for one reviewer pair. The developer explicitly selected claude-opus-5.5 and gemini-3.8-flash. Use exactly one read-only review task per selected model, independently and without sharing findings. Both differ from the GPT-6.1 Sol author. No availability probe, third call, private target read or extra model batch is authorized. Local Python gate is green before review: 1059 passed, 2 skipped, 95% total coverage; see verification.md.

## One review round and repairs (2026-10-23)

Exactly one independent read-only call ran for each developer-selected model. Opus found two medium issues; Gemini reported no significant issues. Accepted both concrete Opus findings despite no corroboration and fixed each after a new failing regression. No extra reviewer/probe call ran. See review.md for full triage, scope and limitations.

Pin the local capture command's submodule display to short without changing user Git config; long/log/diff display can otherwise alter manifest/patch framing. Preserve valid unread manifest paths: native-platform source safety checks apply only to surviving in-module Go input, while basic relative-path validation applies to the manifest. Determine module membership from Git components before interpreting native paths. The special-name regression uses manifest injection on Windows and does not claim real POSIX checkout execution.

The existing build-failure FakeRunner's exact capture command now includes --submodule=short, matching production; its original build failure/no-model assertions remain intact. No correct assertion was weakened. No material scope or public check-policy change was introduced.

## Evidence presentation and whitespace

Captured pytest output contains trailing whitespace and embedded Markdown examples. Preserve those command bytes apart from explicitly documented home/worktree path redactions, using longer tilde fences outside transcripts to prevent embedded triple-backtick examples being interpreted as navigation. The existing link checker now resolves all 237 links. Staged production/source/packaged documentation passes git diff --check; the full artifact-inclusive whitespace check reports retained transcript whitespace and extra EOF blank lines in copied proof artifacts. Those are recorded presentation costs, not hidden production failures; no global Git setting or CI check was disabled.

## Archived proof byte provenance (2026-10-23)

The final staged-proof hash check initially differed from the report's as-run hash. Read-only SHA-256 comparisons resolved the difference exactly: the publication archive has three trailing LF bytes, and removing one final LF reproduces the recorded as-run hash. The artifact-copy pipeline added that one EOF byte. Preserve the archive and original as-run hash rather than silently treating different byte sequences as identical; publish the archive hash and transformation in poc-report.md. No proof rerun, input change, verdict change or production edit occurred.

```text
archive_length= 14583 trailing_LFs= 3
removed_LFs= 0 sha256= 9d99d7808ae06a1b0121c37ec4900947cc4c78ea3745c903ed4d28d2c7a02e6d matches_as_run= False
removed_LFs= 1 sha256= fe87433d3bcb4f4d5c4a6b8ad501d9bd46682761e08eeb6084c2f066c3241c48 matches_as_run= True
```
