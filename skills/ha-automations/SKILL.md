---
name: ha-automations
description: Home Assistant automations, scripts, and blueprints development. Use when writing or modifying HA automation YAML, script YAML, blueprint YAML, or discussing automation triggers, conditions, actions, modes, variables, selectors, or blueprint inputs. Also use when the user mentions HA automations, scripts, choose/if-then, repeat loops, wait_template, wait_for_trigger, blueprint development, or the newer purpose-specific / target-based triggers and conditions (e.g. light.turned_on, battery.became_low, temperature.crossed_threshold, behavior/threshold options).
---

# HA Automations, Scripts & Blueprints — Non-Obvious Reference

This skill contains ONLY things that differ from generic knowledge or are commonly done wrong. If something isn't mentioned here, standard HA docs apply.

## 1. Modern Syntax (2024+)

**Top-level keys are PLURAL:**
```yaml
triggers:    # NOT trigger:
conditions:  # NOT condition:
actions:     # NOT action:
```

**Inside each item, type key is SINGULAR:**
```yaml
triggers:
  - trigger: state       # NOT platform: state
    entity_id: sensor.x
actions:
  - action: light.turn_on  # NOT service: light.turn_on
    data:                   # NOT service_data: or data_template:
      brightness: 100
```

The old `platform:`, `service:`, `data_template:` still work but are deprecated. Always use the modern form.

## 2. State Trigger Gotchas

**Attribute-change filtering behavior:**
- `entity_id` alone with NO `from`/`to`/`not_from`/`not_to` → fires on ALL changes including attribute-only changes
- Adding ANY of `from`/`to`/`not_from`/`not_to` → fires only on STATE changes, ignores attribute-only changes

**YAML boolean coercion — ALWAYS quote these values:**
```yaml
to: "on"     # NOT to: on (YAML reads as boolean true)
from: "off"  # NOT from: off (YAML reads as boolean false)
to: "yes"    # Same issue with yes/no
```

**`for:` does NOT survive HA restart or automation reload.** Timer resets. Workaround: use `input_datetime` + time trigger instead.

**`from`/`to` accept lists:**
```yaml
from:
  - "cleaning"
  - "returning"
to: "error"
```

**`not_from`/`not_to`** exist but CANNOT be combined with `from`/`to` respectively.

## 3. Purpose-Specific Triggers & Conditions (DEFAULT since 2026.7)

**Status:** Introduced in 2025.12 under **Settings → System → Labs**, these **graduated out of Labs and became the new default** in the 2026.7 release. They are now the **recommended** way to build triggers and conditions — no toggle required. The generic `state`/`numeric_state` syntax still works and remains correct for advanced/edge cases, but prefer purpose-specific building blocks for new work.

**What it is:** Purpose-specific building blocks that describe the *intent* ("light turned on", "battery low", "temperature crossed threshold") instead of HA internals (which entity, which raw state, `on`/`detected`/`home`). Format is `domain.trigger_key` / `domain.condition_key`. They handle `unknown`/`unavailable` themselves — you do NOT add logic to ignore those states.

**When reviewing automations:** `trigger: light.turned_on`, `condition: battery.is_low`, `trigger: motion.detected` etc. are valid — do NOT flag as errors.

**Basic example — generic vs purpose-specific:**
```yaml
# GENERIC (still valid):
triggers:
  - trigger: state
    entity_id: light.living_room
    to: "on"
conditions:
  - condition: state
    entity_id: light.living_room
    state: "on"

# PURPOSE-SPECIFIC (preferred):
triggers:
  - trigger: light.turned_on
    target:
      entity_id: light.living_room
conditions:
  - condition: light.is_on
    target:
      entity_id: light.living_room
```

**`target:` is required** and describes *what to watch* — entity, device, area, floor, or label. HA watches every matching entity of that domain behind the target. Combine target types freely.
```yaml
triggers:
  - trigger: light.turned_on
    target:
      area_id: living_room      # any light in the area
      label_id: outdoor         # + any light with this label (types combine)
      # also: entity_id, device_id, floor_id
```
The action side takes a `target:` too, so an automation reads as intent, not a fragile entity list: *"when motion is detected in the outside area, turn on the outside lights."* Swap sensors/lights in that area later and the automation follows.

**⚠️ `behavior` and `threshold` live under an `options:` block — NOT at the top level:**
```yaml
triggers:
  - trigger: light.turned_on
    target:
      area_id: living_room
    options:
      behavior: first   # under options:, NOT a sibling of target:
```

