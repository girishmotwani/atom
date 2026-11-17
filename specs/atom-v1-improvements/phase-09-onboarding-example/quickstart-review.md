---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-17"
status: "verified-fixes-accepted"
---

# Standalone Quickstart Documentation Review

## Result

Two independent non-author reviews completed. Claude Opus 5.5 raised one Major and one Minor; Gemini 4 Argon reported "No findings." Both findings are retained, agreement 1/2 each. Both findings are now fixed under the approved scope, with six synthetic failure cases passing in both normal and forced-interactive Bash, plus documentation checks. Neither finding is deferred or rejected. The developer accepted both verified documentation fixes; the two model passes apply to the original snapshot, not an independently re-reviewed fix. This is not a clean-review verdict, final-page replay, shipping approval or Phase 09 completion.

## Approval, Snapshot And Scope

Developer explicitly selected "Approve two reviews with Claude Opus 5.5 + Gemini 4 Argon", then said "lets launch reviews". Exactly one read-only pass per named model was launched; no additional batch or automatic retry. Author: GPT-6.1 Sol, neither reviewer.

| Reviewer | Agent ID | Result |
|---|---|---|
| Claude Opus 5.5 (claude-opus-5.5) | 962922d4-6b7f-4bef-a765-c62943befee5 | One Major, one Minor |
| Gemini 4 Argon (gemini-4-argon) | c1366e72-136d-423e-870d-3fa38ba673d6 | No findings. |

HEAD: 6b094984bf2213db9af238d76bcf1cc8b0381dff. Tracked changes compared to HEAD; new quickstart reviewed in full. Three public-document scopes:

- docs\quickstart.md: full new page, including setup/request/approval/outputs/limits.
- README.md: changed Try Atom section and surrounding context.
- docs\workflow.md: changed opening qualification and quickstart link with context.

Both reviewers report reading all four supplied evidence artifacts in this phase directory: quickstart-design-spec.md, standalone-quickstart-report.md, standalone-quickstart-recipe.md and standalone-quickstart-preparation.md. Both read AGENTS.md. Claude additionally inspected skills\poc\SKILL.md to confirm the expected scaffold/run subcommands. Neither reports executing the examples, changing files or consulting the other's findings. README/workflow are not represented as full-document substantive audits outside the changed scopes.

Raw-byte SHA-256 snapshots, verified before launch and after both reviews:

| Document | SHA-256 |
|---|---|
| README.md | 1e722c670c8a5a8a36b83971d61a4a26561298ac9fad5a0ef1418609cac33fa1 |
| docs\quickstart.md | e3f835ba29690f87d57f098666db78198cd7928926793e207257d79583a8476d |
| docs\workflow.md | 90d32ca762af1ddf04bab3e80ba642932ec5a7c74e54f8a3096995ba48433194 |

The discovery-helper code, tests, skills and existing review.md are separate and unchanged. No private participant workspace or recording was reviewed. Findings are deduplicated below by location and substance; there are no duplicates to collapse.

## Original Merged Findings (Before Approved Fix)

### Major: Setup failures can exit the reader's interactive shell and obscure diagnostics

- Agreement: 1/2 (Claude; Gemini raised no finding).
- Location: docs\quickstart.md:29-44, with failure instructions at 67-70 and persistent-shell note at 135-136.
- Trigger: The page tells the reader to paste the setup block into a dedicated interactive terminal. The block enables set -e directly in that shell, and its existing-destination guard calls exit 1. A failed prerequisite/install/help command can therefore terminate that shell rather than just the setup operation. If Copilot is absent from PATH, the type -P assignment fails without an explicit diagnostic.
- Consequence: The promised "keep the actual diagnostic and stop" boundary is unreliable. A terminal configured to close when its shell exits can hide the diagnostic; even when the window stays open, the interactive session is gone. Successful setup also leaves errexit enabled in the parent trial shell. Window-closing behavior is terminal-dependent, not a universal Ubuntu/WSL claim.
- Contract/evidence: Spec requirements 3-5 and Failure And Stop Handling require preserving setup/diagnostics and stopping on failed setup. The accepted recipe used guarded launch logic rather than enabling errexit in the parent interactive shell. This behavior was introduced by the independently unreplayed documentation translation; passing bash -n does not validate it.
- Suggested bounded fix: Keep setup failure isolation inside a child shell/subshell, with environment settings and Copilot launch inside the same child, so failure returns to the reader's terminal. Print an explicit missing-Copilot diagnostic. Update only directly dependent setup/rerun wording. Do not introduce a shell-script file, installations, broad permissions or a new end-to-end replay.
- Coordinator assessment: Retained as Major after inspecting the exact lines; no runtime reproduction was executed or claimed. The defect is based on shell control flow, while visibility of a closed window remains conditional.
- Triage: Developer approved fix now on 2026-11-17. Subshell isolation and explicit executable diagnostics are implemented and validated below; accepted by the developer on 2026-11-17.

