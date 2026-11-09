---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
poc_slug: "candidate-delivery"
verdict: "Refuted"
date: "2026-11-09"
status: "accepted"
evidence_method: "approved command validation; stopped at duplicate-plugin criterion"
---

# Isolated Candidate Delivery Report

## The Question

Can an isolated candidate expose the repaired Atom plugin through the pinned
Ubuntu CLI's local-plugin metadata and generate the matching repaired local
instruction bundle through a separate candidate atom-cli installation, while
preserving the named working installations, defaults and original trial?

## Verdict

**Refuted for the proposed no-duplicate local-delivery route.** The pinned CLI
listed two enabled atom plugins: the installed marketplace copy and the external
candidate. The [approved brief](candidate-delivery-brief.md) explicitly required
stopping on duplicate identities. This does not refute the accepted bootstrap
repair or demonstrate how runtime skill selection would resolve that collision.

The local candidate did not replace the installed plugin. No runtime invocation
or priority experiment was attempted, and the package-delivery half was not run.
Do not treat this as partial confirmation of candidate readiness.

## What Actually Ran

After the developer requested "thanks!lets proceed", one bounded Ubuntu run
verified the frozen installed content and named preservation targets, copied the
plugin, fetched the exact public package-source commit and applied only the two
accepted bootstrap references to each new source tree. No simulated plugin
metadata or fabricated Go spike was used.

The private Python observer and Windows transport are retained in the session
files. They are evidence-capture helpers, not repository automation or a new
Atom runtime mechanism. All eleven recorded native commands exited zero; the
observer itself exited 2 after evaluating the documented stopping condition.

Observed run fields:

```json
{
  "started_at": "2026-11-09T14:02:20.773692+00:00",
  "finished_at": "2026-11-09T14:02:26.040572+00:00",
  "elapsed_seconds": 5.266918419998547,
  "status": "stopped",
  "verdict": "Refuted",
  "stop_reason": "Plugin metadata reports duplicate or missing atom identities",
  "fetch_invocations": 1,
  "venv_creation_invocations": 0,
  "install_invocations": 0,
  "model_requests": 0,
  "named_preservation_checks_match": true,
  "installed_plugin_inventory_preserved": true,
  "created_paths": [
    "/home/girish/atom-phase09-candidate-delivery-proof",
    "/home/girish/atom-phase09-candidate-delivery-proof/plugin",
    "/home/girish/atom-phase09-candidate-delivery-proof/package-source"
  ]
}
```

Source/delta checks derived from the retained inventory records:

```json
{
  "plugin_base_files": 594,
  "public_package_base_files": 594,
  "public_package_base_equals_frozen_plugin_inventory": true,
  "candidate_plugin_deltas": [
    "skills/atom/references/bootstrap.md",
    "tools/atom/assets/skills/atom/references/bootstrap.md"
  ],
  "candidate_package_deltas": [
    "skills/atom/references/bootstrap.md",
    "tools/atom/assets/skills/atom/references/bootstrap.md"
  ],
  "repaired_bootstrap_sha256": "ce34395eea5d7049b9ab23a594227a916afae28857ae3b873dac31255f387b3e"
}
```

Original frozen evidence identities rechecked after the run:

```json
{
  "original_recipe_sha256": "69617ba5da1d9f277af92b5e1816058d625e5f57ea0c9d1ef38ec8edd9fb5052",
  "private_original_terminal_sha256": "960cd3b9bfad1ce3b967151bfb75dcdaa7a71b686571c6044985846fe55249b2"
}
```

Only the new proof root, plugin copy and detached public-source checkout were
created. No candidate venv, pip install, fixture module/init, writer round trip,
additional model request or live expense-CLI rehearsal ran. The remaining planned
steps were intentionally not executed after the duplicate-plugin observation.
The original rehearsal remains [Inconclusive](poc-report.md).

## Decisive Output

Actual candidate-plugin-list stdout, exit 0:

```json
[
  {
    "name": "atom",
    "marketplace": "atom",
    "version": "0.2.0",
    "enabled": true,
    "source": "installed"
  },
  {
    "name": "atom",
    "marketplace": "",
    "version": "0.2.0",
    "enabled": true,
    "source": "external"
  },
  {
    "name": "browser-use",
    "marketplace": "",
    "version": "0.1.0",
    "enabled": false,
    "source": "builtin"
  }
]
```

The two atom rows differ in source/marketplace, but share the same name and
version and are both enabled. This is the brief's duplicate condition, not proof
that either plugin's skills were invoked or that Copilot itself is defective.

