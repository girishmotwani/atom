"""Native PR entry must reuse the existing reviewer without changing local modes."""

from contextlib import contextmanager
import json
import hashlib

import pytest

from atom.cli import EXIT_CHECK_FAILED, EXIT_PASSED, EXIT_USAGE_ERROR, main
from atom.review import DEFAULT_REVIEW_MODELS
from atom.pull_request import PullRequestReviewError, prepare_pull_request_review
from tests.conftest import command_result
from tests.test_cli_review import ScriptedRunner
from tests.test_pull_request import BASE, SOURCE, TARGET, CheckoutRunner

PR_URL = "https://dev.azure.com/example/project/_git/repository/pullrequest/42"


def invoke(*arguments):
    try:
        return main(["review", *arguments])
    except SystemExit as error:
        return error.code


def test_pr_source_dispatch(monkeypatch, capsys):
    calls = []

    @contextmanager
    def prepare(pr_url, module_directory, runner):
        calls.append((pr_url, module_directory))
        raise ValueError("test reached PR preparation")
        yield

    monkeypatch.setattr("atom.cli.prepare_pull_request_review", prepare, raising=False)
    assert invoke("--pr", PR_URL) == EXIT_USAGE_ERROR
    assert [url for url, _ in calls] == [PR_URL]
    assert "test reached PR preparation" in capsys.readouterr().err


@pytest.mark.parametrize("extra", [
    ["--working"], ["--staged"], ["--branch", "main"],
    ["--runs", "0"], ["--concurrency", "0"], ["--window", "-1"],
])
def test_pr_invalid_options_fail_before_preparation(monkeypatch, capsys, extra):
    calls = []

    @contextmanager
    def prepare(*arguments):
        calls.append(arguments)
        raise ValueError("preparation should not run")
        yield

    monkeypatch.setattr("atom.cli.prepare_pull_request_review", prepare)
    assert invoke("--pr", PR_URL, *extra) == EXIT_USAGE_ERROR
    assert calls == []
    assert capsys.readouterr().err


@pytest.fixture
def prepared_cli(tmp_path, monkeypatch):
    (tmp_path / "go.mod").write_text("module example.test/project\n")
    checkout_runner = CheckoutRunner(tmp_path)
    monkeypatch.chdir(tmp_path)

    @contextmanager
    def prepare(url, directory, runner):
        with prepare_pull_request_review(url, directory, checkout_runner) as prepared:
            yield prepared

    class LiveCheckoutModels(ScriptedRunner):
        def run(self, command, working_directory, timeout_seconds=300.0, stdin_text=None):
            assert checkout_runner.checkout.exists()
            assert working_directory == checkout_runner.checkout
            return super().run(command, working_directory, timeout_seconds, stdin_text)

    models = LiveCheckoutModels()
    monkeypatch.setattr("atom.cli.prepare_pull_request_review", prepare)
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: models)
    return checkout_runner, models


@pytest.mark.parametrize("as_json", [True, False])
def test_pr_report_provenance_and_limitations(prepared_cli, capsys, as_json):
    checkout_runner, models = prepared_cli
    arguments = ["--pr", PR_URL, "--runs", "1", "--skip-toolchain"]
    if as_json:
        arguments.append("--json")
    assert invoke(*arguments) == EXIT_PASSED
    output = capsys.readouterr().out
    if as_json:
        payload = json.loads(output)
        provenance = payload.get("pull_request")
        assert provenance is not None, "JSON must identify the PR and pinned inputs"
        assert provenance["url"] == PR_URL
        assert provenance["source_commit"] == SOURCE
        assert provenance["target_commit"] == TARGET
        assert provenance["merge_base"] == BASE
        assert provenance["module_path"] == "."
        output = json.dumps(provenance)
    else:
        assert PR_URL in output
        assert all(pin in output for pin in (SOURCE, TARGET, BASE))
    assert "initialized module rules" in output.lower()
    assert "surrounding" in output.lower()
    assert "selected module" in output.lower()
    assert not checkout_runner.checkout.parent.exists()


def test_pr_review_options_and_partial_status(prepared_cli, capsys, tmp_path):
    checkout_runner, models = prepared_cli
    (tmp_path / "AGENTS.md").write_text(
        "LOCAL_PARTIAL_POLICY: preserve rollback", encoding="utf-8",
    )
    models.failing_models = ("bad-model",)
    assert invoke(
        "--pr", PR_URL, "--skip-toolchain", "--model", "good-model", "--model", "bad-model",
        "--runs", "2", "--concurrency", "1", "--window", "3",
        "--disable-mcp-server", "example-server", "--json",
    ) == EXIT_CHECK_FAILED
    payload = json.loads(capsys.readouterr().out)
    assert payload["is_partial"] is True
    assert {entry["model"] for entry in payload["models"]} == {"good-model", "bad-model"}
    assert all(entry["runs_requested"] == 2 for entry in payload["models"])
    assert payload["module_rules"]["status"] == "loaded"
    assert all("LOCAL_PARTIAL_POLICY" in text for text in models.stdin_texts if text is not None)
    reviews = [command for command in models.commands if "--no-custom-instructions" in command
               and "-p" not in command]
    assert reviews
    assert all("example-server" in command for command in reviews)
    assert not checkout_runner.checkout.parent.exists()


