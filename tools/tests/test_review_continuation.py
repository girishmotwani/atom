from __future__ import annotations

import json
import stat
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from atom._review_format import ChangedFilesFormatGate, FormattingFile
import atom.review as review_module
from atom.diff import DiffSource
from atom.gates import BuildGate, GateResult, GateStatus
from atom.go_selection import (
    GoToolchainRequest, GoToolchainSelection, GoToolchainSelectionError,
)
from atom.review import ToolchainGateFailed, run_review
from atom.report import render_review_json, render_review_markdown
from atom.runner import CommandOutcome
from atom.toolchain import ToolchainEvidence
from tests.conftest import FakeRunner, command_result
from tests.test_go_selection import distribution, distribution_runner
from tests.test_review_toolchain import pinned_review_fixture


@pytest.mark.parametrize(("directive", "expected"), [
    ("go 1.27\n", (1, 27, 0)),
    ("go 1.27.3\n", (1, 27, 3)),
    ("module example.com/project\n\ngo 1.27.3 // minimum supported Go\n", (1, 27, 3)),
    ("module example.com/project\n", None),
    ("go 1.27\n\ngo 1.28\n", None),
    ("go 1.027.0\n", None),
    ("go 1.27rc1\n", None),
    ("go latest\n", None),
])
def test_module_minimum_version_requires_one_unambiguous_go_directive(
    tmp_path: Path, directive: str, expected: tuple[int, int, int] | None,
):
    module_file = tmp_path / "go.mod"
    module_file.write_text(directive, encoding="utf-8")

    parser = getattr(review_module, "_read_module_minimum_version", None)
    assert callable(parser), "review continuation must parse the module minimum version"
    assert parser(module_file) == expected


@pytest.mark.parametrize("read_error", [
    PermissionError("permission denied"),
    UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
], ids=("unreadable", "invalid-utf8"))
def test_module_minimum_version_read_failures_are_contextual(
    tmp_path: Path, monkeypatch, read_error,
):
    module_file = tmp_path / "go.mod"
    original_read_text = Path.read_text

    def fail_module_read(path, *arguments, **keywords):
        if path == module_file:
            raise read_error
        return original_read_text(path, *arguments, **keywords)

    monkeypatch.setattr(Path, "read_text", fail_module_read)

    with pytest.raises(
        review_module.ControlToolchainError,
        match="reading Go module minimum from",
    ) as raised:
        review_module._read_module_minimum_version(module_file)

    assert str(module_file) in str(raised.value)
    assert str(read_error) in str(raised.value)


@pytest.mark.parametrize(("outcome", "exit_code"), [
    (CommandOutcome.COMPLETED, 2),
    (CommandOutcome.TIMED_OUT, None),
    (CommandOutcome.TOOL_MISSING, None),
    (CommandOutcome.RUNNER_ERROR, None),
])
def test_build_gate_retains_command_lifecycle_evidence(
    tmp_path: Path, outcome: CommandOutcome, exit_code: int | None,
):
    (tmp_path / "go.mod").write_text("module example.com/project\n", encoding="utf-8")
    command = ("go", "build", "./...")
    runner = FakeRunner({
        command: command_result(
            command, tmp_path, outcome=outcome, exit_code=exit_code,
            stderr="fixture diagnostic",
        ),
    })

    result = BuildGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.FAILED
    assert getattr(result, "command_outcome", None) is outcome
    assert getattr(result, "command_exit_code", None) == exit_code


