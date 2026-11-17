---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-16"
status: "approved-for-three-documentation-edits"
evidence: "standalone-quickstart-report.md"
---

# Standalone Quickstart Documentation Spec

## Purpose And Scope

Give a Go developer one short path from an isolated Atom installation to a real
expense-summary POC, without adopting the project pipeline or reading its manual.
The outcome is disposable proof, not a production expense application.

This is the documentation-only slice explicitly authorized after acceptance of
[the bounded replay evidence](standalone-quickstart-report.md#evidence-gate-accepted).
It is not the final design of every Phase 09 task or a claim that Phase 09 is done.

## Established Before Design

- Fresh public atom-cli 0.1.0 and marketplace plugin 0.2.0 installation worked on
  existing Ubuntu WSL with Copilot CLI 1.0.107, Go 1.22.2, Python 3.12.3 and git
  2.43.0. All 658 plugin files matched public commit
  5bb33cbe2c835382b5ccda840c5268321b24ac0b and remained unchanged afterward.
- The installed POC path generated its brief and separate Go module, ran vet/build/
  execute, captured direct process exits and stopped for its report. It needed no
  root go.mod, .atom project state, phases, design/TDD or extra agents.
- The fixture produced food 20.00 and travel 3.75. Invalid final amount and missing
  file each exited 1 with diagnostics and empty stdout; direct executable evidence
  is separate from the go run wrapper. See the report for the exact saved streams.
- The operator estimated 4-5 active minutes and reported eight specific-command,
  session-only permission approvals. These are observations, not promises.

## Still Assumed Or Unproven

- Independent navigation was not isolated: the setup session advised at the gates
  and supplied continuation wording. The new page will include that missing
  navigation explicitly, but its final wording has not been independently replayed.
- Human-readable trial directory names and a resolved existing Copilot executable
  may replace private rehearsal paths without changing the command contract. This
  is a documentation translation, not evidence that every PATH/client setup works.
- Other platforms/versions, cold authentication and a clean OS were not tested.
  The existing CLI cache was shared; no new cache-isolation promise is introduced.
- Python source installation was pinned; the public marketplace can subsequently
  advance. Its plugin version alone does not guarantee the recorded source bytes.

## Reader Surface And Files

| File | Sole change |
|---|---|
| README.md | Make Try Atom lead to the standalone quickstart; retain links to general setup and the full workflow rather than duplicate their instructions |
| docs\quickstart.md | One page: prerequisites, fresh isolated setup, expense request, approval/continue/stop instructions, output checks and evidence limits |
| docs\workflow.md | Qualify only the opening read-before-first-run guidance as the full-project walkthrough and link the standalone alternative |

No new command, skill, Go API, runtime configuration schema or exported symbol.
Keep the rest of the README/workflow, canonical and packaged skills, Python tools,
tests and the replay workspace unchanged. Aim for roughly 150 nonblank lines in
the quickstart; that is an editorial bound, not a measured usability threshold.

## Reader-Facing Requirements

1. The README links the standalone outcome before suggesting project onboarding;
   the full workflow remains separately available and is not required reading.
2. The page labels commands as Ubuntu/Linux terminal commands and names the exact
   observed environment/source. General documented minima are not presented as a
   tested compatibility matrix; other setups use existing setup guidance.
3. Setup explicitly distinguishes plugin instructions from Python command tools.
   Reuse the observed public marketplace commands and source-pinned venv install,
   with a fresh dedicated profile and sibling workspace. This is a deliberately
   separate trial install, not permission to overwrite or silently replace healthy
   existing tools. Check all chosen destinations for files and symlinks first.
4. Existing supported Copilot, Go, Python with venv, git and ordinary authentication
   are prerequisites, not installed by the page. Resolve and verify the actual
   Copilot executable rather than reproduce a private rehearsal-tools prefix.
   Keep the shared-cache disclosure and supported COPILOT_HOME/no-CLI-update
   controls; do not claim the old client prevents plugin updates.
5. Setup settings apply only in the reader's dedicated terminal or child process.
   No shell-profile/global PATH, HOME, default Copilot profile, login or credential
   copy is prescribed. Both Atom command help checks must succeed before the task.
6. The request keeps the approved question and supplied category,amount fixture
   verbatim, expected food 20.00 / travel 3.75, last-row oops and missing-file cases,
   separate process-exit evidence, one disposable POC and the report stop boundary.
   It does not prewrite Go source/tests or ask for init/start/build or project state.
7. Explain that a POC invocation may first use discovery solely to prepare its brief.
   Read that brief and approve only if it matches; then give the explicit observed
   continuation request in the same session: proceed with the approved brief,
   scaffold/write/execute the POC, capture evidence and stop at its report gate.
8. Distinguish tool-permission prompts from artifact gates. Approve only understood
   displayed actions; no all-tools, unrestricted-path or persistent approval is
   required. Read/accept or reject the report explicitly; acceptance does not start
   planning, design, TDD, review or shipping. End this standalone task there.
9. Show actual success stdout as two lines, food 20.00 then travel 3.75, with exit 0
   and empty stderr. Name the generated source, fixtures and report locations in the
   reader's workspace so the useful result is inspectable and rerunnable.
10. Show the observed invalid-amount/missing-file diagnostics as examples, with exit
    1 and empty stdout. Explain that go run adds an exit-status line; its wrapper
    output is not the direct executable's diagnostic/exit. Retain the expected
    fixture/behavior contract without promising identical generated source or
    platform-dependent error wording in every future model run.
11. State plainly that the observed result was assisted and bounded. Do not promise
    four-minute setup, fewer prompts, newcomer usability, production readiness,
    clean-machine installation, universal model adherence or all-version support.
    Link the accepted report for provenance rather than copy private recordings.
12. Ship only the three documentation edits and existing artifact logs. A worked
    example means the observed request, fixture, commands, outputs and failure
    boundaries; no spike source is promoted to production or newly packaged here.

## Failure And Stop Handling

- Missing prerequisite, unavailable authentication, unsupported client/alias,
  existing destination, failed installation/help or writer refusal: preserve the
  setup and actual diagnostic; stop. No sudo, system-pip override, new interpreter,
  automatic retries, guessed aliases, broad permissions or alternate writer.
- No root go.mod: expected for the empty standalone workspace, not a green project
  baseline. Do not initialize a root module or phase state to silence that probe;
  the POC's separate module carries its actual vet/build/run evidence.
- Negative fixture exit 1 is expected acceptance behavior, not a setup failure or
  Refuted experiment. Unexpected totals, success output on failure or missing
  evidence must not be described as a successful result.
- The public skill may drift or request unrelated lifecycle work. Stop/disclose;
  do not instruct readers to modify installed skills or ignore an approval gate.

## Concurrency And Extension Points

No goroutines, locks, background helpers or concurrent-use API are introduced.
The example uses one interactive session and fresh destinations; it is not safe to
run two copies against the same trial directory. Evidence is not a concurrency
or race claim. Future platform examples belong in separately evidenced additions,
not extra branches in this page. Existing full-pipeline guidance stays authoritative
for later production work; this spec adds no new route or workflow-policy change.

## Trade-offs

| Choice | Reason |
|---|---|
| Separate compact page plus small navigation edits | Avoid another onboarding manual or conflicting repeated setup recipes |
| Keep fresh profile/venv semantics; remove private harness paths and recording machinery | Reuse the proven install boundary without shipping a research harness as the tutorial |
| Keep the existing POC entry and both artifact gates | The observed path already works without phases; no Phase 04 router implementation is needed |
| Include explicit continuation wording | Addresses the observed gate-navigation assistance without claiming it was already independently proven |
| Preserve limitations rather than run another experiment now | The developer approved bounded evidence reuse for documentation, not another model/install attempt |

## Validation And Gate

After approval, implement as factual documentation work, not artificial Go TDD.
Compare every published command/flag, fixture, output, source/version and claim to
[the frozen recipe](standalone-quickstart-recipe.md),
[installation evidence](standalone-quickstart-preparation.md) and accepted report.
Check the new Ubuntu shell blocks with bash -n using UTF-8 LF bytes, not Windows
text-mode CRLF conversion. Run the existing python tools\check_links.py and scoped
git diff --check; read the actual diff for all twelve requirements. These checks
verify syntax/text/links, not an independently replayed final page.

No installs, model sessions, Go runs, root atom check, new test tooling or package
changes are authorized for this documentation implementation. No numerical
usability result or Phase 09 completion is gained by text checks. Publication,
commit/push/PR and a final live-document replay remain separately authorized work.

Approval of this exact spec authorizes only the three documentation edits and
normal findings/decisions updates, followed by their validation and review gate.
No public documentation has been edited during this spec turn.

## Spec Approval: 2026-11-16

Developer selected exactly: "Approve the spec and three documentation edits".
Authorize docs\quickstart.md, the README Try Atom entry and the workflow opening
clarification, plus normal evidence/findings/decisions updates and the specified
factual/link/syntax/diff checks. No runtime, skill, package, dependency, generated
Go source, installation, model session, publication or phase-completion work.
Stop this spec-gate turn before implementing the newly approved documentation.

Spec preparation validation:

```text
checked 572 relative links across markdown files
all relative links resolve
```

Scoped git diff --check exited 0. File reads verified this spec; README/workflow
had no diff and docs\quickstart.md did not exist at the gate. These are document
checks, not a fresh Go run or independent replay of the proposed page.

## Reader-First Presentation Correction: 2026-11-17

The developer requested removal of unnecessary steps-performed information from
the quickstart in favor of a new-user experience. Keep the existing technical
contract, setup commands, fixture, negative exits, isolation and real approval
boundaries. Present the page as an outcome followed by setup, request, approval
and verification, using direct instructions instead of a replay narrative.

For requirements 2, 10 and 11, detailed tested-version/source inventories,
go-run wrapper analysis and replay methodology/limitations remain in the linked
accepted report and its evidence rather than being repeated inline. Keep the
Linux/Bash prerequisite boundary, executable negative checks and no production
claim in the tutorial. Requirement 6 allows clearer prompt wording with the same
question, exact fixture, expected results, separate process evidence and scope.
No compatibility or independently validated usability claim is added. This is
presentation reconciliation for the requested editorial correction, not approval
of a new installation path or experiment. The existing final-page replay limit
and implementation acceptance/publication boundaries remain unchanged.
