# Verification

Completion claims require evidence. Evidence means command output captured from
the machine that ran the work.

> Prose is not evidence. A completion claim requires command output.

Atom's pipeline depends on local, inspectable checks: files on disk, commands you
can re-run, and artifacts the developer can inspect.

---

## Evidence Table

| Claim | Required evidence |
|---|---|
| "It builds" | `go build ./...` output showing success or the exact failure |
| "Tests pass" | `go test ./...` output including the package lines and test count where the runner prints it |
| "The POC works" | Verbatim `go run` output, normally captured by `atom poc run <slug>` |
| "No races" | `go test -race ./...` output |
| "Coverage is adequate" | `go test -cover ./...` output with the actual coverage number |
| "It's fast enough" | `go test -bench . -benchmem ./...` output with actual ns/op, B/op, allocs/op, or benchmark-specific numbers |
| "Vet is clean" | `go vet ./...` output; no output with exit code 0 is acceptable when the command is shown |
| "It's formatted" | `gofmt -l <paths>` returning empty output |
| "The edit landed" | A file read, diff, or command output showing the changed lines exist on disk |

If the command does not print a useful success line, show the command and state
that it exited 0. Do not invent output.

---

## `atom check`

`atom check` is the single gate command for normal phase completion.

It runs the checks Atom expects before a code gate:

```bash
atom check
# go build ./...
# go vet ./...
# go test ./...
# go test -race ./...
# go test -cover ./...
# summary printed at the end
```

Use lower-level commands when you are inside the TDD loop and need fast feedback.
Use `atom check` when making a completion claim at a gate.

A good gate cites the exact output:

````text
Verification:

```bash
atom check
build: ok
govet: ok
test: ok  ./...  128 tests
race: ok
coverage: 83.4%
```
````

---

## Paste Output Verbatim

Paste output verbatim.

Do not:

- Summarise.
- Retype from memory.
- Round benchmark or coverage numbers.
- Remove the failing line because it looks noisy.
- Reconstruct what you think the command printed.

If you did not capture it, re-run it.

| Bad | Good |
|---|---|
| "All tests passed." | The exact `go test ./...` output |
| "Coverage is about 80%." | `ok  github.com/example/project/internal/cache  0.421s  coverage: 81.7% of statements` |
| "The POC printed the expected result." | The literal `go run ./poc/codec` output |

---

## Partial Success Is Failure

Partial success is not success.

| Result | Report it as |
|---|---|
| 47 of 48 tests pass | Failing suite |
| Build passes but vet fails | Failing check |
| Race passes for one package only | Partial race evidence |
| POC confirms happy path but crashes on cleanup | Inconclusive unless cleanup is proven out of scope |
| Coverage target met while an error branch is untested | Coverage number met; behavioural gap remains |

Never write "essentially passing". Say what passed, what failed, and what you
will do next.

---

## Negative Results Are Results

A failing check reported honestly is useful. It prevents the developer from
trusting a false claim and gives the next step a clear target.

Example:

````text
Verification failed:

```bash
go test ./internal/cache -run TestStore_ReloadCorruptFile_ReturnsError
--- FAIL: TestStore_ReloadCorruptFile_ReturnsError (0.00s)
    store_test.go:82: got nil error, want corrupt file error
FAIL
FAIL github.com/example/project/internal/cache 0.103s
```

Next step: fix `Store.Reload` to wrap and return the decode error.
````

A negative result is not a reason to hide the run. It is the reason to preserve
it.

---

## Run, Do Not Describe

The specific failure mode is describing what code would do instead of running it.
This sounds technical, but it is not evidence.

Bad:

```text
The parser now returns an error for empty input because the new guard checks
len(input) before decoding.
```

Good:

````text
```bash
go test ./internal/parser -run TestParser_EmptyInput_ReturnsError
ok  github.com/example/project/internal/parser  0.118s
```
````

The bad claim may be true. The good claim is useful because the developer can see
what was run and what happened.

---

## Verify Your Own Edits

Verification applies to file edits too. After editing, confirm the edit landed on
disk rather than assuming the tool wrote what you intended.

Useful checks:

```bash
git diff -- skills/atom/references/verification.md
gofmt -l internal/cache/store.go
go test ./internal/cache -run TestStore_ReloadCorruptFile_ReturnsError
```

For documentation edits, a file read or line count is enough to prove creation.
For code edits, run the smallest relevant command first, then the broader gate
command before claiming completion.

---

## Evidence in Artifacts

POC reports, design gates, TDD summaries, findings, and review notes should carry
verbatim evidence where they make claims.

| Artifact | Evidence to include |
|---|---|
| `poc-report.md` | `atom poc run <slug>` output and verdict |
| `design-spec.md` | Links to the POC report and any measured constraints |
| `test-spec.md` | The behaviours that will be verified |
| TDD gate summary | RED, GREEN, REFACTOR command output where relevant |
| `findings.md` | The command or file evidence that exposed the finding |
| `decisions.md` | The fact, gate, or constraint that justified the decision |

If a claim matters, attach the command output that made you believe it.
