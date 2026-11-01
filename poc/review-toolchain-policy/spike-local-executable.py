"""One approved offline direct-executable trial; retain the original failed driver."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from spike import CASES, MAIN, PARENTS, TEST, VERSION, WRAPPER, digest, emit, settings_path, source_snapshot

QUESTION = "Can direct invocation of an existing local Go 1.26.9 executable with child-only GOTOOLCHAIN=local keep build, vet and test on that exact version across inherited selection settings and module/workspace suggestions, reject higher language minimums without upgrading, and leave persistent defaults unchanged?"


def find_candidate(environment, configuration):
    settings = {}
    if configuration is not None and configuration.is_file():
        for line in configuration.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key in ("GOMODCACHE", "GOPATH", "GOROOT"):
                settings[key] = value
    roots = []
    cache = environment.get("GOMODCACHE") or settings.get("GOMODCACHE")
    if cache:
        roots.append(Path(cache) / "golang.org" / "toolchain@v0.0.1-go1.26.9.windows-amd64")
    gopath = environment.get("GOPATH") or settings.get("GOPATH") or str(Path.home() / "go")
    for directory in gopath.split(os.pathsep):
        roots.append(Path(directory) / "pkg" / "mod" / "golang.org" / "toolchain@v0.0.1-go1.26.9.windows-amd64")
    roots.append(Path.home() / "sdk" / VERSION)
    configured_root = environment.get("GOROOT") or settings.get("GOROOT")
    if configured_root:
        roots.append(Path(configured_root))
    if os.name == "nt" and environment.get("ProgramFiles"):
        roots.append(Path(environment["ProgramFiles"]) / "Go")
    for root in dict.fromkeys(roots):
        executable = root / "bin" / ("go.exe" if os.name == "nt" else "go")
        version_file = root / "VERSION"
        declared = version_file.read_text(encoding="utf-8").splitlines()[0] if version_file.is_file() else None
        emit("candidate-inspection", path=str(executable), exists=executable.is_file(), declared_version=declared)
        if executable.is_file() and declared == VERSION:
            return executable.resolve()
    raise RuntimeError("no complete existing candidate at the approved cache/SDK locations")


def run_command(command, directory, environment, case, parent):
    try:
        completed = subprocess.run(
            [sys.executable, "-c", WRAPPER, str(directory), *command],
            env=environment, capture_output=True, encoding="utf-8", errors="replace", timeout=70,
        )
    except subprocess.TimeoutExpired as error:
        emit("wrapper-timeout", case=case, parent_selection=parent, argv=command,
             stdout=(error.stdout or b"").decode("utf-8", "replace"),
             stderr=(error.stderr or b"").decode("utf-8", "replace"))
        raise RuntimeError("wrapper exceeded bounded cleanup allowance") from error
    if completed.returncode != 0:
        emit("wrapper-failure", case=case, parent_selection=parent, argv=command,
             exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        raise RuntimeError("command wrapper failed")
    result = json.loads(completed.stdout)
    emit("command", case=case, parent_selection=parent,
         child_selection=environment["GOTOOLCHAIN"], argv=command, **result)
    if result["outcome"] != "completed":
        raise RuntimeError("command did not complete: " + result["outcome"])
    return result


def main():
    repository = Path(__file__).resolve().parents[2]
    original_environment = dict(os.environ)
    configuration = settings_path(original_environment)
    original_settings = digest(configuration) if configuration is not None else None
    emit("start", question=QUESTION, cases=10, timeout_seconds=60, retries=0,
         toolchain_downloads_allowed=False, configuration_sha256_before=original_settings,
         original_driver_sha256=digest(Path(__file__).with_name("spike.py")))
    verdict, reason = "Inconclusive", "trial did not complete"
    completed_cases = command_count = 0
    try:
        if os.name != "nt":
            raise RuntimeError("this approved trial is scoped to the current Windows environment")
        candidate = find_candidate(original_environment, configuration)
        original_executable = digest(candidate)
        emit("selected-candidate", path=str(candidate), sha256=original_executable)
        with tempfile.TemporaryDirectory(prefix="atom-local-toolchain-", dir=repository.parent) as temporary:
            temporary = Path(temporary)
            fixtures, outputs = temporary / "fixtures", temporary / "outputs"
            fixtures.mkdir()
            outputs.mkdir()
            locations = {}
            for name, workspace, suggestion, higher_minimum in CASES:
                base = fixtures / name
                module = base / "module" if workspace else base
                module.mkdir(parents=True)
                minimum = "1.27.0" if higher_minimum and not workspace else "1.26.0"
                module_text = f"module example.invalid/{name}\n\ngo {minimum}\n"
                if suggestion and not workspace:
                    module_text += "toolchain go1.27.0\n"
                (module / "go.mod").write_text(module_text, encoding="utf-8")
                (module / "main.go").write_text(MAIN, encoding="utf-8")
                (module / "main_test.go").write_text(TEST, encoding="utf-8")
                if workspace:
                    floor = "1.27.0" if higher_minimum else "1.26.0"
                    work_text = f"go {floor}\n"
                    if suggestion:
                        work_text += "toolchain go1.27.0\n"
                    (base / "go.work").write_text(work_text + "\nuse ./module\n", encoding="utf-8")
                locations[name] = (module, str(base / "go.work") if workspace else "off")
            original_sources = source_snapshot(fixtures)
            emit("fixture-inputs", sha256=original_sources)
            for parent in PARENTS:
                for name, workspace, suggestion, higher_minimum in CASES:
                    module, gowork = locations[name]
                    inherited = dict(original_environment, GOTOOLCHAIN=parent)
                    child = dict(inherited, GOTOOLCHAIN="local", GOWORK=gowork,
                                 GOPROXY="off", GOFLAGS="", CGO_ENABLED="0",
                                 GODEBUG="toolchaintrace=1", GOTELEMETRY="off",
                                 PYTHONPATH=str(repository / "tools"))
                    child.pop("GOROOT", None)
                    emit("case-start", case=name, parent_selection=parent,
                         child_selection=child["GOTOOLCHAIN"], workspace=workspace,
                         newer_suggestion=suggestion, higher_minimum=higher_minimum)
                    executable = outputs / (name + ".exe")
                    commands = [
                        [str(candidate), "version"],
                        [str(candidate), "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV"],
                        [str(candidate), "build", "-x", "-o", str(executable), "."],
                        [str(candidate), "vet", "-x", "."],
                        [str(candidate), "test", "-count=1", "-v", "-x", "."],
                    ]
                    if not higher_minimum:
                        commands.append([str(executable)])
                    for index, command in enumerate(commands):
                        command_count += 1
                        result = run_command(command, module, child, name, parent)
                        output = result["stdout"] + result["stderr"]
                        if higher_minimum and result["exit_code"] != 0:
                            if "requires go >= 1.27.0" not in output or "running go 1.26.9" not in output:
                                raise RuntimeError("failure was not attributable to the declared higher minimum")
                            continue
                        if result["exit_code"] != 0:
                            raise RuntimeError("compatible fixture command failed")
                        if index == 0 and not result["stdout"].startswith("go version " + VERSION + " "):
                            verdict = "Refuted"
                            raise RuntimeError("unexpected version selected")
                        if index == 1:
                            observed = json.loads(result["stdout"])
                            if observed["GOVERSION"] != VERSION or observed["GOTOOLCHAIN"] != "local":
                                verdict = "Refuted"
                                raise RuntimeError("child selection was not local and exact")
                            actual_settings = None if observed["GOENV"] == "off" else Path(observed["GOENV"]).resolve()
                            if actual_settings != configuration:
                                raise RuntimeError("persistent settings path was not controlled before execution")
                            actual_executable = (Path(observed["GOROOT"]) / "bin" / "go.exe").resolve()
                            if actual_executable != candidate or digest(actual_executable) != original_executable:
                                raise RuntimeError("executed-tool provenance does not match the candidate")
                            emit("provenance", case=name, parent_selection=parent,
                                 actual_go_executable=str(actual_executable), sha256=digest(actual_executable))
                        if higher_minimum and index >= 2:
                            verdict = "Refuted"
                            raise RuntimeError("higher minimum unexpectedly accepted")
                        if index in (4, 5) and "runtime=" + VERSION not in result["stdout"]:
                            raise RuntimeError("compiled runtime-version evidence is absent")
                    if source_snapshot(fixtures) != original_sources:
                        verdict = "Refuted"
                        raise RuntimeError("fixture inputs were modified")
                    if (digest(configuration) if configuration is not None else None) != original_settings:
                        verdict = "Refuted"
                        raise RuntimeError("persistent Go settings changed")
                    if digest(candidate) != original_executable:
                        raise RuntimeError("candidate executable identity changed")
                    completed_cases += 1
                    emit("case-passed", case=name, parent_selection=parent)
            verdict, reason = "Confirmed", "all ten direct-local-executable cases met their expected outcomes"
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        reason = f"{type(error).__name__}: {error}"
        emit("stopped", reason=reason)
    unchanged_environment = dict(os.environ) == original_environment
    unchanged_settings = (digest(configuration) if configuration is not None else None) == original_settings
    if not unchanged_environment or not unchanged_settings:
        verdict, reason = "Refuted", "parent environment or persistent Go settings changed"
    emit("verdict", verdict=verdict, reason=reason, completed_cases=completed_cases,
         command_count=command_count, parent_environment_unchanged=unchanged_environment,
         persistent_settings_unchanged=unchanged_settings)
    return 0 if verdict == "Confirmed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
