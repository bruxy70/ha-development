---
name: esphome-lvgl
description: Complete reference for ESPHome-based HMI displays -- ESPHome framework fundamentals (project config, packages, hardware, HA integration, lambdas) and the LVGL graphics component (widgets, styles, layouts, design guidelines, patterns, troubleshooting).
allowed-tools: WebFetch, Read, Grep
---

# ESPHome HMI Display Reference

Comprehensive reference for writing ESPHome YAML configurations for HMI (Human-Machine Interface) displays. Covers the ESPHome framework fundamentals and the LVGL (Light and Versatile Graphics Library) graphics component for ESP32-based touchscreen displays integrated with Home Assistant.

## Reference Documentation

**ESPHome:**
- ESPHome docs: https://esphome.io/
- ESPHome components: https://esphome.io/components/

**LVGL Component:**
- ESPHome LVGL component: https://esphome.io/components/lvgl/
- ESPHome LVGL widgets: https://esphome.io/components/lvgl/widgets.html
- ESPHome LVGL layouts: https://esphome.io/components/lvgl/layouts.html
- ESPHome LVGL cookbook: https://esphome.io/cookbook/lvgl/
- LVGL v8 docs: https://docs.lvgl.io/master/

---
---

# Part 1: ESPHome Framework

---

## ESPHome Project Configuration

### Substitutions

Device-specific variables that can be overridden per device. Defined at the top of the config and referenced with `${variable_name}`.

```yaml
substitutions:
  device_name: display-kitchen
  friendly_name: Kitchen Display
  ip: 192.168.1.100
  # Hardware-specific
  display_width: "800"
  display_height: "480"
```

### Package System

Packages allow splitting ESPHome configs into reusable fragments via `!include`. Each package merges its contents into the main config.

```yaml
# In main config:
packages:
  wifi: !include common/wifi.yaml
  api: !include common/api.yaml
  base: !include common/base.yaml

# common/wifi.yaml:
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${device_name} Fallback"
```

### YAML Structure Order

A well-organized ESPHome LVGL config follows this order:

```yaml
substitutions:
  # Device identity and secrets

esphome:
  # Name, platform options

esp32:
  # Board, framework, sdkconfig

psram:
  # If applicable

logger:

packages:
  # Common includes (api, ota, wifi)

wifi:
  # Static IP override if needed

i2c:
  # Bus configuration

output:
  # PWM for backlight

light:
  # Backlight control

touchscreen:
  # Touch controller

display:
  # Display driver and pin mapping

image:
  # Icon/image definitions

font:
  # Custom font definitions

lvgl:
  # color_depth, bg_color, defaults
  # style_definitions
  # displays, touchscreens
  # pages (with all widgets)
  # top_layer (persistent UI)

sensor:
  # HA sensor imports with LVGL update handlers

text_sensor:
  # HA text sensor imports with LVGL update handlers

binary_sensor:
  # Touch zones, physical buttons

switch:
  # LVGL platform switches for button state sync

number:
  # LVGL platform number components
```

### YAML Formatting Rules

- 2-space indentation (ESPHome standard)
- Comments for non-obvious choices: pin mappings, magic numbers, workarounds
- Group related config sections with blank lines
- Use `#` comments to label widget groups within pages (e.g., `# Solar gauge`, `# Navigation buttons`)

### Naming Conventions

- **IDs:** lowercase_snake_case: `solar_needle`, `battery_soc_label`, `btn_auto`
- **Substitutions:** lowercase_snake_case: `device_name`, `friendly_name`
- **Prefixes for widget IDs:**
  - `btn_` -- buttons in buttonmatrix
  - `sw_` -- switches (platform: lvgl)
  - `img_` -- images
  - `lbl_` or descriptive name -- labels
  - Sensor-related: match the data they display (`solar_label`, `temperature_needle`)

---

## Hardware Configuration

### ESP32-S3 with PSRAM

