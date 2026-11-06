---
project: "atom-v1-improvements"
phase: "phase-03-risk-proportionate-workflow-policy"
date: "2026-11-05"
status: "approved-for-shipping"
---

# Multi-Model Review

## Scope And Evidence

Two independent full-diff reviews, one each from `gpt-5.3-codex` and `claude-opus-5.5`, neither the implementation author. Four approved calls total: two availability probes and two review calls, with no retries/fallback. Both returned usable responses; no unavailable, silent or unparsed runs. The current checkout's Atom review implementation received the frozen staged change and complete numbered context for all 29 files, including the approved design and restored roadmap. Model-side tools/custom instructions were excluded using fixed-evidence mode.

Repository-root Go gates were explicitly skipped; no category is claimed excluded by those gates. Independent local checks: 50 documentation/distribution tests passed in 50.73s; seven canonical/packaged pairs matched; archived Go spike vet/build/gofmt passed without running its paid calls. The first format check caught a pipeline-added EOF blank line, which was corrected and rechecked. Standard staged whitespace checking flags 57 literal indented blank lines inside the captured POC transcript; those are intentionally preserved as evidence. All other staged files passed diff checking, and all whitespace flags in that report were verified to be whitespace-only lines inside its verbatim block. Earlier unstaged checks did not include these then-untracked artifacts.

These checks establish neither correct model behavior nor a complete taxonomy. Single-run model agreement is not stability evidence.

Staged tree: `089129a92da56fc7eb7767b4e69900a1939ceb7c`. Context: 299932 UTF-8 bytes, SHA-256 `d1f3f0e14c9c25fc229322c6750d686896416ec6ebf86ad93c67fe0729dd5b20`. Review prompt: 461907 bytes, SHA-256 `5e7e19ff0195db862d905fc56214954325bdf97e90aa0b23aad04173e90216ac`. Reported changed lines: 1789.

## Original Merged Findings And Proposed Triage

The tool merged 15 groups. This historical table retains the reported severities, model support and original proposed actions. The developer subsequently approved the scoped repairs below; the table and raw model JSON are not a new review of those repairs. `high` is a Major for triage, not a declaration that the guidance itself is unsafe to run. Packaged copies share the guidance findings even when a model cited only canonical text.

| # | Reported severity | Support | Location | Consequence / proposed action |
|---|---|---|---|---|
| 1 | high (Major) | 2/2 | `poc/atom-v1-risk-proportionate-policy/main.go:158` | Inconclusive/refuted outcomes exit zero and receive an automatic Confirmed wrapper. Already disclosed, but both reviewers flag it. Recommend fixing/verifying verdict handling before publication; no paid rerun required for deterministic paths. |
| 2 | medium | 1/2 | `com.github.copilot/commands/start.md:38` | Earliest-missing-beat rule/table still forces a new POC despite the added proportionality paragraph. Recommend reconciling routing text without adding an entry point. |
| 3 | medium | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:72` | Windows timeout kills cmd only; descendant output pipes may keep the call alive. Previously disclosed and untested. Recommend deferring full Windows lifecycle validation, keeping the rerun warning; do not claim a hard wall-clock guarantee. |
| 4 | medium | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:83` | Successful-call stderr was discarded by `Output()`, not proven empty. Recommend correcting report provenance; do not reconstruct lost historical stderr. Future instrument capture needs a separately verified change. |
| 5 | medium | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:100` | Probe accepts any nonempty text rather than READY. Historical probes actually returned READY. Recommend a focused validation correction for future instrument use or explicit deferral. |
| 6 | medium + low | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:174` | Missing gate_bypass_suggested silently becomes false; generic rejection diagnostic obscures causes. All observed answers contained the field. Recommend strict required-field validation or explicit archive limitation, not a changed historical claim. |
| 7 | medium | 1/2 | `skills/build/SKILL.md:94` | POC-skip row omits developer approval. Recommend explicit approval wording, matching the shared policy. |
| 8 | medium | 1/2 | `skills/spec/SKILL.md:17` | Narrowed entry condition loses the still-allowed specifically approved no-uncertainty skip. Recommend restoring this legitimate existing condition. |
| 9 | medium | 1/2 | `skills/tdd/SKILL.md:214` | Unconditional Done-when tests/Go gate conflict with the documentation-only adaptation. Recommend scoping runtime checklist requirements to runtime code and naming factual/distribution checks for docs. |
| 10 | medium | 1/2 | `specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-brief.md:51` | Uncapped retry procedure can spend 51, not 39: 2 primary probes + 1 alternate probe + 8 slots x (3 primary + 3 alternate attempts). The hard cap stays 48. Recommend correcting arithmetic/provenance, preserving the actual ten-call result. |
| 11 | low | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:95` | Proposed exec-error wrapping: reject as a blocker; invocation logs already identify model/case, and the spike is disposable. |
| 12 | low | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:147` | Proposed comment on same-model comparison: optional clarification, not an observed bug. |
| 13 | low | 1/2 | `poc/atom-v1-risk-proportionate-policy/main.go:167` | Proposed named type/struct: reject as a blocker; no transposition was observed and adding abstraction is not needed for the archived spike. |
| 14 | low | 1/2 | `specs/atom-v1-improvements/decisions.md:32` | Claimed stale no-push/no-commit statement: reject; no push or commit has occurred, and later entries authorize publication rather than claiming execution. |
| 15 | low | 1/2 | `specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-brief.md:6` | Draft metadata is stale after approval/execution. Recommend correcting status metadata. |

