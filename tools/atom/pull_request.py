"""Prepare independently owned PR checkouts for the existing review pipeline."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from atom.diff import DiffRequest, select_source
from atom.runner import CommandRunner


@dataclass(frozen=True)
class _Location:
    organization: str
    project: str
    repository: str
    number: int

    @property
    def prefix(self) -> str:
        components = (self.organization, self.project)
        return "https://dev.azure.com/" + "/".join(quote(value, safe="") for value in components)

    @property
    def url(self) -> str:
        return f"{self.prefix}/_git/{quote(self.repository, safe='')}/pullrequest/{self.number}"

    @property
    def api_url(self) -> str:
        return (
            f"{self.prefix}/_apis/git/repositories/{quote(self.repository, safe='')}"
            f"/pullrequests/{self.number}?api-version=7.1"
        )


def _parse_url(url: str) -> _Location:
    invalid = ValueError("PR URL must be a supported HTTPS Azure DevOps pull request link.")
    if (
        not url or url != url.strip()
        or any(ord(character) < 32 or ord(character) == 127 for character in url)
    ):
        raise invalid
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.port is not None or parsed.username is not None:
            raise invalid
        host = parsed.hostname or ""
        parts = parsed.path.removeprefix("/").removesuffix("/").split("/")
        if host == "dev.azure.com":
            pass
        elif host.endswith(".visualstudio.com"):
            parts.insert(0, host.removesuffix(".visualstudio.com"))
        else:
            raise invalid
        if len(parts) != 6 or parts[2] != "_git" or parts[4] != "pullrequest":
            raise invalid
        if not re.fullmatch(r"[1-9][0-9]*", parts[5]):
            raise invalid
        names = []
        for part in (parts[0], parts[1], parts[3]):
            if re.search(r"%(?![0-9a-fA-F]{2})", part):
                raise invalid
            name = unquote(part, errors="strict")
            if (
                not name.strip() or name in (".", "..")
                or any(character in "/\\%" or ord(character) < 32 or ord(character) == 127
                       for character in name)
            ):
                raise invalid
            names.append(name)
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9-]*", names[0]):
            raise invalid
        return _Location(*names, int(parts[5]))
    except (ValueError, UnicodeError):
        # Never echo a refused URL: it may have contained a password.
        raise invalid from None


class PullRequestReviewError(Exception):
    """Prevent failed preparation or cleanup from becoming a clean review."""


@dataclass(frozen=True)
class _PullRequestProvenance:
    url: str
    number: int
    source_branch: str
    target_branch: str
    source_commit: str
    target_commit: str
    merge_base: str
    module_path: str


@dataclass(frozen=True)
class PreparedPullRequest:
    """Keep review inputs together for the lifetime of their owned checkout."""

    working_directory: Path
    request: DiffRequest
    provenance: _PullRequestProvenance


@dataclass(frozen=True)
class _Metadata:
    location: _Location
    remote_url: str
    source_ref: str
    target_ref: str
    source_commit: str
    repository_names: tuple[str, str]
    project_names: tuple[str, str]

    def matches(self, location: _Location) -> bool:
        return (
            location.organization.casefold() == self.location.organization.casefold()
            and location.project.casefold() in self.project_names
            and location.repository.casefold() in self.repository_names
        )


def _repository_url(url: str) -> _Location:
    if (
        not url or url != url.strip()
        or any(ord(character) < 32 or ord(character) == 127 for character in url)
    ):
        raise ValueError("unsupported repository URL")
    parsed = urlsplit(url)
    if parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError("unsupported repository URL")
    host = parsed.hostname or ""
    # Validate the port before removing userinfo; otherwise normalization hides it.
    if parsed.port is not None:
        raise ValueError("unsupported repository URL port")
    plain = urlunsplit((parsed.scheme, host, parsed.path.rstrip("/"), "", ""))
    location = _parse_url(plain + "/pullrequest/1")
    if parsed.username is not None and unquote(parsed.username).casefold() != location.organization.casefold():
        raise ValueError("repository URL username must be its organization")
    return location


def _branch_ref(value: object) -> str:
    if (
        not isinstance(value, str) or not value.startswith("refs/heads/")
        or value.endswith(("/", ".")) or ".." in value or "@{" in value
        or re.search(r"[\x00-\x20\x7f~^:?*\\\[]", value)
        or any(not part or part.startswith(".") or part.endswith(".lock")
               for part in value.split("/"))
    ):
        raise ValueError("source and target must be valid branch refs")
    return value


def _commit_id(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise ValueError("missing or invalid commit ID")
    return value.lower()


def _read_metadata(text: str, location: _Location) -> _Metadata:
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("expected a PR object")
        if type(data.get("pullRequestId")) is not int or data["pullRequestId"] != location.number:
            raise ValueError("PR identity does not match URL")
        if data.get("status") != "active" or data.get("forkSource") is not None:
            raise ValueError("only active, non-fork PRs are supported")
        repository = data["repository"]
        project = repository["project"]
        repository_names = (repository["name"].casefold(), repository["id"].casefold())
        project_names = (project["name"].casefold(), project["id"].casefold())
        remote = repository["remoteUrl"]
        metadata = _Metadata(
            location=location, remote_url=remote,
            source_ref=_branch_ref(data["sourceRefName"]),
            target_ref=_branch_ref(data["targetRefName"]),
            source_commit=_commit_id(data["lastMergeSourceCommit"]["commitId"]),
            repository_names=repository_names, project_names=project_names,
        )
        if not metadata.matches(location) or not metadata.matches(_repository_url(remote)):
            raise ValueError("repository identity does not match PR URL")
        return metadata
    except (ValueError, KeyError, TypeError, AttributeError):
        # Payloads can contain source or secrets. Report the schema failure, not a dump.
        raise PullRequestReviewError(
            "invalid ADO PR metadata: expected matching active non-fork PR, repository, "
            "branch refs, source commit ID and supported HTTPS clone URL"
        ) from None


def _run(
    runner: CommandRunner, command: Sequence[str], directory: Path,
    operation: str, timeout: float = 60.0,
) -> str:
    result = runner.run(command, directory, timeout_seconds=timeout)
    if not result.succeeded:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        detail = re.sub(r"(https?://)[^/\s]+@", r"\1[redacted]@", detail)
        raise PullRequestReviewError(
            f"{operation}: {result.outcome.value}, exit {result.exit_code}: {detail}"
        )
    return result.stdout


def _local_module(directory: Path, metadata: _Metadata, runner: CommandRunner) -> Path:
    try:
        if not (directory / "go.mod").is_file():
            raise ValueError("run from the corresponding local Go module containing go.mod")
        root = Path(_run(
            runner, ("git", "rev-parse", "--show-toplevel"), directory,
            "locating local repository",
        ).strip()).resolve()
        relative = directory.resolve().relative_to(root)
        origin = _run(
            runner, ("git", "remote", "get-url", "origin"), directory,
            "reading local repository origin",
        ).strip()
        if not metadata.matches(_repository_url(origin)):
            raise ValueError("local origin does not match the PR repository")
        return relative
    except (ValueError, OSError) as error:
        raise PullRequestReviewError(f"selecting local module: {error}") from None


def _materialize(
    checkout: Path, relative_module: Path, metadata: _Metadata, runner: CommandRunner,
) -> PreparedPullRequest:
    try:
        commits = []
        for ref in (metadata.source_ref, metadata.target_ref):
            remote_ref = "refs/remotes/origin/" + ref.removeprefix("refs/heads/")
            text = _run(
                runner, ("git", "rev-parse", "--verify", "--end-of-options",
                         remote_ref + "^{commit}"), checkout, "resolving fetched PR branch",
            )
            commits.append(_commit_id(text.strip()))
        source, target = commits
        if source != metadata.source_commit:
            raise ValueError("PR source moved since metadata resolution; rerun explicitly")
        bases = _run(
            runner, ("git", "merge-base", "--all", source, target),
            checkout, "finding PR merge base",
        ).splitlines()
        if len(bases) != 1:
            raise ValueError("PR must have exactly one merge base")
        merge_base = _commit_id(bases[0].strip())
        _run(
            runner, ("git", "checkout", "--detach", source),
            checkout, "checking out pinned PR source", 300.0,
        )
        if _run(
            runner, ("git", "ls-files", "--deleted", "-z"),
            checkout, "verifying tracked checkout files",
        ):
            raise ValueError("checkout is missing tracked files")
        _run(
            runner, ("git", "diff", "--exit-code", "HEAD", "--"),
            checkout, "verifying clean pinned checkout",
        )
        module = (checkout / relative_module).resolve(strict=True)
        module.relative_to(checkout.resolve())
        (module / "go.mod").resolve(strict=True).relative_to(checkout.resolve())
        if not (module / "go.mod").is_file():
            raise ValueError("cloned module has no go.mod")
    except (ValueError, OSError) as error:
        raise PullRequestReviewError(f"preparing pinned PR checkout: {error}") from None
    return PreparedPullRequest(
        working_directory=module, request=select_source(branch=target),
        provenance=_PullRequestProvenance(
            url=metadata.location.url, number=metadata.location.number,
            source_branch=metadata.source_ref, target_branch=metadata.target_ref,
            source_commit=source, target_commit=target, merge_base=merge_base,
            module_path=relative_module.as_posix(),
        ),
    )


@contextmanager
def prepare_pull_request_review(
    pr_url: str, module_directory: Path, runner: CommandRunner,
) -> Iterator[PreparedPullRequest]:
    """Keep a disposable pinned PR checkout alive while the caller reviews it."""
    location = _parse_url(pr_url)
    text = _run(
        runner,
        ("az", "rest", "--method", "get", "--resource",
         "499b84ac-1321-427f-aa17-267ca6975798", "--url", location.api_url,
         "--output", "json", "--only-show-errors"),
        module_directory, "reading ADO PR metadata (requires authorized Azure CLI login)",
    )
    metadata = _read_metadata(text, location)
    relative_module = _local_module(module_directory, metadata, runner)
    owner = uuid.uuid4().hex
    try:
        owned = Path(tempfile.mkdtemp(prefix="atom-pr-"))
    except OSError as error:
        raise PullRequestReviewError(f"creating temporary checkout: {error}") from error
    try:
        try:
            (owned / ".atom-review-owner").write_text(owner, encoding="ascii")
        except OSError as error:
            raise PullRequestReviewError(f"marking owned checkout {owned}: {error}") from error
        checkout = owned / "repository"
        _run(
            runner,
            ("git", "clone", "--no-checkout", "--no-tags", "--config",
             "core.autocrlf=input", "--", metadata.remote_url, str(checkout)),
            owned, "cloning PR repository", 300.0,
        )
        yield _materialize(checkout, relative_module, metadata, runner)
    finally:
        primary = sys.exc_info()[1]
        try:
            # A target repository can itself contain an importable package named atom.
            _run(
                runner,
                (sys.executable, str(Path(__file__).with_name("_checkout_cleanup.py")),
                 str(owned), owner),
                module_directory, f"cleaning owned checkout (retained path: {owned})", 30.0,
            )
            if os.path.lexists(owned):
                raise PullRequestReviewError(f"cleanup left owned checkout at {owned}")
        except PullRequestReviewError as error:
            if primary is None:
                raise
            # Keep the original exception's type/details and also expose failed cleanup.
            print(f"atom review: {error}", file=sys.stderr)
        except KeyboardInterrupt:
            print(f"atom review: cleanup interrupted; retained checkout: {owned}", file=sys.stderr)
            if primary is not None and not isinstance(primary, KeyboardInterrupt):
                print(f"atom review: original failure: {primary}", file=sys.stderr)
            raise
