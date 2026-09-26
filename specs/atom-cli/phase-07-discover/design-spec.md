---
project: "atom-cli"
phase: "phase-07-discover"
date: "2026-09-25"
status: "superseded — see phase-08-plugin"
poc_report: "poc-report.md"
---

# Design Spec — Phase 7: `poc new`, interactive and document-fed

> **Superseded.** This spec's delivery mechanism — a Python-side interview
> inside `atom poc new` — was abandoned before implementation. Atom now ships
> as a Copilot CLI plugin, so discovery happens through the `/atom` and
> `/atom-discover` slash commands, where the agent can already read the
> repository and run `atom` itself. See
> [phase-08-plugin](../phase-08-plugin/design-spec.md).
>
> What survives unchanged is the **evidence** below: the falsifiability rubric
> results and the zero-dependency `.docx` findings still hold, and still
> constrain whatever surface performs discovery. Nothing in the *Evidence Base*
> section was invalidated; only the *Command Surface* and the modules it
> proposed were.

## Purpose

`atom poc new` currently requires `--question`, which means it demands a
falsifiable question as its *input* — the single hardest artifact in the whole
method, and the one the rest of the pipeline exists to earn. A developer who
arrives with a vague problem, or with a requirements document someone else
wrote, has nowhere to start. This phase lets them start there anyway: run
`atom poc new <slug>` with no question, answer some questions, and leave with a
written `poc-brief.md` and a scaffolded spike.

## Evidence Base

Phase POC report: [POC Report — Phase 7](poc-report.md)

### What the POC proved

- A model can turn a vague problem statement into a falsifiable question:
  **14 of 15** replies passed the pre-registered rubric (bar: 80%), and all 15
  parsed as JSON.
- The standard library alone reads real Word documents: **42 of 42** genuine
  `.docx` files produced non-empty text, with paragraph, table, header and
  tracked-change handling verified against a controlled synthetic document.
- Atom therefore keeps `dependencies = []`.

### What it overturned

- **Question stability is low** — 0.14–0.32 word overlap across three runs on
  the same input. The model produces *a* good question each time, but a
  *different* one. Auto-adopting a single generated question is not defensible.
  → The interview proposes **candidates**; the developer chooses or edits.
- **A `.docx` extension does not mean `.docx`** — 13 of 55 files in a real
  corpus were OLE2 legacy `.doc` binaries, which no `.docx` reader can open.
  → Format is determined by **magic bytes**, never by extension.
- **The rubric is a proxy, and it was wrong** on the one case that mattered.
  → No mechanical score may reject a developer's question.

### Assumptions, not yet proven

- That a ~10% word-count deviation against Word's own figures is harmless for
  prose fed to a model. Character-level deviation was 15.3%, and fidelity is
  **not** established.
- That three candidates is the right number. It is a judgement, not a finding.

## Scope

This phase widens one command and adds one reader. It does not introduce a new
top-level command, and it does not change how spikes are run or reported.

## Command Surface

```text
atom poc new <slug> --question "..."     # unchanged, non-interactive
atom poc new <slug>                      # NEW — starts the interview
atom poc new <slug> --from problem.md    # NEW — seeds the interview
atom poc new <slug> --from mrd.docx      # NEW — seeds from a Word document
```

Making `--question` optional is a **pure widening**: every invocation that
works today keeps working, with identical behaviour and identical output.

:::mermaid
flowchart TD
    CLI[atom poc new] --> HasQ{--question<br>given?}
    HasQ -- yes --> Scaffold[scaffold_spike]
    HasQ -- no --> TTY{stdin is<br>a terminal?}
    TTY -- no --> Fail[exit 2<br>--question required]
    TTY -- yes --> Seed{--from<br>given?}
    Seed -- yes --> Read[documents.read]
    Seed -- no --> Interview
    Read --> Interview[discover.run_interview]
    Interview --> Model{model<br>available?}
    Model -- yes --> Cands[propose candidates]
    Model -- no --> Typed[developer writes<br>the question]
    Cands --> Brief[poc-brief.md]
    Typed --> Brief
    Brief --> Scaffold
