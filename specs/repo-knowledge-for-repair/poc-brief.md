# POC brief: does a repo knowledge base help an agent find every file a repair touches?

Status: **draft, awaiting approval.** Nothing is run until this is agreed.

This brief is written before any data exists. Every rule below is fixed in advance so
the result cannot be argued into being a success after the fact.

## Why this POC exists

A previous POC tested whether mined hints — word expansions, files that match the
request, files that historically change together — help an agent list the files a
repair must touch. It was **refuted**: the benefit was +3.3 points against a bar of
+15, and the confidence interval on the benefit was [-0.4, +7.2], meaning it could
not be told apart from zero.

That POC also produced the finding that motivates this one. Agents are already very
good at small repairs and bad at large ones:

| repair size | plain search recall |
|---|---|
| 1-4 files | 0.910 |
| 9-14 files | 0.758 |
| 16-23 files | 0.669 |

A developer who acts on a two-thirds-complete file list gets a broken build. So the
problem worth solving is large repairs, and the previous treatment is not the tool
for it — it went slightly *negative* there.

The new idea is different in kind. Instead of handing the agent a list of files,
hand it an **understanding of the system**: what the code does, what the modules are,
what each is responsible for, how they interact, and what the interfaces are.

## The question

**Does giving the agent an architecture knowledge base raise recall on repairs of
ten or more files from 0.726 to 0.90 or above?**

This is falsifiable. A run can return a clear no.

## The bar, fixed in advance

| result | meaning |
|---|---|
| mean recall **>= 0.90** | **Confirmed.** Build this into Atom. |
| mean recall **0.80 to 0.89** | **Promising but not proven.** Do not build it. Write down what to try next. |
| mean recall **< 0.80** | **Refuted.** The knowledge base is not the lever either. |

0.726 is the measured plain-search score on the twelve already-curated repairs that
qualify, so the top band is a gain of roughly 17 points. The previous treatment
managed 3.5 points on this same set.

A result that is directionally better but below the bar is reported as **not
confirmed**. Being better than nothing is not the bar.

## What gets compared

Two arms, identical in every respect except one.

| | searches the files | gets the knowledge base |
|---|---|---|
| **plain search** | yes | no |
| **knowledge base** | yes | yes |

Both arms run the full agent with the working directory set to a snapshot of the
code as it stood immediately before the repair. Both can search, open files and walk
directories. Neither can see git history. Both are told to be deliberately
over-inclusive, and both answer in the same format.

The only difference is that one arm receives the knowledge base as part of its
context alongside the problem statement.

## The knowledge base

Built **once**, from the repository as it stood at a fixed cut point — the last
commit before **1 June 2025**, which lands on **30 May 2025**. Code and history both.
It describes:

- what the system does
- what the modules are, and what each one is responsible for
- how the modules interact
- the interfaces between them

It is not a list of files, and it is not derived from any repair being tested.

### What it has to cover

Measured at the cut point, the subsystem under test contains:

| | |
|---|---|
| Go source files | 394 |
| Go test files | 192 |
| Lines of Go source | ~100,000 |
| Areas | 50 |
| Commits of history available | 1,656 |

### How it is built

A **structured sweep**, not a single pass:

1. List the areas.
2. One study pass per area — what it is for, its main interfaces, what it talks to.
3. A synthesis pass describing how the areas fit together.

This is roughly thirty study passes plus a synthesis, a one-off cost that is small
next to the two hundred scoring calls. A single pass over 100,000 lines was rejected
as likely to produce a shallow document, and the structured sweep is also what the
real Atom feature would do.

### How large it may be

**About 10,000 words**, with length scaled to the size of each area rather than
spread evenly: 400 words for the largest areas, 300 for mid-sized ones, 150 for
small ones, plus roughly 1,200 for the synthesis.

**Recorded deviation.** The subsystem turned out to contain 50 areas, not the ~30
that the top-level directory count suggested, because many small areas hold only
one or two files. Two options were available: skip the small areas and stay under
10,000 words, or cover everything and overshoot. Covering everything projects to
about **12,200 words**.

