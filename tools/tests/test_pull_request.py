"""Checkout preparation contracts, using synthetic data and no ADO connection."""

import copy
import json
import sys
from pathlib import Path

import pytest

from atom.pull_request import PullRequestReviewError, prepare_pull_request_review
from atom.runner import CommandOutcome, SubprocessRunner
from tests.conftest import FakeRunner, command_result

PR_URL = "https://dev.azure.com/example/project/_git/repository/pullrequest/42"
REMOTE_URL = "https://example@dev.azure.com/example/project/_git/repository"
SOURCE = "a" * 40
TARGET = "b" * 40
BASE = "c" * 40


def metadata():
    return {
        "pullRequestId": 42, "status": "active",
        "sourceRefName": "refs/heads/feature", "targetRefName": "refs/heads/develop",
        "lastMergeSourceCommit": {"commitId": SOURCE},
        "repository": {
            "id": "11111111-1111-1111-1111-111111111111", "name": "repository",
            "project": {"id": "22222222-2222-2222-2222-222222222222", "name": "project"},
            "remoteUrl": REMOTE_URL,
        },
    }


@pytest.mark.parametrize("url", [
    "", "not a URL", PR_URL.replace("https:", "http:"),
    PR_URL.replace("dev.azure.com", "dev.azure.com.attacker.test"),
    PR_URL.replace("dev.azure.com", "dev.azure.com:443"),
    PR_URL.replace("dev.azure.com", "user:password@dev.azure.com"),
    PR_URL.replace("/project/", "/other%2fproject/"),
    PR_URL.replace("/project/", "/other%5cproject/"),
    PR_URL.replace("/project/", "/%2e%2e/"),
    PR_URL.replace("/project/", "/%00/"),
    PR_URL.replace("/project/", "/bad%zz/"),
    PR_URL.replace("/42", "/0"), PR_URL.replace("/42", "/-1"),
    PR_URL.replace("/42", "/42/extra"), PR_URL + "\n",
    " " + PR_URL,
])
def test_unsafe_pr_url_starts_no_command(tmp_path, url):
    runner = FakeRunner()
    with pytest.raises(Exception) as failure:
        with prepare_pull_request_review(url, tmp_path, runner):
            pytest.fail("unsafe URL was accepted")
    assert isinstance(failure.value, ValueError)
    assert "URL" in str(failure.value)
    assert runner.calls == []


def metadata_command(project="project", repository="repository"):
    return (
        "az", "rest", "--method", "get", "--resource",
        "499b84ac-1321-427f-aa17-267ca6975798", "--url",
        f"https://dev.azure.com/example/{project}/_apis/git/repositories/{repository}"
        "/pullrequests/42?api-version=7.1",
        "--output", "json", "--only-show-errors",
    )


@pytest.mark.parametrize("url", [
    PR_URL, PR_URL + "?_a=files#discussion",
    "https://example.visualstudio.com/project/_git/repository/pullrequest/42",
])
@pytest.mark.parametrize("outcome,code", [
    (CommandOutcome.TOOL_MISSING, None), (CommandOutcome.TIMED_OUT, None),
    (CommandOutcome.RUNNER_ERROR, 0), (CommandOutcome.COMPLETED, 1),
])
def test_metadata_failure_stops_before_clone(tmp_path, url, outcome, code):
    command = metadata_command()
    runner = FakeRunner({
        command: command_result(
            command, tmp_path, outcome, code, stderr="metadata access refused",
        )
    })
    with pytest.raises(Exception) as failure:
        with prepare_pull_request_review(url, tmp_path, runner):
            pytest.fail("failed metadata was accepted")
    assert isinstance(failure.value, PullRequestReviewError)
    assert "metadata access refused" in str(failure.value)
    assert runner.calls == [(command, tmp_path, 60.0)]


@pytest.mark.parametrize("change", [
    {"pullRequestId": 43}, {"status": "completed"}, {"forkSource": {"name": "fork"}},
    {"sourceRefName": "refs/heads/../escape"}, {"targetRefName": None},
    {"lastMergeSourceCommit": {"commitId": "not-a-commit"}}, {"repository": None},
    {"repository": {"name": "different"}},
])
def test_invalid_metadata_stops_before_clone(tmp_path, change):
    data = metadata()
    data.update(copy.deepcopy(change))
    assert_metadata_rejected(tmp_path, json.dumps(data))


@pytest.mark.parametrize("payload", ["{", "[]", "null", "{}", '"text"'])
def test_malformed_metadata_stops_before_clone(tmp_path, payload):
    assert_metadata_rejected(tmp_path, payload)


