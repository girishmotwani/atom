"""Capture explicit review evidence without discovering additional source."""

from __future__ import annotations

import hashlib
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ContextDocument:
    """Keep caller evidence stable while concurrent reviewers use it."""

    label: str
    text: str
    utf8_bytes: int
    sha256: str


@dataclass(frozen=True)
class FixedReviewEvidence:
    """Identify the exact supplied packet without publishing its contents."""

    documents: tuple[ContextDocument, ...]
    prompt_utf8_bytes: int
    prompt_sha256: str


class ContextInputError(Exception):
    """Stop review rather than silently omit requested evidence."""


def load_context_documents(
    paths: Sequence[Path], base_directory: Path,
) -> tuple[ContextDocument, ...]:
    """Freeze explicit evidence before checkout preparation or inference."""

    documents = []
    seen: set[Path] = set()
    for index, path in enumerate(paths, 1):
        try:
            resolved = (base_directory / path).resolve(strict=True)
            if not stat.S_ISREG(resolved.stat().st_mode):
                raise ContextInputError(f"context document {index} is not a regular file")
        except (OSError, ValueError, RuntimeError) as error:
            # OS error messages can include profile paths or remote credentials.
            raise ContextInputError(
                f"context document {index} could not be read ({type(error).__name__})"
            ) from error
        if resolved in seen:
            raise ValueError(f"duplicate context-file: context document {index}")
        seen.add(resolved)
        try:
            content = resolved.read_bytes()
        except OSError as error:
            raise ContextInputError(
                f"context document {index} could not be read ({type(error).__name__})"
            ) from error
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContextInputError(f"context document {index} invalid UTF-8") from error
        problem = _text_problem(text)
        if problem:
            raise ContextInputError(f"context document {index} {problem}")
        documents.append(ContextDocument(
            label=f"context-{index}",
            text=text,
            utf8_bytes=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        ))
    return tuple(documents)


def _validate_context_documents(documents: tuple[ContextDocument, ...]) -> None:
    """Keep direct API input subject to the same snapshot invariants as files."""

    for index, document in enumerate(documents, 1):
        problem = _text_problem(document.text)
        if problem:
            raise ValueError(f"context document {index} {problem}")
        try:
            content = document.text.encode("utf-8")
        except UnicodeEncodeError as error:
            raise ValueError(f"context document {index} invalid UTF-8") from error
        if (
            document.label != f"context-{index}"
            or document.utf8_bytes != len(content)
            or document.sha256 != hashlib.sha256(content).hexdigest()
        ):
            raise ValueError(f"context document {index} inconsistent metadata")


def _text_problem(text: str) -> str:
    if "\x00" in text:
        return "NUL content"
    if not text.strip():
        return "empty content"
    return ""
