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
them named specific third-party servers that happened to be ambient on the
machine it ran on.

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

## Finding 13 — `shutil.which` found an executable that could not be started

Running `atom review` by hand for the first time produced:

    atom review: No review model could be called: gpt-5.4
    (Executable not found on PATH: copilot)

The message was wrong. `copilot` *was* on PATH — `shutil.which` resolved it to
`...\WindowsApps\copilot.EXE` and `os.access(..., os.X_OK)` returned true. The
file is a zero-byte Windows App Execution Alias: a reparse stub left behind
after the package it pointed at was removed. `subprocess.run` refused to start
it with `WinError 2`, the same error Windows reports for a file that is absent.

`shell=True` failed identically, and so did passing the fully resolved absolute
path. Nothing about the call site was wrong; the entry on PATH was a corpse.

**Why it matters more than the bug.** A developer reading "not found on PATH"
checks their PATH, finds `copilot` there, and concludes the tool is lying — the
most expensive possible failure mode, because the message actively directs the
investigation away from the cause. `SubprocessRunner` now distinguishes the
cases and tells the developer to reinstall.

This is the sixth time an external interface has reported something untrue
(after `gofmt -l`, `go run` exit flattening, Go's panic exit code, `os.replace`
on Windows, and `[1,2,3]` parsing as valid JSON).

## Finding 14 — the test for one lie uncovered another

Writing the regression test for finding 13 required a third cause of the same
exception: a working directory that does not exist. That test failed, but not
by producing the wrong message — the process **crashed**.

Windows raises `NotADirectoryError` (`WinError 267`) for a bad working
directory. It is an `OSError`, but it is *not* a subclass of
`FileNotFoundError`, so it escaped the handler entirely. `SubprocessRunner.run`
is documented as "turning expected process failures into data", and for one of
the three ways a process can fail to start it raised instead.

The defect shipped in Phase 1 and survived four phases and 475 tests, because
every existing test supplied a working directory that existed — `tmp_path`
always does. The bug needed a caller careless enough to pass a path that did
not, and no test was ever that careless.

**The habit worth keeping:** when catching an exception by type, check what the
platform actually raises for every case the handler claims to cover. Exception
hierarchies are an interface, and this one does not group by meaning — three
causes of "the process never started" span two unrelated exception classes.

## Finding 15 — the whole diff travelled in argv, and Windows truncated it silently

`review_command` passed the prompt as `-p <text>`, so the entire diff sat in
argv. Measured on Windows against the npm-installed CLI:

| Prompt size | Result |
|---|---|
| ~1,000 chars | works |
| ~8,000 chars | "The syntax of the command is incorrect" |
| ~30,000 chars | "The command line is too long" |
| ~60,000 chars | the process refuses to start at all |

The first two arrive as `COMPLETED` with a non-zero exit — **indistinguishable
from a model that answered badly**. The last arrives as `TOOL_MISSING`, which
reads as a broken install. A review of any diff past roughly 150 lines was
being silently destroyed by the plumbing and blamed on the model.

The POC never saw it because the spike reviewed one small fixture file. The
unit tests never saw it because a test double has no command-line limit — the
constraint lives in the operating system, and mocking the operating system
mocks the constraint away.

**The fix is not a bigger limit.** The prompt now travels on stdin, which has
no such ceiling, and a test asserts that argv is *identical* for a 100-character
prompt and a 500,000-character one. Pinning the invariant rather than a
threshold is what keeps this from regressing at some new boundary.

## Finding 16 — closing stdin was as important as opening it

Moving the prompt to stdin exposed the next layer. The availability probe
printed its answer and then timed out after 60 seconds. The CLI reads stdin
whenever stdin is not a terminal, Atom was itself running from a pipe, and that
pipe never reached EOF — so a correct answer became a timeout.

`subprocess.run` inherits the parent's stdin unless told otherwise, and
inheriting is the wrong default for a non-interactive tool: immediate EOF is
recoverable, an inherited never-closing pipe is not. Every child now gets an
explicitly empty stdin unless given text.

Worth noting how this presented: the model **answered correctly** and the run
was recorded as a failure. Every symptom pointed at the model.

## Finding 17 — "usable" was measured at the wrong boundary

With the calls finally working, a real run reported `1/1 runs completed`, `No
findings were reported`, and **exit 0** — while stderr said the reply was not
valid JSON. A total failure to obtain any opinion printed as a clean review.

