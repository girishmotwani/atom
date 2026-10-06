# Go Style — Readability and Extensibility First

Atom targets Go, but it does **not** target maximally idiomatic Go.

Idiomatic Go optimises for terseness and for readers who already know the codebase.
Atom optimises for a reader — human or agent — encountering the code for the first
time, and for the next person who has to extend it without breaking it.

> **When idiom and clarity conflict, clarity wins.** When they don't conflict, follow
> the idiom.

Everything `gofmt` enforces is non-negotiable — formatting is never the thing we
deviate on. The deviations below are about naming, structure and commentary.

---

## Which of these a reviewer actually sees

This document is written for people. Until recently it reached nobody else: the
`atom review` prompt described the output format and said nothing about style, so
every rule here had exactly zero influence on what a review reported.

Seven of them are now sent to the models on every review. They live in
`tools/atom/style.py`, and that file — not this one — is what a reviewer reads:

1. Errors wrapped with the operation that failed
2. Interfaces narrow, and declared where they are consumed
3. No writable package-level state
4. Whoever starts a goroutine states how it stops
5. Exported surface kept minimal
6. Names spell words
7. Doc comments say why, not what

Seven, not thirty, because of a measured result: a hand-picked seven beat thirty
by 33% and a hundred by 48%, while a *random* seven of the same length behaved
like the hundred. Choosing is the lever; shortening is not.

They each describe something that breaks, for a reason that is half evidence and
half guess. The evidence: seeded defects that were pure matters of preference were
reported 0 times out of 3 *even when the reviewer had been handed the exact rule*,
while seeded defects with a visible consequence were reported 3 out of 3. That
experiment varied the defect, not the sentence describing it, so what it establishes
is which defects are worth having a rule about — not how to word one.

The wording itself is untested. No experiment here has varied rule phrasing while
holding the defect fixed, so "name what breaks" is a reasonable inference rather
than a measured result, and should be read as such.

Anything in this document that `gofmt`, `go vet`, `staticcheck`, `errcheck` or the
race detector already proves is deliberately absent from that list. `atom review`
runs those tools first and tells the models what they settled, so repeating it
would spend reviewer attention on an answered question.

Every other rule below is guidance for a human writing Go in this repository. It
is real, and it is not enforced by anything.

---

## Naming

Go's culture favours very short identifiers. Atom does not.

```go
// Idiomatic Go — fine if you already know this file.
for i, v := range s {
    if v.t > d {
        r = append(r, i)
    }
}

// Atom — obvious to someone who has never seen this file.
for index, session := range activeSessions {
    if session.idleTime > idleTimeout {
        expiredIndexes = append(expiredIndexes, index)
    }
}
```

Rules:

- **Locals** get real words. `retryBudget`, not `rb`. `remainingBytes`, not `n`.
- **Receivers** get a meaningful short name tied to the type: `func (pool *WorkerPool)`,
  not `func (p *WorkerPool)`. Consistency across every method of the type matters more
  than the specific choice.
- **Single letters** are allowed only for loop counters over plain integers (`for i := 0; ...`)
  and for the conventional `err`, `ctx`, `w`/`r` in `http.HandlerFunc`.
- **Booleans** read as assertions: `isDraining`, `hasQuorum`, `canRetry`.
- **Don't abbreviate** unless the abbreviation is more common than the word in the
  problem domain (`ID`, `URL`, `TTL`, `HTTP` are fine; `cfg`, `msg`, `req` are not —
  write `config`, `message`, `request`).

---

## Comments

Comments are a deliverable, not decoration. But a comment that restates the code is
worse than none, because it rots.

**Every exported symbol gets a doc comment that explains why it exists.**

```go
// Bad — restates the signature, tells the reader nothing.
// Drain drains the pool.
func (pool *WorkerPool) Drain(ctx context.Context) error

// Good — explains purpose, contract and consequence.
// Drain stops accepting new work and blocks until every in-flight job finishes or
// ctx is cancelled. Callers use this for graceful shutdown; a cancelled context
// abandons in-flight jobs, which may leave their side effects half-applied.
func (pool *WorkerPool) Drain(ctx context.Context) error
```

