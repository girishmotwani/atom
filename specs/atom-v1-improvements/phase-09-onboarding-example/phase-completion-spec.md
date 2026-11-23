---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-23"
status: "accepted-complete-with-stated-limits"
---

# Phase 09 Documentation Completion Spec

## Purpose And Evidence Choice

Finish the remaining reader-facing lifecycle guidance and reconcile the latest
accepted replay evidence. No new Go application, installer, command, experiment
or replay is needed. This is a documentation-only completion slice, not a new
phase architecture or a claim that the whole release is ready.

Reuse the [existing approved quickstart spec](quickstart-design-spec.md), its
[accepted approval-flow review](quickstart-approval-flow-review.md), and the
[now accepted user-flow result](uninterrupted-quickstart-report.md). The developer
explicitly accepted that replay without another run. Use factual review, command
help and existing documentation validation rather than manufacturing a Go POC,
TDD loop, uninstall experiment or additional model-review batch.

## Established And Still Unproven

Established: README links the standalone quickstart, documents requirements,
installation and updates, and distinguishes Python tools from plugin instructions.
The workflow opening distinguishes the full project route. The published
quickstart includes a complete expense request, expected outputs, failure
boundaries and real brief/report gates. The accepted replay reached those gates
and passed the three technical cases. Earlier source documentation reviews and
repairs remain valid within their snapshots.

The Phase 09 roadmap explicitly includes uninstall guidance, but README, docs
and the shared references currently contain no uninstall instructions. The
quickstart's validation link still points to the older restarted run rather than
the now accepted later replay. These are documentation gaps, not a failed replay.

On 2026-11-23, the same existing Copilot 1.0.107 used by the replay returned exit 0
from --no-auto-update plugin uninstall --help. Its own output states:

~~~text
Usage: copilot plugin uninstall <name>

Uninstall a plugin.

Removes a previously installed plugin and its associated skills.

Arguments:
  <name>
          Plugin name (plugin-name or plugin-name@marketplace-name)
~~~

Only help was executed. No plugin was removed. The current CLI documentation
also describes this syntax; do not extend that to a claim of tested removal on
every supported version. The Python distribution is separately named atom-cli
in tools/pyproject.toml and exposes atom and atom-write-artifact.

Still unproven: actual uninstall behavior across clients/platforms, novice
navigation, clean-machine/cold-authentication setup, arbitrary generated Go cases,
active-time performance and the missing recorder/post-session inventory details.
None is newly promised or silently converted to a passing measurement.

## Public Surface And Numbered Requirements

1. README gains a short uninstall section adjacent to its existing installation/
   update guidance. Show copilot plugin uninstall atom@atom for the selected
   client/profile. Tell isolated-profile users to select the same profile used
   for installation rather than accidentally target the default installation.
2. Distinguish plugin removal from the separately installed Python command tools
   and repository-local artifacts/instruction bundles. Do not promise complete
   project rollback. Keep specs, POC evidence and project work intact; provide no
   recursive deletion or automatic cleanup commands. This change performs no
   uninstall and introduces no new Python removal or migration procedure.
3. Change only the quickstart's final validation-notes link target to
   uninterrupted-quickstart-report.md. Preserve every setup/request/continuation/
   result code block, all generated-output expectations and both approval gates.
   Do not add recorder methodology or repeated evidence narration to the tutorial.
4. Append a current evidence reconciliation to quickstart-design-spec.md. Retain
   its historical approvals and older scope limits as history; explicitly name
   this completion slice. State the accepted experienced-user replay and remaining
   observation/platform limitations without upgrading earlier failed attempts.

No new exported API, configuration schema, concurrency behavior, runtime state,
installation action, tool permission or command alias is introduced. There are
no signatures or goroutines to specify. Existing helpers/skills remain unchanged.

## File Scope And Non-Goals

Source changes: README.md, docs/quickstart.md (one link only), and
quickstart-design-spec.md (append-only evidence/scope reconciliation).
Keep normal findings/decisions updated. The accepted replay report already records
the developer's decision; it needs no further technical experiment.

Do not change tools, tests, packaged/canonical skills, source/version pins,
generated trial files, original report verdicts, the release version, Git state
or runtime phase registration. Do not mark Phase 09 done until the completion
gate is accepted. No publication or Phase 13 execution is authorized here.

## Validation And Gate

