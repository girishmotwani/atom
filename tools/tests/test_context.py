"""Explicit evidence capture must never become silent context omission."""

import hashlib
from pathlib import Path

import pytest

from atom.context import ContextInputError, load_context_documents


def test_context_capture_preserves_bytes_and_order(tmp_path):
    first = 'Contract: \u03bb\r\n```json\r\n{"quote": "\\""}\r\n```\r\n'.encode("utf-8")
    second = b"Caller: requires an initialized cache.\n"
    (tmp_path / "first.md").write_bytes(first)
    (tmp_path / "second.md").write_bytes(second)

    documents = load_context_documents(
        [Path("second.md"), tmp_path / "first.md"], tmp_path,
    )
    (tmp_path / "first.md").write_text("changed after capture", encoding="utf-8")

    assert len(documents) == 2
    for index, (document, content) in enumerate(zip(documents, (second, first)), 1):
        assert document.label == f"context-{index}"
        assert document.text == content.decode("utf-8")
        assert document.utf8_bytes == len(content)
        assert document.sha256 == hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize("kind,message", [
    ("blank", "empty content"),
    ("nul", "NUL content"),
    ("encoding", "invalid UTF-8"),
    ("directory", "is not a regular file"),
    ("missing", "could not be read"),
    ("permission", "could not be read"),
    ("resolution", "could not be read"),
])
def test_context_capture_rejects_invalid_input(tmp_path, monkeypatch, kind, message):
    (tmp_path / "valid").write_bytes(b"valid first document")
    invalid = tmp_path / "private-account-path"
    if kind == "directory":
        invalid.mkdir()
    elif kind != "missing":
        invalid.write_bytes({
            "blank": b" \r\n\t",
            "nul": b"contract\x00source",
            "encoding": b"\xff",
        }.get(kind, b"private content"))
    if kind in ("permission", "resolution"):
        operation = "read_bytes" if kind == "permission" else "resolve"
        original = getattr(Path, operation)

        def refused(path, *args, **kwargs):
            if path == invalid:
                raise PermissionError("private account details")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(Path, operation, refused)

    with pytest.raises(ContextInputError, match=f"context document 2 {message}") as error:
        load_context_documents([Path("valid"), invalid], tmp_path)
    assert "private" not in str(error.value)


def test_context_capture_rejects_duplicate_paths(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("contract", encoding="utf-8")
    (tmp_path / "nested").mkdir()

    with pytest.raises(ValueError, match="duplicate context-file"):
        load_context_documents(
            [source, Path("nested") / ".." / "source.md"], tmp_path,
        )
