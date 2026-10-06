# Human Gates

A gate is a full stop in the Atom pipeline. You present the artifact, end your
turn, and wait for the developer to reply.

> A gate is not a notification. It is the point where you stop doing work until
> the developer decides what the evidence authorises.

Atom is collaborative because the expensive decisions are not purely technical.
The developer owns product intent, acceptable trade-offs, and whether the next
step is worth doing.

---

## Gate Definition

At a gate, do exactly this:

1. Present the artifact.
2. Ask one specific question.
3. End your turn.
4. Wait for the reply.

Do not continue in the same turn. Do not start the next phase while also saying
"please review". Do not assume silence means yes.

```text
Produced: specs/cache/poc-report.md
Question: Does this POC sufficiently prove the file lock approach, or should I
spike cross-process contention before writing the phase plan?
```

---

## Gate Presentation Format

Use the same four-part shape every time.

| Part | Include | Avoid |
|---|---|---|
| 1. Artifact | What was produced and where it is on disk, as a path | Vague names like "the spec above" |
| 2. Decisions or findings | Only the key items the developer must weigh in on | A full summary of every section |
| 3. Surprise or uncertainty | Anything that changed your confidence or exposed a risk | Hiding ambiguity to look decisive |
| 4. One question | The exact decision needed to proceed | Multiple questions or a broad "thoughts?" |

Template:

```text
Produced: specs/<project>/<artifact>.md
Decision needed: <one or two bullets>
Surprise/uncertainty: <one bullet or "None">
Question: <one specific question>
```

The artifact can contain the long detail. The gate message should contain only
what the developer needs to make the next decision.

---

## Pipeline Gates

| Gate | What you present | What a "yes" authorises |
|---|---|---|
| After POC Brief | `specs/<project>/poc-brief.md`: the falsifiable question, risk ranking, planned command, expected evidence | Writing and running that POC only |
| After POC Report | `specs/<project>/poc-report.md`: verdict, verbatim output, limits, plan impact | Proceeding to phase planning if Confirmed; returning to discovery if Refuted or Inconclusive |
| After Phase Plan | `specs/<project>/phase-plan.md`: ordered phases, dependencies, per-phase risks, gate sequence | Starting phase 1 only |
| After each phase's POC Report | `specs/<project>/phase-NN-<slug>/poc-report.md`: phase risk, verdict, verbatim output, limits | Writing that phase's design spec when the verdict is Confirmed |
| After each phase's Design Spec | `specs/<project>/phase-NN-<slug>/design-spec.md`: public behaviour, interfaces, error paths, concurrency, test obligations | Implementing that exact spec with TDD |
| After each phase's TDD implementation | The diff, `atom check` output, findings, decisions, and any review notes | Marking that phase done and moving to the next phase or shipping |

A yes never authorises unbounded work. It authorises the next named step against
the artifact as presented.

---

## Research Loops

Some POCs are not a single spike but a **series of experiments**, where each result
decides what the next experiment should be. Measuring whether a technique works,
comparing approaches, or chasing down why something underperforms all take this shape.

A research loop is the easiest place in Atom to drift, because every individual step
feels like "still finishing the POC". It is not one POC. **Each experiment is its own
POC and carries its own two gates.**

| Gate | What you present | What a "yes" authorises |
|---|---|---|
| Before an experiment runs | The question it answers, the conditions, what result would count as a yes and what would count as a no, and what it will cost | Running that experiment only |
| After an experiment finishes | The result, whether it matched your prediction, and what you now think the next experiment should be | Deciding the next step together — never automatically running it |

Rules specific to research loops:

- **A result that changes the plan is a gate, not a paragraph.** If an experiment
  refutes the approach, exposes a flaw in the measurement, or makes the next step
  obvious, stop and say so. "Obvious" is exactly when you are most likely to be wrong.
- **Discovering the experiment cannot answer the question is a full stop.** Do not
  silently redesign the benchmark and carry on. The redesign is the developer's
  decision, because it changes what is being claimed.
- **Changing what you measure is a material change.** New benchmark, new scoring
  method, new ground truth, or repairing the thing being measured — all re-gate.
- **Batches of parallel agents are spend.** Gate before launching a batch, not after
  the results are in.

State the cost in the pre-run gate, in terms the developer can weigh — how many
agents, roughly how long, and what is thrown away if it is wrong.

---

## Existence Is Not Approval

An artifact already being on disk never auto-satisfies a gate.

Approval is an event in the conversation, not a file. A repository can contain:

- An old spec that predates the current POC evidence.
- A draft report nobody reviewed.
- A phase plan from a different scope.
- A correct file that still needs a trade-off decision.

If you find an existing artifact, inspect it, compare it to the current work,
and present it at the gate. Do not treat its presence as permission to continue.

---

## Approval Is Scoped

Approval does not accumulate across gates.

| Approval | Authorises | Does not authorise |
|---|---|---|
| "Yes" to a POC Brief | Building and running the named POC | Writing the design spec |
| "Yes" to a POC Report | Planning from that evidence | Ignoring a later failed phase POC |
| "Yes" to a Design Spec | Implementing that exact spec | Implementing a materially changed spec |
| "Ship it" after a phase | Completing that reviewed phase | Skipping the next phase's gates |

If the artifact changes materially after approval, re-gate. Material changes
include new public behaviour, different error semantics, new concurrency rules,
new dependencies, or a different POC verdict.

---

## Standing Waivers

A developer may say: "just go, don't ask me again." Honour it only as an explicit
standing waiver, and make its scope visible.

Record in `decisions.md`:

```markdown
## Standing Gate Waiver

- Scope: phase POC gates for phases 2-4 of `specs/cache/phase-plan.md`
- Given by: developer in conversation on 2026-09-14
- Limits: does not cover Refuted or Inconclusive POCs, blocked steps, or material spec changes
- Reason: developer requested uninterrupted execution after approving the phase plan
```

Even with a waiver, you still surface:

- Refuted POCs.
- Inconclusive POCs.
- Blocked steps.
- Material design changes.
- Verification failures.

Those events change the plan rather than merely continuing it.

---

## When Blocked

A blocker is a gate with less certainty. State it plainly and stop.

Use this shape:

```text
Blocked: go test ./... fails before my change in package ./internal/store.
Options:
1. Fix the pre-existing failure first.
2. Narrow validation to ./internal/cache for this phase.
Recommendation: option 1, because the failing package owns the same persistence path.
Question: Should I fix the existing failure before continuing?
```

Never pick silently when the choice changes scope, risk, or developer intent.
If you can make a harmless local investigation without changing the plan, do it
before asking. If the blocker requires a trade-off, ask and stop.

---

## Non-Interactive or CI Contexts

When no human is available, do not simulate approval. There is no such thing as
self-approval at a human gate.

Required behaviour:

1. Halt at the gate.
2. Write the reason into `decisions.md`.
3. Exit non-zero.

Example `decisions.md` entry:

```markdown
## Halted at Human Gate

- Gate: after phase 1 POC Report
- Reason: non-interactive run had no developer available to approve the report
- Next action: present `specs/cache/phase-01-locking/poc-report.md` to the developer
```

Example CI output:

```bash
atom phase show
# phase-01-locking: waiting_for_gate after poc-report
exit 2
```

Stopping is the correct outcome. Continuing would create work from approval that
did not happen.
