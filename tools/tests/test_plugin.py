"""Tier 1 checks on the Copilot CLI plugin manifest shipped at the repo root.

These assert facts about the real repository, not about a fixture. They exist
because plugin and skill names directly determine the slash-command surface,
and naming regressions otherwise install successfully while exposing the wrong
commands.

Measured behaviour (see poc/atom-short-namespace/results.md):

  - plugin `atom` + skill `poc` -> `/atom:poc`
  - an installed command named `atom` shadows `/atom:<skill>`
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_MANIFEST = REPO_ROOT / "plugin.json"
MARKETPLACE_MANIFEST = REPO_ROOT / ".github" / "plugin" / "marketplace.json"
SKILLS_ROOT = REPO_ROOT / "skills"
COMMANDS_ROOT = REPO_ROOT / "com.github.copilot" / "commands"

AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
EXPECTED_SHORT_SKILLS = {
    "build",
    "discover",
    "init",
    "plan",
    "poc",
    "review",
    "ship",
    "spec",
    "tdd",
}

# Agent Plugins 1.0 allows only these top-level manifest fields. Anything else
# is reported and ignored by the CLI, which is easy to miss.
ALLOWED_MANIFEST_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}


def _plugin_manifest():
    return json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))


def _skill_names():
    """Names Copilot CLI will discover, i.e. directories holding a SKILL.md.

    `skills/atom/` deliberately holds shared references and templates and has
    no SKILL.md, so it is not a skill and must not be counted as one.
    """
    return {
        directory.name
        for directory in SKILLS_ROOT.iterdir()
        if directory.is_dir() and (directory / "SKILL.md").is_file()
    }


def _command_names():
    if not COMMANDS_ROOT.is_dir():
        return set()
    names = set()
    for path in COMMANDS_ROOT.glob("*.md"):
        # Both `name.md` and `name.prompt.md` register the command `/name`.
        stem = path.name[: -len(".md")]
        if stem.endswith(".prompt"):
            stem = stem[: -len(".prompt")]
        names.add(stem)
    return names


def test_the_plugin_manifest_declares_agent_plugins_1_0():
    assert _plugin_manifest()["$schema"] == AGENT_PLUGINS_SCHEMA


def test_the_plugin_manifest_uses_only_allowed_fields():
    unexpected = set(_plugin_manifest()) - ALLOWED_MANIFEST_FIELDS
    assert unexpected == set(), f"ignored by the CLI: {sorted(unexpected)}"


def test_no_command_shares_a_name_with_a_skill():
    clashes = _command_names() & _skill_names()
    assert clashes == set(), (
        f"the skill wins and these commands never run: {sorted(clashes)}"
    )


def test_the_plugin_owns_the_atom_command_namespace():
    assert _plugin_manifest()["name"] == "atom"


def test_no_command_shares_a_name_with_the_plugin():
    plugin_name = _plugin_manifest()["name"]
    assert plugin_name not in _command_names(), (
        f"the command shadows /{plugin_name}:<skill> after installation"
    )


def test_the_atom_router_is_available_as_start():
    assert "start" in _command_names()


def test_no_skill_shares_a_name_with_the_plugin():
    plugin_name = _plugin_manifest()["name"]
    assert plugin_name not in _skill_names(), (
        f"the skill {plugin_name!r} is shadowed by the plugin and will not load"
    )


def test_the_plugin_exposes_exactly_the_compact_skill_names():
    assert _skill_names() == EXPECTED_SHORT_SKILLS


def test_the_marketplace_lists_the_plugin_by_its_manifest_name():
    marketplace = json.loads(MARKETPLACE_MANIFEST.read_text(encoding="utf-8"))
    listed = {entry["name"] for entry in marketplace["plugins"]}
    assert _plugin_manifest()["name"] in listed


def test_the_marketplace_sources_the_repository_root():
    marketplace = json.loads(MARKETPLACE_MANIFEST.read_text(encoding="utf-8"))
    entry = next(
        item
        for item in marketplace["plugins"]
        if item["name"] == _plugin_manifest()["name"]
    )
    assert entry["source"] in {".", "./"}


def test_every_atom_skill_directory_is_discoverable():
    """A skill directory without SKILL.md loads nothing and warns nobody."""
    missing = [
        directory.name
        for directory in SKILLS_ROOT.iterdir()
        if directory.is_dir()
        and directory.name != "atom"
        and not (directory / "SKILL.md").is_file()
    ]
    assert missing == [], f"no SKILL.md in: {sorted(missing)}"
