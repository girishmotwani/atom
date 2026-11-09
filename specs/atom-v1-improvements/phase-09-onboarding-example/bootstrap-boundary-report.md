---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-09"
verdict: "Confirmed"
status: "accepted-guidance-repair-authorized"
evidence_method: "approved normal-user command-boundary validation"
---

# Bootstrap Normal-Environment Boundary Report

## The Question

Can the approved Ubuntu bootstrap recipe establish and reuse both usable Atom
command roles at $HOME/.local/share/atom-cli/venv with normal user HOME/pip/Git
configuration, while preserving named existing defaults and installations?

## Verdict

**Confirmed for this observed Ubuntu normal-user boundary only.** One installation
at the developer-selected shared prefix supplied both usable command roles.
Real init persisted its actual baseline, both UTF-8 writer round trips matched,
and read-only reuse preserved metadata and named defaults/installations.

This answers the [approved boundary brief](bootstrap-boundary-brief.md), not the
original usability question. The [first rehearsal](poc-report.md) remains
Inconclusive. Source guidance is still unchanged.

## Approval, Context And Counts

The developer explicitly selected
"Approve the bounded run and named fixture-writer forms", then requested
"lets proeed". This covers only the named run and its new fixture's writer forms.
The [repair spec](bootstrap-repair-spec.md) remains approved subject to accepted
boundary evidence; the [earlier controlled proof](bootstrap-repair-report.md)
retains its separate conditions.

| Observation | Actual value |
|---|---|
| Started UTC | 2026-11-09T10:22:35.535809+00:00 |
| Finished UTC | 2026-11-09T10:22:49.178319+00:00 |
| Monotonic elapsed seconds | 13.642572425000253 |
| Approved cap seconds | 900 |
| Runs / venv creations / install invocations | 1 / 1 / 1 |
| Recorded top-level commands | 34 |
| Exit 0 | 22 |
| Expected exit 1 | 12 |
| CLI distribution | atom-cli 0.1.0 |
| Public source commit | 50622abf2b9f58bcfc2c9d538b7292cf0689ceee |
| Built wheel SHA-256 | e356c6062808087453c02bb9dfae349acc260b14ba10449c3e1dab316690b991 |

Expected exit 1 means exactly two missing-Atom module probes and ten pip
missing-key probes, each with its captured absence diagnostic. No unexpected
command failed or timed out. These negative probes are not hidden as exit 0.
Elapsed time is run context, not a performance benchmark.

The observer was a private Python command executor, not atom poc run or a Go
algorithm spike. No Copilot, agents or model calls ran. Existing Python baseline
evidence was reused rather than rerunning unchanged tests as installation proof.

## Normal User Context And Scheme Checks

The child's HOME remained /home/girish. The executor copied the ordinary
process environment, retaining normal pip/Git configuration. It did not supply
the earlier proof's private HOME, disabled-config settings, credential-free
environment reconstruction or virtualenv-required pip setting.

Only these explicit child overrides were applied:

```json
{
  "GOTOOLCHAIN": "local",
  "GIT_TERMINAL_PROMPT": "0",
  "TMPDIR": "/home/girish/atom-phase09-bootstrap-boundary-proof/tmp",
  "GOCACHE": "/home/girish/atom-phase09-bootstrap-boundary-proof/go-cache",
  "GOMODCACHE": "/home/girish/atom-phase09-bootstrap-boundary-proof/go-mod-cache"
}
```


They make Git noninteractive and keep Go/tool temporary work bounded. They do
not disable normal pip/Git configuration or establish a filesystem sandbox.
Ordinary configuration may still direct ordinary cache/helper/temporary writes.

No relevant install-scheme environment key was set. The exact checked keys were
PIP_TARGET, PIP_PREFIX, PIP_ROOT, PIP_USER and PIP_PYTHON. Each selected pip
global/install target/prefix/root/user/python key was absent with its actual
missing-key diagnostic. The interpreter prefix and pip location were verified
inside the chosen venv before the sole install.

