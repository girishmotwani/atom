---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-11"
status: "local-implementation-accepted-independent-review-open"
scope: "two bootstrap reference files; no runtime resolver or installed-content change"
---

# Package Detection Guidance Repair Validation

## Result

Implemented the [approved detection spec](package-detection-repair-spec.md) in the
canonical bootstrap reference and its byte-identical packaged mirror only. The
[pre-edit mapping](package-detection-repair-test-spec.md) covers all twelve numbered
behaviors. No source test was added, removed or weakened; this is the explicitly
approved documentation-only adaptation, not a production RED/GREEN cycle.

The exact candidate query matched ten expected local import/metadata observations
before shipped edits. After editing, the rendered query matched that candidate
byte-for-byte and executed successfully in the existing interpreter. The two
approved probe invocations used a combined wall-clock window of 37.654308 seconds,
below five minutes. There were no installs, model calls or module-help executions.
Temporary fixture cleanup and restoration of process sys.path were asserted.

Fourteen existing documentation/plugin contracts passed. The two shipped bootstrap
files match byte-for-byte, with SHA-256:

```text
1A2211645E8981D735C6C99E0C78D11E38437A5168B66B3367E8DBF90B06E96E
```

README and both init hashes are unchanged. No runtime source, public API, schema,
configuration, dependency, version, script file, installed plugin or target bundle
changed. The original stopped trial remains Inconclusive; Phase 09 is incomplete.

## Implementation And Contract Walkthrough

The query reports distribution registration, top-level spec presence and optional
non-importing candidate module names. It catches only PackageNotFoundError. When
metadata exists it leaves module_candidates null: no path-based false negative
can discard the installed/editable candidate. Null means not queried, not absent.
Help still determines working forms; a failed help always stops.

Without registration, non-importing child-spec evidence preserves potential
source-only forms and mixed entry-point/module use. Partial/verified unresolved
roles stop. A generic name with no expected candidates is explicitly ambiguous,
not installed or definitively absent. The permitted known-Linux-venv check is
read-only, and ambiguity cannot enter the Step 4 installation path even when that
venv is absent. Existing ownership/prefix/help prerequisites remain intact.

Walked all twelve mapped behaviors against final Steps 2/3 and retained text:
shortcuts before Python discovery; namespace ambiguity; exact exception handling;
registered and inconsistent metadata; source-only/mixed candidates; partial-role
precedence; ordinary absence; read-only ambiguity reuse; absent/unsafe known-venv
stop; occupied-venv no-overwrite; existing Windows/status/writer safeguards; mirror
parity and two-file scope. Steps 1/4 installer recipes and Windows opt-in are not
redesigned. No material spec change was needed.

These are factual/semantic checks of the instructions. Actual agent adherence,
custom importers, live editable installation variants, metadata exception routing,
failing-help routing and the new Linux ambiguity-to-venv path were not exercised.
Source-only/mixed cases validate candidate observations and which missing roles
they can cover, not successful execution of synthetic Atom commands. Existing
registered-install paths retain actual help verification; metadata is not identity
or health authentication. No universal platform/interpreter compatibility claim.

## Probe One: Exact Candidate Before Shipped Edits

Ran one local Python standard-input program. It executed the recorded query with
real-install and isolated temporary-layout controls. Raising fixture initializers
and role-module sentinels must not execute. Expected observation dictionaries
were specified independently; mismatch or import would raise and stop the run.
Captured stdout below is copied directly from the receipt, probe exit 0:

```json
{"probe": "pre_edit_candidate", "query_source": "import importlib.machinery\nimport importlib.metadata\nimport importlib.util\nimport json\ntry:\n    importlib.metadata.distribution('atom-cli')\nexcept importlib.metadata.PackageNotFoundError:\n    registered = False\nelse:\n    registered = True\npackage = importlib.util.find_spec('atom')\ncandidates = None\nif not registered and package is not None:\n    locations = list(package.submodule_search_locations or [])\n    candidates = [\n        module for module in ('atom.cli', 'atom.artifact_cli')\n        if locations and importlib.machinery.PathFinder.find_spec(module, locations) is not None\n    ]\nprint(json.dumps({'distribution': registered, 'package': package is not None, 'module_candidates': candidates}))", "started_utc": "2026-11-11T11:32:19.459221+00:00"}
{"atom_imported": false, "candidates_cover_missing_roles": null, "case": "existing_install", "distribution": true, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": null, "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": null, "case": "ordinary_absence", "distribution": false, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": null, "package": false}
{"atom_imported": false, "candidates_cover_missing_roles": false, "case": "namespace_only", "distribution": false, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": [], "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": false, "case": "unrelated_regular_package", "distribution": false, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": [], "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": true, "case": "source_only_full_roles", "distribution": false, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": ["atom.cli", "atom.artifact_cli"], "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": false, "case": "partial_cli_only", "distribution": false, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": ["atom.cli"], "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": true, "case": "mixed_verified_cli_writer_candidate", "distribution": false, "missing_roles": ["atom.artifact_cli"], "module_candidates": ["atom.artifact_cli"], "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": false, "case": "mixed_verified_cli_writer_absent", "distribution": false, "missing_roles": ["atom.artifact_cli"], "module_candidates": ["atom.cli"], "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": null, "case": "registered_candidate", "distribution": true, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": null, "package": true}
{"atom_imported": false, "candidates_cover_missing_roles": null, "case": "registered_without_package", "distribution": true, "missing_roles": ["atom.cli", "atom.artifact_cli"], "module_candidates": null, "package": false}
{"cases": 10, "elapsed_seconds": 0.06562419998226687, "fixtures_removed": true, "help_executions": 0, "installs": 0, "model_calls": 0, "query_sha256": "2686fd95defab40845c42e0110845a13613e1e5f6f72209ecf6c0d82432fe2f7", "result": "all candidate observations matched", "search_path_restored": true}
```