### Minor: Writer-permission wording can be mistaken for a ban on needed Atom subcommands

- Agreement: 1/2 (Claude; Gemini raised no finding).
- Location: docs\quickstart.md:101-104.
- Trigger: The paragraph says to approve only atom-write-artifact for artifact writes, "not the broader atom executable", but does not explicitly distinguish blanket executable approval from narrow prompts for atom poc new and atom poc run. "For this repository" can also suggest a repository-wide saved grant despite the preceding no-persistent-grant language.
- Consequence: A reader may deny the scoped scaffold/run actions needed for the promised POC evidence, or misunderstand permission persistence. The existing "for ... artifact writes" qualifier means this is an ambiguity, not a categorical instruction that every atom command is forbidden.
- Contract/evidence: Spec requirement 8 requires understandable displayed-action approval without all-tools or persistent permission. The request explicitly requires atom poc run evidence; the accepted report records specific-command, session-only approvals.
- Suggested bounded fix: Explicitly permit understood, displayed atom poc new expense-summary and atom poc run expense-summary actions; reserve artifact-content writes for atom-write-artifact, and distinguish that narrow permission from broad executable-wide or persistent grants.
- Coordinator assessment: Retained as Minor wording clarification, not proof that a participant actually denied a command or that the old client's permission UI has particular wording.
- Triage: Developer approved fix now alongside the setup correction on 2026-11-17. Scoped scaffold/run permissions and writer-only artifact permissions are clarified; accepted by the developer on 2026-11-17.

## Deterministic Preflight

Approved documentation-only adaptation: no root Go module, so Go build/vet/gofmt/race were inapplicable, not passed. No Python suite, static analyzers or live setup/replay ran. Unchecked categories are not excluded. Models received the same preflight facts and evidence limits before review.

Command: python tools\check_links.py, followed by scoped git diff --check -- README.md docs\workflow.md and git rev-parse HEAD. Exit 0; captured stdout:

```text
checked 577 relative links across markdown files
all relative links resolve
Tracked public-document git diff --check exit=0
6b094984bf2213db9af238d76bcf1cc8b0381dff
```

Separate inline Python checked approved hashes, new-file trailing whitespace and each Bash block through wsl.exe --distribution Ubuntu --exec bash -n with actual UTF-8 LF input bytes. Exit 0:

```text
Approved snapshot matches: README.md
Approved snapshot matches: docs/quickstart.md
Approved snapshot matches: docs/workflow.md
quickstart bash block 1: LF-byte syntax check exit=0
quickstart bash block 2: LF-byte syntax check exit=0
checked 2 Bash blocks; no commands executed
New quickstart trailing-whitespace check passed
```

Git warned that docs/workflow.md working-copy CRLF will normalize to LF. Syntax validation deliberately avoided Windows CRLF transport. After both reviews, raw hashes and HEAD were checked again, exit 0:

```text
Reviewed snapshot unchanged: README.md
Reviewed snapshot unchanged: docs\quickstart.md
Reviewed snapshot unchanged: docs\workflow.md
6b094984bf2213db9af238d76bcf1cc8b0381dff
```

## Evidence Limits And Proposed Next Step

