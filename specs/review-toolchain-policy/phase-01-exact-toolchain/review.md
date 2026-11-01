# Exact Go Independent Review And Triage

Status: **two independent reviews completed; later root fix separately tested;
cross-platform CI currently failing**.

## Completed Model Reviews

| Reviewer | Usable reviews | Findings | Context and duration |
|---|---|---|---|
| gemini-3.8-flash | 1 | None | Retained standard-context response; 297.4306458000792 seconds |
| claude-sonnet-5.5 | 1 | Two low/Minor findings | Approved long_context response; 65.40789499995299 seconds |

Both received the same complete twenty-file/context prompt: 721289 UTF-8 bytes,
SHA-256 `891bd89e0334776c3568a6d6af11aeacc581ac74ca3e1329b845ed2a30d958ec`.
Tools/custom instructions were excluded and root responses passed fixed-evidence
validation. The reviewers differ from the primary authoring model.

Actual validated Gemini response:

```json
[]
```

Actual validated Claude response:

```json
[
  {
    "file": "tools/atom/go_selection.py",
    "line": 238,
    "severity": "low",
    "message": "Every field in the `go env -json` output, including GOENV, must be a non-empty string. Go can report GOENV as an empty string when no user config directory resolves, for example a minimal container with neither HOME nor XDG_CONFIG_HOME set. A correct installed distribution would then fail with `verification_failed` (\"missing or malformed Go environment fields\"). Suggested fix: require GOENV to be a string but allow it to be empty, and keep the non-empty requirement for GOVERSION, GOROOT and GOTOOLCHAIN."
  },
  {
    "file": "tools/atom/go_selection.py",
    "line": 222,
    "severity": "low",
    "message": "The version probe regex `go version go<ver> \\S+\\s*` accepts exactly one platform token. A Go build whose `go version` output has an extra experiment token, such as `go1.26.9 X:foo linux/amd64`, is rejected even though the version, root and hash checks that follow would pass. The failure is explicit, not silent. Suggested fix: match `go version go<ver>(\\s+\\S+)+\\s*`, or drop this probe in favour of the exact GOVERSION check from `go env`."
  }
]
```

## Finding Dispositions

| Severity | Agreement | Location | Finding | Disposition |
|---|---|---|---|---|
| Minor (model: low) | 1/2 | tools/atom/go_selection.py:238 | Empty observed GOENV rejects some minimal environments | Deferred under the approved four-non-empty-fields contract. Explicit GOENV=off is an option; no automatic rewrite or acceptance change. |
| Minor (model: low) | 1/2 | tools/atom/go_selection.py:222 | Experiment-labelled version output is rejected | Rejected as outside the exact-stable contract; no ordinary stable-release regression established. |

Each finding was read individually. Neither was discarded for lack of agreement.
No model Blocker/Major finding was reported; these dispositions are not a claim
that the models approved every later change.

## Subsequent Author-Found Root Bug

Publication inspection found that a different canonical GOROOT could share the
selected resolved bin/go and pass executable/hash checks. Approved behavior 7
already requires the inspected distribution root. One independent root-equality
guard and one regression fixed this Minor gap.

The regression first failed with DID NOT RAISE GoToolchainSelectionError, then
179 coupled selection/review/CLI tests passed. The alias is a filesystem-I/O
simulation, not a native junction reproduction. Both models reviewed the
preceding snapshot, not the later check/test. All other reviewed code, tests,
guidance and drivers remained unchanged.

Full RED/GREEN, the failed Windows gate, isolated handle diagnosis and latest
passing full gate remain verbatim in [TDD evidence](tdd-evidence.md). The latest
local result is 1615 passed, 5 skipped in 176.32s, 95%, exit 0. A prior native
handle-count failure remains unexplained, not fixed or erased.

## Invocation History

| Approved batch | Actual commands | Result |
|---|---|---|
| Original default reviewers; 300-second reviews | 3: two probes and one review | GPT unavailable; Gemini rejected prompt budget; zero usable reviews |
| Replacement Claude/Gemini; 300-second reviews | 4: two probes and two reviews | Gemini completed; Claude rejected prompt budget |
| Claude-only long_context; 600-second review | 2: one matching probe and one review | Claude completed; Gemini not rerun |

Nine commands actually ran, yielding two usable independent reviews. None of
the failed attempts timed out and no automatic retry occurred.

The original 780615-byte prompt had SHA-256
`4fe61a7cded1253bbe4eeaf6f17a3f0db44e8852dc9dd6f4ac114ebdff68e0d6`.
The replacement removed duplicate new-file diff text, not complete files/context.
Claude's tokenizer still exceeded its standard context. Raw model captures and
the complete former report are archived outside Git.

Original safe failure diagnostics, unchanged:

```text
Error: Model "gpt-5.4" from --model flag is not available.
```

```text
Execution failed: Request exceeds the model's prompt budget after reserving output (203090 tokens; limit 200000). Reduce context or compact before continuing.
```

```text
Execution failed: Request exceeds the model's prompt budget after reserving output (226156 tokens; limit 200000). Reduce context or compact before continuing.
```

The first gate incorrectly called 300 seconds the existing timeout; the library
default is 600 seconds. The approved stricter deadline did not cause these failures.

## Current Readiness

CI on source commit 2d42f6f is not green: macOS and Windows CLI jobs failed.
Linux CLI, existing POC jobs and documentation passed. Actual summaries and
links are in [findings](../findings.md); this cleanup does not repair code.
Native race/CGO, real dependencies and exhaustive SDK-manager discovery remain
outside established local evidence.

girishmotwani/atom#14 tracks model-budget preflight; girishmotwani/atom#16 tracks
fresh independent post-patch review. Neither repair is implemented in this PR.
