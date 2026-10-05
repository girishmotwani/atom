---
name: atom-discover
description: 'Turn a vague problem statement or market requirements document into a concrete, falsifiable POC Brief by interviewing the developer. Keywords: discover, requirements, MRD, problem statement, what should we build, scope, kick off.'
---

# atom-discover

The entry point. Takes a problem statement — an MRD, a ticket, a paragraph in chat —
and produces a **POC Brief**: a contract for the one thing the first spike must prove.

This skill does not design and does not code. It asks.

## When to use

- A new project or feature is being started from a problem description
- The developer has a requirement but no agreed scope
- An earlier POC was **refuted** and the plan needs re-forming around what was learned

## Before you start

Read, in this order:

1. [AGENTS.md](../../AGENTS.md)
2. [anti-rationalization.md](../atom/references/anti-rationalization.md)
3. [poc-discipline.md](../atom/references/poc-discipline.md)
4. [human-gates.md](../atom/references/human-gates.md)

---

## Step 1 — Explore before asking

Read the repository first. Every question you ask that the code could have answered
spends the developer's attention on something you could have found yourself.

Establish, from the code:

- Module path, Go version, dependency set (`go.mod`)
- Existing packages and what they are responsible for
- How the project builds, tests and runs
- Conventions already in use — error handling, logging, configuration, concurrency
- Anything already attempting to solve this problem

Then run `atom check --no-race` to confirm the tree's baseline **before** you change
anything. This initial untouched-tree check skips race detection; it does not replace
the full `atom check` required for final verification. A pre-existing failure that
you discover later will look like something you caused.

Record the build/test commands — every downstream skill uses them rather than
re-detecting.

## Step 2 — Interview the developer

**One question at a time.** Wait for each answer before forming the next question —
the answers should change what you ask next. A pre-written list of six questions is
a form, not an interview.

Work toward these, in roughly this order, skipping anything the code already told you:

| Area | What you need to come away with |
|---|---|
| Outcome | What becomes possible that isn't possible today |
| Users | Who calls this, and from where |
| Scale | Concrete numbers — request rates, data sizes, latency targets |
| Constraints | Dependencies that are fixed, things that must not change |
| Unknowns | What the developer is *not sure* will work |
| Acceptance | How they will judge that this is done |
| Non-goals | What they explicitly do not want |

The single most valuable question in this skill is some form of:

> **"What part of this are you least sure will work?"**

Developers usually know exactly where the risk is. That answer normally *is* the POC
question. Ask it early, then probe until it is specific enough to be falsifiable.

### Push back when the code disagrees

If the developer states something the repository contradicts, say so and show the
contradiction. Quietly designing around a wrong premise wastes the whole pipeline.

## Step 3 — Name the riskiest unknown

From everything gathered, pick **one** unknown to spike. Rank by what would be most
expensive to discover late:

1. **Feasibility** — is this possible at all here?
2. **Performance** — does it hold at the stated scale?
3. **Integration** — does the external thing behave as documented?
4. **Ergonomics** — is the API pleasant?

Ergonomics can be redesigned cheaply. Feasibility cannot. Spike upward from the top of
that list, not from whatever is most interesting to build.

Write the question as one falsifiable sentence. Test it: *could running a program
return a clear no?* If no, it is not yet a POC question — sharpen it and check with
the developer.

## Step 4 — Write the POC Brief

Fill in [poc-brief.md](../atom/templates/poc-brief.md) at
`specs/{project}/poc-brief.md`.

Pay particular attention to the **Scope** section. Stating what the POC will *not*
cover is what stops its result being over-read later.

Create `specs/{project}/findings.md` and `specs/{project}/decisions.md` now, from
their templates, even if both are empty. Write "No findings." and "No deviations from
instructions." respectively. They are updated as the pipeline runs, not reconstructed
at the end.

## Step 5 — Gate

Present the brief per [human-gates.md](../atom/references/human-gates.md):
what was produced and where, the question you chose, why you chose it over the other
candidates, and one specific question.

**End your turn. Wait.**

Approval here authorises building *this* spike to answer *this* question. It does not
authorise designing, planning phases, or writing production code.

---

## Done when

- [ ] Repository explored; build and test commands confirmed by running them
- [ ] `atom check --no-race` run on the untouched tree and its result recorded
- [ ] Developer interviewed one question at a time
- [ ] Exactly one falsifiable POC question chosen, with the alternatives named
- [ ] `poc-brief.md` complete, including explicit non-scope
- [ ] `findings.md` and `decisions.md` exist
- [ ] Brief presented at a gate and explicitly approved

## Next

`atom-poc` — build and run the spike.
