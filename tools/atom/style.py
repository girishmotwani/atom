"""The style rules that are handed to the reviewing models.

Everything in `skills/atom/references/go-style.md` is written for a human.
Until this module existed, no part of it ever reached a model: the review
prompt described the output format and nothing else. A rule a reviewer never
sees cannot change what the reviewer reports, so the document's influence on
`atom review` was exactly zero.

Two measured findings shape what is in here.

The first is that curation, not count, is the lever. A hand-picked seven beat
thirty by 33% and a hundred by 48%, while a *random* seven of the same length
behaved like the hundred. Shortening the list is not what helps; choosing is.
So this list is seven rules chosen by hand, and growing it is a decision with
a measured cost rather than a free addition.

The second is about which defects get reported at all. Seeded defects that
were pure matters of preference -- nothing visibly breaks -- were reported 0
times out of 3 *even when the reviewer had been handed the exact rule*, while
seeded defects with a visible consequence were reported 3 out of 3. What that
experiment varied was the defect, not the sentence describing it. So it
licenses one thing only: every rule below is about something that breaks, and
a rule covering pure taste would not earn a place.

It does **not** license the phrasing. Writing each rule as "this breaks"
rather than "prefer this" is reasoning from that result, not a result itself.
No experiment here has ever varied rule wording while holding the defect
fixed, so the phrasing is an untested guess that happens to be cheap. The
tripwire test that fails on "prefer", "should", "try to" and "avoid" keeps
the style consistent; it does not make it correct.

Each rule also has to survive one more filter: no tool in the toolchain gate
can catch it. `gofmt` owns formatting, `go vet` owns printf verbs and lost
cancels, `errcheck` owns discarded errors, and the race detector owns data
races on executed paths. Repeating any of those here would spend the
reviewer's attention on something already proven mechanically.
"""

from __future__ import annotations


# Ordered deliberately. The five structural rules come first and the two
# naming-and-comment rules last, at the developer's request. Position within
# the list is unmeasured -- the prompt's instruction sentence moved reported
# volume eightfold, but that was the instruction, not the rules, and nothing
# has tested whether rule 1 outperforms rule 7 -- so this order is a
# preference, not a finding, and reordering costs nothing to try.
STYLE_RULES = """These seven things no tool can check. Each one names what breaks.

1. An error returned without naming the operation reaches the caller
   as "no such file" with nothing saying what was being opened.
   Wrap it: fmt.Errorf("loading config %s: %w", path, err).

2. Every method on an interface must be implemented by every
   implementer and every test fake. A six-method interface makes
   adding a seventh a change to all of them. Keep interfaces to the
   methods the caller actually uses, declared where they are used.

3. Package-level state that can be written is reachable from every
   function in the package and from every test. It cannot be
   substituted, so code reading it cannot be tested without it, and
   tests touching it cannot run at once. Declare variables inside
   functions and pass dependencies in. If a value must live at
   package level, make it const. Go cannot make a slice or map
   const, so return a copy from a function instead.

4. A goroutine with no stated way to stop leaks. It appears as
   memory growth in production and never in a test, and the race
   detector cannot see it. Whoever starts it says in a comment how
   it ends.

5. Unexporting an identifier later breaks every caller; exporting
   one later breaks nobody. Export only what a caller outside the
   package must reach.

6. An abbreviated name (cfg, msg, n, v) makes every later reader
   rebuild its meaning from surrounding code. The author pays once,
   each reader pays again.

7. A doc comment that restates the signature goes stale without
   anyone noticing and then actively misleads. Say why the thing
   exists, or say nothing."""


def style_rules_block() -> str:
    """Return the rule text that goes into the review prompt.

    A function rather than a bare constant because the next open question is
    whether a diff touching only one area should receive a list narrowed to
    that area. That experiment needs somewhere to branch, and a caller that
    already asks a function will not have to change when it does.
    """

    return STYLE_RULES
