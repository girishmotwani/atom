# Design Spec: Dedicated Artifact Writer

## Established by POCs

1. A repository-wide `write` approval also permits source-code edits and is too broad.
2. Permission hooks see generic editor writes one file at a time and can partially
   apply a mixed patch.
3. A Windows directory junction under `specs/` can redirect a lexical path outside the
   repository.
4. Rejecting every reparse point before containment comparison blocks the demonstrated
   junction escape.
5. Copilot's shell permission matcher identifies `atom`, not the nested
   `atom artifact write` operation.
6. Copilot independently identifies and persists approval for an
   `atom-write-artifact` executable.
7. A PowerShell here-string piped to that executable preserves multiline Markdown and
   does not broaden the permission to adjacent `atom` commands.

## Still assumed

1. Windows PowerShell 5.1 defaults native-process stdin to ASCII. Instructions must
   set `$OutputEncoding` explicitly; PowerShell 7 already uses UTF-8. Production tests
   exercise Unicode bytes through the installed process boundary.
2. Copilot's normal interactive approval UI persists the same repository-scoped
   command identifier represented directly in the POCs' isolated permission files.
3. POSIX shells retain the same dedicated-executable permission identity when a
   heredoc is piped to the command. CI can test stdin transport but cannot prove
   Copilot's interactive permission UI.

## User workflow

```text
Atom skill prepares complete artifact content
              |
              v
shell multiline input | atom-write-artifact specs/.../artifact.md
              |
              v
first use: Copilot asks once to approve atom-write-artifact for this repository
later uses: saved command approval suppresses the prompt
              |
              v
artifact_cli reads UTF-8 stdin
              |
              v
artifacts.write_artifacts validates and atomically replaces one file
```

Code edits, tests, `.github/**`, and Atom's copied instructions continue through
Copilot's normal editor and retain their normal approval behavior.

## Public command

```text
atom-write-artifact TARGET
```

- `TARGET` is a repository-relative artifact path.
- The repository root is the current working directory.
- The complete file content is read from standard input as strict UTF-8.
- There is no `--from` option. Reading an arbitrary second path is outside this
  command's authority.
- There is no batch command syntax. Skills write one complete artifact per invocation.
- The package exposes the command through:

  ```toml
  [project.scripts]
  atom = "atom.cli:main"
  atom-write-artifact = "atom.artifact_cli:main"
  ```

The existing `atom` CLI does not expose `artifact write`; otherwise users may infer
that granting `atom` is safe.

## Python surface

`atom.artifact_cli` contains:

```python
def main(argv: Sequence[str] | None = None) -> int:
    """Write one complete Atom artifact through the dedicated permission boundary."""
```

It delegates all authorization and filesystem mutation to the existing
`atom.artifacts.write_artifacts` function. The CLI may classify first to reject an
invalid target before reading stdin, but that result is only an early diagnostic:
`write_artifacts` always performs the authoritative validation again during the write.

`atom.artifacts` remains the single implementation of:

- repository containment;
- the artifact allowlist;
- link and Windows reparse-point rejection;
- component-by-component parent creation;
- exclusive temporary-file staging;
- final revalidation;
- atomic replacement of one destination.

## Allowed destinations

The command permits:

- Files below `specs/`.
- Files below `poc/`.
- Exactly `.atom/config.json`.
- Exactly `.atom/state.json`.
- Exactly `.atom/baseline.json`.

It refuses:

- A bare `specs` or `poc` directory.
- Source, tests, build files, and every other repository path.
- `.github/**`.
- `.atom/atom/**`, because it contains Atom's governing instructions.
- `.atom/events.jsonl`, because it is an append-only audit log whose writes must hold
  `events.lock` through `EventLog.append`.
- Every other `.atom/**` path.
- Absolute destinations outside the repository.
- Normalized `..` traversal outside the allowed set.
- Every symlink, directory junction, or reparse point in the destination path,
  including one currently resolving inside the repository.

## Behaviors

**B1.** Given an allowed target and valid UTF-8 stdin, the command writes those
characters with CRLF and bare CR normalized to LF, prints `Wrote <absolute-path>` to
stdout, and exits `0`.

**B2.** The command supports empty stdin and creates or replaces the allowed target
with an empty file.

**B3.** Given malformed UTF-8 stdin, the command writes nothing, reports that stdin is
not valid UTF-8 to stderr, and exits `1`.

**B4.** Given a refused target, the command does not read stdin, writes nothing, prints
`atom-write-artifact: refused <target> (<reason>)` to stderr, and exits `1`.

**B5.** Given missing or extra positional arguments, argument parsing prints usage and
exits `2` without reading stdin or writing a file.

**B6.** Given an allowed target whose parent cannot be created or whose content cannot
be staged or replaced, the command writes no partial destination, reports the
filesystem error to stderr, and exits `1`.

