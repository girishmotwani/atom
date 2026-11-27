# Review timeout investigation

Date: 2026-11-26. Scope: local diagnosis only, no new model requests, production
edits, timeout changes, settings changes, installation requests or publication.

## Established failure boundary

The 60-second failures are availability-probe failures, not review submissions.

- tools/atom/invoke.py:59 sets DEFAULT_PROBE_TIMEOUT_SECONDS to 60.0.
- tools/atom/invoke.py:187 builds a small copilot -p ping availability command.
- tools/atom/invoke.py:268 passes the 60-second deadline to the runner.
- tools/atom/invoke.py:321 filters out failed probes before planning review calls.
- DEFAULT_TIMEOUT_SECONDS at line 54 is 600.0 for actual review submissions.

The runtime imports Atom from Python site-packages, not this checkout. Direct
inspection verified that installed invoke.py matches checkout bytes, and the ASTs
of probe_command, probe_models, invoke_models and _explain match. The probe timeout
and filtering conclusion therefore applies to the actual launcher.

A 0/3 report for Claude/GPT does not mean three review requests timed out. Their
availability check failed, so zero review submissions for those models were
scheduled. Repeating runs cannot repair that prerequisite. The 119557-byte review
prompt is not the input to the failing ping probe.

## Startup evidence, not a fully isolated root cause

Existing local process logs were inspected selectively; no raw credentials,
account details, full logs or private model payloads are copied here.

Latest failed probe process log, basename process-1795688263128-58844.log:

- Line 2: the launched CLI distribution was 1.0.117-1.
- Lines 551-554 at 10:17:57 UTC: MCP root discovery and snapshot-cache misses
  for both configured custom servers, azure-mcp and azure-devops.
- Line 541 records a successful automatic binary update during this process.
- The process did not yield an available reviewer; the captured review report
  records a timeout at 60.155 seconds. No corresponding persisted child session
  event file was found; absence does not prove that no remote activity occurred.

The next probe process, process-1795688327072-46484.log:

- Line 2: the CLI distribution changed to 1.0.117-2.
- Lines 500/504: the same configured custom MCP servers were still discovered.
- Its persisted session events show Gemini selected at 10:18:48.340 UTC,
  the four-character ping user input at 10:19:25.092 UTC, and an assistant
  message at 10:19:27.549 UTC. Substantial startup precedes the small model call.

Both the failing and succeeding startup logs contain authentication/discovery
warnings; their presence alone does not establish a causal authentication fault.
CLI version drift also prevents treating these two launches as a controlled
comparison. No unsupported-model conclusion is justified for Claude by a timeout.

Fixed-evidence source exclusions remove tool visibility, not custom-server
startup. The probe disables built-in MCPs but has no named custom-server
exclusions unless the caller supplies them. CLI documentation confirms these
are distinct flags. Prior repository evidence in
specs/module-review-rules/poc-report.md records the same startup distinction:
a separately approved custom-server-excluded retry completed its probes, but
that older result is suggestive, not proof for the current CLI/model/account.

Earlier audit statements about no installations mean no deliberate agent
installation command was run. Existing CLI logs show that its own automatic
updater did modify the binary during the review. Future diagnostics should
explicitly control this side effect rather than claim startup is read-only.

## Installed runner drift

Installed runner.py and CLI code differ from this checkout; comparison shows
additional child-environment/Go-selection handling in checkout. Model invocation
uses the legacy inherited-environment path. No evidence currently attributes
the timeout to those differences; no package refresh was attempted.

A version-only command through the actual installed SubprocessRunner, with
updates disabled and a 15-second deadline, returned:

```text
outcome=completed
exit_code=0
stdout=GitHub Copilot CLI 1.0.117-2.
Run 'copilot update' to check for updates.
stderr=
```

This checks local process launch, not model availability or authentication.

## Deterministic validation

From tools, with fake runners only, no model requests:

```text
python -m pytest tests\test_invoke.py -q --tb=short -k 'fixed_probe_failure or failed_excluded_probe or excluded_probes_preserve_partial_review_reporting or no_review_call_happens_before_every_probe_has_run'
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\gimotwan\work\atom\tools
configfile: pyproject.toml
plugins: anyio-4.16.0, cov-7.1.0
collected 62 items / 57 deselected / 5 selected

tests\test_invoke.py .....                                               [100%]

====================== 5 passed, 57 deselected in 0.60s =======================
```

The staged tree remains 7ffadd8569dae01c69100e14d76fb71927375ef7.
No source, tests, timeout constants, installed packages or persistent settings
were edited by this investigation. Only diagnosis/audit artifacts are written.

## Recommended next evidence step

With separate consent, run one Claude ping through the same installed native
runner, keeping the 60-second deadline and tool exclusions, but explicitly
disabling the two configured custom MCP servers and automatic updates for that
child. Do not send the review diff or start review rounds. Preserve a safe
operational result; stop after this one probe regardless of outcome.

An exit-0 response would establish availability under that startup configuration,
not that the historical timeouts had a single cause or that review quality is
proven. An unavailable-model error would identify a separate selection problem.
Another timeout would leave startup/auth/network causes unresolved; do not
increase deadlines or retry automatically. Offline-only analysis remains the
alternative, but cannot establish current remote model availability.
## Isolated ping result on 2026-11-26

The single approved Claude ping completed successfully, exit 0 in 29.018 seconds,
with no stderr. Local session events confirm selected/responding model
claude-sonnet-5.5 and input ping. CLI version 1.0.117-2, both configured custom
MCP servers disabled and automatic updates disabled. See probe-isolated-result.md
for safe actual output and evidence limits. Availability in this configuration
is confirmed; the historical stall's individual cause is not. No additional
model request, full review, fix, timeout increase, source/settings change,
installation command or publication followed. The review requirement remains
unmet. Named MCP exclusions are supported by atom review, but it does not expose
forwarding --no-auto-update; a future plan must not silently equate these setups.
