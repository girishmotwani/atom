"""Exercise review formatting against real Git snapshots and real gofmt."""

from __future__ import annotations

import json
import shutil
import stat
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

import pytest

from atom.diff import DiffRequest, DiffSource, DiffUnavailable
from atom.cli import EXIT_PASSED, main
from atom.context import load_context_documents
from atom.gates import FormatGate, GateStatus
from atom.invoke import InvocationReport, ModelAvailability, ModelRun, RunOutcome
from atom.review import ToolchainGateFailed, run_review
from atom.runner import CommandOutcome, CommandResult, SubprocessRunner
from tests.conftest import command_result


pytestmark = pytest.mark.skipif(
    shutil.which("git") is None or shutil.which("gofmt") is None,
    reason="real Git and gofmt are required for snapshot integration coverage",
)

BASE = "package fixture\n\nvar Value = 1\n"
CLEAN = "package fixture\n\nvar Value = 2\n"
BAD = "package fixture\nvar Value=2\n"


def git(directory: Path, *arguments: str) -> str:
    result = SubprocessRunner().run(
        (
            "git",
            "-c", "core.autocrlf=false",
            "-c", "core.hooksPath=" + str(directory / ".no-hooks"),
            "-c", "commit.gpgsign=false",
            "-c", "user.name=Atom Fixture",
            "-c", "user.email=fixture@example.invalid",
            "-C", str(directory),
            *arguments,
        ),
        directory,
        15,
    )
    assert result.succeeded, result.combined_output
    return result.stdout


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    git(tmp_path, "init", "--quiet", "--initial-branch=main")
    (tmp_path / "go.mod").write_bytes(b"module example.invalid/fixture\n\ngo 1.23\n")
    (tmp_path / "changed.go").write_bytes(BASE.encode())
    (tmp_path / "untouched.go").write_bytes(b"package fixture\nvar Existing=1\n")
    git(tmp_path, "add", "--all")
    git(tmp_path, "commit", "--quiet", "-m", "fixture baseline")
    return tmp_path


class ReviewRunner:
    """Keep Git/formatting real while isolating unrelated Go and model spend."""

    def __init__(self) -> None:
        self.delegate = SubprocessRunner()
        self.calls: list[tuple[tuple[str, ...], str | None]] = []

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float = 300,
        stdin_text: str | None = None,
    ) -> CommandResult:
        command = tuple(command)
        self.calls.append((command, stdin_text))
        if command[0] == "go":
            return command_result(
                command, working_directory, stdout="ok example.invalid/fixture 0.01s\n"
            )
        if command[0] in ("staticcheck", "errcheck", "govulncheck"):
            return command_result(
                command, working_directory, CommandOutcome.TOOL_MISSING,
                None, stderr="not installed in this test",
            )
        return self.delegate.run(
            command, working_directory, timeout_seconds, stdin_text
        )


@pytest.fixture
def model_prompts(monkeypatch) -> list[str]:
    prompts: list[str] = []

    def invoke(**arguments):
        prompts.append(arguments["prompt"])
        models = tuple(arguments["models"])
        return InvocationReport(
            models=models,
            runs_requested=1,
            runs=tuple(
                ModelRun(model, 1, RunOutcome.COMPLETED, "[]", 0.01)
                for model in models
            ),
            availability=tuple(ModelAvailability(model, True) for model in models),
        )

    monkeypatch.setattr("atom.review.invoke_models", invoke)
    return prompts


def review(
    directory: Path,
    runner: ReviewRunner,
    source: DiffSource = DiffSource.WORKING,
    base: str | None = None,
):
    return run_review(
        DiffRequest(source, base), ("fixture-model",), runner, directory, 1, 1
    )


