# Design Spec — Phase 3: `atom state`

> **Status: APPROVED.** Behaviours are numbered so tests can cite them. Phase 1
> numbered B1–B34, Phase 2 B35–B70; this phase continues at **B71** and runs to
> **B102**. Three open questions were resolved in developer review — see
> *Resolved In Developer Review*.

## Purpose

Persist where a project is in the Atom pipeline, so work resumes correctly after a
restart, a crash, or a week away.

This is the phase that makes Atom a *pipeline* rather than a collection of commands.
`atom check` and `atom poc` are stateless: they take a directory and report on it.
From here on, Atom needs to know that this project is in Phase 3, that the POC is
done and the spec is not, and that a particular gate was approved by a human on a
particular day.

**The thing to get right is not the happy path.** Writing JSON to a file is not
interesting. What is interesting is that the file is the only record of work a
developer has already paid for, and every way it can be lost is a way to lose their
afternoon.

## Evidence Base

Every design decision below traces to an observation, not an opinion. All of it comes
from one spike, which refuted three of its five predictions.

| Source | What it established | Used by |
|---|---|---|
| [`poc-report.md`](./poc-report.md) C1, C2, C3 | Unlocked concurrent JSONL appends **silently lose entries**; binary mode does not fix it; an OS file lock does | B86, B87, B88, B89 |
| [`poc-report.md`](./poc-report.md) C4, C5 | `os.replace` raises `PermissionError` on Windows when the destination is open — including by a *reader* | B78, B79, B80, B84 |
| [`poc-report.md`](./poc-report.md) C6 | `[1,2,3]` is valid JSON and invalid state; `except JSONDecodeError` is not enough | B74, B75, B76 |
| [`poc-report.md`](./poc-report.md) C7 | A crash leaves a ~13 KB partial `.tmp` file behind | B81, B82 |
| [`poc-report.md`](./poc-report.md) C8, C9 | Corrupt must be distinguishable from absent; a crash leaves one truncated final log line | B77, B90 |
| Phase 1 [`design-spec.md`](../phase-01-check/design-spec.md) B17 | Report every problem at once, not just the first | B93 |
| Phase 2 [`decisions.md`](../phase-02-poc/decisions.md) A1 → P2-6 | An unanswerable question must exit non-zero | B95 |

---

## Scope

**In.** `.atom/config.json`; `.atom/state.json`; the phase state machine; the JSONL
event log; `atom init`; `atom status`.

**Out.** Multi-project state. Remote or shared state. Any network path. History
rewriting or undo — the event log is append-only and nothing in this phase deletes
from it.

---

## The Storage Model

Three files, with deliberately different durability requirements:

```
.atom/
  config.json      written once by `atom init`, then read-only in practice
  state.json       rewritten on every phase transition   -- must never be torn
  events.jsonl     appended to constantly                -- must never lose a line
  events.lock      zero-byte lock file (see B87)
  state.json.tmp   transient; a leftover means someone crashed (see B81)
```

**B71.** All Atom state lives under `.atom/` in the project root. Nothing is written
outside it.

**B72.** `.atom/` is created by `atom init` and by nothing else. Any command that
needs state and does not find `.atom/` reports that the project is not initialised
and tells the developer to run `atom init`.

**B73.** `config.json` and `state.json` are separate files on purpose. Config is what
the developer chose; state is what Atom observed. Losing state costs progress;
losing config costs a decision the developer made. They have different rewrite
frequencies and should not share a failure mode.

### Reading: validation, not just parsing

**B74.** Loading any state file validates **shape**, not just syntax. A file that
parses to a `list`, a `str`, or a `dict` missing required keys is rejected with the
same clarity as one that does not parse at all.

> *Why this is its own behaviour:* the spike fed five corruption shapes to
> `json.loads`. Four raised `JSONDecodeError`. The fifth — `[1,2,3]` — parsed
> perfectly and returned a list. A `try/except JSONDecodeError` around the load
> would have let it through, and the failure would have surfaced later as an
> `AttributeError` on `.get()`, far from the actual cause.

**B75.** Validation checks, in order: the file parses; the result is a `dict`; every
required key is present; every value has the expected type. The **first** failure is
reported, naming the file and what was wrong with it.

**B76.** A validation failure message states what was expected and what was found —
`expected an object, found a list` — never a bare `KeyError` or a traceback.

**B77.** A **missing** state file and a **corrupt** state file produce different
messages and different exit codes. Missing means "not initialised, run `atom init`".
Corrupt means "something went wrong, here is the file, here is what is wrong with
it". Conflating them would tell a developer whose state was just destroyed to
initialise a project they already initialised.

