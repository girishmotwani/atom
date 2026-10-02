# Decisions — Phase 4: `atom review`

Two kinds of decision are recorded here, kept apart on purpose:

- **P4-n — developer decisions.** Made by the human at a gate.
- **A-n — agent decisions.** Made by the agent because the spec did not say.
  Every one of these is a place the agent chose on the developer's behalf, and
  each is listed so it can be overturned.

---

## Developer Decisions

### P4-1 — The POC's decision rule was amended after seeing the data

**Context.** [`poc-brief.md`](poc-brief.md) fixed a rule *before* running: if strict
compliance fell below 80%, abandon structured JSON. The worst cell came in at **0%**.
Applied literally, the phase ends here.

The agent did not apply it and did not quietly ignore it. It put the conflict to the
developer, naming the risk out loud: amending a pre-registered rule after seeing the
result is the textbook shape of rationalisation, and the framework exists to refuse
exactly that move.

**Decision.** Amend the rule, on the record.

**Why the amendment is legitimate.** The rule's *premise* was refuted, not just its
threshold. It assumed unreliability would be an unpredictable rate — a model that
complies sometimes. What was measured is deterministic per model: `gpt-5.4` complied
20/20, `claude-haiku-4.5` fenced 20/20. Stripping a fence that is always present is
**extraction**, not repair. A rule written about flakiness does not bind a result that
contains no flakiness.

**What keeps this honest.** [`poc-report.md`](poc-report.md) records the conditions
under which this reasoning *would* have been rationalisation: intermittent fencing,
prose outside the fence, any use of the bracket-scan fallback, or any schema violation.
None occurred. If a future run shows any of them, the amendment is void and the
original rule applies.

### P4-2 — Each model is called three times, not once (Q1)

**Decision.** Default **3 runs per model**, overridable with `--runs`.

**What forced the question.** The phase plan's "run a diff past two or more models and
merge" silently assumed one call each. The agreement analysis refuted the assumption:
`claude-haiku-4.5`'s best finding appeared in **13 of 20 runs (65%)**. A single call to
that model omits real defects about a third of the time, and nothing in the output says
so.

**What repetition buys.** Repetition frequency becomes a confidence signal. On the
measured data it is what separates the four real defects — reported by both models —
from the eight noise findings, none of which appeared in more than 5 runs of 20.

**Accepted cost.** Six model calls per review instead of two. Wall-clock stays close to
one call if they run in parallel (see A4); the spend is 3×.

**Behaviours.** B132, B133, B134.

### P4-3 — Exit 0 unless the tool failed, and a partial review counts as failed (Q2)

**Decision.** `atom review` exits **0** whenever the review completed, however many
findings it produced. It exits **non-zero** when the tool failed.

**What "failed" includes.** The clear ends were settled directly: findings present → 0;
no model returned a usable response → non-zero. The seam was the middle — a *partial*
review, where one model answered and the other did not. That was put to the developer
separately and answered: **partial is non-zero**.

> A model failing is a tool failure even though a report came out. Otherwise a CI job
> where one model fails on every single run stays green forever and nobody reads the
> banner.

**Rejected.** Exiting non-zero on findings at or above a severity threshold. Severity is
measurably unstable — the same model gave the same line two different severities across
runs (B123) — and gating a build on an unstable signal makes it flaky for reasons the
developer cannot see.

**Behaviours.** B135, and it refines B131.

### P4-4 — The whole diff goes in one call (Q3)

**Decision.** One call per run carries the entire diff. No per-file chunking.

**Rationale — and it is a methodology argument, not a technical one.** Cross-file
context is where some of the most valuable findings live: a caller that no longer
matches its callee cannot be seen one file at a time. The reason it is safe to keep the
whole diff in one call is that **Atom breaks work into phases before any code is
written**, so a diff that reaches `atom review` should already be small.

**The assumption this rests on.** That phase decomposition actually holds diff size
down. It is an assumption about how the framework is used, not something the tool
enforces, so A5 makes diff size visible in the report instead of letting a large diff
quietly degrade the review.

**Still unmeasured.** D8 stays open. The spike used a 48-line single-file diff, so
nobody has observed what a 2,000-line diff does to any of this.

### P4-5 — The proximity window defaults to 3 lines (Q4)

**Decision.** Default 3, overridable.

**Why it needs a window at all.** Exact `(file, line)` matching reports one defect as
several. `gpt-5.4` reported the same underlying problem at line 36 on some runs and line
37 on others; `claude-haiku-4.5` put it at 34 and 35.

**Honest provenance.** 3 is derived from the near misses observed in **one fixture
diff**. It is not a tuned value and the spec says so. Both failure modes are silent — too
wide merges two real defects into one, too narrow reports one defect repeatedly — and
neither is visible in the output.

---

### P4-6 — The Go toolchain runs before any model, and blocks the review when it fails

**Decision.** `atom review` now runs `go build`, `go vet`, `gofmt -l`, `go test` and
`go test -race` before calling a single model, and refuses to call any model if a
required gate fails. `staticcheck`, `errcheck` and `govulncheck` run as advisory
signals when installed and never block. `--skip-toolchain` opts out.

**Why.** Reviewers were spending attention on questions with exact free answers.
Every model call that reports a vet diagnostic or an ignored error is a call that did
not look at whether the code is readable — which is the category Atom exists to
protect and the one reviewers are already least willing to report. Measured: seeded
defects phrased as style preferences were reported by nobody across repeated runs,
while defects with a visible consequence were reported by everybody.

