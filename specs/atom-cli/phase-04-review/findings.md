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
