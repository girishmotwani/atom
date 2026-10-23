"""Capture review-specific formatting inputs without scanning untouched files."""

from __future__ import annotations

import base64
import binascii
import hashlib
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

from atom.diff import CapturedDiff, DiffRequest, DiffSource, DiffUnavailable, git_command_for
from atom.gates import (
    GateResult, GateStatus, _belongs_to_a_nested_module,
    _result_for_non_completed_command,
)
from atom.runner import CommandRunner


_READ_GIT_BYTES = (
    "import base64,subprocess,sys;"
    "result=subprocess.run(sys.argv[1:],input=b'',stdout=subprocess.PIPE,"
    "stderr=subprocess.PIPE,check=False);"
    "sys.stdout.write(base64.b64encode(result.stdout).decode('ascii'));"
    "sys.stderr.write(result.stderr.decode('utf-8','replace'));"
    "sys.exit(result.returncode)"
)


@dataclass(frozen=True)
class FormattingFile:
    """Keep selected source immutable while subsequent checks and models run."""

    path: str
    content: bytes


class ChangedFilesFormatGate:
    """Check only the source snapshots belonging to the selected review."""

    name = "fmt"
    required = True

    def __init__(
        self, files: tuple[FormattingFile, ...], source: str,
        exclusions: tuple[str, ...] = (),
    ) -> None:
        self.files = files
        self.source = source
        self.exclusions = exclusions

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        scope = (
            f"Formatting checks selected snapshots from {self.source}: "
            + ", ".join(repr(file.path) for file in self.files)
        )
        if self.exclusions:
            scope += "\nNot checked: " + "; ".join(self.exclusions)
        if not self.files:
            return GateResult(
                self.name, GateStatus.SKIPPED,
                f"Checked 0 changed Go files from {self.source}",
                f"No surviving changed Go files belong to this module.\n{scope}",
                True, 0.0,
            )
        duration = 0.0
        for file in self.files:
            try:
                text = file.content.decode("utf-8").replace("\r\n", "\n")
            except UnicodeDecodeError as error:
                return GateResult(
                    self.name, GateStatus.FAILED,
                    f"{file.path!r} is not valid UTF-8",
                    f"{error}\n{scope}", True, duration,
                )
            result = runner.run(("gofmt",), directory, stdin_text=text)
            duration += result.duration_seconds
            incomplete = _result_for_non_completed_command(self.name, result, True)
            if incomplete is not None:
                return GateResult(
                    self.name, GateStatus.FAILED,
                    f"{file.path!r}: {incomplete.summary}",
                    f"{incomplete.details}\n{scope}", True, duration,
                )
            if not result.succeeded:
                return GateResult(
                    self.name, GateStatus.FAILED,
                    f"gofmt failed for {file.path!r}",
                    f"{result.combined_output}\n{scope}", True, duration,
                )
            if result.stdout != text:
                return GateResult(
                    self.name, GateStatus.FAILED,
                    f"{file.path!r} needs gofmt ({self.source})",
                    f"{result.stderr}\n{scope}", True, duration,
                )
        names = ", ".join(repr(file.path) for file in self.files)
        return GateResult(
            self.name, GateStatus.PASSED,
            f"Checked {len(self.files)} changed Go file(s) from {self.source}: {names}",
            scope,
            True, duration,
        )


def _git(runner: CommandRunner, directory: Path, command: tuple[str, ...]) -> str:
    result = runner.run(command, directory, 60)
    if not result.succeeded:
        detail = result.combined_output or result.outcome.value
        raise DiffUnavailable(f"Could not capture review formatting inputs: {detail}")
    return result.stdout


def _blob_hash(content: bytes, object_id: str) -> str:
    algorithm = "sha1" if len(object_id) == 40 else "sha256"
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.new(algorithm, header + content).hexdigest()


