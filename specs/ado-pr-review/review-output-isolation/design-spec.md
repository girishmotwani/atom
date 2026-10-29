# Design: ownership-aware CLI review responses

Status: approved and implemented. Python tooling only; automatic initialized-rule/context delivery remains outside this contract.

## Purpose

Allow delegated CLI reviews to contribute only their authoritative parent answer to Atom's existing strict findings validation, without confusing completed processes with readable review results.

## Evidence and scope

Established: the accepted [POC report](poc-report.md) directly captures silent stdout concatenating a delegated sentinel with valid parent JSON, while JSONL provides separately attributable messages and an explicit terminal result. Selecting the parent final passes the unchanged findings validator. The accepted report discloses its Windows CRLF instrumentation audit and single-sample bounds.

Additional read-only evidence: all three existing Gemini review transcripts lack the optional phase field on their final assistant message. A design requiring phase=final_answer for every model would break these reviewers. The captured JSONL transport ends with a top-level result object containing exitCode, and includes separate assistant messages, child ownership, deltas and tool events.

Still assumed: the installed CLI's model-independent JSONL envelope supplies the same ownership/completion structure for Gemini and other supported models; no new live Gemini JSONL review was run. Deterministic tests will cover unphased final messages and malformed/ambiguous streams. Full live multi-model verification remains a separate gate; no general version/platform/reliability claim is made.

This contract governs response ownership, not automatic rule/context delivery.

## Public surface and placement

No new user flags, dependencies, global defaults, permissions or report-schema fields. review_command keeps its signature but requests --output-format json rather than --silent. Probe commands remain unchanged: they need exit status, not review findings. Preserve stdin prompt delivery and all caller MCP exclusions.

Append one defaulted field to ModelRun so old positional construction and direct plain-response consumers keep their meaning. Raw response_text remains raw stdout; this preserves process-versus-response facts. Existing report serializers do not expose this new internal invocation metadata.

Authoritative changed/internal signatures:

```python
@dataclass(frozen=True)
class ModelRun:
    """Keep process evidence and its encoding separate from validated findings."""

    model: str
    run_index: int
    outcome: RunOutcome
    response_text: str
    duration_seconds: float
    detail: str = ""
    response_format: Literal["text", "copilot_jsonl"] = "text"


def _to_run(
    model: str,
    run_index: int,
    result: CommandResult,
    *,
    response_format: Literal["text", "copilot_jsonl"] = "text",
) -> ModelRun:
    """Preserve actual process completion while recording response encoding."""
    ...


def _content_from_cli_jsonl(text: str) -> str:
    """Select one unambiguous root answer or raise _InvalidCliResponse."""
    ...
```

Keep the small transport selector and private _InvalidCliResponse exception in extract.py, adjacent to the existing extraction boundary. No separate adapter registry or protocol framework. invoke_models marks real review runs copilot_jsonl through _to_run; ModelRun's text default preserves existing direct callers and extraction fixtures. Existing public extraction signatures stay unchanged.

## Numbered behavior

1. Real review calls request CLI JSONL; probes retain their exact prior command. Prompt bytes remain on stdin, and models, runs, concurrency, timeout values and custom MCP exclusions do not change. No auto-retry or fallback to text mode.
2. A completed process remains RunOutcome.COMPLETED even when its transport or final findings are invalid. Real invocation records copilot_jsonl explicitly. Existing direct/default text ModelRun values retain the current extraction behavior, including fence stripping and rejection of prose mixed with bare JSON. Unsupported response-format values fail visibly, not via a guessed decoder.
3. For copilot_jsonl, ignore blank lines and accept LF/CRLF record separators. Each remaining line must decode as a JSON object with a nonempty string type. A malformed line, bare array, missing/invalid type or malformed relevant-message data produces a recorded transport failure, naming the line/category without quoting the raw event stream. Unknown well-formed event types are ignored for forward-compatible metadata handling.
4. Determine assistant-message ownership from both top-level agentId and data.parentToolCallId. Any nonempty string child marker excludes that message, regardless of its content, order or phase. Absent/null markers mean root; invalid marker types or empty-string ownership markers fail closed. Deltas, tool results and child messages are never candidate findings payloads.
5. A root assistant.message is eligible only when it has nonblank string content, no nonempty toolRequests, and phase is either final_answer or absent/null. Ignore explicitly non-final phases and messages that request tools. Reject malformed content/phase/toolRequests types where relevant. Require exactly one eligible root message across the whole stream: missing, blank-only or multiple candidates are failures, not permission to choose the last one. This supports unphased model replies without treating an arbitrary child or commentary block as authoritative.
6. Require exactly one root terminal result as the final nonblank record, with integer exitCode=0 (not bool) and a nonempty sessionId. A missing, nonzero, duplicate or malformed result, events trailing that result, or a root session.error makes the nonempty transport unreadable even if a candidate array exists. Child-owned result/error messages cannot complete or overrule the parent. This completion rule is based on the captured envelope, not on model prose claiming to be finished.
7. Validate the selected content using the unchanged fence/JSON-array/finding-schema/file-guard path. A parent answer containing malformed JSON, wrong field types, an invalid severity or prose is still invalid; child findings cannot rescue it. Parent [] is a legitimate no-findings answer. Do not repair JSON, scan bracket spans, concatenate message content, pick the last assistant event or bypass file attribution.
8. For nonempty unreadable transports, return an ExtractionFailure with a distinct `CLI response transport:` reason, preserving model/run identity, per-run partial status and existing CLI nonzero behavior. Do not include raw CLI-event excerpts in public failures: they can contain account/session metadata. Findings-validation failures may retain the existing bounded excerpt of selected model content. Completed empty streams retain existing silent-run reporting; failed/timed-out/missing-tool processes retain their prior outcomes and diagnostics. No result or agreement denominator is silently inflated.
9. The CLI/composition regressions exercise correctly framed fake JSONL responses, root/child interleaving, unphased answers, completion, malformed transport and partial-report failures. Direct text-mode extraction tests remain intact. README documents structured response isolation and explicit failure on unsupported/ambiguous output without claiming arbitrary CLI versions or previously failed live runs are now verified.

