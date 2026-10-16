# POC Brief: Windows user-PATH bootstrap

## Question

Can Python preserve a Windows user PATH while adding the installed Atom console-script directory exactly once, and run both entry points from a process whose inherited PATH does not contain that directory?

## Why prove this

The installed Atom package works through Python module invocation, but its two console scripts are not on PATH. Onboarding should not need repeated command discovery, implementation reads, or a separate approval for each investigation. An incorrect persistent PATH update could truncate existing settings, expand variables prematurely, or add duplicate directories.

## Approved intent

The developer approved including a one-time, opt-in user-PATH setup before pushing the onboarding fix. Preserve existing entries, leave system PATH unchanged, and use resolved executable paths during the current Copilot session.

## Experiment

Use a throwaway Python spike, because Atom's tooling and proposed setup are Python. Locate candidate Scripts directories through Python's installation schemes and verify both installed console scripts exist. Exercise Windows registry read/write behavior under a unique temporary HKCU Software key, never the real Environment key. Use synthetic PATH values longer than 1,024 characters, including unexpanded environment-variable tokens, mixed casing, trailing separators, empty entries, and existing equivalent script-directory entries. Verify original content and registry value type survive append and a repeated run is a no-op. Remove only that explicitly created temporary key.

Invoke both installed executables by absolute path with --help from a child process whose PATH excludes their directory. Confirm this succeeds without mutating the parent process PATH. Read the real user PATH before and after only to verify it was not changed; do not print its contents.

## Success criteria

- Both Atom executables are found using supported Python installation locations.
- Appending preserves every original character and registry value type, including a PATH longer than 1,024 characters and unexpanded tokens.
- A repeated setup does not add another equivalent directory.
- Both absolute executable help checks exit zero despite the stale inherited PATH.
- The real user PATH and system PATH are not written by this experiment.
- Output gives explicit pass/fail evidence and cleanup succeeds.

## Cost and limits

One local Python spike; no subagents, network calls, dependency installation, or production code. Does not prove Copilot prompt-count reduction or that an already-running parent process can inherit a registry update. No persistent environment change until implementation and explicit opt-in.

## Gate

Approve running this isolated POC before selecting the production command interface.
