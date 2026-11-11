---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
status: "post-fix-local-correction-accepted-windows-minor-deferred"
scope: "five shipped onboarding documentation changes against HEAD"
---

# General Onboarding Guidance Repair: Bounded Pre-PR Review

## Current Disposition

The fresh independent Opus/Terra review returned two Minors and no Blocker/Major,
with complete required context reported. The developer approved README wording
correction and explicit deferral of the unchanged Windows handoff risk. The four
README passages are now corrected and locally validated: 1 existing affected case
passes, 545 links resolve, whitespace is clean and bootstrap/init hashes remain
unchanged. No independent review of the new README hash is claimed.

The [post-fix report](prerequisite-flow-repair-post-fix-review.md) preserves both
original responses, reviewed hashes, fresh correction receipts, explicit Windows
deferral and next-step proposal. The local correction is explicitly accepted.
Original partial-review history remains unchanged rather than retroactively clean.

No extra model, runtime/PATH edit, publication, installed refresh or rehearsal is
authorized or performed. Phase 09 remains incomplete; the next delivery and observed
rehearsal steps require their own explicit decisions.

## Original Review Outcome And Approval Boundary (Before README Fix)

Both approved independent reviewers returned findings. The merged result is one
Major README consistency finding and one Minor package-detection finding. Neither
has been fixed, deferred or rejected. Developer triage is pending.

This is NOT a clean or fully completed review: Opus disclosed that it did not
read the entire README or discovery report. Terra reported reviewing all five
files and the four context artifacts. Both reviewed the canonical instructions
and accounted for their byte-identical packaged mirrors. The full-context-per-
reviewer checklist remains incomplete; the missing reads are not silently credited
or supplied by the author's targeted checks. The two-invocation budget is spent.
No extra model turn, probe, retry, agent or automatic follow-up was launched.

The developer approved exactly "Approve the bounded two-model review", then
selected "claude-opus-5.5 + gpt-6.1-terra" for two independent read-only reviewer
agents, one per model. The author is gpt-6.1-sol. Native review was not used because
its availability probes would add model calls. No repository model defaults were
changed. These were two agent invocations, not a claim about their internal model
request counts or monetary cost.

No production edits, install, tool refresh, commit, push, merge or rehearsal ran.
The stopped rehearsal remains Inconclusive and Phase 09 remains incomplete.

## Reviewed Snapshot And Context

Compared HEAD to the working tree for these five shipped files only:

| File | SHA-256 |
|---|---|
| README.md | 76935B30C29D1AA1BB88A6CC1DC9136EDD8CC9246AE1C22C9A075E238906E5E7 |
| skills\init\SKILL.md | 15E4169B5BE2896DD3D3802129B18D6BC81C48E9C2E956F48CD199AB23AF52F8 |
| tools\atom\assets\skills\init\SKILL.md | 15E4169B5BE2896DD3D3802129B18D6BC81C48E9C2E956F48CD199AB23AF52F8 |
| skills\atom\references\bootstrap.md | E962C45C44A76A223647328F5861DA402EF4680C2771B4BEC9C8DE3FC60DEF33 |
| tools\atom\assets\skills\atom\references\bootstrap.md | E962C45C44A76A223647328F5861DA402EF4680C2771B4BEC9C8DE3FC60DEF33 |

Context supplied to both reviewers: [approved spec](prerequisite-flow-repair-spec.md),
[test mapping](prerequisite-flow-repair-test-spec.md), [discovery evidence](prerequisite-flow-repair-report.md)
and [accepted validation](prerequisite-flow-repair-validation.md), plus root AGENTS.md.
Historical phase journals were not the diff under review. Manual platform recipes
remain outside the approved redesign scope, but a directly coupled README promise
is expressly in scope under spec behavior 14.

## Existing Toolchain Evidence And Limits

The accepted validation contains actual output for 34 passing focused Python/
onboarding/plugin/documentation cases and four passing final documentation cases,
531 resolving relative links, mirror parity and whitespace checks. These are
reused results, not newly executed tests. The init/bootstrap hashes still match
the accepted validation. Source hashes were verified again after both reviews.
No source bytes changed during review. A fresh git diff --check exited 0.

