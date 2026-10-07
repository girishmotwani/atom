# Review: Managed Atom Gitignore Entries

## Reviewers

- Claude Opus 5
- Gemini 3.8 Flash

Atom's built-in review runner was attempted first with its default independent models,
but both subprocesses hit the runner's fixed 60-second timeout and returned no usable
review. The two reviewers above then reviewed the full diff and surrounding files
independently.

## Verification before review

```text
collected 846 items
...
TOTAL                 2559     93    96%
846 passed in 40.42s
```

## Merged findings

### Major

1. **The user-owned `.gitignore` is truncated before its replacement is durable.**
   - Agreement: 1/2
   - Location: `tools/atom/onboarding.py`
   - Consequence: interruption or disk failure after opening with `w` can destroy
     existing ignore rules.
   - Proposed triage: **fix now** with a same-directory temporary file, flush/fsync,
     and atomic `os.replace`.

2. **The malformed-marker recovery command is misleading.**
   - Agreement: 1/2
   - Location: `tools/atom/onboarding.py`
   - Consequence: the error says to run `atom init` again, but the earlier partial init
     makes plain init refuse; recovery requires `atom init --force`.
   - Proposed triage: **fix now** by naming the correct command and testing recovery.

3. **Filesystem errors from reading or replacing `.gitignore` can escape the onboarding
   error contract.**
   - Agreement: 1/2
   - Location: `tools/atom/onboarding.py`
   - Consequence: an inaccessible or unwritable file can produce a traceback instead
     of an actionable `atom init:` diagnostic.
   - Proposed triage: **fix now** by wrapping `OSError` as `OnboardingError`.
     `UnicodeDecodeError` already subclasses `ValueError` and is caught by the CLI.

4. **Existing unmarked `.atom/state.json` ignore rules are not migrated.**
   - Agreement: 1/2
   - Location: `tools/atom/onboarding.py`
   - Proposed triage: **reject**. Removing an unmarked user-owned rule is destructive,
     the observed repository did not report `state.json`, and the agreed scope is to
     manage generated runtime entries only.

5. **Already tracked generated files are not automatically untracked or always
   announced by init.**
   - Agreement: 1/2
   - Location: onboarding documentation and CLI output
   - Proposed triage: **reject automatic index changes**, as already decided. Add a
     concise migration note to the init skill and README; do not run or prescribe
     `git rm --cached` unless a file is actually tracked.

### Minor

1. Isolate `git check-ignore` tests from global ignore configuration.
   - Proposed triage: **fix now**.
2. Assert that onboarding never changes the Git index.
   - Proposed triage: **fix now**.
3. Cover no-final-newline, already-blank-line, missing-marker, and inverted-marker
   boundaries.
   - Proposed triage: **fix now**.
4. Make the single-newline branches explicit instead of treating a bare carriage
   return as a supported newline convention.
   - Proposed triage: **fix now**.
5. Ignore `.atom/*.tmp` and `.atom/*.unsaved`.
   - Proposed triage: **reject** as outside the developer-approved three-file scope.

### Nit

1. Put this repository's own three entries inside the same managed markers.
   - Proposed triage: **fix now** so Atom dogfoods the generated form.
2. Reconsider whether baseline data should be shared.
   - Proposed triage: **reject** because the developer explicitly identified
     `baseline.json` as unwanted PR status data and approved ignoring it.

## Triage outcome

The developer approved the proposed triage.

- Fixed atomic replacement, temporary-file cleanup, actionable read/write errors, and
  the `atom init --force` recovery instruction.
- Added tests for index preservation, global-ignore isolation, LF/CRLF and separator
  boundaries, missing/duplicate/inverted markers, failed replacement, and invalid
  UTF-8 input.
- Added the one-time tracked-file migration note to the README and both init skill
  copies.
- Put this repository's own entries inside the managed block.
- Rejected automatic removal of unmarked `.atom/state.json` rules because those rules
  are user-owned and outside the selected generated-only boundary.
- Rejected automatic Git index changes and the proposed `.atom/*.tmp` /
  `.atom/*.unsaved` expansion.
- Rejected reopening the `baseline.json` policy because the developer explicitly
  selected it as machine-local status data.

## Post-fix verification

```text
collected 853 items
...
TOTAL                 2580     93    96%
853 passed in 45.74s
```

No Blocker or Major findings remain open.
