---
project: "atom-cli"
phase: "phase-06-state"
date: "2026-09-24"
status: "draft — awaiting the developer gate"
---

# Design Spec — Phase 6: `state`, derived

## Purpose

Run this in the Atom repository today:

```
$ atom status
Project: C:\Users\gimotwan\work\atom
Phase:   unknown
1 problem reported below.
Problems:
  - C:\Users\gimotwan\work\atom\.atom\state.json does not exist.
    This project does not look initialised -- run `atom init` first.
exit=1
```

Six phases are on disk. Thirty-eight specification documents. Six hundred and
eighteen passing tests. Five shipped commands. And Atom's own status command
says the project does not look initialised.

It is not lying. `.atom/state.json` is listed in `.gitignore`, so the file that
Atom treats as the sole source of truth about a project has never once survived
a clone. Every fact it held was a *declaration* — written at `atom init`,
advanced by hand, contradicted by reality the moment anyone forgot to advance
it, and erased entirely by the one operation every collaborator performs first.

This phase deletes that dependency. The evidence of where a project has reached
is already on disk, in the artifacts each phase produces. Phase 6 makes
`atom status` read *that* instead.

The framework's own thesis applies to its own state: a design document is a
prediction, and a POC is an observation. `state.json` was Atom predicting where
it had got to. The `specs/` tree is the observation.

## Evidence Base

`poc/derived-state/spike.py`, `probe_mtime.py`, and
[`poc-report.md`](poc-report.md). The brief recorded predictions and a decision
rule **before** the spike ran, which is what makes the central finding binding
rather than a post-hoc rationalisation.

### What the POC proved

**F6-1 — document completeness is not derivable.** This is the phase's central
finding and it eliminates the design I expected to write. A real
`design-spec.md` of 18,024 characters across 13 sections was truncated to its
**first four sections (4,215 characters)** and still passed *every* candidate
rule: exists, non-empty, ≥1 KB, ≥3 sections, has-sections-and-no-TODO. A
document can be structurally perfect and substantively a stub.

The brief had fixed the consequence in advance: if no rule distinguishes a
complete document from a truncated one, then **report presence, never
completeness**.

**F6-2 — the structural rules were simultaneously too weak and too strict.**
They were fooled by the truncation *and* by a headings-only outline, while
**rejecting `phase-01-check/tdd-log.md`** — a genuine, finished, 3,377-character
document whose only sin is having two level-2 sections. A rule that admits
stubs and rejects real work is worse than no rule.

**F6-5 — only two section headings are common to all five completed specs**:
`Purpose` and `Evidence Base`. Both survive the truncation and the outline. Two
sections is the most any structural check could possibly demand, and it is not
enough to be worth having.

**F6-3 — never read mtime.** The prediction (that clone order would scramble
it) was *refuted*: ordering survived 5 of 5 clones, because git checks out in
index order and index order is lexical. An apparent 4-of-5 tie was chased down
and proved to be float rounding in my own probe. But two further measurements
condemned mtime regardless:

| Action | Effect on the phase directory's mtime |
|---|---|
| Editing an existing artifact's contents | **none** — a directory tracks entries, not content |
| **Creating** a new artifact inside an old phase | that phase becomes newest **immediately** |

The second was measured with the exact task that was about to be performed:
writing `phase-01-check/poc-report.md` makes *Phase 1* report as the current
phase. The conclusion stands, for a reason the prediction got wrong.

### What it overturned

Two of five predictions survived. The design I would have written without the
spike — count sections, check a size floor, sort by mtime — is wrong in all
three of its mechanisms. It would have passed its tests, shipped, and reported
Phase 1 as current the moment anyone repaid an old artifact.

## Scope

**In:**

- Deriving the current phase from the repository, not from a declared file.
- Deriving which artifacts a phase has produced, by presence.
- Reducing `.atom/state.json` to the two things that genuinely cannot be
  derived: project configuration and human approvals.
- Committing that file instead of ignoring it.
- Rewriting `atom status` against derivation.
- Removing the phase/status state machine that no longer has a job.

**Out:**

- Judging whether an artifact is *finished*. F6-1 forecloses it. Atom reports
  what exists and leaves the judgement to the developer.
- Enforcing phase order, or refusing to advance. Atom reports; it does not
  police. (See *What This Phase Does Not Settle*.)
- Any new command. `atom status` already exists; this changes what it reads.

## What Is Derived And What Is Declared

The distinction is the whole design, so it is stated once, explicitly:

