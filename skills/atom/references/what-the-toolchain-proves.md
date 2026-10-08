# What The Toolchain Already Proves

A test that asserts something the compiler refuses to compile is not a weak test.
It is **not a test at all** — it can never run, never fail, and never catch a
regression. It costs review time and teaches readers that the test spec is
decorative.

> Write tests for what the toolchain lets through, not for what it stops.

This is the single most common source of redundant tests when test specs are
written by habits carried over from other languages.

---
## The Rule Atom Does Not Inherit

A widespread test-spec convention mandates:

> Null **and** empty-string tests for every mandatory string parameter.

That rule comes from languages where `string` is a reference type and can be
null. **In Go a `string` cannot be nil.** `var s string = nil` does not compile.

Measured — the rule is exactly half right:

| Half of the rule | In Go | Verdict |
|---|---|---|
| Test `nil` string | `cannot use nil as string value` — will not compile | **Impossible.** Never write it |
| Test `""` | Compiles, runs, returns `"hello "` with no complaint | **Valuable.** Always consider it |

The empty string is a real value with real semantics, and nothing in the
toolchain objects to it. That is precisely why it needs a test.

---
## The Three Buckets

Every candidate property falls into one of three buckets. The boundaries were
measured against a real toolchain, not recalled — see
[`poc/compiler-guarantees/`](https://github.com/girishmotwani/atom/tree/main/poc/compiler-guarantees)
for the spike and
`results.json` for raw output.

| Bucket | Meaning | What to do |
|---|---|---|
| **REJECTED** | The compiler refuses it | Write no test. One cannot exist |
| **FLAGGED** | Compiles; `go vet` objects | Fix the CI gate, not the test suite |
| **ACCEPTED** | Compiles and vets clean | **Only a test catches this. Write it** |

Measured on `go1.23.4`, 24 candidate properties: **12 rejected, 3 flagged, 9
accepted.**

---
## REJECTED — do not write these tests

All twelve were refused at build time:

| Property | Why a test is impossible |
|---|---|
| `nil` assigned to a string | `cannot use nil as string value` |
| Wrong argument type | Type mismatch is a compile error |
| A type missing an interface method | `does not implement` at the assignment |
| An unused local variable | `declared and not used` |
| An unused import | `imported and not used` |
| A missing `return` on some path | `missing return` |
| Division by a zero **constant** | `invalid operation: division by zero` |
| A constant too large for its type | `cannot use 300 as int8 value` |
| A duplicated **constant** map key | `duplicate key in map literal` |
| Array index out of range, **constant** index | `invalid argument: out of bounds` |
| Setting a struct field that does not exist | `unknown field` |
| Calling a method the type does not define | `undefined` |

To assert interface satisfaction, use a compile-time assertion, not a test:

```go
// Fails the build if *Store ever stops satisfying Cache. No test needed.
var _ Cache = (*Store)(nil)
```

---
## FLAGGED — fix the gate, not the suite

These compile but `go vet` rejects them. `atom check` already runs `go vet`, so
they are caught on every run. A unit test here duplicates a gate you already have:

| Property | Caught by |
|---|---|
| A `Printf` verb not matching its argument | `go vet` printf check |
| Discarding the `cancel` from `context.WithCancel` | `go vet` lostcancel |
| Copying a struct containing a `sync.Mutex` | `go vet` copylocks |

**The bucket boundary is a function of your toolchain, not a law of Go.** Adding
`errcheck` moves ignored errors from ACCEPTED to FLAGGED; adding `exhaustive`
moves non-exhaustive switches. If you add a linter to `atom check`, revisit this
table — you have just made some tests redundant, which is a good outcome.

---
## ACCEPTED — these are the tests worth writing

Nine properties compiled **and** passed `go vet`. Only a test catches them.

Four fail loudly at runtime:

| Property | Runtime behaviour |
|---|---|
| Writing to a nil map | panics |
| Dereferencing a nil pointer | panics |
| Slice index out of range, **variable** index | panics |
| Division by a zero **variable** | panics |

Five fail **silently** — no panic, no diagnostic, just a wrong answer:

| Property | Observed output | Why it is dangerous |
|---|---|---|
| A nil `*T` returned as an interface | `TYPED NIL IS NOT NIL` | `err != nil` is true for a nil pointer. The classic Go trap |
| `int8` 127 incremented | `wrapped to -128` | Silent wraparound, no overflow error |
| Non-exhaustive switch over an enum-like const block | `Blue -> ` | Go has no exhaustiveness check. Missing case returns the zero value |
| Calling a function and ignoring its `error` | `carried on regardless` | The compiler does not require you to consume a return value |
| Passing `""` to a function requiring a value | `"hello "` | Empty is a valid string; only your rules say otherwise |

**This table is the highest-value test list in the reference.** Those five
produce a wrong answer with no signal whatsoever. Every one is invisible to
the compiler, to `go vet`, and to a passing test suite that never asked.

---
## Applying It

When building the test spec, run each proposed case through one question:

> **Could this test ever fail, given the code compiles and `go vet` passes?**

- **No, it could not compile** → delete it. Record the deletion; do not silently drop it.
- **`go vet` would catch it** → delete it, and confirm the gate runs in `atom check`.
- **Yes, it could fail** → keep it. This is a real test.

Then ask the complementary question, which is where the value is:

> **Which of the nine ACCEPTED properties apply to this code, and does each have a test?**

Zero values deserve care rather than a blanket rule. Go guarantees
zero-initialisation, so `if got.Count != 0` on a freshly constructed struct tests
the *language*. But "a zero-value `Buffer` is usable without construction" is a
genuine design contract — test that, because it is a promise your code makes.

---
## Do Not Over-Apply This

The failure mode in the other direction is worse, because it deletes tests that
catch real bugs. Before removing a test as redundant, confirm the property is
genuinely in REJECTED or FLAGGED. Things that *look* compiler-checked and are not:

- Exhaustive switches (Go is not Rust — there is no check)
- Consumed error returns (ignoring a return value is legal)
- Nil interface comparisons (a typed nil is not nil)
- Integer overflow at runtime (silent wraparound)
- Any bounds or divisor computed from a variable rather than a constant

If you are unsure which bucket a property is in, **measure it** the way
`poc/compiler-guarantees/spike.py` does: write the smallest program that exhibits
it, build it, vet it, run it. That takes a minute and replaces an argument with a
fact.

---
## Recording Removals

A case removed as redundant is a decision, so it goes in `decisions.md` with its
bucket and the evidence:

```text
Removed TestParse_NilInput_ReturnsError: `input` is a string, and
`var s string = nil` does not compile (REJECTED). Replaced with
TestParse_EmptyInput_ReturnsError, which the toolchain accepts silently.
```

Deleting tests without a record looks identical to forgetting to write them.

For the loop itself, re-read [tdd-discipline.md](tdd-discipline.md). For Go
style, re-read [go-style.md](go-style.md).
