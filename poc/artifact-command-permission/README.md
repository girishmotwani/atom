# Artifact command permission spike

Question:

> Does a saved or command-line permission for `atom artifact write` suppress Copilot
> CLI's approval prompt for that command, while leaving other shell commands unapproved?

This integration spike used the installed Copilot CLI directly. The temporary command
wrappers and isolated Copilot homes were deleted after the run; the verbatim commands'
results are preserved in:

`specs/artifact-command-permission/poc-report.md`

Verdict: **Refuted.** Copilot identifies the executable `atom`, not the nested
`artifact write` operation. A dedicated `atom-write-artifact` executable was proven as
the safe replacement.
