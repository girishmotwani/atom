# Findings — Phase 3: `atom state`

Discoveries made while building Phase 3 that outlive it. Recorded here rather
than in commit messages because several of them change how later phases should
be built.

---

## 1. Unlocked concurrent appends silently lose entries — and the obvious fix is worse

Found by the Phase 3 spike, before any code was written. Eight writers, 200
entries each, 1600 expected:

| Approach | Lines present | Lost | Corrupt |
|---|---:|---:|---:|
| Text mode (`a`, utf-8) | 1545 / 1600 | 55 | 3 |
| Binary mode, one pre-encoded `write()` (`ab`) | 1532 / 1600 | **68** | 4 |
| Locked append | **1600 / 1600** | **0** | **0** |

The loss count varies between runs — 55, 68, 73, 85 were all observed. It is a
race, not a constant, which is itself worth knowing: a single clean run proves
nothing here.

Two things matter, and only one of them is obvious.

The obvious one: unlocked appends lose data.

The one that is easy to miss: **most losses leave no trace.** 1600 written, 1545
present, only 3 unparseable. A test asserting "every line in the log is valid
JSON" passes. The file looks healthy. Only counting reveals that 55 entries never
arrived — a corrupt line is visible, a missing line is not.

The third thing, which is why B88 is written as an explicit prohibition: **binary
mode is not a fix — it is worse.** The hypothesis was that Python's text-mode
encoder splits one `write()` into several syscalls, so pre-encoded bytes in
binary mode would be atomic. That is a reasonable hypothesis and it is wrong;
binary mode lost *more* lines in the same run. `O_APPEND` on Windows does not
provide the atomicity POSIX programmers expect from it.

What makes it dangerous is that the *corruption* count improves slightly while
the *loss* count worsens. Anyone measuring only the visible symptom would
conclude the optimisation worked.

**Consequence:** every append takes an OS-level file lock (B86). The prohibition
on the alternative is written into the spec (B88), because someone will
reintroduce it in good faith otherwise.

---

## 2. The lock test proved the lock; the *neutering* proved the test

The cross-process lock test passed the first time it was run. That is exactly
when a test deserves suspicion, because a test that passes against a correct
implementation and a test that asserts nothing are indistinguishable from the
outside.

`_try_acquire` and `_release` were replaced with a true no-op and the test re-run:
**553 of 600 lines, 47 entries lost.** The test has teeth.

The part worth recording is the *first* attempt. Neutering with `if True:` made
the worker crash on release, so the test failed — but for the wrong reason. It
never exercised an unlocked append at all. Had the check stopped there, it would
have produced a false confirmation from a genuine failure.

**Consequence:** when a teeth-check fails, read *why* it failed. A red result is
not self-evidently the right red result.

---

## 3. `Path.with_suffix()` replaces the suffix; it does not append

```python
Path("events.jsonl").with_suffix(".lock")        # -> events.lock
Path("events.jsonl").with_suffix(".jsonl.lock")  # -> events.jsonl.lock
```

Both forms are used in this codebase, deliberately and in opposite directions:

- `storage.py` **appends**: `state.json` → `state.json.tmp`, so the temp file is
  visibly a sibling of the file it will become.
- `eventlog.py` **replaces**: `events.jsonl` → `events.lock`, because the lock is
  not a variant of the log, it is a different object.

Both match the spec's directory listing, which is how the mismatch was caught.

**Consequence, larger than the API detail:** the naming bug moved a file, which
made `test_reading_does_not_take_the_lock` start failing — and revealed it had
been locking a path `EventLog` never touched. It had been asserting nothing. **A
test can pass for years because it is aimed at the wrong object.** The only
reason it surfaced was an unrelated change moving the target.

---

## 4. A recovery instruction can point at a file that another rule deletes

This one occurred **twice**, at two different layers, and is the most transferable
finding in the phase.

At the design gate, writing out the recovery path concretely exposed a
contradiction between two behaviours that each read correctly alone: B83a told the
developer their unsaved state was safe in a `.tmp` file, and B81 swept `*.tmp`
files at startup. The next run would delete the file the developer had just been
told to go and rescue. Fixed by B83b (rename to `.unsaved`) and B83c (never
auto-delete).

During TDD, the identical bug reappeared in the *code*, one level down. When the
rename to `.unsaved` itself fails — the same held handle blocks both operations —
the implementation fell back to naming the `.tmp` file while still printing
"nothing was lost". Found by a test written to close a coverage gap, not by
review; the code read correctly.

