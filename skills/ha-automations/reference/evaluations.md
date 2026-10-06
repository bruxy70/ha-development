# Behavioral evaluations

## Procedure

Run each prompt in fresh isolated fixture contexts with the skill available and unavailable, on both actual supported clients and only the models the user uses. Keep fixtures, tools and task scope equal. Record baseline and with-skill artifacts, observable checks, scope discipline and limits. Do not use live devices or paid APIs without separate authorization. Model names/versions are currently unspecified; ask for them before model runs. Haiku guidance sufficiency, Sonnet efficiency and Opus over-prescription are hypotheses to test; do not invent Fable behavior.

## Three prompts

1. **Prompt P1:** “Convert an attribute-sensitive state automation to purpose syntax without changing behavior.”
   **Observable criteria:** Preserve attribute/transitions; generic fallback when no equivalent verified.
2. **Prompt P2:** “Build a fan auto-off blueprint distinguishing cancellation and expiry during downtime.”
   **Observable criteria:** timer.finished event; restore:true; cancellation separate; missed expiry needs persisted deadline/startup reconciliation.
3. **Prompt P3:** “Correct collapsed optional inputs with missing defaults and duplicate names.”
   **Observable criteria:** Every collapsed input has a default; globally unique names; semantic/syntax limits recorded.

## Results

| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Claude Code / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed only | Untested | Client/model fixture execution unavailable |
| Pending | Codex / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed only | Untested | Client/model fixture execution unavailable |

Prompt definitions are not executed baseline evidence. Rules 4 and 11 remain unverified until genuine paired results are recorded. Retain uncertain generic/scaffolding paragraphs until shorter variants perform no worse on these fixtures while preserving domain invariants.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
