---
project: "review-toolchain-policy"
phase: "phase-01-exact-toolchain"
author: "Copilot"
date: "2026-10-30"
status: "approved"
poc_report: "../poc-report-local-executable.md"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](../publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# Phase 01 Design: Project-Scoped Exact Go Selection

## Purpose And Plan Mapping

Let a project declare the exact stable Go patch version for `atom review`. Its direct Go gates either use that installed distribution or stop with actionable evidence. Do not change user defaults, install a toolchain, silently upgrade or turn failed checks into successful reviews.

This is phase 01 of the accepted Atom v1.0 Improvement Plan: prove selection, specify persistence/precedence/PR behavior, implement isolated execution with provenance, then validate missing/incompatible/environment/platform cases. The full roadmap remains in the original checkout at `specs/atom-v1-improvements/phase-plan.md`; this branch contains focused feature artifacts. Phase 02's degraded-review continuation is excluded.

## Evidence Base

Approved evidence: [direct-local-executable POC report](../poc-report-local-executable.md). The [original trial](../poc-report.md) remains Inconclusive.

**Established before design:**

- Direct use of installed Go 1.26.9 with child GOTOOLCHAIN=local met all ten Windows cases. Six compatible combinations succeeded; four higher-minimum combinations rejected build/vet/test. All 56 commands completed: 44 zero exits and twelve expected nonzero rejections.
- Version/root/hash probes and compiled runtime assertions agreed on 1.26.9. Parent/default/input checks passed. The second parent-setting pass reused vet analysis; not every invocation demonstrated a fresh analyzer.
- Source inspection shows launch-module guidance is captured before PR preparation; build/test may delegate to Makefiles; formatting uses changed-file snapshots; process runners currently inherit the environment.
- The developer explicitly chose: "Direct Go gates first; explicitly reject pinned Makefile delegation". Preserve unpinned delegation.

**Still assumed, not POC results:**

- Discovery beyond the observed default Windows cache, error paths, other stable releases and native Linux/macOS behavior.
- Production environment plumbing, selected-distribution gofmt, race execution and integration with existing formatting/PR paths. The POC's Python wrapper is not the proposed production implementation.
- Config/CLI/report contracts below are proposed policy, not measured outcomes. Existing CI platforms offer future validation, not current evidence.
- Optional analyzer internals and arbitrary test subprocesses are not attested by selecting Go. This is not hermetic execution, distribution trust verification, dependency compatibility or full build reproducibility.

Decisions below reuse the demonstrated route or explicit developer intent, or are labelled proposed policy/implementation assumptions pending this gate and TDD.

## User Surface And Persistence

**Proposed policy:** add one optional field to existing module-root `.atom/config.json`:

```json
{
  "module_path": "example.com/service",
  "build_command": "go build ./...",
  "test_command": "go test ./...",
  "review_go_version": "1.26.9"
}
```

This illustrates an existing config, not an instruction to overwrite it. Preserve all other fields. No new setter command or automatic migration; `atom check`, onboarding and `atom poc` do not consume this review-specific field. Review without initialization remains supported.

Two optional `atom review` flags:

```text
atom review --working
atom review --working --go-version 1.26.9
atom review --working --go-executable "C:\Go1269\bin\go.exe"
atom review --pr ADO_URL --go-version 1.26.9 --go-executable "C:\Go1269\bin\go.exe"
```

These are Windows path examples; POSIX callers supply native `bin/go`. `--go-executable` is a local executable override, not a version policy or installer. It requires an effective configured/CLI version. Resolve relative executable paths from the launch directory once before PR preparation. Never store an absolute developer path in shared config.

Accept an exact stable Go 1.X.Y with X >= 21, without the `go` prefix, leading zeros, ranges, whitespace, `auto`, `local`, `+auto`, prereleases or development versions. This is the GOTOOLCHAIN-era surface; only 1.26.9 has been experimentally observed here. Other stable releases require actual-version verification.

Precedence: explicit CLI version > launch-module `review_go_version` > existing ambient behavior. Report the project version, if any, plus effective request/source so overrides are visible. No new Atom environment variable or inference from go.mod minimum/toolchain suggestions.

Use the existing Project/config reader on only the launch module's `.atom/config.json`. Missing file/field means no pin; null/empty/non-string fields are errors. Validate a present file even with a CLI override: unreadable/corrupt config is not silently treated as no pin. Review newly surfaces malformed present config, an intentional validation change. Do not search ancestors.

For `--pr`, freeze intent before preparation. Neither later edits to launch policy nor target checkout config replace that request. Review from an unrelated/no-policy directory requires `--go-version` or launching from the trusted target module. Testing a pin changed in a PR requires a deliberate CLI override. No configuration is written by review.

## Design Overview

```text
trusted launch config + explicit flags
                  |
         immutable version request
                  |
       existing PR preparation, if any
                  |
       skip / no-module / wrapper check
                  |
        bounded local candidate lookup
                  |
      version + environment + hash probes
                  |
   selected Go/gofmt runner for review gates
                  |
        final executable identity check
                  |
       existing required-gate decision
                  |
  base runner for models + selection evidence
```

Reuse existing process ownership, build detection, gates, formatting snapshots and review lifecycle. No tool manager or new orchestrator. Carry knowledge forward, not imports/copies of the disposable spike.

## Python Integration Contracts

This phase modifies Python tooling, not Go production APIs. Apply the Go-oriented template through Python contracts/docstrings. Keep new types in `atom.go_selection`, without package-level re-exports. This is the sole authoritative declaration block; bodies are deliberately omitted.

```python
@dataclass(frozen=True)
class GoToolchainRequest:
    """Keep launch intent independent of later checkout changes."""

    version: str
    source: Literal["cli", "project"]
    project_version: str | None = None
    executable: Path | None = None


def capture_go_toolchain_request(
    launch_directory: Path,
    *,
    version_override: str | None = None,
    executable_override: Path | None = None,
) -> GoToolchainRequest | None:
    """Freeze trusted policy without preparing a checkout or executing Go."""
    ...


def resolve_go_toolchain(
    request: GoToolchainRequest,
    runner: CommandRunner,
    working_directory: Path,
    *,
    environment: Mapping[str, str],
) -> GoToolchainSelection:
    """Verify a local distribution before pinned gates can use it."""
    ...


class CommandRunner(Protocol):
    """Keep process execution substitutable with isolated child settings."""

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300.0,
        stdin_text: str | None = None,
        *,
        environment: Mapping[str, str] | None = None,
    ) -> CommandResult:
        """Use inherited settings or a complete child-only environment."""
        ...
```

Extend the existing CommandRunner protocol, not a second protocol. None preserves existing inheritance/call shapes; a mapping is a complete child environment, not a delta. Copy on entry. Legacy callers do not receive the new keyword; production implementations and pinned-test collaborators must accept it.

Append only `go_toolchain_request: GoToolchainRequest | None = None` to `run_review`'s existing keyword-only parameters. Existing programmatic calls remain ambient: CLI captures config, not an implicit reread inside `run_review`. Programmatic callers may supply a captured request.

GoToolchainSelection is immutable evidence: request, verified/not-run status, selected source/path/root/version, initial/final Go hashes, gofmt path/hash when verified, not-run reason, discovery diagnostics, probe results and completed gate-command results. Use immutable tuples of existing CommandResult records; never serialize a complete environment or GOENV/config contents. Not-run selections have no observed version, executable or probes.

Add optional selection to ToolchainEvidence, default None. Add an optional keyword-only selection argument to ToolchainGateFailed, default None, to retain failed-gate version context without changing its category. Use focused GoToolchainConfigError and GoToolchainSelectionError exceptions, not a provider registry or generic exception hierarchy.

| Component | Responsibility | Location |
|---|---|---|
| GoToolchainRequest | Frozen launch intent | `tools/atom/go_selection.py` |
| GoToolchainSelection | Observed selection evidence | `tools/atom/go_selection.py` |
| Resolution functions | Bounded candidate verification | `tools/atom/go_selection.py` |
| Private selected-command adapter | Route gates through the verified distribution | `tools/atom/go_selection.py` |
| CommandRunner/SubprocessRunner | Owned execution with optional child environment | `tools/atom/runner.py` |
| Existing native owner | Preserve Windows owned-launch lifetime with that environment | `tools/atom/_windows_process.py` |
| CLI/review orchestration | Apply frozen intent only to review gates | Existing `cli.py`, `review.py` |
| Evidence/renderers | Disclose selection without relabelling results | Existing `toolchain.py`, `report.py` |

## Local Discovery And Execution

**Proposed bounded lookup, not exhaustive discovery:** an explicit executable is the sole candidate, with no fallback. Otherwise inspect in order, deduplicating canonical paths: the go executable currently resolvable on PATH; process GOROOT/bin; the user's SDK directory for the requested version; process GOMODCACHE; process GOPATH entries' pkg/mod directories, or default home/go/pkg/mod when GOPATH is unset. Cache candidates use the exact version and native host OS/architecture suffix, not a recursive scan. Automatic cache lookup initially maps Windows/Linux/macOS amd64/arm64; other layouts/architectures need an explicit path.

Distribution VERSION metadata is a filter, not version proof. Record and skip missing/mismatched automatic candidates without executing them. Retain unexpected read errors in diagnostics; if none qualifies, report attempted sources and the explicit-path remedy. Explicit-path errors fail immediately. Do not execute shell/download wrappers, invoke a generic launcher to obtain candidates, read user GOENV settings to expand discovery, search arbitrary directories or install anything. Persisted custom cache layouts absent from the process environment may need `--go-executable`.

Hash the first qualifying distribution's canonical executable. Directly run `version`, then `env -json GOVERSION GOROOT GOTOOLCHAIN GOENV`, each with a 60-second command deadline. Require the exact requested release, local mode and canonical GOROOT/bin/go identity/hash agreement. Real probe failure/mismatch stops; do not hide a broken candidate by trying another. Require the selected root's native gofmt before gates and record its hash; do not invent an independently measured formatter version.

Copy the parent environment; set GOTOOLCHAIN=local, remove inherited process GOROOT, prepend selected bin to PATH. Handle Windows environment keys case-insensitively so Path/PATH and root variants cannot conflict. Preserve GOENV policy: a persisted root override producing a mismatching observed root is an explicit failure, not permission to rewrite settings.

Preserve GOFLAGS, GOWORK, GOOS/GOARCH, CGO_ENABLED, proxy/checksum and other project settings. Do not import synthetic POC restrictions or override telemetry/debug settings. Standard dependency/cache activity retains existing behavior; the selected route prevents toolchain auto-switching/installation, not all network use.

Before probes, detect actual build/test commands. If either delegates to make, fail as unsupported pinned delegation: do not invoke make, silently substitute direct Go or change unpinned detection. Guard the adapter boundary too if later detection would delegate despite preflight. There is no promise to pin arbitrary recipes or test subprocesses.

For supported gates, replace leading literal go with the verified absolute executable and gofmt with the selected root's formatter. Retain arguments, stdin and gate deadlines. Optional analyzers receive the copied child environment for ordinary helper Go lookup; their own binaries/compiler internals are not attested. Git, binary-safe diff helpers, PR preparation and model invocation use the unmodified base runner. Preserve snapshot selection, nested-module exclusions and CRLF behavior.

After collection, recheck Go and used gofmt identities before models. Changed/missing identities invalidate the run. This before/after check is not an adversarial TOCTOU defense or distribution trust attestation.

Production environment plumbing uses subprocess.Popen's environment on POSIX and a correctly terminated Unicode environment block with CreateProcessW on Windows. Resolve executable names and missing-tool diagnostics against the effective child PATH/PATHEXT, not a different parent search path. Preserve suspended launch, restricted handle inheritance, private Job Object assignment before resume, cleanup outcomes and deadlines. No temporary os.environ mutation, shell wrapper or Python re-execution shim.

## Numbered Behaviour

1. Without an effective pin or config read error, commands, prompts, reports, Makefile delegation, fixed-evidence identity and library defaults remain unchanged; add no selection probe or selection report field.
2. Missing config is normal. Present unreadable/corrupt config or invalid review_go_version fails explicitly; only stable exact versions enter requests. Never derive a pin from module minimums/suggestions.
3. CLI version overrides project version for this run and records both. Write neither config nor Go settings. An executable override without an effective version is a usage error.
4. Freeze policy and resolve explicit relative executable paths before PR preparation. Later launch-file edits/checkout policy cannot change the request; read no ancestor config.
5. Explicit executable errors, unsupported layout, wrong version or failed probes stop without fallback, download or model calls.
6. Automatic discovery uses only the ordered bounded sources and retains failure diagnostics. A real probe failure is terminal even if later candidates exist.
7. Verify actual version, local mode, root and executable hash. Timeout, runner error, malformed environment output or mismatched identity cannot become verified selection.
8. Selected gate children use an isolated copied environment. Parent environment, GOENV file and project policy remain unchanged; preserve project flags/workspace/CGO/proxy/checksum settings.
9. Pinned Makefile delegation fails before recipes, Go probes or models. Unpinned delegation remains unchanged; do not substitute a different build to make the pin appear supported.
10. Direct build/vet/test/race use selected absolute Go; scoped formatting uses selected-root gofmt on the same snapshots/stdin with existing gate semantics.
11. Optional analyzers retain existing advisory/skipped semantics and receive selected environment, but their scope is environment-only, not independently pinned tool/compiler binaries.
12. Configured pin plus --skip-toolchain records requested intent as not_run with no observed version/probes. Explicit --go-version or --go-executable combined with --skip-toolchain is a usage error.
13. Outside a root Go module, preserve existing no-toolchain behavior and disclose any requested pin as not_run with that reason; no discovery, probes or exclusions.
14. Higher module/workspace minimums, source/race failures, missing required tools and unknown failures remain blocking. No compiler-text-based permission to continue; no models after required failure.
15. Retain argv/cwd, outcome, exit status, stdout/stderr and duration for probes/selected gate invocations. Do not serialize environment mappings, credential values or config/GOENV contents.
16. Identity changes after collection block models with before/after evidence; a successful earlier probe cannot conceal replacement/deletion.
17. Pinned successful or explicitly skipped selections appear consistently in Markdown/JSON/prompt. Skips never claim an actual version; unpinned payloads remain unchanged.
18. Required-gate failure diagnostics include selection context and existing compiler/test output. --json failure stdout remains unchanged (no successful outcome); stderr and existing failure code remain authoritative.
19. Environment plumbing preserves defaults, stdin, deadlines, ownership, Unicode, PATH lookup semantics and process cleanup on native Windows/POSIX. Concurrent base/model calls do not inherit another call's selection.
20. Unsupported layouts fail with an explicit-path remedy, never ambient-version fallback. Claim native platform support only after its real tests pass; Windows evidence alone cannot close Linux/macOS obligations.

## Evidence And Report Contract

**Proposed additive contract:** add optional toolchain.selection to review JSON schema version 2 only when a pin exists. Retain existing keys, gate meanings, model counts and exit codes. Omit it for legacy unpinned reviews; an opt-in optional field does not require a schema bump.

Selection fields: status (verified/not_run), requested_version, request_source (cli/project), project_version, selection_source (explicit/path/goroot/sdk/module_cache or null), executable, executable_sha256, executable_sha256_after, goroot, observed_version (canonical 1.X.Y), gofmt_executable, gofmt_sha256, gofmt_sha256_after, reason, discovery_diagnostics, probes and commands. The last three fields are arrays: diagnostic strings, probe records and gate-command records respectively. Each command record contains command (argv array), working_directory (string), outcome (existing enum value), exit_code, stdout, stderr and duration_seconds (rounded to three decimals). Not-run actual fields are null/empty, never requested values copied into observed fields.

Markdown/prompt state requested/observed version, override/source and direct-Go scope; actual argv is available in records. Label analyzer internals/arbitrary descendants outside the attestation. Keep existing exclusions tied to actual passing gates; missing/failed/skipped tools gain no exclusion. Local paths are operational evidence to review before public publication.

Selection/config failure fabricates no ReviewOutcome. Print reason, requested version, available candidate/probe context and remedy to stderr; use existing CLI failure constants. ToolchainGateFailed retains selection context without degraded-success semantics. Fixed-evidence review follows the same mechanical selection rules and frozen prompt bytes; model tool permissions do not change.

## Error Handling

| Condition | Observable behavior | Error / exit |
|---|---|---|
| Invalid explicit version/combination/library request | Name offending argument; no discovery/models | ValueError / EXIT_USAGE_ERROR |
| Corrupt/unreadable config or malformed project version | Name config/field; no no-pin fallback | GoToolchainConfigError / EXIT_CHECK_FAILED |
| No qualifying installed distribution | Show requested version/attempted sources; suggest installed direct executable | GoToolchainSelectionError, reason unavailable / EXIT_CHECK_FAILED |
| Candidate mismatch or malformed/failed probe | Preserve command results; no retries/fallback | GoToolchainSelectionError, reason verification_failed / EXIT_CHECK_FAILED |
| Probe timeout / ownership or cleanup failure | Preserve outcome/output; no models | GoToolchainSelectionError, reason execution_failed / EXIT_CHECK_FAILED |
| Pinned delegated build/test | Name detected command; explain unsupported scope, not a bypass | GoToolchainSelectionError, reason unsupported_wrapper / EXIT_CHECK_FAILED |
| Missing selected gofmt or changed identity | No ambient formatter fallback or verified report | GoToolchainSelectionError, reason verification_failed / EXIT_CHECK_FAILED |
| Required gate failure, including higher minimum | Existing blocking evidence with selection context | ToolchainGateFailed / EXIT_CHECK_FAILED |
| Optional analyzer absent/fails | Existing SKIPPED/WARNING evidence, accurately scoped | Existing advisory behavior |

Missing-version remedies never install automatically. A higher minimum may require a deliberate project/CLI version change, not automatic upgrade. No broad catch turns failed reads, probes or identity checks into success.

## Concurrency And Ownership

No new threads, tasks, native owner or global cache. Requests/published selection are immutable; copy environments per invocation, never install them into os.environ. The private adapter's temporary command log belongs to one sequential collection and is not safe for concurrent calls. Freeze it into tuples before concurrent model work; never share the adapter with models or another review.

Each runner invocation owns its environment and existing child/process-group or Job Object lifecycle. Preserve interrupt/cleanup behavior, not just exit codes. Native regression tests cover Unicode, absent overrides, timeout/descendant cleanup and concurrent calls with distinct overrides. No new lock is needed for review-local state; unrelated event-log locking is unchanged.

## Extension Points And Trade-offs

Reuse the consumer-defined CommandRunner seam with fakes at process/I/O boundaries. Candidate construction is a small ordered helper, not a provider/plugin framework. Future wrapper support needs wrapper evidence; installation needs a separate permission/policy design.

| Option | Chosen? | Basis |
|---|---|---|
| Optional review config + visible CLI override | Proposed | Existing storage, opt-in and explicit divergence |
| Infer exact version from minimum/suggestion | No | Not the selected product contract |
| Global changes or +auto | No | Violates unchanged-default intent / permits upgrade |
| Installed direct distribution + local selection | Yes | Demonstrated route with actual identity verification |
| Bounded common locations + explicit path | Proposed | Demonstrated cache route without exhaustive-discovery claims |
| Generic launcher/bootstrap/installer | No | Not established; no installation permission |
| Absolute developer path in shared config | No | Not portable project intent |
| Unverified pinned Makefile or silently bypassing it | No | Explicit developer boundary; would misrepresent the build |
| Production wrapper matching spike | No | Extend existing native owner, not another lifetime layer |
| Pin optional analyzer binaries or arbitrary descendants | No | Unestablished; disclose narrower scope |
| Continue after tooling failure | No | Separate phase 02 |

## Test Obligations And Release Evidence

After approval, derive a focused test-spec and implement test-first. Reuse runner, CLI/PR, review, toolchain output and formatting test files; add one go-selection test file for genuinely new resolution behavior. Do not copy the disposable driver into production/tests or test trivial constants/accessors.

- Exercise policy/precedence/path resolution and PR request freezing through CLI/review boundaries, with model stubs and no paid calls.
- Table-drive missing/wrong-version/malformed/timeout/identity-change, lookup order, wrappers, skips and source/minimum failures; independently assert zero model calls on blocking paths.
- Test real child isolation/Unicode and unchanged parent/settings alongside native ownership regressions, not only mocked process success.
- Use a small standard-library integration fixture with an already installed stable native Go distribution. Derive requested patch from that distribution; build/test runtime-version assertions and selected-gofmt routing. No tool acquisition/model APIs; owned temporary paths and offline test controls, not production-policy resets.
- Retain existing Windows/Linux/macOS CI, which already provisions Go 1.23. Use its actual installed patch for native integration. A missing prerequisite locally is explicitly unvalidated/skipped, not proof; native CI selection tests must run for each claimed platform. Do not automatically replay the archived budgeted POC.
- Preserve unpinned prompt/report identity and formatting/Makefile behavior; verify custom workspace/CGO/GOFLAGS settings are preserved, not that every such project becomes compatible.

Document the optional field, flag precedence, trusted-launch PR behavior, explicit-path remedy and wrapper/platform limits in existing review usage documentation and CLI help. Keep canonical/packaged copies consistent where that documentation is mirrored; do not broaden this change into unrelated command-example cleanup.

Atom is Python with no root Go module. Final source gate: `python -m pytest tests -v --cov=atom --cov-report=term-missing` from tools. Docs: `python tools/check_links.py`. Use narrower selectors in red/green. No new linter/type-check tooling. Root atom check failure/replacement rationale is in decisions; the old 1504-pass baseline is not new implementation evidence.

Design approval authorizes local TDD and bounded offline/stubbed validation, not public push, remote CI trigger, installation or paid models. Cross-platform evidence can come from existing CI after separately authorized publication. Until then disclose actual validated platforms and do not declare the broader phase outcome fully validated.

## Out Of Scope

Downloads/repair, exhaustive SDK-manager discovery, arbitrary Makefile/wrapper pinning, analyzer binary management, model-side toolchains, adversarial replacement defenses, global migration, changes to atom check/init/poc, degraded-review continuation, dependency compatibility promises, full reproducibility, visibility and publication.

## Design Checklist

- [x] Approved evidence linked; facts separated from assumptions.
- [x] Opt-in surface, precedence, PR trust boundary and non-migration specified.
- [x] Single authoritative Python contract block; review extension without duplicate signatures.
- [x] Numbered testable behaviors, explicit errors and blocking semantics.
- [x] Concurrency/native ownership, unsupported wrappers and validation obligations stated.
- [x] Rejected alternatives recorded.
- [x] Developer approved this exact design for TDD in conversation.

## Design Approval

The developer selected: "Approve this design for TDD". Approval covers this phase and its bounded local/stubbed validation, not publication, installation, paid model calls or unvalidated support claims.

SHA-256 of the presented design before this approval-only update: `81f8b1b55eba8e518ae118da41c2dd2efca758eb6e80dbc0f7a98d7fb95551d2`.

## Implementation Reconciliation

The approved public contract and all twenty behaviors are unchanged. Implementation uses the existing Project/config reader, gate collection and native owner, plus a private selected-command adapter and shared provenance text; it does not import the disposable driver.

Constructed library requests validate exact versions/source and require captured absolute executable paths. The selected adapter accepts the runner protocol's optional complete environment mapping, copies it per call and reapplies selected Go controls without mutating its default mapping. GoToolchainSelectionError can retain completed command/identity evidence when final checks invalidate a selection. These implement the existing input/isolation/error contracts, not new CLI policy.

The full Windows Python gate passed with 1614 passed, 5 skipped and 95% total coverage. A subsequent test-only refinement exercised real automatic PATH discovery as well as an explicit path, deriving and observing installed Go 1.27.0 at C:\Program Files\Go\bin\go.exe; its focused native case also passed. This is separate from the archived Go 1.26.9 POC. Production source did not change after the full gate.

Coverage is reconciled in [test-spec.md](test-spec.md), with complete raw output in [tdd-evidence.md](tdd-evidence.md). Native Linux/macOS, successful native race/CGO execution and real dependency compatibility are not established by this local synthetic fixture. The developer accepted the local TDD result; broader cross-platform completion remains pending actual native CI. No publication or paid review is authorized.
