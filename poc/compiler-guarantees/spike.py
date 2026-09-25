"""Spike: what does the Go toolchain already prove, so a test need not?

The question
------------
Test specs inherited from managed-language frameworks mandate cases like "null
and empty-string tests for every mandatory string parameter". That rule comes
from languages where a string is a reference type and can be null. In Go a
`string` cannot be nil, so half of that rule asks for a test that *cannot be
written*. Atom should not inherit it.

But the useful version of this rule is much narrower than "skip obvious tests",
and getting it wrong is expensive in both directions:

  - Too aggressive, and we delete tests for things that LOOK compiler-checked
    but are not -- a non-exhaustive switch, an ignored error, a typed nil in an
    interface. Those are exactly the bugs Go is famous for.
  - Too timid, and every test spec keeps carrying impossible cases, which
    teaches the reader that the spec is decorative.

So the split we need is three-way, not two-way:

  REJECTED  the compiler refuses it       -> a test is impossible; do not write one
  FLAGGED   it compiles, `go vet` objects -> use the tool in CI, not a unit test
  ACCEPTED  it compiles and vets clean    -> only a test can catch it; WRITE IT

This spike measures which bucket each candidate property falls into, using the
real toolchain, rather than asserting it from memory.

Predictions are recorded BEFORE the run (see `prediction` on each case). A case
whose observed bucket differs from its prediction is the interesting result and
is reported separately -- if everything matches, this spike taught us nothing
new and should say so plainly rather than dressing confirmation up as discovery.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REJECTED = "rejected-by-compiler"
FLAGGED = "flagged-by-vet"
ACCEPTED = "accepted-by-toolchain"


@dataclass
class Case:
    """One candidate property, its prediction, and the Go program that probes it."""

    id: str
    summary: str
    prediction: str
    code: str
    # Whether to also execute the program. Only meaningful for ACCEPTED cases,
    # where the whole point is that the failure is deferred to runtime.
    run: bool = False


@dataclass
class Result:
    case: Case
    observed: str
    build_output: str = ""
    vet_output: str = ""
    run_output: str = ""
    panicked: bool = False
    matched: bool = field(init=False)

    def __post_init__(self) -> None:
        self.matched = self.observed == self.case.prediction


def program(body: str, *, imports: str = "", top: str = "") -> str:
    """Assemble a complete main package so every case compiles in isolation."""
    import_block = f"import (\n{imports}\n)\n" if imports else ""
    return f"package main\n\n{import_block}\n{top}\n\nfunc main() {{\n{body}\n}}\n"


CASES: list[Case] = [
    # ---------------------------------------------------------------- REJECTED
    Case(
        id="nil-to-string",
        summary="Assigning nil to a string variable or parameter",
        prediction=REJECTED,
        code=program("var s string = nil\n\t_ = s"),
    ),
    Case(
        id="wrong-type-argument",
        summary="Passing an int where a string is declared",
        prediction=REJECTED,
        code=program("var s string = 42\n\t_ = s"),
    ),
    Case(
        id="interface-not-satisfied",
        summary="A type missing a method required by an interface it is assigned to",
        prediction=REJECTED,
        code=program(
            "_ = 0",
            top="type Greeter interface{ Greet() string }\ntype Robot struct{}\n\nvar _ Greeter = Robot{}",
        ),
    ),
    Case(
        id="unused-variable",
        summary="A declared local variable that is never used",
        prediction=REJECTED,
        code=program("unused := 42"),
    ),
    Case(
        id="unused-import",
        summary="An imported package that is never referenced",
        prediction=REJECTED,
        code=program("_ = 0", imports='\t"os"'),
    ),
    Case(
        id="missing-return",
        summary="A function with a result type and no return on some path",
        prediction=REJECTED,
        code=program("_ = count()", top="func count() int {\n\tx := 1\n\t_ = x\n}"),
    ),
    Case(
        id="constant-division-by-zero",
        summary="Division by a zero CONSTANT",
        prediction=REJECTED,
        code=program("const x = 1 / 0\n\t_ = x"),
    ),
    Case(
        id="constant-overflow",
        summary="A constant too large for its declared type",
        prediction=REJECTED,
        code=program("var small int8 = 300\n\t_ = small"),
    ),
    Case(
        id="duplicate-map-key",
        summary="A duplicated constant key in a map literal",
        prediction=REJECTED,
        code=program('m := map[string]int{"a": 1, "a": 2}\n\t_ = m'),
    ),
    Case(
        id="constant-index-out-of-range",
        summary="Indexing an array past its end with a CONSTANT index",
        prediction=REJECTED,
        code=program("var a [3]int\n\t_ = a[5]"),
    ),
    Case(
        id="unknown-struct-field",
        summary="Setting a struct field that does not exist",
        prediction=REJECTED,
        code=program('c := Config{Missing: "x"}\n\t_ = c', top="type Config struct{ Name string }"),
    ),
    Case(
        id="unknown-method",
        summary="Calling a method the type does not define",
        prediction=REJECTED,
        code=program("c := Config{}\n\tc.Missing()", top="type Config struct{ Name string }"),
    ),
    # ----------------------------------------------------------------- FLAGGED
    Case(
        id="printf-format-mismatch",
        summary="A Printf verb that does not match its argument type",
        prediction=FLAGGED,
        code=program('fmt.Printf("%d\\n", "not a number")', imports='\t"fmt"'),
    ),
    Case(
        id="lost-cancel",
        summary="Discarding the cancel func returned by context.WithCancel",
        prediction=FLAGGED,
        code=program(
            "ctx, _ := context.WithCancel(context.Background())\n\t_ = ctx",
            imports='\t"context"',
        ),
    ),
    Case(
        id="copy-lock-by-value",
        summary="Passing a struct containing a sync.Mutex by value",
        prediction=FLAGGED,
        code=program(
            "var c Counter\n\t_ = show(c)",
            imports='\t"sync"',
            top="type Counter struct {\n\tmu sync.Mutex\n\tn  int\n}\n\nfunc show(c Counter) int { return c.n }",
        ),
    ),
    # ---------------------------------------------------------------- ACCEPTED
    Case(
        id="nil-map-write",
        summary="Writing to a nil map",
        prediction=ACCEPTED,
        code=program('var m map[string]int\n\tm["a"] = 1'),
        run=True,
    ),
    Case(
        id="nil-pointer-dereference",
        summary="Dereferencing a nil pointer",
        prediction=ACCEPTED,
        code=program("var c *Config\n\tprintln(c.Name)", top="type Config struct{ Name string }"),
        run=True,
    ),
    Case(
        id="typed-nil-in-interface",
        summary="A nil *T stored in an interface is NOT equal to nil",
        prediction=ACCEPTED,
        code=program(
            'if mayFail() != nil {\n\t\tfmt.Println("TYPED NIL IS NOT NIL")\n\t}',
            imports='\t"fmt"',
            top=(
                "type Failure interface{ Error() string }\n"
                "type MyErr struct{}\n\n"
                'func (e *MyErr) Error() string { return "boom" }\n\n'
                "func mayFail() Failure {\n\tvar e *MyErr\n\treturn e\n}"
            ),
        ),
        run=True,
    ),
    Case(
        id="runtime-integer-overflow",
        summary="Incrementing past a type's maximum at RUNTIME (wraps silently)",
        prediction=ACCEPTED,
        code=program(
            'var small int8 = 127\n\tsmall++\n\tfmt.Println("wrapped to", small)',
            imports='\t"fmt"',
        ),
        run=True,
    ),
    Case(
        id="variable-index-out-of-range",
        summary="Indexing a slice past its end with a VARIABLE index",
        prediction=ACCEPTED,
        code=program("s := []int{1, 2, 3}\n\ti := 5\n\t_ = s[i]"),
        run=True,
    ),
    Case(
        id="variable-division-by-zero",
        summary="Dividing by a zero VARIABLE",
        prediction=ACCEPTED,
        code=program("d := 0\n\t_ = 1 / d"),
        run=True,
    ),
    Case(
        id="non-exhaustive-switch",
        summary="A switch over an enum-like const block missing a case",
        prediction=ACCEPTED,
        code=program('fmt.Println("Blue ->", name(Blue))', imports='\t"fmt"', top=(
            "type Colour int\n\n"
            "const (\n\tRed Colour = iota\n\tGreen\n\tBlue\n)\n\n"
            "func name(c Colour) string {\n"
            '\tswitch c {\n\tcase Red:\n\t\treturn "red"\n\tcase Green:\n\t\treturn "green"\n\t}\n'
            '\treturn ""\n}'
        )),
        run=True,
    ),
    Case(
        id="ignored-error-return",
        summary="Calling a function that returns an error and ignoring it entirely",
        prediction=ACCEPTED,
        code=program(
            'save()\n\tfmt.Println("carried on regardless")',
            imports='\t"fmt"',
            top='func save() error { return fmt.Errorf("disk full") }',
        ),
        run=True,
    ),
    Case(
        id="empty-string-argument",
        summary="Passing an empty string where a value is required",
        prediction=ACCEPTED,
        code=program(
            'fmt.Printf("%q\\n", greet(""))',
            imports='\t"fmt"',
            top='func greet(name string) string { return "hello " + name }',
        ),
        run=True,
    ),
]


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=180)


def probe(case: Case, workspace: Path) -> Result:
    """Build, vet, and optionally run one case, and classify what happened."""
    (workspace / "main.go").write_text(case.code, encoding="utf-8")

    build = run_command(["go", "build", "-o", "probe.exe", "."], workspace)
    if build.returncode != 0:
        return Result(case=case, observed=REJECTED, build_output=build.stderr.strip())

    vet = run_command(["go", "vet", "."], workspace)
    if vet.returncode != 0:
        return Result(
            case=case,
            observed=FLAGGED,
            build_output="built cleanly",
            vet_output=vet.stderr.strip(),
        )

    result = Result(
        case=case, observed=ACCEPTED, build_output="built cleanly", vet_output="vet clean"
    )

    if case.run:
        # `go run` flattens exit codes, so the evidence trusted here is a panic
        # in the captured output, not the return code.
        executed = run_command([str(workspace / "probe.exe")], workspace)
        combined = (executed.stdout + executed.stderr).strip()
        result.run_output = combined
        result.panicked = "panic:" in combined

    return result


def main() -> int:
    if shutil.which("go") is None:
        print("go is not on PATH; cannot run this spike")
        return 1

    here = Path(__file__).resolve().parent
    results: list[Result] = []

    with tempfile.TemporaryDirectory() as temporary:
        workspace = Path(temporary)
        init = run_command(["go", "mod", "init", "probe"], workspace)
        if init.returncode != 0:
            print("go mod init failed:", init.stderr)
            return 1

        version = run_command(["go", "version"], workspace).stdout.strip()

        for case in CASES:
            results.append(probe(case, workspace))

    print(f"toolchain: {version}")
    print(f"cases: {len(results)}\n")

    for bucket in (REJECTED, FLAGGED, ACCEPTED):
        chosen = [r for r in results if r.observed == bucket]
        print(f"=== {bucket}  ({len(chosen)}) ===")
        for result in chosen:
            marker = "PANICS" if result.panicked else ("runs ok" if result.case.run else "")
            print(f"  {result.case.id:<32} {marker}")
        print()

    surprises = [r for r in results if not r.matched]
    print(f"=== predictions refuted: {len(surprises)} ===")
    if not surprises:
        print("  none -- every case landed in its predicted bucket.")
        print("  This spike confirmed the split rather than discovering it.")
    for result in surprises:
        print(f"  {result.case.id}: predicted {result.case.prediction}, observed {result.observed}")

    accepted_run = [r for r in results if r.observed == ACCEPTED and r.case.run]
    panicking = [r for r in accepted_run if r.panicked]
    print(f"\naccepted-and-executed: {len(accepted_run)}, of which panic at runtime: {len(panicking)}")
    print("the rest are SILENT failures -- no panic, no diagnostic, wrong answer:")
    for result in accepted_run:
        if not result.panicked:
            first = result.run_output.splitlines()[0] if result.run_output else "(no output)"
            print(f"  {result.case.id:<32} {first}")

    payload = {
        "toolchain": version,
        "cases": [
            {
                "id": r.case.id,
                "summary": r.case.summary,
                "predicted": r.case.prediction,
                "observed": r.observed,
                "matched": r.matched,
                "executed": r.case.run,
                "panicked": r.panicked,
                "build_output": r.build_output,
                "vet_output": r.vet_output,
                "run_output": r.run_output,
            }
            for r in results
        ],
    }
    (here / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {here / 'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
