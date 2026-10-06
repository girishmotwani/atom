# Model Guidance

Atom benefits from models that can reason about evidence, not just generate
code. The framework should choose models by role and capability, then resolve the
concrete model at runtime.

> Do not hard-code model versions in skills or scripts. Name the role and the
> capability; resolve the model from `.atom/config.json`.

---

## Recommended CLI Model: HydraFusion

Use HydraFusion in GitHub Copilot CLI when it is available.

HydraFusion is not a single foundation model. It is a runtime multi-model
orchestration system and research preview. It routes a task through Single,
Cascade, or Critique workflows across models from multiple providers. It uses
cheaper models where they are adequate and escalates to stronger models when the
task needs them.

Enable it:

```text
/update
/experimental on
/model
# select: HydraFusion (Research Preview)
```

HydraFusion is available to Copilot plan users through Copilot CLI experimental
mode.

---

## Why HydraFusion Fits Atom

Atom's loop is judgement-heavy:

- Did the POC actually answer its question?
- Is the result Confirmed, Refuted, or Inconclusive?
- Does the design follow from the evidence, or from an assumption?
- Is a failing test exposing a code defect, a test defect, or a vague spec?
- Does a review finding identify a real bug or just a preference?

Those tasks benefit from critique routing. A single-pass generation model can
produce plausible work quickly; a critique workflow is better at challenging the
work before it becomes the next phase's foundation.

| Atom decision | Why critique helps |
|---|---|
| POC verdict | Separates clean evidence from "basically worked" rationalization |
| Phase plan | Challenges dependency order and missing risks |
| Design spec | Checks that the spec follows from measured facts |
| TDD failure triage | Distinguishes wrong code from wrong test from wrong fixture |
| Review | Brings different blind spots than the authoring model |

---

## Role-Based Selection

Choose models by what the role needs, not by a fixed version string.

| Role | Optimise for |
|---|---|
| Discovery and planning | Reasoning, uncertainty handling, willingness to ask rather than assume |
| POC authoring | Speed and command-line competence; the code is disposable |
| POC verdict | Reasoning, skepticism, and comfort calling a result Inconclusive |
| Spec authoring | Consistency, long-context reasoning, and traceability from evidence to design |
| TDD implementation | Strong code generation, instruction-following, and careful test interpretation |
| Review | A different model from the one that wrote the code, because a model reviewing its own output shares its blind spots |
| Mechanical edits | Speed, reliability, and low cost |
| Gate summaries | Reasoning and concise communication |

Model selection should be version-agnostic. Versions change; roles remain.

---

## Runtime Resolution

Skills and scripts should say what capability they need:

```json
{
  "roles": {
    "specAuthor": {
      "capability": "reasoning",
      "context": "large"
    },
    "pocAuthor": {
      "capability": "fast-code",
      "context": "standard"
    },
    "reviewer": {
      "capability": "independent-critique",
      "distinctFrom": "author"
    }
  }
}
```

The CLI resolves the concrete model from `.atom/config.json` at runtime. This
keeps skills stable when providers rename, replace, or retire models.

Do not write instructions like this:

```text
Use model-x-2026-09 for all reviews.
```

Write this instead:

```text
Use the configured review model. It must be distinct from the authoring model.
```

---

## Reasoning Effort

Raise reasoning effort for weaker or cheaper models to compensate. Lower it for
the strongest models when the task is already well-scoped.

| Model strength | Suggested effort | Why |
|---|---|---|
| Fast or cheap | Higher | Compensates for weaker default reasoning |
| Balanced | Medium to high | Good for planning, spec work, and TDD triage |
| Strongest available | Lower to medium | Avoids unnecessary latency on clear tasks |
| Unknown support | Omit | Not every model accepts an effort setting |

The framework must tolerate models that do not accept an effort setting. Absence
of that knob is not a failure; it is a capability difference.

---

## Context Budget

Compaction erases prior file reads. It does not merely shorten them; it removes
the exact wording from active context.

Compact proactively rather than at the limit. After any compaction, reload these
files before doing anything else:

1. [AGENTS.md](../../../AGENTS.md)
2. [anti-rationalization.md](anti-rationalization.md)
3. The current `SKILL.md`

The honest reason is simple: a summary describes a rule, but cannot substitute
for the rule. Atom's discipline depends on exact wording, tables, and gate
conditions, not on a remembered paraphrase.

| Situation | Action |
|---|---|
| Approaching context limit | Compact before reasoning quality degrades |
| After compaction | Reload the active discipline files |
| Before a gate | Ensure the relevant artifact and reference are in context |
| Before skipping anything | Re-read anti-rationalization and record the decision |

---

## Fallbacks When HydraFusion Is Unavailable

HydraFusion is recommended, not required.

| Task | Fallback |
|---|---|
| Gates | Strongest available reasoning model |
| Spec authoring | Strongest available reasoning model with large context |
| Review | A model distinct from the authoring model |
| POC code | Faster model is fine |
| Mechanical edits | Faster model is fine |
| TDD implementation | Strong code model with good instruction-following |

Multi-model review still works with any two distinct models. The important part
is not the brand name; it is independent critique from a model that does not
share the author's exact blind spots.
