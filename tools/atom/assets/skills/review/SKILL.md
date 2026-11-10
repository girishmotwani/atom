---
name: review
description: 'Standalone or phase multi-model review of a Go diff, merged into one report with severities. Keywords: review, code review, multi-model review, review my changes, review the diff, critique.'
---

# /atom:review

Reviews a diff with **two or more different models** and merges their findings into one
report.

## Why more than one model

A model reviewing its own output shares its own blind spots. It will not flag the
misunderstanding that produced the code, because it still holds that
misunderstanding.

> **The reviewing model must not be the model that wrote the code.**

This is the entire point of the skill. A single-model self-review is not a substitute,
and running one instead is the rationalization this skill exists to prevent.

## When to use

- For a bounded standalone review, without Atom initialization or phase state
- After `/atom:tdd` for a phase
- Before `/atom:ship`
- Any time a diff is large enough that reading it once isn't enough

## Writing artifacts

Send complete review reports, findings, and decisions as UTF-8 standard input to
`atom-write-artifact <relative-path>`. Treat any refusal or non-zero exit as a blocker;
never bypass it with a generic editor or another shell command.

## Step 0 — Scope, propose and wait

Read [standalone-review.md](../atom/references/standalone-review.md) first.
Follow its mode, prerequisite, consent, model-budget and artifact contract in
both standalone and phase contexts. Explicit review-only intent remains standalone
even in an initialized project. Do not require phase discovery or onboarding.

Propose the exact target/diff, actual models, runs/concurrency, evidence and file
effects before availability probes or review submissions. Wait for approval;
refusal launches no reviewers and creates no bundle. Do not call `atom review`
merely to discover the diff or probe models before that gate.

## Step 1 — Establish the diff without calling reviewers

```bash
git diff main...HEAD             # inspect committed changes against agreed main
git diff --staged                # inspect staged changes
git diff                         # inspect unstaged working changes
```

Choose only the intended source/reference; main above is an example, not a default.
Inspect surrounding code as needed for triage. The CLI supplies the selected diff
and its evidence, not an automatic whole-file context or approved design spec.
Do not claim reviewers received context that was not actually supplied.

## Step 2 — Let the toolchain answer first

No separate command: the gate runs inside `atom review`, before the models.

For a normal review with a root Go module, Atom runs `go build`, `go vet`, `gofmt`, `go test`
and `go test -race`, plus `staticcheck`, `errcheck` and `govulncheck` when they are
installed.

Review formatting checks whole surviving changed Go files from the selected
working-tree, staged or committed-branch snapshot, using stdin without rewriting
source. Untouched files are not scanned. The report names checked paths and
outside-module or nested-module exclusions; zero applicable files means SKIPPED,
not a formatting pass. Other review checks retain their existing module-wide
scope, and standalone `atom check` retains module-wide formatting.
Those module-wide checks run against the working tree, not an isolated staged
or committed tree. Without root `go.mod`, tooling is explicitly skipped: an exit-0
report does not verify a build. Missing optional tools exclude nothing.

**A failing required gate normally blocks reviewer calls.** The selected-Go
degraded-continuation exception below must be disclosed in the proposal.
Use explicitly approved `--strict-toolchain` when a hard stop is required.

What passed is then written into the prompt as **excluded**: the models are told not to
re-report an ignored error, a vet diagnostic, a formatting complaint, or a data race on
a tested path. That exclusion is the mechanism that frees attention for the rest of this
page.

These rules keep the exclusion honest:

- **A tool that did not run excludes nothing.** If `errcheck` is not installed, the
  prompt says so and ignored errors stay in scope. Suppressing a category nobody checked
  is how real bugs go missing.
- **Clean is not absent.** `go test -race` only observes paths the tests actually
  executed. Concurrent code with no test is unchecked, not safe — and the prompt says
  that in those words.
- **Formatting proof is file-scoped.** Only the checked snapshots are excluded
  from formatting review; excluded modules and a skipped formatter are not clean.

`--skip-toolchain` bypasses the gate. The prompt then tells the models that nothing was
checked and nothing is excluded, so a skipped gate costs attention rather than silently
hiding findings.
Do not select this bypass or another Go version as automatic failure recovery;
the shared entry contract requires approval of changed evidence/scope.

### Optional exact Go selection

The launch module's existing `.atom/config.json` may set `review_go_version` to an
exact stable `1.X.Y` patch (X >= 21). `--go-version 1.X.Y` overrides it for one run;
`--go-executable PATH` selects an already installed direct `bin/go` (Windows:
`bin/go.exe`) and requires an effective version. No installation, automatic upgrade,
ancestor lookup or version inference from `go.mod` occurs. Malformed present config
is an explicit error. Explicit paths resolve from launch cwd before PR preparation;
target checkout policy never replaces the frozen launch request.

Bounded installed-location discovery may need an explicit path for custom layouts.
Selected direct Go gates and selected-root gofmt retain existing gate semantics;
pinned Makefile build/test delegation fails before probes or recipes rather than
bypassing the project's build. Unpinned delegation is unchanged. Advisory helper-Go
settings are selected, not analyzer binaries/compiler internals or model tools.
Child-only settings do not change defaults or make dependency activity network-free.

Reports/prompts distinguish requested from observed versions. Configured pins with
`--skip-toolchain`, or requests outside a root Go module, remain `not_run` with no
observed executable/probes. Explicit Go flags plus `--skip-toolchain` are usage
errors. Missing, mismatched or changed executable identities still block review;
compiler text alone cannot justify continuation.

