# Behavioral evaluations

Run each prompt in fresh isolated fixtures, once without this skill and once with it, on the actual Claude Code and Codex versions/models used. Preserve fixture inputs and output/check artifacts. No live HA action, deployment, paid API call or data export is authorized by this evaluation.

## Prompt 1

> Render a 300×200 upper gauge at 0/50/100 with correct needle/ticks.

Observable checks: Parse XML; left/up/right endpoint math; upper ticks; crop and label visibility.

## Prompt 2

> Render two translated bidirectional gauges with local gradients and long labels.

Observable checks: Unique IDs; local defs/path coordinates; identical translated colors; label bounds.

## Prompt 3

> Render a 240×240 compass at 0/90/180/270 preserving labels/bounds.

Observable checks: Cardinal headings and arrow positions; actual-dimension rendering and bounds.

## Results

| Date | Client/version | Exact model | Prompt/fixture ID | Baseline artifacts | With-skill artifacts | Checks run | Outcome | Limits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Unspecified | Unspecified | 1–3 | Not run | Not run | None | Untested | Actual client/model set and isolated execution required |

Definitions are not executed baselines. Rules 4 and 11 remain unverified until genuine paired records exist. Compare shorter scaffolding variants only after retaining hard domain invariants; retain original guidance if uncertain or worse.

## Executed structural/geometry checks (not model evaluations)

2026-10-06: resolved actual Template A for values 0/50/100 and two translated copies of actual Template C. All four XML fixtures parsed with Python ElementTree, upper-gauge endpoint calculations passed, and Chromium 153.0.8010.12 rendered the four fixtures. Visual inspection confirmed left/up/right segmented needles clear of text and matching colors on translated bidirectional gauges. Fixtures/screenshots were temporary verification artifacts; long-label and compass model fixtures remain pending. This does not supply a no-skill baseline or client/model evaluation.

## Execution availability

2026-10-06: Claude Code 2.1.278 could not authenticate in an isolated safe-mode/no-tools probe: OAuth session expired and refresh failed, including outside the sandbox. Codex 0.160.1 answered an isolated read-only availability probe, but the used-model set and full skill-discovery isolation are not confirmed. Neither probe is a skill prompt baseline or a completed paired evaluation. Required P1–P3 baseline/with-skill records remain NOT RUN; no model fitness is claimed.
