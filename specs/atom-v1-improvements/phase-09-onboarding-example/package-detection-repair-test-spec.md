---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
design_spec: "package-detection-repair-spec.md"
date: "2026-11-11"
status: "mapped-and-locally-validated-agent-adherence-unproven"
---

# Package Detection Guidance Repair Test Spec

## Evidence Choice And Scope

The developer approved the two-reference spec and its bounded validation, then
requested implementation. Map claims before shipped edits. Use the approved
documentation-only adaptation: execute the candidate discovery query on bounded
local import layouts, review the decision text, then run existing documentation/
package tests. No production RED/GREEN cycle, Go module or runtime resolver is
invented. The already accepted collision receipts establish the understood defect.

## Toolchain Redundancy Audit

None — no proposed case was unfailable.

No existing test is removed or weakened. Go nil/type/format/vet cases are not
proposed: this change has no Go API or runtime source. Python/discovery checks
can fail on wrong package/distribution/module evidence; documentation routing
can contradict the spec despite all tests passing, so semantic review is required.
No prose-constant tests are added as a proxy for agent adherence.

Silent-failure coverage: absent registration, an empty candidate list and partial
module evidence must not silently become permission to reinstall. Expected-module
presence without metadata must not be discarded. These are covered by controlled
query observations plus the decision-text walkthrough, not by compiler guarantees.
Typed nils, integer overflow, context cancellation, workers and shared state are
not applicable; none is introduced. Actual metadata exceptions and help failures
remain explicit semantic cases, not falsely reported execution coverage.

## Coverage Map (Written Before Edits)

| Spec behavior | Case / existing check | Expected evidence |
|---|---|---|
| 1 | Verified-entry-point/form shortcuts; real-install control | Text preserves early return; no new Python prerequisite for working entry points |
| 2 | Namespace-only and unrelated-package controls | Generic name is present while own metadata/candidates are absent; no atom import |
| 3 | Metadata query and exception review | Only PackageNotFoundError is expected absence; other exceptions propagate/stop |
| 4 | Registered-candidate and metadata-without-package controls | Candidate metadata permits help, not a health claim; inconsistent registration stops |
| 5 | Source-only full roles and writer-only mixed-form controls | Candidates cover missing roles without registration; actual help still required |
| 6 | CLI-only partial layout; a verified CLI plus no writer candidate | Partial/verified unresolved state stops; do not enter another env or install |
| 7 | Empty layout plus accepted ordinary-absence/reuse receipts | Explicit absence remains distinct from ambiguity; unchanged consent/install prerequisites |
| 8 | Collision controls plus Step 3 semantic walkthrough | Only read-only known-venv reuse allowed from ambiguity with no verified role |
| 9 | Ambiguous/absent-known-venv walkthrough | Stops before Step 4; healthy known venv requires both successful helps |
| 10 | Occupied-venv/source-only walkthrough | Ownership/prefix checks first; missing registration alone cannot discard working modules or authorize overwrite |
| 11 | Unchanged sections and existing bootstrap/pathsetup contracts | Preserve full errors/status, printed Windows forms, refusal stops and both roles |
| 12 | Byte parity, plugin tests, link/whitespace and scope receipts | Exactly the two references change; all other shipped hashes retained |

## Candidate Boundary Cases

Run the exact proposed inline query, not a substitute guessed predicate. Real
baseline: existing supported interpreter. Controlled layouts: ordinary absence,
namespace-only atom, unrelated regular atom, source-only expected modules,
partial CLI module, writer-only module with CLI already verified, registered
candidate and registered metadata without an import package. Standard-library
fixtures only; no installation or participant changes. A raising initializer in
synthetic packages detects an accidental atom import during discovery.

Assert raw registered/top-level/candidate observations independently of the
routing text. A mixed writer-only layout covers the missing writer role; CLI-only
without a writer cannot cover both roles. These observations do not make a
synthetic package a healthy Atom installation or prove runtime agent routing.
Source/editable forms are retained by metadata-aware and candidate/verified-role
branches; actual untested custom importers remain explicit limitations.

Record the exact query source and raw JSON receipts. At most two probe terminal
invocations and five minutes total; no extra models, installers or known-missing
module help. Any failure or unsupported required form stops before shipped edits.
The optional second invocation may validate the rendered documented query against
the already-tested candidate and existing interpreter; no new experiment/loop.

## Existing Checks After The Two Reference Edits

From tools:

```powershell
python -m pytest tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup -q
```

At root compare the two bootstrap files byte-for-byte, run python tools\check_links.py
and git --no-pager diff --check, and confirm the README/init pairs retain their
pre-edit hashes. Review the final change against all twelve behaviors, especially
ambiguity versus installation and partial/mixed-role precedence.

## Limits And Completion

No concurrent code is introduced; Go race/coverage/build gates are not applicable.
No dependency install is needed unless an approved check reports one missing.
Record actual results in package-detection-repair-validation.md; do not call source
or documentation checks proof of live Linux fallback, help-error adherence or a
clean independent review. Previous reviewer-context and post-fix coverage gaps
remain separate gates. No shipping, installed-content refresh or rehearsal.
## Execution Reconciliation

All twelve rows were checked against the final two references. Ten candidate
observation cases passed before edits; the second probe matched/executed the
actual rendered query, within the two-invocation/five-minute budget. Existing
contracts passed 14 cases; bootstrap bytes match, README/init hashes are unchanged.
Actual receipts and per-claim limitations are in package-detection-repair-validation.md.
Metadata exceptions, actual help failures, custom importers and live Linux routing
remain semantic-only evidence here, not claimed executed branches. No source test
was weakened or fabricated, and no production RED/GREEN loop is claimed.
