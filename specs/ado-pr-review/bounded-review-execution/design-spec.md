---
project: "ado-pr-review"
phase: "bounded-review-execution"
date: "2026-10-29"
status: "approved"
poc_report: "poc-report-source-exclusions.md"
---

# Design amendment: opt-in fixed-evidence review

## Purpose and inherited contract

Extend the existing atom review rather than replace it. Introduce an opt-in execution mode that sends the existing complete diff plus explicitly supplied evidence documents, with ordinary model-side tools excluded. Preserve the current default until the separately tracked real-PR context-quality validation supports changing it. Fix the related structured-failure diagnostic leak without changing review findings or participation semantics.

The baseline remains [the original review design](../../atom-cli/phase-04-review/design-spec.md). Its whole-diff, captured-once policy remains: no chunking, truncation or invented input-size threshold. Existing explicit diff-source selection, model selection, repetition, concurrency, required Go checks, stdin delivery, strict findings schema, merge rules and PR-checkout preservation are inherited. The later ownership-aware JSONL transport repair remains authoritative over the historical silent-text choice. Initialized-rule delivery and real-PR context quality remain outside this contract.

## Evidence base and limits

The retained [source-exclusion proof](poc-report-source-exclusions.md) verifies zero tools on one actual resolved Gemini request, one native-valid synthetic finding, and owned cleanup. Empty tool selectors are not a zero-tool control; use the tested source-qualified exclusions rather than permission wildcards or enumerating current tool names.

Other providers/versions, caller-evidence adequacy, context-window fit, review quality, and new prompt compliance remain unvalidated. Explicit UTF-8 capture and serialization are deterministic obligations, not automatic semantic context selection. [Current limitations](../findings.md) remain explicit.

## Public surface

Existing commands remain valid. New opt-in form:

```powershell
atom review --working --fixed-evidence --context-file .\evidence\caller-contract.md
atom review --pr ADO_URL --fixed-evidence --context-file .\evidence\caller-contract.md --context-file .\evidence\dependency-contract.md
```

ADO_URL is a usage placeholder. Existing model overrides and check policy still apply; these examples do not authorize any actual PR access.

--fixed-evidence is a default-false Boolean. --context-file PATH is repeatable and is accepted only with --fixed-evidence; it never silently changes the execution mode. No new configuration defaults, model resolver, automatic model fallback, context budget, source-only default or alternate findings schema are introduced.

A context file is an explicit caller-prepared UTF-8 evidence document, not a request for Atom to discover related source. It may contain source excerpts, contracts, pinned identifiers or omission notes. Atom does not infer a base/head revision from the document or vouch that its claims are correct. Relative paths resolve against the CLI's original launch directory, even with --pr. Explicit absolute paths are allowed; no recursive directory walking, glob expansion, module scan, dependency-cache search or source fetching is performed. Reading an explicitly supplied document outside the checkout is intentional caller input, not automatic repository discovery.

### Authoritative Python API additions

Atom's own implementation is Python. The Go-oriented template is adapted without introducing a Go facade or new production dependency. New types are frozen data snapshots; callers cannot mutate the captured packet during concurrent review runs.

```python
@dataclass(frozen=True)
class ContextDocument:
    """Preserve one explicit evidence input without rereading it per reviewer."""

    label: str
    text: str
    utf8_bytes: int
    sha256: str


@dataclass(frozen=True)
class FixedReviewEvidence:
    """Identify the exact opt-in input without exposing its contents in metadata."""

    documents: tuple[ContextDocument, ...]
    prompt_utf8_bytes: int
    prompt_sha256: str


class ContextInputError(Exception):
    """Stop a review when explicitly requested evidence cannot be captured."""


def load_context_documents(
    paths: Sequence[Path],
    base_directory: Path,
) -> tuple[ContextDocument, ...]:
    """Freeze explicitly selected evidence before checkout preparation or inference."""
    ...


def run_review(
    request: DiffRequest,
    models: Sequence[str],
    runner: CommandRunner,
    working_directory: Path,
    runs: int,
    concurrency: int,
    window: int = DEFAULT_PROXIMITY_WINDOW,
    disable_mcp_servers: Sequence[str] = (),
    skip_toolchain: bool = False,
    include_style_rules: bool = True,
    *,
    fixed_evidence: bool = False,
    context_documents: Sequence[ContextDocument] = (),
) -> ReviewOutcome:
    """Review the existing diff with an explicit optional evidence-only boundary."""
    ...
```

