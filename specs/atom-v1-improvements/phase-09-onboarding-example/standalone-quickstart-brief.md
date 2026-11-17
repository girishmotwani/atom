---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-16"
status: "approved-for-isolated-preparation"
---

# Standalone Expense Quickstart Replay Brief

## Outcome And Question

Deliver one short clean-install quickstart ending in an executed Go expense-summary
POC, without requiring adoption of Atom's full project pipeline. This is a useful
proof experiment, not a production-ready expense application.

Can the developer install the public Atom plugin and tooling into fresh isolated
locations on Ubuntu WSL, then use one standalone POC to obtain the exact expense
totals and visible input failures, without project onboarding, phase registration,
a design/TDD cycle, or unprovided coaching?

## Existing Evidence And Remaining Risk

The developer restated this outcome in the preceding session. The original
[poc-brief.md](poc-brief.md) instead requires /atom:init, /atom:start and the example's
full implementation cycle. Its Inconclusive reports are preserved, not regraded.
Bootstrap repairs have Ubuntu evidence; the later discovery helper is local and
unpublished. Neither establishes this standalone end-to-end result.

Read-only inspection of tools/atom/cli.py shows poc new/run use cwd/poc directly,
without phase state. Actual local command help exposes:

```text
atom poc new --question QUESTION slug
atom poc run [--json] [--no-colour] [--timeout TIMEOUT] slug
```

This supports trying the existing path, not claiming it already works from a fresh
public install. Phase 04's broader entry-point work remains unimplemented/unproven;
no new shortcut or policy exemption will be invented here. The selected risk is
integration: the installed skill, artifact writer and deterministic POC commands
must work together without unrelated project state. Four synthetic CSV rows raise
no throughput question. Experienced-user success is not newcomer-usability proof.

Recommendation: one bounded observed standalone replay. Alternative: finish the
original full-pipeline rehearsal; that could prove that workflow but would not
answer this brief's question. A parser-only spike also would not prove installation
or the user-facing path.

## Frozen Acceptance Contract

Input is one UTF-8 CSV with header category,amount, one currency and amounts with
two decimal places, including a negative refund:

```csv
category,amount
food,12.50
travel,5.00
food,7.50
travel,-1.25
```

Require one total per category: food 20.00 and travel 3.75. An amount of oops and a
missing file must each produce a visible diagnostic and nonzero process exit,
without success totals. Record exact stdout, stderr and originating exit statuses.
No currency conversion, accounting features, numeric representation, package layout
or production API is selected by this contract.

## One Attempt And Its Boundaries

- One developer-operated interactive session; no parallel agents or review batches.
- Proposed cap: 30 minutes active replay time, measured separately from preparation.
  This is an operator-observed stop condition, not an automatic limit or time promise.
- Existing supported Go, Python, git and Copilot are prerequisites. Do not install or
  update those tools, change authentication, request privilege, or edit shell profiles.
- Use a new Linux-native disposable workspace, a new Python virtual environment,
  and a fresh Copilot profile/cache, each checked absent before creation. Do not use
  or remove earlier rehearsal directories or touch the working Atom checkout.
- Install only the public Atom Python tooling and public marketplace plugin, after
  explicit installation consent and ordinary command approvals. Freeze the public
  source identity and installed plugin content before starting the model session;
  use no editable checkout, local plugin override or unpublished discovery helper.
- Existing credentials may be used only through the client's ordinary supported
  authentication. Never copy tokens/configuration. Stop if fresh-profile access
  requires login or another unapproved authentication change.

The current client's documentation describes COPILOT_HOME, COPILOT_CACHE_HOME and
COPILOT_AUTO_UPDATE=false for isolated profile/cache and disabled CLI/plugin
updates. Verify the actual Ubuntu client's support before use; current Windows
build documentation is not evidence that an older Ubuntu binary supports them.
Use child-process-only settings. Do not change global environment or HOME.

Approval authorizes preparation of this one isolated replay, including the named
Atom-only installations. Present the exact compact recipe and frozen identities
before the active replay. A profile/authentication/version boundary stops preparation;
it does not authorize another bootstrap-repair project.

## Candidate Standalone Path

