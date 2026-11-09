---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-08"
verdict: "Confirmed"
status: "accepted-short-repair-spec-authorized"
evidence_method: "bounded deterministic command validation"
---

# Bootstrap Repair Report

## The Question

Can Ubuntu's existing Python 3 establish and reuse both Atom command boundaries
through an isolated installation that supports first initialization of a fresh
Go module without changing system Python, shell defaults or existing installations?

## Verdict

**Confirmed for the bounded Ubuntu command recipe.** One isolated installation
of the pinned public Atom source supplied both entry-point and Python-module
forms. Real artifact writes matched the complete UTF-8 inputs, first initialization
persisted its actual baseline, and check-only reuse preserved package metadata,
executables and known system/shell/Copilot fingerprints.

**The Go baseline failed**, as expected for the deliberately empty fixture:
vet and test found no packages; race was skipped for the initial baseline.
This is not a green Go project, passing expense-summary implementation or
completed Phase 09. The [original user rehearsal](poc-report.md) remains
Inconclusive. Its frozen recipe and failure recording are unchanged.

## Run Context

The developer approved the [bounded brief](bootstrap-repair-brief.md) and separately
approved both dedicated writer forms for the disposable module. No approval was
simulated, borrowed from another repository or converted into implementation consent.

- Started: 2026-11-08T14:50:47.924857+00:00.
- Finished: 2026-11-08T14:51:03.958246+00:00.
- Monotonic elapsed seconds: 16.569436527999642, below the approved 900-second cap.
- Existing Ubuntu WSL, ordinary user; Python 3.12.3, pip 24.0, Go 1.22.2, git 2.43.0.
- Local Atom checkout HEAD: 4434cdf71b3eaab869f9acf276fa85c1bb9f969c.
- Tested public source: girishmotwani/atom at 50622abf2b9f58bcfc2c9d538b7292cf0689ceee, not unmerged local code.
- One fresh venv and one public pip-install invocation; no pip upgrade/retry.
- Actual installed distribution: atom-cli 0.1.0; this is distinct
  from the pre-existing workflow plugin's 0.2.0 version.
- 17 recorded top-level commands returned 0. atom init's successful
  initialization exit must not be confused with its recorded failing Go baseline.
- No Copilot invocation, live session, extra agent, review batch, login or model call.

## Command Evidence

These are the actual argument lists, complete supplied input, stdout and stderr
captured from the single run. Empty streams are labeled, not filled with invented
success output. Reuse repeats only help/metadata checks, never an installer.

### create-venv

Actual argv rendered for readability (no shell was used); exit 0:

```text
python3 -m venv /home/girish/atom-phase09-bootstrap-proof/.venv
```

stdout: empty.

stderr: empty.

### install-pinned-public-package

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -m pip install --no-cache-dir 'git+https://github.com/girishmotwani/atom.git@50622abf2b9f58bcfc2c9d538b7292cf0689ceee#subdirectory=tools'
```

stdout:

```text
Collecting git+https://github.com/girishmotwani/atom.git@50622abf2b9f58bcfc2c9d538b7292cf0689ceee#subdirectory=tools
  Cloning https://github.com/girishmotwani/atom.git (to revision 50622abf2b9f58bcfc2c9d538b7292cf0689ceee) to ./tmp/pip-req-build-whi1r9mf
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
  Created wheel for atom-cli: filename=atom_cli-0.1.0-py3-none-any.whl size=249840 sha256=121477edc01d7aeb6fecbc9c423e0799fb5e4f6ea8c4cbc222d04316764cce8d
  Stored in directory: /home/girish/atom-phase09-bootstrap-proof/tmp/pip-ephem-wheel-cache-yx9anbt9/wheels/5e/03/40/28a2ee2ae1ac574524e1517d5fda5f416e33db40c655c53fce
