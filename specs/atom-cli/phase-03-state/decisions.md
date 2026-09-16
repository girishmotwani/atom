# Decisions — Phase 3: `atom state`

Two kinds of decision are recorded here, kept apart on purpose:

- **P3-n — developer decisions.** Made by the human at a gate.
- **A-n — agent decisions.** Made by the agent because the spec did not say.
  Every one of these is a place the agent chose on the developer's behalf, and
  each is listed so it can be overturned.

---

## Developer Decisions

### P3-1 — Run the Phase 3 POC rather than skip it

**Context.** The phase plan said *"POC question — justifiably skipped. No technical
uncertainty."* That is the same sentence that was used to skip the Phase 2 POC, where
it turned out to be wrong and cost the project its biggest finding.

The agent challenged the claim with three specific questions rather than accepting or
silently overriding it. The developer pushed back on how the questions related to
Phase 2 — a fair challenge, since the agent had conflated two things: the *questions*
are Phase 3's own, and the only carry-over is the skip-justification phrase.

**Decision.** Spike all three questions.

**Outcome.** Three of five predictions refuted. See [`poc-report.md`](./poc-report.md).
The phrase "no technical uncertainty" has now been wrong twice, written by the agent
both times. It is a red flag, not a justification.

### P3-2 — Tolerate concurrent processes rather than prevent them (Q1)

**Decision.** Atom does not take a whole-project lock. Two processes may run at once.
Safety comes from the event-log lock and state-write retries, not from exclusion.

**Accepted cost.** Concurrent writers of `state.json` are last-one-wins. Recorded
explicitly as B100 rather than left as an emergent property.

**Rationale.** Being unable to run `atom status` while a build is in progress would
be a daily annoyance for a rare failure. The log — the thing the spike proved is
genuinely at risk — is protected either way.

**Behaviours.** B98–B102.

### P3-3 — A lock timeout fails loudly rather than proceeding unlocked (Q2)

**Decision.** Appending blocks with a bounded timeout. On timeout the command fails
and refuses to append.

**Rejected.** Proceeding without the lock after a timeout, so the tool always makes
progress. That converts a loud failure into a silent one — the trade Atom exists to
refuse, and precisely the failure mode the spike measured.

**Accepted cost.** A process killed while holding the lock leaves a stale lock file
that blocks the tool. B86b requires the error message to explain how to clear it.

**Behaviours.** B86a, B86b.

### P3-4 — A failed state write is fatal *and* prints how to recover (Q3)

**Decision.** Exit non-zero, and tell the developer exactly how to recover the
unsaved state.

**This answer was better than either option offered.** The question was framed as a
trade-off: fatal (honest about pipeline integrity) versus non-fatal (kind to a
developer who just did twenty minutes of work). The developer rejected the framing.
A command can refuse to claim success *and* leave the developer one step from
recovery; those were never actually in tension.

**Consequence found while writing it down.** B83a promised to point the developer at
the file holding their unsaved state. That file was the `.tmp` file — which B81
sweeps at startup. The next `atom` invocation would have silently deleted the work
the error message had just told them to go and look at. Fixed by renaming it out of
the swept namespace (B83b) and never auto-deleting it (B83c).

This was caught in the spec, not in TDD, and only because the recovery path was
written out concretely instead of being left as "report an error".

**Behaviours.** B83, B83a, B83b, B83c.

### P3-5 — `atom status` splits its output by stream

**Question.** The spec says status reports everything at once (B93) and that
`--json` is a contract (B97), but says nothing about *which stream*. The agent
proposed one report on stdout with nothing on stderr.

**Decision.** Split by stream. The answer — project, module, phase, last event —
goes to **stdout**. The problems go to **stderr**. Neither is duplicated.

**Why this is better than what was proposed.** Problems on stdout means
`atom status > phase.txt` swallows them: the redirect hides precisely what the
developer needs to see. Splitting keeps the answer machine-capturable *and* the
problems visible. stdout carries a one-line pointer (`1 problem reported below.`)
so a redirected stdout still shows there was more to the story.

**Behaviours.** Refines B93 and B97. See A7 for the full record.

---

## Agent Decisions

### A1 — The spike asserts its findings instead of merely reporting them

**Decision.** `poc/state-persistence-on-windows/spike.py` carries a table of expected
outcomes and exits non-zero if reality diverges, saying the report is now stale.

**Why.** A spike is evidence only for as long as it still runs. Phase 2 set this
precedent. The design quotes specific numbers; if the platform changes, the right
outcome is a loud failure naming the stale document.

**Overturnable by.** A developer who wants spikes to stay pure observations.

### A2 — Windows expectations are not asserted on POSIX

**Decision.** The assertion in A1 applies only on `win32`. Elsewhere the spike
observes, prints whether it matches the Windows baseline, and exits 0.

**Why.** The findings were measured on Windows and nowhere else. Several are
explicitly platform behaviour — POSIX renames over open files happily, and `O_APPEND`
is widely believed atomic there. Asserting numbers on Linux that nobody has ever
observed would be manufacturing evidence, which is the one thing this framework must
never do.

**Consequence.** There is currently no POSIX baseline. CI now produces one on every
run; once recorded in `poc-report.md`, the POSIX branch can become an assertion too.

### A3 — Cross-process locking is called out as unverified rather than assumed

**Decision.** B86 specifies an OS-level lock, but the spec states plainly that the
spike proved it only **between threads**, and requires Phase 3's TDD to verify it
across real processes before B86 is trusted.

