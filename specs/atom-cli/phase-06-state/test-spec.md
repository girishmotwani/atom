---
project: "atom-cli"
phase: "phase-06-state"
date: "2026-09-23"
design_spec: "design-spec.md"
poc_report: "poc-report.md"
---

# Test Spec — Phase 6: `state`, derived

A test spec for Phase 6: deriving the current phase from the repository,
reporting artifact presence without judging completeness, reducing
`.atom/state.json` to configuration and approvals, and rewriting `atom status`
against all of it. It maps behaviours **B158–B185** to the named tests that pin
them.

Like Phase 5, this document is written *before* the tests. The names below are
the contract the TDD cycle must satisfy, not a record of tests already green.

**This phase has an unusual hazard, and the spec is shaped around it.** The
behaviour Phase 6 must preserve is a *refusal to do something*. Atom must not
report completeness, must not count sections, must not read mtime. A refusal
has no output to assert on, and a test suite that simply omits the forbidden
behaviour passes identically whether the prohibition is honoured or forgotten.

Phase 5 taught this the hard way: all 83 ship tests passed **identically**
before and after the check/push ordering was reversed, because nothing asserted
the order. An ordering that nothing asserts is free to regress. A *prohibition*
that nothing asserts is in exactly the same position — worse, in fact, because
the tempting implementation is the one the POC already proved wrong.

So the three central tests of this phase are adversarial. They construct the
input that would fool the wrong implementation and assert Atom is not fooled:

| Guard | Constructs | Asserts |
|---|---|---|
| **The truncation guard** | the POC's V1: a real 13-section spec cut to its first 4 sections | reported **present**, and no output anywhere claims completeness |
| **The mtime guard** | a new artifact written into an *old* phase directory | the current phase does **not** change |
| **The thin-document guard** | a genuine 2-section `tdd-log.md` | reported **present** — the structural rules rejected this real document |

Each is derived from a measurement in [`poc-report.md`](poc-report.md), not from
imagination. If any of the three is deleted, the implementation it guards can
regress to the intuitive-and-wrong design with a fully green suite.

**Suite command:**

```
python -m pytest tools/tests --cov=atom --cov-report=term-missing -q
```

## Coverage Figures

Prospective; targets for the TDD cycle rather than measured results.

| Module | Target | Notes |
|---|---:|---|
| `phases.py` (new) | 100% | Phase discovery, lexical ordering, branch resolution, artifact presence, frontmatter status parsing. The whole derivation engine. |
| `status.py` | 100% | Rewritten against derivation. Report assembly and problem collection. |
| `state.py` | 100% | Reduced to configuration and the approvals record. Much smaller than the 92 statements it holds today. |
| `render.py` | ≥95% | Text and JSON renderings, including the one-line per-phase summary (B178). |
| `cli.py` | ≥90% | Phase 6 paths only: `status` dispatch, flag handling, exit-code mapping. |
| **Total** | **≥96%** | The Phase 4/5 baseline. Below this is a signal to inspect, not to lower the target. |

A caution carried forward from five phases: these numbers measure how much code
ran, not whether the program works. Phase 4 reached 97% while `atom review`
could not produce a single review. The end-to-end section below has equal
standing with the tables.

## Test doubles

Phase 6 touches two external surfaces, and they get different treatment.

**The filesystem is real.** Every test builds an actual directory tree under
`pytest`'s `tmp_path` — real directories, real files, real bytes. There is no
fake filesystem, because the thing under test *is* the filesystem's shape, and
a double would let the test assert the tree it imagined rather than the tree
git would produce. This is cheap here in a way it was not in Phases 1–5, where
the external surface was a network call.

A `phase_tree` fixture builds a repository-shaped `specs/<project>/` tree from
a compact description, so a test can say "phases 1 through 3, phase 1's POC
skipped, phase 3 missing its tdd-log" without fifteen lines of setup.

**Git is faked, narrowly.** The only git fact Phase 6 needs is the current
branch name. It is read through the established `CommandRunner` seam so a test
can present `phase-04-review`, `main`, a detached `HEAD`, or a failure. Two
tests in the end-to-end tier use a real `git` in a throwaway repository, because
a fake runner cannot tell us what a real detached HEAD prints.

**Following the Phase 5 rule: patch one level *below* the wiring, never at it.**
The CLI tests patch the status-collection entry point and leave argument parsing
and exit-code mapping real. Re-introducing the Phase 5 `default_gates` typo
failed 16 of 18 CLI tests, and the only two that passed were the two `--help`
tests — `--help` never reaches the command function, so it proves nothing.

