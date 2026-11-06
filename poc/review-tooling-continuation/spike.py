"""One approved local classification trial; not production review policy."""

import argparse
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time


QUESTION = (
    "Can bounded controls distinguish a declared Go-minimum incompatibility from "
    "genuine or ambiguous source/check failures on the same frozen fixture, allowing "
    "only the evidenced incompatibility to reach a reviewer stub with truthful degraded evidence?"
)
VERSIONS = ("1.26.9", "1.27.0")
CHECKS = ("fmt", "build", "vet", "test")


class StopTrial(Exception):
    def __init__(self, verdict, detail):
        super().__init__(detail)
        self.verdict = verdict


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_hash(directory):
    files = sorted(
        file for file in directory.iterdir()
        if file.suffix == ".go" or file.name in ("go.mod", "go.sum")
    )
    return digest(b"".join(
        file.name.encode("utf-8") + b"\0" + file.read_bytes() + b"\0" for file in files
    ))


def version_tuple(version):
    return tuple(int(part) for part in version.split("."))


def classify(observation):
    """Classify observations without fixture names, expected labels or stderr matching."""
    if not observation["selection_verified"] or not observation["snapshot_equal"]:
        return "unknown", "selection or frozen-input identity is not established"
    selected = observation["selected"]
    if any(result.outcome.value != "completed" for result in selected):
        return "unknown", "a selected command did not complete"
    selected_checks = observation["selected_checks"]
    if all(result.status.value == "passed" for result in selected_checks):
        return "normal", "all bounded selected checks passed"
    control = observation["control"]
    if not control or any(result.outcome.value != "completed" for result in control):
        return "unknown", "compatible control is absent or did not complete"
    if not all(result.status.value == "passed" for result in observation["control_checks"]):
        return "source_or_mixed", "compatible control also has failed or unchecked gates"
    minimum = observation["minimum"]
    if (
        version_tuple(observation["selected_version"]) < minimum
        <= version_tuple(observation["control_version"])
        and selected_checks[0].status.value == "passed"
        and selected_checks[1].status.value == "failed"
    ):
        return "degraded", "verified selected version is below declared minimum; identical control passes"
    return "unknown", "control success alone does not explain the selected failure"


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--output", required=True, type=Path)
    destination = arguments.parse_args().output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    repository = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repository / "tools"))
    from atom.gates import GateResult, GateStatus
    from atom.go_selection import (
        GoToolchainRequest, GoToolchainSelectionError,
        _selected_environment, resolve_go_toolchain,
    )
    from atom.runner import CommandOutcome, CommandResult, SubprocessRunner
    from atom.toolchain import ToolchainEvidence

    events = destination / "events.jsonl"
    native_count = 0
    receipts = []
    results = []
    parent_environment = dict(os.environ)
    goenv_hashes = {}
    selections = {}

    def emit(event, **values):
        with events.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps({"event": event, **values}, sort_keys=True) + "\n")

    def deadline():
        remaining = 900 - (time.monotonic() - started)
        if remaining <= 0:
            raise StopTrial("Inconclusive", "approved 15-minute limit reached")
        return remaining

    class RecordingRunner:
        def run(self, command, working_directory, timeout_seconds=60, stdin_text=None, *, environment=None):
            nonlocal native_count
            remaining = deadline()
            if native_count >= 96:
                raise StopTrial("Inconclusive", "approved 96-command limit reached")
            native_count += 1
            controls = {
                key: environment.get(key) for key in
                ("GOTOOLCHAIN", "GOWORK", "GOPROXY", "CGO_ENABLED", "GOCACHE")
            }
            controls["GOROOT_present"] = any(key.upper() == "GOROOT" for key in environment)
            emit("command_started", index=native_count, argv=list(command),
                 directory=str(working_directory), child_controls=controls,
                 child_environment_sha256=digest(json.dumps(dict(environment), sort_keys=True).encode()))
            result = SubprocessRunner().run(
                command, working_directory, min(timeout_seconds, 60, remaining),
                stdin_text=stdin_text, environment=environment,
            )
            emit("command", index=native_count, argv=list(result.command),
                 directory=str(result.working_directory), outcome=result.outcome.value,
                 exit_code=result.exit_code, stdout=result.stdout, stderr=result.stderr,
                 duration_seconds=result.duration_seconds)
            deadline()
            return result

    runner = RecordingRunner()
    environment = dict(parent_environment)
    environment.update({
        "GOTOOLCHAIN": "local", "GOWORK": "off", "GOPROXY": "off",
        "CGO_ENABLED": "0", "GOCACHE": str(destination / "cache"),
    })
    (destination / "cache").mkdir()

    def gate(name, result):
        passed = result.succeeded and (name != "fmt" or not result.stdout.strip())
        return GateResult(
            name, GateStatus.PASSED if passed else GateStatus.FAILED,
            f"{result.outcome.value}; exit={result.exit_code}",
            result.combined_output, True, result.duration_seconds,
        )

    def skipped(name):
        return GateResult(name, GateStatus.SKIPPED, "earlier bounded gate failed",
                          "No command executed for this gate.", True, 0)

    def check_fixture(selection, directory, *, slow=False):
        child = _selected_environment(environment, selection.executable)
        raw = []
        evaluated = []
        formatter = runner.run((str(selection.gofmt_executable), "-l", "."), directory, environment=child)
        raw.append(formatter)
        evaluated.append(gate("fmt", formatter))
        for name, suffix in (
            ("build", ("build", "./...")),
            ("vet", ("vet", "./...")),
            ("test", ("test", "-count=1", "./...")),
        ):
            if any(result.status is not GateStatus.PASSED for result in evaluated):
                evaluated.append(skipped(name))
                continue
            if slow and name == "test":
                warm = runner.run(
                    (str(selection.executable), "test", "-c", "-o", str(directory / "warm.test.exe")),
                    directory, environment=child,
                )
                if not warm.succeeded:
                    raise StopTrial("Inconclusive", "slow fixture could not compile before timing")
                suffix = ("test", "-v", "-count=1", "-run", "TestWait", "./...")
            result = runner.run(
                (str(selection.executable), *suffix), directory,
                2 if slow and name == "test" else 60, environment=child,
            )
            raw.append(result)
            evaluated.append(gate(name, result))
        return raw, evaluated

    def verify_identities():
        for selection in selections.values():
            if (
                digest(selection.executable.read_bytes()) != selection.executable_sha256
                or digest(selection.gofmt_executable.read_bytes()) != selection.gofmt_sha256
            ):
                raise StopTrial("Inconclusive", "selected/control executable identity changed")

    def stub(prompt):
        content = prompt.encode("utf-8")
        receipt = {"bytes": len(content), "sha256": digest(content), "prompt": prompt}
        receipts.append(receipt)
        emit("stub_receipt", **receipt)

    cases = [
        ("compatible-valid", "1.26.0", "valid", "normal"),
        ("higher-minimum-valid", "1.27.0", "valid", "degraded"),
        ("compile-defect", "1.26.0", "compile", "blocked"),
        ("failing-assertion", "1.26.0", "assertion", "blocked"),
        ("higher-minimum-compile-defect", "1.27.0", "compile", "blocked"),
        ("missing-requested-executable", "1.26.0", "missing", "blocked"),
        ("slow-test", "1.26.0", "slow", "blocked"),
        ("control-runner-error", "1.27.0", "simulated", "blocked"),
        ("changed-source", "1.27.0", "changed", "blocked"),
    ]
    verdict = "Inconclusive"
    detail = "batch did not complete"
    exit_code = 2
    emit("batch_start", question=QUESTION, versions=VERSIONS, sweeps=2,
         maximum_commands=96, maximum_seconds=900,
         driver_sha256=digest(Path(__file__).read_bytes()))
    try:
        for version in VERSIONS:
            selection = resolve_go_toolchain(
                GoToolchainRequest(version, "cli"), runner, destination, environment=environment,
            )
            selections[version] = selection
            values = json.loads(selection.probes[-1].stdout)
            goenv = values["GOENV"]
            if goenv != "off":
                file = Path(goenv)
                goenv_hashes[file] = digest(file.read_bytes()) if file.exists() else None
            emit("verified_distribution", version=selection.observed_version,
                 executable=str(selection.executable), root=str(selection.goroot),
                 go_sha256=selection.executable_sha256, gofmt_sha256=selection.gofmt_sha256)
        selected, compatible = (selections[version] for version in VERSIONS)
        for sweep in (1, 2):
            for label, minimum, treatment, expected in cases:
                deadline()
                directory = destination / "fixtures" / f"sweep-{sweep}" / label
                directory.mkdir(parents=True)
                (directory / "go.mod").write_text(
                    f"module example.invalid/continuation\n\ngo {minimum}\n", encoding="utf-8", newline="\n",
                )
                expression = "missingValue" if treatment == "compile" else "left + right"
                (directory / "fixture.go").write_text(
                    "// Package fixture provides one deterministic arithmetic boundary.\n"
                    "package fixture\n\n"
                    "// Add gives the fixture a public behavior to test.\n"
                    f"func Add(left, right int) int {{ return {expression} }}\n",
                    encoding="utf-8", newline="\n",
                )
                if treatment == "slow":
                    test_source = (
                        'package fixture\n\nimport (\n\t"fmt"\n\t"testing"\n\t"time"\n)\n\n'
                        'func TestWait(t *testing.T) {\n\tfmt.Println("slow-test-entered")\n'
                        '\ttime.Sleep(10 * time.Second)\n}\n'
                    )
                else:
                    expected_sum = 6 if treatment == "assertion" else 5
                    test_source = (
                        'package fixture\n\nimport "testing"\n\n'
                        'func TestAdd(t *testing.T) {\n'
                        f'\tif actual := Add(2, 3); actual != {expected_sum} {{\n'
                        f'\t\tt.Fatalf("Add(2, 3) = %d; want {expected_sum}", actual)\n\t}}\n}}\n'
                    )
                (directory / "fixture_test.go").write_text(test_source, encoding="utf-8", newline="\n")
                parsed = re.search(r"(?m)^go ([0-9]+\.[0-9]+\.[0-9]+)$",
                                   (directory / "go.mod").read_text(encoding="utf-8"))
                if parsed is None:
                    raise StopTrial("Inconclusive", "fixture minimum could not be read")
                before = source_hash(directory)
                observation = {
                    "selection_verified": True, "snapshot_equal": True,
                    "minimum": version_tuple(parsed[1]),
                    "selected_version": selected.observed_version,
                    "control_version": compatible.observed_version,
                    "selected": [], "selected_checks": [], "control": [], "control_checks": [],
                }
                if treatment == "missing":
                    try:
                        resolve_go_toolchain(
                            GoToolchainRequest(
                                VERSIONS[0], "cli", executable=directory / "absent" / "bin" / "go.exe",
                            ), runner, directory, environment=environment,
                        )
                    except GoToolchainSelectionError as error:
                        emit("selection_failure", reason=error.reason, detail=str(error),
                             probes=len(error.probes), diagnostics=list(error.diagnostics))
                        observation["selection_verified"] = False
                    else:
                        raise StopTrial("Inconclusive", "missing executable unexpectedly selected")
                else:
                    raw, evaluated = check_fixture(selected, directory, slow=treatment == "slow")
                    observation["selected"] = raw
                    observation["selected_checks"] = evaluated
                    after_selected = source_hash(directory)
                    if treatment == "slow" and (
                        raw[-1].outcome is not CommandOutcome.TIMED_OUT
                        or "slow-test-entered" not in raw[-1].stdout
                    ):
                        raise StopTrial("Inconclusive", "slow fixture did not reach marker then time out")
                    if any(result.status is not GateStatus.PASSED for result in evaluated) and treatment != "slow":
                        if treatment == "changed":
                            with (directory / "fixture.go").open("a", encoding="utf-8", newline="\n") as file:
                                file.write("\n// Deliberate snapshot change for the comparison guard.\n")
                        control_before = source_hash(directory)
                        if treatment == "simulated":
                            result = CommandResult(
                                (str(compatible.executable), "build", "./..."), directory,
                                CommandOutcome.RUNNER_ERROR, None, "",
                                "SIMULATED: compatible-control runner could not launch", 0,
                            )
                            emit("simulated_command", argv=list(result.command),
                                 outcome=result.outcome.value, stderr=result.stderr)
                            observation["control"] = [result]
                            observation["control_checks"] = [gate("build", result)]
                        else:
                            raw_control, control_checks = check_fixture(compatible, directory)
                            observation["control"] = raw_control
                            observation["control_checks"] = control_checks
                        observation["snapshot_equal"] = (
                            before == after_selected == control_before == source_hash(directory)
                        )
                    else:
                        observation["snapshot_equal"] = before == after_selected
                verify_identities()
                classification, reason = classify(observation)
                previous_receipts = len(receipts)
                prompt_bytes = 0
                if classification in ("normal", "degraded"):
                    evidence = ToolchainEvidence(
                        tuple(observation["selected_checks"]) + (
                            GateResult("race", GateStatus.SKIPPED, "outside bounded POC scope", "", True, 0),
                            GateResult("staticcheck", GateStatus.SKIPPED, "outside bounded POC scope", "", False, 0),
                            GateResult("errcheck", GateStatus.SKIPPED, "outside bounded POC scope", "", False, 0),
                            GateResult("govulncheck", GateStatus.SKIPPED, "outside bounded POC scope", "", False, 0),
                        ),
                        True, "", formatting_is_scoped=True,
                        selection=replace(
                            selected, executable_sha256_after=selected.executable_sha256,
                            gofmt_sha256_after=selected.gofmt_sha256,
                        ),
                    )
                    heading = (
                        "DEGRADED REVIEW: requested-compiler checks did not pass. "
                        "Control passes do not validate the requested compiler.\n"
                        if classification == "degraded" else "BOUNDED POC REVIEW: not a full toolchain gate.\n"
                    )
                    prompt = heading + evidence.as_prompt_block()
                    if classification == "degraded":
                        prompt += "\nCompatible control (same frozen source, not selected validation):\n"
                        prompt += "\n".join(
                            f"{result.name}: {result.status.value}" for result in observation["control_checks"]
                        )
                        exclusion = evidence._exclusion_paragraph()
                        if any(word in exclusion for word in ("build errors", "vet diagnostics", "failing tests")):
                            raise StopTrial("Refuted", "failed selected checks were excluded")
                    stub(prompt)
                    prompt_bytes = receipts[-1]["bytes"]
                admitted = len(receipts) - previous_receipts
                required = expected if expected != "blocked" else classification
                if expected == "blocked" and admitted:
                    raise StopTrial("Refuted", f"{label} unsafely reached the stub")
                if classification != required or (expected in ("normal", "degraded") and admitted != 1):
                    raise StopTrial("Inconclusive", f"{label} did not produce intended observation")
                if treatment == "compile" and not any(
                    result.exit_code not in (None, 0) for result in observation["control"]
                ):
                    raise StopTrial("Inconclusive", "compile fixture did not fail under control")
                if treatment == "assertion" and (
                    observation["selected_checks"][-1].status is not GateStatus.FAILED
                    or observation["control_checks"][-1].status is not GateStatus.FAILED
                ):
                    raise StopTrial("Inconclusive", "assertion fixture did not fail both test commands")
                record = {
                    "sweep": sweep, "fixture": label, "classification": classification,
                    "reason": reason, "stub_calls": admitted, "prompt_bytes": prompt_bytes,
                    "source_sha256_before": before, "source_sha256_after": source_hash(directory),
                }
                results.append(record)
                emit("case_result", **record)
                print(json.dumps(record, sort_keys=True), flush=True)
        if dict(os.environ) != parent_environment:
            raise StopTrial("Refuted", "parent environment was changed")
        for file, expected_hash in goenv_hashes.items():
            observed_hash = digest(file.read_bytes()) if file.exists() else None
            if observed_hash != expected_hash:
                raise StopTrial("Refuted", "parent GOENV contents changed")
        verify_identities()
        deadline()
        verdict, detail, exit_code = "Confirmed", "all eighteen bounded observations matched", 0
    except StopTrial as error:
        verdict, detail = error.verdict, str(error)
        exit_code = 1 if verdict == "Refuted" else 2
    except (GoToolchainSelectionError, OSError, ValueError) as error:
        verdict, detail = "Inconclusive", f"{type(error).__name__}: {error}"
        exit_code = 2
    summary = {
        "verdict": verdict, "detail": detail, "native_commands": native_count,
        "completed_cases": len(results), "stub_receipts": len(receipts),
        "model_calls": 0, "elapsed_seconds": time.monotonic() - started,
        "driver_sha256": digest(Path(__file__).read_bytes()),
    }
    emit("batch_result", **summary)
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True), flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
