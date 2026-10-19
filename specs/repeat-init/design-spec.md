# Repeat-init Design Spec

## Scope and evidence

One maintenance phase for issue #8, grounded in the approved [POC report](poc-report.md). The report established valid repeats exit 2 without writes and partial records bypass the guard and rewrite retained state. It did not prove a validator; the following boundary is a design choice to be verified test-first.

## Public contract

Keep `atom init`, `--module`, and explicit `--force`. A matching valid repeat prints `Already initialised` and `no changes made` on stdout and returns 0. Refused repeats return 2 with an `atom init:` diagnostic on stderr identifying the conflict or damaged path. Diagnostics explain that files were preserved, recommend repairing/restoring the named files, and warn that explicit --force discards recorded approvals. Ordinary operational read failures are reported, not tracebacks. First-init/write errors retain their existing exit behavior.

## Numbered behaviors

1. If `.atom` is absent, preserve first-init behavior: capture the untouched no-race baseline, record its result even when red, install configuration/state/bundle/pointer/ignore rules, and create specs/poc.
2. If any `.atom` entry already exists and --force is absent, perform read-only validation before build detection, checks, installers, writers, events, directory creation, or temp-file sweeping. An empty directory, non-directory entry, partial record, or damaged scaffold is not a fresh project.
3. Configuration must be a readable JSON object with nonempty string module_path, build_command, and test_command. Preserve extra fields and custom commands; do not redetect or compare commands with the current host environment.
4. State must be a readable JSON object with integer version 2 and a valid approvals list according to the existing state reader. Missing files, old/future/invalid versions, wrong shapes, and malformed approvals refuse without changes. Do not change the forgiving behavior of `atom status` or `Project.load`.
5. Match recorded module_path against explicit --module if supplied and against go.mod if it exists. Reject conflicting or unreadable/malformed go.mod even when --module matches. Without go.mod, permit reuse of the recorded module_path (first init already permits explicit --module without go.mod).
6. Validate the shared scaffold structurally: manifest.json is a readable JSON object identifying `atom init`, `atom-cli package`, and the two managed entries AGENTS.md and skills/; local AGENTS.md is nonempty/readable; all eight original skill entrypoints (init, discover, poc, plan, spec, tdd, review, ship) and the seven discipline reference files named in AGENTS.md are nonempty/readable. The local Copilot instruction file must contain the managed marker and the local bundle reference. The .gitignore managed block must have exactly one correctly ordered marker pair and include the three generated runtime rules. Additional instructions, ignored paths, and manifest fields are preserved. Do not compare bundle contents against the installed version or rewrite older complete instructions. This is structural onboarding validation, not an audit of skill text, templates, or all Markdown links.
7. baseline.json, events.jsonl, and events.lock are optional machine-local data, not no-op prerequisites. Do not read, validate, recreate, or update them. Absent specs/poc directories are also allowed because empty directories disappear in Git clones.
8. A valid matching repeat returns 0 without any path membership, bytes, file/directory modification time, approval, or event change. Two consecutive repeats must behave identically. No baseline result is claimed to have been refreshed.
9. Invalid/conflicting repeats return 2 with useful diagnostics and preserve the entire tree exactly, including retained approvals, even when one record file is missing. Never internally add --force or silently repair.
10. Explicit --force bypasses repeat validation and retains the existing deliberate reset/reinstall behavior, including clearing approvals. Do not broaden its semantics or make it implicit.
11. Update CLI help, README onboarding text, and both source and packaged init skills to distinguish first initialization, successful no-op, and refusal. On a no-op, skills must not require a newly captured or present historical baseline, compare commands to a nonexistent new baseline, or claim files were created. Preserve the external-source-lookup boundary.

## Implementation boundaries

Keep CLI flow and module-request handling in cli.py. Reuse storage.read_json, Project.load_config, and the existing approvals reader. Keep local scaffold validation beside its installer in onboarding.py and reuse its existing path/marker constants. Use an OnboardingError for scaffold validation failures and the existing state read errors for record failures. No new dependencies, flags, migration, or public command are needed. Keep configuration/state reader semantics unchanged for other commands.

## Concurrency and limits

This change supports sequential repeat calls only. Read-only validation introduces no locks or background workers. It does not make initialization atomic or safe against concurrent file mutation; a concurrently changing tree may produce an explicit refusal, and no cross-file consistency guarantee is claimed.

## Trade-offs and assumptions

- Fail closed on existing `.atom`, rather than let missing records cause destructive first init; directly justified by the POC's approval loss.
- Structural validation instead of a boolean existence shortcut, avoiding false success for missing/corrupt shared setup.
- Stable original skill/reference anchors instead of installed-package byte comparison, avoiding implicit upgrades and future-package inventory requirements for older complete bundles.
- Ignore optional runtime files and empty artifact directories; they are not guaranteed in fresh clones.
- Keep custom command values rather than redetecting tools; repeat init is not environment repair.
- One maintenance phase rather than a multi-phase project plan; the approved POC covers this phase's failure mode. Python pytest is the relevant completion gate for Atom's Python tooling, not root-level Go checks in a repository without a root Go module.

## Verification obligations

Snapshot paths, bytes, sizes, and nanosecond modification times including directories before successful and rejected repeats. Assert no checks, build detection, bundle installation, project initialization, events, or writes occur. Table cases cover corruption/missing/wrong types, module combinations, custom config/approvals, missing optional runtime files, and scaffold anchors. Keep existing first-init and explicit-force tests. Add a real subprocess repeat smoke test. Run affected Python tests, then the complete tools test suite with coverage; capture exact evidence in the TDD artifact. No independent model review is launched without its gate.
