# POC report: explicit source-wide tool exclusions

## Question

Can the installed Copilot CLI expose zero tools to a Gemini review through Atom's existing stdin/JSONL invocation path, while returning a schema-valid finding for a known synthetic Go defect within the existing per-call deadline?

## Verdict: Confirmed for this single mechanism trial

The approved --excluded-tools builtin:* custom:* mcp:* invocation exposed zero tools on the resolved model-request surface. Request-level response metrics independently report zero available tools and zero tool tokens. Gemini completed one root model call, issued no tool requests, and returned the known synthetic empty-slice-panic finding. The unchanged native ownership-aware JSONL selector and findings validator accepted it. Owned process exit and exact temporary-work-directory removal were independently confirmed.

This confirms the tested no-tools mechanism on the observed CLI, not adequate evidence packaging, general review accuracy, calibrated severity, reliable future completion, or a completed live PR review. The previous Inconclusive wildcard-denial attempt and Refuted empty-selector attempt remain unchanged.

## Invocation and scope

Executed exactly the one call approved in [poc-brief-source-exclusions.md](poc-brief-source-exclusions.md), with no probe, retry, replacement model or delegated agent. The only logical change from the prior capture script is replacing the empty selector with the three source-wide exclusion patterns. Preserved the synthetic fixture, model, prompt, existing MCP exclusions, stdin/JSONL delivery, debug capture, 600-second bound, production runner and observational process-handle cleanup checks.

```powershell
python poc\bounded-review-execution\source_exclusions_spike.py --scratch <new-private-scratch-directory>
```

The scratch argument is an explicitly redacted publication placeholder; exact argv and stdin are retained privately. The executed spike's SHA-256 is 84711dbf5032c4016f0836074c68e35eab63a93b276f54cc0d71f9e15a7224ef. The captured invocation imported Atom's Python tooling directly. Observed external CLI version: 1.0.105. The Go-oriented workflow uses Python here because the uncertain mechanism is Atom's actual Python-to-CLI invocation, not a Go interface.

## Evidence of actual tool exclusion, inspected before the finding

The CLI debug trace contains one turn tool surface resolved record for the selected Gemini model, with zero catalog, resolved and deferred tools. The actual API request summary names the same model and omits the tools field. Omission alone is not credited as evidence: request-level response metrics independently show available_tool_count=0, tool_token_count=0 and num_tool_calls=0. This is actual request-resolution/response evidence, not transient initialization telemetry or the model's claim. No nonexistent tool fingerprint is inferred from header fingerprints.

Verbatim output from offline audit of the saved CLI-generated records:

```json
{
  "resolved_request_surfaces": [
    {
      "model": "gemini-3.8-flash",
      "catalog_tool_count": 0,
      "tool_count": 0,
      "deferred_tool_count": 0
    }
  ],
  "actual_api_request_summaries": [
    {
      "model": "gemini-3.8-flash",
      "tools_field_present": false
    }
  ],
  "response_request_metrics": [
    {
      "available_tool_count": 0,
      "tool_token_count": 0,
      "num_tool_calls": 0
    }
  ],
  "verified_zero_tools": true
}
Request-level zero-tool evidence verified before findings validation.
```

The offline inspection does not create sessions or call models. Raw traces remain private. Capture-summary.json's pending-inspection label is its original pre-audit state, not the final verdict; separate request-exposure-audit.json and native-validation.json retain the completed audit without rewriting that history.

## Process, native validation and cleanup evidence

Verbatim offline validation output, after the exposure check:

```json
{
  "process_outcome": "completed",
  "exit_code": 0,
  "duration_seconds": 32.48058630002197,
  "stderr_bytes": 0,
  "verified_zero_actual_tools": true,
  "root_model_calls_started": 1,
  "root_model_calls_finished": 1,
  "root_tool_requests": 0,
  "tool_executions": 0,
  "child_events": 0,
  "delivered_prompt_matches": true,
  "root_terminal_results": 1,
  "root_terminal_exit_zero": true,
  "parser_failure": null,
  "findings": [
    {
      "file": "head.go",
      "line": 6,
      "severity": "critical",
      "message": "The condition len(values) < 0 is never true because slice lengths are non-negative, causing empty slices to trigger a runtime panic at values[0].",
      "model": "gemini-3.8-flash",
      "run_index": 1
    }
  ],
  "owned_observed_processes_exited": true,
  "owned_work_directory_absent": true
}
```

Elapsed time is one observed process duration, not a latency benchmark. The synthetic severity is the model's output, not proof of severity calibration. Retained process handles were signaled after the unchanged runner returned and were then closed; no job handle was retained. The owned work directory was separately checked absent. Private logs/evidence are intentionally retained, not working-directory leaks. Windows text-file newline expansion was reversed once when loading decoded stdout for native validation; no answer concatenation, bracket scanning or response substitution was used.

## Verification limits

This is the recorded synthetic mechanism result, not a new invocation or an end-to-end ADO review. The captured request and output were inspected offline; no additional model call is implied. Tool isolation does not establish caller-context completeness, general review accuracy, calibrated severity, broader provider/version compatibility, or reliable future completion. Current diagnostic behavior and deterministic validation are described in the [design](design-spec.md) and [verification](../verification.md).
