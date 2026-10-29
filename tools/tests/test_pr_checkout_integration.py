"""Real Git integration with synthetic history; only HTTPS/ADO/model I/O is replaced."""

import json
import subprocess
from pathlib import Path

import pytest

from atom.diff import capture_diff
from atom.pull_request import prepare_pull_request_review
from atom.runner import SubprocessRunner
from tests.conftest import command_result
from tests.test_cli_review import ScriptedRunner
from tests.test_pull_request import PR_URL, REMOTE_URL, metadata


def git(directory, *arguments):
    result = subprocess.run(
        ["git", "-c", "core.autocrlf=input", "-c", "core.hooksPath=",
         "-c", "user.name=Atom Fixture", "-c", "user.email=fixture@example.test",
         *arguments],
        cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.fixture
def history(tmp_path):
    server = tmp_path / "server"
    server.mkdir()
    git(server, "init", "--initial-branch=develop")
    module = server / "src" / "module"
    module.mkdir(parents=True)
    (module / "go.mod").write_text("module fixture.test/module\n", encoding="utf-8")
    (module / "feature.go").write_text("package fixture\n", encoding="utf-8")
    git(server, "add", ".")
    git(server, "commit", "-m", "base")
    base = git(server, "rev-parse", "HEAD")
    git(server, "checkout", "-b", "feature")
    (module / "feature.go").write_text("package fixture\nfunc Added() {}\n", encoding="utf-8")
    (server / "pr-notes.txt").write_text("PR change outside selected module\n", encoding="utf-8")
    git(server, "add", ".")
    git(server, "commit", "-m", "source")
    source = git(server, "rev-parse", "HEAD")
    git(server, "checkout", "develop")
    (server / "target-only.txt").write_text("unrelated target change\n", encoding="utf-8")
    git(server, "add", ".")
    git(server, "commit", "-m", "target")
    target = git(server, "rev-parse", "HEAD")
    original = tmp_path / "original"
    git(tmp_path, "clone", "--no-local", "--", str(server), str(original))
    git(original, "remote", "set-url", "origin", REMOTE_URL)
    local_module = original / "src" / "module"
    (local_module / "feature.go").write_text("package fixture\n// staged\n", encoding="utf-8")
    git(original, "add", ".")
    (local_module / "feature.go").write_text(
        "package fixture\n// staged\n// unstaged\n", encoding="utf-8",
    )
    (local_module / "untracked.txt").write_text("developer's untracked work\n", encoding="utf-8")
    data = metadata()
    data["lastMergeSourceCommit"]["commitId"] = source
    return server, original, local_module, data, (source, target, base)


class LocalTransportRunner:
    def __init__(self, server, data):
        self.server = server
        self.data = data
        self.real = SubprocessRunner()
        self.calls = []
        self.checkout = None
        self.models = ScriptedRunner()

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        command = tuple(command)
        self.calls.append((command, working_directory, timeout_seconds))
        if command[:2] == ("az", "rest"):
            return command_result(command, working_directory, stdout=json.dumps(self.data))
        if command[:2] == ("git", "clone"):
            self.checkout = Path(command[-1])
            assert command[-2] == REMOTE_URL
            # Only test transport changes: Git still performs an independent full clone.
            command = (*command[:2], "--no-local", *command[2:-2], str(self.server), command[-1])
        if command[0] == "copilot":
            assert self.checkout.exists()
            assert working_directory == self.checkout / "src" / "module"
            return self.models.run(command, working_directory, timeout_seconds, stdin_text)
        return self.real.run(command, working_directory, timeout_seconds, stdin_text)


def original_snapshot(original):
    return {
        "head": git(original, "rev-parse", "HEAD"),
        "branch": git(original, "symbolic-ref", "HEAD"),
        "files": {
            str(path.relative_to(original)): path.read_bytes()
            for path in original.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(original).parts
        },
        "git_files": {
            path: (original / path).read_bytes()
            for path in (".git/index", ".git/config", ".git/HEAD")
        },
    }


def test_real_git_merge_base_and_dirty_original_preserved(history):
    server, original, module, data, (source, target, base) = history
    before = original_snapshot(original)
    runner = LocalTransportRunner(server, data)
    with prepare_pull_request_review(PR_URL, module, runner) as prepared:
        diff = capture_diff(prepared.request, runner, prepared.working_directory)
        assert set(diff.files) == {"pr-notes.txt", "src/module/feature.go"}
        assert "target-only.txt" not in diff.text
        assert prepared.provenance.source_commit == source
        assert prepared.provenance.target_commit == target
        assert prepared.provenance.merge_base == base
        assert prepared.provenance.module_path == "src/module"
        assert git(runner.checkout, "rev-parse", "HEAD") == source
        assert not (runner.checkout / ".git/objects/info/alternates").exists()
        assert git(runner.checkout, "config", "core.autocrlf") == "input"
    assert original_snapshot(original) == before
    assert not runner.checkout.parent.exists()


def test_native_cli_uses_real_checkout_and_cleans_it(history, monkeypatch, capsys):
    from atom.cli import main

    server, original, module, data, _ = history
    before = original_snapshot(original)
    runner = LocalTransportRunner(server, data)
    monkeypatch.chdir(module)
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: runner)
    assert main(["review", "--pr", PR_URL, "--skip-toolchain", "--runs", "1", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pull_request"]["module_path"] == "src/module"
    assert set(payload["diff"]["files"]) == {"pr-notes.txt", "src/module/feature.go"}
    assert runner.models.commands
    assert original_snapshot(original) == before
    assert not runner.checkout.parent.exists()
