# Decisions — Phase 6: `state`, derived

Two kinds of decision are recorded here, kept apart on purpose:

- **P6-n — developer decisions.** Made by the human at a gate.
- **A-n — agent decisions.** Made by an agent because the spec did not say.
  Every one of these is a place an agent chose on the developer's behalf, and
  each is listed so it can be overturned.

---

## Developer Decisions

### P6-1 — Derive the phase; never store it

**Context.** `state.json` held a `phase` and a `status`, advanced through a state
machine. The filesystem already carried the same facts in `specs/`, so the two
could disagree — and the POC showed they did, because nothing forced a developer
to run a command when they made a directory.

**Decision.** The phase is derived from the branch, then from the phase
directories. Nothing writes it down. Expanded into B158–B164 and B182.

**What this gives up.** A stored phase can record intent that the filesystem
does not show — "I am working on Phase 7" before Phase 7 exists. B163 recovers
most of that: a branch naming a phase with no directory is still the current
phase, marked not started.

---

### P6-2 — Report artifact presence; never judge completeness

**Context.** The obvious next step after listing artifacts is saying whether
they are *done*. Several rules were candidates: a minimum length, a required set
of headings, a `status:` header.

**Decision.** Presence only. Expanded into B165–B171.

**Settled by measurement, not by preference.** A real 18,024-character,
13-section `design-spec.md` was truncated to its first four sections — 4,215
characters, no conclusions, no test plan — and passed **every** candidate rule.
The decision rule was fixed before the data arrived. A file that is 23% of a
document is not 23% judged incomplete; it is judged complete, confidently, by
every measure available. Recorded in `findings.md` §3.

**Consequence.** No dataclass in this phase carries a completeness field. That
was verified through `dataclasses.fields` rather than by reading the source.

---

### P6-3 — Only an explicit `skipped` excuses a missing POC

**Context.** B168/B170 had to decide what a *missing* POC report means when a
phase legitimately skipped the POC.

**Decision.** Only an explicit `skipped` marker excuses it. Anything else — an
unrecognised token, or no report at all — leaves the POC required.

**Decided on the direction of the error, not its frequency.** Measured across
the repository's own phases: `skipped` → 6 required; an unrecognised token → 7;
no report → 6. The counts were close enough to argue either way. What settled it
is what each mistake costs: wrongly excusing a POC hides a phase that never
proved anything, while wrongly requiring one shows a `[ ]` next to a file the
developer knows they skipped. The first failure is silent; the second is
visible and harmless.

---

### P6-4 — `atom status` exits 0 for a phase in progress

**Context.** Before this phase, an absent state file exited non-zero.

**Decision.** Exit 0 whenever Atom could answer. Missing artifacts are
information, not failure. Expanded into B181.

**Known to be incompletely delivered.** See A-6 below and `findings.md` §8: the
non-zero branch this decision reserves turns out to be unreachable.

---

## Agent Decisions

### A-1 — The project directory is the subdirectory of `specs/` holding phases

**Why it was needed.** B158 said phases live in `specs/<project>/` and never said
how `<project>` resolves. The gap was found while writing the CLI layer, after
the design spec was approved.

**Chosen.** The project directory is the immediate subdirectory of `specs/`
containing at least one phase directory. None means no phases — not an error.
More than one is reported by name, and the lexically first is used.

**Status.** Promoted into the design spec as **B158a** rather than left as an
agent decision, because it is a behaviour the developer should be able to
overturn. Never exercised against a real multi-project repository (F6-D4).

---

### A-2 — `to_dict()` carries more keys than B179 lists

**Why it was needed.** B179 names eight JSON keys. B183 separately requires that
`last_event` and damaged-line reporting survive the phase, which those eight do
not cover.

**Chosen.** Treat B179 as a guaranteed **subset**, not an exhaustive list, and
carry `module_path`, `last_event`, `swept` and `damaged_log_lines` alongside.
The contract test asserts the documented eight are a subset rather than
asserting equality — an equality assertion would have made B183 unimplementable.

---

### A-3 — `artifacts` in JSON is the full presence map

**Why it was needed.** B179 says only "a name → boolean map" and does not say
whether the map holds all seven artifact names or only those required for that
phase.

**Chosen.** All seven, with the required *count* exposed separately as
`phases[].required`. A consumer wanting the required subset can compute it; a
consumer given only the subset cannot recover the rest. Recorded as F6-D8 so the
developer can pin it the other way.