```yaml
esphome:
  platformio_options:
    build_flags: "-DBOARD_HAS_PSRAM"
    board_build.esp-idf.memory_type: qio_opi
    board_build.flash_mode: dio

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf
    sdkconfig_options:
      CONFIG_ESP32S3_DEFAULT_CPU_FREQ_240: y
      CONFIG_ESP32S3_DATA_CACHE_64KB: y
      CONFIG_SPIRAM_FETCH_INSTRUCTIONS: y
      CONFIG_SPIRAM_RODATA: y

psram:
  mode: octal
  speed: 80MHz
```

### Display Drivers

| Driver | Type | Common Displays |
|--------|------|-----------------|
| `rpi_dpi_rgb` | Parallel RGB | CrowPanel, Sunton, and other larger displays |
| `ili9xxx` | SPI | ILI9341, ILI9488, ST7789, etc. |
| `ssd1306` | I2C/SPI | Small OLED displays |
| `st7920` | LCD | Character displays |

### Touchscreen Controllers

| Controller | Interface | Common Usage |
|------------|-----------|-------------|
| `gt911` | I2C | Larger RGB displays |
| `cst816` | I2C | Small round displays |
| `xpt2046` | SPI | Resistive touch |
| `ft5x06` | I2C | Capacitive touch |

### Touch Calibration (Portrait / Rotated Displays)

When using `rotation: 90` (or other rotations) on the display, the touchscreen coordinates must be transformed to match. Use `swap_xy` and `mirror_x`/`mirror_y` on the touchscreen component.

```yaml
touchscreen:
  platform: gt911         # or cst816, etc.
  id: my_touch
  swap_xy: true           # Swap X/Y axes to match rotated display
  mirror_y: true          # Mirror Y axis (common for CrowPanel portrait)
```

**WARNING:** Without correct touch transforms, ALL touch events will silently miss their target widgets -- no errors in the log, but no buttons work. Debug with:
```yaml
touchscreen:
  on_touch:
    - lambda: 'ESP_LOGI("touch", "x=%d y=%d", touch.x, touch.y);'
```
Verify that reported coordinates match the positions of your LVGL widgets.

### Circular SPI Display (GC9A01A)

Round 240x240 displays (common on rotary knob boards) use the ILI9XXX platform:

```yaml
display:
  - platform: ili9xxx
    model: GC9A01A
    id: my_display
    cs_pin: GPIOxx
    dc_pin: GPIOxx
    reset_pin: GPIOxx
    invert_colors: true         # Usually required
    update_interval: never
    auto_clear_enabled: false
    dimensions:
      width: 240
      height: 240
```

- Pixels outside the inscribed circle are not visible (hardware clips) -- no LVGL masking needed
- No `rotation` needed for round displays
- Very small resolution: use arcs and labels primarily, avoid complex grids/panels

### Rotary Encoder Input

For rotary encoders connected via GPIO, use `on_clockwise`/`on_anticlockwise` triggers. They fire once per detent, clean and simple.

```yaml
sensor:
  - platform: rotary_encoder
    id: rotary
    pin_a: GPIOxx
    pin_b: GPIOxx
    on_clockwise:
      - lambda: |-
          // Increment value, switch to next item, etc.
    on_anticlockwise:
      - lambda: |-
          // Decrement value, switch to previous item, etc.

binary_sensor:
  - platform: gpio
    id: rotary_button
    pin:
      number: GPIOxx
      mode: INPUT_PULLUP
      inverted: true
    on_click:
      - lambda: |-
          // Confirm selection, toggle mode, etc.
```

**Do NOT** use `on_value` with delta tracking -- it's noisy and requires min/max management. The direction triggers are far simpler.

### Display Configuration Pattern

A typical display setup includes the display driver, I2C bus (for touchscreen), and touchscreen controller. Adjust pins and driver for your specific board.

```yaml
display:
  - platform: <driver>        # rpi_dpi_rgb, ili9xxx, ssd1306, etc.
    id: my_display
    update_interval: never     # Required for LVGL
    auto_clear_enabled: false  # Required for LVGL
    dimensions:
      width: <width>
      height: <height>
    # Driver-specific pin configuration...

i2c:
  sda: <sda_pin>
  scl: <scl_pin>

touchscreen:
  platform: <controller>      # gt911, cst816, xpt2046, ft5x06
  id: my_touch
```

