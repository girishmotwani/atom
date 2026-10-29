# Repeat-init Test Spec

Approved design: [design-spec.md](design-spec.md).

| Design behavior | Coverage |
|---|---|
| 1: first init untouched baseline/scaffold | Existing test_onboarding baseline and scaffold tests |
| 2, 8: read-only successful repeat | New test_init_repeat snapshot includes root/directories/files, bytes, sizes, mtime_ns; run twice; fail-on-use checks/detection/install/writers/event hooks |
| 3: configuration shape/custom values | New parameter cases for absent keys, nonstrings, empty strings, invalid JSON/object; successful custom-command/extra-field preservation |
| 4: state integrity | New missing/JSON/version/approval shape cases, preserving forgiving status semantics |
| 5: module requests | New inferred/explicit/missing go.mod matches and conflicting/malformed/unreadable cases |
| 6: shared scaffold | New missing/empty/unreadable skill/reference/AGENTS, manifest shape, pointer marker/link, ignore marker/rule cases |
| 7: optional clone/runtime data | Success with missing ignored runtime data and empty specs/poc; do not inspect optional runtime contents |
| 9: refusal preservation | Snapshot each invalid setup; no writes/checks/detection; explicit path/error/repair/force warning |
| 10: deliberate reset | Existing force test plus force over partial/damaged scaffold |
| 11: help/docs/skills | CLI help and source=packaged skill contract assertions, no baseline-required claims on no-op |
| Real process | New python -m atom.cli smoke test, no-go.mod explicit initial module then matching repeat |

## Loop order

Successful no-op, configuration/state/module refusal, shared scaffold refusal, documentation surface. One behavior family per RED/GREEN step; capture actual assertion failures before production edits. Existing behavior tests that pass immediately remain regression evidence rather than claimed RED evidence.

## Redundancy audit

No candidate tests removed. Python can receive null/wrong JSON types at runtime, unlike Go's compile-time nil-string restriction; these are genuine test cases. No Go production code or concurrency is added, so Go-only compile/vet/race properties are inapplicable. Python pytest with coverage is the approved tooling gate.
