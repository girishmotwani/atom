# Synthetic tool-exclusion proof

The retained `source_exclusions_spike.py` tests whether source-wide tool exclusions expose zero tools through Atom's native stdin/JSONL review path and still return the known synthetic Go finding within the existing deadline. It contains no target-repository input.

The [brief](../../specs/ado-pr-review/bounded-review-execution/poc-brief-source-exclusions.md) defines the experiment; the [report](../../specs/ado-pr-review/bounded-review-execution/poc-report-source-exclusions.md) records its single observed result and limits. The frozen source SHA-256 is `84711dbf5032c4016f0836074c68e35eab63a93b276f54cc0d71f9e15a7224ef`.

This is retained evidence, not an instruction to rerun a paid model call. Any new invocation needs separate approval. Request-level tool exclusion does not establish context adequacy, general reviewer accuracy, provider compatibility, or reliable completion. Raw account-bearing traces are not committed.
