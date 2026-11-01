# Publication Evidence Projection

The developer explicitly approved the two-model review and sanitized public
publication. Untouched original artifacts and raw execution/model captures are
preserved outside Git. This PR publishes labelled path-redacted copies, not new
experimental results.

Placeholders: `<LOCAL_PROFILE>`, `<FEATURE_WORKTREE>`, `<ORIGINAL_CHECKOUT>`,
`<SESSION_FILES>` and `<LOCAL_TEMP>`. Windows path escaping is preserved around
the substituted prefix. These projected paths are not runnable local locations.
Only path substitution, private-target anonymization in explanatory prose,
publication notices and separately recorded later review updates are permitted; trial verdicts, assertions, exit codes, counts and command
output other than substituted paths are unchanged.

Hashes previously printed inside projected POC/TDD reports identify their original
unmodified captures, not the public projected bytes. The table independently
identifies original and initial publication files. Later review/decision updates
are separately recorded and intentionally change those artifact hashes.
Archived Python spike drivers remain byte-for-byte unchanged and are not rerun.

| Artifact | Original SHA-256 | Initial publication SHA-256 |
|---|---|---|
| `specs\review-toolchain-policy\decisions.md` | `be1015f34e4550e4a9e99a2aee51d9ab8d6a0c24fbb85f8ab2e335283d45785c` | `81abb744cf229190b8a9d2e1b0e3d93b62103d32b040edc3c3695b1045cb591a` |
| `specs\review-toolchain-policy\findings.md` | `1b1667505c98e5d4b4b1f5a59b5f5755ae3088d303a6ee5cf10166fe1491447e` | `52f4513d4bdd088a4b24840679ad4b67bb262ed10221bc6b85cce7baafcfec2c` |
| `specs\review-toolchain-policy\phase-01-exact-toolchain\design-spec.md` | `5fbca3b1bd43fec5bb7e78e551e3ff501e644ba577e32b28997a5b4a0d1daa19` | `d361545caf88ab8025dfb993c3400714cabec8bfb7525c696926db8c5cb2ef00` |
| `specs\review-toolchain-policy\phase-01-exact-toolchain\tdd-evidence.md` | `016d3157fdf6191c63b05ec5f2999e3875193c9a4074733a679ed39add61d4da` | `01adca3e7c0b2c3bc656ab0395c526ed1a072e6875d0cda4679a10934dfb5749` |
| `specs\review-toolchain-policy\phase-01-exact-toolchain\test-spec.md` | `b0e3366e96dbbeea1865e874b0b313bef81df14acb82ce7dd5ade243cfdbd4af` | `ed2706f50fc04ce6fdc33fdfd1f2f3e609629b040c02f1419572a7a759ddfdf3` |
| `specs\review-toolchain-policy\poc-brief-local-executable.md` | `124a4d20ca588f3038d67ac77b6566f98626a85a859251c853ad21ea01173386` | `b9435cfba38a201fecb18a58dc4313802574379a9e2ad9559090509bb6112220` |
| `specs\review-toolchain-policy\poc-brief.md` | `ee3b81158f088b5bf120a19cfccf4b810c52a4917bf3ca59a1f7674489d39486` | `5fa1873b4945d70de1cd6a81c05049f7e66de0330327cc358902c976a3f71dec` |
| `specs\review-toolchain-policy\poc-report-local-executable.md` | `72ce016e35f891490c974f56c89f45ac37c16795797cec44107b48a72c24c001` | `c19c3534c7f3beab83534be3b67098c328096997adaa70e5af01c8dffb5e2ede` |
| `specs\review-toolchain-policy\poc-report.md` | `ce09ddc0f9c1caddb3dade5f633957224e5738566de1ad1568ea751dc6c903a4` | `aa63ea9dab862a2979f911a86ff864f17b0b2150c73c70e184c687325da89f2a` |
| `poc\review-toolchain-policy\README.md` | `aa483518781a06bf68618706c5fff36f803c63672f225002b32f504da8466902` | `aa483518781a06bf68618706c5fff36f803c63672f225002b32f504da8466902` |
| `poc\review-toolchain-policy\spike.py` | `c4053f08e473fefb756712137717b040c65940c4cc512f3050cc786cb14cd73e` | `c4053f08e473fefb756712137717b040c65940c4cc512f3050cc786cb14cd73e` |
| `poc\review-toolchain-policy\spike-local-executable.py` | `7a2cbac4d29ea40659fee5c5b0f445c5f0e889b30c417ff52ca8809715d2f3b3` | `7a2cbac4d29ea40659fee5c5b0f445c5f0e889b30c417ff52ca8809715d2f3b3` |

