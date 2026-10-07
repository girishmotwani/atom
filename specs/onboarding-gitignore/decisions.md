# Decisions

| Date | Decision | Reason |
|---|---|---|
| 2026-10-07 | Skip the POC and proceed directly to test-first implementation. | The developer explicitly requested this exception for the simple `.gitignore` change. |
| 2026-10-07 | Treat the request to “implement and review” as approval of the narrow behavior contract without a separate design gate. | The selected policy was already confirmed: ignore generated runtime files only. |
| 2026-10-07 | Ignore only `baseline.json`, `events.jsonl`, and `events.lock`. | `config.json`, `state.json`, and `.atom/atom/**` are shared project records. |
| 2026-10-07 | Refuse malformed or duplicate managed markers. | Guessing which user content Atom owns risks destructive edits. |
| 2026-10-07 | Do not alter the Git index. | Automatically untracking files is a destructive repository operation. |
| 2026-10-07 | Correct the existing-content test fixture to write raw LF bytes. | `Path.write_text` translated LF to CRLF on Windows before Atom ran, so the original assertion tested the fixture's newline conversion rather than content preservation. |
| 2026-10-07 | Read captured stderr once in the marker-boundary test. | Pytest clears captured output after `readouterr`; the first review-fix test accidentally consumed the diagnostic before checking the recovery text. |
| 2026-10-07 | Exercise replacement failure through the gitignore helper rather than full init. | Monkeypatching the shared `os.replace` module function also intercepted Atom state writes, so full init failed before reaching the behavior under test. |
| 2026-10-07 | Reject automatic migration of unmarked `.atom/state.json` rules. | An unmarked rule is user-owned, the reported repository did not identify `state.json`, and removing it would exceed the generated-only policy. |
| 2026-10-07 | Reject automatic `git rm --cached`. | Atom must not change the Git index silently; documentation now gives a path-specific migration command when needed. |
| 2026-10-07 | Reject adding `.atom/*.tmp` and `.atom/*.unsaved` to this managed block. | The developer approved exactly the three generated status/log paths; broadening it requires separate evidence and policy agreement. |
| 2026-10-07 | Use atomic replacement for `.gitignore`. | The file is user-owned and may contain uncommitted rules, so truncating it before a durable replacement is unnecessarily destructive. |
