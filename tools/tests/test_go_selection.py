"""Exact Go policy and local distribution selection without real model calls."""

from __future__ import annotations

import json
import hashlib
import os
import platform
import shutil
import re
from pathlib import Path

import pytest

from atom.go_selection import (
    GoToolchainConfigError, GoToolchainRequest, GoToolchainSelectionError,
    _SelectedGoRunner, capture_go_toolchain_request, resolve_go_toolchain,
)
from tests.conftest import FakeRunner, command_result
from atom.runner import CommandOutcome, SubprocessRunner


def write_policy(root: Path, version: object = "1.26.9") -> Path:
    directory = root / ".atom"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "config.json"
    path.write_text(
        json.dumps({"module_path": "example.com/service", "review_go_version": version}),
        encoding="utf-8",
    )
    return path


def test_capture_project_version(tmp_path):
    policy = write_policy(tmp_path)
    original = policy.read_bytes()

    request = capture_go_toolchain_request(tmp_path)

    assert request is not None, "configured exact version was not captured"
    assert (request.version, request.source, request.project_version) == (
        "1.26.9", "project", "1.26.9",
    )
    assert policy.read_bytes() == original


@pytest.mark.parametrize("version", [
    None, "", 1269, True, [], {}, "go1.26.9", "1.26", "1.026.9",
    "1.26.09", "1.20.9", "1.26.9+auto", "1.26.9 ", "1.27rc1",
])
def test_invalid_project_version(tmp_path, version):
    write_policy(tmp_path, version)

    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
        capture_go_toolchain_request(tmp_path)


@pytest.mark.parametrize("configured", [True, False])
def test_cli_override_records_project_version(tmp_path, configured):
    if configured:
        write_policy(tmp_path)
    request = capture_go_toolchain_request(tmp_path, version_override="1.27.0")
    assert request is not None, "explicit version was ignored"
    assert (request.version, request.source, request.project_version) == (
        "1.27.0", "cli", "1.26.9" if configured else None,
    )


@pytest.mark.parametrize("version", ["", "auto", "go1.26.9"])
def test_invalid_cli_override_is_not_ambient_fallback(tmp_path, version):
    with pytest.raises(ValueError, match="exact stable Go"):
        capture_go_toolchain_request(tmp_path, version_override=version)


@pytest.mark.parametrize("content", ["{", "[]", "{}"])
def test_config_read_errors(tmp_path, content):
    policy = write_policy(tmp_path)
    policy.write_text(content, encoding="utf-8")
    try:
        capture_go_toolchain_request(tmp_path, version_override="1.27.0")
    except Exception as error:
        assert isinstance(error, GoToolchainConfigError), (
            f"config error escaped the policy boundary: {type(error).__name__}"
        )
        assert str(policy) in str(error)
    else:
        pytest.fail("invalid existing config silently became a no-pin policy")


def test_unreadable_config_does_not_become_unconfigured(tmp_path, monkeypatch):
    policy = write_policy(tmp_path)

    def unreadable(project):
        raise PermissionError("fixture policy permission denied")

    monkeypatch.setattr("atom.go_selection.Project.load_config", unreadable)
    with pytest.raises(GoToolchainConfigError, match="permission denied") as raised:
        capture_go_toolchain_request(tmp_path, version_override="1.27.0")
    assert str(policy) in str(raised.value)


def test_request_freezes_relative_path_and_policy(tmp_path):
    write_policy(tmp_path)
    request = capture_go_toolchain_request(
        tmp_path, executable_override=Path("sdk") / "bin" / "go.exe",
    )
    write_policy(tmp_path, "1.27.0")
    assert request.executable == (tmp_path / "sdk" / "bin" / "go.exe").resolve()
    assert request.version == "1.26.9"


def test_executable_requires_version(tmp_path):
    with pytest.raises(ValueError, match="requires"):
        capture_go_toolchain_request(tmp_path, executable_override=Path("go.exe"))


@pytest.mark.parametrize("overrides", [
    {"version": "auto"}, {"source": "ambient"}, {"project_version": "1.26"},
    {"executable": Path("relative") / "bin" / "go"},
])
def test_invalid_library_request_is_rejected(overrides):
    arguments = {"version": "1.26.9", "source": "cli", **overrides}
    try:
        GoToolchainRequest(**arguments)
    except ValueError:
        pass
    else:
        pytest.fail("invalid library request was accepted")


def test_no_implicit_or_ancestor_policy(tmp_path):
    write_policy(tmp_path)
    child = tmp_path / "child"
    child.mkdir()
    (child / "go.mod").write_text(
        "module example.com/child\ngo 1.26.0\ntoolchain go1.26.9\n", encoding="utf-8",
    )
    assert capture_go_toolchain_request(child) is None


