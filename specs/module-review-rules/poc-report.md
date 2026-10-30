---
project: "module-review-rules"
phase: "n/a"
poc_slug: "module-review-rules"
verdict: "Inconclusive"
date: "2026-10-30"
spike_path: "poc/module-review-rules"
---

# POC Report: module-local rule delivery

## The Question

Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?

## Verdict

**Inconclusive.** The original trial's two availability probes timed out. A separately approved controlled retry completed both probes, but gpt-5.4 was unavailable and only Gemini reviewed the fixture. The complete frozen guide reached Gemini through the native JSONL pipeline and its finding passed strict extraction. However, that finding used line 9, outside the predeclared lines 10/11, and there is no second review. Do not treat either trial as confirmation of the question asked.

## Evidence: original trial

From the isolated feature worktree, `python -u .\poc\module-review-rules\spike.py --scratch "$SessionFiles\module-review-rules-native-trial"`. $SessionFiles represents the redacted machine-local session root; full invocations and raw evidence remain outside Git.

Verbatim captured output; exit code 2:

```text
Question: Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?
Models resolved from existing defaults: ["gpt-5.4", "gemini-3.8-flash"]
Budget: two availability probes and two reviews; no retries.
Synthetic-only fixed-evidence calls; no live PR, MCP, or real project input.
Synthetic go build ./... exited 0.
Synthetic go vet ./... exited 0.
Frozen guide UTF-8 bytes: 9741
Frozen guide SHA-256: 95db131a87e05a5f3bc6c5a48d59fb1f5251a798e014c2ff19d6661129c4bea9
{
  "question": "Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?",
  "models": [
    "gpt-5.4",
    "gemini-3.8-flash"
  ],
  "expected_file": "lease.go",
  "expected_lines": [
    10,
    11
  ],
  "mode": "existing fixed-evidence isolation",
  "production_loader": false,
  "rule_sha256": "95db131a87e05a5f3bc6c5a48d59fb1f5251a798e014c2ff19d6661129c4bea9",
  "rule_utf8_bytes": 9741,
  "verdict": "Inconclusive",
  "reason": "No review model could be called: gpt-5.4 (timed out (observed elapsed 60.103 seconds)); gemini-3.8-flash (timed out (observed elapsed 60.103 seconds))",
  "calls": {
    "probe": 2,
    "review": 0
  },
  "owned_fixture_removed": true,
  "duration_seconds": 86.45706220006105,
  "review_audits": []
}
```

Both stdout streams were empty. Both stderr streams held only the runner-generated diagnostic:

```text
Command timed out after 60 seconds.
```

The original source hash was 0749dc3c90e377b68dce59527f06e4f932ac1e81b783b1906b6b4fd6f20917e0. It is preserved in the first trial's executed-spike.py outside Git. The original trial and Inconclusive verdict have not been overwritten.

## Separately approved local diagnosis

The developer approved local investigation without additional model calls. The normal PowerShell launcher and the launcher used by Atom's native runner both reported Copilot CLI 1.0.105. The native `copilot --version` completed with exit code 0 in 0.25288259994704276 seconds:

```text
GitHub Copilot CLI 1.0.105.
Run 'copilot update' to check for updates.
```

The original probe logs showed configured custom MCP servers starting despite source exclusions. Locally installed help confirms --excluded-tools makes tools unavailable to the model, while --disable-builtin-mcps disables built-in servers only. The repeatable --disable-mcp-server <server-name> option controls named startup exclusions. This established a plausible startup-isolation issue, not a proven general timeout cause. No settings were changed and no additional model calls were made during diagnosis.

## Evidence: separately approved controlled retry

The developer explicitly approved at most two new probes and two synthetic reviews, preserving the original question, guide, fixture, predeclared attribution, default pair, parser, ownership behavior, and deadlines. The sole invocation-condition change was existing caller-selected exclusions for azure-devops and azure-mcp. The first guide's exact SHA-256 was asserted before any retry model calls. No production code was changed.

Execution command, with the same session-root redaction:

```powershell
python -u .\poc\module-review-rules\spike.py --scratch "$SessionFiles\module-review-rules-isolated-trial"
```

Verbatim captured output; exit code 2:

