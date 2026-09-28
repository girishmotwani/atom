# Bootstrap — make sure the `atom` command exists

Atom is two halves. The plugin carries the workflow you are reading; the `atom`
command does the deterministic work — the Go gates, `.atom/` state, phase
tracking, shipping. Beats shell out to it directly, so it has to be reachable
before a beat can do anything real.

Installing the plugin does not install the command. And `atom init --check`,
which verifies every other tool, cannot report on the one tool it is itself
running from. So establish it here, first.

Work down these steps and **stop at the first one that succeeds**. In the normal
case that is step 1, and costs a single command.

## Step 1 — Is the command there?

```bash
atom --help
```

If that succeeds, use `atom` for the rest of the session. Stop reading.

## Step 2 — Is the package there but hidden?

```bash
python -m atom.cli --help
```

Do this **before** installing anything. A `not found` from step 1 does not mean
the package is missing — more often it is installed and the entry-point script
is simply not on PATH. `pip install --user` puts it in a directory Windows does
not search; a terminal that was already open cannot see a PATH change made after
it launched; a developer's editable install has the same symptom.

If this succeeds, the package is present and working. Use `python -m atom.cli`
wherever these skills say `atom`, for the rest of the session, and tell the
developer once that you are doing so.

**Do not install over it.** That would replace a working package — possibly the
developer's own editable checkout of Atom — with a fetched copy, and would not
fix the PATH anyway.

## Step 3 — Install it

Only if both checks above failed.

```bash
pip install "git+https://github.com/girishmotwani/atom.git#subdirectory=tools"
```

Say what you are doing and why, in one line, before you run it.

Atom is in private testing, so this clones over the developer's own git
credentials. A `Repository not found` failure here is a **permissions** problem
despite reading like a typo — the developer needs access. Say so and stop rather
than retrying.

Then re-run step 1, and if it is still not found, step 2. One of them will now
work; use whichever does.

## What not to do

- **Do not reach for `setx` to repair the PATH.** `%PATH%` expands to the merged
  machine and user value, and `setx` truncates at 1024 characters. On a typical
  workstation that silently destroys part of the PATH it was asked to extend.
  `python -m atom.cli` is equivalent and costs nothing.
- **Do not continue without the command.** A beat that cannot run `atom check`
  has no evidence. Improvising the gates produces a confident answer with
  nothing behind it, which is worse than stopping and saying so.