@pytest.mark.parametrize(("build_status", "build_outcome", "build_exit_code", "expected_calls"), [
    (GateStatus.FAILED, CommandOutcome.COMPLETED, 1, ["fmt", "build"]),
    (GateStatus.FAILED, CommandOutcome.TIMED_OUT, None, ["fmt", "build"]),
    (GateStatus.PASSED, CommandOutcome.COMPLETED, 0, ["fmt", "build", "vet", "test", "race"]),
])
def test_candidate_gate_order_and_build_short_circuit(
    tmp_path: Path, monkeypatch, build_status, build_outcome, build_exit_code, expected_calls,
):
    calls = []

    class ScriptedGate:
        def __init__(self, name, status, outcome=None, exit_code=None):
            self.name = name
            self.required = True
            self.result = GateResult(
                name, status, f"{name} result", "", True, 0.1, outcome, exit_code,
            )

        def evaluate(self, runner, directory):
            calls.append(self.name)
            return self.result

    selected_gates = [
        ScriptedGate("build", build_status, build_outcome, build_exit_code),
        ScriptedGate("vet", GateStatus.PASSED, CommandOutcome.COMPLETED, 0),
        ScriptedGate("fmt", GateStatus.PASSED, CommandOutcome.COMPLETED, 0),
        ScriptedGate("test", GateStatus.PASSED, CommandOutcome.COMPLETED, 0),
        ScriptedGate("race", GateStatus.PASSED, CommandOutcome.COMPLETED, 0),
    ]
    monkeypatch.setattr(review_module, "default_gates", lambda enable_race: selected_gates)
    collector = getattr(review_module, "_collect_candidate_required_gates", None)
    assert callable(collector), "continuation candidates need ordered required-gate collection"

    results = collector(tmp_path, FakeRunner({}), selected_gates[2])

    assert calls == expected_calls
    assert [result.name for result in results] == ["fmt", "build", "vet", "test", "race"][
        :len(results)
    ]
    if build_status is GateStatus.FAILED and build_outcome is CommandOutcome.COMPLETED:
        assert [result.status for result in results] == [
            GateStatus.PASSED, GateStatus.FAILED, GateStatus.SKIPPED,
            GateStatus.SKIPPED, GateStatus.SKIPPED,
        ]
        assert all("because the selected build failed" in result.summary for result in results[2:])
    elif build_status is GateStatus.FAILED:
        assert [result.status for result in results] == [GateStatus.PASSED, GateStatus.FAILED]
    else:
        assert all(result.status is GateStatus.PASSED for result in results)


def test_candidate_format_failure_stops_before_build(
    tmp_path: Path, monkeypatch,
):
    calls = []

    class ScriptedGate:
        def __init__(self, name, status):
            self.name = name
            self.required = True
            self.result = GateResult(
                name, status, f"{name} result", "", True, 0.1,
            )

        def evaluate(self, runner, directory):
            calls.append(self.name)
            return self.result

    selected_gates = [
        ScriptedGate("build", GateStatus.PASSED),
        ScriptedGate("vet", GateStatus.PASSED),
        ScriptedGate("fmt", GateStatus.PASSED),
        ScriptedGate("test", GateStatus.PASSED),
        ScriptedGate("race", GateStatus.PASSED),
    ]
    monkeypatch.setattr(review_module, "default_gates", lambda enable_race: selected_gates)
    format_gate = ScriptedGate("fmt", GateStatus.FAILED)

    results = review_module._collect_candidate_required_gates(
        tmp_path, FakeRunner({}), format_gate,
    )

    assert calls == ["fmt"]
    assert [result.status for result in results] == [GateStatus.FAILED]


@pytest.mark.parametrize(("name", "mutation", "expected"), [
    ("exact candidate shape", None, True),
    ("format failed", ("fmt", {"status": GateStatus.FAILED}), False),
    ("build timed out", ("build", {
        "command_outcome": CommandOutcome.TIMED_OUT, "command_exit_code": None,
    }), False),
    ("build exit code is zero", ("build", {"command_exit_code": 0}), False),
    ("build lifecycle is unknown", ("build", {
        "command_outcome": None, "command_exit_code": None,
    }), False),
    ("vet failed", ("vet", {"status": GateStatus.FAILED}), False),
    ("test skip is unrelated", ("test", {
        "summary": "Skipped for another reason",
    }), False),
])
def test_only_proven_selected_failure_shape_is_eligible(name, mutation, expected):
    results = [
        GateResult("fmt", GateStatus.PASSED, "format passed", "", True, 0.1),
        GateResult(
            "build", GateStatus.FAILED, "build failed", "", True, 0.1,
            CommandOutcome.COMPLETED, 1,
        ),
        *[
            GateResult(
                gate_name, GateStatus.SKIPPED,
                "Skipped because the selected build failed", "", True, 0.0,
            )
            for gate_name in ("vet", "test", "race")
        ],
    ]
    if mutation is not None:
        gate_name, changes = mutation
        results = [
            replace(result, **changes) if result.name == gate_name else result
            for result in results
        ]
    evidence = ToolchainEvidence(
        gate_results=tuple(results), was_run=True, skip_reason="",
    )

    assert review_module._has_proven_selected_build_failure(evidence) is expected, name


