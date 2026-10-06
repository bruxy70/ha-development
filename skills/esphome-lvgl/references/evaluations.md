# Behavioral evaluations

Run each prompt in fresh isolated fixtures, once without this skill and once with it, on the actual Claude Code and Codex versions/models used. Preserve fixture inputs and output/check artifacts. No live HA action, deployment, paid API call or data export is authorized by this evaluation.

## Prompt 1

> Create a gauge and slider controlling an HA light without drag-time service spam; handle unavailable state.

Observable checks: Schema/API correctness; release-only service action; unavailable-state handling and HA feedback.

## Prompt 2

> Migrate this config to the installed ESPHome version; resolve rotation/API differences and report config/compile evidence.

Observable checks: One rotation route; vendored API match; genuine current-source config/compile evidence or honest unavailable results.

## Prompt 3

> Gauge-card taps work only at its edge; diagnose generated code and propose a minimal fix.

Observable checks: Read generated code without edits; hit-test evidence; minimal source fix and verification.

## Results

| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Unspecified | Unspecified | 1–3 | Not run | Not run | None | Untested | Actual client/model set and isolated execution required |

Definitions are not executed baselines. Rules 4 and 11 remain unverified until genuine paired records exist. Compare shorter scaffolding variants only after retaining hard domain invariants; retain original guidance if uncertain or worse.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
