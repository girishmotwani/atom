# TDD Log - Phase 4: `atom review`

A record of how the code was built, kept because the order things happened in is
itself evidence.

Six cycles. The notable fact is not that each cycle went green quickly. The
notable fact is that every cycle passed on the first attempt, and every cycle hid
real defects found only by deliberate probing afterwards. The suite was green at
475, 478, and 482 tests while `atom review` still could not produce a single
review.

---

## Cycle 1 - `diff.py` (B103-B106b)

**RED.** 33 tests against the diff-source and capture contract. Suite count: 275
before the phase, 308 after this cycle.

**GREEN.** `DiffSource`, `DiffRequest`, `CapturedDiff`, `select_source`,
`git_command_for`, and `capture_diff`. The source is explicit, the diff is taken
once, empty diffs are successful empty work, and the size is counted without a
limit.

**It passed first try, so the parser was pointed at hostile diff shapes.** That
found the first real defect: diff body lines that looked like headers were being
classified by prefix. A removed markdown `---` line looked like a file header, and
added content beginning with `+++` could invent a phantom file. The undercount was
small on Atom's own markdown-heavy commit, but the phantom file mattered because
B117 trusts the diff's file list when rejecting model findings for files outside
the review.

The fix was a hunk-aware state machine. Headers are headers before the first
`@@`; after that, hunk body is body even when the content begins with `---`,
`+++`, `diff --git`, or `@@`.

---

## Cycle 2 - `invoke.py` (B107-B112, B129-B134, B137)

**RED.** 40 tests against command construction, availability probing, repeated
runs, per-run outcomes, and bounded concurrency. Suite count: 308 before the
cycle, 348 after it.

**GREEN.** `review_command`, `probe_models`, `invoke_models`, `InvocationReport`,
`ModelRun`, and `RunOutcome`. Calls use the measured flags, probe before review,
run each model three times by default, keep every run's outcome, and treat one
failed run as a partial review.

**It passed first try, so the concurrency test was checked for teeth.** The first
concurrency assertion only proved `peak <= 2`. Removing parallelism entirely made
`peak == 1`, so the test still passed. The fixed test makes the first call wait
for a second call; a serial implementation now deadlocks until the barrier times
out. The assertion became both safety and liveness: never above the limit, and
actually overlapping.

Probing also found `--runs 0`. The code made zero model calls and reported a
complete review with `0/0 runs completed`. That is the same empty-report danger as
B130 reached through a different door, so nonsensical settings are now refused
rather than clamped.

A third probe separated the POC command from the POC environment. The spike's
speed-up used `--disable-builtin-mcps` plus two named enterprise MCP servers. Only
the built-in flag belongs in Atom. Named servers are optional caller input, not a
default baked into an open tool.

---

## Cycle 3 - `extract.py` (B113-B117)

**RED.** 37 collected tests against fence stripping, schema validation, file
validation, and failure reporting. Suite count: 348 before the cycle, 385 after
it.

**GREEN.** `strip_fence`, `extract_from_run`, `extract_all`, `Finding`,
`ExtractionFailure`, and `ExtractionReport`. Bare JSON stays bare, fenced JSON is
stripped, bracket-scan salvage is absent, invalid payloads are loud failures, and
good findings survive a sibling failure.

**It passed first try, so the extractor was run against the saved POC replies.**
That proved B113 is load-bearing. One model parsed 0/10 without fence stripping
and 10/10 with it. Without the stripper, the review silently becomes a one-model
review for that corpus.

Further probing found that the fence regex chose the first fence, not the right
one. A reply could show a Go code sample first and then put the findings in a
`json` fence; the original extractor parsed the Go sample and lost the answer.
The fix prefers a `json`-labelled fence when one exists. That is selection among
model-supplied delimiters, not the bracket guessing B114 refuses.

The same cycle also tightened the line validator. `line: true`, `line: 0`, and
negative lines are now rejected because impossible locations become
confidence-bearing groups in the merge step. A message containing triple backticks
inside a JSON fence still fails loudly; fixing it would require another unobserved
recovery path, so D12 is pinned instead.

---

## Cycle 4 - `merge.py` (B118-B124)

**RED.** 35 tests against proximity grouping, agreement, severity preservation,
ordering, known limits, and impossible fractions. Suite count: 385 before the
cycle, 420 after it.

**GREEN.** `merge_findings`, `MergedFinding`, agreement fractions, attributed
messages, highest-severity ordering, and the default proximity window of 3.
Groups are anchored rather than chained, so a group never grows wider than the
window by transitive adjacency.

**It passed first try, so the merge was run over the real spike responses.** The
end-to-end agreement result reproduced: 82 findings became 5 merged findings, 3
corroborated and 2 solo. The solo findings were noise. That was the result the
phase wanted.