## Preservation Evidence

The complete original installed-plugin file inventory matched before and after.
Named shared-venv launcher, distribution-metadata and packaged-bootstrap hashes;
Copilot binary/profile/PATH checks; and original recording/module checks matched.
These checks do not claim that normal CLI/Git cache/log writes were impossible or
that an exhaustive filesystem sandbox was present.

Before/after named snapshots:

```json
{
  "before": {
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
    "profiles": {
      ".profile": "28b4a453b68dde64f814e94bab14ee651f4f162e15dd9920490aa1d49f05d2a4",
      ".bashrc": "210b69b6cb59d242902d7982773121321165d68e2aa05c57800536d9c2a44584",
      ".bash_profile": null,
      ".zshrc": null
    },
    "copilot": {
      "pinned": "985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4",
      "old": "927f8a3080186770b160a311b736bb40438a8f277ead9bc86ff97f7b4e983bbe"
    },
    "path_sha256": "77c8b9d160b3025813fbaf702c2cacc0a0d6714f11eb7a8776f40500035250a5",
    "original_go_mod": "a2cb4cfde37c8114b68d37bcef33f718a83720172d0dc710ddae7f55e0d1d5bc",
    "original_atom_exists": false,
    "original_terminal": "960cd3b9bfad1ce3b967151bfb75dcdaa7a71b686571c6044985846fe55249b2",
    "shared_launchers": {
      "atom": "f6e090275203dc7d247c7dd80c7ec8f988522f1f84c92b6390ea60d8e4fb301e",
      "atom-write-artifact": "8291abd2873fb233929fef5fd5f3e4bd6b52ca81db648396b326ef028247261b"
    },
    "shared_metadata_files": {
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/INSTALLER": "ceebae7b8927a3227e5303cf5e0f1f7b34bb542ad7250ac03fbcde36ec2f1508",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/METADATA": "b50e24dd6ad3aecc34396c9aaca646b86b4c157bdf3c1cdbe1cfff124113fa55",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/RECORD": "7484a663669a44275c1e4dc1cd33ef41d373d2e1d0b3b0e690846e0a6d7115ea",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/REQUESTED": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/WHEEL": "98e75747d0b7c0c568bfb71263c3d8f970b3a374a6996087bc642be5cb09a1aa",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/direct_url.json": "211d24aacb7603289559550422c38e636c45b557fc0996844f57247a3d8ae0b7",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/entry_points.txt": "964149696ab5abcb29d57ffbe574adfd39b296e54f565c57fa77bb6ba0e1d0bb",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/top_level.txt": "5c54b1344472c4d5e7dfad7f8989bab0b6fd0f8fb6ab08744e59379ba06e51a5"
    },
    "shared_bootstrap": {
      "lib/python3.12/site-packages/atom/assets/skills/atom/references/bootstrap.md": "e561e9ed5e114dd889b438e5c0c37c4ea6e64561831b1c4678b03288b4d8fa56"
    }
  },
  "after": {
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
    "profiles": {
      ".profile": "28b4a453b68dde64f814e94bab14ee651f4f162e15dd9920490aa1d49f05d2a4",
      ".bashrc": "210b69b6cb59d242902d7982773121321165d68e2aa05c57800536d9c2a44584",
      ".bash_profile": null,
      ".zshrc": null
    },
    "copilot": {
      "pinned": "985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4",
      "old": "927f8a3080186770b160a311b736bb40438a8f277ead9bc86ff97f7b4e983bbe"
    },
    "path_sha256": "77c8b9d160b3025813fbaf702c2cacc0a0d6714f11eb7a8776f40500035250a5",
    "original_go_mod": "a2cb4cfde37c8114b68d37bcef33f718a83720172d0dc710ddae7f55e0d1d5bc",
    "original_atom_exists": false,
    "original_terminal": "960cd3b9bfad1ce3b967151bfb75dcdaa7a71b686571c6044985846fe55249b2",
    "shared_launchers": {
      "atom": "f6e090275203dc7d247c7dd80c7ec8f988522f1f84c92b6390ea60d8e4fb301e",
      "atom-write-artifact": "8291abd2873fb233929fef5fd5f3e4bd6b52ca81db648396b326ef028247261b"
    },
    "shared_metadata_files": {
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/INSTALLER": "ceebae7b8927a3227e5303cf5e0f1f7b34bb542ad7250ac03fbcde36ec2f1508",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/METADATA": "b50e24dd6ad3aecc34396c9aaca646b86b4c157bdf3c1cdbe1cfff124113fa55",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/RECORD": "7484a663669a44275c1e4dc1cd33ef41d373d2e1d0b3b0e690846e0a6d7115ea",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/REQUESTED": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/WHEEL": "98e75747d0b7c0c568bfb71263c3d8f970b3a374a6996087bc642be5cb09a1aa",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/direct_url.json": "211d24aacb7603289559550422c38e636c45b557fc0996844f57247a3d8ae0b7",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/entry_points.txt": "964149696ab5abcb29d57ffbe574adfd39b296e54f565c57fa77bb6ba0e1d0bb",
      "lib/python3.12/site-packages/atom_cli-0.1.0.dist-info/top_level.txt": "5c54b1344472c4d5e7dfad7f8989bab0b6fd0f8fb6ab08744e59379ba06e51a5"
    },
    "shared_bootstrap": {
      "lib/python3.12/site-packages/atom/assets/skills/atom/references/bootstrap.md": "e561e9ed5e114dd889b438e5c0c37c4ea6e64561831b1c4678b03288b4d8fa56"
    }
  }
}
```