1. Record actual client/prerequisite versions and absence of Atom/project state in
   the fresh locations. Establish the two Atom command roles through their public
   interfaces using the isolated tooling; preserve failures rather than reinstalling.
2. Install/freeze the public plugin in the isolated client profile. Keep the final
   recipe limited to setup, the bounded request and verification; the participant
   must not need the methodology as a help manual.
3. In the new workspace, ask the installed Atom POC skill for a disposable
   expense-summary experiment with this fixture and error contract. Supply this
   approved experiment question and scope; allow only necessary artifact writes,
   Go scaffold/build/vet/run and input fixtures. Do not invoke init/start/build.
4. The installed skill must retain its brief/report approval pauses and required
   findings/decisions. Use atom poc new expense-summary --question with the agreed
   Go question, then atom poc run expense-summary. The disposable Go question is:
   Can a Go command read the supplied expense CSV, print exact category totals
   including the negative refund, and reject invalid amounts and missing files
   with a nonzero exit and no success totals?
5. Capture real vet/build/run output. Execute the generated command directly for
   all three inputs, since a POC runner's interpretation is not a substitute for
   checking the Go process's negative-case exit statuses. Compare against the
   independent expected totals, not expectations derived from the generated code.
6. Confirm no project onboarding, phase registration, spec/TDD cycle or automatic
   escalation was required. Stop at the POC report gate. Do not proceed to design,
   production implementation, model review, shipping or publication.

If the installed skill cannot support this scope without changed instructions or
unrelated state, preserve that result and stop. Do not coach around it, prewrite the
Go implementation or silently switch to raw Go commands as the claimed Atom path.
No root atom check or full-production/race/coverage completion claim is appropriate
for this throwaway proof. Its normal POC vet/build/run and behavioral checks remain
mandatory; later production work retains its own spec/TDD/full verification gates.

## Verdict And Evidence

Confirmed only if the isolated public install and frozen recipe reach all three
behavioral results, with actual approvals and no full-pipeline requirement or
outside coaching. Refuted if setup succeeds but this standalone recipe cannot
reach the result without that escalation/coaching, or a required approval is
bypassed. Inconclusive if access/setup fails, evidence is incomplete, the cap expires
or conditions change before evaluation. No automatic retry or guide repair mid-run.

Retain exact commands, public snapshot identities, installed asset hashes, relevant
redacted user/agent turns and approval prompts, separate setup/replay durations,
verbatim program output and exit statuses. Do not publish raw recordings, credentials
or unrelated information. A passing replay becomes evidence for a short Phase 09
documentation spec, not permission to publish the final quickstart immediately.

## Explicit Non-Coverage

Fresh Atom tool/plugin locations on existing Ubuntu WSL are not a clean operating
system, independent host, novice test, all-platform guarantee or cold authentication
test. Do not claim compatibility across all documented minimum versions. This
experiment does not accept/publish the local helper fix, implement Phase 04,
produce a production expense CLI, repair inherited CI, create a site, commit,
push, open/merge a PR or authorize another model batch.

## Gate

Draft only. Approve this replacement standalone experiment and its isolated
Atom-only setup scope before any environment preparation or live replay.

## Developer Approval: 2026-11-16

Developer selected exactly: "Approve standalone replay scope and isolated Atom setup".
This authorizes the scoped isolated preparation and Atom-only installations under
ordinary command approvals. Preserve the existing environment and earlier evidence.
The exact frozen recipe/identities are presented before the single active replay;
no live session, automatic retry, production work or publication is authorized by
this preparation gate. Stop this turn before beginning the newly approved setup.

## Approved Isolation Amendment: 2026-11-16

Developer selected exactly: "Approve fresh profile with disclosed shared CLI cache".
Retain the existing pinned Ubuntu CLI 1.0.107. Fresh Atom tooling, profile and
workspace remain required, but a separate fresh CLI cache is no longer required;
the existing shared CLI cache is explicitly disclosed. This supersedes the earlier
fresh-cache condition and its assumption that COPILOT_CACHE_HOME must be available.
Use only supported controls; no HOME change, CLI upgrade or authentication change.
Check the plugin-update/frozen-content boundary during the already approved
preparation. Other stop conditions, ordinary command approvals, the exact-recipe
handoff and the one-session/30-active-minute scope remain unchanged. End this gate
turn without installation or live model work.
