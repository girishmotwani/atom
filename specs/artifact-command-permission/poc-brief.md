# POC Brief: Artifact Command Permission

## Question

Does a saved or command-line permission for `atom artifact write` suppress Copilot
CLI's approval prompt for that command, while leaving other shell commands unapproved?

## Why this question

The proposed workflow depends on approving Atom's guarded artifact writer once per
repository. If Copilot identifies shell permissions only by the executable name, a
grant for `atom artifact write` may either fail to match or approve every `atom`
subcommand. Discovering that after wiring every skill would invalidate the workflow.

## Method

Run Copilot CLI 1.0.93-1 non-interactively in a temporary repository with only the
PowerShell tool available. Use a fake `atom.cmd` to expose permission matching without
side effects, then route a dedicated `atom-write-artifact.cmd` through the real
`tools/atom/artifacts.py` writer.

Test both:

- `--allow-tool` command-line permissions.
- A repository entry in an isolated `COPILOT_HOME/permissions-config.json`.

## Success criteria

Confirmed only if all are true:

1. `atom artifact write` can be approved without approving another `atom` subcommand.
2. The equivalent saved repository approval behaves the same way.
3. The approved command reaches the real guard, which writes an allowed artifact and
   refuses source code.

## Explicitly not covered

- Installing the permission during `atom init`.
- Updating Atom's skills to call the writer.
- Interactive approval UI wording.
- POSIX shell matching.
