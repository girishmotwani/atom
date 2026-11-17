# Repository Setup - Recommend, Approve, Then Act

Use this reference when a developer requests Go repository setup or the selected
task needs setup first. It supports entry without `go.mod`; it does not dispatch
another skill, start a feature or provide an approval enforcement mechanism.

## Inspect The Target And Intent

Establish the target root and whether Go is intended. Inspect existing `go.mod`,
source, workspace files, `.atom` setup, instructions, ignore rules and declared
build/test commands before asking what the repository can already tell you.
Do not initialize Git, fetch remote content or add Go files to a non-Go project
merely to satisfy an Atom check.

Recommend the smallest setup that fits the developer's goal. Existing local
repository identity may suggest a module path, but it is not approval to use it.
When the real module path, application kind or Go-version requirement is unknown,
ask one focused question at a time. Never silently use a directory name or
`example.com` placeholder as the user's module identity.

An existing Go module should be reused, not recreated. Unexpected workspace,
symlink, module or Atom-state conflicts need a named explanation and a separate
decision; do not improvise a migration or repair.

When Atom onboarding is requested, follow [bootstrap.md](bootstrap.md) during
inspection to verify existing working forms for both `atom` and
`atom-write-artifact` through supported `--help` interfaces. Establish both roles
before the final setup proposal or any module/scaffold writes. If either is
unavailable, stop without setup changes and propose the missing prerequisite
separately; installation or PATH changes require their own explicit consent.
After any approved installation, verify both roles before proposing setup.
Module/scaffold-only setup without onboarding does not require Atom commands.

## Present One Concrete Recommendation

Before setup, state:

- The target directory, exact proposed module path and installed Go version,
  including the generated `go.mod` version implications.
- Files to create and any intentional updates, with the purpose and intended
  contents of source/test scaffolding.
- Commands and checks to run, including existing project build/test recipes.
- Atom onboarding effects if requested: `.atom` instructions/configuration/state,
  baseline and event files, managed `.github/copilot-instructions.md` and
  `.gitignore` updates, and `specs`/`poc` directories.
- Expected generated build outputs, such as a CLI executable, and what will
  remain unverified.
- The stopping point: setup only, not automatic discovery or feature development.

Module-only setup is a valid goal. A small new CLI may warrant a minimal
standard-library command and meaningful smoke test; recommend them only when
that fits the goal, show their intended behavior, and get approval. Do not
silently add dependencies, frameworks, CI, Makefiles, licensing or business logic.
Other scaffolding requires its own scoped recommendation and applicable evidence.

If the installed compiler cannot meet the requested Go-version constraint, explain
the mismatch before writing files. Do not silently change the requirement or
install another compiler.

## Wait For Explicit Approval

Ask whether the developer approves the concrete recommendation, then stop and
wait. Inspection, a recommendation, earlier phase approval and ambiguous replies
are not setup approval. Tool-execution permissions remain separate.

Before approval, do not create scaffold/state files, run checks that produce build
outputs, install tools or change PATH. Supported help commands can establish
whether existing tools work; for requested onboarding these checks are required
before the final setup proposal. A missing-tool installation or optional PATH change
needs its own explicit consent under [bootstrap.md](bootstrap.md).

If declined, leave the target unchanged and explain which requested actions remain
unavailable. Do not substitute an unsolicited smaller setup. If the developer
changes the module, files or scope, revise the recommendation and obtain approval
for that revised proposal before acting.

## Execute Only The Agreed Setup

Recheck the target and relevant files before executing. A collision or unexpected
change stops setup; do not overwrite existing modules/source, follow a surprising
symlink, reset approvals or automatically use `--force`. Approved managed
instruction/ignore updates preserve the existing user content.

For a missing module:

1. Run `go mod init <approved-module-path>` in the approved target and verify the
   resulting `go.mod` and module identity.
2. Create only approved scaffold files, formatted before validation.
3. Run `atom init` if Atom onboarding was included in the approval.

For an existing module, skip module creation. Matching existing Atom setup uses
the ordinary read-only repeat path. `atom init --module` alone does not create a
Go module and can omit baseline capture; it is not a shortcut for new-project setup.

For approved onboarding, use the command forms already verified during inspection;
do not turn setup approval into permission for an unapproved tool installation.
Without onboarding approval, skip Atom commands and onboarding-only file checks
and completion requirements.
For the minimal new-module/standard-library path, use child-only
`GOTOOLCHAIN=local`, `GOPROXY=off` and `GOSUMDB=off` as in the local setup trial.
Do not persist those settings or change machine/user defaults. Existing projects'
dependency and toolchain needs must be disclosed; if unavailable, stop and obtain
separate approval rather than downloading, bypassing checks or declaring success.

Execute sequentially. Capture failures with the command, exit status and both
streams; stop remaining setup on an error or timeout. Explain completed and
partial changes. Do not blindly retry, claim transactional rollback or delete
user files to make the error disappear. Repair and cleanup that alter the agreed
plan require another decision. This guidance does not make concurrent setup safe
or guarantee descendant-process cleanup.

## Report Setup And Validation Separately, Then Stop

Report what was created/updated and whether the agreed module/scaffold creation
and, if approved, Atom onboarding succeeded. Without onboarding, report only the
checks actually run; no Atom baseline or bundle is required or claimed as verified.
For approved onboarding, separately report the actual baseline and its scope:

- Module-only setup can finish while vet/test fail because no packages exist.
  Say that setup exists but there is no verified application. Do not add unapproved
  source just to make those checks green.
- A new CLI baseline describes the approved scaffolded tree immediately before
  Atom onboarding, not the original empty directory. Passing smoke tests do not
  prove a future feature works.
- Onboarding exit 0 is not a promise of a passing baseline. Failed checks are
  visible limitations; skipped race/analyzer checks establish nothing.
- Matching repeat onboarding changes nothing and refreshes no baseline or bundle.
  Machine-local baseline/event files may be absent on a clone; do not recreate
  them or report fresh validation.

A setup-only request ends here. Printed advice to create a POC is not permission
to run it. Do not automatically launch discovery, implementation, review, commits,
pushes or publication. For an explicitly requested full feature, recommend the
next evidence step under [poc-discipline.md](poc-discipline.md); setup approval
does not waive that step's gate.

## Evidence Limits

The local trial established these command mechanics for a module-only target and
a tiny CLI on Windows with Go 1.27.0/Python 3.13.14. Those are observed versions,
not project defaults or universal prerequisites. Actual agent waiting/refusal,
other scaffolding and Linux behavior require separate observation. Clear written
instructions are not a technical guarantee of human control.
