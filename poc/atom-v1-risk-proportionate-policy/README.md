# Spike: atom-v1-risk-proportionate-policy

**Created:** 2026-11-04

## Question

With the same risk/evidence rubric and four fixed cases, will two independent models recommend the same justified next workflow step in every case, cite only supplied evidence, and leave the final choice with the developer without suggesting an unapproved gate bypass?

## Method

Run `atom poc run atom-v1-risk-proportionate-policy`. The disposable Go command renders four fixed cases, probes the two named models once, then runs one independent call per model-case. It disables custom instructions, built-in MCPs, and other model tools; captures raw responses; validates response structure and route agreement; and enforces a 48-call hard ceiling. At most two retries per failed case and one alternate model are allowed by the experiment contract.

## Result

The run used 10 calls (two availability probes and eight case responses), with no failures, retries, or alternate model. Both models agreed on all four supplied route labels and stated that the developer decides, without recommending a gate bypass. No developer was simulated, so this does not demonstrate actual approval/rejection behavior or validate the route taxonomy. The full evidence is in `specs/atom-v1-improvements/phase-03-risk-proportionate-workflow-policy/poc-report.md`.

## Verdict

Confirmed for the four fixed cases and this model pair only. This does not establish universal policy quality or authorize production guidance changes.

## Rerun Warning

Running this spike makes paid model calls; the original ten-call run is the only live experiment. The original harness always exited zero and discarded successful-call stderr, so its automatic verdict and printed empty stderr blocks are not independent evidence. Historical stderr remains unknown; the report preserves the original output without reconstructing it.

Post-review deterministic repairs require READY probes and explicit boolean fields, capture stderr on success/failure, and return exit 1 for Refuted or 2 for Inconclusive. Exit 0 still prints only a candidate confirmation requiring manual evidence/rationale review. Run `go test ./...` for fake-CLI regression tests without paid calls; these tests do not establish model quality.

**Windows descendant timeout cleanup remains unvalidated.** The five-minute context is not a proven process-tree/wall-clock guarantee. Re-gate the instrument and lifecycle boundary, and approve a separate call budget before any live rerun. No paid rerun was performed for these repairs.
