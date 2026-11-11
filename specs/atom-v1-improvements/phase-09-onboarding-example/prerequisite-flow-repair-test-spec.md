---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-10"
status: "local-contracts-validated-agent-adherence-unproven"
design_spec: "prerequisite-flow-repair-spec.md"
---

# Onboarding Guidance Repair Test Spec

## Method And Approval

The developer selected exactly "Approve the spec and implement the guidance repair".
Implement the approved five-document scope. No production runtime changes are
planned: apply the spec's factual/semantic review and existing packaging/document
checks, not a fictional production RED/GREEN cycle or new prose-presence tests.
Read the TDD skill and discipline references before edits. Initial git status
showed only prior phase-evidence changes; both canonical/packaged pairs matched.

## Behavior Coverage

Each row maps the corresponding numbered behavior in the approved spec to its
appropriate validation. Semantic review checks the instruction, not whether an
agent actually follows it. Planned checks are not reported as passing in advance.

| Spec behavior | Case and validation |
|---|---|
| 1 | Supported, unsupported, missing and conflicting active identity: semantic review requires actual session context, existing minimum, one clarification/consent question, no substitute binary or auto-update. New live enforcement remains untested. |
| 2 | Missing Go: instruction uses availability data and asks before init; no provisioning/version/build duplication. Existing init tests cover unchanged backend contracts, not compliance with this new instruction. |
| 3 | Both forms established versus unresolved entry points: review no repeated discovery; accepted Windows receipt covers the ordinary resolution/help mechanism. |
| 4 | Found entry points: accepted four exit-0 helps; review exact-error stop for a failing found role. No new failure-injection claim. |
| 5 | No system Atom package: accepted Ubuntu presence result; review interpreter selection before invocation, absence as data, and unexpected-error stop. |
| 6 | Present package, mixed roles or partial package: review fallback only for missing roles, retention of working roles and no reinstall-over-broken rule. No new partial-package execution claim. |
| 7 | Hidden healthy known venv: accepted Ubuntu ancestry/prefix/helps; review preserve-and-stop for unsafe/partial destinations and no arbitrary search. |
| 8 | Truly absent prerequisites/destination: review explicit consent/wait and preservation of old Linux provisioning/configuration constraints; accepted install reports remain limited to their own conditions. |
| 9 | Hidden Windows scripts: existing test_onboarding_documents_one_time_path_setup and test_readme_documents_the_setup_command_and_session_limitation, plus semantic opt-in/printed-command review. |
| 10 | Next beat already has working forms: review record-once/reuse instructions and actual-context-change handling. No automatic new runtime state. |
| 11 | Found-command error or writer refusal: review originating status/full safe diagnostic/stop, no head truncation or invalid-target probe. Prior guard evidence is reused; no new agent-compliance claim. |
| 12 | First init, valid no-op, corrupt setup and empty-module failure: existing test_onboarding.py plus review retained receipts/approval/source boundaries. No new init against the stopped participant module. |
| 13 | Completed init versus no-op and unknown/rejected alias: review concise forms/baseline report and appropriate available-skill handoff, no guessed alias or silent skill substitution. |
| 14 | README minima/consent/history and both source pairs: existing plugin/document tests, explicit byte comparison, semantic README review, link and whitespace checks. |

## Executable Checks

From tools:

```powershell
python -m pytest tests\test_onboarding.py tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

At root: python tools\check_links.py, git diff --check, and SHA-256 byte-parity
comparison of skills\init\SKILL.md and skills\atom\references\bootstrap.md with
their tools\atom\assets counterparts. Preserve full actual output in a validation
artifact. Source diff must contain only the five approved shipped documents plus
phase evidence; no tests, runtime source, schemas, versions, shell script files,
installer runs or installed-plugin updates.

## Redundancy Audit And Limits

No Go cases are applicable: no Go production code, interfaces, nil/zero parameters,
cancellation, shared memory or runtime arithmetic changes. No tests were removed
or weakened. Do not write tests of shutil/importlib language behavior or exact
prose phrases; the accepted real-environment check covers the selected primitive
boundary and existing tests cover current packaging/document contracts.

These checks cannot establish installer safety in new variants, all-client alias
support, actual consent/refusal compliance, fresh-user usability or final Phase 09
success. A later observed trial needs separate approval and frozen delivery/client
conditions. Existing baseline failures stay failures; no placeholder Go code.

## Execution Recorded

The planned selector passed 34 tests; the four directly affected documentation
contracts passed again after final wording refinements. Parity/link/whitespace and
scope checks passed. Full original output is in prerequisite-flow-repair-validation.md.
Semantic checks review the final instructions only; remaining live-agent limits
are unchanged. No production RED/GREEN cycle or new compatibility proof is claimed.
## Pre-Edit Post-Fix README Mapping

After two-model review, the developer approved README-only factual correction and
Windows deferral. Map behavior 14 before these edits: missing system prerequisites
must be supplied, missing Atom commands can reach guided consent only on Linux
with explicit absence and an absent safe destination, and other platforms need an
agreed isolated setup. Compare all four changed passages with init/bootstrap;
retain hidden-tool reuse, broken/unsafe stops and historical evidence wording.
No new behavior is designed. Windows behavior 9 is preserved, with its adjacent
verification gap explicitly deferred rather than silently fixed or marked safe.

Run the existing README setup/session-limitation case in test_pathsetup.py,
links and git diff --check; preserve all four bootstrap/init hashes. The existing
case checks two unchanged literals only. Semantic policy correctness comes from
factual review, not that literal check; no new prose test or runtime TDD is claimed.
Results will be recorded in the named post-fix review report after execution.
## Post-Fix README Execution

All four approved factual-correction passages were read against the existing
policy; no behavior 14 policy change was required. The exact existing README
case passed 1 test in 4.61s. Links (545), whitespace and all four unchanged
bootstrap/init hashes passed. Actual full output/new README hash are retained in
prerequisite-flow-repair-post-fix-review.md. The weak existing literal check is
not claimed as semantic or live-adherence proof. No source test was changed.
Windows behavior 9 remains unchanged with its verification risk explicitly deferred.