### Backlight Control Pattern

```yaml
output:
  - platform: ledc
    pin: <backlight_pin>       # Board-specific GPIO
    frequency: 1220
    id: gpio_backlight_pwm

light:
  - platform: monochromatic
    output: gpio_backlight_pwm
    name: Display Backlight
    id: back_light
    restore_mode: ALWAYS_ON
```

---

## Fonts

**Built-in Montserrat (Medium weight, basic Latin + degree + bullet + FontAwesome subset):**
`montserrat_8`, `montserrat_10`, `montserrat_12`, `montserrat_14` (default), `montserrat_16`, `montserrat_18`, `montserrat_20`, `montserrat_22`, `montserrat_24`, `montserrat_26`, `montserrat_28`, `montserrat_30`, `montserrat_32`, `montserrat_34`, `montserrat_36`, `montserrat_38`, `montserrat_40`, `montserrat_42`, `montserrat_44`, `montserrat_46`, `montserrat_48`

In YAML these are referenced as uppercase: `MONTSERRAT_14`, `MONTSERRAT_16`, etc.

**Built-in Montserrat Unicode limitations:** The built-in fonts contain only ASCII + degree + bullet + a small FontAwesome subset. Any non-ASCII Unicode symbols will render as rectangles:
- Unicode triangles (U+25C0, U+25B6) -- use plain ASCII `<` `>` instead
- Lightning bolt (U+26A1) -- use text like "CHG" instead
- Diacritics (ě, ř, č, ž, š, ú, etc.) -- need custom font (see below)
- **Rule:** Assume any non-Latin symbol is missing from built-in fonts. Test or use ASCII fallbacks.

**Special fonts:**
- `unscii_8` / `unscii_16` -- Pixel-perfect ASCII monospace
- `simsun_16_cjk` -- CJK Radicals
- `dejavu_16_persian_hebrew` -- Persian/Hebrew

**Custom fonts via ESPHome font component:**
```yaml
font:
  - file: "gfonts://Roboto"
    id: roboto_20
    size: 20
    bpp: 4            # Use bpp: 4 for LVGL anti-aliasing
    extras:
      - file: "fonts/materialdesignicons-webfont.ttf"
        glyphs: ["\U000F02D1"]
```

**Extended Latin (diacritics) font pattern:**
For languages with diacritics (Czech, Polish, French, etc.), use a custom font with `GF_Latin_Core` glyphset:
```yaml
font:
  - file: "gfonts://Montserrat@500"    # @500 = Medium weight (matches built-in)
    id: montserrat_ext_16
    size: 16
    bpp: 4                              # Required for LVGL anti-aliasing
    glyphsets:
      - GF_Latin_Core                   # Covers most European diacritics
    # For specific missing chars (e.g. ď, ť, ň), add:
    # glyphs: "ďťň"
```
Each custom font size adds ~42-80KB to flash. Fine on 16MB ESP32-S3.

---

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

### LVGL C API in Lambdas

When you need to call LVGL C functions directly (for features not exposed in ESPHome YAML):

```cpp
// id(widget_id) returns lv_obj_t* directly -- no ->get_obj() needed
lv_obj_t *obj = id(my_label);

// Runtime image switching (ESPHome can't change src via LVGL actions)
lv_img_set_src(id(my_img), id(new_image));

// Style manipulation
lv_obj_set_style_bg_color(id(my_obj), lv_color_hex(0xFF0000), LV_PART_MAIN);
lv_obj_set_style_img_recolor(id(my_img), lv_color_hex(0x00FF00), LV_PART_MAIN);
// NOTE: LVGL 8.x uses "img" not "image": lv_obj_set_style_img_recolor, NOT image_recolor

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

---

## Home Assistant Integration

### Bidirectional State Synchronization (3-Step Pattern)

The canonical pattern for bidirectional HA <-> display sync:

```yaml
# Step 1: HA -> Display: Import state and update widget
sensor:
  - platform: homeassistant
    id: ha_temperature
    entity_id: sensor.temperature
    on_value:
      then:
        - lvgl.label.update:
            id: temp_label
            text:
              format: "%.1f°C"
              args: ['x']

