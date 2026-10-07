# Phase Plan: Artifact Writer

## Evidence carried forward

- A general repository `write` approval is too broad.
- A path-matching permission hook can partially apply a mixed patch.
- A Windows directory junction can escape lexical path matching.
- `tools/atom/artifacts.py` rejects junctions and writes only the agreed artifact set.
- Copilot cannot grant `atom artifact write` independently from other `atom` commands.
- Copilot can grant a dedicated `atom-write-artifact` executable independently.

## Phase 1: Dedicated artifact writer

**Delivers:** an installed `atom-write-artifact` command used by every artifact-producing
Atom skill, with one-time repository approval on first use.

**Risk:** passing realistic multiline Markdown through the shell may alter Copilot's
permission identity or require approval for another shell construct.

**POC question:** Can Copilot pass realistic multiline Markdown to an approved
`atom-write-artifact` executable in one shell invocation, while an adjacent `atom`
command remains unapproved?

**Done when:**

- The installed package exposes only the dedicated writer entry point for artifact
  writes.
- Source and packaged skills use it for `specs/**`, `poc/**`, and the three replaceable
  runtime files; the append-only event log remains behind its locked API.
- The first invocation uses Copilot's normal approval flow; later invocations use the
  saved repository permission.
- Forbidden paths, links, mixed batches, failed writes, and packaging are covered by
  tests.
- The complete Python suite passes on Windows and CI.

This is one phase because splitting the executable, skills, and onboarding assets would
leave intermediate commits that expose a command nobody calls or instructions that call
a command not yet installed.
