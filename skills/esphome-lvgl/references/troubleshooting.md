# Troubleshooting

## Contents

- [Troubleshooting](#troubleshooting)
- [Widget Not Visible](#widget-not-visible)
- [Text Not Showing](#text-not-showing)
- [Meter Needle Not Moving](#meter-needle-not-moving)
- [Image Recolor Not Working](#image-recolor-not-working)
- [HA Actions Silently Failing](#ha-actions-silently-failing)
- [Touch Not Responding](#touch-not-responding)
- [A Child Widget Swallows Taps Meant for Its Container](#a-child-widget-swallows-taps-meant-for-its-container)
- [Read the Generated Code Instead of Guessing](#read-the-generated-code-instead-of-guessing)
- [Compilation Errors in Lambdas](#compilation-errors-in-lambdas)
- [ESPHome YAML Syntax Gotchas](#esphome-yaml-syntax-gotchas)

## Troubleshooting

### Widget Not Visible
- Check `hidden: false` or remove hidden flag
- Verify parent container has sufficient size
- Check `bg_opa` -- might be transparent
- Verify grid_cell position is within grid bounds
- Check if widget is on the active page

### Text Not Showing
- Ensure label has `text:` property set (even empty string for dynamic)
- Check `text_color` is not same as `bg_color`
- Verify font exists and is appropriate size
- For lambda text: must return `std::string`, not `const char*` directly

### Meter Needle Not Moving
- Verify `lvgl.indicator.update` uses the correct indicator ID
- Check `range_from`/`range_to` matches the data range
- Lambda must return a numeric value within range

### Image Recolor Not Working
- Check the canonical image widget recolor contract in the widgets reference (directly linked from SKILL.md): explicit opacity and compatible image type.

### HA Actions Silently Failing
- `homeassistant.action:` calls may fail silently -- no error in ESPHome logs, no effect in HA
- **Cause:** Each ESPHome device must be explicitly authorized to perform HA actions
- **Fix:** In Home Assistant: Settings → Devices & Services → ESPHome → select the device → Configure → enable "Allow the device to perform Home Assistant actions"
- This must be set for **each new ESPHome device** -- it is not enabled by default

### Touch Not Responding
- Verify touchscreen component is configured and listed in `lvgl: touchscreens:`
- Check I2C bus configuration (SDA/SCL pins)
- For touch zones: verify coordinate ranges match display dimensions
- `scrollbar_mode: "off"` on containers to prevent scroll capture

### A Child Widget Swallows Taps Meant for Its Container

**Symptom:** `on_click` on a container fires only when you tap certain *parts* of it -- typically a
thin margin around the edge and the icon/label above the graphic -- while taps on the main visual
body (a gauge dial, its value/unit text, an image) do nothing.

**Cause:** LVGL's base constructor makes **every** widget clickable:

```c
/* lv_obj.c -- lv_obj_constructor() */
obj->flags = LV_OBJ_FLAG_CLICKABLE;
```

Subclasses may clear it again, and they are inconsistent about it: `lv_label` clears it (labels
never block), but **`lv_scale` does not** (its constructor only clears `LV_OBJ_FLAG_SCROLLABLE`).
Hit-testing walks children front-to-back and the first *clickable* one under the point wins, so any
such child sitting on top of your container consumes the tap and the container's `on_click` never
runs.

This bites hardest with `meter:`, which ESPHome builds as a container holding an internal
`lv_scale` sized `100% x 100%` -- it blankets the whole dial. Marking the `meter:` and any crop
`arc:` as `clickable: false` is **not enough**: that inner scale has no `id`, so no YAML key can
reach it. Clear the flag on the whole subtree at runtime instead:

```yaml
esphome:
  on_boot:
    - priority: -100          # after every component's setup() -- widgets exist by now
      then:
        - script.execute: make_gauges_fully_clickable

script:
  - id: make_gauges_fully_clickable
    then:
      - lambda: |-
          lv_obj_t* roots[3] = { id(pv_gauge), id(ev_gauge), id(boiler_gauge) };
          lv_obj_t* stack[128];
          int sp = 0;
          for (int r = 0; r < 3; r++) stack[sp++] = roots[r];
          while (sp > 0) {
            lv_obj_t* o = stack[--sp];
            uint32_t n = lv_obj_get_child_count(o);
            for (uint32_t i = 0; i < n; i++) {
              lv_obj_t* c = lv_obj_get_child(o, i);
              lv_obj_remove_flag(c, LV_OBJ_FLAG_CLICKABLE);
              if (sp < 128) stack[sp++] = c;
            }
          }
```

Clearing `CLICKABLE` affects only hit-testing, never drawing. `LV_OBJ_FLAG_EVENT_BUBBLE` on the
child is the alternative when the child legitimately needs its own events too.

**Diagnosing which child is to blame:** the *shape* of the dead zone identifies it -- match the
working margin against the child's geometry (e.g. a 188px container with a 166px scale centered in
it leaves exactly the ~11px side strips that still work). Confirm it in the generated C++ rather
than guessing; see "Read the generated code" below.

**Do not confuse this with a parent-bounds problem.** A child drawn outside its parent's box is
genuinely unreachable (hit-testing gates recursion on the parent's own area), but
`overflow_visible: true` only expands that area by `ext_draw_size`, which is 0 without a
shadow/outline -- so it is not a fix for ordinary overflow.

### Read the Generated Code Instead of Guessing

ESPHome YAML is a code generator, and LVGL behaviour is decided by flags and geometry you never
wrote by hand. When a widget misbehaves, both are on disk after a compile:

- **Generated C++:** `.esphome/build/<device>/src/main.cpp` -- shows every widget actually created,
  in z-order, with each `lv_obj_add_flag`/`remove_flag`, style and size call, plus `#line`
  references back to your YAML. This is where you see the children ESPHome created implicitly and
  whether a YAML key (`clickable: false`, …) really reached the object you meant.
- **The exact LVGL source in use:** `.esphome/build/<device>/managed_components/lvgl__lvgl/` --
  version-correct constructors and hit-test logic, so widget defaults are a `grep`, not a memory.
  Check `lv_version.h` first; ESPHome ≤2026.3 vendors LVGL v8, 2026.4+ v9.x, and defaults differ.

Both are build artifacts -- read-only, regenerated on each compile, never edited by hand.

### Compilation Errors in Lambdas
- `return x.c_str()` -- for text_sensor to label text
- `return std::string("text")` -- for string literals
- `static_cast<int>(x)` -- for float to int conversion
- `!lambda return x;` -- single line needs `return`
- `!lambda |- \n  code` -- multiline block scalar
- **Not every `id()` is an `lv_obj_t*`.** Most widget ids resolve to the raw object, but some are
  ESPHome wrapper classes -- `line:` gives `LvLineType*`, meter line indicators give
  `IndicatorLine*`. Passing those to a C API fails with
  `cannot convert 'esphome::lvgl::LvLineType* const' to 'lv_obj_t*'`. Use the YAML action instead
  (`lvgl.widget.show:` / `lvgl.widget.hide:` work on any widget, wrapper or not), or the wrapper's
  own method (`id(my_needle).set_value(v)`). Check the type in the generated `main.cpp` when unsure.

### ESPHome YAML Syntax Gotchas
- **init_sequence delay**: `- delay 120ms` (plain string), NOT `- delay: 120ms` (colon makes it a dict key)
- **Image format**: Use type sub-keys (`binary:`, `rgb565:`) NOT flat `type:` field:
  ```yaml
  # CORRECT:
  image:
    binary:
      - file: mdi:icon-name
        id: my_icon

  # WRONG:
  image:
    - file: mdi:icon-name
      type: binary
      id: my_icon
  ```
- **Multiple `on_boot:` entries**: Allowed with different priorities in the same config. Use
  `priority: -100` for anything that has to touch LVGL widgets at startup -- it runs after every
  component's `setup()`, so the widget tree is guaranteed to exist.
- **`!lambda` cannot live inside YAML flow mappings**: `- { x: 0, y: !lambda return v; }` dies with
  `expected ',' or '}'` because the tag swallows the rest of the line. Expand to block style:
  ```yaml
  # CORRECT:
  - x: 0
    y: !lambda return v;

  # WRONG:
  - { x: 0, y: !lambda return v; }
  ```
  Flow style is fine for fully static entries -- this only bites where a lambda is involved.
- **Rotation:** Choose one supported route. Modern `lvgl.rotation`/`lvgl.display.set_rotation` rotates display and touch together; do not also set `display.rotation` or touch transforms except independently required hardware-axis correction. Legacy display-level rotation needs matching touch transforms. Verify coordinate alignment on the target.