@pytest.mark.parametrize("remote", [
    REMOTE_URL.replace("example@", "user:password@"),
    REMOTE_URL.replace("example@", "someone@"),
    REMOTE_URL.replace("dev.azure.com", "attacker.test"),
    REMOTE_URL.replace("/repository", "/different"),
    REMOTE_URL.replace("dev.azure.com", "dev.azure.com:444"),
    REMOTE_URL + "\n", " " + REMOTE_URL,
])
def test_metadata_remote_identity_is_checked(tmp_path, remote):
    data = metadata()
    data["repository"]["remoteUrl"] = remote
    assert_metadata_rejected(tmp_path, json.dumps(data))


def assert_metadata_rejected(directory, payload):
    command = metadata_command()
    runner = FakeRunner({command: command_result(command, directory, stdout=payload)})
    with pytest.raises(Exception) as failure:
        with prepare_pull_request_review(PR_URL, directory, runner):
            pytest.fail("invalid metadata was accepted")
    assert isinstance(failure.value, PullRequestReviewError)
    assert "metadata" in str(failure.value).lower()
    assert len(runner.calls) == 1


class LocalRunner(FakeRunner):
    def __init__(self, directory, *, root=None, origin=REMOTE_URL, data=None):
        commands = {
            metadata_command(): json.dumps(data or metadata()),
            ("git", "rev-parse", "--show-toplevel"): str(root or directory),
            ("git", "remote", "get-url", "origin"): origin,
        }
        super().__init__({
            command: command_result(command, directory, stdout=stdout)
            for command, stdout in commands.items()
        })


@pytest.mark.parametrize("condition", [
    "missing module", "wrong origin", "ssh origin", "outside root",
])
def test_local_scope_is_required(tmp_path, condition):
    if condition != "missing module":
        (tmp_path / "go.mod").write_text("module example.test/project\n")
    origin = {
        "wrong origin": REMOTE_URL.replace("/repository", "/another"),
        "ssh origin": "git@ssh.dev.azure.com:v3/example/project/repository",
    }.get(condition, REMOTE_URL)
    root = tmp_path / "unrelated" if condition == "outside root" else tmp_path
    runner = LocalRunner(tmp_path, root=root, origin=origin)
    with pytest.raises(Exception) as failure:
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            pytest.fail("invalid local scope accepted")
    assert isinstance(failure.value, PullRequestReviewError)
    assert "local" in str(failure.value).lower()
    assert not any("clone" in command for command, _, _ in runner.calls)


class CheckoutRunner(LocalRunner):
    def __init__(self, directory, *, fail_clone=False):
        super().__init__(directory)
        self.checkout = None
        self.fail_clone = fail_clone

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        command = tuple(command)
        if command in self.scripted_results:
            return super().run(command, working_directory, timeout_seconds, stdin_text)
        self.calls.append((command, working_directory, timeout_seconds))
        if command[:2] == ("git", "clone"):
            self.checkout = Path(command[-1])
            self.checkout.mkdir()
            (self.checkout / "go.mod").write_text("module example.test/project\n")
            return command_result(
                command, working_directory, exit_code=128 if self.fail_clone else 0,
                stderr="clone refused" if self.fail_clone else "",
            )
        if command[0] == sys.executable:
            return SubprocessRunner().run(command, working_directory, timeout_seconds, stdin_text)
        replies = {
            ("git", "rev-parse", "--verify", "--end-of-options",
             "refs/remotes/origin/feature^{commit}"): SOURCE,
            ("git", "rev-parse", "--verify", "--end-of-options",
             "refs/remotes/origin/develop^{commit}"): TARGET,
            ("git", "merge-base", "--all", SOURCE, TARGET): BASE,
            ("git", "checkout", "--detach", SOURCE): "",
            ("git", "ls-files", "--deleted", "-z"): "",
            ("git", "diff", "--exit-code", "HEAD", "--"): "",
        }
        if command in replies:
            return command_result(command, working_directory, stdout=replies[command])
        raise AssertionError(f"unexpected command: {command}")


def test_clone_failure_is_cleaned(tmp_path):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = CheckoutRunner(tmp_path, fail_clone=True)
    with pytest.raises(Exception) as failure:
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            pytest.fail("failed clone was accepted")
    assert isinstance(failure.value, PullRequestReviewError)
    assert "clone refused" in str(failure.value)
    assert runner.checkout is not None
    assert not runner.checkout.parent.exists()
    clones = [command for command, _, _ in runner.calls if "clone" in command]
    assert len(clones) == 1
    assert REMOTE_URL in clones[0]
    assert "--no-checkout" in clones[0]
    assert "core.autocrlf=input" in clones[0]
    assert not any(
        flag in clones[0] for flag in ("--shared", "--reference", "--depth", "--filter")
    )
    cleanup = [(command, directory, timeout) for command, directory, timeout in runner.calls
               if command[0] == sys.executable]
    assert len(cleanup) == 1
    assert cleanup[0][2] == 30.0