**Why.** `msvcrt.locking` and `fcntl.flock` are OS-level primitives and *should*
behave identically across processes. "Should" is exactly what this framework exists
to replace. The thread result is strictly weaker evidence for the fix than for the
problem: if threads interleave, processes certainly will — but a lock working between
threads does not prove it works between processes.

**Risk if wrong.** The central safety mechanism of the phase would not work, and
every test would still pass, because the tests would share the flaw.

### A4 — B88 is written as a prohibition

**Decision.** The spec explicitly forbids relying on `O_APPEND` atomicity or
pre-encoded single writes as a substitute for the lock.

**Why.** Normally a spec says what the code does, not what it must not do. This
exception is earned: the spike *measured* that optimisation and it lost more lines
than the naive version (68 vs 55). It is the obvious fix, it looks correct, and it
does not work. Without B88 a future reader removes the lock in good faith and
reintroduces silent data loss.

### A5 — `atom status` takes no lock

**Decision.** B102 makes status read-only and lock-free.

**Why.** It is the command a developer reaches for when something is stuck. A
diagnostic tool that can be blocked by the thing it is meant to diagnose is not
much of a diagnostic tool.

**Tension.** It can therefore read `state.json` while another process is mid-replace.
B78's immediate-close and B79's atomic replace mean it sees either the old file or
the new one, never a torn one — but it may see a *stale* one. Accepted.

### A6 — Recovery instructions extended from failed writes to corrupt reads

**Decision.** A corrupt `state.json` or `config.json` now prints the same kind of
recovery instructions that a failed *write* prints: check for a `.unsaved`
sibling, otherwise `atom init --force`, with the reassurance that spikes and
specs are untouched.

**Why.** P3-4 settled the principle — a fatal error must say exactly what to do.
But it was asked and answered about *write* failures only, so the spec gained
detailed recovery text on that path and none on the corrupt-read path. The
asymmetry was invisible in the document, because the two behaviours live in
different sections and each reads well alone. It became obvious within seconds of
running the program by hand.

Corruption is the **likelier** of the two events: the spike proved torn writes
happen, whereas an exhausted-retry write failure needs a handle held across ten
attempts.

**Why this is the developer's call to review.** The principle was theirs; only
its scope was widened. If they intended P3-4 narrowly, this should be reverted.

### A7 → P3-5 — Text output splits by stream: answer on stdout, problems on stderr

**Agent proposal.** One report on stdout, problems included, nothing on stderr.

**Developer decision (P3-5).** Split by stream instead. The answer — project,
module, phase, last event — goes to **stdout**; the problems go to **stderr**;
neither is duplicated. stdout carries a one-line pointer (`1 problem reported
below.`) so a redirected stdout still shows there was more to the story.

**Why the question arose.** The spec (B93, B97) says status reports everything at
once and that JSON is a contract, but says nothing about *streams*. The first
implementation printed problems to both, which running it by hand showed as the
same message twice, with the stderr copy missing its newline and colliding with
the report: `...mid-write.Project: C:\...`. Every test passed.

**Why the developer's answer beats the proposal.** Putting problems on stdout
makes `atom status > phase.txt` swallow them silently — the redirect hides
exactly what the developer needs to see. Splitting keeps the answer
machine-capturable *and* the problems visible. The agent proposal solved the
duplication and missed that.

**Cost.** Six tests updated. `render_status_text` and `render_status_problems`
are now separate functions, which is also what makes "exactly once" testable:
`test_status_prints_each_problem_exactly_once` counts across both streams.

### Gate outcomes for A6 and A7

Both were put to the developer at the Phase 3 gate. Recorded here because an
agent decision is provisional until reviewed, and the review is the point.

| # | Decision | Outcome |
|---|---|---|
| A6 | Recovery instructions extended from failed writes to corrupt reads | **Confirmed.** P3-4 is a general principle, not specific to writes. |
| A7 | Text output stream handling | **Revised → P3-5.** Answer on stdout, problems on stderr, neither duplicated. The agent proposal would have hidden problems behind a stdout redirect. |

---

## Tracked Debt

| # | Item | Status |
|---|---|---|
| D1 | Cross-process lock behaviour unverified (A3) | **Closed in Phase 3 TDD.** Verified across real processes, then teeth-checked by neutering the lock: 553/600 lines survived without it, 600/600 with it. See [`tdd-log.md`](tdd-log.md) Cycle 1. |
| D2 | No POSIX baseline recorded for the spike (A2) | Pending — CI runs the spike on Linux and macOS, but the numbers have not been read into a report. `filelock.py`'s POSIX branch is the one uncovered region of the phase (84%). |
| D3 | Lock contention cost at high log volume unmeasured | Pending |
| D4 | `state.json` schema versioning undecided | Pending — needed before v1. Changing the shape today breaks existing projects with a corruption error rather than a migration. |
| D5 | Stale-lock recovery is manual (P3-3) | Accepted for now |

---

## Gate Record

| Gate | Date | Outcome |
|---|---|---|
| POC | this session | Spiked on developer instruction (P3-1). 3 of 5 predictions refuted. |
| Design spec | this session | **Approved** after three questions resolved (P3-2, P3-3, P3-4). |
| TDD | this session | **Complete.** 275 tests, 94% coverage. D1 closed. Five cycles recorded in [`tdd-log.md`](tdd-log.md); behaviour-to-test mapping in [`test-spec.md`](test-spec.md); eight findings in [`findings.md`](findings.md). A6 confirmed; A7 revised into P3-5 by the developer. |
| Phase gate | this session | **Closed.** Developer reviewed both agent decisions: A6 confirmed, A7 revised into P3-5 and reimplemented. 275 tests green, links resolve. |
