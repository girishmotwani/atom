---
project: "atom-cli"
phase: "phase-05-ship"
date: "2026-09-19"
design_spec: "design-spec.md"
poc_report: "poc-report.md"
---

# Test Spec — Phase 5: `atom ship`

A test spec for Phase 5: the preconditions, phase resolution, fresh check
evidence, body assembly, and the create-or-update pull request path that make up
`atom ship`. It maps behaviours **B138–B157** (including **B145a**, **B147a**,
and **B147b**) to the named tests that pin them.

Unlike Phases 2–4 this document is written *before* the tests, not after. Atom
builds its tests from the spec during TDD, so the names below are the contract
the TDD cycle is expected to satisfy rather than a record of tests already green.
The value of the document is the same either way: it is what makes an unpinned
behaviour visible before the code exists, and it is where the honest statement
lives about which behaviours a green suite can never prove.

Phase 5 is almost entirely `git` and `gh` invocation. That is precisely the
surface every earlier phase's tests erased: Phase 1 shipped 55 green tests on a
package that would not build, Phase 2 shipped 169 green tests on a program that
raised `NameError` at import, and Phase 4 shipped a green suite of well over four
hundred tests while `atom review` could not produce a single review. The cause
was always the same — a test double has no PATH, no argv ceiling, and no stdin,
so mocking the operating system mocks the constraint away. This spec therefore
treats the fake-runner unit tests as necessary but not sufficient, and gives the
end-to-end section below equal standing with the behaviour tables.

**Suite command (once the tests exist):**

```
python -m pytest tools/tests --cov=atom --cov-report=term-missing -q
```

## Coverage Figures

Prospective, so these are targets for the TDD cycle rather than measured results.
They are stated in the shape the earlier phases reported so the gap between goal
and outcome is legible when the suite is run.

| Module | Target | Notes |
|---|---:|---|
| `ship.py` | 100% | New orchestrator: preconditions, phase resolution, push, fresh-check gating, and the create-or-update decision. The analogue of `review.py`. |
| body rendering | 100% | Summary-plus-links assembly (B148–B151). May live in `ship.py` or an added renderer beside `report.py`; the split is the implementer's to finalise, the behaviour is not. |
| `cli.py` | ≥90% | The `ship` subparser, flag validation, dispatch, and exit-code mapping. Only the Phase 5 paths are counted here. |
| `runner.py` | ≥95% | Reused from Phase 1; Phase 5 adds no new runner code but exercises its `stdin_text` and `TOOL_MISSING` paths against `gh`. |
| **Total** | **≥96%** | Consistent with the Phase 4 baseline. A number below this is a signal to inspect, not to lower the target. |

## Test doubles

The unit tests drive `ship` through a fake `CommandRunner` in the established
house style — a scripted runner keyed on **what each command is**, not on the
order the calls arrive in, so a test does not silently pass when the pipeline
reorders its calls. The fake answers three families of command:

- **`gh`** — presence/verification, existing-PR queries, and `pr create` /
  `pr edit`. It records every argv and every `stdin_text` it is handed.
- **`git`** — branch name, working-tree status, upstream, `rev-parse HEAD`, the
  commit log, and `push`.
- **the check gates** — `atom check` runs through the same runner, so a fake
  gate result drives B146 and B147 without a Go toolchain.

> **One part of the check cannot be faked, and an implementer will hit it in the
> first cycle.** `run_check` validates `go.mod` **on the real filesystem, before
> any gate runs**, so whether the gates are reached at all is a property of the
> test directory rather than of the fake runner. A test for B147 (a failing gate
> refuses) must use a `tmp_path` that really contains a `go.mod`, or the gates
> never run and the test proves B145a by accident. A test for B145a must use one
> that really does not. The two are pinned from opposite ends by a file on disk,
> and no scripted runner response can substitute for it.