```json
{
  "global.target": "absent",
  "global.prefix": "absent",
  "global.root": "absent",
  "global.user": "absent",
  "global.python": "absent",
  "install.target": "absent",
  "install.prefix": "absent",
  "install.root": "absent",
  "install.user": "absent",
  "install.python": "absent"
}
```


This observed absence supports this ordinary configuration only; it does not
test active redirects, all config precedence combinations or hostile settings.
No general configuration audit or authentication-file read was performed.

## Complete Command Evidence

The following argv, working directories, exit codes and stdout/stderr are copied
from the captured execution record. Empty fenced blocks mean empty streams.
All output is included; timing values are the recorded values. Writer input is
also preserved rather than inferred from the output file.

### 1. python-version

Working directory: `/home/girish`

Exact argv:

```json
[
  "python3",
  "--version"
]
```

Exit code: 0; duration seconds: 0.0023518289999628905.

stdout:

```text
Python 3.12.3
```

stderr:

```text
```

### 2. go-version

Working directory: `/home/girish`

Exact argv:

```json
[
  "go",
  "version"
]
```

Exit code: 0; duration seconds: 0.1135658120001608.

stdout:

```text
go version go1.22.2 linux/amd64
```

stderr:

```text
```

### 3. git-version

Working directory: `/home/girish`

Exact argv:

```json
[
  "git",
  "--version"
]
```

Exit code: 0; duration seconds: 0.002330155999516137.

stdout:

```text
git version 2.43.0
```

stderr:

```text
```

### 4. system-pip-version

Working directory: `/home/girish`

Exact argv:

```json
[
  "python3",
  "-m",
  "pip",
  "--version"
]
```

Exit code: 0; duration seconds: 0.40583632400011993.

stdout:

```text
pip 24.0 from /usr/lib/python3/dist-packages/pip (python 3.12)
```

stderr:

```text
```

### 5. preflight-atom.cli

Working directory: `/home/girish`

Exact argv:

```json
[
  "python3",
  "-m",
  "atom.cli",
  "--help"
]
```

Exit code: 1; duration seconds: 0.027127009998366702.

stdout:

```text
```

stderr:

```text
/usr/bin/python3: Error while finding module specification for 'atom.cli' (ModuleNotFoundError: No module named 'atom')
```

### 6. preflight-atom.artifact_cli

Working directory: `/home/girish`

Exact argv:

```json
[
  "python3",
  "-m",
  "atom.artifact_cli",
  "--help"
]
```

Exit code: 1; duration seconds: 0.023023008998279693.

stdout:

```text
```

stderr:

```text
/usr/bin/python3: Error while finding module specification for 'atom.artifact_cli' (ModuleNotFoundError: No module named 'atom')
```

### 7. create-shared-venv

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof`

Exact argv:

```json
[
  "python3",
  "-m",
  "venv",
  "/home/girish/.local/share/atom-cli/venv"
]
```

Exit code: 0; duration seconds: 2.429266725001071.

stdout:

```text
```

stderr:

```text
```

### 8. verify-venv-prefix

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-c",
  "import json,sys; print(json.dumps({'prefix':sys.prefix,'base_prefix':sys.base_prefix}))"
]
```

Exit code: 0; duration seconds: 0.016458527999930084.

stdout:

```text
{"prefix": "/home/girish/.local/share/atom-cli/venv", "base_prefix": "/usr"}
```

stderr:

```text
```

### 9. venv-pip-version

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "--version"
]
```

Exit code: 0; duration seconds: 0.18238190799820586.

stdout:

```text
pip 24.0 from /home/girish/.local/share/atom-cli/venv/lib/python3.12/site-packages/pip (python 3.12)
```

stderr:

```text
```

### 10. scheme-global.target

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "global.target"
]
```

Exit code: 1; duration seconds: 0.20880925500023295.

stdout:

```text
```

stderr:

```text
ERROR: No such key - global.target
```

### 11. scheme-global.prefix

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "global.prefix"
]
```

Exit code: 1; duration seconds: 0.1854648830012593.

stdout:

```text
```

stderr:

```text
ERROR: No such key - global.prefix
```

### 12. scheme-global.root

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "global.root"
]
```

Exit code: 1; duration seconds: 0.1840446830028668.

stdout:

```text
```

stderr:

```text
ERROR: No such key - global.root
```

### 13. scheme-global.user

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "global.user"
]
```

Exit code: 1; duration seconds: 0.19118738699762616.

stdout:

```text
```

stderr:

```text
ERROR: No such key - global.user
```

### 14. scheme-global.python

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "global.python"
]
```

Exit code: 1; duration seconds: 0.20812348099934752.

stdout:

```text
```

stderr:

```text
ERROR: No such key - global.python
```

### 15. scheme-install.target

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "install.target"
]
```

Exit code: 1; duration seconds: 0.18559783399905427.

stdout:

```text
```

stderr:

```text
ERROR: No such key - install.target
```

### 16. scheme-install.prefix

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "install.prefix"
]
```

Exit code: 1; duration seconds: 0.214346402000956.

stdout:

```text
```

stderr:

```text
ERROR: No such key - install.prefix
```

### 17. scheme-install.root

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "install.root"
]
```

Exit code: 1; duration seconds: 0.21556982699985383.

stdout:

```text
```

stderr:

```text
ERROR: No such key - install.root
```

### 18. scheme-install.user

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "install.user"
]
```

Exit code: 1; duration seconds: 0.2044922469976882.

stdout:

```text
```

stderr:

```text
ERROR: No such key - install.user
```

### 19. scheme-install.python

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "config",
  "get",
  "install.python"
]
```

Exit code: 1; duration seconds: 0.1928519069988397.

stdout:

```text
```

stderr:

```text
ERROR: No such key - install.python
```

### 20. install-pinned-public-package

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "pip",
  "install",
  "--no-cache-dir",
  "--no-input",
  "git+https://github.com/girishmotwani/atom.git@50622abf2b9f58bcfc2c9d538b7292cf0689ceee#subdirectory=tools"
]
```

Exit code: 0; duration seconds: 5.43002504299875.

stdout:

```text
Collecting git+https://github.com/girishmotwani/atom.git@50622abf2b9f58bcfc2c9d538b7292cf0689ceee#subdirectory=tools
  Cloning https://github.com/girishmotwani/atom.git (to revision 50622abf2b9f58bcfc2c9d538b7292cf0689ceee) to /home/girish/atom-phase09-bootstrap-boundary-proof/tmp/pip-req-build-rg6qhk4u
  Resolved https://github.com/girishmotwani/atom.git to commit 50622abf2b9f58bcfc2c9d538b7292cf0689ceee
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Building wheels for collected packages: atom-cli
  Building wheel for atom-cli (pyproject.toml): started
  Building wheel for atom-cli (pyproject.toml): finished with status 'done'
  Created wheel for atom-cli: filename=atom_cli-0.1.0-py3-none-any.whl size=249840 sha256=e356c6062808087453c02bb9dfae349acc260b14ba10449c3e1dab316690b991
  Stored in directory: /home/girish/atom-phase09-bootstrap-boundary-proof/tmp/pip-ephem-wheel-cache-8qecouq0/wheels/5e/03/40/28a2ee2ae1ac574524e1517d5fda5f416e33db40c655c53fce
Successfully built atom-cli
Installing collected packages: atom-cli
Successfully installed atom-cli-0.1.0
```

stderr:

```text
  Running command git clone --filter=blob:none --quiet https://github.com/girishmotwani/atom.git /home/girish/atom-phase09-bootstrap-boundary-proof/tmp/pip-req-build-rg6qhk4u
  Running command git rev-parse -q --verify 'sha^50622abf2b9f58bcfc2c9d538b7292cf0689ceee'
  Running command git fetch -q https://github.com/girishmotwani/atom.git 50622abf2b9f58bcfc2c9d538b7292cf0689ceee
```

