"""Disposable, offline exact-Go-selection experiment; no production implementation."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

QUESTION = "Can child-process-only selection of Go 1.26.9 keep build, vet, and test on that exact version across conflicting inherited selection settings and compatible module/workspace toolchain suggestions, reject higher language-version requirements without upgrading, and leave persistent defaults unchanged?"
VERSION = "go1.26.9"
PARENTS = ("local", "go1.26.9+auto")
CASES = (
    ("plain-module", False, False, False),
    ("module-newer-suggestion", False, True, False),
    ("module-newer-minimum", False, False, True),
    ("workspace-newer-suggestion", True, True, False),
    ("workspace-newer-minimum", True, False, True),
)
MAIN = '''package main

import (
    "fmt"
    "runtime"
)

func main() {
    if runtime.Version() != "go1.26.9" {
        panic("unexpected runtime: " + runtime.Version())
    }
    fmt.Println("runtime=" + runtime.Version())
}
'''
TEST = '''package main

import (
    "runtime"
    "testing"
)

func TestExactRuntime(t *testing.T) {
    if runtime.Version() != "go1.26.9" {
        t.Fatalf("runtime = %s; want go1.26.9", runtime.Version())
    }
    t.Log("runtime=" + runtime.Version())
}
'''
# The existing runner owns and cleans up Go's subprocess tree on Windows.
WRAPPER = '''import json, sys
from pathlib import Path
from atom.runner import SubprocessRunner
r = SubprocessRunner().run(sys.argv[2:], Path(sys.argv[1]), timeout_seconds=60)
print(json.dumps({"outcome": r.outcome.value, "exit_code": r.exit_code,
                  "stdout": r.stdout, "stderr": r.stderr}, ensure_ascii=True))
'''


def emit(event, **values):
    print(json.dumps({"event": event, **values}, ensure_ascii=True), flush=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def settings_path(environment):
    explicit = environment.get("GOENV")
    if explicit == "off":
        return None
    if explicit:
        return Path(explicit).resolve()
    if os.name == "nt":
        return Path(environment["APPDATA"]) / "go" / "env"
    return Path(environment.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "go" / "env"


def source_snapshot(directory):
    return {str(p.relative_to(directory)): digest(p) for p in directory.rglob("*") if p.is_file()}


def run_command(command, directory, environment, case, parent):
    try:
        completed = subprocess.run(
            [sys.executable, "-c", WRAPPER, str(directory), *command],
            env=environment, capture_output=True, encoding="utf-8", errors="replace", timeout=70,
        )
    except subprocess.TimeoutExpired as error:
        emit("wrapper-timeout", case=case, parent_selection=parent,
             argv=command, stdout=error.stdout, stderr=error.stderr)
        raise RuntimeError("wrapper exceeded bounded cleanup allowance") from error
    if completed.returncode != 0:
        emit("wrapper-failure", case=case, parent_selection=parent, argv=command,
             exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        raise RuntimeError("command wrapper failed")
    result = json.loads(completed.stdout)
    emit("command", case=case, parent_selection=parent, child_selection=environment["GOTOOLCHAIN"],
         argv=command, **result)
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
         inherited_selection=original_environment.get("GOTOOLCHAIN"),
         launcher=shutil.which("go"))
    verdict, reason = "Inconclusive", "trial did not complete"
    completed_cases = command_count = 0
    try:
        with tempfile.TemporaryDirectory(prefix="atom-toolchain-", dir=repository.parent) as temporary:
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
                    child = dict(inherited, GOTOOLCHAIN=VERSION, GOWORK=gowork,
                                 GOPROXY="off", GOSUMDB="off", GOFLAGS="", CGO_ENABLED="0",
                                 GODEBUG="toolchaintrace=1", GOTELEMETRY="off",
                                 PYTHONPATH=str(repository / "tools"))
                    emit("case-start", case=name, parent_selection=parent,
                         child_selection=child["GOTOOLCHAIN"], workspace=workspace,
                         newer_suggestion=suggestion, higher_minimum=higher_minimum)
                    executable = outputs / (name + (".exe" if os.name == "nt" else ".out"))
                    commands = [
                        ["go", "version"],
                        ["go", "env", "-json", "GOVERSION", "GOROOT", "GOTOOLCHAIN", "GOENV"],
                        ["go", "build", "-x", "-o", str(executable), "."],
                        ["go", "vet", "-x", "."],
                        ["go", "test", "-count=1", "-v", "-x", "."],
                    ]
                    if not higher_minimum:
                        commands.append([str(executable)])
                    for index, command in enumerate(commands):
                        command_count += 1
                        result = run_command(command, module, child, name, parent)
                        output = result["stdout"] + result["stderr"]
                        if higher_minimum and result["exit_code"] != 0:
                            if "1.27.0" not in output or "1.26.9" not in output:
                                raise RuntimeError("failure was not attributable to the declared higher minimum")
                            continue
                        if result["exit_code"] != 0:
                            raise RuntimeError("compatible fixture command failed")
                        if index == 0 and not result["stdout"].startswith("go version " + VERSION + " "):
                            verdict = "Refuted"
                            raise RuntimeError("unexpected version selected")
                        if index == 1:
                            observed = json.loads(result["stdout"])
                            if observed["GOVERSION"] != VERSION or observed["GOTOOLCHAIN"] != VERSION:
                                verdict = "Refuted"
                                raise RuntimeError("child selection was not exact")
                            actual_settings = None if observed["GOENV"] == "off" else Path(observed["GOENV"]).resolve()
                            if actual_settings != configuration:
                                raise RuntimeError("persistent settings path was not controlled before execution")
                            go_executable = Path(observed["GOROOT"]) / "bin" / ("go.exe" if os.name == "nt" else "go")
                            emit("provenance", case=name, parent_selection=parent,
                                 actual_go_executable=str(go_executable), sha256=digest(go_executable))
                            if not go_executable.is_file():
                                raise RuntimeError("actual Go executable provenance is unavailable")
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
                    completed_cases += 1
                    emit("case-passed", case=name, parent_selection=parent)
            verdict, reason = "Confirmed", "all ten predeclared cases met their expected outcomes"
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