# Step 2: Display -> HA: Widget interaction calls HA service
# (defined in LVGL widget)
- slider:
    id: temp_slider
    on_release:
      - homeassistant.action:
          action: climate.set_temperature
          data:
            entity_id: climate.thermostat
            temperature: !lambda return x;

# Step 3: Feedback loop: HA confirms -> display updates
# (handled by step 1 -- HA sensor updates after service call)
```

### Importing Sensor Data

```yaml
sensor:
  - platform: homeassistant
    id: temperature
    entity_id: sensor.outdoor_temperature
    on_value:
      then:
        - lvgl.label.update:
            id: temp_label
            text:
              format: "%.1f°C"
              args: ['x']
        - lvgl.indicator.update:
            id: temp_needle
            value: !lambda return x;
```

### Importing Text Sensor Data

```yaml
text_sensor:
  - platform: homeassistant
    id: status_text
    entity_id: sensor.system_status
    on_value:
      then:
        - lvgl.label.update:
            id: status_label
            text: !lambda return x.c_str();
```

### Conditional Logic Based on State

```yaml
text_sensor:
  - platform: homeassistant
    id: battery_mode
    entity_id: sensor.battery_mode
    on_value:
      then:
        - lvgl.label.update:
            id: battery_status
            text: !lambda return x.c_str();
        - if:
            condition:
              lambda: return x == "Charge";
            then:
              - lvgl.image.update:
                  id: img_battery
                  image_recolor: 0x00FF00
        - if:
            condition:
              lambda: return x == "Discharge";
            then:
              - lvgl.image.update:
                  id: img_battery
                  image_recolor: 0xFF3000
```

### Switch Controlling Home Assistant

```yaml
switch:
  - platform: lvgl
    widget: my_lvgl_switch
    id: sw_feature
```

### Button Calling Home Assistant Action

```yaml
- buttonmatrix:
    rows:
      - buttons:
        - id: btn_action
          text: "Turn On"
          on_press:
            then:
              - homeassistant.action:
                  action: input_select.select_option
                  data:
                    entity_id: input_select.mode
                    option: "Auto"
```

### Slider with Home Assistant Sync

```yaml
- slider:
    id: brightness_slider
    min_value: 0
    max_value: 255
    on_release:                # Use on_release, NOT on_value, to avoid continuous calls
      - homeassistant.action:
          action: light.turn_on
          data:
            entity_id: light.living_room
            brightness: !lambda return static_cast<int>(x);
```

### Radio Button Pattern (Mutually Exclusive Modes)

```yaml
# HA side: input_select with options
# Display side: buttonmatrix with on_press -> input_select.select_option
# Sync: text_sensor watches input_select, turns on/off switches

text_sensor:
  - platform: homeassistant
    id: mode_select
    entity_id: input_select.operating_mode
    on_value:
      then:
        - lambda: |-
            (x == "Auto") ? id(sw_auto).turn_on() : id(sw_auto).turn_off();
            (x == "Fast") ? id(sw_fast).turn_on() : id(sw_fast).turn_off();
            (x == "Off") ? id(sw_off).turn_on() : id(sw_off).turn_off();

switch:
  - platform: lvgl
    widget: btn_auto
    id: sw_auto
  - platform: lvgl
    widget: btn_fast
    id: sw_fast
  - platform: lvgl
    widget: btn_off
    id: sw_off
```

### Time-Remaining Formatting

```yaml
sensor:
  - platform: homeassistant
    id: time_left_sensor
    entity_id: sensor.charging_time_left
    on_value:
      then:
        - lvgl.label.update:
            id: time_left_label
            text: !lambda |-
              if (isnan(x)) return std::string("");
              int hours = static_cast<int>(x) / 60;
              int minutes = static_cast<int>(x) % 60;
              char buf[16];
              snprintf(buf, sizeof(buf), "%02d:%02d", hours, minutes);
              return buf;
```

### Boot-Time State Initialization

HA sensors push state via the API, but LVGL widgets may not be ready, or the initial state push arrives before the display is configured. Widgets show defaults until the first state *change*.

Solution: refresh all widgets from sensor states after API connects:
```yaml
esphome:
  on_boot:
    - priority: -10           # Run after everything else is initialized
      then:
        - wait_until:
            api.connected:
        - delay: 2s           # Give HA time to push initial states
        - script.execute: refresh_all_widgets

