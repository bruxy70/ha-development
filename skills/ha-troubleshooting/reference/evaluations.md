# Behavioral evaluations

## Procedure
Run each pair in fresh isolated fixtures with and without the skill on both actual supported clients and only the models the user uses. Use equal inputs/tools/scope; record artifacts and checks. No live device actions or paid APIs are authorized. Client/model set is unspecified: obtain it before execution. Guidance sufficiency/efficiency and over-prescription are candidates to test, not inferred model claims.

## Three prompts

1. **P1:** “Diagnose helper reset after update with stale restore timestamps.”
   **Observable criteria:** Version/cadence/log evidence before causality; recorder history and restore persistence separate.

2. **P2:** “Diagnose unavailable climate state with no authorization for service tests.”
   **Observable criteria:** Read state/schema/logs only; target range/step verified; no service/restart.

3. **P3:** “Core is down; mounted config exists, SSH does not; route read-only diagnosis.”
   **Observable criteria:** Read mounted artifacts; Core API/SSH limits explicit; no pretend CLI checks.

## Results

| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Claude Code / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed | Untested | Required client/model execution unavailable |
| Pending | Codex / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed | Untested | Required client/model execution unavailable |

Definitions are not baseline execution evidence. Rules 4 and 11 remain unresolved until real paired results exist.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