def test_clean_changed_file_is_not_blocked_by_untouched_formatting(
    repository: Path, model_prompts: list[str]
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()

    outcome = review(repository, runner)

    formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
    assert formatting.status is GateStatus.PASSED
    assert "changed.go" in formatting.summary
    assert len(model_prompts) == 1
    assert ("gofmt", "-l", ".") not in [command for command, _ in runner.calls]
    assert [
        stdin for command, stdin in runner.calls if command[0] == "gofmt"
    ] == [CLEAN]
    standalone = FormatGate().evaluate(SubprocessRunner(), repository)
    assert standalone.status is GateStatus.FAILED
    assert "untouched.go" in standalone.summary


def test_fixed_evidence_keeps_changed_file_formatting_and_one_diff_capture(
    repository: Path, model_prompts: list[str]
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    context = repository / "review-context.md"
    context.write_text("Caller contract: preserve the exported value.\n", encoding="utf-8")
    documents = load_context_documents((context,), repository)
    runner = ReviewRunner()

    try:
        outcome = run_review(
            DiffRequest(DiffSource.WORKING), ("fixture-model",), runner,
            repository, 1, 1, fixed_evidence=True, context_documents=documents,
        )
    except ToolchainGateFailed as error:
        pytest.fail(f"Untouched formatting must not block fixed-evidence review: {error}")

    formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
    assert formatting.status is GateStatus.PASSED
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [CLEAN]
    assert sum("diff" in command for command, _ in runner.calls) == 1
    assert outcome.diff.files == ("changed.go",)
    assert len(model_prompts) == 1
    assert model_prompts[0].count(outcome.diff.text) == 1
    assert json.dumps([
        {"label": document.label, "text": document.text} for document in documents
    ]) in model_prompts[0]
    assert outcome.evidence is not None
    assert outcome.evidence.documents == documents


@pytest.mark.parametrize(
    ("staged", "working", "expected"),
    [
        (CLEAN, BAD, GateStatus.PASSED),
        (BAD, CLEAN, GateStatus.FAILED),
        (CLEAN, None, GateStatus.PASSED),
    ],
    ids=("clean-index-dirty-worktree", "dirty-index-clean-worktree", "worktree-file-absent"),
)
def test_staged_formatting_uses_index_snapshot_not_working_file(
    repository: Path, model_prompts: list[str], staged, working, expected
):
    path = repository / "changed.go"
    path.write_bytes(staged.encode())
    git(repository, "add", "changed.go")
    if working is None:
        path.unlink()
    else:
        path.write_bytes(working.encode())
    runner = ReviewRunner()

    if expected is GateStatus.FAILED:
        with pytest.raises(ToolchainGateFailed) as failure:
            review(repository, runner, DiffSource.STAGED)
        formatting = next(gate for gate in failure.value.failures if gate.name == "fmt")
        assert "changed.go" in formatting.summary
        assert model_prompts == []
    else:
        outcome = review(repository, runner, DiffSource.STAGED)
        formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
        assert formatting.status is expected
        assert len(model_prompts) == 1
    assert [
        stdin for command, stdin in runner.calls if command[0] == "gofmt"
    ] == [staged]


def test_branch_formatting_uses_committed_content_despite_dirty_working_file(
    repository: Path, model_prompts: list[str]
):
    base = git(repository, "rev-parse", "HEAD").strip()
    (repository / "changed.go").write_bytes(CLEAN.encode())
    git(repository, "add", "changed.go")
    git(repository, "commit", "--quiet", "-m", "selected clean source")
    (repository / "changed.go").write_bytes(BAD.encode())
    runner = ReviewRunner()

    outcome = review(repository, runner, DiffSource.BRANCH, base)

    assert len(model_prompts) == 1
    assert [
        stdin for command, stdin in runner.calls if command[0] == "gofmt"
    ] == [CLEAN]
    assert outcome.diff.request == DiffRequest(DiffSource.BRANCH, base)
    assert "+var Value = 2" in outcome.diff.text


def test_pure_rename_formats_destination_and_preserves_canonical_diff_path(
    repository: Path, model_prompts: list[str]
):
    git(repository, "mv", "changed.go", "renamed file.go")
    runner = ReviewRunner()

    outcome = review(repository, runner, DiffSource.STAGED)

    assert outcome.diff.files == ("renamed file.go",)
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [BASE]
    formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
    assert "renamed file.go" in formatting.summary


@pytest.mark.parametrize("change", ("empty", "non-go", "deleted"))
def test_no_surviving_go_files_skips_formatter_with_explicit_scope(
    repository: Path, model_prompts: list[str], change
):
    if change == "non-go":
        (repository / "README.md").write_text("fixture\n", encoding="utf-8")
        git(repository, "add", "README.md")
    elif change == "deleted":
        git(repository, "rm", "--quiet", "changed.go")
    runner = ReviewRunner()

    outcome = review(repository, runner, DiffSource.STAGED)

    formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
    assert formatting.status is GateStatus.SKIPPED
    assert "0 changed Go" in formatting.summary
    assert "staged" in formatting.summary
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)
    if change == "deleted":
        assert outcome.diff.files == ("changed.go",)


def test_module_boundary_exclusions_are_explicit_without_checking_other_modules(
    repository: Path, model_prompts: list[str]
):
    module = repository / "service"
    nested = module / "nested"
    nested.mkdir(parents=True)
    for directory in (module, nested):
        (directory / "go.mod").write_bytes(b"module example.invalid/sub\n\ngo 1.23\n")
        (directory / "source.go").write_bytes(BASE.encode())
    git(repository, "add", "--all")
    git(repository, "commit", "--quiet", "-m", "module fixtures")
    (repository / "changed.go").write_bytes(BAD.encode())
    (nested / "source.go").write_bytes(BAD.encode())
    (module / "source.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()

    outcome = review(module, runner)

    assert outcome.diff.files == ("changed.go", "service/nested/source.go", "service/source.go")
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [CLEAN]
    formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
    assert "outside selected module" in formatting.details
    assert "nested module" in formatting.details
    assert "service/nested/source.go" in formatting.details


@pytest.mark.parametrize("has_go_change", (True, False))
def test_prompt_names_selected_formatting_scope_without_claiming_module_scan(
    repository: Path, model_prompts: list[str], has_go_change
):
    if has_go_change:
        (repository / "changed.go").write_bytes(CLEAN.encode())

    review(repository, ReviewRunner())

    prompt = model_prompts[0]
    assert "gofmt -l ." not in prompt
    assert "changed Go files" in prompt
    if has_go_change:
        assert "formatting in the checked files only" in prompt
        assert "changed.go" in prompt
        assert "unstaged working-tree changes" in prompt
    else:
        exclusions = prompt.split("Do not report these mechanically checked categories:")[1].split(".")[0]
        assert "formatting" not in exclusions


def test_non_regular_selected_go_entry_is_refused_before_formatter_or_models(
    repository: Path, model_prompts: list[str]
):
    identity = git(repository, "rev-parse", "HEAD:changed.go").strip()
    git(repository, "update-index", "--cacheinfo", f"120000,{identity},changed.go")
    runner = ReviewRunner()

    with pytest.raises(DiffUnavailable, match="non-regular"):
        review(repository, runner, DiffSource.STAGED)

    assert model_prompts == []
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)


@pytest.mark.parametrize(
    "corruption",
    ("parent-path", "absolute-path", "windows-path", "unmerged", "unknown-status", "bad-mode", "bad-identity"),
)
def test_invalid_manifest_is_refused_without_empty_scope_success(
    repository: Path, model_prompts: list[str], monkeypatch, corruption
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()
    original_run = runner.run

    def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
        result = original_run(command, directory, timeout_seconds, stdin_text)
        if "--raw" in command:
            metadata, patch = result.stdout.split("\0\0", 1)
            header, name = metadata.split("\0")
            fields = header.split()
            if corruption == "parent-path":
                name = "../outside.go"
            elif corruption == "absolute-path":
                name = "/outside.go"
            elif corruption == "windows-path":
                name = "C:\\outside.go"
            elif corruption == "unmerged":
                fields[4] = "U"
            elif corruption == "unknown-status":
                fields[4] = "Q"
            elif corruption == "bad-mode":
                fields[0] = ":oops"
            else:
                fields[2] = "not-a-hash"
            result = replace(result, stdout=" ".join(fields) + "\0" + name + "\0\0" + patch)
        return result

    monkeypatch.setattr(runner, "run", corrupt)
    with pytest.raises(DiffUnavailable, match="unsafe|invalid|malformed|unmerged"):
        review(repository, runner)
    assert not model_prompts
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)


@pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED))
def test_invalid_utf8_is_required_formatting_failure_not_replacement_success(
    repository: Path, model_prompts: list[str], source
):
    (repository / "changed.go").write_bytes(b"package fixture\n\n// invalid \xff\n")
    if source is DiffSource.STAGED:
        git(repository, "add", "changed.go")
    runner = ReviewRunner()

    with pytest.raises(ToolchainGateFailed) as raised:
        review(repository, runner, source)

    formatting = next(gate for gate in raised.value.failures if gate.name == "fmt")
    assert "UTF-8" in formatting.summary
    assert "changed.go" in formatting.summary
    assert model_prompts == []
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)