**B78.** Readers read the entire file and **close the handle immediately**. No handle
is held across a phase transition, a subprocess call, or a user prompt.

> *Why:* on Windows an open handle — even a read-only one — makes a concurrent
> `os.replace` fail with `PermissionError`. B78 is what makes B80's retries likely
> to succeed rather than merely present.

### Writing: temp-then-replace, with the replace able to fail

**B79.** Every write to `config.json` and `state.json` goes: serialise fully in
memory → write to `<name>.tmp` → flush and `os.fsync` → `os.replace` over the
destination. Nothing ever writes to the destination path directly.

**B80.** `os.replace` is **retried** on `PermissionError`, with a bounded number of
attempts and a short backoff. This is not defensive programming; the spike showed it
fails deterministically whenever another process holds the file open.

**B81.** On startup, Atom removes any `*.tmp` file it finds in `.atom/`. A leftover
temp file is the fingerprint of a previous crash.

**B82.** Removing a leftover temp file emits a `WARNING` naming the file and its size.
It is not silent — a crash the developer did not notice is worth one line of output.

**B83.** If a state write fails after exhausting its retries, the failure is **loud**
and the command exits non-zero. Atom must never report success for work whose record
it failed to persist.

**B83a.** A failed state write prints **recovery instructions**, not just an error.
The message names the file that could not be written, states what the state *would*
have been, and tells the developer how to get there — including the path of the
`.tmp` file holding the serialised state, which is the unsaved work.

> *Why:* this was the developer's answer to Q3, and it is better than either option
> the spec offered. "Fatal" and "kind to the developer" were presented as a trade;
> they are not. The command can refuse to claim success *and* leave the developer
> able to recover in one step. An error that reports a problem without a route out
> of it is only half-finished.

**B83b.** When a write fails, the temp file is **renamed to `<name>.unsaved`** and
kept. It holds the only copy of the state that could not be saved.

> *Why the rename, rather than just leaving the `.tmp` in place:* B81 sweeps every
> `*.tmp` file in `.atom/` at startup, because a leftover one is the fingerprint of a
> crash. Leaving the recovery file as a `.tmp` would mean the **next** `atom`
> invocation silently deletes the unsaved work that B83a just told the developer to
> go and look at. Moving it out of the swept namespace is what makes B83a's promise
> survive contact with B81.

**B83c.** A `*.unsaved` file is **never** removed automatically. It is reported by
`atom status` as a problem until the developer deals with it. Atom does not delete
the only copy of a developer's work on their behalf.

**B84.** The **original file is never removed before the replace succeeds.** The
spike confirmed the original survives a process killed mid-write; B84 is what keeps
that true.

### The event log: append-only, and locked

**B85.** `events.jsonl` is append-only. One JSON object per line. Nothing in this
phase rewrites or truncates it.

**B86.** Every append acquires an **OS-level file lock** first: `msvcrt.locking` on
Windows, `fcntl.flock` elsewhere. The lock is released in a `finally`.

> *Why this is not optional:* eight concurrent writers appending 1600 lines without a
> lock produced 1545 lines, of which only 3 were visibly corrupt. **55 entries
> vanished with no trace.** The same test with a lock produced 1600 clean lines. This
> is the single most consequential finding of the phase.

**B86a.** Acquiring the lock **blocks with a bounded timeout**. On timeout, the
command **fails loudly and refuses to proceed** — it does not append unlocked.

> *Why:* the alternative considered was to proceed without the lock after a timeout,
> so the tool always makes progress. That trades a loud problem for a silent one,
> which is the exact trade Atom exists to refuse. An append that cannot be made
> safely is not made.

**B86b.** A lock timeout names the lock file, the timeout waited, and **how to clear
a stale lock** if no other `atom` process is running. B86a's honesty costs the
developer a blocked tool after a crash; the message is what gives them the way out.

**B87.** The lock is taken on a **separate zero-byte file** (`events.lock`), never on
a byte range of `events.jsonl` itself. Locking a range of the file being appended to
contends with the append.

**B88.** Atom does **not** rely on `O_APPEND` atomicity, single-`write()` calls, or
pre-encoded binary payloads as a substitute for the lock.

> *Why this is stated as a prohibition rather than left implicit:* the spike measured
> exactly that "optimisation". Pre-encoding and writing once in binary mode lost
> **more** lines than text mode (68 vs 55). It is the obvious fix, it looks correct,
> and it does not work. Without B88 a future reader would remove the lock in good
> faith.

