"""Make installed Atom commands usable without changing a project's state."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import ntpath
from pathlib import Path
import sys
import sysconfig


class PathSetupError(RuntimeError):
    """Explain why command setup could not establish a usable user PATH."""


@dataclass(frozen=True)
class PathSetupResult:
    """Keep the current session usable even when its inherited PATH is stale."""

    scripts_directory: Path
    changed: bool


def setup_user_path() -> PathSetupResult:
    """Persist the installed command directory only after an explicit opt-in."""

    if sys.platform != "win32":
        raise PathSetupError(
            "automatic user-PATH setup is Windows-only. Activate the intended "
            "Python environment or configure its command directory in your shell."
        )
    try:
        scripts = _find_scripts_directory()
    except OSError as error:
        raise PathSetupError(f"could not locate installed commands: {error}") from error
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", access=winreg.KEY_QUERY_VALUE
        ) as key:
            original, value_type = winreg.QueryValueEx(key, "Path")
    except FileNotFoundError:
        original, value_type = "", winreg.REG_EXPAND_SZ
    except OSError as error:
        raise PathSetupError(f"could not read user PATH: {error}") from error
    if value_type not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ) or not isinstance(
        original, str
    ):
        raise PathSetupError(
            "the current user's Path must be a REG_SZ or REG_EXPAND_SZ string; "
            "no settings were changed."
        )
    present = any(
        entry.strip() and _normalized_directory(entry) == _normalized_directory(str(scripts))
        for entry in original.split(";")
    )
    if not present:
        updated = original + (";" if original else "") + str(scripts)
        if len((updated + "\0").encode("utf-16-le", errors="surrogatepass")) // 2 > 32767:
            raise PathSetupError(
                "adding the command directory would exceed the Windows "
                "32,767-character PATH limit; no settings were changed."
            )
        try:
            with winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, "Environment", access=winreg.KEY_SET_VALUE
            ) as key:
                winreg.SetValueEx(key, "Path", 0, value_type, updated)
        except OSError as error:
            raise PathSetupError(f"could not write user PATH: {error}") from error
    try:
        _notify_environment_change()
    except OSError as error:
        state = "already present" if present else "saved"
        raise PathSetupError(
            f"user PATH is {state}, but could not notify Windows: {error}. "
            "Use the absolute executable paths or sign out and back in "
            "before relying on command names."
        ) from error
    return PathSetupResult(scripts_directory=scripts, changed=not present)


def _normalized_directory(entry: str) -> str:
    return ntpath.normcase(ntpath.normpath(ntpath.expandvars(entry.strip().strip('"'))))


def _find_scripts_directory() -> Path:
    candidates = (
        sysconfig.get_path("scripts"),
        sysconfig.get_path(
            "scripts", scheme=sysconfig.get_preferred_scheme("user")
        ),
    )
    for directory in dict.fromkeys(candidates):
        if ";" in directory or "\0" in directory:
            raise PathSetupError(
                "Python's Scripts directory contains a PATH delimiter or NUL; "
                "no settings were changed."
            )
        scripts = Path(directory).absolute()
        if all(
            (scripts / name).is_file()
            for name in ("atom.exe", "atom-write-artifact.exe")
        ):
            return scripts
    raise PathSetupError(
        "could not find both atom.exe and atom-write-artifact.exe in this "
        "Python environment's Scripts directories. Repair its console-script "
        "installation, then run `python -m atom.cli setup-path` again."
    )


def _notify_environment_change() -> None:
    broadcast = ctypes.WinDLL("user32", use_last_error=True).SendMessageTimeoutW
    broadcast.argtypes = (
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(ctypes.c_size_t),
    )
    broadcast.restype = ctypes.c_ssize_t
    environment = ctypes.create_unicode_buffer("Environment")
    result = ctypes.c_size_t()
    notified = broadcast(
        0xFFFF,
        0x001A,
        0,
        ctypes.cast(environment, ctypes.c_void_p).value,
        0x0002,
        5000,
        ctypes.byref(result),
    )
    if not notified:
        raise OSError("environment-change broadcast failed or timed out")
