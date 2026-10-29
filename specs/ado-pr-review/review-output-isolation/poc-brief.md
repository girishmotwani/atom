# POC Brief: isolate the top-level review answer

Status: explicitly approved by the developer (approve_transport_probe=true). Scope: a Python-tooling/CLI transport diagnostic, not a Go implementation spike or another PR review.

## Question

When one Copilot CLI invocation delegates exactly one tiny task, does silent text stdout mix the delegated prose with the parent JSON answer, while JSONL stdout preserves enough message ownership to identify only the parent's final answer?

## Why this remains open

Existing owned transcripts show valid root finals plus child prose in both rejected runs, and the unchanged parser reproduces the recorded error on transcript-derived mixed text. Original per-model stdout was not retained. The currently installed CLI advertises JSONL output, but an unmeasured event parser must not be designed from that help text alone.

## Approved-run candidate

Run two top-level gpt-6.1-sol CLI calls sequentially in the same empty, private neutral workspace. Each receives identical synthetic stdin instructing exactly one tiny task delegated to gpt-6.1-sol, returning a fixed prose sentinel without tools or further delegation; the parent's sole final answer must be `[]`. Do not invoke Go, Git, files, shell, network tools or Atom review from the agents. Supply no internal source, account data or PR URL.

Control: existing --silent text invocation. Treatment: same model, stdin, working directory and isolation, but --output-format json rather than --silent. Both retain --no-custom-instructions, --disable-builtin-mcps and explicit exclusions for the two observed custom MCP servers. Do not change global defaults or persistent configuration. Use the existing runner with a 120-second per-parent timeout; cleanup overhead is not an end-to-end guarantee.

Cost: two top-level model sessions and two intended tiny delegated tasks; the number of underlying inference steps is not claimed to be exactly four. No PR clone and no full PR-review batch. No extra availability calls, automatic retry or alternative model. Retain raw stdout/stderr and owned-session metadata privately.

## Treatment checks before interpreting results

1. Verify actual session input equals the shared prompt and actual model/isolation options match the plan. The only intentional arm difference is output transport.
2. Verify each session actually started and completed exactly one delegated task. If the task is missing, denied, still running or recursively delegates, this experiment does not answer the question.
3. Attribute the sentinel and parent answer using actual event ownership and final-answer markers. In the JSONL arm, prove the raw output itself preserves the required ownership markers, rather than borrowing information from a separate session log to make an ambiguous transport appear safe.

## Success, failure and boundaries

Confirmed for this controlled case only if text stdout contains the delegated prose and parent JSON, the unchanged findings parser rejects that text, and the JSONL output contains an unambiguous single root final array accepted by the same strict findings parser after ownership-aware selection. Demonstrate the delegated sentinel is excluded without bracket scanning or schema weakening.

Refuted if the exercised text transport contains only the parent answer or the structured transport demonstrably cannot distinguish the messages. Inconclusive if required actions, ownership, completion or transport evidence are missing. Record actual behavior rather than reinterpret the question.

One sample per arm is a mechanism check, not a reliability or performance estimate. No latency improvement, general model compliance, whole-review quality, cross-platform result, production repair or complete PR-review claim follows. A Confirmed result may inform a separately approved narrow design and TDD; never copy the diagnostic parser into production.