def test_pr_no_model_available_is_not_clean_review(prepared_cli, capsys):
    checkout_runner, models = prepared_cli
    models.unavailable_models = ("unavailable",)
    assert invoke(
        "--pr", PR_URL, "--skip-toolchain", "--model", "unavailable",
    ) == EXIT_CHECK_FAILED
    output = capsys.readouterr()
    assert "not a clean review" in output.err
    assert output.out == ""
    assert not checkout_runner.checkout.parent.exists()


def test_pr_transport_failure_is_partial_and_still_cleans_checkout(prepared_cli, capsys):
    checkout_runner, models = prepared_cli
    models.transport_replies = {model: "[]" for model in DEFAULT_REVIEW_MODELS}

    assert invoke(
        "--pr", PR_URL, "--skip-toolchain", "--runs", "1", "--json",
    ) == EXIT_CHECK_FAILED
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload["is_partial"]
    assert payload["has_no_usable_response"]
    assert payload["pull_request"]["source_commit"] == SOURCE
    assert "CLI response transport:" in captured.err
    assert not checkout_runner.checkout.parent.exists()


@pytest.mark.parametrize("fixed_evidence", [False, True])
def test_pr_required_checks_still_block(
    prepared_cli, monkeypatch, capsys, fixed_evidence,
):
    checkout_runner, models = prepared_cli
    original_run = models.run

    def run(command, working_directory, timeout_seconds=300.0, stdin_text=None):
        if tuple(command) == ("git", "rev-parse", "--show-toplevel"):
            return command_result(
                tuple(command), working_directory, stdout=str(working_directory) + "\n",
            )
        if command[0] == "git" and "--raw" in command:
            return command_result(tuple(command), working_directory)
        if command[0] not in ("git", "copilot"):
            failed = tuple(command) == ("go", "build", "./...")
            return command_result(
                tuple(command), working_directory, exit_code=1 if failed else 0,
                stderr="compiler failure evidence" if failed else "",
                stdout="ok fixture 0.01s\n" if command[0] == "go" and not failed else "",
            )
        return original_run(command, working_directory, timeout_seconds, stdin_text)

    monkeypatch.setattr(models, "run", run)
    options = ["--fixed-evidence"] if fixed_evidence else []
    assert invoke("--pr", PR_URL, *options) == EXIT_CHECK_FAILED
    output = capsys.readouterr()
    assert "compiler failure evidence" in output.err
    assert output.out == ""
    assert not any(command[0] == "copilot" for command in models.commands)
    assert not checkout_runner.checkout.parent.exists()


def test_cleanup_failure_prevents_success_output(prepared_cli, monkeypatch, capsys):
    checkout_runner, models = prepared_cli
    real_prepare = prepare_pull_request_review

    @contextmanager
    def fail_after_review(url, directory, runner):
        with real_prepare(url, directory, checkout_runner) as prepared:
            yield prepared
        raise PullRequestReviewError("cleanup failure fixture")

    monkeypatch.setattr("atom.cli.prepare_pull_request_review", fail_after_review)
    assert invoke("--pr", PR_URL, "--skip-toolchain", "--runs", "1") == EXIT_CHECK_FAILED
    output = capsys.readouterr()
    assert output.out == ""
    assert "cleanup failure fixture" in output.err


def test_local_reports_have_no_pr_fields(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: ScriptedRunner())
    assert invoke("--working", "--skip-toolchain", "--runs", "1", "--json") == EXIT_PASSED
    assert "pull_request" not in json.loads(capsys.readouterr().out)