@pytest.mark.parametrize(("minimum", "observed", "strict", "verified", "expected"), [
    ("1.27.0", "1.26.9", False, True, True),
    ("1.27.0", "1.27.0", False, True, False),
    ("1.27.0", "1.28.0", False, True, False),
    ("1.27.0", "1.26.9", True, True, False),
    ("invalid", "1.26.9", False, True, False),
    ("1.27.0", "unknown", False, True, False),
    ("1.27.0", "1.26.9", False, False, False),
])
def test_continuation_candidate_requires_verified_lower_selection(
    tmp_path: Path, minimum, observed, strict, verified, expected,
):
    module_file = tmp_path / "go.mod"
    module_file.write_text(
        f"module example.com/project\ngo {minimum}\n", encoding="utf-8",
    )
    request = GoToolchainRequest("1.26.9", "cli")
    selection = GoToolchainSelection(
        request,
        status="verified" if verified else "not_run",
        observed_version=observed,
        executable=tmp_path / "go.exe" if verified else None,
    )
    candidate_check = getattr(review_module, "_is_continuation_candidate", None)
    assert callable(candidate_check), "continuation requires structured version eligibility"

    assert candidate_check(module_file, request, selection, strict_toolchain=strict) is expected


@pytest.mark.parametrize(("module_exists", "request_present", "selection_present"), [
    (False, True, True),
    (True, False, True),
    (True, True, False),
])
def test_continuation_candidate_requires_module_and_explicit_selection(
    tmp_path: Path, module_exists: bool, request_present: bool, selection_present: bool,
):
    module_file = tmp_path / "go.mod"
    if module_exists:
        module_file.write_text(
            "module example.com/project\ngo 1.27.0\n", encoding="utf-8",
        )
    request = GoToolchainRequest("1.26.9", "cli") if request_present else None
    selection = (
        GoToolchainSelection(
            request, status="verified", observed_version="1.26.9",
            executable=tmp_path / "go.exe",
        )
        if selection_present and request is not None else None
    )

    assert not review_module._is_continuation_candidate(
        module_file, request, selection, strict_toolchain=False,
    )


@pytest.mark.parametrize(("strict", "expected_gate_calls"), [
    (False, [("gofmt",), ("build", "./...")]),
    (True, [
        ("build", "./..."), ("vet", "./..."), ("gofmt",), ("test", "./..."),
        ("test", "-race", "./..."),
    ]),
])
def test_review_runs_candidate_gates_in_order_and_strict_mode_stays_all_gates(
    tmp_path: Path, monkeypatch, strict, expected_gate_calls,
):
    if strict:
        monkeypatch.setattr(
            review_module, "_resolve_control_toolchain",
            lambda *args, **kwargs: pytest.fail("strict mode attempted a control toolchain"),
        )
    binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    (tmp_path / "go.mod").write_text(
        "module example.com/fixture\ngo 1.27.0\n", encoding="utf-8",
    )
    build = (str(binary), "build", "./...")
    runner.scripted_results[build] = command_result(
        build, tmp_path, exit_code=1, stderr="selected build failed",
    )

    with pytest.raises((ToolchainGateFailed, GoToolchainSelectionError)):
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=binary,
            ),
            strict_toolchain=strict,
        )

    formatter = binary.with_name("gofmt.exe" if binary.name.endswith(".exe") else "gofmt")
    selected_gates = []
    for command, _, _ in runner.calls:
        if command and command[0] == str(formatter):
            selected_gates.append(("gofmt",))
        elif command and command[0] == str(binary) and command[1:] in {
            ("build", "./..."), ("vet", "./..."), ("test", "./..."),
            ("test", "-race", "./..."),
        }:
            selected_gates.append(command[1:])
    assert selected_gates == expected_gate_calls
    assert model_calls == []


def test_selected_build_timeout_does_not_resolve_or_run_control(
    tmp_path: Path, monkeypatch,
):
    selected_binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    control_binary = distribution(tmp_path / "control", "1.27.3")
    control_runner = distribution_runner(control_binary, tmp_path)
    runner.scripted_results.update(control_runner.scripted_results)
    (tmp_path / "go.mod").write_text(
        "module example.com/fixture\ngo 1.27.0\n", encoding="utf-8",
    )
    selected_build = (str(selected_binary), "build", "./...")
    runner.scripted_results[selected_build] = command_result(
        selected_build, tmp_path, outcome=CommandOutcome.TIMED_OUT, stderr="timed out",
    )

    with pytest.raises(ToolchainGateFailed):
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
            control_go_version="1.27.3",
        )

    assert all(command[0] != str(control_binary) for command, _, _ in runner.calls)
    assert model_calls == []


