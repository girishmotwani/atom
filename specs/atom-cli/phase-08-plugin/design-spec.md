---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
status: "implemented"
poc_report: "poc-report.md"
---

# Design Spec — Phase 8: Atom as a Copilot CLI plugin

## Purpose

Before this phase, using Atom meant installing a Python package and then relying
on an agent to notice `AGENTS.md`. There was no way to *ask* for a beat. The
developer had to know Atom's vocabulary and describe it in prose.

This phase makes Atom's beats first-class Copilot CLI commands — `/atom-poc`
next to `/model` — and adds one natural-language entry point, `/atom`, that
takes a plain description of what someone wants to build and routes it to the
earliest beat whose output is missing.

## Evidence Base

[POC Report — Phase 8](poc-report.md). The design follows directly from its six
"take as given" findings; the two that shaped it most are that **skills are
already slash commands** (so almost no new code was needed) and that **name
collisions fail silently** (so they must be caught by a test, not by review).

## Command Surface

Installation, both commands supported by the CLI's own deprecation policy:

```
copilot plugin marketplace add girishmotwani/atom
copilot plugin install atom-go@atom
```

This is global. There is no per-repository step.

| Command | Source | Beat |
|---|---|---|
| `/atom` | `com.github.copilot/commands/atom.md` | Entry point and router |
| `/atom-discover` | `skills/atom-discover/` | Scope a falsifiable question |
| `/atom-poc` | `skills/atom-poc/` | Build the disposable spike |
| `/atom-spec` | `skills/atom-spec/` | Design spec from the verdict |
| `/atom-tdd` | `skills/atom-tdd/` | Test spec, then red-green |
| `/atom-review` | `skills/atom-review/` | Multi-model review |
| `/atom-ship` | `skills/atom-ship/` | Commit, branch, PR |
| `/atom-plan` | `skills/atom-plan/` | Break into phases |
| `/atom-init` | `skills/atom-init/` | Scaffold project state |
| `/atom-status` | `com.github.copilot/commands/atom-status.md` | Report phase and missing artifacts |
| `/atom-check` | `com.github.copilot/commands/atom-check.md` | Run the Go quality gates |
| `/atom-build` | `skills/atom-build/` | The whole loop |

Only `/atom`, `/atom-status` and `/atom-check` required new files. Every other
row already existed as a skill and became a command by virtue of the plugin
manifest. `atom status` and `atom check` are CLI subcommands rather than beats,
so they have no skill to inherit from and needed command files of their own.

## Artifacts added

| Path | Role |
|---|---|
| `plugin.json` | Agent Plugins 1.0 manifest. Name `atom-go`. |
| `.github/plugin/marketplace.json` | Marketplace `atom`, listing `atom-go` with `source: "."`. |
| `com.github.copilot/commands/atom.md` | The `/atom` router. |
| `com.github.copilot/commands/atom-status.md` | `/atom-status`, wrapping `atom status`. |
| `com.github.copilot/commands/atom-check.md` | `/atom-check`, wrapping `atom check`. |
| `tools/tests/test_plugin.py` | Guards the silent-collision failure mode. |

## Behaviours

1. `/atom <description>` establishes current state before routing: it looks for
   `.atom/`, runs `atom status` when present, and reads `specs/` and `poc/`.
2. `/atom` with no argument, outside an Atom project, asks exactly one question —
   what the user wants to build — and then continues.
3. `/atom` routes to exactly one beat: the earliest whose output is missing. It
   never skips ahead.
4. `/atom` announces the beat and the reason in one line before acting.
5. When routing to discovery or POC, the interview proceeds **one question at a
   time** and will not accept a goal without an observable outcome.
6. Thresholds are agreed before the spike runs and are not moved afterwards.
7. Every `/atom` response ends with a literal next slash command, or an explicit
   statement that the work is done.

## Why the plugin is named `atom-go`

A plugin named `atom` would shadow a skill named `atom`. `skills/atom/` is
currently a shared assets directory with no `SKILL.md`, so nothing breaks today —
but naming the plugin `atom` would permanently prevent an `atom` skill from ever
loading. `atom-go` also states the framework's scope. The marketplace keeps the
short name `atom`, so the install line reads `atom-go@atom`.

## Trade-offs

| Decision | Alternative | Why |
|---|---|---|
| Ship as a plugin | Per-repo symlink injection, as Helios does | Install once, works in every repo; nothing to commit into the user's project |
| Skills as the command surface | A command file per beat | Skills win collisions anyway; duplicating them would create nine silent no-ops |
| One `/atom` router | Rely on prose matching `AGENTS.md` | A slash command is discoverable; prose matching is not |
| Marketplace install | `copilot plugin install owner/repo` | Direct installs are deprecated by the CLI |
| Test the collision rule | Rely on review | The failure prints no warning; only a test catches it |

## Known gaps

- The Python `atom` package is still a **separate** install. A plugin cannot
  carry a pip dependency, so `pip install -e ./tools` remains a second step.
- **Free-text routing reaches the right beat reliably once the plugin is
  installed.** Measured at 100% over 25 scored trials, with zero mis-routes. An
  earlier 33.3% figure was an artifact of live-loading the plugin, which drops
  it silently in some sessions and leaves nothing to route to. Slash commands
  remain the exact interface when a developer wants no ambiguity. See
  [the routing POC](../../../poc/atom-routing-rules/results.md).
- **`com.github.copilot/rules/` does nothing in CLI 1.0.89-4**, despite being a
  documented component location. It was the obvious fix for the gap above and
  was refuted under five conditions against a working control. No rules file is
  shipped.
- The marketplace has only been exercised from a local path, never from GitHub.
