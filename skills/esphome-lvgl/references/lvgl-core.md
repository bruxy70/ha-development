# Lvgl Core

## Contents

- [LVGL Core Rules](#lvgl-core-rules)
- [ESPHome 2026.4 / LVGL v9.4 migration](#esphome-20264--lvgl-v94-migration)
- [ESPHome 2026.5-2026.9 LVGL additions](#esphome-20265-20269-lvgl-additions)
- [LVGL Component Configuration](#lvgl-component-configuration)
- [Color Formats](#color-formats)
- [Gradients](#gradients)
- [Opacity Formats](#opacity-formats)
- [Alignment Values](#alignment-values)

## LVGL Core Rules

1. **LVGL version depends on the ESPHome release.** ESPHome **≤ 2026.3** uses LVGL **v8**;
   ESPHome **2026.4+** moved the `meter` widget onto LVGL **v9.4**'s `lv_scale`; **2026.9**
   ships LVGL **9.5** (radial/conical gradients). Most YAML is unchanged across the bumps, but a
   few properties are deprecated and one C API was removed — see "ESPHome 2026.4 / LVGL v9.4
   migration" and "ESPHome 2026.5-2026.9 LVGL additions" below. Match APIs to your target
   ESPHome version.
2. **Color depth is RGB565 only** (16-bit, 2 bytes per pixel).
3. **Display must be configured with:**
   - `auto_clear_enabled: false`
   - `update_interval: never` (except OLED/e-paper)
   - No lambda functions on the display component
4. **PSRAM is recommended** for displays larger than ~240x320.
5. **Buffer size guidance:**
   - Without PSRAM: `buffer_size: 25%`
   - With PSRAM prioritizing speed: `buffer_size: 12%` (internal RAM)
   - Default: 100% (fallback to 12% if allocation fails)
   - **WARNING:** On large RGB displays (e.g. 800x480 via rpi_dpi_rgb), `buffer_size: 100%` = 768KB, which causes OOM, kills WiFi/API, and makes the display blink. Omit `buffer_size` (default ~10%) or set an explicit small value.

---

## ESPHome 2026.4 / LVGL v9.4 migration

ESPHome 2026.4 re-backed the `meter` widget on LVGL 9.4's `lv_scale`. When upgrading older
configs, **compile first** — deprecations only warn; one C API removal hard-fails.

**YAML deprecations (auto-remapped, warnings only):**

| Old | New |
|-----|-----|
| `r_mod: N` (meter line indicator) | `length: -abs(N)` |
| `r_mod: N` (meter **arc** indicator) | `padding: N` |
| `disp_bg_color: 0xRRGGBB` (under `lvgl:`) | `bottom_layer: { bg_color: 0xRRGGBB, bg_opa: COVER }` |
| `display: { platform: ili9xxx, ... }` | `display: { platform: mipi_spi, ... }` (sub-options carry over; `model: GC9A01A` still valid) |

**Hard breakage (compile error):** the C API `lv_meter_set_indicator_value(meter, indicator, value)`
was **removed**. Line indicators are now an `IndicatorLine` C++ class with `set_value(int)`:

```cpp
// OLD (fails to compile on 2026.4+):
lv_meter_set_indicator_value(id(my_meter), id(my_needle), value);
// NEW:
id(my_needle).set_value(value);
```

`id(needle_id)` resolves to the `IndicatorLine` instance. Apply renames one at a time and
re-compile between each. (`r_mod` is still accepted as a deprecated alias — prefer `length:` on
a line indicator and `padding:` on an arc indicator for new work.)

---

## ESPHome 2026.5-2026.9 LVGL additions

Nothing here is a breaking change; all of it is new surface the older syntax in this skill
predates. Listed oldest first so you can tell what your target release actually has.

| Release | Addition | Where |
|---------|----------|-------|
| 2026.6 | `rounded` on meter **arc** indicators | "meter" widget below |
| 2026.7 | `animations:` section + `lvgl.animation.start` / `.stop` | "Animations" below |
| 2026.7 | `paused:` / `resume_on_input:` component options | "LVGL Component Configuration" |
| 2026.7 | `lvgl.display.set_rotation` + `on_landscape` / `on_portrait` | "LVGL Component Actions/Triggers" |
| 2026.7 | `mapping:` + `value:` as a text/image source | "Mapping lookups" below |
| 2026.8 | `lvgl.theme.update` action | "LVGL Component Actions" |
| 2026.8 | `lvgl.widget.set_z_index` action | "Widget Actions (Universal)" |
| 2026.9 | `table` and `list` widgets, `container` widget | "Widget Types" |
| 2026.9 | radial + conical gradients (LVGL 9.5) | "Gradients" below |

**Still absent as of 2026.9:** there is no `chart:` widget. See "Trend Chart" in the patterns
section for the bar/line workarounds.

---

## LVGL Component Configuration

```yaml
lvgl:
  color_depth: 16
  bg_color: 0                    # Black background
  border_width: 0
  outline_width: 0
  shadow_width: 0
  text_font: montserrat_14       # Default font
  align: center
  displays:
    - display_id
  touchscreens:
    - touchscreen_id
  page_wrap: true                # Wrap from last to first page
  rotation: 90                   # 0|90|180|270 -- rotates display AND touch together.
                                 # Do NOT also set rotation on display: or transform
                                 # the touchscreen. HW-accelerated via PPA on ESP32-P4.
  paused: false                  # 2026.7+: boot paused; nothing drawn until lvgl.resume
  resume_on_input: true          # 2026.7+: touch/button release or encoder resumes (default)
  theme: {...}                   # Per-widget-type default styles + dark_mode
  gradients: [...]               # 2026.9: see "Gradients"
  animations: [...]              # 2026.7: see "Animations"
  style_definitions: [...]
  pages: [...]
  top_layer:                     # Always-visible overlay
    widgets: [...]
```

**`theme:`** applies default styles to every widget of a type, and `dark_mode: true` enables
LVGL's built-in dark theme. Both coexist — enable dark mode and still override per type:

```yaml
lvgl:
  theme:
    dark_mode: true
    button:
      border_width: 2
```

---

## Color Formats
- Hexadecimal: `0xFF0000` (red), `0x00FF00` (green), `0x0000FF` (blue)
- CSS color names: `springgreen`, `white`, `black`, etc.
- ESPHome color IDs
- In lambdas: `lv_color_hex(0xRRGGBB)`

## Gradients

Declared under the top-level `gradients:` key, then applied to a widget with the `bg_grad`
style option (`bg_grad: my_gradient_id`). Each entry needs `direction` and at least two `stops`:

- **direction** (required): `hor` (`horizontal`), `ver` (`vertical`), `linear`, `radial`, `conical`
- **stops** (required, >= 2): each with `color`, optional `opa` (defaults `COVER`), and `position`
  — a float `0.0`-`1.0`, a percentage, or an integer `0`-`255`
- `linear` / `radial` / `conical` each require a same-named sub-block (below)

`hor`/`ver` are shorthand spanning the whole width/height. The other three take explicit
coordinates — pixels or a percentage of the widget's size, and may be negative or >100% to put a
point outside the widget — plus an `extend` option for pixels falling outside the stop range:
`PAD` (default, nearest stop's color spreads out), `REPEAT` (tiles), `REFLECT` (mirrored tiles).

```yaml
lvgl:
  gradients:
    # Simple: spans the widget horizontally
    - id: hue_bar
      direction: hor
      stops:
        - color: 0xFF0000
          position: 0
        - color: 0x0000FF
          position: 255

    # linear: arbitrary line, not confined to the widget bounds
    - id: diagonal
      direction: linear
      linear:
        from_x: 0%
        from_y: 0%
        to_x: 100%
        to_y: 100%
        extend: PAD
      stops: [...]

    # radial (2026.9): center -> to sets the radius; optional off-center focal point
    - id: spotlight
      direction: radial
      radial:
        center_x: 50%
        center_y: 50%
        to_x: 100%
        to_y: 50%
        focal_x: 40%        # optional, must be paired with focal_y
        focal_y: 40%
        focal_radius: 10    # default 0
        extend: PAD
      stops: [...]

    # conical (2026.9): sweeps around a center like clock hands
    - id: sweep
      direction: conical
      conical:
        center_x: 50%
        center_y: 50%
        start_angle: 0      # default 0
        end_angle: 360      # default 360
        extend: PAD
      stops: [...]
```

For `conical`, `extend` only matters when `start_angle`/`end_angle` are less than a full circle
apart. A `radial` gradient varies only color along its radius, so "white center fading to full
color at the edge" needs a second white-to-transparent radial gradient layered in its own widget
on top; set `radius: circle` on both (equal width/height) to clip the squares to a circle.

## Opacity Formats
- Strings: `TRANSP` (transparent) or `COVER` (opaque)
- Float: `0.0` to `1.0`
- Percentage: `0%` to `100%`
- In lambdas: Integer `0` to `255`

## Alignment Values
`TOP_LEFT`, `TOP_MID`, `TOP_RIGHT`, `LEFT_MID`, `CENTER`, `RIGHT_MID`, `BOTTOM_LEFT`, `BOTTOM_MID`, `BOTTOM_RIGHT`

For `align_to` (relative to sibling): prefix with `OUT_` e.g. `OUT_TOP_MID`, `OUT_BOTTOM_LEFT`

Rotation reference: https://esphome.io/components/lvgl/#display-rotation (checked 2026-10-06). Match the actual target release before using newer actions.