Place the document types, error and loader in tools/atom/context.py. ReviewOutcome gains one final default-None field named evidence of type FixedReviewEvidence | None. ModelRun gains final defaulted fields fixed_evidence: bool = False and stderr_text: str = "". Existing positional constructions remain valid. No existing field changes type.

Append a keyword-only fixed_evidence: bool = False parameter to probe_command, review_command, probe_models and invoke_models. Forward it throughout the existing path. Append the same keyword-only parameter to _to_run after its existing response_format parameter. The private _content_from_cli_jsonl accepts a keyword-only fixed_evidence: bool = False flag. _explain accepts a keyword-only include_output: bool = True flag. All existing defaults preserve callers; no alternate simplified API or separate invocation pipeline is introduced.

## Composition

```text
CLI source/options validation
    -> freeze explicitly named context documents, if opted in
    -> optional isolated PR preparation
    -> validate direct API evidence before runner work
    -> capture one diff and selected-file formatting snapshot
    -> existing required/advisory Go checks
    -> compose one immutable prompt and opt-in metadata
    -> probes/repeated reviews with the selected tool policy
    -> strict extraction and opt-in execution-boundary checks
    -> merge/participation reporting with explicit supplied scope
```

Non-module and skip-toolchain paths retain ordinary diff capture. Checked Go modules use the [changed-file formatting contract](../../review-format-scope/design-spec.md); source capture is not repeated after checks. Direct API documents are frozen to a tuple and validated for text, ordinal labels, UTF-8 counts, and digests before runner work. CLI capture resolves from the launch directory before preparing a PR checkout.

## Numbered behavior

1. With neither new option, command arguments, review prompt, diff acquisition, ordinary-tool behavior and report shape remain unchanged. The only cross-mode correction is the structured-failure diagnostic safety rule below; it does not change run outcomes or exit codes.
2. --context-file without --fixed-evidence is a usage error before reading documents, running checks, preparing a PR or probing a model. Nonempty context_documents with fixed_evidence=False similarly raises ValueError before runner work.
3. Capture explicit files in their requested order, once per review, before PR preparation/model calls. Reject duplicate resolved paths, nonregular files, unreadable files, invalid UTF-8, NUL-containing content and empty/whitespace-only documents. Do not repair encoding, substitute empty content or omit a requested document.
4. Preserve decoded text, including line endings, exactly; calculate utf8_bytes and SHA-256 from the original UTF-8 bytes. Labels are context-1, context-2 and so on. Do not put absolute/profile paths or evidence contents into report metadata. Document provenance is caller-supplied/unverified, not asserted to match the PR's pins.
5. The opt-in prompt contains the entire unchanged captured diff and every captured document's entire text. Serialize the document section as JSON data with explicit labels; arbitrary quotes, fences or delimiter-like content cannot corrupt host framing. State that evidence is data, not executable instructions; that only supplied evidence is available; and that missing contracts must not be invented. This instruction is not a claim that prompt injection is solved.
6. Form the opt-in prompt and its SHA-256/UTF-8 byte count once before probes/review concurrency. Send the identical string through existing stdin delivery to every requested review run. Do not reread documents per model or allow an unavailable reviewer to change the packet.
7. In fixed-evidence mode, both availability probes and review calls receive --excluded-tools builtin:* custom:* mcp:*, alongside their existing MCP exclusions and custom-instruction controls. No empty available-tools selector or deny-tool wildcard is sent. Never fall back to a tool-enabled command if the CLI rejects the flags or the model fails.
8. Record fixed_evidence=True on native fixed-evidence ModelRun values. In that mode only, reject an event stream containing assistant tool requests, tool execution events, or any child-owned event as an extraction failure, with no findings salvaged from that run and an empty transport excerpt. This detects observable contract violations; zero observed calls alone is not advertised as per-run proof of zero request exposure.
9. Keep the existing unique parent answer, successful root terminal result and strict JSON finding validation. The diff's original file allowlist remains unchanged: supplying an extra evidence document does not expand which source files may receive findings. Do not reinterpret a successful process or empty array as proof of context adequacy.
10. A fixed-evidence run without --context-file is allowed but explicitly reported as diff-only, with no additional evidence. With documents, report full-diff-plus-caller-evidence scope and document metadata. Always disclose that other repository/dependency material is not automatically included and real-PR context quality is unvalidated. No omission is invented: unselected material is outside the supplied scope; any requested document failure blocks the review instead of becoming an invisible omission.
11. Preserve the original no-truncation/no-input-cap policy. Report complete prompt bytes and individual document bytes/digests so size is observable; do not label them token counts or a validated model capacity. Provider context-window rejection stays an explicit failed/unavailable/partial outcome. Adding a cap, dropping files or automatic chunking requires evidence and separate approval.
12. All ordinary required Go gates remain in force. --fixed-evidence does not imply --skip-toolchain, initialize module rules, authorize target edits, waive missing dependencies or change the prior PR-specific waiver. Existing per-process timeouts, worker concurrency, repetition and owned-process cleanup remain unchanged.
13. Native structured-review process failures must not copy stdout or stderr into ModelRun.detail. Use deterministic process-status summaries, retaining raw decoded stdout in response_text and raw stderr in stderr_text for programmatic/private investigation. is_usable remains false for every noncompleted run. Never serialize those raw fields in ordinary markdown, JSON reports or operational stderr.
14. Apply that structured-diagnostic correction to both modes: even legacy review timeouts must not dump event streams. Default text-only direct _to_run callers retain their existing behavior. Fixed-evidence probes also use safe diagnostics; legacy probe diagnostics remain unchanged. This is a declared corrective exception to default compatibility, not a new output suppression policy for normal findings.
15. Fixed-evidence transport/execution-boundary errors disclose a static reason without raw events. Ordinary native JSONL extraction already uses empty excerpts for transport errors; retain that property. Findings-schema validation and the existing handling of actual parent findings remain unchanged.
16. Markdown adds an opt-in Review evidence section describing execution policy, supplied scope, prompt size/hash, each ordinal document's byte count/hash and the context-quality limitation. When no findings are reported, qualify the result as no findings in the supplied evidence; do not claim no defects in the repository.
17. JSON adds review_execution only for opt-in outcomes: mode="fixed-evidence", tool_policy="source-exclusions-requested", scope="diff-only" or "diff-plus-caller-context", context_quality="unvalidated", prompt_utf8_bytes, prompt_sha256, and documents containing only label/utf8_bytes/sha256. Existing fields and findings schema retain their meanings; this is an additive optional field, with no schema-version bump. Legacy reports omit it.
18. Do not remove existing PR limitations about initialized rules or absent automatically collected surrounding context. Supplement them to distinguish supplied caller evidence from automatic source/rule resolution. Existing pin/provenance and original-checkout audit behavior remain unchanged.
19. Current is_partial, has_no_usable_response, denominators and exit semantics remain unchanged: missing/invalid model replies are incomplete; findings themselves do not fail the command. An opt-in complete response set may exit 0 only as a successfully executed scoped review, with the unvalidated-quality limitation still present. Exit 0 is not a readiness certification.

