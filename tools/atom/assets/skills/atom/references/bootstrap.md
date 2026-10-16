# Bootstrap — make sure Atom's commands exist

Atom is two halves. The plugin carries the workflow you are reading; the `atom`
command does the deterministic work — the Go gates, `.atom/` state, phase
tracking, shipping. The `atom-write-artifact` command is the narrow write boundary
for pipeline artifacts and Atom state. Beats shell out to these commands directly,
so both need a reachable form before a beat can do anything real.

Installing the plugin does not install the command. Establish it here, first;
the actual toolchain and baseline checks happen during `/atom:init`.

Work down these steps and **stop at the first one that succeeds**. In the normal
case that is step 1, and costs a single command.

## Use the command interface, not the implementation

Do not locate or read Atom's Python source while onboarding another repository.
Resolve commands only through the entry-point and module checks below, run from
the target repository. Use their `--help` output for supported options.
Do not use `atom.__file__`, `inspect`, or filesystem searches to find `cli.py`,
the Atom checkout, or installed package internals. Do not change into the Atom
checkout or invoke a Python source file by absolute path.

An editable install may execute code from an Atom checkout; Python resolves that
internally. That does not require the agent to read the checkout or request
file-tool access to it. A successful help check is enough to establish that the
command works. If a command fails, report its output instead of opening its
implementation unless the developer explicitly requests debugging Atom itself.

## Step 1 — Are the entry points there?

```bash
atom --help
atom-write-artifact --help
```

Use each entry point that succeeds. If both succeed, stop reading. If either is not
found, continue to step 2 for that command only.

## Step 2 — Is the package there but its entry points hidden?

```bash
python -m atom.cli --help
python -m atom.artifact_cli --help
```

Do this **before** installing anything. A `not found` from step 1 does not mean
the package is missing — more often it is installed and the entry-point scripts are
simply not on PATH. `pip install --user` puts them in a directory Windows does not
search; a terminal that was already open cannot see a PATH change made after it
launched; a developer's editable install has the same symptom.

Unless the developer opts into the Windows setup below, use each successful module
form for the rest of the session:

- Use `python -m atom.cli` wherever these skills say `atom`.
- Use `python -m atom.artifact_cli <relative-path>` wherever these skills say
  `atom-write-artifact <relative-path>`.

Tell the developer once that the package is installed but its entry points are not on
PATH.

**Do not install over it.** That would replace a working package — possibly the
developer's own editable checkout of Atom — with a fetched copy, and would not
fix the PATH anyway.

### Optional one-time Windows user-PATH setup

When the package works but its entry points are hidden, offer this opt-in once.
Explain that it adds the installed command directory to the current user's PATH,
preserves existing entries, and leaves system PATH unchanged. Obtain consent once;
an explicit request to update PATH already supplies that consent.

```bash
python -m atom.cli setup-path
```

The command locates both installed executables, updates user PATH only if needed,
and notifies Windows. It prints the absolute, quoted commands to use immediately:
the current Copilot process still has its old PATH.

Use those printed executable commands for the remainder of the session, including
the dedicated artifact writer. Do not re-probe command names, search for Scripts
directories, read package source, or ask separately which Python scheme to use.
New terminals launched with the refreshed environment can use the command names.
Normal command approvals still apply; this is not a permission bypass.

If setup fails, report its exact output, including any saved-but-not-notified state.
Do not report successful PATH setup or reinstall over the working package. If the
developer declines this optional step, retain the module forms above.

## Step 3 — Install it

Only if both checks above failed.

```bash
pip install "git+https://github.com/gimotwan_microsoft/atom.git#subdirectory=tools"
```

Say what you are doing and why, in one line, before you run it.

Atom is in private testing, so this clones over the developer's own git
credentials. A `Repository not found` failure here is a **permissions** problem
despite reading like a typo — the developer needs access. Say so and stop rather
than retrying.

Then re-run both checks in step 1, and use the corresponding check in step 2 for any
entry point that is still not found. Each command must have a working entry-point or
module form before continuing.

## What not to do

- **Do not reach for `setx` to repair the PATH.** `%PATH%` expands to the merged
  machine and user value, and `setx` truncates at 1024 characters. On a typical
  workstation that silently destroys part of the PATH it was asked to extend.
  `python -m atom.cli` is equivalent and costs nothing.
- **Do not continue without both command boundaries.** A beat that cannot run
  `atom check` has no evidence. A beat that cannot run the guarded artifact writer
  cannot persist its required artifacts safely. Improvising either boundary produces
  a confident answer with nothing behind it, which is worse than stopping and saying
  so.