**Non-obvious logic gets an inline comment explaining the reasoning.** The test is:
would a competent Go developer pause here and ask "why?"

```go
// We resize to the next power of two rather than the exact count because the
// bucket index is computed with a mask (hash & (len-1)), which is only correct
// for power-of-two sizes.
capacity := nextPowerOfTwo(requestedCapacity)
```

**Do not comment the obvious.**

```go
// counter++ // increment the counter   ← delete this
```

**Every file starts with a package comment or, for multi-file packages, exactly one
file (`doc.go`) carries it.** It states what the package is responsible for, in one
sentence, without conjunctions. If you need "and", the package does two things.

---

## Structure

### One concept per file

Name the file after the primary type it contains: `worker_pool.go` holds `WorkerPool`.
A reader should be able to guess the filename from the type name and vice versa.

### Explicit control flow

Prefer flow you can read top to bottom over flow that is compressed.

```go
// Avoid — clever, but the reader has to unpack it.
if err := doThing(); err != nil { return fmt.Errorf("thing: %w", err) }

// Prefer — one idea per line.
err := doThing()
if err != nil {
    return fmt.Errorf("doing thing: %w", err)
}
```

The single-line form is idiomatic and common; Atom still prefers the expanded form
because it produces cleaner diffs, clearer stack-trace-to-source mapping, and a
breakpointable line.

### Errors

- Always wrap with context: `fmt.Errorf("loading config from %s: %w", path, err)`.
- The message says what you were *doing*, in the present participle. It concatenates
  into a readable chain: `starting server: loading config from /etc/x: no such file`.
- Define sentinel errors (`var ErrNotFound = errors.New("not found")`) for conditions
  callers need to branch on, and say so in the doc comment.
- Never discard an error with `_` without an inline comment justifying it.

### Concurrency

- `context.Context` is the first parameter of anything that can block. Always.
- Whoever starts a goroutine is responsible for its shutdown. Say in a comment how it
  stops.
- Prefer a channel that is closed by exactly one writer over shared mutable state.
- Guard mutable shared state with a mutex held for the shortest possible span, and
  name the mutex after what it protects (`sessionsMu` guards `sessions`).
- Anything you write concurrently, you test with `go test -race`.

---

## Extensibility

Design so that new behaviour is **added** rather than existing behaviour **edited**.

- **Define interfaces where they are consumed, not where they are implemented.** The
  consumer declares the narrow interface it needs; the producer returns a concrete type.
- **Keep interfaces small.** One to three methods. A wide interface forces every
  implementation, including test fakes, to carry irrelevant weight.
- **Take dependencies as parameters**, never as package-level globals. Constructors
  accept collaborators:

  ```go
  // NewScheduler builds a Scheduler. Dependencies are injected so tests can supply
  // deterministic substitutes for the clock and the queue.
  func NewScheduler(clock Clock, queue JobQueue, logger *slog.Logger) *Scheduler
  ```

- **Use functional options** once a constructor exceeds roughly four parameters, so
  new options don't break existing call sites.
- **Keep the exported surface minimal.** Export what callers need and nothing else;
  unexporting later is a breaking change, exporting later is not.

---

## Testing

- Table-driven tests are the default. Give each case a `name` and use `t.Run`.
- Test names say the behaviour: `TestDrain_CancelledContextAbandonsInFlightJobs`.
- Prefer real collaborators over fakes when they are deterministic and cheap. Fake
  only across I/O, time, and randomness boundaries.
- `t.Helper()` in assertion helpers. `t.Cleanup()` instead of manual teardown.
- Never weaken a test to make it pass. Fix the code, or fix a genuine defect in the
  test and say so in `decisions.md`.

---

## What We Keep From Idiomatic Go

To be explicit — these are not deviations, and you should follow them:

- `gofmt` / `goimports` formatting, always.
- Accept interfaces, return structs.
- Zero values should be useful where that's natural.
- No stuttering: `bytes.Buffer`, not `bytes.BytesBuffer`.
- Errors are values; don't build exception-like control flow with `panic`.
- `panic` only for programmer error that cannot be recovered from, never for expected
  conditions.
