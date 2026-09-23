# TDD Discipline

TDD is Atom's BUILD beat. It turns an approved design spec into production Go by
writing the proof before writing the implementation.

> No production code without a currently-failing test that demands it.

The loop is small on purpose: one behaviour, one failing test, the minimum code,
then cleanup while the suite is green.

---
## The Loop

| Beat | What you do | Required evidence |
|---|---|---|
| RED | Write one test for one specified behaviour | `go test` output showing it fails for the right reason |
| GREEN | Write the minimum production code that makes that test pass | `go test` output showing the target test passes |
| REFACTOR | Improve names, structure, duplication, and seams without changing behaviour | `go test` output still green after each refactor |

```bash
go test ./internal/cache -run TestStore_ExpiredEntry_ReturnsMiss
# FAIL for the assertion you intended

go test ./internal/cache -run TestStore_ExpiredEntry_ReturnsMiss
# PASS after minimal implementation

go test ./internal/cache
# PASS after refactor
```

Do not batch several behaviours into one RED step. You lose the link between the
failing test and the production change it demanded.

---
## Watch the Test Fail

A test that passes immediately did not demand new code. It is either testing
behaviour that already exists or not testing the behaviour you think it is.

A test that fails with a compile error, nil panic, data race, or fixture problem
has not proven the intended behaviour yet. Get it to a clean assertion failure
first.

| Failure | Meaning | Next action |
|---|---|---|
| Assertion failure matching the intended behaviour | Good RED | Implement the minimum code |
| Compile error from a missing API named in the spec | Acceptable starting point | Add the smallest symbol, then rerun to reach assertion failure |
| Nil pointer panic | Bad RED | Fix the fixture or setup |
| Test passes immediately | Not RED | Strengthen the assertion or pick an unimplemented behaviour |
| Fails for a different package | Not useful for this loop | Narrow the command or fix the unrelated blocker |

Good RED output tells you the test is aimed at the behaviour, not at a broken
harness.

---
## Mapping the Spec to Tests

The design spec controls the test list.

| Spec item | Test obligation |
|---|---|
| Public method behaviour | At least one test named for the condition and outcome |
| Error path | A test that asserts the error value or message contract |
| Cancellation path | A test using `context.Context` cancellation or deadline |
| Concurrent behaviour | A test suitable for `go test -race` |
| Persistence or parsing rule | Table cases for valid, invalid, and boundary input |
| Performance claim | Benchmark output with numbers |

Spec ordering suggests test ordering. If the spec lists validation before I/O,
write the validation tests first.

Anything in the spec with no test is either not implemented or not specified
precisely enough. Fix the spec or add the test; do not leave the gap silent.

---
## Do Not Test What the Toolchain Proves

Before writing a case, ask:

> Could this test ever fail, given the code compiles and `go vet` passes?

If the answer is no, it is not a weak test — it is **not a test**. It can never
run, never fail, and never catch a regression.

Measured against `go1.23.4` across 24 candidate properties:

| Bucket | Count | What to do |
|---|---|---|
| Compiler refuses it | 12 | Write no test; one cannot exist |
| `go vet` flags it | 3 | Rely on the `atom check` gate |
| Toolchain accepts it | 9 | **Only a test catches this — write it** |

The most common inherited mistake is demanding a `nil` test for every string
parameter. **A Go `string` cannot be nil**; `var s string = nil` does not
compile. The empty string, however, sails through the toolchain and returns a
silently wrong answer — so `""` is worth testing and `nil` is impossible.

The inverse error is worse. These *look* compiler-checked and are not, and five
of them fail with **no panic and no diagnostic at all**:

| Looks checked | Actually |
|---|---|
| Exhaustive switch over an enum-like const block | No check. Missing case returns the zero value |
| A consumed `error` return | Ignoring a return value is legal |
| `err != nil` for a nil pointer | A typed nil in an interface is **not** nil |
| Integer overflow | Silently wraps: `int8` 127+1 becomes -128 |
| Bounds and divisors | Only checked for *constants*, never variables |