def distribution(root: Path, version: str = "1.26.9") -> Path:
    binary = root / "bin" / ("go.exe" if os.name == "nt" else "go")
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"fixture go executable")
    binary.chmod(0o755)
    formatter = binary.with_name("gofmt.exe" if os.name == "nt" else "gofmt")
    formatter.write_bytes(b"fixture formatter")
    formatter.chmod(0o755)
    (root / "VERSION").write_text(f"go{version}\n", encoding="utf-8")
    return binary.resolve()


def distribution_runner(binary: Path, directory: Path) -> FakeRunner:
    version = (str(binary), "version")
    environment = (
        str(binary), "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV",
    )
    return FakeRunner({
        version: command_result(version, directory, stdout="go version go1.26.9 windows/amd64\n"),
        environment: command_result(environment, directory, stdout=json.dumps({
            "GOVERSION": "go1.26.9", "GOROOT": str(binary.parent.parent),
            "GOTOOLCHAIN": "local", "GOENV": "off",
        })),
    })


def test_resolve_verifies_actual_distribution(tmp_path):
    binary = distribution(tmp_path / "installed")
    runner = distribution_runner(binary, tmp_path)
    request = GoToolchainRequest("1.26.9", "cli", executable=binary)

    selected = resolve_go_toolchain(request, runner, tmp_path, environment={})

    assert selected.status == "verified", "actual distribution was not verified"
    assert selected.observed_version == "1.26.9"
    assert selected.executable == binary
    assert selected.goroot == binary.parent.parent
    assert selected.executable_sha256 == hashlib.sha256(binary.read_bytes()).hexdigest()
    assert selected.selection_source == "explicit"
    assert len(selected.probes) == 2
    assert all(call[2] == 60 for call in runner.calls)


@pytest.mark.parametrize("kind", [
    "wrong_version", "version_nonzero", "version_timed_out", "version_missing",
    "version_runner_error", "env_nonzero", "env_invalid_json", "env_list",
    "env_null", "env_missing", "env_wrong_version", "env_wrong_root",
    "env_wrong_mode", "env_wrong_type",
])
def test_probe_failure_cannot_verify(tmp_path, kind):
    binary = distribution(tmp_path / "installed")
    runner = distribution_runner(binary, tmp_path)
    version_key, env_key = tuple(runner.scripted_results)
    if kind.startswith("version_"):
        outcome = {
            "version_timed_out": CommandOutcome.TIMED_OUT,
            "version_missing": CommandOutcome.TOOL_MISSING,
            "version_runner_error": CommandOutcome.RUNNER_ERROR,
        }.get(kind, CommandOutcome.COMPLETED)
        runner.scripted_results[version_key] = command_result(
            version_key, tmp_path, outcome, 1, stderr="probe execution diagnostic",
        )
    elif kind == "wrong_version":
        runner.scripted_results[version_key] = command_result(
            version_key, tmp_path, stdout="go version go1.27.0 windows/amd64\n",
        )
    else:
        values = json.loads(runner.scripted_results[env_key].stdout)
        values.update({
            "GOVERSION": "go1.27.0" if kind == "env_wrong_version" else "go1.26.9",
            "GOROOT": str(tmp_path / "another") if kind == "env_wrong_root" else str(binary.parent.parent),
            "GOTOOLCHAIN": "auto" if kind == "env_wrong_mode" else "local",
        })
        if kind == "env_wrong_type":
            values["GOROOT"] = []
        stdout = {
            "env_invalid_json": "{", "env_list": "[]", "env_null": "null", "env_missing": "{}",
        }.get(kind, json.dumps(values))
        runner.scripted_results[env_key] = command_result(
            env_key, tmp_path, exit_code=1 if kind == "env_nonzero" else 0,
            stdout=stdout, stderr="probe environment diagnostic",
        )
    try:
        resolve_go_toolchain(
            GoToolchainRequest("1.26.9", "cli", executable=binary),
            runner, tmp_path, environment={},
        )
    except Exception as error:
        assert isinstance(error, GoToolchainSelectionError), (
            f"invalid probe escaped the selection boundary: {type(error).__name__}"
        )
        assert "1.26.9" in str(error)
    else:
        pytest.fail("invalid actual probe was accepted as exact selection")
    assert len(runner.calls) == (1 if kind == "wrong_version" or kind.startswith("version_") else 2)