**Consequence:** two rules that are each individually correct can contradict each
other, and the contradiction is invisible until someone traces the path end to
end. Fixing it in the spec does not fix it in the code. The general form: **an
error message that names a file is a claim about that file's future, and the rest
of the system has to agree to it.**

---

## 5. A diagnosis is not a recovery

`atom status` on a corrupt state file said what was wrong, precisely, with the
byte offset — and gave the developer nothing to do about it. A *failed write* on
the same data explained recovery in full, because P3-4 had settled that question
explicitly.

The asymmetry was invisible in the spec, where the two behaviours are in different
sections and both read well. It became obvious the moment the program was run by
hand.

**Consequence (agent decision A6):** the recovery-instructions rule was extended
from failed writes to corrupt reads. The developer decided the principle; this
applies it consistently. Corruption is the *likelier* of the two events — the
spike proved torn writes happen.

---

## 6. Every test passed while the output was unreadable

Running `atom status` on a broken project by hand produced this:

```
atom status: C:\...\state.json is not valid JSON: Expecting value: line 1 column 1.
It was probably damaged by a process that stopped mid-write.Project: C:\...
```

Two defects, neither caught by 273 passing tests. The problem was printed twice —
once to stderr and once inside the report — and the stderr copy had no trailing
newline, so it ran into the first line of the report.

The subprocess smoke tests were no help. They assert exit codes and the presence
of substrings, which is what they are for. Nothing asserts *legibility*.

**Consequence:** this is now the fourth consecutive phase in which running the
program found something the test suite could not.

| Phase | Tests green | What running it found |
|---|---:|---|
| 1 | 55 | `pyproject.toml` was invalid; the package would not install |
| 2 | 169 | `NameError` at startup, reachable only via `python -m` |
| 3 | 273 | Two messages printed on top of each other |

A green suite is evidence about the code. It is not evidence about the program.
Atom should make *run the finished thing by hand* an explicit step of the TDD
phase rather than a habit that happens to have held so far.

---

## 7. Coverage found three promises with nothing holding them up

Three behaviours from the approved spec had no test at all: `init`'s
write-failure path, a corrupt config reported separately from state, and damaged
event-log lines being counted. All three were implemented; none was pinned.

They were not found by reading the test list against the spec — they were found by
reading the coverage report's *Missing* column and asking what each uncovered
line was for. One of the three tests then immediately found finding #4 above.

**Consequence:** coverage gaps are worth reading line by line rather than as a
percentage. 94% reads like a finished job; the uncovered 6% contained a defect.

---

## 8. The agent's memory of a measurement reversed its sign

While writing this document, the table in finding #1 was first drafted from
working memory as *text mode lost 73, binary mode lost 24* — binary mode as a
two-thirds improvement. The measured result in
[`poc-report.md`](poc-report.md) is *text 55, binary 68*: binary mode is **worse**.

The numbers were plausible, the shape of the table was right, and the surrounding
prose was coherent. Only cross-checking against `decisions.md` — which cited "68
vs 55" and disagreed — exposed it. Had both documents been written in the same
pass from the same faulty memory, they would have agreed with each other and
disagreed only with reality.

This is the exact failure Atom exists to prevent, occurring inside Atom's own
tooling, against Atom's own data, one phase after it was measured. The POC was
run precisely because a prediction is not an observation; the finding then
decayed back into a prediction while being written up.

**Consequences:**

1. **Every number in a write-up must be traced to the artefact that produced it,
   not recalled.** Recall is what predictions are made of.
2. **Redundant records are worth their cost.** `decisions.md` and `findings.md`
   citing the same figure independently is not duplication — it is the only
   reason the error was caught.
3. Atom should treat *disagreement between two of its own documents* as a signal
   worth surfacing, not as a tidy-up task. Here it was the whole warning.

---

## Tracked debt

| ID | Item | Status |
|---|---|---|
| D1 | Cross-process lock unverified | **Closed.** Verified across real processes and teeth-checked by neutering (553/600 without the lock). |
| D2 | No POSIX baseline for the persistence measurements | Open. CI runs the spike on Linux and macOS; the numbers exist but have not been read into a report. The `filelock.py` POSIX branch is the one uncovered region in the phase. |
| D3 | Lock contention at volume unmeasured | Open. Six processes is not many. |
| D4 | State schema versioning undecided | Open. `state.json` has no version field; changing its shape will break existing projects with a corruption error rather than a migration. |
| D5 | Stale-lock recovery is manual | Open. A process killed while holding the lock leaves it held until the OS releases the handle; the timeout message explains this, but nothing clears it automatically. |
