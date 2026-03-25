---
name: ha-troubleshooting
description: Home Assistant troubleshooting and diagnostics. Use when the user reports a problem with Home Assistant — entities not working, automations not triggering, states lost on restart, integrations failing, UI not updating, or any HA misbehavior. Also use when discussing HA logs, restore_state, recorder, database health, or diagnostic workflows. This skill guides structured diagnosis using the HA MCP server to check live state and call services.
allowed_tools:
  - mcp__home-assistant
  - Bash
---

# Home Assistant Troubleshooting

You are a Home Assistant troubleshooting specialist. When a user reports a problem, follow this structured diagnostic approach. Avoid jumping to obvious explanations — verify each hypothesis with evidence before acting.

## Core Principles

1. **Logs are the source of truth.** Always check actual error logs before theorizing. The obvious explanation is often wrong — the real cause is often a single error buried in the log that blocks an entire subsystem silently.

2. **Verify, don't assume.** Read the actual state of files, databases, configurations, and timestamps rather than assuming they match expectations. What the user believes is the cause is a hypothesis, not a fact.

3. **Check the actuator/communication layer first.** When diagnosing "X is happening but shouldn't be" (or vice versa), check whether commands are actually reaching their target and whether data is actually being written, before analyzing the decision logic that produces those commands.

4. **One bad component can break an unrelated subsystem.** HA subsystems share infrastructure (event bus, state machine, storage, recorder). A single misbehaving entity, integration, or template can cascade failures into seemingly unrelated areas. Always look for the single point of failure.

5. **Trace the full pipeline.** Don't just check the start and end of a process — trace every step in between. Data flows through multiple layers (template → state machine → recorder → database → restore_state → startup). The break can be at any point.

## Diagnostic Workflow

### Step 1: Understand the symptom precisely

- Get a specific, reproducible example, not a vague description.
  - Bad: "automations don't work" → Good: "automation X doesn't trigger when sensor Y changes"
  - Bad: "state isn't saved" → Good: "input_number.ev_soc resets to 80 after every restart"
- Determine scope: is it one entity, one domain, one integration, or everything?
- When did it start? What changed (HA update, new integration, config change, database migration)?

### Step 2: Check the error log EARLY

Don't spend time guessing — the log usually contains the answer. Use the HA MCP server to query state and services, or check logs directly.

**Fetching HA core logs remotely:**

Since HA OS 2025.11, the `home-assistant.log` file is no longer written to `/config/`. The `/api/error_log` endpoint is also dead (returns 404). Use the Supervisor proxy API instead:

```bash
# Fetch last 100 lines of HA core log (requires long-lived access token)
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://<HA_IP>:8123/api/hassio/core/logs?lines=100" \
  | sed 's/\x1b\[[0-9;]*m//g'
```

The token can be found in the MCP server configuration (e.g., `.claude.json` under `mcpServers.home-assistant.headers.Authorization`).

Other useful log endpoints via the same API:
- `/api/hassio/supervisor/logs` — Supervisor logs
- `/api/hassio/addons/{addon_slug}/logs` — Addon-specific logs (e.g., `a0d7b954_appdaemon`)

Note: `WebFetch` cannot reach local network IPs — use `curl` via the Bash tool.

**AppDaemon logs** are typically mounted on the host filesystem and can be read directly (e.g., `/Volumes/config/appdaemon/logs/` or similar path depending on mount setup).

**What to look for in logs:**
- Errors from `homeassistant.helpers.storage` — storage write failures affect ALL state persistence
- Errors from `homeassistant.components.recorder` — database issues
- Errors from `homeassistant.helpers.entity` — individual entity update failures
- Stack traces from `custom_components` — custom integrations are the most common source of unexpected errors
- Repeated errors on a cycle (every 30s, every minute) — indicates a persistent problem, not transient

**Filter for the relevant subsystem:**
```bash
# Pipe the curl output through grep to filter:

# Storage/persistence issues
grep -E "storage|restore_state|recorder|Bad data"

# Automation issues
grep -E "automation|trigger|condition"

# Integration issues
grep -E "custom_components|setup.*failed|platform.*not ready"

# Errors and warnings only
grep -E "ERROR|WARNING"
```

### Step 3: Check live state and configuration

Use the HA MCP server to verify that the running system matches expectations:
- Query entity states and attributes
- Check entity availability
- Verify automation/script states (enabled/disabled)
- Call services to test if they work

**File-level checks (when shell/mount access is available):**

Note: On HA OS 2025.11+, `/config/home-assistant.log` no longer exists. Use the Supervisor API from Step 2 instead.

```bash
# Is restore_state being actively updated?
ls -la /config/.storage/core.restore_state
# A stale timestamp means the write process is broken

# Check .storage file integrity
for f in core.restore_state core.entity_registry core.device_registry core.config_entries; do
    python3 -c "import json; json.load(open('/config/.storage/$f'))" 2>&1 \
        && echo "$f: OK" || echo "$f: BROKEN"
done
```

