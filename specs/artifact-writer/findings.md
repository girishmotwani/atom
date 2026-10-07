# Findings

## 1. Copilot reports permission denial with exit code 0 — Medium

The adjacent `atom` command was correctly denied, but the non-interactive Copilot
process still reported `COPILOT_EXIT=0`. Integration tests must inspect output and
filesystem effects rather than treating the outer Copilot process exit code as the
permission verdict.

## 2. User-level pip Scripts may not be on PATH — Medium

The editable install generated `atom-write-artifact.exe`, but this machine's user-level
Python Scripts directory is not on `PATH`. Invoking the generated executable by its
absolute path succeeded for an artifact and refused source code. This is the same
existing installation issue as the `atom` executable, but the previous README fallback
(`python -m atom.cli`) is unsafe for the writer because approving `python` would broaden
the permission boundary. README troubleshooting now requires adding the Scripts
directory to user PATH for both commands.

## 3. Interactive PowerShell 5.1 defaults native stdin to ASCII — Resolved

Independent review reproduced non-ASCII Markdown becoming `?` before reaching the
writer. README and onboarded instructions now set `$OutputEncoding` to UTF-8 explicitly
and recommend PowerShell 7. The installed-process test covers Unicode bytes; CRLF input
is normalized to LF.

## Carried findings

Additional findings remain recorded in:

- `specs/artifact-write-permissions/findings.md`
- `specs/artifact-path-guard/findings.md`
- `specs/artifact-command-permission/findings.md`
