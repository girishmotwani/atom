# POC Report: top-level review answer isolation

Verdict: Confirmed for the single controlled delegated-task case, with an explicit post-capture Windows newline-delivery audit. This is not a reliability or performance estimate and not a production fix.

## Question (verbatim)

When one Copilot CLI invocation delegates exactly one tiny task, does silent text stdout mix the delegated prose with the parent JSON answer, while JSONL stdout preserves enough message ownership to identify only the parent's final answer?

## Evidence of treatment

Ran the two explicitly approved parent CLI calls sequentially in the same empty neutral workspace, each requesting exactly one tiny same-model delegated task. Each root received the same synthetic prompt, model and isolation; the intended transport difference was --silent text versus --output-format json. Per-arm debug-log destinations were observational only. No PR source, clone, Go execution, source edit or ADO write was involved.

Both calls exited zero with empty stderr. Actual session records show exactly one started/completed child per call, the requested model for parent and child, the child sentinel, one parent final `[]`, and both custom MCP exclusions in discovery signatures.

The initial byte-exact prompt predicate reported false in both arms: the submitted LF prompt was 716 UTF-8 bytes, while the Windows pipe delivered the same CRLF-expanded 725-byte prompt to both. Before transport-output interpretation, an offline audit proved the two actual delivered prompts are byte-identical to each other and exactly equal to the submitted prompt after CRLF-to-LF normalization. This corrects an instrumentation predicate, not a missing treatment or changed prompt. Original failed checks remain untouched in results.json; the separate audited analysis records the correction. No model calls were repeated. Because the correction was post-capture, this is weaker than a clean prevalidated delivery check and is disclosed rather than hidden.

The diagnostic initially wrote captured decoded streams using Windows text-file newline handling. Offline analysis reversed that extra text-file CRLF expansion and checked recovered UTF-8 byte lengths against the runner's recorded stdout lengths before parsing. Both original files and recovered decoded-original files remain private. This is not a claim about recovering arbitrary malformed original byte sequences; the streams here are valid UTF-8.

## Result

The text stdout was exactly the delegated sentinel followed immediately by the parent array and two newlines: `DELEGATED_TRANSPORT_SENTINEL[]\n\n`. The unchanged findings parser rejected it at character zero, reproducing the native failure mechanism without target-repository source.

The JSONL stdout contained 123 valid JSON objects, including one explicitly attributable child reply and exactly one root final-answer message. Selecting that root message using actual event ownership (no top-level agentId or data.parentToolCallId) and phase=final_answer yielded `[]`, accepted by the unchanged findings parser. The child sentinel was not selected. No bracket scanning, prose stripping, schema weakening or last-array guessing occurred.

This confirms the transport/message-selection mismatch: a valid parent review answer is not necessarily the complete plain-text stdout of an agentic CLI call. Rejecting that mixed stream is correct JSON validation; obtaining the authoritative message is the missing integration responsibility.

## Verbatim command evidence

The reproducible Python driver and raw account-bearing debug logs are retained only in the private session workspace. The driver invokes the existing SubprocessRunner with timeout_seconds=120 and identical synthetic stdin; commands differ only by their output flags and observational log destination.

Driver: review-output-isolation.py. Private run directory: review-output-isolation-01. Exact commands, submitted prompt hash, selected session IDs, per-arm raw decoded stdout/stderr and treatment checks are in its retained evidence.

### Initial execution output, including failed predicate
```text
text: treatment_checks={"child_selected_model": true, "child_sentinel_observed": true, "exactly_one_child_started_and_completed": true, "exclusions_verified": true, "prompt_delivered": false, "selected_parent_model": true, "single_owned_session": true, "single_root_final_only": true}
text: result={"arm": "text", "duration_seconds": 24.818215999985114, "exit_code": 0, "interpretation": "inconclusive: action, delivery or process check failed", "outcome": "completed", "prompt_bytes": 716, "stderr_bytes": 0, "stdout_bytes": 32}
jsonl: treatment_checks={"child_selected_model": true, "child_sentinel_observed": true, "exactly_one_child_started_and_completed": true, "exclusions_verified": true, "prompt_delivered": false, "selected_parent_model": true, "single_owned_session": true, "single_root_final_only": true}
jsonl: result={"arm": "jsonl", "duration_seconds": 10.936084100045264, "exit_code": 0, "interpretation": "inconclusive: action, delivery or process check failed", "outcome": "completed", "prompt_bytes": 716, "stderr_bytes": 0, "stdout_bytes": 50876}
Two approved calls finished; no retries, PR data or production edits.
```

### Offline delivery audit and transport analysis

```text
Delivery audit: both received prompts are byte-identical to each other (725 UTF-8 bytes).
Difference from submitted 716-byte prompt: Windows CRLF expansion only; LF-normalized content matches exactly.
The initial byte-exact delivery predicate was false. This audit precedes interpreting transport outputs; no calls were rerun.
text: process exit 0; child action/model/isolation verified.
Captured decoded stdout: 'DELEGATED_TRANSPORT_SENTINEL[]\n\n'
Strict parser diagnostic: reply is not valid json: Expecting value: line 1 column 1 (char 0)
jsonl: process exit 0; child action/model/isolation verified.
JSONL objects: 123 | owned root finals: 1 | owned child replies: 1
Selected parent final: '[]' | strict parser accepts: True
Sentinel belongs only to child: True
Original results and initial failed delivery check retained; native PR report remains partial.
```

## Explicitly not covered

- A production JSONL decoder, compatible CLI-version policy, malformed/incomplete event streams, ambiguous/multiple root finals or alternate final-message schemas.
- General format-compliance rates, latency comparisons, cross-platform behavior or larger review prompts.
- Re-running the internal PR, resolving its Go failures, restoring missing surrounding context/rules, or changing the old partial report to complete.
- Total underlying inference-step counts: the proof bounds parent calls and intended delegated tasks, not provider requests inside agentic execution.

The controlled result was accepted with the disclosed newline audit. The [implemented design](design-spec.md) and [current verification](../verification.md) describe the separate production contract; no new live run is authorized by retaining this report.
