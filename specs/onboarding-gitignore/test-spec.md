# Test Spec: Managed Atom Gitignore Entries

| Behavior | Test |
|---|---|
| Fresh onboarding creates the managed block | `test_init_ignores_only_generated_atom_runtime_files` |
| Generated runtime files are ignored | `test_init_ignores_only_generated_atom_runtime_files` |
| Shared Atom files remain visible to Git | `test_init_ignores_only_generated_atom_runtime_files` |
| Existing content is preserved and repeated init is byte-stable | `test_init_preserves_existing_gitignore_and_updates_it_once` |
| A stale managed block is replaced | `test_init_replaces_stale_atom_gitignore_block` |
| Existing CRLF convention is preserved | `test_init_preserves_existing_gitignore_newlines` |
| Malformed or duplicate markers are refused | `test_init_refuses_ambiguous_atom_gitignore_markers` |
| Existing index entries are unchanged | `test_init_ignores_only_generated_atom_runtime_files` |
| Missing final newline and existing blank separators are handled idempotently | `test_init_separates_the_managed_block_without_changing_existing_content` |
| Failed replacement preserves the original and reports recovery | `test_gitignore_update_keeps_original_when_atomic_replace_fails` |
| Unreadable/non-UTF-8 files produce an actionable init error | `test_init_reports_an_unreadable_gitignore_without_a_traceback` |

## Redundancy audit

No case is guaranteed by Python syntax or static tooling. Each test exercises
observable filesystem or Git behavior.
