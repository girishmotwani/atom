# Pre-registration — copilot-plugin-surface

Written **before** any `copilot plugin install` was run. Do not edit after
seeing results; record outcomes in `results.md` instead.

## Falsifiable question

Can Atom ship as a single Agent Plugins 1.0 plugin such that one
`copilot plugin install` gives a developer Atom's skills **and** `/atom-*`
slash commands inside Copilot CLI — with no bespoke `atom init` injection
step and no relocation of Atom's existing `skills/atom-*/` directories?

## Claims

| ID | Claim | Confirmed when | Refuted when |
|----|-------|----------------|--------------|
| C1 | A plugin installs from a local path | `copilot plugin list` names `atom-probe` | Install errors, or name absent |
| C2 | Skills at plugin-root `skills/NAME/SKILL.md` are discovered | `copilot skill list` names `atom-probe-skill` | Skill absent from the list |
| C3 | `com.github.copilot/commands/NAME.md` registers a slash command | `/atom-probe` is invokable and its body executes | Command unknown, or body never runs |
| C4 | `com.github.copilot/agents/NAME.agent.md` registers an agent | Agent `atom-probe-agent` is selectable | Agent absent |

## Verdict rule

- **Confirmed** — C1, C2 and C3 all pass. C4 is informational.
- **Refuted** — any of C1, C2, C3 fails.

C3 is the load-bearing claim: it is the only one that delivers the
"`/atom-poc` alongside `/model`" experience that motivated this spike.

## What this spike does NOT try to prove

- That the model reliably *chooses* an Atom command from a free-text
  description. That is a separate, model-dependent question.
- That `skills/` and the Python `tools/` package can be installed together.
- Anything about install from a GitHub remote rather than a local path.
