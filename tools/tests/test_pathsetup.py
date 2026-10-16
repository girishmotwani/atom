"""Tests for opt-in Windows command discovery without changing the real PATH."""

from __future__ import annotations

import subprocess
import sys
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import sysconfig
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest

from atom.cli import main


@pytest.fixture
def windows_setup(tmp_path, monkeypatch):
    default_scripts = tmp_path / "default" / "Scripts"
    scripts = tmp_path / "user" / "Scripts"
    default_scripts.mkdir(parents=True)
    scripts.mkdir(parents=True)
    (scripts / "atom.exe").touch()
    (scripts / "atom-write-artifact.exe").touch()
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sysconfig, "get_preferred_scheme", lambda kind: "user")
    monkeypatch.setattr(
        sysconfig,
        "get_path",
        lambda name, scheme=None: str(
            default_scripts if scheme is None else scripts
        ),
    )
    registry = MagicMock(
        REG_SZ=1,
        REG_EXPAND_SZ=2,
        KEY_QUERY_VALUE=1,
        KEY_SET_VALUE=2,
    )
    registry.QueryValueEx.return_value = ("%SystemRoot%\\Keep;;", registry.REG_EXPAND_SZ)
    monkeypatch.setitem(sys.modules, "winreg", registry)
    broadcast = Mock(return_value=1)
    monkeypatch.setattr(
        ctypes,
        "WinDLL",
        Mock(return_value=SimpleNamespace(SendMessageTimeoutW=broadcast)),
        raising=False,
    )
    return SimpleNamespace(
        registry=registry,
        broadcast=broadcast,
        scripts=scripts,
        default_scripts=default_scripts,
    )


def test_setup_path_help_works_in_a_real_process(tmp_path) -> None:
    process = subprocess.run(
        [sys.executable, "-S", "-m", "atom.cli", "setup-path", "--help"],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1])),
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    assert "user PATH" in process.stdout
    assert list(tmp_path.iterdir()) == []