**The developer chose `-race` on every review**, accepting minutes of wall clock per
review. The alternative — racing only on demand — makes the one gate nobody remembers
to run the one gate nobody runs.

**What the gate deliberately does not do.** It excludes a category only when the tool
that proves it actually ran and passed. A missing `errcheck` leaves ignored errors in
scope; a package with no tests leaves races in scope. Excluding a category nobody
checked would be a silent downgrade of the review, which is worse than the waste it
was meant to remove.

**Known cost, unresolved: the measured prompt has changed.** `REVIEW_PROMPT` is
reproduced verbatim from `poc/review-json/spike.py`, and the JSON format-compliance
figures in this phase were measured against that exact wording. The evidence block is
inserted between the opening line and the JSON schema, leaving the schema and the
"nothing else" instruction byte-identical and still adjacent to the diff, and a test
asserts the template collapses back to the original when nothing is inserted. That
bounds the risk; it does not measure it. **Compliance has not been re-measured with a
populated evidence block, and a longer prompt is exactly the kind of change that moves
format compliance.** Recorded as an open cost rather than waved through.

**Also unmeasured: whether the exclusion improves anything.** The reasoning is sound
and the mechanism is verified end to end, but no experiment yet shows that freeing this
attention produces more readability findings. That is the next thing to measure, and
until it is measured this is a justified change, not a proven one.

---

## Agent Decisions

### A1 — The bracket-scan fallback is deliberately not shipped

**Decision.** B114. Extraction strips a markdown fence and nothing else. There is no
"find the outermost `[` and `]`" fallback.

**Why.** The spike measured that path at **zero executions in 40 calls** — 20/20 of
Haiku's responses were fence-only with no prose outside the fence. Shipping it would
mean shipping behaviour nobody has ever observed running, and its failure mode is
silent: it captures the wrong span and produces findings that look fine.

**Risk if wrong.** A model that wraps JSON in prose gets a loud parse failure instead of
a salvaged answer. That is the intended trade: loud beats silently-wrong.

**Overturnable by.** Anyone who observes a model that emits prose around the payload —
at which point the fallback should be written *against that observation*, not against
imagination.

### A2 — B117 rejects findings naming a file outside the diff, with no evidence behind it

**Decision.** A finding whose `file` is not in the reviewed diff is rejected.

**Why this is flagged rather than just stated.** It never happened in 40 calls. By A1's
own logic — do not ship guards for unobserved behaviour — B117 should not exist. The
agent kept it anyway because unlike the bracket scan, its failure mode is *loud and
bounded*: the worst case is rejecting a finding that was somehow legitimate, which shows
up in the report rather than silently corrupting it.

**This is the weakest behaviour in the spec** and is named as such so the developer can
strike it.

### A3 — Ordering uses the highest severity any model assigned

**Decision.** B124. Where models disagree on severity, ordering uses the most severe
claim; the disagreement itself is still shown (B123).

**Why.** Ordering is presentation, and burying the most alarming claim is the worse
error. It does not overwrite B123 — nothing collapses to a single verdict.

### A4 — Parallelism stays at the measured limit of 4

**Decision.** Concurrency defaults to **4**, not 6, even though P4-2 makes six calls per
review and 6 would finish in one wave.

**Why.** Four concurrent calls are what the spike actually measured — no rate limiting,
no interference. Six is unmeasured. Raising the default to make the arithmetic tidy
would be choosing a number for aesthetics over evidence, in a phase whose entire premise
is the opposite.

**Cost.** Six calls run as two waves, roughly 60 seconds instead of 30.

### A5 — A partial *run* makes the whole review partial

**Decision.** If any individual run fails or times out, the review is partial and exits
non-zero under P4-3 — not only when an entire model fails.

**Why.** P4-2 makes run count the denominator of the confidence signal. "Reported in 2
of 3 runs" means something different if the third run never happened, and the report
would otherwise present a degraded denominator as though it were intact. The developer's
reasoning on P4-3 was about *not noticing*; a missing run is precisely a thing not
noticed.

**Cost, and why this may be wrong.** With six calls per review, one flaky timeout turns
a CI run red. That may prove too strict in practice. The alternative — tolerate a
missing run and report the true denominator — is defensible and this should be revisited
once the failure rate has been observed rather than guessed at.

**Overturnable by.** The developer at the Phase 4 gate, or by the first week of real
timeout data.

### A6 — Diff size is reported rather than capped

**Decision.** The report states the size of the reviewed diff. No size limit is enforced
and no truncation is performed.

**Why.** P4-4's safety argument rests on phases keeping diffs small, which the tool does
not enforce. Inventing a threshold would mean picking a number nobody has measured (D8).
Reporting the size lets a developer looking at a thin review of a 2,000-line diff see a
plausible reason, without the tool pretending to know where the cliff is.

---

### A7 — No vendor-specific MCP server names ship in the code

**Decision.** `review_command` always passes `--disable-builtin-mcps` (B109), but the
*named* servers the spike also disabled are **not** hard-coded. They become an optional
`disable_mcp_servers` argument that defaults to empty.

**Why.** The 84s → 30s measurement behind B109 was taken inside one company's
environment, where two third-party servers happened to be ambient. B109's wording ("and
disables ambient MCP servers") reads as though the names are part of the behaviour. They
are not: they are a property of the machine the spike ran on. Hard-coding them would put
one organisation's internal tooling names inside an open-source tool, which is the exact
class of contamination this project was asked to avoid.