Successfully built atom-cli
Installing collected packages: atom-cli
Successfully installed atom-cli-0.1.0
```

stderr:

```text
  Running command git clone --filter=blob:none --quiet https://github.com/girishmotwani/atom.git /home/girish/atom-phase09-bootstrap-proof/tmp/pip-req-build-whi1r9mf
  Running command git rev-parse -q --verify 'sha^50622abf2b9f58bcfc2c9d538b7292cf0689ceee'
  Running command git fetch -q https://github.com/girishmotwani/atom.git 50622abf2b9f58bcfc2c9d538b7292cf0689ceee
```

### installed-metadata

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -c '
import importlib.metadata as metadata
import json, sys
distribution = metadata.distribution("atom-cli")
print(json.dumps({
    "name": distribution.metadata["Name"],
    "version": distribution.version,
    "direct_url": json.loads(distribution.read_text("direct_url.json")),
    "entry_points": {point.name: point.value for point in distribution.entry_points if point.group == "console_scripts"},
    "installed_distributions": sorted((item.metadata["Name"], item.version) for item in metadata.distributions()),
    "isolated": sys.prefix != sys.base_prefix,
    "prefix": sys.prefix,
    "base_prefix": sys.base_prefix,
}))
'
```

stdout:

```text
{"name": "atom-cli", "version": "0.1.0", "direct_url": {"subdirectory": "tools", "url": "https://github.com/girishmotwani/atom.git", "vcs_info": {"commit_id": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "requested_revision": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "vcs": "git"}}, "entry_points": {"atom": "atom.cli:main", "atom-write-artifact": "atom.artifact_cli:main"}, "installed_distributions": [["atom-cli", "0.1.0"], ["pip", "24.0"]], "isolated": true, "prefix": "/home/girish/atom-phase09-bootstrap-proof/.venv", "base_prefix": "/usr"}
```

stderr: empty.

### atom-entry-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/atom --help
```

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

stderr: empty.

### writer-entry-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/atom-write-artifact --help
```

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr: empty.

### atom-module-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -m atom.cli --help
```

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

stderr: empty.

### writer-module-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -m atom.artifact_cli --help
```

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr: empty.

### create-fixture-go-module

Actual argv rendered for readability (no shell was used); exit 0:

```text
go mod init example.com/atom-bootstrap-proof
```

stdout: empty.

stderr:

```text
go: creating new go.mod: module example.com/atom-bootstrap-proof
```

### initialize-fixture-git

Actual argv rendered for readability (no shell was used); exit 0:

```text
git init --quiet --initial-branch=bootstrap-proof
```

stdout: empty.

stderr: empty.

### atom-init

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/atom init
```

stdout:

```text
Initialised /home/girish/atom-phase09-bootstrap-proof/module/.atom
  module:    example.com/atom-bootstrap-proof
  approvals: 0
  local instructions: /home/girish/atom-phase09-bootstrap-proof/module/.github/copilot-instructions.md
  specs:     /home/girish/atom-phase09-bootstrap-proof/module/specs
  poc:       /home/girish/atom-phase09-bootstrap-proof/module/poc
  build:     go build ./...
  test:      go test ./...
             no makefile; using Go defaults
  baseline:  /home/girish/atom-phase09-bootstrap-proof/module/.atom/baseline.json

Untouched baseline (race detector skipped):
atom check /home/girish/atom-phase09-bootstrap-proof/module

  PASS  build  go build ./... passed (0.3s)
  FAIL  vet    go vet ./... failed with exit code 1 (0.2s)

        go: warning: "./..." matched no packages
        no packages to vet

  PASS  fmt    gofmt -l . reported no unformatted files (0.0s)
  FAIL  test   go test ./... failed with exit code 1 (0.3s)

        go: warning: "./..." matched no packages
        no packages to test

  SKIP  race   Race detector disabled for this run (0.0s)

  FAILED in 0.8s

Atom derives where you are from specs/. To see it:
  atom status

Atom starts by proving things, not describing them:
  atom poc new <slug> --question "..."
```

stderr: empty.

### write-findings.md

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/atom-write-artifact specs/bootstrap-proof/findings.md
```

Complete UTF-8 input:

```markdown
# Bootstrap Fixture Findings

This empty module is a command-boundary fixture, not the expense CLI.
Recorded baseline passed: false.
UTF-8 fixture: café.
```

stdout:

```text
Wrote /home/girish/atom-phase09-bootstrap-proof/module/specs/bootstrap-proof/findings.md
```

stderr: empty.

### write-decisions.md

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -m atom.artifact_cli specs/bootstrap-proof/decisions.md
```

Complete UTF-8 input:

```markdown
# Bootstrap Fixture Decisions

Use only the approved artifact-writer command forms.
Real validation conclusions belong in the parent repair report.
```

stdout:

```text
Wrote /home/girish/atom-phase09-bootstrap-proof/module/specs/bootstrap-proof/decisions.md
```

stderr: empty.

### reuse-atom-entry-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/atom --help
```

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

stderr: empty.

### reuse-writer-entry-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/atom-write-artifact --help
```

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr: empty.

### reuse-atom-module-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -m atom.cli --help
```

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

stderr: empty.

### reuse-writer-module-help

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -m atom.artifact_cli --help
```

stdout:

```text
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
```

stderr: empty.

### reused-metadata

Actual argv rendered for readability (no shell was used); exit 0:

```text
/home/girish/atom-phase09-bootstrap-proof/.venv/bin/python -c '
import importlib.metadata as metadata
import json, sys
distribution = metadata.distribution("atom-cli")
print(json.dumps({
    "name": distribution.metadata["Name"],
    "version": distribution.version,
    "direct_url": json.loads(distribution.read_text("direct_url.json")),
    "entry_points": {point.name: point.value for point in distribution.entry_points if point.group == "console_scripts"},
    "installed_distributions": sorted((item.metadata["Name"], item.version) for item in metadata.distributions()),
    "isolated": sys.prefix != sys.base_prefix,
    "prefix": sys.prefix,
    "base_prefix": sys.base_prefix,
}))
'
```

stdout:

```text
{"name": "atom-cli", "version": "0.1.0", "direct_url": {"subdirectory": "tools", "url": "https://github.com/girishmotwani/atom.git", "vcs_info": {"commit_id": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "requested_revision": "50622abf2b9f58bcfc2c9d538b7292cf0689ceee", "vcs": "git"}}, "entry_points": {"atom": "atom.cli:main", "atom-write-artifact": "atom.artifact_cli:main"}, "installed_distributions": [["atom-cli", "0.1.0"], ["pip", "24.0"]], "isolated": true, "prefix": "/home/girish/atom-phase09-bootstrap-proof/.venv", "base_prefix": "/usr"}
```

stderr: empty.


## Onboarding Evidence

Actual go.mod:

```text
module example.com/atom-bootstrap-proof