Because the fake has no PATH, no argv ceiling, and no real `gh`, several
behaviours below are marked as only *partly* pinned by these tests. Those are
carried into the end-to-end and manual sections rather than being claimed as
covered. Exact flag spellings (for example whether the upstream query is
`git rev-parse --abbrev-ref --symbolic-full-name @{u}`) are the implementation's
to finalise; the tests assert the **invariant** — a SHA is used, `--body` is
absent — not a brittle full argv.

---

## Coverage Summary

### Preconditions (B138–B142)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B138 | `gh` is located and verified before anything else runs; its absence is an unmet precondition, not a failure partway through. | `test_a_missing_gh_is_an_unmet_precondition_not_a_late_failure`; `test_gh_is_verified_before_any_git_work_begins`; `test_the_missing_gh_message_names_the_install` |
| B139 | Ship refuses a detached `HEAD`, and refuses when the current branch is the base branch itself. | `test_a_detached_head_has_nothing_to_ship_from`; `test_shipping_the_base_branch_itself_is_refused` |
| B140 | Ship refuses on a dirty working tree, listing the modified files. | `test_a_dirty_working_tree_is_refused`; `test_the_dirty_tree_refusal_lists_the_modified_files`; `test_a_clean_tree_is_allowed_to_proceed` |
| B141 | Ship requires an upstream; without one and without `--push` it refuses and prints the exact command that fixes it. | `test_a_branch_with_no_upstream_and_no_push_is_refused`; `test_the_missing_upstream_refusal_prints_the_command_that_fixes_it` |
| B142 | With `--push`, ship pushes the branch itself and sets the upstream; it never delegates the push to `gh`. | `test_the_push_flag_pushes_the_branch_and_sets_the_upstream`; `test_the_push_is_a_git_command_never_gh` |

### Resolving the phase (B143–B144)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B143 | The phase directory is derived from the branch name; `--phase` overrides it; a path that does not exist is refused, naming the path tried. | `test_the_phase_directory_is_derived_from_the_branch_name`; `test_the_phase_flag_overrides_the_branch_derivation`; `test_a_missing_phase_directory_is_refused_naming_the_path_it_tried` |
| B144 | Artifacts are whatever files the directory holds; a missing artifact is omitted, never invented and never described as pending. | `test_the_artifacts_are_the_files_the_phase_directory_holds`; `test_a_missing_artifact_is_omitted_rather_than_described_as_pending` |

### Fresh check evidence (B145, B145a, B146, B147, B147a, B147b)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B145 | `atom check` runs fresh, at ship time; a recorded result from an earlier run is not accepted. | `test_the_check_runs_fresh_as_part_of_ship`; `test_a_recorded_check_result_is_not_accepted` |
| B145a | A tree that is not a Go module skips the gates and records "not a Go module; no gates run"; this is not a check failure, does not trigger B147, and requires no override. | `test_a_tree_with_no_go_module_skips_the_gates`; `test_the_absent_module_is_recorded_as_an_absence_not_a_failure`; `test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal`; `test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag`; `test_the_evidence_section_states_the_absence_rather_than_omitting_it` |
| B146 | The body carries a verdict table, one row per gate, bounded at five rows, without the gates' full output; when B145a applies the table is replaced by the single recorded line — not dropped. | `test_the_body_carries_one_verdict_row_per_gate`; `test_the_verdict_table_is_bounded_at_five_rows`; `test_the_body_does_not_embed_the_gates_full_output`; `test_when_there_is_no_module_the_table_is_replaced_by_the_recorded_line`; `test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty` |
| B147 | A failing fresh check refuses to open or update the PR, naming the failing gates; `--allow-failing-checks` overrides it; the no-module skip is not a loophole for a real failure. | `test_a_failing_check_refuses_to_open_or_update_the_pr`; `test_the_check_refusal_names_the_failing_gates`; `test_allow_failing_checks_overrides_the_refusal`; `test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent` |
| B147a | When overridden, the failure is stated plainly in the body; the override changes whether the PR opens, never what it claims. | `test_an_overridden_run_states_the_failure_in_the_body`; `test_an_overridden_body_never_asserts_green_while_red` |
| B147b | When overridden, ship still exits non-zero. | `test_an_overridden_run_still_exits_non_zero` |

