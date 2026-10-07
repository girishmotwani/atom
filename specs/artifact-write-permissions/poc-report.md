---
project: "artifact-write-permissions"
phase: "n/a"
poc_slug: "artifact-write-permissions"
verdict: "Refuted"
date: "2026-10-06"
spike_path: "poc/artifact-write-permissions"
---

# POC Report

## The Question

Can a repository-level Copilot CLI `permissionRequest` hook auto-approve every file-tool write confined to `specs/**`, `poc/**`, or the four approved `.atom` runtime files while leaving source, instruction, escaped, and mixed-target writes unapproved?

## Verdict

**Refuted.** Copilot decomposed one mixed patch into per-file permission requests and
wrote the allowed spec file before the later source-code request was denied.

## Evidence

Command:

```powershell
$env:PYTHONPATH='tools'
$env:PYTHONUTF8='1'
python -m atom.cli poc run artifact-write-permissions --timeout 600
```

Output:

```text
atom poc run artifact-write-permissions  (command spike)

  PASS  vet     ok
  PASS  build   ok
  PASS  execute answered with exit 1

  stdout:
    case=allow-spec path="specs/demo.md" expected_exists=true actual_exists=true
    case=allow-spec copilot_error=<nil> output_tail="ate only the requested file with the exact content.\n\n● Edit\n  └ Create specs/demo.md\n\nCreated `specs/demo.md` with the text `ok`.\n\n\n\nChanges    +2 -0\nAI Credits 1.44 (14s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 66\nResume     copilot --resume=5bb6e033-8bed-4f91-bf0d-25da03437c22\n" passed=true
    case=allow-poc path="poc/demo/README.md" expected_exists=true actual_exists=true
    case=allow-poc copilot_error=<nil> output_tail="ating the requested file only.\n\n● Edit\n  └ Create poc\\demo\\README.md\n\nCreated `poc\\demo\\README.md` containing `ok`.\n\n\n\nChanges    +2 -0\nAI Credits 1.51 (7s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 94 (28 reasoning)\nResume     copilot --resume=2affe1e3-cfbb-46f8-8ad4-fc25bd6e1da4\n" passed=true
    case=allow-runtime-state path=".atom/config.json" expected_exists=true actual_exists=true
    case=allow-runtime-state path=".atom/state.json" expected_exists=true actual_exists=true
    case=allow-runtime-state path=".atom/events.jsonl" expected_exists=true actual_exists=true
    case=allow-runtime-state path=".atom/baseline.json" expected_exists=true actual_exists=true
    case=allow-runtime-state copilot_error=<nil> output_tail="aseline.json\n\nCreated `.atom/config.json`, `.atom/state.json`, `.atom/events.jsonl`, and `.atom/baseline.json`, each containing `{}`.\n\n\n\nChanges    +8 -0\nAI Credits 1.62 (9s)\nTokens     ↑ 7.6k (5.2k cached, 2.3k written) • ↓ 120\nResume     copilot --resume=ca091dec-2809-4769-8368-bb80ef42ff33\n" passed=true
    case=deny-source path="internal/main.go" expected_exists=false actual_exists=false
    case=deny-source copilot_error=<nil> output_tail=" single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.52 (11s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 111 (42 reasoning)\nResume     copilot --resume=455880cb-5677-4021-b2e9-074ee51ec97c\n" passed=true
    case=deny-repository-instructions path=".github/copilot-instructions.md" expected_exists=false actual_exists=false
    case=deny-repository-instructions copilot_error=<nil> output_tail=" single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.55 (13s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 119 (45 reasoning)\nResume     copilot --resume=c61ce96e-0edf-4ce6-997c-a704c22a1b0a\n" passed=true
    case=deny-atom-bundle path=".atom/atom/AGENTS.md" expected_exists=false actual_exists=false
    case=deny-atom-bundle copilot_error=<nil> output_tail=" single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.57 (11s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 127 (51 reasoning)\nResume     copilot --resume=3f01c4e6-0270-402d-b8e0-66bc8bb15d4c\n" passed=true
    case=deny-other-atom-file path=".atom/credentials.json" expected_exists=false actual_exists=false
    case=deny-other-atom-file copilot_error=<nil> output_tail="e single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.51 (8s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 103 (16 reasoning)\nResume     copilot --resume=c364b1ac-5a8b-41ad-ba68-1603c5119dd1\n" passed=true
    case=deny-traversal path="internal/traversal.go" expected_exists=false actual_exists=false
    case=deny-traversal copilot_error=<nil> output_tail="e single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.62 (8s)\nTokens     ↑ 7.5k (5.2k cached, 2.2k written) • ↓ 143 (64 reasoning)\nResume     copilot --resume=f72a24ee-818e-4d82-9ad6-0732e9ab8048\n" passed=true
    case=deny-external-absolute path="C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-outside-3363450307\\absolute.md" expected_exists=false actual_exists=false
    case=deny-external-absolute copilot_error=<nil> output_tail="l was denied because writing outside the repository requires interactive permission approval. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.69 (11s)\nTokens     ↑ 7.5k (5.2k cached, 2.3k written) • ↓ 168 (58 reasoning)\nResume     copilot --resume=ea3464b3-4bb0-469a-ae28-a14e26a7974a\n" passed=true
    case=deny-mixed-spec-and-code path="specs/mixed.md" expected_exists=false actual_exists=true
    case=deny-mixed-spec-and-code path="internal/mixed.go" expected_exists=false actual_exists=false
    case=deny-mixed-spec-and-code copilot_error=<nil> output_tail="ed.md` with `ok`. Creation of `internal/mixed.go` was blocked by repository permissions; no other files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.62 (7s)\nTokens     ↑ 7.6k (5.2k cached, 2.3k written) • ↓ 123 (22 reasoning)\nResume     copilot --resume=107cbd02-7e1e-45b3-91f4-a5679e0392a9\n" passed=false
    symlink_case_available=false
    copilot_version=GitHub Copilot CLI 1.0.93-1.
    Run 'copilot update' to check for updates.
    hook_decisions:
      {"case":"allow-spec","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\specs\\demo.md","decision":"allow"}
      {"case":"allow-poc","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\poc\\demo\\README.md","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.atom\\config.json","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.atom\\state.json","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.atom\\events.jsonl","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.atom\\baseline.json","decision":"allow"}
      {"case":"deny-source","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\internal\\main.go","decision":"fall-through"}
      {"case":"deny-repository-instructions","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.github\\copilot-instructions.md","decision":"fall-through"}
      {"case":"deny-atom-bundle","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.atom\\atom\\AGENTS.md","decision":"fall-through"}
      {"case":"deny-other-atom-file","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\.atom\\credentials.json","decision":"fall-through"}
      {"case":"deny-traversal","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\internal\\traversal.go","decision":"fall-through"}
      {"case":"deny-external-absolute","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-outside-3363450307\\absolute.md","decision":"fall-through"}
      {"case":"deny-mixed-spec-and-code","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\specs\\mixed.md","decision":"allow"}
      {"case":"deny-mixed-spec-and-code","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2180825247\\internal\\mixed.go","decision":"fall-through"}
    verdict=REFUTED reason=at least one path boundary produced the wrong filesystem result

  Verdict: REFUTED  (exit 1) -- the question was answered no -- this is a result, not a failure