**What is lost.** A developer who *does* have ambient MCP servers gets the slower path
until they name them. That is the right default: the fast path should not be bought with
somebody else's server names baked into the binary.

**Overturnable.** If measurement shows `--disable-builtin-mcps` alone does not recover
most of the speed-up, the gap should be closed with a documented flag, not with a
built-in list.

---

### A8 — Nonsensical invocation settings are refused, not clamped

**Decision.** `runs < 1`, `concurrency < 1` and an empty model list raise `ValueError`
rather than being silently corrected to a working value.

**Why.** `--runs 0` was measured doing something worse than failing: it made zero calls,
reported `is_partial = False`, and printed `0/3 → 0/0 runs completed`. That output is
indistinguishable from a clean review in which every model was consulted and found
nothing. It is precisely the confusion B130 exists to prevent, reached through a door
B130 does not cover. Clamping to 1 would have hidden the developer's mistake; refusing
shows it.

**Overturnable.** If `--runs 0` turns out to be a useful "just show me the diff" mode, it
should be a separate flag with its own output, not a review that reports nothing.

---

## Tracked Debt

| # | Item | Status |
|---|------|--------|
| D6 | Review quality unmeasured — agreement predicted the real defects on one fixture where the evaluator planted them | Pending — the Phase 4 **gate** addresses this by running `atom review` over the Phase 1 diff and triaging the findings |
| D7 | Deduplication strategy | **Partially closed.** `analyse_agreement.py` measured cross-model and within-model agreement on the spike data; the merge model (B118–B124) is derived from it. Still one fixture. |
| D8 | Large diffs untested (Q3, P4-4) | Pending — A6 makes size visible; the cliff remains unmeasured |
| D9 | Fence behaviour observed under one prompt only | Pending |
| D10 | Non-Windows behaviour unmeasured | Pending — consistent with D2 from Phase 3 |
| D12 | A finding whose message contains a triple backtick truncates the fence and fails the run | Pending — pinned by a test; fixing needs a greedy retry, an unobserved path |
| D11 | Cost per review unmeasured, and P4-2 tripled it | Pending — no token or credit figure exists for a single review, let alone six calls |

---

## Gate Record

| Gate | Date | Outcome |
|------|------|---------|
| POC | this session | Run. 2 of 6 predictions refuted. Compliance is bimodal, not a rate; no truncations occurred. Decision rule amended on the record (P4-1). |
| Design spec | this session | **Approved.** Four open questions resolved (P4-2 … P4-5) plus one follow-up on partial-review exit codes. |
| TDD | — | Not started |
| Phase gate | — | Does not close until `atom review` has been run over the Phase 1 diff and its findings triaged — inherited bootstrap debt agreed at the Phase 1 gate. Six agent decisions (A1–A6) await developer review, A2 and A5 most in need of it. |

---

### A9 — A `line` below 1 is rejected

**Decision.** Extraction rejects `line <= 0`, and rejects booleans before the integer
check.

**Why.** B116 asks only for "an integer `line`". A negative or zero line is an integer
and has nowhere to point. Left in, it reaches the merge step, where proximity grouping
(P4-5, window 3) clusters impossible line numbers together and presents them as one
corroborated location. An impossible value does not stay impossible — it acquires
apparent confidence.

**Overturnable.** If some model uses `0` to mean "the whole file", the right answer is to
represent file-level findings explicitly, not to accept a sentinel the prompt never
offered.

---

### A10 — A `json`-labelled fence wins over an earlier unlabelled one

**Decision.** When a reply contains several fences, extraction prefers the one labelled
`json`.

**Why.** Measured: a reply that illustrates a problem with a ```go sample and *then*
supplies findings in a ```json fence loses everything, because the regex takes the first
fence regardless of label.

**Why this is not the heuristic B114 refuses.** The bracket scan invents a boundary by
guessing where data begins. Choosing among fences the model itself delimited and labelled
invents nothing — the delimiters are given. Selecting between candidates and fabricating
one are different acts, and only the second has a silent failure mode.

**Not extended further.** A finding whose message contains a triple backtick still
truncates and fails loudly. Fixing that would need a greedy retry — a third recovery path
nobody has observed firing. Tracked as D12 instead.


### A11 — groups are anchored, not chained

**Decision.** Within a file, findings are sorted by line; the lowest line anchors a group
and only findings within `window` of that **anchor** join it. A group is therefore never
wider than the window the developer asked for.

**Why.** Proximity is not transitive. With a window of 3, lines 10 and 12 are near, 12 and
14 are near, but 10 and 14 are not. Single-linkage chaining — the obvious implementation —
would place all three in one group, and on findings at consecutive lines the chain grows
without bound: one group could span an entire file while every adjacent pair looked
correct. That is precisely the "merges two genuinely different defects" failure B119 warns
about, arriving without anyone having chosen it.

**Cost, stated plainly.** Anchoring makes the partition depend on where the lowest finding
sits. Lines 10/12/14 group as {10,12},{14} rather than {10},{12,14}; both are defensible
and the tool picks one. It is deterministic and bounded, which chaining is not.

### A12 — an impossible agreement fraction is refused, not rendered

**Decision.** A model recorded with fewer than one completed run, or reporting a finding on
more runs than it completed, raises `ValueError`. An unrecognised severity does too, naming
the allowed set instead of leaking a bare `KeyError`.