## Coverage Summary

| Group | Behaviours | Cases |
|---|---|---:|
| Resolving the current phase | B158–B164 | 30 |
| Artifact presence | B165–B171 | 32 |
| The approvals record | B172–B176 | 19 |
| Output | B177–B181 | 22 |
| What is removed | B182–B185 | 8 |
| **Behaviour tests** | **B158–B185** | **111** |
| Program-level (real subprocess) | — | 5 |
| End-to-end tier 1 (real repository) | — | 5 |
| End-to-end tier 2 (real `git`) | — | 3 |
| **Total** | | **121** |

These counts are recounted from the tables below rather than estimated, and the
arithmetic is checked: the five behaviour groups plus the thirteen end-to-end
and program-level cases account for all 118 uniquely named tests in this
document, with none left over.

### Resolving the current phase (B158–B164)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B158 | A phase directory matches `^phase-(\d{2})-([a-z0-9-]+)$`; the anchors stop a stray folder masquerading as one. | `test_a_well_formed_phase_directory_is_recognised`; `test_a_single_digit_phase_number_is_not_a_phase_directory`; `test_an_uppercase_slug_is_not_a_phase_directory`; `test_a_directory_merely_containing_a_phase_name_is_not_one`; `test_a_file_named_like_a_phase_directory_is_not_one` |
| B158a | The project directory is the immediate subdirectory of `specs/` holding at least one phase directory: none means no phases rather than an error, and more than one is reported by name with the lexically first used. | `test_a_specs_directory_without_a_project_reports_no_phases`; `test_more_than_one_project_directory_is_reported_and_the_first_used`; `test_the_real_repository_resolves_to_the_atom_cli_project` |
| B159 | Non-matching directories are ignored silently — a non-match is not a problem to report. | `test_a_non_phase_directory_is_ignored`; `test_a_non_phase_directory_produces_no_problem`; `test_the_phase_plan_document_beside_the_phases_is_not_a_phase` |
| B160 | Phases are ordered lexically on the full directory name; mtime is never read. | `test_phases_are_ordered_lexically`; `test_the_two_digit_prefix_makes_lexical_order_numeric`; `test_phase_ten_sorts_after_phase_nine` |
| B161 | A branch matching the phase pattern names the current phase. | `test_a_phase_branch_names_the_current_phase`; `test_the_branch_wins_over_the_lexically_greatest_phase` |
| B162 | Otherwise the current phase is the lexically greatest phase directory. | `test_main_falls_back_to_the_lexically_greatest_phase`; `test_a_detached_head_falls_back_to_the_lexically_greatest_phase`; `test_an_unrelated_branch_name_falls_back`; `test_a_branch_that_cannot_be_read_falls_back` |
| B163 | A branch naming a phase with no directory is still the current phase, marked not started, all artifacts absent — not an error. | `test_a_branch_naming_a_missing_phase_directory_is_still_current`; `test_a_phase_with_no_directory_is_marked_not_started`; `test_a_phase_with_no_directory_reports_every_artifact_absent`; `test_a_phase_with_no_directory_is_not_an_error` |
| B164 | No phase directories and no matching branch means no current phase — reported, not an error. | `test_a_project_with_no_phases_has_no_current_phase`; `test_a_project_with_no_phases_is_not_an_error`; `test_an_absent_specs_directory_is_not_a_crash` |

**The mtime guard** lives here, pinning B160 against the measurement in F6-3:

| Guard | Test(s) |
|---|---|
| Writing a new artifact into an old phase must not make it current | `test_creating_an_artifact_in_an_old_phase_does_not_make_it_current`; `test_editing_an_artifact_in_an_old_phase_does_not_make_it_current`; `test_the_current_phase_is_stable_when_every_directory_is_touched_in_reverse_order` |

The third case is the decisive one. It `touch`es every phase directory in
reverse order — newest-first becomes oldest-last — and asserts the answer is
unchanged. Under a lexical implementation it passes trivially. Under an mtime
implementation it fails, because the ordering has been deliberately inverted.
That is what makes it a guard rather than a restatement.

