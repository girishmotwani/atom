# Design Spec — Phase 5: `atom ship`

**Status.** Approved at the developer gate — all six questions resolved.
**POC report.** [`poc-report.md`](poc-report.md)
**Behaviours.** B138–B157.

## Purpose

`atom ship` turns a finished phase into a pull request without asking the developer
to reassemble, by hand, facts that are already written down. The branch, the
commits, the spec, the POC report and the review are all on disk already. Ship's
job is to point at them and to attach evidence that the tree is green *right now*.

It is deliberately the smallest command in the tool. Everything it reports already
exists; ship writes nothing into the repository and creates nothing that a human
did not already create.

## Evidence Base

Six predictions were recorded before the spike ran. **Four were refuted.** The two
that matter most both changed this design rather than confirming it.

### What the POC proved

- **`gh` refuses to push.** `gh pr create` on a branch with no upstream aborts in
  1.4 s with `you must first push the current branch to a remote, or use the
  --head flag`. The plan had assumed `gh` would push as a convenience.
- **The argv limit belongs to the launcher, not the platform.** `gh` is a native
  `.exe`: ~32 KB of arguments is fine, ~64 KB raises `WinError 206` *before the
  process starts*. A `.cmd` shim routed through `cmd.exe` dies at ~8 KB instead.
- **A 70,000-character body was stored intact**, above the documented 65,536 cap,
  and `gh pr edit` exited 0 either way. The body had to be read back to learn what
  had actually been stored.
- **Windows text-mode writes inflate a body by ~2%** — 70,000 characters written,
  71,228 stored, the difference being one `\r` per line.
- **A duplicate `gh pr create` exits 1 and prints the existing PR's URL.**
- **An unauthenticated call returns `HTTP 401` and names the exact fix**,
  `gh auth login -h github.com`.

### What it overturned

The phase plan called this phase "low risk — shelling out to `git` and `gh`". That
description survived contact with the first question. Two design inputs that would
have been settled by assumption were settled by measurement instead, and both went
the other way.

It also produced a **near-miss worth recording**: the first `gh pr create` with
inherited stdin took **44.4 s** and died with a TCP write error — the exact
signature of Phase 4's stdin hang. Three repeats ran clean in ~1.4 s. It was a
network fault. Recording it would have been a false finding, and it was caught by
repetition rather than by judgement. **One observation cannot distinguish a
behaviour from a blip.**

## Scope

**In.** Preconditions; fresh `atom check` evidence; PR body assembled from links;
creating or updating the pull request; pushing behind an explicit flag.

**Out.** Merging. Responding to review. Any form of commit creation — see B157.
Branch management beyond the current branch. Reaching backwards over history
(branch-per-phase removed the need; see *What This Phase Does Not Settle*).

## The Pipeline

```
preconditions ──► resolve phase ──► fresh atom check
                                          │
                                          ▼
                   push (only with --push) ──► assemble body ──► create or update PR
```

The order is not arbitrary, and two separate constraints fix it.

**Push happens before the body is assembled**, because
the body links to artifacts at a specific commit, and a link to a commit the remote
has never seen is a 404. Assembling first and pushing afterwards would produce a PR
whose every link was broken until the moment it wasn't.

**The check happens before the push**, because a refusal should leave no trace. Ship
refuses on a failing gate unless `--allow-failing-checks` is given, and if the push
came first, that refusal would already have published the branch and set its
upstream — a command that declines to act would have changed the remote on its way
to declining. Ordering the check first costs nothing: it is local and fast, and the
push still happens in both cases that reach it, the passing run and the overridden
one. *(Found during implementation, not during the POC: the POC probed `gh` and the
check separately and never asked what their ordering implied.)*

## Preconditions

All preconditions are checked **before any work begins**, so a failure costs a
second rather than leaving a half-made pull request behind.