**Why.** Extends A8 to the one number B121 and B122 ask the developer to trust. `1/0` and
`5/3` were both accepted before this (finding 10). A fraction that cannot exist does not
misreport one finding — it discredits every number in the report, and the reader has no way
to tell which others are affected.

**Why not clamp.** Clamping `5/3` to `3/3` would convert a caller bug into maximum
confidence: the single worst direction to be wrong in.

### A13 — the default window stays at 3 despite a measured over-merge

**Decision.** `DEFAULT_PROXIMITY_WINDOW` remains 3, as decided in P4-5, even though it
demonstrably merges two distinct planted defects on the only real data available.

**Why.** No window fixes it (finding 9): 3 merges defects at lines 44/45, and 2 splits the
genuine 33–36 cluster. The choice is between two errors, and the current one is the safer
of the two because B120 keeps both defects' messages visible — the developer still reads
about both problems. Splitting a real defect in two, by contrast, manufactures corroboration
that was never observed.

**Flagged for the gate.** P4-5 is the developer's decision and this evidence postdates it,
so it is raised rather than absorbed. The specific thing to decide: whether a merged finding
spanning several lines should say so prominently, given that its headline count can
understate the number of real defects.

### A14 — the report names what is missing, stderr explains why

**Decision.** When a model cannot be called, or a response cannot be parsed, the markdown
report states *that* the opinion is missing and stderr states *why*. Neither repeats the other.

**Why.** B127 requires the report to admit when a model's opinion is absent, so a reader
cannot mistake a partial review for a clean one. B128 requires operational problems to go to
stderr and forbids duplicating them. Written naively the two collide: the reason a model is
missing is both a fact about the review and an operational problem.

Splitting by *question answered* resolves it. The report answers "is this review complete?"
— a permanent fact belonging in the artefact. stderr answers "what went wrong on this run?"
— a transient diagnostic belonging in the terminal. The same split applies to unavailable
models and to unparseable responses.

### A15 — `SubprocessRunner` diagnoses the cause rather than reporting the exception

**Decision.** A failure to start a process is explained by cause — absent tool, unlaunchable
PATH entry, or missing working directory — instead of mapping one exception to one message.

**Why.** Findings 13 and 14. The operating system uses two exception classes for three causes
and gives the same `WinError 2` to both "absent" and "present but dead". Reporting the
exception reports the operating system's vocabulary, not the developer's problem. The cost is
one `shutil.which` call on a path that has already failed, where latency is irrelevant.

**What is deliberately not done.** Atom does not try to repair a broken alias, guess an
alternative install location, or fall back to `shell=True` — all three were tested and none
launch a stale alias. A tool that cannot start is reported, not worked around.

### A16 — the prompt travels on stdin, and the invariant pinned is argv size

**Decision.** `review_command` does not carry the prompt. `SubprocessRunner` grew a
`stdin_text` parameter, and the test asserts argv is byte-identical for a 100-character
prompt and a 500,000-character one.

**Why the invariant rather than a limit.** Finding 15 measured three different thresholds on
one machine (~8,000, ~30,000, ~60,000), each from a different layer. A test pinning any one
of them would pass on a machine with different limits while the defect remained. "Argv does
not grow with the diff" is the property that actually has to hold.

**What is given up.** `-p` is the documented scripting entry point; piped stdin is documented
but less travelled. Accepted, because B106 requires the whole diff in one call and argv
cannot carry it.

### A17 — children get an explicitly empty stdin

**Decision.** Every subprocess receives empty stdin unless the caller supplies text.

**Why.** Finding 16. Inheriting stdin makes correctness depend on how Atom itself was
launched — the same command succeeds from a terminal and times out from a pipe or CI job.

**The trade-off, named.** A POC that reads stdin now sees end-of-input immediately rather
than the developer's keyboard. That is the better failure: EOF is a value a program can
handle, while a never-closing inherited pipe is an unbreakable hang.

### A18 — usability is decided after extraction, not after the process exits

**Decision.** `has_no_usable_response` consults extraction results. A run is discounted only
when extraction failed *and* recovered nothing from it.

**Why.** Finding 17. A process exiting zero with prose in stdout proves the CLI worked, not
that a review happened. B130 forbids an infrastructure failure from printing as a clean bill
of health, and the process boundary is one layer too early to tell the difference.

**Why not simply require findings.** A model that answers `[]` has reviewed the diff and
found nothing. Treating an empty finding list as failure would make a clean review
unreportable — the exact inversion B130 warns about.

---

## A5 (revised) — a run that did not *answer* makes the review partial

**Supersedes the original A5**, which made a run that did not *complete* make the review
partial. The original invited revision "by the first week of real timeout data". That data
now exists, and it overturned the classification rather than the strictness.

**Measured across three real reviews (Phase 6, Phase 1, and this change), 18 model calls:**

| Event | Times observed |
| --- | --- |
| Run failed to complete (timeout, crash) | **0** |
| Run completed, reply could not be read | **4** (all `gpt-5.4`) |

The feared cost of A5 — a flaky timeout reddening CI — never happened once. The failure
that *did* happen was invisible to A5, because the process exited zero.