:::

## Public API

Two new modules. Both surfaces are deliberately small; the interview is driven
through a `Prompter` protocol so tests never touch a terminal.

```python
# tools/atom/documents.py

class DocumentFormat(enum.Enum):
    """The format actually found on disk, independent of the file extension."""

    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain-text"
    DOCX = "docx"
    LEGACY_DOC = "legacy-doc"
    RTF = "rtf"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Document:
    """A document's extracted text plus an honest account of what was dropped."""

    path: Path
    document_format: DocumentFormat
    text: str
    dropped: tuple[str, ...]


class UnsupportedDocument(Exception):
    """Raised when a file's real format cannot be read, with remedy in the message."""


def classify(path: Path) -> DocumentFormat:
    """Identify a file's real format by inspecting its leading bytes."""


def read(path: Path) -> Document:
    """Extract readable text, or raise UnsupportedDocument naming the remedy."""
```

```python
# tools/atom/discover.py

@dataclass(frozen=True)
class Candidate:
    """One proposed spike question paired with what would refute it."""

    question: str
    refuted_when: str


@dataclass(frozen=True)
class Brief:
    """The developer's settled answers, ready to render as poc-brief.md."""

    slug: str
    problem: str
    question: str
    refuted_when: str
    will_do: tuple[str, ...]
    will_not_do: tuple[str, ...]
    success_criteria: tuple[str, ...]


class Prompter(Protocol):
    """Lets tests drive the interview without a terminal."""

    def ask(self, prompt: str, default: str = "") -> str: ...

    def choose(self, prompt: str, options: Sequence[str]) -> int: ...


def propose_candidates(
    problem: str,
    runner: CommandRunner,
    model: str,
    count: int = 3,
) -> tuple[Candidate, ...]:
    """Ask the model for candidate questions; return empty when unavailable."""


def run_interview(
    prompter: Prompter,
    slug: str,
    seed: Document | None,
    candidates: Sequence[Candidate],
) -> Brief:
    """Walk the developer from a vague problem to a settled Brief."""


def render_brief(brief: Brief, project: str, phase: str, date: str) -> str:
    """Render a Brief as poc-brief.md matching the repository template."""
```

## Types And Responsibilities

| Type | Responsibility | File |
|---|---|---|
| `DocumentFormat` | Names the formats Atom can distinguish | `documents.py` |
| `Document` | Carries extracted text with its dropped-content list | `documents.py` |
| `UnsupportedDocument` | Signals an unreadable format with its remedy | `documents.py` |
| `Candidate` | Pairs a proposed question with its refuting observation | `discover.py` |
| `Brief` | Holds the developer's settled answers | `discover.py` |
| `Prompter` | Supplies developer input to the interview | `discover.py` |
| `ConsolePrompter` | Implements `Prompter` against the real terminal | `discover.py` |

## Behaviour

1. When `--question` is supplied, `poc new` behaves exactly as today: no
   prompting, no model call, no brief written.
2. When `--question` is omitted and `sys.stdin.isatty()` is false, the command
   exits 2 with `--question is required when stdin is not a terminal` and
   writes nothing. It never blocks waiting for input.
3. When `--question` is omitted and stdin is a terminal, the interview runs.
4. The interview asks for the problem in the developer's own words, unless
   `--from` supplied one.
5. When a model is available, the interview presents `count` candidates,
   numbered, each showing its question and its refuting observation.
6. The developer may select a candidate, edit a candidate, or reject all and
   write their own question. No candidate is ever adopted without a choice.
7. When no model is available, the interview says so in one line and asks the
   developer to write the question directly. It does not fail.
8. `classify` returns `DOCX` only when the file begins with `PK\x03\x04`, and
   `LEGACY_DOC` when it begins with the OLE2 signature `D0CF11E0A1B11AE1`.
