---
project: "ado-pr-review"
phase: "native-pr-entry"
date: "2026-10-24"
status: "approved"
poc_basis: "approved ordinary Git preparation; synthetic local-Git verification"
---

# Design: native PR entry using ordinary Git

## Purpose and boundary

Add `atom review --pr <ADO URL>` as a fourth explicit review source. Resolve the PR, prepare an independent temporary checkout of its source, and run the existing review pipeline against its actual target branch. Do not switch, stash, clean, fetch into, or rewrite the developer's checkout. Do not post to ADO.

Initialized-rule delivery and automatic surrounding-code context are not implemented. Both Markdown and JSON PR reports explicitly disclose that limitation; they do not claim initialization-aware, contextual review.

## Established versus assumed

Established by repository inspection:

- `tools\atom\diff.py` already captures `git diff <base>...HEAD`; reuse it unchanged unless integration exposes a directly related defect.
- `tools\atom\cli.py` already selects an explicit local source, invokes `run_review`, and preserves required-check/model/partial-result failures.
- `tools\atom\invoke.py` disables ambient custom instructions. A clone alone does not cause initialized module rules to reach reviewers.
- The Azure CLI is installed locally. Its actual `az rest --help` states that it authenticates with the logged-in credential and accepts an explicit `--resource`. No authentication or remote request was exercised.
- Synthetic local-Git tests verify checkout, merge-base selection, original-worktree preservation, and cleanup. They do not prove live ADO authentication or review quality.

Approved direction: the developer waived another checkout/diff spike and selected a native `atom review --pr` command rather than assistant-only orchestration.

Assumptions to validate through deterministic tests, not another throwaway POC:

- Normal non-shared HTTPS cloning and checkout are the appropriate Git operations. A real ADO checkout/authentication result is not yet claimed.
- Azure CLI Entra authentication can read PR metadata; Git uses its own existing HTTPS credentials. Neither login mechanism is supplied by the assistant's MCP connection.
- The initial native mode runs from the corresponding local Go module, so its relative path can select that same module in the clone without a new module-selection flag.

## Public surface

```text
# Run from the local Go module belonging to this PR's repository:
atom review --pr <ADO URL> [existing model/run/concurrency/output options]
```

`--pr` is mutually exclusive with `--working`, `--staged`, and `--branch`. The existing three modes retain their behavior and output. `--branch main` is not required or inferred: the target comes from ADO.

The new preparation boundary belongs in `tools\atom\pull_request.py`. Its only exported operation is the context manager below. The prepared value exposes `working_directory: Path`, `request: DiffRequest`, and immutable PR provenance (canonical URL, PR number, source/target branch names, source/target commit IDs, merge base, and repository-relative module path). The provenance value type is internal and has an explanatory docstring. No parallel review engine or diff parser is added.

```python
@dataclass(frozen=True)
class PreparedPullRequest:
    """Keep review inputs together for the lifetime of their owned checkout."""

    working_directory: Path
    request: DiffRequest
    provenance: _PullRequestProvenance


@contextmanager
def prepare_pull_request_review(
    pr_url: str,
    module_directory: Path,
    runner: CommandRunner,
) -> Iterator[PreparedPullRequest]:
    """Keep a disposable pinned PR checkout alive while the caller reviews it."""
```

`PreparedPullRequest` is the minimal returned concrete value described above, not a configurable checkout service. The CLI enters this context, calls existing `run_review` with its prepared directory/request and the existing options, then leaves the context before rendering a successful report. PR provenance is attached to `ReviewOutcome` through an optional default-absent field. Existing local reports remain identical; native PR reports add provenance and explicit scope limitations. There is no change to the findings schema.

## Read-only resolution and authentication

Accept HTTPS Azure DevOps Services browser links in these forms, including ordinary browser query/fragment suffixes:

- `https://dev.azure.com/<organization>/<project>/_git/<repository>/pullrequest/<positive-id>`
- `https://<organization>.visualstudio.com/<project>/_git/<repository>/pullrequest/<positive-id>`

Parse with standard-library URL handling. Support percent-encoded project/repository names; reject encoded path separators, control characters, malformed paths, embedded credentials, custom ports, non-HTTPS links and unrecognized hosts before any subprocess. Azure DevOps Server/on-premises URLs are not supported in this increment.

Request the documented PR metadata endpoint with core `az rest --method get --resource 499b84ac-1321-427f-aa17-267ca6975798 --url <constructed-api-url> --output json --only-show-errors`. Build the URL from validated components, not an arbitrary metadata-supplied endpoint. This needs Azure CLI plus an existing authorized login, but not the azure-devops extension or a new Python package. Never extract an access token, pass credentials in argv, install an extension, change account/configuration, or perform login automatically.