def test_default_control_resolves_and_verifies_direct_path_distribution(tmp_path: Path):
    binary = distribution(tmp_path / "control", "1.27.3")
    runner = distribution_runner(binary, tmp_path)
    version_probe, environment_probe = tuple(runner.scripted_results)
    runner.scripted_results[version_probe] = command_result(
        version_probe, tmp_path, stdout="go version go1.27.3 windows/amd64\n",
    )
    runner.scripted_results[environment_probe] = command_result(
        environment_probe, tmp_path, stdout=json.dumps({
            "GOVERSION": "go1.27.3",
            "GOROOT": str(binary.parent.parent),
            "GOTOOLCHAIN": "local",
            "GOENV": "off",
        }),
    )
    resolver = getattr(review_module, "_resolve_path_control_toolchain", None)
    assert callable(resolver), "default control must resolve from PATH and verify its identity"

    selection = resolver(
        (1, 27, 0), runner, tmp_path, environment={"PATH": str(binary.parent)},
    )

    assert selection.status == "verified"
    assert selection.observed_version == "1.27.3"
    assert selection.executable == binary
    assert selection.selection_source == "path"
    assert selection.executable_sha256 is not None


def test_path_control_version_decode_failure_is_contextual(
    tmp_path: Path, monkeypatch,
):
    binary = distribution(tmp_path / "control", "1.27.3")
    runner = distribution_runner(binary, tmp_path)
    version_file = binary.parent.parent / "VERSION"
    original_read_text = Path.read_text
    decode_error = UnicodeDecodeError(
        "utf-8", b"\xff", 0, 1, "invalid start byte",
    )

    def fail_version_read(path, *arguments, **keywords):
        if path == version_file:
            raise decode_error
        return original_read_text(path, *arguments, **keywords)

    monkeypatch.setattr(Path, "read_text", fail_version_read)

    with pytest.raises(
        review_module.ControlToolchainError,
        match="reading PATH Go distribution",
    ) as raised:
        review_module._resolve_path_control_toolchain(
            (1, 27, 0), runner, tmp_path,
            environment={"PATH": str(binary.parent)},
        )

    assert str(binary.parent) in str(raised.value)
    assert str(decode_error) in str(raised.value)


def test_control_version_override_uses_exact_local_resolution(tmp_path: Path):
    binary = distribution(tmp_path / "control", "1.27.3")
    runner = distribution_runner(binary, tmp_path)
    version_probe, environment_probe = tuple(runner.scripted_results)
    runner.scripted_results[version_probe] = command_result(
        version_probe, tmp_path, stdout="go version go1.27.3 windows/amd64\n",
    )
    runner.scripted_results[environment_probe] = command_result(
        environment_probe, tmp_path, stdout=json.dumps({
            "GOVERSION": "go1.27.3",
            "GOROOT": str(binary.parent.parent),
            "GOTOOLCHAIN": "local",
            "GOENV": "off",
        }),
    )
    resolver = getattr(review_module, "_resolve_control_toolchain", None)
    assert callable(resolver), "control override must use exact local toolchain resolution"

    selection = resolver(
        (1, 27, 0), runner, tmp_path,
        environment={"PATH": str(binary.parent)}, exact_version="1.27.3",
    )

    assert selection.status == "verified"
    assert selection.request.version == "1.27.3"
    assert selection.executable == binary
    with pytest.raises(GoToolchainSelectionError):
        resolver(
            (1, 27, 0), runner, tmp_path,
            environment={"PATH": str(binary.parent)}, exact_version="1.28.0",
        )

    older_binary = distribution(tmp_path / "older-control", "1.26.9")
    older_runner = distribution_runner(older_binary, tmp_path)
    with pytest.raises(review_module.ControlToolchainError, match="below module minimum"):
        resolver(
            (1, 27, 0), older_runner, tmp_path,
            environment={"PATH": str(older_binary.parent)}, exact_version="1.26.9",
        )


def test_default_control_rejects_incompatible_path_without_searching_other_locations(
    tmp_path: Path,
):
    binary = distribution(tmp_path / "path-control", "1.26.9")
    runner = distribution_runner(binary, tmp_path)
    resolver = getattr(review_module, "_resolve_control_toolchain", None)
    assert callable(resolver), "default control must fail closed when PATH Go is too old"

    with pytest.raises(review_module.ControlToolchainError, match="below module minimum"):
        resolver(
            (1, 27, 0), runner, tmp_path,
            environment={
                "PATH": str(binary.parent),
                "GOROOT": str(tmp_path / "other-valid-install"),
            },
        )

    assert runner.calls == []


