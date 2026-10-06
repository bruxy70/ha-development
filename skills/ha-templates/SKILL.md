---
name: ha-templates
description: Home Assistant Jinja2 templating reference. Use when writing or modifying HA templates in automations, scripts, sensors, template entities, or any YAML that contains {{ }} Jinja2 expressions. Also use when discussing HA template functions (states, state_attr, is_state), filters, time handling, namespace loops, or template sensor configuration. Critical for avoiding sandbox security errors and HA-specific Jinja2 differences.
---

# HA Jinja2 Templates — Non-Obvious Reference

This skill contains ONLY HA-specific Jinja2 differences, sandbox restrictions, and pitfalls. Standard Jinja2 knowledge applies for everything else.

**Function/filter/test names:** the complete documented set is bundled in [`reference/template-functions.md`](reference/template-functions.md) (200 entries) — use it to discover documented names, then verify target-version support and exact signatures. Before using a function/filter/test that isn't standard Jinja2, confirm it's in that file, or read its official page and confirm the target-version signature. HTTP 200 verifies that a documentation page exists, not that its feature is supported by the target installed version or that a guessed signature is valid. Read the page and match its feature/version/schema before emission. A snapshot's absence alone does not prove invalidity. Do not invent names. The docs were restructured in 2026.4: the reference now lives at [/template-functions/](https://rc.home-assistant.io/template-functions/) and the guides at [/docs/templating/](https://rc.home-assistant.io/docs/templating/).

## Workflow and checklist

Check sandbox restrictions, missing-state handling, return type and execution context before writing a template.

1. Identify the template's consumer, target HA version, intended type and available inputs.
2. Choose state-based sensors for automatic dependency tracking or trigger-based sensors for explicitly triggered updates. Check limited-template context and documented function signatures; on uncertainty, return to step 1.
3. Draft with safe state access, conversion defaults and namespace/concatenation where needed.
4. Render normal, missing, unknown/unavailable and boundary inputs in the target HA template context, then run [ha-validate](../ha-validate/SKILL.md). Offline Jinja can check supported syntax but cannot prove HA helpers, native return types or update behavior. On failure return to step 3, fix and re-render; stop repeated unchanged failure with a blocker.
5. Report observed values/types and checks separately from unavailable live verification.

- [ ] Confirm consumer, version, inputs and output type.
- [ ] Check context and helper signatures; return to scope if unknown.
- [ ] Render edge cases and validate; return to draft on failure.
- [ ] Record type/update evidence and verification limits.

## Requirements and execution boundary

Uses host filesystem text tools and browser/web-fetch access to current HA docs; no package install is needed for lookup. Rendering/semantic checks require configured supported HA access using [connection setup](../ha-mcp-setup/SKILL.md); check tools use [validation](../ha-validate/SKILL.md). These references support both Claude Code and Codex marketplace consumers; resolve links relative to the loaded skill, independently of the working directory.

Examples are adaptable fragments, not complete configurations. Preserve required schema/API, nesting and semantic guards; replace entities, inputs, timing and targets with project values. Loading this skill does not authorize live actions, reloads, restarts or deployment. Use only the live target/actions already authorized by the user; otherwise report offline results and obtain explicit scope before live changes.

[Cross-client enforcement proposals](../ha-validate/reference/enforcement.md) describe candidate hook events and their limits; no hook is activated by reading this skill. [Three evaluation prompts and results](reference/evaluations.md) track model/client evidence.


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

{# Filtering — Jinja select; Python comprehensions are unsupported: #}
{{ [1, 6, 9] | select('gt', 5) | list }}  {# [6, 9] #}
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
| `symmetric_difference(list2)` | In either, but NOT both |
| `union(list2)` | All unique elements |
| `combine(dict2, recursive=False)` | Merge dicts |
| `flatten(levels)` | Flatten nested lists |
| `merge_response(response)` | Flatten action `response_variable` dicts into one list (e.g. `calendar.get_events` across entities) |
| `shuffle` / `typeof` | Randomize list order / return a value's type name as string (2023.x+) |

## 19. Area/Device/Label/Entity Helper Functions

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

**Name/description lookups** (return the human-readable name, or `None` if not found):
```jinja
{{ entity_name('sensor.living_room_temperature') }}  {# "Living Room Temperature" #}
{{ device_name('a1b2c3…') }}      {# accepts a device_id OR an entity_id #}
{{ area_name('living_room') }}    {# also floor_name(), label_name(), label_description() #}
```

**Localized state text** — the state/attribute as shown in the UI language, not the raw value:
```jinja
{{ state_translated('climate.living_room') }}                    {# "Heizen" in German, not "heating" #}
{{ state_attr_translated('climate.living_room', 'hvac_action') }}
```
Use these for notifications/dashboards; keep raw `states()`/`state_attr()` for logic/comparisons.

## 20. Math Helpers & the Radians Gotcha

- **Trig functions take RADIANS, not degrees:** `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`. Convert first: `{{ sin(45 | radians) }}`.
- `clamp(value, min, max)` (2025.4) — constrain to a range. `remap(value, low1, high1, low2, high2, steps=…, edges=…)` (2025.5) — rescale between ranges (e.g. 0–100 → 0–255); `edges` controls out-of-range handling.
- Stats: `average(list)`, `median`, `statistical_mode`. Hashes: `md5`, `sha1`, `sha256`, `sha512`. Bitwise: `bitwise_and/or/xor`. Encoding: `from_hex`, `pack`/`unpack`, `base64_encode`/`_decode`.
- Most of these are `limited: true` — they work in [limited templates](#9-limited-templates) (unlike `states()` etc.).

## 21. `apply` — Pass a Function Where a Filter Is Expected

Complements `as_function` (§11). `apply(value, fn, *args)` calls `fn` with `value`, so you can use a function inside `map`/`select`/`reject`:
```jinja
{{ [1, 2, 3] | map('apply', my_fn) | list }}
{{ apply(5, float) }}   {# 5.0 #}
```
