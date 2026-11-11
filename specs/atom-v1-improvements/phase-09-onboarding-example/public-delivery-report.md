# Public Ubuntu Delivery Report

**Status:** verified maintenance delivery, not a Phase 09 usability verdict.

## Scope and result

The developer approved one named Atom plugin update and one pinned atom-cli
refresh in the existing Ubuntu user-owned venv. Both completed once.
Source: ec605a715f53db93abd54d6e88f887cf20525940 (merged PR #20).
Started: 2026-11-10T09:52:34.270514+00:00. Finished: 2026-11-10T09:52:51.083325+00:00.
Elapsed: 16.81284103100188 seconds; approved cap: 300 seconds.
Model calls: 0. No automatic retries or rollback.

The installed plugin changed from 594 to 607 source files.
Every resulting file matched the approved commit's Git blob inventory. Both
plugin and Python-package bootstrap assets now have the accepted SHA-256:

```text
ce34395eea5d7049b9ab23a594227a916afae28857ae3b873dac31255f387b3e
```

The package records the approved source commit. Plugin 0.2.0 and atom-cli 0.1.0
retain their version numbers; content/source checks, not version labels, establish
delivery. Both entry points and both module help forms exited 0.

All 20 observed commands are accounted for: 10 exit 0 and 10 expected exit-1
pip missing-key diagnostics, each checked against its actual diagnostic. All five
checked scheme environment variables had no nonempty values, and all ten queried
pip scheme keys returned their expected missing-key diagnostics before mutation. Normal HOME/pip/Git configuration was retained; no child
environment overrides were applied.

## Preservation and limits

Named before/after checks match for the original rehearsal module and recording,
shell profiles, command resolution/hashes, PATH hash, both Copilot launchers and
other installed-plugin content. Other installed distribution versions are equal.
The immutable first-attempt recipe also retains its original hash.

No system Python or pip upgrade, PATH/profile/auth change, other-plugin update,
new module/init, generated-bundle patch, artifact-writer fixture or live rehearsal
was performed. Existing generated module bundles were not refreshed. Package
asset correctness is verified; generation into a new module has not been tested
in this run. Both command roles were checked by help, not by manufacturing a
passing Go project or performing an unapproved write.

The first rehearsal remains Inconclusive, and this experienced user's future
prepared-environment attempt cannot establish genuine-newcomer or cold-start
PEP 668 usability. Phase 09 and the expense CLI remain incomplete.

## Command outcomes

| Observed command step | Exit |
| --- | --- |
| `package-metadata-before` | 0 |
| `pip-config-global.target` | 1 |
| `pip-config-global.prefix` | 1 |
| `pip-config-global.root` | 1 |
| `pip-config-global.user` | 1 |
| `pip-config-global.python` | 1 |
| `pip-config-install.target` | 1 |
| `pip-config-install.prefix` | 1 |
| `pip-config-install.root` | 1 |
| `pip-config-install.user` | 1 |
| `pip-config-install.python` | 1 |
| `plugin-list-before` | 0 |
| `named-plugin-update` | 0 |
| `pinned-package-refresh` | 0 |
| `package-metadata-after` | 0 |
| `atom-entry-point` | 0 |
| `writer-entry-point` | 0 |
| `atom-module-form` | 0 |
| `writer-module-form` | 0 |
| `plugin-list-after` | 0 |

## Verbatim installation and command-role evidence

### named-plugin-update

```text
$ /home/girish/.local/atom-phase09-tools/bin/copilot --no-auto-update plugin update atom@atom
Exit: 0
STDOUT:
Plugin "atom@atom" updated successfully (v0.2.0, already at latest). Updated 9 skills.
STDERR:
```

### pinned-package-refresh

```text
$ /home/girish/.local/share/atom-cli/venv/bin/python -m pip install --no-cache-dir --no-input --no-deps --force-reinstall 'git+https://github.com/girishmotwani/atom.git@ec605a715f53db93abd54d6e88f887cf20525940#subdirectory=tools'
Exit: 0
STDOUT:
Collecting git+https://github.com/girishmotwani/atom.git@ec605a715f53db93abd54d6e88f887cf20525940#subdirectory=tools
  Cloning https://github.com/girishmotwani/atom.git (to revision ec605a715f53db93abd54d6e88f887cf20525940) to /tmp/pip-req-build-ms5drq90
  Resolved https://github.com/girishmotwani/atom.git to commit ec605a715f53db93abd54d6e88f887cf20525940
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Getting requirements to build wheel: started
  Getting requirements to build wheel: finished with status 'done'
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Building wheels for collected packages: atom-cli
  Building wheel for atom-cli (pyproject.toml): started
  Building wheel for atom-cli (pyproject.toml): finished with status 'done'
  Created wheel for atom-cli: filename=atom_cli-0.1.0-py3-none-any.whl size=251432 sha256=3aa1a0e488f42f36409ba974aae60bc6e5e0d2e4ed4565b57c857dc8acb82314
  Stored in directory: /tmp/pip-ephem-wheel-cache-0z0bojpp/wheels/3a/35/59/f14718c8f5568825eb5be989a2e8900fb65a0ed199f858ada5
Successfully built atom-cli
Installing collected packages: atom-cli
  Attempting uninstall: atom-cli
    Found existing installation: atom-cli 0.1.0
    Uninstalling atom-cli-0.1.0:
      Successfully uninstalled atom-cli-0.1.0
Successfully installed atom-cli-0.1.0
STDERR:
  Running command git clone --filter=blob:none --quiet https://github.com/girishmotwani/atom.git /tmp/pip-req-build-ms5drq90
  Running command git rev-parse -q --verify 'sha^ec605a715f53db93abd54d6e88f887cf20525940'
  Running command git fetch -q https://github.com/girishmotwani/atom.git ec605a715f53db93abd54d6e88f887cf20525940
```

### atom-entry-point

```text
$ /home/girish/.local/share/atom-cli/venv/bin/atom --help
Exit: 0
STDOUT:
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
STDERR:
```

### writer-entry-point

```text
$ /home/girish/.local/share/atom-cli/venv/bin/atom-write-artifact --help
Exit: 0
STDOUT:
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
STDERR:
```

### atom-module-form

```text
$ /home/girish/.local/share/atom-cli/venv/bin/python -m atom.cli --help
Exit: 0
STDOUT:
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
STDERR:
```

### writer-module-form

```text
$ /home/girish/.local/share/atom-cli/venv/bin/python -m atom.artifact_cli --help
Exit: 0
STDOUT:
usage: atom-write-artifact [-h] target

positional arguments:
  target

options:
  -h, --help  show this help message and exit
STDERR:
```

## Verbatim refreshed distribution metadata

```json
{"prefix": "/home/girish/.local/share/atom-cli/venv", "base_prefix": "/usr", "pip_file": "/home/girish/.local/share/atom-cli/venv/lib/python3.12/site-packages/pip/__init__.py", "version": "0.1.0", "source_commit": "ec605a715f53db93abd54d6e88f887cf20525940", "bootstrap_sha256": "ce34395eea5d7049b9ab23a594227a916afae28857ae3b873dac31255f387b3e", "bootstrap_path": "/home/girish/.local/share/atom-cli/venv/lib/python3.12/site-packages/atom/assets/skills/atom/references/bootstrap.md", "dependencies": {"pip": "24.0"}}
```

## Verbatim expected missing-key diagnostics

```text
ERROR: No such key - global.target
ERROR: No such key - global.prefix
ERROR: No such key - global.root
ERROR: No such key - global.user
ERROR: No such key - global.python
ERROR: No such key - install.target
ERROR: No such key - install.prefix
ERROR: No such key - install.root
ERROR: No such key - install.user
ERROR: No such key - install.python
```

## Next gate

Accept this delivery result before preparing a newly frozen user-run rehearsal
recipe. That recipe must disclose working prerequisites and use a new module and
evidence destination. Approval of this maintenance run did not approve that
preparation, a live attempt, example design, publication or Phase 09 completion.
