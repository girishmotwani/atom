---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
author: "Copilot with developer gates"
date: "2026-11-11"
status: "local-implementation-accepted-independent-review-open"
poc_report: "prerequisite-flow-repair-review.md"
scope: "shared bootstrap reference and its packaged mirror only"
---

# Package Detection Guidance Repair Spec

## Purpose

Avoid executing known-missing Atom module forms merely because Python can find an
unrelated top-level atom package. Preserve verified command reuse, source/editable
module forms and genuine-error stops. This is a documentation addendum to the
[accepted flow spec](prerequisite-flow-repair-spec.md), not a new resolver engine,
installer or claim that agents enforce the rules.

The developer selected exactly "Accept the collision evidence and draft the narrow
repair spec", then "continue". That authorizes this draft, not implementation.

## Evidence Base

Accepted evidence: [bounded collision result and original receipts](prerequisite-flow-repair-review.md).

Established before design:

- In the existing local Windows interpreter, the generic atom presence query,
  both expected command-module lookups and atom-cli distribution metadata were
  present. The probe did not execute either command.
- In a controlled namespace-only layout and a synthetic unrelated regular-package
  layout, find_spec('atom') returned a spec but both expected command modules and
  the atom-cli distribution were absent. This reproduces the name ambiguity.
- The probe used non-importing PathFinder lookup through package-spec search
  locations. The unrelated-package initializer was not executed. Temporary
  fixtures were removed and process sys.path was restored.
- One probe invocation took 0.023066100024152547 seconds; no model, installer,
  participant write or missing-module help ran. Full JSON receipts are retained
  in the accepted report, not reconstructed here.
- The earlier [flow discovery receipts](prerequisite-flow-repair-report.md) cover
  ordinary absence and safe known-Linux-venv reuse, within their original limits.
  The [flow validation](prerequisite-flow-repair-validation.md) covers existing
  documentation/package contracts and the subsequent local README fix.

Still assumed or requiring boundary validation:

- Combining metadata and module evidence will preserve supported installed,
  editable, source-only and mixed entry-point/module use. One real installation
  and two synthetic collisions do not establish all these combinations.
- Non-importing path-based lookup does not resolve every custom importer. A
  negative role lookup under a same-named package is ambiguous, not universal
  proof that Python could never import that role.
- Metadata absence does not prove command absence; metadata presence does not
  prove the selected import path is healthy or unshadowed.
- Actual query exceptions, partial/broken installations and failing help were
  not newly exercised. Preserve their stop rules; do not claim tested adherence.
- A known venv can be reused safely only under the existing ownership, prefix,
  interpreter and successful two-role checks. The collision probe did not run
  those checks or demonstrate live Linux fallback from a collision.

This supports a bounded guidance design, not universal replacement-detector proof.
Material uncertainty exposed by candidate validation stops implementation for a
new evidence decision rather than being patched around silently.

## Scope And Supersession

Change exactly these shipped files after approval:

- skills\atom\references\bootstrap.md
- tools\atom\assets\skills\atom\references\bootstrap.md

The shared reference owns detection. The main init skill already delegates to it,
requires both verified roles and preserves partial/error stops; it need not grow
a duplicate detector. README's separately approved fix remains unchanged. If a
required directly dependent change is discovered elsewhere, stop and re-scope.

This addendum replaces the earlier top-level-name-only presence criterion and
clarifies its use in Steps 2 and 3. It also proposes one explicit narrow exception
to the old Step 3 entry condition: with no verified role and ambiguous same-name
module evidence, allow READ-ONLY checking of the single known Linux venv. This
is not confirmed absence and does not permit Step 4 installation. All existing
installer, permission, client-identity and failing-baseline contracts remain.

## Public Surface And Responsibilities

No exported Go/Python API, helper package, subcommand, dependency, persisted JSON
schema or configuration field is added. Callers still use established atom and
atom-write-artifact command forms. No implementation source is read during target
onboarding, and no shell/PowerShell script file is introduced.

The reference describes standard-library discovery evidence, not a new runtime
classification API. Gather only these facts with the selected supported Python:

- whether the atom-cli distribution is registered, distinguishing only the
  expected PackageNotFoundError from unexpected metadata errors;
- whether a top-level atom import spec is available;
- where necessary, whether expected atom.cli and atom.artifact_cli module specs
  are locatable without importing atom or executing its initializer.

Use the accepted non-importing path-based approach as candidate evidence for the
last point; do not use a dotted find_spec lookup that imports its parent merely
to classify an unrelated package. Do not inspect source, scan arbitrary paths,
print origins or claim these flags prove identity/health. Exact inline command
wording belongs to the approved documentation edit, not a copied production body
in this spec. This spec adds no enforcement or automatic classifier.

## Decision Shape

Apply in order; an already verified role is never discarded for another Python.

| Evidence | Next permitted action |
|---|---|
| Both roles already verified in the unchanged session | Reuse them without metadata discovery |
| Unexpected discovery exception/nonzero result | Report the actual diagnostic and stop |
| atom-cli metadata present but top-level atom absent | Report inconsistent/partial own installation and stop; no missing-module help |
| atom-cli metadata and top-level atom present | Recognized installation candidate: verify only missing roles with actual help; a failed help stops, never falls through |
| No own metadata; expected module specs cover every still-missing role | Possible source-only module forms: help-check only those roles; no metadata requirement for a form that works |
| Some role already verified, or some required modules present, but remaining roles unavailable/uncertain | Partial or mixed unresolved setup: preserve working forms, report the gap and stop |
| No own metadata, no top-level atom and no verified role | Confirmed ordinary absence: existing known-venv-then-consent path |
| No own metadata, top-level atom present, no expected role located and no verified role | Ambiguous same-name package/importer: do not execute presumed Atom module forms; read-only known-venv reuse may be attempted under existing safety checks |
| Ambiguous case has no healthy reusable known venv | Explain ambiguity and ask for resolution/known working forms; do not turn it into absence or enter the install recipe |

A successful help remains the authority for a working role, not metadata or a
path lookup. A negative path-based lookup is not allowed to erase own metadata,
a verified role, a partial candidate or an actual failure. Contradictory/unsupported
lookup evidence stops as ambiguous rather than being coerced into False.

## Numbered Behaviors

1. Retain the existing availability-first, supported-interpreter and verified-form
   shortcuts. Do not add a Python/metadata prerequisite when both entry points
   already work; do not rediscover established module or mixed forms.
2. Do not treat find_spec('atom') alone as proof that Atom CLI is installed or
   that either expected module exists. State the namespace/unrelated-package
   ambiguity beside the discovery instructions, not only in a footnote.
3. Query metadata without importing atom. Treat only PackageNotFoundError as
   missing registration. Other exceptions/nonzero results report their actual
   safe diagnostic and stop; no broad catch, install or fallback hides them.
4. Recognized own metadata preserves the installed/editable candidate path;
   actual missing-role help determines usability. Missing top-level import
   evidence despite own metadata is inconsistent and stops before known-missing
   module execution. Help failure never becomes an absence result.
5. Without metadata, retain source-only or mixed module forms when non-importing
   evidence covers all still-required roles and their help succeeds. Do not
   require distribution metadata for an already working form. Never execute an
   unrelated initializer merely to decide whether these candidates exist.
6. A verified role or partial candidate plus an unavailable/uncertain remaining
   role is a stop, not permission to install or switch environments to hide it.
   Report the verified forms and missing/uncertain role without inventing a
   module-error transcript for a command that was deliberately not run.
7. Complete ordinary absence follows the existing safe known-venv discovery;
   only confirmed absence and an absent safe destination can later reach the
   unchanged explicit installation-consent gate.
8. The ambiguous same-name case with neither role verified may check only the
   existing known Linux venv, read-only and with all original safety preconditions.
   It must not execute guessed selected-Python module forms, scan other envs or
   disclose implementation paths. Explain that original-interpreter identity
   remains unresolved rather than claiming it was repaired.