There is no root Go module. Go build/vet/test/race/fmt checks are inapplicable,
not passed. No artificial module or nested spike was used as a substitute gate.
No tool exclusion is claimed for semantic correctness, package-name collisions,
active alias registration, failing-help routing or actual agent adherence.

The Major finding means the earlier semantic claim that README automatic-install
promises were corrected was incomplete. Passing text/packaging checks did not
establish full compliance with all fourteen spec behaviors.

## Merged Findings

### Major: The README Run It Section Still Contradicts The New Onboarding Flow

- Agreement: 2/2 reviewers identified the automatic-install contradiction. Opus
  rated it Major and Terra Minor; this report retains Major because an explicit
  approved repair requirement remains unmet in the primary usage handoff, not
  because both reviewers agreed on severity.
- Location: README.md:602-609, in "Run it". Terra's finding header cited line 666
  but its body identified the unchanged Run It promise. Opus provided the direct
  range; targeted parent reads confirmed the same paragraph.
- Evidence: the paragraph still says the atom command "installs itself the first
  time a beat needs it" and "Neither is yours to do by hand." New front-page and
  manual-install text instead require consent. Spec behavior 14 expressly forbids
  automatic-install promises. This unchanged paragraph is a missed directly
  coupled repair obligation, not an unrelated pre-existing issue.
- Breaks when: a reader follows Run It and expects automatic installation rather
  than missing-tool guidance and a consent stop, including on platforms where
  the documented automatic Linux bootstrap is not applicable.
- Related handoff concern: Opus alone (1/2) noted the adjacent unqualified
  /atom:start handoff, while the new quickstart/init use appropriate discovery
  and qualify unverified aliases. The active-client alias rejection remains
  unexplained; this review does not prove that the alias fails everywhere.
- Minimal suggested repair: align this paragraph with healthy-tool reuse and
  consent-gated installation; align or qualify the adjacent handoff without
  inventing aliases or redesigning the manual platform recipes. Correct the
  earlier semantic-validation claim by recording this missed paragraph.
- Triage: OPEN. No silent fix, deferral or rejection. Developer decision required.

### Minor: A Top-Level Atom Package Is Not Proof That Atom CLI Is Installed

- Agreement: 1/2, Opus only. Terra did not independently report it.
- Locations: skills\atom\references\bootstrap.md:84-90, with routing at 125 and
  157; identical locations in tools\atom\assets\skills\atom\references\bootstrap.md.
- Evidence: find_spec('atom') being non-None permits role-help calls. Any failed
  help then stops before known-venv reuse. An unrelated installed atom package
  or a repository-local atom namespace can satisfy that top-level-name check
  without providing Atom CLI's modules. The reviewed example tests name presence,
  not distribution identity or successful command roles.
- Breaks when: the selected interpreter resolves a colliding atom package but
  not atom.cli, while a healthy known Linux venv exists. The prescribed module
  help fails and the workflow stops rather than reaching that healthy venv.
- Evidence limit: this is a statically identified case, not an executed collision
  reproduction. The discovery receipts did not cover it. An interpreter/path
  collision may itself warrant the existing safe stop, so the intended boundary
  must be decided rather than automatically weakening genuine-error handling.
- Suggested next step: validate the collision boundary before changing guidance.
  Opus suggested atom-cli distribution metadata as a discriminator; that is NOT
  an approved design or proven replacement. Any solution must preserve working
  editable/module forms, actual import-error stops and no reinstall-over-working-
  tooling behavior. Metadata presence alone does not prove module help works.
- Triage: OPEN. No runtime or guidance change approved for this case.

## Participation And Remaining Checklist

| Reviewer | Result | Context limitation |
|---|---|---|
| claude-opus-5.5 | One Major and one Minor | Read README lines 1-60 and 400-760 plus the diff, not its entire content; grepped rather than fully read the discovery report |
| gpt-6.1-terra | One Minor, merged with README finding | Reported all five files, all four context artifacts and root AGENTS.md reviewed |

