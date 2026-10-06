# Widgets

## Contents

- [Widget Types](#widget-types)
- [obj (Base Object / Container)](#obj-base-object--container)
- [container](#container)
- [label](#label)
- [button](#button)
- [buttonmatrix](#buttonmatrix)
- [switch](#switch)
- [checkbox](#checkbox)
- [slider](#slider)
- [arc](#arc)
- [bar](#bar)
- [meter](#meter)
- [image (img)](#image-img)
- [animimg (Animated Image)](#animimg-animated-image)
- [line](#line)
- [spinner](#spinner)
- [led](#led)
- [dropdown](#dropdown)
- [roller](#roller)
- [textarea](#textarea)
- [keyboard](#keyboard)
- [spinbox](#spinbox)
- [tabview](#tabview)
- [tileview](#tileview)
- [canvas](#canvas)
- [qrcode](#qrcode)
- [msgbox (Message Box)](#msgbox-message-box)
- [table (2026.9+)](#table-20269)
- [list (2026.9+)](#list-20269)
- [Mapping lookups (2026.7+)](#mapping-lookups-20267)

## Widget Types

### obj (Base Object / Container)
Generic container that catches touches. Used for grouping and layout.
```yaml
- obj:
    id: my_container
    width: 800
    height: 480
    bg_color: 0x000000
    border_width: 0
    scrollbar_mode: "off"
    layout:
      type: grid
      grid_rows: [FR(1), FR(1)]
      grid_columns: [FR(1), FR(1)]
    widgets:
      - label: ...
      - button: ...
```

### container
Functionally identical to `obj` but with **no styles applied**, so it is invisible until you style
it or fill it. Defaults to `width: 100%` / `height: 100%`. Prefer it over `obj` for pure layout
scaffolding — it saves having to zero out `bg_opa`/`border_width` on every wrapper.
```yaml
- container:
    align: CENTER
    width: 80%
    height: 80%
    outline_width: 1        # set temporarily to see where it is
    widgets:
      - ...
```

### label
Text display widget.
```yaml
- label:
    id: my_label
    text: "Hello World"
    text_font: MONTSERRAT_24
    text_color: 0xFFFFFF
    align: center
    long_mode: WRAP|DOT|SCROLL|SCROLL_CIRCULAR|CLIP
    recolor: true                # Enables #RRGGBB inline color codes
```

**Text property formats:**
```yaml
# Static text
text: "Hello"

# Printf-style formatting
text:
  format: "%.1f°C"
  args: ['x']
  if_nan: "N/A"

# Time format
text:
  time_format: "%H:%M"
  time: sntp_id

# Lambda
text: !lambda return id(my_sensor).state;
text: !lambda return x.c_str();
```

**Actions:** `lvgl.label.update` -- update id, text, and any style properties.
**Triggers:** `on_value` (text changed, `x` = new text string)
**Integration:** text_sensor (read-only), text (read-write)

### button
Simple push or toggle button.
```yaml
- button:
    id: my_button
    text: "Click Me"       # Creates internal label (cannot combine with widgets:)
    checkable: true        # Makes it a toggle button
    width: 100
    height: 40
    # OR use child widgets instead of text:
    widgets:
      - label:
          text: "Custom"
```

**Actions:** `lvgl.button.update` -- update id, text, styles
**Triggers:** `on_press`, `on_click`, `on_short_click`, `on_long_press`, `on_release`, `on_value` (for checkable: x = checked state), `on_change` (user interaction only)
**Integration:** binary_sensor (pressed state), switch (checked state for checkable buttons)

**Trigger selection guide:**
- **`on_click`**: Fires on release -- **USE THIS** for most cases (matches official ESPHome LVGL cookbook)
- **`on_press`**: Fires immediately on touch-down -- good for debugging
- **`on_short_click`**: Can be **suppressed by scroll detection** -- unreliable if parent is scrollable
- **`on_change`**: Only fires when `checked` state changes -- **useless on non-checkable buttons**

### buttonmatrix
Memory-efficient multiple buttons (~8 bytes vs ~200 per button).
```yaml
- buttonmatrix:
    id: my_btnmatrix
    width: 200
    height: 300
    rows:
      - buttons:
        - id: btn_1
          text: "Option A"
          width: 2              # Relative width (1-15, default 1)
          control:
            checkable: true
            checked: false
            disabled: false
            hidden: false
            no_repeat: false
            popover: false
            recolor: false
          on_press:
            then:
              - logger.log: "Button A pressed"
      - buttons:
        - id: btn_2
          text: "Option B"
    one_checked: true           # Radio button behavior
```

**Actions:** `lvgl.buttonmatrix.update`, `lvgl.matrix.button.update`
**Triggers:** per-button `on_value` (x = checked state), `on_press`, `on_click`, matrix-level triggers (x = pressed button index)

### switch
Toggle switch widget.
```yaml
- switch:
    id: my_switch
    indicator:               # Foreground when checked
      bg_color: 0x00FF00
    knob:                    # Draggable handle
      bg_color: 0xFFFFFF
```

**Triggers:** `on_value` (any change, x = checked state), `on_change` (user only)
**Integration:** switch component

### checkbox
Toggle with tick box and label.
```yaml
- checkbox:
    id: my_checkbox
    text: "Enable feature"
    indicator:               # The tick box
      bg_color: 0x333333
```

**Actions:** `lvgl.checkbox.update` (text, styles)
**Triggers:** `on_value`, `on_change` (x = boolean checked state)
**Integration:** switch component

### slider
Value selector with draggable knob.
```yaml
- slider:
    id: my_slider
    value: 50
    min_value: 0
    max_value: 100
    width: 200
    animated: true
    mode: NORMAL|RANGE|SYMMETRICAL
    indicator:
      bg_color: 0x0000FF
    knob:
      bg_color: 0xFFFFFF
```

**Actions:** `lvgl.slider.update` (value, min/max, styles)
**Triggers:** `on_value` (continuous during drag), `on_change` (user only), `on_release` (preferred for hardware control to avoid continuous calls)
**Integration:** number, sensor

### arc
Circular value display/input with optional knob.
```yaml
- arc:
    id: my_arc
    value: 75
    min_value: 0
    max_value: 100
    start_angle: 135          # 0=3 o'clock, clockwise
    end_angle: 45
    rotation: 0               # Offset for 0-degree position
    adjustable: true           # Enable knob dragging
    mode: NORMAL|REVERSE|SYMMETRICAL
    change_rate: 720           # Degrees/second for knob
    arc_width: 10
    arc_color: 0x0000FF
    arc_rounded: true
    indicator:                 # Value arc
      arc_width: 10
      arc_color: 0x00FF00
    knob:
      bg_color: 0xFFFFFF
```

Note: Zero degrees is at 3 o'clock, increasing clockwise. Use `adv_hittest: true` to allow clicking through the middle.

**Actions:** `lvgl.arc.update` (value, angles, ranges, mode, styles)
**Triggers:** `on_value` (continuous), `on_change` (user only)
**Integration:** number, sensor

### bar
Progress bar widget. Vertical when width < height.
```yaml
- bar:
    id: my_bar
    value: 75
    min_value: 0
    max_value: 100
    animated: true
    mode: NORMAL|RANGE|SYMMETRICAL
    start_value: 0            # For RANGE mode
    indicator:
      bg_color: 0x00FF00
```

**Actions:** `lvgl.bar.update` (value, min/max, mode, start_value, styles)
**Integration:** number (read-write), sensor (read-only)

### meter
Gauge with scales, needles, tick marks, and arc indicators.
```yaml
- meter:
    id: my_meter
    height: 160
    width: 160
    scales:
      angle_range: 180         # Total arc angle (0-360)
      rotation: 0              # Rotation offset
      range_from: 0
      range_to: 100
      ticks:
        count: 11              # Number of tick marks
        width: 2               # Tick width in pixels
        length: 10             # Tick length in pixels
        color: 0xFFFFFF
        major:                 # Major ticks (nested inside ticks:, NOT a sibling)
          stride: 5            # Every Nth tick is major
          width: 3
          length: 15
          color: 0xFFFFFF
          label_gap: 10        # Gap between tick and label
      indicators:
        - line:                # Needle indicator
            id: needle_id
            value: 0
            width: 4
            color: 0xFFFFFF
            length: 80%        # % or px; default 100% of scale radius (was `r_mod`)
            radial_offset: 0   # Offset of the needle from the scale centre
            rounded: true      # Rounded needle end points
        - arc:                 # Arc segment indicator
            color: 0xFF0000
            padding: 10        # Offset from scale radius, may be negative (was `r_mod`)
            width: 20
            rounded: false     # 2026.6+: round the arc's start/end
            start_value: 0
            end_value: 50
        - arc:
            color: 0x00FF00
            padding: 10
            width: 20
            start_value: 50
            end_value: 100
        - tick_style:          # Color range on ticks
            start_value: 0
            end_value: 100
            color_start: 0x0000FF
            color_end: 0xFF0000
```

**Actions:** `lvgl.indicator.update` (id, value), `lvgl.meter.update`

**Key names:** `padding` (arc) and `length` (line) replaced `r_mod` in 2026.4. `r_mod` still
compiles as a deprecated alias but warns; see the migration table above for the mapping.

### image (img)

**Recolor contract:** set explicit `image_recolor_opa` (for full recolor, `100%`; default is transparent) and use an image type compatible with recoloring, such as binary icons. Preserve these guards when adapting examples.
Displays images defined in the ESPHome image component.
```yaml
# Image definition (outside lvgl:)
image:
  binary:
    - file: mdi:sun-wireless-outline
      id: solar_icon
      resize: 32x32

# In LVGL widgets:
- image:
    src: solar_icon
    id: my_image
    align: top_left
    image_recolor: 0xF0E000
    image_recolor_opa: 100%    # Must set for recolor to work (defaults to 0%)
    angle: 0                   # 0-360 rotation
    zoom: 1.0                  # Scale factor
    antialias: false
    mode: REAL|VIRTUAL         # VIRTUAL: overflow bounds without layout impact
```

**Actions:** `lvgl.image.update` / `lvgl.img.update` (src, image_recolor, image_recolor_opa, angle, zoom, etc.)

### animimg (Animated Image)
Cycles through multiple images.
```yaml
- animimg:
    id: my_anim
    src: [frame1, frame2, frame3]
    duration: 1000ms
    repeat_count: forever      # Or integer
    auto_start: true
```

**Actions:** `lvgl.animimg.start`, `lvgl.animimg.stop`, `lvgl.animimg.update`

### line
Draws lines between points.
```yaml
- line:
    points:
      - 5, 5
      - 70, 70
      - 120, 10
    line_width: 4
    line_color: 0x0000FF
    line_rounded: true
    line_dash_width: 0         # 0 = solid line
    line_dash_gap: 0
```

**Actions:** `lvgl.line.update` (points, styles)

### spinner
Rotating loading indicator.
```yaml
- spinner:
    spin_time: 2s
    arc_length: 60deg
    arc_color: 0x00FF00
    arc_width: 8
    indicator:
      arc_color: 0xd4d4d4
```

### led
Status indicator with adjustable brightness.
```yaml
- led:
    id: my_led
    color: 0xFF0000
    brightness: 70%            # 0% = black, 100% = full
```

**Integration:** light component

### dropdown
Single selection from expandable list.
```yaml
- dropdown:
    id: my_dropdown
    options:
      - "Option 1"
      - "Option 2"
      - "Option 3"
    selected_index: 0
    dir: BOTTOM|TOP|LEFT|RIGHT
    dropdown_list:
      selected:
        checked:
          text_color: 0xFF0000
```

**Actions:** `lvgl.dropdown.update` (selected_index, options, dir, styles)
**Triggers:** `on_value` (x = selected index), `on_change` (user only)
**Integration:** select component

### roller
Scrollable selection list.
```yaml
- roller:
    id: my_roller
    options:
      - "Item 1"
      - "Item 2"
      - "Item 3"
    selected_index: 0
    mode: NORMAL|INFINITE
    visible_row_count: 3
```

**Actions:** `lvgl.roller.update` (selected_index, animated, styles)
**Triggers:** `on_value` (x = index), `on_change` (user only)
**Integration:** select component

### textarea
Multi-line text input.
```yaml
- textarea:
    id: my_textarea
    text: ""
    placeholder_text: "Enter text..."
    one_line: true
    password_mode: false
    max_length: 100
    accepted_chars: "0123456789"
```

**Actions:** `lvgl.textarea.update` (text, max_length, placeholder_text, styles)
**Triggers:** `on_value` (every keystroke, `text` = contents), `on_ready` (Enter key in one_line mode)
**Integration:** text, text_sensor

### keyboard
Virtual on-screen keyboard linked to textarea.
```yaml
- keyboard:
    id: my_keyboard
    textarea: my_textarea
    mode: TEXT_LOWER|TEXT_UPPER|TEXT_SPECIAL|NUMBER
```

**Actions:** `lvgl.keyboard.update` (mode, textarea)
**Triggers:** `on_ready` (checkmark pressed), `on_cancel` (keyboard icon pressed)

### spinbox
Numeric input with increment/decrement.
```yaml
- spinbox:
    id: my_spinbox
    value: 25
    range_from: -10
    range_to: 40
    digits: 3
    decimal_places: 1
    rollover: false
```

**Actions:** `lvgl.spinbox.update` (value), `lvgl.spinbox.increment`, `lvgl.spinbox.decrement`
**Triggers:** `on_value` (x = value), `on_change` (user only)
**Integration:** number, sensor

### tabview
Tab-organized content.
```yaml
- tabview:
    id: my_tabview
    position: TOP|BOTTOM|LEFT|RIGHT
    size: 10%                  # Tab button size
    tab_style:
      items:
        text_color: 0xFFFFFF
    tabs:
      - name: "Tab 1"
        id: tab_1
        widgets: [...]
      - name: "Tab 2"
        id: tab_2
        widgets: [...]
```

**Actions:** `lvgl.tabview.select` (id, index, animated)
**Triggers:** `on_value` (x = tab index, `tab` = tab ID), `on_change`

### tileview
Swipeable grid of tiles.
```yaml
- tileview:
    id: my_tileview
    tiles:
      - id: tile_1
        row: 0
        column: 0
        dir: HOR|VER|ALL|LEFT|RIGHT|TOP|BOTTOM
        widgets: [...]
      - id: tile_2
        row: 0
        column: 1
        dir: LEFT
        widgets: [...]
```

**Actions:** `lvgl.tileview.select` (id, tile_id or row/column, animated)
**Triggers:** `on_value` (`tile` = tile ID)

### canvas
Drawing surface for custom graphics.
```yaml
- canvas:
    id: my_canvas
    width: 200
    height: 200
    transparent: false
```

**Actions:** `lvgl.canvas.fill`, `lvgl.canvas.set_pixels`, `lvgl.canvas.draw_rectangle`, `lvgl.canvas.draw_polygon`

### qrcode
QR code display.
```yaml
- qrcode:
    text: "https://esphome.io"
    size: 150
    dark_color: 0x000000
    light_color: 0xFFFFFF
```

### msgbox (Message Box)
Modal dialog. Defined at top-level `lvgl:` component.
```yaml
lvgl:
  msgboxes:
    - id: my_msgbox
      title: "Alert"
      close_button: true
      body:
        text: "Something happened."
        bg_color: 0x808080
      buttons:
        - id: msgbox_ok
          text: "OK"
          on_click:
            then:
              - lvgl.widget.hide: my_msgbox
```

Hidden by default. Show with `lvgl.widget.show: my_msgbox`.

### table (2026.9+)
Rows and columns of **text** cells. Cells hold text only — no images, no per-cell colors (the
`items` part styles every cell uniformly), so it is not a substitute for a flex/grid layout of
labels when you need icons or per-column styling.
```yaml
- table:
    id: readings_table
    width: 100%
    row_count: 3             # defaults to len(rows), or 0
    column_count: 2          # defaults to the widest row, or 0
    columns:                 # per column, in order
      - width: 40%           # % is of the table's content width, recalculated on resize
      - width: 60%
    rows:
      - ["Name", "Value"]    # bare list of cells...
      - cells:               # ...or a dict per cell
          - text: "Temperature"
          - text: "22.5"
            merge_right: false   # draw merged with the cell to its right
            text_crop: false     # crop instead of wrapping when it doesn't fit
    selected_row: 0          # giving only one of row/column selects the whole row/column
    selected_column: 0
    on_value:                # selected cell changed (by touch OR by lvgl.table.update)
      - logger.log:
          format: "Selected cell: %u, %u"
          args: [ row, column ]
```
**Actions:**
- `lvgl.table.update` — any of the options above
- `lvgl.table.cell.update` — `id`, `row`, `column` (both zero-based) plus at least one of
  `text`, `merge_right`, `text_crop`. This is the one to use for live data:
  ```yaml
  - lvgl.table.cell.update:
      id: readings_table
      row: 0
      column: 1
      text: !lambda return to_string(id(my_sensor).state);
  ```
Declare a pre-sized empty table (`row_count`/`column_count`, no `rows:`) when every cell is
filled at runtime.

### list (2026.9+)
A plain scrollable container **populated at runtime by action**, not by a fixed `widgets:` list.
Use it for content unknown until the device runs (scan results, a variable-length set of open
doors); for a fixed set of rows a flex `obj`/`container` is simpler.
```yaml
- list:
    id: my_list
    width: 200
    height: 150
    pad_row: 4               # vertical spacing between entries
    on_add:                  # fires per entry added; index in `list_index`
      - logger.log:
          format: "Entry added at %d"
          args: [ list_index ]
    on_remove:               # fires per entry removed; clear fires it last-index-down-to-0
      - logger.log:
          format: "Entry removed at %d"
          args: [ list_index ]
```
**Actions** (all take `id`; `add_text`/`add` take an optional templatable `index`, default = end):
- `lvgl.list.add_text` — a plain text entry, typically a section header. Needs `text`.
- `lvgl.list.add` — an entry built from any other widget type, with its children and triggers.
  Exactly one widget key alongside `id`, configured as it would be under `widgets:`.
- `lvgl.list.remove` — `index` (required), removes that entry and its children
- `lvgl.list.clear` — removes every entry

Entries added via `lvgl.list.add` are built fresh on each run and freed automatically on
`remove`/`clear`. There is no YAML loop, so building N entries from a sensor means a `repeat:`
with an index lambda — often more code than one multi-line label.

A trigger on an added widget does **not** receive its row index (the widget config is shared with
every other use of that type). Get it in a lambda from the `event` variable:
```cpp
int row = lvgl::lv_list_get_row_index(id(my_list),
            static_cast<lv_obj_t *>(lv_event_get_target(event)));
// returns -1 if the widget isn't inside the list
```

### Mapping lookups (2026.7+)
A label's text or an image's `src` can be looked up from a `mapping:` component instead of
being built with a lambda — useful for enum-to-string / enum-to-icon translation:
```yaml
- label:
    mapping: string_map      # a mapping component whose `to` type is `string`
    value: !lambda return id(my_state).state;   # the lookup key, matching the `from` type
- image:
    src:
      mapping: icon_map      # mapping whose `to` type is `image`
      value: !lambda return id(my_state).state;
```