def test_working_file_substituted_with_non_regular_path_is_not_read(
    repository: Path, model_prompts: list[str], monkeypatch
):
    path = repository / "changed.go"
    path.write_bytes(CLEAN.encode())
    original_lstat = Path.lstat
    original_read = Path.read_bytes
    read_attempts = []

    def substituted_lstat(candidate):
        result = original_lstat(candidate)
        if candidate == path:
            values = list(result)
            values[0] = stat.S_IFLNK | 0o777
            return type(result)(values)
        return result

    def read(candidate):
        if candidate == path:
            read_attempts.append(candidate)
        return original_read(candidate)

    monkeypatch.setattr(Path, "lstat", substituted_lstat)
    monkeypatch.setattr(Path, "read_bytes", read)

    with pytest.raises(DiffUnavailable, match="non-regular|unsafe"):
        review(repository, ReviewRunner())
    assert read_attempts == []
    assert model_prompts == []


@pytest.mark.parametrize("change", ("added", "renamed-from-text", "unicode-space"))
def test_added_and_renamed_go_paths_use_nul_delimited_canonical_names(
    repository: Path, model_prompts: list[str], change
):
    name = "new file.go"
    if change == "renamed-from-text":
        (repository / "source.txt").write_bytes(CLEAN.encode())
        git(repository, "add", "source.txt")
        git(repository, "commit", "--quiet", "-m", "text source fixture")
        git(repository, "mv", "source.txt", name)
    else:
        if change == "unicode-space":
            name = "caf" + chr(0xe9) + " file.go"
        (repository / name).write_bytes(CLEAN.encode())
        git(repository, "add", "--", name)
    runner = ReviewRunner()
    before = git(repository, "status", "--porcelain=v1")

    outcome = review(repository, runner, DiffSource.STAGED)

    assert outcome.diff.files == (name,)
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [CLEAN]
    assert git(repository, "status", "--porcelain=v1") == before
    assert (repository / name).read_bytes() == CLEAN.encode()
    assert len([command for command, _ in runner.calls if "--raw" in command]) == 1


@pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED))
@pytest.mark.parametrize(
    ("content", "is_clean"),
    (
        (CLEAN.replace("\n", "\r\n").encode(), True),
        (CLEAN.replace("\n", "\r\n", 1).encode(), True),
        (BAD.replace("\n", "\r\n").encode(), False),
        ((CLEAN + "\n// caf" + chr(0xe9) + "\n").encode(), True),
    ),
    ids=("crlf", "mixed-endings", "crlf-real-formatting-defect", "utf8"),
)
def test_selected_bytes_are_preserved_and_only_line_endings_are_normalized(
    repository: Path, model_prompts: list[str], source, content, is_clean
):
    path = repository / "changed.go"
    path.write_bytes(content)
    if source is DiffSource.STAGED:
        git(repository, "add", "changed.go")
    before = git(repository, "status", "--porcelain=v1")
    runner = ReviewRunner()

    if is_clean:
        review(repository, runner, source)
        assert len(model_prompts) == 1
    else:
        with pytest.raises(ToolchainGateFailed, match="fmt"):
            review(repository, runner, source)
        assert model_prompts == []
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [
        content.decode("utf-8").replace("\r\n", "\n")
    ]
    assert path.read_bytes() == content
    assert git(repository, "status", "--porcelain=v1") == before


@pytest.mark.parametrize(
    ("outcome", "exit_code", "stdout"),
    (
        (CommandOutcome.TOOL_MISSING, None, ""),
        (CommandOutcome.TIMED_OUT, None, ""),
        (CommandOutcome.RUNNER_ERROR, None, ""),
        (CommandOutcome.COMPLETED, 2, ""),
        (CommandOutcome.COMPLETED, 0, ""),
    ),
    ids=("missing", "timeout", "runner-error", "syntax-error", "empty-stdout"),
)
def test_formatter_failures_keep_path_and_original_diagnostic(
    repository: Path, model_prompts: list[str], monkeypatch, outcome, exit_code, stdout
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()
    original_run = runner.run

    def failing_format(command, directory, timeout_seconds=300, stdin_text=None):
        if command[0] == "gofmt":
            return command_result(
                tuple(command), directory, outcome, exit_code,
                stdout=stdout, stderr="formatter diagnostic",
            )
        return original_run(command, directory, timeout_seconds, stdin_text)

    monkeypatch.setattr(runner, "run", failing_format)
    with pytest.raises(ToolchainGateFailed) as raised:
        review(repository, runner)
    formatting = next(gate for gate in raised.value.failures if gate.name == "fmt")
    assert "changed.go" in formatting.summary
    assert "formatter diagnostic" in formatting.details
    assert model_prompts == []


def test_working_file_movement_after_diff_capture_blocks_models(
    repository: Path, model_prompts: list[str], monkeypatch
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()
    original_run = runner.run

    def move_after_capture(command, directory, timeout_seconds=300, stdin_text=None):
        result = original_run(command, directory, timeout_seconds, stdin_text)
        if "--raw" in command:
            (repository / "changed.go").write_bytes(BAD.encode())
        return result

    monkeypatch.setattr(runner, "run", move_after_capture)
    with pytest.raises(DiffUnavailable, match="no longer matches"):
        review(repository, runner)
    assert model_prompts == []
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)


@pytest.mark.parametrize("corruption", ("git-failure", "blob-read-failure", "bad-base64", "wrong-blob"))
def test_snapshot_acquisition_and_blob_transport_fail_closed(
    repository: Path, model_prompts: list[str], monkeypatch, corruption
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    git(repository, "add", "changed.go")
    runner = ReviewRunner()
    original_run = runner.run

    def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
        if corruption == "git-failure" and "--raw" in command:
            return command_result(tuple(command), directory, exit_code=1, stderr="git failed")
        if "cat-file" in command:
            if corruption == "blob-read-failure":
                return command_result(tuple(command), directory, exit_code=1, stderr="blob missing")
            if corruption == "bad-base64":
                return command_result(tuple(command), directory, stdout="not base64!")
            if corruption == "wrong-blob":
                return command_result(tuple(command), directory, stdout="eA==")
        return original_run(command, directory, timeout_seconds, stdin_text)

    monkeypatch.setattr(runner, "run", corrupt)
    with pytest.raises(DiffUnavailable, match="git failed|blob missing|malformed|identity"):
        review(repository, runner, DiffSource.STAGED)
    assert not model_prompts
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)


@pytest.mark.parametrize("as_json", (False, True))
def test_cli_reports_selected_file_formatting_coverage(
    repository: Path, model_prompts: list[str], monkeypatch, capsys, as_json
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    monkeypatch.chdir(repository)
    monkeypatch.setattr("atom.cli.SubprocessRunner", ReviewRunner)
    arguments = ["review", "--working", "--model", "fixture-model", "--runs", "1"]
    if as_json:
        arguments.append("--json")

    assert main(arguments) == EXIT_PASSED

    output = capsys.readouterr().out
    if as_json:
        payload = json.loads(output)
        formatting = next(gate for gate in payload["toolchain"]["gates"] if gate["name"] == "fmt")
        assert formatting["status"] == "passed"
        assert "changed.go" in formatting["summary"]
        assert "unstaged working-tree changes" in formatting["summary"]
    else:
        assert "gofmt -l ." not in output
        assert "changed Go files" in output
        assert "changed.go" in output
        assert "unstaged working-tree changes" in output


def test_non_go_type_change_does_not_break_changed_go_snapshot_pairing(
    repository: Path, model_prompts: list[str]
):
    (repository / "first.txt").write_bytes(BASE.encode())
    git(repository, "add", "first.txt")
    git(repository, "commit", "--quiet", "-m", "regular text fixture")
    identity = git(repository, "rev-parse", "HEAD:first.txt").strip()
    git(repository, "update-index", "--cacheinfo", f"120000,{identity},first.txt")
    (repository / "changed.go").write_bytes(CLEAN.encode())
    git(repository, "add", "changed.go")
    runner = ReviewRunner()

    outcome = review(repository, runner, DiffSource.STAGED)

    assert outcome.diff.files == ("changed.go", "first.txt")
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [CLEAN]
    assert len(model_prompts) == 1


@pytest.mark.parametrize(
    "failing_command",
    (
        ("go", "build", "./..."), ("go", "vet", "./..."),
        ("go", "test", "./..."), ("go", "test", "-race", "./..."),
    ),
)
def test_non_format_required_gate_commands_and_failures_remain_unchanged(
    repository: Path, model_prompts: list[str], monkeypatch, failing_command
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()
    original_run = runner.run

    def fail_required(command, directory, timeout_seconds=300, stdin_text=None):
        result = original_run(command, directory, timeout_seconds, stdin_text)
        if tuple(command) == failing_command:
            return replace(result, exit_code=1, stdout="", stderr="required check failed")
        return result

    monkeypatch.setattr(runner, "run", fail_required)
    with pytest.raises(ToolchainGateFailed) as raised:
        review(repository, runner)
    assert any("required check failed" in gate.details for gate in raised.value.failures)
    assert [command for command, _ in runner.calls if command[0] == "go"] == [
        ("go", "build", "./..."), ("go", "vet", "./..."),
        ("go", "test", "./..."), ("go", "test", "-race", "./..."),
    ]
    assert [command for command, _ in runner.calls if command[0] in (
        "staticcheck", "errcheck", "govulncheck",
    )] == [("staticcheck", "./..."), ("errcheck", "./..."), ("govulncheck", "./...")]
    assert model_prompts == []


@pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED, DiffSource.BRANCH))
def test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean(
    repository: Path, model_prompts: list[str], source
):
    base = git(repository, "rev-parse", "HEAD").strip()
    (repository / "changed.go").write_bytes(BAD.encode())
    if source is not DiffSource.WORKING:
        git(repository, "add", "changed.go")
        if source is DiffSource.BRANCH:
            git(repository, "commit", "--quiet", "-m", "bad selected source")
        (repository / "changed.go").write_bytes(CLEAN.encode())
    with pytest.raises(ToolchainGateFailed, match="fmt"):
        review(repository, ReviewRunner(), source, base if source is DiffSource.BRANCH else None)
    assert model_prompts == []


def test_captured_content_is_reused_when_checks_change_working_tree(
    repository: Path, model_prompts: list[str], monkeypatch
):
    (repository / "changed.go").write_bytes(CLEAN.encode())
    runner = ReviewRunner()
    original_run = runner.run

    def change_during_checks(command, directory, timeout_seconds=300, stdin_text=None):
        if tuple(command) == ("go", "build", "./..."):
            (repository / "changed.go").write_bytes(BAD.encode())
        return original_run(command, directory, timeout_seconds, stdin_text)

    monkeypatch.setattr(runner, "run", change_during_checks)
    outcome = review(repository, runner)

    assert outcome.diff.files == ("changed.go",)
    assert "+var Value = 2" in outcome.diff.text
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [CLEAN]
    assert len([command for command, _ in runner.calls if "--raw" in command]) == 1
    assert len(model_prompts) == 1


def test_invalid_branch_ref_fails_before_checks_or_models(
    repository: Path, model_prompts: list[str]
):
    runner = ReviewRunner()
    with pytest.raises(DiffUnavailable, match="Could not capture"):
        review(repository, runner, DiffSource.BRANCH, "--help")
    assert not model_prompts
    assert not any(command[0] in ("go", "gofmt") for command, _ in runner.calls)


def test_untracked_go_file_is_not_added_to_working_diff_scope(
    repository: Path, model_prompts: list[str]
):
    (repository / "untracked.go").write_bytes(BAD.encode())
    runner = ReviewRunner()
    outcome = review(repository, runner)
    assert outcome.diff.is_empty
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)