Both models differ from the author and each other. Findings are deduplicated and
severity-ranked; the single-model Major assessment and Minor finding are retained
on their own merits. Full-context completion, developer triage and any fixes /
post-fix validation remain open. No third reviewer invocation is authorized.
The recommended immediate triage is to fix the README consistency miss; the
collision finding requires its own evidence/intent decision before an edit.

## Original Reviewer Responses

The following are the returned reviewer text, preserved independently of the
merged severity/triage. Their individual claims and limitations remain theirs.

### GPT-6.1 Terra

```text
**Scope:** Reviewed the five requested files against HEAD, the four prerequisite-flow artifacts, and root `AGENTS.md`. Both packaged mirrors match their canonical files.

## Issue: README still promises automatic installation
**File:** `C:\Users\gimotwan\work\atom\README.md:666`
**Severity:** Medium (Minor)
**Problem:** A reader following “Run it” is told at line 601 that Atom installs itself when needed. That contradicts the new guidance that installation requires consent and healthy tools are reused.
**Evidence:** The conflicting promise remains alongside the changed consent wording at lines 23–26 and 666–668.
**Suggested fix:** Align the “Run it” promise with the consent and reuse guidance.

**Limitations:** No tests or live onboarding were run. Failing-help routing, alias acceptance, and agent adherence remain unverified. Phase 09 remains incomplete.
```

### Claude Opus 5.5