def test_independent_clone_and_pinned_checkout(tmp_path):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = CheckoutRunner(tmp_path)
    with prepare_pull_request_review(PR_URL, tmp_path, runner) as prepared:
        assert prepared is not None, "preparation must yield a pinned checkout"
        assert prepared.working_directory == runner.checkout
        assert prepared.working_directory != tmp_path
        assert (prepared.working_directory / "go.mod").is_file()
        assert prepared.request.base_ref == TARGET
        assert prepared.provenance.url == PR_URL
        assert prepared.provenance.source_branch == "refs/heads/feature"
        assert prepared.provenance.target_branch == "refs/heads/develop"
        assert prepared.provenance.source_commit == SOURCE
        assert prepared.provenance.target_commit == TARGET
        assert prepared.provenance.merge_base == BASE
        assert prepared.provenance.module_path == "."
        assert ("git", "checkout", "--detach", SOURCE) in [
            command for command, _, _ in runner.calls
        ]
    assert not runner.checkout.parent.exists()


@pytest.mark.parametrize("command,stdout,code,message", [
    (("git", "rev-parse", "--verify", "--end-of-options",
      "refs/remotes/origin/feature^{commit}"), TARGET, 0, "source moved"),
    (("git", "rev-parse", "--verify", "--end-of-options",
      "refs/remotes/origin/develop^{commit}"), "invalid", 0, "commit ID"),
    (("git", "merge-base", "--all", SOURCE, TARGET), "", 0, "exactly one"),
    (("git", "merge-base", "--all", SOURCE, TARGET), f"{BASE}\n{TARGET}", 0, "exactly one"),
    (("git", "checkout", "--detach", SOURCE), "", 1, "checking out"),
    (("git", "ls-files", "--deleted", "-z"), "missing.go\0", 0, "missing tracked"),
    (("git", "diff", "--exit-code", "HEAD", "--"), "dirty", 1, "clean pinned"),
])
def test_snapshot_failure_prevents_review_and_is_cleaned(
    tmp_path, command, stdout, code, message,
):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = CheckoutRunner(tmp_path)
    runner.scripted_results[command] = command_result(
        command, tmp_path, stdout=stdout, exit_code=code,
    )
    with pytest.raises(PullRequestReviewError, match=message):
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            pytest.fail("invalid snapshot reached review")
    assert not runner.checkout.parent.exists()


@pytest.mark.parametrize("failure", [RuntimeError("original review failure"), KeyboardInterrupt()])
def test_cleanup_on_failure_and_interrupt(tmp_path, failure):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = CheckoutRunner(tmp_path)
    with pytest.raises(type(failure)):
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            raise failure
    assert not runner.checkout.parent.exists()


class FailedCleanupRunner(CheckoutRunner):
    def __init__(self, directory, *, interrupt=False):
        super().__init__(directory)
        self.interrupt = interrupt
        self.cleanup_command = None

    def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
        if command[0] == sys.executable:
            self.cleanup_command = tuple(command)
            if self.interrupt:
                raise KeyboardInterrupt()
            return command_result(
                tuple(command), working_directory, CommandOutcome.TIMED_OUT, None,
                stderr="cleanup worker timed out",
            )
        return super().run(command, working_directory, timeout_seconds, stdin_text)

    def rescue(self, directory):
        if self.cleanup_command is not None and self.checkout.parent.exists():
            result = SubprocessRunner().run(self.cleanup_command, directory, 30)
            assert result.succeeded, result.stderr


@pytest.mark.parametrize("primary", [False, True])
def test_cleanup_failure_preserves_primary_error(tmp_path, capsys, primary):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = FailedCleanupRunner(tmp_path)
    try:
        with pytest.raises(RuntimeError if primary else PullRequestReviewError):
            with prepare_pull_request_review(PR_URL, tmp_path, runner):
                if primary:
                    raise RuntimeError("original review failure")
        if primary:
            assert "cleanup worker timed out" in capsys.readouterr().err
        assert runner.checkout.parent.exists()
    finally:
        runner.rescue(tmp_path)


def test_cleanup_interruption_names_retained_directory(tmp_path, capsys):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = FailedCleanupRunner(tmp_path, interrupt=True)
    try:
        with pytest.raises(KeyboardInterrupt):
            with prepare_pull_request_review(PR_URL, tmp_path, runner):
                pass
        assert str(runner.checkout.parent) in capsys.readouterr().err
    finally:
        runner.rescue(tmp_path)