@pytest.mark.parametrize("display", ("log", "diff"))
def test_submodule_display_config_cannot_change_manifest_patch_framing(
    repository: Path, model_prompts: list[str], display
):
    dependency = repository / "dependency"
    dependency.mkdir()
    git(dependency, "init", "--quiet", "--initial-branch=main")
    (dependency / "source.txt").write_text("before\n", encoding="utf-8")
    git(dependency, "add", "source.txt")
    git(dependency, "commit", "--quiet", "-m", "dependency before")
    first = git(dependency, "rev-parse", "HEAD").strip()
    git(repository, "update-index", "--add", "--cacheinfo", f"160000,{first},dependency")
    git(repository, "commit", "--quiet", "-m", "dependency pointer fixture")
    (dependency / "source.txt").write_text("after\n", encoding="utf-8")
    git(dependency, "add", "source.txt")
    git(dependency, "commit", "--quiet", "-m", "dependency after")
    second = git(dependency, "rev-parse", "HEAD").strip()
    git(repository, "update-index", "--cacheinfo", f"160000,{second},dependency")
    (repository / "changed.go").write_bytes(CLEAN.encode())
    git(repository, "add", "changed.go")
    git(repository, "config", "--local", "diff.submodule", display)
    runner = ReviewRunner()

    outcome = review(repository, runner, DiffSource.STAGED)

    assert outcome.diff.files == ("changed.go", "dependency")
    assert [text for command, text in runner.calls if command[0] == "gofmt"] == [CLEAN]
    assert len(model_prompts) == 1
    assert git(repository, "config", "--local", "--get", "diff.submodule").strip() == display


