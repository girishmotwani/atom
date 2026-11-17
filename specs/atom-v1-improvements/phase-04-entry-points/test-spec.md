# Test Spec - New-Repository Setup Guidance

Scope: approved `design-spec.md`, new-repository setup slice only.
No production runtime API is changing. Go error-type, typed-nil, cancellation,
concurrency and coverage cases are not applicable to instruction text.

## Behavior Mapping

| Design behavior | Required check | What it cannot establish |
|---|---|---|
| 1. Enter without a module | Inspect init/start instructions for a missing-module setup recommendation; preserve the Python-repository boundary | Actual agent routing |
| 2. Inspect before asking | Semantic review of local evidence, target inspection and no remote/Git initialization | Completeness of an agent's inspection |
| 3. Resolve choices | Review explicit module identity, application kind and Go-version approval choices | Correct naming for every real project |
| 4. Concrete proposal | Review target/files/commands/onboarding effects/build-output disclosure | User comprehension without interaction |
| 5. Wait for approval | Review ordering and prerequisite/bootstrap permission boundaries | Actual waiting |
| 6. Refusal/revision | Review no-change refusal and revised-proposal reapproval | Actual refusal handling |
| 7. Bounded scaffold | Compare module-only/minimal CLI scope against the approved POC | Arbitrary application templates |
| 8. Recheck/preserve | Review conflict/no-force handling; run existing onboarding/repeat tests | Atomicity or concurrent setup safety |
| 9. Existing commands | Check examples against current CLI, with missing module creation before init | Untested platform/toolchain combinations |
| 10. Bounded errors | Review sequential execution, explicit partial results and no blind cleanup | Timeout process-tree guarantees |
| 11. No silent installs | Review local/offline child settings and separately approved bootstrap/PATH changes | Universal network isolation of existing project recipes |
| 12. Setup versus validation | Compare wording with actual module-only and CLI POC results | Real application quality |
| 13. Repeat semantics | Existing onboarding/repeat tests; preserve no-refresh/no-force guidance | Bundle upgrading on a repeat |
| 14. Stop at outcome | Review init/start/build integration and full-feature evidence gate | Live end-to-end stopping |

## Distribution And Existing Behavior Checks

- Add a focused onboarding integration check that initializes a fixture module,
  installs the new setup reference, and compares installed/package bytes with
  canonical bytes. This checks real bundle inclusion, not sentence matching.
  Its baseline gate follows the test file's existing deterministic fixture.
- Run existing plugin command-surface and onboarding/repeat/scaffold/CLI-state
  tests together. No command name, API, exit status or repeat semantics changes.
- Run the existing Markdown relative-link checker.
- Compare all changed canonical/package pairs byte-for-byte.
- Review changed guidance against every numbered design behavior and confirm
  that the shared reference never dispatches back to its caller.

A missing-file distribution failure and its subsequent passing check may be
recorded, but do not call this a Go production RED/GREEN loop or evidence of
human approval enforcement.

## Remaining Interaction Gate

Before claiming end-to-end usability, separately scope developer-observed
approval, refusal and changed-proposal cases. Capture actual tools/file changes
and the point at which the agent waits/stops, not merely its account of events.
No paid model batch or new setup target is authorized by this test spec.

## Evidence Reuse

The approved local POC establishes missing-module command composition and honest
baseline reporting on Windows. Reuse it for those unchanged mechanics; do not
repeat it just to generate another green result. Any new runtime behavior,
template or platform claim needs its own applicable evidence decision.


## Approved Review-Correction Mapping - 2026-11-13

- Behaviors 2/4/5/11: semantic ordering check that onboarding-inclusive requests
  establish both existing command roles with --help during inspection, before a
  final setup proposal or module/scaffold writes. Missing roles stop without files;
  installation/PATH still requires separate consent. Go-only setup bypasses Atom
  prerequisites rather than triggering an unsolicited smaller fallback.
- Behaviors 9/12/14: inspect every init step, report item and completion item so
  onboarding-only execution, local-file verification, baseline claims and model
  guidance are conditional. With no onboarding approval, only agreed Go setup and
  checks occur; absent Atom files are not treated as failure or permission to init.
- Extend the existing canonical/package/installed byte-equality parameterization
  to the corrected init skill, alongside the setup reference; reuse real fixture
  onboarding with its deterministic baseline collaborator. Add no phrase-matching
  test and claim it proves agent ordering or actual refusal.
- Run focused onboarding/plugin/repeat checks, current relative-link checker and
  canonical/package byte checks. This is documentation/distribution validation;
  no production runtime test or Go atom check is invented.

Existing installed-preview and live records describe the pre-correction treatment.
Do not overwrite those hashes/reports or claim the new missing-tool ordering and
Go-only path were live-tested. Current source/packaged assets may be newer than the
unchanged installed preview until a separately approved installation/trial.


## Publication Context - 2026-11-17

The preceding sections preserve the dated implementation/approval history, including
then-pending gates. The setup corrections and bounded installed observations were
subsequently accepted. See [current evidence and limits](setup-evidence.md),
[review provenance](review.md), [shipping verification](verification.md) and
[publication decisions](decisions.md). References to the original setup-review
archive name local historical records, not additional files published in this PR.
The combined instructions retain newer upstream bootstrap guidance; the historical
live observations do not cover those combined bytes.
