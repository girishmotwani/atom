---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
author: "Copilot with developer gates"
date: "2026-11-10"
status: "accepted-local-guidance-repair"
poc_report: "prerequisite-flow-repair-report.md"
scope: "general onboarding guidance repair, not the final expense example"
---

# General Onboarding Prerequisite Flow Repair Spec

## Purpose And Scope

Make ordinary missing prerequisites a clear user decision, not a sequence of
failed commands. Reuse an existing installation, obtain consent for genuinely
needed provisioning, and stop on real failures. This changes shipped agent
instructions, not deterministic Python/Go behavior, runtime APIs or configuration.
It does not add enforcement or promise agent compliance.

Change only skills\init\SKILL.md, skills\atom\references\bootstrap.md, their two
mirrors under tools\atom\assets, and directly related README onboarding,
prerequisite and install-consent wording. The existing
[bootstrap repair spec](bootstrap-repair-spec.md) remains authoritative for the
unchanged installation safeguards; this spec replaces its intentionally failing
discovery instructions only. Preserve historical ledgers and frozen recipes.

## Evidence Base

The developer accepted the [discovery boundary report](prerequisite-flow-repair-report.md)
and selected exactly "Accept the evidence and draft the repair spec".

Established:

- Windows command resolution found both roles before successful help calls.
- Ubuntu command/package presence checks returned absence without executing
  missing forms. Owned non-symlink ancestor checks and a prefix/package query
  preceded successful reuse of both known-venv module roles.
- The accepted [controlled installation report](bootstrap-repair-report.md) and
  [normal-user boundary report](bootstrap-boundary-report.md) cover bounded Linux
  installation/reuse, exact UTF-8 writes and preserved failing baselines.
- The [stopped rehearsal](prepared-rehearsal-report.md) records confusing discovery,
  different active/pinned client versions, a masked writer refusal and subsequent
  continuation. The writer guard itself refused correctly.

Still assumed, not newly proven:

- Agents will follow clearer instructions and stop/ask at the prescribed points.
- Failure-path handling will be followed; this check encountered no failing helps.
- All clients satisfying the existing minimum expose the same interactive aliases.
  Neither file presence nor a skill listing proves interactive alias acceptance.
- Unsafe/partial environments and other installation/configuration variants are
  comprehensively covered. Retain the safeguards, not a new coverage claim.

Phase 09 still requires a successful supported-user path and useful verified Go
example under its phase-plan entry. This repair is one prerequisite, not phase
completion. No expense rounding or implementation decision is authorized.

## Public Surface And Responsibility

No exported Go/Python type, signature, new subcommand, state field, resolver helper
or dependency is added. Callers remain the existing skills. The main init skill
states the critical order and stop/consent rules; the shared bootstrap owns the
full resolution procedure. README describes expectations, not an alternative
installer. Packaged skill/reference text must be byte-identical to canonical text.

Retain exact verified command forms per role for the current environment/session,
without persisting new state or importing/scanning external implementation. A
Python presence query may check find_spec('atom') is not None, but must not print
origin paths, inspect internals or mistake package presence for a working role.
The two roles still require successful --help checks before use.

## Behavior

1. Confirm go.mod as before. Before onboarding, use available current-session
   client identity; never substitute the version of a different executable on
   PATH. Preserve the existing documented Copilot CLI minimum (1.0.89). An unknown,
   conflicting or unsupported active identity gets one focused clarification or
   switch/update consent question and a stop, never an automatic update. Previously
   established identity is reusable while its session/environment is unchanged.
2. Check Go executable availability without running a known-missing command. If
   absent, explain that Go is required and ask the developer to supply/install it
   before init. Do not provision Go or duplicate baseline/build/toolchain checks;
   atom init retains its existing real verification and failure record.
3. Reuse command forms already verified for this environment/session. Otherwise
   resolve both entry points without intentionally invoking missing commands.
   Availability uses normal platform command resolution or the demonstrated
   shutil.which primitive when Python is already available; discovery does not
   require finding Python when both entry points already work.
