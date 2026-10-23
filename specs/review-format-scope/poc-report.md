---
project: "review-format-scope"
phase: "n/a"
date: "2026-10-22"
verdict: "Confirmed"
status: "accepted-under-scoped-waiver"
---

# POC Report: changed-file formatting for review

## The Question

Can one selected working, staged or branch diff supply only its changed, surviving Go-file snapshots to a read-only formatting check, so untouched formatting defects do not block review while genuine formatting failures in the selected files still do?

## Verdict

**Confirmed for the approved fixed synthetic cases.** Fourteen observations matched their preregistered expectations in one attempt. The actual path/content hashes passed to gofmt agreed with independent fixture expectations. The original and clean tooling checkout audits matched, and the exact owned fixture directory was removed.

This does not prove the broader ADO workflow, an existing PR's correctness, or general review reliability. The earlier project-level Inconclusive result is unchanged.

## Executed command and evidence

The approved Python exception was used, with a process-local import path pointing to the clean reviewed phase 1 helpers at a90fbe1bb44ffa3bc1b1e9866b4078be1948cf0c:

```text
python poc\review-format-scope\spike.py --scratch <new-session-owned-fixture-directory>
```

The command exited 0. Verbatim combined stdout/stderr (the private scratch argument alone is abstracted in the command above; the output below is unchanged):

```text
experiment=changed_file_formatting fixed_fixture_set=true model_calls=0
tooling_revision=a90fbe1bb44ffa3bc1b1e9866b4078be1948cf0c
case=clean-working-ignores-untouched status=passed inputs=1 exact_input_match=true
case=clean-staged-ignores-untouched status=passed inputs=1 exact_input_match=true
case=clean-branch-ignores-untouched status=passed inputs=1 exact_input_match=true
case=bad-changed-file status=failed inputs=1 exact_input_match=true
case=staged-bad-working-clean status=failed inputs=1 exact_input_match=true
case=staged-clean-working-bad status=passed inputs=1 exact_input_match=true
case=added-file status=passed inputs=1 exact_input_match=true
case=pure-rename status=passed inputs=1 exact_input_match=true
case=deleted-file status=skipped inputs=0 exact_input_match=true
case=unicode-space-and-module-prefix status=passed inputs=1 exact_input_match=true
case=no-surviving-go status=skipped inputs=0 exact_input_match=true
case=git-error status=blocked exact_error_preserved=true
case=formatter-syntax-error status=error inputs=1 exact_input_match=true
case=standalone-control status=failed untouched_defect_detected=true
original_checkout_unchanged=true
tooling_checkout_unchanged=true
fixture_removed=true
cases_completed=14 elapsed_seconds=11.03387909999583
verdict=Confirmed reason=all fixed fixture expectations met
```

As-run generic spike SHA-256: `fe87433d3bcb4f4d5c4a6b8ad501d9bd46682761e08eeb6084c2f066c3241c48`. The fixed fixture set was not rerun or repaired after execution. Before the attempt, authoring checks established valid Python syntax, real Unicode fixture names and explicit LF writes on Windows; those were setup checks, not failed or hidden experiment runs.

Publication archive SHA-256 for `poc/review-format-scope/spike.py`: `9d99d7808ae06a1b0121c37ec4900947cc4c78ea3745c903ed4d28d2c7a02e6d`. The artifact-copy pipeline appended exactly one LF byte at EOF. A read-only check of the staged archive established that removing that single final LF yields the as-run hash above. No other bytes differ. The archived file was not rerun; the verdict and captured execution remain those of the original as-run bytes.

Complete real subprocess commands, outcomes, exit codes, stdout/stderr, selected input hashes and per-case expected hashes remain in private session evidence (`review-format-proof-01/commands.jsonl` and `summary.json`). Only generic synthetic data was used. Original checkout audit transcripts are not publication fixtures.

## What this establishes

- Working, index and committed branch snapshots need distinct content sources; substituting the current working file in all modes would fail the staged/branch observations.
- An independent NUL-delimited Git status listing can preserve exact rename destination and Unicode/space paths, including when the module is below the Git root. Patch header parsing alone is insufficient for a pure rename.
- Formatting selected content on standard input is read-only and avoids scanning unrelated files. Actual formatter input hashes, not a claim in the harness, establish which bytes were checked.
- Added content is checked; deletion-only and non-Go changes have explicitly inapplicable formatting coverage and issue no formatter command.
- Required Git errors and formatter syntax errors stay visible. A zero process exit from gofmt is not itself the formatting verdict: its output must still match the selected content.
- The unchanged standalone FormatGate still reports the deliberately unformatted untouched file.

## Consequences for the correction

Proceed to an evidence-grounded design and test-first production implementation under the developer's explicit routine-gate waiver for this correction. Only review formatting changes. Preserve the other required/advisory gates, default standalone atom check, existing review modes and source-context access. Make the selected formatting scope explicit in result evidence rather than implying that the whole module passed formatting.

Production code must be independently written against the design and tests; do not copy this disposable harness. Additional failure and path-safety cases belong in production regression coverage, not an unapproved repeat of this proof.

## Explicitly not covered

Private target repositories or metadata; model calls, prompt delivery, rule resolution or finding quality; build/vet/test/race behavior; multi-module review orchestration; arbitrary Git filters, submodules or hostile filesystem races; production compatibility and supported-platform CI. These limits are not claims that such cases work.

The timing is one bounded execution observation, not a performance benchmark. No statistical confidence or repeated-run guarantee is claimed.

## Gate disposition

The developer explicitly waived routine proof/spec/TDD pauses for this formatting-only correction through a draft PR, with at most two independent non-author review calls. The result is Confirmed, so continuation is within that waiver. Refuted/Inconclusive results or material scope/validation/privacy blockers still require a stop. No other project phase is authorized.

