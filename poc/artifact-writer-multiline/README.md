# Artifact writer multiline spike

Question:

> Can Copilot pass realistic multiline Markdown to an approved
> `atom-write-artifact` executable in one shell invocation, while an adjacent `atom`
> command remains unapproved?

The spike used the installed Copilot CLI, an isolated Copilot home, and a temporary
wrapper over the real Python guard. The temporary repository was not production code;
verbatim evidence is preserved in:

`specs/artifact-writer/phase-01-dedicated-writer/poc-report.md`

Verdict: **Confirmed.**
