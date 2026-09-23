# Code review
Problems:

Reviewed this branch against 3d026b6: 6860 changed lines across 32 files.

- `.gitignore`
- `poc/compiler-guarantees/results.json`
- `poc/compiler-guarantees/spike.py`
- `poc/derived-state/probe_mtime.py`
- `poc/derived-state/results.json`
- `poc/derived-state/spike.py`
- `skills/atom-tdd/SKILL.md`
- `skills/atom/references/tdd-discipline.md`
- `skills/atom/references/what-the-toolchain-proves.md`
- `skills/atom/templates/test-spec.md`
- `specs/atom-cli/phase-01-check/poc-report.md`
- `specs/atom-cli/phase-02-poc/poc-report.md`
- `specs/atom-cli/phase-03-state/poc-report.md`
- `specs/atom-cli/phase-04-review/poc-report.md`
- `specs/atom-cli/phase-05-ship/poc-report.md`
- `specs/atom-cli/phase-05-ship/tdd-log.md`
- `specs/atom-cli/phase-06-state/decisions.md`
- `specs/atom-cli/phase-06-state/design-spec.md`
- `specs/atom-cli/phase-06-state/findings.md`
- `specs/atom-cli/phase-06-state/poc-brief.md`
- `specs/atom-cli/phase-06-state/poc-report.md`
  - gpt-5.4 run 2: reply is not valid json: Expecting value: line 1 column 1 (char 0)
- `specs/atom-cli/phase-06-state/tdd-log.md`
- `specs/atom-cli/phase-06-state/test-spec.md`
- `tools/atom/cli.py`
- `tools/atom/phases.py`
- `tools/atom/report.py`
- `tools/atom/state.py`
- `tools/atom/status.py`
- `tools/tests/test_cli_state.py`
- `tools/tests/test_phases.py`
- `tools/tests/test_state.py`
- `tools/tests/test_status.py`

| Model | Runs completed |
| --- | --- |
| `gpt-5.4` | 3/3 |
| `claude-haiku-4.5` | 3/3 |

Responses that could not be read:

- `gpt-5.4` run 2 (see stderr for the reason)

## Findings

### `tools/atom/state.py`

#### tools/atom/state.py:171 - high

Reported by: `gpt-5.4` 1/3

- `gpt-5.4` run 3, line 171 (high): Requiring an `approvals` key here makes every existing v1 `state.json` from pre-Phase-6 checkouts look corrupt, so upgrading the CLI will start reporting broken state until users manually delete or reinitialize their local file.

#### tools/atom/state.py:254-255 - medium

Reported at lines 254, 255; nearby lines are grouped, so this entry may cover more than one problem.

Reported by: `gpt-5.4` 2/3

- `gpt-5.4` run 3, line 254 (medium): Malformed approval objects are silently coerced to empty strings instead of being rejected, so a corrupt entry like `{}` becomes an apparently valid approval record with blank fields rather than surfacing a state-file problem.
- `gpt-5.4` run 1, line 255 (medium): Malformed approval entries are coerced into empty strings here, so missing or non-string `phase`, `gate`, or `date` fields are silently accepted instead of being reported as a corrupt state file.

### `tools/atom/phases.py`

#### tools/atom/phases.py:177 - medium

Reported by: `gpt-5.4` 1/3

- `gpt-5.4` run 1, line 177 (medium): This only propagates `poc-report.md` parsing problems from the current phase, so malformed status frontmatter in any other discovered phase is silently dropped even though those phases were already scanned.

### `tools/atom/status.py`

#### tools/atom/status.py:181 - medium

Reported by: `gpt-5.4` 1/3

- `gpt-5.4` run 3, line 181 (medium): Only the current phase's derivation problems are added to the report, so an invalid `poc-report.md` in any non-current phase is silently dropped even though status is supposed to report every problem it finds.

#### tools/atom/status.py:247 - low

Reported by: `gpt-5.4` 1/3

- `gpt-5.4` run 1, line 247 (low): When no project subdirectory is found, returning `specs_directory` makes phase directories placed directly under `specs/` look valid instead of reporting 'no phases', which contradicts the new `specs/<project>/phase-*` layout.