Full tables, evidence, and the reasoning are in
[what-the-toolchain-proves.md](what-the-toolchain-proves.md). A case removed as
redundant is a decision — record it in `decisions.md` with its bucket, because a
deleted test and a forgotten test look identical afterwards.

---
## Go Test Shape

Table-driven tests are the default. Give each case a `name` and run it with
`t.Run`.

```go
func TestParser_Parse_EmptyInputReturnsError(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name string
        input string
        wantError string
    }{
        {name: "empty input", input: "", wantError: "empty input"},
    }

    for _, test := range tests {
        test := test
        t.Run(test.name, func(t *testing.T) {
            t.Parallel()

            _, err := Parse(test.input)
            if err == nil || !strings.Contains(err.Error(), test.wantError) {
                t.Fatalf("error = %v, want containing %q", err, test.wantError)
            }
        })
    }
}
```

Naming convention:

```text
TestThing_Condition_ExpectedOutcome
```

| Name | Why it works |
|---|---|
| `TestParser_EmptyInput_ReturnsError` | Names unit, condition, outcome |
| `TestWorkerPool_CancelledContextStopsDrain` | Names cancellation behaviour |
| `TestStore_ConcurrentPutAndGet_HasNoRace` | Makes concurrency intent explicit |

---
## Helpers, Cleanup, and Parallelism

| Tool | Use when | Rule |
|---|---|---|
| `t.Helper()` | Writing assertion or fixture helpers | Call it at the top so failures point at the test |
| `t.Cleanup()` | Creating files, goroutines, listeners, or environment changes | Prefer it over manual defer chains in tests |
| `t.Parallel()` | Test and collaborators are isolated | Do not use it when tests share global state |
| `go test -race` | Code starts goroutines or touches shared state | Required before claiming concurrent code is done |

Prefer real collaborators when they are deterministic and cheap. Fake only across
I/O, time, randomness, network boundaries, and slow external processes.

---
## Never Weaken a Test

Do not change a correct failing test just because the implementation made it
inconvenient.

| Change | Allowed? | Reason |
|---|---|---|
| Fixing a wrong expected value after re-reading the spec | Yes | Genuine test defect |
| Replacing exact error type with substring because wrapping is unspecified | Yes, if the spec permits it | Test was more specific than the contract |
| Removing a boundary case because it fails | No | The implementation is wrong or the spec is unclear |
| Ignoring a returned error to make setup pass | No | The test is hiding evidence |
| Changing the spec to match the code without a gate | No | That is design drift |

If you change a test, record the reason in `decisions.md`. If the spec is wrong,
re-gate the corrected spec before continuing.

---
## Coverage

Coverage is a target, not a goal. Useful coverage finds untested behaviour,
especially error branches, cancellation branches, empty input, boundary values,
concurrent access, and cleanup failure.

```bash
go test -cover ./...
```

Chasing a percentage by testing trivial getters, generated code, or constructor
assignments is waste. If coverage is low, ask what behaviour lacks a test.

---
## Refactoring

Refactor only with a green suite.

Rules:

1. One refactor at a time.
2. Re-run the relevant tests after each refactor.
3. Keep behaviour unchanged.
4. Refactor tests too.

Duplicated setup in tests is as costly as duplicated setup in production code.
Move it into helpers when it obscures the behaviour under test, and use
`t.Helper()` so failures still point at the calling test.

---
## TDD Does Not Replace the POC

TDD verifies behaviour you already decided to build. The POC discovers what
behaviour is possible, practical, or false.

| POC | TDD |
|---|---|
| Throwaway program | Production test suite |
| Answers uncertainty | Locks down expected behaviour |
| May be ugly | Must be maintainable |
| Runs before design | Runs during build |
| Can refute the plan | Implements the approved spec |

Do not use tests as a substitute for the PROVE beat. Tests are precise after the
question is known; the POC exists because the question is still risky.

For POC rules, re-read [poc-discipline.md](poc-discipline.md). For Go style,
re-read [go-style.md](go-style.md).

