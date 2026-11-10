"""Disposable standalone-review composition trial; all reviewers are synthetic."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import time
from unittest.mock import patch

import atom
from atom.cli import main as atom_main
from atom.runner import CommandOutcome, CommandResult, SubprocessRunner


REPOSITORY = Path(__file__).resolve().parents[2]
TARGET_ROOT = Path(
    r"C:\Users\gimotwan\AppData\Local\Temp\atom-phase04-standalone-review-20261108"
)
ARTIFACT_ROOT = r"specs\atom-v1-improvements\phase-04-entry-points\standalone-review"
REVIEWERS = ("fixture-reviewer-one", "fixture-reviewer-two")
BASE_SOURCE = (
    "package sample\n\n"
    "// Double supports a deterministic fixture smoke test.\n"
    "func Double(value int) int {\n\treturn value * 2\n}\n"
)
CHANGED_SOURCE = BASE_SOURCE.replace("value * 2", "value + value")
TEST_SOURCE = (
    'package sample\n\nimport "testing"\n\n'
    "func TestDouble(t *testing.T) {\n"
    "\tif result := Double(3); result != 6 {\n"
    '\t\tt.Fatalf("Double(3) = %d; want 6", result)\n\t}\n}\n'
)


class TrialBlocked(Exception):
    """Stop an observation that cannot establish its registered question."""


class ContractContradiction(Exception):
    """Record an observed contradiction instead of repairing the treatment."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractContradiction(message)


class ObservingRunner:
    def __init__(self, environment: dict[str, str]) -> None:
        self.delegate = SubprocessRunner()
        self.environment = environment
        self.commands: list[dict] = []
        self.real_command_count = 0
        self.synthetic_call_count = 0

    def run(self, command, working_directory, timeout_seconds=180, stdin_text=None,
            *, environment=None):
        command = tuple(str(part) for part in command)
        executable = Path(command[0]).stem.lower()
        synthetic = executable == "copilot"
        if synthetic:
            self.synthetic_call_count += 1
            if "--model" not in command:
                raise TrialBlocked("Unrecognized reviewer command; not delegated.")
            reviewer = command[command.index("--model") + 1]
            if reviewer not in REVIEWERS:
                raise TrialBlocked(f"Unexpected reviewer identity: {reviewer}")
            if "--output-format" in command:
                finding = json.dumps([{
                    "file": "sample.go",
                    "line": 5,
                    "severity": "low",
                    "message": "Synthetic transport sentinel; not a real code defect.",
                }])
                stdout = "\n".join(json.dumps(event) for event in (
                    {"type": "assistant.message", "data": {
                        "content": finding, "phase": "final_answer",
                    }},
                    {"type": "result", "exitCode": 0,
                     "sessionId": "synthetic-review-session"},
                ))
            elif "-p" in command and command[command.index("-p") + 1] == "ping":
                stdout = "synthetic availability response"
            else:
                raise TrialBlocked("Unrecognized reviewer mode; not delegated.")
            result = CommandResult(
                command, working_directory, CommandOutcome.COMPLETED,
                0, stdout, "", 0.0,
            )
        else:
            if executable not in {"git", "go", "gofmt"}:
                raise TrialBlocked(f"Unapproved real executable: {command[0]}")
            if executable == "git" and any(
                word in command for word in ("fetch", "push", "pull", "clone")
            ):
                raise TrialBlocked("Remote Git operation is outside this trial.")
            if self.real_command_count >= 100:
                raise TrialBlocked("Real-command ceiling reached.")
            self.real_command_count += 1
            result = self.delegate.run(
                command, working_directory,
                min(timeout_seconds, 180),
                stdin_text,
                environment=self.environment if environment is None else environment,
            )
        self.commands.append({
            "command": list(command),
            "cwd": str(working_directory),
            "synthetic": synthetic,
            "stdin": stdin_text,
            "outcome": result.outcome.value,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_seconds": result.duration_seconds,
        })
        if result.outcome is not CommandOutcome.COMPLETED:
            raise TrialBlocked(
                f"Command did not complete: {command!r}; "
                f"{result.outcome.value}: {result.stderr}"
            )
        return result


def checked(runner: ObservingRunner, target: Path, *command: str) -> str:
    result = runner.run(command, target)
    if result.exit_code != 0:
        raise TrialBlocked(
            f"Preparation/observation command failed: {command!r}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result.stdout


def git(runner: ObservingRunner, target: Path, *arguments: str) -> str:
    return checked(
        runner, target, "git",
        "-c", f"core.hooksPath={TARGET_ROOT / 'disabled-hooks'}",
        "-c", "commit.gpgsign=false",
        "-c", "user.name=Atom Fixture",
        "-c", "user.email=atom-fixture@example.com",
        *arguments,
    )


def snapshot(runner: ObservingRunner, target: Path) -> dict:
    files = {}
    for path in sorted(target.rglob("*")):
        relative = path.relative_to(target)
        if ".git" in relative.parts or not path.is_file():
            continue
        files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "files": files,
        "head": git(runner, target, "rev-parse", "HEAD"),
        "staged_diff": git(runner, target, "diff", "--cached"),
        "working_diff": git(runner, target, "diff"),
        "unexpected_pipeline_paths": [
            name for name in (".atom", "specs", "poc") if (target / name).exists()
        ],
    }