The probe also found the phase's sharpest limitation: two distinct planted
defects merged when the proximity window plus ordinary line drift overlapped.
The ignored `os.Create` error drifted across lines 42-44, so a window of 3 reached
line 45, where the unlocked `Export` iteration lived. No window fixes both sides:
2 splits a genuine 33-36 cluster, while 3 merges 44-45. B120 is what makes the
trade tolerable: both messages remain visible even when the count is wrong.

Additional probes found impossible agreement fractions (`1/0`, `5/3`) and an
ordering dependency on `ALLOWED_SEVERITIES` being an ordered tuple, not a set. Both
are pinned because a wrong confidence number damages every number in the report.

---

## Cycle 5 - `review.py`, report renderers, and CLI wiring (B125-B131, B135-B137)

**RED.** 55 new tests across `test_review_output.py` and `test_cli_review.py`.
Suite count: 420 before the cycle, 475 after it.

**GREEN.** `ReviewOutcome`, markdown rendering, JSON rendering, problem rendering,
`atom review` parser wiring, exit-code mapping, stdout/stderr separation, and
subprocess smoke tests for the paths that do not need a model.

**It passed first try, so the finished command was treated as suspect rather than
finished.** The renderers exposed the facts a developer needs: what was reviewed,
which models answered, which runs failed, the per-model agreement fractions, every
attributed message, and severity disagreement. The CLI kept reports on stdout and
operational detail on stderr so `atom review > review.md` produces a clean file.

The probing step was simply running the command as a developer would. That is
where the next cycle began. The tests had proved the in-process pipeline. They had
not proved that the real Copilot CLI could be started, that the operating system
could carry the prompt, or that a completed process had produced a usable answer.

---

## Cycle 6 - making `atom review` actually run (runner, argv, stdin, usability, PATHEXT)

**RED.** 12 new tests across `test_invoke.py`, `test_review_output.py`,
`test_runner.py`, and the Phase 4 CLI paths. Suite count: 475 before the cycle,
487 after it.

**GREEN.** The prompt moved from argv to stdin; `SubprocessRunner` gained
`stdin_text`; children receive explicit empty stdin by default; a completed but
unparseable reply no longer counts as usable; failed process startup is diagnosed
by cause; command launch resolves the program the way a developer's shell does,
including PATHEXT-backed `.cmd` shims.

**It passed first try at each sub-step, and each green point hid the next defect.**
At 475 tests, `atom review` could not call a model and the diagnostic blamed PATH
even when PATH resolved a stale Windows App Execution Alias. It also crashed on a
missing working directory because Windows reports that as `NotADirectoryError`,
not `FileNotFoundError`.

At 478 tests, the diff no longer travelled in argv. That fixed the Windows
command-line ceiling, where prompts around 8,000 characters, 30,000 characters,
and 60,000 characters failed in different layers. The invariant pinned by the
test is stronger than any threshold: argv is byte-identical for a 100-character
prompt and a 500,000-character prompt. But moving the prompt to stdin exposed the
next bug: subprocesses inherited Atom's own stdin and the availability probe timed
out waiting for EOF from a pipe.

At 482 tests, stdin inheritance had been closed, but `atom review` still produced
a clean-looking report from no usable opinion. The process completed and returned
text, so `invocation.usable_runs` called it usable. Extraction later rejected the
reply as prose, and the report still said no findings with exit 0. Usability now
lives after extraction: `[]` is a real clean review, but prose that yields no
findings is not.

PATHEXT was the final launch-boundary fix. Windows `CreateProcess` does not search
for `.cmd` the way a shell does, while npm installs command shims as `.cmd` files.
Resolving the executable through `shutil.which` before launch makes Atom agree
with the command a developer can type. The same diagnosis path names a working
copy shadowed behind a dead PATH entry, because reinstalling cannot fix a binary
that is never reached.

---

## Result

| | |
|---|---|
| Tests | 487 (275 before this phase) |
| Phase 4 collected files | `test_diff.py` 33; `test_invoke.py` 40; `test_extract.py` 37; `test_merge.py` 35; `test_review_output.py` 34; `test_cli_review.py` 27; `test_runner.py` 11 |
| Coverage | 96% overall; `diff.py`, `invoke.py`, `extract.py`, `merge.py`, and `review.py` at 100% |
| Uncovered | `cli.py` 90%, `runner.py` 95%, `report.py` 97% |

## What this phase says about the method

Every cycle passed on the first attempt. Every cycle hid a real defect until a
probe asked a different kind of question: a real diff, a neutered concurrency
implementation, saved POC replies, real spike responses, a real process, then a
real model CLI at the operating-system boundary.

The recurring lesson is sharper than Phase 3's. A green suite is evidence that the
implementation matches the tests' mental model. It is not evidence that the tests
asked the right questions, that the program starts, or that the operating system
can carry the input. Phase 4 had green suites at 475, 478, and 482 tests while
`atom review` could not produce a single review. The probes were not extra polish;
they were the step that found the defects.

