# Failure patterns and version-sensitive notes

## Contents
- [Common failure patterns](#common-failure-patterns)
- [HA-specific technical knowledge](#ha-specific-technical-knowledge)

## Common Failure Patterns

### Pattern: "Everything lost on restart"

**Scope**: All or most entities lose state after restart.

**Diagnostic path**:
1. Compare `core.restore_state` timestamps with installed-version write cadence, clean-shutdown history and storage logs; timestamps alone do not prove a stuck writer.
2. If stale: check HA log for `homeassistant.helpers.storage` errors writing `core.restore_state`
3. Common cause: a single entity producing a value that fails JSON serialization (oversized integer, NaN, circular reference) may block a restore-state write; confirm the installed-version failure scope
4. The error message names the exact entity and value — fix that entity

**Check scope**: A serialization failure may block a restore-state write; confirm its exact affected scope from installed-version implementation and logs rather than generalizing to every persistence mechanism.

### Pattern: "Specific helpers reset on restart"

**Scope**: Some helpers reset, others don't.

**Diagnostic path**:
1. Check if YAML-defined helpers have `initial:` set — this ALWAYS overrides restored state by design
2. Inspect the affected helper integration's restore behavior and storage errors; recorder history filters do not establish RestoreEntity persistence.
3. Compare startup logs, prior persisted state and actual integration/version.
4. Check UI-created helpers in `.storage/input_number` etc. for `initial` values

### Pattern: "Automation doesn't trigger / triggers incorrectly"

**Diagnostic path**:
1. Check automation traces (HA UI → Automations → the automation → Traces)
2. Check if the automation is enabled (state = "on")
3. Verify the trigger entity actually changes state (check logbook)
4. Check conditions — template conditions may silently evaluate to false
5. Check if house mode or other global conditions are blocking it
6. For device triggers: verify `device_id` still matches (can break after re-pairing)

### Pattern: "Entity shows wrong value / unavailable"

**Diagnostic path**:
1. Check the integration providing the entity — is it connected?
2. Check HA log for errors from that integration
3. For template sensors: test the template in Developer Tools → Templates
4. For MQTT entities: check Zigbee2MQTT / broker connectivity
5. For ESPHome: check device logs via ESPHome dashboard

### Pattern: "Service call does nothing"

**Diagnostic path**:
1. Inspect service schema and traces first; exercise a changing service only within the entrypoint authorization boundary.
2. Check if the target entity is available
3. Read the target climate entity's supported range and temperature step; acceptance varies by integration/device. Do not assume a universal 0.5°C step.
4. Check the installed-version [shell_command documentation](https://www.home-assistant.io/integrations/shell_command/) for restart/reload requirements and supported service-data templating; do not assume parameters are unsupported.
5. Check HA log for errors during the service call

### Pattern: "Integration won't load / setup failed"

**Diagnostic path**:
1. Check HA log for setup errors from the integration
2. Verify credentials in `secrets.yaml` or config entries
3. Check network connectivity to external services
4. For custom components: check compatibility with current HA version
5. Check `.storage/core.config_entries` for the integration's config

### Pattern: "Dashboard / UI not updating"

**Diagnostic path**:
1. Hard-refresh browser (Ctrl+Shift+R)
2. Check if the entity state updates in Developer Tools → States
3. If entity updates but UI doesn't: check the dashboard card configuration
4. For custom cards: check browser console for JavaScript errors
5. For Lovelace YAML: check for syntax errors

## HA-Specific Technical Knowledge

### Template engine quirks
Verify native conversion behavior against the installed-version implementation and the consumer context; do not infer a live failure from these snapshot notes alone.
- `_parse_result()` auto-converts all-digit strings to integers — a string like `"111100001111"` becomes a massive int
- The `| string` Jinja2 filter does NOT prevent this — `_parse_result()` runs after Jinja2 rendering
- To force string output: include at least one non-digit character in the result
- Template sensors with `state: "{{ expression }}"` may silently fail if the expression returns None

### Recorder and restore_state
Verify periodic cadence against installed-version source and storage logs; a stale file alone is insufficient causal evidence.
- `core.restore_state` is written periodically (~15 min) AND on clean shutdown
- An unclean shutdown (crash, power loss) loses state changes since last periodic write
- Recorder history filters and RestoreEntity state persistence are separate mechanisms; inspect the affected integration's restore behavior before attributing a reset to recorder filters.
- `commit_interval` affects database write frequency, not restore_state writes

### YAML and packages
- ALL `.yaml` files in the `packages/` directory are loaded — use `.SOURCE`, `.BACKUP`, or `.disabled` extensions to prevent loading
- Check installed-version shell_command documentation for reload/restart requirements; do not infer a restart is authorized.
- AppDaemon apps and HA packages are separate systems — changes to one don't require restarting the other

### Common entity quirks
- TRVs typically don't have `current_temperature` — use separate room sensors
- Read the target climate entity's supported range and temperature step; acceptance varies by integration/device. Do not assume a universal 0.5°C step.
- Device IDs can change after re-pairing, breaking device triggers in automations
- Entity IDs can change if a device is re-added, breaking automations and templates

