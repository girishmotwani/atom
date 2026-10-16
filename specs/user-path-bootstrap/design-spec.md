# Design Spec: Opt-in Windows user-PATH setup

## Purpose and evidence

Make installed Atom commands directly usable without repeated package-location searches during onboarding. The approved [POC report](poc-report.md) established preservation of long PATH values and registry types, duplicate detection, Python installation-scheme discovery, and absolute executable invocation with a stale process PATH.

This is one bounded Python-tooling change, not a Go application phase. No production code is included in this spec.

## Established facts

- Both installed console scripts can be located through Python's installation schemes; this machine requires the user scheme rather than the default scheme.
- Appending one directory can preserve the exact existing user PATH prefix and REG_SZ or REG_EXPAND_SZ type without setx.
- Equivalent casing, quoting, trailing separators, and dot components can be recognized without rewriting existing entries.
- Absolute executable paths work without updating the parent process PATH.

## Assumptions and unproven boundaries

- A standard Windows environment-change broadcast should allow environment-aware launchers to refresh future child environments. The POC did not exercise this; production adapter tests and a real opt-in run must verify the API call and report failures honestly.
- No promise is made that every existing terminal or Copilot process reloads PATH, or that Copilot will request fewer approvals in every configuration.
- Concurrent non-Atom PATH editors are not coordinated by this command. It is not a transaction across unrelated programs.

## Public command

`python -m atom.cli setup-path`

The dedicated command is the opt-in: ordinary `atom init`, help, and all other commands leave persistent PATH unchanged. It works before onboarding and outside a Go module, and does not create or reset .atom state. When already discoverable, `atom setup-path` is equivalent. No extra confirmation is performed inside the deterministic CLI; the onboarding skill obtains consent once before invoking this command unless the developer already explicitly requested the change.

On success, print whether the directory was added or already present, both absolute executable paths with Windows invocation examples, and a notice that the running parent process is unchanged. Use those exact executable paths for the remainder of the session; do not re-probe command names or read package source.

## Internal shape

Add one small Python module, `atom.pathsetup`, containing a concrete result with the scripts directory and whether the registry value changed, a domain-specific `PathSetupError`, and the setup operation consumed by the CLI. Keep discovery, PATH comparison, registry I/O, and Windows notification helpers private. No third-party dependencies or shell scripts.

## Numbered behaviors

1. The parser exposes setup-path and its help. Help has no registry side effects. The command requires neither go.mod nor an existing .atom directory.
2. Without this explicit command, init and other existing commands never call PATH setup. The existing bootstrap module fallbacks remain supported without opting in.
3. On non-Windows systems, report that automatic user-PATH setup is Windows-only and perform no registry or shell-profile write. Existing cross-platform Atom commands still import and run.
4. Inspect only the current Python default Scripts location and its preferred user Scripts location, in that order, de-duplicated. Select the first directory containing both atom.exe and atom-write-artifact.exe as files. Do not inspect source files, recurse through the filesystem, install packages, or assume a Python version.
5. If neither directory contains both files, fail before any registry write and tell the developer to repair console-script installation for the intended Python environment. A discovered directory containing a PATH delimiter or NUL is rejected rather than writing an ambiguous PATH entry.
6. Read only HKCU Environment's Path value. If absent, begin with an empty value and REG_EXPAND_SZ. Preserve existing REG_SZ and REG_EXPAND_SZ types. Reject any other type or non-string value without writing. Read errors other than a missing key/value are explicit failures.
7. Preserve the original PATH string exactly and append only a separator and the discovered directory when needed. Do not use the merged process PATH, expand stored tokens, normalize stored entries, truncate, or change system PATH.
8. Compare entries using Windows case-insensitive path normalization, environment-variable expansion for comparison only, surrounding whitespace/quotes, trailing separators, and dot components. If an equivalent directory already exists, do not write the registry. Empty PATH and existing empty entries remain valid inputs.
9. Before writing, reject a resulting PATH longer than the Windows 32,767-character limit including its terminating NUL. Existing long but valid values above 1,024 characters must remain intact.
10. Write only the current user's Path value, preserving its type. A write failure returns an explicit error and never prints a success message. Do not request administrator privileges or modify process/system PATH.
11. After establishing the user PATH, including the already-present case, broadcast WM_SETTINGCHANGE with Environment using SendMessageTimeoutW and a 5,000ms timeout parameter. A failed notification returns an explicit partial-completion error stating that PATH is saved/already present but Windows could not be notified; do not roll back a saved value or pretend setup fully succeeded.
12. On complete success, return and print the resolved absolute executables. Make clear that the current parent process is not updated and use these paths for remaining onboarding commands. All setup errors are concise stderr messages with an atom setup-path prefix, exit 1, and no traceback; parser errors remain exit 2.
13. Bootstrap and init documentation, both source and packaged copies, explain the one-time Windows opt-in, preserve the no-opt-in module fallback, prohibit source inspection, and avoid repeated probing after successful setup. README documents manual usage and the current-session limitation. Do not claim setup removes legitimate permission approvals.

## Error handling

Registry, discovery, and notification errors are wrapped with their failed operation in PathSetupError. Only expected OS and setup errors are caught; programming errors are not silently converted to success. A missing registry value is an explicitly supported initial condition, not an error fallback. A failed notification after a successful write identifies that partial state so a retry or fresh login can recover without overwriting unrelated entries.

## Concurrency and ownership

No threads, subprocess daemons, or background jobs. The command reads and writes one current-user registry value synchronously; it is not safe against concurrent external PATH edits. Tests must never write the real user Environment key. Registry adapter tests use fakes or a uniquely named disposable HKCU Software key; notification tests use a stub except the explicit real-machine opt-in run.

## Tests and verification

Derive tests directly from the numbered behaviors: CLI reachability and output, safe non-Windows import, discovery schemes, missing scripts, malformed directories, absent/unsupported registry values, preservation of both string types, long/unexpanded/empty values, equivalent-directory forms, idempotence, read/write/notification errors, and source/bundle documentation parity. Cover setup isolation from ordinary init. Use real temporary registry I/O on Windows where feasible without touching Environment. Test the ctypes adapter's pointer-sized argument contract and timeout through a fake function.

Use the existing Python pytest runner. This repository has no root Go module; atom check is not the validation tool for its Python implementation. Run targeted tests during red/green development, then the full existing Python suite with coverage before shipping. After developer implementation approval, the explicit requested machine setup can run the real setup-path command, verify the stored directory and successful notification without printing existing PATH contents, and invoke both emitted executable paths.

## Trade-offs

- A dedicated setup command avoids silently changing persistent user settings during every init, and can repair command discovery without resetting an already-onboarded project.
- Registry APIs avoid setx truncation and preserve expandable string types. No system-wide environment edit or shell-profile script is introduced.
- Absolute executable output handles the stale current session without trying to mutate Copilot's parent environment.
- Automatic support is Windows-only for this change; other platforms retain working bootstrap behavior. Shell-specific profile edits are out of scope.
- Environment notification is required for an honest usable setup outcome. A notification failure is a visible partial failure, not an ignored warning.

## Shipping follow-through

Preserve the three unrelated poc/atom-short-namespace edits. Push only this approved fix and its relevant artifacts to the current origin. The installed marketplace currently points to an inaccessible old repository; completing the requested plugin update will require correcting the atom marketplace to this checkout's GitHub origin, then updating and verifying installed instruction bytes. Never claim an old-source update includes this fix.