### Artifact presence (B165–B171)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B165 | The required set is exactly the seven measured artifact names. | `test_the_required_artifacts_are_the_seven_named`; `test_an_unexpected_file_in_a_phase_directory_is_not_required`; `test_an_unexpected_file_does_not_appear_in_the_artifact_report` |
| B166 | Each artifact is reported present or absent; there is no third state. | `test_an_existing_artifact_is_present`; `test_a_missing_artifact_is_absent`; `test_an_empty_artifact_file_is_still_present`; `test_a_directory_named_like_an_artifact_is_not_present`; `test_the_artifact_report_has_exactly_two_states` |
| B167 | Atom never reads an artifact's size, sections, headings, or content to judge it. | `test_a_one_byte_artifact_is_present`; `test_a_document_with_no_headings_is_present`; `test_a_document_of_only_headings_is_present`; `test_no_artifact_but_the_poc_report_is_ever_opened` |
| B168 | `poc-brief.md` is required only when `poc-report.md` declares `status: "ran"`; only an explicit `skipped` excuses it. | `test_a_ran_poc_requires_a_brief`; `test_a_skipped_poc_does_not_require_a_brief`; `test_a_skipped_phase_with_no_brief_is_complete`; `test_a_skipped_phase_requires_the_other_six`; `test_a_phase_with_no_poc_report_still_requires_the_brief` |
| B169 | An unrecognised `status:` is a problem, and the brief is treated as required. | `test_an_unrecognised_status_is_reported_as_a_problem`; `test_an_unrecognised_status_still_requires_the_brief`; `test_a_missing_status_field_is_reported_and_requires_the_brief`; `test_the_unrecognised_status_problem_names_the_value_it_found` |
| B170 | An absent `poc-report.md` leaves the question unanswerable: both it and the brief are absent, with no extra problem. | `test_an_absent_poc_report_makes_both_it_and_the_brief_absent`; `test_an_absent_poc_report_raises_no_problem_beyond_the_absences` |
| B171 | The vocabulary is closed and matched exactly, never by substring. | `test_the_status_vocabulary_is_exactly_two_tokens`; `test_a_status_containing_skipped_as_a_substring_is_not_skipped`; `test_the_prose_status_values_this_repo_used_before_are_not_accepted`; `test_status_matching_is_case_sensitive` |

**The truncation guard and the thin-document guard** live here. They are the
most important tests in the phase:

| Guard | Test(s) |
|---|---|
| A 13-section spec cut to 4 sections is reported present, never complete | `test_a_truncated_design_spec_is_reported_present`; `test_no_rendering_describes_any_artifact_as_complete`; `test_the_report_exposes_no_completeness_field` |
| A genuine 2-section document is reported present | `test_a_two_section_tdd_log_is_present`; `test_the_real_phase_one_tdd_log_is_present` |

`test_no_rendering_describes_any_artifact_as_complete` is the phase's
prohibition test, and it is written to be hard to satisfy accidentally. It
renders both text and JSON for a tree of deliberately stubbed artifacts and
asserts the output contains none of `complete`, `valid`, `sufficient`, `done`,
`finished`, or `ok` as a description of an artifact. A future contributor who
adds a helpful-looking "✓ complete" column fails this test, which is the entire
point — the POC proved that column cannot be computed, and nothing in the code
itself will remind anyone of that.

`test_the_real_phase_one_tdd_log_is_present` reads the **actual** file from
this repository rather than a fixture. It is the document the POC's structural
rules rejected. Pointing a test at the real artifact means the guard cannot
drift away from the thing it was built to protect.

### The approvals record (B172–B176)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B172 | `.atom/state.json` holds version and approvals — no phase, no status, and no `module_path`, which stays in `config.json` per Phase 3's B73. | `test_the_state_file_holds_configuration_and_approvals`; `test_the_state_file_has_no_phase_field`; `test_the_state_file_has_no_status_field`; `test_an_approval_records_phase_gate_and_date`; `test_the_module_path_stays_in_config_not_state` |
| B173 | The file is committed, not ignored. | `test_the_state_file_is_not_gitignored`; `test_the_gitignore_no_longer_lists_the_state_file` |
| B174 | An absent state file is not an error; the phase and artifact report is produced in full. | `test_an_absent_state_file_is_not_an_error`; `test_an_absent_state_file_still_reports_the_phase`; `test_an_absent_state_file_still_reports_every_artifact`; `test_an_absent_state_file_reports_no_approvals` |
| B175 | A corrupt state file is a problem, and the report is still produced in full. | `test_a_corrupt_state_file_is_reported_as_a_problem`; `test_a_corrupt_state_file_still_reports_the_phase`; `test_a_corrupt_state_file_still_reports_every_artifact`; `test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem` |
| B176 | `atom init` writes `config.json` with the `module_path` and a `state.json` with an empty approvals list; it no longer writes a phase or status. | `test_init_writes_the_module_path`; `test_init_writes_an_empty_approvals_list`; `test_init_writes_no_phase_or_status`; `test_init_records_an_event` |

