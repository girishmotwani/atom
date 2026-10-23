# Changed-file formatting proof

Question: Can one selected working, staged or branch diff supply only its changed, surviving Go-file snapshots to a read-only formatting check, so untouched formatting defects do not block review while genuine formatting failures in the selected files still do?

This is a disposable Python integration proof, not production code. It creates synthetic Git fixtures, checks real gofmt input hashes and expected results, audits the original/tooling checkouts and removes only its owned fixture directory. It does not access an ADO repository or call a reviewer.

Run only with an approved brief and a new non-existing session-owned scratch path. The process-local PYTHONPATH must point to the clean reviewed phase 1 tools checkout at the recorded revision; this frozen historical program intentionally asserts that revision. It is not the regression-test entry point for later production changes.

```text
python poc\review-format-scope\spike.py --scratch <new-session-owned-fixture-directory>
```

The original approved single attempt was Confirmed. See the accompanying POC report for verbatim evidence, exact bounds and non-coverage. Do not promote this source into production or silently rerun a changed experiment.

