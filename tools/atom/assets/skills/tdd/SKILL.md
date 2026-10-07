---
name: tdd
description: 'Implement one phase test-first in Go: red, green, refactor, against an approved design spec. Keywords: TDD, test driven, test first, implement, red green refactor, build the phase, write the code.'
---

# /atom:tdd

The **BUILD** beat. Implements one phase from its approved design spec, test-first.

## When to use

- A phase design spec exists and has been approved

## Never use when

- No approved spec exists. Implementing an unapproved design means the developer
  reviews finished code instead of a reversible decision. Go to `/atom:spec`.

## Writing artifacts

Send complete test specs, findings, decisions, and reviewable TDD evidence as UTF-8
standard input to `atom-write-artifact <relative-path>`. Treat any refusal or non-zero
exit as a blocker; never bypass it with a generic editor or another shell command.
This command is never used for production code or tests; those retain the normal
editing and approval flow.

## Before you start

Read:

1. [tdd-discipline.md](../atom/references/tdd-discipline.md) — **the authority for this skill**
2. [what-the-toolchain-proves.md](../atom/references/what-the-toolchain-proves.md) — which tests are worth writing
3. [go-style.md](../atom/references/go-style.md)
4. [anti-rationalization.md](../atom/references/anti-rationalization.md)
5. [verification.md](../atom/references/verification.md)
6. This phase's approved `design-spec.md`

---

## Step 1 — Build the test spec

Map every numbered behaviour in the design spec to at least one test case, using
[test-spec.md](../atom/templates/test-spec.md) at
`specs/{project}/phase-NN-{slug}/test-spec.md`.

A behaviour with no test is either not going to be implemented, or was not specified
precisely enough to test. Both are problems to resolve **now**, before writing code —
go back to `/atom:spec` rather than papering over it.

Add the cases the spec did not enumerate: error paths, boundaries, zero values, empty
inputs, cancelled contexts. Uncovered error branches are where real coverage gaps
live.

Then **audit the list for cases that can never fail**, per
[what-the-toolchain-proves.md](../atom/references/what-the-toolchain-proves.md). Ask
of every case:

> Could this test ever fail, given the code compiles and `go vet` passes?

If not, it is not a weak test — it is not a test. A Go `string` cannot be nil, so a
nil-string case can never be written; a `""` case can, and should be. Delete the
unfailable cases into the test spec's Redundancy Audit with their evidence, and carry
the decision into `decisions.md` — a deleted test and a forgotten test look identical
a month later.

Then spend the time you just saved on the opposite list: the properties the toolchain
accepts **silently**, where a wrong answer arrives with no panic and no diagnostic —
ignored errors, typed nils, non-exhaustive switches, runtime overflow, empty strings.
Those are the tests that earn their keep.

Order the cases so the first ones build the simplest working path through the phase.

## Step 2 — The loop

One behaviour at a time:

```
  RED       write one failing test
            run it — watch it fail
            confirm it failed for the right reason
     │
  GREEN     write the minimum code to pass
            run it — watch it pass
     │
  REFACTOR  improve the code, suite stays green
            run again
     │
     └──▶ next behaviour
```

### RED — watch it fail

> No production code without a currently-failing test that demands it.

Run the test and read the failure. A test that passes the moment you write it is
testing nothing, or is testing something already built.

Check *how* it fails. A compile error or a nil-pointer panic has not yet proven the
test is asserting the right thing — it has only proven the code is absent. Get to a
clean assertion failure, where the message says what was expected and what was got,
before writing any implementation.

### GREEN — minimum only

Write the least code that passes. Not the code you know you'll need in three
behaviours' time. Speculative structure written under a green bar never gets the test
that would have justified it.

### REFACTOR — with a green bar

Only refactor when the suite is green. One change at a time, re-running between them,
so a break is attributable.

Refactor the tests as well. Duplicated setup costs as much in a test file as anywhere
else.

### Comment pass — explain the decisions the code cannot

Before leaving REFACTOR, read every changed Go file once more and add the explanation
the syntax cannot carry:

- Every exported symbol gets a doc comment saying **why** it exists and what contract
  callers depend on — not a restatement of its name or signature.
- Every non-obvious decision gets an inline comment giving its reason: a validation
  that fails closed, a path transformation, a security or containment check, an
  ordering or concurrency constraint, a deliberate rejection of a plausible
  alternative. Say what breaks without it.
- Obvious code stays uncommented. A comment that narrates an assignment or a return
  rots into a lie, and that is worse than silence.

A green suite proves the behaviour. It does not record the reasoning a maintainer
needs to change that behaviour safely, and that reasoning is only in your head right
now. This pass is part of BUILD, not polish afterwards.

## Step 3 — Go specifics

Follow [go-style.md](../atom/references/go-style.md). In tests specifically:

- Table-driven by default, each case with a `name`, run via `t.Run`
- Name for behaviour: `TestDrain_CancelledContext_AbandonsInFlightJobs`
- `t.Helper()` in assertion helpers so failures point at the caller
- `t.Cleanup()` rather than manual teardown
- `t.Parallel()` only where cases are genuinely independent
- Prefer real collaborators; fake only across I/O, time and randomness
- Anything concurrent runs under `-race`

## Step 4 — Never weaken a test

When a test fails, the default assumption is that the **code** is wrong.

Sometimes the test genuinely is wrong — a bad expectation, a broken fixture. That is a
claim you have to justify, not assume. If you change a test, write down in
`decisions.md` what was defective about it and why. "It was failing" is not a defect.

Loosening an assertion to get to green converts a caught bug into a shipped one.

## Step 5 — Verify

```bash
atom check
```

Runs build, `vet`, `gofmt`, the full test suite, `-race`, and coverage.

Per [verification.md](../atom/references/verification.md): paste the real output.
Never summarise, never round, never reconstruct from memory.

**Partial success is failure.** 47 of 48 passing is a failing suite, not "essentially
passing".

Coverage is a signal, not a target. Look at *what* is uncovered rather than at the
percentage — and do not manufacture tests for trivial getters to move a number.

## Step 6 — Reconcile the spec

Implementation always teaches something the spec got wrong. Update the design spec so
it describes what was actually built.

A spec left describing the design you abandoned is worse than no spec, because it is
confidently wrong.

Record what changed and why in `decisions.md`. Anything you noticed and chose not to
fix goes in `findings.md`.

## Step 7 — Gate

Present per [human-gates.md](../atom/references/human-gates.md): the `atom check`
output, behaviour-to-test coverage, what the spec had to change and why, what you
left in `findings.md`, and one specific question.

**End your turn. Wait.**

---

## Done when

- [ ] Every numbered behaviour maps to at least one test case
- [ ] No test asserts something the compiler or `go vet` already refuses
- [ ] Silent-failure properties are covered or explicitly marked not applicable
- [ ] Every test was watched failing, for the right reason, before its code existed
- [ ] Error paths, boundaries and cancellation covered
- [ ] Concurrent code tested under `-race`
- [ ] Every exported symbol has a doc comment saying why it exists, and every
      non-obvious decision has a comment giving its reason; obvious code is uncommented
- [ ] No test weakened; any test change justified in `decisions.md`
- [ ] `atom check` fully green, output pasted verbatim
- [ ] Design spec reconciled to what was built
- [ ] `findings.md` and `decisions.md` updated during the work
- [ ] Presented at a gate and explicitly approved

## Next

`/atom:review` — multi-model review of the diff.