def test_setup_path_adds_commands_without_onboarding(
    windows_setup, tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    original = windows_setup.registry.QueryValueEx.return_value[0]

    assert main(["setup-path"]) == 0

    windows_setup.registry.SetValueEx.assert_called_once_with(
        windows_setup.registry.CreateKeyEx.return_value.__enter__.return_value,
        "Path",
        0,
        windows_setup.registry.REG_EXPAND_SZ,
        original + ";" + str(windows_setup.scripts),
    )
    windows_setup.broadcast.assert_called_once()
    output = capsys.readouterr().out
    assert "Added" in output
    assert str(windows_setup.scripts / "atom.exe") in output
    assert str(windows_setup.scripts / "atom-write-artifact.exe") in output
    assert "current" in output.lower()
    assert not (tmp_path / ".atom").exists()


@pytest.mark.parametrize(
    "existing_form",
    ["exact", "case", "quoted", "trailing-separator", "dot", "variable"],
)
def test_setup_path_does_not_rewrite_an_equivalent_entry(
    windows_setup, monkeypatch, capsys, existing_form
) -> None:
    scripts = str(windows_setup.scripts)
    monkeypatch.setenv("ATOM_TEST_SCRIPTS", scripts)
    forms = {
        "exact": scripts,
        "case": scripts.upper(),
        "quoted": f' "{scripts}" ',
        "trailing-separator": scripts + "\\",
        "dot": scripts + "\\.\\",
        "variable": "%ATOM_TEST_SCRIPTS%",
    }
    windows_setup.registry.QueryValueEx.return_value = (
        "C:\\keep;;" + forms[existing_form],
        windows_setup.registry.REG_EXPAND_SZ,
    )

    assert main(["setup-path"]) == 0

    windows_setup.registry.SetValueEx.assert_not_called()
    windows_setup.registry.CreateKeyEx.assert_not_called()
    windows_setup.broadcast.assert_called_once()
    assert "Already present" in capsys.readouterr().out


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_setup_path_rejects_unsupported_platform_without_io(
    windows_setup, monkeypatch, capsys, platform
) -> None:
    monkeypatch.setattr(sys, "platform", platform)

    assert main(["setup-path"]) == 1

    windows_setup.registry.OpenKey.assert_not_called()
    windows_setup.registry.SetValueEx.assert_not_called()
    windows_setup.broadcast.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert "atom setup-path:" in output.err
    assert "Windows-only" in output.err


@pytest.mark.parametrize(
    ("value", "value_type"),
    [("C:\\keep", 7), (["C:\\keep"], 7), (123, 1)],
)
def test_setup_path_rejects_an_invalid_registry_value(
    windows_setup, capsys, value, value_type
) -> None:
    windows_setup.registry.QueryValueEx.return_value = (value, value_type)

    assert main(["setup-path"]) == 1

    windows_setup.registry.SetValueEx.assert_not_called()
    windows_setup.broadcast.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert "string" in output.err


@pytest.mark.parametrize("missing", ["key", "value"])
def test_setup_path_creates_a_missing_user_path(windows_setup, missing) -> None:
    if missing == "key":
        windows_setup.registry.OpenKey.side_effect = FileNotFoundError("missing key")
    else:
        windows_setup.registry.QueryValueEx.side_effect = FileNotFoundError("missing value")

    assert main(["setup-path"]) == 0

    windows_setup.registry.SetValueEx.assert_called_once_with(
        windows_setup.registry.CreateKeyEx.return_value.__enter__.return_value,
        "Path",
        0,
        windows_setup.registry.REG_EXPAND_SZ,
        str(windows_setup.scripts),
    )


@pytest.mark.parametrize(
    ("operation", "action"),
    [
        ("OpenKey", "read"),
        ("QueryValueEx", "read"),
        ("CreateKeyEx", "write"),
        ("SetValueEx", "write"),
    ],
)
def test_setup_path_reports_registry_permission_errors(
    windows_setup, capsys, operation, action
) -> None:
    getattr(windows_setup.registry, operation).side_effect = PermissionError(
        "denied by test"
    )

    assert main(["setup-path"]) == 1

    windows_setup.broadcast.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert f"could not {action} user PATH" in output.err
    assert "denied by test" in output.err
    assert "Traceback" not in output.err


@pytest.mark.parametrize("already_present", [False, True])
@pytest.mark.parametrize("failure", ["timeout", "os-error"])
def test_setup_path_reports_partial_notification_failure(
    windows_setup, capsys, already_present, failure
) -> None:
    if already_present:
        windows_setup.registry.QueryValueEx.return_value = (
            str(windows_setup.scripts),
            windows_setup.registry.REG_SZ,
        )
    if failure == "timeout":
        windows_setup.broadcast.return_value = 0
    else:
        windows_setup.broadcast.side_effect = OSError("notification denied")

    assert main(["setup-path"]) == 1

    assert windows_setup.registry.SetValueEx.call_count == (0 if already_present else 1)
    output = capsys.readouterr()
    assert output.out == ""
    assert "could not notify Windows" in output.err
    assert ("already present" if already_present else "saved") in output.err
    assert "Traceback" not in output.err


@pytest.mark.parametrize("invalid", ["semicolon", "nul"])
def test_setup_path_rejects_an_ambiguous_scripts_directory(
    windows_setup, tmp_path, monkeypatch, capsys, invalid
) -> None:
    scripts = tmp_path / "unsafe;Scripts"
    scripts.mkdir()
    (scripts / "atom.exe").touch()
    (scripts / "atom-write-artifact.exe").touch()
    candidate = str(scripts) if invalid == "semicolon" else str(scripts) + "\0"
    monkeypatch.setattr(sysconfig, "get_path", lambda name, scheme=None: candidate)

    assert main(["setup-path"]) == 1

    windows_setup.registry.OpenKey.assert_not_called()
    windows_setup.registry.SetValueEx.assert_not_called()
    assert "PATH delimiter or NUL" in capsys.readouterr().err


@pytest.mark.parametrize("extra_unit", [0, 1])
@pytest.mark.parametrize("non_bmp", [False, True])
def test_setup_path_enforces_the_windows_utf16_length_limit(
    windows_setup, capsys, extra_unit, non_bmp
) -> None:
    scripts_units = len(str(windows_setup.scripts).encode("utf-16-le")) // 2
    original_units = 32767 - 1 - scripts_units - 1
    original = (
        "\U0001f600" * (original_units // 2) + "x" * (original_units % 2)
        if non_bmp
        else "x" * original_units
    ) + "x" * extra_unit
    windows_setup.registry.QueryValueEx.return_value = (
        original,
        windows_setup.registry.REG_SZ,
    )

    assert main(["setup-path"]) == (1 if extra_unit else 0)

    output = capsys.readouterr()
    if extra_unit:
        windows_setup.registry.SetValueEx.assert_not_called()
        assert output.out == ""
        assert "32,767" in output.err
    else:
        saved = windows_setup.registry.SetValueEx.call_args.args[-1]
        assert saved == original + ";" + str(windows_setup.scripts)
        assert len((saved + "\0").encode("utf-16-le")) // 2 == 32767


def test_setup_path_reports_discovery_errors(
    windows_setup, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        sysconfig, "get_path", Mock(side_effect=OSError("scheme unavailable"))
    )

    assert main(["setup-path"]) == 1

    windows_setup.registry.OpenKey.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert "could not locate installed commands" in output.err
    assert "scheme unavailable" in output.err


@pytest.mark.parametrize("missing", ["atom.exe", "atom-write-artifact.exe", "not-a-file"])
def test_setup_path_requires_both_installed_console_scripts(
    windows_setup, capsys, missing
) -> None:
    target = windows_setup.scripts / (
        "atom.exe" if missing == "not-a-file" else missing
    )
    target.unlink()
    if missing == "not-a-file":
        target.mkdir()

    assert main(["setup-path"]) == 1

    windows_setup.registry.OpenKey.assert_not_called()
    assert "Repair its console-script installation" in capsys.readouterr().err


def test_setup_path_prefers_the_default_scheme_when_complete(windows_setup) -> None:
    for name in ("atom.exe", "atom-write-artifact.exe"):
        (windows_setup.default_scripts / name).touch()

    assert main(["setup-path"]) == 0

    saved = windows_setup.registry.SetValueEx.call_args.args[-1]
    assert saved.endswith(";" + str(windows_setup.default_scripts))


def test_setup_path_changes_only_the_user_registry_value(windows_setup) -> None:
    process_environment = dict(os.environ)

    assert main(["setup-path"]) == 0

    registry = windows_setup.registry
    registry.OpenKey.assert_called_once_with(
        registry.HKEY_CURRENT_USER, "Environment", access=registry.KEY_QUERY_VALUE
    )
    registry.CreateKeyEx.assert_called_once_with(
        registry.HKEY_CURRENT_USER, "Environment", access=registry.KEY_SET_VALUE
    )
    assert dict(os.environ) == process_environment


def test_setup_path_uses_a_pointer_sized_environment_notification(windows_setup) -> None:
    payloads = []

    def notify(*arguments):
        payloads.append(ctypes.wstring_at(arguments[3]))
        return 1

    windows_setup.broadcast.side_effect = notify

    assert main(["setup-path"]) == 0

    assert payloads == ["Environment"]
    arguments = windows_setup.broadcast.call_args.args
    assert arguments[:3] == (0xFFFF, 0x001A, 0)
    assert arguments[4:6] == (0x0002, 5000)
    assert windows_setup.broadcast.argtypes == (
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(ctypes.c_size_t),
    )
    assert windows_setup.broadcast.restype is ctypes.c_ssize_t


def test_ordinary_init_does_not_opt_in_to_path_setup(
    windows_setup, tmp_path, monkeypatch
) -> None:
    setup = Mock(side_effect=AssertionError("unexpected PATH setup"))
    monkeypatch.setattr("atom.cli.setup_user_path", setup)
    monkeypatch.chdir(tmp_path)

    assert main(["init", "--module", "example.com/untouched-path"]) == 0

    setup.assert_not_called()
    windows_setup.registry.OpenKey.assert_not_called()


def test_setup_path_prints_literal_powershell_executable_paths(
    windows_setup, tmp_path, monkeypatch, capsys
) -> None:
    scripts = tmp_path / "$literal's `Scripts"
    scripts.mkdir()
    for name in ("atom.exe", "atom-write-artifact.exe"):
        (scripts / name).touch()
    monkeypatch.setattr(sysconfig, "get_path", lambda name, scheme=None: str(scripts))

    assert main(["setup-path"]) == 0

    output = capsys.readouterr().out
    for name in ("atom.exe", "atom-write-artifact.exe"):
        quoted = str(scripts / name).replace("'", "''")
        assert f"& '{quoted}'" in output


@pytest.mark.parametrize(
    "relative",
    [
        Path("skills/atom/references/bootstrap.md"),
        Path("skills/init/SKILL.md"),
    ],
)
def test_onboarding_documents_one_time_path_setup(relative) -> None:
    repository = Path(__file__).parents[2]
    source = (repository / relative).read_text(encoding="utf-8")
    packaged = (
        repository / "tools" / "atom" / "assets" / relative
    ).read_text(encoding="utf-8")

    assert source == packaged
    assert "setup-path" in source
    assert "opt-in" in source
    assert "Do not re-probe" in source


def test_readme_documents_the_setup_command_and_session_limitation() -> None:
    repository = Path(__file__).parents[2]
    readme = (repository / "README.md").read_text(encoding="utf-8")

    assert "python -m atom.cli setup-path" in readme
    assert "current parent process" in readme
