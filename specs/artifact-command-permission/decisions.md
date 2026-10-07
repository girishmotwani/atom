# Decisions

## 1. Used the installed Copilot CLI as the spike

The uncertainty is Copilot CLI permission matching. A throwaway Go program could only
wrap the CLI and would add no evidence, so the experiment invoked Copilot directly.
This deviates from Atom's normal Go-spike shape.

## 2. Ran before writing the brief to disk

The developer explicitly approved verifying the exact permission claim, and the
question had already been stated in the conversation. The brief was persisted after
execution rather than gated as a separate turn. This is a process deviation; it did
not change the question or success criteria during the run.

## 3. Used isolated Copilot homes for saved-permission tests

Each saved-permission case used a temporary `COPILOT_HOME` containing only copied
non-secret settings and a purpose-built `permissions-config.json`. The developer's
real permission file was not modified.

## 4. The corrected design must use a dedicated executable

Do not grant `atom` shell permission. Package a narrowly named executable such as
`atom-write-artifact` whose only operation calls the guarded writer. Atom onboarding
may then save approval for that executable without approving `atom check`, `atom ship`,
or any future Atom command.
