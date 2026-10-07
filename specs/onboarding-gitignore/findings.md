# Findings

- Ignore rules do not remove files already tracked by Git. Existing onboarded
  repositories need a one-time `git rm --cached .atom/baseline.json
  .atom/events.jsonl .atom/events.lock` for whichever files are tracked.