### 21. installed-metadata

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-c",
  "\nimport importlib.metadata as metadata\nimport json, sys\ndistribution = metadata.distribution(\"atom-cli\")\nprint(json.dumps({\n    \"name\": distribution.metadata[\"Name\"],\n    \"version\": distribution.version,\n    \"direct_url\": json.loads(distribution.read_text(\"direct_url.json\")),\n    \"wheel_metadata\": distribution.read_text(\"WHEEL\"),\n    \"entry_points\": {p.name: p.value for p in distribution.entry_points if p.group == \"console_scripts\"},\n    \"installed_distributions\": sorted((d.metadata[\"Name\"], d.version) for d in metadata.distributions()),\n    \"prefix\": sys.prefix, \"base_prefix\": sys.base_prefix,\n}))\n"
]
```

Exit code: 0; duration seconds: 0.05051674899732461.

stdout:

```text
{"name": "atom-cli", "version": "0.1.0", "direct_url": {"subdirectory": "tools", "url": "https://github.com/girishmotwani/atom.git", "vcs_info": {"commit_id": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "requested_revision": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "vcs": "git"}}, "wheel_metadata": "Wheel-Version: 1.0\nGenerator: setuptools (84.2.1)\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n", "entry_points": {"atom": "atom.cli:main", "atom-write-artifact": "atom.artifact_cli:main"}, "installed_distributions": [["atom-cli", "0.1.0"], ["pip", "24.0"]], "prefix": "/home/girish/.local/share/atom-cli/venv", "base_prefix": "/usr"}
```

stderr:

```text
```

### 22. atom-entry-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/atom",
  "--help"
]
```

Exit code: 0; duration seconds: 0.08797835400037002.

stdout:

```text
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...

Atom -- prove it, describe it, then build it.

positional arguments:
  {check,poc,init,status,review,ship,setup-path}
    check               Run every Go quality gate and report the result.
    poc                 Create, run and list throwaway spikes.
    init                Set up Atom, or confirm an existing matching project
                        without changes.
    status              Show the current phase, recent activity, and any
                        problems.
    review              Ask several models to review a diff and merge what
                        they agree on.
    ship                Turn the current branch's finished phase into a pull
                        request.
    setup-path          Add Atom's installed commands to the Windows user PATH
                        (opt-in).

options:
  -h, --help            show this help message and exit
```

stderr:

```text
```

### 23. writer-entry-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/atom-write-artifact",
  "--help"
]
```

Exit code: 0; duration seconds: 0.0373924449995684.

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr:

```text
```

### 24. atom-module-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "atom.cli",
  "--help"
]
```

Exit code: 0; duration seconds: 0.08086298299895134.

stdout:

```text
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...

Atom -- prove it, describe it, then build it.

positional arguments:
  {check,poc,init,status,review,ship,setup-path}
    check               Run every Go quality gate and report the result.
    poc                 Create, run and list throwaway spikes.
    init                Set up Atom, or confirm an existing matching project
                        without changes.
    status              Show the current phase, recent activity, and any
                        problems.
    review              Ask several models to review a diff and merge what
                        they agree on.
    ship                Turn the current branch's finished phase into a pull
                        request.
    setup-path          Add Atom's installed commands to the Windows user PATH
                        (opt-in).

options:
  -h, --help            show this help message and exit
```

stderr:

```text
```

### 25. writer-module-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "atom.artifact_cli",
  "--help"
]
```

Exit code: 0; duration seconds: 0.0371356450013991.

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr:

```text
```

### 26. create-fixture-go-module

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "go",
  "mod",
  "init",
  "example.com/atom-bootstrap-boundary-proof"
]
```

Exit code: 0; duration seconds: 0.14989331899778335.

stdout:

```text
```

stderr:

```text
go: creating new go.mod: module example.com/atom-bootstrap-boundary-proof
```

### 27. initialize-fixture

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/atom",
  "init"
]
```

Exit code: 0; duration seconds: 0.49638273999880766.

stdout:

```text
Initialised /home/girish/atom-phase09-bootstrap-boundary-proof/module/.atom
  module:    example.com/atom-bootstrap-boundary-proof
  approvals: 0
  local instructions: /home/girish/atom-phase09-bootstrap-boundary-proof/module/.github/copilot-instructions.md
  specs:     /home/girish/atom-phase09-bootstrap-boundary-proof/module/specs
  poc:       /home/girish/atom-phase09-bootstrap-boundary-proof/module/poc
  build:     go build ./...
  test:      go test ./...
             no makefile; using Go defaults
  baseline:  /home/girish/atom-phase09-bootstrap-boundary-proof/module/.atom/baseline.json

