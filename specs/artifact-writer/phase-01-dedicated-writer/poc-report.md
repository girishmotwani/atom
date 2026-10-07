# Phase 1 POC Report: Multiline Artifact Transport

## Question

Can Copilot pass realistic multiline Markdown to an approved
`atom-write-artifact` executable in one shell invocation, while an adjacent `atom`
command remains unapproved?

## Verdict

**Confirmed.**

A PowerShell here-string piped to `atom-write-artifact` ran under the saved permission
for that executable. The real Python guard wrote the exact multiline Markdown. Under
the same permission configuration, `atom artifact check` was denied.

## Evidence

Approved multiline invocation:

```text
Wrote C:\Users\gimotwan\AppData\Local\Temp\atom-multiline-permission-poc\specs\multiline.md

COPILOT_EXIT=0
--- FILE ---
# Design: "quoted"

- first
- second: a | b
```

Adjacent Atom command under the same saved permission:

```text
Permission denied because no interactive user response was available. Retry in an interactive session so the user can approve it, or try an alternative that does not require this permission.

COPILOT_EXIT=0
```

The isolated permission file contained only:

```json
{
  "kind": "commands",
  "commandIdentifiers": [
    "atom-write-artifact"
  ]
}
```

No generic `write`, `powershell`, or `atom` approval was present.

## What changes

The production command can read UTF-8 content from standard input. Skills can use a
PowerShell here-string on Windows without creating an intermediate file or requesting a
second approval. The dedicated executable remains the permission boundary.

## Explicitly not covered

- Documents near Windows command or process-input size limits.
- POSIX shell heredoc syntax.
- Interactive approval UI wording.
- Building and installing the final package entry point.
