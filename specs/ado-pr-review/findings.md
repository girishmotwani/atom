# ADO review limitations

- Real-PR fixed-evidence context quality, caller-document completeness, and broader provider/CLI-version compatibility remain unvalidated. The retained synthetic trials establish only their narrow mechanisms.
- Initialized module rules and automatic surrounding-code/dependency collection are not delivered. Reports disclose this; explicit caller documents are unverified input, not authenticated source matching PR pins.
- Go checks cover the selected module, while the diff retains all PR files. Forks, inactive PRs, SSH origins, and on-premises ADO URLs are unsupported by the current native-entry contract.
- Azure CLI authentication and Git HTTPS credentials are separate prerequisites. Deterministic tests and local-Git fixtures do not establish live ADO permissions, remote checkout success, or target build quality.
- Prompt hashes/counts identify logical UTF-8 before platform stdin normalization. Existing Windows LF-to-CRLF transport is not an exact-byte input guarantee for arbitrary subprocess protocols.
- No new runtime defect was found during this artifact-only cleanup. See [verification](verification.md); no fresh model review or target execution is claimed.

## Existing hosted-CI blocker

[The pre-cleanup hosted-CI run](https://github.com/girishmotwani/atom/actions/runs/40903164788) includes failing path-equality assertions in the PR checkout fixtures on macOS and hosted Windows: resolved temporary-directory paths differ from their alias spellings (/private/var versus /var, or long Windows names versus 8.3 aliases). The local Python gate passed, but hosted CI is not green. This artifact-only cleanup has not changed those tests or runtime paths; The developer explicitly deferred fixture repairs and selected cleanup-only publication; CI remains a merge-readiness blocker.