**The defect this exposed.** `runs_per_model` returned the completed-run count, so an
unreadable reply stayed in the denominator of every agreement fraction. A finding reported
by both readable `gpt-5.4` replies out of three runs printed **"2 of 3"** — inventing a
dissenting run from a reply nobody could parse. The confidence signal is the entire premise
of Phase 4, and it was reporting a number that was not true.

**Decision.** Three disjoint categories, decided by what a run *contributed*:

| Category | Denominator | Partial? |
| --- | --- | --- |
| **Answered** — contributed at least one in-scope finding, or a valid empty list | counted | no |
| **Overruled** — reply read, but every finding refused by the B117 file guard | left | no |
| **Silent** — no readable reply at all: empty, unparseable, or never completed | left | **yes** |

**Why overruled is not partial.** Partial means "no answer arrived", not "the answer was
refused". A working guard must not redden CI. It still leaves the denominator, because it
offered no opinion about *this* diff — shrinking a fraction and failing a build are
different penalties for different faults.

**Why the categories must be disjoint.** A reply holding one in-scope finding and one
out-of-scope one produced both a finding and a file-guard failure, landing in two sets at
once. That made the partial total subtract it twice and filed an answered run under a
heading about replies that produced nothing. Found by the review gate, on this change.

**Decided by the developer at the Phase 4 gate**, on the measurements above.

## A19 — `reply_was_readable` is set only when the file guard alone objected

**Decision.** An extraction failure is marked readable only if *every* rejected element was
refused by B117. One malformed element anywhere drops the reply back to silence.

**Why.** The first implementation set the flag for any rejected element, so a reply whose
findings were all schema-invalid — missing fields, impossible line numbers — counted as
"answered but overruled" and kept the review green. A reply Atom could not understand is
silence no matter how much well-formed JSON surrounded it.

**Found by the review gate** reviewing this very change, and confirmed by measurement
before being accepted.

## A20 — the report sections are keyed to the run, not to the failure

**Decision.** "Responses that could not be read" and "Replies that named files outside this
diff" list runs, chosen by which category the run fell into — never by inspecting an
individual failure record.

**Why.** A run can answer and still produce a failure record. Keying the headings to the
failure reported an answered run as a missing one. The banner's count is derived the same
way, from the disjoint totals.

**Also fixed here.** The partial banner promised "Details were written to stderr" for runs
that produce no stderr detail at all — an empty reply is dropped before extraction and
generates no failure record. The banner now says every counted run is named above, and a
section exists to name the ones that returned nothing.

---

## Resolved at the Phase 4 gate discussion

### A2 (resolved) — B117 stays

**Decision.** Keep the file guard. B117 rejects a finding naming a file outside the
reviewed diff.

**The evidence that settled it.** The guard has now never fired in **58 real calls** —
both committed reviews (`phase-01-check/review.md`, `phase-06-state/review.md`) record
only unreadable replies, never an out-of-diff finding. A1's rule would strike it.

**Why it stays anyway.** 58 calls is too small a sample to remove a guard whose failure
mode is loud, bounded and visible in the report. The developer weighed the cost of
keeping an unfired guard against the cost of a corrupted finding reaching a reader, and
kept it.

**Named honestly:** the `overruled` run category added under A5 exists entirely for a
guard that has never fired on real data. That is a deliberate, recorded bet, not an
oversight.

**Also named:** B117 does **not** catch the one false-positive class actually measured
(Finding 21 — a model calling an in-diff symbol undefined because its definition was not
in the diff). Those findings name files inside the diff. B117 was never going to help
with the problem we actually have.

---

### A6 (resolved) — unchanged

**Decision.** Diff size stays reported, not capped.

**Why.** No new data in 18 further calls. Inventing a threshold still means picking a
number nobody has measured. Reporting it still lets a developer reading a thin review of
a huge diff see a plausible reason. Nothing observed argues for moving.

---

### A13 (resolved) — window stays 3; the flagged question was already answered

**Decision.** `DEFAULT_PROXIMITY_WINDOW` remains 3. The flagged question — whether a
merged finding spanning several lines should say so prominently — is **closed as already
satisfied**, not by new code.

**Verified by rendering the exact measured case** (two planted defects at 44 and 45):

    #### g.py:44-45 - high
    Reported at lines 44, 45; nearby lines are grouped, so this entry may cover
    more than one problem.

The headline carries the span (`_line_span`, A13) and the body states the grouping caveat.
Both defects' messages stay visible per B120.

**But the same render exposed a defect in A13's own reasoning — see A21.**

---

### A17 (resolved) — settled

**Decision.** Children keep an explicitly empty stdin. Closed as settled.

**Why.** 18 further subprocess calls across three real reviews, zero hangs, zero timeouts.
The trade-off named in the original decision — a POC reading stdin sees EOF rather than a
keyboard — remains the better failure and has cost nothing observed.

---

### A21 — corroboration means the same line, not the same group

**Decision.** `MergedFinding.is_corroborated` is true only when two distinct models
reported the **same line**. Distinct models scattered across a merged group no longer
count.

**Why.** A13 justifies the window of 3 by arguing that the opposite error, splitting a
real defect, "manufactures corroboration that was never observed". Rendering the measured
case showed the over-merge manufactures it too, in the channel that matters most:

| input | old result |
| --- | --- |
| `gpt-5.4` "nil map write" @44, `claude-haiku-4.5` "unchecked error" @45 | `is_corroborated: True`, model_count 2 |

Two models, two demonstrably different problems, one line apart, reported as cross-model
agreement. B122 calls corroboration the one signal that separated the four real defects
from the eight noise findings. A signal that fires on disagreement is not a signal.

