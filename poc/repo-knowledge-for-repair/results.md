# Result: a written knowledge base of the repo did not help

**Verdict: refuted.** Writing a long guide to the codebase and handing it to the
agent did not help it find the files a repair touches. It did slightly worse than
giving the agent nothing but the repo itself.

## What was tested

Two approaches, same model, same repairs, same scoring, five repeats each:

- **Plain** — the agent gets the problem description and the code. It looks
  around the repo by itself.
- **Knowledge base** — the same thing, plus an 18,000 word guide to the codebase
  written in advance by the same model. The guide covers all 50 parts of the
  repo: what each one does, how it is structured, and what it talks to.

The guide was built only from code and history from *before* any of the repairs
existed, so it cannot contain the answers.

20 repairs, 2 approaches, 5 repeats = 200 runs. All 200 produced a complete
answer; none had to be thrown away.

## The headline

The measure is **how many of the files the real repair touched did the agent
find**. 1.000 means it found all of them.

| | Plain | Knowledge base | Difference |
|---|---|---|---|
| All 20 repairs | 0.723 | 0.690 | **-0.033** |
| 19 repairs (the odd one removed) | 0.734 | 0.712 | **-0.023** |

Against the bar set before the run — 0.90 or better confirms, 0.80 to 0.89 is
promising, below 0.80 is refuted — the knowledge base scores **0.690**. That is
**refuted**, and it is not close to the line.

It also loses to plain search. The guide did not just fail to help; the agent did
marginally better without it.

## It holds up every way we agreed to check

We said in advance we would report this with and without the 20 runs that were cut
short when the machine went to sleep, and with and without one odd repair that was
a toolchain sweep rather than a real fix. All four versions agree:

| Version | Plain | Knowledge base | Difference |
|---|---|---|---|
| Everything | 0.723 | 0.690 | -0.033 |
| Odd repair removed | 0.734 | 0.712 | -0.023 |
| Cut-short runs removed | 0.692 | 0.668 | -0.024 |
| Both removed | 0.703 | 0.691 | -0.012 |

No version comes anywhere near the bar, and none favours the knowledge base.

## How confident are we that it is actually worse?

Not very — and that is the point. The difference is too small to call.

- The knowledge base helped on **6** repairs, hurt on **11**, changed nothing on **3**.
- A test of whether that split is more lopsided than chance: **not significant**.
- Best estimate of the difference across all 20: **-0.033**, plausible range
  **-0.065 to -0.005**. That range excludes zero, but it is carried by the single
  odd repair. Drop that one and the range becomes **-0.047 to +0.002**, which
  includes zero.

The honest summary is **no real difference, leaning slightly negative**.

The size of the effect is worth putting next to the noise. Running the *same*
prompt on the *same* repair five times produces answers that vary by **0.152** on
average between the best and worst attempt. The gap we measured between the two
approaches is **0.033** — about a fifth of the variation you get from simply
running the same thing again.

## It is worst exactly where it was supposed to help

The guide was meant to help most on big, sprawling repairs, where an agent has to
know that one part of the system quietly depends on another.

| Repair size | Repairs | Plain | Knowledge base | Difference |
|---|---|---|---|---|
| 10-12 files | 8 | 0.724 | 0.687 | -0.037 |
| 13-17 files | 8 | 0.829 | 0.821 | -0.008 |
| 18+ files | 4 | 0.507 | 0.433 | **-0.074** |

The biggest repairs are where both approaches do worst, and where the knowledge
base does the most damage.

## The obvious objection, tested and dismissed

The guide happens to mention **33 of the 305 answer files by name** (11%), across
15 of the 20 repairs. A fair worry is that any gain is just a cheat — the agent
reading a filename off the page rather than understanding anything.

The opposite turned out to be true. On the files the guide **names**, the
knowledge-base agent scored **0.817** against plain search's **0.863**. It did
*worse* on the very files it was handed.

| Which files | Plain | Knowledge base | Difference |
|---|---|---|---|
| Ones the guide names | 0.863 | 0.817 | -0.047 |
| Ones it does not name | 0.700 | 0.670 | -0.030 |

So there is no hidden head start to subtract. There is no benefit anywhere.

## Why it probably failed

This is the explanation we favour, not something the experiment proves.

**The agent could already find this out for itself.** Both approaches let the
agent read the whole repo. Anything the guide says about how a part of the system
is laid out, the agent can establish in a few minutes of looking — and when it
looks, it gets today's answer rather than a summary written earlier.

**18,000 words is a large distraction.** The guide fills a big part of the
agent's attention before it has read a single line of code. Most of it is about
parts of the repo the repair never touches. That cost is paid on every run, and
it may be what the small negative difference is measuring.

**Summaries lose the thing that matters.** What makes a repair sprawl is usually
specific and awkward — one unobvious caller, a test fixture that hardcodes a
value. Describing a part of the system in 300 words naturally keeps the tidy
structural facts and drops the awkward details.

## What this means

Two ideas have now been tested for helping an agent find every file a repair
touches, and both failed:

| Idea | Result |
|---|---|
| Show which files changed together in the past | +0.033, bar was +0.15 — refuted |
| Write the agent a guide to the codebase | -0.033 — refuted |

The pattern across both: **giving the agent pre-digested material about the repo
does not beat letting it read the repo**. Future attempts should not be another
flavour of prepared context. If this problem is worth another attempt, the thing
to change is how the agent searches, not what it is handed before it starts.

Worth keeping in proportion: plain search already finds about **72%** of the
files, and on 5 of the 20 repairs it finds **everything**. The gap is real but
the starting point is not bad.

## Honest limitations

- One codebase, one model, one kind of task. This does not show that written
  guides are useless in general.
- The guide was written by the same model being tested. A human-written guide, or
  one from a stronger model, might carry more.
- 18,000 words was chosen to test the idea at full strength. A much shorter guide
  might cost less attention and do better; that was not tested.
- 20 repairs is enough to rule out a large effect, not enough to rule out a small
  one.
- The machine slept twice during the run, cutting short 20 of the 200 runs. All 20
  had already produced complete answers, and removing them does not change the
  conclusion.
