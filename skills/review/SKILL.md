---
name: review
description: 'Multi-model review of a Go diff, merged into one deduplicated report with severities. Keywords: review, code review, multi-model review, review my changes, review the diff, critique.'
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

- After `/atom:tdd` for a phase
- Before `/atom:ship`
- Any time a diff is large enough that reading it once isn't enough

## Writing artifacts

Send complete review reports, findings, and decisions as UTF-8 standard input to
`atom-write-artifact <relative-path>`. Treat any refusal or non-zero exit as a blocker;
never bypass it with a generic editor or another shell command.

## Step 1 — Establish the diff

```bash
atom review --base main          # branch diff
atom review --staged             # staged changes
atom review --working            # working tree
```

Review the diff **with** the surrounding file, not the hunks alone. Context-free hunk
review produces confident nonsense about code that is already handled ten lines up.

## Step 2 — Let the toolchain answer first

No separate command: the gate runs inside `atom review`, before the models.

Before a single model is called, Atom runs `go build`, `go vet`, `gofmt`, `go test`
and `go test -race`, plus `staticcheck`, `errcheck` and `govulncheck` when they are
installed.

Review formatting checks whole surviving changed Go files from the selected
working-tree, staged or committed-branch snapshot, using stdin without rewriting
source. Untouched files are not scanned. The report names checked paths and
outside-module or nested-module exclusions; zero applicable files means SKIPPED,
not a formatting pass. Other review checks retain their existing module-wide
scope, and standalone `atom check` retains module-wide formatting.

**A failing required gate stops the review.** Reviewing code that does not compile, or
that `go vet` already objects to, spends model attention on a question that has an
exact free answer — and the findings would be about code you are about to change
anyway.

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
errors. Missing, mismatched or changed executable identities and required failures
still block review; no compiler-text-based continuation is permitted.

## Step 3 — Run the models

```bash
atom review --base main --models <model-a>,<model-b>,<model-c>
```

Each model reviews each changed file independently, in parallel. They do not see each
other's findings — shared context would collapse them into agreement, which is exactly
the diversity you are paying for.

Models are resolved from `.atom/config.json`. Never hard-code a version; see
[model-guidance.md](../atom/references/model-guidance.md).

## Step 4 — What reviewers look for

Everything the toolchain decides has already been decided and excluded. What is left is
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

## Step 5 — Merge

Findings are deduplicated by file, line and substance, then merged into one report at
`specs/{project}/phase-NN-{slug}/review.md`.

Each merged finding carries:

- **Severity** — Blocker / Major / Minor / Nit
- **Agreement** — how many models raised it
- **Location** — `file:line`
- **The finding**, and a concrete suggested fix

**Agreement is a signal, not a verdict.** Something all three models flagged is
probably real. Something one model flagged may be the one that understood the code —
single-model findings at Blocker or Major severity get read individually, never
dismissed for lacking consensus.

## Step 6 — Triage with the developer

Go through Blockers and Majors together. For each: fix now, defer to `findings.md`
with a reason, or reject with a reason.

**Reject freely, silently never.** Reviewers are often wrong about a codebase they saw
in fragments. A rejected finding with a written reason is a good outcome; a finding
quietly dropped is a lost bug.

Every fix re-runs `atom check`. Every deferral and rejection is recorded.

## Step 7 — Report

Present the merged report, the triage outcome, and what remains open.

---

## Done when

- [ ] The toolchain gate passed before any model was called
- [ ] At least two **different** models reviewed, none of them the author of the code
- [ ] Every changed file reviewed with its surrounding context
- [ ] Findings merged, deduplicated, severity-ranked
- [ ] Single-model Blockers and Majors read individually, not dismissed
- [ ] Blockers and Majors triaged with the developer
- [ ] Fixes verified by a fresh `atom check`
- [ ] Deferrals in `findings.md`, rejections recorded with reasons

## Next

`/atom:ship`, or the next phase's `/atom:poc`.
