# TDD Log - Phase 5: `atom ship`

A record of how the code was built, kept because the order things happened in is
itself evidence.

This log was written **after** the phase shipped, which is a process failure in
its own right and is recorded as such in
[`decisions.md`](decisions.md). Phases 1 through 4 each produced one as the work
happened; Phase 5's orchestrator never did. It was discovered during Phase 6's
discussion gate, by a survey that was looking for exactly this kind of gap. The
content below is reconstructed from the commits, the test files, and the
measurements taken at the time — not from memory of intent.

Five cycles. The phase's defining fact is that it produced **three defects after
the design spec was written, and all three lived in a seam** — between two
components that had each been examined carefully on their own.

---

## Cycle 1 - `body.py` (B146-B152)

**RED.** 22 tests against link assembly, the parts table, and the body contract.
Suite count: 487 before the phase, 509 after this cycle.

**GREEN.** The pull request body, assembled entirely out of links to artifacts
that already exist. Nothing in `body.py` authors prose; it selects, orders, and
points. That constraint is the whole design — a body that summarises can drift
from what it summarises, while a body made of links cannot.

**Two of the five cycle's test groups passed on the first attempt.** They are
regression guards rather than discoveries, and are flagged here as such because
a log that presents every green as a finding is not worth reading.

**The cycle's real output was a defect in the specification, not the code.**
B148's parts table bounded the "Why" section at *one paragraph*. The contract
returns the design spec's Purpose section verbatim, and Phase 5's own Purpose is
**two** paragraphs. Shipping Phase 5 would have violated Phase 5's own stated
bound, in the very document that stated it. The spec was corrected rather than
the code, because the code was right and the bound was arbitrary.

---

## Cycle 2 - `ship.py` (B138-B157)

**RED.** 83 tests against preconditions, phase resolution, gate execution,
pushing, PR creation, PR update, and refusal. Suite count: 509 before the cycle,
592 after it.

**GREEN.** `run_ship`, `ShipOutcome`, `PrAction`, and `ShipRefused`. Every
refusal names the remedy command a developer can run.

**This cycle was delegated to a background agent, and the delegation itself
produced the phase's sharpest process finding.** The agent generated nothing for
**2.4 days**. The cause was not the agent: the prompt written for it said to
*poll for* `body.py`, a dependency owned by a different agent, with no release
signal of any kind. A background worker was told to wait for an event that could
never be delivered.

> **Lesson:** never make one parallel agent wait on a file another one owns.
> Give every agent independent work at the start, and wire shared dependencies
> last.

Two further honest notes on this cycle:

- **Test distribution reflects supervision, not importance.** B145a received 11
  tests. B154, B155, and B147b received one each. The difference measures how
  hard the follow-up prompt pushed on each, not how much risk each carried.
- **B153 had zero citation comments** when the cycle finished. Before writing
  replacement tests, the *behaviour* was checked — and it was fully covered by
  `test_re_running_on_a_branch_with_a_pr_updates_the_body`, `PrAction.UPDATED`,
  and `_edit_pull_request`. Only the traceability comment was missing. Checking
  first avoided writing a duplicate test to satisfy a comment.

The agent also raised a genuine design objection rather than implementing the
spec as given: the pipeline pushed before it checked. That became Cycle 3.

---

## Cycle 3 - reordering the pipeline to check → push → assemble (B140, B141)

**RED.** 3 tests. Suite count: 592 before the cycle, 595 after it.

**GREEN.** The pipeline became preconditions → resolve phase → **fresh check** →
**push** → assemble → create or update. A push is the first irreversible act in
the sequence, so nothing irreversible now happens before the gates have passed.

**The reorder passed all 83 existing ship tests identically, before and after.**
Eighty-three tests covering this exact pipeline could not tell the two orderings
apart, because not one of them asserted anything about *order*.

> **Lesson:** an ordering that nothing asserts is free to regress silently.

The three new tests were then verified the only way that proves anything: **the
code was actually reverted to the old order and the tests were run.** Two of the
three failed. The third passed under both orderings, and is labelled in the file
as a regression guard rather than being quietly counted as evidence. Reasoning
about whether a test *would* fail is not the same as watching it fail.

