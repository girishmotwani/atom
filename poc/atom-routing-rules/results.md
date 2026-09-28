# POC Results: plugin-shipped rules and beat-routing accuracy

Claims were registered in [claims.md](claims.md) before any measurement ran.
Nothing in this document moves a threshold that was set there.

Environment: GitHub Copilot CLI **1.0.89-4/5**, Windows, plugin `atom-go@atom`.
The first measurement ran with the plugin **live-loaded** from a local
marketplace; the re-measurement ran with it **installed** from the marketplace.
That difference turned out to matter more than anything else in this document.

> **Correction (F15).** The 33.3% headline below was confounded. Live loading
> drops the plugin silently in some sessions, so trials where no plugin existed
> at all were scored as routing failures. Re-measured on an installed plugin,
> recording plugin presence per trial, prose routing scores **100%**. The
> original numbers are kept, marked superseded, because the conclusions they led
> to were wrong in a way worth remembering.

---

## C1 — Do plugin-shipped rules reach the model? **REFUTED**

`com.github.copilot/rules/` is an officially documented component location for
Agent Plugins 1.0. It is listed in the component table in the CLI plugin
reference alongside agents, commands, hooks and LSP servers.

A rules file was placed there containing a single instruction: end every reply
with the token `RULESPROBE7391`. The token never appeared, under any of five
conditions:

| # | Condition | Sentinel seen |
|---|---|---|
| 1 | Prose question, neutral directory, `--no-custom-instructions` | no |
| 2 | Prose question, neutral directory, custom instructions enabled | no |
| 3 | After `marketplace update` + `plugin update` | no |
| 4 | With `applyTo: '**'` added to the rule frontmatter | no |
| 5 | File-touching question, run inside the plugin's own repository | no |

### The control that makes this a real negative

A null result is worthless if the plugin simply was not loading. It was.

In the same session type, same flags, same neutral directory, a prompt about
implementing a design test-first loaded a skill from that very plugin and named
it outright:

> Use **`atom-tdd`**: map every specified behaviour to tests, then implement one
> behaviour at a time through **RED -> GREEN -> REFACTOR**.

So skills and commands from the plugin load, while rules from the same plugin
do nothing. The negative is specific to rules, not to the plugin or the rig.

**Consequence.** Rules are not currently a usable mechanism for shipping a
routing table. The pre-registered adoption bar required rules to improve
accuracy; they cannot be measured at all, so the rules file was deleted rather
than shipped on the strength of documentation that does not match behaviour.

---

## C2 — Do rules suppress skills or commands? **NOT APPLICABLE**

Untestable while C1 fails. No interference was observed in any of the five
conditions above.

---

## C3 — Beat-routing accuracy **MEASURED**

27 trials, three prompts for each of the nine beats. Prompts are phrased the way
a developer would type them and never name a skill, a slash command, or Atom.
All trials ran from a neutral home directory containing no Atom checkout and no
`AGENTS.md`, so the plugin was the only possible source of a skill.

### The instrument had to be fixed twice

**First attempt — sentinel injected into each SKILL.md.** Reported 22.2%. It was
wrong twice over, and was discarded:

- 11 of 27 calls hit a 240s timeout and were graded as routing failures. A
  timeout says nothing about routing.
- The model does not reliably obey a planted instruction. Replies that missed
  the sentinel were still plainly on-beat — *"turn it into a build-ready
  brief"*, *"benchmark ... against 50k events/s"*, *"outcome-based milestones"*.
  The detector under-reported.

**Second attempt — read the debug log.** `--log-level debug` records the actual
tool call the CLI made:

    "name": "skill", "arguments": "{\"skill\":\"atom-tdd\"}"

This is ground truth and does not depend on the model cooperating. It was
validated in both directions before use: it returned `atom-tdd` for a run known
to have invoked the skill, and `None` for a run whose log showed no skill call
at all. The sentinel was then reverted so the measurement ran against the
**unmodified** skills.

### Result (SUPERSEDED — see the re-measurement below)

| Metric | Value |
|---|---|
| Trials | 27 |
| Excluded as timeouts | 3 |
| Scored | 24 |
| Skill actually loaded | 8 (33.3%) |
| Routed to the correct beat | 8 (33.3%) |
| **Precision when a skill loaded** | **100.0%** |
| Mis-routed to the wrong beat | 0 |
| Wall clock | 10,363s |

Per beat, out of three prompts each:

| Beat | Loaded |
|---|---|
| atom-poc | 2 |
| atom-build | 2 |
| atom-discover | 1 |
| atom-plan | 1 |
| atom-tdd | 1 |
| atom-init | 1 |
| atom-spec | 0 |
| atom-ship | 0 |
| atom-review | excluded — all three timed out |

### What this meant at the time (SUPERSEDED)

**The failure mode is recall, not precision.** Not one prompt reached the wrong
beat. When a skill loads, the description keywords pick the right one every
time. The problem is that a skill loads only about a third of the time.

The remaining two thirds are the dangerous case, because they do not look like
failures. Skill *descriptions* are always present in the model's tool list, so
the model can paraphrase a beat's description convincingly without ever loading
the SKILL.md behind it. The developer gets description-shaped advice in place of
the actual workflow, with no signal that anything was skipped.

This was confirmed directly: a prompt that produced fluent TDD-flavoured advice
had a log showing `tool_counts: {"session_store_sql":1}` and no skill call.

All three `atom-review` prompts timing out is consistent rather than random —
review prompts send the agent exploring the filesystem, which is expensive from
a home directory with no repository.

---

---

## C3 (re-measured) — Beat-routing accuracy on an installed plugin **100%**

Same harness, same 27 prompts, same unmodified skills — verified byte for byte:
all nine `SKILL.md` files in the installed copy hash-match the repository. The
only substantive change is that the plugin is installed rather than live-loaded.
Two instrument fixes came with it:

- **Plugin presence is recorded per trial.** A session without the plugin has no
  Atom skill to reach, so it is excluded from the routing denominator rather
  than counted as a routing miss. This is the control the first run lacked, and
  the absence of it is what produced the 33.3%.
- **Stale logs are cleared before the run.** The previous run's logs were still
  on disk and would otherwise have been read as this run's results.

| Metric | Live-loaded (first) | Installed (re-measured) |
|---|---|---|
| Trials | 27 | 27 |
| Excluded as timeouts | 3 | 2 |
| Excluded — plugin absent | not measured | **0** |
| Scored | 24 | 25 |
| Skill actually loaded | 8 (33.3%) | **25 (100%)** |
| Routed to the correct beat | 8 (33.3%) | **25 (100%)** |
| Precision when loaded | 100% | 100% |
| Mis-routed | 0 | 0 |
| Wall clock | 10,363s | 2,357s |

Every beat scored 3 of 3 except `atom-review`, which scored 1 of 3 with the
other two lost to the 600s timeout — the same expensive-exploration behaviour
seen the first time, and still not a routing failure.

The invisible failure described above — fluent, description-shaped advice with
no skill call behind it — **did not occur once** in 25 scored trials.

**Against the pre-registered bar of >= 80%, prose routing passes at 100%.** The
bar was not moved; the defect underneath it was removed.

### What the re-measurement does not prove

- That routing is 100% in general. These prompts were written before the first
  measurement rather than tuned to pass this one, but they remain 27 prompts
  from one author against one model.
- That the installed path never drops a plugin. Zero of 25 here, and 12 of 12 in
  the F15 trials, is consistent with reliability rather than proof of it.
- Anything about a different model, a real Go repository, or a later CLI build.

---

## C4 — Do rules improve accuracy? **CANNOT BE TESTED**

Blocked by C1.

---

## Verdict

**Refuted** for the rules mechanism. **Measured, then corrected,** for routing.

Against the pre-registered bar of >= 80%, prose routing scores **100%** on an
installed plugin and passes. The 33.3% recorded first was an artifact of live
loading, not a property of the keywords.

### What Atom should do

1. **Install the plugin; do not rely on live loading.** Live loading drops the
   plugin silently, with no error logged anywhere. It is a development
   convenience only, and every measurement taken under it is suspect.
2. **Prose routing can be claimed** — with the honest caveat that it was
   measured on 27 prompts against a single model. Slash commands remain the
   explicit path when a developer wants certainty rather than a good bet.
3. **Do not ship a rules file** until the mechanism demonstrably works.
4. Re-run this harness against future CLI versions. It is repeatable:
   `python measure_routing.py run`.

## Not proven

- Whether routing improves with a different model.
- Whether rules work in any other Copilot client, or in a later CLI build.
- Whether an explicit `/atom` invocation routes more accurately than bare prose;
  every trial here used bare prose.
- Whether load rate differs inside a real Go repository, where the agent has
  project context to work from. All trials ran from an empty home directory.
