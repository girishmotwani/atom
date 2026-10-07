# Decisions

- Added the `atom.artifact_cli` module entry-point guard rather than relying only on the generated console script, because bootstrap explicitly supports hidden entry points through `python -m`.
- Extended both bootstrap copies and pinned byte-for-byte parity in tests.
- Made `atom init` own baseline capture, config command recording, scaffold creation, and local bundle installation. The developer chose this deterministic CLI ownership over agent-authored follow-up files.
- Kept a failing baseline as recorded onboarding evidence rather than making it block scaffold creation; onboarding must distinguish pre-existing failures from failures it caused.
- Kept race detection disabled only for the onboarding baseline, matching the existing init contract; normal completion gates still use race detection.
- Verified successful onboarding through named reads after the single init command and explicitly prohibited normal-path `git status`, recursive shell scans, and extra Atom commands.
- Used Python `pywinpty` and `pyte` only as throwaway experiment dependencies to drive and capture the real Windows TUI. They are not project dependencies.
- Counted `/exit` as experiment cleanup, not workflow typing, because it occurred after Copilot completed the onboarding response.
- Preserved the user's unrelated modifications under `poc/atom-short-namespace/` and excluded them from this change.