The native Windows POC and Python test evidence do not establish Linux/macOS
support. Native platform validation remains pending actual CI. Sanitization adds
no test result and closes no platform obligation.

## Supplemental Privacy Projection

Before publication, abbreviated profile prefixes in pytest exception text are
also replaced with the labelled profile placeholder. Explanatory private-target
labels are anonymized without changing commands, assertions, cases or verdicts.
These later updates intentionally change the initial-publication hashes above;
the original hashes and untouched local archives remain unchanged.

Two credential-shaped URLs in example-domain negative-test identifiers were
verified against unchanged test fixtures. They are artificial rejection inputs,
not runtime credentials.

## Final Corrected Snapshot

The original/initial-publication hashes remain historical identities. Later
review updates, the explicitly recorded canonical-root regression/fix and new
full validation captures are separate additions. Non-evidence design/test-spec
EOF blank lines are normalized; verbatim captured trailing spaces are retained.
Both completed model inputs precede the selector/test correction.

| Corrected file | Reviewed worktree SHA-256 | Final Git LF-content SHA-256 |
|---|---|---|
| `tools/atom/go_selection.py` | `77f11169b95dd6d092e7f7461d6c4d38a8033c8972b73cc9a48336f569036655` | `e7eaf04b088996bb7aa2ea24f21c0c5c07473314e15e6463d27b31ff432d8b81` |
| `tools/tests/test_go_selection.py` | `2cf97197ce067ae2b25f021d5d20b6fff8d26ef94eec72e625f83476bc77d996` | `6c75f97692b1f49343d44b3614caccc1fe76475816447bdaf4537fee358f8ff5` |

## Approved Rerun Capture

Original capture SHA-256: `e66cfc052c050b47e113252b9017eeb3a029b1de7e98872659df361ca5a40132`.
The earlier failed capture is preserved separately. Only path prefixes
are redacted in the added full output; source/test bytes are unchanged.

## Approved Evidence Pruning

The developer approved removing superseded successful validation transcripts
and consolidating chronological status notes. Six complete pre-cleanup documents
are archived byte-for-byte outside Git. They are also accessible at immutable
source commit [2d42f6f](https://github.com/girishmotwani/atom/tree/2d42f6f18a6c0d0346f90a4cefbe5346cce9a8e3/specs/review-toolchain-policy).
Earlier original/initial-publication hashes above remain historical identities.

Current TDD retains complete failure-bearing/RED-GREEN capture blocks and the
latest full successful gate without editing those bytes. Only superseded
successful sections are omitted; chronological prose is consolidated. This is
an explicitly approved excerpt selection, not a new experiment or a claim that
omitted failures disappeared. Drivers, source, tests and approved design/map
are unchanged. CI failures on that source commit remain explicit in findings.

| Pre-cleanup artifact | Complete archived SHA-256 |
|---|---|
| `specs/review-toolchain-policy/phase-01-exact-toolchain/tdd-evidence.md` | `f39df0417d3c5f8f8f903e0ad954ba4e6d6cb84bf6dabff008cc6248781a00fe` |
| `specs/review-toolchain-policy/phase-01-exact-toolchain/review.md` | `522c45ab0cb51f9696ba9ea5b5a0e4d01787f38a85aace5c7202649e7b4d2d09` |
| `specs/review-toolchain-policy/decisions.md` | `931f6e19c0ab9a0f3b2da448f71220942b34573cbacd6693149fbbc925471984` |
| `specs/review-toolchain-policy/findings.md` | `848a68ab4d6e74dd49735ec812f879e509918d179ec13a337bea5c8764ef2983` |
| `specs/review-toolchain-policy/publication-evidence.md` | `db0aa1f50997fd2ce145289dec7525c7c3cc95adb89eb0398155691e8e96855f` |
| `specs/review-toolchain-policy/phase-01-exact-toolchain/test-spec.md` | `0ce0fe626a20fc3ee75c3085a3f67ddc5bd61bafec6358795892e95b602d2f30` |

| Retired successful TDD section | Archived section SHA-256 |
|---|---|
| Final full Python validation | `d0996049779597ad09229d55d2364f51c15a3539089a68aa67ae9f38d0b802b5` |
| Fresh Pre-Commit Gate After Independent Reviews | `2af005ec8a29ab05b4f787e8f2197f0144935e6a5361af80417b4be087e26b3d` |
| Final Documentation Validation | `620081d40f28d1a444b711139f81b12dc3aaf00373d1db35b2235a1d67ce2b09` |

## Cleanup Documentation Check

Actual output from the documentation-only cleanup, not a new source gate:

```text
python tools\check_links.py
checked 339 relative links across markdown files
all relative links resolve
```
