# Init UX Evidence

## Scope and verdict

The developer-reported init transcript showed repeated individual bootstrap
checks. Prior accepted evidence in [prerequisite flow](../atom-v1-improvements/phase-09-onboarding-example/prerequisite-flow-repair-report.md) and [package detection](../atom-v1-improvements/phase-09-onboarding-example/package-detection-repair-validation.md) covers the original discovery operations and their stated limits.

A separately approved one-operation Python prototype was **Inconclusive** as an
integrated resolver: local classification worked for the listed cases, but the
operation was not invoked through a plugin. A further interactive trial established
that a harmless script bundled with a local plugin ran from a separate workspace;
the participant reported at least one approval or trust prompt but did not remember
its contents or response. The script was not the discovery prototype. Neither
experiment establishes an approval count, actual init prompt reduction or behavior
of an installed marketplace plugin. No runtime resolver is part of this change.

## Selected verbatim prototype results

These are the case/result lines as emitted by the respective local runs. Other
output, including environment-specific paths and command streams, is intentionally
omitted from this public artifact. The original complete local reports remain in
the developer's working tree. Windows and Ubuntu each exited 0.

### Windows

```text
{"case": "actual", "result": "usable-entry-points"}
{"case": "missing", "expected": "absent", "result": "absent"}
{"case": "ambiguous", "expected": "ambiguous", "result": "ambiguous"}
{"case": "partial", "expected": "partial", "result": "partial"}
{"case": "mixed", "expected": "partial", "result": "partial"}
{"case": "healthy", "expected": "usable", "result": "usable"}
{"case": "failing", "expected": "error", "result": "error"}
{"case": "unsafe-symlink", "result": "not-exercised-on-windows"}
{"result": "local-cases-finished", "plugin-invocation": "not-exercised", "interactive-permissions": "not-exercised"}
```

### Ubuntu

```text
{"case": "actual", "result": "usable-known-venv"}
{"case": "missing", "expected": "absent", "result": "absent"}
{"case": "ambiguous", "expected": "ambiguous", "result": "ambiguous"}
{"case": "partial", "expected": "partial", "result": "partial"}
{"case": "mixed", "expected": "partial", "result": "partial"}
{"case": "healthy", "expected": "usable", "result": "usable"}
{"case": "failing", "expected": "error", "result": "error"}
{"case": "unsafe-symlink", "expected": "unsafe", "result": "unsafe"}
{"result": "local-cases-finished", "plugin-invocation": "not-exercised", "interactive-permissions": "not-exercised"}
elapsed_seconds=14.096755399994436
```

The Linux symlink case exercised its checker directly, not complete unsafe routing;
Windows did not exercise this Linux-specific check. Source-only fixtures ran under
`-S`; they are not exhaustive installation or custom-importer evidence. The overall
recorded duration is execution context, not a usability benchmark.