Validate the returned PR number, repository identity, active status, source/target branch refs, source commit ID, and HTTPS clone URL. Reject forks and missing/ambiguous required metadata visibly. Permit a clone URL's organization-label username only when it matches its organization and no password is present; it is not a credential. Canonicalize modern/legacy HTTPS forms for identity checks. Do not copy raw metadata into committed artifacts or errors.

Read the local Git root/origin and require that it identifies the same organization/project/repository. Locate the current Go module relative to that root. Missing `go.mod`, a different repository, unsupported SSH/local origin, or a path escaping the root is a visible preparation failure, not a guessed repository/module choice. Initialization is neither created nor overwritten by this increment; applying its rules remains the explicitly disclosed later work.

## Preparation and lifecycle

Create a fresh uniquely owned temporary directory. Clone the validated HTTPS remote normally with no checkout, no tags, no shallow/filter/shared/reference options and no original-repository alternates. Store `core.autocrlf=input` only in the disposable clone, preserving the earlier Windows line-ending choice without changing global or original configuration. Do not clone the local partial repository or retrieve individual objects through stdin.

Resolve fetched source and target branch refs to full commit IDs. Require the fetched source to match the metadata's source commit; a moved source is an error, not an automatic retry or a different PR version. Pin the fetched target commit, find a unique merge base, and check out the source detached. The target is the actual named PR branch at fetch time, not an assumed main and not an unrelated merge-preview commit. Later remote movement cannot change the clone's pinned report.

Before checks/models, require successful checkout and verify that tracked files are present and clean against HEAD. This is ordinary Git checkout verification, not a claim of raw byte equality for every tracked blob under all possible attributes/filters. Check command outcomes as well as exit codes; ownership/cleanup errors are never successful evidence.

Keep the clone for the entire existing check/model pipeline. Use `DiffRequest` with the pinned target as its base so `capture_diff` supplies the existing three-dot merge-base diff. Preserve repository-relative paths and all files in that diff; do not silently narrow it to the current module. PR mode reports that its Go checks cover the selected module; additional module checking remains out of scope.

All external commands use the injected `CommandRunner`, not shell interpolation. Metadata/ref/diff operations have 60-second command limits, clone/checkout have 300-second limits, and cleanup has a 30-second owned-worker limit. These are individual command limits, not a claimed end-to-end review SLA. Existing model/check limits remain unchanged. No automatic retries, blob hydration loop, Go setup/repair, hidden skip-toolchain fallback, push, vote, or comment operation is introduced.

Remove only the uniquely created owned directory in a `finally` path after success, preparation failure, review failure, timeout or interruption. Use a bounded Python cleanup worker through the existing runner; handle read-only Git files only inside that exact owned tree. A cleanup failure reports the retained path and remains nonzero. Preserve the original review/preparation failure alongside any cleanup failure rather than replacing it with success or suppressing it.

## Numbered behavior contract

1. `--pr` alone selects native PR review; no source, multiple sources, empty/malformed URL or invalid existing review settings return the established usage exit before remote/model work.
2. Both supported URL forms resolve to the same canonical request; unsafe or unsupported URLs start no subprocess.
3. Metadata uses one bounded read-only `az rest` request with the ADO resource ID; missing CLI/login, denied access, malformed JSON, mismatched identity, inactive PR, forks or incomplete required fields stop before clone/models with an operation-specific diagnostic.
4. Local root/origin/module selection must match the requested repository and remain inside its root; unsupported or ambiguous selection stops without modifying it.
5. Clone uses a fresh independent remote checkout, never a shared/local-object clone or a fetch into the original repository. Organization-only HTTPS userinfo is accepted; passwords are not.
6. Resolve full source/target/merge-base IDs, reject a moved source and ambiguous/missing merge base, and check out source detached. Fetch/checkout/verification failure prevents all checks/model calls.
7. Existing diff capture compares pinned target `...HEAD`; a fixture with unrelated target-only changes excludes them while retaining all PR changes. Test a target named something other than main.
8. Run existing checks/review in the corresponding cloned module and keep the checkout alive until all runs finish. Required checks still block models; `--skip-toolchain` remains an explicit user request, never a fallback.
9. Existing model/runs/concurrency/MCP-disable/output options reach the existing pipeline unchanged. Missing/failed/partial model behavior and findings exit semantics remain unchanged.
10. PR Markdown and JSON identify the URL, branch names, immutable pins, merge base and selected module/check scope. Both explicitly say initialized module rules and additional surrounding context are not yet applied. Local reports do not gain PR fields or warnings.
11. Success, setup/review failure, timeout and Ctrl-C all attempt bounded exact-owned-path cleanup. Cleanup failure is visible and nonzero, with the original failure retained when there is one; a success-shaped report is not emitted before cleanup succeeds.
12. A real local-Git integration fixture with dirty tracked, staged and untracked content proves the original HEAD/branch/index/worktree contents are unchanged and the owned checkout is gone. No test contacts ADO or invokes a real reviewer.

