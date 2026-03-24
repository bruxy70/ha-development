---
name: ha-templates
description: Home Assistant Jinja2 templating reference. Use when writing or modifying HA templates in automations, scripts, sensors, template entities, or any YAML that contains {{ }} Jinja2 expressions. Also use when discussing HA template functions (states, state_attr, is_state), filters, time handling, namespace loops, or template sensor configuration. Critical for avoiding sandbox security errors and HA-specific Jinja2 differences.
---

# HA Jinja2 Templates — Non-Obvious Reference

This skill contains ONLY HA-specific Jinja2 differences, sandbox restrictions, and pitfalls. Standard Jinja2 knowledge applies for everything else.

## 1. Sandbox Security Restrictions

**BLOCKED operations (raise `SecurityError: unsafe operation`):**
- `list.append()`, `list.remove()`, `list.pop()`, `list.insert()`, `list.extend()`
- `dict.pop()`, `dict.update()`
- ANY in-place mutation of objects

**Safe alternatives:**
```jinja
{# List building — use concatenation: #}
{% set items = items + [new_item] %}

{# Dict merging — use combine filter: #}
{{ dict1 | combine(dict2) }}
{{ dict1 | combine(dict2, recursive=True) }}

{# Filtering — use comprehension or selectattr: #}
{{ [x for x in list if x > 5] }}
{{ items | selectattr('active', 'eq', true) | list }}
```

## 2. State Access — Safe vs Unsafe

| Pattern | Returns | Missing entity |
|---|---|---|
| `states('sensor.x')` | String | `"unknown"` (safe) |
| `states.sensor.x.state` | String | **Raises error** |
| `state_attr('sensor.x', 'attr')` | Value or None | `None` (safe) |
| `is_state('sensor.x', 'on')` | Bool | `False` (safe) |

**Rule:** ALWAYS prefer function forms (`states()`, `state_attr()`, `is_state()`) over attribute access.

**Extended parameters:**
```jinja
{{ states('sensor.temp', rounded=True, with_unit=True) }}
```

**Iteration:** `states` yields all state objects; `states.sensor` yields sensor domain only.

## 3. Pipe Operator Precedence — MAJOR PITFALL

`|` binds TIGHTER than arithmetic:
```jinja
{# WRONG — rounds 10, then divides: #}
{{ states('sensor.x') | float / 10 | round(2) }}

{# CORRECT — parentheses required: #}
{{ (states('sensor.x') | float / 10) | round(2) }}
```

## 4. `iif()` Does NOT Short-Circuit

```jinja
{# WRONG — float conversion executes even if sensor unavailable: #}
{{ iif(has_value('sensor.x'), states('sensor.x') | float, 0) }}

{# CORRECT — ternary short-circuits: #}
{{ states('sensor.x') | float if has_value('sensor.x') else 0 }}
```

## 5. Namespace for Loop Variable Scoping

Variables set inside `{% for %}` do NOT persist outside (standard Jinja2 scoping):
```jinja
{# WRONG — total stays 0 outside loop: #}
{% set total = 0 %}
{% for item in items %}
  {% set total = total + item %}
{% endfor %}
{{ total }}  {# Always 0! #}

{# CORRECT — use namespace: #}
{% set ns = namespace(total=0, items=[]) %}
{% for item in source %}
  {% set ns.total = ns.total + item %}
  {% set ns.items = ns.items + [item] %}  {# concat, not append! #}
{% endfor %}
{{ ns.total }}
```

## 6. Type Conversion

- `states()` ALWAYS returns a string. Must convert before math.
- `| float(0)` — returns 0 on conversion failure (safe default)
- `| int(0)` — same pattern
- Cannot catch undefined variables — check with `is not none` first
- `is_number` returns False for infinity, NaN, and boolean strings

## 7. Unavailable/Unknown Handling

```jinja
{# Best practice: #}
{% if has_value('sensor.x') %}
  {{ states('sensor.x') | float }}
{% endif %}

{# Alternative: #}
{% if states('sensor.x') not in ['unknown', 'unavailable'] %}
```

`has_value(entity_id)` returns True only if state is NOT "unknown" and NOT "unavailable".

## 8. Time/Date Functions

