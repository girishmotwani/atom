# Findings

- Marketplace-installed command `atom` shadows `/atom:<skill>`, even though
  direct `--plugin-dir` loading does not. Distribution-path evidence must win.
- `/atom:start` successfully reaches a non-colliding command in the namespace
  probe, so the router can move without losing the guided entry point.
- The marketplace-install probe exposed a Copilot child process that outlived
  Python's timeout. The delayed process still wrote complete results, and the
  previously installed `atom-go@atom` plugin was restored after the probe.
