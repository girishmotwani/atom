# Bootstrap — make sure Atom's commands exist

Atom is two halves. The plugin carries the workflow you are reading; the `atom`
command does the deterministic work — the Go gates, `.atom/` state, phase
tracking, shipping. The `atom-write-artifact` command is the narrow write boundary
for pipeline artifacts and Atom state. Beats shell out to these commands directly,
so both need a reachable form before a beat can do anything real.

Installing the plugin does not install these commands. Establish them here, first;
the actual toolchain and baseline checks happen during `/atom:init`.

Treat expected absence as prerequisite information, not a failed installation:

| State | Action |
|---|---|
| Commands/package absent | Explain what is missing; propose installation only after the checks below and explicit consent |
| Healthy installation outside PATH | Reuse its verified forms; do not reinstall |
| Found but broken, partial or unsafe | Preserve it, show the actual problem and stop |

Use the active Copilot session's reported identity; the documented minimum is
Copilot CLI 1.0.89. Another executable's `--version` does not identify this session.
If identity is unavailable, conflicting or unsupported, ask one focused clarification
or switch/update consent question and wait. Do not automatically update the client.

If both forms are already verified for this session/environment, retain them; do
not repeat discovery at every beat. Otherwise work down these steps and **stop as
soon as both command roles work**. A context change or real failure needs explicit
resolution, not an assumption that stale forms still work.

Group compatible read-only checks into as few terminal invocations as safely
possible, rather than issuing a separate call for every probe. Within a group,
preserve the order and decisions below, each originating status and full relevant
output. Stop on a real failure before running later checks. If a group cannot
preserve a prerequisite, diagnostic, ownership check or required user decision,
run those checks separately. Never combine discovery with installation consent.

Keep full relevant diagnostics and originating exit statuses. Do not pipe help or
writer checks through `head` or a success-shaped fallback. A writer refusal or
nonzero result stops the workflow even if a wrapper reports zero: no later write,
alternate target or generic-editor bypass. Use `--help` to verify writer support,
not an invalid target. Missing-tool consent is not permission to ignore real errors.

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

Resolve both names through the platform's command-availability mechanism before
executing them. If Python is already available, `shutil.which("atom")` and
`shutil.which("atom-write-artifact")` return a path or `None`; otherwise use the
platform's resolver without presenting expected absence as failed Atom execution.
Do not require Python discovery when both entry points already work.

Run **only a found role's** help command, one at a time:

```bash
atom --help
atom-write-artifact --help
```

Use each entry point that succeeds. If both succeed, record their forms once and
stop. For absent roles, continue to step 2 without executing their missing names.
If a found command fails, report its actual diagnostic and stop immediately; do not
mask it with another form or a new install.

## Step 2 — Is the package there but its entry points hidden?

Only for missing roles, resolve an existing interpreter before executing it.
On Linux, choose Python >=3.10: check an available `python3 --version` first, then
an available `python --version` only if `python3` is absent or unsupported.
On Windows, retain the existing `python` fallback. If no supported interpreter is
available, explain that prerequisite and ask the developer to supply it; stop
without provisioning Python. Use the selected interpreter for all module checks.

Query distribution and module evidence **before** module help. A top-level `atom`
name can be an unrelated package or a repository-local namespace; it does not
establish that Atom CLI is installed. With selected `python3` (substitute `python`
on Windows), use:

```bash
python3 -c "
import importlib.machinery
import importlib.metadata
import importlib.util
import json
try:
    importlib.metadata.distribution('atom-cli')
except importlib.metadata.PackageNotFoundError:
    registered = False
else:
    registered = True
package = importlib.util.find_spec('atom')
candidates = None
if not registered and package is not None:
    locations = list(package.submodule_search_locations or [])
    candidates = [
        module for module in ('atom.cli', 'atom.artifact_cli')
        if locations and importlib.machinery.PathFinder.find_spec(module, locations) is not None
    ]
print(json.dumps({'distribution': registered, 'package': package is not None, 'module_candidates': candidates}))
"
```

Only `PackageNotFoundError` means missing distribution registration. Any other
query exception/nonzero result stops with its actual diagnostic; never turn an
unexpected error into absence. The query does not import `atom`, read source or
print origins. Do not replace it with a dotted `find_spec('atom.cli')` lookup:
that can execute the parent package merely to discover a child.

Interpret the JSON in order, preserving any already verified entry-point role:

