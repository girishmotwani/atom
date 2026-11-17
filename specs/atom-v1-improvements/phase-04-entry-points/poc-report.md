---
project: "atom-v1-improvements"
phase: "phase-04-entry-points"
date: "2026-11-06"
verdict: "Confirmed"
status: "approved"
---

# POC Report - New-Repository Setup Mechanics

## The Question

Can the existing Go module-initialization and Atom onboarding commands compose
into a locally usable setup from a repository without `go.mod`, preserving
pre-existing files and reporting empty-module validation honestly?

## Verdict

**Confirmed, mechanically only, on this Windows environment.** All four approved
fixtures met their declared observations in one run. This does not establish
real agent approval/refusal behavior, cross-platform support, a general template
system or completion of Phase 04.

## Evidence

Base: `50622ab`, including merged Phase 3. Go: `go1.27.0 windows/amd64`.
Python: `3.13.14`. Atom: the local editable CLI.
Child-only `GOTOOLCHAIN=local`, `GOPROXY=off`, `GOSUMDB=off`.
The child PATH contained Go, the Python launcher directory and Windows System32;
no optional analyzers were installed or run. Race detection was explicitly skipped
by the existing onboarding-baseline behavior.

Command:

```text
python -m atom.cli poc run atom-v1-new-repo-setup --timeout 600 --no-colour
```

The [complete verbatim transcript](../../../poc/atom-v1-new-repo-setup/execution.txt)
contains all nine subprocess commands, separate stdout/stderr, exit codes,
the complete baseline JSON for each initialized module, created-file lists,
preservation outcomes, cleanup and verdict.
The [disposable Go source](../../../poc/atom-v1-new-repo-setup/main.go) is archived
with its isolated module.

Verbatim outer gate output:

```text
atom poc run atom-v1-new-repo-setup  (command spike)

  PASS  vet     ok
  PASS  build   ok
  PASS  execute ok
```

Verbatim selected stdout events:

```json
{"application_verified":false,"event":"empty-module-limit","passed":false,"reason":"fixture contains no application or tests"}
{"case":"declined","event":"case-result","scope":"fixed harness decision only, not a real agent approval/refusal test","unchanged":true}
{"event":"cleanup","path":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-v1-new-repo-setup-1143531370","removed":true}
{"commands":9,"event":"verdict","real_agent_consent_tested":false,"verdict":"Confirmed"}
```

Verbatim final outer verdict:

```text
  Verdict: CONFIRMED  (exit 0) -- the question was answered yes
```

| Fixture | Observation | Interpretation |
|---|---|---|
| Module only | `go mod init` and onboarding exited 0; baseline `passed` was false, with vet/test failures because no packages exist; README was preserved | Module setup succeeded, but there is no verified application. Exit 0 from onboarding is not a clean-baseline guarantee. |
| Approved tiny CLI and test | Module creation and onboarding exited 0; build/vet/format/test passed; README was preserved | Existing commands can compose into the proposed minimal CLI setup without a new runtime setup API. This is feasibility evidence, not a final interface decision. |
| Existing module and repeat | Existing module/source/test/README bytes survived; baseline passed; matching repeat left the complete file-content snapshot unchanged | Current onboarding can be reused without recreating the module or resetting matching state. Timestamps were not measured. |
| Declined | Harness performed no target commands and file snapshots matched; neither `go.mod` nor `.atom` was created | The scripted no-action branch works. No real agent was asked to wait or honor rejection. |

No commands failed or timed out, no retries were used, and the exact temporary
fixture root was removed. Source files were formatted in memory before onboarding
so fixture formatting did not create an unrelated baseline failure.

## Findings That Affect The Design

1. **Setup and application verification are distinct outcomes.** Creating only a
   module gives a failing no-package baseline here. Do not silently add an
   application just to obtain a green result. Recommend source/test scaffolding
   only when appropriate to the user's goal and explicitly approved.
2. **Onboarding produces additional files.** Besides Atom's bundle/config/state,
   instructions and ignore block, `go build ./...` produced a CLI executable
   in each CLI fixture. A setup recommendation must disclose baseline execution
   and expected generated build outputs, not promise that only hand-authored
   scaffold files will appear.
3. **Onboarding prints full-pipeline recommendations.** Its current closing
   message recommends a POC even when only setup was requested. The bounded entry
   path must not treat that printed suggestion as authorization to continue.
4. **Existing commands are sufficient for this mechanical trial.** No new
   runtime command is justified solely by the missing `go.mod` case.

## Explicitly Not Covered

- Actual agent recommendation, waiting, approval interpretation, refusal or stopping.
- Choosing a real user's module path or deciding library versus CLI scaffolding.
- Conflicting existing Atom state, malformed modules, symlinks, permission errors,
  concurrent setup, installation failures or recovery after partial setup.
- Timeout process-tree cleanup; there was no timeout and this harness does not
  claim to safely clean up a timed-out descendant tree.
- Git metadata, remote inference, commits, pushes, publication or model calls.
  Targets were disposable directories rather than newly initialized Git repositories.
- Linux/POSIX behavior, race evidence, coverage thresholds, optional analyzer
  results, real application complexity or performance.
- Standalone review and diagnosis, packaged live interaction or full Phase 04 routing.

## Approval And Next Step

The developer approved this report on 2026-11-06 and requested continuation.
Draft the bounded new-repository setup design using existing commands and
Phase 3's evidence-choice/approval policy.
Keep real developer-interaction validation as a separate explicit obligation
before claiming the entry path works end to end. The other Phase 04 entry paths
remain separate work; this report does not prove or approve them.
