# artifact-path-guard — throwaway spike

Disposable. Not production code, not imported by anything.

Answers one question: can a Python path guard deny a write through a real Windows
directory junction that points outside the repository, while still allowing ordinary
`specs/**`, `poc/**` and the four `.atom` runtime files?

```powershell
python spike.py
```

Exit 0 Confirmed / 1 Refuted / 2 Inconclusive.

Creates two temp directories and links them with `mklink /J`. Writes nothing through the
guard — it only prints decisions.

Verdict and evidence: `specs/artifact-path-guard/poc-report.md`.

## Superseded

The production guard is `tools/atom/artifacts.py`, which also performs the write. This
spike remains as the record of how the reparse-point-before-containment ordering was
established. Nothing imports it.
