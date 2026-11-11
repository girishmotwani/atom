---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-11"
status: "local-correction-accepted-windows-minor-deferred"
scope: "five shipped onboarding files versus HEAD; post-fix snapshot"
---

# General Onboarding Repair: Independent Post-Fix Review

## Current Disposition

The developer explicitly approved README correction and local Windows deferral.
The four README passages are now corrected and locally validated: the existing
affected test passes, 545 links resolve and whitespace is clean. Bootstrap/init
bytes remain unchanged. Actual outputs and the new README hash are recorded
below after the preserved reviewer responses. The developer accepted this local
correction with the Windows issue deferred. No independent review of the new
README hash is claimed. Delivery, refresh and rehearsal remain gated.

## Original Review Outcome Before Triage

Two independent reviewers returned two distinct Minor findings; neither reported
a Blocker or Major. This is not a clean review and no fix/deferral is presumed.
Both report complete required file/evidence context and explicitly account for
byte-identical mirrors. This supplies a new full-context review of this snapshot;
it does not retroactively complete the earlier partial review.

The developer requested "lets do the review and next steps", then selected exactly
"Approve two read-only reviewers: claude-opus-5.5 + gpt-6.1-terra". One fresh agent
invocation per model ran, without availability probes, retries, follow-up turns,
new experiments or installs. These two invocations exhaust this new allowance;
no claim about underlying API-request counts or monetary cost is made. Neither
reviewer is author gpt-6.1-sol. No repository model default was changed.

Opus agent: df324544-4ef1-4bcd-a8d3-79c1a674fad3.
Terra agent: 3e7e33a6-de5c-4b7e-bfbd-0d78b17bd598.
The reviewers did not see one another's findings or prior review responses.

## Snapshot And Reused Checks

All five SHA-256 values were checked before launch, reported matching by both
reviewers, and checked by the parent again after both reports. No shipped bytes
changed during review.

| File | SHA-256 |
|---|---|
| README.md | 1390ECFC411EB065CEA74FC41383EFA5DBA611B79E6AE47DBA3DE6F5C369B5D1 |
| skills\init\SKILL.md | 15E4169B5BE2896DD3D3802129B18D6BC81C48E9C2E956F48CD199AB23AF52F8 |
| tools\atom\assets\skills\init\SKILL.md | 15E4169B5BE2896DD3D3802129B18D6BC81C48E9C2E956F48CD199AB23AF52F8 |
| skills\atom\references\bootstrap.md | 1A2211645E8981D735C6C99E0C78D11E38437A5168B66B3367E8DBF90B06E96E |
| tools\atom\assets\skills\atom\references\bootstrap.md | 1A2211645E8981D735C6C99E0C78D11E38437A5168B66B3367E8DBF90B06E96E |

Reused the accepted [detection validation](package-detection-repair-validation.md)
and its verbatim 14-test, exact-query, parity/link/whitespace receipts against
these unchanged source hashes. Original README validation remains scoped to its
captured hash. No test or candidate probe was newly executed for this review.
There is no root Go module: build/vet/fmt/test/race are inapplicable, not passed.
The developer approved this read-only-agent documentation-review adaptation;
native review's paid availability calls/Go gate were not invoked. No tool category
excludes semantic instruction errors, evidence overclaim or actual agent behavior.

Contracts are the [flow spec](prerequisite-flow-repair-spec.md) and
[detection addendum](package-detection-repair-spec.md). Both reviewers report full
reads of root instructions, all five shipped files (mirror parity applied), and
both specs/mappings/validations plus the complete original discovery report.
Their exact coverage manifests and original responses appear below.

## Merged Findings And Proposed Triage

### Minor: README Overstates When An Installation Question Is Offered

Agreement: 1/2, Opus. Primary location README.md:482-483; related broad wording at
25, 603 and 673. The explicit blanket promise of an installation question is not
what the approved instructions do. Missing Go/Python/Git/venv/ensurepip are
prerequisites the developer must supply; the guided Atom installation recipe is
Linux-only, only after explicit absence and an absent safe destination. Other
platforms need a setup decision, not an automatic installation offer.