Both reviews were static and do not establish terminal-window behavior, authentication, marketplace immutability, universal CLI compatibility or independent final-page usability. The accepted assisted-run/shared-cache/moving-marketplace limits remain. One reviewer separately noted uncertainty about combining --no-auto-update and --version; the preparation evidence records that exact combination succeeding for the observed 1.0.107 client, so no additional compatibility defect is established. This does not claim support in every version.

Recommend fixing both findings now within the existing documentation contract. Because the shell failure is understood, propose a bounded synthetic Bash failure-path check (no installer, installed CLI or model calls) to verify parent-shell survival and visible diagnostics, then existing link, LF-syntax and whitespace checks plus factual permission-text review. Alternative: explicitly defer or reject a finding with rationale; no silent drop or automatic fix. No new Go spike, full install replay, second review-model batch or production code is required or approved.

Developer selected exactly: "Fix both now with bounded shell validation and documentation checks". Authorize only those contract-preserving documentation corrections, bounded synthetic shell failure checks and existing documentation validation. No installation, live replay, additional model review, commit, push, publication or Phase 09 completion. End the triage-gate turn before starting the newly approved work.

## Post-Fix Implementation And Validation: 2026-11-17

The developer said "lets fix" after the explicit fix-now approval. Changed only docs\quickstart.md and existing review/findings/decisions artifacts. The setup block now runs wholly inside parentheses, including its set -e, environment exports and Copilot launch. A failed operation returns to the caller shell; it is not wrapped in an if/OR test that would suppress errexit inside the block. Missing, unresolvable and non-executable Copilot cases get explicit diagnostics. Updated directly dependent setup/rerun wording. Permission text now names the expected atom poc new/run expense-summary actions with displayed options, distinguishes them from blanket atom permission, and reserves artifact-content permission for atom-write-artifact and intended paths.

Existing spec requirements 3-5, 8 and 10 cover these corrections. Requirement 5 already allows child-only settings; no contract or design-spec change is needed. The install commands, pin, marketplace-update/shared-cache caveats, request/fixture/outputs and brief/report gates are unchanged. README and workflow hashes still match the reviewed snapshot. No shell-script file, runtime/skill/helper/package or production test changed.

### Bounded Shell Regression Method

Kept a Python-only validation harness and JSON captures in the current session's files directory: check_quickstart_shell.py, quickstart-shell-before.json, quickstart-shell-after.json, quickstart-shell-after-final.json, quickstart-shell-interactive.json and quickstart-shell-interactive-after.json. These are retained local evidence, not packaged tooling or a public source addition.

The harness extracts the actual first Bash block from docs\quickstart.md and executes it as a standalone command, never as an if/OR condition. It invokes wsl.exe --distribution Ubuntu --exec bash --noprofile --norc -s; the additional interactive pass uses -i -s. PATH/HOME, executable discovery, filesystem predicates and prerequisite commands are synthetic stand-ins. Later stages are denied, all cases stop before filesystem creation, and no installed Copilot/Atom/Go/Python tool, installer or marketplace command is invoked by the example. No shell-script file or trial workspace is created. This validates document shell control flow under the supplied failure boundaries, not real filesystem discovery, terminal-window configuration, successful installation or end-to-end usability.

For each case, the parent must survive, observe setup exit 1 (23 for the injected Go prerequisite failure), retain its flags/umask/cwd/HOME/PATH/TMPDIR/COPILOT_HOME/COPILOT_AUTO_UPDATE, emit the case's actual diagnostic and never reach a denied later stage. The outer validation shell exits 0 on success; that does not convert the failed setup into success.

Before the edit, invocation of the harness with --save quickstart-shell-before.json exited 1. Captured stdout:

