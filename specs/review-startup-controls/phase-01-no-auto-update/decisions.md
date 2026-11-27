# Decisions

## Evidence reuse approved on 2026-11-27

The developer selected "Approve evidence reuse and scoped spec". Reuse the
approved isolated ping under specs/phase-tracking-guidance and validate the new
argument-forwarding boundary with failing Python regressions. A further live
model spike would investigate historical causality, not this wiring contract.

## Scope

Track this distinct runtime repair in this phase without altering the earlier
documentation-only #33 design. Keep the existing branch and staged snapshot
untouched; new implementation work remains unstaged pending later decisions.
One independently reviewable change needs no artificial multi-phase plan.

## Boundaries

Default behavior and existing 60/600-second deadlines remain unchanged.
The preparation gate authorized the spec only; the later implementation
approval is recorded below.
Use the already approved artifact writer for phase artifacts and normal editing
tools for source/tests/docs. No paid calls, settings edits, installation, package
refresh or shipping is authorized.


## Implementation approval on 2026-11-27

The developer selected "Approve this spec and implement" for design-spec.md.
This approves the bounded forwarding/help/README repair and fake-runner tests.
No live calls, installation, global configuration change or shipping is included.

## Help test normalization

The new help-content test initially failed because argparse wrapped the expected
phrase across lines, not because the required wording was absent. Normalize
whitespace before checking the same flag/scope/bundled-version assertions; help
line width is not part of the approved contract. No production behavior or
asserted semantic content was relaxed. The first end-to-end red run remains the
clean unknown-option regression, preserved in regression-evidence.md.

## Directly dependent test doubles

Extend the two strict invoke_models doubles in test_style.py and
test_review_toolchain.py with the new optional keyword. Preserve their existing
assertions and all default behavior. This is signature consistency, not a bypass.

## Validation and reconciliation

Use the approved Python-tooling validation adaptation instead of claiming a Go
atom check: no root Go module or Go source was changed. The 457-test affected
suite and existing relative-link checker passed; no full-suite/coverage claim.
CI and pyproject.toml define pytest and link checks, not a separate Python
linter or type-checker. Do not install tooling or refresh installed Atom merely
to broaden this bounded validation. No spec behavior changed in implementation.
Completion approval, independent review and any deployment remain separate gates.

## Completion gate accepted

The developer selected "Accept implementation; leave installation and review
pending" after presentation of the implementation, 457-test verification,
relative-link/whitespace evidence, unchanged spec and recorded findings.
This accepts the scoped implementation only. Installed-package refresh,
independent model review, live calls and shipping remain unapproved/pending.

## Draft publication approved on 2026-11-27

The developer requested "lets create PR", then selected "Create one draft PR
with both changes; defer review gate for draft publication only". Publish the
accepted phase-command guidance fix and startup-control repair as two separate
commits in one draft PR on the existing branch. Rerun affected Python tests and
relative-link/whitespace checks before committing. Push this branch only.

This explicitly defers the independent-review prerequisite for draft publication;
it does not declare either phase's multi-model review complete. Keep the missing
review participation and unreviewed runtime repair prominent in the PR. No new
paid calls, installed-package refresh, saved-setting change or merge is approved.
Earlier no-publication/index-preservation boundaries are superseded only as
necessary to stage, commit, push and open this approved draft. The original
staged tree remains recorded in prior artifacts for audit.

## Draft creation command

Use gh pr create --draft with explicit repository, base and head. The existing
atom ship implementation assembles one phase and offers no draft option, so its
normal create path cannot represent this approved two-phase draft publication.
Using GitHub CLI directly preserves draft status from creation and allows both
artifact sets plus the explicit pending-review limitation in one description.
This changes publication assembly only, not implementation or review verdicts.