B174 and B175 are the phase's reason for existing, expressed as tests. Both
assert the *full* report survives — not that an error is handled, but that the
question is still answered. Today, with the state file absent, `atom status`
answers nothing at all.

`test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem` exists because
of a lie this project has already been told: `[1, 2, 3]` is valid JSON and
invalid state. Parsing successfully is not the same as being usable.

### Output (B177–B181)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B177 | Text reports root, current phase, how it was resolved, the artifact table, and any approval. | `test_the_text_rendering_names_the_project_root`; `test_the_text_rendering_names_the_current_phase`; `test_the_text_rendering_says_the_phase_came_from_the_branch`; `test_the_text_rendering_says_the_phase_came_from_the_fallback`; `test_the_text_rendering_lists_every_required_artifact`; `test_the_text_rendering_shows_a_recorded_approval` |
| B178 | Every other phase gets one summary line with present-of-required counts. | `test_every_other_phase_gets_one_summary_line`; `test_the_summary_line_reports_present_over_required`; `test_a_skipped_poc_phase_summarises_out_of_six`; `test_the_current_phase_is_not_repeated_in_the_summary`; `test_the_summary_is_ordered_lexically` |
| B179 | JSON carries the full contract including a `phases` array covering every phase. | `test_the_json_contract_has_the_documented_keys`; `test_the_json_phases_array_covers_every_phase`; `test_the_json_phases_array_includes_the_current_phase`; `test_the_json_artifact_map_is_name_to_boolean`; `test_the_json_is_parseable_when_problems_exist` |
| B180 | Every problem is reported, not just the first. | `test_two_problems_are_both_reported`; `test_a_problem_does_not_suppress_the_rest_of_the_report` |
| B181 | Exit 0 whenever Atom could answer; non-zero reserved for an unreadable project root. | `test_a_phase_missing_artifacts_exits_zero`; `test_a_project_with_no_phases_exits_zero`; `test_a_corrupt_state_file_exits_zero`; `test_an_unreadable_project_root_exits_non_zero` |

`test_a_skipped_poc_phase_summarises_out_of_six` is a small test carrying a
disproportionate amount of the design. Phase 1 must read `6/6`, not `6/7` and
not `7/7`. It is the only place the conditional artifact rule and the output
layer meet, and getting it wrong would make a correct project look incomplete
forever.

`test_the_json_is_parseable_when_problems_exist` preserves an existing
guarantee from `status.py`: a caller who asked for JSON gets parseable output
even when the answer is bad news. A traceback on stderr and nothing on stdout
would make the failure invisible to exactly the caller most likely to be
automated.

### What is removed (B182–B185)

| Behaviour | One-line description | Test(s) pinning it |
|---|---|---|
| B182 | The `Phase` and `Status` enums, `phase_index`, `next_phase`, and `InvalidTransition` are gone. | `test_the_state_module_exposes_no_phase_enum`; `test_the_state_module_exposes_no_status_enum`; `test_the_state_module_exposes_no_transition_machinery` |
| B183 | `ProjectState` is an approvals-shaped record. | `test_project_state_carries_configuration_and_approvals`; `test_project_state_carries_no_phase` |
| B184 | `status.py` is rewritten against derivation; the sweep (B81/B82) and report-everything (B93) survive. | `test_the_temp_file_sweep_still_runs`; `test_the_sweep_is_still_reported_never_silent` |
| B185 | Tests for removed behaviour are deleted, not skipped or weakened. | `test_no_test_in_the_suite_is_skipped` |

`test_no_test_in_the_suite_is_skipped` is a deliberate tripwire. The easy way
to "keep the suite green" while deleting a state machine is to mark its tests
`@pytest.mark.skip` and move on, leaving a suite that reports success while
measuring less than it claims. This asserts the count of skipped tests is zero,
so the shortcut is a failure rather than a quiet erosion.

## Program-level tests

Unit tests over a fake runner have now failed to catch a broken program in
**five consecutive phases**. Phase 1 shipped 55 green tests on a package that
would not build. Phase 2, 169 green with a `NameError` at import. Phase 4, 482
green while `atom review` could not produce a review. Phase 5, 595 green *and*
a clean `atom ship --help`, and the command crashed on first real use with
`TypeError: default_gates() got an unexpected keyword argument`.

