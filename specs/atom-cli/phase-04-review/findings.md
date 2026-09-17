# Findings — Phase 4: `atom review`

Discoveries made while building Phase 4 that outlive it. Recorded here rather
than in commit messages because several of them change how later phases should
be built.

---

## 1. Diff *content* imitates diff *headers*, and a prefix rule cannot tell them apart

Found in Cycle 1, by distrusting a suite that went green on the first attempt.

Unified diff puts a `+`, `-` or space in front of **every line inside a hunk**.
So a file whose content already begins with those characters produces body lines
that are indistinguishable from headers if you only look at the prefix:

| Original content | Line in the diff | What a prefix rule concludes |
|---|---|---|
| `---` (markdown rule or front-matter delimiter), removed | `----` | starts with `---` → header → **skipped** |
| `-- a sql comment`, removed | `--- a sql comment` | starts with `--- ` → header → **skipped** |
| `++ something`, added | `+++ something` | starts with `+++ ` → **a new file named `something`** |

The first implementation used exactly that rule, and 22 tests passed over it.

### The two failures are not equally serious, and the obvious one is the milder

**The undercount is real but small.** Measured on a real Atom commit — the
Phase 4 spec commit, three markdown files thick with `---`:

```
hunk-aware (correct) : 393
naive prefix rule    : 392
silently lost        :   1 changed line
```

One line in 393. Worth fixing, not worth alarm — and worth stating plainly,
because "markdown diffs are badly undercounted" was the claim that felt true
before it was measured. It was not true.

**The phantom file is the serious one.** Added content beginning with `++`
becomes an entry in the diff's file list:

```
+++ phantom/invented.go      →  files == ('phantom/invented.go', 'real.go')
```

That matters because **B117 rejects any finding naming a file that is not in the
diff** — the one guard against a model describing code it was never shown. A
phantom entry widens the guard using content taken from the diff itself. Its
frequency is low; its failure mode is a security-shaped hole in a validation
rule, and it is silent.

### The fix is positional, not lexical

Track whether the parser is inside a hunk. Headers occur before the first `@@`
of a file; everything after it is body, whatever it looks like. A bare
`diff --git` line can only be a header, because body lines always carry a
prefix — that is what makes the state machine decidable.

### What this says about the method

Three earlier phases established that a green suite does not prove a program
runs. This is the variant one step further in: **a green suite does not prove
the tests were asking hard questions.** The 22 original tests were not weak by
accident — they were written from the same mental model as the implementation,
so they tested the rule rather than the requirement. The bug surfaced only when
the code was pointed at input nobody had imagined while writing either.

Two habits caught it, and both are cheap:

1. **Treat first-attempt green as a smell.** It usually means the tests and the
   code share an assumption.
2. **Run the real thing against real input early.** Every Cycle 1 test used a
   fake git; the first real `git diff` was what produced the markdown-heavy
   input that exposed the shape of the problem.

### Consequence for later cycles

Cycle 3 implements B117 using `CapturedDiff.files`. It now has a correctness
dependency on this parser that the design spec does not mention — worth a line
in the test spec, because the guard is only as good as the file list behind it.

---

## 2. A test fixture can be wrong in a way that looks like an implementation bug

While fixing finding 1, `test_nothing_is_truncated_however_large_the_diff`
failed. The fixture built a 5,000-line diff with no `@@` header, so the
hunk-aware parser correctly counted zero changed lines.

The tempting fix is to make the parser tolerate missing hunk headers. That would
have been weakening the implementation to satisfy a fixture that did not
describe anything git emits. The fixture was fixed instead.

Worth recording because the pressure ran the right way and was still easy to
miss: the failing test was one *I* had just written, the implementation was
*also* one I had just written, and "make the failure go away" points at
whichever is easier to change.

The rule that resolves it: **ask whether the input is real before asking whether
the code is right.** Real `git diff` output always carries a hunk header.

---

## 3. A test that bounds a maximum can prove nothing at all

Cycle 2's concurrency test counted how many calls were in flight and asserted
`peak <= 2`. It passed. It also passes when parallelism is removed entirely —
measured by monkey-patching the concurrency helper to a plain serial loop:

```
parallelism REMOVED -> peak=1.  Test asserts peak<=2 -> STILL PASSES
```

An upper bound is satisfied by doing less work, so it can never detect a
version that does *no* concurrent work. B111 exists to make reviews fast; a
silently sequential implementation would have satisfied every test in the
module while taking six times as long as designed, and nothing would have said
so.

The fix is a runner that refuses to return until a second call joins it. If
execution is serial the first call waits alone and the barrier times out, so
the test can only pass when two calls are genuinely in flight. The assertion
also tightened from `peak <= 2` to `peak == 2`.

