# Actions Navigation

## Contents

- [Pages and Navigation](#pages-and-navigation)
- [Widget Actions (Universal)](#widget-actions-universal)
- [Widget Triggers (Universal)](#widget-triggers-universal)
- [LVGL Component Actions](#lvgl-component-actions)
- [LVGL Component Triggers](#lvgl-component-triggers)
- [LVGL Conditions](#lvgl-conditions)
- [Idle Screen Management](#idle-screen-management)
- [Animations (2026.7+)](#animations-20267)

## Pages and Navigation

```yaml
pages:
  - id: page_home
    skip: false               # Include in page navigation
    layout: ...
    widgets: [...]
  - id: page_settings
    widgets: [...]

top_layer:                    # Always-visible overlay on all pages
  widgets:
    - buttonmatrix:
        align: bottom_mid
        rows:
          - buttons:
            - text: "\uF053"
              on_press:
                - lvgl.page.previous
            - text: "\uF015"
              on_press:
                - lvgl.page.show: page_home
            - text: "\uF054"
              on_press:
                - lvgl.page.next
```

**Page actions:**
- `lvgl.page.next` -- go to next page
- `lvgl.page.previous` -- go to previous page
- `lvgl.page.show`:
  - `id`: page ID
  - `animation`: NONE|OVER_LEFT|OVER_RIGHT|OVER_TOP|OVER_BOTTOM|MOVE_LEFT|MOVE_RIGHT|FADE_IN|FADE_OUT (default: NONE)
  - `time`: animation duration (default: 50ms)

**Condition:** `lvgl.page.is_showing: page_id`

---

## Widget Actions (Universal)

These actions work on ALL widget types:

- **`lvgl.widget.show`**: `id: widget_id` -- make visible
- **`lvgl.widget.hide`**: `id: widget_id` -- make hidden (excluded from layout)
- **`lvgl.widget.enable`**: `id: widget_id` -- enable widget
- **`lvgl.widget.disable`**: `id: widget_id` -- disable widget
- **`lvgl.widget.update`**: Update any state, flag, or style property on any widget
  ```yaml
  - lvgl.widget.update:
      id: widget_id
      bg_color: 0xFF0000
      hidden: false
      state:
        checked: true
  ```
- **`lvgl.widget.redraw`**: Force redraw of widget(s) or full screen
- **`lvgl.widget.refresh`**: Re-evaluate lambda-based properties
- **`lvgl.widget.focus`**: Set keyboard/encoder focus
- **`lvgl.widget.set_z_index`** (2026.8+): Change stacking order among **siblings** only; touches
  no other property. `position:` is `top`, `bottom`, `up`, `down`, or an integer sibling index
  (`0` = back-most, positive counts from the back, negative from the front so `-1` == `top`).
  ```yaml
  - lvgl.widget.set_z_index:
      id: popup_box
      position: top
  - lvgl.widget.set_z_index:
      id: [icon_1, icon_2]
      position: down
  ```
  Useful for raising a modal above siblings without a dedicated `top_layer`.

---

## Widget Triggers (Universal)

Available on ALL widget types:

- `on_press` -- widget pressed
- `on_release` -- widget released (always fires)
- `on_click` -- pressed then released without scrolling
- `on_short_click` -- pressed briefly then released (no scroll, no long press)
- `on_long_press` -- pressed for `long_press_time`
- `on_long_press_repeat` -- repeated after long press
- `on_scroll_begin`, `on_scroll_end`, `on_scroll`
- `on_focus`, `on_defocus`
- `on_gesture`, `on_swipe_left`, `on_swipe_right`, `on_swipe_up`, `on_swipe_down`
- `on_all_events` -- fires on any event (debugging)

---

## LVGL Component Actions

Act on the LVGL instance rather than one widget. All take an optional `lvgl_id:`, needed only
when more than one LVGL instance is configured.

- `lvgl.pause` / `lvgl.resume` — stop/restart drawing. `lvgl.pause` takes
  `show_snow: true` to scatter random pixels as burn-in relief while paused.
- `lvgl.update` — re-evaluate the component's own lambda-based properties
- `lvgl.style.update` — update a `style_definitions:` entry at runtime
- `lvgl.theme.update` (2026.8+) — restyle **every** widget of a type at once, e.g. to swap an
  accent color without touching each widget. Takes a dict shaped like `theme:` — keyed by widget
  type, optionally nested by part and state. A type never declared under `theme:` is created on
  first reference (so it has no visual effect until the action first fires), and every affected
  widget is refreshed automatically — no follow-up redraw needed.
  ```yaml
  - lvgl.theme.update:
      button:
        border_width: 4
        pressed:
          border_color: 0xFF0000
  ```
- `lvgl.display.set_rotation` (2026.7+) — `0`, `90`, `180` or `270`, templatable. The angle is
  **absolute**, not relative, so the current rotation doesn't affect the result.
  ```yaml
  - lvgl.display.set_rotation: 90
  - lvgl.display.set_rotation: !lambda "return id(my_rotation_number).state;"
  ```
- `lvgl.page.next` / `lvgl.page.previous` / `lvgl.page.show`
- `lvgl.animation.start` / `lvgl.animation.stop` — see "Animations"

## LVGL Component Triggers

- `on_idle`: Display inactive for `timeout` duration
  ```yaml
  on_idle:
    timeout: 120s
    then:
      - light.turn_off: back_light
  ```
- `on_pause`, `on_resume`, `on_boot`
- `on_draw_start`, `on_draw_end` (useful for e-paper)
- `on_landscape` / `on_portrait` (2026.7+): fire when the effective width/height ratio changes —
  `on_landscape` when it becomes wider than tall (a square display counts as landscape),
  `on_portrait` when taller than wide. The matching one **also fires once at boot** to establish
  the initial orientation; later changes normally come from `lvgl.display.set_rotation`.

## LVGL Conditions

- `lvgl.is_idle: timeout`
- `lvgl.is_paused`
- `lvgl.page.is_showing: page_id`

---

## Idle Screen Management

```yaml
lvgl:
  on_idle:
    timeout: 120s
    then:
      - light.turn_off: back_light
  on_idle:
    timeout: 240s
    then:
      - lvgl.pause
  resume_on_input: true
  on_resume:
    then:
      - light.turn_on: back_light
```

---

## Animations (2026.7+)

An animation interpolates one or more **style properties** on one or more widgets from `from` to
`to` across `duration`. Declared under the top-level `animations:` key and referenced by `id`.

```yaml
lvgl:
  animations:
    - id: slide
      duration: 1s             # default 5s
      start_delay: 0s          # delay before the first value change
      auto_start: true         # start at boot; default false
      loop: true               # restart on completion; default false
      timing: ease_in_out      # default: linear
      widgets:
        - id: box
          x:
            from: 0
            to: 200
          y:
            from: 0
            to: 100
      on_start: [...]          # runs each start, after start_delay
      on_stop: [...]           # runs on completion, restart, or lvgl.animation.stop
```

Every listed property and widget animates together over the same `duration` and `timing`.

**Animatable properties** — position/size (`x`, `y`, `translate_x/y`, `translate_radial`,
`min/max_width`, `min/max_height`, `length`), transforms (`transform_width/height/rotation/
skew_x/skew_y/pivot_x/pivot_y`), colors (`bg_color`, `bg_grad_color`, `border_color`,
`outline_color`, `line_color`, `text_color`, `arc_color`, `shadow_color`, `drop_shadow_color`,
`image_recolor`, `bg_image_recolor`, `recolor`, …), opacities (`opa`, `opa_layered`, `bg_opa`,
`arc_opa`, `image_opa`, `text_opa`, `shadow_opa`, `color_filter_opa`, …), and border/line/shadow/
text metrics (`border_width`, `line_width`, `shadow_width/spread/offset_x/offset_y`,
`blur_radius`, `text_letter_space`, `text_line_space`, …).

> **Colors cannot be animated from a lambda** — a `from`/`to` for a color property must be a
> constant. Numeric properties may use lambdas, evaluated once per start (with no arguments), so
> they can randomise or compute each run's endpoints:
> ```yaml
> x:
>   from: !lambda "return random_uint32() % 200;"
>   to: 200
> ```

**Timing functions** — a single one, or a list applied in order. Parameterless ones are a bare
string; with parameters use a mapping with `type:`:

| Timing | Parameters |
|--------|-----------|
| `round_trip` | `pause` (percentage of total duration spent paused between the halves; default 0) |
| `ease_in_out` | `weight` (0-100%, how strongly; default `100%`) |
| `gravity` | `acceleration` (float, default `0.5`), `bounce` (0-1, speed retained per bounce, default `0.5`) |

```yaml
  animations:
    - id: bounce_in
      duration: 2s
      timing:
        - type: gravity
          bounce: 0.3
          acceleration: 0.8
      widgets:
        - id: box
          y:
            from: 0
            to: 200
```

**Actions** — `lvgl.animation.start` restarts from the beginning if already running, and its
`duration` / `start_delay` / `loop` options override the configured values for this **and
subsequent** runs. `lvgl.animation.stop` leaves properties at their current values and fires
`on_stop`; stopping a non-running animation is a no-op.

```yaml
- lvgl.animation.start: slide          # single ID shorthand
- lvgl.animation.start:
    id: [slide, fade]
    duration: 2s
    loop: false
- lvgl.animation.stop: slide
- lvgl.animation.stop: [slide, fade]
```
