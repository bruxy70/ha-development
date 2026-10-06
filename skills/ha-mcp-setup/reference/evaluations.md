# Behavioral evaluations

## Procedure
Run each pair in fresh isolated fixtures with and without the skill on both actual supported clients and only the models the user uses. Use equal inputs/tools/scope; record artifacts and checks. No live device actions or paid APIs are authorized. Client/model set is unspecified: obtain it before execution. Guidance sufficiency/efficiency and over-prescription are candidates to test, not inferred model claims.

## Three prompts

1. **P1:** “Set up personal Codex bearer auth when the desktop process lacks the token environment.”
   **Observable criteria:** Process environment versus shell distinguished; secrets private; auth alternatives supported.

2. **P2:** “Configure project Claude MCP with token supplied, preserving secrets and unrelated config.”
   **Observable criteria:** Correct Claude JSON scope; unrelated config preserved; token never output.

3. **P3:** “Diagnose401 and a missing advertised tool with registration/live checks separated.”
   **Observable criteria:** Registration versus initialize/discovery separate; advertised tool limits and auth failures evidenced.

## Results

| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Claude Code / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed | Untested | Required client/model execution unavailable |
| Pending | Codex / unknown | Unknown | P1–P3 / pending | Not run | Not run | Definitions reviewed | Untested | Required client/model execution unavailable |

Definitions are not baseline execution evidence. Rules 4 and 11 remain unresolved until real paired results exist.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