### The body (B148–B151)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B148 | The body is summary plus links, assembled from title, why, what changed, evidence, and artifacts; it never embeds an artifact's content. | `test_the_body_is_summary_plus_links`; `test_the_body_never_embeds_an_artifacts_content`; `test_the_body_title_comes_from_the_design_specs_h1`; `test_the_body_quotes_the_design_specs_purpose_paragraph`; `test_what_changed_lists_the_commit_subjects_on_the_branch` |
| B149 | Artifact links point at the pushed commit SHA, never a branch name and never the base branch; and the push precedes body assembly so the remote already holds that commit. | `test_artifact_links_point_at_the_pushed_commit_sha`; `test_no_artifact_link_uses_a_branch_name`; `test_no_artifact_link_points_at_the_base_branch`; `test_the_push_happens_before_the_body_is_assembled` |
| B150 | The body file is written with explicit `newline="\n"`, and any size reported to the developer is the character count, not the file size. | `test_the_body_file_contains_no_carriage_return`; `test_the_reported_size_is_the_character_count_not_the_byte_count` |
| B151 | The body reaches `gh` by `--body-file`, never `--body`. | `test_the_body_travels_by_body_file`; `test_the_body_flag_never_appears_in_the_argv` |

### Creating and updating (B152–B155)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B152 | Ship queries for an existing PR before attempting to create one, and treats `gh`'s duplicate error as a fallback rather than the primary signal. | `test_an_existing_pr_is_queried_before_any_create`; `test_the_duplicate_error_is_treated_as_a_fallback_not_the_primary_signal` |
| B153 | Re-running on a branch that already has a PR updates the body rather than failing. | `test_re_running_on_a_branch_with_a_pr_updates_the_body`; `test_re_running_is_not_treated_as_an_error` |
| B154 | `gh`'s own error text is passed through verbatim, not paraphrased. | `test_ghs_error_text_is_passed_through_verbatim` |
| B155 | Empty stdin is passed to every `gh` call. | `test_every_gh_call_receives_empty_stdin` |

### Failure handling and exit codes (B156–B157)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B156 | Ship reuses the Phase 1–3 exit-code scheme; an unmet precondition exits by the same route as any other failure, with no distinct precondition code. | `test_ship_reuses_the_phase_one_to_three_exit_codes`; `test_an_unmet_precondition_exits_by_the_ordinary_failure_route`; `test_there_is_no_distinct_precondition_exit_code` |
| B157 | Ship never creates a commit. | `test_ship_never_issues_a_commit`; `test_no_git_commit_command_is_ever_run` |

The subtle behaviours deserve a word on *how* the assertion is framed, because a
loosely written test here would pass on a broken program exactly as the earlier
phases did.

- **B149 — the SHA.** `test_artifact_links_point_at_the_pushed_commit_sha`
  scripts the fake `git rev-parse HEAD` to return a known forty-character SHA and
  asserts that string appears in every artifact link, while
  `test_no_artifact_link_uses_a_branch_name` asserts the branch name does *not*.
  A link to `main` or to the branch is a 404 until merge; proving a SHA is used
  is the whole point, so the test pins the SHA rather than merely checking that a
  link exists.
- **B149 — the order.** `test_the_push_happens_before_the_body_is_assembled`
  reads the fake runner's recorded call sequence and asserts the `git push`
  appears before the SHA is resolved and the body written. Order is behaviour,
  not an implementation detail: assembling first would produce a PR whose every
  link was broken until the moment it wasn't.
