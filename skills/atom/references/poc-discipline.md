# POC Discipline

The rules governing Atom's first beat: **PROVE**.

---

## What a POC Is

A POC is a **throwaway Go program that answers exactly one uncomfortable question.**

It is not a prototype, not a skeleton, not "v0 of the real thing". It is an
experiment. Its only job is to convert an assumption into a fact before that
assumption gets baked into a design.

A good POC:

- Fits in one `main.go`, or very close to it.
- Runs from the command line and prints what it found.
- Takes minutes to hours, never days.
- Is allowed to be ugly. Hardcoded values, no error handling, `panic` on failure — fine.
- Gets **deleted or archived**, never promoted into production code.

## What a POC Is Not

| Not this | Why |
|---|---|
| A skeleton of the final architecture | You don't know the architecture yet — that's the point |
| A feature behind a flag | That's an increment, not an experiment |
| A design document with code samples | Unrun code proves nothing |
| A test suite | Tests verify known behaviour; a POC discovers unknown behaviour |
| Production-quality code | Polish spent on throwaway code is waste |

---

## Choosing the Question

Before writing a line, state the question in one sentence. It must be **falsifiable**.

| Weak question | Strong question |
|---|---|
| "Will this design work?" | "Can a single goroutine drain this channel fast enough to keep p99 under 10ms at 50k msg/s?" |
| "Is library X good?" | "Does library X's client survive the upstream closing the connection mid-stream, or does it deadlock?" |
| "Should we use generics here?" | "Does a generic store avoid the `interface{}` allocation that showed up in the profile?" |

If you cannot phrase the question so that running the program yields a clear yes or
no, you are not ready to write the POC. Go back to the developer and ask.

### Ranking risk

When several things are uncertain, spike the one that would be **most expensive to
discover late**. Usually that is, in order:

1. **Feasibility** — can this be done at all with this runtime/library/protocol?
2. **Performance** — does it hold at the target scale?
3. **Integration** — does the external thing behave the way its docs claim?
4. **Ergonomics** — is the API pleasant to call?

Ergonomics can be redesigned cheaply. Feasibility cannot.

---

## Running It

**A POC that has not been executed does not exist.** Reading the code and concluding
it would work is the exact failure mode Atom prevents.

Every POC must produce real terminal output. Paste it into the POC Report verbatim.
If the POC measures something, the numbers in the report are the numbers the program
printed — never estimates, never "approximately".

```bash
atom poc new <slug>      # scaffold poc/<slug>/ with go.mod, main.go, README
atom poc run <slug>      # go vet + go build + go run, captures output
```

---

## Comparison POCs

A spike that compares arms carries a failure an ordinary spike does not: the
treatment may never have reached the model. There is no error when this happens —
every arm completes and the result looks exactly like a genuine null.

Before reading any result from a comparison spike, work through
[treatment-evidence.md](treatment-evidence.md). The short version:

- A treatment carried **in the prompt** arrives by construction. Render the prompt and
  record its size.
- A treatment the agent must **do something** to use — run a script, query an index,
  call an API — can fail silently and must log its own use.
- **The agent's account of what it did is not evidence.** A blocked agent may describe
  the action in the past tense and fabricate output in the right shape.

---

## Evaluating It

A POC has three possible outcomes. **All three are successes.**

| Outcome | Meaning | What happens next |
|---|---|---|
| **Confirmed** | The assumption held | Proceed to `/atom:spec`, citing the evidence |
| **Refuted** | The assumption was wrong | Excellent — you saved the design. Return to `/atom:discover` with what you learned |
| **Inconclusive** | The POC didn't isolate the question | Sharpen the question and spike again. Do **not** proceed on a shrug |

An inconclusive POC treated as a confirmation is worse than no POC at all, because it
launders a guess into the design as if it were evidence.

> Refuting your own plan is the highest-value outcome in the whole pipeline. Report it
> with enthusiasm, not apology.

---

## Writing It Up

Fill in [poc-report.md](../templates/poc-report.md). The report must contain:

- The question, restated exactly as it was asked.
- The verdict: Confirmed / Refuted / Inconclusive.
- **Verbatim command output.** Not paraphrased.
- What this changes about the plan.
- What the POC deliberately did *not* cover, so nobody mistakes its scope later.

That last point matters. A POC proving a happy path at 1k req/s is not evidence about
error paths at 100k req/s, and the report must say so out loud.

---

## After the POC

Move the spike to `poc/<slug>/` and leave it there. It is documentation now: the next
person who doubts the decision can re-run it.

**Do not copy POC code into the implementation.** The POC earned its shortcuts by
being disposable; production code has to earn its shape from the spec and the tests.
Take the *knowledge* forward, not the source.