## Error handling and boundaries

_InvalidCliResponse is a private expected transport exception caught only at the extraction boundary. Decode errors and schema/ownership/completion violations become its explicit, non-payload diagnostic. Do not broadly catch unrelated programming failures. Do not reinterpret a successful process as a failed process just because its output was unreadable; completion and readability remain distinct.

Empty or missing root answers, ambiguous candidates, unknown phase formats with no eligible answer, unsupported CLI output and malformed envelopes all remain observable incomplete review evidence. No old PR response is recovered or relabeled by this change.

## Concurrency and lifecycle

No new concurrency, I/O or lifecycle owner. Each run's immutable response format and local parser state belong to that run. Existing bounded workers, runner ownership/cleanup, probe-before-review ordering, timeout handling and stable report ordering remain unchanged. No shared buffers combine separate runs or models.

Concurrent calls are safe because selection uses only local state and immutable run metadata; no new lock or worker is needed.

## Extension points

The existing injected CommandRunner remains the testable execution boundary. Response-format dispatch is the sole transport extension seam; adding a future encoding or a different CLI message contract requires its own explicit decoder and behavioral approval, not auto-detection. The strict findings validator and public renderers remain reusable without transport-specific branches.

## Trade-offs

Choose explicit JSONL message boundaries over silent text even though the envelope is larger. The new delegated-output measurement supersedes the earlier overhead-only reason for silent review output; do not rewrite historical POC results. Keep legacy direct text extraction for existing callers, not as a fallback for malformed live JSONL.

Choose one eligible root message plus verified completion over heuristics such as last-array, last-message or brace/bracket scans. A future valid stream with multiple unphased candidate messages will fail visibly until its contract is deliberately supported. Do not require the OpenAI-specific phase marker from Gemini.

Do not disable delegation, change the review prompt, broaden tool permissions, replace models, apply module rules, add surrounding context, rerun Go gates on target source, fix target code, commit or push as part of this repair.

## Validation and gate

Use deterministic Python red/green loops against numbered behavior. Add a sanitized minimal envelope helper to existing test fixtures only where real CLI-output simulation requires it; do not wrap intended malformed cases into success. Preserve direct ModelRun fixtures in text mode, all pre-existing Windows/native-entry changes and unaffected public report contracts. Reuse shared fixtures instead of duplicating event builders.

Run the affected extraction, invocation, CLI review, PR-entry, review-output and review-toolchain tests together, plus existing Markdown link and scoped whitespace checks. Run any broader existing Python checks justified by changed composition. No real model call belongs in TDD, and no Go gate is fabricated for Python tooling. A new live batch and shipping verification require separate approval.

Approving this spec authorizes only this test-first transport repair and directly related documentation. Result acceptance, independent review, a live PR retry and shipping remain separate gates.




## Implementation reconciliation

Implemented the approved signatures and behavior in Python, without material design changes. The default-text ModelRun preserves existing callers; native review runs carry raw JSONL and explicit encoding. Stream selection, completion and safe extraction failures live in extract.py; existing strict findings validation and report schema remain unchanged. See the [test map](test-spec.md) and [current verification](../verification.md). Local deterministic/full-suite evidence does not establish a fresh live Gemini JSONL review, general CLI-version support or a completed original PR report.
