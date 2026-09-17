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

## Tracked Debt

| # | Item | Status |
|---|------|--------|
| D6 | Review quality unmeasured — agreement predicted the real defects on one fixture where the evaluator planted them | Pending — the Phase 4 **gate** addresses this by running `atom review` over the Phase 1 diff and triaging the findings |
| D7 | Deduplication strategy | **Partially closed.** `analyse_agreement.py` measured cross-model and within-model agreement on the spike data; the merge model (B118–B124) is derived from it. Still one fixture. |
| D8 | Large diffs untested (Q3, P4-4) | Pending — A6 makes size visible; the cliff remains unmeasured |
| D9 | Fence behaviour observed under one prompt only | Pending |
| D10 | Non-Windows behaviour unmeasured | Pending — consistent with D2 from Phase 3 |
| D11 | Cost per review unmeasured, and P4-2 tripled it | Pending — no token or credit figure exists for a single review, let alone six calls |

---

## Gate Record

| Gate | Date | Outcome |
|------|------|---------|
| POC | this session | Run. 2 of 6 predictions refuted. Compliance is bimodal, not a rate; no truncations occurred. Decision rule amended on the record (P4-1). |
| Design spec | this session | **Approved.** Four open questions resolved (P4-2 … P4-5) plus one follow-up on partial-review exit codes. |
| TDD | — | Not started |
| Phase gate | — | Does not close until `atom review` has been run over the Phase 1 diff and its findings triaged — inherited bootstrap debt agreed at the Phase 1 gate. Six agent decisions (A1–A6) await developer review, A2 and A5 most in need of it. |