`has_no_usable_response` consulted `invocation.usable_runs`, which asks whether
the *process* completed and returned text. A model replying "I reviewed the
diff and found nothing" satisfies that and contributes nothing. B130 is about
usable *answers*, and the check was one layer short of the answer.

It now consults extraction, excluding a run only when extraction failed *and*
salvaged nothing — a reply with two good findings and one malformed element
still contributed an opinion and still counts.

**The pattern across 15–17:** each fix revealed the next defect, and none of
the three was reachable without running the program against the real tool. The
suite was green at 475, 478 and 482 tests respectively while the command could
not produce a single review.

## Finding 18 — `atom review` cannot review a historical range

Closing the Phase 1 bootstrap debt requires reviewing a diff from the past, and
there is no way to ask for one. `--branch REF` always diffs the working HEAD
against `REF`, so the only reviewable ranges are ones ending at HEAD.

Not a defect in anything built, but a capability the gate itself needs, which
is the kind of gap a gate is supposed to find. Recorded for the Phase 5 plan
rather than fixed here.

## Finding 19 — the confidence signal was counting runs that said nothing

Phase 4 exists to turn repetition into a confidence signal: a finding "reported in 2 of 3
runs" means more than one reported once. The denominator of that fraction came from
`InvocationReport.completed_for`, which counts runs whose *process* exited — not runs whose
*reply* could be read.

Across three real reviews, 18 model calls, `gpt-5.4` returned an unparseable reply four
times and never once failed to complete. Every one of those four stayed in the denominator.
A finding both readable replies agreed on printed "2 of 3": a dissent manufactured from a
run that never spoke.

**How it was found.** Not by a model. By pulling the run tables out of two committed review
artifacts before opening a discussion about whether A5's strictness had proved annoying in
practice. The question was "has the feared cost materialised"; the answer was "no, and a
different one did".

**What it cost to fix.** Twenty-seven tests and four rounds with the review gate, because
the first fix was wrong in three separate ways that only a real run exposed.

## Finding 20 — a measurement that skips the real path is not a measurement

The review gate reported that basing silence on `invocation.usable_runs` would miss
completed runs whose reply was empty. The claim was checked by handing an empty reply
straight to `extract_all`, which duly recorded a failure. The finding was marked refuted.

It was not refuted. `extract_all` is never called with raw runs in production — it is
called with `invocation.usable_runs`, which filters empty replies out *first*. The
measurement had bypassed the exact filter the finding was about, and confirmed a path that
does not exist.

The test, written against the real path, failed immediately and proved the model right.

**The lesson is narrower than "measure":** a measurement is only evidence about the code it
actually traverses. Reproducing a claim through a shortcut answers a question nobody asked.
This is the second time in this project an unreproduced defect was real (see the Phase 1
cold-cache non-reproduction); both times the shortcut was the problem, not the claim.

## Finding 21 — the two models are not two opinions

Across three real reviews of this change:

| Model | Findings | Real defects | False positives |
| --- | --- | --- | --- |
| `gpt-5.4` | 15 | **5** | 10 |
| `claude-haiku-4.5` | 9 | 0 | **9** |

Every one of haiku's nine was the same error: reporting a symbol as undefined because its
definition was not in the diff. It is a structural consequence of showing a reviewer only
the changed lines, so it will recur on essentially every diff that references unchanged
code — which is nearly all of them.

`gpt-5.4`'s ten false positives were not noise of that kind: several were precise, specific,
and wrong only because the behaviour they described had already been handled. Two were
confidently wrong about a case that measurement settled in one command.

**This does not argue for dropping a model.** It argues that agreement between these two
models is not the confidence signal Phase 4 assumes it is, and that the *denominator* fixed
in Finding 19 matters more than the numerator. It is recorded here because the sample is
still small and the conclusion is not yet earned.

## Finding 22 — the gate found four real defects in the fix for the gate

The change that corrected the denominator was itself reviewed by `atom review`, four times,
and every round found something true:

| Round | Defect |
| --- | --- |
| 1 | silence based on `usable_runs` missed empty replies entirely |
| 2 | a reply refused by the file guard was reported as unreadable, and reddened CI |
| 3 | `reply_was_readable` was set for schema-invalid replies, not just out-of-scope ones |
| 4 | answered and overruled overlapped, so the partial total subtracted a run twice |

