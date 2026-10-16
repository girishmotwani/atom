"""Tests for the self-contained onboarding bundle installed by `atom init`."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from atom import cli
from atom.check import CheckReport
from atom.cli import main
from atom.gates import GateResult, GateStatus
from atom import onboarding
from atom.onboarding import GITIGNORE_BLOCK_END, GITIGNORE_BLOCK_START


@pytest.fixture(autouse=True)
def deterministic_baseline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep onboarding unit tests fast while preserving the baseline contract."""

    def passing_check(directory: Path, gates, runner) -> CheckReport:
        results = tuple(
            GateResult(
                name=gate.name,
                status=(
                    GateStatus.SKIPPED
                    if gate.name == "race"
                    else GateStatus.PASSED
                ),
                summary=(
                    "Race detector disabled for this run"
                    if gate.name == "race"
                    else f"{gate.name} passed"
                ),
                details="",
                required=gate.required,
                duration_seconds=0.0,
            )
            for gate in gates
        )
        return CheckReport(
            directory=directory,
            gate_results=results,
            warnings=(),
            total_duration_seconds=0.0,
        )

    monkeypatch.setattr(cli, "run_check", passing_check)


def test_init_records_the_makefile_commands_it_will_actually_run(
    tmp_path: Path, monkeypatch
) -> None:
    """A repository that declares its own build must not be told it runs go build."""

    monkeypatch.setattr("atom.buildsystem.shutil.which", lambda name: "/usr/bin/make")
    (tmp_path / "go.mod").write_text(
        "module example.com/target\n\ngo 1.23.0\n", encoding="utf-8"
    )
    (tmp_path / "Makefile").write_text(
        "build:\n\tgo build -tags prod ./...\ntest:\n\tgo test -count=1 ./...\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    config = json.loads((tmp_path / ".atom" / "config.json").read_text(encoding="utf-8"))
    assert config["build_command"] == "make build"
    assert config["test_command"] == "make test"


def test_init_records_a_partial_makefile_one_gate_at_a_time(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr("atom.buildsystem.shutil.which", lambda name: "/usr/bin/make")
    (tmp_path / "go.mod").write_text(
        "module example.com/target\n\ngo 1.23.0\n", encoding="utf-8"
    )
    (tmp_path / "Makefile").write_text("build:\n\tgo build ./...\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    config = json.loads((tmp_path / ".atom" / "config.json").read_text(encoding="utf-8"))
    assert config["build_command"] == "make build"
    assert config["test_command"] == "go test ./..."


def test_init_infers_module_and_installs_local_instructions(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "go.mod").write_text(
        "module example.com/target\n\ngo 1.23.0\n", encoding="utf-8"
    )
    (tmp_path / "target.go").write_text(
        "package target\n\nfunc Value() string { return \"ok\" }\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    config = json.loads(
        (tmp_path / ".atom" / "config.json").read_text(encoding="utf-8")
    )
    assert config == {
        "build_command": "go build ./...",
        "module_path": "example.com/target",
        "test_command": "go test ./...",
    }
    baseline = json.loads(
        (tmp_path / ".atom" / "baseline.json").read_text(encoding="utf-8")
    )
    assert baseline["passed"] is True
    assert {gate["name"] for gate in baseline["gates"]} == {
        "build",
        "fmt",
        "race",
        "test",
        "vet",
    }
    assert next(gate for gate in baseline["gates"] if gate["name"] == "race")[
        "status"
    ] == "skipped"
    assert (tmp_path / "specs").is_dir()
    assert (tmp_path / "poc").is_dir()

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


def test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command() -> None:
    repository_root = Path(__file__).parents[2]
    source = (repository_root / "skills" / "init" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    packaged = (
        repository_root
        / "tools"
        / "atom"
        / "assets"
        / "skills"
        / "init"
        / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert source == packaged
    assert "atom init" in source
    assert "runs the untouched no-race baseline before writing Atom files" in source
    assert "atom check --no-race" not in source
    assert "Do not run `git status`, recursive shell scans" in source
    assert "Do not locate or read Atom's Python source" in source
    assert "Existing `.atom/` files do not require an implementation audit" in source


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


def test_init_ignores_only_generated_atom_runtime_files(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    subprocess.run(["git", "init", "--quiet"], cwd=tmp_path, check=True)
    (tmp_path / ".atom").mkdir()
    (tmp_path / ".atom" / "events.jsonl").write_text("", encoding="utf-8")
    subprocess.run(
        ["git", "add", ".atom/events.jsonl"], cwd=tmp_path, check=True
    )
    index_before = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    ignored = subprocess.run(
        [
            "git",
            "-c",
            "core.excludesFile=",
            "check-ignore",
            "--no-index",
            ".atom/baseline.json",
            ".atom/events.jsonl",
            ".atom/events.lock",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    shared = subprocess.run(
        [
            "git",
            "-c",
            "core.excludesFile=",
            "check-ignore",
            "--no-index",
            ".atom/config.json",
            ".atom/state.json",
            ".atom/atom/AGENTS.md",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert ignored.returncode == 0
    assert set(ignored.stdout.splitlines()) == {
        ".atom/baseline.json",
        ".atom/events.jsonl",
        ".atom/events.lock",
    }
    assert shared.returncode == 1
    assert shared.stdout == ""
    index_after = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert index_after == index_before


def test_init_preserves_existing_gitignore_and_updates_it_once(
    tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    gitignore = tmp_path / ".gitignore"
    existing = b"# Developer rules\nvendor/\n"
    gitignore.write_bytes(existing)
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0
    first = gitignore.read_bytes()
    assert first.startswith(existing)
    assert main(["init", "--force"]) == 0
    second = gitignore.read_bytes()

    assert first == second
    assert second.count(GITIGNORE_BLOCK_START.encode()) == 1
    assert second.count(GITIGNORE_BLOCK_END.encode()) == 1


def test_init_replaces_stale_atom_gitignore_block(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(
        "# Before\n"
        f"{GITIGNORE_BLOCK_START}\n"
        ".atom/obsolete.json\n"
        f"{GITIGNORE_BLOCK_END}\n"
        "# After\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    contents = gitignore.read_text(encoding="utf-8")
    assert contents.startswith("# Before\n")
    assert contents.endswith("# After\n")
    assert ".atom/obsolete.json" not in contents
    assert ".atom/baseline.json" in contents


def test_init_preserves_existing_gitignore_newlines(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    gitignore = tmp_path / ".gitignore"
    gitignore.write_bytes(b"# Developer rules\r\nvendor/\r\n")
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0

    contents = gitignore.read_bytes()
    assert b"\r\n" in contents
    assert contents.replace(b"\r\n", b"").find(b"\n") == -1


@pytest.mark.parametrize(
    "managed_section",
    [
        (
            f"{GITIGNORE_BLOCK_START}\n"
            ".atom/first.json\n"
            f"{GITIGNORE_BLOCK_START}\n"
            ".atom/second.json\n"
            f"{GITIGNORE_BLOCK_END}\n"
        ),
        f"{GITIGNORE_BLOCK_START}\n.atom/first.json\n",
        f"{GITIGNORE_BLOCK_END}\n.atom/first.json\n",
        f"{GITIGNORE_BLOCK_END}\n{GITIGNORE_BLOCK_START}\n",
    ],
)
def test_init_refuses_ambiguous_atom_gitignore_markers(
    tmp_path: Path, monkeypatch, capsys, managed_section: str
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    gitignore = tmp_path / ".gitignore"
    original = "# Developer rule\n" + managed_section
    gitignore.write_text(original, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) != 0
    error = capsys.readouterr().err
    assert "managed .gitignore markers" in error
    assert "atom init --force" in error
    assert gitignore.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    ("existing", "separator"),
    [
        (b"vendor/", b"\n\n"),
        (b"vendor/\n\n", b""),
    ],
)
def test_init_separates_the_managed_block_without_changing_existing_content(
    tmp_path: Path, monkeypatch, existing: bytes, separator: bytes
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    gitignore = tmp_path / ".gitignore"
    gitignore.write_bytes(existing)
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) == 0
    first = gitignore.read_bytes()
    assert first.startswith(existing + separator + GITIGNORE_BLOCK_START.encode())
    assert main(["init", "--force"]) == 0
    assert gitignore.read_bytes() == first


def test_gitignore_update_keeps_original_when_atomic_replace_fails(
    tmp_path: Path, monkeypatch
) -> None:
    gitignore = tmp_path / ".gitignore"
    original = b"# Developer rule\nvendor/\n"
    gitignore.write_bytes(original)

    def fail_replace(source: Path, destination: Path) -> None:
        raise PermissionError("held open")

    monkeypatch.setattr(onboarding.os, "replace", fail_replace)

    with pytest.raises(onboarding.OnboardingError) as raised:
        onboarding._install_gitignore_rules(tmp_path)

    assert "could not update" in str(raised.value)
    assert "atom init --force" in str(raised.value)
    assert gitignore.read_bytes() == original
    assert list(tmp_path.glob(".gitignore.atom-*.tmp")) == []


def test_init_reports_an_unreadable_gitignore_without_a_traceback(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    (tmp_path / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_bytes(b"\xff")
    monkeypatch.chdir(tmp_path)

    assert main(["init"]) != 0
    error = capsys.readouterr().err
    assert "could not read" in error
    assert "atom init --force" in error
    assert "Traceback" not in error
