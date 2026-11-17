# Try Atom with one Go POC

Ask Atom for a disposable expense-summary command, inspect real totals and input
failures, then stop. No repository onboarding or full-project pipeline is needed.

## Before you start

These are **Ubuntu/Linux Bash terminal commands**, not PowerShell commands.
The observed run used existing Ubuntu WSL, Copilot CLI 1.0.107, Go 1.22.2,
Python 3.12.3 with venv, and git 2.43.0. Have those tools and ordinary Copilot
authentication available already; this page does not install prerequisites.
Other setups should use the [general setup guidance](../README.md#getting-started);
documented minima are not a tested compatibility matrix.

The plugin supplies instructions; the separate Python package supplies `atom`
and `atom-write-artifact`. Below is a deliberately separate trial installation,
not a repair or replacement of healthy tools. It uses a fresh profile and venv,
but **shares the existing CLI cache**. No shell profile, default Copilot profile,
global PATH, HOME, or credentials should be changed or copied.

The replay used atom-cli 0.1.0 and plugin 0.2.0, matching public source
`5bb33cbe2c835382b5ccda840c5268321b24ac0b`. Python is pinned below; the marketplace
can advance, so a plugin version alone does not guarantee those same bytes.
The no-auto-update controls prevent CLI updates; do not infer that the observed
older client also prevents plugin updates.

## Set up in a dedicated terminal

Use a new terminal solely for this trial. Paste the complete block, including
the parentheses: setup and Copilot run in a subshell, so failure returns to your
terminal without closing its shell or changing its settings. The directory name
is reader-owned: choose an unused name, and never run two trials against the same
directory. The checks refuse existing destinations, including dangling symlinks.

```bash
(
  set -e
  trial="$HOME/atom-quickstart"
  for destination in "$trial" "$trial/workspace" "$trial/profile" "$trial/tmp" "$trial/venv"; do
    if [ -e "$destination" ] || [ -L "$destination" ]; then
      printf 'Destination already exists; stop: %s\n' "$destination" >&2
      exit 1
    fi
  done
  if ! copilot_bin="$(type -P copilot)"; then
    printf 'Copilot executable not found on PATH; stop.\n' >&2
    exit 1
  fi
  if ! copilot_bin="$(readlink -f "$copilot_bin")" || ! test -x "$copilot_bin"; then
    printf 'Cannot resolve an executable Copilot; stop.\n' >&2
    exit 1
  fi
  "$copilot_bin" --no-auto-update --version
  go version
  python3 --version
  git --version
  umask 077
  mkdir "$trial"
  mkdir "$trial/workspace" "$trial/profile" "$trial/tmp"
  export TMPDIR="$trial/tmp"
  python3 -m venv "$trial/venv"
  "$trial/venv/bin/python" -m pip install --no-cache-dir "git+https://github.com/girishmotwani/atom.git@5bb33cbe2c835382b5ccda840c5268321b24ac0b#subdirectory=tools"
  export PATH="$trial/venv/bin:$PATH"
  export COPILOT_HOME="$trial/profile"
  export COPILOT_AUTO_UPDATE=false
  cd "$trial/workspace"
  "$copilot_bin" --no-auto-update plugin marketplace add girishmotwani/atom
  "$copilot_bin" --no-auto-update plugin install atom@atom
  atom --help
  atom-write-artifact --help
  "$copilot_bin" --no-auto-update
)
```

Both Atom help commands must succeed before starting the task. If any command
fails, authentication is unavailable, or installation needs more permissions,
keep the actual diagnostic and **stop**. Do not retry automatically, use sudo,
override system pip, install another interpreter, log in, or copy credentials.
The existing supported client must accept the flags shown.

## Ask for the experiment

In the interactive Copilot session just opened, send:

```text
/atom:poc I want one standalone disposable expense-summary Go POC, not a production feature or the full Atom pipeline. Prepare its brief and stop for my approval before coding. The question is: Can a Go command read the supplied expense CSV, print exact category totals including the negative refund, and reject invalid amounts and missing files with a nonzero exit and no success totals?

Read a UTF-8 CSV with header category,amount and these rows:
food,12.50
travel,5.00
food,7.50
travel,-1.25

Expected totals: food 20.00; travel 3.75. Replace the final row's amount with oops for the invalid-input fixture. That input and a missing file must each visibly fail with a nonzero Go process exit and no success totals. Capture exact stdout, stderr and exits, including atom poc run vet/build/run evidence and direct Go-command negative checks.

Keep this to one disposable POC under poc/expense-summary and its brief/report/findings/decisions. Use the existing Atom tools on PATH and existing Go/Python. Preserve the brief/report approval pauses. No init/start/build, phase registration, phase plan, design spec, TDD cycle, extra agents, tool installation, model review, commit, push or publication. Stop at the POC report gate.
```

The POC skill may first use discovery solely to prepare its missing brief. That
is not project onboarding. If the command is unknown, stop and check the active
client; do not guess aliases, reinstall, or edit installed skills.

An empty workspace has no root `go.mod`; a root baseline probe may fail for that
reason. Record it honestly, not as a green baseline. Do not initialize a project
or phase state to silence it: the POC gets its own separate Go module.

## Approve, continue, then stop

**Tool permissions are not artifact approvals.** Approve only displayed commands
and paths you understand. No all-tools, unrestricted-path, or persistent grant
is required. Expected scoped actions include `atom poc new expense-summary` and
`atom poc run expense-summary`, with their displayed question/capture options;
inspect the full commands before approving them. This is not blanket approval
for every `atom` action. Limit artifact-writing permission to
`atom-write-artifact` and the intended artifact paths; source edits retain normal
permissions.
Unexpected setup, broad access, or unrelated lifecycle work is a stop condition,
not a reason to bypass a gate.

Read `specs/expense-summary/poc-brief.md`. It must match the question, fixture,
exact totals, both failure cases, evidence requirements, and disposable scope.
Reject or request correction if it does not. Approve only that brief if it does.
Then send this explicit continuation **in the same session**:

```text
Proceed with specs/expense-summary/poc-brief.md as approved. Scaffold, write and execute the disposable POC, capture all required evidence, and write the report. Stop at the report approval gate.
```

At that gate, read `specs/expense-summary/poc-report.md` and the captured evidence.
Accept or reject the report explicitly; acceptance does **not** authorize planning,
design, TDD, review, shipping, or production code. End this standalone task there.
If the agent continues outside that scope, stop it rather than treating written
instructions as a technical guarantee that a model always waits.

## Inspect the result

Under your trial's `workspace`, inspect `poc/expense-summary/main.go`, its `go.mod`,
`expenses.csv`, `invalid.csv`, and rerun `README.md`. The brief, report,
`findings.md`, and `decisions.md` live under `specs/expense-summary`.
The observed Atom vet/build/execute stages all exited 0. Success stdout was:

```text
food 20.00
travel 3.75
```

The direct executable exited 0 with empty stderr. To rerun after the report gate,
leave Copilot and change into your trial's `workspace/poc/expense-summary` in
your original terminal. The subshell has not enabled `set -e` there. Run these
observed commands individually; immediately after each, use
`printf 'exit=%s\n' "$?"` to see its exit:

```bash
go build -o expense-summary .
./expense-summary expenses.csv
./expense-summary invalid.csv
./expense-summary missing.csv
```

The last two are **expected to exit 1**, with empty stdout, not setup failures.
The report contains separate captured exits and streams. Observed
direct-executable stderr examples, one per failing command:

```text
reading invalid.csv row 5: invalid amount "oops"
```

```text
reading missing.csv: open missing.csv: no such file or directory
```

`go run . invalid.csv` and `go run . missing.csv` additionally printed
`exit status 1`; that line belongs to the Go wrapper, not the executable's own
diagnostic. Verify direct process exits separately. Generated source and exact
platform-dependent error wording can vary; the fixture, exact totals, visible
errors, nonzero failure exits, and absence of success totals are the contract.
Missing evidence or unexpected totals must not be reported as success.

## What this example establishes

The [accepted replay report](../specs/atom-v1-improvements/phase-09-onboarding-example/standalone-quickstart-report.md)
records an **assisted, bounded experienced-user run**, not independent newcomer
navigation. The directory names, executable resolution, and final wording here
are documentation translations, not an independently replayed final page.
No setup-time, prompt-count, clean-OS, universal-version/model-adherence, or
production-readiness promise follows. No spike source is packaged as production.
Close the dedicated terminal when finished; the trial files remain inspectable.
For later full-project work, use the [workflow walkthrough](workflow.md).