```text
Question: Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?
Models resolved from existing defaults: ["gpt-5.4", "gemini-3.8-flash"]
Budget: two availability probes and two reviews; no retries.
Synthetic-only fixed-evidence calls; custom MCP servers disabled: azure-devops, azure-mcp
Synthetic go build ./... exited 0.
Synthetic go vet ./... exited 0.
Frozen guide UTF-8 bytes: 9741
Frozen guide SHA-256: 95db131a87e05a5f3bc6c5a48d59fb1f5251a798e014c2ff19d6661129c4bea9
{
  "question": "Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?",
  "models": [
    "gpt-5.4",
    "gemini-3.8-flash"
  ],
  "expected_file": "lease.go",
  "expected_lines": [
    10,
    11
  ],
  "mode": "existing fixed-evidence isolation",
  "production_loader": false,
  "disabled_mcp_servers": [
    "azure-devops",
    "azure-mcp"
  ],
  "rule_sha256": "95db131a87e05a5f3bc6c5a48d59fb1f5251a798e014c2ff19d6661129c4bea9",
  "rule_utf8_bytes": 9741,
  "calls": {
    "probe": 2,
    "review": 1
  },
  "verdict": "Inconclusive",
  "delivery_verified": false,
  "recognized_models": [],
  "findings": [
    {
      "file": "lease.go",
      "line": 9,
      "severity": "high",
      "message": "Disable fails to clear Reserved, violating the contract that a disabled lease must not retain a reservation.",
      "model": "gemini-3.8-flash",
      "run_index": 1
    }
  ],
  "extraction_failures": [],
  "runs": [
    {
      "model": "gemini-3.8-flash",
      "outcome": "completed",
      "duration_seconds": 13.417735800030641,
      "detail": ""
    }
  ],
  "owned_fixture_removed": true,
  "duration_seconds": 53.3902694999706,
  "review_audits": [
    {
      "kind": "review",
      "model": "gemini-3.8-flash",
      "timeout_seconds": 600.0,
      "prompt_sha256": "d9abe14c74a27ba41cce198bb67f1a55ecd45033569be944a24c05dcb98e810a",
      "prompt_utf8_bytes": 13798,
      "frozen_rule_present": true,
      "outcome": "completed",
      "exit_code": 0,
      "duration_seconds": 13.417735800030641,
      "cli_user_event_matches_logical_prompt": true
    }
  ]
}
```

The gpt-5.4 availability probe completed with exit code 1. Its complete stderr diagnostic was:

```text
Error: Model "gpt-5.4" from --model flag is not available.
```

That probe took 11.43126569991 seconds. Gemini's probe exited 0 in 13.599472699919716 seconds. Only Gemini then received one review call. This is the existing pipeline's partial-review behavior, not a substituted model or a smaller success denominator. Cumulative across both explicitly approved trials: four probes and one review; there were no additional attempts.

## What The Spike Did

The disposable [Python harness](../../poc/module-review-rules/spike.py) installed Atom's real onboarding instruction bundle into an owned synthetic launch module, customized its copied Go guide, and froze it with the existing context helper. It then mutated the launch source and planted conflicting review-checkout guidance. A process-local style composition seam retained the shared seven and added the complete frozen guide.

All Go code, the added domain rule, launch/checkouts, and conflicting policies were synthetic. Real dependencies were Atom's native prompt/invocation/extraction implementation, Copilot, Git, and Go. The tiny dependency-free fixture build and vet exited 0 before model calls. Full review gate collection was explicitly skipped in the harness, not changed in production.

The fixture removed Disable's unconditional reservation reset. Before model calls, the expected finding was a retained reservation in lease.go with attribution at line 10 (method declaration) or new-file line 11 (removed reset position). Gemini's message describes that defect, but names line 9, the preceding contract comment. That is valid schema/file ownership but does not meet the frozen attribution expectation. The criteria were not broadened after seeing the response.

## Delivery And Extraction Observations

For the sole actual review, the audited native runner input contained the full 9741-byte frozen guide, including its controlled addition. Its SHA-256 remained 95db131a87e05a5f3bc6c5a48d59fb1f5251a798e014c2ff19d6661129c4bea9. Both the mutated launch marker and conflicting checkout marker were absent from the explicit packet.

The logical prompt was 13798 UTF-8 bytes with SHA-256 d9abe14c74a27ba41cce198bb67f1a55ecd45033569be944a24c05dcb98e810a. The CLI's root user event matched that logical prompt after LF/CRLF normalization. This proves that specific packet reached Gemini; it is not raw Windows child-stdin byte-identity evidence or evidence about a second reviewer.