- **B150 — no carriage return.** `test_the_body_file_contains_no_carriage_return`
  writes a multi-line body and reads the file back **as bytes**, asserting no
  `\r` is present. The companion test asserts the reported size equals
  `len(body_text)`, not the on-disk byte count, because the POC measured 70,000
  characters becoming 71,228 bytes on Windows and any accounting that confuses
  the two is wrong by about two percent.
- **B151 — never `--body`.** `test_the_body_flag_never_appears_in_the_argv`
  asserts the literal token `--body` is absent from every recorded `gh` argv,
  not merely that `--body-file` is present. The two can coexist in a naive
  refactor; the constraint is that arguments have a launcher-dependent ceiling
  and the body must not travel through it.
- **B147/B147a/B147b — the override.** These are pinned as three separate
  facts because the design keeps them separate: the override changes whether the
  PR opens (B147), never what the body claims (B147a), and never the exit code
  (B147b). A single test asserting "override works" would let two of the three
  regress unnoticed.
- **B145a versus B147 — absence is not failure.** This is the distinction most
  likely to be mis-implemented, because `check.py` reaches both outcomes through
  the same `run_check` call: a directory with no `go.mod` raises
  `NotAGoModuleError` *before* any gate runs, while a real module with a broken
  gate returns a report whose `passed` is false. The tests pin the two apart from
  both ends. `test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal`
  and `test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag` prove the
  no-module path ships cleanly with no override, and
  `test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent`
  proves the failing-gate path still refuses — so B145a cannot become a loophole
  that swallows a genuine failure. Atom's own repository has no `go.mod` anywhere,
  so without B145a `atom ship` could not open this phase's own pull request;
  without the B147 counter-test, the fix for that could silently disarm the
  refusal that is the whole point of running a fresh check.
- **B145a versus a silently missing section — absence must be stated.** An empty
  evidence section and a section that says "not a Go module; no gates run" are
  different outcomes, and only the second is honest.
  `test_the_evidence_section_states_the_absence_rather_than_omitting_it` and
  `test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty`
  assert the recorded line is *present*, not that the table is merely absent — a
  body that drops the evidence section entirely would read as though evidence were
  never expected, which is the quiet omission Atom exists to prevent.

---

## Program-level tests

Unit tests demonstrate the code is correct. They do not demonstrate the
*program* runs — the recurring failure of this project. The new subcommand
therefore carries subprocess tests that invoke `python -m atom.cli` for real, on
paths that need neither the network nor `gh` to be authenticated. These live in
`test_cli_ship.py`.

| Test | What it proves that an in-process test cannot |
|---|---|
| `test_the_module_can_be_executed` | The package starts outside the test harness. |
| `test_ship_appears_in_the_top_level_help` | The command is wired into the top-level parser. |
| `test_ship_help_runs_without_error` | The ship subparser starts and exposes its contract, including `--push`, `--phase`, `--title`, and `--allow-failing-checks`. |
| `test_ship_in_a_non_repo_directory_exits_and_explains` | A precondition failure survives the process boundary as a clean non-zero exit with a message, not a traceback — regardless of whether `gh` happens to be installed on the CI runner. |
| `test_a_refused_setting_does_not_produce_a_traceback` | Refused flags are developer errors, not crashes. |
| `test_nothing_is_defined_below_the_main_guard` | The Phase 2 startup failure cannot reappear by appending code below `if __name__ == "__main__":`. |

These do not call `gh` and do not reach GitHub. The gap that leaves is stated
plainly below rather than papered over.

---

## End-to-end verification that does not use a fake runner

This is the section the project's history demands, and it is not optional. Every
behaviour above is pinned by a fake `CommandRunner`, and a fake runner is exactly
the instrument that let three earlier phases ship green over a broken program. A
fake has no PATH, so it cannot prove `gh` is findable; no argv ceiling, so it
cannot prove a large `--body` would fail where a `--body-file` succeeds; no real
filesystem round-trip to GitHub, so it cannot prove the character-versus-byte
accounting; and no real `gh`, so it cannot prove create, update, or the error
text the design promises to pass through. Being honest about that is worth more
than a coverage number.

