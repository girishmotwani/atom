"""Repeat onboarding must never reset the existing project implicitly."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from atom import cli, storage
from atom.eventlog import EventLog
from atom.onboarding import (
    GITIGNORE_BLOCK_END,
    GITIGNORE_BLOCK_START,
    INSTRUCTIONS_LINE,
    MANAGED_MARKER,
)
from atom.state import Project


def snapshot(root: Path) -> dict[Path, tuple[bool, int | None, int, bytes | None]]:
    return {
        path.relative_to(root): (
            path.is_dir(),
            path.stat().st_size if path.is_file() else None,
            path.stat().st_mtime_ns,
            path.read_bytes() if path.is_file() else None,
        )
        for path in [root, *sorted(root.rglob("*"))]
    }


@pytest.fixture
def initialized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    assert cli.main(["init", "--module", "example.com/target"]) == 0
    Project(tmp_path).record_approval(
        phase="phase-01-proof", gate="design-spec", date="2026-10-17"
    )
    return tmp_path


def forbid_initialization(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args, **kwargs):
        pytest.fail("repeat init must not check, detect, install, write, or append events")

    for name in ("run_check", "detect", "install_local_bundle", "write_json"):
        monkeypatch.setattr(cli, name, forbidden)
    monkeypatch.setattr(Project, "initialise", forbidden)
    monkeypatch.setattr(EventLog, "append", forbidden)
    monkeypatch.setattr(storage, "write_json", forbidden)
    monkeypatch.setattr(storage, "sweep_temp_files", forbidden)


@pytest.mark.parametrize("explicit_module", [False, True])
def test_matching_repeat_is_a_read_only_success(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    explicit_module: bool,
) -> None:
    (initialized / "go.mod").write_text("module example.com/target\n", encoding="utf-8")
    config_path = initialized / ".atom" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config.update(
        build_command="custom-build --tags production",
        test_command="custom-test --all",
        roles={"reviewer": {"capability": "independent-critique"}},
    )
    storage.write_json(config_path, config)
    before = snapshot(initialized)
    capsys.readouterr()
    forbid_initialization(monkeypatch)
    arguments = ["init"]
    if explicit_module:
        arguments += ["--module", "example.com/target"]

    for _ in range(2):
        assert cli.main(arguments) == 0
        captured = capsys.readouterr()
        assert "already initialised" in captured.out.lower()
        assert "no changes made" in captured.out.lower()
        assert captured.err == ""
        assert snapshot(initialized) == before


@pytest.mark.parametrize("missing", ["config.json", "state.json"])
def test_partial_initialization_is_refused_without_writes(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    missing: str,
) -> None:
    (initialized / ".atom" / missing).unlink()
    before = snapshot(initialized)
    capsys.readouterr()
    forbid_initialization(monkeypatch)

    assert cli.main(["init", "--module", "example.com/target"]) == 2

    captured = capsys.readouterr()
    assert missing in captured.err
    assert "No changes made" in captured.err
    assert "--force" in captured.err
    assert "discard recorded approvals" in captured.err
    assert captured.out == ""
    assert snapshot(initialized) == before


@pytest.mark.parametrize("directory", [True, False])
def test_existing_atom_entry_is_not_a_fresh_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    directory: bool,
) -> None:
    monkeypatch.chdir(tmp_path)
    atom_path = tmp_path / ".atom"
    if directory:
        atom_path.mkdir()
    else:
        atom_path.write_text("existing data\n", encoding="utf-8")
    before = snapshot(tmp_path)

    assert cli.main(["init", "--module", "example.com/target"]) == 2

    assert ".atom" in capsys.readouterr().err
    assert snapshot(tmp_path) == before


def assert_refused(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    problem: str,
    *arguments: str,
) -> None:
    before = snapshot(root)
    capsys.readouterr()
    forbid_initialization(monkeypatch)

    assert cli.main(["init", *arguments]) == 2

    captured = capsys.readouterr()
    assert problem in captured.err
    assert "No changes made" in captured.err
    assert "--force" in captured.err
    assert "discard recorded approvals" in captured.err
    assert captured.out == ""
    assert snapshot(root) == before


@pytest.mark.parametrize("field", ["module_path", "build_command", "test_command"])
@pytest.mark.parametrize("value", [None, 7, [], "", "   "])
def test_repeat_refuses_invalid_configuration_fields(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    field: str,
    value: object,
) -> None:
    config_path = initialized / ".atom" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config[field] = value
    storage.write_json(config_path, config)

    assert_refused(initialized, monkeypatch, capsys, field)


@pytest.mark.parametrize("field", ["module_path", "build_command", "test_command"])
def test_repeat_refuses_missing_configuration_fields(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    field: str,
) -> None:
    config_path = initialized / ".atom" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    del config[field]
    storage.write_json(config_path, config)

    assert_refused(initialized, monkeypatch, capsys, field)


@pytest.mark.parametrize("filename", ["config.json", "state.json"])
@pytest.mark.parametrize("contents", ["{", "[]", "\ufffd"])
def test_repeat_refuses_damaged_json_records(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    filename: str,
    contents: str,
) -> None:
    (initialized / ".atom" / filename).write_text(contents, encoding="utf-8")

    assert_refused(initialized, monkeypatch, capsys, filename)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"phase": "poc", "status": "not_started"},
        {"version": 2},
        {"version": 2, "approvals": None},
        {"version": 2, "approvals": [{}]},
        {"version": 2, "approvals": ["not an approval"]},
        {"version": 2, "approvals": [{"phase": 7, "gate": "spec", "date": "today"}]},
        {"approvals": []},
        {"version": 1, "approvals": []},
        {"version": 3, "approvals": []},
        {"version": True, "approvals": []},
        {"version": 2.0, "approvals": []},
        {"version": "2", "approvals": []},
    ],
)
def test_repeat_refuses_invalid_state_records(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    payload: dict,
) -> None:
    storage.write_json(initialized / ".atom" / "state.json", payload)

    assert_refused(initialized, monkeypatch, capsys, "state.json")


@pytest.mark.parametrize(
    ("go_mod", "arguments", "problem"),
    [
        (None, ["--module", "example.com/other"], "--module"),
        ("module example.com/other\n", [], "go.mod"),
        ("module example.com/other\n", ["--module", "example.com/target"], "go.mod"),
        ("module example.com/target\n", ["--module", "example.com/other"], "--module"),
        ("go 1.23.0\n", [], "go.mod"),
    ],
)
def test_repeat_refuses_module_conflicts(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    go_mod: str | None,
    arguments: list[str],
    problem: str,
) -> None:
    if go_mod is not None:
        (initialized / "go.mod").write_text(go_mod, encoding="utf-8")

    assert_refused(initialized, monkeypatch, capsys, problem, *arguments)


@pytest.mark.parametrize(
    "relative_path",
    [Path(".atom") / "config.json", Path(".atom") / "state.json", Path("go.mod")],
)
def test_repeat_reports_record_read_failures(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    relative_path: Path,
) -> None:
    target = initialized / relative_path
    if relative_path.name == "go.mod":
        target.write_text("module example.com/target\n", encoding="utf-8")
    original_read = Path.read_text

    def denied_read(path: Path, *args, **kwargs):
        if path == target:
            raise PermissionError(f"cannot read {path}")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", denied_read)

    assert_refused(initialized, monkeypatch, capsys, target.name)


REQUIRED_BUNDLE_FILES = [
    Path("AGENTS.md"),
    *(
        Path("skills") / name / "SKILL.md"
        for name in ("init", "discover", "poc", "plan", "spec", "tdd", "review", "ship")
    ),
    *(
        Path("skills") / "atom" / "references" / name
        for name in (
            "anti-rationalization.md",
            "poc-discipline.md",
            "tdd-discipline.md",
            "go-style.md",
            "human-gates.md",
            "verification.md",
            "model-guidance.md",
        )
    ),
]


@pytest.mark.parametrize("relative_path", REQUIRED_BUNDLE_FILES)
@pytest.mark.parametrize("damage", ["missing", "empty"])
def test_repeat_refuses_incomplete_bundle_files(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    relative_path: Path,
    damage: str,
) -> None:
    target = initialized / ".atom" / "atom" / relative_path
    if damage == "missing":
        target.unlink()
    else:
        target.write_text(" \n", encoding="utf-8")

    assert_refused(initialized, monkeypatch, capsys, target.name)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"managed_by": "other", "source": "atom-cli package", "files": ["AGENTS.md", "skills/"]},
        {"managed_by": "atom init", "source": "other", "files": ["AGENTS.md", "skills/"]},
        {"managed_by": "atom init", "source": "atom-cli package", "files": ["AGENTS.md"]},
        {"managed_by": "atom init", "source": "atom-cli package", "files": "AGENTS.md skills/"},
        {"managed_by": "atom init", "source": "atom-cli package", "files": ["AGENTS.md", "skills/", 7]},
    ],
)
def test_repeat_refuses_invalid_bundle_manifest(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    payload: dict,
) -> None:
    storage.write_json(initialized / ".atom" / "atom" / "manifest.json", payload)

    assert_refused(initialized, monkeypatch, capsys, "manifest.json")


@pytest.mark.parametrize("contents", [None, "{", "[]", "\ufffd"])
def test_repeat_refuses_damaged_bundle_manifest(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    contents: str | None,
) -> None:
    manifest = initialized / ".atom" / "atom" / "manifest.json"
    if contents is None:
        manifest.unlink()
    else:
        manifest.write_text(contents, encoding="utf-8")

    assert_refused(initialized, monkeypatch, capsys, "manifest.json")


@pytest.mark.parametrize("contents", [None, "", MANAGED_MARKER, "../.atom/atom/AGENTS.md"])
def test_repeat_refuses_missing_local_instruction_reference(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    contents: str | None,
) -> None:
    instructions = initialized / ".github" / "copilot-instructions.md"
    if contents is None:
        instructions.unlink()
    else:
        instructions.write_text(contents, encoding="utf-8")

    assert_refused(initialized, monkeypatch, capsys, "copilot-instructions.md")


@pytest.mark.parametrize(
    "contents",
    [
        None,
        "",
        f"{GITIGNORE_BLOCK_START}\n.atom/baseline.json\n",
        f"{GITIGNORE_BLOCK_END}\n{GITIGNORE_BLOCK_START}\n",
        f"{GITIGNORE_BLOCK_START}\n{GITIGNORE_BLOCK_START}\n{GITIGNORE_BLOCK_END}\n",
        f"{GITIGNORE_BLOCK_START}\n{GITIGNORE_BLOCK_END}\n",
        (
            f"{GITIGNORE_BLOCK_START}\n.atom/baseline.json\n.atom/events.jsonl\n"
            f"{GITIGNORE_BLOCK_END}\n"
        ),
    ],
)
def test_repeat_refuses_incomplete_managed_ignore_rules(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    contents: str | None,
) -> None:
    gitignore = initialized / ".gitignore"
    if contents is None:
        gitignore.unlink()
    else:
        gitignore.write_text(contents, encoding="utf-8")

    assert_refused(initialized, monkeypatch, capsys, ".gitignore")


@pytest.mark.parametrize(
    "relative_path",
    [
        Path(".atom") / "atom" / "AGENTS.md",
        Path(".atom") / "atom" / "manifest.json",
        Path(".github") / "copilot-instructions.md",
        Path(".gitignore"),
    ],
)
def test_repeat_reports_scaffold_read_failures(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    relative_path: Path,
) -> None:
    target = initialized / relative_path
    original_read = Path.read_text

    def denied_read(path: Path, *args, **kwargs):
        if path == target:
            raise PermissionError(f"cannot read {path}")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", denied_read)

    assert_refused(initialized, monkeypatch, capsys, target.name)


@pytest.mark.parametrize("runtime_files", ["absent", "unusable"])
def test_repeat_does_not_require_or_inspect_machine_local_files(
    initialized: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    runtime_files: str,
) -> None:
    for name in ("baseline.json", "events.jsonl", "events.lock"):
        path = initialized / ".atom" / name
        if runtime_files == "absent":
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(b"\xffnot JSON or a usable event log")
    (initialized / "specs").rmdir()
    (initialized / "poc").rmdir()
    (initialized / ".atom" / "atom" / "AGENTS.md").write_text(
        "# Older complete bundle, intentionally customized\n", encoding="utf-8"
    )
    instructions = initialized / ".github" / "copilot-instructions.md"
    instructions.write_text("# Developer rules\n\n" + INSTRUCTIONS_LINE, encoding="utf-8")
    before = snapshot(initialized)
    forbid_initialization(monkeypatch)
    capsys.readouterr()

    assert cli.main(["init"]) == 0

    assert capsys.readouterr().err == ""
    assert snapshot(initialized) == before


def test_repeat_succeeds_as_a_real_process(initialized: Path) -> None:
    before = snapshot(initialized)

    for arguments in (["init"], ["init", "--module", "example.com/target"]):
        result = subprocess.run(
            [sys.executable, "-m", "atom.cli", *arguments],
            cwd=initialized,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert "no changes made" in result.stdout.lower()
        assert result.stderr == ""
        assert snapshot(initialized) == before


def test_force_still_resets_a_partial_project(initialized: Path) -> None:
    (initialized / ".atom" / "config.json").unlink()
    (initialized / ".atom" / "atom" / "manifest.json").write_text("{", encoding="utf-8")

    assert cli.main(["init", "--module", "example.com/replacement", "--force"]) == 0

    loaded = Project(initialized).load()
    assert loaded.problems == []
    assert loaded.state.module_path == "example.com/replacement"
    assert loaded.state.approvals == []


def test_init_help_explains_no_op_and_destructive_force(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as exited:
        cli.main(["init", "--help"])

    assert exited.value.code == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert "read-only no-op" in help_text
    assert "recorded approvals" in help_text
