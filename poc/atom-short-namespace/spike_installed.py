"""Second probe: does the plugin-name/command-name collision bite on the real
install path?

`spike.py` loaded the fixture with `--plugin-dir`. Atom actually ships through
a marketplace entry, and `poc/copilot-plugin-surface/results.md` recorded that
an *installed* plugin shadows a command of the same name. This probe repeats
the `/atom` probe against an installed plugin so the two paths are compared
rather than assumed equivalent.

Disposable. Not part of the `atom` package.
"""

import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
FIXTURE = SPIKE_DIR / "fixture"

PROBES = [
    ("N1-installed", "/atom:poc"),
    ("N2-installed", "/atom"),
    ("N3-installed", "/start"),
]

TIMEOUT_SECONDS = 180


def copilot(arguments: list[str], copilot_home: Path) -> subprocess.CompletedProcess:
    environment = dict(os.environ)
    environment["COPILOT_HOME"] = str(copilot_home)
    return subprocess.run(
        ["copilot.cmd", *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=TIMEOUT_SECONDS,
        shell=False,
        env=environment,
    )


def main() -> int:
    copilot_home = Path(tempfile.mkdtemp(prefix="atom-ns-install-home-"))
    atexit.register(shutil.rmtree, copilot_home, ignore_errors=True)
    real_home = Path(os.environ.get("USERPROFILE", "")) / ".copilot"
    for name in ("github-copilot-apps.json", "config.json", "hosts.json"):
        source = real_home / name
        if source.is_file():
            shutil.copy2(source, copilot_home / name)
    config_file = copilot_home / "config.json"
    config_text = "\n".join(
        line
        for line in config_file.read_text(encoding="utf-8-sig").splitlines()
        if not line.lstrip().startswith("//")
    )
    config = json.loads(config_text)
    config["installedPlugins"] = []
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    marketplace_root = Path(tempfile.mkdtemp(prefix="atom-ns-market-"))
    atexit.register(shutil.rmtree, marketplace_root, ignore_errors=True)
    # The source must be inside the marketplace directory or installation rejects it.
    plugin_copy = marketplace_root / "atom"
    shutil.copytree(FIXTURE, plugin_copy)
    marketplace_file = marketplace_root / ".github" / "plugin" / "marketplace.json"
    marketplace_file.parent.mkdir(parents=True, exist_ok=True)
    marketplace_file.write_text(
        json.dumps(
            {
                "name": "atom-ns-probe",
                "owner": {"name": "Atom"},
                "metadata": {"description": "namespace probe", "version": "0.0.1"},
                "plugins": [
                    {
                        "name": "atom",
                        "description": "namespace probe",
                        "version": "0.0.1",
                        "source": str(plugin_copy),
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    setup = {}
    steps = [
        (
            "marketplace add",
            ["plugin", "marketplace", "add", str(marketplace_root)],
        ),
        ("install", ["plugin", "install", "atom@atom-ns-probe"]),
        ("list", ["plugin", "list"]),
    ]
    for label, arguments in steps:
        print(f"--- starting {label}", flush=True)
        completed = copilot(arguments, copilot_home)
        setup[label] = {
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip()[-2000:],
            "stderr": completed.stderr.strip()[-2000:],
        }
        print(f"--- {label}\n{json.dumps(setup[label], indent=2)}", flush=True)

    if setup["install"]["exit_code"] != 0 or "atom-go@atom" in setup["list"]["stdout"]:
        (SPIKE_DIR / "installed-probe-results.json").write_text(
            json.dumps({"setup": setup, "probes": []}, indent=2), encoding="utf-8"
        )
        return 1

    results = []
    for claim_id, prompt in PROBES:
        print(f"--- {claim_id}: {prompt}", flush=True)
        completed = copilot(
            ["-p", prompt, "-s", "--allow-all-tools", "--log-level", "none"],
            copilot_home,
        )
        outcome = {
            "claim": claim_id,
            "prompt": prompt,
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip()[-2000:],
        }
        results.append(outcome)
        print(json.dumps(outcome, indent=2), flush=True)

    (SPIKE_DIR / "installed-probe-results.json").write_text(
        json.dumps({"setup": setup, "probes": results}, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