```text
FAIL existing-destination: shell_exit=1; setup terminated the parent shell; parent did not retain the expected setup failure exit; parent shell/environment state was not preserved
FAIL dangling-symlink: shell_exit=1; setup terminated the parent shell; parent did not retain the expected setup failure exit; parent shell/environment state was not preserved
FAIL missing-copilot: shell_exit=1; setup terminated the parent shell; parent did not retain the expected setup failure exit; parent shell/environment state was not preserved; explicit failure diagnostic missing
FAIL unresolvable-copilot: shell_exit=1; setup terminated the parent shell; parent did not retain the expected setup failure exit; parent shell/environment state was not preserved; explicit failure diagnostic missing
FAIL nonexecutable-copilot: shell_exit=1; setup terminated the parent shell; parent did not retain the expected setup failure exit; parent shell/environment state was not preserved; explicit failure diagnostic missing
FAIL prerequisite-failure: shell_exit=23; setup terminated the parent shell; parent did not retain the expected setup failure exit; parent shell/environment state was not preserved
0 passed; 6 failed
```

The original noninteractive post-fix pass exited 0 with all six cases passing. To check the actual interactive-shell target rather than infer it only from script mode, added the same assertions under forced-interactive Bash. That first interactive harness invocation falsely reported six failures: its substring oracle treated echoed function definitions containing UNEXPECTED_EXTERNAL_STAGE as emitted execution diagnostics. Every capture already showed parent_survived=yes, parent_state=unchanged and the expected setup status. This was an evidence-parser defect, not a document failure.

Corrected only the harness oracle to match actual emitted diagnostic/sentinel lines, not quoted source echoed by interactive Bash. This also strengthens the positive diagnostic check: a diagnostic quoted in the setup source cannot satisfy it. No shell-survival, state, exit-status, diagnostic or denied-stage requirement was removed. Kept the failed interactive capture rather than overwriting it. Reran both modes with the same six cases and corrected oracle. Each invocation exited 0 and printed this same output:

```text
PASS existing-destination: shell_exit=0; parent survives, diagnostic visible, state unchanged
PASS dangling-symlink: shell_exit=0; parent survives, diagnostic visible, state unchanged
PASS missing-copilot: shell_exit=0; parent survives, diagnostic visible, state unchanged
PASS unresolvable-copilot: shell_exit=0; parent survives, diagnostic visible, state unchanged
PASS nonexecutable-copilot: shell_exit=0; parent survives, diagnostic visible, state unchanged
PASS prerequisite-failure: shell_exit=0; parent survives, diagnostic visible, state unchanged
6 passed; 0 failed
```

Final capture arguments were --save quickstart-shell-after-final.json and --interactive --save quickstart-shell-interactive-after.json. The script and captures use absolute paths within this session's files directory; commands ran from the repository root. Forced-interactive stdin is not a GUI-terminal or cold-install replay.

### Documentation Checks

Command: python tools\check_links.py, followed by LF-byte bash -n for both published Bash blocks and new-page whitespace/EOF checks. Exit 0; captured stdout:

```text
checked 577 relative links across markdown files
all relative links resolve
quickstart bash block 1: LF-byte syntax check exit=0
quickstart bash block 2: LF-byte syntax check exit=0
New quickstart whitespace checks passed
quickstart nonblank lines: 155
```

Read the full corrected page and checked the affected requirements against the approved spec and original evidence. Tracked navigation whitespace check exited 0. No new reviewer batch, installation, live Copilot/Go replay, Python/Go suite, static analysis, clean-machine claim or independent final-page usability result. The original model reviews are not represented as a second review of the corrected bytes. Neither finding remains unfixed or deferred; post-fix implementation acceptance is recorded below.

### Final Persistence Check And Fix Acceptance

After writing the review and logs, reran the link checker, scoped tracked-document/artifact git diff --check, new-page/report whitespace and EOF checks, and README/workflow hash checks. Exit 0; captured stdout:

```text
checked 577 relative links across markdown files
all relative links resolve
Final tracked-document/artifact and new-file whitespace checks passed
README and workflow remain unchanged from the reviewed snapshot
Corrected quickstart SHA-256: 57ec287e117a361eab22d4c4b539158790e9132601f32a549f29c6ae488d2a62
```

Developer selected exactly: "Accept both verified documentation fixes" after the corrected surface, synthetic validation, evidence path and no-live-replay/no-second-review limits were presented. Both findings are fixed and accepted, not deferred or rejected. Acceptance covers only these documentation fixes; no commit, push, publication, additional experiment or Phase 09 completion. End this gate without starting the next step.
