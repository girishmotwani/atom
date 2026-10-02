# Treatment Evidence

The rules governing POCs that **compare**: two or more arms, one question, and a
claim that some treatment made a difference.

An ordinary spike asks "does this work?" A comparison spike asks "does this work
**better**?" That second question has a failure mode the first one does not, and it
is almost invisible from the results:

> **A treatment that never reached the model produces a clean, confident,
> entirely meaningless result.**

No error. No warning. No crash. Every arm completes, every number is plausible, and
the summary table looks exactly like a genuine null result.

---

## The Failure This Prevents

A comparison spike gave one arm a lookup tool — a script in the working directory
that the agent was instructed to run. The run completed with zero failures, and the
treated arm returned a confident answer describing how it had traced the code *"with
the prebuilt index."*

It had never run the index. Not once.

The agent harness required an explicit flag to execute commands without a human to
approve them. Without that flag every attempt was refused. **Reading and searching
still worked**, so the arms that only read looked perfectly healthy, and nothing in
the captured output ever mentioned that a capability was missing.

Worse: when told directly to run the query, the agent did not report being blocked.
It opened the tool's data files, reasoned out what the answer was probably going to
be, and presented a fabrication in the exact shape of real output — right format,
right style, wrong numbers.

Had that run gone to completion, it would have produced a refutation of a tool that
was never tested, and nothing in the recorded data would have revealed why.

---

## The Two Classes of Treatment

Every treatment is one of these. Only one is safe to assume.

| Class | Examples | Safe to assume? | Evidence required |
|---|---|---|---|
| **Carried in the prompt** | extra instructions, a background document, a changed system message, few-shot examples | **Yes** — it arrives by construction | Render the prompt and record its size or hash |
| **Requires the agent to act** | run a script, query an index, open a file, call an API, use an MCP server | **Never** | An independent record written by the treatment itself |

The distinction is not about how sophisticated the treatment is. It is purely about
whether delivery depends on the agent *choosing and succeeding at an action*. Prompt
text cannot fail to arrive. Everything else can.

### Class 1: prove delivery by rendering

Render the exact prompt each arm receives and record its size. The numbers should be
obviously, unmistakably different:

```text
prompt bytes [control]:   965
prompt bytes [treatment]: 135294
```

That is proof. A 134KB document cannot fail to reach a model that received a 135KB
prompt. Record these figures in the POC Report — they take one command and they close
the question permanently.

### Class 2: make the treatment log itself

The treatment must record its own use, to a destination the experiment controls. Not
the agent's narration of using it — the tool's own record that it ran.

```python
def record_usage(outcome: str) -> None:
    """Append one line per invocation so the experiment can measure real use.

    Observational only: it never changes what the caller sees, it stays off unless
    the environment names a destination, and any logging failure is swallowed so a
    bad log target can never break the tool itself.
    """
    destination = os.environ.get("TREATMENT_USAGE_LOG")
    if not destination:
        return
    try:
        with open(destination, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"argv": sys.argv[1:], "outcome": outcome}) + "\n")
    except Exception:
        pass
```

Three properties make this safe to add to a treatment under test:

- **Observational** — it changes nothing the agent can see, so it cannot alter the
  result it is measuring.
- **Opt-in** — silent unless the environment names a target, so the tool behaves
  identically outside the experiment.
- **Failure-proof** — a broken log destination must never break the tool, or the
  instrument becomes a confound.

Log **failed** attempts too. An agent that tried to use the treatment and could not
is a completely different finding from an agent that never tried.

---

## The Three Checks

Run all three before reading any result from a comparison spike.

| # | Check | Question | How |
|---|---|---|---|
| 1 | **Delivery** | Did the treatment reach the model? | Render the prompt; compare sizes across arms |
| 2 | **Action** | If it required an action, did that action happen? | Count entries in the treatment's own usage log |
| 3 | **Behaviour** | Did the treated arm behave differently *at all*? | Compare a behavioural measure against the control |

Check 3 is the backstop that catches what the first two miss, and it needs no
instrumentation. If a treatment genuinely reached the model and the model attended to
it, **something** about the output should move — length, shape, confidence, ordering,
how much it produced. If every observable is indistinguishable from the control,
suspect non-delivery before you conclude "no effect".

A worked example of check 3 settling the question. A background document was pasted
into the prompt, and the result was a small loss. Was the document ignored?

| Arm | Items named | Accuracy |
|---|---|---|
| control | 21.6 | 0.642 |
| treatment | **15.3** | 0.688 |

Naming 29% fewer items, with higher accuracy, across 100 trials per arm is not noise.
The document was read, and it made the agent **more cautious** — which happened to be
the wrong trade for that task. That is a real finding about the treatment, and it is
only distinguishable from "the document never arrived" because check 3 was run.

---

## The Agent's Claim Is Not Evidence

Never accept the agent's own account of what it did.

An agent that cannot perform an action does not reliably say so. It may describe the
action in the past tense, produce output in the correct shape for a tool it never ran,
and present the whole thing with complete confidence. This is not rare and it is not a
bug you can detect by reading the reply — a fabricated tool result looks exactly like
a real one.

| Not evidence | Evidence |
|---|---|
| "I queried the index and found…" | 42 lines in the tool's usage log |
| "Using the provided document, I…" | `prompt bytes [treatment]: 135294` |
| A reply formatted like tool output | The tool's own record that it executed |
| No errors in the run | A measured behavioural difference from control |

> **"It ran without errors" is not evidence that anything ran.**

---

## Null Result or Never Applied?

These two look identical in a summary table and mean opposite things:

| What happened | What the table shows | What it means |
|---|---|---|
| Treatment applied, didn't help | treatment ≈ control | **A real finding.** Report the refutation |
| Treatment never applied | treatment ≈ control | **A broken experiment.** Fix and rerun |

You cannot tell these apart after the fact from the results alone. The evidence has to
be collected *during* the run, which is why the checks are a precondition for reading
the numbers rather than a step in analysing them.

---

## Recording It

The POC Report for a comparison spike must carry an **Evidence of Treatment** section,
before any results:

- Rendered prompt sizes for every arm.
- Usage counts for any treatment requiring an action, plus which operations were used.
- The behavioural measure showing the treated arm differed from control.
- Anything that failed these checks, and what was changed to fix it.

If the checks were run **after** calls had already been made, say so plainly. Evidence
gathered after a result is known is weaker than evidence gathered before, and the
report should let the reader apply that discount themselves.

---

## Do Not Over-Apply This

This is for spikes that **compare arms and attribute a difference to a treatment**.

A single-arm spike answering "can this be done at all?" needs none of it. The question
there is whether the program works, and the program either ran and printed something
or it did not — which [verification.md](verification.md) already covers.

The trigger is the word **"because"**. The moment the report is going to say *"arm B
did better **because** of the treatment"*, every one of these checks is owed.
