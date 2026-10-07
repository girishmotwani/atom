# Phase 1 POC Brief: Multiline Artifact Transport

## Question

Can Copilot pass realistic multiline Markdown to an approved
`atom-write-artifact` executable in one shell invocation, while an adjacent `atom`
command remains unapproved?

## Why this is the riskiest unknown

The permission matcher recognizes the dedicated executable, but Atom artifacts are
usually multiline Markdown. If piping or quoting that content changes the permission
identity, the workflow will still prompt repeatedly and the proposed integration fails.

## Method

In a temporary repository:

1. Expose `atom-write-artifact.cmd` as a thin wrapper over the real Python guard.
2. Give an isolated Copilot home a saved repository permission for only
   `atom-write-artifact`.
3. Ask Copilot to pipe a Markdown document containing headings, punctuation, quotes,
   and multiple lines to the executable in one PowerShell invocation.
4. Read the resulting file byte-for-byte.
5. Ask Copilot to run an adjacent `atom artifact check` command under the same saved
   permission.

## Success criteria

- The multiline command runs without an interactive permission response.
- The resulting file exactly matches the requested Markdown.
- The adjacent `atom` command is denied.
- No generic `write` or broad `atom` approval is present.

## Explicitly not covered

- Very large documents near Windows command-size limits.
- POSIX shell syntax.
- Packaging the final console script.
- Interactive approval UI wording; the saved repository grant represents the state
  after the one-time approval.
