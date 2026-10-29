# POC brief: explicit source-wide tool exclusions

Status: completed and accepted; retained as the contract for the recorded synthetic result. It does not authorize another invocation.

## Question

Can the installed Copilot CLI expose zero tools to a Gemini review through Atom's existing stdin/JSONL invocation path, while returning a schema-valid finding for a known synthetic Go defect within the existing per-call deadline?

## Evidence motivating the changed control

The previous empty-selector trial is Refuted: the actual request advertised 21 tools despite a successful one-turn response. The approved offline investigation found that both a bare selector and an explicitly empty string normalize to an unset filter. The installed CLI/SDK expose source-qualified exclusion patterns, and the actual parser plus exact normalizer preserve nonempty builtin:*, custom:* and mcp:* filters. That supports this candidate, not a claim that the actual request is already isolated.

## One trial and cost

Exactly one root Gemini 3.8 Flash invocation against the existing source-free empty-slice-guard fixture. No probe, retry, replacement model, delegated agent, batch or private ADO source. Existing native stdin/JSONL invocation, no-custom-instructions, disable-builtin-mcps, azure-devops/azure-mcp exclusions, debug logging, 600-second process bound and independent owned-process/work-directory cleanup remain unchanged. Expected spend: one synthetic model call, bounded at 600 seconds; it may still fail.

Change only the candidate exposure control: omit the empty --available-tools selector and append --excluded-tools builtin:* custom:* mcp:*. Use source_exclusions_spike.py and a separate external evidence directory. No installed CLI, global defaults, production implementation or dependency changes.

## Required evidence and success criteria

Before grading the answer, inspect CLI-generated metadata for the actual model request, not transient initialization events. It must establish zero available tools through the actual request fingerprint/count and corroborating request-level metrics where available. A missing direct tools property, a model assertion or zero tool calls alone is insufficient. Report disagreement or missing evidence explicitly.

All are required for Confirmed: verified zero actual request exposure; zero tool requests/executions and child events; exactly one root model call starts and completes; successful process within the existing bound with one successful terminal root result; unchanged native JSONL/finding validators accept the known empty-slice-panic finding on head.go's changed guard/indexing path; independently confirmed owned-process exit and exact temporary-work-directory removal.

A demonstrated failure to suppress tools is Refuted. Unverifiable exposure, invalid output, unavailable model or timeout is Inconclusive. Stop at the result; no fourth trial is authorized automatically.

## Limits and gate

One mechanism/functional observation, not a timing benchmark, ADO review, evidence-package-quality comparison or guarantee that future model calls always succeed. It does not choose host context collection, change strict output validation, waive explicit incomplete failures, repair raw timeout diagnostics, authorize design/TDD, or authorize a push. Success permits presenting the bounded fixed-evidence design for approval, not silently implementing it.