def test_default_control_missing_from_path_does_not_search_other_locations(
    tmp_path: Path,
):
    resolver = getattr(review_module, "_resolve_path_control_toolchain", None)
    assert callable(resolver)
    runner = FakeRunner({})

    with pytest.raises(review_module.ControlToolchainError, match="no Go executable"):
        resolver(
            (1, 27, 0), runner, tmp_path,
            environment={
                "PATH": str(tmp_path / "empty-path"),
                "GOROOT": str(tmp_path / "other-install"),
            },
        )

    assert runner.calls == []


def test_default_control_rejects_unverified_path_executable(tmp_path: Path):
    binary = distribution(tmp_path / "control", "1.27.3")
    runner = distribution_runner(binary, tmp_path)
    version_probe = (str(binary), "version")
    runner.scripted_results[version_probe] = command_result(
        version_probe, tmp_path, stdout="go version go1.27.4 windows/amd64\n",
    )
    resolver = getattr(review_module, "_resolve_path_control_toolchain", None)
    assert callable(resolver)

    with pytest.raises(GoToolchainSelectionError, match="version probe did not match"):
        resolver(
            (1, 27, 0), runner, tmp_path,
            environment={"PATH": str(binary.parent)},
        )

    assert [command for command, _, _ in runner.calls] == [version_probe]


@pytest.mark.parametrize("failed_gate", [None, "fmt", "build", "vet", "test"])
def test_control_runs_only_bounded_gates_once(
    tmp_path: Path, monkeypatch, failed_gate,
):
    calls = []

    class ScriptedGate:
        def __init__(self, name):
            self.name = name
            self.required = True

        def evaluate(self, runner, directory):
            calls.append(self.name)
            status = GateStatus.FAILED if self.name == failed_gate else GateStatus.PASSED
            return GateResult(
                self.name, status, f"{self.name} result", "", True, 0.1,
                CommandOutcome.COMPLETED, 1 if status is GateStatus.FAILED else 0,
            )

    gates = [ScriptedGate(name) for name in ("build", "vet", "fmt", "test", "race")]
    monkeypatch.setattr(review_module, "default_gates", lambda enable_race: gates)
    control_runner = getattr(review_module, "_run_control_gates", None)
    assert callable(control_runner), "control must run only the approved bounded gate set"

    results = control_runner(tmp_path, FakeRunner({}), gates[2])

    assert calls == ["fmt", "build", "vet", "test"]
    assert [result.name for result in results] == calls
    assert all(result.status is GateStatus.PASSED for result in results) is (failed_gate is None)


def test_review_snapshot_identity_covers_only_selected_go_files(
    tmp_path: Path, monkeypatch,
):
    fingerprint = getattr(review_module, "_fingerprint_review_snapshot", None)
    assert callable(fingerprint), "continuation requires changed-review-file identity"
    selected_file = tmp_path / "src" / "changed.go"
    selected_file.parent.mkdir()
    selected_file.write_bytes(b"package changed\n")
    unrelated_file = tmp_path / "large-data.bin"
    unrelated_file.write_bytes(b"before")
    snapshot = ChangedFilesFormatGate(
        (FormattingFile("src/changed.go", b"package changed\n"),), "fixture",
    )

    before_unrelated_change = fingerprint(tmp_path, snapshot)
    unrelated_file.write_bytes(b"after")
    original_open = Path.open
    opened_paths = []

    def track_open(path, *arguments, **keywords):
        opened_paths.append(path)
        return original_open(path, *arguments, **keywords)

    monkeypatch.setattr(Path, "open", track_open)
    after_unrelated_change = fingerprint(tmp_path, snapshot)

    assert after_unrelated_change == before_unrelated_change
    assert opened_paths == [selected_file]
    monkeypatch.undo()
    selected_file.write_bytes(b"package changed\nvar edited = true\n")
    assert fingerprint(tmp_path, snapshot) != before_unrelated_change


def test_review_snapshot_identity_rejects_selected_symlinks(
    tmp_path: Path, monkeypatch,
):
    fingerprint = review_module._fingerprint_review_snapshot
    root = tmp_path / "module"
    root.mkdir()
    selected_file = root / "link.go"
    snapshot = ChangedFilesFormatGate(
        (FormattingFile("link.go", b"package link\n"),), "fixture",
    )
    original_lstat = Path.lstat

    def report_symlink(path, *arguments, **keywords):
        if path == selected_file:
            return SimpleNamespace(st_mode=stat.S_IFLNK)
        return original_lstat(path, *arguments, **keywords)

    monkeypatch.setattr(Path, "lstat", report_symlink)

    with pytest.raises(review_module.SourceFingerprintError, match="symlink"):
        fingerprint(root, snapshot)


