# Atom - AI coding skills for Go

**Proof-first AI development for Go: runnable POCs, evidence-backed specs,
TDD, and multi-model review.**

Atom exists to stop AI agents from writing large amounts of confident code against an
imagined design.

Built for **Go developers using GitHub Copilot CLI**. Prove a risky idea before
designing it, implement behavior test-first, or review a Go change with multiple
models.

## Try Atom

You need GitHub Copilot CLI and Go. Atom's local tooling uses Python 3.10 or later.
Install the plugin from your terminal:

```bash
copilot plugin marketplace add girishmotwani/atom
copilot plugin install atom@atom
```

Then open Copilot CLI in a Go module and run:

```text
/atom:init
```

Onboarding runs the Go checks, records the baseline, and adds Atom's workflow files.
It records a failing baseline too; onboarding success is not a clean bill of health
for the code. To start a feature afterward, use `/atom:start` and describe your goal.

See the [setup and review instructions](#getting-started) for prerequisites and
options, or the [workflow walkthrough](docs/workflow.md) for what happens next.

If Atom is useful to you, consider
[starring the repository](https://github.com/girishmotwani/atom).

---

## The one rule

> **Nothing gets designed until something has been proven to work.**

Every unit of work — the project, and then each phase within it — runs the same three
beats:

```
   PROVE  ──────────▶  DESCRIBE  ──────────▶  BUILD
   (POC)               (spec)                 (TDD)
```

1. **PROVE** — a throwaway Go program that answers one uncomfortable question. Run it.
2. **DESCRIBE** — *now* write the design spec, informed by what actually happened.
3. **BUILD** — red, green, refactor, with the developer in the loop.

Most agent frameworks start at step 2. The design reads beautifully, the code gets
written, and the assumption underneath it turns out to be wrong three days later. Atom
front-loads that discovery into an hour of disposable code.

---

## Why the POC comes first

A design document is a prediction. A POC is an observation.

When you design first, every later artifact inherits the design's assumptions — the
spec elaborates them, the tests encode them, the implementation hardens them. By the
time reality disagrees, disagreeing is expensive.

A POC has three possible outcomes, and **all three are wins**:

| Outcome | What it means | What it saved you |
|---|---|---|
| **Confirmed** | The assumption held | You can now design on evidence instead of hope |
| **Refuted** | The assumption was wrong | The entire design you were about to write |
| **Inconclusive** | The spike missed the question | A false confidence you were about to bake in |

Atom's most valuable moment is an agent reporting *"I was wrong, here's the output."*

---

## Pipeline

```
  problem statement / MRD
        │
        ▼
  /atom:discover   interview the developer → POC Brief
        │  ◆
        ▼
  /atom:poc        throwaway Go spike, executed → POC Report
        │  ◆
        ▼
  /atom:plan       phase breakdown → Phase Plan
        │  ◆
        ▼
  ┌─ per phase ────────────────────────────────┐
  │   /atom:poc     spike this phase's risk     │
  │        ◆                                   │
  │   /atom:spec    high-level design spec      │
  │        ◆                                   │
  │   /atom:tdd     red → green → refactor      │
  │        ◆                                   │
  │   /atom:review  multi-model review          │
  └────────────────────────────────────────────┘
        │
        ▼
  /atom:ship       commit + pull request

  ◆ = gate: the agent presents, stops, and waits for you
```

| Skill | Purpose |
|---|---|
| `/atom:init` | Onboard a Go repository |
| `/atom:discover` | Vague problem → concrete, falsifiable POC Brief |
| `/atom:poc` | Build, run and evaluate a throwaway spike |
| `/atom:plan` | Break proven work into independently shippable phases |
| `/atom:spec` | High-level design spec for one phase |
| `/atom:tdd` | Implement one phase test-first |
| `/atom:review` | Multi-model review |
| `/atom:ship` | Commit and open a pull request |
| `/atom:build` | End-to-end orchestrator |

**New to Atom?** [docs/workflow.md](docs/workflow.md) walks through what happens at
each step, what you are expected to do at the gates, and what ends up on disk.

---

## Design principles

### Readable Go, not clever Go

Atom deliberately prefers **readable and extensible** Go over maximally idiomatic Go.
When the two conflict, readability wins.

```go
// Idiomatic — fine if you already know this file.
for i, v := range s {
    if v.t > d { r = append(r, i) }
}

// Atom — obvious to someone who has never seen it.
for index, session := range activeSessions {
    if session.idleTime > idleTimeout {
        expiredIndexes = append(expiredIndexes, index)
    }
}
```

Real names, explicit control flow, a doc comment on every exported symbol explaining
*why* it exists, and inline comments wherever a competent Go developer would pause and
ask "why?". `gofmt` is still absolute — the deviations are about naming, structure and
commentary. Full rules in [go-style.md](skills/atom/references/go-style.md).

### Honest enforcement

Atom has **no hidden compliance monitor**, no fabricated consequences, no invented
authority. Frameworks that coerce agents with fictional surveillance teach them that
stated rules may be bluffs — and an agent that learns to discount one rule discounts
the rest.

Atom's gates are real and local: commands you can run, artifacts on disk, and a human
in the conversation.

```bash
atom check     # build + vet + gofmt + test + race + coverage
```

`atom review` checks formatting only for surviving changed Go files in the
selected module. It formats each whole file from the selected working-tree,
staged or committed-branch snapshot over stdin, without rewriting it. Untouched
formatting defects do not block review; a changed-file defect still does.
Reports name the checked paths and any outside-module or nested-module
exclusions. Build, vet, tests, race and optional review checks keep their existing
module-wide scope; standalone `atom check` still checks module-wide formatting.

On Windows, command execution assigns a suspended process to a private Job Object
before it runs. Remaining owned children are stopped on success, timeout or
interruption; Atom's runner is not a background-service launcher. Ownership setup
fails closed rather than running without containment. Lifecycle failures are reported
as `runner_error`, not a successful tool exit; a timeout keeps its timeout outcome
and includes any incomplete-cleanup or output diagnostics. Cleanup waits share a
two-second allowance, not a hard real-time guarantee for Windows kernel calls.
A change in job membership while collecting exit identities is reported as
incomplete cleanup, never verified completion.
POSIX commands retain their existing session/group behavior.

### The developer is a participant

Gates are conversations, not approvals of finished work. The agent asks **one question
at a time**, explores the code before asking anything, and stops at every gate — it
presents, ends its turn, and waits.

### Everything is on disk

```
.atom/          state, config, event log
specs/          briefs, POC reports, plans, design specs, test specs, findings, decisions
poc/            every spike ever run, kept as re-runnable evidence
```

Two artifacts are always written, even when empty: `findings.md` (what you saw and
chose not to fix) and `decisions.md` (every time your judgement replaced the
developer's). They exist so that judgement can be audited.

Those artifacts are also the *only* thing Atom writes outside a throwaway spike.
Atom sends their complete UTF-8 content through one narrowly approved executable:

```powershell
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
@'
# Design

The complete artifact goes here.
'@ | atom-write-artifact specs/design.md
```

Copilot asks once before the first `atom-write-artifact` invocation in a repository.
Approve that command—not the broader `atom` executable—and later artifact writes are
silent. Source-code edits keep their normal approval flow.

It will write `specs/**`, `poc/**` and the replaceable `.atom/config.json`,
`.atom/state.json`, and `.atom/baseline.json` runtime files, and nothing else — not
source, tests, `.github/`, `.atom/atom/`, or the append-only `.atom/events.jsonl` audit
log. It refuses `..` traversal, absolute paths outside the repository, and any
destination reached through a symlink or Windows junction. A refusal must never be
bypassed with another command or the generic editor. The point is that the developer
never has to approve a general-purpose file editor for the whole repository just so
Atom can save a spec.

PowerShell 7 already sends native-process input as UTF-8. The explicit
`$OutputEncoding` line also protects Windows PowerShell 5.1, whose ASCII default would
silently replace non-ASCII Markdown with `?`. The writer normalizes native CRLF input
to repository-standard LF.

---

## Getting started

### Review an Azure DevOps pull request

From the corresponding **local Go module directory**, run:

```powershell
atom review --pr "https://dev.azure.com/organization/project/_git/repository/pullrequest/42"
```

This requires Git HTTPS access, an authorized Azure CLI login for read-only PR
metadata, and the existing Copilot CLI reviewer setup. Atom does not log in, install
tools, store tokens, or post comments. Both `dev.azure.com` and
`organization.visualstudio.com` PR links are supported. The local HTTPS `origin`
must match the PR repository; forks, inactive PRs, SSH origins and on-premises ADO
links are not supported by this first increment.

Atom creates a full independent temporary clone, checks out the pinned source, and
reviews its merge-base diff against the PR's **actual target branch**, not an assumed
`main`. The original branch, index and dirty files stay untouched. Reports identify
the source, fetched target, merge base and selected module. Changed files outside
that module remain in the diff, but Go checks cover only the selected module.
Cleanup is attempted on every exit; failures name the retained directory and do not
become a successful review.

**Current boundary:** normal reviews include the shared Go rules and selected
launch-module guidance described below. Automatic surrounding-code collection is
not supplied; Go checks still cover only the selected module.
Required checks still block review unless you explicitly use `--skip-toolchain`.
Existing `--model`, `--runs`, `--concurrency`, `--window`,
`--disable-mcp-server`, and `--json` options apply. Choose exactly one source:
`--pr`, `--working`, `--staged`, or `--branch`.

Use repeated `--model NAME` options to select reviewers available to your Copilot
account when a default model is unavailable; Atom does not silently substitute one.
Repeated `--disable-mcp-server NAME` options exclude named custom MCP servers from
both availability probes and review calls, without changing saved configuration.
Disabling built-in MCP servers alone does not exclude custom servers.

Normal reviews freeze two optional files from the **launch module root**, in order:
`.atom\atom\skills\atom\references\go-style.md` and `AGENTS.md`. Local edits apply,
including during PR review; files in the temporary checkout do not replace them.
Run from the module root: Atom does not walk ancestors, infer nested modules, follow
Markdown links, or import other instruction files. Missing sources are reported;
present but unreadable, invalid, blank, nonregular, dangling, outside-root or
duplicate-resolved sources stop review before PR preparation or model calls.

Use `--no-module-rules` for shared-rules-only review. For conflicting code-review
conventions, module `AGENTS.md` takes precedence over the initialized guide, then
shared style. This does not authorize workflow execution or change tool permissions,
output format or evidence scope. Reports include status, relative source names,
byte counts and SHA-256 digests, not captured policy text or absolute paths.
Delivery is not proof of rule compliance or improved review quality.

Review calls request structured CLI events so Atom can isolate one parent answer
from delegated replies, commentary and tool output. Atom requires successful stream
completion, then applies its existing strict findings validation. Malformed,
incomplete or ambiguous output remains an explicit partial-review failure; Atom
does not guess at JSON fragments or fall back to mixed plain text. This relies on
the CLI event contract, not a guarantee of compatibility with every CLI version.

### Opt-in fixed-evidence review

```powershell
atom review --working --fixed-evidence --context-file .\evidence\caller-contract.md
```

`--fixed-evidence` requests exclusions for all built-in, custom and MCP tools on
both probes and reviews. Observable tool activity or child-owned events invalidate
that review response; rejected options never trigger a tool-enabled fallback.
Tool exclusions do not necessarily prevent MCP startup; named custom servers still
require `--disable-mcp-server NAME` when startup isolation is needed.
This mode does not automatically collect module rules, even when those files exist;
its report records `fixed-evidence` status. Shared Go rules remain present.

Repeat `--context-file PATH` to supply caller-prepared UTF-8 documents. Each is
captured once, before PR preparation, relative to the original launch directory;
explicit absolute paths are also accepted. Missing, invalid, blank or duplicate
inputs stop the review. Atom does not discover callers, dependencies or other
context automatically. The complete diff and documents are sent without truncation
or an input-size cap; provider capacity errors remain explicit failures.

Reports identify diff-only versus diff-plus-caller-context scope and include byte
counts and SHA-256 digests, not document contents or local evidence paths.
Prompt metadata (`prompt_utf8_bytes` and `prompt_sha256` in JSON) identifies the
logical UTF-8 prompt before platform stdin normalization, not raw subprocess stdin
bytes or a verified provider request. Existing Windows transport converts physical
LF to CRLF. Individual document metadata identifies the original captured UTF-8
file bytes; JSON serialization preserves document text through this conversion.
Document provenance is **caller-supplied/unverified** and real-PR context quality
remains **unvalidated**. A successful scoped review is not a readiness certification.
The CLI exclusion mechanism was live-proven with one Gemini invocation; broader
model/version compatibility and real-PR quality require separate validation.

In both modes, structured review failures now report process-status summaries
instead of dumping raw CLI streams. Raw stdout/stderr remain available on native
`ModelRun` values for private programmatic diagnosis, not in ordinary reports.

### Install the plugin — the only setup step

Atom ships as a Copilot CLI plugin. Installing it once puts the `/atom` commands into
**every** repository you work in. When you onboard a Go repository, `atom init` also
captures the untouched no-race baseline, creates `specs/` and `poc/`, records the
build and test commands it exercised, and copies a self-contained instruction and
skill bundle into that repository. Later sessions do not need to read Atom's checkout
or installed-plugin directory.

Onboarding also maintains a marked `.gitignore` block for Atom's machine-local
`.atom/baseline.json`, `.atom/events.jsonl`, and `.atom/events.lock` files. Shared
configuration, gate approvals, and the local instruction bundle remain tracked.
Repositories that already committed one of the generated files need a one-time
`git rm --cached <path>` for that specific file; onboarding never changes the Git
index automatically.

> Atom is public at [girishmotwani/atom](https://github.com/girishmotwani/atom).
> Installation does not require access to a private repository.

```bash
copilot plugin marketplace add girishmotwani/atom
copilot plugin install atom@atom
```

Check it landed. Expect twelve `atom` entries — the nine beats plus `/atom:start`,
`/atom-status` and `/atom-check`:

```bash
copilot skill list
```

You now have these inside Copilot CLI, alongside built-ins like `/model`:

| Command | Beat |
|---|---|
| `/atom:start` | Describe what you want to build; Atom picks the right beat |
| `/atom:discover` | Turn a vague goal into one falsifiable question |
| `/atom:poc` | Build a disposable Go spike that answers it |
| `/atom:plan` | Break proven work into independently shippable phases |
| `/atom:spec` | Turn the POC's verdict into a design spec |
| `/atom:tdd` | Derive the test spec, then red-green |
| `/atom:review` | Multi-model review of the diff |
| `/atom:ship` | Commit, branch, pull request |
| `/atom:init` | Scaffold project state in a Go repo |
| `/atom-status` | Show the current phase, what exists, what is missing |
| `/atom-check` | Run every Go quality gate and explain failures |
| `/atom:build` | Run the whole loop end to end |

> Install from the marketplace, not directly from the repository URL. Copilot CLI has
> deprecated direct repo, URL and local-path installs, and will only support
> `plugin@marketplace` in a future release.

### Onboard a Go repository

Open a Copilot CLI session in the repository you want to onboard and type one command:

```
/atom:init
```

That is the only thing you type. Everything else is Atom's job.

**What you will be asked to approve.** Onboarding runs shell commands, and Copilot
asks before each one. A captured run on a previously un-onboarded Go repository needed
**three approvals, no denials, and no file-write prompts at all**:

| # | Approval | Why it appears |
|---|---|---|
| 1 | `atom init` | The single command that performs onboarding |
| 2 | Check `atom` / `atom-write-artifact` entry points | Discovery — finds out whether Atom's commands are on your `PATH` |
| 3 | Check `python -m atom.cli` / `python -m atom.artifact_cli` | Discovery fallback, only reached when the entry-point check finds nothing |

`atom init` is the approval that matters; it is the one that does the work. The other
two are discovery probes Copilot runs first to locate Atom's commands, and if your
Python scripts directory is already on `PATH`, the third never appears. The ledger for
the captured run, in the order the prompts actually arrived, is in
[specs/onboarding-workflow/interactions.md](specs/onboarding-workflow/interactions.md).

**You are never asked to approve writes to Atom's own state.** `.atom/state.json`,
`.atom/baseline.json`, `.atom/config.json` and the event log are written inside the
`atom init` command you already approved, so they never surface as separate prompts.

**What one `atom init` leaves behind:**

```
.atom/config.json        module path, plus the build and test commands it just exercised
                         (`make build` / `make test` when a Makefile defines them)
.atom/state.json         pipeline and phase state
.atom/baseline.json      the untouched no-race gate result, captured before anything changed
.atom/events.jsonl       structured event log
.atom/atom/              self-contained instruction and skill bundle
.github/copilot-instructions.md
specs/                   design artifacts
poc/                     throwaway spikes
.gitignore               a marked block for the machine-local files above
```

**A repository's own Makefile wins.** If `make` is installed and the Makefile defines a
`build` or `test` target, `atom init` and `atom check` run `make build` / `make test`
instead of the Go defaults — a project that declares how it is built usually encodes
build tags, ldflags or code generation that `go build ./...` would skip. Each target is
decided on its own, so a Makefile that builds but does not test delegates only the build.
Vet, format and the race detector stay Go-native: there is no conventional target for
them, and the format gate reads its verdict from `gofmt`'s stdout rather than an exit
code, so delegating it would hide the filenames it exists to report. `atom init` prints
the commands it chose and why, and records them in `.atom/config.json`.

**A red baseline does not stop onboarding.** `atom init` records the result it found
and moves on, so you can onboard a repository whose gates are already failing and see
exactly what was broken before Atom touched it.

**Repeating `atom init` is read-only when setup is valid and matching.** It returns 0
with an explicit no-op message, without rerunning the baseline, resetting approvals,
refreshing instructions, appending events, or changing files and timestamps. Custom
build/test commands are preserved. Machine-local baseline and event files, and empty
`specs/` and `poc/` directories, may be absent on a fresh clone.

Conflicting module requests and incomplete or corrupt shared setup return a nonzero
error without changes. Restore or repair the named files; do not use `--force` as a
repeat-call workaround. Explicit `atom init --force` deliberately reinstalls setup and
discards recorded approvals.

**Confirm it worked** by reading `.atom/baseline.json` and `.atom/config.json`, or by
running `/atom-status`. Both are read-only. After a no-op, the baseline may be absent;
the command has validated the shared setup structurally, not captured a new baseline
or upgraded the local bundle.

### Installing and updating as Atom evolves

Installing copies Atom into `~/.copilot/installed-plugins/atom/atom`. That copy is a
**snapshot, not a live link** — it has no `.git` inside it and does not track the source.
New bits never arrive on their own, so this is the command that matters:

```bash
copilot plugin update atom@atom         # one plugin
copilot plugin update --all             # everything installed
```

**Know what you are updating *from* before you run it.** A plugin updates from the
marketplace it was installed from, which is not necessarily the copy you are editing:

```bash
copilot plugin marketplace list
```

That distinction gives two different workflows:

| You are | Marketplace points at | To get new bits |
|---|---|---|
| **Using** Atom | `girishmotwani/atom` on GitHub | `copilot plugin update atom@atom` |
| **Developing** Atom | your local clone | same command — no push required |

To develop against your own clone, point the marketplace at it with an **absolute** path
(a relative path is parsed as `owner/repo`) and reinstall:

```bash
copilot plugin marketplace add /absolute/path/to/atom
copilot plugin update atom@atom
```

Because the marketplace is a local directory, this picks up committed changes without
pushing anything.

> **Do not develop with `--plugin-dir`.** Live-loading from a directory silently fails to
> load the plugin in some sessions, which is exactly how this README once reported a
> bogus 33% routing figure — two thirds of those "failures" were sessions with no Atom
> loaded at all. Installed properly the problem disappears. The evidence is in
> [the routing POC](poc/atom-routing-rules/results.md).

When publishing a change for other people, bump the version in **both** `plugin.json` and
`.github/plugin/marketplace.json` — they must agree — and push before asking anyone to
update.

Confirm the update actually landed, rather than assuming:

```bash
copilot plugin list                     # shows the installed version
```

### Run it

That is the whole setup. Atom's other half — the `atom` command that runs the Go gates
and tracks phase state — installs itself the first time a beat needs it, and `/atom:start`
scaffolds a project the first time you point it at one. Neither is yours to do by hand.

Start from a plain description of what you want to build:

```
/atom:start add topic-based routing to the event bus
```

Atom works out where you are, picks the earliest beat whose output is missing, and
tells you the next command to run. It opens by asking what the riskiest part is —
because the first thing Atom builds is a spike that could prove the idea wrong.

A session then walks the beats, and you can check in at any point:

```
/atom:discover        scope one falsifiable question
/atom:poc             build the spike, grade it against the thresholds
/atom:plan            break proven work into phases
/atom:spec            design spec for this phase
/atom:tdd             test spec, then red-green
/atom-check           are the Go gates green?
/atom:review          second opinion on the diff
/atom:ship            commit, branch, pull request

/atom-status          where am I, and what is missing?
```

`/atom-status` and `/atom-check` are safe to run at any time — they report and never
change your code.

### Prose works, and the slash command is still the certain path

Atom's skills carry routing keywords, so you can describe what you want in plain
English and Copilot will pick the right beat.

Measured over 25 trials from a clean directory, with prompts that never name a skill,
a slash command, or Atom: a plain-English prompt loaded the right skill **25 times out
of 25**. It never once chose the wrong beat, and never answered from the one-line
description without loading the workflow behind it.

That number replaces an earlier 33% figure quoted here. The 33% was real but
misleading — it was measured with the plugin *live-loaded* from a local directory, a
development-only mode that silently drops the plugin in some sessions. Two thirds of
those "routing failures" were sessions with no Atom plugin loaded at all. Installed
normally, as the step above does it, the problem does not occur.

So: **prose is reliable enough to use, and the slash command is exact.** Reach for the
slash command when you want no ambiguity about which beat runs. Full numbers, the
correction, and the method are in [the routing POC](poc/atom-routing-rules/results.md).

If you are extending Atom itself rather than using it, [AGENTS.md](AGENTS.md) documents
the same rules for agents working inside this repository.

### If setup goes wrong

**`Repository not found` when adding the marketplace.** Verify that the command uses
`girishmotwani/atom` and that Git can reach GitHub. The repository is public; do not
assume this error means private-repository access is required. Report the exact
failure instead of retrying an unchanged command. If you already have a clone,
you can point the marketplace at it directly with
`copilot plugin marketplace add /absolute/path/to/atom`. The path must be absolute; a
relative one is parsed as `owner/repo`.

**Installing the `atom` command by hand.** The first beat that needs it installs it for
you. To do it yourself, or to keep it off your system Python:

```bash
python -m venv .venv                # optional; deleting .venv undoes everything
source .venv/bin/activate           # macOS / Linux
.venv\Scripts\Activate.ps1          # Windows

pip install "git+https://github.com/girishmotwani/atom.git#subdirectory=tools"
atom --help
```

A virtual environment has to be activated in each new terminal.

**`atom` or `atom-write-artifact` installs, then reports "not found".**
`pip install --user` puts both executables in a directory Windows may not search, and a
terminal that was already open copied its environment at launch, so it cannot see a
later PATH change. On Windows, opt into a one-time setup using the working Python
package:

```powershell
python -m atom.cli setup-path
```

This finds both installed executables, adds their Scripts directory to your **user**
PATH without changing existing entries or system PATH, and notifies Windows.
It is safe to run again: an equivalent existing entry is not rewritten.
The current parent process still has its old PATH, so use the absolute PowerShell
commands printed by setup for the rest of this session. A new terminal launched
with the refreshed environment can use `atom` and `atom-write-artifact` by name.
Ordinary `atom init` never opts into this persistent change automatically.

Without the opt-in, bootstrap can use `python -m atom.cli` and
`python -m atom.artifact_cli` as temporary fallbacks. Approving the dedicated writer
executable is narrower than approving `python`, so prefer the writer path printed by
setup rather than broadening executable permissions.

Do not use `setx PATH "%PATH%;..."` to do that. `%PATH%` expands to the *merged* machine
and user value and `setx` truncates at 1024 characters, so on a typical workstation it
silently destroys part of the PATH it was asked to extend.

**Working on Atom itself?** Install from your clone so edits take effect without
reinstalling: `pip install -e ./tools`.

### Recommended model

Atom's loop is heavy on judgement — deciding whether a POC actually answered its
question, whether a design follows from evidence, whether a test failure is a code
defect or a test defect.

**HydraFusion** in GitHub Copilot CLI suits this well. It is not a single model but a
multi-model orchestration layer that routes each task through single, cascade or
critique workflows across providers.

```
/update
/experimental on
/model          → HydraFusion (Research Preview)
```

Fallbacks and role guidance in
[model-guidance.md](skills/atom/references/model-guidance.md).

---

## Requirements

| Tool | Version | For |
|---|---|---|
| Copilot CLI | ≥ 1.0.89 | the plugin and the `/atom` commands |
| Go | ≥ 1.21 | everything |
| Python | ≥ 3.10 | the `atom` CLI |
| git | any | installing Atom, and `/atom:ship` |
| gh | any | pull requests (optional) |

Go is the **target** language. Python is the **tooling** language. Atom never asks you
to write or run PowerShell.

---

## Atom is its own worked example

The `atom` CLI was built with Atom.

`specs/atom-cli/` contains the real POC brief, the real POC report with verbatim
terminal output, the phase plan and the design specs. `poc/module-isolation/` contains
the actual spike — and you can still run it.

That spike asked whether a throwaway module under `poc/` could break the parent build.
The answer was no, which validated the design. It also **refuted** a smaller assumption
along the way: Go writes compile errors to stderr, so capturing stdout alone would have
shown POC failures to developers as silent success. That is a bug that never shipped,
because a disposable program found it before a design was written around it.

---

## License

MIT — see [LICENSE](LICENSE).
