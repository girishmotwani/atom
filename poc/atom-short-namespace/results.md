# POC Report — Short Atom Namespace

## Question

If Atom's plugin is renamed to `atom` and its skills are renamed to bare beat
names (`poc`, `spec`, `tdd`, …), can a developer invoke a beat as
`/atom:poc` — and what happens to the existing `/atom` router command, whose
name would then equal the plugin name?

## Verdict

**Confirmed for the short skill namespace; refuted for keeping the router named
`atom`.**

The pre-registered verdict rule requires N1 to pass. In the isolated
`--plugin-dir` run, `/atom:poc` returned the fixture skill's unique response,
`ATOM_NS_SKILL_OK`, so that registered claim is confirmed.

The follow-up used Atom's actual marketplace installation path in the same
isolated home. There, `/atom:poc` returned `ATOM_NS_ROUTER_OK`. The installed
router command shadows the namespaced skill, so the short namespace can ship
only if the router command is renamed or removed.

## Environment

- GitHub Copilot CLI 1.0.92

## Evidence

Verbatim output captured by the clean, isolated `--plugin-dir` probe run:

```json
[
  {
    "prompt": "/atom:poc",
    "exit_code": 0,
    "stdout": "ATOM_NS_SKILL_OK",
    "stderr": "",
    "claim": "N1"
  },
  {
    "prompt": "/atom",
    "exit_code": 0,
    "stdout": "ATOM_NS_ROUTER_OK",
    "stderr": "",
    "claim": "N2"
  },
  {
    "prompt": "/start",
    "exit_code": 0,
    "stdout": "ATOM_NS_START_OK",
    "stderr": "",
    "claim": "N3"
  },
  {
    "prompt": "/atom:start",
    "exit_code": 0,
    "stdout": "ATOM_NS_START_OK",
    "stderr": "",
    "claim": "N4"
  },
  {
    "prompt": "/atom:atom",
    "exit_code": 0,
    "stdout": "ATOM_NS_ROUTER_OK",
    "stderr": "",
    "claim": "N5"
  }
]
```

## Claim Results

| Claim | Outcome | Evidence |
|---|---|---|
| N1 | Passed | `/atom:poc` returned `ATOM_NS_SKILL_OK` |
| N2 | Refuted | `/atom` returned `ATOM_NS_ROUTER_OK` |
| N3 | Passed | `/start` returned `ATOM_NS_START_OK` |
| N4 | Passed | `/atom:start` returned `ATOM_NS_START_OK` |
| N5 | Passed | `/atom:atom` returned `ATOM_NS_ROUTER_OK` |

N2-N5 are informational and do not change the registered direct-load verdict.

Verbatim probe results from the isolated installed-marketplace run:

```json
[
  {
    "claim": "N1-installed",
    "prompt": "/atom:poc",
    "exit_code": 0,
    "stdout": "ATOM_NS_ROUTER_OK",
    "stderr": ""
  },
  {
    "claim": "N2-installed",
    "prompt": "/atom",
    "exit_code": 0,
    "stdout": "ATOM_NS_ROUTER_OK",
    "stderr": ""
  },
  {
    "claim": "N3-installed",
    "prompt": "/start",
    "exit_code": 0,
    "stdout": "I’ll initialize with the authoritative CLI guidance and repository operating rules.\n\n**Ready.** I’m GitHub Copilot CLI, powered by GPT-5.6 Sol, working in `atom-short-namespace`.\n\nDescribe the change you want, reference files with `@`, or use `/help` for available commands. Repository access to `AGENTS.md` currently requires interactive approval.",
    "stderr": ""
  }
]
```

The setup evidence in `installed-probe-results.json` shows that only
`atom@atom-ns-probe` was installed and enabled; `atom-go@atom` was absent.
Therefore the router response can be attributed to the fixture.

## What This Changes

The short skill namespace works, but the command named `atom` shadows it after
installation. The production router must move to the already-proven,
non-colliding command name `start`, making the entry point `/atom:start` and
leaving `/atom:poc`, `/atom:spec`, and the other skills unshadowed.

## Explicitly Not Covered

- Behavior on Copilot CLI versions other than 1.0.92.
- Behavior when another installed plugin also claims the `atom` name.
- Whether free-text requests route to the correct beat.
- Why installed and direct-load command resolution differ internally.
