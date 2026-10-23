"""Disposable Git/gofmt experiment; no production code or target repository writes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import time

from atom.gates import FormatGate, GateStatus
from atom.runner import CommandOutcome, SubprocessRunner


BASE = "package fixture\n\nvar Value = 1\n"
CLEAN = "package fixture\n\nvar Value = 2\n"
BAD = "package fixture\nvar Value=2\n"


class Blocked(RuntimeError):
    pass


class CommandFailed(RuntimeError):
    pass


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Commands:
    def __init__(self, scratch):
        self.scratch = scratch
        self.started = time.monotonic()
        self.delegate = SubprocessRunner()
        self.cleanup = False
        self.calls = []
        self.hooks = scratch / "empty-hooks"
        self.hooks.mkdir()

    def record(self, value):
        with (self.scratch / "commands.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(value, ensure_ascii=True) + "\n")

    def run(self, command, working_directory, timeout_seconds=300, stdin_text=None):
        budget = 120 if self.cleanup else 90
        remaining = self.started + budget - time.monotonic()
        if remaining <= 0:
            raise Blocked("experiment budget exhausted")
        result = self.delegate.run(command, working_directory,
                                   min(15, timeout_seconds, remaining), stdin_text)
        record = {"command": list(command), "cwd": str(working_directory),
                  "stdin_sha256": None if stdin_text is None else digest(stdin_text),
                  "outcome": result.outcome.value, "exit_code": result.exit_code,
                  "stdout": result.stdout, "stderr": result.stderr,
                  "duration_seconds": result.duration_seconds}
        self.calls.append(record)
        self.record(record)
        if result.outcome is not CommandOutcome.COMPLETED:
            raise Blocked("owned command did not complete; see command evidence")
        return result

    def git(self, root, *arguments):
        command = ("git", "--no-optional-locks", "-c", "core.autocrlf=false",
                   "-c", f"core.hooksPath={self.hooks}", "-c", "commit.gpgsign=false",
                   "-c", "user.name=Atom Fixture", "-c", "user.email=fixture@example.invalid",
                   "-C", str(root), *arguments)
        result = self.run(command, root)
        if not result.succeeded:
            raise CommandFailed("required Git command failed; see command evidence")
        return result.stdout


def audit(commands, root):
    index = Path(commands.git(root, "rev-parse", "--path-format=absolute",
                              "--git-path", "index").strip())
    return {
        "head": commands.git(root, "rev-parse", "HEAD").strip(),
        "branch": commands.git(root, "rev-parse", "--abbrev-ref", "HEAD").strip(),
        "index": hashlib.sha256(index.read_bytes()).hexdigest(),
        "diff": digest(commands.git(root, "diff", "--no-ext-diff", "--no-textconv",
                                     "--binary", "HEAD", "--")),
        "untracked": digest(commands.git(root, "ls-files", "--others", "--exclude-standard", "-z")),
    }


def fixture(commands, parent, name, prefix=""):
    root = parent / name
    root.mkdir()
    module = root / prefix if prefix else root
    module.mkdir(exist_ok=True)
    (module / "go.mod").write_text("module example.invalid/fixture\n\ngo 1.23\n", encoding="utf-8", newline="\n")
    (module / "untouched.go").write_text("package fixture\nvar Existing=1\n", encoding="utf-8", newline="\n")
    (module / "changed.go").write_text(BASE, encoding="utf-8", newline="\n")
    commands.git(root, "init", "--quiet", "--initial-branch=main")
    commands.git(root, "add", "--all")
    commands.git(root, "commit", "--quiet", "-m", "fixture baseline")
    base = commands.git(root, "rev-parse", "HEAD").strip()
    return root, module, base


def selected_format(commands, root, module, mode, base):
    head = commands.git(module, "rev-parse", "HEAD").strip() if mode == "branch" else None
    arguments = ["diff", "--no-ext-diff", "--no-textconv", "--name-status", "-z", "--find-renames"]
    if mode == "staged":
        arguments.append("--cached")
    elif mode == "branch":
        arguments.append(f"{base}...{head}")
    arguments.append("--")
    raw = commands.git(module, *arguments)
    fields = raw.split("\0") if raw else []
    if fields:
        assert fields.pop() == "", "Git status stream must be NUL terminated"
    entries = []
    deleted = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        name = fields[index]
        index += 1
        if status.startswith(("R", "C")):
            name = fields[index]
            index += 1
        assert status[0] in "AMDRCT", "unsupported status"
        if not name.endswith(".go"):
            continue
        path = root.joinpath(*name.split("/"))
        relative = path.relative_to(module).as_posix()
        if status == "D":
            deleted.append(relative)
            continue
        if mode == "working":
            text = path.read_bytes().decode("utf-8")
        else:
            spec = f":{name}" if mode == "staged" else f"{head}:{name}"
            text = commands.git(root, "show", spec)
        entries.append((relative, text))
    checked = {}
    status = "skipped" if not entries else "passed"
    for name, text in entries:
        checked[name] = digest(text)
        commands.record({"formatter_input": name, "mode": mode, "sha256": digest(text)})
        result = commands.run(("gofmt",), module, stdin_text=text)
        assert commands.calls[-1]["stdin_sha256"] == digest(text)
        if result.exit_code != 0:
            status = "error"
        elif result.stdout != text and status != "error":
            status = "failed"
    return status, checked, deleted


def remove_readonly(function, path, error):
    os.chmod(path, stat.S_IWRITE)
    function(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch", required=True, type=Path)
    arguments = parser.parse_args()
    scratch = arguments.scratch.resolve()
    scratch.mkdir()
    fixtures = scratch / "fixture"
    fixtures.mkdir()
    commands = Commands(scratch)
    original = Path(__file__).resolve().parents[2]
    tooling = Path(os.environ["PYTHONPATH"]).resolve().parent
    verdict = "Inconclusive"
    reason = "not completed"
    completed = 0
    before = {}
    clean_before = {}
    print("experiment=changed_file_formatting fixed_fixture_set=true model_calls=0", flush=True)
    try:
        revision = commands.git(tooling, "rev-parse", "HEAD").strip()
        assert revision == "a90fbe1bb44ffa3bc1b1e9866b4078be1948cf0c", "unexpected tooling revision"
        assert not commands.git(tooling, "status", "--porcelain"), "tooling checkout is dirty"
        before = audit(commands, original)
        clean_before = audit(commands, tooling)
        print(f"tooling_revision={revision}", flush=True)

        def verify(name, root, module, mode, base, expected, expected_status, expected_deleted=()):
            nonlocal completed
            before_calls = len(commands.calls)
            actual_status, checked, deleted = selected_format(commands, root, module, mode, base)
            expected_hashes = {path: digest(text) for path, text in expected.items()}
            assert checked == expected_hashes, f"{name}: wrong selected paths or snapshot bytes"
            assert actual_status == expected_status, f"{name}: unexpected formatter status"
            assert sorted(deleted) == sorted(expected_deleted), f"{name}: deletion evidence mismatch"
            formatter_calls = [call for call in commands.calls[before_calls:] if call["command"][0] == "gofmt"]
            assert len(formatter_calls) == len(expected), f"{name}: formatter input count mismatch"
            completed += 1
            commands.record({"case": name, "expected": expected_hashes, "actual": checked,
                             "status": actual_status, "deleted": deleted})
            print(f"case={name} status={actual_status} inputs={len(checked)} exact_input_match=true", flush=True)

        for mode in ("working", "staged", "branch"):
            root, module, base = fixture(commands, fixtures, f"clean-{mode}")
            (module / "changed.go").write_text(CLEAN, encoding="utf-8", newline="\n")
            if mode in ("staged", "branch"):
                commands.git(root, "add", "changed.go")
            if mode == "branch":
                commands.git(root, "commit", "--quiet", "-m", "clean changed file")
                (module / "changed.go").write_text(BAD, encoding="utf-8", newline="\n")
            verify(f"clean-{mode}-ignores-untouched", root, module, mode, base,
                   {"changed.go": CLEAN}, "passed")

        root, module, base = fixture(commands, fixtures, "bad-working")
        (module / "changed.go").write_text(BAD, encoding="utf-8", newline="\n")
        verify("bad-changed-file", root, module, "working", base, {"changed.go": BAD}, "failed")

        for name, staged, working, expected_status in (
            ("staged-bad-working-clean", BAD, CLEAN, "failed"),
            ("staged-clean-working-bad", CLEAN, BAD, "passed"),
        ):
            root, module, base = fixture(commands, fixtures, name)
            (module / "changed.go").write_text(staged, encoding="utf-8", newline="\n")
            commands.git(root, "add", "changed.go")
            (module / "changed.go").write_text(working, encoding="utf-8", newline="\n")
            verify(name, root, module, "staged", base, {"changed.go": staged}, expected_status)

        root, module, base = fixture(commands, fixtures, "added")
        (module / "added.go").write_text(CLEAN, encoding="utf-8", newline="\n")
        commands.git(root, "add", "added.go")
        verify("added-file", root, module, "staged", base, {"added.go": CLEAN}, "passed")

        root, module, base = fixture(commands, fixtures, "renamed")
        commands.git(root, "mv", "changed.go", "renamed.go")
        verify("pure-rename", root, module, "staged", base, {"renamed.go": BASE}, "passed")

        root, module, base = fixture(commands, fixtures, "deleted")
        commands.git(root, "rm", "--quiet", "changed.go")
        verify("deleted-file", root, module, "staged", base, {}, "skipped", ("changed.go",))

        root, module, base = fixture(commands, fixtures, "names", "module")
        name = "review caf\u00e9 file.go"
        (module / name).write_text(CLEAN, encoding="utf-8", newline="\n")
        commands.git(root, "add", "--all")
        verify("unicode-space-and-module-prefix", root, module, "staged", base, {name: CLEAN}, "passed")

        root, module, base = fixture(commands, fixtures, "no-go")
        (module / "README.md").write_text("fixture\n", encoding="utf-8", newline="\n")
        commands.git(root, "add", "README.md")
        verify("no-surviving-go", root, module, "staged", base, {}, "skipped")

        root, module, base = fixture(commands, fixtures, "git-error")
        try:
            selected_format(commands, root, module, "branch", "missing-fixture-ref")
        except CommandFailed:
            completed += 1
            print("case=git-error status=blocked exact_error_preserved=true", flush=True)
        else:
            raise AssertionError("Git failure became a successful empty scope")

        root, module, base = fixture(commands, fixtures, "syntax-error")
        invalid = "package fixture\nfunc (\n"
        (module / "changed.go").write_text(invalid, encoding="utf-8", newline="\n")
        verify("formatter-syntax-error", root, module, "working", base,
               {"changed.go": invalid}, "error")

        root, module, base = fixture(commands, fixtures, "standalone")
        standalone = FormatGate().evaluate(commands, module)
        assert standalone.status is GateStatus.FAILED, "standalone FormatGate was weakened"
        assert "untouched.go" in standalone.summary, "standalone blocker not attributed"
        completed += 1
        print("case=standalone-control status=failed untouched_defect_detected=true", flush=True)
        assert completed == 14, "fixed fixture set incomplete"
        verdict = "Confirmed"
        reason = "all fixed fixture expectations met"
    except AssertionError as error:
        verdict, reason = "Refuted", str(error)
    except (Blocked, CommandFailed, OSError, ValueError) as error:
        verdict, reason = "Inconclusive", str(error)
    finally:
        commands.cleanup = True
        try:
            original_matches = bool(before) and audit(commands, original) == before
            tooling_matches = bool(clean_before) and audit(commands, tooling) == clean_before
            print(f"original_checkout_unchanged={str(original_matches).lower()}", flush=True)
            print(f"tooling_checkout_unchanged={str(tooling_matches).lower()}", flush=True)
            if not original_matches or not tooling_matches:
                verdict, reason = "Inconclusive", f"audit mismatch; prior outcome: {verdict}: {reason}"
        except (Blocked, CommandFailed, OSError) as error:
            verdict, reason = "Inconclusive", f"audit incomplete: {error}; prior outcome: {verdict}: {reason}"
        try:
            assert fixtures.parent == scratch and fixtures.name == "fixture"
            shutil.rmtree(fixtures, onerror=remove_readonly)
            print(f"fixture_removed={str(not fixtures.exists()).lower()}", flush=True)
        except OSError as error:
            verdict, reason = "Inconclusive", f"cleanup failed: {error}; prior outcome: {verdict}: {reason}"
    elapsed = time.monotonic() - commands.started
    if elapsed > 120:
        verdict, reason = "Inconclusive", f"total budget exceeded; prior outcome: {verdict}: {reason}"
    summary = {"verdict": verdict, "reason": reason, "cases_completed": completed,
               "elapsed_seconds": elapsed, "fixture_removed": not fixtures.exists()}
    (scratch / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")
    print(f"cases_completed={completed} elapsed_seconds={elapsed}", flush=True)
    print(f"verdict={verdict} reason={reason}", flush=True)
    return {"Confirmed": 0, "Refuted": 1, "Inconclusive": 2}[verdict]


if __name__ == "__main__":
    raise SystemExit(main())


