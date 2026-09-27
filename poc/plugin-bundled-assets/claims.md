# Can a plugin bundle the `atom` CLI and run it?

Registered **before** any measurement.

## Why this matters

The `atom` CLI already travels with the plugin. `marketplace.json` declares
`"source": "."`, so the whole repository is the plugin and `marketplace add`
clones all of it — `tools/atom/cli.py` included. What is unproven is whether a
skill can *find* and *execute* it at runtime.

If it can, the `pip install` step disappears for plugin users and the two
install paths collapse into one. If it cannot, pip stays and this question is
closed for good rather than revisited on vibes.

## The one thing that decides it

A skill cannot hard-code the path. The user's working directory is their own Go
project, so a relative path is meaningless, and the absolute path differs
between a live local plugin and a marketplace clone under
`%LOCALAPPDATA%\copilot\marketplaces\<owner>-<repo>`.

So everything turns on: **does the agent know where the skill it just loaded
lives on disk?**

## Claims

- **C1** — A loaded skill can report the absolute path of its own `SKILL.md`.
- **C2** — Given only a path expressed *relative to itself*, the agent can
  execute a script bundled in the same plugin.
- **C3** — The script really runs, proven by an artifact it writes to disk,
  not by the agent saying it ran.

## Detection

C3 is the real test, and it is deliberately measured outside the model. The
bundled script writes a sentinel file containing its own `__file__` and the
arguments it received. The file either exists afterwards or it does not.

This follows F10: never let the agent be its own instrument. An agent that
narrates running a script, convincingly, while running nothing, is the exact
failure this spike must be immune to.

## Adoption bar

Set before measuring, so the result cannot be rationalised after the fact:

- **C2 and C3 must both hold** for the bundled CLI to replace `pip install` as
  the documented path for plugin users.
- If C1 holds but C2 does not, record the mechanism and keep pip.
- Any single success is an anecdote. Each claim is probed **3 times** from a
  directory that is not a clone of this repository, because installing from
  inside a clone is what hid F11 and F12.
