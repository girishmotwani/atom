---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
status: "implementation-approved"
---

# Init UX Guidance-Only Repair Spec

## Goal and scope

Reduce unnecessary visible bootstrap operations and the optional Windows PATH
question without replacing Atom's commands or weakening its safety boundaries.
Change `skills/init/SKILL.md`, `skills/atom/references/bootstrap.md`, and their
byte-identical `tools/atom/assets/skills` mirrors. If the README or another
shipped contract conflicts, stop and propose its narrow correction before adding
it to scope. No Python runtime, bundled resolver, public command, dependency,
permission configuration, installation recipe or current installed plugin changes.

## Evidence and limits

The accepted [prerequisite-flow-repair-report.md](../atom-v1-improvements/phase-09-onboarding-example/prerequisite-flow-repair-report.md) established working Windows
entry-point discovery and Ubuntu known-venv reuse with separate read-only
operations. The accepted [package-detection-repair-validation.md](../atom-v1-improvements/phase-09-onboarding-example/package-detection-repair-validation.md) established
selected metadata/module observations and document parity. Those observations
are reused only within their recorded platform, health and error limits.

The new [evidence.md](evidence.md) is Inconclusive for an integrated resolver:
its local prototype found the observed installations and selected fixtures but
was not invoked through a plugin. The separately authorized interactive local-plugin
trial proved a harmless bundled script ran, but approval details were not captured
([evidence.md](evidence.md)). Neither report establishes a prompt count,
marketplace-plugin behavior or agent compliance. The developer selected the
narrower guidance-only path rather than another trial. This is not a confirmed
resolver POC; no new resolver is designed here.

## Intended workflow

1. Retain the active-client and Go prerequisites and both verified command roles
   before `atom init`. Reuse exact forms already verified in the unchanged session
   and stop discovery immediately when both roles work.
2. In bootstrap, explicitly instruct agents to group compatible **read-only**
   discovery checks into as few terminal invocations as safely possible. Within
   any group, retain the original sequential order, decisions and exact role forms;
   a real failure stops before later checks, and diagnostics/statuses stay visible.
   Do not require Python if both entry points work. Do not execute a missing role
   to discover absence, inspect Python source, or switch away from partial/broken
   installations. Do not invent a new packaged script or broad approval.
3. Where checks cannot be safely combined without losing a prerequisite decision,
   output, status, ownership validation or required user consent, perform them
   separately. Combining is an instruction about tool-call grouping, not a shortcut
   around the existing Step 1-4 decision table, package-collision rules, ownership/
   prefix checks, explicit install consent or writer-refusal stop.
4. Do not ask the developer to opt into Windows PATH changes during normal init
   when verified module forms already work. Explain once that those forms are in
   use. If the developer explicitly requests PATH setup, follow the existing
   opt-in `setup-path` procedure and reuse its printed absolute commands. Do not
   alter PATH or profiles without that instruction. This deliberately replaces the
   old automatic one-time offer; it does not remove the feature.
5. Keep `atom init`, installation and artifact-writing approvals distinct. Do not
   add success-path verification shell calls, conceal failing baselines, claim
   fixed approval counts or imply the text enforces agent behavior.
6. Align both canonical/packaged pairs byte-for-byte; retain all other bootstrap,
   first-init, repeat/no-op, error and handoff contracts.

## Errors, concurrency and extension

The grouping must propagate each originating nonzero status and full relevant
output; expected absence remains an observation, not a synthetic failed help.
Unsafe, ambiguous, conflicting, partially working or failing installations remain
preserved and reported as under the accepted prior specs. Concurrent installation
remains unsupported, and the change adds no workers, locks or persistent state.
The existing shared bootstrap remains the extension point; package or runtime
changes require a separate evidenced decision.

## Validation and trade-offs

Before shipped edits, record a claim-to-check mapping. Factual review must walk the
existing bootstrap branches and ensure grouping does not cross a consent/error stop.
Run the existing targeted plugin, hidden-writer and PATH documentation contracts;
check both canonical/packaged pairs are byte-identical; run `python tools\check_links.py`
and `git --no-pager diff --check`. Run any directly affected documentation tests and
record exact output. Do not claim these text checks prove model behavior or actual
interactive approval reduction; the question remains open for a separately agreed
user rehearsal. A runtime resolver would give deterministic grouping but its plugin
integration and permission UX have not been established. Keeping the old flow avoids
instruction changes but leaves the reported friction. This narrower text approach
is reversible and keeps the existing technical discovery behavior.

## Approval boundary

The developer approved this guidance-only spec for implementation. Approval covers
only the four shipped guidance files and the stated factual/packaging checks. A needed wider edit,
failed safety mapping or material change requires a new decision. The developer's
previous PR request authorizes pushing and opening a PR after the required work and
review, not merging. The actual user-visible improvement remains unmeasured.
