# Decisions — Phase 5: `atom ship`

Two kinds of decision are recorded here, kept apart on purpose:

- **P5-n — developer decisions.** Made by the human at a gate.
- **A-n — agent decisions.** Made by an agent because the spec did not say.
  Every one of these is a place an agent chose on the developer's behalf, and
  each is listed so it can be overturned.

---

## Developer Decisions

### P5-1 — A failing check refuses, with an explicit override flag

**Context.** The spec did not say what happens when the fresh `atom check` fails.
Three options were live: ship anyway and state it, refuse outright, or refuse
with an override.

**Decision.** Refuse, with `--allow-failing-checks` as an explicit override.
Expanded into B147, B147a and B147b. The override opens the pull request,
changes nothing the body claims, and **still exits non-zero** — because the
artifact existing and the run succeeding are different facts.

**Why a flag rather than a prompt.** Ship must be runnable from CI, where there
is nobody to answer a prompt.

---

### P5-2 — A tree with no Go module has not failed

**Context.** `run_check` raises `NotAGoModuleError` for any directory without a
root `go.mod` — *before any gate runs*. The Atom repo has no `go.mod` anywhere.
B145 as written would have made `atom ship` unable to ship Atom itself,
including Phase 5's own pull request.

**Decision.** Skip the gates and record *"not a Go module — no gates run"* in the
body. Added as B145a, leaning on a principle already in `check.py`: *"SKIPPED and
WARNING are both non-failures by design: a tree with no tests has not failed."*
A tree with no Go module has not failed either.

**Consequence carried into the tests.** A B147 test must use a `tmp_path` that
really contains a `go.mod`, or it proves B145a by accident; a B145a test must use
one that really does not. Pinned from opposite ends by a file on disk.

---

### P5-3 — The check moves ahead of the push

**Context.** The implementing agent pushed back on the spec: with `--push`, a
failing gate and no override, the pipeline pushed the branch and set its upstream
*before* refusing to open the PR.

**Decision.** Reorder to **check → push → assemble**, and amend the spec. B149's
real requirement — push before *assembly* — is satisfied either way, and a
refusal now leaves the remote untouched.

**Noted at the time.** The agent implemented the spec's stated order and flagged
the problem rather than silently "fixing" it. That is the behaviour the framework
wants; recorded so it is reinforced rather than assumed.

---

### P5-4 — Review before shipping

**Decision.** Run `atom review --branch main` before opening the pull request,
rather than shipping on a green suite.

**Outcome.** It found a high-severity defect that 104 tests had missed (B141a).
The decision paid for itself on its first use.

---

### P5-5 — Fix the high finding, defer the mediums

**Context.** The review returned one high and three mediums.

**Decision.** Fix the upstream defect now; record the rest in
[`findings.md`](findings.md) §8 as F5-1 through F5-5 rather than expanding Phase
5's scope.

---

### P5-6 — Delegate the TDD, verify every cycle

**Decision.** Two parallel agents wrote `body.py` and `ship.py`; the developer
verified each cycle and the CLI wiring stayed with the orchestrator.

**Outcome, stated plainly.** The delegation worked — 22 and 86 tests, both green,
both honest about what they could not prove. The wiring the orchestrator kept
is the one part that shipped a bug. The lesson is not "delegate less"; it is that
**the unshared seam is the dangerous one** (see findings §1).

---

## Agent Decisions

Each of these was chosen because the spec was silent. All are reversible.

### In `ship.py`

| # | Decision | Reasoning given |
|---|---|---|
| A5-1 | `base_branch` defaults to `"main"` | The spec never named a default; exposed as `--base` and as `DEFAULT_BASE_BRANCH` |
| A5-2 | `--phase` used verbatim if it resolves, else resolved by globbing `specs/*/<phase>` | The project segment is not otherwise available from the branch name |
| A5-3 | The body file is written to the **system temp dir**, never inside the repo | Writing inside would create an untracked file and violate the dirty-tree precondition ship had just enforced |
| A5-4 | Existing-PR lookup uses `gh pr view --json url` and parses JSON, not `--jq .url` | A raw stdout blob can never then masquerade as a URL |
| A5-5 | Empty or failed commit-subject lookup is non-fatal | The body degrades gracefully rather than aborting a ship over a cosmetic section |
| A5-6 | Verdict rows capped at 5 | Matches the five default gates. **Known limit:** `_failing_gate_names` reads the capped rows, so a sixth failing gate would go unnamed |
| A5-7 | An unreadable ahead-count **refuses** rather than assuming zero | Ship cannot then show the remote holds the commit, and a PR whose links it cannot vouch for is worse than a refusal one command clears |

### In `body.py`

| # | Decision | Reasoning given |
|---|---|---|
| A5-8 | `extract_purpose` returns the **whole** Purpose section, not the first paragraph | Truncating would silently drop authored content — the exact omission this project exists to prevent |
| A5-9 | Absent purpose, commits and artifacts each render an explicit italic note | Consistent with B145a: an absent section and a silently missing one are different outcomes, and only one is honest |
| A5-10 | `_render_evidence` states the verdict in words | An overridden failing check can then never read green |

**A5-8 corrected the spec.** B148's parts table bounded "Why" at *one paragraph*
while the same behaviour's contract returns the section's prose — and this
spec's own Purpose is two paragraphs. A faithful `atom ship` shipping Phase 5
would have violated Phase 5's own stated bound. The bound now reads *"the
section, however many paragraphs"*.

### In `cli.py`

| # | Decision | Reasoning given |
|---|---|---|
| A5-11 | The CLI returns its own `EXIT_PASSED` / `EXIT_CHECK_FAILED` rather than `ShipOutcome.exit_code` | The CLI owns exit codes via named constants. **Leaves two sources of truth** — recorded as F5-5 |
| A5-12 | Every `ShipRefused` leaves by one route | B156: ship reuses the Phase 1–3 exit scheme rather than inventing a "precondition" code no other command speaks |

---

## Honest notes

- **Test distribution reflects emphasis, not importance.** B145a received 11
  tests; B154, B155 and B147b received one each. That ordering tracks how hard
  the orchestrator pushed in a follow-up message, not the behaviours' relative
  weight.
- **Cycles 3 and 5 of `body.py` passed on first run.** The agent flagged this
  rather than presenting them as red-green. Those tests are regression guards.
- **B153 was implemented and tested but never cited by number** until the
  orchestrator's coverage audit caught it. The behaviour was never at risk; the
  traceability was.
- **Phase 4 decisions A2, A5, A13, A6 and A17 were surfaced for review and never
  answered.** Still open.
