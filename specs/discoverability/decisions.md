# Discoverability and publication decisions

The developer approved recommendation 1: a searchable Go/AI README heading, a Go-focused repository description, and the proposed seven topics. The developer then explicitly directed that all changes and PRs target public girishmotwani/atom and completed owner-account browser authentication. Confirmed ADMIN access without requesting or exposing credentials.

Applied the approved public description and topics. Kept the original remote and dirty worktrees intact; added a separate public remote and created docs/go-ai-discoverability from public/main for the documentation edit. The repeat-init and ADO open-PR inventory was read with the already stored working-account credential scoped to one child process, without switching the active public account or printing the credential.

This recommendation is documentation/repository metadata, not executable behavior or a new Go phase: no throwaway Go POC, synthetic heading unit test, or runtime quality claim is appropriate. Use the existing Markdown link checker and whitespace checks for this edit. Do not claim that setting keywords empirically improves search rankings. No visibility change, direct main push, new skill compatibility claim or further discoverability recommendation is included.

The read-only public-main compatibility check exposed substantive ADO merge conflicts. Stop before choosing an integration strategy. Recommend recreating the unchanged reviewed branches publicly, with ADO explicitly draft/not merge-ready and reconciliation separately gated; alternatively reconcile under a separately approved scope before publishing. Private PRs remain open until public replacements are verified. No automatic closing or merging is authorized.

## Publication strategy approved

The developer selected publish-unchanged-with-ado-draft. Publish the exact reviewed repeat-init and ADO branch commits to the public repository, recreate their PRs, and explicitly mark the ADO PR draft/conflicting. This does not authorize runtime integration edits, conflict resolution, force-pushes, merges or private-PR closures. Public-main integration is deferred separately. The README heading and subtitle change is a separate public-main-based documentation PR; the description and seven topics are already live.

Set the GitHub CLI repository default and Git's default push remote to the verified public repository, while retaining the private origin for historical lookup. This follows the developer's instruction that all publication target the public repository and avoids silently redirecting or deleting the old remote. Keep all existing dirty worktrees untouched.

## Documentation verification and historical-publication privacy gate

The README heading is now Atom - AI coding skills for Go; its subtitle names runnable POCs, evidence-backed specs, TDD and multi-model review. Only this first-screen wording is changed; quickstart layout, examples, compatibility and remaining recommendations are outside scope. Public repository description and all seven selected topics were read back successfully. Documentation-only check output:

```text
checked 237 relative links across markdown files
all relative links resolve
```

Tracked whitespace checks passed. No runtime test, Go POC, synthetic heading unit test or ranking improvement is claimed for this copy-only edit. Publish it as its own documentation PR with the required findings and decisions.

The approved unchanged-branch migration exposed a new disclosure consideration: original historical logs retain local Windows profile/worktree paths. Preserve the developer's decision authority and stop before either code-branch push for a specific privacy disposition. No credentials were found by the limited signature scan, and no secret values were printed. This is separate from the already approved ADO draft/conflict strategy; no runtime edit or integration change is selected.
