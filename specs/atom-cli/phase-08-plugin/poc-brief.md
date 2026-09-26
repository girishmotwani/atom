---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
---

# POC Brief — Phase 8

## Problem

The developer's words: *"we went the wrong direction with the user experience.
we need the user to just run one atom command to inject the atom skills and
scripts into a repo. after that ... the atom family of commands should be part
of the copilot cli similar to allow-all or experimental or model."*

## Falsifiable question

Can Atom ship as a single Agent Plugins 1.0 plugin such that one install gives a
developer Atom's skills **and** `/atom-*` slash commands inside Copilot CLI —
with no bespoke injection step and no relocation of `skills/atom-*/`?

## Scope

- A throwaway plugin containing one skill, one command, one agent.
- Install it, and observe what Copilot CLI actually registers.
- Repeat the decisive checks against the **real** Atom repository.

## Non-goals

- Measuring how reliably a model picks the right beat from free text.
- Installing from a GitHub remote.
- Bundling the Python package with the plugin.

## Acceptance

Confirmed when a plugin installs, its plugin-root `skills/` are discovered, and
a `com.github.copilot/commands/` file produces a working slash command. Refuted
if skills need relocating or commands do not register.

Thresholds were fixed in
[claims.md](../../../poc/copilot-plugin-surface/claims.md) before the first
install and were not changed afterwards.

## Prior belief, recorded before running

That a command file would be required for every beat, and that Atom's skills
would need moving into `.github/skills/`. **Both were wrong** — see the
[POC report](poc-report.md).
