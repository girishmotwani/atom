---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
author: "Copilot"
date: "2026-11-07"
status: "approved"
---

# Phase 09 Replay Brief

## Problem

A new developer should reach a useful verified result without first reading Atom's
whole methodology. The existing README covers setup and commands, while
docs/workflow.md gives a conceptual walkthrough rather than an executable example.
The developer selected a Go CLI that summarizes expenses by category, built from
scratch with Atom. The main uncertainty is whether the prompts and gates make the
next action understandable without the full methodology.

The developer will perform the first replay personally and explicitly selected an
experienced-user rehearsal. This cannot prove genuine newcomer usability. The
initial environment is the existing Ubuntu WSL installation plus a fresh example
module, not a clean machine or independently provisioned Linux host.

## The Question

Can the developer complete one bounded Ubuntu WSL rehearsal from a fresh example
module to a tested expense-summary CLI using only the frozen candidate quickstart,
the actual Atom prompts, and the artifacts presented at its gates, without opening
the full methodology or bypassing an applicable approval?

## Evidence Recommendation And Alternatives

Recommend a bounded observed workflow replay, not an artificial Go feasibility
spike. A Go parser demonstration would not answer the selected human-interaction
question. The recipe and the generated CLI are disposable evidence; they are not
the final Phase 09 design or public worked example.

Existing evidence: the README documents marketplace installation, /atom:init and
the individual beats; local onboarding/plugin tests pass. Phase 03's synthetic
model agreement did not test actual human understanding or approval behavior.
The approved roadmap explicitly calls for an example replay.

Alternative: use a Go developer new to Atom for a real first-use trial. That would
address the original usability question more directly. The developer chose an
experienced-user rehearsal first; a newcomer trial remains separate future work.

- Feasibility: no new CSV algorithm feasibility claim is the target.
- Performance: four synthetic rows do not need a throughput experiment.
- Integration: plugin installation and onboarding must actually work before the
  workflow can be evaluated; record any blocker, do not hide it as a UX result.
- Ergonomics: this is the developer-selected risk. Producing more documentation
  before observing the workflow could merely repeat its existing confusion.

Approval of this brief approves this evidence method and its bounded rehearsal,
not the final example's design or implementation.

## Proposed Example Contract

These are proposed acceptance boundaries for approval, not an implementation design:

- Read one UTF-8 CSV file with the header category,amount.
- Use synthetic amounts in one currency, with two decimal places; include one
  negative refund. Do not add currency conversion or accounting features.
- Report one exact total for each category. Presentation details can be settled
  in the example's own gated spec; expected numbers are independent of the code.
- An invalid amount and a missing input file must fail visibly with a nonzero
  process exit, rather than silently dropping data or printing success totals.

Happy-path fixture:

```csv
category,amount
food,12.50
travel,5.00
food,7.50
travel,-1.25
```

Independent expected totals: food = 20.00; travel = 3.75.
An invalid-amount fixture replaces one amount with oops.

No numeric representation, parsing abstraction, package layout or dependency
choice is prescribed here. Do not prewrite the feature or its tests before the
example's own evidence/spec/implementation approvals.

## Candidate Quickstart To Freeze Before The Rehearsal

The participant may read this compact recipe and each presented artifact, but not
AGENTS.md, the discipline references or docs/workflow.md as a human help manual.
The agent must still read the instructions required by its skills.

1. Record the existing Linux tooling and plugin state. Current README prerequisites
   are Copilot CLI >= 1.0.89, Go >= 1.21, Python >= 3.10 and git. These are documented
   minima, not newly proven compatibility across every version.

   ```text
   copilot --version
   go version
   python3 --version
   git --version
   ```

2. After brief approval and ordinary command approvals, update Copilot CLI only
   inside Ubuntu WSL if needed, using its official supported installation method.
   Do not change Windows tools, Go/Python defaults, authentication or existing
   repositories. Stop if additional provisioning or login is required.
