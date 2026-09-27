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

## F11 — The documented install works, but only for the author

Until now every install had been from the local path, so the instructions the
README actually gives a new user had never been run. Testing them end to end,
`copilot plugin marketplace add girishmotwani/atom` followed by
`copilot plugin install atom-go@atom` does work: the marketplace resolves,
`"source": "."` is interpreted correctly against a GitHub clone, 9 skills
install and `copilot skill list` reports the expected 12 entries.

That result is misleading on its own, because the repository is private. The
marketplace command shells out to `git clone`, which uses whatever git
credentials are in the environment. The first attempt failed with
`Repository not found` because this shell carries an injected token for a
different account; with that cleared, the author's own credentials made the
identical command succeed. So the install is really being tested by someone who
already has access.

Two consequences. For anyone outside that set — which is the entire intended
open-source audience — the first command in the README fails, and it fails with
`Repository not found`, which reads as a typo in the repo name rather than a
permissions problem. And because the outcome depends on ambient credentials,
this is a genuine "works on my machine" hazard.

**Suggested:** the repository has to be public before the README's install
instructions are true for anyone but the author; until it is, say so in the
README rather than leaving instructions that cannot work. Re-run this check
from an unauthenticated environment as a release gate, since passing it while
authenticated proves nothing about a new user.

**Status.** The install path itself is verified. To prove it, the repository was
made public briefly and the check was re-run the way it should be run: an
anonymous clone with the credential helper disabled and `GIT_TERMINAL_PROMPT=0`
succeeded, so the packaging is genuinely fetchable by a stranger, and the full
documented flow then installed 9 skills for 12 listed entries.

The repository has since been set back to private, deliberately, until the
author has finished testing. That re-breaks the README's install instructions
for everyone else, which is the correct trade while there is no audience — but
it means the instructions are currently aspirational rather than true, and the
README should not be treated as verified-for-users until the repository is
public again.

**Release gate:** at the moment the repository goes public, re-run the
unauthenticated clone and the documented install from an environment with no
credentials. Passing either check while authenticated proves nothing about a
new user, which is exactly the trap this finding started as.

## F12 — The two install steps assumed different worlds

Step 1 of the README installed the plugin from the marketplace, which clones into
Copilot's own storage and leaves the user without a checkout. Step 2 then told
that same user to run `pip install -e ./tools`. There is no `./tools` in their
working directory, so the `atom` CLI could not be installed at all — and the
beats depend on it in 25 places (`atom check`, `atom status --start`,
`atom phase add`), so the plugin on its own is inert.

The defect survived because the instructions were only ever exercised by someone
standing inside a clone, where `./tools` happens to resolve. This is the same
root cause as F11: an instruction validated from a position no real user
occupies.

**Resolved.** The install now uses
`pip install "git+https://github.com/girishmotwani/atom.git#subdirectory=tools"`,
verified end to end in a throwaway virtualenv against the private repository: it
builds `atom-cli` and the `atom` entry point runs. It needs the same repository
access as the plugin, which is the correct coupling — both halves come from the
same place by the same credentials. The editable install is kept, but labelled
as the contributor path rather than the default.

**Suggested:** whenever an install instruction changes, run it the way a user
would — from a directory that is *not* a clone of this repository. Every
instruction that assumes a clone will pass when tested by a contributor and fail
for everyone else.

## F13 — Bundling the CLI works, and still loses to `pip install`

The `atom` CLI already ships with the plugin: `marketplace.json` uses
`"source": "."`, so `marketplace add` clones the whole repository, `tools/`
included. The open question was whether a skill could find and run it.

It can. A loaded skill reports its own absolute `SKILL.md` path correctly, and
resolves a sibling script from it. The script then executes and leaves proof on
disk — verified by a sentinel file, not by the agent's account of itself.

It still loses, for a reason unrelated to the mechanism. The plugin sits outside
the user's project, so executing anything inside it needs a path grant
(`--add-dir <plugin root>`), and that root is not a stable path — it differs
between a live local plugin and a marketplace clone under `%LOCALAPPDATA%`. The
instruction would become "locate the plugin, then pass it on every launch",
against `pip install` once. Bundling would also cost the standalone `atom`
binary that a terminal and CI need on PATH.

**Suggested:** keep `pip install`. Revisit only if Copilot CLI begins trusting a
plugin's own directory by default — that single change flips the decision. The
interactive case is untested and could soften it: every trial used `-p`, where
the refusal is literally "could not request permission from user", and approvals
persist per working directory in `permissions-config.json`.

## F14 — Plugin skills are not reliably available, which may invalidate F8

Across 8 sessions that asked for a skill **by name**, with the plugin installed
and enabled the whole time, it loaded 3 times and returned
`Skill not found` 5 times. `copilot skill list` showed it registered and
`copilot plugin list` showed it enabled during the failing window, and the files
were on disk throughout. The same prompt failed and then later succeeded,
unchanged.

This is availability, not routing — and it casts doubt on F8. That finding
measured a 33% skill-load rate from free-text prompts and attributed the missing
67% to the model declining to load a skill. These trials removed routing from
the question entirely by naming the skill, and still failed around 60% of the
time. A shared upstream cause is the simpler explanation for both numbers.

**Suggested:** treat F8's interpretation as unsafe until this is separated. The
next measurement should hold routing constant and vary only session count, so
availability and routing stop being confounded. If availability is the real
cause, better keywords cannot fix anything, and the honest README guidance —
type the slash command — is right for a different reason than stated.
