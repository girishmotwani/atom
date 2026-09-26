# POC Claims: plugin-shipped rules and beat-routing accuracy

Question: can a plugin ship a routing table that reaches the model without
repo injection, and does it make beat selection more accurate?

Registered before any measurement was taken.

## Claims

C1. A file at `com.github.copilot/rules/*.md` ships with the plugin and its
    instructions reach the model from a neutral working directory (no Atom
    repo, no AGENTS.md, `--no-custom-instructions`).
    Detect: a unique sentinel token placed in the rules file appears in the
    reply to an unrelated prompt.

C2. Adding rules does not suppress skills or commands.
    Detect: all 9 skills and all 10 commands still register, and `/atom-poc`
    still resolves to the skill.

C3. Baseline beat-routing accuracy is measurable across 9 beats x 3 prompts.
    Detect: each SKILL.md carries a sentinel that names itself, so the loaded
    skill is read off the reply instead of inferred from tone.

C4. Rules change routing accuracy.

## Pre-registered adoption bar

Ship the rules file ONLY if BOTH hold:
  - accuracy with rules >= 80% (>= 22 of 27 trials), AND
  - accuracy with rules is strictly greater than baseline.

If rules do not improve accuracy, do not ship them. Record the null result.
Do not move this bar after seeing the numbers.

## Verdict rule

Confirmed if C1 and C2 pass and C3 produces a number.
C4 decides adoption, not the verdict.