3. Use the public marketplace path, not a local clone or preview branch:

   ```text
   copilot plugin marketplace add girishmotwani/atom
   copilot plugin install atom@atom
   copilot plugin marketplace list
   copilot plugin list
   copilot skill list
   ```

   If Atom is already installed or the marketplace points elsewhere, stop and
   resolve the conflict explicitly rather than mixing installations. Record the
   actual installed version/source and freeze that snapshot for the attempt.
   A public-marketplace trial does not claim to exercise unmerged Phase 03 code.
4. Choose the Linux home directory, outside the Atom checkout, and create a new
   disposable module. If the named directory already exists, stop; do not reuse or
   remove it automatically. These are manual terminal commands, not a new script:

   ```text
   cd "$HOME"
   mkdir atom-phase09-rehearsal
   cd atom-phase09-rehearsal
   git init
   go mod init example.com/expense-summary
   copilot
   ```

   Do not supply the working CLI. Inside that session run /atom:init. Capture its
   untouched baseline even if an empty module reports no packages; do not describe
   onboarding as a clean build by default.
5. Enter:

   ```text
   /atom:start Build a Go CLI that reads an expense CSV and prints totals by category.
   ```

   Supply the proposed fixture/contract from this brief. Follow the actual next
   beat Atom requests, rather than a new shortcut or a guessed command sequence.
   Tell the agent that no commit, push, model-review batch or extra agent launch
   is authorized. Do not approve broad unrelated command permissions.
6. At each gate, read the named artifact and decide explicitly. A brief approval
   allows only its experiment; a report approval allows the stated next beat; a
   design approval allows only that implementation. Ask for clarification or
   withhold approval when needed. Do not automatically answer yes to every gate.
   Observe at least one actual pause before approval; record whether work waits.
7. After the example's own approved implementation, run its recorded build/test
   commands, full atom check with race enabled, and go run . expenses.csv.
   Check the two independent totals and the invalid-amount/missing-file failures.
   Stop at the verified implementation gate, before multi-model review or shipping.

The public quickstart and example are not written or declared complete by this
rehearsal. Final documentation must be based on the captured behavior and later
approved Phase 09 spec.

## Proposed Bounds And Stop Conditions

- One attempt, one interactive Copilot CLI session, one small example.
- Operator-controlled cap of 60 minutes of active rehearsal. This is a proposed
  spend/effort bound, not a setup-time promise or automatically enforced timeout.
- Normal interactive model responses in that session require brief approval.
  No parallel agents, additional model-review batches or automatic retries.
  Record the chosen model and observed turns/calls where the CLI exposes them;
  one session is not a fixed monetary or API-call guarantee.
- Record setup time and active workflow time separately, without a speed claim.
- Stop for the time cap, missing access, unexpected installation scope, ambiguous
  permissions, a required additional model batch, or a gate that cannot be resolved
  from the permitted material. Preserve partial output and decide the next step
  with the developer; do not repair the guide during the frozen attempt.
- The candidate recipe must be reviewed for completeness before starting the
  clock. Any necessary material change returns to a brief/recipe approval.

## Verdicts And Required Evidence

| Observation | Verdict |
|---|---|
| The bounded recipe reaches the correct CLI result, its negative checks and full Go gate pass, all approvals are actual participant decisions, and no outside methodology/coaching is needed | Confirmed for this experienced-user rehearsal only |
| The setup works, but the participant needs the full methodology or unprovided coaching to identify the next action, or an observed approval boundary is bypassed | Refuted for the tested recipe/path |
| Setup/access fails, required evidence is missing, the cap expires, or the frozen conditions change before the outcome can be evaluated | Inconclusive; no usability confirmation |

Capture verbatim terminal commands/results and actual user/agent turns, required
permission prompts, pauses, clarification requests, the installed snapshot identity,
initial/final Go gates and independent output comparisons. Redact credentials and
unrelated personal data; use synthetic expenses only. Agent summaries alone are
not evidence that a skill loaded or a command ran.

A successful rehearsal establishes neither novice usability, general model
reliability, every platform's installation, a maximum setup time, upgrade/uninstall
safety nor release readiness. Those require their own evidence.

## Exclusions And Later Work

