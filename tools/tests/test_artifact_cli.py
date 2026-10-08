"""Tests for the dedicated artifact-writer executable."""

from __future__ import annotations

import io
from pathlib import Path

import pytest


def test_main_allowed_target_writes_exact_utf8_content(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    from atom.artifact_cli import main

    monkeypatch.chdir(tmp_path)
    content = "# Design\n\nUnicode: café — 東京\n"
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(content.encode("utf-8"))))

    assert main(["specs/project/design.md"]) == 0
    destination = tmp_path / "specs" / "project" / "design.md"
    assert destination.read_text(encoding="utf-8") == content
    assert capsys.readouterr().out == f"Wrote {destination}\n"


def test_main_empty_stdin_creates_empty_artifact(
    tmp_path: Path, monkeypatch
) -> None:
    from atom.artifact_cli import main

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"")))

    assert main(["specs/empty.md"]) == 0
    assert (tmp_path / "specs" / "empty.md").read_bytes() == b""


def test_module_execution_runs_main_entry_point(
    tmp_path: Path, monkeypatch
) -> None:
    import subprocess
    import sys

    repository = tmp_path / "repository"
    repository.mkdir()
    monkeypatch.chdir(repository)

    process = subprocess.run(
        [sys.executable, "-m", "atom.artifact_cli", "specs/from_module.md"],
        input=b"# module\n",
        capture_output=True,
    )

    assert process.returncode == 0, process.stderr.decode()
    assert (repository / "specs" / "from_module.md").read_text(
        encoding="utf-8"
    ) == "# module\n"


def test_bootstrap_documents_hidden_artifact_writer_fallback() -> None:
    repository_root = Path(__file__).parents[2]
    source = (
        repository_root / "skills" / "atom" / "references" / "bootstrap.md"
    ).read_text(encoding="utf-8")
    packaged = (
        repository_root
        / "tools"
        / "atom"
        / "assets"
        / "skills"
        / "atom"
        / "references"
        / "bootstrap.md"
    ).read_text(encoding="utf-8")

    assert source == packaged
    assert "atom-write-artifact --help" in source
    assert "python -m atom.artifact_cli --help" in source
    assert "python -m atom.artifact_cli <relative-path>" in source


def test_main_normalizes_native_shell_line_endings_to_lf(
    tmp_path: Path, monkeypatch
) -> None:
    from atom.artifact_cli import main

    monkeypatch.chdir(tmp_path)
    content = "first\r\nsecond\rthird\r\n"
    monkeypatch.setattr(
        "sys.stdin", io.TextIOWrapper(io.BytesIO(content.encode("utf-8")))
    )

    assert main(["specs/line-endings.md"]) == 0
    assert (tmp_path / "specs" / "line-endings.md").read_bytes() == (
        b"first\nsecond\nthird\n"
    )


def test_main_strips_the_byte_order_mark_windows_shells_prepend(
    tmp_path: Path, monkeypatch
) -> None:
    """A BOM arriving on stdin is shell framing, never artifact content.

    Windows PowerShell prepends a UTF-8 BOM when piping to a native command,
    so without this the first heading of every artifact written that way is
    silently corrupted by an invisible U+FEFF.
    """

    from atom.artifact_cli import main

    monkeypatch.chdir(tmp_path)
    piped = b"\xef\xbb\xbf# Report\n\nbody\n"
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(piped)))

    assert main(["specs/bom.md"]) == 0
    assert (tmp_path / "specs" / "bom.md").read_bytes() == b"# Report\n\nbody\n"


def test_main_strips_only_the_first_byte_order_mark(
    tmp_path: Path, monkeypatch
) -> None:
    """Only the leading mark is framing; a later U+FEFF is content."""

    from atom.artifact_cli import main

    monkeypatch.chdir(tmp_path)
    piped = "\ufeffone \ufeff two\n".encode("utf-8")
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(piped)))

    assert main(["specs/inner-bom.md"]) == 0
    assert (tmp_path / "specs" / "inner-bom.md").read_text(encoding="utf-8") == (
        "one \ufeff two\n"
    )


def test_main_invalid_utf8_writes_nothing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    from atom.artifact_cli import main

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"\xff")))

    assert main(["specs/invalid.md"]) == 1
    assert "stdin is not valid UTF-8" in capsys.readouterr().err
    assert not (tmp_path / "specs" / "invalid.md").exists()


def test_main_refused_target_does_not_read_stdin(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    from atom.artifact_cli import main

    class UnreadableInput:
        @property
        def buffer(self):
            raise AssertionError("stdin was read for a refused target")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.stdin", UnreadableInput())

    assert main(["internal/server.go"]) == 1
    assert (
        "atom-write-artifact: refused internal/server.go (outside-artifact-set)"
        in capsys.readouterr().err
    )
    assert not (tmp_path / "internal").exists()


@pytest.mark.parametrize("arguments", [[], ["specs/a.md", "specs/b.md"]])
def test_main_wrong_argument_count_exits_usage_error(arguments: list[str]) -> None:
    from atom.artifact_cli import main

    with pytest.raises(SystemExit) as exited:
        main(arguments)

    assert exited.value.code == 2


def test_main_filesystem_failure_reports_error_without_partial_file(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    import atom.artifact_cli as artifact_cli

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.stdin", io.TextIOWrapper(io.BytesIO(b"# content\n"))
    )

    def fail_write(root: Path, contents: dict[str, str]) -> list[Path]:
        raise OSError("disk full")

    monkeypatch.setattr(artifact_cli, "write_artifacts", fail_write)

    assert artifact_cli.main(["specs/report.md"]) == 1
    assert "atom-write-artifact: disk full" in capsys.readouterr().err
    assert not (tmp_path / "specs" / "report.md").exists()


def test_main_refusal_during_write_is_reported(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    import atom.artifact_cli as artifact_cli
    from atom.artifacts import ArtifactWriteRefused, Decision

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.stdin", io.TextIOWrapper(io.BytesIO(b"# content\n"))
    )

    def refuse_after_read(root: Path, contents: dict[str, str]) -> list[Path]:
        raise ArtifactWriteRefused(
            [Decision("specs/report.md", False, "reparse-point-in-path")]
        )

    monkeypatch.setattr(artifact_cli, "write_artifacts", refuse_after_read)

    assert artifact_cli.main(["specs/report.md"]) == 1
    assert (
        "refused specs/report.md (reparse-point-in-path)"
        in capsys.readouterr().err
    )
