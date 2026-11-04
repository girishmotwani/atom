---
project: "review-tooling-continuation"
phase: "phase-02-honest-review-continuation"
poc_slug: "review-snapshot-fingerprint"
verdict: "Confirmed"
date: "2026-11-03"
spike_path: "poc/review-snapshot-fingerprint/main.go"
---

# POC Report: Review-Snapshot Input Identity

## The Question

Can identity checks limited to the exact changed-file paths captured for a review detect changes to those paths across selected and control checks without traversing or hashing unrelated module files?

## Verdict

**Confirmed for the scoped Go fixture.** The spike detected a selected-file mutation while reading only the one selected path. A separate mutation to an unrelated file left the selected-path identity unchanged, and the instrumented reader recorded no unrelated paths opened. This confirms the proposed scope mechanics, not production integration or full module-input identity.

## Evidence

Command:

```text
atom poc run review-snapshot-fingerprint
```

Captured output:

```text
atom poc run review-snapshot-fingerprint  (command spike)

  PASS  vet     ok
  PASS  build   ok
  PASS  execute ok

  stdout:
    fixture_files=1002 selected_paths=1
    selected_mutation_detected=true selected_reads=2 bytes_read=31
    unrelated_mutation_ignored=true unrelated_files_opened=false scoped_reads=2

  Verdict: CONFIRMED  (exit 0) -- the question was answered yes
```

The fixture contained 1,002 files: one selected file and 1,001 unrelated files. In both before/after comparisons the identity function opened the selected file once per read and no unrelated path. It detected the changed selected file; it intentionally did not detect the changed unrelated file.

## What This Changes

The approved design may replace whole-module content hashing with an identity guard limited to the selected review snapshot's changed paths. The guard can still reject a change to an included path between the selected and control checks while avoiding traversal/content reads for unrelated paths.

The developer explicitly accepted that changes to module inputs outside the selected review snapshot may not be detected by this guard. This is a reduced guarantee, not proof that module-wide build/vet/test consumed an identical complete source tree. The design must state that limitation and preserve fail-closed handling for missing/unreadable selected paths.

## Explicitly Not Covered

- Production Python integration, Git diff sources (working/staged/branch), nested modules, renames/deletions, missing paths, unreadable files, or symlinks.
- Whether changed-file snapshots are the complete set of module inputs that Go build/vet/test consume.
- Concurrent mutation-and-restore between identity checks, file metadata races, or adversarial filesystem behavior.
- A real-repository performance benchmark; this only proves that the scoped function reads one selected file in a 1,002-file fixture.
- Cross-platform behavior beyond this Windows run.

## Completeness Checklist

- [x] Question copied verbatim from the approved brief.
- [x] Verdict is limited to the observed behavior.
- [x] Verbatim `atom poc run` output is included.
- [x] The change to the design and the intentionally weakened guarantee are explicit.
- [x] Uncovered integration/error cases are listed.
- [x] No production code, test, or design change was made during the POC.