**`behavior` — multi-target matching (values differ between triggers and conditions):**
- **Triggers:** `each` (default — fire on every matching entity), `first` (only when the first of the group enters the state), `all` (only after every targeted entity has).
- **Conditions:** `any` (default — pass if at least one matches), `all` (pass only if every targeted entity matches).
```yaml
conditions:
  - condition: light.is_on
    target:
      area_id: living_room
    options:
      behavior: all     # true only if ALL lights in the area are on
```

**Threshold triggers** — numeric crossings, also under `options:`:
```yaml
triggers:
  - trigger: temperature.crossed_threshold
    target:
      area_id: bedroom
    options:
      threshold:
        type: below            # above | below | between | outside
        value:                 # single value for above/below
          number: 18
          unit_of_measurement: "°C"   # REQUIRED with `number:`
      behavior: each
      for: "00:00:30"          # optional; also under options:
```
- `type: above`/`below` use `value:`; `type: between`/`outside` use `value_min:` and `value_max:`.
- Each value is either `number:` (literal — then `unit_of_measurement:` is required) **or** `entity:` (an `input_number`/`number`/`sensor` — unit taken from the entity), letting you compare against a dynamic setpoint.
- `above`/`below`/`between` are exclusive (equal to bound ≠ crossed); `outside` is inclusive.

**Device-class ("purpose") domains — the big win:** Many building blocks are NOT real entity domains but map by device class across whatever entity reports it. `temperature.crossed_threshold` watches any sensor with the temperature device class; `battery.became_low` watches `binary_sensor` battery-class entities; `motion.detected` watches motion `binary_sensor`s. You target a room, not a sensor model.
- `temperature.*`, `humidity.*`, `illuminance.*`, `power.*`, `air_quality.*` (CO₂, PM2.5, VOC, smoke…) — `.changed`, `.crossed_threshold`, and conditions `.is_value`.
- `motion.*`, `occupancy.*`, `moisture.*`, `illuminance.*` — `.detected` / `.cleared` triggers, `.is_detected` / `.is_not_detected` conditions.
- `battery.*` — triggers `became_low`, `no_longer_low`, `level_crossed`, `level_changed`, `started_charging`, `stopped_charging`; conditions `is_low`, `is_not_low`, `is_level`, `is_charging`, `is_not_charging`.

**Common keys by domain** (representative, not exhaustive — ~189 triggers / ~144 conditions and growing; integrations can add their own):

| Domain | Triggers | Conditions |
|---|---|---|
| `light` | `turned_on`, `turned_off`, `brightness_changed`, `brightness_crossed_threshold` | `is_on`, `is_off`, `is_brightness` |
| `switch`/`fan`/`siren`/`remote` | `turned_on`, `turned_off` | `is_on`, `is_off` |
| `climate` | `turned_on`, `turned_off`, `started_heating`, `started_cooling`, `started_drying`, `hvac_mode_changed`, `target_temperature_crossed_threshold`, `target_humidity_crossed_threshold` | `is_heating`, `is_cooling`, `is_drying`, `is_on`, `is_off`, `is_hvac_mode`, `is_target_temperature` |
| `cover` (per type) | `blind_opened`/`blind_closed`, `curtain_opened`/`closed`, `shutter_opened`/`closed`, `shade_*`, `awning_*` | `blind_is_open`/`blind_is_closed`, `curtain_is_open`, `shutter_is_closed`, … |
| `door`/`window`/`garage_door`/`gate`/`valve` | `opened`, `closed` | `is_open`, `is_closed` |
| `lock` | `locked`, `unlocked`, `opened`, `jammed` | `is_locked`, `is_unlocked`, `is_open`, `is_jammed` |
| `alarm_control_panel` | `armed`, `armed_away`, `armed_home`, `armed_night`, `armed_vacation`, `disarmed`, `triggered` | `is_armed`, `is_armed_away`, `is_disarmed`, `is_triggered`, … |
| `battery` | `became_low`, `no_longer_low`, `level_crossed`, `started_charging`, `stopped_charging` | `is_low`, `is_not_low`, `is_level`, `is_charging` |
| `update` | `became_available` | `is_available`, `is_not_available` |
| `zone` | `entered`, `left`, `occupancy_detected`, `occupancy_cleared` | `in_zone`, `not_in_zone`, `occupancy_is_detected` |
| `sun` | `sunrise`, `sunset`, `dawn`, `dusk`, `elevation_crossed_threshold`, `solar_noon` | `is_up`, `is_night`, `is_ascending`, `elevation` |
| `timer` | `started`, `finished`, `paused`, `cancelled`, `restarted` | `is_active`, `is_idle`, `is_paused` |
| `media_player` | `started_playing`, `stopped_playing`, `paused_playing`, `muted`, `volume_crossed_threshold` | `is_playing`, `is_paused`, `is_muted`, `is_volume` |
| `button` | `pressed` | — |