Before approval, name the effective launch Go pin and any explicit executable.
Without `--strict-toolchain`, a verified selected Go older than the root module
minimum can qualify for degraded continuation after a proven selected build
failure. Compatible control gates must pass and the checked input fingerprint
must remain unchanged before reviewer calls. This can apply to `review_go_version`
without CLI Go flags; not every pin or failure qualifies. Preserve the failures,
control evidence and warning: a degraded review exits nonzero, not clean or
gate-passed. This existing runtime policy is not permission for an agent to retry,
switch versions or expand the approved plan. Propose `--strict-toolchain` explicitly
if desired; do not silently change defaults.

## Step 3 — Run the models

```bash
atom review --branch main --model MODEL_A --model MODEL_B --runs 1 --concurrency 1
```

Run only the complete approved command. MODEL_A and MODEL_B are placeholders for
actual approved available models, neither the author. Use the agreed selector;
working/staged alternatives are in the shared reference. Runs=1/concurrency=1 is
a bounded recommendation, not the CLI default.

Each model run receives the full selected diff and evidence, not a separate
invocation for each file. Runs do not receive each other's findings; concurrency
is controlled by the approved option. The CLI uses repeated `--model` values or
built-in defaults, not general model-role resolution from `.atom/config.json`.
Report unavailable, silent, unparsed or insufficient independent responses
honestly; do not substitute a clean review or automatically retry.

## Step 4 — What reviewers look for

Only successful, applicable toolchain evidence is excluded. Unchecked concerns remain
in scope. What is left is
the set of questions no tool can answer — and it is deliberately short, because a
reviewer handed thirty concerns reports on none of them well.

| Priority | Category | Why no tool catches it |
|---|---|---|
| 1 | **Wrong logic** | It compiles, vets clean and the tests pass — because the tests assert the wrong thing |
| 2 | **Untested concurrency** | The race detector only observes paths the tests ran. A goroutine with no test is unchecked |
| 3 | **Misleading names** | A name that says the wrong thing costs every future reader, and no linter can tell |
| 4 | **Code that resists extension** | A wide interface or a package-level dependency forces the next change to edit working code |
| 5 | **Contract drift** | The code disagrees with the approved design spec, which no tool has read |
| 6 | **Tests that cannot fail** | A green suite that asserts nothing looks identical to a green suite that works |
| 7 | **Unvalidated input** | `govulncheck` finds known holes in dependencies, never the one you just wrote |

Severity still comes from consequence. A finding that cannot be stated as "this breaks
when X" is a preference, and preferences are the findings reviewers drop first. That is
measured, not assumed: seeded defects phrased as style preferences were reported by
nobody, while defects with a visible consequence were reported by everybody — even when
the reviewer was handed the exact rule.

[go-style.md](../atom/references/go-style.md) is the reference behind priorities 3 and 4.
Use it to explain a finding, not as a checklist to walk: thirty rules handed to a
reviewer produce worse coverage than seven.

Formatting in the checked file snapshots is **not** reviewed. `gofmt` settled it
for those files only; a skipped formatter or an excluded module proves nothing
about formatting there.

> **Where the real instruction lives.** This table guides *your* triage. The sentences
> actually sent to the models are `REVIEW_PROMPT` and the toolchain block in
> `tools/atom/review.py`. Changing this table alone changes nothing the models see —
> if you want different findings, change the prompt and re-measure.

## Step 5 — Capture the actual merged report

The runtime groups findings by file and line proximity, retaining every message
and severity disagreement. This is not semantic deduplication: nearby reports
may describe different defects. It emits Markdown or JSON to stdout.

Persist the report at the approved mode-specific path from the shared reference.
Standalone uses its small review/findings/decisions bundle; phase review retains
`specs/{project}/phase-NN-{slug}/review.md` and existing project audit locations.

Each merged finding carries:

- **Severity** — critical / high / medium / low, with disagreements retained
- **Agreement** — participating models and per-model reporting runs
- **Location** — `file:line`
- **Messages** — the original findings; a concrete suggested fix is not guaranteed

**Agreement is a signal, not a verdict.** Read critical/high findings individually,
including single-model findings. Group proximity or identical synthetic replies
are not proof of independent corroboration or correctness.

## Step 6 — Triage with the developer

Go through critical/high findings together. For each: propose a separately
approved fix, defer to `findings.md` with a reason, or reject with a reason.
Review-only approval does not authorize editing source.

**Reject freely, silently never.** Reviewers are often wrong about a codebase they saw
in fragments. A rejected finding with a written reason is a good outcome; a finding
quietly dropped is a lost bug.

Every approved code fix requires appropriate verification (`atom check` for
phase Go implementation). Every deferral and rejection is recorded.

## Step 7 — Report

Present the actual report, participation/tooling limits, triage and what remains
open. Always persist findings/decisions, explicitly empty when appropriate.
Standalone stops without fixes, phase advancement or publication. Phase review
presents its existing gate; a next-step recommendation is not permission to act.

---

## Done when

- [ ] Exact scope, model/probe budget and output effects approved before calls
- [ ] Applicable gates passed, or approved missing/skipped/degraded evidence is explicit
- [ ] At least two **different** models reviewed, none of them the author of the code
- [ ] Actual supplied context and response/participation limits stated
- [ ] Findings grouped, severity-ranked, with messages/disagreements retained
- [ ] Critical/high findings, including single-model ones, triaged with developer
- [ ] Any separately approved fixes verified; no review-only source edits
- [ ] Review, findings and decisions persisted at approved locations

## Next

Standalone: stop at the review result.

Phase review: after its gate, recommend `/atom:ship` or the next phase's
`/atom:poc` when applicable. Do not execute it automatically.
