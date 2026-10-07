# POC Report: Artifact Command Permission

## Question

Does a saved or command-line permission for `atom artifact write` suppress Copilot
CLI's approval prompt for that command, while leaving other shell commands unapproved?

## Verdict

**Refuted.**

Copilot's shell permission matcher does not distinguish the nested
`atom artifact write` subcommand. The narrow grant does not match; the grant that does
match approves the whole `atom` executable.

A corrected approach was also proven: a dedicated `atom-write-artifact` executable has
its own permission identity and can call the real path guard.

## Evidence

Installed CLI:

```text
GitHub Copilot CLI 1.0.93-1

You are running the latest version.
```

Command-line grant for the proposed nested command:

```text
Permission denied because no interactive user response was available. Retry in an interactive session so the user can approve it, or try an alternative that does not require this permission.
```

The broader executable grant:

```text
FAKE_ATOM_EXECUTED args=artifact write specs/probe.md --from payload.md
```

Saved repository permission with command identifier `atom artifact write`:

```text
Permission denied because no interactive user response was available. Retry in an interactive session so the user can approve it, or try an alternative that does not require this permission.
```

Saved repository permission with command identifier `atom`, running an adjacent
subcommand:

```text
FAKE_ATOM_EXECUTED args=artifact check specs/probe.md
```

Saved repository permission with command identifier `atom-write-artifact`:

```text
Wrote C:\Users\gimotwan\AppData\Local\Temp\atom-command-permission-poc\specs\persisted.md

FILE_EXISTS=True
```

The same dedicated permission calling the real guard with an allowed target:

```text
Wrote C:\Users\gimotwan\AppData\Local\Temp\atom-command-permission-poc\specs\allowed.md

FILE_EXISTS=True
```

The same permission with a source-code target:

```text
atom artifact: refused internal/main.go (outside-artifact-set)

FILE_EXISTS=False
```

The dedicated permission did not approve the adjacent `atom artifact check` command:

```text
Permission denied because no interactive user response was available. Retry in an interactive session so the user can approve it, or try an alternative that does not require this permission.
```

## What changes

The skills must not invoke `atom artifact write` through a generally approved `atom`
command. The safe workflow requires a separate packaged entry point whose complete
authority is the artifact guard, for example:

```text
atom-write-artifact specs/project/design-spec.md --from draft.md
```

Only `atom-write-artifact` is saved as an approved command. Other Atom commands and
ordinary code edits continue to prompt.

## Explicitly not covered

- Whether `atom init` should edit the user's permission file automatically or instruct
  the user to approve the dedicated command once.
- Skill wording and transport of multi-line content.
- POSIX shell permission behavior.
- The separate artifact guard's Windows race limitations, already documented in
  `specs/artifact-path-guard/findings.md`.