After approval, compare the uninstall syntax with the captured pinned-client
help, check that selected-profile and separate-tool wording does not imply a
full rollback, and review all four requirements against the actual diff.
Verify that the quickstart's fenced blocks and all other text except its one
link are byte-identical after LF normalization. Run the existing
python tools\check_links.py and git diff --check; read the written source.

No runtime suite is required for this prose/link-only change. The original
module atom check output remains in the accepted replay report with skipped
test/race stages disclosed. A fresh product release requires its own Python,
packaging/platform and release checks, not reused counts represented as fresh.

Present the completed documentation and a concise Phase 09 task-to-evidence
checklist for acceptance. Approval of this spec authorizes only the described
three-file documentation change and checks, not phase closure, another replay,
model reviewers, commit, push, PR, merge, tag or release.

## Spec Approval: 2026-11-23

Developer selected exactly: "Approve the documentation-only completion spec".
Implement the four requirements in the named three documents, keep normal
findings/decisions updated, run the specified documentation checks, and present
the Phase 09 completion checklist. No replay, uninstall, runtime change, model
review batch, publication or phase closure is approved by this spec acceptance.

## Implementation And Verification: 2026-11-23

Implemented the three approved documentation changes. README now documents the
selected-profile plugin uninstall and distinguishes separate Python tooling and
project artifacts. The quickstart changes only its evidence link. The existing
quickstart spec has an append-only acceptance/scope reconciliation. No command
was executed to uninstall anything, and no new replay or runtime work ran.

Actual verification output:

~~~text
PASS: quickstart differs only in the approved evidence link; all 6 fenced blocks unchanged
PASS: README changes only the uninstall guidance; profile, separate tools and project retention are explicit
PASS: original spec prefix, workflow, runtime, skills and plugin files preserved
checked 646 relative links across markdown files
all relative links resolve
~~~

git diff --check exited 0. Read the complete three-file source diff against the
four numbered requirements; no unresolved issue in this documentation slice.
The command-help validation is not a tested uninstall or universal-client claim.
No runtime/TDD/race/coverage success is inferred from these documentation checks.

## Phase 09 Task-To-Evidence Checklist

| Roadmap task | Evidence and bounded disposition |
| --- | --- |
| Prerequisites, installation/update/uninstall and entry-point choice | README Try Atom/Getting started/Requirements and adjacent lifecycle sections; docs/quickstart.md Before you start and isolated setup; new uninstall syntax verified with the actual replay client's help |
| Public worked Go example with real commands, outputs and failure boundaries | Published quickstart request, fixture and expected results; uninterrupted-quickstart-report.md contains inspected original vet/build/execute, direct exits 0/1/1, exact output/error streams and real approvals |
| Standalone versus full-pipeline guidance | README Try Atom and standalone review entry; docs/workflow.md opening; quickstart states no onboarding/full project pipeline and stops at report acceptance |
| Stated-environment replay and duplication/version limits | Accepted replay from fresh Atom locations on existing Ubuntu WSL; preparation records client/tooling/plugin identities. Earlier candidate-delivery-report.md identifies the duplicate local-loader hazard; the documented quickstart uses an isolated marketplace installation, not mixed local live-loading. Existing README warns against --plugin-dir. Other platforms, clean OS/auth/cache, newcomer/timing and missing post-session recorder/inventory measurements remain unproven |

**Recommendation:** accept Phase 09 as complete for its documented and accepted
Ubuntu/WSL experienced-user scope, retaining all listed limitations. This is not
an independently tested newcomer study or a clean-machine/platform certification.
The developer explicitly accepted the existing replay; no further replay is
required to repair observer bookkeeping. Original failed/interrupted trials remain
historical evidence, not newly passing runs.

The completion gate is pending. No roadmap completion boxes, runtime phase state,
commits, pushes, PRs, merges, tags or releases have been changed by this report.
After acceptance, reconcile the remaining Must-phase backlog before proposing
release-readiness work; website/distribution phases 10-11 remain deferred.

## Phase Completion Accepted: 2026-11-23

Developer selected exactly: "Accept Phase 09 completion with the stated limits".
Phase 09 is complete within the documented, accepted Ubuntu/WSL experienced-user
scope. This supersedes pending/open statements above and authorizes recording
the roadmap task completion, not a broader compatibility/newcomer certification.
Keep all original recording/timing/platform limitations and historical trial
verdicts. No replay, publication or release is authorized. The remaining Must
backlog must still be reconciled before any release-readiness claim.