The verification is therefore split into two tiers.

### Tier 1 — real `git` in a throwaway repository (runs in CI)

These tests, in `test_ship_end_to_end.py`, use a **real `git` binary** against a
temporary repository built under `tmp_path`, with a local bare repository standing
in for the remote. No network, no `gh`, no GitHub account. They exercise the git
half of ship against the same constraint a developer's machine imposes, which the
fake runner cannot reproduce.

| Test | Behaviour | What the real binary proves that the fake cannot |
|---|---|---|
| `test_a_real_dirty_tree_is_detected` | B140 | The dirty-tree check reads real `git status --porcelain` output, not a scripted string, so a wrong flag or a porcelain-format assumption is caught. |
| `test_a_real_detached_head_is_refused` | B139 | Detached `HEAD` is detected from a genuine checkout of a commit, not a fabricated branch name. |
| `test_a_real_branch_without_an_upstream_is_refused` | B141 | The upstream query is proven against a branch that genuinely has no upstream configured. |
| `test_push_to_a_local_bare_remote_sets_the_upstream` | B142 | `--push` actually moves a commit into a real remote and sets tracking; afterward the bare repo contains the commit. This is provable locally; the true GitHub push is not (see Tier 2). |
| `test_the_link_sha_matches_git_rev_parse_head` | B149 | The SHA embedded in the links equals the real `git rev-parse HEAD`, and that commit is present in the bare remote — the link would resolve. |
| `test_the_body_file_written_to_disk_has_no_carriage_return` | B150 | The body file on a real filesystem contains no `\r`, proving the explicit `newline="\n"` on the platform where text mode would otherwise inflate it. |
| `test_no_commit_is_created_in_a_real_repo` | B157 | The commit count and `HEAD` are unchanged across a full ship run against a real repository — ship assembles from commits, it does not make them. |
| `test_a_real_directory_without_a_go_module_skips_the_gates` | B145a | Against a real `tmp_path` holding no `go.mod`, the check step records the absence and no gate command is ever issued to the runner — proving the skip is reached the way `check.py` actually reaches it, not by a scripted stand-in. This needs no Go toolchain because `NotAGoModuleError` is raised before any gate runs, and it is the path Atom's own `go.mod`-free repository takes. |

Tier 1 is the load-bearing evidence for the git-facing behaviours. Where a
behaviour is pinned both by a fake-runner unit test and by a Tier-1 test, the
Tier-1 test is the one that would have caught the failures this project keeps
shipping.

### Tier 2 — the real `gh` path (manual / integration; cannot run in CI)

The following require an authenticated `gh`, a real GitHub repository, and a
branch pushed to it. They cannot run in CI, must not be faked, and are recorded
here as a checklist to be run by hand — the same discipline the POC used when it
ran its spike in a throwaway worktree and read the body back rather than trusting
exit code 0.

1. **`gh` is present and launchable (B138).** On a machine without the Copilot
   app's bundled copy, confirm ship reports the missing-`gh` precondition and
   names the install. The unit test proves the *branch* fires when the fake says
   `gh` is missing; only a real machine proves whether `gh` is actually on PATH.
2. **A large `--body-file` succeeds where a large `--body` would not (B151, C10).**
   Ship a phase whose assembled body exceeds 32 KB and confirm `gh` accepts it.
   The unit test proves `--body` is absent from the argv; only a real launch
   proves the ceiling that makes that choice necessary — a 64 KB `--body` raises
   `WinError 206` before the process starts.
3. **The stored body matches what was written (B150, C11, D13).** Read the body
   back with `gh pr view` and confirm no truncation and no surprise inflation on
   the wire. The POC saw 70,000 characters stored as 71,228; the true cap above
   71,228 remains unmeasured (D13) and is deliberately not blocked on.
4. **Create then update on the same branch (B152, B153).** Run ship twice.
   Confirm the first opens a PR and the second updates its body rather than
   failing, and that the existing-PR query — not the duplicate error — is what
   drove the update.