**The general shape:** an assertion of the form "not more than N" is a safety
property, and safety properties are trivially satisfied by inaction. Anything
that must actually *happen* needs a liveness assertion to go with it — bound
the maximum *and* require the minimum.

This is the same failure as Cycle 1's finding 1 seen from the other side.
There, the tests shared a wrong assumption with the code. Here, the test was
simply too weak to distinguish the working implementation from a broken one.
Both are green suites that are not asking hard questions.

---

## 4. `--runs 0` produced a clean-looking review that consulted nobody

Found by asking what the new `--runs` flag does at its boundary:

```
runs=0 -> calls=0, is_partial=False, participation='gpt-5.4: 0/0 runs completed'
```

Zero model calls, and a report that says nothing is wrong with it. `is_partial`
is false because "completed equals requested" holds trivially when both are
zero, and `0/0` reads as a complete fraction rather than an absent one.

B130 already guards the neighbouring case — *no model available* fails loudly,
precisely because an empty report is indistinguishable from a clean one. The
same danger simply arrived through a door B130 does not cover. The guard was
written against one cause of emptiness rather than against emptiness itself.

Refused with a `ValueError` rather than clamped to 1: clamping would hide the
mistake, and the whole point is that this output is *unreadable as a mistake*.

**Worth generalising:** when a behaviour exists to prevent a dangerous output,
ask what else produces that same output. B130's rationale is about the *report*
being empty; its implementation is about *models* being unavailable. Wherever a
rule's stated reason is broader than its trigger, the gap is where the next bug
lives.

---

## 5. The spike's speed fix contained one company's internal server names

B109 is backed by a real measurement — disabling MCP servers took a call from
84 seconds to about 30. But the spike achieved it with three flags, and two of
them named specific servers that happened to be ambient on the machine it ran
on: `azure-mcp` and `azure-devops`.

Only `--disable-builtin-mcps` is a property of the CLI. The other two are a
property of that environment. Copying all three into the implementation — which
is what "reproduce the spike's command" naturally means — would have shipped
one organisation's internal tooling names inside an open-source tool.

Recorded as A7: the built-in flag is always sent, the named servers become an
optional argument defaulting to empty.

**The pattern to watch:** a POC is run somewhere, and "somewhere" leaks into the
result. The measurement was sound and the conclusion was sound; the *command*
carried an assumption about the host that neither of them did. When promoting
spike commands to production, each argument needs asking separately whether it
describes the tool or the machine.

---

## 6. The fence regex took the first fence, not the right one

Cycle 3's extractor passed 31 tests, then failed on the most ordinary thing a
review model does — illustrate a point before answering:

```
The problem is here:
```go
var mu sync.Mutex
```
Findings:
```json
[{"file": "store/cache.go", ...}]
```
```

The pattern `` ```(?:json)?\s*(.*?)``` `` matches the **first** fence whatever
its label. It captured `go\nvar mu sync.Mutex`, failed to parse, and discarded
the entire run — including findings that were sitting correctly formatted a few
lines further down.

The fix is to prefer a `json`-labelled fence when one exists. This is worth
distinguishing from the bracket scan that B114 refuses: the bracket scan
*invents* a boundary by guessing where data starts, whereas choosing between
fences the model itself delimited and labelled invents nothing. Selection
between candidates is not the same act as fabricating one.