script:
  - id: refresh_all_widgets
    then:
      - lambda: |-
          // Read current sensor states and update all LVGL widgets
          // This ensures display matches HA on boot
```

### Time Source from Home Assistant

```yaml
time:
  - platform: homeassistant
    id: ha_time
    timezone: Europe/Prague     # Or your timezone
```

- Use `platform: homeassistant` instead of SNTP if the device can't reach NTP servers directly
- **LVGL auto-format `time:` labels** don't reliably refresh after delayed HA time sync. Use a regular label + interval instead:
```yaml
interval:
  - interval: 10s
    then:
      - lvgl.label.update:
          id: time_label
          text: !lambda |-
            return id(ha_time).now().strftime("%H:%M");
```

### Edit Mode Bidirectional Sync (Guard Pattern)

When the user is editing a value on the display, incoming HA sensor updates for that field must be ignored to prevent flickering:

```yaml
globals:
  - id: edit_state
    type: int
    initial_value: "0"         # 0=VIEW, 1=EDIT_FIELD_A, 2=EDIT_FIELD_B

sensor:
  - platform: homeassistant
    id: ha_value
    entity_id: sensor.my_value
    on_value:
      then:
        - lambda: |-
            // Only update display if NOT currently editing this field
            if (id(edit_state) != 1) {
              lv_label_set_text_fmt(id(value_label), "%d", (int)x);
            }
```

On confirm, push to HA via `homeassistant.action` -- the round-trip through HA provides authoritative feedback. On timeout (no confirmation), revert to last known HA value.

### HA Actions from ESPHome

**Prerequisite:** Enable "Allow device to perform Home Assistant actions" in the ESPHome integration settings (per device) in HA. Without this, action calls fail silently -- no error in ESPHome logs. See Troubleshooting → "HA Actions Silently Failing".

```yaml
# Newer syntax (preferred):
- homeassistant.action:
    action: input_select.select_option
    data:
      entity_id: input_select.mode
      option: "Auto"

# Older syntax (still works):
- homeassistant.service:
    service: light.toggle
    data:
      entity_id: light.my_light
```

### Error Handling and Resilience

```yaml
# WiFi fallback
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${device_name} Fallback"
  use_address: ${ip}          # Static IP for reliability

# API with reboot timeout
api:
  encryption:
    key: !secret api_key
  reboot_timeout: 0s          # Don't reboot if HA disconnects
```

---
---

# Part 2: LVGL Graphics Component

LVGL (Light and Versatile Graphics Library) is an ESPHome component that provides a rich widget toolkit for building graphical interfaces on embedded displays.

---

## LVGL Core Rules

1. **ESPHome LVGL uses LVGL v8** -- not v9. All widget properties and APIs must match v8.
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
  style_definitions: [...]
  pages: [...]
  top_layer:                     # Always-visible overlay
    widgets: [...]
```

---

## Color Formats
- Hexadecimal: `0xFF0000` (red), `0x00FF00` (green), `0x0000FF` (blue)
- CSS color names: `springgreen`, `white`, `black`, etc.
- ESPHome color IDs
- In lambdas: `lv_color_hex(0xRRGGBB)`

## Opacity Formats
- Strings: `TRANSP` (transparent) or `COVER` (opaque)
- Float: `0.0` to `1.0`
- Percentage: `0%` to `100%`
- In lambdas: Integer `0` to `255`

## Alignment Values
`TOP_LEFT`, `TOP_MID`, `TOP_RIGHT`, `LEFT_MID`, `CENTER`, `RIGHT_MID`, `BOTTOM_LEFT`, `BOTTOM_MID`, `BOTTOM_RIGHT`

For `align_to` (relative to sibling): prefix with `OUT_` e.g. `OUT_TOP_MID`, `OUT_BOTTOM_LEFT`