| Fact | Source | Why |
|---|---|---|
| Which phases exist | derived — directory names | the directories *are* the phases |
| Which phase is current | derived — branch, then lexical order | both are observable |
| Which artifacts a phase has | derived — file presence | presence is a fact |
| Whether an artifact is *complete* | **neither** — not reported | F6-1: not derivable, and a declaration would be a lie with a checkbox |
| Whether a POC was skipped | declared — `poc-report.md` frontmatter | a skip leaves no trace to observe; absence of a spike is indistinguishable from a spike not yet run |
| Whether a gate was approved | declared — `.atom/state.json` | a human said yes; nothing on disk records consent |
| The Go module path | declared — `.atom/config.json` | configuration, not evidence; kept separate from state per B73 |

The two declarations are honest about being declarations. A `status: "skipped"`
line sits **in the same file** as the reasoning that justifies it, where a
reviewer reading the evidence cannot miss it. That is weaker than measurement
and stronger than a section count, and the spec says so rather than pretending
otherwise.

## Resolving The Current Phase

**B158** — A phase directory is one matching `^phase-(\d{2})-([a-z0-9-]+)$`
inside `specs/<project>/`. The anchors are deliberate: a stray folder cannot
masquerade as a phase.

**B158a** — `<project>` is resolved by looking one level down: the project
directory is the immediate subdirectory of `specs/` that contains at least one
phase directory. If none does, there are no phases (B164). If more than one
does, that is a genuine ambiguity — Atom reports it as a problem naming the
candidates and uses the lexically first, so `status` still answers rather than
refusing.

This was missed in the first draft of this spec, which said `specs/<project>/`
and never said how `<project>` was chosen. Today the question is invisible
because this repository has exactly one such directory (`specs/atom-cli/`,
alongside two loose `.md` files that are correctly ignored) — which is
precisely why it was easy to miss and would have been resolved by whichever
implementer hit it first. A rule that is unambiguous on the only data you have
is still an unwritten rule.

**B159** — Directories that do not match are ignored silently. `specs/` holds
`phase-plan.md` and will hold more; a non-match is not a problem to report.

**B160** — Phases are ordered **lexically on the full directory name**. The
two-digit `NN` prefix makes lexical order numeric order. mtime is never read,
for any purpose, anywhere in this phase (F6-3).

**B161** — If the current git branch matches the phase-directory pattern, the
phase it names is the current phase.

**B162** — Otherwise the current phase is the lexically greatest phase
directory. This covers `main`, detached HEAD, `scratch/...`, and any branch
that simply is not named after a phase.

**B163** — If the branch names a phase that **has no directory**, that phase is
still reported as current, marked **not started**, with every required artifact
absent. This is not an error.

F6-6 demanded this be decided explicitly, so here is the reasoning. Creating
the branch before the directory is not a mistake; it is the ordinary first
move of a new phase. A developer who has just run `git switch -c phase-07-foo`
and then runs `atom status` is asking "what do I owe?" — and the useful answer
is the list of seven artifacts, not an error. The cost is that a typo
(`phase-09-ghost`) reports as a pristine new phase rather than a mistake. Atom
cannot tell those apart, so it reports what it sees and says where it got it
(B177) rather than guessing.

**B164** — If there are no phase directories and the branch names none, there
is no current phase. Reported as such; not an error. A project that has not
started a phase yet is in a legitimate state.

## Artifact Presence

**B165** — The required artifacts are exactly:

```
poc-brief.md  poc-report.md  design-spec.md  test-spec.md
tdd-log.md    findings.md    decisions.md
```

This set is not invented. It is the measured union of every file across all
six existing phase directories — the workflow already produces these and
nothing else.

**B166** — For each required artifact Atom reports **present** or **absent**.
There is no third state. It never reports "complete", "valid", "sufficient",
or any synonym (F6-1).

**B167** — Atom never reads an artifact's size, section count, heading
structure, or content in order to judge it. The only file whose *content* is
ever parsed is `poc-report.md`, and only for the single field in B168.

This is stated as a prohibition rather than left implicit because the
prohibited design is the intuitive one. Every rule the POC tested was
reasonable-looking, and every one of them was wrong.

**B168** — `poc-brief.md` is required **only when a POC actually ran**. Atom
reads `status:` from `poc-report.md`'s YAML frontmatter, which is one of
exactly two tokens:

| Token | Meaning | Is `poc-brief.md` required? |
|---|---|---|
| `ran` | a spike was executed | yes |
| `skipped` | the POC was deliberately not run | no |

**Only an explicit `skipped` excuses the brief.** Every other condition —
`ran`, an unrecognised token, a missing `status:` line, or no `poc-report.md`
at all — leaves it required.