| Evidence | Action |
|---|---|
| `distribution: true`, `package: false` | Inconsistent own installation: report it and stop; do not run missing modules |
| Both flags true | Installed/editable candidate: help-check only missing roles; metadata does not prove they work |
| No distribution; candidates cover every still-missing role | Possible source-only forms: help-check only those roles, without requiring metadata |
| Some role already verified or some required candidates found, but remaining roles unavailable/uncertain | Partial/mixed setup: name the gap and stop; no environment switch or install |
| Both flags false, no verified role | Explicit absence: continue to Step 3 without missing-module help |
| No distribution, package present, empty candidates, no verified role | Ambiguous same-name package/importer: do not run presumed Atom modules; only read-only known-venv reuse in Step 3 is permitted |

`module_candidates: null` means the path-based lookup was not needed, not that
roles are missing. An empty list under a same-named package is ambiguous: custom
importers may resolve modules that this lookup cannot. Contradictory or unsupported
evidence stops for resolution; it is not permission to install. Never discard own
metadata, a partial candidate, a verified role or a real error because a path-based
lookup was negative.

Only a permitted successful help establishes a working form. With `python3`, the
missing-role help forms are:

```bash
python3 -m atom.cli --help
python3 -m atom.artifact_cli --help
```

With the selected Windows `python`, the missing-role help forms are:

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

Once both roles work, record their exact forms and retain them for subsequent
beats; no repeated bootstrap. Continue to Step 3 only for explicit absence or the
read-only ambiguity case above, with neither role verified. A partly working
package, a non-absence import failure or another damaged command is a stop: report
the unavailable role and actual evidence. Do not invent error output for an
unexecuted command or treat any failed help result as permission to install.

### Optional one-time Windows user-PATH setup

When the package works but its entry points are hidden, keep the verified module
forms without asking to change PATH. If the developer requests PATH setup, explain
that this opt-in adds the installed command directory to the current user's PATH,
preserves existing entries, and leaves system PATH unchanged. An explicit request
to update PATH supplies consent; otherwise do not run it.

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

After explicit package absence, or the Step 2 ambiguity case with neither role
verified, check the single known user-owned location
`$HOME/.local/share/atom-cli/venv`, outside repositories and their `.atom/` trees.
Ambiguity permits only read-only reuse of an existing healthy venv, not installation.
Keep that distinction even if the known environment is absent. Do not search
arbitrary environments or inspect package implementation.

Before executing through this path, check that its directory and ancestors within
HOME are owned by the user and are not symlinked, including the interpreter's
parent directory. Check that the interpreter exists before invoking it. Query it
for supported Python, `sys.prefix` and `sys.base_prefix`: the prefix must be this
venv, distinct from the base prefix. Only then apply Step 2's distribution/module
evidence through this interpreter. Missing metadata alone does not disqualify
source-only forms whose candidates permit both successful helps. Missing, partial
or ambiguous roles in an occupied venv are preserved partial setup, not permission
to install over it. If permitted, verify both module forms and retain the successful
absolute commands:

```bash
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.cli --help
"$HOME/.local/share/atom-cli/venv/bin/python" -m atom.artifact_cli --help
```

If both work, stop without reinstalling. If the destination is partial, invalid,
unowned or a directory symlink, preserve it and report the exact path/problem;
never delete, recreate, force or upgrade it. Do not execute through unsafe ancestors.
Concurrent installers are unsupported; reuse assumes a stable installation.

If the environment is absent and Step 2 established explicit absence, continue
below. If Step 2 was ambiguous, stop and ask for resolution or known working forms;
do not enter Step 4. Successful venv reuse does not repair or identify the original
interpreter's same-named package. The new-install recipe is Linux-only; on another
platform, stop and agree on an isolated setup rather than extrapolating this recipe
or installing into system Python.

## Step 4 — Install once into an isolated Linux environment

Only explicit package absence and an absent safe destination permit this step.
Resolve Git and query the selected Python for `venv` and `ensurepip` availability
before creation. If missing, explain the prerequisite and ask the developer to
supply it; do not install system tools. Presence does not guarantee creation works:
real errors still stop.

With prerequisites available, explain the missing Atom commands, shared user-owned
location and public source. Ask one explicit installation-consent question and
**wait** before provisioning. Recheck writable, owned, non-symlink ancestors within HOME.
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
