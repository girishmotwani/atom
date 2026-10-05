"""Throwaway probe for the `/atom:<short-skill>` namespace.

Runs the five pre-registered probes in `claims.md` against a fixture plugin
named `atom`, loaded with `copilot --plugin-dir` under an isolated
`COPILOT_HOME` so the installed `atom-go` plugin cannot answer instead.

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
    ("N1", "/atom:poc"),
    ("N2", "/atom"),
    ("N3", "/start"),
    ("N4", "/atom:start"),
    ("N5", "/atom:atom"),
]

TIMEOUT_SECONDS = 180


def run_probe(prompt: str, copilot_home: Path) -> dict:
    environment = dict(os.environ)
    environment["COPILOT_HOME"] = str(copilot_home)
    completed = subprocess.run(
        [
            "copilot",
            "-p",
            prompt,
            "-s",
            "--allow-all-tools",
            "--log-level",
            "none",
            "--plugin-dir",
            str(FIXTURE),
        ],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        shell=True,
        env=environment,
    )
    return {
        "prompt": prompt,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip()[-2000:],
    }


def main() -> int:
    copilot_home = Path(tempfile.mkdtemp(prefix="atom-ns-home-"))
    atexit.register(shutil.rmtree, copilot_home, ignore_errors=True)
    # Authentication is stored in config.json; remove its plugin registrations below.
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

    results = []
    for claim_id, prompt in PROBES:
        print(f"--- {claim_id}: {prompt}", flush=True)
        try:
            outcome = run_probe(prompt, copilot_home)
        except subprocess.TimeoutExpired:
            outcome = {"prompt": prompt, "exit_code": None, "stdout": "", "stderr": "TIMEOUT"}
        outcome["claim"] = claim_id
        results.append(outcome)
        print(json.dumps(outcome, indent=2), flush=True)

    (SPIKE_DIR / "probe-results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
