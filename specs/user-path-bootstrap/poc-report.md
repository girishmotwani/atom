# POC Report: Windows user-PATH bootstrap

## Question

Can Python preserve a Windows user PATH while adding the installed Atom console-script directory exactly once, and run both entry points from a process whose inherited PATH does not contain that directory?

## Verdict

Confirmed for the tested Windows registry and executable-invocation behavior. No claim is made about Copilot approval counts.

## Evidence

Command: `python poc\user-path-bootstrap\spike.py`

```text
Can Python preserve a Windows user PATH while adding the installed Atom console-script directory exactly once, and run both entry points from a process whose inherited PATH does not contain that directory?
Script discovery: both entry points found; schemes inspected=2
Registry append: type=1; original_chars=2131; preserved=True; idempotent=True
Registry append: type=2; original_chars=2131; preserved=True; idempotent=True
Equivalent existing entries: 4 passed; empty PATH passed
Temporary registry key: removed
Absolute executable with empty child PATH: atom.exe; exit=0; usage: atom [-h] {check,poc,init,status,review,ship} ...
Absolute executable with empty child PATH: atom-write-artifact.exe; exit=0; usage: atom-write-artifact [-h] target
Real user PATH unchanged=True; system PATH unchanged=True; parent-process PATH unchanged=True
Verdict: Confirmed for registry preservation and absolute executable invocation; Copilot prompt count not measured
```

The command exited 0. The synthetic original PATH contained 2,131 characters, literal environment-variable tokens, a quoted entry, empty entries, and a trailing delimiter. Both REG_SZ and REG_EXPAND_SZ retained their value type and exact original prefix. Case differences, trailing separators, quotes, and a dot component did not create duplicate entries.

## What this changes

Python's user installation scheme locates both real console scripts on this Microsoft Store Python installation; the default scheme alone does not. Python can write the existing user PATH plus one directory without involving setx or copying the merged process PATH. Absolute entry-point invocation works even when the child PATH is empty, so the current Copilot session need not inherit a registry update or inspect Atom's source.

## Explicitly not covered

- No write to the actual user Environment key or the system PATH.
- No other operating system, shell-profile update, missing-script repair, or package installation.
- No simulation of registry permission failure or concurrent PATH writers.
- No Windows environment-change broadcast or proof that existing parent processes refresh their environment.
- No Copilot TUI onboarding run or measured reduction in approval prompts.

## Next gate

Approve using this evidence to write the production design and its error-handling/test obligations. Keep persistent changes opt-in and system PATH untouched.
