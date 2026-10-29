# Discoverability and public publication findings

The public repository grants the authenticated owner ADMIN access. The approved Go-focused GitHub description and seven topics are applied and independently read back. The README change is isolated on a public-main-based documentation worktree; the original dirty checkout remains untouched.

## Public migration needs an integration decision

The two open working-repository PRs correspond to fix/repeat-init-no-op at 0bb4bc68447fc6f39dadd5090b0404d619c0e20d and feat/ado-pr-review at 8e32944b56488d57f2ea6aec9c36012cc7c3519f. Public main already contains separately published Windows process-ownership and changed-file-formatting fixes. The ADO feature branch is based on a different history and has real conflicts against current public main, including runner, diff, review, tests and archived POCs. Do not silently overwrite the public fixes or call an unchanged migrated PR merge-ready.

A read-only git merge-tree --write-tree check, which did not modify any worktree, printed:

```text
ADO feature merge-tree exit: 1
Repeat-init merge-tree exit: 0
```

The repeat-init branch predicts a clean merge, not a tested integrated result. The developer must choose unchanged public publication with ADO marked draft/conflicting, or separately scoped reconciliation before publication. No source resolution, force-push, merge or private-PR closure has occurred. New public branch pushes and PR creation wait for this decision.

The developer chose unchanged public publication with ADO explicitly draft/not merge-ready. The integration conflicts remain deferred and visible, not resolved. The repeat-init prediction is not a claim that the combined public-main result was tested. Both exact branch tips receive fresh Python checks before publication; only their branches, not public main, are pushed. The documentation PR contains no runtime code.

## Historical log-path disclosure requires owner confirmation

The pre-publication scan found local Windows profile/worktree paths in historical repeat-init proof and verification logs and the shared PATH-bootstrap review artifact. These are actual historical local paths, not credentials or synthetic path placeholders. Credential-signature checks found no matching secrets; that limited scan is not a blanket secrets assurance. The same shared review artifact is also in the ADO branch.

Publishing the exact existing commits would make those paths available in public history. Editing only branch tips would not remove them from earlier reachable commits. Before pushing either unchanged branch, ask the owner whether to preserve the original evidence including these local paths or create properly sanitized public-history copies. Do not silently redact history, rewrite original refs or call a tip-only redaction sufficient. The separate public-main-based README documentation branch contains no such paths and is unaffected.