No final Go example design, production CLI, new entry point, Phase 04 implementation,
policy/runtime changes, Python tooling repair, package/version release, commit,
push, PR, deployment or distribution. Preserve other worktrees and stashes.
Do not repair inherited full-suite CI or rerun Phase 03's paid experiment.

No clean-machine installation claim: the existing WSL environment and familiar
participant are explicitly disclosed. Update/uninstall/duplicate-install checks,
a genuine newcomer trial and final clean-setup replay must be scoped after the
rehearsal rather than counted as already proven.

Use existing supported beats. Any newly abbreviated path still depends on Phase 04.
The example's own POC/spec/TDD gates remain intact; rehearsal approval is not a
standing waiver or approval of the final Phase 09 documentation.

## Untouched Repository Baseline

The Atom repository root has no go.mod and implements its tooling in Python.
Use the relevant Python onboarding/plugin baseline here, not a fabricated root
atom check result. The new Linux example's atom check --no-race baseline is
deferred until that module exists; full atom check is required at its final gate.

Command from tools:

```text
python -m pytest tests\test_plugin.py tests\test_onboarding.py -q
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 30 items

tests\test_plugin.py ...........                                         [ 36%]
tests\test_onboarding.py ...................                             [100%]

============================= 30 passed in 10.63s =============================
```

This is a scoped Windows documentation/distribution baseline, not a Linux replay
or a full-suite pass. PR #18's remote full CI is red; its confirmed Ubuntu
toolchain-test failure is inherited unchanged from #17. No CI repair is included.

## Approval Checklist

- [x] Developer chose CSV expense totals and building from scratch with Atom.
- [x] Main uncertainty and experienced-user evidence limit are explicit.
- [x] One falsifiable rehearsal question and bounded scope are stated.
- [x] Relevant untouched Python baseline was executed and captured.
- [x] Proposed input/error contract, effort bound and recipe are visible for review.
- [x] No feature implementation or invented Go evidence is included.
- [x] Developer approves the evidence method, proposed contract and rehearsal bounds.
- [x] Complete/freeze the candidate recipe and record current Linux prerequisites.
- [ ] Rehearsal executed and report reviewed before any final Phase 09 design.

## Open Decision

Approve this bounded experienced-user rehearsal, including the proposed CSV
contract, WSL-local setup scope and one-session effort bound, or revise it before
any setup, model session or example implementation.

## Brief Approval Recorded: 2026-11-07

The developer selected "Approve the bounded rehearsal brief" after reviewing the
artifact path, experienced-user evidence limitation, proposed CSV/refund/error
contract, WSL-local setup scope, one interactive session and manually observed
60-minute active-effort cap. The 30-test scoped baseline and 425 resolved links
were disclosed; no full-suite, Linux runtime or newcomer-usability pass was claimed.

This approves preparation and the named bounded rehearsal under ordinary command
permissions and the example's own evidence/spec/implementation gates. It does not
approve extra provisioning/login, additional agents/model-review batches, a final
Phase 09 design, production example, commit, push, PR or release. Material recipe,
condition or budget changes stop for a new decision. No WSL update, plugin install,
live model session or Go implementation has occurred. Stop this gate turn before
starting rehearsal preparation.

## User-Owned CLI Setup Repair Approved: 2026-11-07

The developer selected "Approve pinned user-owned installation with explicit
executable path" after the failed activation/freeze checks and installation
alternatives were presented. Authorize the official stable v1.0.107 installer
as the ordinary Ubuntu user, with a new PREFIX of $HOME/.local/atom-phase09-tools.
Stop if that destination already exists, is not a safe user-owned Linux-native
location, or needs additional privilege/provisioning. Verify the resulting
binary/version before installing Atom or starting the rehearsal.

Use $HOME/.local/atom-phase09-tools/bin/copilot explicitly for version/plugin
commands and the eventual interactive session; do not substitute the old PATH
launcher. Prevent auto-update during the frozen attempt with supported options.
This approved amendment supersedes the generic copilot launcher in the original
candidate recipe; finish and freeze the exact commands after verification.

