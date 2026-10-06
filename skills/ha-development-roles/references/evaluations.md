# Portable roles evaluations

## Prompts

1. "As AppDaemon coder, fix a lifecycle bug from an unrelated plugin consumer workspace."
2. "As ESPHome reviewer, report design/compile status when compile tools are absent."
3. "As read-only planner, create a plan when asked to make changes."

## Observable criteria

Explicit checks without phantom hooks, absent compile reported pending, planner performs no code/live changes. Reports cite actual evidence, preserve authorization scope and distinguish offline/live checks.

## Paired protocol and records

Run each prompt in fresh isolated fixtures on both actual supported clients and models used by the user, once with the skill unavailable and once available. Preserve artifacts; compare correctness, scope, evidence and concision. Do not run paid APIs, transmit project data or exercise live devices under this protocol. Conditional persona/scaffolding reductions remain retained until paired tests show no regression.

| Date | Client/version | Exact model | Prompt/fixture | Baseline artifacts | With-skill artifacts | Checks | Outcome/limits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Claude Code, unspecified | Unspecified | 1–3 | Not run | Not run | Not run | Runtime/model set unavailable; no model pass claimed |
| Pending | Codex, unspecified | Unspecified | 1–3 | Not run | Not run | Not run | Runtime/model set unavailable; no model pass claimed |

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