**Same defect class as A5:** the tool reported a number that was not true.

**Scope, named honestly.** This has never fired on real data — but only because
`claude-haiku-4.5` has never once agreed with `gpt-5.4` on anything (Finding 21). It is
latent, not absent, and it sits in the one number Phase 4 exists to produce.

**What deliberately did not change.** `model_count` and the per-model agreement fractions
still report every model that contributed to the entry. Narrowing corroboration must not
hide who spoke — guarded by
`test_model_count_still_reports_every_model_in_the_group`.

---

### A22 — nearby multi-model reports are their own signal

**Decision.** `is_corroborated` stays same-line only (A21). A second, weaker and
deliberately **disjoint** signal, `has_nearby_multi_model_reports`, reports the case A21
would otherwise have hidden: several models landed in one group but never on the same line.

**Why A21 alone was wrong.** The review gate caught it, and measurement confirmed it:

    SAME defect, adjacent lines, two models
      lines: (44, 45)   model_count: 2   is_corroborated: False

That is the shape `test_merge.py`'s own docstring names as what the original analysis
observed most often — "the same defect reported at adjacent lines". Proximity merging
(B118) exists precisely for it. A21 shipped alone would have understated genuine
cross-model agreement on the commonest real case in order to fix a latent one.

**The underlying problem, named.** These two shapes are indistinguishable in the data:

| | lines | models | truth |
| --- | --- | --- | --- |
| same defect, adjacent lines | (44, 45) | 2 | genuine agreement |
| different defects, adjacent lines | (44, 45) | 2 | no agreement |

Line numbers cannot separate them, so **one boolean must be wrong in one direction**. A21
did not fix the error; it swapped which error was made. Message-similarity matching was
rejected as fuzzy and unmeasured.

**Resolution.** Stop forcing one boolean to answer a question the data cannot answer.
Report both measured facts and let the reader judge, with every contributing message still
visible (B120):

    Several models reported problems in this group, but on different lines,
    so this is not recorded as agreement.

**Disjointness is load-bearing**, for the same reason it was under A20: an entry counted in
both would render under two contradictory headings. `has_nearby_multi_model_reports`
returns false whenever `is_corroborated` is true.

**Verified over four shapes**, all disjoint: same defect adjacent (nearby), different
defects adjacent (nearby), same line (corroborated), one model two lines (neither).

---

### A23 — each report carries its own schema version

**Decision.** The single shared `SCHEMA_VERSION` is replaced by one constant per report
kind: `CHECK_SCHEMA_VERSION`, `SPIKE_SCHEMA_VERSION`, `SPIKE_LIST_SCHEMA_VERSION`,
`STATUS_SCHEMA_VERSION` (all 1) and `REVIEW_SCHEMA_VERSION` (**2**).

**Why.** The review gate found that A21 changed what `is_corroborated` answers for the same
input — a breaking change to the review JSON contract — while `schema_version` stayed at 1.
The design-spec entry written minutes earlier said "the addition is additive, so
`SCHEMA_VERSION` is unchanged", which was true of the *new* field and false of the
*narrowed* one. Both were in the same commit.

**Why not simply bump the shared constant to 2.** One number served five independent
contracts, so it could not be true for all of them: bumping it signals a change to four
reports that did not move, and not bumping it hides a real change from review consumers.
**This is the same shape as the defect it was reporting** — a single value forced to answer
several questions — and it gets the same treatment.

**The rule, now stated in the code.** Adding a field is not a bump. Changing what an
existing field answers for the same input is.

**Guarded against over-correction** by `test_the_other_reports_did_not_change_and_keep_their_version`,
which pins the four unmoved reports at 1.


## A24 — the second review model stays `claude-haiku-4.5`, on the evidence

> **Superseded by A26.** The decision below is correct about the models it
> measured: no *Claude* was worth swapping to. It was then read more broadly
> than it was measured -- as "the pair stays" -- when the question it actually
> answered was "does a stronger Claude help". Widening the field to non-Claude
> families found one that does, and the pair changed. The reasoning here is
> kept intact because A26 is only legible next to it.

**Question.** `claude-haiku-4.5` contributes little to the review pair. Should it
be swapped for a stronger Claude -- `claude-sonnet-5` or `claude-opus-5`?

**Decision.** No. Keep the pair as `("gpt-5.4", "claude-haiku-4.5")`.

**How this was settled.** By measurement, not by reputation:
`poc/review-model-swap/spike.py`, 40 calls, four models by ten trials, against
the Phase 4 fixture with four planted defects. Every call goes through
production's own `review_command`, production's `REVIEW_PROMPT` and production's
`extract_from_run`, so "readable" means exactly what it means to `atom review`.

| Model | Readable | Planted found | Precision | Distinct FP lines | Median |
|---|---|---|---|---|---|
| `gpt-5.4` | 10/10 | **98%** | **95%** | **1** | 48s |
| `claude-haiku-4.5` | 10/10 | 30% | 32% | 8 | 39s |
| `claude-sonnet-5` | 10/10 | 48% | 30% | 18 | 32s |
| `claude-opus-5` | **7/10** | 54% | 26% | 15 | 38s |

Medians are taken over runs that produced a readable report. Three opus calls
did not, and each recorded roughly 3,890 seconds -- not because opus is slow,
but because the harness could not bound a timeout, which is the defect described
in Phase 1 finding "The deadline that was not a deadline". Folding those three
into a latency figure would have described the harness rather than the model.

