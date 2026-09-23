---
project: "atom-cli"
phase: "phase-03-state"
date: "2026-09-16"
status: "ran"
spike: "../../../poc/state-persistence-on-windows/spike.py"
---

# POC Report — Phase 3: state persistence on Windows

**Spike:** `poc/state-persistence-on-windows/spike.py`
**Run on:** Windows 11, Python 3.13.14
**Verdict:** **three of five predictions refuted.** "Ordinary JSON persistence"
was not ordinary.

---

## Summary

| # | Prediction | Outcome |
|---|---|---|
| P1 | `os.replace` fails when the destination is open by another process | **CONFIRMED** |
| P1b | ...also with a *writer* attached (follow-up) | **CONFIRMED** |
| P2 | Concurrent appends do **not** interleave | **REFUTED** |
| P2b | Binary-mode single-write appends fix it (follow-up) | **REFUTED** |
| P2c | An OS-level file lock fixes it (follow-up) | **CONFIRMED** |
| P3 | Every corruption shape raises `JSONDecodeError` | **REFUTED** |
| P4 | The original survives a mid-write kill | **CONFIRMED** |
| P5 | A partial temp file is left behind | **CONFIRMED** |

The phase plan said this phase had *"no technical uncertainty."* Three
refutations later, that claim was wrong — and one of them invalidates the
obvious fix as well as the obvious approach.

---

## Evidence

### P2 — concurrent appends corrupt the log, and lose entries

```
P2:  REFUTED -- expected 1600 clean lines, got 1545 lines with 3 corrupt
P2b: REFUTED -- binary mode ALSO corrupts: 1532 lines (68 lost), 4 corrupt
P2c: CONFIRMED -- an OS file lock produced a clean log: 1600 lines, 0 corrupt
```

Eight writers, 200 lines each, separate file handles. Reproduced across runs
with the loss count varying (55, 68, 73, 85) — it is a race, not a constant.

**Two things are worse than expected.** First, entries are not merely torn, they
are **silently lost** — 1600 written, 1545 present, only 3 unparseable. Most
losses leave no trace at all. A corrupt line is visible; a missing line is not.

Second, the obvious explanation was wrong. The hypothesis was that Python's
text-mode encoder splits one `write()` into several syscalls, so binary mode
with pre-encoded bytes would be atomic. **P2b refuted that too** — binary mode
lost *more* lines than text mode in the same run. `O_APPEND` on Windows does not
provide the atomicity POSIX programmers expect from it.

Had P2b not been run, the design would have adopted binary mode, seen the
corruption drop, and shipped a log that quietly loses entries under load.

### P1 — `os.replace` is not unconditionally safe on Windows

```
P1:  CONFIRMED -- replace failed while a reader was attached: PermissionError
P1b: CONFIRMED -- replace failed with a writer attached: PermissionError
```

The write-temp-then-replace recipe is normally quoted as if the rename cannot
fail. On Windows it fails with `PermissionError` whenever any other process
holds the destination open — including a reader. Concurrent `atom status`
during `atom phase advance` is exactly that situation.

### P3 — not every corruption raises `JSONDecodeError`

```
truncated              -> JSONDecodeError
empty                  -> JSONDecodeError
nul_bytes              -> JSONDecodeError
whitespace             -> JSONDecodeError
valid_json_wrong_type  -> NO EXCEPTION, parsed as list
```

Four of five shapes are caught by one `except`. The fifth is not: a file
containing `[1, 2, 3]` parses perfectly and returns a `list` where the code
expects a `dict`. The failure then surfaces much later as an `AttributeError`
or `KeyError` far from the real cause — precisely the "stack trace instead of a
clear error" the phase promised to avoid.

### P4 / P5 — a real process killed mid-write

```
P4: CONFIRMED -- original survived the kill intact: {'phase': 'design', 'step': 3}
P5: CONFIRMED -- a partial temp file was left behind (13041 bytes)
```

A child process was started, allowed to signal that it was genuinely mid-write,
and then killed — rather than simulating the crash, which would have assumed the
answer. The write-temp-then-replace strategy is sound in its core promise. It
just leaves rubbish behind.

---

## Binding consequences for the Phase 3 design

| # | Consequence |
|---|---|
| **C1** | **The JSONL event log must be written under an OS-level file lock.** `msvcrt.locking` on Windows, `fcntl.flock` elsewhere. This is not a precaution; unlocked appends silently lose entries. |
| **C2** | **The lock lives in its own file** (`events.lock`), not a byte range of the log. Locking a range of the file being appended to contends with the append. |
| **C3** | **Binary mode is not a substitute for a lock.** A future "optimisation" removing the lock because writes are small and pre-encoded will reintroduce silent loss. The spike pins P2b to prevent exactly that. |
| **C4** | **`os.replace` must be retried**, with a bounded number of attempts and a clear error on exhaustion. A single unguarded `os.replace` will raise `PermissionError` in normal use. |
| **C5** | **Readers must not hold handles open.** Read the whole file and close immediately — never keep a handle across a phase transition. This is what makes C4's retries likely to succeed rather than merely present. |
| **C6** | **Loading state requires schema validation, not just `try/except json.JSONDecodeError`.** Check the parsed object is a `dict` and carries the expected keys. `[1,2,3]` is valid JSON and invalid state. |
| **C7** | **Stale `.tmp` files accumulate after a crash and must be cleaned up** on the next `atom` invocation. They are not harmless — one 13 KB fragment per crash, and they look like real state to anyone reading the directory. |
| **C8** | **Corruption must be distinguishable from absence.** A missing state file means "not initialised"; a corrupt one means "something went wrong". They need different messages and different exit codes. |
| **C9** | **The event log must tolerate a truncated final line.** A crash mid-append leaves one. Readers should skip it with a warning rather than refusing to read the log at all. |

---

## What this did not settle

- **Cross-process locking was not directly tested.** The spike uses threads with
  separate file handles. That is strictly *weaker* than separate processes for
  the corruption finding (if threads interleave, processes certainly will), but
  the *fix* in P2c was verified only between threads. `msvcrt.locking` and
  `flock` are OS-level primitives and should behave identically across
  processes — but "should" is what this spike exists to replace. **Phase 3 must
  verify the lock across real processes before relying on it.**
- **Lock contention cost was not measured.** Eight writers serialised through
  one lock completed quickly at this volume. Behaviour under a chattier log is
  unknown.
- **No POSIX run yet.** CI runs this spike on Linux and macOS as well; the
  results there are expected to differ, and the CI output is the record.
- **Lock starvation and stale locks.** A process killed while holding the lock
  was not tested. That is a real failure mode and Phase 3's design must address
  it.
- **Network drives and UNC paths.** Out of scope; Atom assumes a local tree.

---

## Why this spike was worth running

The phase plan's exact words were *"POC question — justifiably skipped. No
technical uncertainty."*

Three predictions were refuted, and the most important one — P2b — refuted the
*fix* rather than the original assumption. A design review would not have caught
any of them: the code that loses log entries is four lines long, looks correct,
and matches what most Python programmers believe about `O_APPEND`.

The finding that justifies the whole exercise is that **the corruption is mostly
invisible**. 1600 lines in, 1545 out, 3 of them visibly broken. A test asserting
"the log contains valid JSON" would pass.