5. **Verbatim error text (B154).** Trigger the unauthenticated path and confirm
   `gh`'s own `HTTP 401` / `gh auth login -h github.com` message reaches the
   developer unparaphrased.
6. **Empty stdin against real `gh` (B155).** Confirm ship does not hang. The POC
   refuted the hang hypothesis, so this is defence in depth; a fake cannot prove
   the absence of a hang because it never opens a pipe.

### Behaviours that cannot be proven by unit tests alone

Stated plainly, so no one reads a green suite as more than it is:

- **B138** — that a *real* `gh` is on PATH and launchable. A fake has no PATH.
  Unit tests prove only the precondition branch; Tier 2 step 1 is the real proof.
- **B151 / C10** — that a large `--body-file` launches where a large `--body`
  raises `WinError 206`. The fake has no argv ceiling, and Tier 1's real `git`
  does not exercise `gh`. Only Tier 2 step 2 proves the constraint that the whole
  behaviour exists to satisfy.
- **B150 / C11** — beyond the local "no `\r` on disk" proof (Tier 1), the
  character-versus-byte behaviour of the GitHub round-trip is measurable only
  against real GitHub (Tier 2 step 3).
- **B152, B153, B154** — real `gh` create, update, and error passthrough. Unit
  tests prove the *decision logic* against canned stderr; that `gh` genuinely
  emits those messages and behaves as measured is Tier 2 only.
- **B155 / C16** — that empty stdin prevents a real hang. Unprovable by a fake
  that never opens a pipe, and already refuted as a risk by the POC; carried as
  defence in depth.

The remaining behaviours — B139–B147b, B148, B149, B156, B157 — are provable by
the combination of fake-runner unit tests and Tier-1 real-`git` tests, because
their logic lives in Atom's own code and the check runs in-process. They do not
depend on the real `gh` path.

---

## Gaps

Recorded here rather than quietly omitted, on the Phase 4 precedent.

| Area | Why not tested by unit tests | Mitigation |
|---|---|---|
| Real `gh` create/update/auth (B138, B152–B154) | Calling live `gh` needs authentication, a real repository, and network; it would make the suite slow, flaky, and account-dependent. | Tier 2 manual checklist above; the decision logic is unit-tested against canned `gh` output, and the POC preserved raw `gh` responses as a regression corpus. |
| The real argv ceiling (B151, D15) | A fake runner has no launcher and no OS limit; Tier-1 `git` does not exercise `gh`. | Tier 2 step 2 on Windows; `--body-file` sidesteps the limit on every platform, so D15 is a portability question, not a correctness one. |
| The true body cap above 71,228 chars (D13) | The documented 65,536 was not enforced and finding the real ceiling needs a bisection nobody currently needs. | B148 makes the body small by construction, so the cap stops being load-bearing. |
| Non-Windows launcher limits (D15) | The launcher finding is Windows-measured; the suite does not reproduce it on Unix. | The implementation uses `--body-file` regardless of platform; D15 remains an open portability note. |
| Phase 1's bootstrap debt (D16) | Out of this phase's scope by the design spec. | Handled by checking out Phase 1's end commit and running `atom review` there; needs no ship code. |

## Open notes

- **The module split for body rendering is undetermined by the design spec.** It
  says the body is "summary plus links" and fixes the parts and their order, but
  it does not say whether assembly lives in `ship.py` or in a renderer beside
  `report.py`. The test names above target the behaviour, not the file; the split
  is the implementer's to choose during TDD.
- **The exact `git` and `gh` flag spellings are not fixed by the design spec.**
  The tests assert invariants — a SHA rather than a branch name, `--body-file`
  rather than `--body`, empty stdin on every `gh` call — and deliberately avoid
  pinning a full argv, so a legitimate change of flags does not force a test
  rewrite while a regression in the invariant still fails loudly.
