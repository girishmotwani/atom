# Decisions

- Add user-PATH setup only through explicit opt-in, as approved by the developer in this conversation. Do not change system PATH or use setx.
- Use Python for the throwaway spike rather than Go: the uncertain behavior is Python installation-scheme discovery and the Python Windows registry API used by Atom's own tooling. No Go project behavior is being changed.
- The developer approved both the POC brief and the confirmed report through separate gates. Write tests used only a unique temporary registry key, never the real user or system PATH.
- Invoke the real installed executables by absolute path with --help and an empty child PATH to test current-session usability independently of inherited command discovery.
- Propose a dedicated setup-path command rather than changing init's defaults: explicit invocation is the opt-in and can fix discovery before init or without resetting existing project state.
- Include an environment-change broadcast because changing registry values alone does not tell launchers to refresh. This was not covered by the POC; label it as an assumption and require adapter tests and an explicit real setup run. A failure after a registry write must report partial completion.
- Preserve existing registry types and text, compare normalized entries only for duplicates, and reject malformed or oversized additions. No persistent shell-profile editing on other platforms is included.
- Keep the prior explicit authorization to push and update the installed plugin pending until the requested addition is ready. Do not amend commits or include unrelated POC edits. Correcting the inaccessible old marketplace source is called out in the design's shipping follow-through.
- The repository implements Python tooling rather than a Go module, so verification uses its existing pytest suite; do not manufacture a root go.mod to make atom check run.
- Stop at the design gate before implementation. The approved POC is evidence for the design, not approval to skip the design gate.

## Implementation

- The developer approved design-spec.md, including the marketplace source correction, then explicitly ordered instruction-fix publication, PATH implementation, installed-plugin update, and real user-PATH setup. The instruction fix was published separately first.
- Followed the approved explicit setup-path surface; ordinary init remains unchanged. Added native environment notification with partial-failure reporting rather than silently ignoring timeouts.
- Count the Windows limit in UTF-16 code units, including the terminating NUL; tests cover BMP and non-BMP boundary values. Preserve the original registry text, including unexpanded tokens and empty entries.
- Print single-quoted PowerShell commands and escape literal apostrophes so dollar signs/backticks in installation paths cannot alter the invocation.
- Changed the active bootstrap/README installation URLs to the accessible current origin after the old source returned 404. Historical experiment artifacts and unrelated documentation were not rewritten.
- Added characterization coverage for paths already demanded by the happy-path behavior; did not claim those already-green cases were new red/green cycles. No test expectations were weakened to obtain green results.
- Full Python verification ran once after the affected suite passed. No new tooling or dependencies were installed.
- Preserve separate user requests as issues #8 and #7 rather than expanding this implementation to init idempotence or ADO review integration.

## Review and delivery approval

- The developer approved the completed implementation for independent review, publication, installed-plugin update, and actual user-PATH setup.
- Both configured review models completed one run against the staged feature. No author-model self-review was substituted. The tool correctly reported no Go-module gate evidence; Python verification remains the applicable evidence.
- Fixed the non-hermetic subprocess fixture by explicitly selecting this checkout with PYTHONPATH and disabling site initialization in the child. The original return-code assertion was preserved and first observed failing in the isolated scenario.
- Deferred the medium stale-variable-alias finding rather than silently broadening the approved native/environment-resolution design. This can add a redundant directory but does not remove or truncate settings; subsequent literal-entry detection remains idempotent. The limitation is documented in findings.md and review.md.
- Re-ran the affected 113 tests after the test-only correction. Did not repeat the unchanged full Python suite or re-run model calls over a documentation/test-harness-only follow-up.