**Note there is no `person.*` block** — presence is handled via `zone.entered`/`zone.left` and `zone.in_zone` / `zone.not_in_zone` conditions (target the person entity + a zone), or keep the generic `zone` trigger. The **complete documented set** of every trigger/condition key is bundled in [`reference/purpose-specific-keys.md`](reference/purpose-specific-keys.md) — treat it as the allowlist. The live source is [rc.home-assistant.io/triggers](https://rc.home-assistant.io/triggers/) and [/conditions](https://rc.home-assistant.io/conditions/) (each key links to its own page with exact YAML).

### Converting generic → purpose-specific (review/optimize task)

The table above is a snapshot; **the real list grows every release** and integrations add their own keys. So when converting existing automations:

1. **Verify the key exists before proposing it — do NOT invent one.** Check the bundled allowlist [`reference/purpose-specific-keys.md`](reference/purpose-specific-keys.md) first (the complete documented set of trigger/condition keys). If a key is in that file, use it. If it is NOT, do not assume it's invalid (the list grows) but do NOT emit it until you confirm by fetching its own doc page — `https://rc.home-assistant.io/triggers/<key>/` or `.../conditions/<key>/`: **HTTP 200 = real, 404 = does not exist**. A hallucinated key (e.g. `person.arrived_home`, `sensor.co2_high`) produces YAML that silently never fires — worse than leaving the generic form.
2. **Convert only when it preserves behavior exactly.** Prefer purpose-specific when a matching key exists AND the intent maps cleanly (on/off, open/closed, threshold crossing, presence, device-class sensor reading).
3. **Keep the generic `state`/`numeric_state`/`template`/`event` form when:**
   - the entity has **no device class**, so device-class domains (`temperature.*`, `motion.*`, `battery.*`, …) can't match it (check `device_class`/`original_device_class` in `config/.storage/core.entity_registry`, or the entity's attributes via MCP);
   - the trigger keys on a **specific attribute** or uses complex `from`/`to`/`not_from`/`not_to` transitions with no purpose equivalent;
   - it's a **template**, `event`, `mqtt`, or `webhook` trigger, or a custom-integration state;
   - it's a `numeric_state` on a measurement that **has no purpose domain yet**.
4. **When unsure, leave it generic and say why** — a correct generic automation beats an unverified "optimized" one. Present conversions as suggestions with the before/after, not silent rewrites.

Bonus wins conversion often unlocks: replacing a hard-coded entity list with an `area_id`/`label_id` target, and dropping manual `unavailable`/`unknown` guards the building blocks handle for you.

## 4. Numeric State Trigger — Crossing Semantics

Fires ONLY when value CROSSES the threshold. If value is already below threshold and changes to another below-threshold value, it does NOT fire. Must go above first, then come back below.

When `above` AND `below` both specified: defines a range. Fires once on entry, only fires again after leaving and re-entering.

Thresholds can reference entities: `above: sensor.inside_temperature`.

## 5. Template Trigger

Fires when template goes from falsy → truthy (not on every re-evaluation).
- Truthy = non-zero number or strings `true`, `yes`, `on`, `enable`
- Templates with no entity references render once per minute
- `for:` also does NOT survive restart

## 6. Time Trigger Features

**Weekday filtering:**
```yaml
triggers:
  - trigger: time
    at: "06:30:00"
    weekday: ["mon", "tue", "wed"]
```

**Multiple times + sensor offsets:**
```yaml
triggers:
  - trigger: time
    at:
      - input_datetime.leave_for_work
      - "18:30:00"
      - entity_id: sensor.bus_arrival
        offset: "-00:10:00"
```

**Time pattern:** `/5` in minutes = every 5 minutes. Do NOT zero-prefix: `'1'` not `'01'`.

## 7. Automation Modes