Breaks when a reader missing a system prerequisite or Atom on Windows/macOS
expects the universal installation question promised at line 483. Parent targeted
reads confirm the contradiction with init:30-32 and bootstrap Steps 2-4. The other
three phrases are broader/less explicit and should be aligned, not treated as
proof that installation is always promised by every conditional consent phrase.
These README sentences were changed by this repair and its behavior 14 requires
accurate missing/hidden/broken choices: this is directly in scope.

Suggested fix: clarify those four README passages without changing the existing
platform/tool policy. Ask developers to supply missing system prerequisites;
only confirmed missing Atom on supported Linux can reach consent-gated guided
installation; other platforms/ambiguity stop for a setup decision. Use factual
review and existing affected documentation checks, no new spike or tool install.

Proposed disposition: fix the README wording now, pending developer approval.
No edit has been made.

### Minor: Optional Windows PATH Setup Switches To Unverified Executables

Agreement: 1/2, Terra. Location skills\atom\references\bootstrap.md:189-193 and
its identical packaged mirror. Working module/mixed forms can be replaced by
printed executable paths without verifying those executables. Parent read
of tools\atom\pathsetup.py:90-108 confirms selection checks that both files exist,
not their help/health. Broken or stale wrappers can therefore turn a healthy
working session into a failing one after optional PATH setup. No stale-wrapper
experiment or PATH mutation was run; this is static evidence of the missing check.

Suggested repair direction: preserve verified forms until each proposed absolute
replacement passes help; retain genuine-error stops rather than silently hiding
an actual failure. Exact behavior, evidence and approvals belong to that repair.

The full bootstrap diff shows the optional Windows paragraph unchanged from
HEAD. Existing flow/detection scopes preserve that opt-in path and do not redesign
its implementation. This is a valid pre-existing adjacent risk, not a regression
introduced by the detection repair. Do not silently expand this repair or drop it.

Proposed disposition: record/defer to a separately scoped Windows command-handoff
repair, pending developer approval. No issue was created and no deferral approved.

## Next Steps Proposed, Not Authorized

First triage these two findings. Recommended: correct the in-scope README promise
and explicitly defer/log the existing Windows issue. Verify the approved wording
change with relevant existing checks and unchanged bootstrap/init hashes; present
local acceptance. Any independent review of a new source hash needs a separate
model allowance, not a third turn under this budget.

After triage/acceptance, decide whether to prepare a focused delivery PR. A read-only
GitHub query returned no PR for feat/phase09-public-rehearsal. Publication/commit/
push are not authorized by this review. Human review/merge remains separate.

A later installed-plugin/package refresh needs named-source/target approval and
content verification; source edits do not update installed instructions. The
recorded Ubuntu delivery is still the older ec605a715f53db93abd54d6e88f887cf20525940
snapshot. Do not treat it as delivery of this local repair.

A further observed rehearsal requires a newly approved source/client/model,
capture method, effort budget and success criteria. Preserve both frozen recipes,
stopped module/recordings and the Inconclusive prepared result. Do not resume the
old attempt, approve its pending spike, or mark Phase 09 complete. The phase plan
still requires a successful supported replay and one useful verified Go example.

## Original Reviewer Responses (Verbatim)

### claude-opus-5.5
## (1) Findings

### Minor: README promises an install question for missing tools, but the shipped guidance only offers one for Atom on Linux
**Files:**
- `C:\Users\gimotwan\work\atom\README.md:25` ("asks before installing missing tools")
- `C:\Users\gimotwan\work\atom\README.md:482-483` ("missing tools receive a prerequisite explanation and an explicit installation question")
- `C:\Users\gimotwan\work\atom\README.md:603` ("asks before installing missing tools")
- `C:\Users\gimotwan\work\atom\README.md:673` ("requests installation consent only when tools are truly missing")

These contradict:
- `skills\init\SKILL.md:30-32`: if Go is missing, "ask the developer to supply it… do not install Go".
- `skills\atom\references\bootstrap.md:76-78`: if Python is missing, ask the developer to supply it and stop without provisioning it.
- The Step 4 Git/venv/ensurepip prerequisite rule: ask the developer to supply them and don't install system tools.
- `bootstrap.md:229-234`: the install recipe is Linux-only, and Step 2 ambiguity never reaches Step 4.

**Breaks when:**
- A Windows or macOS user doesn't have Atom installed. The README says they will get an installation question. Bootstrap actually stops and asks them to agree on an isolated setup, with no install offer.
- Any user is missing Go, Python or Git. The README describes an "explicit installation question", but the skill asks them to supply the tool themselves.