---

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
- **Needle visibility**: `r_mod` must be POSITIVE (e.g. +5) so the needle extends past the tick edge. Negative `r_mod` with a crop arc makes the needle nearly invisible
- **Min/max labels**: position BELOW the diameter line (`y = meter_y_offset + gap`). Compute positions from meter geometry, don't guess pixel offsets
- **Contrast**: all text on `0x1E1E1E` card background must be at least `0x909090` (~4.5:1). Lower contrast text is unreadable at arm's length on small displays
- **Scrolling**: every `obj` container needs BOTH `scrollbar_mode: "off"` AND `scrollable: false`. The scrollbar property alone only hides the visual; content still scrolls on touch
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

**Background:** `bg_color`, `bg_opa`, `bg_grad` (gradient ID), `bg_grad_color`, `bg_grad_dir` (NONE|HOR|VER), `bg_main_stop`, `bg_grad_stop`, `bg_dither_mode` (NONE|ORDERED|ERR_DIFF), `bg_image_src`, `bg_image_opa`, `bg_image_recolor`, `bg_image_recolor_opa`

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

---

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
            r_mod: 12          # Length offset from scale radius
        - arc:                 # Arc segment indicator
            color: 0xFF0000
            r_mod: 10          # Radius offset from scale
            width: 20
            start_value: 0
            end_value: 50
        - arc:
            color: 0x00FF00
            r_mod: 10
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

### image (img)
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

---

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
                  color_start: 0xDARK
                  color_end: 0xBRIGHT
                  start_value: 0
                  end_value: 10
                  local: true    # REQUIRED for proper gradient
              - line:
                  id: my_needle
                  width: 3
                  color: 0xFFFFFF
                  r_mod: 5       # POSITIVE: extends past ticks for visibility
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
            r_mod: -2
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

---

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

---

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
- `image_recolor_opa: 100%` MUST be set (defaults to 0%)
- Image must be `binary` type for recoloring to work

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

### Compilation Errors in Lambdas
- `return x.c_str()` -- for text_sensor to label text
- `return std::string("text")` -- for string literals
- `static_cast<int>(x)` -- for float to int conversion
- `!lambda return x;` -- single line needs `return`
- `!lambda |- \n  code` -- multiline block scalar

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
- **Multiple `on_boot:` entries**: Allowed with different priorities in the same config
- **Display rotation is NOT an LVGL setting**: `rotation:` belongs on the `display:` platform component, NOT under `lvgl:`. LVGL renders to whatever the display driver provides -- to rotate the output, set `rotation: 90/180/270` on the display component and adjust touchscreen `swap_xy`/`mirror_x`/`mirror_y` to match.

---

## Best Practices

1. **Use `on_release` instead of `on_value`** for sliders/arcs controlling hardware -- avoids continuous service calls during drag.
2. **Use `adv_hittest: true`** on arcs to prevent accidental touches through the center.
3. **Buttonmatrix saves memory** -- ~8 bytes per button vs ~200 for individual buttons.
4. **Always set `image_recolor_opa: 100%`** when using `image_recolor` -- opacity defaults to 0%.
5. **Use style_definitions** for consistent styling across widgets -- reduces YAML duplication.
6. **Grid layout** is preferred for dashboard-style layouts with fixed widget positions.
7. **Flex layout** is preferred for responsive layouts that adapt to content.
8. **Use `top_layer`** for persistent navigation buttons and status indicators.
9. **Home Assistant actions** require explicit enablement per device in HA settings.
10. **Use `scrollbar_mode: "off"` AND `scrollable: false`** on every container object. `scrollbar_mode` only hides the visual scrollbar; without `scrollable: false`, content still scrolls on touch drag.
11. **For floats in formatted text**, use `args: ['x']` or `args: ['x/1000']` -- these are C++ expressions.
12. **Lambda text returns** must return `std::string` -- use `return x.c_str();` for text_sensor values or `return std::string("text");` for string literals.
13. **Use `if_nan`** in text format to handle NaN/Inf sensor values gracefully.
14. **Multiple LVGL instances** are supported for multi-display setups.
15. **Binary image format** is recommended for MDI icons: `image: { binary: [{ file: "mdi:icon-name", id: icon_id, resize: 32x32 }] }`