def test_different_observed_root_is_rejected_even_when_binary_identity_matches(tmp_path, monkeypatch):
    binary = distribution(tmp_path / "installed")
    other_root = tmp_path / "other-root"
    other_root.mkdir()
    alias = other_root / "bin" / binary.name
    original_resolve = Path.resolve

    def resolve_alias(path, strict=False):
        if path == alias:
            return binary
        return original_resolve(path, strict=strict)

    monkeypatch.setattr(Path, "resolve", resolve_alias)
    runner = distribution_runner(binary, tmp_path)
    command = tuple(runner.scripted_results)[1]
    values = json.loads(runner.scripted_results[command].stdout)
    values["GOROOT"] = str(other_root)
    runner.scripted_results[command] = command_result(command, tmp_path, stdout=json.dumps(values))

    with pytest.raises(GoToolchainSelectionError, match="observed version/root/mode/hash") as raised:
        resolve_go_toolchain(
            GoToolchainRequest("1.26.9", "cli", executable=binary),
            runner, tmp_path, environment={},
        )
    assert raised.value.reason == "verification_failed"
    assert len(runner.calls) == 2


@pytest.mark.parametrize("kind", [
    "missing_binary", "missing_version", "wrong_metadata", "wrapper", "missing_formatter",
])
def test_explicit_candidate_never_falls_back(tmp_path, kind):
    binary = distribution(tmp_path / "installed")
    runner = distribution_runner(binary, tmp_path)
    if kind == "missing_binary":
        binary.unlink()
    elif kind == "missing_version":
        (binary.parent.parent / "VERSION").unlink()
    elif kind == "wrong_metadata":
        (binary.parent.parent / "VERSION").write_text("go1.27.0\n", encoding="utf-8")
    elif kind == "missing_formatter":
        binary.with_name("gofmt.exe" if os.name == "nt" else "gofmt").unlink()
    else:
        wrapper = binary.with_suffix(".cmd")
        binary.rename(wrapper)
        binary = wrapper
        runner = distribution_runner(binary, tmp_path)
    try:
        resolve_go_toolchain(
            GoToolchainRequest("1.26.9", "cli", executable=binary),
            runner, tmp_path, environment={"PATH": str(tmp_path / "another")},
        )
    except Exception as error:
        assert isinstance(error, GoToolchainSelectionError), (
            f"candidate failure escaped the selection boundary: {type(error).__name__}"
        )
        assert error.reason == "verification_failed"
        assert "--go-executable" in str(error), "explicit-path remedy was omitted"
    else:
        pytest.fail("incomplete or wrong explicit distribution was accepted")
    if kind != "missing_formatter":
        assert runner.calls == []


@pytest.mark.parametrize("source", ["path", "goroot", "sdk", "module_cache", "gopath", "default_cache"])
def test_bounded_discovery_order(tmp_path, monkeypatch, source):
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(platform, "machine", lambda: "AMD64")
    cache_leaf = Path("golang.org") / "toolchain@v0.0.1-go1.26.9.windows-amd64"
    locations = {
        "path": tmp_path / "path-go",
        "goroot": tmp_path / "root-go",
        "sdk": home / "sdk" / "go1.26.9",
        "module_cache": tmp_path / "mod-cache" / cache_leaf,
        "gopath": tmp_path / "gopath" / "pkg" / "mod" / cache_leaf,
        "default_cache": home / "go" / "pkg" / "mod" / cache_leaf,
    }
    binary = distribution(locations[source])
    ambient = {
        "PATH": "", "GOROOT": str(locations["goroot"]),
        "GOMODCACHE": str(tmp_path / "mod-cache"),
    }
    if source != "default_cache":
        ambient["GOPATH"] = str(tmp_path / "gopath")
    monkeypatch.setattr(shutil, "which", lambda *args, **kwargs: str(binary) if source == "path" else None)
    runner = distribution_runner(binary, tmp_path)
    selected = resolve_go_toolchain(
        GoToolchainRequest("1.26.9", "project"), runner, tmp_path, environment=ambient,
    )
    assert selected.status == "verified", "bounded installed distribution was not found"
    assert selected.executable == binary
    expected_source = "module_cache" if source in ("gopath", "default_cache") else source
    assert selected.selection_source == expected_source
    assert len(runner.calls) == 2


