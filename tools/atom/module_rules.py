"""Freeze developer-selected module policy before review preparation."""

from dataclasses import dataclass
from pathlib import Path
import stat
from typing import Literal

from atom.context import (
    ContextDocument, ContextInputError, _validate_context_documents, load_context_documents,
)

_SOURCES = (".atom/atom/skills/atom/references/go-style.md", "AGENTS.md")


@dataclass(frozen=True)
class ModuleReviewRules:
    """Keep local policy and its provenance stable across checkout preparation."""

    status: Literal["loaded", "not-found", "disabled", "fixed-evidence"]
    sources: tuple[str, ...]
    documents: tuple[ContextDocument, ...]


class ModuleRulesInputError(Exception):
    """Stop review rather than silently omit a selected local policy."""


def _validate_module_review_rules(rules: ModuleReviewRules, *, fixed_evidence: bool) -> None:
    if (
        rules.status not in ("loaded", "not-found", "disabled", "fixed-evidence")
        or not isinstance(rules.sources, tuple)
        or not isinstance(rules.documents, tuple)
        or len(rules.sources) != len(rules.documents)
        or rules.sources != tuple(source for source in _SOURCES if source in rules.sources)
        or (rules.status == "loaded") != bool(rules.sources)
    ):
        raise ValueError("module rules: inconsistent snapshot")
    if fixed_evidence and rules.documents:
        raise ValueError("module rules cannot be applied in fixed-evidence mode")
    _validate_context_documents(rules.documents)


def capture_module_review_rules(
    launch_directory: Path, *, enabled: bool = True, fixed_evidence: bool = False,
) -> ModuleReviewRules:
    """Freeze supported launch-local sources without discovering other policy."""
    if fixed_evidence:
        return ModuleReviewRules("fixed-evidence", (), ())
    if not enabled:
        return ModuleReviewRules("disabled", (), ())
    try:
        root = launch_directory.resolve(strict=True)
    except (OSError, ValueError, RuntimeError) as error:
        raise ModuleRulesInputError(
            f"module rules: launch root could not be resolved ({type(error).__name__})"
        ) from error
    sources = []
    paths = []
    for source in _SOURCES:
        try:
            path = root
            # Inspect each entry without following it first: exists() would hide
            # dangling links, including links in an otherwise missing guide path.
            components = Path(source).parts
            for index, component in enumerate(components):
                path = path / component
                try:
                    path.lstat()
                except FileNotFoundError:
                    break
                resolved = path.resolve(strict=True)
                resolved.relative_to(root)
                # Windows can report a non-directory parent's child as missing.
                if index < len(components) - 1 and not stat.S_ISDIR(resolved.stat().st_mode):
                    raise ModuleRulesInputError(
                        f"module rules: {source} parent is not a directory"
                    )
            else:
                sources.append(source)
                paths.append(resolved)
        except (OSError, ValueError, RuntimeError) as error:
            raise ModuleRulesInputError(
                f"module rules: {source} could not be selected ({type(error).__name__})"
            ) from error
    try:
        documents = load_context_documents(paths, root)
    except (ContextInputError, ValueError) as error:
        raise ModuleRulesInputError(f"module rules: {error}") from error
    return ModuleReviewRules("loaded" if documents else "not-found", tuple(sources), documents)
