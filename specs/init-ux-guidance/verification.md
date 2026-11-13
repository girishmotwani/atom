# Init UX Guidance Validation

## Factual walkthrough

- Both init and bootstrap retain active-session client and Go prerequisites,
  both verified command roles before init, reuse and immediate discovery stops.
- Read-only grouping is conditional on preserving ordering, statuses, output,
  ownership checks and user decisions. Existing package ambiguity, partial/broken
  stops, known-venv checks and explicit installation consent remain in place.
- Windows hidden-entry-point guidance now retains verified module forms without a
  PATH question. Explicit PATH requests retain the existing opt-in command and
  printed absolute forms, without re-probing.
- Writer refusals, distinct approvals, baseline failure reporting and the existing
  success-path file reads remain unchanged. No installer or runtime code changed.
- The README describes PATH setup as opt-in, not as an automatic offer, so it
  remains consistent without a README edit.

## Focused Python Documentation and Packaging Contracts

From `tools`:

```text
python -m pytest -o addopts= -q --no-header tests\test_plugin.py tests\test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback tests\test_pathsetup.py::test_onboarding_documents_one_time_path_setup
..............                                                           [100%]
14 passed in 0.25s
```

## Packaged Parity

```text
skills/init/SKILL.md == tools/atom/assets/skills/init/SKILL.md: True
skills/atom/references/bootstrap.md == tools/atom/assets/skills/atom/references/bootstrap.md: True
```

## Documentation Checks

From the repository root:

```text
python tools\check_links.py
checked 584 relative links across markdown files
all relative links resolve

git --no-pager diff --check
git diff --check: exit 0
```

These checks and the factual review do not demonstrate agent adherence, fewer
interactive approvals, a fresh onboarding rehearsal, or a functioning new resolver.
The repository root is not a Go module; no root `atom check` or Go RED/GREEN is claimed.
