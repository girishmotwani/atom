# Spike: New-Repository Setup Mechanics

## Question

Can the existing Go module-initialization and Atom onboarding commands compose into a locally usable setup from a repository without `go.mod`, preserving pre-existing files and reporting empty-module validation honestly?

## Method And Result

This archived Windows-only throwaway Go command was run on 2026-11-06 through
`python -m atom.cli poc run atom-v1-new-repo-setup --timeout 600 --no-colour`.
It exercised four local temporary fixtures using existing Go/Atom commands,
standard-library source and child-only offline settings. It did not ask a real
agent to approve or refuse anything. It did not initialize Atom's repository.

The [verbatim execution transcript](execution.txt) records successful vet, build
and execution, all nine subprocess commands, baselines, file preservation,
cleanup and the mechanically **Confirmed** verdict. The empty-module baseline
failed vet/test because no packages existed; race was skipped. This is not a
verified application, live approval test, Linux claim or a fresh shipping run.

See the [approved brief](../../specs/atom-v1-improvements/phase-04-entry-points/poc-brief.md)
and [report](../../specs/atom-v1-improvements/phase-04-entry-points/poc-report.md)
for grading criteria and complete limits. Running the spike requires installed
Go and working Atom Python module forms; no dependency installation is implicit.
