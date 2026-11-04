# Honest Review Continuation Spike

Disposable Python automation around standard-library Go fixtures, not production
review policy. The [approved brief](../../specs/review-tooling-continuation/poc-brief.md)
defines the nine cases, two sweeps and stop conditions.

Run only with explicit batch approval, from the repository root:

```text
python poc\review-tooling-continuation\spike.py --output <FRESH_OUTSIDE_GIT_DIRECTORY>
```

The output directory must not exist. The driver writes complete native command
events, fixture sources, stub receipts and a summary there. A fresh output path
does not authorize another batch. No models, downloads or global Go settings.

The original trial required verified, already installed Go 1.26.9 and Go 1.27.0.
Compatible controls are experimental evidence, not replacement selected gates.
Runner-error simulation is explicitly labelled; the timeout uses a real Go test.
Race/CGO, dependencies, advisory analyzers and cross-platform readiness are not
established. The parent PR's CI failures remain separate.

The approved 2026-11-01 batch was
[Inconclusive](../../specs/review-tooling-continuation/poc-report.md):
the Go 1.27.0 control could not be verified; no fixture ran and no retry occurred.

The separately approved revised driver is `spike-control-1.27.3.py`.
It changes exactly the compatible-control constant and leaves this original
driver intact. Its [report](../../specs/review-tooling-continuation/poc-report-control-1.27.3.md)
is also Inconclusive: partial first-sweep evidence preceded a Windows timeout
cleanup/output-collection failure. Neither batch authorizes another run.


The developer approved and the agent executed one revised classification
batch on 2026-11-02. Its separate driver is `spike-compiled-timeout.py`; only
the slow fixture changes, using a selected-compiler-built test binary invoked
directly with entry-marker, source-hash, binary-hash and clean-timeout checks.
The approved control remains Go 1.27.3. The
[revised report](../../specs/review-tooling-continuation/poc-report-compiled-timeout.md)
is Confirmed for the bounded matrix only. Preserve earlier evidence; no retry
or production change is authorized by that result.
