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
- ESPHome LVGL widgets: https://esphome.io/components/lvgl/widgets/
- ESPHome LVGL layouts: https://esphome.io/components/lvgl/layouts/
- ESPHome LVGL animations: https://esphome.io/components/lvgl/animation/
- ESPHome LVGL cookbook: https://esphome.io/cookbook/lvgl/
- LVGL upstream docs: https://docs.lvgl.io/master/

**Doc currency:** this skill is synced to **ESPHome 2026.9**. When working against a newer
release, check the changelog for `[lvgl]` lines before trusting the syntax here.

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

### ESP32-P4 with MIPI-DSI

Newer boards (e.g. CrowPanel/Waveshare 7" P4) use the ESP32-P4 with a built-in MIPI-DSI
interface and a separate ESP32-C6 co-processor for Wi-Fi. Config differs substantially from S3
— these keys are the non-obvious, load-bearing ones (pin numbers are board-specific):

```yaml
esp32:
  variant: esp32p4              # NOT `board:` — P4 uses `variant:`
  engineering_sample: true      # required for pre-rev3 P4 silicon
  cpu_frequency: 360MHZ
  flash_size: 16MB
  framework:
    type: esp-idf
    advanced:
      execute_from_psram: true              # REQUIRED (keep true; false overflows flash)
      enable_idf_experimental_features: true
  # Do NOT use the old `sdkconfig_options:` block — replaced by `advanced:`

psram:
  speed: 200MHz                 # no `mode:` key on P4

esp_ldo:                        # P4 needs TWO LDO channels (3 AND 4), both 2.5V
  - channel: 3
    voltage: 2.5V
  - channel: 4
    voltage: 2.5V

esp32_hosted:                   # Wi-Fi runs on a C6 co-processor over SDIO
  variant: esp32c6
  # ...reset/cmd/clk/d0–d3 pins per board...
  # sdio_frequency: 10MHz       # stability fix: default 40MHz causes
                                # `sdmmc_io_rw_extended ... 0x109` timeouts/reboots (ESPHome #14313)

display:
  - platform: mipi_dsi          # built into ESPHome — no external_components needed
    model: WAVESHARE-ESP32-P4-WIFI6-TOUCH-LCD-7B   # or CUSTOM with explicit timings
    reset_pin: { number: 41 }
    update_interval: never
    auto_clear_enabled: false
    dimensions: { width: 1024, height: 600 }
    color_order: RGB
    color_depth: 16
```

**RGB565 images need explicit byte order on P4 MIPI-DSI** — set `byte_order: little_endian` on
the `lvgl:` block *and* on every `rgb565`/`RGB565` image, or images render with corrupted
colours. (Not needed on S3 RPI-DPI-RGB.)

```yaml
image:
  - file: foo.png
    type: RGB565
    byte_order: little_endian
lvgl:
  byte_order: little_endian
```

**Backlight + power pins:** backlight is LEDC PWM (e.g. GPIO31); a separate inverted GPIO
"power_light" (e.g. GPIO29) must be turned **off** shortly after boot (`on_boot`). **Flashing:**
native USB — hold BOOT, tap RESET, release; command-line `esphome run` is more reliable than
WebSerial. **Portrait:** put `rotation:` on `display:` (not under `lvgl:`) and add
`swap_xy`/`mirror_y` to the touchscreen — see "Touch Calibration" below.

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

### HA Actions That Return Data (`capture_response`)

Some HA actions return a payload rather than just acting (`weather.get_forecasts`,
`recorder.get_statistics`, …). Set `capture_response: true` and read the result in `on_success`,
where it is exposed as a `JsonObjectConst` named `response`. `on_success` is **required** when
`capture_response` is set. This is the only way to pull *bulk* data (multi-day forecast, history
series) onto the display -- a `platform: homeassistant` sensor can only mirror one scalar/attribute.

```yaml
- homeassistant.action:
    action: weather.get_forecasts
    data:
      entity_id: weather.home
      type: daily
    capture_response: true
    on_success:
      - lambda: |-
          JsonArrayConst days = response["response"]["weather.home"]["forecast"];
          for (int i = 0; i < 5 && i < (int) days.size(); i++) {
            JsonObjectConst d = days[i];
            float high = d["temperature"] | NAN;    // `| default` guards a missing key
            std::string cond = d["condition"] | "";
            // ...update widgets...
          }
    on_error:
      - logger.log: "forecast fetch failed"
```

Note the payload nesting: `response["response"][<entity_id>]` -- the outer `"response"` key is
always there, and the inner key is the entity id string, not a generic name.

**Gotchas:**

- **Scalar, not list.** ESPHome's `data:` validator rejects YAML lists here: `statistic_ids: [a, b]`
  fails with `Must be string, got <class 'esphome.helpers.EList'>`. Pass a single value as a plain
  scalar (`statistic_ids: sensor.foo`, `types: mean`). Same for any other list-typed action field.
- **Computed arguments go in `data_template:`**, not `data:` -- that's where `!lambda` is allowed
  (e.g. building an ISO timestamp for `start_time`).
- **The device must be authorized** to perform HA actions (see the prerequisite above) -- a
  response-capturing call fails just as silently as a fire-and-forget one when it isn't.
- `recorder.get_statistics` is documented as admin-only in HA; verify on-device rather than
  assuming the ESPHome device is allowed to call it.

**Fetching a history series** (for a trend chart) with `recorder.get_statistics`. Align the window
to whole hours *and* pass `end_time`, otherwise the still-accumulating current hour comes back as a
bucket with no `mean` and the last point of the chart collapses to zero:

```yaml
- homeassistant.action:
    action: recorder.get_statistics
    data:
      statistic_ids: sensor.battery_state_of_charge   # needs a state_class for LTS to exist
      period: hour
      types: mean
    data_template:
      start_time: !lambda |-
        time_t now_epoch = id(ha_time).now().timestamp;
        time_t hour_start = now_epoch - (now_epoch % 3600);   // last COMPLETE hour
        auto t = ESPTime::from_epoch_utc(hour_start - 24 * 3600);
        char buf[32];
        snprintf(buf, sizeof(buf), "%04d-%02d-%02dT%02d:%02d:%02d+00:00",
                 t.year, t.month, t.day_of_month, t.hour, t.minute, t.second);
        return std::string(buf);
      end_time: !lambda |-
        // ...same, at hour_start -- excludes the partial current hour...
    capture_response: true
    on_success:
      - lambda: |-
          JsonArrayConst buckets = response["response"]["statistics"]["sensor.battery_state_of_charge"];
          // buckets[i]["mean"] -- may be absent for hours with no recorded data
```

Only entities with a `state_class` of `measurement`/`total`/`total_increasing` have long-term
statistics; anything else returns nothing. Gaps are normal -- decide explicitly whether to carry
the previous value forward or show a break, and if you carry it forward, **say so on screen**, or a
guessed flat line is indistinguishable from a real one.

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
- **Needle visibility**: the needle must extend past the tick edge, or a crop arc makes it nearly invisible. On 2026.4+ size the needle with `length:` (a `%` or px of the scale radius) and nudge arcs with `padding:`; the old `r_mod` alias needed a POSITIVE value (e.g. +5) for the same effect
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
