"""
Spike: how does `go run .` behave on a spike that does not work?

THROWAWAY CODE. This is evidence, not a component. It is kept only so the claims in
poc-report.md can be re-verified, and so CI can prove they still hold.

Question
--------
`atom poc run` will shell out to `go run .` inside a nested spike module. The original
module-isolation spike only ever ran `go run .` on a spike that COMPILED. But the normal
state of a spike under development is broken.

If `go run` reports a compile failure differently from `go build` -- or worse, exits 0 --
then `atom poc run` would report a broken spike as a successful one. That is a false
Confirmed verdict, the worst outcome in poc-discipline.md.

Predictions (from poc-brief.md)
-------------------------------
P1  `go run .` on a compile error exits non-zero.
P2  The compile error appears on stderr, not stdout.
P3  A panicking spike also exits non-zero, with the panic on stderr.
P4  A spike writing to both streams has both captured, neither lost.
P5  `go mod init` works offline and pins the full patch version.
P6  (ADDED MID-SPIKE) `go run .` preserves the spike's own exit code.
    P4 incidentally showed a spike calling os.Exit(3) surfacing as exit 1.
    That was not what P4 was testing, so it is promoted to its own
    prediction rather than being mentioned in passing. Atom's POC verdicts
    are three-valued (0/1/2), so this is not a detail -- if it fails, the
    framework itself would launder Inconclusive into Refuted.

Run it
------
    python poc/go-run-failure-modes/spike.py

Exit 0 means every prediction was settled as predicted.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# Spike fixtures. Each is the smallest program that exhibits one failure mode.
# --------------------------------------------------------------------------

PARENT_GO_MOD = "module example.com/parent\n\ngo 1.23\n"

# A deliberate type error: assigning a string to an int.
BROKEN_MAIN = """package main

import "fmt"

func main() {
	var count int = "this is not an int"
	fmt.Println(count)
}
"""

# Compiles cleanly, fails at runtime.
PANICS_MAIN = """package main

func main() {
	var values []int
	_ = values[5]
}
"""

# Writes to BOTH streams, then exits non-zero deliberately.
# The stdout write is the control: if we only ever saw stderr, "stderr was
# captured" would prove nothing about the two streams being kept separate.
NOISY_MAIN = """package main

import (
	"fmt"
	"os"
)

func main() {
	fmt.Fprintln(os.Stdout, "THIS-IS-STDOUT")
	fmt.Fprintln(os.Stderr, "THIS-IS-STDERR")
	os.Exit(3)
}
"""

GENERATED_MAIN = """package main

import "fmt"

func main() {
	fmt.Println("generated spike ran")
}
"""

# Exits with a distinctive code. Used to ask whether the runner preserves it.
EXIT_CODE_MAIN = """package main

import "os"