def test_discovery_unavailable_does_not_use_ambient(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(shutil, "which", lambda *args, **kwargs: None)
    runner = FakeRunner()
    with pytest.raises(GoToolchainSelectionError, match="--go-executable") as raised:
        resolve_go_toolchain(
            GoToolchainRequest("1.26.9", "cli"), runner, tmp_path, environment={},
        )
    assert raised.value.reason == "unavailable"
    assert raised.value.diagnostics
    assert runner.calls == []


def test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics(tmp_path, monkeypatch):
    first = distribution(tmp_path / "first")
    later = distribution(tmp_path / "later")
    monkeypatch.setattr("atom.go_selection._local_candidates", lambda *args: [
        ("path", tmp_path / "missing"),
        ("sdk", first),
        ("module_cache", later),
    ])
    runner = distribution_runner(first, tmp_path)
    command = (str(first), "version")
    runner.scripted_results[command] = command_result(
        command, tmp_path, stdout="go version go1.27.0 windows/amd64\n",
    )
    with pytest.raises(GoToolchainSelectionError) as raised:
        resolve_go_toolchain(
            GoToolchainRequest("1.26.9", "cli"), runner, tmp_path, environment={},
        )
    assert len(runner.calls) == 1
    assert raised.value.probes[0].command == command
    assert raised.value.diagnostics, "real probe failure discarded earlier candidate diagnostics"
    assert str(tmp_path / "missing") in str(raised.value)


def test_unsupported_host_mapping_requires_an_inspectable_installed_path(tmp_path, monkeypatch):
    binary = distribution(tmp_path / "custom-layout")
    monkeypatch.setattr(platform, "system", lambda: "UnsupportedHost")
    monkeypatch.setattr(platform, "machine", lambda: "unsupported-arch")
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "empty-home")
    monkeypatch.setattr(shutil, "which", lambda *args, **kwargs: None)
    runner = distribution_runner(binary, tmp_path)
    with pytest.raises(GoToolchainSelectionError, match="--go-executable"):
        resolve_go_toolchain(
            GoToolchainRequest("1.26.9", "cli"), runner, tmp_path, environment={},
        )
    assert runner.calls == []
    selected = resolve_go_toolchain(
        GoToolchainRequest("1.26.9", "cli", executable=binary),
        runner, tmp_path, environment={},
    )
    assert selected.selection_source == "explicit"


def test_selected_environment_preserves_project_settings(tmp_path):
    binary = distribution(tmp_path / "installed")
    runner = distribution_runner(binary, tmp_path)
    path_key, root_key = ("Path", "gOrOoT") if os.name == "nt" else ("PATH", "GOROOT")
    environment = {
        path_key: "ambient-bin", root_key: "unrelated-root", "GOTOOLCHAIN": "go1.27.0+auto",
        "GOFLAGS": "-tags=custom", "GOWORK": "custom.work", "CGO_ENABLED": "1",
        "GOPROXY": "custom-proxy", "GOSUMDB": "custom-checksum", "GODEBUG": "gctrace=1",
    }
    original = dict(environment)
    resolve_go_toolchain(
        GoToolchainRequest("1.26.9", "cli", executable=binary),
        runner, tmp_path, environment=environment,
    )
    child = runner.environments[0]
    assert environment == original
    assert child["GOTOOLCHAIN"] == "local"
    assert not any(key.casefold() == "goroot" for key in child)
    assert len([key for key in child if key.casefold() == "path"]) == 1
    assert child["PATH"] == str(binary.parent) + os.pathsep + "ambient-bin"
    for key in ("GOFLAGS", "GOWORK", "CGO_ENABLED", "GOPROXY", "GOSUMDB", "GODEBUG"):
        assert child[key] == original[key]