None of the four were found by running the tests, which were green at every round. Three of
the four were found by a model and confirmed by measurement; one was found by a test written
*because* a model's claim needed checking.

---

## Finding 23 — the over-merge manufactures the corroboration it was chosen to avoid

A13 keeps `DEFAULT_PROXIMITY_WINDOW` at 3 and justifies it by arguing the opposite error
is worse: splitting a real defect in two "manufactures corroboration that was never
observed."

Rendering the exact measured over-merge case showed the reasoning is half right. The
over-merge manufactures corroboration too — and in the cross-model channel, which is the
one B122 says carries all the signal.

| input | `is_corroborated` (before) |
| --- | --- |
| `gpt-5.4` "nil map write" @44, `claude-haiku-4.5` "unchecked error" @45 | **True**, model_count 2 |

Two models, two demonstrably different messages, one line apart — counted as agreement.
`is_corroborated` was `model_count > 1`, and `model_count` counts distinct models in the
*group*, not on a line. Proximity grouping is deliberately loose (B118), so the group is
exactly the wrong unit for an agreement claim.

**How it was found.** Not by a model and not by a test. By rendering the case A13 already
described in prose, to check whether a different claim was true. The output answered the
question asked and exposed something else in passing.

**The general lesson.** A decision's *justification* can be stale even when its
*conclusion* is still right. The window of 3 survived; the argument for it did not. When
re-opening a decision, re-check the reasoning, not just the verdict.

**Scope, named honestly.** Never observed on real data — but only because
`claude-haiku-4.5` has never agreed with `gpt-5.4` on anything (Finding 21). Latent, not
absent. Fixed under A21.

---

## Finding 24 — three of four re-opened decisions needed no code

A2, A6, A13 and A17 were re-opened with fresh data from 18 further model calls. The
outcome:

| Decision | Outcome | Code change |
| --- | --- | --- |
| A2 | Kept — 58 calls, zero firings, kept anyway on failure-mode grounds | none |
| A6 | Unchanged — no new data | none |
| A13 | Flagged question **already satisfied** by shipped code | none |
| A17 | Closed as settled — 18 hang-free calls | none |

A13 is the instructive one. The flagged question asked for behaviour that `_line_span`
and the grouping caveat already provided; building it would have duplicated working code.
**Checking the current behaviour before implementing an agreed change cost one render and
saved a wasted cycle.**

The value of the exercise was not in the four verdicts. It was that looking closely enough
to confirm "no change needed" is what surfaced Finding 23.

---

## Finding 25 — a fix for a false positive shipped a false negative, and the gate caught it

A21 narrowed `is_corroborated` from group-level to same-line to stop the over-merge
manufacturing agreement (Finding 23). Six tests passed, four shapes were verified by hand,
and the artifacts were already written up.

The review gate then reported, in **one readable run out of six**:

> Requiring two models to match the exact same line drops corroboration for the
> nearby-line reports that `merge_findings` intentionally treats as one defect, so real
> cross-model agreement will now be understated whenever models anchor the same issue on
> adjacent lines.

Measured directly: correct. The narrowed rule hid genuine agreement for **the shape the
original analysis observed most often**, which is the shape proximity merging was built for.

**What the six tests missed.** Every over-correction guard asked "does the strong case
still fire?" using *same-line* inputs. Not one asked "what happens to two models at
adjacent lines describing the same defect" — the case the fix actually changed. The guards
were written against the mechanism that was altered, not against the behaviour that
depended on it.

**The generalisable lesson.** When narrowing a rule, the over-correction guard must be
built from the inputs that *used* to satisfy the rule and no longer do. Guards drawn from
inputs that still satisfy the rule cannot fail, and six of them passing says nothing.

**Second-order lesson.** Two decisions in a row (A5, A21) were fixes for "a number that was
not true" that themselves reported a number that was not true. Narrowing a signal is not
obviously safer than widening it — both directions are errors, and the choice needs the
same evidence either way.

**Also consistent with Finding 21:** `claude-haiku-4.5` again returned nothing across 3/3
runs; the finding came from a single `gpt-5.4` run. That is now the third change in a row
where the entire review signal came from one model.

---

## Finding 26 — the contract broke in the same commit that documented it as unbroken

The design-spec entry for A22 ended: *"The addition is additive, so `SCHEMA_VERSION` is
unchanged."*

That sentence was written while the same working tree also contained A21, which narrowed
`is_corroborated` from "several models in this group" to "several models on this line". The
new field beside it was indeed additive. The existing field was not — the same input now
produces a different answer under the same version number.