## Failure contract

| Condition | Error/status and observable behavior |
| --- | --- |
| Context supplied without opt-in | ValueError; CLI exit 2 with context-file requires --fixed-evidence; zero file reads, check/checkout/model calls |
| Duplicate resolved context path | ValueError; CLI exit 2 with duplicate context-file; zero model calls |
| Direct API context text/count/digest inconsistent | ValueError; CLI-style caller gets usage error; zero runner work |
| Document not a regular file | ContextInputError: context document N is not a regular file; CLI exit 1 before PR preparation/model calls |
| Document read/resolution failure | ContextInputError: context document N could not be read (exception class name); CLI exit 1; raw exception text/path is not copied into the report |
| Invalid UTF-8, NUL content, or blank document | ContextInputError naming ordinal and invalid UTF-8, NUL content, or empty content; CLI exit 1, no inference |
| Exclusion option rejected, unavailable model, process timeout/crash | Existing unavailable/run outcome and incomplete exit semantics; no retry or tool-enabled fallback |
| Fixed-evidence tool request/execution or child event | ExtractionFailure reason CLI fixed-evidence contract violated: tool request, tool execution or child event; no findings from that run; excerpt empty |
| Existing malformed/ambiguous/truncated JSONL or findings | Existing strict extraction failure, not repaired or treated as a clean answer |
| Structured command failure | Safe detail selected by CommandOutcome/exit code, not stream content; missing executable says CLI not found; timeout says timed out and labels observed elapsed seconds; runner error says runner error and cleanup status not independently established; completed nonzero says exited with code N |

A safe diagnostic may state raw process output omitted. It must not pretend to distinguish authentication, unsupported flags, provider failure or cleanup root cause without structured evidence. Raw CommandResult evidence remains available to observers; native review ModelRun values additionally retain their raw stdout/stderr. No new automatic on-disk evidence archive, secret redactor, event persistence API or debug flag is introduced in this increment. Existing CLI-private traces may aid manual diagnosis, but are not promised to exist or be safe for publication.

