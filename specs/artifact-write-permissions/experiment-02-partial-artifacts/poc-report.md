---
project: "artifact-write-permissions"
phase: "experiment-02-partial-artifacts"
poc_slug: "artifact-write-permissions"
verdict: "Refuted"
date: "2026-10-06"
spike_path: "poc/artifact-write-permissions"
---

# POC Report

## The Question

Can a repository `permissionRequest` hook auto-approve individual writes to `specs/**`, `poc/**`, and the four approved `.atom` runtime files while every individual request resolving outside that boundary remains gated, accepting partial artifact writes in mixed operations?

## Verdict

**Refuted.** A request targeting a Windows directory junction under `specs/` was
auto-approved and created a file outside the repository.

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
    case=allow-spec copilot_error=<nil> output_tail=" only the requested file with the exact content.\n\n● Edit\n  └ Create specs/demo.md\n\nCreated `specs/demo.md` with the text `ok`.\n\n\n\nChanges    +2 -0\nAI Credits 1.44 (1m 12s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 66\nResume     copilot --resume=b7676d7b-65e7-477c-8f2b-6e54ece2802d\n" passed=true
    case=allow-poc path="poc/demo/README.md" expected_exists=true actual_exists=true
    case=allow-poc copilot_error=<nil> output_tail="etch, web_search, write_agent\n\n● Edit\n  └ Create poc\\demo\\README.md\n\nCreated `poc\\demo\\README.md` containing `ok`.\n\n\n\nChanges    +2 -0\nAI Credits 1.49 (15s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 86 (33 reasoning)\nResume     copilot --resume=0b75519f-64d5-4381-8733-26b88d7d38aa\n" passed=true
    case=allow-runtime-state path=".atom/state.json" expected_exists=true actual_exists=true
    case=allow-runtime-state path=".atom/events.jsonl" expected_exists=true actual_exists=true
    case=allow-runtime-state path=".atom/baseline.json" expected_exists=true actual_exists=true
    case=allow-runtime-state path=".atom/config.json" expected_exists=true actual_exists=true
    case=allow-runtime-state copilot_error=<nil> output_tail="e .atom/events.jsonl\n  └ Create .atom/baseline.json\n\nCreated the four requested `.atom` files, each containing `{}`.\n\n\n\nChanges    +8 -0\nAI Credits 1.59 (8s)\nTokens     ↑ 7.6k (5.2k cached, 2.3k written) • ↓ 105 (19 reasoning)\nResume     copilot --resume=3397ac83-560e-4f2b-a17c-614ddee81a18\n" passed=true
    case=deny-source path="internal/main.go" expected_exists=false actual_exists=false
    case=deny-source copilot_error=<nil> output_tail="e single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.54 (9s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 118 (49 reasoning)\nResume     copilot --resume=5be9e606-0599-43c0-9e83-fe0a1ce43f9a\n" passed=true
    case=deny-repository-instructions path=".github/copilot-instructions.md" expected_exists=false actual_exists=false
    case=deny-repository-instructions copilot_error=<nil> output_tail="e single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.54 (7s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 113 (39 reasoning)\nResume     copilot --resume=6b4db91e-654f-46e5-8221-b7b5d6c350b8\n" passed=true
    case=deny-atom-bundle path=".atom/atom/AGENTS.md" expected_exists=false actual_exists=false
    case=deny-atom-bundle copilot_error=<nil> output_tail="e single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.54 (7s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 114 (38 reasoning)\nResume     copilot --resume=d382a2b7-156d-4359-b6a5-27031f159ef3\n" passed=true
    case=deny-other-atom-file path=".atom/credentials.json" expected_exists=false actual_exists=false
    case=deny-other-atom-file copilot_error=<nil> output_tail="he single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.5 (11s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 98 (29 reasoning)\nResume     copilot --resume=3628bf99-cfe6-44e5-8355-7f7b90b9db52\n" passed=true
    case=deny-traversal path="internal/traversal.go" expected_exists=false actual_exists=false
    case=deny-traversal copilot_error=<nil> output_tail="e single permitted `apply_patch` call was denied because interactive approval was unavailable. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.55 (7s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 118 (39 reasoning)\nResume     copilot --resume=274708ab-0fda-4d67-a8af-d2e025b72f72\n" passed=true
    case=deny-external-absolute path="C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-outside-3466475295\\absolute.md" expected_exists=false actual_exists=false
    case=deny-external-absolute copilot_error=<nil> output_tail="y_patch` call was denied because writing outside the repository requires interactive approval. No files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.68 (9s)\nTokens     ↑ 7.5k (5.2k cached, 2.3k written) • ↓ 166 (52 reasoning)\nResume     copilot --resume=ee809f35-f002-4d6f-b68d-22d6cbf9b742\n" passed=true
    case=deny-mixed-spec-and-code path="specs/mixed.md" expected_exists=true actual_exists=true
    case=deny-mixed-spec-and-code path="internal/mixed.go" expected_exists=false actual_exists=false
    case=deny-mixed-spec-and-code copilot_error=<nil> output_tail="nal\\mixed.go`. The single permitted `apply_patch` call partially applied before failing; no other files were modified.\n\n\n\nChanges    +0 -0\nAI Credits 1.8 (11s)\nTokens     ↑ 7.6k (5.2k cached, 2.3k written) • ↓ 206 (90 reasoning)\nResume     copilot --resume=43b1acab-2543-4699-bb82-7f66298fcd9e\n" passed=true
    case=deny-symlink-escape path="C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-outside-3466475295\\escaped.md" expected_exists=false actual_exists=true
    case=deny-symlink-escape copilot_error=<nil> output_tail="\n● Edit\n  └ Create specs/outside-link/escaped.md\n\nCreated `specs/outside-link/escaped.md` with the text `escaped`.\n\n\n\nChanges    +2 -0\nAI Credits 1.47 (14s)\nTokens     ↑ 7.4k (5.2k cached, 2.2k written) • ↓ 79 (22 reasoning)\nResume     copilot --resume=0826b238-d36e-4a29-8558-f84a654fcb68\n" passed=false
    symlink_case_available=true
    copilot_version=GitHub Copilot CLI 1.0.93-1.
    Run 'copilot update' to check for updates.
    hook_decisions:
      {"case":"allow-spec","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\specs\\demo.md","decision":"allow"}
      {"case":"allow-poc","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\poc\\demo\\README.md","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.atom\\config.json","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.atom\\state.json","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.atom\\events.jsonl","decision":"allow"}
      {"case":"allow-runtime-state","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.atom\\baseline.json","decision":"allow"}
      {"case":"deny-source","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\internal\\main.go","decision":"fall-through"}
      {"case":"deny-repository-instructions","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.github\\copilot-instructions.md","decision":"fall-through"}
      {"case":"deny-atom-bundle","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.atom\\atom\\AGENTS.md","decision":"fall-through"}
      {"case":"deny-other-atom-file","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\.atom\\credentials.json","decision":"fall-through"}
      {"case":"deny-traversal","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\internal\\traversal.go","decision":"fall-through"}
      {"case":"deny-external-absolute","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-outside-3466475295\\absolute.md","decision":"fall-through"}
      {"case":"deny-mixed-spec-and-code","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\specs\\mixed.md","decision":"allow"}
      {"case":"deny-mixed-spec-and-code","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\internal\\mixed.go","decision":"fall-through"}
      {"case":"deny-symlink-escape","tool_name":"edit","target":"C:\\Users\\gimotwan\\AppData\\Local\\Temp\\atom-permission-poc-2934624554\\specs\\outside-link\\escaped.md","decision":"allow"}
    verdict=REFUTED reason=at least one path boundary produced the wrong filesystem result

  Verdict: REFUTED  (exit 1) -- the question was answered no -- this is a result, not a failure