| Mode | Behavior | `max` default |
|------|----------|---------------|
| `single` | Won't start if running; warns | 1 (fixed) |
| `restart` | Stops current, starts new | 1 (fixed) |
| `queued` | FIFO queue | 10 |
| `parallel` | Independent concurrent runs | 10 |

`max_exceeded: silent` suppresses the warning log.

## 8. Variables & Scope

**Three scopes:**
1. **`trigger_variables:`** — evaluated ONCE at automation load time. LIMITED templates only (no `states()`, `now()`, etc.). Primarily for `!input` references in triggers.
2. **`variables:`** (automation-level) — full template support including `trigger` variable.
3. **`variables:`** (per-trigger) — set when that specific trigger fires.

**Critical scoping rule:** Variables set inside `if/then`, `choose`, or `repeat` blocks bubble UP to the parent scope. This is NOT block-scoped like most programming languages.

**Available in templates:**
- `trigger` — object with trigger details; `trigger.id`, `trigger.idx`, `trigger.platform`
- `this` — state object of the automation at moment of triggering (snapshot, does NOT update during execution)

**`!input` is a YAML tag, NOT a template.** Cannot be used inside `{{ }}`. To use in templates, expose via variables:
```yaml
variables:
  my_input: !input my_input
```

## 9. Action Details

**`target:` accepts templates:**
```yaml
target: "{{ {'entity_id': ['light.office', 'light.office_2']} }}"
```

**Condition as sequence stopper:** A bare `condition:` step in actions stops execution if false. Inside `repeat`, stops only current iteration, not the whole loop.

**Multiple conditions (AND logic) use plural key:**
```yaml
- conditions:
    - condition: state
      entity_id: sensor.x
      state: "on"
    - condition: numeric_state
      entity_id: sensor.y
      below: 20
```

## 10. Scripts — Key Differences from Automations

**Fields (parameters):** UI hints only — HA does NOT enforce `required` at runtime. Guard with templates yourself.
```yaml
script:
  my_script:
    fields:
      param1:
        name: Parameter
        required: true  # UI hint only!
        selector:
          text:
    sequence:
      - action: notify.notify
        data:
          message: "{{ param1 }}"
```

**Response variables:**
```yaml
- action: calendar.get_events
  target:
    entity_id: calendar.school
  data:
    duration:
      hours: 24
  response_variable: agenda
```

**Wait patterns:**
```yaml
- wait_template: "{{ is_state('sensor.x', 'ready') }}"
  timeout: "00:05:00"
  continue_on_timeout: false  # DEFAULT IS TRUE! Must set false to abort
```

After wait: `wait.completed` (bool), `wait.remaining` (time left or none), `wait.trigger` (for wait_for_trigger).

**`wait_template` only re-evaluates when a referenced entity changes.** Using `now()` alone won't trigger re-evaluation.

**Blocking vs fire-and-forget calls — DIFFERENT data structure:**
```yaml
# Blocking (caller waits, errors propagate):
- action: script.my_script
  data:
    param1: value1

# Fire-and-forget (caller doesn't wait):
- action: script.turn_on
  target:
    entity_id: script.my_script
  data:
    variables:        # Note: wrapped in variables!
      param1: value1
```

**Parallel execution:**
```yaml
- parallel:
    - sequence:
        - action: notify.person1
    - action: notify.person2
```
If one parallel branch fails, others still complete. Avoid modifying same variable in parallel branches (race condition).

**`continue_on_error: true`** per action — catches execution failures only, NOT YAML/config errors.

**`set_conversation_response:`** — returns text to voice/conversation agents. Last value wins if called multiple times.

## 11. Blueprints

**Input sections (2024.6+):** Group inputs visually. All inputs in collapsed sections MUST have a `default`.
```yaml
input:
  top_level_input:
    name: Always visible
    selector:
      text:
  my_section:
    name: Optional Settings
    icon: mdi:cog
    collapsed: true
    input:
      grouped_input:
        name: Hidden by default
        default: "fallback"
        selector:
          text:
```

**Input names must be globally unique** across ALL sections.

**Key selectors:**
```yaml
# Action selector — lets user define custom action sequences:
selector:
  action: {}

# Trigger selector — lets user define custom triggers:
selector:
  trigger: {}

# Entity with filters:
selector:
  entity:
    multiple: true
    filter:
      - domain: [light, switch]
        device_class: button

# Target selector (returns entity_id/device_id/area_id):
selector:
  target:

# Number with slider:
selector:
  number:
    min: 0
    max: 100
    step: 1
    mode: slider

# Duration:
selector:
  duration:
    enable_day: true

# Constant (value when enabled, nothing when disabled):
selector:
  constant:
    value: true
    label: Enable feature
```

