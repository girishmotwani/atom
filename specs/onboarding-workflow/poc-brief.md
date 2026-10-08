# POC Brief: Existing-repository onboarding UX

## Question

> After you have fixed this, can you spike onboarding to an existing repo and running the atom init command. Verify that the onboarding is complete and also the user is not asked for approval to write to atom's state files.

## Success criteria

- Start from a committed, non-Atom Go repository.
- Enter `/atom:init` through a real interactive Copilot CLI session in Manual Approval mode.
- `atom init` captures the untouched no-race baseline and produces the complete onboarding scaffold.
- No approval prompt asks to write `.atom/config.json`, `.atom/state.json`, `.atom/baseline.json`, `.atom/events.jsonl`, or `.atom/events.lock`.
- Every user text entry and every approve/deny action is preserved in an interaction ledger and full transcript.
- The installed local bundle has no reference back to the Atom checkout or installed-plugin directory.