---

## Per-Phase POCs

The project-level POC proves the project is possible. Each phase then gets its own,
smaller POC when *that phase's* specific risk remains unproven. Choose the evidence
step using the recommendation guidance below, not a blanket spike requirement.

A phase POC may legitimately be skipped when the phase carries **no technical
uncertainty** — pure refactoring, mechanical wiring, or a pattern already proven by an
earlier phase's POC in the same codebase.

Skipping is a decision, not a default:

1. State in `decisions.md` which phase was skipped and the specific reason.
2. Confirm it with the developer at the phase gate.

"It seemed straightforward" is not a reason. "Phase 2's POC already proved the codec
round-trips, and this phase only moves the call site" is a reason.

---

## Recommend The Evidence Step, Let The Developer Decide

This is guidance for existing skills, not a new command, automatic classifier,
risk score, or compliance monitor. It does not change runtime phase/gate checks.
The full PROVE → DESCRIBE → BUILD path remains the default for unproven technical
work. A recommendation is never approval to implement, install tools, spend on
model calls, publish, or bypass an applicable gate.

### Assess evidence before recommending

Read the repository and available artifacts first. If intent or acceptance is
missing, ask one focused discovery question; do not guess the desired outcome.
Once intent is clear, distinguish observed facts from assumptions:

- What behavior is new or still uncertain? Name the unknown rather than calling
  the task "simple" or "low risk".
- What evidence already exists, and was it approved? Identify its source,
  assumptions, environment and covered behavior.
- Does that evidence still apply to this change? A proven helper does not prove
  new caller wiring, changed arguments, or different external behavior.
- What could fail if the assumption is wrong, and how costly or reversible would
  that be? Consequences guide which unknown to investigate first, not a score.

### Recommend one bounded next step

These are reviewable distinctions, not an exhaustive taxonomy. When a task mixes
categories, address the uncovered material uncertainty rather than choosing the
cheapest label.

| Evidence state | Recommendation | Boundary |
|---|---|---|
| Intent or acceptance is missing | Continue discovery, one question at a time | An interview does not prove technical feasibility |
| Material technical uncertainty has no applicable evidence | Run a bounded, falsifiable POC before design | Name Confirmed, Refuted and Inconclusive outcomes before running |
| A defect reproduces and its cause/fix scope is understood | Start with a failing regression test as proof for that defect | A separate spike is needed only for another material unknown; production changes still require an approved spec and TDD |
| An approved POC/spec covers the same assumptions and behavior | Reuse that evidence and validate the changed boundary | Cite the artifact and limits; helper proof does not prove caller integration |
| Work is already specified with no new uncertainty | Run relevant validation for the changed contract | Do not manufacture a POC to repeat known checks or relax approval gates |
| Documentation only, with no behavior/API/configuration change | Check factual claims against verified behavior and run relevant documentation checks | Do not invent a Go experiment or claim text checks prove code correctness |

For reuse, name the approved artifact, behavior and assumptions it covers, what it
does not cover, and the validation for the current boundary. A missing, unapproved,
or inapplicable artifact is not reuse evidence. Changed assumptions return the task
to a discovery/POC/spec decision rather than being silently treated as routine.
Record the evidence choice and any skipped spike in `decisions.md`; preserve the
existing design-spec and implementation approval gates.

### Present the recommendation

State the observed evidence and its source, remaining uncertainty, one bounded
recommended action with its reason, and the relevant alternative with what it
would or would not establish. Use plain language, not opaque route codes.

When a gate or preference decision is needed, present the applicable artifact and
ask one specific question under [human-gates.md](human-gates.md). Stop before the
gated work. If the developer rejects the recommendation, stop and ask which path
they prefer; do not reinterpret silence or earlier approval as consent.
Documentation-only work retains the repository's normal review/approval
expectations; this policy adds no enforced gate.

### Illustrative cases and evidence limits

- A new toolchain selector with unknown workspace/version interactions needs a
  focused POC before design.
- An isolated, reproducible normalization defect can begin with its failing
  regression; this does not authorize implementation before spec approval.
- Wiring a caller to a proven helper can reuse approved helper evidence, but
  still needs focused validation of arguments and error propagation.
- A verified command-example correction needs documentation review, not a spike.

Two models agreed on these four synthetic cases under supplied route definitions.
That supports consistency in that sample only, not policy correctness,
completeness, or independent discovery of the factors. Discovery and routine
validation were not exercised. Required decision markers in model responses did
not test an actual developer's acceptance, rejection, or whether a workflow waits.
Written guidance is not a technical guarantee of developer control.