The real ownership-aware extractor produced the printed Gemini finding with no extraction failures. Native commands retained --no-custom-instructions, --disable-builtin-mcps, fixed-evidence source exclusions, and the approved caller-selected server exclusions. There was no parser recovery, canned response, model substitution, retry, or deadline extension.

## Run Context And Preservation

- Controlled retry started at 2026-10-30T09:29:43.102537+00:00 on Windows.
- Base commit: 7c0f2d0901aba0c4aff6ee16896efe922ab163b5.
- Controlled-retry source SHA-256: fe26154581cff22177b2451403932961de4b172b8c4fa68b3c08ab81068dec46; the executed source is also preserved outside Git in the second trial's executed-spike.py.
- Toolchain: `go version go1.26.9 windows/amd64`. Fixture build/vet is not a full-project, race, coverage, or production-feature completion claim.
- Native deadlines remained 60 seconds for probes and 600 seconds for reviews. Timings are incidental observations, not a benchmark; no latency target was established.
- Raw output, prompts, argv audits, captured guide, predeclared inputs, source snapshots, and summaries remain under the two named session trial directories. No raw machine logs or real project content were added to Git.
- Owned temporary fixtures were removed. Production source, tests, packaged assets, installed tools, real module files, and machine defaults remain unchanged.
- The earlier source/test baseline is 1465 passed, 2 skipped, 95% coverage. This is not a claim that the new feature is implemented or the POC passed.

## What We Learned

The complete local guide can travel through one real native review while retaining strict extraction and ambient custom-instruction suppression. That is bounded one-review evidence, not the required two-model confirmation.

Named MCP startup exclusions changed the observed startup outcome: both probes completed rather than timing out. Different run times and the small sample prevent claiming that MCP was the sole timeout cause or that this is a general performance fix.

A separate blocker is now explicit: the configured default gpt-5.4 is unavailable for this account/runtime. That does not justify silently replacing a default in production. Gemini also chose adjacent comment line 9 rather than the predeclared positions; semantic recognition must not be reported as meeting the attribution criterion.

## What This Changes

The original question remains Inconclusive. Do not proceed to production design on a single successful transport or relax the expected finding location. A supported second reviewer must be explicitly selected and the next brief approved before another batch; any changed attribution/scoring condition must be presented, not silently tuned. Default model policy remains separate from module-rule delivery.

## Explicitly Not Covered

No second reviewer delivery/extraction was observed. Automatic rule discovery, supported formats, linked instructions, full-guide quality, ordinary tool-enabled reviews, broad compliance, cross-platform behavior, real DNC reviews, portable toolchains, and degraded-review policy remain unproven. Source exclusions are not proof that CLI startup initializes no services or accesses no network. No review-quality improvement or production gate bypass is claimed.

## Recommendation

Stop at this report gate. Return to brief revision to explicitly select a supported second reviewer and address the attribution observation. Any new calls need their own bounded approval. No design spec or production implementation starts from these results.

## Completeness Checklist

- [x] Question preserved verbatim from the approved brief.
- [x] Both trials, separate approvals, source hashes, and Inconclusive outcomes preserved.
- [x] Verbatim output and failure diagnostic included.
- [x] Actual one-review delivery and extraction separated from the missing second review and failed attribution expectation.
- [x] No post-result criterion changes or silent substitution.
- [x] Findings, decisions, explicit noncoverage, and next gate recorded.

## Report-gate reviewer selection

The developer selected Claude Sonnet 5 for a revised experiment in place of unavailable gpt-5.4. This does not change either recorded verdict or authorize additional calls. Its availability has not been probed. Attribution criteria and the next bounded brief remain to be approved; no production implementation starts yet.

## Accepted narrower milestone at the subsequent gate

On 2026-10-30 the developer accepted using the observed one-model delivery as the narrow transport-feasibility milestone and proceeding to design preparation. The original question, criteria, evidence, and Inconclusive verdict remain unchanged. This is an explicit scoped acceptance of the narrower evidence, not a post-hoc POC pass.

The prior recommendation to rerun merely for two-model/line-attribution acceptance is superseded for this milestone. Correct default source discovery and identical frozen input to all requested reviewers are implementation-test obligations. Model-specific behavior, quality improvements, and automatic production discovery remain unproven. No additional model batch or production implementation was approved; the design gate still applies.