**B7.** Existing destination content remains intact until a complete temporary file has
been flushed and the destination path has passed final validation.

**B8.** A link or reparse point appearing after initial classification but before final
validation causes refusal; staged temporary files are removed.

**B9.** `write_artifacts` validates every requested target before staging any content.
A batch containing a refused target stages and writes nothing. The dedicated CLI uses a
single-target batch.

**B10.** Onboarding does not edit `~/.copilot/permissions-config.json`. The first
`atom-write-artifact` invocation follows Copilot's normal permission prompt.

**B11.** Every artifact-producing source skill and every packaged copy instructs the
agent to send the complete artifact through `atom-write-artifact`; none instructs the
agent to use the generic editor for an allowed artifact path.

**B12.** Instructions explicitly prohibit using `atom-write-artifact` for source code
and state that a refusal must not be bypassed with another shell command.

## Error handling

| Condition | Exit | Output |
|---|---:|---|
| Success | `0` | `Wrote <absolute-path>` on stdout |
| Refused destination | `1` | Stable refusal reason on stderr |
| Invalid UTF-8 | `1` | UTF-8 diagnostic on stderr |
| Filesystem failure | `1` | Operation and OS error on stderr |
| Invalid arguments | `2` | `argparse` usage on stderr |

No exception traceback is part of the user-facing contract. Unexpected programming
errors are not broadly caught and may still surface as tracebacks.

## Atomicity and concurrency

Each single destination is atomically replaced with `os.replace`. A reader sees either
the previous complete file or the new complete file, never a partially written file.

The API is safe for concurrent writes to different destinations. Concurrent writes to
the same destination are permitted but not coordinated: each replacement is atomic and
the last successful replacement wins. No ordering guarantee is provided.

`write_artifacts` prevalidates multi-target batches, but it is not a filesystem
transaction. If an OS failure occurs after one of several replacements, earlier
replacements are not rolled back. The dedicated command avoids that ambiguity by
accepting exactly one destination.

The known residual race between final path validation and `os.replace` remains
documented in `specs/artifact-path-guard/findings.md`; eliminating it requires native
handle-relative filesystem APIs and is outside this phase.

## Skill and onboarding integration

The source skills under `skills/` are the authoring source. Matching files under
`tools/atom/assets/skills/` are package assets installed by `atom init`; they must carry
the same artifact-writing instruction.

Each affected skill will:

1. Build the complete artifact content before invoking the command.
2. Send it to `atom-write-artifact <relative-target>` through stdin.
3. Treat exit `0` as the only success condition.
4. Surface refusal or write errors rather than bypassing them.
5. Continue using the generic editor for production code during TDD.

The locally installed `.atom/atom/AGENTS.md` will state the same boundary. `atom init`
copies the updated assets but does not create a permission hook or modify user-level
Copilot configuration.

## Testing obligations

1. Unit tests for every behavior B1-B9.
2. Windows junction tests and POSIX symlink tests, skipped only where the platform
   cannot create the link type.
3. A subprocess test that builds and installs the wheel into an isolated environment,
   invokes the generated `atom-write-artifact` console script, and verifies both an
   allowed write and a refused source write.
4. Asset tests proving every artifact-producing packaged skill references
   `atom-write-artifact`.
5. Onboarding test proving the installed local bundle contains those instructions.
6. The full Python test suite with coverage.
7. A manual Copilot acceptance check: first invocation prompts, approval is saved, the
   second invocation is silent, and an adjacent `atom` command still prompts.

## Trade-offs

### Dedicated executable instead of an `atom` subcommand

Chosen because Copilot permissions identify the executable. An `atom` grant is broader
than the writer and includes current and future Atom commands.

### Standard input instead of `--from`

Chosen because it keeps the writer from reading an arbitrary second path and the POC
proved multiline stdin preserves the narrow command identity.

### Single target instead of a batch wire format

Chosen because skills naturally produce one artifact at each gate and atomic
multi-file commit semantics are not available from portable Python filesystem APIs.
The internal API retains prevalidated batches for tightly controlled callers.

### First-use approval instead of editing Copilot configuration

Chosen because the permission file is private user-level state whose schema Atom does
not own. Copilot's own approval flow owns persistence and future migrations.

### Refuse every link instead of resolving benign links

Chosen because the junction POC demonstrated that link interpretation is the dangerous
boundary. The developer confirmed no artifact workflow needs links.

## Extension points

A future Copilot extension or MCP tool may call `write_artifacts` directly, preserving
the same policy without invoking a shell. It must not duplicate the allowlist or accept
a previously classified path as authorization.

Additional writable paths require a design change, explicit developer approval, and
new negative tests. They are not runtime configuration because allowing the agent to
expand its own write boundary would defeat the boundary.
