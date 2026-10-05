# Pre-registration — atom-short-namespace

Written **before** any probe was run. Do not edit after seeing results; record
outcomes in `results.md` instead.

## Falsifiable question

If Atom's plugin is renamed to `atom` and its skills are renamed to bare beat
names (`poc`, `spec`, `tdd`, …), can a developer invoke a beat as
`/atom:poc` — and what happens to the existing `/atom` router command, whose
name would then equal the plugin name?

## Claims

| ID | Claim | Confirmed when | Refuted when |
|----|-------|----------------|--------------|
| N1 | A skill `poc` inside a plugin named `atom` is invokable as `/atom:poc` | The skill body runs and the reply is `ATOM_NS_SKILL_OK` | The command is unknown, or something else answers |
| N2 | A command whose name equals the plugin name never runs | `/atom` does **not** reply `ATOM_NS_ROUTER_OK` | `/atom` replies `ATOM_NS_ROUTER_OK` |
| N3 | A command whose name differs from the plugin name still runs | `/start` replies `ATOM_NS_START_OK` | Command unknown, or body never runs |
| N4 | Commands are reachable under the plugin namespace | `/atom:start` replies `ATOM_NS_START_OK` | The command is unknown under that form |
| N5 | A namespace-qualified command named like the plugin runs | `/atom:atom` replies `ATOM_NS_ROUTER_OK` | Unknown, or something else answers |

## Verdict rule

- **Confirmed** — N1 passes. N1 is the load-bearing claim: without it there is
  no `/atom:<short-skill>` surface to ship.
- **Refuted** — N1 fails.

N2–N5 are informational: together they decide *where the `/atom` router has to
live* after the rename. They are pre-registered so the answer cannot be
rationalised afterwards.

## Method

A throwaway plugin fixture is loaded with `copilot --plugin-dir`, under an
isolated `COPILOT_HOME`, so the installed `atom-go` plugin cannot intercept any
invocation. Each probe is a separate non-interactive `copilot -p` run.

## What this spike does NOT try to prove

- Behaviour on any CLI version other than the one recorded in `results.md`.
- Behaviour when a second installed plugin also claims the name `atom`.
- That the model picks the right beat from free text. Measured separately in
  `poc/atom-routing-rules/`.
