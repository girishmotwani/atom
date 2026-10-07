# Review: Dedicated Artifact Writer

## Reviewers

- Claude Opus 5: no significant issues.
- Gemini 3.8 Flash: three Major, three Minor, and one Nit finding.

Both reviewed the staged feature diff against `origin/main` with the approved design
spec and surrounding files. Unrelated unstaged short-namespace notes were excluded.

## Triage

### Major — PowerShell 5.1 silently corrupts non-ASCII stdin

- **Agreement:** 1/2
- **Locations:** `README.md`, `AGENTS.md`, packaged `AGENTS.md`, skill instructions
- **Finding:** Windows PowerShell 5.1 defaults native-process pipeline encoding to
  ASCII, replacing non-ASCII Markdown with `?`. Its object pipeline also emits native
  CRLF.
- **Outcome:** Fixed.
- **Fix:** Instructions set `$OutputEncoding` to BOM-less UTF-8 and recommend
  PowerShell 7. The writer normalizes CRLF and bare CR to LF. The built-wheel test now
  sends Unicode directly and through the documented Windows PowerShell 5.1 recipe.

### Major — Unicode was not tested across a real process boundary

- **Agreement:** 1/2
- **Location:** `tools/tests/test_artifact_integration.py`
- **Finding:** The original Unicode case called `main()` in-process; the installed
  console-script test used ASCII only.
- **Outcome:** Fixed.
- **Fix:** The installed executable now round-trips `café — 東京` as UTF-8, including
  an actual `powershell.exe` pipeline on Windows.

### Major — `.atom/events.jsonl` bypasses the append-only event lock

- **Agreement:** 1/2
- **Location:** `tools/atom/artifacts.py`
- **Finding:** Whole-file replacement could erase event history or race with
  `EventLog.append`, which owns `events.lock`.
- **Outcome:** Fixed after developer approval.
- **Fix:** `.atom/events.jsonl` was removed from the writer allowlist. Event writes
  remain exclusively behind `EventLog.append`.

### Minor — The permission-config test used an environment variable Atom never reads

- **Agreement:** 1/2
- **Location:** `tools/tests/test_artifact_integration.py`
- **Outcome:** Fixed.
- **Fix:** The test now isolates `HOME` and `USERPROFILE`, removes `COPILOT_HOME`, runs
  onboarding, and verifies no user-level `.copilot/permissions-config.json` appears.

### Minor — Refused writes left newly created empty directories

- **Agreement:** 1/2
- **Location:** `tools/atom/artifacts.py`
- **Outcome:** Fixed.
- **Fix:** Parent creation records only directories created by the current write.
  Failure cleanup removes them in reverse order when still empty and never removes a
  concurrent writer's non-empty directory. The link-swap test now asserts the refused
  destination directory is absent.

### Minor — B6 CLI test replaced the filesystem implementation

- **Agreement:** 1/2
- **Location:** `specs/artifact-writer/phase-01-dedicated-writer/test-spec.md`
- **Outcome:** Fixed.
- **Fix:** B6 now maps its CLI reporting half to the mocked CLI test and its no-partial
  filesystem guarantee to the real staging- and replacement-failure tests.

### Nit — Test-spec names and packaging claim drifted from implemented tests

- **Agreement:** 1/2
- **Location:** `specs/artifact-writer/phase-01-dedicated-writer/test-spec.md`
- **Outcome:** Fixed.
- **Fix:** B5 references the implemented parametrized test, and packaging claims only
  the dedicated executable that the test builds and runs.

## Verification after fixes

```text
collected 890 items
...
TOTAL                   2729    107    96%
======================= 890 passed in 77.42s (0:01:17) ========================
```

## Open review findings

No Blocker or Major findings remain open.