## Full Command Evidence

Each argv/cwd/exit field below is from the actual observer record. Stdout and
stderr are copied verbatim; empty fenced streams are genuinely empty. No command
was rerun to improve its result.

### 1. python-version

```json
{
  "arguments": [
    "python3",
    "--version"
  ],
  "cwd": "/home/girish",
  "exit_code": 0,
  "duration_seconds": 0.0014898809968144633,
  "timed_out": false
}
```

Stdout:

```text
Python 3.12.3
```

Stderr:

```text
```

### 2. go-version

```json
{
  "arguments": [
    "go",
    "version"
  ],
  "cwd": "/home/girish",
  "exit_code": 0,
  "duration_seconds": 0.1298787049963721,
  "timed_out": false
}
```

Stdout:

```text
go version go1.22.2 linux/amd64
```

Stderr:

```text
```

### 3. git-version

```json
{
  "arguments": [
    "git",
    "--version"
  ],
  "cwd": "/home/girish",
  "exit_code": 0,
  "duration_seconds": 0.00344210299954284,
  "timed_out": false
}
```

Stdout:

```text
git version 2.43.0
```

Stderr:

```text
```

### 4. copilot-version

```json
{
  "arguments": [
    "/home/girish/.local/atom-phase09-tools/bin/copilot",
    "--no-auto-update",
    "--version"
  ],
  "cwd": "/home/girish",
  "exit_code": 0,
  "duration_seconds": 0.0764449069974944,
  "timed_out": false
}
```

Stdout:

```text
GitHub Copilot CLI 1.0.107.
Run 'copilot update' to check for updates.
```

Stderr:

```text
```

### 5. plugin-list-help

```json
{
  "arguments": [
    "/home/girish/.local/atom-phase09-tools/bin/copilot",
    "--no-auto-update",
    "plugin",
    "list",
    "--help"
  ],
  "cwd": "/home/girish",
  "exit_code": 0,
  "duration_seconds": 0.09349396400648402,
  "timed_out": false
}
```

Stdout:

```text
Usage: copilot plugin list [OPTIONS]

List installed plugins.

Shows all plugins currently installed, their versions, and status.
Plugins mounted via the global --plugin-dir option are also listed,
under a separate "External Plugins (via --plugin-dir)" section.

Options:
      --json
          Output as JSON

  -h, --help
          Print help (see a summary with '-h')

Examples:
  # List all installed plugins
  $ copilot plugin list

  # Also include plugins loaded via the global --plugin-dir option
  $ copilot --plugin-dir ./my-plugin plugin list

  # Machine-readable output
  $ copilot plugin list --json

Learn More:
  Use `copilot <command> --help` for more information about a command.
  Read the documentation at https://docs.github.com/copilot/how-tos/copilot-cli
```

Stderr:

```text
```

### 6. create-package-source-repository

```json
{
  "arguments": [
    "git",
    "init",
    "--quiet"
  ],
  "cwd": "/home/girish/atom-phase09-candidate-delivery-proof/package-source",
  "exit_code": 0,
  "duration_seconds": 0.01200604799669236,
  "timed_out": false
}
```

Stdout:

```text
```

Stderr:

```text
```

### 7. set-public-source-origin

```json
{
  "arguments": [
    "git",
    "remote",
    "add",
    "origin",
    "https://github.com/girishmotwani/atom.git"
  ],
  "cwd": "/home/girish/atom-phase09-candidate-delivery-proof/package-source",
  "exit_code": 0,
  "duration_seconds": 0.003682429000036791,
  "timed_out": false
}
```