def create_fixture(runner: ObservingRunner, name: str, go_version: str) -> Path:
    target = TARGET_ROOT / name
    target.mkdir()
    git(runner, target, "init", "--quiet", "--initial-branch=main")
    if name != "no-module":
        (target / "go.mod").write_text(
            f"module example.com/atom-review-fixture-{name}\n\ngo {go_version}\n",
            encoding="utf-8",
        )
    (target / "sample.go").write_text(BASE_SOURCE, encoding="utf-8")
    (target / "sample_test.go").write_text(TEST_SOURCE, encoding="utf-8")
    (target / "notes.txt").write_text("Initial selection fixture.\n", encoding="utf-8")
    (target / "observer-sentinel.txt").write_text(
        "Observer-owned preservation fixture.\n", encoding="utf-8"
    )
    git(runner, target, "add", ".")
    git(runner, target, "commit", "--quiet", "-m",
        "Prepare disposable review fixture\n\n"
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>")
    if name == "branch":
        git(runner, target, "switch", "--quiet", "-c", "fixture-change")
    source = (
        BASE_SOURCE.replace("value * 2", "value + missingFixtureValue")
        if name == "broken-source" else CHANGED_SOURCE
    )
    (target / "sample.go").write_text(source, encoding="utf-8")
    if name in {"staged", "branch"}:
        git(runner, target, "add", "sample.go")
    if name == "branch":
        git(runner, target, "commit", "--quiet", "-m",
            "Commit disposable review change\n\n"
            "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>")
    if name in {"working", "staged", "branch"}:
        (target / "notes.txt").write_text(
            "This change must not be selected for review.\n", encoding="utf-8"
        )
        if name == "working":
            git(runner, target, "add", "notes.txt")
    return target


def observe_case(runner: ObservingRunner, name: str, target: Path,
                 observations: list[dict]) -> dict:
    arguments = ["review"]
    arguments.extend(
        ["--branch", "main"] if name == "branch"
        else ["--staged"] if name == "staged" else ["--working"]
    )
    arguments.extend(["--runs", "1", "--concurrency", "1"])
    for reviewer in REVIEWERS:
        arguments.extend(["--model", reviewer])
    if name != "branch":
        arguments.append("--json")
    before = snapshot(runner, target)
    start = len(runner.commands)
    synthetic_before = runner.synthetic_call_count
    stdout = io.StringIO()
    stderr = io.StringIO()
    original_cwd = Path.cwd()
    try:
        os.chdir(target)
        with patch("atom.cli.SubprocessRunner", return_value=runner):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = atom_main(arguments)
    finally:
        os.chdir(original_cwd)
    commands = runner.commands[start:]
    reviewer_calls = runner.synthetic_call_count - synthetic_before
    after = snapshot(runner, target)
    result = {
        "name": name, "target": str(target), "cli_arguments": arguments,
        "exit_code": exit_code, "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(), "before": before, "after": after,
        "reviewer_calls": reviewer_calls, "commands": commands,
    }
    observations.append(result)
    require(before == after, f"{name}: review mutated source or Git selection.")
    require(not after["unexpected_pipeline_paths"], f"{name}: pipeline paths created.")
    if name == "broken-source":
        require(exit_code != 0, "Broken source did not block review.")
        require(reviewer_calls == 0, "Reviewers were consulted after a required gate failure.")
        require(not result["stdout"].strip(), "Broken source produced a success-shaped report.")
        require("required Go toolchain gates failed" in result["stderr"],
                "Broken source did not expose required gate failure.")
    else:
        if exit_code != 0:
            raise TrialBlocked(
                f"{name}: review could not complete with the available tooling:\n"
                f"{result['stdout']}{result['stderr']}"
            )
        require(reviewer_calls == 4, f"{name}: expected two probes and two synthetic replies.")
        if name == "branch":
            require(result["stdout"].startswith("# Code review\n"),
                    "Branch report is not Markdown.")
            require("sample.go" in result["stdout"], "Branch report lost the selected file.")
            require("Synthetic transport sentinel" in result["stdout"],
                    "Branch report lost the synthetic finding.")
        else:
            payload = json.loads(result["stdout"])
            require(payload["diff"]["files"] == ["sample.go"],
                    f"{name}: report includes unselected files.")
            require(not payload["is_partial"] and not payload["has_no_usable_response"],
                    f"{name}: synthetic responses were not fully extracted.")
            require(len(payload["findings"]) == 1, f"{name}: synthetic findings not merged.")
            require(all(model["runs_answered"] == 1 for model in payload["models"]),
                    f"{name}: synthetic participation was not recorded.")
            if name == "no-module":
                require(not payload["toolchain"]["was_run"],
                        "Missing module claimed a toolchain run.")
                require("go.mod" in payload["toolchain"]["skip_reason"],
                        "Missing-module reason was not exposed.")
                require(not (target / "go.mod").exists(), "Missing module was silently created.")
                require(payload["toolchain"]["gates"] == [],
                        "Missing module invented passing gates.")
            else:
                require(payload["toolchain"]["was_run"], f"{name}: gates were skipped.")
                require(all(gate["status"] == "passed" for gate in payload["toolchain"]["gates"]
                            if gate["required"]), f"{name}: required gates did not pass.")
    return result


def write_artifact(relative: str, content: str) -> None:
    result = SubprocessRunner().run(
        (sys.executable, "-m", "atom.artifact_cli", relative),
        REPOSITORY, 180, content,
    )
    if not result.succeeded:
        raise TrialBlocked(
            f"Artifact writer failed; no alternate writer will be used:\n"
            f"{result.stdout}{result.stderr}"
        )


def execute() -> int:
    if TARGET_ROOT.exists():
        raise TrialBlocked("Disposable root already exists; refusing reuse or deletion.")
    runtime = Path(atom.__file__).resolve()
    if runtime.is_relative_to(REPOSITORY):
        raise TrialBlocked("This trial must exercise the installed non-editable runtime.")
    environment = dict(os.environ)
    tool_directories = []
    for executable in ("git", "go", "gcc"):
        found = shutil.which(executable)
        if found is None:
            raise TrialBlocked(f"Existing required executable is missing: {executable}")
        tool_directories.append(str(Path(found).parent))
    tool_directories.extend((str(Path(sys.executable).parent),
                             str(Path(os.environ["SystemRoot"]) / "System32")))
    environment["PATH"] = os.pathsep.join(dict.fromkeys(tool_directories))
    environment.update(GOTOOLCHAIN="local", GOPROXY="off", GOSUMDB="off")
    for name in ("staticcheck", "errcheck", "govulncheck"):
        if shutil.which(name, path=environment["PATH"]):
            raise TrialBlocked(f"Unexpected advisory tool in bounded PATH: {name}")
    TARGET_ROOT.mkdir()
    (TARGET_ROOT / "disabled-hooks").mkdir()
    runner = ObservingRunner(environment)
    observations = []
    started_at = time.perf_counter()
    verdict = "Confirmed"
    problem = ""
    with patch.dict(os.environ, environment, clear=True):
        try:
            version_output = checked(runner, TARGET_ROOT, "go", "version")
            version = version_output.split()[2].removeprefix("go")
            for name in ("working", "staged", "branch", "broken-source", "no-module"):
                if time.perf_counter() - started_at > 300:
                    raise TrialBlocked("Five-minute local execution ceiling reached.")
                target = create_fixture(runner, name, version)
                observation = observe_case(runner, name, target, observations)
                print(f"{name}: declared observation met; CLI exit {observation['exit_code']}; "
                      f"{observation['reviewer_calls']} synthetic transport calls", flush=True)
        except ContractContradiction as error:
            verdict = "Refuted"
            problem = str(error)
        except (TrialBlocked, OSError, ValueError) as error:
            verdict = "Inconclusive"
            problem = str(error)
    evidence = {
        "question": "Can the installed Atom review CLI select working, staged and branch "
                    "changes in local Go repositories without Atom or phase state, "
                    "produce correctly scoped reports, preserve source/state, and retain "
                    "honest missing-module and failing-gate behavior, with a deterministic "
                    "reviewer transport instead of real model calls?",
        "verdict": verdict, "problem": problem,
        "runtime": str(runtime), "target_root": str(TARGET_ROOT),
        "real_command_count": runner.real_command_count,
        "synthetic_call_count": runner.synthetic_call_count,
        "model_calls": 0, "duration_seconds": time.perf_counter() - started_at,
        "observations": observations, "all_commands": runner.commands,
        "limits": "CLI entry function with a patched external runner; real Git/Go, "
                  "synthetic reviewer transport. No real model or human-control evidence. "
                  "Fixtures retained; no cleanup performed.",
    }
    write_artifact(ARTIFACT_ROOT + r"\execution.json", json.dumps(evidence, indent=2))
    print(f"Verdict: {verdict}; real commands: {runner.real_command_count}; "
          f"synthetic calls: {runner.synthetic_call_count}; model calls: 0", flush=True)
    if problem:
        print(problem, file=sys.stderr)
    return 0 if verdict == "Confirmed" else 1


if __name__ == "__main__":
    raise SystemExit(execute())
