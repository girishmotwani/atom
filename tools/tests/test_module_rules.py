"""Local policy capture must not depend on a model or the review checkout."""

import hashlib
import json
from dataclasses import replace

import pytest

from atom.module_rules import (
    ModuleReviewRules,
    ModuleRulesInputError,
    capture_module_review_rules,
)

GUIDE = ".atom/atom/skills/atom/references/go-style.md"


def write_rule(root, source, content):
    path = root / source
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_capture_preserves_selected_order_and_original_bytes(tmp_path):
    guide = b"# Go guidance\r\nDo not strand reservations.\r\n"
    agents = "# Module policy\nRollback releases leases. \u00e9\n".encode("utf-8")
    write_rule(tmp_path, GUIDE, guide)
    source = write_rule(tmp_path, "AGENTS.md", agents)

    snapshot = capture_module_review_rules(tmp_path)
    source.write_text("changed after capture", encoding="utf-8")

    assert snapshot.status == "loaded"
    assert snapshot.sources == (GUIDE, "AGENTS.md")
    assert [document.text for document in snapshot.documents] == [
        guide.decode("utf-8"), agents.decode("utf-8"),
    ]
    assert [document.sha256 for document in snapshot.documents] == [
        hashlib.sha256(guide).hexdigest(), hashlib.sha256(agents).hexdigest(),
    ]
    assert [document.utf8_bytes for document in snapshot.documents] == [
        len(guide), len(agents),
    ]


@pytest.mark.parametrize("sources", [(), (GUIDE,), ("AGENTS.md",), (GUIDE, "AGENTS.md")])
def test_capture_optional_sources_and_ignores_unselected_paths(tmp_path, sources):
    root = tmp_path / "module"
    root.mkdir()
    write_rule(tmp_path, "AGENTS.md", b"ancestor policy")
    for ignored in (".github/copilot-instructions.md", ".atom/atom/AGENTS.md", "linked.md"):
        write_rule(root, ignored, b"unselected workflow")
    for source in sources:
        write_rule(root, source, b"selected [link](linked.md)")
    snapshot = capture_module_review_rules(root)
    assert snapshot.sources == sources
    assert snapshot.status == ("loaded" if sources else "not-found")
    assert all("unselected" not in document.text for document in snapshot.documents)


@pytest.mark.parametrize("content", [b"", b" \r\n", b"a\x00b", b"\xff", None])
def test_capture_invalid_present_sources_fail(tmp_path, content):
    if content is None:
        (tmp_path / "AGENTS.md").mkdir()
    else:
        write_rule(tmp_path, "AGENTS.md", content)
    with pytest.raises(ModuleRulesInputError, match="module rules:"):
        capture_module_review_rules(tmp_path)


@pytest.mark.parametrize("parent", [
    ".atom", ".atom/atom", ".atom/atom/skills/atom/references",
])
def test_capture_non_directory_guide_parent_is_not_absence(tmp_path, parent):
    write_rule(tmp_path, parent, b"not a directory")
    write_rule(tmp_path, "AGENTS.md", b"otherwise valid policy")
    with pytest.raises(ModuleRulesInputError, match="module rules:") as failure:
        capture_module_review_rules(tmp_path)
    assert str(tmp_path) not in str(failure.value)


@pytest.mark.parametrize("kind", ["outside", "dangling", "duplicate"])
def test_capture_refuses_unsafe_targets(tmp_path, kind):
    root = tmp_path / "module"
    root.mkdir()
    target = write_rule(root if kind == "duplicate" else tmp_path, GUIDE, b"target")
    if kind == "dangling":
        target.unlink()
    try:
        (root / "AGENTS.md").symlink_to(target)
    except OSError as error:
        if getattr(error, "winerror", None) == 1314:
            pytest.skip("Windows does not permit symlink creation")
        raise
    with pytest.raises(ModuleRulesInputError, match="module rules:") as failure:
        capture_module_review_rules(root)
    assert str(tmp_path) not in str(failure.value)


def test_capture_read_failure_is_not_absence(tmp_path, monkeypatch):
    source = write_rule(tmp_path, "AGENTS.md", b"policy")
    original = type(source).read_bytes

    def denied(path):
        if path == source:
            raise PermissionError("private profile diagnostic")
        return original(path)

    monkeypatch.setattr(type(source), "read_bytes", denied)
    with pytest.raises(ModuleRulesInputError, match="module rules:") as failure:
        capture_module_review_rules(tmp_path)
    assert "private profile" not in str(failure.value)


