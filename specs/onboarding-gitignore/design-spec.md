# Design Spec: Managed Atom Gitignore Entries

## Purpose

Keep machine-generated Atom runtime files out of pull requests without hiding shared
configuration, approvals, or onboarded instructions.

## Behavior

`atom init` maintains one clearly marked block in the repository root `.gitignore`:

```gitignore
# >>> Atom generated runtime files >>>
# Machine-local Atom runtime data; project configuration and approvals stay tracked.
.atom/baseline.json
.atom/events.jsonl
.atom/events.lock
# <<< Atom generated runtime files <<<
```

The operation:

1. Creates `.gitignore` when it does not exist.
2. Appends the block without changing existing user-authored content.
3. Replaces an existing Atom-managed block rather than adding another.
4. Produces identical bytes when repeated.
5. Uses the existing file's newline convention.
6. Refuses malformed or duplicate managed markers rather than guessing which content
   Atom owns.
7. Replaces `.gitignore` atomically so a failed write leaves the original intact.
8. Reports filesystem failures with a concrete `atom init --force` recovery command.

It does not ignore `.atom/config.json`, `.atom/state.json`, `.atom/atom/**`, or the
whole `.atom/` directory. It does not modify the Git index, so previously tracked
runtime files require an explicit one-time `git rm --cached`.
