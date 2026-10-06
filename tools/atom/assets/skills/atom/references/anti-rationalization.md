# Anti-Rationalization

Agents do not usually skip a step because they have proven the step is safe to
skip. They skip because continuing feels locally reasonable, then generate a
reason after the decision.

This file names those reasons before you need them. When one of these thoughts
appears, treat it as a signal to stop and follow the required action instead.

> Skipping feels efficient in the moment because the cost is delayed until the
> design is wrong, the test is biased, or the developer loses trust.

---

## The Table

| The thought | Why it's wrong | Required action |
|---|---|---|
| "This is simple enough that a POC is unnecessary" | Simple is a judgement, not evidence. Atom exists because agents routinely misjudge what is simple before running code. | Write the smallest POC that answers the risky question, or record a specific skipped-POC reason in `decisions.md` and gate it. |
| "I can see from reading the code that this will work" | Unrun code proves nothing. Reading can show plausibility; only execution shows behaviour. | Run the code. Capture the command and output in the relevant report. |
| "I'll write the POC after the design, to validate it" | That reverses the pipeline. The POC is not a stamp on the design; it is the evidence that shapes the design. | Stop designing. Write the POC first, then update the design from what the POC actually showed. |
| "The POC basically worked, the remaining failure is unrelated" | "Basically" launders inconclusive evidence into confirmation. A failure is unrelated only when you can prove its cause and scope. | Mark the POC Confirmed only if the stated question was answered. Otherwise mark it Inconclusive or Refuted and say why. |
| "I'll write the tests after the implementation, they'll be the same tests" | They will not. Tests written after code tend to describe what the code does, not what the spec requires. | Delete or set aside the production change. Write the failing test first, watch it fail for the right reason, then implement. |
| "The developer is busy, I'll proceed and they can review at the end" | That skips the gate. End-review catches mistakes after they are expensive and after later work depends on them. | Present the artifact, ask one question, end your turn. Continue only after a reply or an explicit standing waiver. |
| "The developer said go ahead earlier, that covers this gate too" | Approval is scoped. A yes to one artifact is not a yes to later artifacts, changed artifacts, or new uncertainty. | Gate the current artifact. If relying on a standing waiver, quote its scope in `decisions.md`. |
| "I'll note this in findings.md at the end so I don't lose flow" | Findings written from memory lose the detail that made them worth recording: the file, command, symptom, and reason. | Record the finding immediately, even as one rough sentence. Refine it later if needed. |
| "findings.md would be empty so I'll skip creating it" | An explicit "No findings" is evidence the check happened. Absence is ambiguous: maybe no findings, maybe no check. | Create `findings.md` and write "No findings." when that is true. |
| "This deviation is too small to record in decisions.md" | Small deviations compound. The developer cannot audit judgement they cannot see. | Record the deviation, the reason, and the consequence in `decisions.md`. |
| "The existing design doc covers this, so the design gate is already satisfied" | Existence is not approval. A file on disk is not an event in the conversation, and it may not cover the current evidence. | Re-read the design, compare it to the POC evidence, present it at the gate, and wait. |
| "I'm running low on context, I'll skip the verification step" | Context pressure makes verification more important, not less. Skipping at the limit is how false claims enter the record. | Compact or narrow context, reload required references, then run verification. |
| "The test is failing because the test is wrong" | Sometimes true, usually not. The burden of proof is on the claim that the test is defective. | First confirm the test expresses the spec. If you change it, record the reason in `decisions.md` and rerun it. |
| "I already know Go conventions, I don't need to re-read go-style.md" | Atom deliberately deviates from terse idiomatic Go where clarity benefits future readers and agents. Memory of Go idiom is not enough. | Re-read [go-style.md](go-style.md) before editing Go code or reviewing Go style. |
| "Phase 3 is just wiring, it doesn't need its own spec" | Wiring still defines contracts, ownership, error paths, and cancellation behaviour. If it can break, it needs a spec. | Write a short phase spec, or record the precise reason the previous spec already governs the wiring. Gate that decision. |
| "I'll fix the lint/vet failure later" | Later means the failure becomes background noise. A known failing check makes every later verification ambiguous. | Fix it now or record the blocker, stop, and ask the developer how to proceed. |

---

## The Tell

Rationalization has a recognizable shape. The reasoning arrives after you
already want to skip.

Common signals:

- You are estimating instead of running.
- You are describing what code *would* do, not what code *did*.
- You use softening words: "essentially", "basically", "probably", "should be fine", "straightforward".
- You are trying to preserve flow rather than preserve evidence.
- You are treating the developer's future review as permission to skip the current gate.
- You are calling a failed or partial run "good enough".
- You are relying on memory of a reference instead of reading the current file.

| Signal | Translation | Safer move |
|---|---|---|
| "Should pass" | You have not run it | Run the command |
| "Basically confirmed" | The evidence is not clean | Mark Inconclusive |
| "Straightforward wiring" | You have not named the risk | Write the small spec |
| "I'll document later" | You are about to lose detail | Write the finding now |

Bad:

```text
The retry path should be fine because it follows the existing helper.
```

Good:

```text
go test ./internal/retry -run TestClient_RetryAfterReset_Succeeds
ok  github.com/example/project/internal/retry  0.214s
```

---

## When Skipping Is Legitimate

Skipping sometimes is correct. Atom does not require ritual; it requires
specific, reviewable judgement.

A legitimate skip passes all three tests:

1. You can state a specific, checkable reason.
2. You record it in `decisions.md` at the time.
3. You tell the developer at the next gate.

| Bad reason | Good reason |
|---|---|
| "It seemed straightforward." | "Phase 2's POC already proved the codec round-trips; this phase only moves the call site." |
| "The tests are obvious." | "The existing table covers the new parser branch because the input differs only in whitespace normalization; added case `trims leading spaces`." |
| "The design already exists." | "The approved phase spec already includes this call-site move and no public contract changed." |

Skipping is never silent. If the skip is still defensible after being written
plainly, it can survive developer review. If it looks weak in `decisions.md`, do
not skip.

---

## Re-read This

Context compaction erases prior file reads. The summary may say this file was
read, but it does not carry every rule, table, and warning forward with the same
force.

Re-read this file:

- After any context compaction.
- At each pipeline step transition.
- Before deciding a POC, spec, test, gate, or verification step can be skipped.

A summary of a rule is not the rule. Reload the actual file, then continue.