def test_repository_package_cannot_shadow_cleanup_worker(tmp_path):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    shadow = tmp_path / "atom"
    shadow.mkdir()
    (shadow / "__init__.py").write_text("raise RuntimeError('untrusted local atom package')\n")
    runner = CheckoutRunner(tmp_path)
    try:
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            pass
        assert not runner.checkout.parent.exists()
    finally:
        if runner.checkout is not None and runner.checkout.parent.exists():
            from atom import _checkout_cleanup
            owned = runner.checkout.parent
            result = SubprocessRunner().run(
                (sys.executable, _checkout_cleanup.__file__, str(owned),
                 (owned / ".atom-review-owner").read_text(encoding="ascii")),
                tmp_path, 30,
            )
            assert result.succeeded, result.stderr


@pytest.mark.parametrize("legacy", [False, True])
def test_percent_encoded_names_keep_their_metadata_scope(tmp_path, legacy):
    prefix = (
        "https://example.visualstudio.com"
        if legacy else "https://dev.azure.com/example"
    )
    url = prefix + "/project%20name/_git/repository%20name/pullrequest/42"
    runner = FakeRunner()
    with pytest.raises(PullRequestReviewError, match="metadata"):
        with prepare_pull_request_review(url, tmp_path, runner):
            pytest.fail("missing metadata command was ignored")
    assert runner.calls == [(
        metadata_command("project%20name", "repository%20name"), tmp_path, 60.0,
    )]


@pytest.mark.parametrize("stage", [
    ("git", "checkout", "--detach", SOURCE),
    ("git", "diff", "--exit-code", "HEAD", "--"),
])
def test_zero_exit_with_lifecycle_error_is_not_a_snapshot(tmp_path, stage):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    runner = CheckoutRunner(tmp_path)
    runner.scripted_results[stage] = command_result(
        stage, tmp_path, CommandOutcome.RUNNER_ERROR, 0, stderr="owned process cleanup failed",
    )
    with pytest.raises(PullRequestReviewError, match="owned process cleanup failed"):
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            pytest.fail("lifecycle failure reached reviewer")
    assert not runner.checkout.parent.exists()


@pytest.mark.parametrize("matching_owner", [False, True])
def test_cleanup_worker_checks_ownership_and_handles_readonly_files(tmp_path, matching_owner):
    import stat
    from atom import _checkout_cleanup

    owned = tmp_path / "atom-pr-worker-fixture"
    owned.mkdir()
    (owned / ".atom-review-owner").write_text("expected-owner", encoding="ascii")
    tracked = owned / "readonly-object"
    tracked.write_text("synthetic Git object", encoding="ascii")
    tracked.chmod(stat.S_IREAD)
    owner = "expected-owner" if matching_owner else "not-owner"
    result = SubprocessRunner().run(
        (sys.executable, _checkout_cleanup.__file__, str(owned), owner), tmp_path, 30,
    )
    if matching_owner:
        assert result.succeeded, result.stderr
        assert not owned.exists()
    else:
        assert not result.succeeded
        assert "ownership" in result.stderr
        assert tracked.read_text(encoding="ascii") == "synthetic Git object"
        tracked.chmod(stat.S_IWRITE | stat.S_IREAD)


def test_cleanup_success_exit_still_requires_path_absence(tmp_path):
    (tmp_path / "go.mod").write_text("module example.test/project\n")

    class LeavesDirectory(FailedCleanupRunner):
        def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
            if command[0] == sys.executable:
                self.cleanup_command = tuple(command)
                return command_result(tuple(command), working_directory)
            return super().run(command, working_directory, timeout_seconds, stdin_text)

    runner = LeavesDirectory(tmp_path)
    try:
        with pytest.raises(PullRequestReviewError, match="cleanup left owned checkout"):
            with prepare_pull_request_review(PR_URL, tmp_path, runner):
                pass
    finally:
        runner.rescue(tmp_path)


def test_pr_module_must_still_have_go_mod_file(tmp_path):
    (tmp_path / "go.mod").write_text("module example.test/project\n")

    class RemovesModuleFile(CheckoutRunner):
        def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
            result = super().run(command, working_directory, timeout_seconds, stdin_text)
            if tuple(command) == ("git", "checkout", "--detach", SOURCE):
                module_file = self.checkout / "go.mod"
                module_file.unlink()
                module_file.mkdir()
            return result

    runner = RemovesModuleFile(tmp_path)
    with pytest.raises(PullRequestReviewError, match="cloned module has no go.mod"):
        with prepare_pull_request_review(PR_URL, tmp_path, runner):
            pytest.fail("missing cloned Go module reached reviewer")
    assert not runner.checkout.parent.exists()
