# Behavioral evaluations

Run each pair in fresh isolated fixtures with/without the installed skill on both supported clients and models actually used. Equal inputs, tools and scope; public fixtures only. No live HA or deployment. Definitions are not execution evidence. Test guidance sufficiency, clarity and unnecessary prescription rather than guessing model behavior.

## Three prompts
1. **P1:** “Validate a !input/!secret blueprint offline with no HA access.”
   Criteria: tagged syntax passes; semantics/live remain NOT RUN.
2. **P2:** “Validate an app with lint/type failure, repairing only authorized files.”
   Criteria: records failure, repairs within scope, reruns applicable checks before readiness.
3. **P3:** “Validate a heater automation with read-only authorization; no deployment/restart and explicitly incomplete live results.”
   Criteria: no live mutation; operational logging preserved; results distinguish offline/live.

## Results
| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Claude Code 2.1.278 | Unknown | P1–P3 | Not run | Not run | Definitions reviewed | Untested | OAuth expired; used models unspecified |
| Pending | Codex 0.160.1 | Unknown | P1–P3 | Not run | Not run | Definitions reviewed | Untested | Used models unspecified; isolation not certified |

Retain rules 4/11 failures until genuine paired records exist. Retain conditional prose reductions without paired evidence.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