9. If that known venv is healthy and both helps pass, retain those absolute forms
   without reinstalling. If absent, ambiguous, partial, unsafe or failing, stop
   with the actual safe evidence. Ambiguity never authorizes provisioning, deletion,
   overwrite or an unchanged retry. A developer resolution is not install consent.
10. Within an existing known venv, use the same identity/role distinction only
    after ownership, non-symlink ancestor, supported-interpreter and prefix checks.
    Missing own metadata alone is not proof of damage if both module forms work;
    unavailable/uncertain roles in an occupied venv remain a preserved partial
    destination, never permission to install over it.
11. Preserve full relevant output/status, Windows setup-path opt-in and printed
    commands, both-role requirements, writer-refusal stops and unchanged init/
    baseline behavior. Do not print origins, inspect package internals, alter
    PATH/profiles or broaden command approvals to make discovery work.
12. Both shipped bootstrap copies remain byte-identical. No README/init-skill,
    runtime/test/schema/version/dependency, installed bundle or historical recipe
    changes are authorized by this spec.

## Error Handling

No new runtime exception, sentinel or fixed CLI error message is added.

| Condition | Required observable response |
|---|---|
| atom-cli registration absent | Expected discovery fact, not a failed installation |
| Same-named import without established Atom roles | Explain identity ambiguity; no fabricated command failure |
| Metadata/query/import-spec exception | Preserve actual safe diagnostic/status and stop |
| Own metadata with no top-level import | Explain inconsistent installation; preserve it and stop |
| Verified/partial setup cannot provide remaining role | Name the gap and verified forms; stop without fallback installation |
| Found help fails | Preserve the full actual relevant output and exit status; stop immediately |
| Known venv unsafe, partial or fails | Existing ownership/prefix/destination safeguards; no execution through unsafe ancestors or repair |
| Ambiguous selected interpreter plus absent known venv | Ask one focused resolution question; no install by default |

Only diagnostics actually produced may be reported as command output. Presence
facts are observations, not synthetic error logs or a passing onboarding receipt.

## Concurrency And Extension Points

Discovery is sequential per environment. No workers, shared mutable runtime state,
locks or persistent processes are introduced. Concurrent modification of an
installation remains unsupported: reuse assumes it stays stable until help checks;
contradictory observations stop. No new concurrency safety claim is made.

Future custom-loader/platform support extends the shared guidance only after
applicable evidence and approval. Do not add an abstraction or duplicate logic in
init/README as an extension mechanism. Intentional packaged mirrors remain until
the separate single-source packaging repair is proven and approved.

## Validation And Approval Boundary

After implementation approval, write the test/claim mapping BEFORE shipped edits.
Continue the accepted documentation-only adaptation: factual review, bounded
candidate boundary validation and existing documentation/package tests, not a
fabricated Go/Python production RED/GREEN cycle or root atom check.

Candidate validation: at most two local Python probe terminal invocations and five
minutes total, no models, installations, live Ubuntu/participant changes or known-
missing module help. Temporary controlled fixtures must be cleaned after capture.
Cover the prior real-install/namespace/unrelated controls, ordinary absence,
source-only roles without metadata, partial roles and mixed verified/missing-role
routing. Review metadata exceptions, actual-help-failure stops and unknown importers
as explicit semantic cases; do not claim they executed unless separately exercised.
If support for a required candidate cannot be established within that boundary,
stop with evidence instead of extending the loop or guessing. This budget does
not authorize provisioning, a new runtime resolver or extra reviewer invocations.

From tools, run existing coupled contracts after edits:

```powershell
python -m pytest tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup -q
```

Compare the two bootstrap files byte-for-byte; at root run:

```powershell
python tools\check_links.py
git --no-pager diff --check
```

Walk the decision table and all numbered behaviors against the final text. Reuse
prior Linux/install/README evidence within its original boundaries; do not repeat
unchanged unrelated suites or claim prose tests establish agent adherence. Paste
actual new outputs into a named validation section/artifact. A fresh live agent
trial and missing independent-review coverage remain separate decisions.

