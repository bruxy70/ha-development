# Ha Integration

## Contents

- [Home Assistant Integration](#home-assistant-integration)
- [Bidirectional State Synchronization (3-Step Pattern)](#bidirectional-state-synchronization-3-step-pattern)
- [Importing Sensor Data](#importing-sensor-data)
- [Importing Text Sensor Data](#importing-text-sensor-data)
- [Conditional Logic Based on State](#conditional-logic-based-on-state)
- [Switch Controlling Home Assistant](#switch-controlling-home-assistant)
- [Button Calling Home Assistant Action](#button-calling-home-assistant-action)
- [Slider with Home Assistant Sync](#slider-with-home-assistant-sync)
- [Radio Button Pattern (Mutually Exclusive Modes)](#radio-button-pattern-mutually-exclusive-modes)
- [Time-Remaining Formatting](#time-remaining-formatting)
- [Boot-Time State Initialization](#boot-time-state-initialization)
- [Time Source from Home Assistant](#time-source-from-home-assistant)
- [Edit Mode Bidirectional Sync (Guard Pattern)](#edit-mode-bidirectional-sync-guard-pattern)
- [HA Actions from ESPHome](#ha-actions-from-esphome)
- [HA Actions That Return Data (`capture_response`)](#ha-actions-that-return-data-capture_response)
- [Error Handling and Resilience](#error-handling-and-resilience)

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
    - priority: -100          # After component setup; LVGL widgets exist
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
