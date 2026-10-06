---
name: ship
description: 'Commit, push and open a pull request for a completed phase, with the pipeline artifacts linked. Keywords: ship, PR, pull request, commit, push, open a PR, submit.'
---

# /atom:ship

Gets a completed phase into review on GitHub.

## When to use

- A phase passed `/atom:tdd` and `/atom:review` and was approved

## Before you start

`atom check` must be green **right now**. Not "green when I last ran it" — re-run it.

---

## Step 1 — Review your own diff

Read the whole diff before committing. You are looking for what shouldn't be there:

- Debug prints, commented-out code, stray `TODO`s you added
- Files you didn't mean to touch
- Anything under `.atom/` that should be ignored
- Credentials, tokens, hostnames, real customer data

> **Never commit a secret.** If one has already been committed locally, stop and tell
> the developer — do not push and do not quietly amend it away, because the object
> still exists in the local history and needs deliberate removal.

## Step 2 — Commit

One phase, one commit, unless the developer wants otherwise.

```
<type>(<scope>): <what changed>

<why it changed, and what it enables>

Phase: NN-<slug>
Spec:  specs/<project>/phase-NN-<slug>/design-spec.md
POC:   specs/<project>/phase-NN-<slug>/poc-report.md
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`.

The body explains **why**. The diff already shows what.

Commit `specs/` and `poc/` alongside the code. They are the record of how the design
was arrived at, and they are worth more attached to the commit that used them than
sitting in a wiki.

## Step 3 — Push

> **Do not push unless the developer has asked you to.**

Committing locally is always fine. Pushing is a visible, shared action — it needs an
explicit instruction, not an inferred one. "Finish the phase" is not "push it".

```bash
git push -u origin <branch>
```

## Step 4 — Open the pull request

```bash
atom ship --pr
```

The description is assembled from the artifacts you already wrote:

```markdown
## What
{phase objective from the phase plan}

## Why
{purpose from the design spec}

## Evidence
POC verdict: {Confirmed}  →  specs/.../poc-report.md
{verbatim key output from the POC}

## Verification
{verbatim atom check output}

## Review
{n} models, {n} blockers resolved  →  specs/.../review.md

## Artifacts
- Design spec: ...
- Test spec:   ...
- Findings:    ...
- Decisions:   ...

## Notes for the reviewer
{anything genuinely uncertain, and what you deliberately did not do}
```

That last section is the one reviewers actually use. Fill it honestly — flagging your
own weak spot costs a sentence and saves a review round trip.

## Step 5 — Report

Give the developer the PR URL, what's in it, and what's still open in `findings.md`.

---

## Done when

- [ ] `atom check` green, re-run immediately before committing
- [ ] Diff read end to end; no debris, no secrets
- [ ] Commit message explains why, and links spec and POC report
- [ ] `specs/` and `poc/` committed with the code
- [ ] Pushed **only** after an explicit instruction to push
- [ ] PR description carries real evidence, not claims
- [ ] Open findings surfaced to the developer

## Next

The next phase's `/atom:poc` — or done, if that was the last phase.