go 1.22.2
```


The named configuration, baseline, local manifest, Copilot instructions and
.gitignore existed after first initialization. The module/build/test commands
matched this fixture, and the generated instructions refer to the local bundle.
Named file contents are retained in private evidence; no external Python source
audit was used to verify them.

Actual baseline.json, including failing gates and skipped race:

```json
{
  "directory": "/home/girish/atom-phase09-bootstrap-proof/module",
  "exit_code": 1,
  "gates": [
    {
      "command_exit_code": 0,
      "command_outcome": "completed",
      "details": "go: warning: \"./...\" matched no packages\n",
      "duration_seconds": 0.298,
      "name": "build",
      "required": true,
      "status": "passed",
      "summary": "go build ./... passed"
    },
    {
      "command_exit_code": 1,
      "command_outcome": "completed",
      "details": "go: warning: \"./...\" matched no packages\nno packages to vet\n",
      "duration_seconds": 0.239,
      "name": "vet",
      "required": true,
      "status": "failed",
      "summary": "go vet ./... failed with exit code 1"
    },
    {
      "command_exit_code": 0,
      "command_outcome": "completed",
      "details": "",
      "duration_seconds": 0.007,
      "name": "fmt",
      "required": true,
      "status": "passed",
      "summary": "gofmt -l . reported no unformatted files"
    },
    {
      "command_exit_code": null,
      "command_outcome": null,
      "details": "go: warning: \"./...\" matched no packages\nno packages to test\n",
      "duration_seconds": 0.3,
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
  "total_duration_seconds": 0.844,
  "warnings": []
}
```


Manifest summary from the named installed local file:

```json
{
  "managed_by": "atom init",
  "source": "atom-cli package",
  "recorded_bundle_files": 2
}
```


## Artifact Round Trips

Comparison of captured expected bytes with the actual named artifact files:

```json
{
  "findings.md": {
    "expected_sha256": "2a2a90dea1897280f7681831dc820d59ad99b8a337d403bf2c134935a8c99a81",
    "actual_sha256": "2a2a90dea1897280f7681831dc820d59ad99b8a337d403bf2c134935a8c99a81",
    "byte_match": true,
    "bytes": 155
  },
  "decisions.md": {
    "expected_sha256": "ec5c767124adb053b89fb3843dd37049364948ef0151a86f29765d27e9274781",
    "actual_sha256": "ec5c767124adb053b89fb3843dd37049364948ef0151a86f29765d27e9274781",
    "byte_match": true,
    "bytes": 148
  }
}
```


findings.md used the executable; decisions.md used the equivalent venv-Python
module form. Both exit codes were 0 and both byte comparisons matched.
The non-ASCII UTF-8 fixture was intentional; no generic editor substituted for
the dedicated writer.

## Preservation And Reuse

The before/after comparisons matched for known Python/pip/Go/git resolutions
and executable hashes, shell profile fingerprints, old and pinned Copilot
binaries, parent PATH fingerprint, installed metadata and proof entry points.
One installer invocation occurred, before reuse; none occurred during the repeated
command/module discovery.

Derived comparisons and captured fingerprints:

```json
{
  "known_defaults_unchanged": true,
  "metadata_unchanged_during_reuse": true,
  "entry_point_hashes_before": {
    "atom": "821bf5c3866606e2600db5cb0d4e002ec0ae8168a385ccf15552282a94ae2878",
    "atom-write-artifact": "86e760d95221b2b4ba26957f42d2d0b3b828aa2d28f08d412dc4dbf6286466a7"
  },
  "entry_point_hashes_after": {
    "atom": "821bf5c3866606e2600db5cb0d4e002ec0ae8168a385ccf15552282a94ae2878",
    "atom-write-artifact": "86e760d95221b2b4ba26957f42d2d0b3b828aa2d28f08d412dc4dbf6286466a7"
  },
  "existing_command_hashes": {
    "python": null,
    "python3": "e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f",
    "pip": "6d1f19b17ef3ab9b6d3532be2198766bb1709c83da6a6684152b8af1930da6fa",
    "go": "89b81bd72c27404ccfd701c136b7e3ace9a4ccb26d96d97e874b48829aed27a1",
    "git": "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668"
  },
  "existing_copilot_hashes": {
    "old": "927f8a3080186770b160a311b736bb40438a8f277ead9bc86ff97f7b4e983bbe",
    "pinned": "985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4"
  },
  "shell_profile_hashes": {
    ".profile": "28b4a453b68dde64f814e94bab14ee651f4f162e15dd9920490aa1d49f05d2a4",
    ".bashrc": "210b69b6cb59d242902d7982773121321165d68e2aa05c57800536d9c2a44584",
    ".bash_profile": null,
    ".zshrc": null
  },
  "parent_environment_modified": false,
  "install_invocations": 1
}
```


This verifies this executed check-only reuse path; it does not prove an agent
will choose that path or enforce that a future agent cannot reinstall.

## Build Provenance

The package's recorded direct_url metadata matches the exact requested source
commit. pip recorded a built wheel SHA-256 in its verbatim output above.
The installed distributions were atom-cli 0.1.0 and pip 24.0, with no runtime
dependencies installed.

One subsequent read-only distribution-metadata query recovered WHEEL build
provenance; it did not rerun pip or read Atom's implementation:

```text
Wheel-Version: 1.0
Generator: setuptools (84.2.1)
Root-Is-Purelib: true
Tag: py3-none-any

```


Recorded Requires-Dist fields are optional development extras, not runtime inputs:

```json
[
  "pytest>=7.4; extra == \"dev\"",
  "pytest-cov>=4.1; extra == \"dev\"",
  "tomli>=2.0; python_version < \"3.11\" and extra == \"dev\""
]
```


The generator was setuptools 84.2.1. This records observed build provenance;
the source pin is not a promise to resolve the same build inputs in every future run.

## Controlled Environment And Limits

The venv lived outside the Go module and its .atom/, so creating it did not make
onboarding start with a conflicting partial .atom/ tree. No activation, global
PATH change, system pip installation, source edit or existing-package overwrite
was performed.

The executor used an explicit credential-free child environment: proof-local HOME,
temporary and Go cache directories, disabled child pip/Git configuration,
virtualenv-required pip, noninteractive public Git and local-only Go toolchain.
It did not copy authentication variables or read authentication files. These are
experimental controls, not a proposed final bootstrap policy or a claim of an OS
sandbox. Custom user pip/Git/HOME configurations remain a changed boundary for
later relevant validation.

The before/after check covers named defaults and known binaries, not every file
on the machine or every editable environment. No claim of clean-machine,
Windows/macOS, repeat/no-op init, unsupported-version, conflicting-directory,
all-agent compliance or genuine-newcomer behavior is made.

The observer program and complete outputs remain in private persistent session
evidence, with a copy of run-evidence.json in the private proof root. This was
the approved Python/command validation, not atom poc run or a synthetic Go spike.
No executor is promoted into production tooling. Named experimental files remain
available; no recursive cleanup was performed.

## What We Learned And What Changes

The guide's existing bare-pip route failed on Ubuntu, but an explicit venv Python
can install the public package and supply both real command boundaries there.
Module forms work without adding scripts to PATH. The initial Go-baseline result
can be preserved honestly even when empty-module gates fail.

This provides bounded evidence for the Linux bootstrap-guidance repair, not for
the original usability question. The short spec should settle interpreter
resolution, the user-facing isolated environment location, successful-form reuse
and safe stop/approval behavior while preserving existing working packages and
Windows's one-time PATH opt-in. No new CLI framework is justified by this result.

## Recommendation And Gates

Recommend accepting this bounded result and proceeding to the short bootstrap
repair spec. The spec must still be approved before canonical and packaged
guidance edits. Its checks must address any difference between the experimental
child environment and the final documented recipe; this proof cannot silently
cover changed conditions.

The alternative is further boundary evidence before that spec if the developer
needs custom-environment or another-platform claims. No new run, model spend,
implementation, release or revised live rehearsal is authorized by this report.

## Completeness

- [x] Approved question copied verbatim and scored against the approved conditions.
- [x] One actual installation, source/distribution/build identities and output captured.
- [x] Both entry-point/module forms and actual writer round trips verified.
- [x] Real first-init baseline captured; vet/test failures and skipped race disclosed.
- [x] Known preservation and check-only reuse verified without reinstall.
- [x] No Go/UX/platform/agent-control claim beyond the observed boundary.
- [x] First failed rehearsal and its evidence retained.
- [x] Developer accepts this result before the short repair spec.

## Bootstrap Result Accepted; Short Spec Authorized: 2026-11-08

The developer selected exactly:
"Accept the result; proceed to the short repair spec".

Accept the Confirmed result only for the bounded isolated Ubuntu command recipe,
including the honestly failing empty-module baseline and named preservation
checks. The original experienced-user rehearsal remains Inconclusive.

Authorize the short bootstrap-guidance repair spec next, with the final
user-environment boundary and applicable validation made explicit. This is not
approval to edit canonical/package guidance, choose untested material changes,
run another experiment, restart the live rehearsal or publish. The spec still
needs its own implementation gate.