**Found by the gate, in one readable run of six:**

> This changes the meaning of the existing `is_corroborated` JSON field without bumping
> `schema_version`, so consumers treating version 1 as a stable machine contract cannot
> detect the incompatible semantics change.

**Why the reasoning failed.** "Additive" was assessed against the change being written at
that moment (A22's new field) rather than against the whole diff. A21 had already been
mentally filed as finished. **A contract question has to be asked of the release, not of the
edit.**

**What it exposed underneath.** Fixing it revealed that one `SCHEMA_VERSION` served five
independent reports, so no value of it could be true — the identical defect shape being
fixed two decisions earlier in `is_corroborated`. A single symbol answering several
questions produces a number that is not true, whatever the domain.

**Third finding in a row from a lone `gpt-5.4` run**, with `claude-haiku-4.5` again
contributing nothing. See Finding 21.

---

## Finding 27 — superseding a false sentence does not make the document true

The B122b design-spec note said `SCHEMA_VERSION` was unchanged. When A23 fixed that, the
correction was written as a **"Supersedes"** paragraph further down the file, and the
original sentence was left in place.

The gate caught it on the next pass:

> This spec now states that the schema version is unchanged, but the same diff bumps the
> review JSON contract to version 2, so the documented machine contract is incorrect.

A reader who stops at the first statement gets the wrong answer, and nothing on that line
warns them a correction exists. **A document is not a changelog.** Where a statement is
simply wrong, fix it where it is written and record the history in the findings; reserve
supersession notes for decisions that were reasonable when made.

The sentence was corrected in place, the amendment now says it corrects rather than
supersedes, and the original wording is preserved in Finding 26.

**Worth noting about the run.** This was the first fully clean review of the session:
6 of 6 runs answered, not partial, exit 0 — and it still found something. A clean run is
not an empty one.


## Finding 28 — the model that scored highest had read the answer key

While building the swap comparison, `claude-sonnet-5` scored a perfect 4/4 on
the fixture. It did so by running a repository-wide search for the string
`"planted defect"` and reading `specs/atom-cli/phase-04-review/design-spec.md`,
`decisions.md` and `findings.md` — all of which name the four planted defects by
line number, and all of which are committed.

The score was real. The measurement was worthless.

This is not a quirk of one model. Any agent given a working directory inside
this repository can reach the ground truth of every fixture-based experiment the
repository contains, and the stronger the model, the more likely it is to go
looking. **Every fixture-based measurement must run from an empty temporary
directory.** The harness now does.

> *When a subject can reach the answer key, a high score is evidence about the
> filesystem, not about the subject.*

## Finding 29 — the Phase 4 measurement harness stopped working; its numbers did not

The Phase 4 POC passes the prompt in argv, via `copilot -p`. On CLI 1.0.89-1
that call still exits zero, and the model answers as though no diff arrived and
then starts searching the filesystem for one. A 2×2 probe (baseline prompt vs
scoped prompt × repo cwd vs neutral cwd) failed in all four cells, which is what
ruled out the prompt wording; the prompt was verified intact in argv at 1,896
chars, which ruled out truncation. Delivering the identical prompt on **stdin**
returned clean JSON in all four cells.

Production was never affected: `invoke.review_command` pipes the prompt on stdin
and passes no `-p` at all, for the unrelated reason that argv corrupts large
diffs near 8,000 characters on Windows. A decision taken for one reason turned
out to be load-bearing for another.

**The harness is broken; the published numbers are not.** Both Phase 4 controls
reproduced over stdin, which is precisely the evidence needed to say so. The
first version of this finding claimed the harness "silently invalidates" its
published figures — that was written before the controls were run, and it was
false. It has been corrected where it was written rather than corrected
underneath.

> *"The tool that produced this number no longer runs" and "this number is
> wrong" are different claims, and only one of them was true.* Running the
> controls is what separated them; without controls the alarming reading is the
> one that survives.


## Finding 30 — the models differ at attribution, not at detection, and the confidence signal pays for it

Measuring `gpt-5.6-luna` produced a 15% "planted found" rate, which read as a
model that cannot review Go. Reading its replies instead of its score showed the
opposite: it identifies all four planted defects in nearly every run, describes
each one accurately, and volunteers two more that are real but unplanted -- the
nil-map assignment on a zero-value `Store`, and the file that is never closed.

Across ten runs it reported the *same* `Lookup` race at lines **18, 19, 22, 23
and 24**, anchoring it to the struct field, the doc comment, the function
signature, or the offending statement, depending on the run.

Re-scoring every model as the line tolerance widens separates the two abilities:

| Model | exact line | +/-3 | +/-6 |
|---|---|---|---|
| `gpt-5.4` | 98% | 100% | 100% |
| `claude-haiku-4.5` | 30% | 80% | 80% |
| `claude-sonnet-5` | 48% | 100% | 100% |
| `claude-opus-5` | 54% | 100% | 100% |
| `gpt-5.6-luna` | 15% | 70% | 100% |

(+/-6 is included to show where the curve flattens and should not be read as a
score: on a 48-line file with planted defects at 24, 36, 44 and 45, a window
that wide makes a hit nearly free.)

**Detection is not the differentiator. Attribution is.** Every model finds the
defects. Only `gpt-5.4` reliably says where they are.

### The cost is paid in the corroboration signal, and it is measurable

Atom's confidence signal groups findings within `--window 3` and reports how
many runs agreed. Three runs of each model, through production's own
`_group_by_proximity`:

| Model | Findings | Groups | Corroboration |
|---|---|---|---|
| `gpt-5.4` | 12 | 3 | **3/3, 3/3, 3/3** -- at lines 24, 36, 44-46 |
| `gpt-5.6-luna` | 13 | 6 | 1/3, 2/3, 2/3, 1/3, 3/3, 1/3 |

Luna found the `Lookup` race in all three runs. It is reported as **two separate
findings, at 1/3 and 2/3** -- neither showing the unanimity that actually
existed. Half its groups are single-run findings, which is exactly the signal a
developer uses to decide what to ignore.

So a model with unstable attribution is punished twice over: once because the
finding points at the wrong line, and again because Atom cannot tell that its
own repeated findings are the same finding. **The confidence signal silently
assumes that a model attributes consistently.**

### Widening the window cannot fix this

The obvious repair -- group at a wider tolerance -- is already ruled out by
evidence in this phase: the planted defects at 44 and 45 are genuinely distinct
and one line apart, and `--window 3` **already** merges them (`gpt-5.4`'s
`[44, 45, 46]` group above is two real defects reported as one). Luna shows both
failures at once: `[38, 39, 40, 41]` merges three distinct problems while `[18]`
and `[22]` split one.

There is no window that separates defects one line apart while also uniting the
same defect reported six lines apart. Precise attribution is a requirement Atom
places on the model, not a property it can recover in aggregation.

**Learnings.**

- *A metric's name is a claim, and it needs checking too.* "Planted found" was
  an exact-line match reported as a detection rate. Three times this session a
  headline number has turned out to measure something other than its label.
- *Read the replies, not only the score.* The score said luna could not review
  Go. Sixty seconds of reading said it reviews well and cannot point. Opposite
  conclusions from the same data, and only one of them survives contact with the
  raw output.
- *An aggregation step carries assumptions about its inputs.* Grouping by line
  proximity is sound only while models agree on lines; nothing in the code says
  so, and nothing measured it until a model turned up that does not.

## Finding 31 — "the harness stopped waiting" was reported as "the model did not answer"

The A26 measurement published `grok-4.7` at 6/10 answered. It had answered 10/10.
The four missing runs contain complete, correct JSON naming all four planted
defects; one of them is 1,150 bytes of accurate review. They were discarded
without being read.

The mechanism is one line in the harness:

```python
outcome=RunOutcome.TIMED_OUT if timed_out else RunOutcome.COMPLETED
```

`extract_from_run` refuses a `TIMED_OUT` run on principle -- correctly, because in
production a timed-out run is one that genuinely produced nothing usable. But
`timed_out` in the harness meant *the harness's clock expired*, which is a fact
about the harness. Whether the model answered is a fact about the model. The two
were fused into one flag, and the flag was named after the wrong one.

The cost was not a cosmetic error in a table. It was very nearly a wrong decision:
the second-most-accurate model available was presented as the least reliable, with
a 40% failure rate it did not have. Had gemini not also been measured in the same
batch, the run would have concluded that no non-Claude model was worth adopting.

**This is the fifth instance this phase of a name being a claim** -- after the
review denominator counting runs that never spoke, a false-positive count rendered
as a rate, `runs_per_model` answering two questions, and A25's "planted found"
column being read as detection when it measured attribution. The recurring shape
is now specific enough to state as a rule: **when one value is derived from two
independent facts, it will eventually be read as whichever of the two is more
convenient.** The fix is always the same -- separate the facts, and let the name
describe exactly one of them.

**Fixed** by deriving the outcome from whether a reply arrived, and keeping the
expired clock as a latency note that is already excluded from the median:

```python
outcome=RunOutcome.COMPLETED if stdout.strip() else RunOutcome.TIMED_OUT
```

Verified against the banked reply that had been discarded: it now scores 4/4.

## Finding 32 — the fix landed in one of the two places the defect lived

The same batch took **6 hours 22 minutes** against a 300-second per-call timeout,
because four calls each blocked for over 22,000 seconds. The cause was the
unbounded post-kill drain in `subprocess.run` -- the exact defect repaired in
`runner.py` earlier in the same session, and repaired properly, with tests.

The harness never used `runner.py`. It borrows production's command construction
and production's extractor, so it looked like it was exercising the real path, but
it executed calls through its own `subprocess.run`. One defect, two implementations,
and the fix went to the one that was on screen.

**The aggravating detail is that this was already known.** The spike's own module
docstring, written in the same session, described the mechanism exactly:

> `subprocess.run` kills a timed-out process and then drains its pipes with no
> deadline, so the wait is bounded by whatever child the killed process left
> behind rather than by the timeout.

It was diagnosed correctly and then *documented instead of fixed*. The
justification was that it touched only three rows and the medians excluded them,
so no published figure was wrong -- reasoning about the numbers rather than about
the defect. That held until a model hit the same path four times and the cost
arrived as six lost hours plus the discarded results of finding 31.

**Rule.** A defect that is understood well enough to write a paragraph explaining
how to read around it is understood well enough to fix. Documentation that tells
a reader to discount a value is a repair deferred, not a repair made.

**Fixed** by giving the harness the same bounded kill, imported from `runner.py`
rather than copied, so the next repair has one site and not two. Verified live: a
call with a 5-second limit now returns in 5.6 seconds where this shape previously
produced 22,434.
---

## 33. Removing a name from the code does not remove it from the evidence

A7 (Phase 4) kept two third-party MCP server names out of the shipped tool, and a
test enforced it. That test asserted that one vendor's name was absent from the
issued commands. The decision was honoured in `tools/atom/` -- which contained no
such name anywhere -- and the work was treated as done.

It was not done. The names survived in three other places the decision never
looked at:

- **The spike that produced the measurement.** `poc/review-json/spike.py` still
  passed two `--disable-mcp-server` flags naming those servers. It is committed,
  so it is published.
- **Twenty recorded replies.** Each raw envelope carries a `session.mcp_servers_loaded`
  event naming every server the CLI saw. The evidence recorded the environment.
- **The guard itself.** The test could only forbid the name by containing it, and
  the two documents explaining the removal both quoted what was removed.

The last one is the interesting one: **a check written as "this specific string is
absent" has to carry the string, so it reintroduces exactly what it exists to
exclude, and it fails to catch the next vendor's name.** Rewritten to assert that
no `--disable-mcp-server` flag is passed at all -- name-free, and strictly
stronger, because it cannot be satisfied by substituting a different vendor.

**Rule.** A decision to exclude something is scoped to wherever the excluded thing
can appear, not to the file the decision was written about. Shipped code, spikes,
recorded evidence, tests, and the decision record are all publication surfaces.

**Fixed.** Spike flags dropped; `envelope-sample.txt` deleted (nothing referenced
it, and it carried a full captured server-instruction blob); the twenty raw
envelopes redacted to `third-party-server-a` / `-b`; both documents reworded to
describe the servers without naming them.

**The redaction was verified inert before it was believed.** These files are a
re-score input (`spike.py --analyse`), so editing them could have silently moved a
published number. The analysis was run before and after: output byte-identical,
and the diff touches exactly one line in each of the twenty files. Finding 31 was
caused by trusting a derived value without re-deriving it; the same mistake was
available here and was refused.

**Known limit.** Redaction changes the files from a verbatim capture to an edited
one. Git history still holds the originals, so this scrub is a repository-hygiene
measure and not a security one -- anything genuinely sensitive would need the
history rewritten, which is why the credential scan run alongside this mattered
more than the name scrub. It found nothing.