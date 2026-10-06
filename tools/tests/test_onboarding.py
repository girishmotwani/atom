"""Tests for the self-contained onboarding bundle installed by `atom init`."""

from __future__ import annotations

import json
from pathlib import Path

from atom.cli import main


def test_init_infers_module_and_installs_local_instructions(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "go.mod").write_text(
        "module example.com/target\n\ngo 1.23.0\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    bundle = tmp_path / ".atom" / "atom"
    assert json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))[
        "managed_by"
    ] == "atom init"
    assert (bundle / "AGENTS.md").is_file()
    assert (bundle / "skills" / "poc" / "SKILL.md").is_file()
    assert (bundle / "skills" / "atom" / "references" / "verification.md").is_file()

    instructions = (tmp_path / ".github" / "copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    assert "Read [Atom's local instructions](../.atom/atom/AGENTS.md)" in instructions
    assert "C:\\Users\\" not in instructions
    assert "verification.md" not in instructions


def test_init_updates_existing_instructions_once(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    instructions_path = tmp_path / ".github" / "copilot-instructions.md"
    instructions_path.parent.mkdir()
    instructions_path.write_text("# Existing instructions\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0
    first = instructions_path.read_text(encoding="utf-8")
    assert main(["init", "--force"]) == 0
    second = instructions_path.read_text(encoding="utf-8")

    assert first == second
    assert second.count("Atom managed onboarding") == 1


def test_init_removes_legacy_external_atom_references(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    instructions_path = tmp_path / ".github" / "copilot-instructions.md"
    instructions_path.parent.mkdir()
    instructions_path.write_text(
        "# Existing instructions\n"
        "Read Atom at ..\\..\\atom\\AGENTS.md and its skills/atom directory.\n"
        "Keep this developer instruction.\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    instructions = instructions_path.read_text(encoding="utf-8")
    assert "..\\..\\atom\\AGENTS.md" not in instructions
    assert "skills/atom" not in instructions
    assert "Keep this developer instruction." in instructions
    assert ".atom/atom/AGENTS.md" in instructions


def test_init_requires_module_when_go_mod_is_absent(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) != 0
    assert "no go.mod found" in capsys.readouterr().err
