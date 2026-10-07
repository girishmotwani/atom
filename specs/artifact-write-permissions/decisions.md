---
project: "artifact-write-permissions"
phase: "n/a"
date: "2026-10-06"
---

# Decisions Log

## Decisions

| # | Date | Choice point | Decision | Why | Raised with developer? |
|---|---|---|---|---|---|
| 1 | 2026-10-06 | Persist broad write approval or evaluate a repository hook | Evaluate a path-checking `permissionRequest` hook. | Persistent `write` approval includes production code. | Yes |
| 2 | 2026-10-06 | Define “all Atom artifacts” | Allow `specs/**`, `poc/**`, and only `.atom/config.json`, `.atom/state.json`, `.atom/events.jsonl`, and `.atom/baseline.json`. | This preserves prompts for code and prevents the agent from modifying its own bundled instructions. | Yes |
| 3 | 2026-10-06 | Include shell commands | Exclude all shell auto-approval from this POC. | Shell permission cannot be safely constrained by destination path. | Yes |
| 4 | 2026-10-06 | First POC showed partial application of a mixed patch | Accept partial artifact writes when the protected code target remains gated. | The developer confirmed this behavior is acceptable for the desired prompt reduction. | Yes |
| 5 | 2026-10-06 | Second POC demonstrated a Windows junction escape outside the repository | Stop the auto-approval work and retain normal Copilot write prompts. | Shipping the hook would auto-approve at least one write outside the declared artifact boundary. | Yes |

## Standing Waivers

None.

## Skipped Steps

None.