In both cases the user expects Atom to offer an install and it doesn't. Spec behavior 14 requires the README to describe the missing/hidden/broken choices accurately and to avoid automatic-install promises. The repair rewrote these four sentences specifically, so the overgeneralization is directly coupled to this change, not legacy text.

**Evidence:** Direct comparison of the README text above with init Step 2 and bootstrap Steps 2–4 in the final snapshot. The repair-spec Behavior 8 and package-detection-spec Behavior 9 confirm that only "explicit absence + absent safe destination" on Linux leads to an install proposal.

**Suggested fix:** Scope the four README sentences to what actually happens:
- Missing Go, Python or Git: Atom explains the prerequisite and asks you to supply it.
- Missing Atom commands on Linux: Atom asks for consent before an isolated user-venv install.
- Other platforms, or an ambiguous same-name package: Atom stops for a setup decision.

No other findings. Discovery ordering, the decision-table precedence (I walked the mixed, partial, null and empty-candidate rows in order), the metadata-versus-health caveat, real-error and writer-refusal stops, consent boundaries, safe venv reuse and the client/alias handoffs are consistent with both accepted specs.

## (2) Context manifest
- **Hashes:** I computed SHA-256 locally and all five match the stated snapshot. Both init files are `15E4…52F8` and both bootstrap files are `1A22…6E96E`, so each mirror is byte-identical to its canonical file. My full review of the canonical init and bootstrap files applies to the mirrors unchanged.
- **Diff:** read the full `git diff` for README, `skills/init/SKILL.md` and `skills/atom/references/bootstrap.md` (24.2 KB, read completely through a full-file view).
- **README.md:** lines 1–260, 261–520 and 521–772 (EOF, 772 lines).
- **skills\init\SKILL.md:** lines 1–200 (EOF).
- **skills\atom\references\bootstrap.md:** lines 1–320 (EOF).
- **AGENTS.md:** full, 229 lines.
- **Spec files** (all under `specs\atom-v1-improvements\phase-09-onboarding-example\`), each read in full:
  - `prerequisite-flow-repair-spec.md` (217 lines)
  - `prerequisite-flow-repair-test-spec.md` (77)
  - `prerequisite-flow-repair-report.md` (134)
  - `prerequisite-flow-repair-validation.md` (218)
  - `package-detection-repair-spec.md` (330)
  - `package-detection-repair-test-spec.md` (108)
  - `package-detection-repair-validation.md` (196)
- **Supplementary:** read `plugin.json` and listed the skill and command entries only to sanity-check the README entry-count wording; I'm not reporting anything from that.
- **Not read, as instructed:** `prerequisite-flow-repair-review.md`, `findings.md`, `decisions.md` and other reviewers' output.
- No reads truncated, so coverage of the required files is complete.

## (3) Validation limits
- This was static reading of the documents plus git and hash checks only. I didn't run any tests, probes, the documented query, the link checker or installers.
- The validation results above are the author's captured outputs, which I reused, not results I reproduced.
- The root has no Go module, so build, vet, fmt, test and race don't apply; nothing is claimed as passed.
- Agent adherence, live Linux ambiguity-to-venv routing, custom importers, metadata-exception and failing-help branches, and interactive alias acceptance all remain unproven. The specs bound these explicitly, so I did not reopen them.
### gpt-6.1-terra
## Issue: PATH setup replaces verified forms with unchecked executables
**File:** `C:\Users\gimotwan\work\atom\skills\atom\references\bootstrap.md:189`
**Severity:** Medium (Minor)
**Problem:** On Windows, opting into PATH setup can replace working module or mixed forms with stale executables. Onboarding may then fail despite having verified working forms.
**Evidence:** The setup command checks that both executable files exist, not that they work. The guidance nevertheless requires using both printed paths without help-checking them.
**Suggested fix:** Retain the verified forms, or help-check each printed absolute executable before replacing one.

## Context manifest
- `C:\Users\gimotwan\work\atom\README.md`: 1–772
- `C:\Users\gimotwan\work\atom\AGENTS.md`: 1–229
- `C:\Users\gimotwan\work\atom\skills\init\SKILL.md`: 1–200
- `C:\Users\gimotwan\work\atom\skills\atom\references\bootstrap.md`: 1–320
- Under `C:\Users\gimotwan\work\atom\specs\atom-v1-improvements\phase-09-onboarding-example\`:
  - `prerequisite-flow-repair-spec.md`: 1–217
  - `prerequisite-flow-repair-test-spec.md`: 1–77
  - `prerequisite-flow-repair-report.md`: 1–134
  - `prerequisite-flow-repair-validation.md`: 1–218
  - `package-detection-repair-spec.md`: 1–330
  - `package-detection-repair-test-spec.md`: 1–108
  - `package-detection-repair-validation.md`: 1–196
- Both packaged mirrors are byte-identical to their fully read canonical files; HEAD mirrors also match. All five snapshot hashes matched. No incomplete context.

## Validation limits
No tests or experiments were run. Captured validation was reused, not independently reproduced; it does not prove agent adherence or live Linux routing. Root Go gates are inapplicable.
## Saved-Report Integrity Receipt

Direct reads confirmed the complete saved report, both original responses and
coverage manifests. After saving, ran python tools\check_links.py and
 git --no-pager diff --check at root. Actual captured output (both exited 0):

```text
checked 545 relative links across markdown files
all relative links resolve
git diff --check: exit 0
```

These are fresh artifact-integrity checks only. The 14 source-contract cases and
candidate-query receipts remain reused evidence; no new model/probe/install or
shipped edit followed the two reviewer responses. Developer triage is pending.
## Approved Triage And Local README Correction

The developer selected exactly "Fix README wording and record the Windows issue
for separate repair". Corrected the four README passages only: missing system
prerequisites must be supplied, the guided Atom installation recipe is Linux-only
and consent-gated, and other platforms need an agreed isolated setup. The approval
paragraph also states explicit absence, absent destination and safe ancestors.
Healthy hidden-tool reuse, broken/unsafe stops, manual recipes and historical
ledger claims are retained. The final four passages were read and factually
compared with the existing init/bootstrap policy. No material spec change.

The Windows handoff Minor is explicitly deferred to separate repair and recorded
in findings.md with location, consequence and evidence direction. No Windows
source, runtime or PATH change and no GitHub issue/publication was made. Both
reviewer invocations are spent; the new README hash is locally validated, NOT
independently re-reviewed. Original reviewer responses above remain unchanged.

### Fresh Existing README Contract Check

From tools, actual command (exit 0):

```powershell
python -m pytest tests\test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation -q
```

Verbatim captured output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_pathsetup.py .                                                [100%]

============================== 1 passed in 4.61s ==============================
```

This pre-existing case preserves only the setup command/session-limitation text;
it is not proof of installation-policy correctness or actual agent behavior.
No test was added, removed or weakened; no production RED/GREEN is claimed.

### Links, Whitespace And Preserved Reviewed References

At root ran python tools\check_links.py and git --no-pager diff --check; compared
all four init/bootstrap hashes to the reviewed snapshot. Actual captured output
(all checks exited 0):

```text
checked 545 relative links across markdown files
all relative links resolve
git diff --check: exit 0
All four bootstrap/init hashes unchanged.
README SHA-256: 64E6120B27F05EF224B56C4A8CD6D239A331E420FC09D46687E987630E07D68D
```

No new query probe/model/installation was executed. Previous 14-case and candidate
receipts are reused only for unchanged contracts/references, not reported as fresh
results for this README hash. No root Go module or fictitious Go gate was added.
Local acceptance is the next gate, followed only by separately scoped delivery,
installed-content refresh and a new approved observed rehearsal. Phase 09 remains
incomplete; frozen recipes and the stopped/Inconclusive result are preserved.
## Explicit Correction Acceptance And Stop

The developer selected exactly "Accept the correction; keep delivery, refresh
and rehearsal gated". The README correction is accepted locally; the existing
Windows handoff Minor remains explicitly deferred. Both findings have a recorded
disposition, with no Blocker/Major reported. Review/correction work is complete
within this scope, not a clean zero-finding review or Phase 09 completion.

The next proposed gate is authorization for a focused delivery PR. No commit/push,
publication, installed-content refresh, extra reviewer or live rehearsal follows
this acceptance. The new README hash remains locally validated only; the two
independent review responses apply to their recorded older README snapshot.
