"""Remove one marked disposable checkout in a separately bounded process."""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path


def _remove(directory: Path, owner: str) -> None:
    attributes = getattr(directory.lstat(), "st_file_attributes", 0)
    if (
        not directory.is_absolute() or not directory.name.startswith("atom-pr-")
        or directory.is_symlink()
        or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    ):
        raise ValueError("refusing an unowned or redirected checkout directory")
    marker = directory / ".atom-review-owner"
    if marker.is_symlink() or marker.read_text(encoding="ascii") != owner:
        raise ValueError("checkout ownership marker does not match")

    def remove_readonly(function, path, error_info):
        if not isinstance(error_info[1], PermissionError):
            raise error_info[1]
        os.chmod(path, os.stat(path).st_mode | stat.S_IWUSR)
        function(path)

    shutil.rmtree(directory, onerror=remove_readonly)


def main() -> int:
    try:
        if len(sys.argv) != 3:
            raise ValueError("expected exact owned directory and ownership marker")
        _remove(Path(sys.argv[1]), sys.argv[2])
    except (OSError, ValueError) as error:
        print(f"checkout cleanup failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