This is stated as a single rule because the alternative was measurably
inconsistent. An unrecognised token led to the brief being required (B169),
while a *missing report* — strictly the more unknown case — excused it. The
more ignorant Atom was, the less it asked for. A phase that had not yet
written its report would show six artifacts owed when it will almost certainly
owe seven: five of this project's six phases ran a POC.

The direction of the error matters more than its size. Over-requiring shows a
developer a document they may not owe, and they resolve it by declaring the
skip — which is exactly the record the framework wants. Under-requiring hides
a document they do owe, and nothing ever surfaces it.

**B169** — An unrecognised `status:` value is reported as a problem, and
`poc-brief.md` is treated as **required**. The failure leans toward asking for
more evidence, never less. A typo must not silently excuse an artifact.

**B170** — If `poc-report.md` is absent, the question "was a POC run?" has no
answer. Both `poc-report.md` and `poc-brief.md` are reported absent, and no
problem beyond those two absences is raised — the missing report already says
everything.

Absent is a statement about **presence**, not about **requirement**. The brief
stays required (B168), so it is reported as *absent and owed* rather than
quietly dropped from the tally. This phase reports what exists; it does not
shrink the list of what a phase owes just because it cannot yet see it.

**B171** — The vocabulary is closed and matched exactly, not by substring. A
rule that substring-matches prose breaks the first time someone rephrases the
sentence; this repository already accumulated four different header
conventions across five phases before anyone noticed.

Against the real repository the rule scores:

| Phase | `status` | Result |
|---|---|---|
| phase-01-check | `skipped` | all required present |
| phase-02-poc … phase-05-ship | `ran` | all required present |
| phase-06-state | `ran` | missing 5 — the artifacts this spec is part of |

## The Approvals Record

**B172** — `.atom/state.json` is reduced to a version and an approvals list:

```json
{
  "version": 2,
  "approvals": [
    {"phase": "phase-06-state", "gate": "design-spec", "date": "2026-09-24"}
  ]
}
```

No `phase`. No `status`. Those are derived now, and a file that repeats a
derived fact is a file that can disagree with reality.

`module_path` stays in `.atom/config.json`, where Phase 3 put it. **B73 is not
repealed by this phase**: config is what the developer chose, state is what the
tool tracks, and they are separate files on purpose. An earlier draft of this
spec folded `module_path` into `state.json`; that was an error, caught during
implementation, and it is recorded here rather than quietly corrected because
the split it violated is load-bearing. The two files now have cleanly different
lifetimes — config is written once at `init` and read-only in practice, while
approvals accumulate.

**B173** — The file is **removed from `.gitignore` and committed**. It records
human decisions, which are project history, not machine scratch. That it was
ignored is the root cause of the failure in *Purpose*.

**B174** — An absent `.atom/state.json` is **not an error** for `atom status`.
It means no approvals have been recorded. The phase and artifact report is
produced in full regardless.

**B175** — A corrupt or unreadable `.atom/state.json` is reported as a problem,
and the phase and artifact report is **still produced in full**. Derivation
does not depend on the file, so a broken file must not suppress the answer.

B174 and B175 are the point of the whole phase, expressed as behaviour: the
question `atom status` exists to answer is now answerable when the state file
is missing, stale, or wrecked. Today, it is not.

**B176** — `atom init` keeps its job: it writes `config.json` with the
`module_path` exactly as before, and a `state.json` holding an empty approvals
list. It no longer writes a phase or a status. Initialising a project is
configuration, not a claim about progress.

## Output

**B177** — The text rendering reports, in order: the project root, the current
phase, **how that phase was resolved** (branch or lexical fallback), the
artifact table, and any recorded approval for that phase.

Naming the resolution source is not decoration. B163 lets a typo'd branch
report as a new phase, and B162 silently falls back; a developer seeing an
unexpected answer needs to know which rule produced it.

**B178** — After the current phase, every **other** phase is summarised on one
line: its name, and how many of its required artifacts are present out of how
many are required.

The detail belongs to the phase you are working on; the rest is peripheral
vision. A developer wants to see at a glance that Phase 3 is `7/7` and Phase 1
is `6/6` — the latter being six because its POC was skipped (B168), which is
exactly the kind of quiet correctness that is worth being able to eyeball. A
full report for every phase would bury the current one, and no report at all
would hide the project's shape.

**B179** — The JSON rendering carries the same facts under a stable contract:
`root`, `phase`, `phase_source`, `phase_started`, `artifacts` (a name →
boolean map), `approvals`, `problems`, and `phases` — an ordered array
covering **every** phase including the current one, each with its name,
artifact map, and required count.