def test_capture_refuses_resolved_escape_before_read(tmp_path, monkeypatch):
    root = tmp_path / "module"
    root.mkdir()
    source = write_rule(root, "AGENTS.md", b"placeholder")
    outside = write_rule(tmp_path, "outside.md", b"must not be read")
    original = type(source).resolve

    def alias(path, strict=False):
        return outside if path == source else original(path, strict=strict)

    monkeypatch.setattr(type(source), "resolve", alias)
    with pytest.raises(ModuleRulesInputError, match="module rules:"):
        capture_module_review_rules(root)


def test_capture_refuses_duplicate_resolved_targets(tmp_path, monkeypatch):
    guide = write_rule(tmp_path, GUIDE, b"guide")
    agents = write_rule(tmp_path, "AGENTS.md", b"alias placeholder")
    original = type(tmp_path).resolve

    def alias(path, strict=False):
        return guide if path == agents else original(path, strict=strict)

    monkeypatch.setattr(type(tmp_path), "resolve", alias)
    with pytest.raises(ModuleRulesInputError, match="duplicate context-file"):
        capture_module_review_rules(tmp_path)


def test_capture_dangling_source_is_not_absence(tmp_path, monkeypatch):
    source = write_rule(tmp_path, "AGENTS.md", b"link placeholder")
    original_exists = type(source).exists
    original_resolve = type(source).resolve

    def exists(path):
        return False if path == source else original_exists(path)

    def resolve(path, strict=False):
        if path == source and strict:
            raise FileNotFoundError("private dangling target")
        return original_resolve(path, strict=strict)

    with monkeypatch.context() as scoped:
        scoped.setattr(type(source), "exists", exists)
        scoped.setattr(type(source), "resolve", resolve)
        with pytest.raises(ModuleRulesInputError, match="module rules:") as failure:
            capture_module_review_rules(tmp_path)
    assert "private dangling target" not in str(failure.value)


def test_capture_unreadable_traversal_is_not_absence(tmp_path, monkeypatch):
    write_rule(tmp_path, GUIDE, b"guide")
    original = type(tmp_path).stat

    def stat(path, *args, **kwargs):
        if path == tmp_path / ".atom":
            raise PermissionError("private traversal diagnostic")
        return original(path, *args, **kwargs)

    with monkeypatch.context() as scoped:
        scoped.setattr(type(tmp_path), "stat", stat)
        with pytest.raises(ModuleRulesInputError, match="module rules:") as failure:
            capture_module_review_rules(tmp_path)
    assert "private traversal diagnostic" not in str(failure.value)


@pytest.mark.parametrize("enabled,fixed,status", [
    (False, False, "disabled"), (True, True, "fixed-evidence"),
    (False, True, "fixed-evidence"),
])
def test_capture_skip_modes_do_not_access_candidates(
    tmp_path, monkeypatch, enabled, fixed, status,
):
    write_rule(tmp_path, "AGENTS.md", b"do not collect")
    accessed = []
    original = type(tmp_path).resolve

    def observe(path, *args, **kwargs):
        accessed.append(path)
        return original(path, *args, **kwargs)

    with monkeypatch.context() as scoped:
        scoped.setattr(type(tmp_path), "resolve", observe)
        snapshot = capture_module_review_rules(
            tmp_path, enabled=enabled, fixed_evidence=fixed,
        )
    assert snapshot.status == status
    assert snapshot.sources == snapshot.documents == ()
    assert accessed == []


