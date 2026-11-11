---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-10"
verdict: "Confirmed"
status: "accepted-spec-drafting-authorized"
evidence_method: "approved non-installing Windows and Ubuntu discovery checks"
---

# General Onboarding Discovery Boundary Report

## The Question

Can the proposed availability checks identify the existing usable command forms
and explicit package absence in the available Windows and Ubuntu environments
without executing known-missing Atom commands or hiding real execution failures?

## Verdict And Limits

**Confirmed for the observed availability/reuse boundary in these two existing
environments only.** Windows had both entry points; resolution preceded both
successful help calls. Ubuntu had neither command on PATH and no Atom package in
system Python. Those were successful presence queries returning absence as data,
not failed command/module invocations. After six owned, non-symlink ancestor
checks and a successful prefix/package check, both known-venv module roles worked.
No known-missing form ran and no installation was needed.

All actually executed help/presence commands succeeded and their full streams and
statuses were retained. No head-ended diagnostic pipeline was used. This does
**not** establish behavior under a real failing-help/import command: none failed,
so that error branch was not exercised. Unsafe/partial environments, install
consent, active-client mismatch handling, interactive slash aliases and actual
agent adherence are not newly proven. The writer refusal remains prior evidence,
not an event replayed by this check. Do not call the general onboarding repair or
Phase 09 complete from these results.

## Approval, Budget And Method

The developer selected exactly: "Approve the scope and bounded discovery checks".
This authorized only the proposed evidence reuse and check pass, not an installer,
new model session, repair spec, implementation or publication.

Two terminal invocations ran in parallel, below the six-invocation cap. The
observed per-process elapsed times were 3.5464673000387847 seconds on Windows and
0.45461390299897175 seconds on Ubuntu, below the five-minute total cap. Their UTC
start times and exact elapsed values appear below. These are execution context,
not performance benchmark claims. There were four help subprocesses and one
known-venv presence subprocess. No model calls, installs or retries ran.

Each top-level invocation executed a private inline Python observer, not a new
Atom executable or shipped runtime helper. The Windows observer received its
source through python standard input. The Ubuntu observer received its source
through a base64-encoded python3 -c payload via the existing WSL default. No
fixture/script files or environments were created. Private evidence logs are
observer receipts, not changes to participant files.

Observers used shutil.which for entry-point availability; missing roles then used
importlib.util.find_spec('atom') is not None, without reading package source or
printing module locations. Help ran only for discovered candidates. Windows
stopped resolution after establishing both roles. Ubuntu changed only its child
working directory to the named existing participant repository, preserved HOME
and normal configuration, then validated the known venv before executing through
it. Help/presence children inherited their parent's environment with only
PYTHONDONTWRITEBYTECODE=1 added to avoid bytecode writes. No PATH/profile changes,
init, Go checks, writer targets, pip calls or target-file writes occurred.

The complete help/presence argument arrays, stdout, stderr, statuses and safe
ancestor results are preserved below directly from the observer logs. The
observer retained every command result and stopped on any unexpected nonzero
status; that stop branch was not triggered and remains unexercised here.

The current Windows client's identity was taken from the actual agent runtime
context, not from resolving another copilot executable. No Ubuntu client was
launched. Its stopped participant session's previously observed 1.0.5 identity
was labeled historical rather than misrepresented as a newly validated client.

## Windows Evidence

Verbatim JSON-lines receipt; the top-level terminal invocation exited 0:

```jsonl
{"event": "context", "platform": "win32", "started_utc": "2026-11-10T14:43:51.309194+00:00", "python_version": "3.13.14", "active_client_evidence": "Current agent runtime context reports Copilot CLI 1.0.106-9; no alternate executable was queried."}
{"event": "entry_point_availability", "roles": {"atom": "present", "atom-write-artifact": "present"}}
{"event": "help_check", "role": "atom", "argv": ["C:\\Users\\gimotwan\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\Scripts\\atom.EXE", "--help"], "exit_code": 0, "stdout": "usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...\n\nAtom -- prove it, describe it, then build it.\n\npositional arguments:\n  {check,poc,init,status,review,ship,setup-path}\n    check               Run every Go quality gate and report the result.\n    poc                 Create, run and list throwaway spikes.\n    init                Set up Atom, or confirm an existing matching project\n                        without changes.\n    status              Show the current phase, recent activity, and any\n                        problems.\n    review              Ask several models to review a diff and merge what\n                        they agree on.\n    ship                Turn the current branch's finished phase into a pull\n                        request.\n    setup-path          Add Atom's installed commands to the Windows user PATH\n                        (opt-in).\n\noptions:\n  -h, --help            show this help message and exit\n", "stderr": ""}
{"event": "help_check", "role": "atom-write-artifact", "argv": ["C:\\Users\\gimotwan\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\Scripts\\atom-write-artifact.EXE", "--help"], "exit_code": 0, "stdout": "usage: atom-write-artifact [-h] target\n\npositional arguments:\n  target\n\noptions:\n  -h, --help  show this help message and exit\n", "stderr": ""}
{"event": "result", "classification": "usable", "working_forms": {"atom": ["C:\\Users\\gimotwan\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\Scripts\\atom.EXE"], "atom-write-artifact": ["C:\\Users\\gimotwan\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\Scripts\\atom-write-artifact.EXE"]}, "known_missing_forms_executed": 0, "elapsed_seconds": 3.5464673000387847, "limitations": "Observed local discovery only; not agent compliance or interactive alias validation."}
```