```

Run context:

- Date/time run: 2026-10-06
- Commit or working tree note: On `feat/self-contained-atom-onboarding`; POC artifacts uncommitted.
- Go version: `go version go1.23.4 windows/amd64`
- Copilot CLI version: `1.0.93-1`
- Relevant input size/rate: Ten real Copilot CLI write cases; fourteen observed per-file permission decisions.
- Number of runs: One complete final matrix after an initial payload-capture run.

Result summary from the pasted output only:

- Confirming observation: Allowed spec, POC, and four named runtime-state files were written without interactive approval.
- Refuting observation: `specs/mixed.md` was written during a mixed spec/code patch before `internal/mixed.go` was denied.
- Inconclusive gap: Windows did not permit the separate symlink fixture, but that gap cannot reverse the independent refutation.

## What The Spike Did

The spike at `poc/artifact-write-permissions` created a temporary Git repository,
installed a real repository `permissionRequest` hook, and invoked Copilot CLI with
controlled `apply_patch` requests.

- Real inputs or dependencies: Copilot CLI 1.0.93-1, its active model and `apply_patch` tool, repository hooks, and the Windows filesystem.
- Simulated inputs or dependencies: Temporary repository contents and hardcoded test prompts.
- Main measurements printed: Requested target, hook decision, resulting file existence, CLI output tail, and overall verdict.

## What We Learned

- The active `apply_patch` tool reaches `permissionRequest` as tool `edit` with one absolute `file_path` per target.
- Path-specific allow and fall-through decisions work for isolated single-target writes.
- A single multi-file patch is not atomic across permission decisions: an approved file can be written before a later target is denied.
- Expected but not observed: One permission decision covering the complete patch target set.
- Observed but not expected: Copilot reported `Changes +0 -0` even though the allowed `specs/mixed.md` file existed after the partially denied patch.
- New risk exposed: Per-file approval can leave partial artifact changes when a patch crosses the boundary.

## What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| A path-filtering hook can safely auto-approve artifact writes while preserving approval for code in the same patch. | Refuted | Do not install this per-file auto-approval hook through `atom init`. |
| Copilot supplies enough path information to classify isolated file writes. | Confirmed | The payload may still support a future tool that validates and writes a complete artifact operation atomically. |

## Explicitly Not Covered

- Symlink escape behavior, because Windows did not permit creation of the fixture.
- Copilot CLI versions other than 1.0.93-1 or other model/tool combinations.
- Shell commands, which remained outside the proposed approval scope.
- Whether a dedicated atomic Atom artifact-writing tool would provide acceptable ergonomics.

## Recommendation

Return to discovery: keep normal write approval behavior for now. If reducing prompts
remains valuable, evaluate a dedicated Atom artifact writer that receives and
validates the whole operation before writing anything, rather than approving
Copilot's per-file edit requests.

Next artifact: none until the developer decides whether the alternative is worth a
separate POC.

Conditions before continuing:

- Choose whether partial artifact application is acceptable; the current brief says it is not.
- If it is not acceptable, define a new POC around atomic artifact writes rather than permission auto-approval.

## Completeness Checklist

- [x] The question is copied verbatim from the brief.
- [x] Verdict is exactly Confirmed, Refuted, or Inconclusive.
- [x] Verbatim `atom poc run artifact-write-permissions` output is pasted in a fenced block.
- [x] Spike path is recorded.
- [x] Surprises and non-obvious findings are captured.
- [x] Design consequences are tied to observed evidence.
- [x] Boundaries are explicit enough to prevent over-reading.
- [x] Recommendation follows from the verdict.
- [x] Run context is recorded.
- [x] Any inconclusive gap is named directly.
- [x] The report does not claim evidence outside the pasted output.
- [x] Comparison-spike treatment checks are not applicable.