Untouched baseline (race detector skipped):
atom check /home/girish/atom-phase09-bootstrap-boundary-proof/module

  PASS  build  go build ./... passed (0.1s)
  FAIL  vet    go vet ./... failed with exit code 1 (0.1s)

        go: warning: "./..." matched no packages
        no packages to vet

  PASS  fmt    gofmt -l . reported no unformatted files (0.0s)
  FAIL  test   go test ./... failed with exit code 1 (0.1s)

        go: warning: "./..." matched no packages
        no packages to test

  SKIP  race   Race detector disabled for this run (0.0s)

  FAILED in 0.4s

Atom derives where you are from specs/. To see it:
  atom status

Atom starts by proving things, not describing them:
  atom poc new <slug> --question "..."
```

stderr:

```text
```

### 28. write-findings.md

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/atom-write-artifact",
  "specs/bootstrap-boundary-proof/findings.md"
]
```

Exit code: 0; duration seconds: 0.0384764289992745.

Complete UTF-8 stdin:

```text
# Bootstrap Boundary Fixture Findings

Synthetic command fixture, not the expense CLI.
UTF-8 round trip: café.
```

Input SHA-256: af080f8db46b91babf889389d5494038e23e8dae41597f4c09d44d4b49498b2b.

stdout:

```text
Wrote /home/girish/atom-phase09-bootstrap-boundary-proof/module/specs/bootstrap-boundary-proof/findings.md
```

stderr:

```text
```

### 29. write-decisions.md

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "atom.artifact_cli",
  "specs/bootstrap-boundary-proof/decisions.md"
]
```

Exit code: 0; duration seconds: 0.03546871300204657.

Complete UTF-8 stdin:

```text
# Bootstrap Boundary Fixture Decisions

Use only the two approved fixture writer forms.
Real conclusions belong in the parent boundary report.
```

Input SHA-256: b3771962016355589e475ea42662b1219488c84bb67df63506986daa64c3ee20.

stdout:

```text
Wrote /home/girish/atom-phase09-bootstrap-boundary-proof/module/specs/bootstrap-boundary-proof/decisions.md
```

stderr:

```text
```

### 30. reuse-atom-entry-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/atom",
  "--help"
]
```

Exit code: 0; duration seconds: 0.08472862799681025.

stdout:

```text
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...

Atom -- prove it, describe it, then build it.

positional arguments:
  {check,poc,init,status,review,ship,setup-path}
    check               Run every Go quality gate and report the result.
    poc                 Create, run and list throwaway spikes.
    init                Set up Atom, or confirm an existing matching project
                        without changes.
    status              Show the current phase, recent activity, and any
                        problems.
    review              Ask several models to review a diff and merge what
                        they agree on.
    ship                Turn the current branch's finished phase into a pull
                        request.
    setup-path          Add Atom's installed commands to the Windows user PATH
                        (opt-in).

options:
  -h, --help            show this help message and exit
```

stderr:

```text
```

### 31. reuse-writer-entry-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/atom-write-artifact",
  "--help"
]
```

Exit code: 0; duration seconds: 0.03587468800105853.

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr:

```text
```

### 32. reuse-atom-module-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "atom.cli",
  "--help"
]
```

Exit code: 0; duration seconds: 0.0939543490021606.

stdout:

```text
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...

Atom -- prove it, describe it, then build it.

positional arguments:
  {check,poc,init,status,review,ship,setup-path}
    check               Run every Go quality gate and report the result.
    poc                 Create, run and list throwaway spikes.
    init                Set up Atom, or confirm an existing matching project
                        without changes.
    status              Show the current phase, recent activity, and any
                        problems.
    review              Ask several models to review a diff and merge what
                        they agree on.
    ship                Turn the current branch's finished phase into a pull
                        request.
    setup-path          Add Atom's installed commands to the Windows user PATH
                        (opt-in).

options:
  -h, --help            show this help message and exit
```

stderr:

```text
```

