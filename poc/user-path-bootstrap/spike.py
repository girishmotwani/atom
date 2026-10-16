"""Throwaway proof of Windows PATH preservation and installed-script discovery."""

import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import tempfile
import uuid
import winreg


QUESTION = (
    "Can Python preserve a Windows user PATH while adding the installed Atom "
    "console-script directory exactly once, and run both entry points from a "
    "process whose inherited PATH does not contain that directory?"
)


def read_registry_path(root, name):
    with winreg.OpenKey(root, name) as key:
        try:
            return winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            return None


def equivalent(entry):
    return os.path.normcase(os.path.normpath(os.path.expandvars(entry.strip().strip('"'))))


def append_once(original, directory):
    if any(entry and equivalent(entry) == equivalent(directory) for entry in original.split(";")):
        return original
    return original + (";" if original else "") + directory


def main():
    print(QUESTION)
    schemes = [sysconfig.get_default_scheme(), sysconfig.get_preferred_scheme("user")]
    directories = list(dict.fromkeys(sysconfig.get_path("scripts", scheme=scheme) for scheme in schemes))
    candidates = [
        Path(directory)
        for directory in directories
        if all((Path(directory) / executable).is_file() for executable in ("atom.exe", "atom-write-artifact.exe"))
    ]
    assert candidates, "No Python Scripts directory contains both entry points"
    scripts = str(candidates[0])
    print(f"Script discovery: both entry points found; schemes inspected={len(directories)}")

    user_before = read_registry_path(winreg.HKEY_CURRENT_USER, "Environment")
    system_key = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    system_before = read_registry_path(winreg.HKEY_LOCAL_MACHINE, system_key)
    process_before = os.environ.get("PATH")
    test_key = rf"Software\AtomPathPoc-{uuid.uuid4()}"
    original = ";".join([r"%SystemRoot%\System32", '"C:\\Folder With Spaces\\bin"', ""] + [rf"C:\existing\directory-{index:03d}" for index in range(80)]) + ";"
    assert len(original) > 1024

    try:
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, test_key, access=winreg.KEY_ALL_ACCESS) as key:
            for value_type in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
                winreg.SetValueEx(key, "Path", 0, value_type, original)
                value, actual_type = winreg.QueryValueEx(key, "Path")
                updated = append_once(value, scripts)
                winreg.SetValueEx(key, "Path", 0, actual_type, updated)
                saved, saved_type = winreg.QueryValueEx(key, "Path")
                assert saved == original + ";" + scripts
                assert saved.startswith(original)
                assert saved_type == value_type
                assert "%SystemRoot%" in saved
                assert append_once(saved, scripts) == saved
                print(f"Registry append: type={value_type}; original_chars={len(original)}; preserved=True; idempotent=True")

            duplicate_forms = [scripts.upper(), scripts + "\\", '"' + scripts + '"', scripts + os.sep + "." + os.sep]
            for entry in duplicate_forms:
                value = original + ";" + entry
                assert append_once(value, scripts) == value
            assert append_once("", scripts) == scripts
            print(f"Equivalent existing entries: {len(duplicate_forms)} passed; empty PATH passed")
    finally:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, test_key)
    print("Temporary registry key: removed")

    with tempfile.TemporaryDirectory(prefix="atom-path-poc-") as directory:
        environment = dict(os.environ, PATH="")
        for name in ("atom.exe", "atom-write-artifact.exe"):
            process = subprocess.run([str(Path(scripts) / name), "--help"], cwd=directory, env=environment, capture_output=True, text=True, timeout=30)
            assert process.returncode == 0, (name, process.stdout, process.stderr)
            print(f"Absolute executable with empty child PATH: {name}; exit={process.returncode}; {process.stdout.splitlines()[0]}")

    assert read_registry_path(winreg.HKEY_CURRENT_USER, "Environment") == user_before
    assert read_registry_path(winreg.HKEY_LOCAL_MACHINE, system_key) == system_before
    assert os.environ.get("PATH") == process_before
    print("Real user PATH unchanged=True; system PATH unchanged=True; parent-process PATH unchanged=True")
    print("Verdict: Confirmed for registry preservation and absolute executable invocation; Copilot prompt count not measured")


if __name__ == "__main__":
    main()
