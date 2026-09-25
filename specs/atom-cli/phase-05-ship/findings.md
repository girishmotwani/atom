# Findings — Phase 5: `atom ship`

Discoveries made while building Phase 5 that outlive it. Recorded here rather
than in commit messages because several of them change how later phases should
be built.

---

## 1. `--help` is not a smoke test, and believing it was cost a shipped bug

`atom ship` was wired into the CLI with 595 tests green. `atom ship --help`
printed a flawless usage block. The first real invocation died:

```
TypeError: default_gates() got an unexpected keyword argument 'include_race'
```

The parameter is `enable_race`. The call sits in `_run_ship_command`, one line
above the `run_ship` call — and **argparse never reaches the command function**.
`--help` exercises the parser and exits. It cannot reach a single line of the
code that does the work.

This is the sixth consecutive phase whose green suite did not prove the program
runs, and the first where the gap was *the wiring itself* rather than the
library beneath it. The reason is structural: the ship tests call `run_ship`
directly, and the two implementing agents were deliberately kept out of
`cli.py`. Nobody tested the seam between them.

### The fix, and the proof it works

`test_cli_ship.py` goes through `main()` with the real `default_gates`.
Re-introducing the exact typo now fails **16 of 18** tests. The only two that
still pass are the two `--help` tests — which is the entire point, stated as a
measurement rather than an opinion.

| What was tested | Caught the typo? |
|---|---|
| 595 unit tests calling `run_ship` directly | ✗ |
| `atom ship --help` | ✗ |
| 18 tests going through `main()` | ✓ (16 of 18) |

**Rule for later phases.** Every command needs tests that call `main()` with the
real collaborators, not just tests of the function the command calls. Patch one
level *below* the wiring — never at it — or the mock removes the defect.

---

## 2. An upstream existing is not the remote holding the commit

Found by running `atom review --branch main` on Phase 5's own branch: the
reviewer Phase 4 built, reviewing the phase that would ship it.

`_require_upstream` asked one question — *is an upstream configured?* — for a
precondition that needed a different one. A branch with an upstream and three
unpushed commits passed. Then B149 pinned every artifact link to `HEAD`, and the
pull request's every link 404ed: the exact failure B149 exists to prevent,
reached *through* the precondition meant to guarantee it.

Two facts were conflated, and the names were close enough to hide it:

| Fact | What it tells you |
|---|---|
| The branch has an upstream | there is somewhere to push *to* |
| The remote contains `HEAD` | the links in the body will resolve |

Only the second one matters to B149. Only the first was checked.

### Low consensus did not mean false positive

Worth recording precisely, because it contradicts the obvious reading of the
`--runs 3` design:

| | |
|---|---|
| Runs completed | 6/6 (`gpt-5.4` 3/3, `claude-haiku-4.5` 3/3) |
| Findings from `claude-haiku-4.5` | **none** |
| Consensus on every `gpt-5.4` finding | **1 of 3 runs** |

Every finding was low-agreement, and the highest-severity one was real. The
second model found nothing at all. **Agreement measures how many models looked,
not how true the finding is.** A consensus threshold that suppressed 1-of-3
findings would have suppressed this bug.

---

## 3. A refusal should leave no trace

The design spec's pipeline put the push before the fresh check. Its stated
justification only ever covered push-before-*assembly* — links must name a
commit the remote already holds. Nothing required push-before-*check*, and
putting it there had a cost: `atom ship --push` on a failing gate pushed the
branch and set its upstream, **then** refused to open the PR. A command that
declines to act had changed the remote on its way to declining.

Found by the implementing agent reading the spec, not by the POC — the POC
probed `gh` and `atom check` separately and never asked what their ordering
implied. This is the second Phase 5 defect of that exact shape (see the `go.mod`
gap, B145a): **both sat between two components each examined carefully and never
examined together.**

### The reorder was invisible to 83 tests

All 83 ship tests passed identically before and after. An ordering that nothing
asserts is an ordering free to regress. Three tests now pin it, and two were
confirmed to fail by *actually reverting the code and running them* rather than
by reasoning that they would. The third — an overridden failing check must still
push — passes under both orders, so it is labelled a regression guard, not
evidence.

