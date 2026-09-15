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

---

## Tracked Debt

| # | Item | Status |
|---|---|---|
| D1 | Cross-process lock behaviour unverified (A3) | **Must be closed in Phase 3 TDD** |
| D2 | No POSIX baseline recorded for the spike (A2) | Pending — CI will produce one |
| D3 | Lock contention cost at high log volume unmeasured | Pending |
| D4 | `state.json` schema versioning undecided | Pending — needed before v1 |
| D5 | Stale-lock recovery is manual (P3-3) | Accepted for now |

---

## Gate Record

| Gate | Date | Outcome |
|---|---|---|
| POC | this session | Spiked on developer instruction (P3-1). 3 of 5 predictions refuted. |
| Design spec | this session | **Approved** after three questions resolved (P3-2, P3-3, P3-4). |
| TDD | — | Not started. D1 must be closed here. |