9. Reading a `LEGACY_DOC` raises `UnsupportedDocument` whose message names the
   remedy: open it in Word and save as `.docx`.
10. Reading a `.docx` returns text in which tracked deletions are absent and
    tracked insertions are present.
11. Reading a `.docx` populates `dropped` with the content kinds not
    extracted — footnotes, endnotes, comments and textboxes — and the CLI
    prints that list once, so silent truncation is impossible.
12. Table rows survive as tab-separated cells, one row per line.
13. On completion the brief is written to the current phase directory when
    `phases.derive` resolves one, and to `poc/<slug>/poc-brief.md` otherwise.
14. The brief is written before the spike is scaffolded, so an interrupted run
    never leaves a spike with no record of why it exists.
15. `render_brief` output satisfies the repository's `poc-brief.md` template,
    including its frontmatter keys.

## Error Handling

| Condition | Behaviour | Result |
|---|---|---|
| `--question` omitted, stdin not a terminal | Exit without prompting | Exit 2, message naming `--question` |
| `--from` path does not exist | Exit before prompting | Exit 2, message naming the path |
| `--from` file is a legacy `.doc` | Exit before prompting | `UnsupportedDocument`, message naming the remedy |
| `--from` file is `.rtf` or unknown | Exit before prompting | `UnsupportedDocument`, naming supported formats |
| `.docx` is corrupt or has no `word/document.xml` | Exit before prompting | `UnsupportedDocument`, naming the defect |
| Model unavailable or call fails | Continue without candidates | Interview proceeds, one-line notice |
| Developer sends EOF mid-interview | Abandon, write nothing | Exit 130, message stating nothing was written |
| Slug invalid | Exit before prompting | Existing `scaffold_spike` validation, unchanged |

Failures that can be detected before prompting are detected before prompting.
Asking a developer six questions and *then* rejecting their slug wastes their
work, so every input that can be validated up front is.

## Concurrency

- Goroutine owner: none — this is Python, single-threaded throughout.
- Shared state: none.
- Concurrent use contract: `run_interview` is **not** safe for concurrent use;
  it owns the terminal.
- The model call reuses `SubprocessRunner`, whose timeout handling is already
  hardened. `subprocess.run(timeout=...)` must not be used.

## Extension Points

- `Prompter` admits a non-terminal driver later — a TUI, or a scripted
  interview for demos — without touching interview logic.
- `DocumentFormat` admits `.odt` or `.rtf` by adding a reader, with no change
  to callers.
- `propose_candidates` takes `count`, so the three-candidate default can be
  tuned once there is evidence for a better number.

## Trade-offs Considered

| Option | Chosen? | Why |
|---|---|---|
| Widen `atom poc new` | **Yes** | Pure widening; no existing invocation changes. |
| New `atom discover` command | No | Adds a command for a step that belongs to the command that already needs it. |
| Auto-adopt the model's question | No | Refuted by the POC: stability 0.14–0.32. |
| Reject questions failing a rubric | No | The rubric is a proxy and was wrong on its one disagreement. |
| Add `python-docx` | No | The POC showed the standard library suffices; Atom keeps zero dependencies. |
| Trust the file extension | No | 24% of a real corpus was mislabelled. |
| Interview by default, even without a TTY | No | Would hang CI. Behaviour 2 forbids it. |
| Require a model for the interview | No | A core command must not require credentials. |

## What This Phase Does Not Settle

- Whether three candidates is better than two or five.
- Whether low stability is specific to `gpt-5.4`.
- Extraction fidelity beyond "good enough for prose fed to a model".
- Footnotes, endnotes, comments and textboxes remain unextracted; they are
  *declared* dropped, not *handled*.
- `.doc`, `.rtf` and `.odt` remain unreadable by design.
- Whether the interview should also seed `design-spec.md` later in the pipeline.

## Size

Two new modules and one widened argument. The interview is the only genuinely
new logic; document reading is settled code lifted from the spike, which has
already run against 42 real documents.
