# Decisions

- The developer chose guidance-only changes over another interactive trial and
  approved [design-spec.md](design-spec.md). Existing accepted discovery evidence is
  reused within its stated limits; no unproven runtime resolver is introduced.
- Windows PATH setup becomes request-only rather than an automatic question. It
  remains explicitly opt-in and its implementation is unchanged.
- This is a documentation-only change with no Go module at the repository root.
  The approved verification maps claims to factual review and existing Python
  documentation/packaging checks; no Go RED/GREEN or root `atom check` is claimed.
- The developer requested a pull request and push. Merging remains a human-only gate.
- Reviewed this small documentation diff directly rather than running a multi-model
  review. The limitation is explicit in review.md and findings.md; no independent
  review or Go review gate is claimed.
