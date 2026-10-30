# Independent review: module-rule delivery

Status: independent review complete; developer triage approved; fixes verified for commit/push.

## Scope and evidence

Both approved independent models completed one review: Claude Sonnet 5 and Gemini 3.8 Flash, neither the authoring GPT-6.1 Sol. Exactly two availability probes and two review calls were used, with no retries, substitutions or deadline changes. Native tool exclusions and the approved named custom-server startup exclusions applied only to these calls. Strict ownership-aware JSONL extraction succeeded for both, with no extraction failures. Gemini reported no findings; Sonnet reported two. Neither reviewer saw the other's output.

Both received the same 558255-byte logical prompt containing the complete 18-file diff and 28 full changed/dependency-file contexts. Prompt SHA-256: 1306314a7d0cb2e85c5d71f835a326fe6275699e659e2d918b4945f231ed6dd9. Diff SHA-256: f94e76f84867c17fff78d93e3c654e42abaed625448e8c1d302b8b4c2bece0c4. These identify logical pre-transport UTF-8, not physical Windows stdin bytes. Raw streams, invocation audits, file hashes, full prompt and summary remain outside Git in session evidence, module-rules-independent-review.

Fresh pre-review Python gate, exit 0:

```text
TOTAL                        4181    220    95%
================= 1501 passed, 5 skipped in 189.26s (0:03:09) =================
```

Claude completed in 445.81942960002925 seconds; Gemini in 239.3040737999836 seconds. These are observations, not a latency benchmark. Existing probe/review deadlines remained 60/600 seconds. A single run per model is the approved bounded review, not evidence that all defects were found.

## Deduplicated findings and proposed triage

| Severity | Location | Attribution | Finding and proposed disposition |
|---|---|---|---|
| Major | tools/atom/module_rules.py:63-70 | Direct verification of related Sonnet concern; not two-model agreement | A non-directory intermediate guide component is silently treated as missing on Windows because lstat of its child raises FileNotFoundError. The approved contract fails explicitly on malformed present policy trees. Add an explicit intermediate-directory check and a real-filesystem regression, preserving fail-closed behavior across platforms. Proposed: fix. |
| Minor | tools/tests/test_cli_pr_review.py:213-216 | Sonnet 1/1; Gemini 0/1 | The existing local report test now depends on ambient launch-directory rules. Running it from a temporary directory with blank AGENTS.md fails with exit 1 instead of expected 0. Chdir to the existing isolated tmp_path fixture. Proposed: fix. |
| Minor | poc/module-review-rules/README.md:5-13 | Direct offline verification | The guide exposition changed after the historical trial, so current bundle plus synthetic contract no longer matches the original frozen guide pin. Retain the pin and original verdicts; clarify that historical replay requires the original bundle/evidence, rather than weakening the assertion or spending new calls. Proposed: document limitation. |

Sonnet's reported **high** finding recommended treating NotADirectoryError as optional absence, or broadening the inner catch to OSError. Proposed rejection of that remedy: the approved design explicitly fails on unreadable/nonregular/unsupported present input, and broad OSError handling would also hide permission failures. Direct Windows reproduction instead revealed the related fail-closed portability gap above. Do not silently drop the original report or claim that Sonnet identified the exact Windows behavior.

### Direct reproduction evidence

Malformed `.atom` entry, a real regular file in a temporary module, did not raise ModuleRulesInputError on Windows; the explicit expected-error assertion failed:

```text
AssertionError: Malformed present rule tree unexpectedly treated as absent
```

The existing local report test executed from an isolated directory containing blank AGENTS.md failed for the claimed reason:

```text
E   AssertionError: assert 1 == 0
atom review: module rules: context document 1 empty content
============================== 1 failed in 1.96s ==============================
Controlled invocation-directory reproduction exit code: 1
```

Offline-only historical-guide check; no POC main or model was invoked:

```text
Current bundle plus synthetic contract SHA-256: c86e7bba6bd2886ce8a96bf1c3b2cec47061af63ec634f345132fb1da44ddc17
Matches original trial guide: False
Archived spike would stop at its unchanged frozen-guide assertion before model calls.
```

## Original model findings

The following extracted findings are preserved verbatim as data; proposed triage above does not rewrite their severity or wording:

```json
[
  {
    "file": "tools/atom/module_rules.py",
    "line": 67,
    "severity": "high",
    "message": "The per-component traversal only treats FileNotFoundError as \"source absent\" (line 67), so when an intermediate path segment of the fixed GUIDE path (e.g. a stray non-directory file literally named `.atom`) exists but is not a directory, `path.lstat()`/`path.resolve(strict=True)` raises NotADirectoryError instead, which escapes the inner except and is re-raised as ModuleRulesInputError by the outer handler, causing `atom review` to hard-fail instead of treating the optional source as genuinely not-found as required by design behavior #3; the inner except should also catch NotADirectoryError (or broaden the inner catch to OSError) so a malformed/non-directory intermediate segment is treated as absence rather than aborting the whole review before any model call.",
    "model": "claude-sonnet-5",
    "run_index": 1
  },
  {
    "file": "tools/tests/test_cli_pr_review.py",
    "line": 213,
    "severity": "medium",
    "message": "test_local_reports_have_no_pr_fields invokes `atom review --working` without chdir-ing into an isolated tmp_path, so after this diff's change to always call capture_module_review_rules(Path.cwd()) in cli.py, the test's captured module-rule status (and therefore the prompt contents and potential ModuleRulesInputError) now silently depends on whatever AGENTS.md/.atom bundle happens to exist in the real process working directory at test time, making the test non-hermetic and its pass/fail outcome unreproducible across different invocation directories; the test should chdir into tmp_path (as prepared_cli and the other new module-rule tests do) to pin down the launch root before asserting on review output.",
    "model": "claude-sonnet-5",
    "run_index": 1
  }
]
```

## Gate

No fixes, commit or push performed during triage. Developer decision required on the two proposed fixes and the POC replay clarification. Any fixes require fresh verification. The approved paid-call budget is exhausted; additional model calls need separate approval. Original POC verdicts remain Inconclusive, and portable toolchain/degraded-review requests remain separate.
## Final triage and verification

The developer explicitly approved both fixes, the historical-guide clarification, rejection of the broad filesystem-error-as-absence remedy, and continuation to commit/push after verification. The Windows malformed-parent fix now validates intermediate directories explicitly. Three real-filesystem regression cases were observed failing, then passed. The local report test now changes into tmp_path; the same ambient-policy reproduction changed from failure to success without loosening assertions. The archived POC README documents its original-guide replay boundary; the original pin and Inconclusive verdicts are unchanged.

All proposed triage items are resolved by fixes or explicit documentation; no accepted Blocker/Major remains open. The two independent reviews cover their recorded pre-triage snapshot. These approved small corrections were verified deterministically and by the full suite, not by an unapproved second model batch. The three native symlink fixtures remain privilege-limited, and real-project review quality remains unvalidated.

Final full-suite command, from tools: python -m pytest tests -v --cov=atom --cov-report=term-missing. Exit 0:

```text
TOTAL                        4185    220    95%
================= 1504 passed, 5 skipped in 198.94s (0:03:18) =================
```

The full unedited stream remains outside Git as module-rules-final-shipping-tests.txt. The five skips comprise two baseline skips plus three native-link privilege skips. No additional paid calls were made.
