"""Throwaway spike: can Python reject a Windows junction escape from specs/?

Disposable. Hardcoded paths, no error handling, prints what it found.

Exit 0 Confirmed / 1 Refuted / 2 Inconclusive.
"""

import os
import stat
import subprocess
import sys
import tempfile

ALLOWED_DIRECTORIES = ("specs", "poc")
ALLOWED_RUNTIME_FILES = (
    os.path.join(".atom", "config.json"),
    os.path.join(".atom", "state.json"),
    os.path.join(".atom", "events.jsonl"),
    os.path.join(".atom", "baseline.json"),
)


def contains_reparse_point(repository, target):
    """Walk every existing component under the repository looking for a link."""
    current = repository
    relative = os.path.relpath(target, repository)
    for component in relative.split(os.sep):
        current = os.path.join(current, component)
        if not os.path.lexists(current):
            return False
        entry = os.lstat(current)
        if stat.S_ISLNK(entry.st_mode):
            return True
        attributes = getattr(entry, "st_file_attributes", 0)
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            return True
    return False


def is_allowed(repository, target):
    repository_real = os.path.realpath(repository)
    target_absolute = target
    if not os.path.isabs(target_absolute):
        target_absolute = os.path.join(repository_real, target_absolute)

    # Check 1: lexical containment after normalisation.
    lexical = os.path.normpath(target_absolute)
    try:
        relative = os.path.relpath(lexical, repository_real)
    except ValueError:
        return False, "different-drive"
    if relative == os.pardir or relative.startswith(os.pardir + os.sep):
        return False, "lexically-outside"

    # Check 2: no symlink or junction anywhere in the path we are about to use.
    if contains_reparse_point(repository_real, lexical):
        return False, "reparse-point-in-path"

    # Check 3: the fully resolved destination is still inside the repository.
    resolved = os.path.realpath(lexical)
    resolved_relative = os.path.relpath(resolved, repository_real)
    if resolved_relative == os.pardir or resolved_relative.startswith(os.pardir + os.sep):
        return False, "resolves-outside"

    # Check 4: the resolved path is in the approved artifact set.
    normalised = os.path.normcase(resolved_relative)
    for allowed_file in ALLOWED_RUNTIME_FILES:
        if normalised == os.path.normcase(allowed_file):
            return True, "allowed-runtime-file"
    head = normalised.split(os.sep)[0]
    for allowed_directory in ALLOWED_DIRECTORIES:
        if head == os.path.normcase(allowed_directory) and os.sep in normalised:
            return True, "allowed-artifact-directory"
    return False, "outside-artifact-set"


def main():
    repository = tempfile.mkdtemp(prefix="atom-guard-repo-")
    outside = tempfile.mkdtemp(prefix="atom-guard-outside-")
    os.makedirs(os.path.join(repository, "specs"), exist_ok=True)

    junction = os.path.join(repository, "specs", "junction-link")
    junction_made = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", junction, outside],
        capture_output=True,
    ).returncode == 0

    symlink = os.path.join(repository, "specs", "symlink-link")
    try:
        os.symlink(outside, symlink, target_is_directory=True)
        symlink_made = True
    except OSError:
        symlink_made = False

    inner = os.path.join(repository, "specs", "inner-link")
    inner_made = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", inner, os.path.join(repository, "specs")],
        capture_output=True,
    ).returncode == 0

    cases = [
        ("specs/demo.md", True),
        ("poc/demo/README.md", True),
        (".atom/config.json", True),
        (".atom/state.json", True),
        (".atom/events.jsonl", True),
        (".atom/baseline.json", True),
        ("specs/nested/deep/report.md", True),
        ("internal/main.go", False),
        (".github/copilot-instructions.md", False),
        (".atom/atom/AGENTS.md", False),
        (".atom/credentials.json", False),
        ("specs/../internal/escape.go", False),
        ("specs", False),
        (os.path.join(outside, "absolute.md"), False),
    ]
    if junction_made:
        cases.append(("specs/junction-link/escaped.md", False))
    if symlink_made:
        cases.append(("specs/symlink-link/escaped.md", False))
    if inner_made:
        # Rejected on purpose: the guard refuses every reparse point, even one
        # that happens to point back inside the repository. Proving a link is
        # benign costs more than it is worth.
        cases.append(("specs/inner-link/inside.md", False))

    failures = 0
    for target, expected in cases:
        allowed, reason = is_allowed(repository, target)
        ok = allowed == expected
        if not ok:
            failures += 1
        print(
            f"target={target!r} expected_allowed={expected} "
            f"actual_allowed={allowed} reason={reason} pass={ok}"
        )

    print(f"junction_created={junction_made}")
    print(f"symlink_created={symlink_made}")
    print(f"inner_junction_created={inner_made}")
    print(f"platform={sys.platform} python={sys.version.split()[0]}")

    if not junction_made:
        print("verdict=INCONCLUSIVE reason=the junction escape case could not be created")
        return 2
    if failures:
        print(f"verdict=REFUTED reason={failures} case(s) produced the wrong decision")
        return 1
    print("verdict=CONFIRMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