## Ubuntu Evidence

Verbatim JSON-lines receipt; the top-level terminal invocation exited 0:

```jsonl
{"event": "context", "platform": "linux", "started_utc": "2026-11-10T14:43:51.427703+00:00", "python_version": "3.12.3", "cwd": "/home/girish/atom-phase09-prepared-rehearsal", "active_client_evidence": "No active client launched or inferred from another executable. Stopped participant session was previously observed as CLI 1.0.5."}
{"event": "entry_point_availability", "roles": {"atom": "absent", "atom-write-artifact": "absent"}}
{"event": "package_availability", "interpreter": "/usr/bin/python3", "package": "atom", "present": false}
{"event": "ancestor_check", "path": "/home/girish", "owned_non_symlink_directory": true}
{"event": "ancestor_check", "path": "/home/girish/.local", "owned_non_symlink_directory": true}
{"event": "ancestor_check", "path": "/home/girish/.local/share", "owned_non_symlink_directory": true}
{"event": "ancestor_check", "path": "/home/girish/.local/share/atom-cli", "owned_non_symlink_directory": true}
{"event": "ancestor_check", "path": "/home/girish/.local/share/atom-cli/venv", "owned_non_symlink_directory": true}
{"event": "ancestor_check", "path": "/home/girish/.local/share/atom-cli/venv/bin", "owned_non_symlink_directory": true}
{"event": "known_environment_presence", "argv": ["/home/girish/.local/share/atom-cli/venv/bin/python", "-c", "import importlib.util,json,sys; print(json.dumps({'prefix':sys.prefix,'base_prefix':sys.base_prefix,'supported_python':sys.version_info >= (3,10),'atom_present':importlib.util.find_spec('atom') is not None}))"], "exit_code": 0, "stdout": "{\"prefix\": \"/home/girish/.local/share/atom-cli/venv\", \"base_prefix\": \"/usr\", \"supported_python\": true, \"atom_present\": true}\n", "stderr": ""}
{"event": "help_check", "role": "atom", "argv": ["/home/girish/.local/share/atom-cli/venv/bin/python", "-m", "atom.cli", "--help"], "exit_code": 0, "stdout": "usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...\n\nAtom -- prove it, describe it, then build it.\n\npositional arguments:\n  {check,poc,init,status,review,ship,setup-path}\n    check               Run every Go quality gate and report the result.\n    poc                 Create, run and list throwaway spikes.\n    init                Set up Atom, or confirm an existing matching project\n                        without changes.\n    status              Show the current phase, recent activity, and any\n                        problems.\n    review              Ask several models to review a diff and merge what\n                        they agree on.\n    ship                Turn the current branch's finished phase into a pull\n                        request.\n    setup-path          Add Atom's installed commands to the Windows user PATH\n                        (opt-in).\n\noptions:\n  -h, --help            show this help message and exit\n", "stderr": ""}
{"event": "help_check", "role": "atom-write-artifact", "argv": ["/home/girish/.local/share/atom-cli/venv/bin/python", "-m", "atom.artifact_cli", "--help"], "exit_code": 0, "stdout": "usage: atom-write-artifact [-h] target\n\npositional arguments:\n  target\n\noptions:\n  -h, --help  show this help message and exit\n", "stderr": ""}
{"event": "result", "classification": "usable_outside_path", "working_forms": {"atom": ["/home/girish/.local/share/atom-cli/venv/bin/python", "-m", "atom.cli"], "atom-write-artifact": ["/home/girish/.local/share/atom-cli/venv/bin/python", "-m", "atom.artifact_cli"]}, "known_missing_forms_executed": 0, "elapsed_seconds": 0.45461390299897175, "limitations": "Observed known environment only; not unsafe/partial installation coverage, agent compliance or interactive alias validation."}
```

## What This Changes

The availability-first primitives can replace intentionally failing discovery
calls while preserving the existing command-role priority and healthy venv reuse
in these observed conditions. This supplies a narrow basis for proposing shipped
guidance, not for adding a runtime bootstrap engine, changing the installer or
asserting that instructions will be obeyed. Reuse accepted installation/boundary
reports only within their recorded assumptions; do not generalize this check to
new platforms or unsupported clients.

Recommended next step, only after this evidence is accepted: draft a short repair
spec for the init skill, shared bootstrap reference, two packaged mirrors and
directly related README wording. Specify absent/usable/broken handling, active
client identification, install consent, exact command-form retention, real-error
stop rules and qualified next-beat handoff. Preserve Windows setup-path opt-in,
Linux isolation/ownership/configuration rules, module-local writer permissions,
real Go baseline results and the stopped trial's immutable history.

The spec should distinguish factual/packaging validation from the separately
gated observed-agent test needed for a future usability/compliance claim. Its
approval remains separate from this evidence gate. No shipped guidance has changed.

## Evidence Acceptance Recorded

The developer selected exactly: "Accept the evidence and draft the repair spec".
Spec drafting only was authorized; implementation requires its separate gate.
