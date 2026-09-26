---
project: "atom-cli"
phase: "phase-07-discover"
date: "2026-09-25"
status: "ran"
spike: "poc/discover-falsifiability/spike.py, poc/docx-zero-dependency/spike.py"
raw: "poc/discover-falsifiability/results.json"
---

# POC Report — Phase 7: `discover`, interactive and document-fed

Two spikes were run for this phase, because the feature rests on two
independent unknowns. Either one could have killed the design on its own, so
each was asked and answered separately.

| Spike | Question | Verdict |
|---|---|---|
| A — `discover-falsifiability` | Can a model turn a vague problem statement into a falsifiable question? | **Confirmed** (14/15, bar 80%) |
| B — `docx-zero-dependency` | Can a `.docx` be read with zero third-party dependencies? | **Confirmed** (42/42 genuine files) |

---

## Spike A — falsifiable questions from vague input

### The Question

Can `gpt-5.4` turn a vague problem statement into a falsifiable question?

### Verdict

**Confirmed.** 14 of 15 replies met the pre-registered rubric, against a bar of
80%; all 15 replies parsed.

### Evidence

Command:

```bash
python poc/discover-falsifiability/spike.py            # 15 live calls
python poc/discover-falsifiability/spike.py --analyse  # re-scores saved replies
```

Output (tail; full run in `poc/discover-falsifiability/analyse.log`):

```text
stability (word overlap across runs, per document):
  batch-importer   0.14
  cache-layer      0.24
  config-reload    0.32
  echo-service     0.23
  event-bus        0.26

pass rate        : 14/15 = 93%
confirmed at     : >= 80%
refuted below    : 50%

Verdict: Confirmed -- questions met the pre-registered bar.
```

A representative passing reply, verbatim:

```text
  [PASS] event-bus run 3
         Q: Can a Go prototype of a topic-routed event bus deliver our representative peak
            traffic to matching subscribers with p99 end-to-end latency under 50 ms and
            zero dropped messages?
         R: It is refuted if a replay of representative peak traffic produces any dropped
            message or a p99 end-to-end latency above 50 ms for matching subscribers.
```

Run context:

- Date/time run: 2026-09-25
- Working tree at `66b7a6b`, spikes untracked
- Python 3.13.14; model `gpt-5.4` via `copilot --silent`
- Inputs: 5 deliberately vague problem statements x 3 runs = 15 calls
- Thresholds pre-registered in source before the first call

### What The Spike Did

The spike at `poc/discover-falsifiability/spike.py` sends each vague document
to the model with a fixed prompt, asks for JSON (`question`, `refuted_when`,
`program_sketch`), and scores every reply against a four-check rubric:
`single_subject`, `refuting_observation`, `not_a_preference`,
`mechanically_checkable`.

- Real: the model, the CLI invocation path, the JSON parsing.
- Simulated: the problem statements, which were written for the spike rather
  than taken from a real backlog.
- Measured: rubric pass rate, and question stability across repeat runs.

### What We Learned

- **The single failure is the rubric's fault, not the model's.** The
  `mechanically_checkable` regex lists `serve|serves` but not `serving`, so a
  sound config-reload question was marked unusable. Judged by a human, the
  result is 15/15. The rubric was deliberately **not** edited after seeing the
  result; changing a pre-registered instrument to improve its own score is how
  measurement becomes storytelling.
- **Stability is low: 0.14–0.32 word overlap** across three runs on the same
  document. The model reliably produces *a* good question, but a *different*
  good question each time. This is the finding with the largest design
  consequence.
- The rubric is a **proxy**. It detects the shape of falsifiability — a named
  observation, a single subject, no preference language — not falsifiability
  itself. Its pass rate must never be quoted as a measurement of question
  quality.
- Cost of a scoring bug is real: the first run crashed on a wrong enum member
  *before* the raw-save line, discarding all 15 paid-for replies. The spike now
  writes each reply to `raw/` before any scoring runs, and one failed call no
  longer aborts the other fourteen.

### What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| A model can convert vagueness into a falsifiable question | Confirmed | The interview may rely on model assistance for this step. |
| The model will converge on one question per problem | **Refuted** | The interview must present **candidates and let the developer choose**, not auto-adopt a single generated question. |
| A mechanical rubric can gate question quality | Inconclusive | Usable as a hint to the developer; unusable as an automatic accept/reject gate. |

### Explicitly Not Covered

- One model only (`gpt-5.4`); low stability may or may not be model-specific.
- Synthetic problem statements, not real backlog items.
- The rubric was never validated against human judgement at scale — only
  against six hand-written cases and the one disagreement found above.
- Nothing about latency or cost at interview scale: calls took 18–29s each.

---

## Spike B — reading `.docx` with zero dependencies

### The Question

Can the standard library alone (`zipfile` + `xml.etree.ElementTree`) recover
the readable text of a real Word document — including table cells and headers,
and correctly excluding text deleted under tracked changes?

### Verdict

**Confirmed.** Every genuine `.docx` in a 42-file real-world corpus yielded
non-empty text, and median deviation against Word's own recorded word count was
11.3%, inside the pre-registered 15% tolerance.

