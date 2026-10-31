---
project: "review-toolchain-policy"
phase: "phase-01-exact-toolchain"
design_spec: "design-spec.md"
date: "2026-10-30"
status: "windows-local-gate-accepted"
---

> **Sanitized publication copy.** Local profile, worktree/session and temporary prefixes are replaced with labelled placeholders. Untouched original bytes are retained outside Git; see [publication evidence](../publication-evidence.md) for original and publication hashes. Output is otherwise unchanged. Historical gate limits describe their original approval scope; current review/publication authorization is recorded separately.

# Phase 01 Test Spec

Approved contract: [design](design-spec.md). Python names and pytest replace the
Go-oriented template. This map was created before implementation and is now
reconciled to actual test names. Complete observed loop output and final results
belong in [TDD evidence](tdd-evidence.md).

## Toolchain Redundancy Audit

None: no proposed behavior case was unfailable. No new tests assert dataclass
assignments, enum constants, Python argument binding or Go compiler type checks.
JSON null, empty and wrong-type values are real runtime policy inputs.

| Silent failure | Coverage |
|---|---|
| Empty/invalid values | Project/CLI version and invalid library request tables |
| Ignored failures | Actual probe outcomes, candidate/config read errors and failed required gates |
| Non-exhaustive outcomes | Nonzero, timeout, missing-tool and runner-error cases |
| Null/malformed output | Environment JSON null/list/missing/wrong-type fields |
| Typed Go nil / bounded overflow | Not applicable: Python orchestration without bounded arithmetic |

## Reconciled Behavior Coverage

Selection tests live in `tools/tests/test_go_selection.py`; review integration in
`test_review_toolchain.py`; CLI/PR boundaries in `test_cli_review.py` and
`test_cli_pr_review.py`; native plumbing in `test_runner.py` and
`test_windows_process.py`.

| Design # | Actual tests / retained regressions | Evidence |
|---|---|---|
| 1 | test_unconfigured_review_preserves_legacy_evidence; existing prompt/report, formatting and buildsystem tests | Preservation |
| 2 | test_capture_project_version; test_invalid_project_version; test_config_read_errors; test_unreadable_config_does_not_become_unconfigured; test_no_implicit_or_ancestor_policy | RED/GREEN plus read-error preservation |
| 3 | test_cli_override_records_project_version; test_executable_requires_version; test_review_cli_version_and_executable_override; test_invalid_library_request_is_rejected | RED/GREEN |
| 4 | test_request_freezes_relative_path_and_policy; test_pr_freezes_launch_toolchain_request | RED/GREEN capture, then real PR-boundary preservation |
| 5 | test_explicit_candidate_never_falls_back; test_invalid_go_policy_fails_before_runner_commands | RED/GREEN and CLI preservation |
| 6 | test_bounded_discovery_order; test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics | RED/GREEN |
| 7 | test_resolve_verifies_actual_distribution; test_probe_failure_cannot_verify; test_different_observed_root_is_rejected_even_when_binary_identity_matches | RED/GREEN, including subsequent author-found root-alias regression |
| 8 | test_selected_environment_preserves_project_settings; test_selected_runner_keeps_optional_child_mapping_isolated; native installed-distribution and runner child-environment tests | RED/GREEN plus native regression |
| 9 | test_pinned_makefile_stops_before_probes; test_pinned_runner_refuses_delegation_added_after_preflight; existing unpinned buildsystem tests | RED/GREEN and preservation |
| 10 | test_pinned_review_uses_selected_gates; test_native_installed_distribution_runtime_formatter_and_minimum; unchanged formatting snapshot/CRLF/nested-module tests | RED/GREEN and native regression |
| 11 | test_advisory_commands_receive_environment_only_scope | Existing advisory semantics through selected adapter |
| 12 | test_unexecuted_pin_retains_intent_without_observations; test_explicit_go_options_conflict_with_skip_toolchain; test_review_cli_captures_project_toolchain_policy | RED/GREEN |
| 13 | test_unexecuted_pin_retains_intent_without_observations; explicit CLI outside-module case | RED/GREEN |
| 14 | test_pinned_gate_failure_retains_selection_and_blocks_models; native installed-distribution higher-minimum rejection | RED/GREEN and native regression |
| 15 | test_pinned_evidence_is_consistent_across_outputs; test_pinned_review_uses_selected_gates | Actual command records and non-serialization of environment values |
| 16 | test_changed_selected_identity_blocks_models | RED/GREEN, Go/gofmt replacement and deletion |
| 17 | test_pinned_evidence_is_consistent_across_outputs; test_unconfigured_review_preserves_legacy_evidence | RED/GREEN and byte/field preservation regressions |
| 18 | test_toolchain_setup_failures_are_stderr_only; test_invalid_go_policy_fails_before_runner_commands | RED/GREEN and actual capture validation |
| 19 | Runner environment copy/empty/Unicode/concurrency/PATH/PATHEXT/relative/absolute/timeout tests; existing Windows ownership suite; test_posix_launch_errors_are_failed_command_evidence | Native Windows RED/GREEN; POSIX fault classification is not native POSIX proof |
| 20 | test_discovery_unavailable_does_not_use_ambient; test_unsupported_host_mapping_requires_an_inspectable_installed_path; native installed-distribution integration | Explicit remedy and bounded lookup; native Linux/macOS pending CI |

