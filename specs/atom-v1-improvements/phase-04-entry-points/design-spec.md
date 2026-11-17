# Approved Go Repository Setup

## Problem And Scope

The existing init instructions require `go.mod` before entry. Support the request
"set up this Go repository, optionally onboard Atom, then stop" using existing
`go mod init` and `atom init` commands. This is agent guidance, not a new CLI/API,
scaffold generator, permission monitor or requirement for standalone POCs/reviews.

## Contract

- Establish Go intent, target root and real module identity from local inspection;
  ask about unresolved identity/application/version choices rather than invent them.
- Inspect existing module/source/workspace/Atom files, instructions and recipes.
  Preserve user content; do not initialize Git or fetch remote identity evidence.
- For onboarding, follow existing bootstrap safeguards and establish both working
  Atom command roles before the final proposal or setup writes. Go-only skips Atom.
- Propose exact files/contents, module and installed-Go version implications,
  commands/checks, onboarding effects, generated outputs and stopping point.
- Wait for explicit approval. Refusal changes nothing; changed proposals need new
  approval. Tool execution, installs and PATH changes retain separate consent.
- Recheck before writing. Conflicts, symlinks, collisions or unexpected state stop
  setup; no unapproved overwrite, `--force`, migration or repair.
- Create a missing module with `go mod init`, verify it, add only agreed scaffold,
  then run `atom init` only if approved. `atom init --module` is not module creation.
- Reuse existing modules and matching Atom setup. Preserve read-only repeat,
  custom commands and absent machine-local baseline files; do not imply a refresh.
- For minimal new-module setup, use child-only local/offline Go settings. Do not
  install/download tools or change user defaults without separate approval.
- Run sequentially, stop on failures/timeouts and report partial results plus
  diagnostics. Do not promise rollback or silently retry/delete files.
- Report setup separately from baseline/application readiness. Empty-module
  vet/test failures do not authorize source additions; skipped checks prove nothing.
- Stop after setup-only work. Full-feature/resume requests retain their own gates;
  printed CLI suggestions do not authorize feature work, reviews or publication.

## Evidence And Delivery

The approved Windows [mechanical POC report](https://github.com/girishmotwani/atom/blob/c57e52b7dcc5521646a8172ab54249b12896966d/specs/atom-v1-improvements/phase-04-entry-points/poc-report.md)
and [source/transcript](https://github.com/girishmotwani/atom/blob/c57e52b7dcc5521646a8172ab54249b12896966d/poc/atom-v1-new-repo-setup/README.md)
remain in Git history. Installed observations were accepted with limits: missing
commands Confirmed; module+Atom, Go-only and aggregate protocol results Inconclusive.
They do not prove universal adherence, Linux behavior or the later combined text.

Reuse the shared setup reference from init/start/build; keep packaged copies equal.
The existing onboarding distribution test checks actual installed bytes for the
reference and init. Guidance, delivery and live behavior are different evidence.
See [findings](findings.md) and [decisions](decisions.md) for current limits and scope.
