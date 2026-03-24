---
name: ha-automations
description: Home Assistant automations, scripts, and blueprints development. Use when writing or modifying HA automation YAML, script YAML, blueprint YAML, or discussing automation triggers, conditions, actions, modes, variables, selectors, or blueprint inputs. Also use when the user mentions HA automations, scripts, choose/if-then, repeat loops, wait_template, wait_for_trigger, or blueprint development.
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

## 3. Numeric State Trigger — Crossing Semantics

Fires ONLY when value CROSSES the threshold. If value is already below threshold and changes to another below-threshold value, it does NOT fire. Must go above first, then come back below.

When `above` AND `below` both specified: defines a range. Fires once on entry, only fires again after leaving and re-entering.

Thresholds can reference entities: `above: sensor.inside_temperature`.

## 4. Template Trigger

Fires when template goes from falsy → truthy (not on every re-evaluation).
- Truthy = non-zero number or strings `true`, `yes`, `on`, `enable`
- Templates with no entity references render once per minute
- `for:` also does NOT survive restart

## 5. Time Trigger Features

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

## 6. Automation Modes

| Mode | Behavior | `max` default |
|------|----------|---------------|
| `single` | Won't start if running; warns | 1 (fixed) |
| `restart` | Stops current, starts new | 1 (fixed) |
| `queued` | FIFO queue | 10 |
| `parallel` | Independent concurrent runs | 10 |

`max_exceeded: silent` suppresses the warning log.

## 7. Variables & Scope

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

## 8. Action Details

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

## 9. Scripts — Key Differences from Automations

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

## 10. Blueprints

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

## 11. Timer-Based Automation Pattern (Restart-Safe)

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

## 12. Polling vs Event-Driven — Architecture Decision

Two paradigms for HA automations. Choose based on failure mode:

**Polling (periodic check)** — use `time_pattern` trigger + condition check:
- **When:** Missing the event would leave the system in a bad/dangerous state (water running, heater stuck on, device not turning off)
- **Why:** Numeric state triggers only fire on threshold CROSSING (section 3). If you miss the single crossing moment (HA restart, network glitch, sensor hiccup), the automation never fires. Periodic checks catch the condition even if the crossing was missed.
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
  - Device on → start timer → auto-off (timer pattern from section 11)
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

## 13. Webhook Trigger Notes

- A webhook ID can only be used in ONE automation at a time
- `local_only: true` by default — must set `false` for internet access
- `trigger.json` (JSON payloads) vs `trigger.data` (form data) vs `trigger.query` (URL params)