JSON gets the full detail for every phase where text gets one line. The text
rendering is triaged for a human reading a terminal; the JSON contract exists
for a program, which has no attention to conserve and every reason to want the
whole picture in a single call.

**B180** — Every problem found is reported, not just the first. This is B93,
inherited from Phase 1's B17, and it is unchanged.

**B181** — The exit code is 0 when Atom could answer the question — which,
after this phase, is nearly always. A non-zero exit is reserved for a project
root that cannot be read at all. Missing artifacts are **information, not
failure**; `atom status` is a report, and a phase in progress is the normal
case.

This is a deliberate change from today's behaviour, where the absent state
file produced exit 1.

The cost is accepted knowingly: `atom status` can never serve as a CI gate
asserting that a phase is finished. That is the correct trade. Such a gate
would have to decide what "finished" means, and F6-1 proved that question has
no answer Atom can compute — it could only ever check presence, which is
precisely the stub-shaped hole the POC found. A gate that passes on seven
truncated documents is worse than no gate, because it converts an unanswered
question into a green tick. If blocking is ever wanted, it needs its own
design and its own evidence, not an exit code borrowed from a reporting
command.

## What Is Removed

**B182** — Removed from `state.py`: the `Phase` enum, the `Status` enum,
`phase_index`, `next_phase`, `InvalidTransition`, and the phase/status fields
and transition logic on `ProjectState`. They encode a state machine whose every
fact is now derived.

**B183** — `ProjectState` is replaced by an approvals-shaped record. `Project`
keeps the approvals surface, `initialise`, `is_initialised`, the config
accessor, **and the event log accessor**.

The event log is **not** in scope for removal. `.atom/events.jsonl` remains a
machine-generated append-only log, still gitignored, and `atom status` keeps
reporting the last event and any damaged lines — Phase 3 behaviour that this
phase does not repeal. It is named explicitly because an earlier draft of this
sentence read "keeps only what `init` and the approvals record need", which is
narrower than intended and led an implementation to delete a working feature.
A removal list must name what goes; it must not be inferred from what a
summary happens to mention.

**B184** — `status.py` is rewritten against derivation. `StatusReport` loses
`state`/`initialised` in favour of the derived phase and artifact map.

**B185** — Tests for removed behaviour are deleted, not skipped or weakened.
Tests for surviving behaviour are kept. The temp-file sweep (B81/B82) and the
report-everything rule (B93) survive intact.

This phase is a **net reduction**: roughly 250 lines of state machine removed
against roughly 150 added.

## Resolved At The Developer Gate

Settled with the developer before this spec was written:

| Question | Decision |
|---|---|
| Should a justified POC skip still produce an artifact? | Yes — a `poc-report.md` that records the skip and its reasoning. |
| Is `tdd-log.md` required? | Yes — and Phase 5's was written before deriving anything. |
| How is the current phase resolved? | Branch name first, falling back to the newest phase directory. |
| Does `status` report one phase or all of them? | Current phase in detail, plus a one-line summary of every other (B178). |
| What does the exit code mean when artifacts are missing? | 0 — Atom answered the question. Missing artifacts are information, not failure (B181). |

Settled by measurement, not opinion, and not open for redesign without new
evidence:

| Question | Settled by |
|---|---|
| Report completeness? | **No.** F6-1 — a 4-section truncation passed every rule. |
| Count sections or bytes? | **No.** F6-2 — fooled by stubs, rejects real documents. |
| Sort by mtime? | **No.** F6-3 — repaying an old artifact makes that phase "current". |

## What This Phase Does Not Settle

- **Whether `status: "skipped"` is the right long-term signal.** It is a
  declaration, and a report could claim `skipped` beside a spike that plainly
  ran. It is adopted because it is co-located with its own justification, and
  because the alternative the POC tested was measurably worse. If a stronger
  signal appears, this is the seam to revisit.
- **Enforcement.** Nothing here refuses to proceed when artifacts are missing.
  Atom reports. Whether any gate should ever *block* is a separate decision,
  and one worth making deliberately rather than by accident.
- **Phase 1's outstanding re-review.** The trigger condition is met and the
  debt is still open; it is not this phase's work.
- **Multi-project repositories.** `specs/<project>/` implies more than one
  project could exist. This phase resolves against a single configured project
  and does not settle what `status` means when there are several.

## Size

| Item | Estimate |
|---|---|
| Behaviours | 28 (B158–B185) |
| Production lines | ~150 added, ~250 removed |
| Files touched | `state.py`, `status.py`, `render.py`, `cli.py`, `.gitignore` |