def test_native_installed_distribution_runtime_formatter_and_minimum(tmp_path):
    """Exercise production selection/ownership without generic launcher bootstrap."""
    location = shutil.which("go")
    if location is None:
        if os.environ.get("CI"):
            pytest.fail("native CI must provision Go for selected-distribution integration")
        pytest.skip("native Go distribution is unavailable locally")
    binary = Path(location).resolve()
    metadata = binary.parent.parent / "VERSION"
    if not metadata.is_file():
        if os.environ.get("CI"):
            pytest.fail("native CI Go must be a direct distribution with VERSION metadata")
        pytest.skip("PATH Go is not an inspectable installed distribution")
    version = metadata.read_text(encoding="utf-8").splitlines()[0].removeprefix("go")
    assert re.fullmatch(r"1\.[0-9]+\.[0-9]+", version), "native fixture needs stable Go"
    parent = dict(os.environ)
    module = tmp_path / "module-\u03bb"
    module.mkdir()
    policy = tmp_path / "fixture-goenv"
    policy.write_text("GOFLAGS=-tags=atom_selection_fixture\nGOTOOLCHAIN=auto\n", encoding="utf-8")
    original_policy = policy.read_bytes()
    environment = {
        key: value for key, value in parent.items()
        if key.upper() not in {"GOFLAGS", "GOOS", "GOARCH", "GOROOT", "GOTOOLCHAIN"}
    }
    environment.update({
        "GOENV": str(policy), "GOWORK": "off", "GOTOOLCHAIN": "auto",
        "GOROOT": str(tmp_path / "incorrect-process-root"), "CGO_ENABLED": "0",
        "GOPROXY": "off", "GOSUMDB": "off",
    })
    original_environment = dict(environment)
    (module / "go.mod").write_text(
        f"module example.com/selectionfixture\ngo 1.{version.split('.')[1]}.0\n", encoding="utf-8",
    )
    (module / "fixture.go").write_text("package selectionfixture\n", encoding="utf-8")
    (module / "fixture_test.go").write_text(
        '//go:build atom_selection_fixture\n\npackage selectionfixture\n'
        'import ("runtime"; "testing")\n'
        'func TestSelectedRuntime(t *testing.T) {\n'
        f' if runtime.Version() != "go{version}" {{ t.Fatal(runtime.Version()) }}\n'
        ' t.Log("selected-runtime=" + runtime.Version())\n}\n',
        encoding="utf-8",
    )
    runner = SubprocessRunner()
    selected = resolve_go_toolchain(
        GoToolchainRequest(version, "cli", executable=binary),
        runner, module, environment=environment,
    )
    automatic = resolve_go_toolchain(
        GoToolchainRequest(version, "cli"), runner, module, environment=environment,
    )
    assert automatic.executable == selected.executable
    assert automatic.selection_source == "path"
    assert automatic.observed_version == version
    print(json.dumps({
        "native_platform": platform.system(), "requested_version": version,
        "observed_version": automatic.observed_version,
        "automatic_source": automatic.selection_source,
        "executable": str(automatic.executable),
        "formatter": str(automatic.gofmt_executable),
    }, sort_keys=True))
    adapter = _SelectedGoRunner(selected, runner, environment)
    for arguments in (("build", "./..."), ("vet", "./..."), ("test", "-v", "-count=1", "./...")):
        result = adapter.run(("go", *arguments), module, 120)
        assert result.succeeded, result.combined_output
        if arguments[0] == "test":
            assert f"selected-runtime=go{version}" in result.stdout
    formatted = adapter.run(("gofmt",), module, stdin_text="package selectionfixture\nvar answer=42\n")
    assert formatted.succeeded, formatted.combined_output
    assert formatted.stdout == "package selectionfixture\n\nvar answer = 42\n"
    final = adapter.finish()
    assert final.observed_version == version
    assert final.executable_sha256_after == final.executable_sha256
    assert final.gofmt_sha256_after == final.gofmt_sha256
    higher = f"1.{int(version.split('.')[1]) + 1}.0"
    (module / "go.mod").write_text(
        f"module example.com/selectionfixture\ngo {higher}\n", encoding="utf-8",
    )
    rejected = adapter.run(("go", "build", "./..."), module, 60)
    assert not rejected.succeeded
    assert f"requires go >= {higher}" in rejected.combined_output
    assert dict(os.environ) == parent
    assert environment == original_environment
    assert policy.read_bytes() == original_policy


def test_selected_runner_keeps_optional_child_mapping_isolated(tmp_path):
    binary = distribution(tmp_path / "installed")
    runner = distribution_runner(binary, tmp_path)
    selected = resolve_go_toolchain(
        GoToolchainRequest("1.26.9", "cli", executable=binary),
        runner, tmp_path, environment={"BASE_ONLY": "base"},
    )
    adapter = _SelectedGoRunner(selected, runner, {"BASE_ONLY": "base"})
    supplied = {"CUSTOM_ONLY": "custom", "GOTOOLCHAIN": "auto", "PATH": "custom-bin"}
    original = dict(supplied)
    try:
        adapter.run(("go", "test", "./..."), tmp_path, environment=supplied)
    except TypeError:
        pytest.fail("selected runner dropped the runner protocol's child-environment argument")
    assert runner.environments[-1].get("CUSTOM_ONLY") == "custom", "child override was ignored"
    assert runner.environments[-1]["GOTOOLCHAIN"] == "local"
    assert runner.environments[-1]["PATH"] == str(binary.parent) + os.pathsep + "custom-bin"
    assert "BASE_ONLY" not in runner.environments[-1]
    adapter.run(("go", "test", "./..."), tmp_path)
    assert runner.environments[-1]["BASE_ONLY"] == "base"
    assert "CUSTOM_ONLY" not in runner.environments[-1]
    assert supplied == original
