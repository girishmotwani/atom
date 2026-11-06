# Spike: review-snapshot-fingerprint

**Created:** 2026-11-03

## Question

Can identity checks limited to the exact changed-file paths captured for a review detect changes to those paths across selected and control checks without traversing or hashing unrelated module files?

> A good spike question is falsifiable. If there is no observation that could
> answer it "no", it is not a question -- it is a preference.

## Method

`main.go` created a temporary fixture with one selected file and 1,001 unrelated files. Its identity helper opened and hashed only explicitly selected paths, recording every path read. The spike changed the selected file between identity reads, then restored it and changed one unrelated file. Command: `atom poc run review-snapshot-fingerprint`.

## Result

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

## Verdict

**Confirmed for the scoped fixture only.** Selected-file mutation changed the identity; unrelated-file mutation did not, and no unrelated paths were opened. This supports a review-snapshot-only guard, not a claim that the entire module input set remained identical. Production Git capture integration, unreadable/missing/symlinked selected files, races, and real-repository performance remain untested.
