# Review Entry - One Local Diff, Then Stop

Use the existing `/atom:review` skill and `atom review` command. This reference
defines their bounded entry contract, not a new command or runtime approval
mechanism. Instructions do not prove that a live agent waits or respects refusal.

## Select The Mode

An explicit review-only request is **standalone**, even if `.atom/` exists.
No initialization, registered phase, POC or design spec is required for reviewing
an existing diff. Do not run `atom status`, search for phase artifacts or adopt
the lifecycle just to perform this review.

Use **phase review** when the current developer-approved work explicitly calls
for it. Retain the established phase report, project audit artifacts and gate.
The presence of Atom files alone does not choose this mode. If intent is truly
ambiguous, ask one focused question rather than inventing project context.

## Inspect Without Starting Review

Establish the local Git target and the intended changes through read-only
inspection. Choose exactly one source: unstaged working changes (`--working`),
staged changes (`--staged`), or committed branch changes against an explicit
reference (`--branch REF`). Do not assume the reference is main or include
untracked files that Git's selected diff does not contain.

If command forms are unknown, use [bootstrap.md](bootstrap.md) and supported
help checks. No separate Atom checkout or inspection of installed Python source
is needed. Missing commands require an installation proposal and consent, not
automatic installation or PATH changes.

Read the root module/configuration only as needed for the selected review.
Missing root `go.mod` does not require `atom init`: disclose that Go tooling will
be skipped. Offer setup separately only if the developer wants it; review intent
is not permission to create a module or repair source.

## Propose Before Probes Or Paid Work

Present one concrete plan, then ask for approval and stop:

- Target directory and exact diff selector/reference.
- Actual reviewer model identifiers, number of runs, concurrency and expected
  submission count. Include availability probes in the call budget: two models
  with one run each can involve two probes plus two review submissions. Do not
  promise a token or monetary ceiling the runtime does not enforce.
- Normal Go checks, missing/skipped evidence and relevant side effects. Go checks
  may invoke project build commands, dependencies, toolchains and caches; ordinary
  review is not inherently offline, read-only or free of cache writes.
- Effective launch Go pin (`review_go_version` or approved `--go-version` override,
  plus any explicit executable) and possible degraded continuation described below.
  If a hard stop on required-gate failure is wanted, explicitly propose
  `--strict-toolchain`; do not silently add it or change the runtime default.
- Report format and exact report/audit paths, including any directories created.
- The review-only exit: report and triage, not fixes, setup, phase advancement,
  commit, push or publication.

Recommend one run per model and concurrency 1 as a bounded starting choice,
not a change to CLI defaults. Choose at least two different reviewer models,
neither the authoring model. Resolve unknown identities/authorship explicitly;
do not infer independence from a label. This is skill policy, not CLI enforcement.

Use actual approved identifiers rather than silently accepting CLI defaults.
Repeated `--model NAME` selects reviewers; without it the CLI has built-in
defaults. It does **not** resolve reviewer model roles from `.atom/config.json`.
That file may independently configure Go-version policy. General role advice in
[model-guidance.md](model-guidance.md) does not change this CLI-specific contract.

No reviewer availability probe or review submission occurs before approval.
Earlier setup/phase approval is not automatically approval of this review spend.
If declined, do not launch reviewers, create the bundle or modify the target.
A changed selector, additional runs/models, installation, gate bypass, fix or
publication requires a separately approved scope. Never silently retry a failed
review with more spend or a different toolchain.

## Execute Only The Approved Command

These are alternatives, not a batch to run. Replace MODEL_A and MODEL_B with
approved available identifiers and use the approved branch reference:

```text
atom review --working --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
atom review --staged --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
atom review --branch main --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
```

Add `--json` only when that output was selected. Use the successful command form
from bootstrap. Keep normal gates enabled; do not add `--skip-toolchain`, change
Go versions or repair the diff to get past a failure. Existing explicit advanced
options remain available under their own approved scope, not as automatic recovery.

Formatting checks selected surviving changed Go snapshots without rewriting them.
Build, vet, test and race checks instead examine the working module, not an
isolated staged index or committed branch tree. Passed race tests cover exercised
paths only. Absent optional analyzers and missing-module tooling exclude nothing.

Required-gate failures normally block reviewer calls. One existing exception can
apply when a verified selected Go is older than the root module minimum, including
a launch `review_go_version` pin, and `--strict-toolchain` is not set. After a
proven selected build failure, compatible control gates must pass and the checked
input fingerprint must remain unchanged before reviewers can run with degraded
evidence. Not every pin or build failure qualifies. Disclose this policy before
approval; it is runtime continuation, not permission for an agent to retry or
change versions.

Surface actual failures and preserve any degraded report and warning. A degraded
review exits nonzero; passing control checks do not make the selected Go checks
clean or the review gate-passed. Stop after reporting, without automatic recovery.
An exit-0 report with missing `go.mod` is still unverified tooling evidence, not a
verified build or application. Distinguish skipped checks, unavailable/silent/unparsed
responses, partial participation and genuinely empty findings. No usable response
is not a clean review. If fewer than two qualifying independent models answered,
report that the skill's multi-model obligation remains unmet; do not invent
participation or automatically retry.

## Persist And Triage Without Adopting A Lifecycle

The CLI emits its report to stdout; it does not choose a phase path. The skill
proposes a small standalone bundle, for example:

```text
specs/reviews/<slug>/review.md
specs/reviews/<slug>/findings.md
specs/reviews/<slug>/decisions.md
```

Choose the exact permitted paths with the developer before creating anything.
For phase review, retain `specs/{project}/phase-NN-{slug}/review.md` and the
project's existing findings/decisions locations instead.

Preserve the actual runtime report and participation/evidence limitations.
Always produce `findings.md` and `decisions.md`, even when they say "No findings."
and "No deviations." Use `atom-write-artifact` for these `specs/**` artifacts,
obtaining its repository-scoped permission on first use. Check existing paths;
do not overwrite conflicting work. Any writer refusal or nonzero exit is a
blocker: surface it and stop, without a generic editor or alternate path.

If the developer declines audit-file creation, explain that the skill cannot
complete its persisted audit under this plan. Do not silently drop the records
or force a phase directory. Direct CLI stdout behavior remains available and
unchanged; that is not permission to execute a different paid plan.

Triage high-consequence findings with the developer. Record deferrals/rejections
and reasons. Any fix is a separate approved action with appropriate verification,
not part of review-only consent.

**Standalone stops here:** present report, triage and remaining limitations.
Do not invoke ship, start another phase or modify source automatically.
**Phase review** presents its normal gate and may recommend its next beat; that
recommendation does not authorize executing it.
