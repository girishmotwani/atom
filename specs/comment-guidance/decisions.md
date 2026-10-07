# Decisions

| # | Decision | Why |
|---|---|---|
| 1 | Required meaningful comments only, not broad commenting | The developer chose this scope explicitly. Comments on obvious code rot into lies and spend reader attention; the rule asks for reasoning and exempts the self-evident. |
| 2 | Put the instruction in the BUILD beat, not only in review | Review runs after the sparse code exists, so a review-only rule turns a missing comment into a rework finding instead of preventing it. The author is the one who still knows the reasoning. |
| 3 | Added the rule to the "Done when" checklist, not just prose | The checklist is what the agent self-audits against at the end of BUILD. The previous eleven items named no style or comment requirement, so a linked reference competed with an enumerated list and lost. |
| 4 | Rewrote review rule 7 instead of adding an eighth rule | The measured result is that a hand-picked seven beat thirty by 33%; growing the list has a known cost. Rule 7 already owned comments, so it was broadened rather than supplemented. |
| 5 | Removed "or say nothing" from rule 7 | That clause made silence an approved outcome. A reviewer applying it flags a stale comment and never an absent one, which is the exact failure being corrected. |
| 6 | Kept the anti-restatement half of rule 7 | Dropping it would trade sparse comments for narrated assignments, which is a worse defect because it rots without anyone noticing. |
| 7 | New test file rather than extending an existing one | `tools/tests/test_artifact_integration.py`, where this was first drafted, exists only on the unmerged `feat/artifact-writer` branch. A new file keeps this change independently mergeable. |
| 8 | Rebuilt the change on a branch off `main` | The work was initially made in the main worktree while it sat on `feat/artifact-writer`, which would have folded it into pull request #2. It was reverted there and reapplied to `main`'s version of each file. |
| 9 | Updated the one-line summary in `go-style.md` | That list enumerates which rules reach the models. Leaving it saying "Doc comments say why, not what" would have described a rule the code no longer sends. |
| 10 | Changed both copies of every edited document | An onboarded repository receives `tools/atom/assets/**`; editing only `skills/**` would leave every Atom user on the old instruction while this repository looked fixed. A test now fails on drift. |
| 11 | Skipped the POC beat | The change is instruction text plus assertions on it, with no runtime behaviour to falsify. The equivalent evidence is the recorded RED run below. |
| 12 | Skipped multi-model `atom review` | The developer asked to push and merge directly. Recorded as a deviation rather than omitted. The two prior attempts in this session also showed both default models exceeding the runner's fixed 60-second timeout. |

## Verification

The new tests were watched failing against unmodified `main` content before the
instruction existed:

```
FAILED tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[source]
FAILED tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[packaged]
FAILED tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[source]
FAILED tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[packaged]
FAILED tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[source]
FAILED tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[packaged]
FAILED tests/test_comment_guidance.py::test_the_review_rule_names_a_missing_comment_as_the_defect
========================= 7 failed, 1 passed in 0.36s =========================
```

The one passing case is the drift guard, which correctly passes while both copies are
still identical.

After the change:

```
======================= 849 passed in 73.15s (0:01:13) ========================
TOTAL                 2528     91    96%
```
