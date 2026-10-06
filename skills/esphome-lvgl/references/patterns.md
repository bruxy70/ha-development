# Patterns

## Contents

- [Common LVGL Patterns](#common-lvgl-patterns)
- [Semicircle Gauge (tick_style gradient + Crop Arc + Center Cap)](#semicircle-gauge-tick_style-gradient--crop-arc--center-cap)
- [Wind Compass (360deg Meter)](#wind-compass-360deg-meter)
- [Circular Ring Indicator (Overlaid Arcs)](#circular-ring-indicator-overlaid-arcs)
- [Meter Needle with Dark Mask (Ring-Only Segment)](#meter-needle-with-dark-mask-ring-only-segment)
- [Multi-State UI Pattern (View/Edit Modes)](#multi-state-ui-pattern-viewedit-modes)
- [Multi-Page Touch Navigation](#multi-page-touch-navigation)
- [Trend Chart (there is no chart widget)](#trend-chart-there-is-no-chart-widget)
- [ESPHome Component Integration Table](#esphome-component-integration-table)
- [Platform Switch Integration](#platform-switch-integration)

## Common LVGL Patterns

### Semicircle Gauge (tick_style gradient + Crop Arc + Center Cap)
Professional gauge pattern using tick_style gradient fill, major tick scale marks, thin needle, and center cap.

Widget tree order: `icon → name label → meter → crop arc → center cap → min/max labels → value label → unit label`

```yaml
- obj:
    width: 150
    height: 120
    bg_opa: TRANSP
    border_width: 0
    pad_all: 0
    scrollbar_mode: "off"
    scrollable: false          # BOTH required to prevent touch scrolling
    widgets:
      - image:
          src: my_icon
          align: TOP_MID
          y: 0
          image_recolor: 0xF0E000
          image_recolor_opa: 100%
      - label:
          text: "GAUGE"
          text_font: MONTSERRAT_12
          text_color: 0xF0E000
          bg_opa: TRANSP
          align: TOP_MID
          y: 26
      - meter:
          width: 130             # or 105 for small gauges
          height: 130
          align: center
          y: 40                  # offset from parent center
          bg_opa: TRANSP
          border_width: 0
          text_font: MONTSERRAT_10
          scales:
            angle_range: 180
            range_from: 0
            range_to: 10
            ticks:
              count: 41          # Dense ticks for smooth gradient
              width: 2
              length: 16
              color: 0x1E1E1E    # Invisible base (matches card bg)
              major:
                stride: 4
                width: 2
                length: 20       # Longer = visible scale marks
                color: 0x333333
            indicators:
              - tick_style:
                  color_start: 0x1E1E1E
                  color_end: 0xF0E000
                  start_value: 0
                  end_value: 10
                  local: true    # REQUIRED for proper gradient
              - line:
                  id: my_needle
                  width: 3
                  color: 0xFFFFFF
                  r_mod: 5       # POSITIVE: extends past ticks for visibility
                                 # (deprecated alias; 2026.4+ name is `length:` --
                                 #  these values are field-verified, so re-tune on migration)
                  value: 0
      - arc:                     # Crop arc hides meter center
          width: 84              # or 66 for small
          height: 84
          align: center
          y: 40                  # Must match meter y
          start_angle: 0
          end_angle: 360
          border_width: 0
          arc_color: 0x1E1E1E
          arc_width: 100
          indicator:
            arc_width: 100
            arc_color: 0x1E1E1E
      - obj:                     # Center cap covers needle hub
          width: 10              # or 8 for small
          height: 10
          align: center
          y: 40                  # Must match meter y
          bg_color: 0x333333
          bg_opa: COVER
          border_width: 0
          radius: 5
      - label:                   # Min endpoint
          text: "0"
          text_font: MONTSERRAT_10
          text_color: 0x909090   # Must be legible on card bg
          bg_opa: TRANSP
          align: center
          y: 46                  # = meter_y(40) + 6px gap below diameter
          x: -58                 # = -(radius(65) - ~7)
      - label:                   # Max endpoint
          text: "10"
          text_font: MONTSERRAT_10
          text_color: 0x909090
          bg_opa: TRANSP
          align: center
          y: 46
          x: 58
      - label:                   # Value
          id: my_value_label
          text_font: MONTSERRAT_22
          text_color: 0xFFFFFF
          bg_opa: TRANSP
          align: center
          y: 14
          text: "0.0"
      - label:                   # Unit
          text_font: MONTSERRAT_12
          text_color: 0xB0B0B0
          bg_opa: TRANSP
          align: center
          y: 32
          text: "kW"
```

For bidirectional gauges (e.g. grid power), use two `tick_style` indicators split at zero:
```yaml
indicators:
  - tick_style:                  # Negative half (red → dark)
      color_start: 0xFF3000
      color_end: 0x1E1E1E
      start_value: -10
      end_value: 0
      local: true
  - tick_style:                  # Positive half (dark → green)
      color_start: 0x1E1E1E
      color_end: 0x00E000
      start_value: 0
      end_value: 10
      local: true
```

### Wind Compass (360deg Meter)
```yaml
- meter:
    scales:
      angle_range: 360
      range_from: 360
      range_to: 0
      rotation: 270            # North at top
      ticks:
        count: 13
      indicators:
        - line:
            id: wind_needle
            width: 4
            color: 0xFFFFFF
            value: 0
```
Note: `value: !lambda return 360-x;` to convert degrees to needle position.

### Circular Ring Indicator (Overlaid Arcs)

Two overlaid arcs (background + indicator) are simpler and more memory-efficient than meter widgets for circular ring displays (e.g. battery SoC, power gauges):

```yaml
# Background arc (gray ring)
- arc:
    id: soc_bg_arc
    align: center
    width: 220
    height: 220
    start_angle: 135
    end_angle: 45
    value: 100
    min_value: 0
    max_value: 100
    adjustable: false
    arc_width: 14
    arc_color: 0x333333
    indicator:
      arc_width: 14
      arc_color: 0x404040
# Indicator arc (colored, overlaid on top)
- arc:
    id: soc_arc
    align: center
    width: 220
    height: 220
    start_angle: 135
    end_angle: 45
    value: 0
    min_value: 0
    max_value: 100
    adjustable: false
    arc_width: 14
    arc_color: 0x333333       # Unfilled portion (transparent-ish)
    indicator:
      arc_width: 14
      arc_color: 0x00FF00     # Filled portion (green)
```

### Meter Needle with Dark Mask (Ring-Only Segment)

A meter `line` indicator makes an excellent needle for gauges. To show only the segment near the ring (hiding the line crossing through center text), overlay a dark circle mask:

```yaml
# 1. Background arc
- arc:
    id: bg_arc
    # ... ring configuration

# 2. Meter with needle (stacked on top of arc)
- meter:
    id: needle_meter
    align: center
    width: 220
    height: 220
    bg_opa: TRANSP
    scales:
      angle_range: 270
      rotation: 135
      range_from: 0
      range_to: 100
      indicators:
        - line:
            id: my_needle
            width: 4
            color: 0xFFFFFF
            r_mod: -2          # deprecated alias for `length:` -- see migration table
            value: 0

# 3. Dark circle mask (covers inner portion of needle)
- obj:
    id: needle_mask
    align: center
    width: 172              # Smaller than meter, larger than text area
    height: 172
    radius: 86              # Perfect circle
    bg_color: 0x000000
    bg_opa: COVER
    border_width: 0

# 4. Labels on top of everything
- label:
    id: value_label
    align: center
    text: "50%"
```

Widget stacking order: arc (bg) -> meter (needle) -> mask (center cover) -> labels.

### Multi-State UI Pattern (View/Edit Modes)

For displays with view and edit modes, use `globals:` for state tracking and `script: mode: restart` for edit timeouts:

```yaml
globals:
  - id: edit_state
    type: int
    initial_value: "0"       # 0=VIEW, 1=EDIT_MODE, 2=EDIT_VALUE
  - id: temp_value
    type: int
    initial_value: "50"

script:
  - id: edit_timeout
    mode: restart             # Calling again resets the timer
    then:
      - delay: 10s
      - lambda: |-
          id(edit_state) = 0;
          // Revert to last known HA values, update display
      - script.execute: update_display

  - id: update_display
    then:
      - lambda: |-
          int state = id(edit_state);
          if (state == 0) {
            // Show view mode widgets, hide edit widgets
          } else if (state == 1) {
            // Show edit mode A widgets
          } else if (state == 2) {
            // Show edit mode B widgets
          }
```

Route ALL display updates through a single `update_display` script. Guard incoming HA sensor updates with state checks to prevent flickering during edits.

### Multi-Page Touch Navigation
```yaml
binary_sensor:
  - platform: touchscreen
    id: page_next
    x_min: 400
    x_max: 800
    y_min: 0
    y_max: 480
    on_press:
      - lvgl.page.next
```

### Trend Chart (there is no chart widget)

ESPHome's LVGL component exposes no `chart:` — still true as of 2026.9. (The 2026.9 `table`
widget is text cells only, so it's an alternative for a *tabular* readout, not for plotting.)
Two ways to plot a series, both fixed-point-count:

- **Bar chart** -- a flex row of `bar:` widgets, one per sample, updated via `lv_bar_set_value()`.
  Good for a value that is naturally per-slot (hourly tariff, per-day rainfall) and for showing
  category colour per bar. Reads poorly for a smooth quantity like SoC or power.
- **Line chart** -- a single `line:` widget re-pointed at runtime. Better for continuous values.

For the line variant, keep the scaled Y values in a `globals:` array and rebuild the point list from
it. Points are declared once at their fixed X positions; only Y is a lambda. Convert to pixel space
when filling the array (Y is inverted: 0 = top):

```yaml
globals:
  - id: chart_values           # pre-scaled to pixel-Y inside the chart area
    type: float[24]
    restore_value: false

script:
  - id: render_chart
    then:
      - lvgl.line.update:
          id: chart_line
          points:
            - x: 0
              y: !lambda return (int) id(chart_values)[0];
            - x: 23
              y: !lambda return (int) id(chart_values)[1];
            # ...one entry per sample; note block style -- see YAML gotchas...
```

```cpp
// filling it, for a 150px-tall area and a 0..100 range:
id(chart_values)[i] = 150.0f - (v / 100.0f) * 150.0f;
```

Axes and grid are plain widgets: 1px `obj`s at computed offsets for gridlines, `label`s for the
scale. Keep the grid sparse -- one line per *labelled* reference point, not one per sample -- and
label the axis with real values (clock times, units), not sample indices. A dot at the last point
plus a numeric readout of the current value matters more than density: a modal chart usually covers
the live widget the user tapped.

### ESPHome Component Integration Table

| LVGL Widget | ESPHome Platform | Purpose |
|---|---|---|
| button | binary_sensor | Reports pressed state |
| button (checkable) | switch | Reports checked state |
| switch, checkbox | switch | Toggle control |
| slider, arc, spinbox | number | Numeric input/output |
| slider, arc, spinbox, bar | sensor | Display sensor values |
| dropdown, roller | select | Selection control |
| label, textarea | text_sensor | Display text |
| label, textarea | text | Text input |
| led | light | Status indicator |

### Platform Switch Integration
```yaml
switch:
  - platform: lvgl
    widget: my_lvgl_button     # Reference to LVGL widget with checkable
    id: my_switch_id
```
