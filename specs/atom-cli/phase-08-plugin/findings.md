---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
---

# Findings — Phase 8

Things seen while building the plugin surface that were not fixed here.

## F1 — `atom init` no longer means what its name implies

Installation is now global, so `atom init` is not an installation step. It only
scaffolds `.atom/` project state. The README still presents it immediately after
install, which invites the reading that it is part of setup.

**Suggested:** rename to `atom project new`, or document it explicitly as
"per-project state, not installation". Not done here because renaming a shipped
command is a breaking change and deserves its own decision.

## F2 — The Python package cannot ride along with the plugin

A plugin bundles skills, agents, commands, hooks, MCP and LSP configuration —
not pip dependencies. So a developer runs two installs: the plugin, then
`pip install -e ./tools`. The skills call the `atom` binary, so skipping the
second leaves commands that fail at their first shell-out.

**Suggested:** have `/atom` detect a missing `atom` binary and say precisely
what to install, instead of surfacing a raw command-not-found. Worth a small
behaviour in a later phase.

## F3 — Nothing warns about a shadowed skill directory

`skills/atom/` has no `SKILL.md` and silently contributes nothing. That is
correct today, but the same silence would hide a genuine mistake — a new skill
whose `SKILL.md` was misnamed would simply never appear.
`test_every_atom_skill_directory_is_discoverable` now catches this, with `atom`
explicitly exempted. The exemption is a hard-coded name and will need revisiting
if the shared-assets directory ever moves.

## F4 — Command resolution order is undocumented

The measured rule is: skill beats command, plugin name beats command. This came
from experiment, not documentation, so it may change between CLI releases.
The tests encode the *consequence* (never collide) rather than the rule itself,
which is the more durable thing to assert — but a CLI change could still make
the guard unnecessary rather than wrong.

## F5 — The deprecation warning has no stated date

"Only plugin@marketplace installs will be supported in a future release" gives
no version or timeline. Documentation now uses the marketplace path only, so
Atom is already on the supported route, but any external guide that tells users
`copilot plugin install girishmotwani/atom` will break without notice.

## F6 — Live-loading makes local development pleasant but surprising

A marketplace added from a local path loads the plugin **live** from that
directory: "edits take effect on the next session — nothing was copied." Editing
a skill and re-running in the *same* session silently uses the old text. This
cost one confusing observation during the spike.

**Suggested:** note it in contributor documentation.

## F7 — Two Tier-1 tests break on every new phase

`test_the_real_repository_resolves_eight_phases` and
`test_the_real_repository_orders_phases_one_through_eight` hard-code the phase
list. Adding phase 8 broke both, as adding phase 7 did before it, and phase 6
before that. Each time the implementation was correct and the pinned facts were
stale.

The tests do carry real signal — they prove discovery works against the actual
repository rather than a fixture — so deleting them would lose something.

**Suggested:** assert the *properties* instead of the literal list: that phases
are ordered by numeric prefix, contiguous from 01, and that discovery finds
every directory matching the phase pattern. That keeps the real-repo check and
removes the churn. Not done here because weakening a Tier-1 test is the
developer's call, not the agent's.

## F8 — Free-text routing usually loads no skill at all, and it is invisible

Measured over 24 scored trials from a neutral directory: a skill loaded 33.3% of
the time. Precision was perfect — zero prompts reached the wrong beat — so the
description keywords do discriminate correctly. The problem is that two thirds
of the time nothing is invoked.

The failure is silent by construction. Skill *descriptions* sit in the model's
tool list permanently, so the model can paraphrase a beat convincingly without
ever loading the SKILL.md behind it. One trial produced fluent TDD advice while
its log recorded `tool_counts: {"session_store_sql":1}` and no skill call. The
developer receives description-shaped advice instead of the workflow and has no
way to tell the difference.

**Suggested:** document slash commands as the supported interface and stop
implying prose is equivalent. Re-run
`poc/atom-routing-rules/measure_routing.py` against future CLI builds and
against other models before claiming any improvement.

## F9 — A documented plugin component does nothing

`com.github.copilot/rules/` appears in the official Agent Plugins 1.0 component
table beside agents, commands, hooks and LSP servers. In CLI 1.0.89-4 a rules
file has no observable effect, tested under five conditions including with
`applyTo: '**'`, after an explicit plugin update, and inside the plugin's own
repository. A control in the same conditions confirmed the plugin itself was
loading, because a skill from it was invoked by name.

This matters beyond Atom: the documentation gives no way to tell that the
component is inert, and a plugin author would reasonably ship a rules file and
assume it worked.

**Suggested:** report it upstream. Re-test on each CLI upgrade — if rules start
working they are the natural fix for F8.

## F10 — Measuring agent behaviour needs an instrument outside the agent

The first routing harness asked each skill to emit a sentinel token naming
itself, and reported 22.2%. That number was wrong twice over: 11 of 27 calls had
timed out and were being scored as routing failures, and the model did not
reliably obey the planted instruction, so genuinely on-beat replies were counted
as misses.

The fix was to stop asking the agent to report on itself and read
`--log-level debug` output instead, which records the actual `skill` tool call.
The detector was then validated in both directions — positive on a run known to
have invoked a skill, negative on a run whose log showed none — before any
number was trusted, and the sentinel was reverted so the measurement ran against
unmodified skills.

**Suggested:** treat self-reported agent behaviour as unreliable evidence
throughout Atom. Where a measurement matters, find an observation point outside
the model, and validate the detector both ways before reporting a result.