---

### A-4 — "A root that cannot be read" means "is not a directory"

**Why it was needed.** B181 reserves a non-zero exit for a root that cannot be
read at all, without defining the test.

**Chosen.** `root.is_dir()`. A permission-denied but existing directory would
still report readable. Simulating an unreadable-but-present directory is not
portable across Windows and POSIX, and inventing a second mechanism to detect it
was out of scope. Recorded as F6-D9.

---

### A-5 — Ambiguity reports from implementers are treated as defect reports

**Why it was needed.** An implementing agent reported that B172 appeared to
merge `module_path` into `state.json`, contradicting Phase 3's B73. It flagged
this as "the only ambiguity" and then resolved it toward the spec — which was
wrong. A spec error had become a code error, quietly and correctly.

**Chosen.** When an implementer reports an ambiguity, fix the document and
re-issue rather than answering the question in a message. The answer in a
message dies with the conversation; the defect stays in the spec and reaches the
next reader.

**This is a process decision, not a code decision**, and it is the most portable
thing this phase produced. Five design-spec defects were found this way.

---

### A-6 — The unreachable non-zero exit was left in place

**Why it was needed.** `atom status` has no `--root`; the root is the process's
working directory, which necessarily exists and is a directory. So
`could_answer` is always true, and B181's reserved non-zero exit — along with
the red problem rendering tied to it — can never fire. Measured, not assumed.

**Chosen.** Leave both in place and report the finding rather than delete them.
The repair is a genuine design fork: declare `status` a report that always exits
0 and delete the dead branch; give `could_answer` a reachable meaning; or add
`--root` so a caller can name a bad path. Choosing among those is the
developer's call at a gate, not the implementer's.

**This one is uncomfortable to record**, because this phase also added a
framework rule against exactly this shape — a branch that cannot fail is
decoration claiming to be robustness. The rule was written against *tests*; here
it applies to production code, and the finding stands unfixed. Recorded as
F6-D6.

---

## A-7. Triage the review gate against source, not against agreement counts

**Context.** The review gate produced five finding groups. All five came from
one of the two models; four appeared in 1 of 3 runs.

**Chosen.** Read every finding against the actual code before judging it, and
ignore the run counts entirely when deciding what is real. Three of the five
were genuine defects, and two of those three were 1-of-3 findings — so treating
low agreement as low confidence would have shipped all three.

**Rejected:** ranking by how many runs reproduced a finding. Repetition is a
recall mechanism, not a precision one. The reviewer that raised each defect once
was right each time; the reviewer that stayed silent across three runs was not
casting a vote against them.

---

## A-8. Fix three of five, defer the fourth, and say which is which

**Chosen.** Fixed the two state-file defects and the problem-scoping defect;
deferred the `specs/` fallback as F6-D10. The three fixed share a property that
made them in-scope: each is a case where Atom *says something untrue* — an
intact file called broken, a blank record presented as an approval, a phase
rendered without its reason for being unreadable. The deferred one is a case
where Atom is merely more permissive than its spec, which is a behaviour
question for the developer rather than a correctness one.

**Rejected:** fixing all five in the same pass. F6-D10 changes what layouts
Atom accepts, and widening or narrowing that is a gate decision.

---

## A-9. Recognise a version-1 file by its fields, not by its version number

**Context.** B172 adds `"version": 2` to `state.json`, which reads like the
mechanism for telling file generations apart. It is not: the v1 writer emitted
no version key.

**Chosen.** Detect v1 by the simultaneous presence of `phase` and `status` and
the absence of `approvals`. Requiring both v1 fields keeps the gentler message
away from arbitrary junk that merely lacks `approvals`.

**Rejected:** trusting `payload.get("version") == 1`, which no real file carries
and which would therefore have produced a fix that never fires — the §8 mistake
repeated in a new place.

**Also rejected:** migrating v1 to v2. Nothing in v1 is worth keeping; it stored
a phase and a status, both of which this phase derives.

---

## A-10. Re-read through the existing parser rather than parse again

**Chosen.** `_outdated_file_problem` calls `read_json` with no required keys
instead of calling `json.loads` directly, so the shape rules that define "a
usable state file" live in exactly one place.

**Rejected:** a local `json.loads` on the error path. It is shorter, and it is a
second reader free to drift from the first about what counts as a JSON object —
the same duplication B172 rejects for `module_path`, at a smaller scale.
