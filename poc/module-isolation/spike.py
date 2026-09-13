"""
Atom POC spike: module-isolation

QUESTION
    Does a nested Go module under poc/<slug>/ stay completely invisible to the parent
    module's `go build ./...`, `go vet ./...` and `go test ./...` -- such that a spike
    that does not even compile cannot fail the parent's `atom check`?

This is a THROWAWAY spike. It hardcodes paths, does no error handling, and lets
exceptions surface. Do not promote any of this into the atom package.

Run:  python poc/module-isolation/spike.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# The scenario we build on disk.
#
#   parent/
#     go.mod                 module example.com/parent
#     calc/calc.go           a real package, compiles fine
#     calc/calc_test.go      a real passing test
#     poc/spike/
#       go.mod               module example.com/spike  <-- its own module
#       main.go              DELIBERATELY BROKEN: will not compile
#
# If nesting works the way the docs claim, the broken spike is invisible to every
# parent-level command.
# ---------------------------------------------------------------------------

PARENT_GO_MOD = """module example.com/parent

go 1.21
"""

CALC_GO = """package calc

// Add returns the sum of two integers.
func Add(a, b int) int {
	return a + b
}
"""

CALC_TEST_GO = """package calc

import "testing"

func TestAdd(t *testing.T) {
	if Add(2, 3) != 5 {
		t.Fatal("bad math")
	}
}
"""

SPIKE_GO_MOD = """module example.com/spike

go 1.21
"""

# This is the whole point of the experiment: the spike is garbage.
# Undefined function, unused import, type error -- three separate reasons to fail.
SPIKE_MAIN_GO = """package main

import (
	"fmt"
	"os"
)

func main() {
	var count int = "this is not an int"
	fmt.Println(thisFunctionDoesNotExist(count))
}
"""

# A second, VALID spike, so we can check that a runnable spike is still runnable
# in its own directory while remaining invisible to the parent.
GOOD_SPIKE_GO_MOD = """module example.com/goodspike

go 1.21
"""

GOOD_SPIKE_MAIN_GO = """package main

import "fmt"

func main() {
	fmt.Println("spike-ran-independently=true")
}
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> dict:
    """Run a command and capture everything. No error handling on purpose."""
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=180,
    )
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "exit": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def mentions_poc(result: dict) -> bool:
    """Did any parent-level command leak a reference to the poc/ tree?"""
    blob = (result["stdout"] + result["stderr"]).replace("\\", "/").lower()
    return "poc/" in blob


def main() -> int:
    go = shutil.which("go")
    if go is None:
        print("FATAL: go not on PATH")
        return 2

    workdir = Path(tempfile.mkdtemp(prefix="atom-poc-isolation-"))
    parent = workdir / "parent"

    write(parent / "go.mod", PARENT_GO_MOD)
    write(parent / "calc" / "calc.go", CALC_GO)
    write(parent / "calc" / "calc_test.go", CALC_TEST_GO)
    write(parent / "poc" / "spike" / "go.mod", SPIKE_GO_MOD)
    write(parent / "poc" / "spike" / "main.go", SPIKE_MAIN_GO)
    write(parent / "poc" / "goodspike" / "go.mod", GOOD_SPIKE_GO_MOD)
    write(parent / "poc" / "goodspike" / "main.go", GOOD_SPIKE_MAIN_GO)

    print("=" * 72)
    print("ATOM POC: module-isolation")
    print("=" * 72)
    print(f"scenario built at: {parent}")
    print(run([go, "version"], parent)["stdout"])
    print()

    # --- Control: prove the spike really is broken -------------------------
    print("-- CONTROL: the spike must genuinely fail to compile --")
    control = run([go, "build", "./..."], parent / "poc" / "spike")
    print(f"  cmd={control['cmd']} (in poc/spike) exit={control['exit']}")
    print(f"  stderr: {control['stderr'].splitlines()[0] if control['stderr'] else '(none)'}")
    spike_is_really_broken = control["exit"] != 0
    print(f"  spike_is_really_broken={spike_is_really_broken}")
    print()
    if not spike_is_really_broken:
        print("INVALID EXPERIMENT: the 'broken' spike compiled. Nothing was tested.")
        return 3

    # --- The actual question -----------------------------------------------
    print("-- PARENT COMMANDS with the broken spike present --")
    results = {
        "build": run([go, "build", "./..."], parent),
        "vet": run([go, "vet", "./..."], parent),
        "test": run([go, "test", "./..."], parent),
    }
    for name, res in results.items():
        print(f"  go {name} ./...  exit={res['exit']}  leaked_poc_ref={mentions_poc(res)}")
        for line in (res["stdout"] or res["stderr"]).splitlines():
            print(f"      | {line}")
    print()

    # --- Can a good spike still run on its own? ----------------------------
    print("-- INDEPENDENT SPIKE EXECUTION --")
    good = run([go, "run", "."], parent / "poc" / "goodspike")
    print(f"  cmd={good['cmd']} (in poc/goodspike) exit={good['exit']}")
    print(f"  stdout: {good['stdout']}")
    spike_still_runnable = good["exit"] == 0 and "spike-ran-independently=true" in good["stdout"]
    print(f"  spike_still_runnable={spike_still_runnable}")
    print()

    # --- Verdict ------------------------------------------------------------
    all_parent_clean = all(r["exit"] == 0 for r in results.values())
    no_leaks = not any(mentions_poc(r) for r in results.values())
    confirmed = all_parent_clean and no_leaks and spike_still_runnable

    print("=" * 72)
    print("VERDICT")
    print("=" * 72)
    print(f"  broken spike genuinely broken ........ {spike_is_really_broken}")
    print(f"  parent build/vet/test all exit 0 ..... {all_parent_clean}")
    print(f"  no parent command referenced poc/ .... {no_leaks}")
    print(f"  valid spike still runs standalone .... {spike_still_runnable}")
    print()
    print(f"  RESULT: {'CONFIRMED' if confirmed else 'REFUTED'}")
    print("=" * 72)

    print()
    print("machine-readable:")
    print(json.dumps({
        "confirmed": confirmed,
        "parent_exits": {k: v["exit"] for k, v in results.items()},
        "poc_leak": {k: mentions_poc(v) for k, v in results.items()},
        "spike_runnable": spike_still_runnable,
    }, indent=2))

    shutil.rmtree(workdir, ignore_errors=True)
    return 0 if confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