Approval authorizes only the two bootstrap documentation edits, their mapping and
the bounded validation above. Material drift, probe failure or unsupported required
forms stops and re-gates. No commit/push/merge, package/plugin refresh, extra model
turn, rehearsal restart or Phase 09 completion is authorized.

## Trade-offs Considered

| Option | Choice and reason |
|---|---|
| Keep generic top-level name as sufficient | Rejected: accepted controlled collisions demonstrate it is ambiguous |
| Require distribution metadata for every working form | Rejected: metadata absence alone cannot discard source-only or established module forms |
| Treat non-importing negative lookup as universal absence | Rejected: custom importers and shadowing are not established by the probe |
| Import unrelated atom to resolve child specs | Rejected: discovery should not execute a collision's initializer |
| Combined metadata/module evidence, explicit ambiguity | Chosen: uses observed signals without claiming universal identity or health proof |
| Permit read-only known-venv reuse from ambiguity | Proposed narrow exception: can recover the observed hidden-tool case without overwriting anything; no installation permission follows |
| Stop immediately on every same-name ambiguity | Conservative alternative: avoids guessing but retains an avoidable block even when the known safe venv can provide both roles |
| Install/overwrite on ambiguous evidence | Rejected: would disguise partial/working/custom environments as absence |
| New runtime resolver or comprehensive importer support | Out of scope: not needed for this guidance repair and not proven |

## Completeness And Remaining Assumptions

Established facts and assumptions are separate. Public API/signature additions are
none; no contradictory function sketches are included. Behaviors and decision
rows are independently reviewable; errors, concurrency and extension boundaries
are explicit. A diagram is unnecessary for this sequential table. Findings and
decisions record the evidence choice and proposed known-venv exception.

This draft is not approval, not proof of every candidate form and not a clean
review of the existing five-file repair. Opus's unread context and post-README-fix
independent coverage remain open; the previous two-reviewer budget is spent.
## Draft Verification Receipt

A direct read confirmed the full saved draft, including the decision table,
twelve behaviors, unsupported-case limits and implementation gate. Ran at root:

```powershell
python tools\check_links.py
git --no-pager diff --check
```

Actual output (both exited 0):

```text
checked 539 relative links across markdown files
all relative links resolve
git diff --check: exit 0
```

Compared current SHA-256 against the five pre-draft shipped-document hashes:

```text
All five shipped-document hashes unchanged during spec drafting.
```

No new runtime test, collision probe, model invocation or shipped edit was run
for this draft. Verification is artifact integrity, not candidate implementation
or live adherence proof.
## Explicit Implementation Approval Recorded

The developer selected exactly "Approve the two-file spec and bounded validation".
Approval covers only this spec's two bootstrap-reference edits, pre-edit mapping,
at most two local Python probe terminal invocations/five minutes, and the listed
existing checks. No extra models, installations, publication, refresh or rehearsal
are authorized. Implementation and candidate validation have not started. Preserve
the material-change/failure gate and the existing independent-review gaps.
## Implementation Reconciliation

Implemented exactly the two approved bootstrap references. The concrete inline
query reports distribution/package facts and optional module_candidates; null is
explicitly not queried. Registered candidates retain help-based verification,
while source-only candidates use non-importing lookup. The accepted read-only
known-venv exception and no-install-from-ambiguity boundary are present. No public
surface or material behavior changed from this spec; no new runtime API exists.

All twelve behaviors were walked against final text. The exact candidate passed
ten local observation cases before edits; the rendered query matched and ran
successfully in the second probe. Combined validation window: 37.654308 seconds.
Fourteen existing contracts passed; mirrors match. Full actual output and evidence
limits are in package-detection-repair-validation.md. Local implementation is not
acceptance or an independent review; all previously separate gates remain.
## Local Implementation Accepted

The developer selected exactly "Accept the local detection repair; keep further
work gated". The implemented spec and bounded validation are accepted locally;
independent review, publication, installed-content refresh and rehearsal remain
separate decisions. No Phase 09 completion or additional spend is authorized.
