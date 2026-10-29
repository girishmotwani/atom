Publication redaction: local Windows profile prefixes in this historical evidence were replaced with <LOCAL_PROFILE>. Original evidence remains private; this copy is not byte-identical to the captured transcript.

# Repeat-init POC Report

## Question

Does the current init guard reject a valid repeat call while allowing a partial initialization to be rewritten?

## Verdict: Confirmed

Both valid repeats exited 2 while preserving all 56 snapshot entries and one approval. Missing either config.json or state.json bypassed the guard: init exited 0 and rewrote six paths, including configuration, state, baseline, and events. With config missing, the retained approval was erased.

## Reproduction

Run `python poc\repeat-init\probe.py` from the Atom checkout with the editable Python package installed. The driver uses real public CLI subprocesses and automatically removes temporary modules. The developer approved this reproduction and the Python-tooling deviation in conversation.

## Evidence

Command: `python poc\repeat-init\probe.py` (driver exit 0).

```text
CASE: first initialization
COMMAND: python -m atom.cli init
EXIT: 0
STDOUT:
Initialised <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\.atom
  module:    example.com/repeat-init
  approvals: 0
  local instructions: <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\.github\copilot-instructions.md
  specs:     <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\specs
  poc:       <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\poc
  build:     go build ./...
  test:      go test ./...
             no makefile; using Go defaults
  baseline:  <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\.atom\baseline.json

Untouched baseline (race detector skipped):
atom check <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete

  PASS  build  go build ./... passed (0.5s)
  PASS  vet    go vet ./... passed (50.1s)
  PASS  fmt    1 file(s) differ only in line endings, not formatting: target.go. gofmt expects LF; set core.autocrlf=input or commit a .gitattributes entry to stop the checkout rewriting them. (0.1s)
  SKIP  test   No packages contain test files (3.2s)
  SKIP  race   Race detector disabled for this run (0.0s)

  PASSED in 53.9s

Atom derives where you are from specs/. To see it:
  atom status

Atom starts by proving things, not describing them:
  atom poc new <slug> --question "..."
STDERR:

CASE: valid repeat 1
COMMAND: python -m atom.cli init
EXIT: 2
STDOUT:

STDERR:
atom init: <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\.atom already exists.
Re-initialising would discard the phase this project has reached.
Pass --force if that is genuinely what you want.
SNAPSHOT entries=56 unchanged=True
CHANGED: []
APPROVALS: 1
CASE: valid repeat 2
COMMAND: python -m atom.cli init
EXIT: 2
STDOUT:

STDERR:
atom init: <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\complete\.atom already exists.
Re-initialising would discard the phase this project has reached.
Pass --force if that is genuinely what you want.
SNAPSHOT entries=56 unchanged=True
CHANGED: []
APPROVALS: 1
CASE: missing config.json
COMMAND: python -m atom.cli init
EXIT: 0
STDOUT:
Initialised <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-config.json\.atom
  module:    example.com/repeat-init
  approvals: 0
  local instructions: <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-config.json\.github\copilot-instructions.md
  specs:     <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-config.json\specs
  poc:       <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-config.json\poc
  build:     go build ./...
  test:      go test ./...
             no makefile; using Go defaults
  baseline:  <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-config.json\.atom\baseline.json

Untouched baseline (race detector skipped):
atom check <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-config.json

  PASS  build  go build ./... passed (0.3s)
  PASS  vet    go vet ./... passed (5.1s)
  PASS  fmt    1 file(s) differ only in line endings, not formatting: target.go. gofmt expects LF; set core.autocrlf=input or commit a .gitattributes entry to stop the checkout rewriting them. (0.1s)
  SKIP  test   No packages contain test files (3.8s)
  SKIP  race   Race detector disabled for this run (0.0s)

  PASSED in 9.3s

Atom derives where you are from specs/. To see it:
  atom status

Atom starts by proving things, not describing them:
  atom poc new <slug> --question "..."
STDERR:

SNAPSHOT entries=55 unchanged=False
CHANGED: ['.atom', '.atom\atom\manifest.json', '.atom\baseline.json', '.atom\config.json', '.atom\events.jsonl', '.atom\state.json']
APPROVALS: 0
CASE: missing state.json
COMMAND: python -m atom.cli init
EXIT: 0
STDOUT:
Initialised <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-state.json\.atom
  module:    example.com/repeat-init
  approvals: 0
  local instructions: <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-state.json\.github\copilot-instructions.md
  specs:     <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-state.json\specs
  poc:       <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-state.json\poc
  build:     go build ./...
  test:      go test ./...
             no makefile; using Go defaults
  baseline:  <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-state.json\.atom\baseline.json

Untouched baseline (race detector skipped):
atom check <LOCAL_PROFILE>\AppData\Local\Temp\atom-repeat-init-g25lrr_x\missing-state.json

  PASS  build  go build ./... passed (0.3s)
  PASS  vet    go vet ./... passed (2.8s)
  PASS  fmt    1 file(s) differ only in line endings, not formatting: target.go. gofmt expects LF; set core.autocrlf=input or commit a .gitattributes entry to stop the checkout rewriting them. (0.0s)
  SKIP  test   No packages contain test files (3.1s)
  SKIP  race   Race detector disabled for this run (0.0s)

  PASSED in 6.3s

Atom derives where you are from specs/. To see it:
  atom status

Atom starts by proving things, not describing them:
  atom poc new <slug> --question "..."
STDERR:

SNAPSHOT entries=55 unchanged=False
CHANGED: ['.atom', '.atom\atom\manifest.json', '.atom\baseline.json', '.atom\config.json', '.atom\events.jsonl', '.atom\state.json']
APPROVALS: 0
```

## Plan impact

Replace the existence-only guard with a read-only validation path for existing onboarding. Do not treat a partial record as a new project. The design must distinguish shared scaffold from optional machine-local runtime data. The repeat path must run before build detection, baseline checks, or any writer. Keep explicit --force semantics.

## Explicitly not covered

No production fix has been implemented. This proves current sequential behavior, not a future validator, every corrupt shape, concurrency safety, or performance. Final regression tests must cover the approved validation boundary. The generated module has no test files; this experiment does not claim Go application test coverage.