def _read_blob(runner: CommandRunner, directory: Path, object_id: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", object_id) or not int(object_id, 16):
        raise DiffUnavailable("Git provided an invalid selected file identity.")
    # The existing runner is text-only. Its owned Python/Git descendants encode
    # bytes before newline/UTF-8 decoding can change the selected object.
    encoded = _git(
        runner, directory,
        (sys.executable, "-c", _READ_GIT_BYTES, "git", "cat-file", "blob", object_id),
    )
    try:
        content = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise DiffUnavailable(f"Git blob transport was malformed: {error}") from error
    if _blob_hash(content, object_id) != object_id:
        raise DiffUnavailable("Git blob content does not match its selected identity.")
    return content


def _validate_name(name: str, read_source: bool = False) -> None:
    if (
        not name or (read_source and ("\\" in name or ":" in name))
        or any(part in ("", ".", "..") for part in name.split("/"))
    ):
        raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")


def capture_review_diff(
    request: DiffRequest,
    runner: CommandRunner,
    working_directory: Path,
) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
    """Capture the patch and changed-file identities in the same Git operation."""

    root = Path(_git(
        runner, working_directory, ("git", "rev-parse", "--show-toplevel")
    ).rstrip("\r\n")).resolve()
    module = working_directory.resolve()
    module_parts = tuple(os.path.normcase(part) for part in module.relative_to(root).parts)
    selected_request = request
    if request.source is DiffSource.BRANCH:
        base = _git(
            runner, working_directory,
            ("git", "rev-parse", "--verify", "--end-of-options", f"{request.base_ref}^{{commit}}"),
        ).strip()
        selected_request = DiffRequest(DiffSource.BRANCH, base)
    command = git_command_for(selected_request) + (
        "--raw", "--no-abbrev", "-z", "--patch", "--full-index",
        "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative",
        "--submodule=short", "--",
    )
    raw = _git(runner, working_directory, command)
    if not raw:
        return CapturedDiff("", request), ChangedFilesFormatGate((), request.describe())
    metadata, separator, patch = raw.partition("\0\0")
    if not separator:
        raise DiffUnavailable("Git did not provide a framed review file manifest.")
    fields = metadata.split("\0")
    blocks = re.split(r"(?m)(?=^diff --git )", patch)[1:]
    files: list[FormattingFile] = []
    paths: list[str] = []
    exclusions: list[str] = []
    index = 0
    block_index = 0
    while index < len(fields):
        record = fields[index]
        if not re.fullmatch(
            r":(?:[0-7]{6}) (?:[0-7]{6}) "
            r"(?:[0-9a-f]{40}|[0-9a-f]{64}) (?:[0-9a-f]{40}|[0-9a-f]{64}) "
            r"(?:[ADMT]|M[0-9]{1,3}|[RC][0-9]{1,3})",
            record,
        ) or index + 1 >= len(fields):
            raise DiffUnavailable("Git provided a malformed review file manifest.")
        header = record.split()
        name = fields[index + 1]
        _validate_name(name)
        index += 2
        if header[4].startswith(("R", "C")):
            if index >= len(fields):
                raise DiffUnavailable("Git omitted a rename destination.")
            name = fields[index]
            _validate_name(name)
            index += 1
        paths.append(name)
        # Git renders a type change as deletion plus addition, but supplies
        # one raw entry. The second patch carries the surviving content.
        block_count = 2 if header[4] == "T" else 1
        if block_index + block_count > len(blocks):
            raise DiffUnavailable("Git manifest and patch entries do not match.")
        block_index += block_count
        block = blocks[block_index - 1]
        if not name.endswith(".go") or header[4] == "D":
            continue
        parts = name.split("/")
        # Compare Git components before native path interpretation: names
        # outside the selected module are never opened on this platform.
        if tuple(os.path.normcase(part) for part in parts[:len(module_parts)]) != module_parts:
            exclusions.append(f"{name!r}: outside selected module")
            continue
        _validate_name(name, read_source=True)
        if header[1] not in ("100644", "100755"):
            raise DiffUnavailable(f"Selected Go file {name!r} is a non-regular Git entry.")
        path = root.joinpath(*parts)
        relative = path.relative_to(module).as_posix()
        if request.source is DiffSource.WORKING:
            try:
                if (
                    not stat.S_ISREG(path.lstat().st_mode)
                    or not path.resolve().is_relative_to(module)
                ):
                    raise DiffUnavailable(f"Changed Go file {name!r} is unsafe or non-regular.")
            except OSError as error:
                raise DiffUnavailable(f"Could not inspect changed Go file {name!r}: {error}") from error
        if _belongs_to_a_nested_module(relative, working_directory):
            exclusions.append(f"{name!r}: nested module")
            continue
        try:
            if request.source is not DiffSource.WORKING:
                content = _read_blob(runner, working_directory, header[3])
            else:
                content = path.read_bytes()
        except (OSError, ValueError) as error:
            raise DiffUnavailable(f"Could not read changed Go file {name!r}: {error}") from error
        if request.source is DiffSource.WORKING:
            identity = re.search(r"(?m)^index [0-9a-f]+\.\.([0-9a-f]+)", block)
            expected = identity.group(1) if identity else header[2]
            # Git may normalize CRLF while computing its diff, but no other
            # transforming filter can safely substitute the bytes we format.
            if all(
                _blob_hash(candidate, expected) != expected
                for candidate in (content, content.replace(b"\r\n", b"\n"))
            ):
                raise DiffUnavailable(f"Changed Go file {name!r} no longer matches the captured diff.")
        files.append(FormattingFile(name, content))
    if block_index != len(blocks):
        raise DiffUnavailable("Git manifest and patch entries do not match.")
    return CapturedDiff(patch, request, tuple(sorted(set(paths)))), ChangedFilesFormatGate(
        tuple(files), request.describe(), tuple(exclusions)
    )