```text
## 1. Scope and context reviewed

I compared HEAD against the working tree for these five files only. All five hashes match the frozen values.
- **`C:\Users\gimotwan\work\atom\README.md`** (76935B30…): I read the full diff, lines 1–60 and lines 400–760 completely. That covers Try Atom, install, onboard, update, Run it, If setup goes wrong and Requirements.
- **`C:\Users\gimotwan\work\atom\skills\init\SKILL.md`** (15E4169B…): read in full.
- **`C:\Users\gimotwan\work\atom\tools\atom\assets\skills\init\SKILL.md`**: same SHA-256 as the canonical init skill, so the canonical findings (none) cover it.
- **`C:\Users\gimotwan\work\atom\skills\atom\references\bootstrap.md`** (E962C45C…): read in full.
- **`C:\Users\gimotwan\work\atom\tools\atom\assets\skills\atom\references\bootstrap.md`**: same SHA-256 as the canonical bootstrap, so the bootstrap finding below applies to it too.

Contract and context: I read the repair spec, test spec and validation artifact in full. I only grepped the report for specific claims. I also read root `AGENTS.md` and `tools\pyproject.toml`, the latter only to confirm the distribution and top-level package names.

## 2. Findings

### Major: README "Run it" still promises automatic install and a `/atom:start` handoff
**File:** `C:\Users\gimotwan\work\atom\README.md:602-603`, with `README.md:606-609` following.
**Problem:** This unchanged paragraph still says the `atom` command "installs itself the first time a beat needs it" and "Neither is yours to do by hand." It then sends users to `/atom:start` as the entry point.
- The changed text says the opposite: line 25 says onboarding "asks before installing missing tools", lines 663–665 cover consent-gated install, and the bootstrap reference requires an explicit consent question and a wait.
- Spec behavior 14 requires the README to avoid "automatic-install … promises". Behavior 13 replaces the unverified start alias with the discover handoff, which the changed Try Atom text now follows.
- The validation artifact (line 38) claims the README "corrects automatic-install … expectations". For this paragraph, that claim is false.

**Breaks when:** a user reads "Run it" (the section after install/update) and expects installation without being asked. They then hit the consent stop, or the stop-and-agree path on non-Linux platforms. "Neither is yours to do by hand" also contradicts the "Installing the `atom` command by hand" section 60 lines later. The README now gives two handoffs: `/atom:discover` in Try Atom and the init skill, `/atom:start` here.
**Evidence:** the README lines above, spec line 138, and validation line 38. None of the repair artifacts mention this paragraph, so it was missed rather than deliberately left out of scope.
**Suggested minimal fix:** reword lines 602–603 to match line 25: tools are reused when healthy and installed only with consent. Either align the `/atom:start` recommendation with the discover handoff or state that it is the documented alias, with the same alias caveat. Alternatively, record a decision that leaves it out of scope and correct the validation claim.

### Minor: the package-presence query matches any top-level `atom`, not Atom's tooling
**File:** `C:\Users\gimotwan\work\atom\skills\atom\references\bootstrap.md:84-90` (gating also at lines 125 and 157). The packaged mirror has the same text at the same lines.
**Problem:** `find_spec('atom') is not None` is now the single gate between "explicit absence" (which allows Step 3 known-venv reuse and the Step 4 install offer) and "present, so any help failure is a stop". Atom's distribution is `atom-cli`, but its import package is the generic top-level `atom` (`tools\pyproject.toml`: `name = "atom-cli"`, `include = ["atom*"]`). Two ordinary cases return `True` when Atom is not installed:
- the unrelated PyPI package `atom` (nucleic/atom, an enaml dependency) is installed in the selected interpreter;
- the target repository has an `atom/` directory. `python -c` puts the current directory on `sys.path`, and a bare directory resolves as a namespace package.

**Breaks when:** either case happens on Linux. The query returns `True`, `python3 -m atom.cli --help` fails with `No module named 'atom.cli'`, and line 88 plus line 125 classify that as a non-absence failure and stop. Step 3 then never runs, so a healthy `$HOME/.local/share/atom-cli/venv` is not reused and the install offer never appears. The new text routes this to a hard stop on a false "present" signal, where the old "diagnostics explicitly establish absence" wording left the call to judgment.
**Suggested minimal fix:** check for Atom's own distribution, e.g. `importlib.metadata.distribution('atom-cli')`, treating `PackageNotFoundError` as absence. Or require both `find_spec('atom')` and the `atom-cli` distribution before treating the package as present. Either way, keep the existing rule that unexpected exceptions stop.

## 3. No other findings

The init skill (both copies) has no consequential issues. The rest of the bootstrap reference holds together:
- missing, hidden-but-healthy and broken/partial tooling are routed separately;
- tools are resolved before they are run, and Git/venv/ensurepip are checked before the consent question;
- active-session identity is required rather than another binary's version;
- writer refusals and nonzero results stop;
- verified forms are recorded once and reused;
- the existing Linux installer safeguards are unchanged.

## 4. Limitations

- Per scope, I ran no tests, installs or scripts.
- I did not read the README outside lines 1–60 and 400–760 beyond the diff hunks, and I relied on the grep that showed no other relevant `/atom:start` or minimum statements.
- I did not read the full repair report, the prior bootstrap reports or the historical rehearsal records.
- Live agent adherence, failing-help routing and client alias behavior were not exercised. Neither finding depends on them.
```
## Saved-Artifact Validation Receipt

After saving this report and journal/validation qualifications, ran at root:

```powershell
python tools\check_links.py
git --no-pager diff --check
```

Actual output (both commands exited 0):

```text
checked 535 relative links across markdown files
all relative links resolve
git diff --check: exit 0
```

A direct read confirmed the saved report, including both open findings and the
incomplete full-context checklist. No production/source change was made.
## Original Collision Check Proposal (Subsequently Approved And Executed)

Question: can the current top-level atom presence query return True in an import
layout that has no Atom CLI modules, making the documented routing stop before
healthy known-venv reuse? The review identified this statically, not by execution.

Recommend one bounded local Python-only check before changing bootstrap text:
maximum five minutes and two probe terminal invocations, zero models/agents,
installs, init/check/writer probes or participant-environment changes. Compare
the existing real Atom installation with temporary synthetic namespace/unrelated-
package layouts using non-importing standard-library discovery. Keep fixtures
local to private session evidence, remove them after capture, do not execute
unrelated package code or any known-missing module help, and do not change tools,
PATH, profiles or the accepted bootstrap query. Record actual outputs.

