# Publication decisions

All installation commands, source links and publication target public `girishmotwani/atom`.

This change corrects README installation/update guidance and both source and packaged bootstrap instructions. The repository is public; installation failures must be reported accurately instead of assuming access approval is required. No runtime logic, dependencies, tests, PATH behavior or initialization contract changes.

This log records the current source of truth, scope and verification decisions. Historical verification outcomes are not reclassified or presented as new experiments. Labeled profile-prefix redactions in captured evidence remain explicit.

The earlier full Windows/Python gate is retained in [verification.txt](verification.txt). The current documentation correction passed the existing bootstrap source/package parity and PATH-documentation tests: four cases passed. No new constant-string test, Go POC, full runtime retest or paid multi-model review is warranted for a reference-only documentation correction.

Further adoption work, runtime changes and merging are outside this correction. The developer explicitly approved committing and pushing this documentation-only correction to the existing public PRs 9, 10 and 11. No merge or force-push is included.

Final link-check output (python tools\check_links.py, exit 0):

```text
checked 238 relative links across markdown files
all relative links resolve
```

Tracked repository-reference scan: no stale matches. Whitespace check: git diff --check exited 0 with no output.
