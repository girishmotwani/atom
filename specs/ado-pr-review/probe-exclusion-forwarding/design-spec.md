# Design: consistent MCP exclusions for model probes

Status: approved and implemented locally; implementation explicitly accepted by the developer on 2026-10-27. Scope: one Python-tooling repair, not the remaining initialized-rule/context phases.

## Purpose and evidence

Apply existing caller-selected MCP exclusions consistently to availability probes and review calls. Deterministic invocation tests verify forwarding, ordering, defaults, and failure behavior. Small availability responses do not establish large-prompt quality, provider compatibility, or a completed PR review.

## Public surface

No new CLI flags or result types. Extend only the two existing invocation helpers with default-empty parameters. Python signatures are authoritative here because Atom's tooling is Python, not Go.

```python
def probe_command(
    model: str, disable_mcp_servers: Sequence[str] = (),
) -> tuple[str, ...]:
    """Let availability checks use the same caller-selected isolation as reviews."""
    ...


def probe_models(
    models: Sequence[str],
    runner: CommandRunner,
    working_directory: Path,
    timeout_seconds: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
    concurrency: int = DEFAULT_CONCURRENCY,
    disable_mcp_servers: Sequence[str] = (),
) -> tuple[ModelAvailability, ...]:
    """Probe selected models without starting servers their caller excluded."""
    ...
```

Append the probe_models parameter after its existing positional arguments so old callers retain their meaning. invoke_models keeps its existing signature; forward its existing disable_mcp_servers argument into probe_models. Existing review_command behavior is unchanged.

## Flow and responsibilities

Existing CLI option -> run_review -> invoke_models -> probe_models -> probe_command -> CommandRunner. After all probes settle, available models continue through the existing review_command with the same exclusions. No new abstraction, config source, model resolver, network client or lifecycle owner is introduced. Use the existing command-building conventions and avoid unrelated refactoring.

## Behavior

1. An omitted or empty exclusion sequence leaves the probe command exactly unchanged, including ping and mandatory silent/model/no-custom-instructions/built-in-MCP flags. No vendor-specific server is disabled by default.
2. probe_command appends one --disable-mcp-server/name pair per supplied entry, preserving order and duplicates without mutating caller data.
3. probe_models forwards every exclusion to every model probe and preserves the existing working directory, timeout and concurrency settings. Existing positional timeout/concurrency calls remain compatible.
4. invoke_models passes the same exclusions to availability probes and all actual review calls. No review starts until all availability probes finish; prompts remain on stdin for reviews.
5. A rejected or timed-out excluded probe still produces the existing unavailable entry and diagnostic. No available model still raises NoModelAvailable, no review call runs in that case, and a partially available model set retains existing partial-result semantics.
6. Existing repeated --disable-mcp-server CLI options reach real native probe/review commands in a deterministic fake-runner integration test. README states that exclusions apply to both phases and that unavailable default models can be overridden explicitly. No model default, fallback policy, persistent configuration, result schema or report limitation changes.

## Errors and concurrency

No new exceptions or success-shaped fallback. Preserve ModelAvailability detail, NoModelAvailable, per-run outcome mapping and the CLI's nonzero failure behavior. Keep the existing 60-second probe setting and 600-second review setting; do not claim new end-to-end bounds or increase limits. CommandRunner retains lifecycle ownership.

The existing bounded thread pool owns probe concurrency and joins before reviews. Exclusion strings are read-only input; callers must not mutate supplied sequences while invocation is in flight. Add no shared mutable state and do not change synchronization. Fake-runner tests cover forwarding, ordering, timeout diagnostics and compatibility without real model calls.

## Trade-offs and exclusions

Choose explicit user-supplied exclusions, not hard-coded Azure server names or blanket global MCP disabling. Choose explicit reviewer overrides for the eventual PR run, not an unmeasured replacement for historical defaults or silent availability fallback. Do not repair unrelated account/permission settings, source code, Go dependencies, formatting or race failures. Do not redesign model discovery, clone retention or timeout lifecycle. Do not bundle the live PR retry with this implementation approval.

## Validation and gate

Use failing Python behavior tests before implementation, then the existing invocation, CLI review, PR CLI and review-composition tests. Run the existing Markdown link checker and scoped whitespace check. Preserve pre-existing dirty edits, especially test_invoke.py's Windows runner regression and README additions. No dependencies or validation tooling are added, and no root Go gate is claimed for Python tooling.

API signatures, parameter ordering and call flow were checked against current invoke.py. Approving this design authorizes only this test-first forwarding repair and directly related documentation; result acceptance and live PR review remain separate gates.

## Verification

The existing [test map](test-spec.md) and [current verification](../verification.md) cover the implemented helper forwarding. No new model execution is implied.
