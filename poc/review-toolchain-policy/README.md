# Exact Go Selection Experiment

Approved question, verbatim:

> Can child-process-only selection of Go 1.26.9 keep build, vet, and test on that exact version across conflicting inherited selection settings and compatible module/workspace toolchain suggestions, reject higher language-version requirements without upgrading, and leave persistent defaults unchanged?

Run from the worktree root with `python poc\review-toolchain-policy\spike.py` only under an approved experiment budget. This driver makes ten predeclared cases and no retries. It uses existing local Go tools only, disables proxy/dependency retrieval, and gives each Go command 60 seconds through Atom's existing owned-process runner. The wrapper has a separate 70-second outer guard to allow failure reporting and bounded cleanup; this is not extra Go execution time.

Python automation generates isolated standard-library Go modules/workspaces, records complete JSONL command evidence, verifies input/settings snapshots and removes its owned temporary fixture directory. No normal Go-root scaffold or `atom poc run` is used because the approved question requires a matrix of independent modules and per-child environments, not one Go program's ambient toolchain.

No production code, project selection format, dependency compatibility, real PR, model, Linux/macOS result or runtime-wide reproducibility claim is covered. The experiment is not a benchmark. Copy its knowledge, never its driver, into production design.

## Separately Approved Follow-Up

`spike-local-executable.py` imports the original fixture definitions/helpers without altering the executed original source. Its distinct question and approved limits are in `specs/review-toolchain-policy/poc-brief-local-executable.md`.

It ran once with all ten direct-local-executable cases meeting their expected outcomes; see `poc-report-local-executable.md` for complete command evidence and limits. The original `spike.py` trial remains Inconclusive. Neither archived driver may be automatically rerun or promoted into production. A future invocation needs a fresh explicit budget, and no publication is approved by successful local execution.
