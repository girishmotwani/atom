---
project: "{project-slug}"
phase: "{phase-01-slug}"
design_spec: "{relative_path_to_design_spec}"
date: "{yyyy-mm-dd}"
---

# Test Spec

<!-- GUIDANCE: Write this at the start of atom-tdd. It maps design behaviours to concrete Go tests before implementation. The test spec is complete only when every numbered behaviour in the design spec is represented. -->

## Coverage Map

<!-- GUIDANCE: Every numbered behaviour from the design spec appears here at least once. An unmapped behaviour is either unimplemented or underspecified. Priority: P0 must, P1 should, P2 nice. Status starts as ☐ red and becomes ☑ green after the test passes. Replace the example row. -->

| Behaviour # | Test name | Priority | Status |
|---|---|---|---|
| _example — replace_ 1 | `TestDrain_CancelledContext_ReturnsBeforeStartingWorker` | P0 must | ☐ red |
| {behaviour_number} | `{TestThing_Condition_ExpectedOutcome}` | {P0-must-or-P1-should-or-P2-nice} | ☐ red |
| {behaviour_number_2} | `{TestThing_Condition_ExpectedOutcome}` | {P0-must-or-P1-should-or-P2-nice} | ☐ red |
| {behaviour_number_3} | `{TestThing_Condition_ExpectedOutcome}` | {P0-must-or-P1-should-or-P2-nice} | ☐ red |

Mapping notes:

- Behaviours intentionally combined in one test: {combined_behaviours_or_none}
- Behaviours needing multiple tests: {multi_test_behaviours_or_none}
- Behaviours requiring clarification before test writing: {clarification_needed_or_none}

## Test Cases

<!-- GUIDANCE: Repeat this block for each test. Use Go naming convention `TestThing_Condition_ExpectedOutcome`. Arrange / Act / Assert should be specific enough that an agent can implement the test without inventing behaviour. Fake only across I/O, time, and randomness; prefer real collaborators everywhere else. -->

### `{TestThing_Condition_ExpectedOutcome}`

<!-- GUIDANCE: Name the exact design behaviour under test. If a test covers multiple behaviours, list each and explain why they belong together. -->

- Behaviour under test: {behaviour_number_and_text}

<!-- GUIDANCE: Arrange names inputs, collaborators, fakes, and initial state. Avoid vague setup like "create normal object". -->

- Arrange: {arrange_steps}

<!-- GUIDANCE: Act is usually one public API call. If more than one call is needed, explain the sequence. -->

- Act: {act_steps}

<!-- GUIDANCE: Assert observable outcomes, returned errors, state changes, and calls across boundaries. Do not assert implementation details unless the design makes them part of the contract. -->

- Assert: {assertions}

<!-- GUIDANCE: List fakes and why each is necessary. If no fakes are needed, write "None — real collaborators are deterministic and cheap." -->

- Fakes needed and why: {fakes_or_none}

Red command expected to fail:

```bash
go test ./... -run {TestThing_Condition_ExpectedOutcome}
```

Expected red failure:

```text
{expected_red_failure_or_compile_error}
```

Green command expected to pass:

```bash
go test ./... -run {TestThing_Condition_ExpectedOutcome}
```

## Edge Cases And Error Paths

<!-- GUIDANCE: Uncovered error branches are the usual real coverage gap, not uncovered getters. Include boundary values, invalid inputs, cancellations, dependency failures, and partial writes where relevant. Replace the example row. -->

| Case | Expected | Test name |
|---|---|---|
| _example — replace_ dependency returns temporary error | error is wrapped with operation context | `TestLoad_DependencyTemporaryError_ReturnsWrappedError` |
| {edge_case_1} | {expected_1} | `{test_name_1}` |
| {edge_case_2} | {expected_2} | `{test_name_2}` |
| {edge_case_3} | {expected_3} | `{test_name_3}` |

Error-path audit:

- Constructor errors covered: {constructor_errors_or_none}
- Dependency errors covered: {dependency_errors_or_none}
- Context cancellation or timeout covered: {context_cases_or_none}
- Invalid input covered: {invalid_input_cases_or_none}

## Concurrency Tests

<!-- GUIDANCE: State what runs under `go test -race`, or write exactly "none — no concurrent code in this phase". If the design starts goroutines or shares mutable state, include at least one race-aware test. -->

{race_test_plan_or_none}

Race command:

```bash
{go_test_race_command_or_none}
```

## Fixtures And Helpers

<!-- GUIDANCE: List helper functions, fixture files, and test data. Helpers should clarify tests, not hide the behaviour being asserted. Assertion helpers must call `t.Helper()`. -->

- {fixture_or_helper_1}
- {fixture_or_helper_2}

## Coverage Target

<!-- GUIDANCE: Use coverage percentage as a signal, not a goal. Chasing coverage by testing trivial getters is waste. Prefer meaningful behaviour and error-path coverage over a high number. -->

Target: {coverage_target_or_behaviour_target}

Rationale: {coverage_rationale}

## Completeness Checklist

<!-- GUIDANCE: Check these before writing production code. Leave gaps visible rather than inventing tests after implementation. -->

- [ ] Every numbered design behaviour appears in the Coverage Map.
- [ ] Each P0 behaviour has at least one named test.
- [ ] Test names follow `TestThing_Condition_ExpectedOutcome`.
- [ ] Arrange / Act / Assert is specified for every test case.
- [ ] Fakes are limited to I/O, time, randomness, or other nondeterministic boundaries.
- [ ] Error paths and edge cases are mapped to tests.
- [ ] Concurrency tests or an explicit no-concurrency statement are included.
- [ ] Coverage target is framed as a signal, not a reason to test trivial code.
- [ ] Each test has an expected red failure recorded before implementation.
- [ ] Race-enabled tests are included for any shared mutable state.
- [ ] The spec does not weaken or reinterpret design behaviours.
