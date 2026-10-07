# Decisions

Deviations from instructions, and choices made without asking, during the
artifact-path-guard POC.

## 1. The spike is Python, not Go

Atom's POC discipline describes throwaway **Go** spikes. This spike is Python.

Reason: the question is entirely about Python stdlib path semantics
(`os.lstat`, `st_file_attributes`, `os.path.realpath`) on Windows. A Go spike would
have re-proven the Go behaviour we already have evidence for, and said nothing about the
module we intend to build. Atom's own tooling is Python under `tools/`.

Recorded rather than asked, because the alternative would not have answered the question.

## 2. Ran `python spike.py` directly instead of `atom poc run`

`atom poc run` crashes on this console with a `UnicodeEncodeError` (see findings #5), and
it is a Go-spike runner besides. The report pastes verbatim output from the command that
was actually run, and names it as such.

## 3. The guard refuses every reparse point, including ones pointing inside the repository

The spike's first run flagged `specs/inner-link/inside.md` as a failure because the
written expectation said an inside-pointing junction should be allowed.

The expectation was changed, not the guard. Deciding whether a link is benign requires
resolving it and re-validating the target, which adds exactly the kind of reasoning that
produced the previous escape. Refusing all links is simpler and fails safe. An author who
genuinely needs a link inside `specs/` can be told no.

This is a real policy choice and belongs in the design spec, not buried in a spike.

## 4. Corrected an expectation mid-POC, and reported both runs

Changing a test's expectation after seeing the result is how a refutation gets quietly
converted into a confirmation. To keep that visible, the first run's failing line and
`verdict=REFUTED` are pasted into the report alongside the passing second run, with the
reasoning for the change stated.

The guard's behaviour was not modified between the two runs — only the expectation.

## 5. Scoped the POC to the decision, not the write

The brief deliberately excludes writing files, batching, and atomicity. Those were part
of the broader `atom_write_artifacts` idea, but the containment question is the one that
can kill the feature, and mixing the two would have made a mixed result hard to read.

## 6. Reused the allowlist boundary agreed earlier without re-asking

`specs/**`, `poc/**`, and exactly `.atom/config.json`, `.atom/state.json`,
`.atom/events.jsonl`, `.atom/baseline.json`. This was settled with the developer during
the `artifact-write-permissions` work and is treated as still current.

## 7. Built the guard immediately after the POC, without a design spec

The POC proved the containment decision; the developer then asked for "a python script
to make sure only allowed paths are writeable". That is a build instruction, and the
module is roughly 200 lines whose shape was already fixed by two refuted experiments, so
a spec between the two would have restated the POC report.

Recorded rather than asked. It is still a deviation from PROVE -> DESCRIBE -> BUILD, and
findings #8 says what to do if the guard grows.

## 8. Shipped as `tools/atom/artifacts.py` plus `atom artifact`, not as a Copilot tool

The original idea was an `atom_write_artifacts` tool the CLI could auto-approve. That
needs agreement about tool registration which is not ours to make, so the write path
ships as an ordinary Atom module with a thin command on top. A tool, a hook, or a skill
instruction can all call the same function later; the guard does not depend on which.

## 9. Kept the spike after superseding it

`poc/artifact-path-guard/spike.py` still classifies and still prints its verdict, even
though `tools/atom/artifacts.py` now does the real work. Atom keeps every spike as
re-runnable evidence, and this one is the record of how the reparse-point ordering was
established. It is not imported by anything and must not be.

## 10. No links are permitted beneath writable artifact paths

The developer confirmed that no real workflow needs a symlink, directory junction, or
other reparse point beneath `specs/` or `poc/`.

The guard therefore rejects every link in a destination path, including links that
currently resolve back inside the repository. There is no benign-link exception to
resolve, maintain, or accidentally widen.
