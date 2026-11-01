"""Select installed Go distributions without changing user toolchain policy."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal, Mapping, Sequence

from atom.runner import CommandOutcome, CommandResult, CommandRunner
from atom.state import Project
from atom.storage import StateFileError


class GoToolchainConfigError(Exception):
    """Distinguish damaged project policy from an absent optional pin."""


class GoToolchainSelectionError(Exception):
    """Keep failed selection distinct from a passing or intentionally skipped gate."""

    def __init__(
        self, request: GoToolchainRequest, reason: str, detail: str,
        *, probes: tuple[CommandResult, ...] = (), diagnostics: tuple[str, ...] = (),
        selection: GoToolchainSelection | None = None,
    ) -> None:
        self.request = request
        self.reason = reason
        self.probes = probes
        self.diagnostics = diagnostics
        self.selection = selection
        lines = [f"Go {request.version} selection {reason}: {detail}", *diagnostics]
        for result in probes:
            lines.append(
                f"{' '.join(result.command)}: {result.outcome.value}, exit={result.exit_code}"
            )
            if result.combined_output:
                lines.append(result.combined_output.rstrip())
        super().__init__("\n".join(lines))


@dataclass(frozen=True)
class GoToolchainRequest:
    """Keep launch intent independent of later checkout changes."""

    version: str
    source: Literal["cli", "project"]
    project_version: str | None = None
    executable: Path | None = None

    def __post_init__(self) -> None:
        _validate_version(self.version)
        if self.source not in ("cli", "project"):
            raise ValueError("Go request source must be cli or project")
        if self.project_version is not None:
            _validate_version(self.project_version)
        if self.executable is not None and (
            not isinstance(self.executable, Path) or not self.executable.is_absolute()
        ):
            raise ValueError("Go executable must be a captured absolute Path")


@dataclass(frozen=True)
class GoToolchainSelection:
    """Keep observed execution separate from a requested version."""

    request: GoToolchainRequest
    status: Literal["verified", "not_run"] = "not_run"
    observed_version: str | None = None
    executable: Path | None = None
    goroot: Path | None = None
    executable_sha256: str | None = None
    selection_source: str | None = None
    probes: tuple[CommandResult, ...] = ()
    gofmt_executable: Path | None = None
    gofmt_sha256: str | None = None
    discovery_diagnostics: tuple[str, ...] = ()
    commands: tuple[CommandResult, ...] = ()
    executable_sha256_after: str | None = None
    gofmt_sha256_after: str | None = None
    reason: str | None = None


class _SelectedGoRunner:
    """Keep selected gate execution separate from Git and model processes."""

    def __init__(
        self, selection: GoToolchainSelection, runner: CommandRunner,
        environment: Mapping[str, str],
    ) -> None:
        if selection.executable is None or selection.gofmt_executable is None:
            raise ValueError("a verified Go distribution is required")
        self.selection = selection
        self.runner = runner
        self.binary = selection.executable
        self.formatter = selection.gofmt_executable
        self.environment = _selected_environment(environment, self.binary)
        self.commands: list[CommandResult] = []

    def run(
        self, command: Sequence[str], working_directory: Path,
        timeout_seconds: float = 300.0, stdin_text: str | None = None,
        *, environment: Mapping[str, str] | None = None,
    ) -> CommandResult:
        selected = tuple(command)
        if selected and selected[0] == "make":
            # Gates redetect commands; a late recipe must not escape preflight.
            raise GoToolchainSelectionError(
                self.selection.request, "unsupported_wrapper",
                "pinned review cannot attest delegated command: " + " ".join(selected),
                probes=self.selection.probes,
            )
        if selected and selected[0] == "go":
            selected = (str(self.binary), *selected[1:])
        elif selected and selected[0] == "gofmt":
            selected = (str(self.formatter), *selected[1:])
        result = self.runner.run(
            selected, working_directory, timeout_seconds, stdin_text,
            environment=(
                self.environment if environment is None
                else _selected_environment(dict(environment), self.binary)
            ),
        )
        self.commands.append(result)
        return result

    def finish(self) -> GoToolchainSelection:
        """Invalidate replaced or missing identities before models can run."""

        identities = [(self.binary, self.selection.executable_sha256)]
        if any(result.command[0] == str(self.formatter) for result in self.commands):
            identities.append((self.formatter, self.selection.gofmt_sha256))
        after: dict[Path, str | None] = {}
        failures: list[str] = []
        for path, before in identities:
            try:
                after[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as error:
                after[path] = None
                failures.append(f"reading final identity {path}: {error}")
            if after[path] != before:
                failures.append(f"{path}: before={before}, after={after[path]}")
        selection = replace(
            self.selection, commands=tuple(self.commands),
            executable_sha256_after=after[self.binary],
            gofmt_sha256_after=after.get(self.formatter),
        )
        if failures:
            raise GoToolchainSelectionError(
                selection.request, "verification_failed",
                "selected executable identity changed after gates",
                probes=selection.probes, diagnostics=tuple(failures), selection=selection,
            )
        return selection


def resolve_go_toolchain(
    request: GoToolchainRequest,
    runner: CommandRunner,
    working_directory: Path,
    *,
    environment: Mapping[str, str],
) -> GoToolchainSelection:
    """Verify a local distribution before pinned gates can use it."""

    candidates = (
        [("explicit", request.executable)] if request.executable is not None
        else _local_candidates(request.version, environment)
    )
    diagnostics: list[str] = []
    seen: set[Path] = set()
    for source, candidate in candidates:
        try:
            canonical = candidate.resolve()
            if canonical in seen:
                continue
            seen.add(canonical)
            binary, initial_hash, formatter, formatter_hash = _inspect_distribution(
                canonical, request.version,
            )
        except (OSError, ValueError, UnicodeError, RuntimeError) as error:
            diagnostics.append(f"{source}: {candidate}: {error}")
            if source == "explicit":
                raise GoToolchainSelectionError(
                    request, "verification_failed",
                    "reading explicit distribution; provide --go-executable pointing "
                    "to the matching installed distribution's direct bin/go executable",
                    diagnostics=tuple(diagnostics),
                ) from error
            continue
        # A real probe failure is terminal, not permission to hide a broken install.
        break
    else:
        raise GoToolchainSelectionError(
            request, "unavailable",
            "no installed distribution matched; provide --go-executable with its direct bin/go",
            diagnostics=tuple(diagnostics),
        )
    child = _selected_environment(environment, binary)
    probes: list[CommandResult] = []

    def probe(command: tuple[str, ...]) -> CommandResult:
        result = runner.run(command, working_directory, 60, environment=child)
        probes.append(result)
        if not result.succeeded:
            reason = (
                "verification_failed"
                if result.outcome is CommandOutcome.COMPLETED else "execution_failed"
            )
            raise GoToolchainSelectionError(
                request, reason, "direct Go probe did not succeed", probes=tuple(probes),
                diagnostics=tuple(diagnostics),
            )
        return result

    version = probe((str(binary), "version"))
    if not re.fullmatch(rf"go version go{re.escape(request.version)} \S+\s*", version.stdout):
        raise GoToolchainSelectionError(
            request, "verification_failed", "version probe did not match request",
            probes=tuple(probes), diagnostics=tuple(diagnostics),
        )
    actual = probe(
        (str(binary), "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV"),
    )
    try:
        values = json.loads(actual.stdout)
    except json.JSONDecodeError as error:
        raise GoToolchainSelectionError(
            request, "verification_failed", f"invalid Go environment JSON: {error}",
            probes=tuple(probes), diagnostics=tuple(diagnostics),
        ) from error
    fields = ("GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV")
    if not isinstance(values, dict) or any(
        not isinstance(values.get(field), str) or not values[field] for field in fields
    ):
        raise GoToolchainSelectionError(
            request, "verification_failed", "missing or malformed Go environment fields",
            probes=tuple(probes), diagnostics=tuple(diagnostics),
        )
    try:
        root = Path(values["GOROOT"]).resolve(strict=True)
        actual_binary = (root / "bin" / binary.name).resolve(strict=True)
        actual_hash = hashlib.sha256(actual_binary.read_bytes()).hexdigest()
    except (OSError, ValueError, RuntimeError) as error:
        raise GoToolchainSelectionError(
            request, "verification_failed", f"reading observed executable: {error}",
            probes=tuple(probes), diagnostics=tuple(diagnostics),
        ) from error
    # A bin-only alias can preserve executable identity while changing compiler roots.
    if (
        values["GOVERSION"] != f"go{request.version}" or values["GOTOOLCHAIN"] != "local"
        or root != binary.parent.parent or actual_binary != binary or actual_hash != initial_hash
    ):
        raise GoToolchainSelectionError(
            request, "verification_failed", "observed version/root/mode/hash disagrees",
            probes=tuple(probes), diagnostics=tuple(diagnostics),
        )
    return GoToolchainSelection(
        request, status="verified", observed_version=values["GOVERSION"].removeprefix("go"),
        executable=binary, goroot=root, executable_sha256=initial_hash,
        selection_source=source, probes=tuple(probes),
        gofmt_executable=formatter, gofmt_sha256=formatter_hash,
        discovery_diagnostics=tuple(diagnostics),
    )


def _environment_value(environment: Mapping[str, str], name: str) -> str:
    if name in environment:
        return environment[name]
    if os.name == "nt":
        return next(
            (value for key, value in environment.items() if key.casefold() == name.casefold()),
            "",
        )
    return ""


def _selected_environment(environment: Mapping[str, str], binary: Path) -> dict[str, str]:
    controls = {"PATH", "GOROOT", "GOTOOLCHAIN"}
    # Windows treats key casing as equivalent; remove every inherited variant.
    child = {
        key: value for key, value in environment.items()
        if (key.upper() if os.name == "nt" else key) not in controls
    }
    path = _environment_value(environment, "PATH")
    child["PATH"] = str(binary.parent) + (os.pathsep + path if path else "")
    child["GOTOOLCHAIN"] = "local"
    return child


def _local_candidates(
    version: str, environment: Mapping[str, str],
) -> list[tuple[str, Path]]:
    executable_name = "go.exe" if os.name == "nt" else "go"
    candidates: list[tuple[str, Path]] = []
    on_path = shutil.which("go", path=_environment_value(environment, "PATH"))
    if on_path is not None:
        candidates.append(("path", Path(on_path)))
    root = _environment_value(environment, "GOROOT")
    if root:
        candidates.append(("goroot", Path(root) / "bin" / executable_name))
    home = Path.home()
    candidates.append(("sdk", home / "sdk" / f"go{version}" / "bin" / executable_name))
    host_os = {"Windows": "windows", "Linux": "linux", "Darwin": "darwin"}.get(platform.system())
    host_arch = {
        "amd64": "amd64", "x86_64": "amd64", "arm64": "arm64", "aarch64": "arm64",
    }.get(platform.machine().lower())
    if host_os is None or host_arch is None:
        return candidates
    caches: list[Path] = []
    module_cache = _environment_value(environment, "GOMODCACHE")
    if module_cache:
        caches.append(Path(module_cache))
    go_path = _environment_value(environment, "GOPATH")
    if go_path:
        caches.extend(
            Path(entry) / "pkg" / "mod" for entry in go_path.split(os.pathsep) if entry
        )
    else:
        caches.append(home / "go" / "pkg" / "mod")
    leaf = f"toolchain@v0.0.1-go{version}.{host_os}-{host_arch}"
    candidates.extend(
        ("module_cache", cache / "golang.org" / leaf / "bin" / executable_name)
        for cache in caches
    )
    return candidates


def _inspect_distribution(binary: Path, version: str) -> tuple[Path, str, Path, str]:
    binary = binary.resolve(strict=True)
    expected_name = "go.exe" if os.name == "nt" else "go"
    if binary.name != expected_name or binary.parent.name != "bin":
        raise ValueError(f"{binary} is not a direct distribution bin/{expected_name}")
    metadata = (binary.parent.parent / "VERSION").read_text(encoding="utf-8").splitlines()
    if not metadata or metadata[0].strip() != f"go{version}":
        raise ValueError(f"{binary} has missing or mismatching VERSION metadata")
    formatter = binary.with_name("gofmt.exe" if os.name == "nt" else "gofmt").resolve(strict=True)
    return (
        binary, hashlib.sha256(binary.read_bytes()).hexdigest(),
        formatter, hashlib.sha256(formatter.read_bytes()).hexdigest(),
    )


def capture_go_toolchain_request(
    launch_directory: Path,
    *,
    version_override: str | None = None,
    executable_override: Path | None = None,
) -> GoToolchainRequest | None:
    """Freeze trusted policy without preparing a checkout or executing Go."""

    project = Project(launch_directory)
    try:
        config = project.load_config() if project.config_path.exists() else {}
    except (StateFileError, OSError) as error:
        raise GoToolchainConfigError(f"reading {project.config_path}: {error}") from error
    project_version = config.get("review_go_version")
    if "review_go_version" in config:
        try:
            _validate_version(project_version)
        except ValueError as error:
            raise GoToolchainConfigError(
                f"{project.config_path}: review_go_version: {error}"
            ) from error
    executable = (
        (launch_directory / executable_override).resolve()
        if executable_override is not None else None
    )
    if version_override is not None:
        _validate_version(version_override)
        return GoToolchainRequest(version_override, "cli", project_version, executable)
    if project_version is None:
        if executable is not None:
            raise ValueError("--go-executable requires a configured or explicit Go version")
        return None
    return GoToolchainRequest(project_version, "project", project_version, executable)


def _validate_version(version: object) -> None:
    if not isinstance(version, str):
        raise ValueError("expected an exact stable Go version such as 1.26.9")
    match = re.fullmatch(r"1\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version)
    if match is None or int(match[1]) < 21:
        raise ValueError("expected an exact stable Go 1.X.Y version with X >= 21")
