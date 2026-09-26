---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
---

# TDD Log — Phase 8

## This phase was not test-first, and this log says so

Atom's method is red-green. This phase was **spike-first**: the rule the tests
enforce did not exist until the spike discovered it. There was no failing test
to write on day one, because nobody knew that a command sharing a skill's name
silently loses.

Recorded as a deviation in [decisions.md](decisions.md) (D2) rather than
disguised as a red-green sequence that did not happen.

## What was done instead

The compensating control was **mutation testing**: rather than watching each
test fail before the code existed, each guard was made to fail *after* the code
existed, by reintroducing the exact defect it claims to catch.

| Step | Action | Observed |
|---|---|---|
| 1 | Write `test_plugin.py`, 8 cases | `8 passed` |
| 2 | Add `commands/atom-poc.md`, colliding with the `atom-poc` skill | `FAILED ... the skill wins and these commands never run: ['atom-poc']` |
| 3 | Remove it | `8 passed` |
| 4 | Add `commands/atom-go.md`, colliding with the plugin name | `FAILED ... a command named 'atom-go' never runs; rename it` |
| 5 | Remove it | `8 passed` |

Both critical guards were therefore observed red and green, in that order, for
the precise defect each exists to catch. That is weaker than true TDD — it does
not prove the *design* was driven by the tests — but it does prove the tests are
not vacuous.

## Regression caught during the phase

Rewriting the README's "Run it" section dropped the only link to `AGENTS.md`.
`check_links.py` reported 136 → 135 links. The link was restored in the new
prose; the check was not adjusted to accept the loss.

## Pinned facts updated

Adding `phase-08-plugin` broke two Tier-1 tests that hard-code the phase list:

```
assert len(discover_phases(REAL_SPECS)) == 7
E  AssertionError: assert 8 == 7
```

The implementation was correct, so the pinned facts were updated rather than the
behaviour. This is the third phase in a row to break these two tests; the
friction is recorded in `findings.md` for the developer to decide on.

## Final state

```
811 passed
checked 140 relative links across markdown files
all relative links resolve
atom status -> phase-08-plugin
```
