"""Tests for the artifact write guard.

These cover both halves of the guard: the decision about a path, and the write
that depends on that decision still being true when the bytes land.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from atom.artifacts import ArtifactWriteRefused, classify, write_artifacts


@pytest.fixture()
def repository(tmp_path: Path) -> Path:
    (tmp_path / "specs").mkdir()
    (tmp_path / "poc").mkdir()
    (tmp_path / ".atom").mkdir()
    return tmp_path


def make_junction(link: Path, destination: Path) -> bool:
    """Create a Windows directory junction, reporting whether it worked.

    A junction needs no privilege, unlike a symlink, which is why it is the
    escape route worth testing on Windows.
    """

    if os.name != "nt":
        try:
            link.symlink_to(destination, target_is_directory=True)
            return True
        except OSError:
            return False
    completed = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(link), str(destination)],
        capture_output=True,
    )
    return completed.returncode == 0


@pytest.mark.parametrize(
    "target,reason",
    [
        ("specs/project/design.md", "allowed-artifact-directory"),
        ("poc/spike/README.md", "allowed-artifact-directory"),
        (".atom/config.json", "allowed-runtime-file"),
        (".atom/state.json", "allowed-runtime-file"),
        (".atom/baseline.json", "allowed-runtime-file"),
    ],
)
def test_artifact_paths_are_allowed(repository: Path, target: str, reason: str) -> None:
    decision = classify(repository, target)
    assert decision.allowed
    assert decision.reason == reason


@pytest.mark.parametrize(
    "target,reason",
    [
        ("internal/server.go", "outside-artifact-set"),
        ("tools/atom/cli.py", "outside-artifact-set"),
        (".github/copilot-instructions.md", "outside-artifact-set"),
        (".atom/atom/AGENTS.md", "outside-artifact-set"),
        (".atom/events.jsonl", "outside-artifact-set"),
        (".atom/credentials.json", "outside-artifact-set"),
        ("specs", "outside-artifact-set"),
        ("specs/../internal/escape.go", "outside-artifact-set"),
        ("../elsewhere/escape.md", "outside-repository"),
    ],
)
def test_non_artifact_paths_are_refused(
    repository: Path, target: str, reason: str
) -> None:
    decision = classify(repository, target)
    assert not decision.allowed
    assert decision.reason == reason


def test_absolute_path_outside_the_repository_is_refused(
    repository: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("outside") / "escape.md"
    decision = classify(repository, outside)
    assert not decision.allowed
    assert decision.reason == "outside-repository"


def test_link_inside_specs_is_refused_before_containment(
    repository: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("outside")
    link = repository / "specs" / "outside-link"
    if not make_junction(link, outside):
        pytest.skip("this platform would not create a directory junction")

    decision = classify(repository, "specs/outside-link/escaped.md")

    assert not decision.allowed
    assert decision.reason == "reparse-point-in-path"


def test_link_pointing_back_inside_is_still_refused(repository: Path) -> None:
    link = repository / "specs" / "inner-link"
    if not make_junction(link, repository / "specs"):
        pytest.skip("this platform would not create a directory junction")

    decision = classify(repository, "specs/inner-link/inside.md")

    assert not decision.allowed
    assert decision.reason == "reparse-point-in-path"


def test_write_creates_nested_artifact_directories(repository: Path) -> None:
    written = write_artifacts(
        repository, {"specs/project/phase-01/design-spec.md": "# Design\n"}
    )

    assert written == [repository / "specs" / "project" / "phase-01" / "design-spec.md"]
    assert written[0].read_text(encoding="utf-8") == "# Design\n"


def test_write_replaces_an_existing_artifact(repository: Path) -> None:
    destination = repository / "specs" / "findings.md"
    destination.write_text("old\n", encoding="utf-8")

    write_artifacts(repository, {"specs/findings.md": "new\n"})

    assert destination.read_text(encoding="utf-8") == "new\n"


def test_write_leaves_no_temporary_files_behind(repository: Path) -> None:
    write_artifacts(repository, {"specs/findings.md": "content\n"})

    assert [entry.name for entry in (repository / "specs").iterdir()] == [
        "findings.md"
    ]


def test_mixed_batch_writes_nothing(repository: Path) -> None:
    with pytest.raises(ArtifactWriteRefused) as refused:
        write_artifacts(
            repository,
            {
                "specs/notes.md": "allowed\n",
                "internal/server.go": "package main\n",
            },
        )

    assert [refusal.target for refusal in refused.value.refusals] == [
        "internal/server.go"
    ]
    assert not (repository / "specs" / "notes.md").exists()
    assert not (repository / "internal").exists()


def test_every_refusal_in_a_batch_is_reported(repository: Path) -> None:
    with pytest.raises(ArtifactWriteRefused) as refused:
        write_artifacts(
            repository,
            {"internal/server.go": "x", ".github/workflows/ci.yml": "y"},
        )

    assert sorted(refusal.target for refusal in refused.value.refusals) == [
        ".github/workflows/ci.yml",
        "internal/server.go",
    ]


def test_write_through_a_link_is_refused_and_writes_nothing(
    repository: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    outside = tmp_path_factory.mktemp("outside")
    link = repository / "specs" / "outside-link"
    if not make_junction(link, outside):
        pytest.skip("this platform would not create a directory junction")

    with pytest.raises(ArtifactWriteRefused):
        write_artifacts(repository, {"specs/outside-link/escaped.md": "leaked\n"})

    assert list(outside.iterdir()) == []


def test_link_appearing_after_validation_is_caught_before_the_write(
    repository: Path, tmp_path_factory: pytest.TempPathFactory, monkeypatch
) -> None:
    """Simulate the time-of-check to time-of-use race the guard exists to close.

    The link is planted at the moment the directories are created -- after the
    first decision, before the bytes are moved into place -- which is precisely
    the window a validate-then-write-elsewhere design leaves open.
    """

    outside = tmp_path_factory.mktemp("outside")
    import atom.artifacts as artifacts

    original = artifacts._create_validated_directories
    planted: list[Path] = []

    def plant_link_then_create(root: Path, directory: Path) -> list[Path]:
        created = original(root, directory)
        if not planted:
            planted.append(directory)
            os.rmdir(directory)
            if not make_junction(directory, outside):
                pytest.skip("this platform would not create a directory junction")
        return created

    monkeypatch.setattr(
        artifacts, "_create_validated_directories", plant_link_then_create
    )

    with pytest.raises(ArtifactWriteRefused) as refused:
        write_artifacts(repository, {"specs/raced/report.md": "leaked\n"})

    assert refused.value.refusals[0].reason == "reparse-point-in-path"
    assert list(outside.iterdir()) == []
    assert not os.path.lexists(repository / "specs" / "raced")


def test_cleanup_removes_a_link_planted_where_it_created_a_directory(
    repository: Path, tmp_path_factory: pytest.TempPathFactory, monkeypatch
) -> None:
    """POSIX ``rmdir`` refuses a symlink, so rmdir-only cleanup leaves it behind.

    Windows removes a directory junction with ``rmdir``, which hides this on the
    platform the guard was written on. The refusal is simulated here so the gap
    is caught everywhere rather than only on the CI leg that happens to be POSIX.
    """

    import atom.artifacts as artifacts

    outside = tmp_path_factory.mktemp("outside")
    planted = repository / "specs" / "raced"
    if not make_junction(planted, outside):
        pytest.skip("this platform would not create a directory junction")

    real_rmdir = os.rmdir

    def posix_rmdir(path, *args, **kwargs):
        if artifacts._is_reparse_point(Path(path)):
            raise NotADirectoryError(20, "Not a directory", str(path))
        return real_rmdir(path, *args, **kwargs)

    monkeypatch.setattr(os, "rmdir", posix_rmdir)

    artifacts._remove_empty_directories([planted])

    assert not os.path.lexists(planted)
    assert list(outside.iterdir()) == []


def test_a_file_in_place_of_a_directory_is_refused(repository: Path) -> None:
    (repository / "specs" / "project").write_text("not a directory\n", encoding="utf-8")

    with pytest.raises(ArtifactWriteRefused) as refused:
        write_artifacts(repository, {"specs/project/design.md": "# Design\n"})

    assert refused.value.refusals[0].reason == "parent-is-a-file"


@pytest.mark.skipif(os.name != "nt", reason="only Windows has per-drive paths")
def test_a_path_on_another_drive_is_refused(repository: Path) -> None:
    decision = classify(repository, r"Z:\elsewhere\escape.md")

    assert not decision.allowed
    assert decision.reason == "outside-repository"


def test_a_failed_stage_leaves_nothing_behind(repository: Path, monkeypatch) -> None:
    """A write that dies mid-stream must not leave a half-written artifact."""

    import atom.artifacts as artifacts

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(artifacts.os, "fdopen", fail)

    with pytest.raises(OSError):
        write_artifacts(repository, {"specs/findings.md": "content\n"})

    assert list((repository / "specs").iterdir()) == []


def test_a_failed_replace_preserves_existing_file_and_removes_temporary(
    repository: Path, monkeypatch
) -> None:
    import atom.artifacts as artifacts

    destination = repository / "specs" / "findings.md"
    destination.write_text("old\n", encoding="utf-8")

    def fail_replace(source: Path, target: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(artifacts.os, "replace", fail_replace)

    with pytest.raises(OSError):
        write_artifacts(repository, {"specs/findings.md": "new\n"})

    assert destination.read_text(encoding="utf-8") == "old\n"
    assert [entry.name for entry in (repository / "specs").iterdir()] == [
        "findings.md"
    ]