## Probe Two: Rendered Documented Query

Extracted the Python program from the shipped python3 -c example, compared it to
the pre-edit query and checked the two reference files' bytes. Ran the exact
extracted program through the existing interpreter with a 20-second subprocess
limit, preserving stdout/stderr/status. No fixture, installation or help was run.
Actual receipt (probe exit 0):

```json
{"bootstrap_byte_parity": true, "bootstrap_sha256": "1a2211645e8981d735c6c99e0c78d11e38437a5168b66b3367e8dbf90b06e96e", "exit_code": 0, "probe": "rendered_documented_query", "query_matches_pre_edit_candidate": true, "query_sha256": "2686fd95defab40845c42e0110845a13613e1e5f6f72209ecf6c0d82432fe2f7", "stderr": "", "stdout": "{\"distribution\": true, \"package\": true, \"module_candidates\": null}\n"}
{"elapsed_seconds_this_probe": 0.4455324999871664, "help_executions": 0, "installs": 0, "model_calls": 0, "probe_invocations_used": 2, "total_window_seconds": 37.654308}
```

The query SHA-256 agrees in both probes:
2686fd95defab40845c42e0110845a13613e1e5f6f72209ecf6c0d82432fe2f7.
This verifies the actual documented query, not another implementation of it. The
Windows interpreter executed the extracted program; a new Linux shell/agent trial
was not run. No unused probe allowance remains and no retry was performed.

## Existing Documentation And Packaging Contracts

From tools, actual command (exit 0):

```powershell
python -m pytest tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup -q
```

Verbatim captured output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 14 items

tests\test_plugin.py ...........                                         [ 78%]
tests\test_artifact_cli.py .                                             [ 85%]
tests\test_pathsetup.py ..                                               [100%]

============================= 14 passed in 3.78s ==============================
```

## Parity, Links, Whitespace And Source Scope

After the two-reference edits and before creating this validation artifact, ran
python tools\check_links.py and git --no-pager diff --check at root, compared the
bootstrap hashes and compared README/init hashes with the accepted pre-edit
snapshot. Actual output (all checks exit 0):

```text
checked 539 relative links across markdown files
all relative links resolve
git diff --check: exit 0
README and both init hashes unchanged.
Bootstrap pair SHA-256: 1A2211645E8981D735C6C99E0C78D11E38437A5168B66B3367E8DBF90B06E96E
```

The 539-link count is that checkpoint, before this artifact's new evidence links.
Final saved-artifact link/whitespace checks are recorded separately below. Existing
broader Python/Linux/README validation is reused only within its original scope;
no root Go module or Go build/vet/test/race/fmt pass is fabricated.

## Acceptance And Remaining Gates

The package-collision finding is locally addressed under the approved scope, not
independently re-reviewed. The previous two-reviewer budget remains exhausted;
Opus's original context gap and post-fix independent coverage for README/bootstrap
remain open. No model invocation, publication, commit/push/merge, installed-content
refresh or rehearsal occurred. Local acceptance and any further review/delivery
step require an explicit scoped decision. Do not equate this evidence with full
Phase 09 completion or compliance enforcement.
## Final Saved-Artifact Validation Receipt

After saving the validation/mapping/reconciliation artifacts, ran the same root
link and whitespace commands. Actual captured output (both exited 0):

```text
checked 541 relative links across markdown files
all relative links resolve
git diff --check: exit 0
```

A direct read confirmed the full saved validation, raw receipts, existing test
output and remaining limitations. git status --short contains the known earlier
five-document repair plus its phase evidence; this implementation changed only
the two bootstrap references and named evidence/journals. No new runtime/test or
script file is present.
## Persistence Process Qualification

During final evidence persistence after compaction, actual mandatory instruction
reloads occurred after initial artifact writes rather than before. This deviation
is recorded in decisions.md/findings.md, not treated as compliant. Required actual
reads and the final spec-to-reference walkthrough were completed before the gate.
No shipped source change or additional probe/model/install occurred in that lapse;
no receipt or independent-review limitation is replaced by this qualification.
## Explicit Local Acceptance

The developer selected exactly "Accept the local detection repair; keep further
work gated" after seeing the evidence, unexercised Linux/agent behavior,
independent-review gaps and recorded reload-order deviation. This accepts the
bounded local two-reference repair only. Further review/model spend, commit/push/
publication, installed-content refresh and rehearsal remain separately gated.
No further source edit, probe, install, model or later phase is authorized by this
acceptance. Phase 09 remains incomplete.
