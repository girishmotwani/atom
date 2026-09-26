---
project: "atom-cli"
phase: "phase-08-plugin"
date: "2026-09-26"
---

# Test Spec — Phase 8

Tests for `tools/tests/test_plugin.py`. All are Tier 1: they assert facts about
the real repository, because the artifacts under test are the real manifests.

## What is worth testing here

Almost nothing in this phase is code. The risk is not a wrong branch; it is a
**silent misconfiguration**. The spike measured two failure modes that produce
no warning at all:

- a command whose name matches a skill is shadowed by that skill;
- a command whose name matches the plugin never runs.

In both cases install succeeds, the CLI reports no error, and the command simply
does the wrong thing. Only a test catches that.

## Cases

| # | Test | Asserts | Priority |
|---|---|---|---|
| 1 | `test_the_plugin_manifest_declares_agent_plugins_1_0` | `$schema` is the Agent Plugins 1.0 URL, so the CLI uses 1.0 discovery rather than legacy | High |
| 2 | `test_the_plugin_manifest_uses_only_allowed_fields` | No extra top-level field, which the CLI reports and ignores | High |
| 3 | `test_no_command_shares_a_name_with_a_skill` | No command is shadowed by a skill | Critical |
| 4 | `test_no_command_shares_a_name_with_the_plugin` | No command is shadowed by the plugin name | Critical |
| 5 | `test_no_skill_shares_a_name_with_the_plugin` | No skill is shadowed by the plugin name | Critical |
| 6 | `test_the_marketplace_lists_the_plugin_by_its_manifest_name` | Marketplace entry and manifest agree, so `install name@market` resolves | High |
| 7 | `test_the_marketplace_sources_the_repository_root` | `source` stays `"."`, so the repo remains the plugin | Medium |
| 8 | `test_every_atom_skill_directory_is_discoverable` | Every skill directory except the shared-assets `atom/` has a `SKILL.md` | High |

## Cases deliberately not written

- **That `/atom-poc` actually invokes the skill.** This needs a live Copilot CLI
  and a paid model call. It was verified by hand during the spike and recorded
  verbatim in the POC report, but it is not suitable for the suite.
- **That the model routes free text to the right beat.** Unmeasured; see
  `findings.md` and the POC report's "Not proven".

## Falsifiability check

Cases 3 and 4 were mutation-tested. Adding `commands/atom-poc.md` made case 3
fail with `the skill wins and these commands never run: ['atom-poc']`; adding
`commands/atom-go.md` made case 4 fail with `a command named 'atom-go' never
runs; rename it`. Removing both restored green.