---

## Cycle 4 - CLI wiring, and the defect that 595 green tests did not see

**RED.** 18 tests in `test_cli_ship.py`. Suite count: 595 before the cycle, 613
after it.

**GREEN.** `atom ship` wired into `cli.py` with the established
`_add_X_parser` / `_run_X_command` pattern and mapped exit codes.

**The first real invocation of `atom ship` crashed immediately:**

```
TypeError: default_gates() got an unexpected keyword argument 'include_race'
```

The parameter is `enable_race`. The call sat **one line above** `run_ship`. At
the moment it crashed, the suite was **595 green** and `atom ship --help`
printed a flawless help page.

> **`--help` is not a smoke test.** argparse never reaches the command function,
> so a help page proves the parser parses and nothing else.

This is not an assertion; it was measured. After `test_cli_ship.py` was written,
the exact typo was **re-introduced** and the file re-run: **16 of the 18 tests
failed, and the only two that passed were the two `--help` tests.**

The fixture design follows directly from that. `calls` patches
`atom.cli.run_ship` and deliberately leaves `default_gates` real — patching one
level lower would have mocked away the precise line that broke. The rule the
phase adopted: **patch one level below the wiring, never at it.**

Re-running after the fix produced real behaviour against real `git`: B140 fired
on a dirty tree, naming the exact file just edited; after committing, B141 fired
on the missing upstream, naming the exact remedy command.

---

## Cycle 5 - B141a: an upstream existing is not the remote holding the commit

**RED.** 5 tests. **3 of them failed**, which makes this the one cycle in the
phase that went red the ordinary way. Suite count: 613 before the cycle, 618
after it.

**GREEN.** `_require_upstream` now also calls `_commits_ahead_of_upstream`,
using `git rev-list --count @{u}..HEAD`. An **unreadable count refuses** rather
than assuming zero.

**This defect was found by `atom review --branch main` — the tool built in
Phase 4, reviewing the phase built after it.** It was reported at high severity
in 3 separate runs, and was then verified by reading the code rather than
accepted on the model's word.

`_require_upstream` checked only that an upstream *existed*. A branch with an
upstream and three unpushed commits passed it — and B149 then pinned every
artifact link in the pull request body to a commit GitHub had never seen. That
is precisely the 404 that B149 exists to prevent. **The function answered its
own name correctly and its purpose wrongly.**

The review run that found it is also the phase's strongest evidence against
consensus filtering: 6 of 6 runs completed, `claude-haiku-4.5` found **nothing
at all**, and **every** `gpt-5.4` finding appeared in only **1 of 3** runs —
including this one.

> **Low consensus is not a false positive.** Agreement measures how many models
> looked, not how true a finding is. A consensus threshold would have suppressed
> the best finding of the phase.

---

## Result

| | |
|---|---|
| Tests | 618 (487 before this phase) |
| Phase 5 collected files | `test_body.py` 22; `test_ship.py` 91; `test_cli_ship.py` 18 |
| Coverage | 97% overall; `body.py` 100%, `ship.py` 99% |
| Uncovered | `cli.py` 91% |
| Shipped by | `atom ship --push` — the tool opening its own pull request, PR #2, exit 0 |

Verification of the ship itself was not left at exit 0. The stored body was read
back with `gh pr view` (both Purpose paragraphs present; Evidence correctly reads
"not a Go module; no gates run"), and **two artifact links were resolved at the
pinned SHA through `gh api`** — proving B149 against real GitHub rather than
against the test suite's fake runner.

## What this phase says about the method

**All three defects found after the spec was written lived in a seam.** The
`go.mod` gap sat between `check` and `ship`. The push/check ordering sat between
`gh` and `check`. B141a sat between git's notion of an upstream and B149's notion
of a resolvable link. Each component had been reviewed carefully on its own, and
each was correct on its own. **The defects were in the space between them, which
is the one place a per-component review never looks.**

Phase 4 concluded that a green suite proves only that the implementation matches
the tests' mental model. Phase 5 sharpens it by one turn: **595 green tests and a
clean `--help` still shipped a command that could not run at all.** That is six
phases in a row where a green suite did not establish that the program works.
