# TDD Log — Phase 3: `atom state`

A record of how the code was built, kept because the order things happened in is
itself evidence.

Five cycles. The notable entries are not the cycles that went smoothly — they are
the two places where a passing test turned out to prove less than it claimed, and
the one place where a test caught a defect that reading the code had not.

---

## Cycle 1 — `filelock.py` (B84–B87)

**RED.** 8 tests against a module that did not exist.

**GREEN.** `FileLock`, `LockTimeout`. Platform primitives are bound at import
time; the non-blocking call sits in a poll loop so the caller's timeout is
honoured exactly rather than approximately.

**It passed first try, so the tests were checked for teeth.** The cross-process
test is the one that matters — it is the only evidence that D1 is closed — so
`_try_acquire` and `_release` were neutered into a true no-op and the test re-run
across real processes:

```
with the lock     600 / 600 lines
without the lock  553 / 600 lines   47 entries silently lost
```

The test has teeth. Worth recording that the *first* neutering attempt failed for
the wrong reason: an `if True:` short-circuit made the worker crash on release,
so the test failed without ever exercising the unlocked append. A teeth-check
that fails is not automatically a teeth-check that worked — the reason has to be
read.

This also extends the spike's finding. The spike measured threads; this measured
processes. Same result.

---

## Cycle 2 — `storage.py` (B77–B83)

**RED.** 23 tests.

**GREEN.** `read_json`, `write_json`, `sweep_temp_files` — first try.

**Notes.** `test_a_write_that_cannot_succeed_fails_loudly` is what stops the
retry tests passing trivially. It holds a real handle open so all ten replaces
are genuinely rejected; without it, a `write_json` that never retried would pass
the retry tests by succeeding on the first attempt.

---

## Cycle 3 — `eventlog.py` (B88–B92)

**RED.** 15 tests.

**GREEN after one failure.** `with_suffix(suffix + ".lock")` produced
`events.jsonl.lock`, but the approved spec's directory listing says `events.lock`.
The implementation was changed to match the reviewed contract rather than the
other way round.

**That failure exposed a test passing for the wrong reason.**
`test_reading_does_not_take_the_lock` had been locking `events.jsonl.lock` while
`EventLog` used a different path, so it was asserting nothing about the lock the
code actually takes. It only surfaced because the naming bug moved the file.

`Path.with_suffix()` **replaces** the suffix; it does not append. `storage.py`
uses the appending form deliberately (`state.json` → `state.json.tmp`),
`eventlog.py` the replacing form (`events.jsonl` → `events.lock`). Both match the
spec's listing, which is why the mismatch was a real error and not a preference.

---

## Cycle 4 — `state.py` (B71–B76, B94)

**RED.** 31 tests.

**GREEN.** `Phase`, `Status`, `ProjectState`, `Project`, `state_from_dict`,
`next_phase`, `InvalidTransition` — first try.

**Notes.** The transition rule encodes Atom's thesis directly: backwards is
always allowed, forwards is one step only. A developer who learns something in
TDD that invalidates the spec must be able to go back without fighting the tool;
a developer who wants to skip from POC to SHIP should not be able to, because
skipping is the failure mode the framework exists to prevent.

---

## Cycle 5 — `atom init` / `atom status` (B81–B83, B93, B95–B102)

**RED.** 20 tests, all failing on an unknown command.

**GREEN**, then three rounds of correction — all three prompted by evidence
rather than by review.

**Three documented behaviours had no test at all.** Coverage flagged them:
`init`'s write-failure path, a corrupt config reported separately from state, and
damaged event-log lines being counted. Each was a promise in the spec with
nothing holding it up. Tests were added for all three.

**One of those tests found a real defect.** When `write_json` exhausts its
retries it renames the temp file to `.unsaved` (B83b) precisely because the
startup sweep deletes `*.tmp` (B81) — this was a bug found in the spec at the
design gate and fixed there. But the last-resort branch, taken when the
`.unsaved` rename *itself* fails, fell back to naming the `.tmp` file while still
printing "nothing was lost". The next `atom status` would sweep it away. The same
trap, one level down, in the code rather than the spec. The message now tells the
truth on that path.

**Running the program by hand found two things the tests did not.** A subprocess
smoke test asserts exit codes, not legibility. Running `atom status` on a broken
project showed the problem printed twice — once to stderr, once inside the report
— with the stderr copy missing its trailing newline, so it collided with the
first line of the report: `...mid-write.Project: C:\...`. Every test passed.

That prompted agent decision **A7** (one report to stdout in text mode; stderr
reserved for `--json`, where stdout belongs to the payload) and required changing
two earlier tests that had asserted the stderr behaviour. The spec is silent on
streams, so this was a genuine choice, not a correction — it is recorded in
`decisions.md` for the gate rather than made quietly.

It also prompted **A6**: a corrupt state file was diagnosed but gave the
developer nothing to do about it, while a failed *write* explained recovery in
full. P3-4 settled the principle; corruption is the likelier event, since the
spike proved torn writes happen. Both paths now carry a route out.

---

## Result

| | |
|---|---|
| Tests | 275 (172 before this phase) |
| Coverage | 94% overall; `state.py` and `status.py` 100%, `storage.py` and `eventlog.py` 97–100% |
| Uncovered | `filelock.py` 84% — the POSIX branch, which cannot run on Windows. Tracked as D2. |

## What this phase says about the method

The spike found that unlocked appends lose data. TDD found that the fix's
last-resort path lied about it. Running the finished program found that the
output was unreadable. Three different activities, three different classes of
defect, none of which would have been caught by the other two.

The recurring lesson, now four phases deep: **a green suite is evidence about the
code, not about the program.** Phase 1 shipped 55 green tests on an unbuildable
package. Phase 2 shipped 169 green tests on a program that crashed at startup.
Phase 3 shipped 275 green tests on output that ran two messages together. Each
time the gap was found by running the thing, and each time the tests added
afterwards were cheap.
