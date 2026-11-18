# Setup Scope Decisions

The developer requested simplifying PR #25 on 2026-11-17. Keep the approved setup
behavior, shared reference, init/start/build integrations, packaged mirrors and
installed-byte test. No executable behavior, CLI/API or dependency changes.

Remove the added throwaway spike and verbose chronological specs/reports from the
final PR tree. Keep this concise contract, findings and decisions. Restore the
unrelated installation-preview section and broad phase-plan changes to main rather
than mix them into this setup change; their separate concerns remain deferred.

Full proof/design/test/review/history is preserved at
[the pre-simplification snapshot](https://github.com/girishmotwani/atom/blob/c57e52b7dcc5521646a8172ab54249b12896966d/specs/atom-v1-improvements/phase-04-entry-points/design-spec.md)
and in local archive `pr25-before-simplification-c57e52b.zip`, SHA-256
`07f1ec3f8c80147cc9d166675bd0f6d90bc0b054d0fa152cf8058da3ce9cdc78`.
This deliberately departs from keeping the full spike/report in the latest tree,
with the developer's scope approval; it does not erase the evidence or verdicts.

Reuse approved mechanics with their stated limits. This is documentation
consolidation, not a new design, Go spike, live trial, paid review or fabricated
root Go gate. Existing canonical/package/installed-byte checks cover delivery;
source review does not prove actual agent compliance.

The full CI failure is also present on main and unrelated to this diff. Record it
without changing review runtime, fixture expectations or CI tools in this PR.
Publish a normal follow-up commit, not a history rewrite/force push; keep the PR
open for human review and do not merge. No account or installation changes.
