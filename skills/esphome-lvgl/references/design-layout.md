# Design Layout

## Contents

- [Design Guidelines](#design-guidelines)
- [Color Guidelines](#color-guidelines)
- [Typography Guidelines](#typography-guidelines)
- [Layout Principles](#layout-principles)
- [Meter/Gauge Design Principles](#metergauge-design-principles)
- [Interactive Element Guidelines](#interactive-element-guidelines)
- [Style Definitions](#style-definitions)
- [Complete Style Properties](#complete-style-properties)
- [Layout Systems](#layout-systems)
- [Flex Layout](#flex-layout)
- [Grid Layout](#grid-layout)

## Design Guidelines

### Color Guidelines
- **Background:** Pure black (`0x000000`) saves power on OLED and maximizes contrast on LCD
- **Primary text:** White (`0xFFFFFF`) or light gray (`0xC0C0C0`)
- **Secondary text:** Medium gray (`0x808080`)
- **Status colors (consistent meanings):**
  - Green (`0x00FF00` / `0x00F000`): Active, charging, exporting, healthy, ON
  - Red (`0xFF3000` / `0xFF0000`): Alert, discharging, importing, critical, OFF
  - Yellow/Amber (`0xF0E000` / `0xFFC300`): Warning, solar, caution
  - Blue (`0x0000FF` / `0x3498DB`): Info, cold, water
  - Gray (`0x707070`): Inactive, standby, disabled
- **Never use color alone** to convey meaning -- pair with text labels or icons

### Typography Guidelines
- **Primary values:** `MONTSERRAT_24` or larger -- the number the user glances at
- **Secondary info:** `MONTSERRAT_16` -- units, labels, status text
- **Small details:** `MONTSERRAT_10` or `MONTSERRAT_12` -- timestamps, fine print
- **Monospace (`unscii_8`/`unscii_16`):** Only for technical/debug data
- **Rule of thumb:** If you squint and can't read it at arm's length, the font is too small

### Layout Principles
- **Grid layout** for dashboards with fixed-size widget tiles
- **Group related data** -- a meter + its label + its icon should be in one `obj` container
- **Consistent widget sizes** within a page -- use `style_definitions` for uniformity
- **Padding:** Minimum 2px between elements; 4-8px between widget groups
- **Page design:** Each page should have a clear purpose (energy, weather, controls)
- **Navigation:** Keep it obvious -- touch zones, swipe areas, or persistent nav buttons in `top_layer`

### Meter/Gauge Design Principles
- **Semicircle gauges (180deg)** are the most readable for dashboard tiles
- **Use the crop pattern:** meter + black arc overlay to clean up the center, then center cap (small circle) to cover needle hub
- **tick_style gradient** (preferred over arc indicators): dense ticks with `local: true` gradient fill look dramatically more professional than flat-color arcs. Use `major:` ticks for scale reference marks
- **Needle visibility**: the needle must extend past the tick edge, or a crop arc makes it nearly invisible. On 2026.4+ size the needle with `length:` (a `%` or px of the scale radius) and nudge arcs with `padding:`; the old `r_mod` alias needed a POSITIVE value (e.g. +5) for the same effect
- **Min/max labels**: position BELOW the diameter line (`y = meter_y_offset + gap`). Compute positions from meter geometry, don't guess pixel offsets
- **Contrast**: all text on `0x1E1E1E` card background must be at least `0x909090` (~4.5:1). Lower contrast text is unreadable at arm's length on small displays
- **Scrolling**: fixed dashboard `obj` containers use BOTH `scrollbar_mode: "off"` AND `scrollable: false`. Preserve scrolling on lists, rollers and intentionally scrollable containers; the scrollbar property alone only hides the visual
- **Needle + numeric label** together -- needle for trend, label for precision
- **Icon above gauge** identifies what the gauge measures; gray when idle, accent color when active

### Interactive Element Guidelines
- **Buttons:** Minimum 48x48px for reliable touch; use `buttonmatrix` for groups
- **Sliders:** Use `on_release` (not `on_value`) for actions that call services
- **Visual feedback:** Ensure pressed/checked states are visually distinct
- **Confirmation for destructive actions:** Use a two-step process or hold-to-confirm

---

## Style Definitions

Reusable style blocks that can be applied to any widget via `styles: style_id`.

```yaml
style_definitions:
  - id: my_style
    bg_color: 0x000000
    bg_opa: COVER
    text_font: MONTSERRAT_16
    text_color: 0xFFFFFF
    border_width: 0
    outline_width: 0
    shadow_width: 0
    radius: 4
    pad_all: 2
    align: center
    # State-based overrides:
    pressed:
      bg_color: 0x333333
    checked:
      bg_color: 0x00FF00
```

### Complete Style Properties

**Background:** `bg_color`, `bg_opa`, `bg_grad` (gradient ID -- see "Gradients" for `linear`/`radial`/`conical`), `bg_grad_color`, `bg_grad_dir` (NONE|HOR|VER -- two-color shorthand only), `bg_main_stop`, `bg_grad_stop`, `bg_dither_mode` (NONE|ORDERED|ERR_DIFF), `bg_image_src`, `bg_image_opa`, `bg_image_recolor`, `bg_image_recolor_opa`

**Border:** `border_width`, `border_color`, `border_opa`, `border_post` (bool), `border_side` (TOP|BOTTOM|LEFT|RIGHT|INTERNAL|NONE)

**Outline:** `outline_width`, `outline_color`, `outline_opa`, `outline_pad`

**Shadow:** `shadow_color`, `shadow_opa`, `shadow_ofs_x`, `shadow_ofs_y`, `shadow_spread`, `shadow_width`

**Padding:** `pad_all`, `pad_top`, `pad_bottom`, `pad_left`, `pad_right`, `pad_row`, `pad_column`

**Size:** `width`, `height`, `min_width`, `max_width`, `min_height`, `max_height` (pixels, percentage, or `SIZE_CONTENT`)

**Position:** `x`, `y` (int16 or percentage)

**Corners:** `radius` (0=square, 65535=pill), `clip_corner` (bool)

**Text:** `text_color`, `text_opa`, `text_font`, `text_align` (LEFT|CENTER|RIGHT), `text_decor` (NONE|UNDERLINE|STRIKETHROUGH), `line_space`, `letter_space`

**Transform:** `transform_angle` (0-360), `transform_zoom` (0.1-10), `transform_pivot_x`, `transform_pivot_y`, `translate_x`, `translate_y`

**Image:** `image_recolor`, `image_recolor_opa`

**Arc (for arc/spinner):** `arc_color`, `arc_opa`, `arc_width`, `arc_rounded`

**Line (for line widget):** `line_color`, `line_opa`, `line_width`, `line_rounded`, `line_dash_width`, `line_dash_gap`

**General:** `opa` (overall opacity, inherited)

---

## Layout Systems

### Flex Layout
```yaml
layout:
  type: flex
  flex_flow: ROW|COLUMN|ROW_WRAP|COLUMN_WRAP|ROW_REVERSE|COLUMN_REVERSE
  flex_align_main: START|END|CENTER|SPACE_EVENLY|SPACE_AROUND|SPACE_BETWEEN
  flex_align_cross: START|END|CENTER|STRETCH
  flex_align_track: START|END|CENTER|SPACE_EVENLY|SPACE_AROUND|SPACE_BETWEEN
  pad_row: 4
  pad_column: 4
```

Child widget property: `flex_grow: 1` (growth factor, 0=disabled)

### Grid Layout
```yaml
layout:
  type: grid
  grid_rows: [FR(1), FR(1), FR(1)]      # Fractional, pixel, or CONTENT
  grid_columns: [200, FR(1), FR(2)]
  grid_row_align: START|END|CENTER|SPACE_EVENLY|SPACE_AROUND|SPACE_BETWEEN
  grid_column_align: START|END|CENTER|SPACE_EVENLY|SPACE_AROUND|SPACE_BETWEEN
  pad_row: 0
  pad_column: 0
```

Per-widget grid placement:
```yaml
grid_cell_row_pos: 0          # 0-based row index
grid_cell_column_pos: 0       # 0-based column index
grid_cell_row_span: 1         # Rows to span
grid_cell_column_span: 1      # Columns to span
grid_cell_x_align: STRETCH    # START|END|CENTER|STRETCH
grid_cell_y_align: STRETCH    # START|END|CENTER|STRETCH
```

Shorthand: `layout: 2x3` equals grid with 2 equal rows, 3 equal columns.
