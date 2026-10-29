# Public publication decisions

The developer explicitly directed all publication to public girishmotwani/atom, selected sanitized public-history copies, and reconfirmed sanitizing and publishing both PRs before further adoption work. ADO remains draft/conflicting. No private PR closure, merge, force-push, public-history rewrite or integration change is authorized.

Recreated each unpublished commit with mapped sanitized parents, keeping original private refs and captured evidence intact. This is not a tip-only redaction. Original private commits are not newly reachable through the public branches. Public common ancestry is deliberately unchanged. The [commit map](history-map.json) records provenance; text references to old hashes are historical identifiers, not newly published Git objects.

Only explicit profile-prefix substitutions and publication labels change the historical evidence trees. All runtime code, tests, packaged assets, skills, POC source, file modes and non-evidence blobs are byte-identical to the accepted originals. No replacement design, runtime implementation, new POC, paid review or real-model call is included. Prior independent [review](../review.md) applies to that unchanged code; this publication audit is not a new independent model review.

The fresh full Windows/Python gate ran on sanitized code snapshot `f58e639038c8abb764e132bfda3a457b6960b3a9` before this final evidence-only commit. It uses Atom's existing Python test gate, not a fictional root Go/race gate. Historical copied commits were constructed before this fresh run, but no runtime code changed; the final publication-record commit follows the passing run. The [complete captured output](verification.txt) is retained with any local profile prefixes explicitly redacted; outcome/counts are unmodified.

The first full attempts failed one wheel-installation test on each branch because the launch command explicitly injected source PYTHONPATH into the test's isolated environment. The failing test passed unchanged with that override removed; both complete suites were then rerun with the normal environment. No assertion, dependency or runtime code was changed. The failed logs and narrow recheck remain privately retained.

Historical redaction paths relative to the accepted original tip:

- `specs/repeat-init/poc-report.md`
- `specs/repeat-init/ship-verification.txt`
- `specs/repeat-init/verification-probe.txt`
- `specs/repeat-init/verification.txt`
- `specs/user-path-bootstrap/review.md`

Final documentation verification (python tools\check_links.py, exit 0):

```text
checked 240 relative links across markdown files
all relative links resolve
```
