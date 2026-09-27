---
name: atom-bundle-probe
description: 'Probe skill testing whether a skill can locate and execute a script bundled beside it inside the same plugin. Keywords: atombundleprobe, bundled asset probe, bundled script.'
---

# atom-bundle-probe

This skill ships inside a Copilot CLI plugin. A Python script is bundled in the
same plugin, beside the `skills/` directory:

```
<plugin root>/
  skills/atom-bundle-probe/SKILL.md    <- this file
  scripts/probe.py                     <- the bundled script
```

Nothing here tells you an absolute path, because the plugin root differs between
installs. You must resolve it from the location of this file.

Do both steps, in order.

**Step 1 — report your own location.** State the absolute path of this
`SKILL.md` on disk. If you genuinely cannot determine it, reply with exactly
`PATH_UNKNOWN` rather than guessing a plausible-looking path.

**Step 2 — run the bundled script.** The plugin root is two directories above
this file. Resolve `scripts/probe.py` against it and run:

```
python <plugin root>/scripts/probe.py <TOKEN>
```

using the token you were given in the request. Report the exact command you ran
and its output verbatim.

Do not simulate, describe, or approximate step 2. Actually execute it. The
script writes a file to disk, and that file — not your description of it — is
what this probe measures.
