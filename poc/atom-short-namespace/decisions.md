# Decisions

- The existing Python probe was evaluated as-is rather than replaced with a Go
  spike. This experiment tests Copilot CLI plugin resolution, and replacing the
  already-executed instrument would discard the pre-registered evidence.
- The report is stored beside the spike as `results.md`, as required by
  `claims.md`, because this isolated probe directory has no `.atom/` project
  state or corresponding accessible project specification directory.
- The registered `--plugin-dir` verdict remains confirmed because its criterion
  passed. The installed-distribution conclusion is separately reported as
  refuted because that follow-up exercises the real shipping path and returned
  the router response for `/atom:poc`.
- The temporary `config.json` copy is parsed without comment lines and its
  `installedPlugins` list is cleared. Authentication is preserved while the
  user's real configuration is never modified.
