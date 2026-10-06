---
name: svg-rendering
description: Creates and checks SVG mockups of LVGL HMI displays and gauges. Use when converting embedded layouts into previews or diagnosing geometry, text, gradients and layering.
---

# SVG HMI mockups

## Acceptance checks

For an upper gauge, minimum/midpoint/maximum are left/up/right (SVG angles 180/270/360 degrees). A crop painted before a needle hides only earlier graphics: draw the later needle from crop boundary outward, or paint a center-to-edge needle before the crop. Keep text above overlapping graphics. Generated mockups are previews, not proof of hardware behavior.

- [ ] XML parses with resolved placeholders and unique IDs.
- [ ] Needle and ticks at minimum/midpoint/maximum stay in the upper half.
- [ ] Crop/needle order follows one of the two routes above; text stays clear.
- [ ] Gradients and paths share local coordinates; translated copies render consistently.
- [ ] Centered text is visibly aligned using renderer-supported baseline or tested font-metric offset.
- [ ] Long labels, bounds and clipping inspected at actual target dimensions.
- [ ] Failed checks return to geometry/layout and are re-rendered; unavailable checks reported.

## Workflow

1. Resolve target dimensions, input ranges, fonts and project style. Choose upper, bidirectional or compass geometry.
2. Read geometry and the relevant template; adapt palette/layout while preserving coordinates, XML and paint relationships.
3. Parse XML using Python stdlib `xml.etree.ElementTree.parse(<resolved-file>)`; repair failures and return to step 2.
4. Render at target dimensions, inspect edge values, multiple translations and long labels. If any check fails, return to step 2 and repeat. Stop and report a repeated blocker with no new evidence.
5. Report artifact, renderer/version, checks and limitations; do not claim unexecuted render or model tests.

## Requirements

Use a browser that renders SVG. Python's stdlib `xml.etree.ElementTree` checks XML. If browser rendering is unavailable, optional CairoSVG (`python -m pip install cairosvg`) produces PNG; record renderer/version and view it. See [CairoSVG provisioning](https://cairosvg.org/documentation/) for platform-specific Cairo dependencies. Supply the project font or document fallback.

## Input/output example

Input: 300×200 card, center (150,120), radius 65, range 0–100, value 50. Expected geometry: group `translate(150,120)`, upper arc (-65,0)→(65,0), middle tick (0,-65), segmented needle (0,-42)→(0,-70), value text clear of needle. This example defines expected output; it is not an executed render.

## Resources

- [SVG geometry](references/svg-geometry.md) — coordinates, shapes, text, gradients and gauge math.
- [Pitfalls](references/pitfalls.md) — diagnose XML and rendering errors.
- [Templates](references/templates.md) — adaptable upper, bidirectional and compass layouts.
- [Example style](references/example-style.md) — optional palette and geometry defaults.
- [Behavioral evaluations](references/evaluations.md) — paired fixture tests and pending results.
- [ESPHome LVGL](../esphome-lvgl/SKILL.md) — implementation counterpart.
- [Optional enforcement](../ha-validate/reference/enforcement.md) — cross-client hook candidates and explicit fallback checks.