## Cycle 8 (late) — the denominator counted runs that said nothing

Run after Phase 4 shipped, prompted by a developer discussion of the open A5 decision
rather than by a failing test.

| Step | Result |
| --- | --- |
| Evidence gathered first | Run tables from two committed review artifacts: 0 incomplete runs, 2 unreadable replies |
| Tests written | 5 red (denominator, agreement fraction, partial, banner count, JSON) + 3 guards that passed immediately |
| Guards re-checked after the fix | All 3 still green — the only moment they mean anything |
| Suite | 756 -> 783 |
| Real CLI runs | 4, each one finding a defect the tests did not |

**Rounds with the review gate, all four of which found something true:**

1. Silence was based on `usable_runs`, which drops empty replies before extraction — so a
   blank reply was in neither the answered set nor the silent one. Claimed refuted by a
   measurement that bypassed `usable_runs`; the test, written against the real path,
   proved the model right. See Finding 20.
2. A reply overruled by the file guard was reported as unreadable and reddened CI.
   Escalated to the developer as a decision rather than resolved silently.
3. `reply_was_readable` was set for any rejected element, so schema-invalid replies counted
   as answered. Narrowed to the file guard alone (A19).
4. Answered and overruled overlapped, so the partial total subtracted one run twice and the
   report filed an answered run under a heading about replies that produced nothing (A20).

**Two findings were refuted by measurement and not acted on** — both claimed a valid empty
JSON array would be classified as silent. One command over seven reply shapes showed
`[]` classified as answered, denominator 1, not partial.

**Process deviation, recorded honestly.** The fourth round's fix was implemented before its
tests were written, so those five tests are regression pins rather than red-green. The
behaviours they assert did not exist beforehand and would have failed, but the order was
wrong and is noted rather than presented as TDD.

## Cycle 9 — corroboration (A21, A22)

**Round 1, A21.** Six tests written first. Red run gave exactly one failure — the new
behaviour — with five over-correction guards passing, as guards should. Implemented
same-line bucketing in `is_corroborated`. Suite 783 -> 789. Four shapes verified by hand.

**Round 2, the gate.** Two real `atom review --working` passes. The first returned no
findings with 4 of 6 runs readable; rather than accept a weak clean result, a second pass
was run. It reported that same-line-only corroboration hides genuine agreement when two
models anchor one defect at adjacent lines. Measured: correct, and the shape is the one the
original analysis observed most often.

**Round 3, A22.** Five tests written first for the disjoint companion signal. Implemented
`has_nearby_multi_model_reports`, plus report rendering and the JSON field. Suite 789 -> 794.
Four shapes verified disjoint by hand.

**Process note, recorded honestly.** A21 reached written-up artifacts before the gate ran.
The decision, finding, design-spec and test-spec entries for it were all committed to disk
describing a fix that was incomplete. They were corrected rather than rewritten, so the
record shows the error and its repair rather than a clean result that never happened.

**Round 4, A23.** Gate found the review JSON contract had broken silently. Two tests
written first; red run failed at import, as intended, because the constants did not exist.
Split `SCHEMA_VERSION` into five per-report constants and bumped only review to 2.
Suite 794 -> 796. The four unmoved reports are pinned at 1 by an over-correction guard, and
`atom status --json` was checked through the real CLI to confirm it still reports 1.

## Cycle 10 — the default model pair (A26)

**Red.** Two tests written first against a default that was still
`("gpt-5.4", "claude-haiku-4.5")`. Both failed, and the second failed for the
more interesting reason: `--help` had already been updated to name gemini while
the tuple still named haiku, so the pair and its documentation disagreed. That
is precisely the drift the test exists to catch, demonstrated before it was
written up.

**Green.** Default changed to `("gpt-5.4", "gemini-3.8-flash")`; both pass.

**Then three unrelated tests broke**, which was the useful part. They had encoded
the default pair implicitly -- `ScriptedRunner(failing_models=("claude-haiku-4.5",))`
only fails a run if haiku is one of the models actually consulted. Those tests were
not testing the model name; they were testing partial-failure handling, and the
literal was an accident of when they were written. Rewritten against
`DEFAULT_REVIEW_MODELS[1]` so they follow the default instead of pinning it. The
literals that remain elsewhere in the suite are genuine fixture labels -- arbitrary
names in merge and extract tests -- and were deliberately left alone.

**Suite: 801 -> 803.**

**Not a TDD cycle, recorded here for the trail:** the harness fixes under findings
31 and 32 were verified by direct observation rather than by unit tests, because
both concern a POC harness rather than shipped code. The reduce fix was checked by
re-scoring the banked reply that had been discarded (now 4/4 at the exact lines);
the timeout fix by a live call with a 5-second limit, which returned in 5.6s where
this shape previously produced 22,434s. The production guarantee behind the second
one is already covered by B2a-B2e in phase-01.