The overshoot was accepted. Several of the small areas — telemetry, metrics,
caching, certificates, retry handling — are touched by repairs already in the
sample, so skipping them would have left the knowledge base silent on code the
agent genuinely has to find. Two thousand words is a poor trade against a blind
spot. The ceiling existed to protect the context budget, and 12,200 words does not
threaten it.

The knowledge base deliberately does **not** list files. Its job is to tell the agent
which areas are involved, so that the agent's own search lands in the right place.
File-level discovery stays the agent's work, exactly as it is in the plain arm.

### Why a single cut point, and why that date

Every repair in the sample happened **after** the cut point. That is what makes the
result trustworthy: the knowledge base cannot contain the answer, because at the
moment it was built none of these repairs had happened yet.

Building it from the current code would leak. Today's code already contains all
twenty fixes, so an architecture document written from it would describe the system
*after* the repairs — the renamed interface, the extra parameter, the removed check.
Scoring against that would be measuring nothing.

### The cost we are accepting

The knowledge base will be up to fourteen months behind the newest repair in the
sample. This is a real weakness and it is deliberate: the alternative was building
twenty separate knowledge bases, one per repair.

It is also the honest situation. A real knowledge base is always somewhat behind the
repository, and architecture ages more slowly than file lists — modules and
interfaces move far less than individual files do.

**Secondary observation, not a result:** because the repairs are spread across the
window, we will look at whether the benefit is smaller for repairs further from the
cut point. Twenty samples cannot answer that. It is recorded as a signal for the
next POC, never reported as a finding.

### Recorded deviation: the finished size

The assembled document came out at **18,019 words** (~33,000 tokens), not the
~12,200 projected or the ~10,000 originally set. The write-ups ran consistently
longer than their targets.

It is used as-is. The question this POC asks is whether repository knowledge helps
at all, so it should be asked of the best knowledge base we can actually produce.
If a thorough one does not help, a shorter one will not either. The original limit
existed to stop the document becoming skimmable; that risk is accepted and noted as
a limitation rather than silently engineered away.

### Recorded deviation: it names some files

The document was instructed not to list files. It names 21 anyway, in prose.
Across the twenty repairs, **11.5% of answer files are named somewhere in it**, and
15 of the 20 cases have at least one answer named.

This is not a leaked answer key. The document was built only from code and history
from before the cut point, so it has no knowledge of any repair in the sample. The
named files are central ones that any honest description of the system would
mention, and most are files an agent's own search would reach immediately.

It is still an unearned head start on file discovery, so rather than assume it does
not matter, **it is measured**:

> **Pre-registered analysis.** Recall is reported twice for each arm — once over
> answer files that the knowledge base names, and once over answer files it does
> not. If the knowledge-base arm's gain appears only on named files, the gain is
> the head start and not repository knowledge, and will be reported as such.

The alternative — deleting the 21 names — was rejected because editing sentences to
remove the files they are about damages the document's meaning, and because
measuring a confound is better evidence than assuming it away.

## The sample

Twenty repairs, each touching **ten or more files**, all dated after the cut point.

Ten files is where the real cliff is, not fifteen. Both the 9-to-14 and the 16-plus
groups scored far below the bar in the previous POC, so both are the hard case. The
strict fifteen-file definition was also not achievable: the repository contains only
about a dozen such repairs in the whole window, too few to conclude anything from.

Twelve qualifying repairs were already curated and validated. Eight more were added,
and each of the eight was independently re-checked: correct parent commit, dated
after the cut, no duplicate or out-of-subtree paths, every truth file genuinely
present in the commit's own diff, and no request sentence naming a file.

A repair is a fix or an improvement to existing behaviour — not a new capability.

### One case is reported separately

One of the twenty is a Go toolchain upgrade touching 37 files. It satisfies every
rule fixed in advance, so it is **not** removed — dropping a case after looking at
its contents is exactly the kind of choice that pre-registration exists to prevent.

But it does not measure what this POC asks about. Nine of its files are Dockerfiles,
two are module files, one is a shell script, and the whole change is about 82 added
lines spread across 37 files — roughly two lines each. It is a sweep, not a repair
with a blast radius to reason about, and no amount of knowledge about what the code
does helps anyone find a Dockerfile. It is also 76% larger than the next biggest
case, so in a sample of twenty it moves the average on its own.

