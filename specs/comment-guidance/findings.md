# Findings

- The gap was asymmetric delivery, not a missing rule. `skills/atom/references/go-style.md`
  has always required why-focused doc comments and inline rationale for non-obvious
  logic, but only the reviewer ever received engineered rule text (`tools/atom/style.py`).
  The author received a documentation link during BUILD and an eleven-item completion
  checklist that mentioned neither comments nor style.
- The pasted Fidelius diff shows the consequence. Its new code performs cgroup path
  parsing, containment checks, filesystem-identity probing and fail-closed validation
  -- decisions whose reasoning is not recoverable from the syntax -- while most added
  comment lines were test labels rather than rationale.
- Not fixed: nothing mechanically verifies comment quality. `atom check` runs build,
  vet, gofmt, tests, race and coverage, none of which observes commentary, so this
  change strengthens an instruction rather than adding a gate. A Go linter such as
  revive or staticcheck ST1000/ST1020 would convert the exported-symbol half of the
  rule into toolchain evidence; that is a separate decision with its own cost, because
  it would gate every onboarded repository.
- Not fixed: the wording of the new instruction is untested. Atom has measured which
  *defects* reviewers report, never which *phrasings* produce better authoring, so the
  effect of this text on generated comments is unmeasured.
- Unrelated and pre-existing: the "Doc links resolve" CI job fails on every open pull
  request because `tools/atom/assets/skills/atom/references/what-the-toolchain-proves.md`
  links to `../../../poc/compiler-guarantees/`, which resolves only from the source copy
  of that file and not from the packaged mirror three directories deeper.