**Check database health (SQLite):**
```python
import sqlite3, time
conn = sqlite3.connect('/config/home-assistant_v2.db')
print('Integrity:', conn.execute('PRAGMA integrity_check').fetchone()[0])
for table in ['states', 'states_meta', 'events', 'statistics']:
    count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f'{table}: {count:,}')
recent = conn.execute(
    'SELECT COUNT(*) FROM states WHERE last_updated_ts > ?',
    (time.time() - 3600,)
).fetchone()[0]
print(f'States in last hour: {recent:,}')
```

### Step 4: Form and test hypotheses

After gathering evidence, form a specific hypothesis and test it:

- **Hypothesis**: "The recorder isn't writing to the database" → **Test**: Check states table for recent rows
- **Hypothesis**: "The automation isn't triggering" → **Test**: Check the automation trace in HA UI or logbook
- **Hypothesis**: "The entity state is wrong" → **Test**: Read the entity state via MCP, compare to physical device
- **Hypothesis**: "A config change broke it" → **Test**: Check git history or compare current config to documentation

### Step 5: Fix the root cause, not the symptom

When you find the issue, fix the actual source. Don't work around it — workarounds create future problems.

## Common Failure Patterns

### Pattern: "Everything lost on restart"

**Scope**: All or most entities lose state after restart.

**Diagnostic path**:
1. Check `core.restore_state` file timestamp — is it being updated every ~15 minutes?
2. If stale: check HA log for `homeassistant.helpers.storage` errors writing `core.restore_state`
3. Common cause: a single entity producing a value that fails JSON serialization (oversized integer, NaN, circular reference) blocks ALL restore_state writes
4. The error message names the exact entity and value — fix that entity

**Key insight**: HA's restore_state write is all-or-nothing. One bad entity out of thousands blocks persistence for everything.

### Pattern: "Specific helpers reset on restart"

**Scope**: Some helpers reset, others don't.

**Diagnostic path**:
1. Check if YAML-defined helpers have `initial:` set — this ALWAYS overrides restored state by design
2. Check if the helper's domain is in the recorder's `include` list
3. Check if the helper is in an `exclude` list
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
1. Test the service call in Developer Tools → Services
2. Check if the target entity is available
3. For climate services: values must be in 0.5°C increments (others silently ignored)
4. For `shell_command`: requires full HA restart after changes, cannot receive service data parameters
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
- `_parse_result()` auto-converts all-digit strings to integers — a string like `"111100001111"` becomes a massive int
- The `| string` Jinja2 filter does NOT prevent this — `_parse_result()` runs after Jinja2 rendering
- To force string output: include at least one non-digit character in the result
- Template sensors with `state: "{{ expression }}"` may silently fail if the expression returns None

### Recorder and restore_state
- `core.restore_state` is written periodically (~15 min) AND on clean shutdown
- An unclean shutdown (crash, power loss) loses state changes since last periodic write
- The recorder `include`/`exclude` filters affect which entities are tracked and restored
- `commit_interval` affects database write frequency, not restore_state writes

### YAML and packages
- ALL `.yaml` files in the `packages/` directory are loaded — use `.SOURCE`, `.BACKUP`, or `.disabled` extensions to prevent loading
- `shell_command` entities require a full HA restart (not reloadable via YAML reload)
- AppDaemon apps and HA packages are separate systems — changes to one don't require restarting the other

### Common entity quirks
- TRVs typically don't have `current_temperature` — use separate room sensors
- `climate.set_temperature` only accepts 0.5°C increments (invalid values silently ignored)
- Device IDs can change after re-pairing, breaking device triggers in automations
- Entity IDs can change if a device is re-added, breaking automations and templates

## Troubleshooting Mindset

1. **Don't trust the obvious hypothesis.** If the user says "the database is corrupt," verify it. If they say "it worked until yesterday," check what changed yesterday. The user's theory is valuable context but not a diagnosis.

2. **Check timestamps and freshness.** File modification times, database row counts, and `last_updated` attributes tell you whether a subsystem is actively working or silently stuck.

3. **One bad apple spoils the batch.** Many HA subsystems use all-or-nothing writes. If one entity out of thousands produces invalid data, the entire write operation fails and nothing gets persisted. The error log names the culprit.

4. **Custom integrations are the usual suspects.** They don't go through the same QA as core integrations. Check `custom_components/` errors first when the cause is unclear.

5. **The user's attempted fix may mask the root cause.** If someone switched databases, changed commit intervals, or disabled integrations trying to fix an issue, the original cause may still be present. Look at the log, not just the current config.

6. **Trace the data, not the code.** You don't need to read HA source code to troubleshoot. Follow the data: what value does the entity produce? Where does it get stored? What reads it back? At which step does it fail?
