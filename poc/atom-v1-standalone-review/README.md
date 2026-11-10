# Standalone Review Composition Trial

Original approved question:

Can the installed Atom review CLI select working, staged and branch changes in
local Go repositories without Atom or phase state, produce correctly scoped
reports, preserve source/state, and retain honest missing-module and failing-gate
behavior, with a deterministic reviewer transport instead of real model calls?

Approved scopes and raw results live under
`specs\atom-v1-improvements\phase-04-entry-points\standalone-review\`:

- `execution.json`: original trial, stopped on the observer's advisory-tool gap.
- `transport-correction-execution.json`: advisory correction, completed working
  review but stopped on the observer's missing Python blob-helper allowance.
- `remaining-cases-brief.md`: approved exact-helper correction and only four
  remaining cases; `remaining-cases-execution.json` is that run's separate output.

Current `run_trial.py` observes staged, branch, broken-source and no-module cases.
It reuses the completed working case rather than repeat it. Exact source archives
preserve both earlier observer versions; the advisory-corrected archive also
records the validated frozen-wheel/runtime boundary for evidence reuse.

Run from this repository only within the approved one-execution scope:

```powershell
python .\poc\atom-v1-standalone-review\run_trial.py
```

The observer imports installed non-editable Atom and calls its CLI entry function
with external reviewer transport intercepted. Actual Git/Go commands run; absent
optional analyzers are honestly recorded. Only the exact installed interpreter
and shipped binary-safe Git-blob reader may execute Python in a fixture. Its
nested Git child is counted from the verified helper body, not independently
instrumented. No Copilot process or real model is launched. This is mechanics
and output-selection evidence, not independent review quality or human-control
proof, a published GitHub installation, or full Phase 04 completion.

Executable spike code uses ordinary source editing. Documents and raw evidence
use the approved artifact writer. Refuse an existing target; preserve fixtures
and prior evidence. Do not retry, repair a failed observation or clean up without
a separate scoped decision. All three raw outputs remain distinct.
