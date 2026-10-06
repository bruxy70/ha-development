# Behavioral evaluations

## Procedure

Run each prompt in fresh isolated fixture contexts with the skill available and unavailable, on both actual supported clients and only the models the user uses. Keep fixtures, tools and task scope equal. Record baseline and with-skill artifacts, observable checks, scope discipline and limits. Do not use live devices or paid APIs without separate authorization. Model names/versions are currently unspecified; ask for them before model runs. Haiku guidance sufficiency, Sonnet efficiency and Opus over-prescription are hypotheses to test; do not invent Fable behavior.

## Three prompts

1. **Prompt P1:** “Sum valid power states excluding unknown/unavailable and return a typed number.”
   **Observable criteria:** Safe state access and defaults; declared native type checked in HA, not inferred from string rendering.
2. **Prompt P2:** “Filter[1,6,9] to values>5 in HA Jinja without mutation.”
   **Observable criteria:** Jinja select returns [6,9]; no Python comprehension or unsafe mutation.
3. **Prompt P3:** “Build timestamp and trigger-based sensors handling missing source and limited contexts.”
   **Observable criteria:** ISO timestamp; missing source safe; explicit update triggers; limited-context helpers verified.

## Results

| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Claude Code / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed only | Untested | Client/model fixture execution unavailable |
| Pending | Codex / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed only | Untested | Client/model fixture execution unavailable |

Prompt definitions are not executed baseline evidence. Rules 4 and 11 remain unverified until genuine paired results are recorded. Retain uncertain generic/scaffolding paragraphs until shorter variants perform no worse on these fixtures while preserving domain invariants.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
