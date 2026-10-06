# Purpose-specific automation details

## Contents
- [Purpose-specific triggers and conditions](#3-purpose-specific-triggers--conditions-default-since-20267)
- [Converting generic to purpose-specific](#converting-generic--purpose-specific-reviewoptimize-task)

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

**Note there is no `person.*` block** — presence is handled via `zone.entered`/`zone.left` and `zone.in_zone` / `zone.not_in_zone` conditions (target the person entity + a zone), or keep the generic `zone` trigger. The **complete documented set** of every trigger/condition key is bundled in [`purpose-specific-keys.md`](purpose-specific-keys.md) — verify target-version support and exact schema before emission. The live source is [rc.home-assistant.io/triggers](https://rc.home-assistant.io/triggers/) and [/conditions](https://rc.home-assistant.io/conditions/) (each key links to its own page with exact YAML).

### Converting generic → purpose-specific (review/optimize task)

The table above is a snapshot; **the real list grows every release** and integrations add their own keys. So when converting existing automations:

1. **Verify the key exists before proposing it — do NOT invent one.** Check the bundled allowlist [`purpose-specific-keys.md`](purpose-specific-keys.md) first (the complete documented set of trigger/condition keys). If a key is in that file, verify its documented schema against the target installed version before use. If it is NOT, do not assume it's invalid (the list grows) but do NOT emit it until you confirm by fetching its own doc page — `https://rc.home-assistant.io/triggers/<key>/` or `.../conditions/<key>/`: HTTP 200 verifies that a documentation page exists, not that its feature is supported by the target installed version or that a guessed signature is valid. Read the page and match its feature/version/schema before emission. A snapshot's absence alone does not prove invalidity. A hallucinated key (e.g. `person.arrived_home`, `sensor.co2_high`) produces YAML that silently never fires — worse than leaving the generic form.
2. **Convert only when it preserves behavior exactly.** Prefer purpose-specific when a matching key exists AND the intent maps cleanly (on/off, open/closed, threshold crossing, presence, device-class sensor reading).
3. **Keep the generic `state`/`numeric_state`/`template`/`event` form when:**
   - the entity has **no device class**, so device-class domains (`temperature.*`, `motion.*`, `battery.*`, …) can't match it (check `device_class`/`original_device_class` in `config/.storage/core.entity_registry`, or the entity's attributes via MCP);
   - the trigger keys on a **specific attribute** or uses complex `from`/`to`/`not_from`/`not_to` transitions with no purpose equivalent;
   - it's a **template**, `event`, `mqtt`, or `webhook` trigger, or a custom-integration state;
   - it's a `numeric_state` on a measurement that **has no purpose domain yet**.
4. **When unsure, leave it generic and say why** — a correct generic automation beats an unverified "optimized" one. Present conversions as suggestions with the before/after, not silent rewrites.

Bonus wins conversion often unlocks: replacing a hard-coded entity list with an `area_id`/`label_id` target, and dropping manual `unavailable`/`unknown` guards the building blocks handle for you.