**Why the stronger models lose.** They do find more planted defects -- and they
are *less precise* while doing it, at roughly double the false-positive volume.
The swap trades a second model that is quiet and largely useless for one that is
loud and largely wrong, and every false line it adds is a line a developer must
read and dismiss. Opus additionally failed to produce a readable report 3 times
in 10, which is a correctness problem before it is a quality one.

**Correction, from the later `gpt-5.6-luna` evaluation (A25).** The "planted
found" column above is an *exact-line* match, and measuring a fifth model showed
that it does not mean what its name suggests. Re-scored at production's own
grouping tolerance of +/-3 lines, the same runs read:

| Model | exact line | +/-3 lines |
|---|---|---|
| `gpt-5.4` | 98% | 100% |
| `claude-haiku-4.5` | 30% | 80% |
| `claude-sonnet-5` | 48% | 100% |
| `claude-opus-5` | 54% | 100% |

Every model finds essentially all four defects. What separates them is not
detection but **line attribution** -- whether they can say where the defect is.
The decision is unchanged and its reason is sharper: `gpt-5.4` is the only model
that reliably names the exact line, and a finding attributed to the wrong line
costs a developer the same search as a finding that is simply wrong.

**What the numbers actually say.** `gpt-5.4` does essentially all of the work.
That confirms Finding 21 -- the two models are not two opinions -- at four times
the original sample. The question worth asking is therefore not *which Claude*,
but whether the second slot should hold a non-Claude model, or be spent on a
second `gpt-5.4` pass instead. That is left open deliberately; this decision
records only what was measured, which is that the proposed swap is not justified.

**Trust in these figures rests on the controls.** Both incumbents reproduced
their published Phase 4 behaviour in the new harness -- `gpt-5.4` found line 24
in 10/10 (published 20/20), haiku found line 44 in 6/10 (published 13/20). A
comparison whose controls do not reproduce is measuring the harness.


## A25 — `gpt-5.6-luna` is not adopted, and measuring it corrected A24's reasoning

**Question.** Is `gpt-5.6-luna` a better second review model than
`claude-haiku-4.5`?

**Decision.** No. The pair is unchanged.

**Measured the same way as A24** -- same fixture, same planted defects, same
production call shape, ten trials. The other four models were reloaded from
`results.json` rather than re-called: every run in that file came from the same
fixture, prompt and call shape, so reloading is sound, and re-running would have
changed the comparison as well as its cost.

| Model | Readable | Exact line | +/-3 lines | Precision | Distinct FP lines | Median |
|---|---|---|---|---|---|---|
| `gpt-5.4` | 10/10 | **98%** | **100%** | **95%** | **1** | 48s |
| `claude-haiku-4.5` | 10/10 | 30% | 80% | 32% | 8 | 39s |
| `claude-sonnet-5` | 10/10 | 48% | 100% | 30% | 18 | 32s |
| `claude-opus-5` | 7/10 | 54% | 100% | 26% | 15 | 38s |
| `gpt-5.6-luna` | 10/10 | 15% | 70% | 12% | 18 | 93s |

**Why not, at production's own tolerance.** At +/-3 -- the window `atom review`
actually groups findings with -- luna is the weakest of the five. It is also
roughly twice as slow as anything else measured, and it produces the largest
spread of lines that hold no planted defect.

**What the 15% does not mean.** Read as a detection rate it would be a
libel. Luna identifies all four planted defects in nearly every run, and its
messages are accurate and specific: the unsynchronised `Lookup`, the unvalidated
`Reserve`, the discarded `os.Create` error, the unlocked iteration in `Export`.
It also volunteers two real defects the fixture's author did not plant -- the
nil-map assignment on a zero-value `Store`, and the file that is never closed.

What it cannot do is say **where**. Across ten runs it reported the *same*
`Lookup` defect at lines 18, 19, 22, 23 and 24, anchoring it variously to the
struct field, the doc comment, the function signature and, occasionally, the
offending statement. Exact-line scoring charges that twice: once as a miss on
the planted line, once as a false positive on the line it named.

**The caveat on latency.** Quality here is fixture-determined and comparable
across runs. Wall-clock is not: luna's ten calls were made on a different day
from the other forty. The gap is wide enough (93s against 32-48s) to survive
ordinary variation, but it is a weaker number than the rest of the table.

## A26 — the second review model becomes `gemini-3.8-flash`

**Question.** A24 asked whether a stronger *Claude* helped and found none did.
That left the real question unasked: is the second slot better spent outside the
Claude family entirely?

**Decision.** Yes. `DEFAULT_REVIEW_MODELS` becomes
`("gpt-5.4", "gemini-3.8-flash")`, and `DEFAULT_TIMEOUT_SECONDS` rises from 300
to 600 to fit the new model's latency.

**How this was settled.** Seventy calls through `poc/review-model-swap/spike.py`
-- seven models by ten trials, same fixture, same four planted defects, same
production call shape, every call from an empty temporary directory so no model
can read the committed answer key (finding 28).

