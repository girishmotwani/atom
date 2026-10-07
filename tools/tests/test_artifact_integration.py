"""Integration contracts for the dedicated artifact-writer workflow."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from atom.cli import main

REPOSITORY = Path(__file__).resolve().parents[2]
ARTIFACT_SKILLS = ("discover", "poc", "plan", "spec", "tdd", "review")


def test_package_registers_only_the_dedicated_artifact_writer() -> None:
    project = tomllib.loads(
        (REPOSITORY / "tools" / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert project["project"]["scripts"]["atom-write-artifact"] == (
        "atom.artifact_cli:main"
    )


def test_main_atom_cli_does_not_expose_artifact_subcommand(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exited:
        main(["artifact"])

    assert exited.value.code == 2


@pytest.mark.parametrize("skill", ARTIFACT_SKILLS)
def test_artifact_producing_skills_use_dedicated_writer(skill: str) -> None:
    source = (REPOSITORY / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    packaged = (
        REPOSITORY / "tools" / "atom" / "assets" / "skills" / skill / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "atom-write-artifact" in source
    assert "atom-write-artifact" in packaged
    assert source == packaged


def test_artifact_writer_instruction_forbids_bypass_and_source_writes() -> None:
    for agents_path in (
        REPOSITORY / "AGENTS.md",
        REPOSITORY / "tools" / "atom" / "assets" / "AGENTS.md",
    ):
        instructions = agents_path.read_text(encoding="utf-8")
        assert "Never bypass an artifact-writer refusal" in instructions
        assert "never for production code" in instructions


def test_onboarding_installs_artifact_writer_instructions(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    installed_agents = (
        tmp_path / ".atom" / "atom" / "AGENTS.md"
    ).read_text(encoding="utf-8")
    installed_spec_skill = (
        tmp_path / ".atom" / "atom" / "skills" / "spec" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "atom-write-artifact" in installed_agents
    assert "atom-write-artifact" in installed_spec_skill


def test_onboarding_does_not_edit_copilot_permission_configuration(
    tmp_path: Path, monkeypatch
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "go.mod").write_text(
        "module example.com/target\n", encoding="utf-8"
    )
    user_home = tmp_path / "user-home"
    user_home.mkdir()
    monkeypatch.setenv("HOME", str(user_home))
    monkeypatch.setenv("USERPROFILE", str(user_home))
    monkeypatch.delenv("COPILOT_HOME", raising=False)
    monkeypatch.chdir(repository)

    assert main(["init"]) == 0

    assert not (user_home / ".copilot" / "permissions-config.json").exists()


def test_built_package_installs_working_dedicated_console_script(
    tmp_path: Path,
) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--quiet",
            "--no-deps",
            "--wheel-dir",
            str(wheelhouse),
            str(REPOSITORY / "tools"),
        ],
        check=True,
    )
    wheel = next(wheelhouse.glob("atom_cli-*.whl"))

    environment = tmp_path / "environment"
    subprocess.run([sys.executable, "-m", "venv", str(environment)], check=True)
    environment_python = (
        environment / "Scripts" / "python.exe"
        if os.name == "nt"
        else environment / "bin" / "python"
    )
    subprocess.run(
        [
            str(environment_python),
            "-m",
            "pip",
            "install",
            "--quiet",
            "--no-deps",
            str(wheel),
        ],
        check=True,
    )
    writer = (
        environment / "Scripts" / "atom-write-artifact.exe"
        if os.name == "nt"
        else environment / "bin" / "atom-write-artifact"
    )

    repository = tmp_path / "repository"
    repository.mkdir()
    allowed = subprocess.run(
        [str(writer), "specs/installed.md"],
        cwd=repository,
        input="# Installed\n".encode(),
        capture_output=True,
    )
    refused = subprocess.run(
        [str(writer), "internal/server.go"],
        cwd=repository,
        input=b"package internal\n",
        capture_output=True,
    )

    assert allowed.returncode == 0, allowed.stderr.decode()
    assert (repository / "specs" / "installed.md").read_text(
        encoding="utf-8"
    ) == "# Installed\n"
    assert refused.returncode == 1
    assert b"outside-artifact-set" in refused.stderr
    assert not (repository / "internal" / "server.go").exists()

    unicode_content = "café — 東京\r\n".encode("utf-8")
    unicode_write = subprocess.run(
        [str(writer), "specs/unicode.md"],
        cwd=repository,
        input=unicode_content,
        capture_output=True,
    )
    assert unicode_write.returncode == 0, unicode_write.stderr.decode()
    assert (repository / "specs" / "unicode.md").read_bytes() == (
        "café — 東京\n".encode("utf-8")
    )

    if os.name == "nt":
        powershell_command = (
            "$OutputEncoding = [System.Text.UTF8Encoding]::new($false)\n"
            "@'\n"
            "café — 東京\n"
            f"'@ | & '{writer}' 'specs/powershell.md'"
        )
        powershell_write = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                powershell_command,
            ],
            cwd=repository,
            capture_output=True,
        )
        assert powershell_write.returncode == 0, powershell_write.stderr.decode()
        assert (repository / "specs" / "powershell.md").read_bytes() == (
            "café — 東京\n".encode("utf-8")
        )