Confirmed means a controlled layout returns top-level presence while the own
role modules are absent, exposing a gap in absence discrimination. Refuted means
the proposed collision does not reproduce under the controlled conditions.
Inconclusive means the fixture/interpreter cannot isolate it or a check fails.
A result does not by itself choose the intended collision/error handling policy,
a replacement detector or approval to implement. Present the evidence first.

Alternative: explicitly defer the Minor finding with its limits; do not silently
claim package identity is proven. The full-context review gap still requires its
own spend decision and is not repaired by this proposed Python check.
## Approved Collision Evidence Check: Result And Limits

The developer selected exactly "Approve the bounded local Python collision check".
One probe terminal invocation ran; the second allowance was not used. Execution
finished in 0.023066100024152547 seconds, below five minutes. This was the existing
local Windows Python interpreter and controlled temporary import layouts, not an
Ubuntu/live onboarding run or another measured rehearsal.

Mechanism: run the current find_spec('atom') presence query without importing the
package, and compare non-importing PathFinder lookup for atom.cli/artifact_cli
with atom-cli distribution metadata. Synthetic arms restrict sys.path to their
own empty namespace or unrelated-package directory. The regular-package fixture
contains a raising __init__.py sentinel that must never execute. Restore the
process search path in finally and clean only the uniquely created fixture root.
The real installed interpreter is a positive control; no help commands, foreign
package code, installations or participant writes are executed.

Verbatim JSON-line output, copied from the captured receipt (probe exit 0):

```json
{"atom_cli_distribution_present": true, "atom_imported": false, "case": "existing_interpreter", "cli_module_present_without_import": true, "top_level_atom_present": true, "writer_module_present_without_import": true}
{"atom_cli_distribution_present": false, "atom_imported": false, "case": "namespace_only", "cli_module_present_without_import": false, "top_level_atom_present": true, "writer_module_present_without_import": false}
{"atom_cli_distribution_present": false, "atom_imported": false, "case": "unrelated_regular_package", "cli_module_present_without_import": false, "top_level_atom_present": true, "writer_module_present_without_import": false}
{"collision_cases": 2, "elapsed_seconds": 0.023066100024152547, "fixtures_removed": true, "installs": 0, "model_calls": 0, "module_help_executions": 0, "process_search_path_restored": true, "verdict": "Confirmed for synthetic top-level-name discrimination only"}
```

Verdict: Confirmed only for synthetic top-level-name discrimination. Both
collision arms return True for the current gate despite absent own role modules
and distribution. The real control resolves both own modules and distribution.
The package was not imported; temporary fixtures were removed and sys.path was
restored. No source, configuration, PATH/profile or installed content changed.

The documented downstream help-failure stop is inferred from bootstrap text; it
was deliberately not executed against a missing module. Healthy Linux-venv reuse,
actual import errors, broken/partial own installations, every editable/custom-
loader form and a real unrelated third-party package were not exercised. Metadata
is a comparison signal here, not a proven universal replacement or instruction to
change the approved detector. No claim is made that collisions should universally
be ignored or automatically reinstalled over.

Recommendation: accept this bounded result for a narrow detection-repair spec,
retaining working editable/module forms and genuine-error stops. Any candidate
needs applicable boundary validation before implementation. Alternative: explicitly
defer the Minor with this evidence and reason. Stop at this evidence/disposition
gate; do not design or implement a replacement, spend on another reviewer, refresh
installed content, publish or resume the rehearsal without applicable approval.
## Local Detection Repair Acceptance

The developer selected exactly "Accept the local detection repair; keep further
work gated". This accepts the bounded collision-guidance implementation and its
local evidence, not independent review completeness. Both original reviewer
responses and gaps remain intact. No additional reviewer/model, publication,
installed-content refresh or rehearsal is authorized.
## Post-Fix Correction Acceptance

The developer selected "Accept the correction; keep delivery, refresh and
rehearsal gated". The README Minor is corrected/locally accepted; the pre-existing
Windows Minor is explicitly deferred. Both fresh reviewers completed their
approved read-only snapshot review. No independent re-review of the newer README
hash, further spend, publication/refresh/rehearsal or Phase 09 completion is claimed.