### Evidence

Command:

```bash
python poc/docx-zero-dependency/spike.py "$env:USERPROFILE\Downloads"
```

Output, verbatim:

```text
Question: can zipfile + ElementTree read a real .docx?

files named .docx   : 55
actually .docx      : 42
mislabelled         : 13  (13 x legacy-doc)
                      no .docx reader can open these; the extension lies.
extracted non-empty : 42/42  (100% of genuine)

containing tables   : 24
tracked changes     : 2
with header parts   : 9

comparable to Word's count : 23
median deviation           : 11.3%
within 15% tolerance          : 17/23

deleted-text exclusion tested on : 1 documents
deleted text correctly excluded  : 1/1

pre-registered: success >= 95%, median deviation <= 15%

Verdict: Confirmed -- the standard library alone reads these documents.
```

Run context:

- Date/time run: 2026-09-25
- Corpus: 55 files named `.docx` in a local private folder; no content was
  printed, stored, or transmitted. No model was involved.
- Python 3.13.14, standard library only
- Ground truth: Word's own `<Words>` / `<Characters>` values in
  `docProps/app.xml`, written by Word at save time

### What The Spike Did

The spike at `poc/docx-zero-dependency/spike.py` opens each file as a zip,
parses `word/document.xml`, walks the body in document order, and emits
paragraphs as lines and table rows as tab-separated cells. Headers are read
from their separate parts. `<w:delText>` is skipped; `<w:ins>` content is kept.

- Real: 42 genuine Word documents produced by Word itself.
- Synthetic: a hand-built document with known expected output, used to verify
  the extraction *rules* where ground truth is controlled.
- Measured: extraction success, deviation against Word's counts, structural
  flags, and deleted-text exclusion.

### What We Learned

- **24% of the corpus is not `.docx` at all.** Thirteen files are OLE2 legacy
  `.doc` binaries renamed to `.docx`. No `.docx` reader can open them —
  `python-docx` would fail identically, because OLE2 is not a zip. This is the
  highest-value finding of the spike, and it is a *product requirement*, not a
  parser defect.
- **The first run reported Refuted at 76%** because those thirteen sat in the
  denominator. The instrument was corrected — classification by magic bytes —
  and the bar was left untouched. The correction is defensible only because it
  rests on a verifiable file signature rather than on judgement.
- The extraction rules were verified exactly against a synthetic document:
  paragraphs do not run together, table cells stay tab-separated, insertions
  are kept, deletions are excluded. The deletion check was **mutation-tested**:
  a deliberately leaky extractor makes it fail, so it is not vacuous.
- **Fidelity is not proven.** Deviation against Word's counts is 11.3% for
  words but **15.3% for characters**, with only 11 of 23 documents inside 15%
  on the character measure. The character check was run *after* the fact and
  was not pre-registered.
- The undercount is **not** explained by unread parts: of 42 documents, only 1
  has substantive footnotes, 0 have endnotes, and 1 has a textbox. The
  residual is most plausibly noise in `app.xml` itself, which is written by
  whichever application last saved the file — but that is a hypothesis, not a
  measurement.

### What This Changes

| Assumption going in | Status | Consequence for the design |
|---|---|---|
| Reading `.docx` requires a third-party dependency | **Refuted** | Atom keeps `dependencies = []`. |
| Files named `.docx` are `.docx` | **Refuted** | Ingestion must classify by magic bytes and report a specific, actionable error for legacy `.doc`. |
| Extraction fidelity is good enough to feed a model | Confirmed, weakly | Acceptable for prose fed to a model; **not** established for any use needing exact text. |

### Explicitly Not Covered

- Real-world deleted-text evidence rests on **one** document; the rest of the
  assurance is synthetic.
- Byte-exact fidelity is unproven, and the character-level check is the weaker
  of the two measures.
- Footnotes, endnotes, comments and textboxes are **not** extracted. They were
  nearly absent from this corpus, so their absence is untested rather than
  known-safe.
- `.rtf` and `.odt` were not present and are unhandled.
- One corpus, one authoring environment.

---

## What the design must now take as given

1. **The interview offers candidates; the developer chooses.** Spike A's low
   stability makes auto-adopting a single generated question indefensible.
2. **The model is an assistant, not a gate.** The rubric is a proxy and
   disagreed with human judgement on the only case where it mattered.
3. **Atom takes no runtime dependency for document ingestion.**
4. **Format is determined by content, not by extension.** A legacy `.doc` must
   produce a clear "save this as .docx" message, never `not a zip archive`.
5. **Ingestion is lossy and must say so.** Footnotes, comments and textboxes
   are dropped today; the design must state this where the developer can see
   it rather than silently truncating their problem statement.

## Recommendation

**Proceed to spec.** Both unknowns resolved in favour of the proposed design,
and the two refuted assumptions (question stability, extension trustworthiness)
sharpen the spec rather than block it.

Next artifact: `specs/atom-cli/phase-07-discover/design-spec.md`

Conditions before continuing:

- The design must specify candidate selection, not single-question adoption.
- The design must specify the unsupported-format error path explicitly.
- The design must state which document content is silently dropped.