## Error handling and concurrency

Malformed source selection/URL/settings retain `EXIT_USAGE_ERROR`. Expected preparation, transport, checkout and cleanup failures raise an operation-specific `PullRequestReviewError` caught by the CLI and use `EXIT_CHECK_FAILED`. Existing `DiffUnavailable`, `ToolchainGateFailed`, `NoModelAvailable` and partial-review semantics are retained, including actual diagnostic details without credential-bearing URL/metadata dumps. Ctrl-C remains interruption, not a clean review; cleanup diagnostics are printed if interruption also prevents reclamation.

Preparation and cleanup are synchronous. No new threads, process pool, global configuration or writable module-level state. Each call owns a distinct temporary directory. Existing reviewer concurrency is unchanged and must complete inside the context. A prepared checkout is valid only inside its owning context and is not safe for external concurrent mutation; no caller may retain its path for later review.

The consumed `CommandRunner` remains the extension/test seam. Do not add an authentication-provider hierarchy or generic repository abstraction. A later phase can reuse the prepared context while adding explicitly tested rule/context delivery to `run_review`.

## Trade-offs and non-goals

- Choose core Azure CLI authentication over new SDK/PAT storage/custom credential plumbing. Cost: an authorized `az` login is required separately from working Git credentials; installation alone proves neither.
- Choose a full independent clone over shared clones, worktrees or manual missing-blob fetches. Cost: more transfer/storage in exchange for a simple ownership/object boundary.
- Keep native PR entry separate from automatic rule/context delivery; do not claim the latter is complete.
- Choose source pin mismatch rejection over retries or silently reviewing a moving source. Target provenance explicitly names the fetched target revision.
- Keep the existing review engine, instruction isolation and findings format. Do not claim initialization-aware/contextual review, repair target code, add multi-module checking, post comments, or run another representative proof/model batch under design approval.

## TDD obligations

Use Python/pytest because Atom's tooling is Python. Tests first: public CLI/source validation, metadata/command/error contracts, then lifecycle and review integration. Mock only external ADO/model boundaries. Use real synthetic local Git repositories for merge-base semantics and dirty-checkout preservation, with local fixture transport isolated to tests rather than relaxing production HTTPS validation.

Capture actual red/green/refactor command output in this increment's TDD log. Run the smallest combined relevant pytest selection; do not start with another spike, live PR checkout or live reviewer. Preserve pre-existing dirty files and tests. Update the existing README review section without replacing unrelated edits. Documentation/spec production here is not a claim that implementation or authentication passed.

## References

- [ADO Get Pull Request API](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/get-pull-request?view=azure-devops-rest-7.1)
- [Azure DevOps Entra resource ID](https://learn.microsoft.com/en-us/azure/devops/cli/entra-tokens?view=azure-devops)
- Local `az rest --help`, executed read-only on 2026-10-24, confirms logged-in credential handling and explicit resource/method/URL/output options.

## Approval and verification boundary

The native-entry contract was approved with an explicit waiver of another ordinary-checkout POC. Its deterministic tests do not establish live ADO access or model quality. See the [current verification](../verification.md) and [test map](test-spec.md).

## Implementation reconciliation

The implementation retains this contract. The Python contextmanager generator is annotated Iterator[PreparedPullRequest]; its decorator supplies the promised context-manager caller surface. PreparedPullRequest is immutable and ReviewOutcome adds an optional, default-absent provenance field; local reports keep their schema and values.

Cleanup launches the trusted absolute installed _checkout_cleanup.py file, not python -m atom from the developer module: a regression demonstrated that a local atom package could shadow the module launcher. This is a private launch correction, not a different public operation or new dependency. Cleanup diagnostics preserve the original exception type and details, and explicitly identify the retained path if cleanup itself is interrupted. Exact path absence is checked even after a zero cleanup-worker exit.

A synthetic real-Git fixture exercises both preparation/diff and the native CLI using a nested Go module, a non-main target, target-only changes, PR changes outside the module, and dirty staged/unstaged/untracked original contents. Only ADO, HTTPS fixture transport and model I/O are substituted. Synthetic verification does not establish live ADO authentication, target builds, or model-review quality.