```

Run context:

- Date/time run: 2026-10-06
- Working tree: `feat/self-contained-atom-onboarding`, POC artifacts uncommitted.
- Go version: `go version go1.23.4 windows/amd64`
- Copilot CLI version: `1.0.93-1`
- Cases: Eleven real Copilot CLI write cases and fifteen observed permission decisions.
- Runs: One complete revised matrix.

Result summary:

- Confirming observation: Normal artifact writes were auto-approved and all ordinary protected targets remained gated.
- Refuting observation: `specs/outside-link/escaped.md` resolved through a Windows junction and created `escaped.md` outside the repository.
- Inconclusive gap: None for the stated current-environment question.

## What The Spike Did

The disposable Go command created a temporary repository, installed the real hook,
created a Windows directory junction from `specs/outside-link` to an external
temporary directory, and invoked the real Copilot CLI `apply_patch` tool.

- Real dependencies: Copilot CLI, repository hooks, Windows junction behavior, and the filesystem.
- Simulated inputs: Temporary repository and controlled prompts.
- Measurements: Hook decision and resulting file existence for every target.

## What We Learned

- Accepting partial artifact writes resolves the first experiment's product trade-off.
- Lexical path membership and `filepath.EvalSymlinks` were insufficient to detect the Windows junction in this spike.
- The permission payload contained the lexical repository path, not the final external destination.
- The external file was actually created; this is not a hypothetical bypass.

## What This Changes

| Assumption going in | Status | Consequence |
|---|---|---|
| Every outside-boundary request can be identified from the permission target before approval. | Refuted | Do not ship the current path-based auto-approval approach. |
| Partial artifact writes are acceptable if code remains gated. | Confirmed | Patch atomicity is no longer the blocker; reparse-point containment is. |

## Explicitly Not Covered

- Whether a Windows-native final-path API can reliably reject every reparse-point escape.
- Linux and macOS symlink behavior.
- Shell commands or future Copilot tool payload formats.

## Recommendation

Return to discovery. Keep normal write prompts for now. A further experiment would
need to prove a cross-platform, final-destination containment check before any
repository hook could be considered safe.

Next artifact: none until the developer decides whether another security-boundary
experiment is worth running.

## Completeness Checklist

- [x] The question is copied verbatim from the brief.
- [x] Verdict is Refuted.
- [x] Verbatim command output is included.
- [x] Spike path and run context are recorded.
- [x] The surprising external write is captured.
- [x] The recommendation follows from the evidence.
- [x] Non-covered platforms and approaches are explicit.