def test_review_snapshot_identity_rejects_path_replaced_before_open(
    tmp_path: Path, monkeypatch,
):
    root = tmp_path / "module"
    root.mkdir()
    selected_file = root / "changed.go"
    selected_file.write_bytes(b"package selected\n")
    redirected_file = tmp_path / "outside.go"
    redirected_file.write_bytes(b"package outside\n")
    snapshot = ChangedFilesFormatGate(
        (FormattingFile("changed.go", b"package selected\n"),), "fixture",
    )
    original_open = Path.open

    def redirect_selected_open(path, *arguments, **keywords):
        if path == selected_file:
            return original_open(redirected_file, *arguments, **keywords)
        return original_open(path, *arguments, **keywords)

    monkeypatch.setattr(Path, "open", redirect_selected_open)

    with pytest.raises(review_module.SourceFingerprintError, match="between validation and opening"):
        review_module._fingerprint_review_snapshot(root, snapshot)


def test_review_snapshot_identity_rejects_missing_selected_files(tmp_path: Path):
    snapshot = ChangedFilesFormatGate(
        (FormattingFile("missing.go", b"package missing\n"),), "fixture",
    )

    with pytest.raises(review_module.SourceFingerprintError, match="inspecting"):
        review_module._fingerprint_review_snapshot(tmp_path, snapshot)


def test_review_snapshot_identity_rejects_unreadable_selected_files(
    tmp_path: Path, monkeypatch,
):
    root = tmp_path / "module"
    root.mkdir()
    selected_file = root / "private.go"
    selected_file.write_text("package private\n", encoding="utf-8")
    snapshot = ChangedFilesFormatGate(
        (FormattingFile("private.go", b"package private\n"),), "fixture",
    )
    original_open = Path.open

    def deny_file_read(path, *arguments, **keywords):
        if path == selected_file:
            raise PermissionError("fixture read denied")
        return original_open(path, *arguments, **keywords)

    monkeypatch.setattr(Path, "open", deny_file_read)
    with pytest.raises(review_module.SourceFingerprintError, match="reading changed Go file"):
        review_module._fingerprint_review_snapshot(root, snapshot)


def test_review_snapshot_identity_rejects_non_regular_selected_paths(
    tmp_path: Path,
):
    root = tmp_path / "module"
    root.mkdir()
    (root / "directory.go").mkdir()
    snapshot = ChangedFilesFormatGate(
        (FormattingFile("directory.go", b"package directory\n"),), "fixture",
    )

    with pytest.raises(review_module.SourceFingerprintError, match="non-regular"):
        review_module._fingerprint_review_snapshot(root, snapshot)


def eligible_control_review_fixture(tmp_path: Path, monkeypatch):
    selected_binary, runner, request, model_calls = pinned_review_fixture(tmp_path, monkeypatch)
    control_binary = distribution(tmp_path / "control", "1.27.3")
    control_runner = distribution_runner(control_binary, tmp_path)
    control_version_probe, control_environment_probe = tuple(control_runner.scripted_results)
    control_runner.scripted_results[control_version_probe] = command_result(
        control_version_probe, tmp_path, stdout="go version go1.27.3 windows/amd64\n",
    )
    control_runner.scripted_results[control_environment_probe] = command_result(
        control_environment_probe, tmp_path, stdout=json.dumps({
            "GOVERSION": "go1.27.3",
            "GOROOT": str(control_binary.parent.parent),
            "GOTOOLCHAIN": "local",
            "GOENV": "off",
        }),
    )
    runner.scripted_results.update(control_runner.scripted_results)
    control_formatter = control_binary.with_name(
        "gofmt.exe" if control_binary.name.endswith(".exe") else "gofmt",
    )
    runner.scripted_results[(str(control_formatter),)] = command_result(
        (str(control_formatter),), tmp_path, stdout="package main\n",
    )
    for arguments in (
        ("build", "./..."), ("vet", "./..."), ("test", "./..."),
    ):
        command = (str(control_binary), *arguments)
        runner.scripted_results[command] = command_result(
            command, tmp_path, stdout="ok example.com/fixture 0.1s\n",
        )
    selected_build = (str(selected_binary), "build", "./...")
    runner.scripted_results[selected_build] = command_result(
        selected_build, tmp_path, exit_code=1, stderr="go.mod requires go >= 1.27.0",
    )
    (tmp_path / "go.mod").write_text(
        "module example.com/fixture\ngo 1.27.0\n", encoding="utf-8",
    )
    monkeypatch.setenv("PATH", str(control_binary.parent))
    return selected_binary, control_binary, runner, request, model_calls