Stdout:

```text
```

Stderr:

```text
```

### 8. fetch-pinned-public-source

```json
{
  "arguments": [
    "git",
    "fetch",
    "--depth",
    "1",
    "origin",
    "50622abf2b9f58bcfc2c9d538b7292cf0689ceee"
  ],
  "cwd": "/home/girish/atom-phase09-candidate-delivery-proof/package-source",
  "exit_code": 0,
  "duration_seconds": 1.612362364998262,
  "timed_out": false
}
```

Stdout:

```text
```

Stderr:

```text
From https://github.com/girishmotwani/atom
 * branch            50622abf2b9f58bcfc2c9d538b7292cf0689ceee -> FETCH_HEAD
```

### 9. checkout-pinned-public-source

```json
{
  "arguments": [
    "git",
    "checkout",
    "--detach",
    "FETCH_HEAD"
  ],
  "cwd": "/home/girish/atom-phase09-candidate-delivery-proof/package-source",
  "exit_code": 0,
  "duration_seconds": 0.06983489699632628,
  "timed_out": false
}
```

Stdout:

```text
```

Stderr:

```text
HEAD is now at 50622ab feat(workflow): add risk-proportionate evidence guidance (#18)
```

### 10. verify-package-source-commit

```json
{
  "arguments": [
    "git",
    "rev-parse",
    "HEAD"
  ],
  "cwd": "/home/girish/atom-phase09-candidate-delivery-proof/package-source",
  "exit_code": 0,
  "duration_seconds": 0.0013505899987649173,
  "timed_out": false
}
```

Stdout:

```text
50622abf2b9f58bcfc2c9d538b7292cf0689ceee
```

Stderr:

```text
```

### 11. candidate-plugin-list

```json
{
  "arguments": [
    "/home/girish/.local/atom-phase09-tools/bin/copilot",
    "--no-auto-update",
    "--plugin-dir",
    "/home/girish/atom-phase09-candidate-delivery-proof/plugin",
    "plugin",
    "list",
    "--json"
  ],
  "cwd": "/home/girish/atom-phase09-candidate-delivery-proof",
  "exit_code": 0,
  "duration_seconds": 0.8526334590060287,
  "timed_out": false
}
```

Stdout:

```text
[
  {
    "name": "atom",
    "marketplace": "atom",
    "version": "0.2.0",
    "enabled": true,
    "source": "installed"
  },
  {
    "name": "atom",
    "marketplace": "",
    "version": "0.2.0",
    "enabled": true,
    "source": "external"
  },
  {
    "name": "browser-use",
    "marketplace": "",
    "version": "0.1.0",
    "enabled": false,
    "source": "builtin"
  }
]
```

Stderr:

```text
```

## What We Learned And What Changes

The advertised --plugin-dir flag adds an external copy while retaining the
installed atom entry in plugin-list metadata. The proposed unchanged-installation
route therefore does not meet its own unambiguous/no-duplicate criterion.
The source overlays and preservation checks succeeded; those narrower facts do
not establish that an agent would use the repaired candidate instructions.

Return to a delivery decision, not a phase design or another automatic retry.
Recommend the normal publication route for the accepted three-document bootstrap
repair rather than adding an isolation workaround to this onboarding exercise.
Scope that shipping work explicitly first; a PR is not a merged public update.
A separately approved isolation revision remains an alternative, but this run
authorizes neither it nor changing the installed plugin/configuration.

## Explicitly Not Covered

No candidate Python installation or generated-bundle validation, candidate writer
round trip, actual skill/command invocation, precedence/deduplication behavior,
public release/update, cold-start onboarding behavior, expense totals/error tests,
passing Go baseline, genuine newcomer usability or Phase 09 completion is proven.
No existing bootstrap evidence or source-repair acceptance is withdrawn.

Retain the partial candidate/evidence. Do not remove/reuse the proof root, disable
an installed plugin, rename namespaces, change configuration/HOME/authentication,
repair this test in place, or start a new rehearsal without its own approval.

## Gate

Result acceptance and the next delivery route are pending. Recommendation:
accept the stopped result and scope publication of the accepted bootstrap repair.
No commit, push, merge, release or additional experiment is authorized here.


## Result Acceptance And PR Authorization

The developer selected "Accept result; commit, push and open the bootstrap-fix PR".
The Refuted delivery result is accepted; publish the accepted documentation repair
through a normal PR. This authorizes neither a revised local experiment nor a
merge, installed update, release or new participant trial. Phase 09 stays open.
