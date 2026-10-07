# Findings

Problems noticed during the artifact-path-guard POC that were **not** fixed here.

## 1. The symlink arm of the case matrix never ran — Medium, partly addressed

`os.symlink` raised `OSError` on this machine (Developer Mode off, unprivileged shell),
so `symlink_created=False`. The junction case passed, and junctions and symlinks are
both NTFS reparse points caught by the same attribute test — but that is an argument,
not evidence. The real test suite needs a symlink case guarded by skip-if-unavailable,
and CI needs at least one runner where it actually executes.

**Partly addressed.** `tools/tests/test_artifacts.py` uses a junction on Windows and a
real `symlink_to` on POSIX, skipping if neither can be created. On this machine only the
junction path executed, so the symlink branch still has no evidence here; it needs a
POSIX or Developer-Mode runner in CI.

## 2. TOCTOU window between deciding and writing — Medium, now closed

The guard answers a question about the filesystem at time T. A writer acting at time
T+1 can be redirected by a link created in between. The spike does not address this and
the eventual writer must either re-validate at write time or open the file in a way that
refuses to follow links.

**Resolved in `tools/atom/artifacts.py`.** `write_artifacts` creates each directory
component itself (refusing a link at the component where it appears), re-validates the
destination after the directories exist and again after every file is staged, stages the
content with `O_CREAT|O_EXCL` (plus `O_NOFOLLOW` where the platform has it), and only
then `os.replace`s it into place. `test_link_appearing_after_validation_is_caught_before_the_write`
plants a junction in exactly that window and asserts nothing is written. The residual
risk is honest and unavoidable without native handle-based APIs: another process could
still swap a component between the final re-validation and `os.replace`. That final
window writes to a *name*, not through a followed link, so the worst case is a rename
into a directory that has just become a link — narrow, but not provably zero.

## 3. Exotic Windows path aliases untested — Medium

Not exercised: NTFS alternate data streams (`specs/demo.md:hidden`), 8.3 short names,
trailing-dot and trailing-space aliases, hard links, and `\\?\` extended-length prefixes.
Several of these can make two different strings name the same file, which is the general
shape of the bug that refuted the previous POC. They need to become test cases or a
written non-goal.

## 4. Non-Windows platforms unproven — Low

Only `win32` was exercised. The guard's POSIX branch (`stat.S_ISLNK`) is written but
never ran.

## 5. `atom poc run` crashes on Windows cp1252 consoles — Medium

Carried over from the previous POC and still unfixed: `atom poc run` raises
`UnicodeEncodeError: 'charmap' codec can't encode character '\u25cf'` when the console
code page is cp1252. Workaround is `$env:PYTHONUTF8='1'`. This spike was run directly
with `python spike.py` for that reason. The defect is in the report rendering path
(`tools/atom/report.py` / `tools/atom/cli.py`) and deserves its own fix.

## 6. A bare directory target is denied by accident, not by design — Low, now deliberate

`specs` on its own is denied with `outside-artifact-set`, because the allowlist match
requires at least one component below the allowed directory. The behaviour is correct
but it was not deliberately designed, and nothing currently records the intent.

**Now deliberate.** `_artifact_set_reason` in `tools/atom/artifacts.py` states the rule
("a bare directory name is not writable on its own -- only files beneath it") and
`test_non_artifact_paths_are_refused` pins `specs` as refused.

## 8. The guard was built without an intervening design spec — Medium

Atom's pipeline is PROVE → DESCRIBE → BUILD, and this went POC → implementation with no
`design-spec.md` between them. The module is small and its shape was settled by the two
refuted experiments, but the policy choices inside it — refuse every link, deny a bare
directory, treat `.atom/atom/` as off-limits — are design decisions that currently exist
only as code comments and this file. If the guard grows a second caller, write the spec
first.

## 7. This POC was written in Python, not Go — Low

Atom's POC discipline describes Go spikes. Atom's own tooling is Python, and the thing
under test is Python stdlib path behaviour, so a Go spike would have proven nothing
about it. Recorded as a deviation in `decisions.md`; worth clarifying in
`poc-discipline.md` whether self-hosted Python spikes are a sanctioned exception.

## 9. Nine lines of the guard are defence-in-depth and never execute — Low

`tools/atom/artifacts.py` is at 94% line coverage. The uncovered lines are branches that
cannot be reached through the public functions given the checks that precede them:
`resolves-outside-repository` (the link check already rejected every way to get there),
the `outside-repository` guard inside `_create_validated_directories`, and the
`OSError` fallback in `_is_reparse_point`. They are kept because each one fails closed
and removing them would make a later edit to the ordering silently dangerous. If they
are still dead after the guard grows a second caller, delete them rather than writing
contrived tests.