def test_control_format_gate_uses_selected_changed_file_scope(
    tmp_path: Path, monkeypatch,
):
    selected_binary, control_binary, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    (tmp_path / "unrelated.go").write_text(
        "package main\nvar unrelated=1\n", encoding="utf-8",
    )
    control_formatter = control_binary.with_name(
        "gofmt.exe" if control_binary.name.endswith(".exe") else "gofmt",
    )
    whole_module_command = (str(control_formatter), "-l", ".")
    runner.scripted_results[whole_module_command] = command_result(
        whole_module_command, tmp_path, stdout="unrelated.go\n",
    )
    changed_snapshot_command = (str(control_formatter),)
    runner.scripted_results[changed_snapshot_command] = command_result(
        changed_snapshot_command, tmp_path, stdout="package main\n",
    )

    try:
        outcome = run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
        )
    except ToolchainGateFailed as error:
        pytest.fail(f"unrelated unformatted Go file blocked continuation: {error}")

    control_format = outcome.toolchain.control_gate_results[0]
    assert control_format.status is GateStatus.PASSED, control_format.summary
    formatter_calls = [
        (command, runner.stdin_texts[index])
        for index, (command, _, _) in enumerate(runner.calls)
        if command[0] == str(control_formatter)
    ]
    assert (changed_snapshot_command, "package main\n") in formatter_calls
    assert whole_module_command not in [command for command, _ in formatter_calls]


def test_eligible_control_success_preserves_selected_and_control_evidence(
    tmp_path: Path, monkeypatch,
):
    selected_binary, control_binary, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )

    try:
        outcome = run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
        )
    except ToolchainGateFailed as error:
        pytest.fail(f"eligible control run was blocked before review: {error}")

    assert getattr(outcome.toolchain, "degraded", False) is True
    assert [result.name for result in outcome.toolchain.gate_results[:5]] == [
        "fmt", "build", "vet", "test", "race",
    ]
    assert outcome.toolchain.gate_results[1].status is GateStatus.FAILED
    assert all(
        result.status is GateStatus.SKIPPED
        for result in outcome.toolchain.gate_results[2:5]
    )
    assert [result.name for result in outcome.toolchain.control_gate_results] == [
        "fmt", "build", "vet", "test",
    ]
    assert all(
        result.status is GateStatus.PASSED
        for result in outcome.toolchain.control_gate_results
    )
    assert outcome.toolchain.control_selection.executable == control_binary
    assert model_calls
    prompt = model_calls[0]["prompt"]
    assert "Selected compiler did not pass" in prompt
    assert "control checks do not validate the requested compiler" in prompt
    assert "Race detection and advisory analyzers were not established by control" in prompt

    markdown = render_review_markdown(outcome)
    payload = json.loads(render_review_json(outcome))
    assert "DEGRADED REVIEW" in markdown
    assert payload["schema_version"] == 3
    assert payload["toolchain"].get("degraded") is True
    assert payload["toolchain"].get("control_gates") is not None
    assert payload["toolchain"]["control_gates"][0]["command_outcome"] == "completed"
    assert payload["toolchain"]["control_gates"][0]["command_exit_code"] == 0
    assert payload["toolchain"]["gates"][1]["status"] == "failed"
    assert payload["toolchain"]["gates"][1]["command_outcome"] == "completed"
    assert payload["toolchain"]["gates"][1]["command_exit_code"] == 1


@pytest.mark.parametrize(("outcome", "exit_code"), [
    (CommandOutcome.COMPLETED, 1),
    (CommandOutcome.TIMED_OUT, None),
    (CommandOutcome.TOOL_MISSING, None),
    (CommandOutcome.RUNNER_ERROR, None),
])
def test_control_gate_failure_blocks_models(
    tmp_path: Path, monkeypatch, outcome: CommandOutcome, exit_code: int | None,
):
    selected_binary, control_binary, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    failed_build = (str(control_binary), "build", "./...")
    runner.scripted_results[failed_build] = command_result(
        failed_build, tmp_path, outcome=outcome, exit_code=exit_code,
        stderr="control failed",
    )

    with pytest.raises(ToolchainGateFailed) as raised:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
        )

    assert any(failure.name == "control build" for failure in raised.value.failures)
    assert model_calls == []