@pytest.mark.parametrize("as_json", [False, True])
def test_pr_context_is_captured_before_preparation_from_launch_directory(
    prepared_cli, tmp_path, monkeypatch, capsys, as_json,
):
    from atom import cli

    checkout_runner, models = prepared_cli
    content = b"private pinned caller contract\r\n"
    source = tmp_path / "caller.md"
    source.write_bytes(content)
    original_loader = cli.load_context_documents
    original_prepare = cli.prepare_pull_request_review
    captures = []

    def capture(paths, base_directory):
        assert base_directory == tmp_path
        documents = original_loader(paths, base_directory)
        captures.append(documents)
        return documents

    @contextmanager
    def prepare(*args):
        assert len(captures) == 1
        source.unlink()
        with original_prepare(*args) as prepared:
            assert not (prepared.working_directory / "caller.md").exists()
            yield prepared

    monkeypatch.setattr(cli, "load_context_documents", capture)
    monkeypatch.setattr(cli, "prepare_pull_request_review", prepare)
    arguments = [
        "--pr", PR_URL, "--fixed-evidence", "--context-file", "caller.md",
        "--skip-toolchain", "--runs", "1",
    ]
    if as_json:
        arguments.append("--json")
    assert invoke(*arguments) == EXIT_PASSED
    text = capsys.readouterr().out
    assert "private pinned caller contract" not in text
    assert "initialized module rules" in text.lower()
    assert "selected module" in text.lower()
    assert "not automatically collected" in text
    assert "caller evidence" in text
    assert not checkout_runner.checkout.parent.exists()
    assert len(captures) == 1
    assert all(
        "private pinned caller contract" in prompt
        for prompt in models.stdin_texts if prompt is not None
    )
    if as_json:
        payload = json.loads(text)
        assert payload["pull_request"]["source_commit"] == SOURCE
        assert payload["pull_request"]["target_commit"] == TARGET
        assert payload["pull_request"]["merge_base"] == BASE
        assert payload["review_execution"]["documents"] == [{
            "label": "context-1", "utf8_bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }]


def test_pr_context_failure_prevents_preparation(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    def forbidden(*args):
        pytest.fail("invalid requested evidence must fail before PR preparation")

    monkeypatch.setattr("atom.cli.prepare_pull_request_review", forbidden)
    assert invoke(
        "--pr", PR_URL, "--fixed-evidence", "--context-file", "missing.md",
    ) == EXIT_CHECK_FAILED
    captured = capsys.readouterr()
    assert "context document 1 could not be read" in captured.err
    assert captured.out == ""


def test_missing_source_help_mentions_pr(capsys):
    assert invoke() == EXIT_USAGE_ERROR
    assert "--pr" in capsys.readouterr().err


@pytest.mark.parametrize("as_json", [False, True])
def test_cli_freezes_launch_rules_before_pr_preparation(
    prepared_cli, tmp_path, monkeypatch, capsys, as_json,
):
    from atom import cli

    _, models = prepared_cli
    guide_relative = ".atom/atom/skills/atom/references/go-style.md"
    guide = tmp_path / guide_relative
    guide.parent.mkdir(parents=True)
    guide.write_bytes(b"LAUNCH_GUIDE: preserve cancellation\r\n")
    agents = tmp_path / "AGENTS.md"
    agents.write_bytes(b"LAUNCH_AGENTS: rollback releases leases\n")
    original_prepare = cli.prepare_pull_request_review

    @contextmanager
    def prepare(*args):
        guide.unlink()
        agents.unlink()
        with original_prepare(*args) as prepared:
            clone_guide = prepared.working_directory / guide_relative
            clone_guide.parent.mkdir(parents=True)
            clone_guide.write_text("CHECKOUT_GUIDE must not become policy", encoding="utf-8")
            (prepared.working_directory / "AGENTS.md").write_text(
                "CHECKOUT_AGENTS must not become policy", encoding="utf-8",
            )
            yield prepared

    monkeypatch.setattr(cli, "prepare_pull_request_review", prepare)
    options = ["--json"] if as_json else []
    assert invoke("--pr", PR_URL, "--skip-toolchain", "--runs", "2", *options) == EXIT_PASSED
    output = capsys.readouterr().out
    prompts = [text for text in models.stdin_texts if text is not None]
    assert len(prompts) == 4
    assert len(set(prompts)) == 1
    assert all("LAUNCH_GUIDE" in text and "LAUNCH_AGENTS" in text for text in prompts)
    assert all("CHECKOUT_GUIDE" not in text and "CHECKOUT_AGENTS" not in text for text in prompts)
    assert "LAUNCH_GUIDE" not in output and "LAUNCH_AGENTS" not in output
    limitations = (
        json.loads(output)["pull_request"]["limitations"] if as_json else output
    )
    assert "Initialized module rules are not applied." not in limitations
    assert "selected module" in str(limitations).lower()
    assert "surrounding" in str(limitations).lower()


@pytest.mark.parametrize("pr", [False, True])
def test_cli_rule_error_prevents_preparation_or_execution(tmp_path, monkeypatch, capsys, pr):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "AGENTS.md").write_bytes(b" \r\n")
    models = ScriptedRunner()
    preparations = []

    @contextmanager
    def prepare(*args):
        preparations.append(args)
        raise ValueError("unexpected PR preparation")
        yield

    monkeypatch.setattr("atom.cli.SubprocessRunner", lambda: models)
    monkeypatch.setattr("atom.cli.prepare_pull_request_review", prepare)
    source = ["--pr", PR_URL] if pr else ["--working"]
    assert invoke(*source, "--skip-toolchain") == EXIT_CHECK_FAILED
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "module rules:" in captured.err
    assert str(tmp_path) not in captured.err
    assert models.commands == []
    assert preparations == []