| model | answered | exact line | +-3 lines | precision | FP lines | median |
|---|---|---|---|---|---|---|
| `gemini-3.8-flash` | 10/10 | **100%** | 100% | 83% | **0** | 102.5s |
| `gpt-5.4` | 10/10 | 98% | 100% | **95%** | 1 | **47.6s** |
| `grok-4.7` | 10/10 | 90% | 100% | 58% | 4 | 79.8s |
| `claude-opus-5` | 8/10 | 56% | 100% | 29% | 15 | 37.8s |
| `claude-sonnet-5` | 10/10 | 48% | 100% | 30% | 18 | 32.4s |
| `claude-haiku-4.5` | 10/10 | 30% | 80% | 32% | 8 | 38.6s |
| `gpt-5.6-luna` | 10/10 | 15% | 70% | 12% | 18 | 93.3s |

**Why `gemini-3.8-flash`.** It found all forty planted defects at the exact line
and named no line that was not one, which no other model managed. A25 established
that the models separate on *attribution*, not detection -- everything finds the
bugs, few can say where they are -- and attribution is the property the merge
step actually consumes. Run through production's own `_group_by_proximity`, three
gemini runs produce three groups at 3/3 support, identical in shape to `gpt-5.4`
and unlike `gpt-5.6-luna`, whose unanimous finding fragmented into a 1/3 and a 2/3.

**Why its lower precision is not the objection it looks like.** Gemini reports
about 4.8 findings per run against `gpt-5.4`'s 4.1, and the extras are *real*
defects that happen to sit on planted lines -- the unclosed file at line 44
alongside the discarded `os.Create` error already planted there. The precision
denominator counts findings while the numerator counts planted lines, so finding
a second true defect at a planted line is scored as a miss. It is the metric
that is wrong here, not the model; the false-positive-line count, which does not
have that flaw, is zero.

**What it costs.** Latency. Gemini's median is 102.5s against `gpt-5.4`'s 47.6s,
and the gate finishes when the slower model finishes, so a review gets roughly
twice as long. Accepted deliberately: the gate runs a handful of times per change
and its value is entirely in being right.

**Why `grok-4.7` was not chosen**, despite being second on exact-line accuracy
and 23s faster: four false-positive lines against gemini's zero, and its 58%
precision reflects genuinely wrong lines rather than the scoring artefact above.
It is the better fallback if gemini's latency becomes intolerable.

**That last paragraph overstates the case, and the overstatement is instructive.**
"False positive" here means *a line that was not planted*, which is not the same
as *a line that was wrong*. Grok's most frequent one is line 38, reported in all
ten runs: the nil-map write in `Reserve`, which is a real defect the fixture was
never designed to test. Line 46, its second, is the ignored `fmt.Fprintf` error --
also real. So grok is not hallucinating four lines; it is finding unplanted bugs
and being charged for them, and gemini avoids the charge partly because its extra
findings happened to land on lines that were already planted.

The choice stands, on the narrower ground that survives this: gemini named every
planted line in every run and grok missed line 36 four times out of ten. But the
fixture cannot separate "wrong" from "right about something I did not plant",
and any future comparison that leans on the false-positive column needs a fixture
whose unplanted defects are known and enumerated, not assumed absent.

**Why the timeout moved.** 300s left 1.5x headroom over gemini's slowest observed
call (194.1s). A limit that clips a healthy model does not merely lose a reply --
it reports the model as having failed to answer, which is the precise confusion
that hid grok's real score during this measurement (finding 31). 600s is about 3x
the observed maximum. Raising it is only safe because the phase-01 fix made the
limit real; before that, a larger number would have bought a larger lie rather
than a longer wait.

**What would overturn this.** A different fixture. Seventy calls against one Go
file with four planted defects is enough to separate 100% from 30% and is not
enough to separate 100% from 95%. `gpt-5.4` and `gemini-3.8-flash` are not
distinguishable here on accuracy; they are distinguishable from everything else.

**Known cost: the default now assumes access to a model not every account has.**
Raised by the review gate against this very change. Model availability is
account-specific, and Atom's behaviour when a default model is unavailable is
deliberate but unforgiving: the review runs with the surviving model, reports
itself as partial, and **exits non-zero** (P4-3, so a CI job cannot sit green
while half its reviewers are silently failing). For a developer without gemini
access that means a failing gate until they pass `--model gpt-5.4 --model <other>`.

That is a real adoption barrier for an open-source tool and it is recorded as a
cost, not resolved. The measured fallback order is `grok-4.7` (90% exact, 4
unplanted lines) then `claude-haiku-4.5` (30%). **Pending:** whether the default
should probe availability and substitute a fallback rather than failing. It is
not decided here because "degrade quietly to a weaker reviewer" and "tell the
developer their review is not the review that was measured" are in direct
tension, and picking between them on the spot would be exactly the unmeasured
guess this phase exists to refuse.

## A27 — staticcheck gets a prompt exclusion even though the brief did not name one

**Decision.** A passing `staticcheck ./...` run is shown in the prompt's verdict list
and adds "staticcheck diagnostics" to the excluded mechanical categories.

**Why.** The brief required a `StaticcheckGate` and required the prompt to tell models
what was already proven, but its example exclusion list named vet, errcheck, race, and
govulncheck categories while omitting staticcheck. Omitting staticcheck from the
exclusion paragraph would make the new gate visible but not useful: a clean
`staticcheck` run would still allow models to spend attention re-reporting diagnostics
the tool already settled.

**Consequence.** The wording is intentionally generic. Staticcheck's exact diagnostic
set is broad and versioned, so the prompt does not enumerate every possible check or
pretend it is a proof about readability or extensibility.