**Left unfixed, deliberately:** a fence closes at the first ``` it meets, so a
finding whose *message* contains a triple backtick truncates the payload and the
run fails loudly. A greedy retry would fix it and would also be a third
unobserved recovery path. Pinned by a test so the behaviour is visible and any
future fix is a decision rather than a drift. Tracked as D12.

---

## 7. Line numbers below 1 were accepted, and the merge step would have believed them

`"line": -5` and `"line": 0` both validated. `isinstance(line, int)` is true for
both, and nothing else looked.

Harmless in isolation — but the merge model groups findings within a few lines
of each other, so line 0 and line -5 would cluster into a single group and be
presented as one location with corroboration from two runs. An impossible line
number does not stay impossible; it becomes a confident-looking finding.

Now rejected with a reason. Recorded as A9 because it is a tightening the spec
did not ask for: B116 says "an integer `line`", and requiring it to be a *real*
line is an inference about intent.

Related, and already caught in the same pass: `isinstance(True, int)` is `True`
in Python, so `"line": true` validated and produced a finding pointing at line 1.
The spike's own validator has this hole. The bool check has to come first.

---

## 8. The extractor was validated against the 40 real spike responses

Rather than trusting 37 unit tests built from imagined inputs, the finished
extractor was run over every reply the spike actually saved:

| Model | n | Fenced | Parses as-is | With the extractor |
|---|---:|---:|---:|---:|
| `gpt-5.4` | 10 | 0 | **10** | 10 |
| `claude-haiku-4.5` | 10 | **10** | **0** | **10** |

Two things this settles that no unit test could.

**The measured compliance figures reproduce exactly** through production code —
100% for one model, 100%-after-fence-stripping for the other. The spike's
conclusion survives the trip from analysis script to shipped module.

**B113 is entirely load-bearing.** Without fence stripping, `claude-haiku-4.5`
contributes *nothing* — not a degraded signal, zero findings, on every single
response. A "minor formatting quirk" turns out to be the difference between a
two-model review and a one-model review, and the failure would have been silent:
the report would have shown one model's findings and a run that "returned
nothing".

**The habit worth keeping:** saved POC artefacts are a regression corpus. The
spike's 40 responses cost real time and money to collect; running the finished
implementation back over them is free and checks something unit tests
structurally cannot — that the inputs were imagined correctly.

---

## Finding 9 — proximity merging cannot separate defects closer than the drift

Running the finished merge module back over the 20 real spike responses produced
82 findings → 5 merged, 3 corroborated, 2 solo. The 2 solo findings were noise
(2/10 and 1/10 runs). That is the agreement analysis reproduced end to end, and
it is the result the phase wanted.

It also merged two genuinely different defects into one.

The fixture had **four** planted defects — lines 24, 36, 44 and 45. Merging
returned **three** corroborated findings. Lines 44 and 45 landed in a single
group spanning 42–45:

| line | what the models described |
|------|---------------------------|
| 42, 43, 44 | error from `os.Create` ignored; `f` is nil when writing |
| 45 | `Export` iterates `s.items` without holding the lock |

Those are not the same defect. They merged because **line drift moved the
anchor**. Both models attributed the `os.Create` problem to lines 42, 43 and 44
on different runs; the lowest anchors the group, so a window of 3 reaches line
45. The effective reach past the true defect is `window + drift`, not `window`.

**No window value fixes this.** Shrinking to 2 would split the genuine 33–36
cluster, which is one defect, into two. Proximity merging cannot distinguish
"one defect described with drift" from "two defects one line apart", because on
the evidence available they are the same shape.

**Why it is nevertheless tolerable.** B120 keeps every message attributed, so
both defects are still described in the output — the developer reads about the
ignored error *and* the missing lock. What is wrong is the **count** and the
headline: three corroborated findings for four real defects. A report that
claimed "3 issues found" would be quietly wrong.

This bears directly on P4-5, which is the developer's decision, so it is raised
rather than absorbed. Pinned by `test_drift_lets_a_group_reach_further_than_the_window`.

## Finding 10 — the number the phase rests on could render impossible values

`1/0` and `5/3`. Both were accepted and would have been printed.

The agreement fraction is the one output B121 and B122 ask the developer to
trust; nothing else separates a real defect from noise. `runs_total = 0` with a
finding present gave "reported by 1/0 runs". Findings from five run indices with
`runs_per_model = 3` — an ordinary caller mistake, passing the configured
`--runs` alongside findings from a longer review — gave "5/3".

Neither was caught by 29 passing tests at 100% coverage, because every test
supplied a consistent pair of numbers. Coverage measures which lines ran, not
which combinations of arguments were imagined.

A single impossible fraction does not just misreport one finding. It tells the
reader that none of the numbers can be relied on. Both are now refused (A12).

## Finding 11 — an ordering guarantee resting on an unstated type

Severity ranking is built by enumerating `ALLOWED_SEVERITIES`. That works
because it is an ordered tuple. Had it been the set it superficially resembles,
Python's per-process string hash randomisation would have reordered every report
between runs, and the failure would have looked like model non-determinism
rather than a type choice three modules away.

Nothing documented the coupling and no test asserted it. Now pinned by
`test_severity_ordering_depends_on_the_allowed_list_staying_ordered`.

**The habit worth keeping:** when a module depends on a property of another
module's constant rather than on its value, assert the property. Type and order
are as load-bearing as content, and only content tends to get tested.

## Finding 12 — first-attempt green, four times out of four

Cycles 1, 2, 3 and 4 each passed on the first implementation pass. Each hid real
defects found only by deliberate probing afterwards — a phantom-file parser, a
concurrency test that passed with concurrency removed, a fence regex that
discarded whole runs, and now impossible agreement fractions.

The mechanism is consistent: tests written from the same mental model as the
implementation verify *the rule as understood*, never *the requirement*. Passing
confirms the two halves of one idea agree with each other.

Four for four is no longer an observation about individual cycles. Green on the
first attempt should be treated as an unexplored area, and the probe is the step
that actually finds things — in this cycle, running the module over real POC
data and feeding it deliberately inconsistent arguments.
