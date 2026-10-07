# Decisions

## 1. Use one vertically sliced phase

The executable, skill instructions, packaged onboarding assets, and tests form one
user-visible behavior. None is independently useful without the others.

## 2. Approval occurs on first use

`atom init` will not edit Copilot's private user-level permission configuration. The
developer approved the normal first-use prompt, after which Copilot persists the
repository-scoped executable grant.

## 3. The approved command is `atom-write-artifact`, never `atom`

The permission POC proved that approving `atom` also approves adjacent commands. The
dedicated executable's entire authority is the guarded artifact writer.

## 4. Use standard input for artifact content

The phase POC confirmed that a PowerShell here-string piped to the dedicated executable
retains the executable's narrow permission identity and preserves multiline Markdown.
This avoids creating an unguarded intermediate file.

## 5. Used an isolated saved grant instead of automating the interactive approval UI

The POC represented the state after first-use approval with an isolated
`permissions-config.json`. Automating Copilot's interactive terminal UI would test
terminal keystrokes rather than the permission boundary. The user-visible first-use
prompt remains an integration acceptance check.

## 6. The production executable accepts one target and stdin only

There is no `--from` option and no public batch format. Standard input keeps arbitrary
file reading outside the approved command's authority. A single target gives the
command a truthful atomic-replacement contract without pretending portable filesystem
operations provide transactional multi-file commits.

## 7. Same-destination concurrent writes are last-writer-wins

Every replacement is atomic, but the writer does not serialize independent agents.
Adding a lock would introduce stale-lock recovery and cross-platform semantics without
evidence that Atom needs concurrent writes to the same artifact.

## 8. Writable paths are code, not configuration

The allowlist remains fixed in `atom.artifacts`. An agent-editable configuration file
would let the caller expand the boundary that is supposed to constrain it.

## 9. Corrected the packaging-test build environment

The first packaging test used `pip wheel --no-build-isolation`, but the active test
environment does not contain the declared `setuptools.build_meta` backend. The failure
occurred before Atom's package was inspected. The flag was removed so pip honors
`pyproject.toml`'s `[build-system]` declaration and creates the same isolated build
environment used for a normal install; no assertion was weakened.

## 10. Corrected the real-repository status fixture after adding this project

`test_the_real_repository_resolves_to_the_atom_cli_project` assumed `specs/atom-cli`
was the repository's only project directory. Adding the approved
`specs/artifact-writer/phase-plan.md` made that premise false and the full suite failed
because the resolver correctly reported ambiguity and selected the lexically first
project. The test now asserts that real ambiguity and separately reads the atom-cli
phase history; production status behavior was not changed.

## 11. The path guard predates this phase's approved spec

`tools/atom/artifacts.py` and its initial tests were written during the earlier guard
investigation before this phase's design gate. They were retained because they contain
the executed junction and race protections the design now depends on; deleting and
retyping them would manufacture a TDD history rather than create one. The dedicated
CLI, console-script registration, skill integration, onboarding assertions, and
replace-failure cleanup were driven from observed RED tests in this phase.

## 12. Removed `.atom/events.jsonl` from the writer allowlist after review

Independent review identified that whole-file `os.replace` bypasses `EventLog.append`'s
cross-process lock and can erase or lose audit entries. The developer approved removing
it. Event writes remain exclusively behind the append-only event-log API.

## 13. Normalize native shell newlines and require explicit PowerShell UTF-8

Windows PowerShell 5.1 encodes native-process stdin as ASCII unless `$OutputEncoding`
is changed. Instructions now set UTF-8 explicitly, the installed-process test sends
non-ASCII bytes, and the writer normalizes CRLF and bare CR to LF so shell transport
does not change repository newline conventions.