4. Help-check each found entry point. Keep successful roles and stop discovery
   when both work. A found command's nonzero result stops immediately with its
   actual diagnostic, not another installation or fallback to hide it.
5. For missing roles only, resolve an existing supported interpreter before
   executing it: python3 then python on Linux as needed; retain the existing
   Windows python fallback. Query package presence before module help. An explicit
   absent result is normal discovery data, not a failed installation. Unexpected
   query/import errors are real errors and stop. Missing/unsupported Python gets
   clear prerequisite guidance and a developer decision, not provisioning.
6. If Atom is present, help-check only missing roles through that interpreter;
   retain successful mixed entry-point/module forms. Partial or broken roles stop
   with actual output; no package overwrite, reinstall or arbitrary env search.
7. Only when no role works and selected-Python package absence is established,
   check the one known Linux venv. Verify user ownership/non-symlink ancestors
   within HOME before execution; reuse both healthy forms. Preserve partial,
   conflicting or unsafe destinations and stop with the named problem.
8. Only explicit absence and an absent safe destination permit an installation
   proposal. Explain which tools are missing and the existing user-owned Linux
   venv/source plan, ask one explicit consent question, and wait. Preserve the
   existing exclusively-created destination, non-secret scheme checks, normal
   pip/Git configuration, one install, no unchanged retry, and post-install role
   verification. Missing Git/venv/ensurepip receives prerequisite guidance; no
   system-tool provisioning, new platform recipe or silent repair is introduced.
9. Keep Windows setup-path as one explicit opt-in for a working package with
   hidden entry points. Printed absolute commands are authoritative for that
   current parent process. Do not re-probe; declined opt-in keeps module forms.
10. Record the two working forms once and use them throughout subsequent beats.
    Do not repeat discovery merely because the next skill uses the literal atom
    or atom-write-artifact name. Changed context or an actual failure is not proof
    the old forms remain valid; disclose it and stop for resolution when needed.
11. Preserve full relevant stdout/stderr and the actual originating status. No
    head-ended help/writer pipelines or success-shaped fallback may hide a failure.
    Verify writer support with --help; do not test it against an invalid target.
    A refusal/nonzero result stops the workflow, even if a wrapper reports zero.
    No alternate path, generic editor or subsequent write bypasses that stop.
12. Run atom init only after prerequisites and both roles work, under the target
    module's normal command approval. Installation/bootstrap approval does not
    approve init or artifact writes. Preserve no-op/force behavior, real empty-
    module baseline failures and the five named-file receipt reads. Do not add
    placeholder Go code, repeated Go checks or success-path recursive scans.
13. Report the verified forms and honest baseline/no-op result concisely. Use the
    appropriate discovery/existing-workflow handoff, not an unverified start alias.
    If alias registration is unknown/rejected, state that uncertainty rather than
    guessing another alias or changing/reinstalling the plugin. Explicitly naming
    the appropriate available skill in ordinary language is not proof a slash
    alias works and must not silently substitute a different skill.
14. README puts existing supported minima and plugin-versus-Python distinction
    near the front, describes missing/hidden/broken choices and separate consent,
    and avoids automatic-install or fixed-approval-count promises. Keep historical
    counts as historical evidence with their original ledger link. Correct the
    directly coupled manual-install introductory promise, without redesigning
    manual platform recipes. Both canonical/packaged pairs remain byte-identical.

## Error Handling And Concurrency

No new runtime error strings or sentinels. Missing capabilities get a clear
prerequisite explanation plus one user decision. Found-but-failing commands,
uncertain ownership/prefix/configuration, collisions and writer refusals retain
actual safe diagnostics and stop. Never reinterpret an exception as package
absence, disclose secrets or broaden executable approvals to resolve permission
friction. Command/writer approvals remain module-local and narrowly scoped.

Resolution is sequential per environment; stop at the first real failure. No new
threads, processes running persistently, locks or migrations are added. Concurrent
installers remain unsupported; exclusive creation is not a new lock service.
Read-only reuse assumes the existing installation is stable. Existing runtime
init/writer concurrency contracts remain unchanged.