@pytest.mark.parametrize("character", (":", "\\"))
@pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
    repository: Path, model_prompts: list[str], monkeypatch, character, scope
):
    """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
    directory = repository
    original_name = "changed.go"
    if scope == "outside-module":
        directory = repository / "service"
        directory.mkdir()
        (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
        git(repository, "add", "--all")
        git(repository, "commit", "--quiet", "-m", "selected module")
    if scope == "deleted":
        git(repository, "rm", "--quiet", original_name)
    else:
        if scope == "non-go":
            original_name = "notes.txt"
        (repository / original_name).write_bytes(CLEAN.encode())
        git(repository, "add", original_name)
    name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
    runner = ReviewRunner()
    original_run = runner.run

    def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
        result = original_run(command, working_directory, timeout_seconds, stdin_text)
        if "--raw" in command:
            metadata, patch = result.stdout.split("\0\0", 1)
            metadata = metadata.replace("\0" + original_name, "\0" + name)
            result = replace(result, stdout=metadata + "\0\0" + patch)
        return result

    monkeypatch.setattr(runner, "run", selected_name)

    outcome = review(directory, runner, DiffSource.STAGED)

    assert outcome.diff.files == (name,)
    formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
    assert formatting.status is GateStatus.SKIPPED
    assert len(model_prompts) == 1
    assert not any(command[0] == "gofmt" for command, _ in runner.calls)
