# Atom

**An agentic development framework for Go.**

Atom exists to stop AI agents from writing large amounts of confident code against an
imagined design.

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

### Install the plugin — the only setup step

Atom ships as a Copilot CLI plugin. Installing it once puts the `/atom` commands into
**every** repository you work in. When you onboard a Go repository, `atom init` also
copies a self-contained instruction and skill bundle into that repository, so later
sessions do not need to read Atom's checkout or installed-plugin directory.

Onboarding also maintains a marked `.gitignore` block for Atom's machine-local
`.atom/baseline.json`, `.atom/events.jsonl`, and `.atom/events.lock` files. Shared
configuration, gate approvals, and the local instruction bundle remain tracked.
Repositories that already committed one of the generated files need a one-time
`git rm --cached <path>` for that specific file; onboarding never changes the Git
index automatically.

> **Atom is in private testing, so the repository is not public yet.** The command below
> clones it using your own git credentials, so it works only if you have been granted
> access — see [if setup goes wrong](#if-setup-goes-wrong) if it fails.

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
| `/atom:spec` | Turn the POC's verdict into a design spec |
| `/atom:tdd` | Derive the test spec, then red-green |
| `/atom:review` | Multi-model review of the diff |
| `/atom:ship` | Commit, branch, pull request |
| `/atom:plan` | Break work too large for one pass into phases |
| `/atom:init` | Scaffold project state in a Go repo |
| `/atom-status` | Show the current phase, what exists, what is missing |
| `/atom-check` | Run every Go quality gate and explain failures |
| `/atom:build` | Run the whole loop end to end |

> Install from the marketplace, not directly from the repository URL. Copilot CLI has
> deprecated direct repo, URL and local-path installs, and will only support
> `plugin@marketplace` in a future release.

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

**`Repository not found` when adding the marketplace.** Atom is in private testing, so
this is a permissions error despite reading like a typo. Ask for access — or, if you
already have a clone, point the marketplace at it directly with
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
later PATH change. Add that Scripts directory to your **user** PATH and open a new
terminal. `python -m atom.cli` is useful for diagnosing the main CLI, but do not replace
`atom-write-artifact` with `python -m atom.artifact_cli`: Copilot would approve the
broader `python` executable instead of the deliberately narrow writer command.

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
