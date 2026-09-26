---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
---

# Decisions — Phase 8

Every point where judgement replaced the developer's, or where Atom's own
method was not followed exactly.

## D1 — Phase 7's design spec was superseded, not deleted

The developer's redirection ("we went the wrong direction with the user
experience") invalidated phase 7's *mechanism* — a Python-side interview in
`atom poc new` — but not its evidence. The spec was marked superseded with a
pointer here, and its Evidence Base left intact. Deleting it would have
destroyed the falsifiability and `.docx` findings, which were paid for and
still constrain any discovery surface.

## D2 — Tests were written after the code, not before

Atom's method is test-first. `tools/tests/test_plugin.py` was written **after**
`plugin.json` and the marketplace manifest existed.

The honest reason: the failure mode being guarded — silent command/skill name
collision — was *discovered* by the spike, not known in advance. There was
nothing to test-drive until the spike revealed the rule.

The tests were mutation-checked rather than assumed: introducing a colliding
command name made each guard fail with a readable message, and removing it
restored green. A test that has never failed proves nothing.

## D3 — The plugin is named `atom-go`, which the developer did not choose

Naming the plugin `atom` measurably shadows a skill named `atom`. The developer
asked for "the atom family of commands", not for a specific plugin name, so this
was decided without consulting them. It changes the documented install line to
`copilot plugin install atom-go@atom`. Reversible: renaming the plugin back to
`atom` costs one line in two manifests and permanently forfeits `/atom` as a
skill.

## D4 — `/atom` was added as a command, though no beat asked for it

The developer asked that a free-text description route into the POC flow.
Nothing in Atom's existing skill set does that. Rather than widen an existing
skill, a new `/atom` command was added as the router. This is the only new
command file in the phase.

## D5 — A README link was dropped and restored

Rewriting "Run it" removed the only link to `AGENTS.md`, which the link check
caught as a drop from 136 to 135 links. The link was restored in the new text
rather than the check being adjusted.

## D6 — Beat-selection accuracy was not measured

`/atom` was exercised once, on one description, and routed correctly. That was
treated as a smoke test and reported as an anecdote, not as evidence. Measuring
it properly needs a pre-registered rubric and repeated runs, which is a spike in
its own right and was not attempted here.

## D7 — Probe artifacts were left in the repository

`poc/copilot-plugin-surface/fixture/` is a throwaway plugin. It was kept because
it is the executable evidence behind the claims, consistent with how earlier
phases keep their spikes. The temporary `market-fixture/` copy was deleted once
its finding (`source: "."` works) was recorded.
