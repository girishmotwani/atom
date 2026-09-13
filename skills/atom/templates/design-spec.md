---
project: "{project-slug}"
phase: "{phase-01-slug}"
author: "{agent-or-developer-name}"
date: "{yyyy-mm-dd}"
status: "draft"
poc_report: "{relative_path_to_phase_poc_report}"
---

# Design Spec

<!-- GUIDANCE: Write this for one phase only, after that phase's POC. Every significant decision should trace to POC evidence or be labelled as an assumption. -->

## Purpose

<!-- GUIDANCE: One paragraph explaining what this phase makes possible that was not possible before. Good answers focus on capability. Bad answers describe implementation chores. -->

{purpose_paragraph}

## Evidence Base

<!-- GUIDANCE: Link the phase POC report and summarize what it established. Every significant design decision below should trace to this evidence or to an explicit assumption. Unsupported decisions are guesses and must be labelled as assumptions. -->

Phase POC report: [{poc_report_title}]({relative_path_to_phase_poc_report})

- Proven by POC: {proven_fact_1}
- Proven by POC: {proven_fact_2}
- Assumption, not yet proven: {explicit_assumption_1}

## Design Overview

<!-- GUIDANCE: Provide concise prose plus one diagram. Diagrams must be ASCII art or Mermaid only; no image files and no PlantUML. For Mermaid, use <br> for line breaks in labels, never \n. -->

{design_overview_prose}

:::mermaid
flowchart LR
    Caller[Caller] --> API[{exported_api_name}]
    API --> Core[{core_type}<br>{single_responsibility}]
    Core --> Dependency[{dependency_interface}]
:::

## Public API

<!-- GUIDANCE: Show the exported Go surface as a code block with a doc comment on every exported symbol. Keep it minimal: unexporting later is a breaking change, exporting later is not. Signatures here must match the implementation and be internally consistent everywhere they appear in this document. Check every parameter, return value, and call site. -->

```go
// {ExportedType} exists so callers can {reason_the_type_exists}.
type {ExportedType} struct {
    // unexported fields omitted
}

// New{ExportedType} constructs {ExportedType} with dependencies supplied by the caller.
func New{ExportedType}({dependencyName} {DependencyInterface}) *{ExportedType}

// {ExportedMethod} {why_the_method_exists_and_what_contract_it_provides}.
func ({receiverName} *{ExportedType}) {ExportedMethod}(ctx context.Context, {inputName} {InputType}) ({OutputType}, error)
```

## Types And Responsibilities

<!-- GUIDANCE: One responsibility per type, stated without the word "and". File names should make the primary type obvious. Replace the example row. -->

| Type | Responsibility | File |
|---|---|---|
| _example — replace_ `WorkerPool` | Owns bounded worker lifecycle | `worker_pool.go` |
| `{TypeName}` | {single_responsibility} | `{file_name.go}` |

## Behaviour

<!-- GUIDANCE: Number each testable behaviour statement. These become test cases in the next step, so each must be independently verifiable. If you cannot imagine the test, the statement is too vague. Replace the example. -->

1. _example — replace_ When the context is cancelled before work starts, `{ExportedMethod}` returns `{expected_error}` without starting a goroutine.
2. {behaviour_statement_2}
3. {behaviour_statement_3}

## Error Handling

<!-- GUIDANCE: List expected failure conditions, observable behaviour, and the error returned. Errors should carry enough context for callers to diagnose the failed operation. -->

| Condition | Behaviour | Error returned |
|---|---|---|
| {condition_1} | {behaviour_1} | `{error_value_or_wrapped_error}` |
| {condition_2} | {behaviour_2} | `{error_value_or_wrapped_error}` |

## Concurrency

<!-- GUIDANCE: State goroutine ownership, shutdown, mutex or channel ownership, and what is safe for concurrent use. If the type is not safe for concurrent use, say that explicitly; silence is not a contract. Anything concurrent must be validated with `go test -race`. -->

- Goroutine owner: {owner_or_none}
- Shutdown path: {shutdown_path_or_none}
- Shared state: {state_and_guard_or_none}
- Concurrent use contract: {safe_or_not_safe_statement}
- Race validation: `{race_command_or_none}`

## Extension Points

<!-- GUIDANCE: Describe where future behaviour can be added without editing existing code. Prefer narrow interfaces consumed at the point of use and concrete types returned by constructors. -->

- {extension_point_1}
- {extension_point_2}

## Trade-offs Considered

<!-- GUIDANCE: Record rejected options so the next reader does not re-litigate them. A good row explains why the chosen option fits the POC evidence and phase scope. Replace the example row. -->

| Option | Chosen? | Why |
|---|---|---|
| _example — replace_ single goroutine drain loop | No | The POC refuted the latency target at required throughput. |
| {option_1} | {Yes-or-No} | {reason_1} |
| {option_2} | {Yes-or-No} | {reason_2} |

## Out Of Scope

<!-- GUIDANCE: List work intentionally excluded from this phase. Exclusions should line up with the phase plan and prevent design creep. -->

- {out_of_scope_1}
- {out_of_scope_2}

## Completeness Checklist

<!-- GUIDANCE: Check these before the design gate. Inconsistent API signatures are the most common spec error; verify every occurrence manually. -->

- [ ] Purpose states the new capability this phase enables.
- [ ] Phase POC report is linked.
- [ ] Every significant design decision traces to POC evidence or a labelled assumption.
- [ ] Diagram is ASCII art or Mermaid only.
- [ ] Every exported Go symbol has a doc comment.
- [ ] Public API is minimal.
- [ ] Every API signature is consistent everywhere it appears in this document.
- [ ] Every behaviour statement is numbered and independently testable.
- [ ] Concurrency contract is explicit, including "not safe for concurrent use" if applicable.
- [ ] Rejected trade-offs are recorded.