So these tests invoke the real CLI in a subprocess:

| Test | What it proves that a unit test cannot |
|---|---|
| `test_the_atom_package_imports_cleanly` | no `NameError` or circular import at module load |
| `test_status_runs_as_a_subprocess_and_exits_zero` | argparse actually reaches the command function |
| `test_status_json_output_is_parseable_from_a_subprocess` | the JSON path survives real stdout encoding |
| `test_status_runs_in_a_directory_that_is_not_a_project` | the no-phases path does not crash outside a project |
| `test_status_runs_with_no_state_file_present` | the phase's central claim, end to end |

`--help` is **not** among them. It is not a smoke test: argparse short-circuits
before the command function, which is why the Phase 5 typo survived a clean
`--help` and 595 green tests.

## End-to-end verification that does not use a fake runner

### Tier 1 — the real repository (runs in CI)

Atom's own `specs/` tree is the best test fixture this phase will ever have:
six phases, one with a deliberately skipped POC, one in progress, built by
hand over six phases without any of this code existing.

| Test | Asserts |
|---|---|
| `test_the_real_repository_resolves_six_phases` | discovery against real directories |
| `test_the_real_repository_orders_phases_one_through_six` | lexical order on real names |
| `test_phases_one_through_five_have_every_required_artifact` | the conditional rule scores real history correctly |
| `test_the_real_phase_one_is_complete_despite_having_no_brief` | the skip rule, against the real skip |
| `test_the_real_phase_six_is_missing_exactly_its_unwritten_artifacts` | absence is reported truthfully |

These are regression tests against reality. If someone later tightens the rules
into the shape the POC refuted, this repository stops scoring correctly and
these fail — which is precisely how the mistake should surface.

### Tier 2 — real `git` in a throwaway repository (runs in CI)

| Test | Asserts |
|---|---|
| `test_a_real_detached_head_falls_back_to_lexical` | what a real detached `HEAD` reports, not what a fake says it does |
| `test_a_real_phase_branch_resolves_to_its_directory` | real `git branch --show-current` output, including its trailing newline |
| `test_a_real_clone_preserves_phase_ordering` | the F6-3 measurement, pinned: clone and re-derive |

### Behaviours that cannot be proven by unit tests alone

Stated plainly, because a green suite will otherwise be read as proving more
than it does:

- **B173** — that `.atom/state.json` is *actually committed* is a property of
  git and this repository's `.gitignore`, not of any Python function.
  `test_the_state_file_is_not_gitignored` shells out to `git check-ignore`,
  which is real evidence; but only an actual commit proves the end state.
- **B177/B178 readability.** Tests can assert the summary line contains the
  right counts. Whether the output is *usable* is a judgement, and the
  developer gate is where it gets made — after running the command for real.
- **The prohibition in B167** is asserted over the outputs Atom produces today.
  A future rendering path that no test covers could reintroduce a completeness
  claim without failing anything. This is an inherent limit of testing a
  negative, and it is why the rule is also written into the design spec's
  *Scope* as an explicit out.

## Gaps

- **No test pins the *reason* a phase resolved when both rules agree.** If the
  branch names the lexically greatest phase — the common case — branch
  resolution and fallback produce identical answers, so a bug swapping their
  precedence is invisible. `test_the_branch_wins_over_the_lexically_greatest_phase`
  deliberately constructs disagreement, which is the only configuration where
  the precedence is observable. Worth remembering that the common case proves
  nothing here.
- **Multi-project repositories are untested**, matching the design spec's
  explicit out. `specs/<project>/` implies more than one project could exist;
  nothing here says what `status` should do about that.
- **The approvals array has no concurrency story.** Two developers approving
  gates on separate branches will conflict in git. No test covers it because no
  behaviour specifies it.

## Open notes

- The `phases.py` module name is the implementer's to confirm; the behaviours
  are not. Derivation does not belong in `state.py`, which is now about
  declarations — keeping the derived and the declared in separate modules is
  the point of the phase made structural.
- Case counts above are recounted from the tables, not estimated — but they are
  still counts of *planned* tests, and Phase 5 showed these drift during TDD for
  a reason worth naming: B145a received 11 tests while B154, B155 and B147b
  received one each — a distribution that reflected how hard a follow-up prompt
  pushed, not the relative importance of the behaviours. If the counts drift
  again, check whether the *thin* behaviours are thin because they are simple or
  because nobody pushed on them.
