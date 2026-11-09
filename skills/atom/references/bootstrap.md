# Bootstrap — make sure Atom's commands exist

Atom is two halves. The plugin carries the workflow you are reading; the `atom`
command does the deterministic work — the Go gates, `.atom/` state, phase
tracking, shipping. The `atom-write-artifact` command is the narrow write boundary
for pipeline artifacts and Atom state. Beats shell out to these commands directly,
so both need a reachable form before a beat can do anything real.

Installing the plugin does not install these commands. Establish them here, first;
the actual toolchain and baseline checks happen during `/atom:init`.

Work down these steps and **stop as soon as both command roles work**. In the
normal case that is step 1: two help checks, with no installation or further search.

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
found, continue to step 2 for that command only. If a found command fails for another
reason, report its actual diagnostic and stop; do not mask it with a new install.

## Step 2 — Is the package there but its entry points hidden?

On Linux, choose an existing Python >=3.10: check `python3 --version` first, then
`python --version` only if `python3` is absent or unsupported. If neither is
supported, report the result and stop; do not provision Python. Use the selected
interpreter for all module checks. With `python3`, the missing-role checks are:

```bash
python3 -m atom.cli --help
python3 -m atom.artifact_cli --help
```

On Windows, retain the existing `python` fallback:

```bash
python -m atom.cli --help
python -m atom.artifact_cli --help
```

Do this **before** installing anything. A `not found` from step 1 does not mean
the package is missing: an existing user or editable install can have scripts
outside PATH, and a terminal opened before a PATH change still has its old value.

Unless the developer opts into the Windows setup below, use each successful module
form for the rest of the session. On Linux, substitute the selected interpreter
in these forms:

- Use `python -m atom.cli` wherever these skills say `atom`.
- Use `python -m atom.artifact_cli <relative-path>` wherever these skills say
  `atom-write-artifact <relative-path>`.

Tell the developer once that the package is installed but its entry points are not on
PATH.

**Do not install over it.** That would replace a working package — possibly the
developer's own editable checkout of Atom — with a fetched copy, and would not
fix the PATH anyway.

Continue only if neither role works and the diagnostics explicitly establish
that Atom is absent. A partly working package, a non-absence import failure or
another damaged command is a stop: report the unavailable role and exact error.
Do not treat every nonzero help result as permission to install.

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

## Step 3 — Reuse the known Linux environment

Only after explicit package absence, check the single known user-owned location
`$HOME/.local/share/atom-cli/venv`, outside repositories and their `.atom/` trees.
Do not search arbitrary environments or inspect package implementation.

Before executing through this path, check that its directory and ancestors within
HOME are owned by the user and are not symlinked. If a healthy environment exists,
verify both module forms and retain the successful absolute commands:

```bash
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.cli --help
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.artifact_cli --help
```

If both work, stop without reinstalling. If the destination is partial, invalid,
unowned or a directory symlink, preserve it and report the exact path/problem;
never delete, recreate, force or upgrade it. Do not execute through unsafe ancestors.
Concurrent installers are unsupported; reuse assumes a stable installation.

If the environment is absent, continue below. The new-install recipe is Linux-only;
on another platform, stop and agree on an isolated setup rather than extrapolating
this recipe or installing into system Python.

## Step 4 — Install once into an isolated Linux environment

Only explicit package absence and an absent safe destination permit this step.
Explain the shared user-owned location and public source, and obtain consent
before provisioning. Recheck writable, owned, non-symlink ancestors within HOME.
Create only absent parents and the venv destination exclusively; a collision or
permission failure stops without overwrite. Do not use a repository-local venv
or create `.atom/` before onboarding.

Using the selected supported interpreter (`python3` in this example), create
one environment:

```bash
python3 -m venv "$HOME/.local/share/atom-cli/venv"
```

If venv/ensurepip is unavailable, report the actual error and stop before installing
system tooling. Confirm that the interpreter's `sys.prefix` is the chosen venv,
differs from `sys.base_prefix`, and that its pip is located inside the venv:

```bash
"$HOME/.local/share/atom-cli/venv/bin/python" -m pip --version
```

**Before installing**, check only non-secret install-scheme settings: PIP_TARGET,
PIP_PREFIX, PIP_ROOT, PIP_USER and PIP_PYTHON, plus the corresponding `global` and
`install` target/prefix/root/user/python keys through this interpreter's
`-m pip config get <key>`. A missing key can return exit 1; confirm its actual
missing-key diagnostic rather than treating another error as an absent setting.
If settings would redirect installation outside the venv, enable user-site
installation, or leave the effective scheme uncertain, stop and ask for resolution.
Report only key names and safe scheme conclusions, not full config or credentials.
Do not disable user pip/Git configuration to force success or copy credentials.

Only then install once through the venv's Python:

```bash
"$HOME/.local/share/atom-cli/venv/bin/python" -m pip install --no-cache-dir --no-input "git+https://github.com/girishmotwani/atom.git#subdirectory=tools"
```

Do not use bare/system pip, `--user`, `sudo`, system-protection overrides or a pip
upgrade. Do not activate the environment or change PATH/profiles. Say what you
are doing and why before the install; normal command approvals still apply.

Atom's canonical repository, `girishmotwani/atom`, is public; installation does not
require private-repository access. If installation fails, report the exact output
and stop rather than retrying an unchanged command. For `Repository not found`,
verify the public URL and GitHub connectivity; do not assume a permissions problem
or ask the developer to request access to the abandoned private fork.

Verify both installed entry points and module forms without relying on PATH:

```bash
"$HOME/.local/share/atom-cli/venv/bin/atom" --help
"$HOME/.local/share/atom-cli/venv/bin/atom-write-artifact" --help
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.cli --help
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.artifact_cli --help
```

Record the actual working command forms once and use them for the session.
If installation or either role fails verification, report the exact diagnostic
and stop without retrying, overwriting or automatically cleaning up a partial
environment. Never proceed without both roles.

Bootstrap does not approve later init or artifact writes. Preserve the target
repository's command/writer permissions and complete UTF-8 stdin. A failing Go
baseline remains failing, including an empty module; do not insert code to hide it.

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