---

## 4. One observation still cannot distinguish a behaviour from a blip

The first `atom review` run failed outright:

```
atom review: No review model could be called: gpt-5.4 (**pong** Command timed out after 60 seconds.)
```

Both models answered `pong` and then failed to exit inside the 60-second probe
timeout. Re-measured immediately afterwards through the same runner: **19.5s and
20.6s**. A third measurement direct from the shell: **33.0s**. The next full
review completed 6/6 runs.

It was latency, not a defect. This is the same trap as the Phase 5 POC's 44.4-
second `gh` call, and it has now been avoided twice by the same discipline:
**re-measure before recording a finding.**

### But it exposed something real

| | |
|---|---|
| Probe timeout | 60s, hardcoded |
| Review timeout | 300s, hardcoded |
| Override flag | **none** |
| Observed probe times | 19.5s, 20.6s, 33.0s |

A 33-second observation against a 60-second budget is under 2× headroom, and
**a single slow probe fails the entire review** with "no model could be called".
`atom review` has no `--timeout`. A developer on a slow network cannot raise it.
Pending — a candidate for a later phase.

---

## 5. A phase diff is bigger than the assumption behind reviewing it whole

`atom review` sends the whole diff in one call, justified by phases keeping
diffs small. Phase 5's actual diff against `main`:

```
17 files, 5,024 insertions, 233,651 characters
```

It fit, and the review succeeded. But the number is far from "small", and it
grows with every artifact a phase produces — specs, POC reports and test specs
are most of it, not code. The assumption is not yet wrong; it is closer to its
limit than the reasoning behind it suggests. Worth re-measuring in Phase 6
rather than waiting for a truncation nobody notices.

---

## 6. Two sources of truth for one exit code

`ShipOutcome.exit_code` returns a hardcoded `0` or `1`. `cli.py` returns
`EXIT_PASSED` / `EXIT_CHECK_FAILED`. They agree today by coincidence of value,
not by construction, and the CLI does not use the property at all.

No live bug — recorded because the two will diverge silently the first time the
constants change. Pending.

---

## 7. Never make one background agent wait on a file another owns

`ship.py` was delegated to an agent told to "poll for" `body.py` and not create
it. That is a dependency with **no release signal**. The agent produced nothing
for 2.4 days.

The fault was in the instruction, not the agent: it was given a blocking
condition and no way to observe it clearing. The unblock that worked did two
things — told it to stop waiting, and gave it the ~15 behaviours that needed
nothing from `body.py`.

**Rule.** Give every parallel agent work that is independent *at the start*, and
let shared dependencies be wired in last.

---

## 8. Deferred findings from the Phase 5 review

Real, judged non-blocking, carried forward rather than dropped.

| # | Where | Finding | Status |
|---|---|---|---|
| F5-1 | `body.py:50` | Artifact links hardcode `https://github.com`; a GitHub Enterprise remote produces links to the wrong host | Pending |
| F5-2 | `ship.py:596` | Existing-PR lookup ignores `--base`, so shipping one branch to a different base updates the wrong PR | Pending |
| F5-3 | `ship.py:376` | `--phase` resolves to any directory on disk; a path outside the repo is accepted and rendered into blob links | Pending |
| F5-4 | `review` | Probe and review timeouts are hardcoded with no override (see §4) | Pending |
| F5-5 | `ship.py` | `ShipOutcome.exit_code` duplicates the CLI's exit constants (see §6) | Pending |

---

## Learnings

- **Test the seam, not just the parts.** Both Phase 5 defects found after the
  spec was written lived *between* two components, each of which had been
  examined carefully on its own.
- **Ask what a check is for, not what it checks.** `_require_upstream` answered
  its own name correctly and its purpose wrongly.
- **A green suite is not a specification.** Two separate behaviours this phase —
  the pipeline order and the upstream precondition — could be changed or broken
  without a single test objecting.
- **Re-measure before recording.** Twice now, a first observation would have
  produced a false finding.
- **Dogfooding found what testing did not.** The highest-severity defect in
  Phase 5 was found by running Phase 4's tool against Phase 5's code.