**B138.** `gh` is located and verified before anything else runs. Its absence is
reported as an unmet precondition naming the install, not as a failure partway
through. *(C15. The only `gh` on the development machine turned out to be the
Copilot app's bundled copy; a developer without that app has none.)*

**B139.** Ship refuses on a detached `HEAD`, and refuses when the current branch is
the base branch itself. There is nothing to open a pull request *from*.

**B140.** Ship refuses when the working tree is dirty, listing the modified files.

> **This is the one precondition not derived from the POC, and the reason matters
> more than the rule.** The body links to artifacts *at a commit*, and the fresh
> `atom check` runs against the *working tree*. When the tree is dirty those two
> are different states, so the PR would present evidence gathered from files that
> are not in the commit it points at. The refusal is what keeps the body's claims
> and the body's links describing the same thing.

**B141.** Ship requires an upstream branch. Without one, and without `--push`, it
refuses and prints the exact command that would fix it. *(C13.)*

**B142.** With `--push`, ship pushes the branch itself and sets the upstream. It
never delegates the push to `gh`, because `gh` does not do it. *(C13, Q5.)*

## Resolving The Phase

**B143.** The phase directory is derived from the branch name: `phase-05-ship`
resolves to `specs/<project>/phase-05-ship/`. `--phase` overrides it. If neither
resolves to a directory that exists, ship refuses and says which path it tried.

This is the first place branch-per-phase pays for itself beyond review: the branch
name is already the phase name, so nothing has to be passed or remembered.

**B144.** The artifacts are whatever files that directory contains. Missing
artifacts are **omitted from the body, never invented and never described as
pending**. A phase with no review report links to no review report; the body does
not editorialise about its absence.

## Evidence

**B145.** `atom check` runs **fresh**, at ship time, as part of the command. A
recorded result from an earlier run is not accepted, because the point of the
evidence is that it describes the commit being shipped.

**B145a.** When the repository is **not a Go module** — no `go.mod` at the root —
the gates are skipped and the body records *"not a Go module; no gates run"*. This
is **not** a check failure and does not trigger B147.

> Found while reading `check.py` rather than by the POC, which probed `gh` and
> never touched the check integration. `run_check` raises `NotAGoModuleError` on
> any directory without a `go.mod`, and **the Atom repository has none**, because
> Atom's own tooling is Python. B145 unqualified would have made `atom ship`
> unable to ship Atom — including this phase's own pull request.
>
> Treating the absence as a failure would be the wrong reading. `check.py` already
> settles the principle for the analogous case: *"SKIPPED and WARNING are both
> non-failures by design: a tree with no tests has not failed."* A tree with no Go
> module has not failed either. The body reports the absence as an absence, which
> is the honest description and also the useful one.

**B146.** The body carries a verdict table — one row per gate, bounded at five
rows. It does not carry the gates' full output. When B145a applies, the table is
replaced by the single recorded line.

**B147.** When the fresh `atom check` fails, ship **refuses to open or update the
pull request**, naming the failing gates. `--allow-failing-checks` overrides it.

**B147a.** When overridden, the failure is stated plainly in the body — the
override changes whether the PR opens, never what it claims. A PR that asserts
green while red is the confident falsehood Atom exists to prevent.

**B147b.** When overridden, ship still **exits non-zero**. This follows B136's
precedent: a partial review exits non-zero even though a report was produced. The
artifact existing and the run succeeding are different facts.

> The override is a flag rather than a prompt so that it survives in shell history.
> A decision to ship over a failing gate should be visible afterwards to the person
> reviewing, not just to the person who made it.

## The Body

**B148.** The body is **summary plus links**. It never embeds the content of an
artifact.

This is not a style preference. Phase 4's artifacts total **107 KB** against a
confirmed-intact ceiling of 71,228 characters and a real ceiling nobody has
measured. A body built by concatenation grows with the phase; a body built from
links grows with the *number of artifacts*, which is single digits. The design that
cannot outgrow the limit is preferable to the design that merely has not yet.

The summary is assembled from, in order:

| Part | Source | Bounded by |
|---|---|---|
| Title | The design spec's `H1`, else the branch name; `--title` overrides | one line |
| Why | The design spec's **Purpose** section, quoted | the section, however many paragraphs |
| What changed | Commit subjects on the branch | commit count |
| Evidence | The `atom check` verdict table (B146) | five rows |
| Artifacts | One link per file in the phase directory (B144) | file count |

**B149.** Artifact links point at the **pushed commit SHA**, never at a branch name
and never at the base branch. A link to `main` would 404 until merge — the files do
not exist there yet — and a link to a moving branch name would silently start
describing different content later.

**B150.** The body file is written with explicit `newline="\n"`, and any size
reported to the developer is the **character count**, not the file size. *(C11. The
two are different numbers, and the POC measured the difference at 1,228 characters
in 70,000.)*

**B151.** The body reaches `gh` by `--body-file`, never `--body`. *(C10. Arguments
have a launcher-dependent ceiling; files do not.)*

## Creating And Updating

**B152.** Ship queries for an existing pull request **before** attempting to create
one, and treats `gh`'s duplicate error as a fallback rather than the primary
signal. *(C12. Q1 showed the duplicate path works and prints the existing URL, but
depending on stderr wording to detect the normal re-run case makes the tool hostage
to `gh`'s phrasing.)*

**B153.** Re-running `atom ship` on a branch that already has a pull request
**updates the body** rather than failing. Re-running is the normal case, not the
edge case: every push of a fix should refresh the links to the new commit.

**B154.** `gh`'s own error text is passed through verbatim, not paraphrased. *(C14.
Both failure messages the POC produced were better than anything this tool would
invent — they name the exact next command to run.)*

**B155.** Empty stdin is passed to every `gh` call. *(C16.)*

> Justified as defence in depth, **not** by evidence of a hang. Q4 specifically
> refuted the hang: `gh` without a TTY aborts in 1.4 s. It costs nothing and the
> runner already does it. Recorded this way so a later reader cannot cite Q4 as
> support for something Q4 disproved.

## Failure Handling

**B156.** Ship reuses the exit codes established in Phases 1–3 rather than
introducing its own. An unmet precondition exits non-zero by the same route as any
other failure; there is no distinct "precondition" code.

**B157.** **Ship never creates a commit.** It assembles a pull request from commits
that already exist. A tool that commits on the developer's behalf decides what a
change *is*, and that is the developer's decision.

## Resolved At The Developer Gate

| # | Question | Answer | Trace |
|---|---|---|---|
| Q1 | Should ship commit the work? | **No.** Assembles from existing commits only | → B157 |
| Q2 | Should ship push? | **Only behind an explicit `--push`**; otherwise refuse with the command | → B141, B142 |
| Q3 | What goes in the body? | **Summary plus links** to artifacts in the repo | → B148–B151 |
| Q4 | Where does the check evidence come from? | **A fresh `atom check` at ship time** | → B145, B146 |
| Q5 | How are historical phases reviewed? | **Branch-per-phase**, adopted now; Phase 1 by checking out its end commit | → *Not settled*, below |
| Q6 | What happens when the fresh `atom check` fails? | **Refuse**, with `--allow-failing-checks` as a visible override | → B147, B147a, B147b |

Q6 was raised as an open question at this gate with three options. **A** was
chosen: refuse by default, override explicitly. The two rejected options are kept
below rather than deleted, so the next reader does not re-open a settled question.

| Rejected | Why not |
|---|---|
| Open the PR anyway, stating the failure in the body | A reasonable reading of "the tool reports, the developer decides" — but it makes the common accident (shipping red without noticing) silent, and the deliberate act (shipping red on purpose) indistinguishable from it |
| Open it as a draft, exit non-zero | Introduces draft-vs-ready as a concept this phase needs for nothing else |

## What This Phase Does Not Settle

| # | Open | Why it is left open |
|---|---|---|
| D13 | The real GitHub body cap above 71,228 characters | B148 makes the body small by construction, so the cap stops being load-bearing. Worth knowing, not worth blocking on |
| D14 | Whether `gh pr create --head` removes the need for an upstream | B142 pushes explicitly instead, which is clearer regardless of the answer |
| D15 | Argument limits on Linux and macOS | The launcher finding is Windows-measured. `--body-file` sidesteps it on every platform, so this is a portability question rather than a correctness one |
| D16 | Phase 1's bootstrap debt | Handled by checking out Phase 1's end commit and running `atom review` there. Needs no code, so it is not in this phase's scope |

## Size

~200 lines production.

*Phase 3 was estimated at 250 and came in at ~430 once its spike revealed what was
actually required. This phase's spike has already run, which should make the
estimate better — but every estimate in this plan so far has been low, and the
honest expectation is the upper half of that range rather than the lower.*