def test_skipped_control_gate_blocks_models(
    tmp_path: Path, monkeypatch,
):
    selected_binary, control_binary, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    passing_results = tuple(
        GateResult(
            name, GateStatus.PASSED, f"{name} passed", "", True, 0.1,
            CommandOutcome.COMPLETED, 0,
        )
        for name in ("fmt", "build", "vet", "test")
    )
    skipped_format = GateResult(
        "fmt", GateStatus.SKIPPED, "format skipped", "", True, 0.0,
    )
    monkeypatch.setattr(
        review_module, "_run_control_gates",
        lambda directory, control_runner, format_gate: (
            skipped_format, *passing_results[1:],
        ),
    )

    with pytest.raises(ToolchainGateFailed) as raised:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
        )

    assert any(failure.name == "control fmt" for failure in raised.value.failures)
    assert model_calls == []


def test_source_change_after_selected_checks_blocks_before_models(
    tmp_path: Path, monkeypatch,
):
    selected_binary, control_binary, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    source_file = tmp_path / "main.go"
    source_file.write_bytes(b"package main\n")
    control_test = (str(control_binary), "test", "./...")
    result = runner.scripted_results[control_test]

    def mutate_source(_stdin):
        source_file.write_text("package changed\n", encoding="utf-8")
        return result

    runner.scripted_results[control_test] = mutate_source

    with pytest.raises(review_module.SourceFingerprintError, match="inputs changed"):
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
        )

    assert model_calls == []


@pytest.mark.parametrize(("source", "should_block"), [
    (DiffSource.WORKING, True),
    (DiffSource.STAGED, False),
])
def test_initial_fingerprint_matches_captured_bytes_only_for_working_source(
    tmp_path: Path, monkeypatch, source, should_block,
):
    selected_binary, _, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    request = replace(request, source=source)
    capture_snapshot = review_module.capture_review_diff

    def capture_then_change_live_file(*arguments):
        diff, format_gate = capture_snapshot(*arguments)
        (tmp_path / "main.go").write_text("package changed\n", encoding="utf-8")
        return replace(diff, request=request), format_gate

    monkeypatch.setattr(
        review_module, "capture_review_diff", capture_then_change_live_file,
    )

    if should_block:
        with pytest.raises(
            review_module.SourceFingerprintError,
            match="does not match the captured working-tree snapshot",
        ):
            run_review(
                request, ("fixture",), runner, tmp_path, 1, 1,
                go_toolchain_request=GoToolchainRequest(
                    "1.26.9", "cli", executable=selected_binary,
                ),
            )
        assert model_calls == []
        assert not any(
            command[1:3] == ("build", "./...")
            for command, _, _ in runner.calls
        )
        return

    outcome = run_review(
        request, ("fixture",), runner, tmp_path, 1, 1,
        go_toolchain_request=GoToolchainRequest(
            "1.26.9", "cli", executable=selected_binary,
        ),
    )

    assert outcome.toolchain.degraded is True
    assert model_calls


def test_missing_review_snapshot_scope_blocks_before_selected_checks(
    tmp_path: Path, monkeypatch,
):
    selected_binary, _, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    capture_diff = review_module.capture_review_diff
    diff, _ = capture_diff(request, runner, tmp_path)
    monkeypatch.setattr(
        review_module, "capture_review_diff", lambda *arguments: (diff, None),
    )

    error = None
    try:
        run_review(
            request, ("fixture",), runner, tmp_path, 1, 1,
            go_toolchain_request=GoToolchainRequest(
                "1.26.9", "cli", executable=selected_binary,
            ),
        )
    except Exception as caught:
        error = caught

    assert isinstance(error, review_module.SourceFingerprintError), (
        f"error = {error!r}, want SourceFingerprintError"
    )
    assert "formatting scope is unavailable" in str(error)
    assert not any(command[1:3] == ("build", "./...") for command, _, _ in runner.calls)
    assert model_calls == []


def test_unrelated_source_change_does_not_block_control_review(
    tmp_path: Path, monkeypatch,
):
    selected_binary, control_binary, runner, request, model_calls = (
        eligible_control_review_fixture(tmp_path, monkeypatch)
    )
    (tmp_path / "main.go").write_bytes(b"package main\n")
    unrelated_file = tmp_path / "metadata.json"
    unrelated_file.write_text('{"state":"before"}', encoding="utf-8")
    control_test = (str(control_binary), "test", "./...")
    result = runner.scripted_results[control_test]

    def mutate_unrelated_file(_stdin):
        unrelated_file.write_text('{"state":"after"}', encoding="utf-8")
        return result

    runner.scripted_results[control_test] = mutate_unrelated_file
    outcome = run_review(
        request, ("fixture",), runner, tmp_path, 1, 1,
        go_toolchain_request=GoToolchainRequest(
            "1.26.9", "cli", executable=selected_binary,
        ),
    )

    assert outcome.toolchain.degraded is True
    assert model_calls