### 33. reuse-writer-module-help

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-m",
  "atom.artifact_cli",
  "--help"
]
```

Exit code: 0; duration seconds: 0.04008970699942438.

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr:

```text
```

### 34. reused-metadata

Working directory: `/home/girish/atom-phase09-bootstrap-boundary-proof/module`

Exact argv:

```json
[
  "/home/girish/.local/share/atom-cli/venv/bin/python",
  "-c",
  "\nimport importlib.metadata as metadata\nimport json, sys\ndistribution = metadata.distribution(\"atom-cli\")\nprint(json.dumps({\n    \"name\": distribution.metadata[\"Name\"],\n    \"version\": distribution.version,\n    \"direct_url\": json.loads(distribution.read_text(\"direct_url.json\")),\n    \"wheel_metadata\": distribution.read_text(\"WHEEL\"),\n    \"entry_points\": {p.name: p.value for p in distribution.entry_points if p.group == \"console_scripts\"},\n    \"installed_distributions\": sorted((d.metadata[\"Name\"], d.version) for d in metadata.distributions()),\n    \"prefix\": sys.prefix, \"base_prefix\": sys.base_prefix,\n}))\n"
]
```

Exit code: 0; duration seconds: 0.05517544599933899.

stdout:

```text
{"name": "atom-cli", "version": "0.1.0", "direct_url": {"subdirectory": "tools", "url": "https://github.com/girishmotwani/atom.git", "vcs_info": {"commit_id": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "requested_revision": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "vcs": "git"}}, "wheel_metadata": "Wheel-Version: 1.0\nGenerator: setuptools (84.2.1)\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n", "entry_points": {"atom": "atom.cli:main", "atom-write-artifact": "atom.artifact_cli:main"}, "installed_distributions": [["atom-cli", "0.1.0"], ["pip", "24.0"]], "prefix": "/home/girish/.local/share/atom-cli/venv", "base_prefix": "/usr"}
```

stderr:

```text
```

## Installed Metadata And Actual Writer Results

The distribution version is not the workflow plugin version. WHEEL metadata
records the build generator; build-tool and transitive inputs are not all pinned
by the source commit. A successful rebuild does not claim reproducible wheel bytes.

```json
{
  "name": "atom-cli",
  "version": "0.1.0",
  "direct_url": {
    "subdirectory": "tools",
    "url": "https://github.com/girishmotwani/atom.git",
    "vcs_info": {
      "commit_id": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee",
      "requested_revision": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee",
      "vcs": "git"
    }
  },
  "wheel_metadata": "Wheel-Version: 1.0\nGenerator: setuptools (84.2.1)\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n",
  "entry_points": {
    "atom": "atom.cli:main",
    "atom-write-artifact": "atom.artifact_cli:main"
  },
  "installed_distributions": [
    [
      "atom-cli",
      "0.1.0"
    ],
    [
      "pip",
      "24.0"
    ]
  ],
  "prefix": "/home/girish/.local/share/atom-cli/venv",
  "base_prefix": "/usr"
}
```

```json
{
  "findings.md": {
    "byte_match": true,
    "bytes": 112,
    "expected_sha256": "af080f8db46b91babf889389d5494038e23e8dae41597f4c09d44d4b49498b2b",
    "actual_sha256": "af080f8db46b91babf889389d5494038e23e8dae41597f4c09d44d4b49498b2b"
  },
  "decisions.md": {
    "byte_match": true,
    "bytes": 143,
    "expected_sha256": "b3771962016355589e475ea42662b1219488c84bb67df63506986daa64c3ee20",
    "actual_sha256": "b3771962016355589e475ea42662b1219488c84bb67df63506986daa64c3ee20"
  }
}
```

The findings payload contains U+00E9; both exact byte comparisons passed.
Writer entry-point help alone was not used as a proxy for actual writing.

## Onboarding And Honest Empty-Module Baseline

Init returned 0 for completed initialization, not for passing Go gates. The new
fixture had no Go implementation: vet/test failed for no packages, build emitted
its no-packages warning, fmt passed and initial-baseline race was skipped.
No Go code was inserted to hide those results. This is not a phase-completion
atom check claim or proof that the expense CLI works.

Actual persisted baseline:

```json
{
  "directory": "/home/girish/atom-phase09-bootstrap-boundary-proof/module",
  "exit_code": 1,
  "gates": [
    {
      "command_exit_code": 0,
      "command_outcome": "completed",
      "details": "go: warning: \"./...\" matched no packages\n",
      "duration_seconds": 0.148,
      "name": "build",
      "required": true,
      "status": "passed",
      "summary": "go build ./... passed"
    },
    {
      "command_exit_code": 1,
      "command_outcome": "completed",
      "details": "go: warning: \"./...\" matched no packages\nno packages to vet\n",
      "duration_seconds": 0.138,
      "name": "vet",
      "required": true,
      "status": "failed",
      "summary": "go vet ./... failed with exit code 1"
    },
    {
      "command_exit_code": 0,
      "command_outcome": "completed",
      "details": "",
      "duration_seconds": 0.005,
      "name": "fmt",
      "required": true,
      "status": "passed",
      "summary": "gofmt -l . reported no unformatted files"
    },
    {
      "command_exit_code": null,
      "command_outcome": null,
      "details": "go: warning: \"./...\" matched no packages\nno packages to test\n",
      "duration_seconds": 0.108,
      "name": "test",
      "required": true,
      "status": "failed",
      "summary": "go test ./... failed with exit code 1"
    },
    {
      "command_exit_code": null,
      "command_outcome": null,
      "details": "",
      "duration_seconds": 0.0,
      "name": "race",
      "required": true,
      "status": "skipped",
      "summary": "Race detector disabled for this run"
    }
  ],
  "passed": false,
  "schema_version": 1,
  "total_duration_seconds": 0.398,
  "warnings": []
}
```

Named onboarding files were read and retained in private evidence:

| File | UTF-8 bytes | SHA-256 |
|---|---|---|
| .atom/config.json | 137 | 17206f746859319f305f18da0d8e21826eea2c25e4949a45de709f2576418727 |
| .atom/baseline.json | 1676 | eb496c343e4c7c1832b026024acea119975a2869995a8cf5353cbc586d40dc7e |
| .atom/atom/manifest.json | 113 | 156f5bad662a3817dc1b42249e381d7b98bc644bd812b9eb8e02ebeb4a8215b9 |
| .github/copilot-instructions.md | 192 | 8c370b1221f2712cb3d5989f18b9b1f22f0cea05ed54006444cc42a3830b848d |
| .gitignore | 220 | 2e8a6d4aeb6d257299fa4a331bbbe442f9823d56d9627de9eb8227a8b5e5b543 |

The module config names example.com/atom-bootstrap-boundary-proof, not the expense CLI.

## Reuse And Named Preservation

The second four-form help/metadata pass invoked no installer.
Installed metadata and both entry-point hashes were identical before and after.
Resolved Python/pip/Go/Git/Atom commands, known Copilot binaries, PATH and named
shell-profile fingerprints matched the pre-run snapshot. The user-owned venv
and disposable proof directory remain available; neither was deleted.

Recorded before/after comparison inputs:

```json
{
  "resolved_commands": {
    "python": null,
    "python3": "/usr/bin/python3",
    "pip": "/usr/bin/pip",
    "go": "/usr/bin/go",
    "git": "/usr/bin/git",
    "atom": null,
    "atom-write-artifact": null
  },
  "command_hashes": {
    "python": null,
    "python3": "e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f",
    "pip": "6d1f19b17ef3ab9b6d3532be2198766bb1709c83da6a6684152b8af1930da6fa",
    "go": "89b81bd72c27404ccfd701c136b7e3ace9a4ccb26d96d97e874b48829aed27a1",
    "git": "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668",
    "atom": null,
    "atom-write-artifact": null
  },
  "profile_hashes": {
    ".profile": "28b4a453b68dde64f814e94bab14ee651f4f162e15dd9920490aa1d49f05d2a4",
    ".bashrc": "210b69b6cb59d242902d7982773121321165d68e2aa05c57800536d9c2a44584",
    ".bash_profile": null,
    ".zshrc": null
  },
  "copilot_hashes": {
    "old": "927f8a3080186770b160a311b736bb40438a8f277ead9bc86ff97f7b4e983bbe",
    "pinned": "985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4"
  },
  "path_sha256": "77c8b9d160b3025813fbaf702c2cacc0a0d6714f11eb7a8776f40500035250a5"
}
```

Entry-point hashes, unchanged:

```json
{
  "atom": "f6e090275203dc7d247c7dd80c7ec8f988522f1f84c92b6390ea60d8e4fb301e",
  "writer": "8291abd2873fb233929fef5fd5f3e4bd6b52ca81db648396b326ef028247261b"
}
```

The comparison covers named files/defaults, not every filesystem write,
every environment or every concurrent user action. No shell activation or
profile/PATH/authentication/system-Python change was made.

## Evidence Identity And Retention

Complete raw outputs, exact inputs, metadata, generated named file contents and
comparison records remain in the private session files. A Linux copy is retained
at $HOME/atom-phase09-bootstrap-boundary-proof/run-evidence.json.

| Private session file | SHA-256 |
|---|---|
| phase09-bootstrap-boundary.json | 9ce55800fef3982fc2fccb4a0524f97795c477b6cf1dee048367c904462245f0 |
| phase09-bootstrap-boundary.stdout.json | 3e09bdec83abe617ba0472a4092a13fe31c2bbeeb60439499b3192587721489b |
| phase09-bootstrap-boundary.stderr.log | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| phase09-bootstrap-boundary.linux.py | 0e0d5d167209d59d7664a72ca476e61701e4f24eabea860826ae03d0974a07aa |
| phase09-run-bootstrap-boundary.py | 83bff7ef98e871fd7b2c9e6fd6205c3565ae042e81dc6edaa85ed8b20d9c2b16 |

No credential/token pattern was found in the captured report material; normal
configuration itself was not dumped. Preserve raw evidence privately if later
review discovers sensitive output rather than publishing it.

## What We Learned And Explicit Limits

The private-HOME control was not required for this observed normal-user setup:
the selected external venv supplied both command roles with unchanged ordinary
pip/Git configuration. No non-secret install-scheme redirects were observed.
There was no new functional bootstrap defect; the empty-module gate failures
were the expected disclosed baseline, not a repaired or waived failure.

Not covered: active custom install redirects, partial/unsafe destinations,
concurrent installers, arbitrary editable environments, Windows/macOS provisioning,
future moving-public-source compatibility, all filesystem mutations, installed
plugin delivery, actual agent route compliance, genuine-newcomer UX or the
expense-summary CLI. The original recording and frozen recipe are unchanged.

## Recommendation And Gate

Accept this bounded result and proceed to the already approved three-document
repair: canonical bootstrap reference, byte-identical packaged copy, and a small
README clarification/link. No material recipe change was needed.

Alternative: keep the repair blocked if more environment evidence is required;
name the additional boundary rather than silently extending this run.
This result is not approval for another run, a live retry, plugin refresh,
commit, push or release. Source edits have not begun. Present this report and
wait for result acceptance before documentation implementation.

## Completeness

- [x] Question copied verbatim; source pin and approved conditions preserved.
- [x] One actual run/install; all commands and expected negative probes retained.
- [x] Normal HOME/config context, pre-install scheme checks and limited overrides.
- [x] Both actual writers, real persisted baseline and check-only reuse verified.
- [x] Named preservation compared; private evidence and environment retained.
- [x] Limits and implementation/rehearsal/publication gates explicit.
- [x] Developer accepts this bounded result before documentation implementation.


## Result Accepted; Guidance Repair Authorized: 2026-11-09

The developer selected exactly:
"Accept result; proceed with approved guidance repair".

Accept this Confirmed result only for the observed normal-user Ubuntu boundary.
Proceed with the already approved three-document spec: canonical and packaged
bootstrap guidance plus the small README clarification/link. Preserve its working
package and Windows behavior, run the scoped documentation/packaging checks, and
re-gate material changes. No further experiment, live rehearsal, plugin refresh,
commit, push or release is authorized. Source guidance is not yet implemented
when recording this acceptance; the original trial remains Inconclusive.
