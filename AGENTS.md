# Atom — Agent Instructions

Atom is an agentic development framework for **Go**. It exists to stop agents from
writing large amounts of speculative code against an imagined design.

Read this file before doing any work in an Atom-enabled repository.

---

## The One Rule

> **Nothing gets designed until something has been proven to work.**

Every unit of work — the whole project, and then each phase within it — follows the
same three beats:

```
   PROVE  ──────────▶  DESCRIBE  ──────────▶  BUILD
   (POC)               (spec)                 (TDD)
```

1. **PROVE** — write a throwaway Go program that exercises the risky part. Run it.
   Watch it work, or watch it fail and learn why.
2. **DESCRIBE** — only now write the design spec, informed by what the POC taught you.
3. **BUILD** — red/green/refactor against that spec, with the developer in the loop.

Skipping straight to step 2 or 3 is the failure mode Atom is built to prevent. If you
catch yourself reasoning "this is simple enough that a POC is unnecessary", see
[anti-rationalization.md](skills/atom/references/anti-rationalization.md).

---

## Pipeline

```
  problem statement / MRD
        │
        ▼
  atom-discover   interview the developer → POC Brief
        │  ◆ gate
        ▼
  atom-poc        throwaway Go spike, executed → POC Report
        │  ◆ gate
        ▼
  atom-plan       phase breakdown → Phase Plan
        │  ◆ gate
        ▼
  ┌─ per phase ────────────────────────────────┐
  │   atom-poc     spike this phase's risk     │
  │        ◆ gate                              │
  │   atom-spec    high-level design spec      │
  │        ◆ gate                              │
  │   atom-tdd     red → green → refactor      │
  │        ◆ gate                              │
  │   atom-review  multi-model review          │
  └────────────────────────────────────────────┘
        │
        ▼
  atom-ship       commit + pull request
```

| Skill | Purpose |
|---|---|
| `atom-init` | Onboard a Go repository to Atom |
| `atom-discover` | Turn a vague problem into a concrete POC Brief, by asking |
| `atom-poc` | Build, run and evaluate a throwaway Go spike |
| `atom-plan` | Break proven work into ordered, independently shippable phases |
| `atom-spec` | Write the high-level design spec for one phase |
| `atom-tdd` | Implement one phase test-first |
| `atom-review` | Multi-model review of a diff |
| `atom-ship` | Commit, push, open a pull request |
| `atom-build` | End-to-end orchestrator chaining all of the above |

Each skill lives in `skills/<name>/SKILL.md`.

---

## Working With the Developer

Atom is **collaborative, not autonomous**. The developer is a participant, not an
approver of finished work.

- **Ask one question at a time.** Never present a numbered list of questions and ask
  the developer to answer them all.
- **Explore before asking.** Read the repository first. Only ask what the code cannot
  tell you — intent, priorities, trade-offs, acceptance criteria.
- **Stop at gates.** A gate means: present the artifact, end your turn, wait. Do not
  proceed on an assumed yes. The full protocol is in
  [human-gates.md](skills/atom/references/human-gates.md).
- **Disagree when you have evidence.** If the developer states something the code
  contradicts, say so and show the contradiction. Agreeing without checking is a
  failure, not politeness.

---

## Verification

A claim of completion requires evidence. "It should work" is not evidence; a
command's output is.

```bash
atom check          # go build ./... + go vet ./... + go test ./... + coverage
```

Every gate that claims code works must be backed by real `atom check` output pasted
into the artifact. Rules in
[verification.md](skills/atom/references/verification.md).

Atom has **no hidden enforcement**. There is no secret monitor rejecting your work.
The gates are local, runnable, and inspectable — which is precisely why you must
actually run them.

---

## Go Code Standards

Atom deliberately **prefers readable and extensible Go over maximally idiomatic Go**.
When the two conflict, readability wins.

The rules are in [go-style.md](skills/atom/references/go-style.md). The short version:

- Name things for what they mean, not how short they can be. `retryBudget`, not `rb`.
- Prefer an explicit `if err != nil` chain over a clever abstraction that hides flow.
- Every exported symbol has a doc comment explaining *why* it exists, not just what it is.
- Non-obvious logic gets an inline comment explaining the reasoning.
- Accept interfaces you define at the point of use; return concrete types.
- Prefer composition and small interfaces so behaviour can be extended without editing
  existing code.
- `context.Context` is always the first parameter on anything that can block.

---

## Model Guidance

Atom's loop involves planning, critique and self-review, which benefits from stronger
reasoning than single-pass code generation.

**Recommended: HydraFusion** in GitHub Copilot CLI — it orchestrates several models
per task (single / cascade / critique routing) rather than committing to one.

```
/update
/experimental on
/model          → select HydraFusion (Research Preview)
```

Details and fallbacks in [model-guidance.md](skills/atom/references/model-guidance.md).

---

## Artifacts

Atom writes everything to disk so the work is reviewable, resumable, and diffable.

```
.atom/
  state.json                   # pipeline + phase state
  events.jsonl                 # structured event log
specs/
  <project>/
    poc-brief.md
    poc-report.md
    phase-plan.md
    findings.md                # discovered problems, deferred items
    decisions.md               # every deviation from these instructions
    phase-01-<slug>/
      poc-brief.md
      poc-report.md
      design-spec.md
      test-spec.md
      review.md
poc/
  <slug>/                      # throwaway Go spikes, kept for reference
```

Two artifacts are **always** produced, even when empty:

- **`findings.md`** — anything you noticed but did not fix. Ambiguity, tech debt,
  suspicious code. If nothing, write "No findings."
- **`decisions.md`** — every time you deviated from an instruction, skipped a step, or
  chose between two valid approaches on your own. If nothing, write "No deviations."

These exist so the developer can audit your judgement. Omitting them hides it.

---

## Delegation

Use subagents for bulk work — reading large files, implementing independent
components, running long test suites. Run independent work in parallel.

Do **not** delegate: gate conversations with the developer, the decision of whether a
POC succeeded, or reading this file and the discipline references. Those are yours.
