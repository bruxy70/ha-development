# Lambdas

## Contents

- [Lambda Reference](#lambda-reference)
- [Lambda Value Scales (YAML vs C++)](#lambda-value-scales-yaml-vs-c)
- [Lambda Syntax Patterns](#lambda-syntax-patterns)
- [Accessing ESPHome Components](#accessing-esphome-components)
- [Image update action](#image-update-action)
- [LVGL C API in Lambdas](#lvgl-c-api-in-lambdas)
- [ESPTime API](#esptime-api)
- [NeoPixel / Addressable LED Control in Lambdas](#neopixel--addressable-led-control-in-lambdas)
- [Type Conversions](#type-conversions)
- [Common Lambda Patterns](#common-lambda-patterns)
- [Edge Case Handling](#edge-case-handling)

## Lambda Reference

### Lambda Value Scales (YAML vs C++)

Values in lambdas use different scales than YAML:
- **Opacity**: integer 0-255 (not float/percentage)
- **Angle**: 1/10 degrees (0-3600 for 0-360deg)
- **Zoom**: multiply by 256 (256 = 1.0x, 512 = 2.0x)
- **Color**: `lv_color_hex(0xRRGGBB)`
- **Percentage**: `lv_pct(value * 100)`

### Lambda Syntax Patterns

```yaml
# Short lambdas (single expression) -- inline
value: !lambda return x / 1000;

# Medium lambdas (2-4 lines) -- block scalar
text: !lambda |-
  char buf[32];
  snprintf(buf, sizeof(buf), "%.1f kW", x / 1000.0);
  return std::string(buf);

# Long lambdas -- block scalar with clear structure
on_value:
  then:
    - lambda: |-
        // Check for invalid values
        if (isnan(x)) return;

        // Convert and update
        float kw = x / 1000.0;
        // ... more logic
```

### Accessing ESPHome Components

```cpp
// Access sensor value
id(my_sensor).state

// Access text sensor
id(my_text_sensor).state.c_str()

// Access switch state
id(my_switch).state  // bool

// Turn on/off a switch
id(my_switch).turn_on();
id(my_switch).turn_off();

// Access number component
id(my_number).state

// Publish to template sensor
id(my_template_sensor).publish_state(42.0);

// Log output
ESP_LOGD("tag", "Value: %.1f", x);
ESP_LOGW("tag", "Warning: %s", x.c_str());
```

### Image update action

```yaml
- lvgl.image.update:
    id: my_img
    src: new_image
    image_recolor: 0x00FF00
    image_recolor_opa: 100%
```

### LVGL C API in Lambdas

When you need to call LVGL C functions directly (for features not exposed in ESPHome YAML):

```cpp
// id(widget_id) returns lv_obj_t* directly -- no ->get_obj() needed
lv_obj_t *obj = id(my_label);

// Style manipulation; verify direct C APIs against the vendored target headers.
lv_obj_set_style_bg_color(id(my_obj), lv_color_hex(0xFF0000), LV_PART_MAIN);

// Show/hide widgets
lv_obj_add_flag(id(my_widget), LV_OBJ_FLAG_HIDDEN);
lv_obj_clear_flag(id(my_widget), LV_OBJ_FLAG_HIDDEN);

// Arc value
lv_arc_set_value(id(my_arc), 75);
```

### ESPTime API

```cpp
// CORRECT: time.strftime() returns std::string directly
auto time = id(ha_time).now();
std::string time_str = time.strftime("%H:%M");

// WRONG: Do NOT use C strftime() with time.to_c_tm()
// time.to_c_tm() returns struct tm by value (not pointer) -- compilation error
```

### NeoPixel / Addressable LED Control in Lambdas

```cpp
auto call = id(led_strip).make_call();
call.set_rgb(0.0, 1.0, 0.0);           // Green
call.set_effect("pulse_green");          // Named effect from light: component
call.perform();

// Turn off
auto off = id(led_strip).make_call();
off.set_state(false);
off.perform();
```

Define named effects in the `light:` component, reference by name in lambdas.

### Type Conversions

```cpp
// Float to int
static_cast<int>(x)
int(x)

// Int to float
static_cast<float>(x)

// String formatting
char buf[32];
snprintf(buf, sizeof(buf), "%02d:%02d", hours, minutes);
return std::string(buf);

// String comparison (text_sensor on_value)
x == "Charging"    // x is std::string in text_sensor context
x.c_str()          // Convert to C string for return

// NaN check (sensor values)
isnan(x)
std::isnan(id(sensor_id).state)
```

### Common Lambda Patterns

```cpp
// Conditional color (returns lv_color_t)
return x > 80 ? lv_color_hex(0x00FF00) : lv_color_hex(0xFF0000);

// Time formatting from minutes
int hours = static_cast<int>(x) / 60;
int mins = static_cast<int>(x) % 60;

// Clamping values
return std::max(0.0f, std::min(100.0f, x));

// Unit conversion
return x / 1000.0;  // W to kW
return x * 3.6;     // m/s to km/h
```

### Edge Case Handling

```yaml
# NaN check for numeric sensors
text: !lambda |-
  if (isnan(x)) return std::string("--");
  return to_string(static_cast<int>(x)) + "%";

# Empty string check for text sensors
text: !lambda |-
  if (x.empty()) return std::string("N/A");
  return x.c_str();

# Time formatting with bounds
text: !lambda |-
  if (isnan(x) || x < 0) return std::string("");
  int hours = static_cast<int>(x) / 60;
  int mins = static_cast<int>(x) % 60;
  char buf[16];
  snprintf(buf, sizeof(buf), "%02d:%02d", hours, mins);
  return std::string(buf);
```
