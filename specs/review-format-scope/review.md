# Independent review: changed-file review formatting

## Participation and scope

The developer selected claude-opus-5.5 and gemini-3.8-flash explicitly. Exactly one read-only code-review task ran for each, independently against the staged formatting-only correction and surrounding source. Both are distinct from the GPT-6.1 Sol author. They did not receive each other's findings. No availability probe or third reviewer call ran. The pre-review full Python gate was green: 1059 passed, 2 skipped, 95% coverage; see verification.md.

Review scope was the Python implementation, regression tests, neutral proof/spec evidence and directly related source/packaged documentation. No private target source or target check was sent to a reviewer. This report records triage under the developer's scoped waiver, not an additional approval or a post-fix review round.

## Merged findings and triage

| Severity | Reviewer | Pre-fix location | Scenario, consequence and repair | Disposition |
|---|---|---|---|---|
| Medium | claude-opus-5.5 | tools/atom/_review_format.py:162-178,206-209,249-250 | Git diff.submodule=log/diff can change the number of patch blocks for a non-Go gitlink. The raw/patch count check can then block review before formatting. Pin --submodule=short and cover local gitlink updates with both configured display modes. | Fixed; real-Git RED reproduced the log-mode failure (the diff-mode fixture already passed), then both modes passed. User Git configuration remains unchanged. |
| Medium | claude-opus-5.5 | tools/atom/_review_format.py:139-145,193-200 | Colon/backslash source-path restrictions were applied to every manifest entry, rejecting POSIX-valid non-Go/deleted/outside-module paths that formatting never reads. Apply basic relative-manifest validation globally, but native source restrictions only to surviving in-module Go inputs, determining module membership from Git components before native path interpretation. | Fixed; six deterministic cross-platform manifest cases failed before the fix and passed afterward. Existing unsafe selected-source and identity guards still pass. |

Both Opus findings had high stated confidence and were accepted. Gemini reported: "No significant issues found in the reviewed changes." Lack of corroboration did not dismiss either concrete Opus finding.

Opus also noted a patch-layout configuration test gap rather than a separate demonstrated bug. The submodule regression closes its concrete case. No independent finding was deferred or rejected. The author did not claim the reviewers re-reviewed subsequent fixes; the one-round budget is exhausted.

## Repair evidence and limits

Post-review regressions: 65 passed in 40.13s. The fresh full Python gate after these fixes passed 1067 tests with 2 existing POSIX-only skips on Windows and 95% total coverage; exact output is recorded in verification.md. Exact RED/GREEN outputs are retained in tdd-log.md. The POSIX-special-name cases inject valid Git manifest names because those checkout names cannot be created on Windows; they are not represented as a real POSIX execution. Supported-platform CI remains required publication evidence.

No unresolved review finding remains after the two repairs. This is a formatting-only correction, not end-to-end ADO PR review feasibility or quality evidence.