## Original Decision Gate (Subsequently Triaged)

At this gate, no fixes, push, commit or PR had occurred after the review. The substantive new evidence-provenance finding is that successful stderr was not captured; historical output cannot be repaired by inventing empty streams. The raw model suggestions are preserved below, not silently dropped. The developer subsequently approved guidance/provenance/deterministic-harness repairs and deferred Windows lifecycle validation. The reviewed snapshot above remains the original pre-repair snapshot, not an independent review of the later changes. Any additional model calls require separate approval; the four-call budget is exhausted.

## Approved Repair Disposition

- Findings 1, 2, 4-10 and 15: accepted; deterministic harness, guidance, provenance, arithmetic and metadata repairs implemented. Verification is recorded separately below/in the test spec.
- Finding 3: Windows process-tree timeout validation explicitly deferred. Keep the archive warning; no hard wall-clock or descendant-cleanup claim.
- Findings 11-14: not blockers under the approved triage; retain their original suggestions and evidence above.

Only the original four review calls were authorized and used. No new model review or live POC rerun has occurred. Repairs require local verification; they must not be described as having passed another independent model review.

## Actual Atom Review JSON

```json
{
  "diff": {
    "changed_lines": 1789,
    "files": [
      ".github/copilot-instructions.md",
      ".gitignore",
      "AGENTS.md",
      "README.md",
      "com.github.copilot/commands/start.md",
      "docs/workflow.md",
      "poc/atom-v1-risk-proportionate-policy/README.md",
      "poc/atom-v1-risk-proportionate-policy/go.mod",
      "poc/atom-v1-risk-proportionate-policy/main.go",
      "skills/atom/references/poc-discipline.md",
      "skills/atom/references/tdd-discipline.md",
      "skills/build/SKILL.md",
      "skills/discover/SKILL.md",
      "skills/spec/SKILL.md",
      "skills/tdd/SKILL.md",
      "specs/atom-v1-improvements/decisions.md",
      "specs/atom-v1-improvements/findings.md",
      "specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/design-spec.md",
      "specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-brief.md",
      "specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-report.md",
      "specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/test-spec.md",
      "specs/atom-v1-improvements/phase-plan.md",
      "tools/atom/assets/AGENTS.md",
      "tools/atom/assets/skills/atom/references/poc-discipline.md",
      "tools/atom/assets/skills/atom/references/tdd-discipline.md",
      "tools/atom/assets/skills/build/SKILL.md",
      "tools/atom/assets/skills/discover/SKILL.md",
      "tools/atom/assets/skills/spec/SKILL.md",
      "tools/atom/assets/skills/tdd/SKILL.md"
    ],
    "source": "staged"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        },
        {
          "model": "gpt-5.3-codex",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "high",
      "is_corroborated": true,
      "line": 158,
      "lines": [
        158
      ],
      "messages": [
        {
          "line": 158,
          "message": "The harness only prints INCONCLUSIVE or REFUTED and always exits 0, so `atom poc run` reports `CONFIRMED (exit 0)` for any outcome; call os.Exit with a non-zero status for those verdicts.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 158,
          "message": "The program prints INCONCLUSIVE/REFUTED outcomes but always exits 0, so callers can treat failed experiments as successful runs.",
          "model": "gpt-5.3-codex",
          "run_index": 1,
          "severity": "high"
        }
      ],
      "severities": [
        "high"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "com.github.copilot/commands/start.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 38,
      "lines": [
        38
      ],
      "messages": [
        {
          "line": 38,
          "message": "\"Pick the earliest beat whose output is still missing. Never skip ahead.\" plus a routing table with no regression or evidence-reuse rows still routes an understood regression to /atom:poc, contradicting the new paragraph that follows.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 72,
      "lines": [
        72
      ],
      "messages": [
        {
          "line": 72,
          "message": "On Windows the context timeout kills only cmd.exe and cmd.WaitDelay is unset, so an orphaned copilot child holding the stdout pipe can block Output() past the 5-minute bound.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 83,
      "lines": [
        83
      ],
      "messages": [
        {
          "line": 83,
          "message": "command.Output() keeps stderr only inside *exec.ExitError, so stderr from successful calls is discarded, yet the report presents ten empty \"stderr (verbatim)\" blocks as captured evidence.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "gpt-5.3-codex",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 100,
      "lines": [
        100
      ],
      "messages": [
        {
          "line": 100,
          "message": "The availability probe accepts any non-empty response as success instead of requiring the expected READY token, which can misclassify unavailable models and waste call budget before fallback.",
          "model": "gpt-5.3-codex",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": true,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 174,
      "lines": [
        174
      ],
      "messages": [
        {
          "line": 174,
          "message": "A response that omits gate_bypass_suggested decodes to false and passes validation, so a missing gate-control field is silently treated as compliant instead of unclassifiable.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        },
        {
          "line": 174,
          "message": "The json.Unmarshal error is discarded and every rejection is logged with one generic reason, which hides whether the JSON was malformed or a required field was missing.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "medium",
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "skills/build/SKILL.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 94,
      "lines": [
        94
      ],
      "messages": [
        {
          "line": 94,
          "message": "The per-phase POC row still says \"skippable only with a specific recorded justification\" without the developer approval that docs/workflow.md and poc-discipline.md now require, so the gate condition drifts across documents.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "skills/spec/SKILL.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 17,
      "lines": [
        17
      ],
      "messages": [
        {
          "line": 17,
          "message": "Replacing the approved-skip entry condition removes the documented no-uncertainty skip path (pure refactor or mechanical wiring) that poc-discipline.md lines 146-153 still allow, and the \"Never use when\" rule now sends those cases to /atom:poc.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "skills/tdd/SKILL.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 214,
      "lines": [
        214
      ],
      "messages": [
        {
          "line": 214,
          "message": "The new documentation-only adaptation forbids fabricating an `atom check` result, but the unchanged Done-when list still requires green `atom check` output and watched-failing tests, so the guidance contradicts itself.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-brief.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "medium",
      "is_corroborated": false,
      "line": 51,
      "lines": [
        51
      ],
      "messages": [
        {
          "line": 51,
          "message": "The stated 39-call worst case is wrong: two probes, one alternate probe, and 8 model-cases x 6 attempts give 51 calls, so the 48-call cap, not the procedure, is the binding limit (repeated at lines 76 and 101 and in decisions.md line 11).",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "medium"
        }
      ],
      "severities": [
        "medium"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 95,
      "lines": [
        95
      ],
      "messages": [
        {
          "line": 95,
          "message": "The exec error is returned unwrapped, so callers cannot tell which model or case invocation failed; wrap it with the model and case ID.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 147,
      "lines": [
        147
      ],
      "messages": [
        {
          "line": 147,
          "message": "The `left.model == right.model` guard (the alternate model filling both slots) has no comment explaining why it makes a comparison incomplete, so a maintainer could delete it as incidental.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "poc/atom-v1-risk-proportionate-policy/main.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 167,
      "lines": [
        167
      ],
      "messages": [
        {
          "line": 167,
          "message": "The `func(string, string, string, string)` parameter hides argument order (kind, model, caseID, prompt) and invites silent transposition; use a named type or struct.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "specs/atom-v1-improvements/decisions.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 32,
      "lines": [
        32
      ],
      "messages": [
        {
          "line": 32,
          "message": "The statement \"No push or commit made for this phase\" is stale beside the later publication entries in the same file and should be marked superseded.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    },
    {
      "agreement": [
        {
          "model": "claude-opus-5.5",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-brief.md",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "low",
      "is_corroborated": false,
      "line": 6,
      "lines": [
        6
      ],
      "messages": [
        {
          "line": 6,
          "message": "Frontmatter still says `status: \"draft\"` even though the brief was approved and executed, which contradicts its own execution annotation.",
          "model": "claude-opus-5.5",
          "run_index": 1,
          "severity": "low"
        }
      ],
      "severities": [
        "low"
      ]
    }
  ],
  "has_no_usable_response": false,
  "is_partial": false,
  "models": [
    {
      "model": "gpt-5.3-codex",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    },
    {
      "model": "claude-opus-5.5",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "fixed-evidence"
  },
  "review_execution": {
    "context_quality": "unvalidated",
    "documents": [
      {
        "label": "context-1",
        "sha256": "d1f3f0e14c9c25fc229322c6750d686896416ec6ebf86ad93c67fe0729dd5b20",
        "utf8_bytes": 299932
      }
    ],
    "mode": "fixed-evidence",
    "prompt_sha256": "5e7e19ff0195db862d905fc56214954325bdf97e90aa0b23aad04173e90216ac",
    "prompt_utf8_bytes": 461907,
    "scope": "diff-plus-caller-context",
    "tool_policy": "source-exclusions-requested"
  },
  "schema_version": 3,
  "silent_runs": [],
  "toolchain": {
    "control_gates": [],
    "degraded": false,
    "gates": [],
    "skip_reason": "toolchain checks were skipped by request",
    "source_fingerprint": null,
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
```


## Local Repair Verification

The [repair verification log](tdd-log.md) preserves the actual failing/passing regressions and combined local checks. The archived module passed build, vet, format, tests and race via atom check; the selected Python documentation/distribution suite passed all 50 tests. Content parity, historical transcript/raw-review integrity and the bounded literal-transcript whitespace exception were checked separately.

Accepted deterministic/guidance/provenance findings are repaired and locally verified; Windows lifecycle validation remains explicitly deferred. This does not claim another model review, a live rerun, universal policy quality or actual developer-control enforcement. No push/PR occurred after repair. The repaired snapshot is awaiting the developer's completion gate.


## Completion Gate Approval

The developer selected "Approve repaired snapshot for shipping" after reviewing the verification summary and deferred Windows lifecycle limitation. Shipping is authorized under the earlier explicit stacked push/PR request; no additional model calls or merge are authorized. This approval supersedes the waiting-gate statements above. No commit/push/PR has yet occurred.
