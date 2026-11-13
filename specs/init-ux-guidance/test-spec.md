# Guidance Validation Mapping

This change modifies instructions, not executable command behavior. The developer
approved the documentation-only validation in [design-spec.md](design-spec.md).
No production RED/GREEN loop or new Go test is claimed.

| Spec | Required check |
|---|---|
| 1 | Review unchanged active-client, Go, verified-role and reuse instructions. |
| 2 | Review grouping instructions for order, availability, immediate real-error stops and diagnostic/status preservation. |
| 3 | Walk package ambiguity, partial/broken installations, safe venv and explicit-install-consent branches. |
| 4 | Review canonical and packaged init/bootstrap wording: no automatic PATH question; explicit request retains setup-path and exact forms. |
| 5 | Review distinct init/install/writer approvals, baseline failure, writer-refusal and success-path verification guidance. |
| 6 | Compare both canonical/packaged pairs byte-for-byte; run existing plugin, hidden-writer and PATH documentation contracts. |

Run the listed focused Python tests and relative-link/whitespace checks. Walk the
changed documents for contradictions. Text assertions cannot establish actual
agent adherence or approval count; report those as unverified. No behavioral
performance, concurrency or runtime claim is made.
