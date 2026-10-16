# Test Spec: Opt-in Windows user-PATH setup

The developer approved design-spec.md in this conversation. Tests use the existing Python pytest runner. Windows registry writes are faked or restricted to a unique temporary Software key; no automated test may write the real Environment key.

| Design behavior | Test obligations |
| --- | --- |
| 1 | Real subprocess setup-path --help exits zero; setup works in an empty directory and leaves project files untouched. |
| 2 | Ordinary init and help never invoke setup; module bootstrap fallback remains documented. |
| 3 | Non-Windows setup fails clearly before discovery/registry access; importing Atom remains portable. |
| 4 | Discover default and user installation schemes; prefer first complete pair; ignore partial pairs and non-files; de-duplicate directories. |
| 5 | Missing scripts and delimiter/NUL directory fail without a registry write; OS discovery failures are explicit. |
| 6 | Absent key/value initializes empty REG_EXPAND_SZ; preserve REG_SZ/REG_EXPAND_SZ; invalid types/non-string values and permission errors fail explicitly. |
| 7 | Preserve literal tokens, casing, quotes, empty entries, trailing separators, and a value longer than 1,024 characters; never use merged process PATH. |
| 8 | Empty value succeeds; equivalent case, quote, variable, slash, trailing separator, and dot-component forms are no-write cases; unrelated similar prefixes are appended. |
| 9 | Accept exact Windows-length boundary and reject oversized additions before writing. Count UTF-16 units, including terminating NUL, for Windows limits. |
| 10 | Write only HKCU Environment Path with original type; verify idempotence and unchanged process/system environment; permission failures do not print success. |
| 11 | Assert broadcast arguments, pointer-sized types, Environment payload and timeout; call notification for changed and unchanged state; notification failure reports saved/already-present partial state without rollback. |
| 12 | CLI prints changed/unchanged status, resolved absolute paths and stale-parent notice; domain errors become stderr exit 1 with no traceback. |
| 13 | Source/bundle bootstrap and init docs remain byte-equivalent and explain explicit opt-in/current-session paths; README documents setup. |

## Redundancy audit

No Go compiler/vet-only cases apply: this is Python tooling. Keep behavior tests for empty/malformed values, missing files, OS errors, and pointer-sized native invocation because compilation alone cannot establish them. Do not test dataclass assignment getters solely for coverage.

## Sequence

First parser help and isolated CLI wiring; then script discovery, exact PATH construction, registry read/write behavior, native notification/error propagation, and documentation. Run each new behavior red before its implementation, then run the affected tests green. Use the full existing Python suite with coverage for completion.

## Scope

The POC, not these tests, established the initial Windows feasibility. Actual user-PATH mutation is reserved for the developer-requested final machine setup after implementation validation.
