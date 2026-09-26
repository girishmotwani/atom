# POC Results: plugin-shipped rules and beat-routing accuracy

Claims were registered in [claims.md](claims.md) before any measurement ran.
Nothing in this document moves a threshold that was set there.

Environment: GitHub Copilot CLI **1.0.89-4**, Windows, plugin `atom-go@atom`
live-loaded from a local marketplace.

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

### Result

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

### What this means

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

## C4 — Do rules improve accuracy? **CANNOT BE TESTED**

Blocked by C1.

---

## Verdict

**Refuted** for the rules mechanism. **Measured** for routing accuracy.

Against the pre-registered bar of >= 80%, prose routing scores 33.3% and fails.
The bar was not lowered to accommodate the result.

### What Atom should do

1. **Slash commands are the contract.** They are explicit, and they work. The
   documentation should say so plainly instead of implying prose is equivalent.
2. **Do not ship a rules file** until the mechanism demonstrably works.
3. **Do not claim natural-language routing as a feature.** It works one time in
   three, and its failure mode is invisible.
4. Re-run this harness against future CLI versions. It is repeatable:
   `python measure_routing.py run`.

## Not proven

- Whether routing improves with a different model.
- Whether rules work in any other Copilot client, or in a later CLI build.
- Whether an explicit `/atom` invocation routes more accurately than bare prose;
  every trial here used bare prose.
- Whether load rate differs inside a real Go repository, where the agent has
  project context to work from. All trials ran from an empty home directory.