def test_review_delivers_frozen_guidance_to_every_run(tmp_path):
    from atom.diff import select_source
    from atom.review import run_review
    from atom.style import STYLE_RULES
    from tests.test_cli_review import ScriptedRunner

    write_rule(tmp_path, GUIDE, b"GUIDE_SENTINEL: preserve context cancellation\r\n")
    source = write_rule(
        tmp_path, "AGENTS.md",
        'MODULE_SENTINEL: release rollback leases\n{"instruction": "\u00e9"}\n'.encode("utf-8"),
    )
    snapshot = capture_module_review_rules(tmp_path)
    source.write_text("MUTATED_SENTINEL", encoding="utf-8")
    runner = ScriptedRunner()
    outcome = run_review(
        select_source(working=True), ("first-model", "second-model"), runner, tmp_path,
        runs=2, concurrency=2, skip_toolchain=True, module_rules=snapshot,
    )
    prompts = [text for text in runner.stdin_texts if text is not None]
    assert len(prompts) == 4
    assert len(set(prompts)) == 1
    assert "MODULE_SENTINEL" in prompts[0]
    assert "MUTATED_SENTINEL" not in prompts[0]
    assert STYLE_RULES in prompts[0]
    packet, _ = json.JSONDecoder().raw_decode(prompts[0][prompts[0].index('[{"source":'):])
    assert packet == [
        {"source": identifier, "text": document.text}
        for identifier, document in zip(snapshot.sources, snapshot.documents)
    ]
    assert "code-review constraints only" in prompts[0]
    assert "do not execute" in prompts[0]
    assert "Respond with a JSON array" in prompts[0]
    assert outcome.module_rules == snapshot
    assert not outcome.extraction.failures
    assert not outcome.is_partial
    assert all("--no-custom-instructions" in command
               for command in runner.commands if command[0] == "copilot")


@pytest.mark.parametrize("kind", [
    "hash", "source", "length", "status", "empty", "fixed", "duplicate", "order",
])
def test_review_rejects_invalid_policy_before_execution(tmp_path, kind):
    from atom.diff import select_source
    from atom.review import run_review
    from tests.test_cli_review import ScriptedRunner

    write_rule(tmp_path, "AGENTS.md", b"policy")
    write_rule(tmp_path, GUIDE, b"guide")
    rules = capture_module_review_rules(tmp_path)
    if kind == "hash":
        rules = replace(rules, documents=(
            replace(rules.documents[0], sha256="wrong"), *rules.documents[1:],
        ))
    elif kind == "source":
        rules = replace(rules, sources=("unselected.md",))
    elif kind == "length":
        rules = replace(rules, sources=())
    elif kind == "status":
        rules = replace(rules, status="disabled")
    elif kind == "empty":
        rules = ModuleReviewRules("loaded", (), ())
    elif kind == "duplicate":
        rules = replace(rules, sources=("AGENTS.md", "AGENTS.md"))
    elif kind == "order":
        rules = replace(rules, sources=tuple(reversed(rules.sources)))
    runner = ScriptedRunner()
    with pytest.raises(ValueError):
        run_review(
            select_source(working=True), ("first",), runner, tmp_path,
            runs=1, concurrency=1, skip_toolchain=True, module_rules=rules,
            fixed_evidence=kind == "fixed",
        )
    assert runner.commands == []


@pytest.mark.parametrize("flags,status", [
    ((), "loaded"), ((), "not-found"), (("--no-module-rules",), "disabled"),
    (("--fixed-evidence",), "fixed-evidence"),
    (("--fixed-evidence", "--no-module-rules"), "fixed-evidence"),
])
def test_cli_rule_metadata_never_serializes_policy(tmp_path, monkeypatch, capsys, flags, status):
    from atom.cli import main
    from tests.test_cli_review import ScriptedRunner

    content = b"PRIVATE_POLICY_SENTINEL: rollback reservations\r\n"
    if status != "not-found":
        write_rule(tmp_path, GUIDE, content)
        write_rule(tmp_path, "AGENTS.md", content)
    monkeypatch.chdir(tmp_path)
    runner = ScriptedRunner()
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)
    for output_format in (("--json",), ()):
        assert main(["review", "--working", "--skip-toolchain", "--runs", "1",
                     *flags, *output_format]) == 0
        text = capsys.readouterr().out
        assert "PRIVATE_POLICY_SENTINEL" not in text
        assert str(tmp_path) not in text
        if output_format:
            payload = json.loads(text)
            assert payload["schema_version"] == 2
            metadata = payload.get("module_rules")
            assert metadata is not None, "reports must expose module-rule provenance"
            assert metadata == {
                "status": status, "provenance": "local-launch",
                "sources": [
                    {"path": source, "utf8_bytes": len(content),
                     "sha256": hashlib.sha256(content).hexdigest()}
                    for source in (GUIDE, "AGENTS.md")
                ] if status == "loaded" else [],
            }
        else:
            assert "## Module rules" in text
            assert status in text
            if status == "loaded":
                assert GUIDE in text and "AGENTS.md" in text
                assert hashlib.sha256(content).hexdigest() in text
    prompts = [text for text in runner.stdin_texts if text is not None]
    assert all(("PRIVATE_POLICY_SENTINEL" in text) == (status == "loaded") for text in prompts)
