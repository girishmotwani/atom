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
smaller POC proving *that phase's* specific risk.

A phase POC may legitimately be skipped when the phase carries **no technical
uncertainty** — pure refactoring, mechanical wiring, or a pattern already proven by an
earlier phase's POC in the same codebase.

Skipping is a decision, not a default:

1. State in `decisions.md` which phase was skipped and the specific reason.
2. Confirm it with the developer at the phase gate.

"It seemed straightforward" is not a reason. "Phase 2's POC already proved the codec
round-trips, and this phase only moves the call site" is a reason.
