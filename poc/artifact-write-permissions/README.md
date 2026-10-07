# Spike: artifact-write-permissions

**Created:** 2026-10-06

## Question

Can a repository-level Copilot CLI permissionRequest hook auto-approve every file-tool write confined to specs/**, poc/**, or the four approved .atom runtime files while leaving source, instruction, escaped, and mixed-target writes unapproved?

> A good spike question is falsifiable. If there is no observation that could
> answer it "no", it is not a question -- it is a preference.

## Method

The Go command creates a temporary Git repository, installs a repository
`permissionRequest` hook, and runs real Copilot CLI `apply_patch` requests against
allowed, denied, escaped, and mixed paths.

## Result

See `specs/artifact-write-permissions/poc-report.md` for the complete verbatim
`atom poc run artifact-write-permissions` output.

## Verdict

**Refuted.** A mixed spec/code patch wrote the approved spec file before the
source-code target was denied, so per-file hook approval cannot enforce an atomic
artifact-only boundary.
