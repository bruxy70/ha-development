# Framework

## Contents

- [ESPHome Project Configuration](#esphome-project-configuration)
- [Substitutions](#substitutions)
- [Package System](#package-system)
- [YAML Structure Order](#yaml-structure-order)
- [YAML Formatting Rules](#yaml-formatting-rules)
- [Naming Conventions](#naming-conventions)

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
