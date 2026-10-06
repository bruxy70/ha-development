---
name: esphome-lvgl
description: Writes and reviews ESPHome LVGL display configurations, hardware bindings, and Home Assistant interactions. Use for embedded HMI implementation, migration, or display/input troubleshooting.
---

# ESPHome HMI display development

Identify the target ESPHome version and vendored LVGL version before selecting APIs. Handle missing, unknown and unavailable HA state explicitly. Generated build artifacts are read-only. Config and compile must pass for the current source before an explicitly authorized flash; confirm touch coordinates and HA feedback after deployment. Loading this skill authorizes no live action.

## Workflow

1. Confirm target version, board/pins, project inputs and authorized scope; resolve hardware or deployment ambiguity before implementation.
2. Read the relevant directly linked reference and current official docs; choose modern or legacy rotation consistently.
3. Implement the smallest scoped change. Examples are adaptable fragments, not complete configurations: preserve required schema/API, nesting, semantic guards and lifecycle constraints; replace entities, pins, timing, colors and ranges with project values.
4. Run config validation then compile using [the validation gate](../esphome-validate/SKILL.md). If either fails, return to step 2/3 with the literal diagnostic; repair and repeat. Stop and report when a repeated error yields no new evidence.
5. Deploy only within confirmed target/action authorization. Check boot, rendering, touch/encoder input and HA confirmation; on failure return to diagnosis before further changes.
6. Report changed files and executed checks separately from unavailable live/model checks.

## Checklist

- [ ] Target version and hardware scope confirmed.
- [ ] Missing-state and HA feedback behavior specified.
- [ ] Config and compile passed on current source; otherwise return to implementation.
- [ ] Authorized runtime checks passed, or explicitly unavailable; otherwise return to diagnosis.
- [ ] Evidence and remaining limitations reported.

## Requirements

Requires Python and ESPHome CLI (`python -m pip install esphome`, or `uv tool install esphome` if uv is already provisioned), or dashboard Validate/Compile access. LVGL is vendored by ESPHome. Configure the target HA ESPHome integration; enable per-device actions only when needed. Fonts/images are supplied project inputs; `fonts/materialdesignicons-webfont.ttf` is an example, not bundled. Preserve project version pins.

## Reference routing

- [framework](references/framework.md) — read for this area of implementation or diagnosis.
- [hardware fonts](references/hardware-fonts.md) — read for this area of implementation or diagnosis.
- [lambdas](references/lambdas.md) — read for this area of implementation or diagnosis.
- [ha integration](references/ha-integration.md) — read for this area of implementation or diagnosis.
- [lvgl core](references/lvgl-core.md) — read for this area of implementation or diagnosis.
- [design layout](references/design-layout.md) — read for this area of implementation or diagnosis.
- [widgets](references/widgets.md) — read for this area of implementation or diagnosis.
- [actions navigation](references/actions-navigation.md) — read for this area of implementation or diagnosis.
- [patterns](references/patterns.md) — read for this area of implementation or diagnosis.
- [troubleshooting](references/troubleshooting.md) — read for this area of implementation or diagnosis.
- [Behavioral evaluations](references/evaluations.md) — paired tests and pending evidence.
- [HA connection setup](../ha-mcp-setup/SKILL.md) — configure supported access.
- [HA troubleshooting](../ha-troubleshooting/SKILL.md) — diagnose runtime failures.
- [SVG mockups](../svg-rendering/SKILL.md) — visual geometry previews.
- [Optional cross-client enforcement](../ha-validate/reference/enforcement.md) — suggested hooks and explicit fallback checks; no hooks enabled by this skill.

## Reference Documentation

**ESPHome:**
- ESPHome docs: https://esphome.io/
- ESPHome components: https://esphome.io/components/

**LVGL Component:**
- ESPHome LVGL component: https://esphome.io/components/lvgl/
- ESPHome LVGL widgets: https://esphome.io/components/lvgl/widgets/
- ESPHome LVGL layouts: https://esphome.io/components/lvgl/layouts/
- ESPHome LVGL animations: https://esphome.io/components/lvgl/animation/
- ESPHome LVGL cookbook: https://esphome.io/cookbook/lvgl/
- LVGL upstream docs: https://docs.lvgl.io/master/

**Doc currency:** this skill is synced to **ESPHome 2026.9**. When working against a newer
release, check the changelog for `[lvgl]` lines before trusting the syntax here.

## Implementation Checklist

When implementing a page or feature, verify:

- [ ] All widget IDs are unique across the entire config
- [ ] All referenced IDs (sensors, images, styles) exist
- [ ] Grid positions match the grid definition (0-based, within bounds)
- [ ] Style definitions are defined before they're referenced
- [ ] Images are defined in the `image:` section before LVGL uses them
- [ ] Fonts used are either built-in or defined in `font:` section
- [ ] `image_recolor_opa: 100%` is set wherever `image_recolor` is used
- [ ] `on_release` (not `on_value`) is used for sliders/arcs calling HA services
- [ ] Lambda return types match expectations (std::string for text, float for values)
- [ ] Sensors have appropriate `on_value` handlers to update their LVGL widgets
- [ ] Switches (`platform: lvgl`) reference valid widget IDs

## Best Practices

1. **Use `on_release` instead of `on_value`** for sliders/arcs controlling hardware -- avoids continuous service calls during drag.
2. **Use `adv_hittest: true`** on arcs to prevent accidental touches through the center.
3. **Buttonmatrix saves memory** -- ~8 bytes per button vs ~200 for individual buttons.
4. **Image recolor:** follow the image widget contract in the directly linked widgets reference, including explicit opacity and compatible image type.
5. **Use style_definitions** for consistent styling across widgets -- reduces YAML duplication.
6. **Grid layout** is preferred for dashboard-style layouts with fixed widget positions.
7. **Flex layout** is preferred for responsive layouts that adapt to content.
8. **Use `top_layer`** for persistent navigation buttons and status indicators.
9. **Home Assistant actions** require explicit enablement per device in HA settings.
10. **Use `scrollbar_mode: "off"` AND `scrollable: false`** on fixed dashboard container objects; preserve intentionally scrollable lists and rollers. `scrollbar_mode` only hides the visual scrollbar; without `scrollable: false`, content still scrolls on touch drag.
11. **For floats in formatted text**, use `args: ['x']` or `args: ['x/1000']` -- these are C++ expressions.
12. **Lambda text returns** must return `std::string` -- use `return x.c_str();` for text_sensor values or `return std::string("text");` for string literals.
13. **Use `if_nan`** in text format to handle NaN/Inf sensor values gracefully.
14. **Multiple LVGL instances** are supported for multi-display setups.
15. **Binary image format** is recommended for MDI icons: `image: { binary: [{ file: "mdi:icon-name", id: icon_id, resize: 32x32 }] }`
16. **A tappable container must be tappable everywhere it looks tappable.** Widgets ESPHome creates
    implicitly (notably `meter:`'s inner `lv_scale`) are clickable by default and will eat taps on
    the part users actually aim at. See Troubleshooting → "A child widget swallows taps".
17. **When a widget misbehaves, read the generated `main.cpp` and the vendored LVGL source** before
    theorising -- both sit under `.esphome/build/<device>/` after any compile and settle questions
    about flags, z-order, geometry and version defaults outright.
18. **Anything fetched from HA can be missing.** Guard every `response[...]`/sensor read with a
    default or NaN check, reset shared widgets when a fetch fails (or a stale reading stays on
    screen under a new title), and make interpolated/carried-forward data visibly distinct from
    measured data.
