---
project: "readme-first-run"
date: "2026-10-30"
---

# Decisions

- The developer explicitly requested publishing the existing README update first. Use one narrow documentation commit and a pull request against public `girishmotwani/atom`; do not merge main or publish any other plan.
- Reuse the already drafted first-run introduction: supported Go/Copilot audience, existing plugin commands, onboarding action and failing-baseline caveat, detailed-documentation links and one optional star prompt. Preserve the existing detailed instructions below.
- No artificial Go POC, design/TDD implementation or paid multi-model review is performed: this change adds no executable behavior and repeats shipped/documented commands. It does not relax the engineering pipeline for other work.
- Validate the actual documentation diff and internal links immediately before committing. Do not rerun unchanged Python/Go code suites or claim they passed for this documentation-only change. The repository has no root Go module for `atom check`.
- Commit only README and these two required audit records. Exclude all local visibility planning, site experiments, v1.0 roadmap material, installation changes and private operational evidence.
- Push is authorized by the explicit publication request. Opening the PR does not authorize merging it, release publication or other external writes.