**Decided before the run:** the headline number is reported over the other nineteen,
and this case is reported beside it as its own line. Both figures are published
whichever way they fall.

## How it is scored

- **Recall is the headline**: of the files the real repair touched, how many did the
  agent name? A missed file is the failure this POC cares about, because it is the
  one that breaks the build.
- **Precision is reported, never optimised.** Both arms are told to over-include.
  Precision is expected to be poor and that is the intended trade.
- Files marked excluded during curation are ignored — neither credited nor penalised.
- **Five trials per repair per arm**, because the same prompt on the same repair
  varies by about 0.145 between runs. One trial per arm would measure noise.
- Total: 20 repairs x 2 arms x 5 trials = **200 agent calls**.
- An unreadable reply is excluded and counted, never guessed at or filled in.

### Recorded deviation: thirteen calls outlived their time limit

Part way through the run the machine put itself to sleep for close to two hours.
Calls that were in flight stayed open across the sleep, so their elapsed time ran
past the fifteen minute limit and the driver stopped them. Thirteen calls are
marked failed for this reason.

These are being kept, for three reasons:

- **The answers are complete.** The driver only produces a score when the reply
  contains a whole answer block; a cut-off reply is marked unreadable instead.
  All thirteen produced scores, so all thirteen finished answering. The agent had
  done its work and only the exit was stuck.
- **Sleep gives no advantage.** A sleeping machine pauses the work; it does not
  let the agent think longer or look at more of the repo. The agent gets the same
  budget either way.
- **It cannot favour one side.** Sleep stops whatever happens to be running at
  that moment. Because the work runs in repair order, a stretch of paused time
  lands on a run of neighbouring jobs no matter which side of the comparison
  they belong to. It looks lopsided per repair for that reason alone.

To keep this honest, the result is reported **both ways**: once with these
thirteen included, and once with all thirteen dropped. If the two versions land
on different sides of the bar, the result is reported as inconclusive rather than
picking the flattering one.

Timing: this rule was written down after the per-call lines for these thirteen
were visible in the run log, but before any total or comparison was worked out.
That is weaker than deciding it before the run started, and is recorded as such.

## Decided in advance, so it cannot be chosen later

- The bar is the table above. It is applied verbatim.
- Recall is the headline measure. Precision is not a fallback to claim success with.
- Results are reported by repair size as well as overall, so a good average cannot
  hide failure on the largest repairs.
- The eight new repairs are curated **before** any result is seen.
- Every repair curated is scored. No dropping cases that look unfavourable.
- If the knowledge base turns out to contain anything traceable to a repair under
  test, that repair is removed and the removal is reported.

## Known limitations, stated up front

- **The request wording comes from curators who had already seen the repair.** They
  may name things a developer starting cold would not. This inflates both arms.
- **One repository, one language, one subsystem.** Nothing here generalises beyond
  that without a second POC elsewhere.
- **The knowledge base is stale by construction**, by up to fourteen months.
- Twenty repairs is enough to detect a large effect and not enough to resolve a
  small one. That is intentional: only a large effect is worth building.

## Settled before the run

| decision | choice | why |
|---|---|---|
| cut point | last commit before 1 June 2025 | precedes every repair in the sample, so no answer can leak |
| how the knowledge base is built | structured sweep, one pass per area then synthesis | a single pass over 100,000 lines risks a shallow document |
| how large it may be | ~12,200 words, scaled by area size | enough to point at the right areas without becoming skimmable; overshoots the original ~10,000 target to cover small areas (see above) |
| arms | two | the question is knowledge base versus nothing; the old hints arm was already refuted |
| sample | 20 repairs of 10+ files, all after the cut point | that is where recall actually fails |
| trials | 5 per repair per arm | repeat runs of the same prompt vary by ~0.145 |
| model | `gpt-5.4`, both arms | the 0.726 plain-search baseline was measured on this model; changing it invalidates the comparison |

## Privacy

The repository under test is private. No file path, module name, commit identifier or
subject line from it appears in this brief or in anything committed to Atom. Curated
repair data and raw agent replies stay in the uncommitted working set.