**B89.** The spike at `poc/state-persistence-on-windows/spike.py` is wired into CI
and asserts that these findings still hold, so a platform change makes this document
loudly stale rather than quietly wrong.

**B90.** Reading the log tolerates a **truncated final line** — it is skipped with a
`WARNING`. A crash mid-append leaves one, and refusing to read the entire log because
its last line is incomplete would turn a small loss into a total one.

**B91.** A corrupt line **anywhere else** in the log is also skipped with a `WARNING`
that names the line number. The log is diagnostic, not authoritative; one bad line
must not make the rest unreadable.

---

## The Phase State Machine

**B92.** A project's state is a phase (`poc`, `spec`, `tdd`, `review`, `ship`) plus a
status for that phase. Transitions are explicit; there is no inference from files on
disk.

**B93.** `atom status` reports **everything it knows at once** — current phase, status,
last event, and any problems found — rather than stopping at the first problem. This
matches Phase 1's B17: a developer wants the whole picture in one run.

**B94.** An invalid transition is refused with a message naming the current phase, the
requested phase, and which transitions are legal from here.

**B95.** If `atom status` cannot determine the state — because the file is corrupt —
it exits **non-zero**. A command that cannot answer its question has not succeeded,
even though it ran fine. This follows the Phase 2 gate decision (P2-6).

---

## Public Surface

```
atom init [--force]      create .atom/ with config.json and state.json
atom status [--json]     report current phase, status and problems
```

**B96.** `atom init` on an already-initialised project refuses and exits non-zero
unless `--force` is given. Silently overwriting a state file is destroying work.

**B97.** `--json` emits a stable schema, as in Phase 1. Human output is for people;
JSON output is a contract.

---

## Concurrency Model

**B98.** Atom **tolerates** two or more processes in one project rather than
preventing them. There is no whole-project lock; `atom status` works while a long
`atom tdd` run is in progress.

**B99.** Safety under concurrency comes from two mechanisms, not from exclusion: the
event-log lock (B86) and the state-write retry (B80).

**B100.** Concurrent writers of `state.json` are **last-one-wins**, and this is
accepted rather than solved. Two processes driving the same project through
different phase transitions at the same time is a developer error Atom does not
attempt to detect.

> *Why this is written down rather than left unsaid:* it is the known cost of B98.
> The event log is protected and the state file is not, and a reader of this code
> deserves to know that was a decision rather than an oversight. If it turns out to
> bite in practice, the fix is a lock on `state.json` too — but no evidence yet
> justifies the cost.

**B101.** Every write path assumes another process may hold the file open at any
moment. This is what B80's retries and B78's immediate closes exist for.

**B102.** `atom status` is **read-only** and takes no lock. It must remain usable
when everything else is stuck — it is the command a developer reaches for when they
want to know why.

---

## Resolved In Developer Review

| # | Question | Decision | Behaviours |
|---|---|---|---|
| Q1 | Support concurrent processes? | **Tolerate, don't prevent.** Lock the log, retry state writes. `atom status` always works. | B98–B102 |
| Q2 | Process dies holding the lock? | **Timeout, then fail loudly.** Never append unlocked. Message explains how to clear a stale lock. | B86a, B86b |
| Q3 | Failed state write fatal? | **Fatal — and print exactly how to recover.** Keep the unsaved state as `<name>.unsaved`. | B83, B83a–B83c |

**Q3's answer improved the spec.** The question offered fatal-or-kind as a trade-off.
The developer rejected the framing: a command can refuse to claim success *and*
leave the developer one step from recovery. That produced B83a–B83c, and B83b exists
only because writing it down exposed a collision with B81's temp-file sweep — the
recovery file would have been deleted by the next `atom` run.

---

## What This Phase Does Not Settle

- **Cross-process locking is unverified.** The spike used threads. `msvcrt.locking`
  and `flock` are OS-level and *should* behave identically across processes — but
  "should" is what this framework exists to replace. **Phase 3's TDD must verify the
  lock across real processes before B86 is trusted.**
- **Lock contention cost at volume** is unmeasured.
- **POSIX behaviour** has no recorded baseline. CI now runs the spike on Linux and
  macOS and will produce one.
- **State schema versioning.** What happens when a newer Atom reads an older
  `state.json` is out of scope here and needs its own decision before v1.

---

## Size

~250 lines production, ~450 lines test. The test:production ratio is higher than
earlier phases because the failure modes — concurrent appends, killed processes,
five corruption shapes — cost more to set up than the code costs to write.