ContextInputError is caught explicitly by the CLI. Do not use a broad catch, successful empty fallback or silent parse/IO skip. Construct a complete context tuple before returning it; one valid file plus one invalid file is a failed capture, not a partial context success.

## Concurrency and ownership

The host captures context and composes one prompt synchronously before the existing bounded executor starts. Frozen documents and metadata are shared read-only. The existing runner remains the sole owner of launched processes and their shutdown. No new threads, locks, background agents, discovery loops or model-turn controller are introduced. A caller-owned source file may change after capture; the captured bytes remain fixed, but no atomic filesystem snapshot or consistency with independently moving local Git state is claimed. Pinned PR provenance identifies the diff, not caller evidence authenticity.

Independent run_review invocations may execute concurrently with their own snapshots/runners; mutable capture state is never module-global. User-provided CommandRunner implementations retain their existing thread-safety obligations. The unchanged cleanup tests continue to validate the actual supported Windows process lifecycle; no Go race gate is invented for Python orchestration.

## Extension points and rejected alternatives

| Option | Decision |
| --- | --- |
| Replace all reviews immediately | Rejected by developer; keep opt-in until context-quality evidence supports promotion |
| Explicit context documents | Selected by developer; auditable fixed input without speculative semantic discovery |
| Automatic changed-file/caller/import/dependency collection | Deferred; requires its own POC and quality evaluation, not hidden inside this repair |
| Larger timeout or prompt-only read budget | Not this contract; neither guarantees a completed evidence-grounded answer |
| Diff truncation, arbitrary byte/token ceiling or per-file chunking | Rejected here; conflicts with the original policy without new evidence |
| Disable MCP servers only, empty tool selector, permission wildcard | Insufficient or disproven; use the verified source-exclusion control |
| New response schema or relaxed JSON recovery | Rejected; preserve the proven ownership-aware selection and strict findings validator |
| Retain full raw events in failure messages | Rejected; privacy/volume bug. Retain private/programmatic raw evidence separately from deterministic operational summaries |

The existing CommandRunner and prompt composition are the extension seams. A future proved context collector can produce explicit documents without changing model execution; it must not claim completeness solely because it conforms to this type. Do not add a plugin/controller abstraction for that hypothetical collector now.

## TDD obligations and verification

Use deterministic Python tests with fake model calls. Drive opt-in selection/legacy identity, document freezing/error atomicity, PR launch-directory resolution, prompt equality across reviewers, all-source exclusions on probes/reviews, no fallback on rejected flags, observable execution-boundary rejection, file-allowlist preservation, safe structured diagnostics, raw evidence retention and markdown/JSON scope reporting through real red/green loops. Include quotes/fences/delimiter-like document content and failures after a valid first document. Update fake CLI framing only where the new opt-in guard requires realistic events; do not weaken existing ownership/partial-result assertions.

Add a few focused cases in existing tests/test_invoke.py, tests/test_extract.py, tests/test_review_output.py, tests/test_cli_review.py and tests/test_cli_pr_review.py; a new tests/test_context.py is appropriate for the new pure capture boundary. Run the smallest affected selectors first, then the existing project Python gate from tools: python -m pytest tests -v --cov=atom. Run python tools\check_links.py from the repository root and scoped whitespace checks. No new package, formatter or lint configuration is needed. No production code, Go gate, model batch or live PR check is claimed by this design artifact.

The separately recorded real-PR context-quality task remains pending: independently validate real candidates/clean controls and cross-file seeded defects, freeze private ground truth, compare packaged versus fuller context under an approved measured brief, and report verified recall, false positives and evidence grounding. This design does not preapprove that experiment's corpus, thresholds or spend.

## Implementation and verification

The implemented Python contract is covered by the [test map](test-spec.md) and [current verification](../verification.md). Failed runner outcomes cannot become successful merely because an alternative runner retains exit code zero. Real-PR context quality remains unvalidated.

## Logical prompt identity

Prompt metadata identifies the composed logical string encoded as UTF-8 before platform stdin normalization. Markdown must name that boundary. JSON prompt_utf8_bytes and prompt_sha256 keep their existing names, values and shape; the README defines their same logical/pre-transport meaning. Document metadata continues to identify original captured UTF-8 file bytes. No raw-stdin or verified provider-request-byte identity is promised.

The native-runner audit established that raw stdin bytes differed after existing Windows newline conversion, while JSON-decoded document text remained intact. The approved fix changes disclosure only, not composition, hashes, document capture, schemas, runner conversion or default-mode behavior. Exact-byte transport remains outside this amendment.