**Merging trigger lists (2024.10+):** Flatten user-provided triggers into main list:
```yaml
triggers:
  - trigger: event
    event_type: manual_event
  - triggers: !input user_triggers
```

**`homeassistant.min_version`** format: `YYYY.M.P` (all three parts required).

**Disabling individual triggers:** `enabled: false` or `enabled: !input toggle_input`. Evaluated ONCE at load time, not dynamically.

## 12. Timer-Based Automation Pattern (Restart-Safe)

Use timer entities + state triggers instead of `delay:` or `wait_template:` in action sequences. This pattern survives HA restarts because the timer state persists.

```yaml
triggers:
  - trigger: state
    entity_id: !input controlled_entity
    to: "on"
    id: device_on
  - trigger: state
    entity_id: !input timer_entity
    to: idle
    id: timer_finished
  - trigger: state
    entity_id: !input controlled_entity
    to: "off"
    id: device_off
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: device_on
        sequence:
          - action: timer.start
            target:
              entity_id: !input timer_entity
      - conditions:
          - condition: trigger
            id: timer_finished
        sequence:
          - action: homeassistant.turn_off
            target:
              entity_id: !input controlled_entity
      - conditions:
          - condition: trigger
            id: device_off
        sequence:
          - if:
              - condition: state
                entity_id: !input timer_entity
                state: active
            then:
              - action: timer.cancel
                target:
                  entity_id: !input timer_entity
```

**When to use this pattern:**
- Any automation that needs a timeout/delay and must survive restarts
- Device auto-shutoff (fans, heaters, coffee machines)
- Debouncing state changes
- Cooldown periods between automation runs

**When NOT to use:** Simple one-shot delays where restart safety isn't needed.

## 13. Polling vs Event-Driven — Architecture Decision

Two paradigms for HA automations. Choose based on failure mode:

**Polling (periodic check)** — use `time_pattern` trigger + condition check:
- **When:** Missing the event would leave the system in a bad/dangerous state (water running, heater stuck on, device not turning off)
- **Why:** Numeric state triggers only fire on threshold CROSSING (section 4). If you miss the single crossing moment (HA restart, network glitch, sensor hiccup), the automation never fires. Periodic checks catch the condition even if the crossing was missed.
- **Pattern:** Run every 1/5/15 min or at a fixed time, check whether current state warrants action
- **Examples:**
  - Temperature safety: check every 5 min if temp is above limit → turn off heater (don't rely on crossing the threshold)
  - Energy management: run every 15 min, check surplus/deficit conditions → adjust loads
  - Daily schedule: run at fixed time, check if conditions met → execute
  - Watchdog: periodically verify that a device that should be off IS off

```yaml
triggers:
  - trigger: time_pattern
    minutes: "/5"
conditions:
  - condition: numeric_state
    entity_id: sensor.water_temp
    above: 65
actions:
  - action: switch.turn_off
    target:
      entity_id: switch.water_heater
```

**Event-driven (reactive)** — use state/event triggers for immediate response:
- **When:** Immediate reaction matters AND missing the event is either unlikely or self-correcting
- **Why:** Low latency, no unnecessary polling overhead
- **Examples:**
  - Motion → light on (next motion re-triggers anyway)
  - Device on → start timer → auto-off (timer pattern from section 12)
  - Button press → action
  - Door open → notification

**Hybrid (belt-and-suspenders):** Combine both — event trigger for immediate response + periodic trigger as safety net:
```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.water_temp
    above: 65
    id: threshold
  - trigger: time_pattern
    minutes: "/5"
    id: periodic_check
conditions:
  - condition: numeric_state
    entity_id: sensor.water_temp
    above: 65
actions:
  - action: switch.turn_off
    target:
      entity_id: switch.water_heater
```
The condition ensures the periodic trigger only acts when needed, while the event trigger provides immediate response when available.

## 14. Webhook Trigger Notes

- A webhook ID can only be used in ONE automation at a time
- `local_only: true` by default — must set `false` for internet access
- `trigger.json` (JSON payloads) vs `trigger.data` (form data) vs `trigger.query` (URL params)