## Fixtures And Test Boundaries

Policy tests use real owned config files and the existing Project reader.
Distribution-shaped byte fixtures fake process results only: they are never
executed. Probe tables assert actual version/root/mode/lifecycle failures rather
than treating VERSION metadata as proof. Automatic probe failure is terminal even
when another candidate exists; prior candidate diagnostics remain visible.

Review tests reuse actual gate collection and changed-file formatter snapshots.
Models are stubbed. Build/test Makefile cases use real detection and a fake
availability boundary; a file introduced during the environment probe verifies
the second adapter guard. The original fixture also scripts ambient commands so
an ignored pin reaches the intended routing assertion rather than a missing fake.

Required-failure cases retain version and raw output while independently asserting
zero model calls. Changed/deleted Go and used gofmt identities retain before/after
evidence and block models. Advisory warning/skipped/passed semantics are unchanged.

CLI tests exercise real parsing and request capture. The PR test freezes intent,
mutates launch and target policies during actual fake-checkout preparation, then
stops at a recording review boundary without models. An initially unpinned launch
remains unpinned; a target policy cannot introduce a pin. Existing CLI fake runner
signatures are unchanged when no pin is supplied.

## Native Evidence And Limits

The installed-distribution test reads the already installed PATH distribution's
VERSION, then verifies explicit-path and native automatic PATH selection with actual probes. Real build/vet/test
commands run in an owned standard-library module with a tagged runtime.Version
assertion. Real selected-root gofmt consumes stdin. A higher module minimum must
fail under local selection. Parent settings, the supplied environment and an
owned GOENV file must remain byte-for-byte unchanged.

The fixture explicitly isolates workspace/proxy/checksum/CGO settings to avoid
downloads or requiring a C compiler; production does not impose these resets.
This fixture does not establish successful native race/CGO execution or real
dependency compatibility. Selected race routing and blocking failures are covered
at the review boundary. The earlier approved POC supplies separate workspace
minimum evidence and is not replayed.

Runner tests execute native Windows child processes with Unicode, stdin, distinct
concurrent mappings, empty mappings, child PATH/PATHEXT and relative lookup, and
timeout/descendant cleanup. Existing owned-launch fault/interrupt tests remain.
POSIX launch error classification is fault-injected locally; native Linux/macOS
execution remains an explicit CI obligation, not a local result.

Existing CI supplies native Go. The installed-distribution test fails if CI lacks
that prerequisite instead of silently claiming platform verification. No tool
acquisition, paid model call or archived spike replay is part of these tests.

## Loop And Validation Protocol

New code follows observed assertion RED, minimum GREEN and verified REFACTOR.
Missing parser/signature scaffolding is followed by a real forwarding/isolation
assertion failure. Existing behavior and native integration can pass immediately:
they are preservation evidence, not fabricated new REDs.

The optional child-map test initially leaked a KeyError from its assertion; using
get preserves the exact expected value and yields the intended clean ignored-map
failure before production implementation. The failed selector referencing a
nonexistent report test file collected nothing; its corrected command is retained.
These corrections are recorded in decisions.

Full source gate from `tools`: `python -m pytest tests -v --cov=atom
--cov-report=term-missing`. Documentation gate: `python tools/check_links.py`.
No new lint/type-check tooling is introduced. Coverage is inspected for meaningful
behavior gaps, not optimized through trivial tests.

- [x] All twenty behaviors mapped before production changes.
- [x] Actual test names reconciled without weakening assertions.
- [x] New behavior RED/GREEN and preservation/native evidence distinguished.
- [x] Native Windows evidence distinguished from pending Linux/macOS CI.
- [x] Full final validation completed and captured in the TDD evidence artifact.
- [x] Local implementation gate explicitly accepted by the developer; subsequent cross-platform CI results are recorded below.

## Current Verification Status

The complete final local gate passed 1615 tests, with 5 skipped, 95% coverage.
The earlier native handle failure is preserved, not claimed fixed.
CI run 41194476670 passed Linux CLI/POC/docs but failed macOS/Windows CLI suites;
see [findings](../findings.md). Only evidence/status prose is consolidated here:
all twenty behavior-to-test rows and actual source/tests are unchanged.