## Validation Mapping

| Contract | Validation after approval |
|---|---|
| Active identity, Go prerequisite, absent/hidden/broken routing, stop/consent, handoff | Semantic walkthrough against numbered behavior and accepted receipts; not a claim of agent compliance |
| Existing Linux safety, Windows fallback/setup-path and init receipts | Preserve current procedure; existing onboarding/pathsetup/artifact tests plus source review |
| Canonical/package text and manifest contracts | Existing parity and plugin tests; explicit byte comparison of both changed pairs |
| README minima/consent/history, link integrity and whitespace | Factual review, existing README path test, link checker, git diff --check |

From tools, run the existing focused selector:

```powershell
python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

At root run python tools\check_links.py and git diff --check. Preserve literals
required by current contracts; do not weaken tests or add prose-presence tests to
pretend instruction adherence was tested. Since there is no production runtime
change, use this documentation/packaging validation adaptation rather than a
fabricated Go/Python production RED/GREEN loop. No root atom check is appropriate.
Existing test/environment failures are surfaced before broadening work.

## Trade-offs And Extension Points

Availability-first checks preserve healthy/editable installs and avoid needless
failure output; direct missing-command execution is rejected for the observed UX.
Guidance consolidation is chosen over a new bootstrap engine, monitor, extra
package manager or blanket reinstall. Active-session evidence is chosen over an
unrelated executable version. Existing minima are support requirements, not a
new blanket compatibility result. A fresh live agent experiment is deferred, not
replaced by text tests: it requires its own frozen sources/client/model and gates.
Future platform or provisioning support extends the shared reference only after
new bounded evidence and approval; no abstraction is needed now.

## Approval Boundary

Approval authorizes only this five-document guidance repair and its existing
local documentation/packaging checks. Findings/decisions and repair validation
artifacts accompany the change. It does not authorize installer execution,
plugin/package refresh, profiles/PATH/default changes, target-trial mutations,
model spend, new live trials, runtime code, final Phase 09 implementation,
commit, push, publication or merge. Source edits do not update installed plugins
or existing local bundles. A material design or evidence change re-gates.

## Spec Approval Recorded

The developer selected exactly: "Approve the spec and implement the guidance repair".
Approval is limited to the five-document change and stated local validation.

## Implementation Reconciliation

Implemented the five approved shipped documents with no runtime/API/schema change
or material design deviation. Local validation is in prerequisite-flow-repair-validation.md.
Source/package parity is verified; installed delivery and actual agent adherence
remain outside this completion claim. The expense example is not implemented.

## Local Repair Acceptance Recorded

The developer selected exactly: "Accept the local repair; keep delivery and rehearsal gated".
No publication, installed-plugin refresh, model review or new live trial is authorized.
## Reviewed README Clarification Reconciled

Following the independent post-fix review, the developer explicitly selected
"Fix README wording and record the Windows issue for separate repair". Corrected
four README passages under unchanged behavior 14: ask developers to supply system
prerequisites, limit guided Atom installation to the consent-gated Linux recipe
with confirmed absence/safe absent destination, and require an agreed isolated
setup elsewhere. No new policy/runtime/API or material spec change. The existing
README contract and local link/whitespace/hash checks pass, with full receipts in
prerequisite-flow-repair-post-fix-review.md; local acceptance is pending.

Behavior 9 and its existing Windows procedure remain unchanged, with the printed-
command verification gap explicitly deferred for a separately scoped repair.
This reconciliation does not silently fix it or claim its wrappers were verified.
No independent re-review of the new README hash, delivery/refresh or rehearsal is
included in the local correction approval.
## Reviewed README Correction Accepted

The developer selected "Accept the correction; keep delivery, refresh and
rehearsal gated". The behavior 14 factual correction is locally accepted with
Windows behavior 9 unchanged and its handoff verification gap explicitly deferred.
The post-fix report retains actual validation, source hashes and independent-
review limits. No later delivery, refresh, model spend or rehearsal is authorized.