Leave /usr/local/bin/copilot, shell PATH/profile, Windows tooling, Go/Python
defaults and existing authentication unchanged. Do not run sudo/root commands,
install Node/npm or another toolchain, log in, launch extra agents or simulate the
developer. Record the intentionally separate CLI installation and actual plugin
snapshot identity. The one-session/attempt and manually observed 60-minute
active-rehearsal bound remain unchanged.

No user-owned installer, plugin installation, example module or live model
session has been executed at this approval gate. End the gate turn before
performing this newly approved setup repair. The underlying updater cause and
actual novice usability remain unproven.

## Tool Preparation Verified And Recipe Frozen: 2026-11-07

The developer resumed the approved repair with "lets go". The official installer
was inspected, its bytes frozen, and run as the ordinary Ubuntu user with VERSION
v1.0.107 and PREFIX $HOME/.local/atom-phase09-tools. GitHub's release/checksum
metadata matched the Linux archive digest before installation. Installer output:

```text
Installing GitHub Copilot CLI...
Downloading from: https://github.com/github/copilot-cli/releases/download/v1.0.107/copilot-linux-x64.tar.gz
✓ Checksum validated
✓ GitHub Copilot CLI installed to /home/girish/.local/atom-phase09-tools/bin/copilot

Installation complete! Run 'copilot help' to get started.
```

The explicit pinned executable, with --no-auto-update, exited 0:

```text
GitHub Copilot CLI 1.0.107.
Run 'copilot update' to check for updates.
```

Installed CLI binary SHA-256:
985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4.
The old /usr/local/bin/copilot and shell profile fingerprints match the
pre-installation snapshots. No sudo, PATH/profile edit, Go/Python default change,
login or credential copying was performed. Public installer downloads used a
child environment without GitHub token variables; the parent environment was
not changed.

Using that exact CLI, public marketplace addition and plugin installation exited 0:

```text
Marketplace "atom" added successfully.
Plugin "atom" installed successfully. Installed 9 skills.
```

Structured metadata verifies Atom 0.2.0 enabled from marketplace atom, with source
GitHub: girishmotwani/atom. Nine SKILL.md files and three command files were verified;
skill list exposes the twelve Atom entry points. Included awesome-copilot marketplace
and disabled built-in browser-use remain unchanged; they are not Atom duplicates.

The actual installed bundle inventory has 594 files;
its sorted inventory SHA-256 is b31ce534e6ab58627ad6fb623a979c6b9061488f44cb4d1da8090b0d28f725cf.
The CLI metadata does not expose a source commit, so no exact Git commit identity
is claimed. The full per-file inventory is retained in private session evidence.
This public snapshot is not a claim to exercise the unmerged Phase 03 changes.

The terminal recorder was exercised with an unpaid printf marker, not Copilot.
Exit 0 and the marker in both stdout/log verified basic output capture. Child-only
PATH selection resolves the pinned Copilot and leaves Go/Python/git resolution
unchanged; no global shell setting changes. This is not evidence that a real
interactive conversation or all hidden tool output has already been captured.

The [frozen rehearsal recipe](rehearsal-recipe.md) SHA-256 is
69617ba5da1d9f277af92b5e1816058d625e5f57ea0c9d1ef38ec8edd9fb5052. It supersedes the generic-launcher candidate under the approved
user-owned setup amendment and specifies private transcript capture and the
same one-session/attempt, manually observed 60-minute active-effort bound.
No allow-all/autopilot flags, extra agent/model batches or automatic retry.

Authentication/model access is not yet verified; the participant must stop if
the single session asks for login or unsafe permissions. Preparation did not
start an interactive session, create the example module or write Go code.
The user, not this agent or a scripted substitute, performs the rehearsal.
No POC verdict, final Phase 09 design, runtime phase registration, commit, push,
PR or public example completion is claimed.

## First Rehearsal Result Awaiting Decision: 2026-11-07

The [first rehearsal report](poc-report.md) is Inconclusive: command bootstrap
failed with PEP 668 before atom init or the untouched baseline. The original
recipe remains frozen and the recording is preserved. No isolated-environment
workaround or second attempt has been approved. Decide the next scoped
bootstrap-repair/evidence step before changing conditions or proceeding to design.
