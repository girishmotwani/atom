# POC Brief - Standalone Review Without Phase State

Date: 2026-11-08.
Status: proposed; execution awaits approval.
Scope: Phase 04 standalone review mechanics, independent of the paused setup trial.

## Question

Can the installed Atom review CLI select working, staged and branch changes in
local Go repositories without Atom or phase state, produce correctly scoped
reports, preserve source/state, and retain honest missing-module and failing-gate
behavior, with a deterministic reviewer transport instead of real model calls?

## Observed Evidence And Remaining Risk

The accepted roadmap explicitly requires standalone review without unrelated
pipeline state. The runtime `_run_review_command` selects the diff and optional
local review inputs without requesting registered phases. Reports go to stdout,
not an automatically created phase directory. `run_review` collects Go gates
before invoking reviewers; absence of `go.mod` is recorded as skipped evidence.

Existing `test_cli_review.py` tests use a scripted runner at the external-command
boundary. Fresh baseline command/output:

```text
python -m pytest tools\tests\test_cli_review.py -q --tb=short
============================= 76 passed in 4.42s ==============================
```

That supports existing argument/output contracts, not a real Git/Go fixture with
missing state. The installed CLI help confirms the real options are `--branch REF`
and repeated `--model NAME`; current skill examples instead use unsupported
`--base` and `--models`. Model identifiers in the CLI come from explicit options
or built-in defaults, not general model-role resolution from absent project state.
Keep these factual discrepancies for the subsequent approved guidance design.

Go preflight reports CGO_ENABLED=1 and an existing gcc command. This is prerequisite
availability, not proof that a real race gate passes. No tool installation is
recommended or authorized here.

## Recommended Evidence Step

Run one bounded deterministic composition trial. Reuse the existing CLI transport
fixture pattern, but execute actual local Git and Go commands. Intercept all
Copilot reviewer availability/review commands in the observer harness; return
explicitly synthetic event streams and log every interception. No Copilot process,
agent or model is launched, even for availability probing.

Use two named synthetic reviewer identities and one run each, concurrency 1.
They test extraction/deduplication/reporting, not independent reviewer quality.
The alternative is relying on existing tests and changing the guidance immediately;
that leaves the missing-state real-Git/Go boundary unobserved. A live reviewer trial
needs a separate later decision and budget; do not spend that budget here.

## Throwaway Harness And Fixtures

Because the integration being examined is Atom's Python CLI/runner boundary,
use a throwaway Python observer under `poc\atom-v1-standalone-review\`, not an
invented Go wrapper around Python. The actual fixtures are tiny Go modules and
exercise real Go build/vet/format/test/race behavior. This adaptation changes no
production code and is recorded explicitly in decisions.

After approval only, create a previously absent disposable root:

`C:\Users\gimotwan\AppData\Local\Temp\atom-phase04-standalone-review-20261108`

Create five independent local Git fixtures. Minimal standard-library library
source and meaningful tests, no network/dependencies, no Atom onboarding or
phase state. Fixture setup may run Git init/add/local commits with synthetic
per-command author identity; do not change global Git configuration, run hooks,
add remotes, fetch, push or publish. Include the usual Copilot co-author trailer
in fixture commit messages. Use an observer-owned preservation sentinel.

Before each review, snapshot module/source/test/sentinel contents and Git
refs/staged/worktree diff semantics. Verify no `.atom`, project `specs` or `poc`
appears afterward. Capture raw CLI stdout/stderr/exit status and every delegated
real command/result; archive reports outside the fixture through the artifact
writer. Git index timestamps and build caches are not a source-preservation claim.

## Cases

| Case | Review selection | Required evidence |
|---|---|---|
| Working changes | `--working`, JSON report, normal gates | Selected real Go diff; complete synthetic report; actual required gates pass; no Atom/phase files created |
| Staged changes | `--staged`, JSON report, normal gates | Only staged fixture changes; complete synthetic report; actual required gates pass; source/staging semantics preserved |
| Branch changes | `--branch main`, Markdown report, normal gates | Only committed branch changes relative to fixture main; correct report; actual required gates pass; no workflow/state adoption |
| Broken Go source | `--working`, normal gates | Nonzero review, explicit required gate failure, no report masquerading as clean and zero reviewer-transport calls |
| No root module | `--working`, JSON report, no go.mod | Runtime's actual skipped-toolchain reason is visible; no invented module/state or claimed clean Go gates; any synthetic review is clearly unverified tooling evidence |

Do not skip the normal gates in the three valid-module cases. If the existing
compiler/race prerequisites fail, stop and report Inconclusive rather than install
anything, suppress gates or redefine success. The broken-source case intentionally
expects the declared gate failure; it is not permission to repair the fixture.
The no-module case observes current behavior rather than prescribing automatic
setup or promoting missing evidence to a pass.

## Execution Limits

Use child-only GOTOOLCHAIN=local, GOPROXY=off and GOSUMDB=off. Bound child PATH to
already installed Git, Go, Python, gcc and required Windows directories. Exclude
optional analyzer locations so no vulnerability database or tool download is
introduced. Record advisory checks as absent/skipped, never passed. If an
unexpected optional analyzer is discoverable in that environment, stop before
running it rather than silently change measurement. Do not persist settings.

Ceiling: one harness execution, five review calls, at most 100 real child-command
executions, 180 seconds per child, approximately five minutes of local machine time.
Zero model calls, subagents, retries, installations or publication. If a timeout,
command budget exhaustion, unexpected mutation or measurement problem occurs,
stop, preserve fixtures and report Inconclusive. No process-tree cleanup guarantee.

Retain fixtures/evidence initially. Cleanup requires a separately scoped decision;
never recursively delete the Temp root or overwrite an existing target.

## Verdict And Approval

Confirmed only if all five declared observations hold and all reviewer calls are
proven synthetic interceptions. A contract contradiction is Refuted. Tooling or
observation gaps are Inconclusive. Report actual output and limits, not a fabricated
clean review or claimed model agreement.

Approval authorizes this mechanical trial only. It does not approve a standalone
review design/implementation, real reviewer calls, changes to the installed preview,
cleanup, shipping, or completion of Phase 04. If confirmed, present the report
before drafting the standalone guidance spec. Setup live evidence stays incomplete;
this independent trial is not a retry of the filtered setup session.