| Function | Returns | Note |
|---|---|---|
| `now()` | Local datetime | Causes template to re-render every minute |
| `utcnow()` | UTC datetime | Also triggers minute refresh |
| `today_at("HH:MM")` | Today + time | Also triggers minute refresh |
| `as_timestamp(dt)` | Float UNIX timestamp | Input: datetime or ISO string |
| `as_datetime(val)` | Datetime object | Input: timestamp or ISO string |
| `as_local(dt)` | Local datetime | Input: datetime object |
| `as_timedelta("1:30:00")` | timedelta | Accepts "DD HH:MM:SS", ISO 8601 |
| `timedelta(hours=1)` | timedelta | Standard Python kwargs |
| `relative_time(dt)` | Human string | **Past only** — "2 hours ago" style |
| `time_since(dt, precision)` | Human string | Future returns "0 seconds" |
| `time_until(dt, precision)` | Human string | Past returns "0 seconds" |

**Frontend timestamp pitfall:** For `device_class: timestamp`, state MUST be ISO 8601. Use `.isoformat()`.

## 9. Limited Templates

Certain contexts (some trigger configs, `trigger_variables`) only support a SUBSET. NOT available in limited templates:
- `states()`, `state_attr()`, `is_state()`, `has_value()`
- `now()`, `utcnow()`, `today_at()`
- Device/area/label functions, `expand()`, `closest()`

## 10. Enabled Jinja2 Extensions

- **Loop Controls:** `{% break %}` and `{% continue %}` work in loops
- **Expression Statement:** `{% do expression %}` evaluates without output

## 11. `as_function` Filter — Typed Returns from Macros

Macros normally return strings. To return typed values (lists, dicts, numbers):
```jinja
{% macro calc(x, returns) %}
  {%- do returns(x * 2) -%}
{% endmacro %}
{{ calc | as_function }}(5)  {# Returns integer 10, not "10" #}
```
The macro MUST have a `returns` parameter and call `do returns(value)`.

## 12. Regex Support

```jinja
{{ "123-456" is match("\\d+-\\d+") }}          {# Anchored to start #}
{{ "hello 123" is search("\\d+") }}             {# Anywhere in string #}
{{ "a1b2" | regex_findall("\\d+") }}            {# ['1','2'] #}
{{ "foo-bar" | regex_replace("(\\w+)-(\\w+)", "\\2-\\1") }}
```

## 13. Entity IDs Starting with Numbers

```jinja
{# WRONG — parser error: #}
{{ states.device_tracker.2008_gmc.state }}

{# CORRECT — bracket notation: #}
{{ states.device_tracker['2008_gmc'].state }}
```

## 14. Custom Reusable Templates

Files in `config/custom_templates/*.jinja` (max 5MB each):
```jinja
{% from 'power_helpers.jinja' import calculate_surplus %}
{{ calculate_surplus() }}
```
Reload with `homeassistant.reload_custom_templates` action.

## 15. Template Sensor Configuration

**Modern (use this):**
```yaml
template:
  - sensor:
      - name: "My Sensor"
        unique_id: my_sensor_id
        unit_of_measurement: "W"
        state_class: measurement
        device_class: power
        state: "{{ states('sensor.source') | float(0) }}"
        availability: "{{ has_value('sensor.source') }}"
        attributes:
          detail: "{{ state_attr('sensor.source', 'detail') }}"
```

**Legacy (deprecated) — different keys:**
```yaml
sensor:
  - platform: template
    sensors:
      my_sensor:
        value_template: "..."      # NOT "state:"
        attribute_templates:        # NOT "attributes:"
          detail: "..."
```

## 16. Trigger-Based Template Sensors

Only render when trigger fires (not automatic entity tracking). State persists across HA restarts.
```yaml
template:
  - triggers:
      - trigger: state
        entity_id: sensor.source
    actions:
      - variables:
          computed: "{{ trigger.to_state.state | float * 1.1 }}"
    sensor:
      - name: "Computed"
        state: "{{ computed }}"
```

## 17. Binary Sensor State Evaluation

Returns `on` for: `True`, `"yes"`, `"on"`, `"enable"`, positive number.
Returns `off` for: `False`, `"no"`, `"off"`, `"disable"`, `0`.

## 18. Collection Filters

| Filter | Purpose |
|---|---|
| `intersect(list2)` | Common elements |
| `difference(list2)` | In first, not second |
| `union(list2)` | All unique elements |
| `combine(dict2)` | Merge dicts |
| `flatten(levels)` | Flatten nested lists |

## 19. Area/Device/Label Helper Functions

```jinja
{{ area_entities('living_room') }}
{{ area_devices('living_room') }}
{{ device_entities('device_id') }}
{{ label_entities('energy') }}
{{ integration_entities('hue') }}
{{ areas() }}    {# All area IDs #}
{{ floors() }}   {# All floor IDs #}
{{ labels() }}   {# All label IDs #}
{{ labels('sensor.temp') }}  {# Labels on entity #}
```
All also work as filters: `'living_room' | area_entities`.
