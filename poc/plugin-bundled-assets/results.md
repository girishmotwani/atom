# Can a plugin bundle the `atom` CLI and run it?

## Verdict: **Mechanically yes — but keep `pip install`**

Bundling works. It is not worth adopting, for a reason that has nothing to do
with whether the files travel.

Measured against the bar in [claims.md](claims.md), which was registered before
any trial was run.

| Claim | Result |
|---|---|
| **C1** — a skill can report its own absolute path | **Confirmed** (3/3 sessions where the skill loaded) |
| **C2** — it can resolve a sibling script from that path | **Confirmed** |
| **C3** — the script actually runs, proven on disk | **Confirmed, but only with a path grant** |

## What the agent knows about itself

A loaded skill knows exactly where it lives. Asked for its own location it
returned, unprompted and correct:

```
C:\Users\dev\work\atom\poc\plugin-bundled-assets\fixture\skills\atom-bundle-probe\SKILL.md
```

This was the assumed blocker and it is not one. A `SKILL.md` can legitimately
say "the script is two directories above this file" and the agent resolves it.

## The real blocker is path permission, not path discovery

With no grant, the agent resolved the correct path, built the correct command,
and was refused:

```
python "...\fixture\scripts\probe.py" T8
  -> Permission denied and could not request permission from user
```

It then retried by `Set-Location`-ing to the plugin root first. Refused again.
The plugin lives outside the user's project, and file access outside the working
directory is verified.

Granting the directory makes everything work:

```
copilot -p "..." --allow-all-tools --add-dir <plugin root>
```

The sentinel file appeared on disk — the evidence this spike was built around,
since an agent can narrate running a script it never ran (F10):

```
script_path=...\fixture\scripts\probe.py
argv=T3
cwd=C:\Users\dev\AppData\Local\Temp\bundleprobe-f52328
```

Note `cwd`: the script ran from the throwaway working directory, not from the
plugin, which is exactly how a real user's session would invoke it.

## Why this still loses to `pip install`

`--add-dir` takes the plugin root, and that path is not stable. For a live local
plugin it is wherever the clone sits; for a marketplace install it is
`%LOCALAPPDATA%\copilot\marketplaces\<owner>-<repo>`. So the instruction would
be "find where Copilot put the plugin, then pass it with `--add-dir` every time
you start a session" — against `pip install ...` once, ever.

Bundling also costs the standalone `atom` binary. `atom check` in a terminal or
in CI needs something on PATH; a bundled copy is only reachable as
`python <path>\cli.py`.

**Decision: keep `pip install` as the documented path.** Revisit only if Copilot
CLI starts trusting a plugin's own directory by default, which is the single
change that would flip this.

## The thing worth more than the answer

The skill was **not reliably available at all**. Across 8 sessions that all
explicitly asked for it by name, with the plugin installed and enabled
throughout:

| Outcome | Sessions |
|---|---|
| Skill loaded | 3 |
| `Skill not found: atom-bundle-probe` | 5 |

`copilot skill list` showed it registered and `copilot plugin list` showed it
enabled *during* the failing window, and the files were on disk. The same
prompt that failed then succeeded later unchanged.

This is flakiness in plugin skill availability, not in routing. It matters far
beyond this spike, because the routing measurement in
[atom-routing-rules](../atom-routing-rules/results.md) recorded a 33% load rate
and attributed the other 67% to the model choosing not to load a skill. These
trials named the skill explicitly and still failed about 60% of the time, which
points at a shared cause upstream of routing.

If that is right, the routing number is measuring the wrong thing, and the fix
is not better keywords.

**It was right.** F15 traced it to live-loading: a live plugin resolves through
a separate startup step that sometimes does not run, leaving the session with
only built-in skills and no error logged anywhere. Installed from the
marketplace, the plugin loaded 12 of 12, and the re-measured routing figure is
100% over 25 scored trials rather than 33%.

## Not proven here

- **Interactive behaviour.** Every trial used `-p`, where the refusal message is
  literally "could not request permission from user". A real session can prompt,
  and the approval might persist in `permissions-config.json`, which is keyed by
  working directory. If it persists per project, the cost of bundling drops a
  lot. Untested.
- **The cause of the availability flake.** Not diagnosed, only observed.
- **Whether `--allow-all-paths` affects skills.** An early trial suggested it
  did; that was wrong. It coincided with the flake above, and a later run with
  no flags failed identically. No effect is claimed.
- **Marketplace-installed plugins.** The fixture was a live local plugin. A
  cloned plugin under `%LOCALAPPDATA%` was never exercised.

## Instrument defects hit while running this

Three, all the same shape as F10 — a detector that reported confidently while
measuring nothing:

1. `copilot skill list --add-dir` and `--allow-all-paths` return
   `error: unexpected argument`. Counting matching lines turned that error into
   "0 skills found", which read as a dramatic finding and was an argument
   mistake.
2. A helper used `$args`, a PowerShell automatic variable, to build the command.
3. The helper then printed only booleans, which hid the refusal text and made a
   flake look like a flag effect.

Every one of these produced a plausible wrong answer rather than an obvious
failure. The only reason the final result is trustworthy is the sentinel file:
an artifact written by the thing being measured, checked by something that is
not the agent.