func main() {
	os.Exit({code})
}
"""


def run(command, working_directory, timeout=180):
    """Run a command, capturing both streams separately. Never raises on failure."""
    completed = subprocess.run(
        command,
        cwd=working_directory,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def show(label, exit_code, stdout, stderr):
    """Print verbatim evidence, so the report can quote rather than summarise."""
    print(f"\n--- {label} ---")
    print(f"exit code : {exit_code}")
    print(f"stdout    : {stdout.strip()!r}")
    stderr_lines = stderr.strip().splitlines()
    if stderr_lines:
        print(f"stderr    : {stderr_lines[0]!r}")
        for line in stderr_lines[1:4]:
            print(f"            {line!r}")
    else:
        print("stderr    : '' (EMPTY)")


def main() -> int:
    go = shutil.which("go")
    if not go:
        print("FATAL: go not found on PATH. Cannot answer the question.")
        return 2

    _, version_out, _ = run([go, "version"], Path.cwd())
    print(f"toolchain : {version_out.strip()}")

    workspace = Path(tempfile.mkdtemp(prefix="atom-poc-run-spike-"))
    results = {}

    try:
        parent = workspace / "parent"
        write(parent / "go.mod", PARENT_GO_MOD)
        write(parent / "main.go", "package main\n\nfunc main() {}\n")

        # Three hand-written spikes, each with its own go.mod so it stays
        # isolated from the parent -- the invariant the first spike proved.
        for slug, source in (
            ("broken", BROKEN_MAIN),
            ("panics", PANICS_MAIN),
            ("noisy", NOISY_MAIN),
        ):
            write(parent / "poc" / slug / "go.mod", f"module example.com/{slug}\n\ngo 1.23\n")
            write(parent / "poc" / slug / "main.go", source)

        # ------------------------------------------------------------------
        # P1 + P2 -- a spike that does not compile
        # ------------------------------------------------------------------
        code, out, err = run([go, "run", "."], parent / "poc" / "broken")
        show("P1/P2  go run .  on a COMPILE ERROR", code, out, err)
        results["P1"] = code != 0
        results["P2"] = "not an int" in err or "cannot use" in err.lower()

        # ------------------------------------------------------------------
        # P3 -- a spike that compiles but panics
        # ------------------------------------------------------------------
        code, out, err = run([go, "run", "."], parent / "poc" / "panics")
        show("P3     go run .  on a RUNTIME PANIC", code, out, err)
        results["P3"] = code != 0 and "panic" in err.lower()

        # ------------------------------------------------------------------
        # P4 -- both streams preserved, with stdout as the control
        # ------------------------------------------------------------------
        code, out, err = run([go, "run", "."], parent / "poc" / "noisy")
        show("P4     go run .  writing to BOTH streams", code, out, err)
        stdout_captured = "THIS-IS-STDOUT" in out
        stderr_captured = "THIS-IS-STDERR" in err
        streams_not_crossed = "THIS-IS-STDERR" not in out and "THIS-IS-STDOUT" not in err
        results["P4"] = stdout_captured and stderr_captured and streams_not_crossed
        print(f"  stdout captured: {stdout_captured}   stderr captured: {stderr_captured}")
        print(f"  streams kept separate: {streams_not_crossed}   exit code preserved: {code == 3}")

        # ------------------------------------------------------------------
        # P5 -- go mod init rather than a hand-written template
        # ------------------------------------------------------------------
        generated = parent / "poc" / "generated"
        generated.mkdir(parents=True, exist_ok=True)
        init_code, _, _ = run([go, "mod", "init", "example.com/generated"], generated)
        go_mod_path = generated / "go.mod"
        go_mod_text = go_mod_path.read_text(encoding="utf-8") if go_mod_path.exists() else ""
        write(generated / "main.go", GENERATED_MAIN)
        gen_code, gen_out, _ = run([go, "run", "."], generated)

        print("\n--- P5     go mod init ---")
        print(f"init exit : {init_code}")
        print(f"go.mod    : {go_mod_text.strip()!r}")
        print(f"then ran  : exit={gen_code} stdout={gen_out.strip()!r}")
        results["P5"] = init_code == 0 and "module example.com/generated" in go_mod_text and gen_code == 0

        # Is the pinned version a full patch version, or just major.minor?
        pinned = [ln.strip() for ln in go_mod_text.splitlines() if ln.strip().startswith("go ")]
        pinned_version = pinned[0][3:] if pinned else ""
        print(f"pinned    : {pinned_version!r}  (full patch version: {pinned_version.count('.') >= 2})")

        # ------------------------------------------------------------------
        # P6 -- does the runner preserve the spike's OWN exit code?
        #
        # This is the prediction that matters most. Atom POC verdicts are
        # three-valued: 0 = Confirmed, 1 = Refuted, 2 = Inconclusive. If the
        # runner flattens 2 to 1, Atom reports "Refuted" for a spike that
        # actually said "Inconclusive" -- the precise failure mode that
        # poc-discipline.md forbids, committed by the tool rather than the
        # developer.
        #
        # Compare two ways of running the same program: `go run .` versus
        # `go build` followed by executing the binary directly.
        # ------------------------------------------------------------------
        exit_probe = parent / "poc" / "exitcode"
        write(exit_probe / "go.mod", "module example.com/exitcode\n\ngo 1.23\n")

        print("\n--- P6     is the spike's own exit code preserved? ---")
        print(f"{'spike exits':<14}{'via go run .':<16}{'via built binary':<18}")
        binary_name = "spike.exe" if sys.platform == "win32" else "spike"
        exit_code_rows = []

        for wanted in (0, 1, 2, 3, 42):
            write(exit_probe / "main.go", EXIT_CODE_MAIN.replace("{code}", str(wanted)))

            via_go_run, _, _ = run([go, "run", "."], exit_probe)

            build_code, _, _ = run([go, "build", "-o", binary_name, "."], exit_probe)
            if build_code == 0:
                via_binary, _, _ = run([str(exit_probe / binary_name)], exit_probe)
            else:
                via_binary = None

            exit_code_rows.append((wanted, via_go_run, via_binary))
            print(f"{wanted:<14}{via_go_run:<16}{via_binary}")

        go_run_preserves = all(actual == wanted for wanted, actual, _ in exit_code_rows)
        binary_preserves = all(actual == wanted for wanted, _, actual in exit_code_rows)

        # P6 as originally written predicted `go run` WOULD preserve the code.
        # It does not. The prediction is recorded as REFUTED, and what this
        # check now locks in is the CORRECTED understanding -- so CI keeps
        # verifying the fact the design actually rests on, rather than a
        # prediction we already know to be wrong.
        results["P6 (as predicted)"] = go_run_preserves
        results["P6 (corrected)"] = (not go_run_preserves) and binary_preserves

        print(f"\n  go run .      preserves exit codes: {go_run_preserves}")
        print(f"  built binary  preserves exit codes: {binary_preserves}")
        if not go_run_preserves and binary_preserves:
            print("  => P6 REFUTED. `go run` is UNSAFE for three-valued POC verdicts.")
            print("     `atom poc run` must build, then execute the binary.")

        # ------------------------------------------------------------------
        # The isolation invariant must STILL hold with all the spikes present.
        # ------------------------------------------------------------------
        parent_build = run([go, "build", "./..."], parent)
        parent_vet = run([go, "vet", "./..."], parent)
        print("\n--- INVARIANT  parent unaffected by 4 spikes, 3 of them broken ---")
        print(f"parent go build ./... : exit={parent_build[0]}  stderr={parent_build[2].strip()!r}")
        print(f"parent go vet   ./... : exit={parent_vet[0]}  stderr={parent_vet[2].strip()!r}")
        results["ISOLATION"] = parent_build[0] == 0 and parent_vet[0] == 0

        # ------------------------------------------------------------------
        # Verdict
        # ------------------------------------------------------------------
        print("\n" + "=" * 62)
        print("VERDICT")
        print("=" * 62)
        for name, settled in results.items():
            print(f"  {name:<22} {'CONFIRMED' if settled else 'REFUTED'}")

        # One prediction is knowingly recorded as REFUTED. The spike still
        # exits 0, because a refutation IS a result -- what would make this
        # spike fail is the evidence no longer matching the report.
        expected_refutations = {"P6 (as predicted)"}
        unexpected = [
            name for name, settled in results.items()
            if not settled and name not in expected_refutations
        ]
        missing_refutation = [
            name for name in expected_refutations if results.get(name) is True
        ]

        if not unexpected and not missing_refutation:
            print("\nEvidence matches poc-report.md.")
            print("P1-P5 confirmed. P6 refuted -- `go run` flattens every non-zero")
            print("exit code to 1, so `atom poc run` MUST build then execute the")
            print("binary. A spike's Inconclusive verdict would otherwise be")
            print("reported by Atom itself as Refuted.")
            return 0

        if missing_refutation:
            print(f"\nSTALE REPORT: {missing_refutation} now confirms but the report")
            print("records it as refuted. Go's behaviour changed. Re-read the report.")
        if unexpected:
            print(f"\nUNEXPECTED REFUTATION: {unexpected}")
            print("The Phase 2 design must account for this before any code is written.")
        return 1

    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
