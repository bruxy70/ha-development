---
name: ha-troubleshooting
description: Home Assistant troubleshooting and diagnostics. Use when the user reports a problem with Home Assistant — entities not working, automations not triggering, states lost on restart, integrations failing, UI not updating, or any HA misbehavior. Also use when discussing HA logs, restore_state, recorder, database health, or diagnostic workflows. This skill guides structured diagnosis using the HA MCP server to check live state and call services.
---

# Home Assistant Troubleshooting

Start with read-only/offline checks. Editing or compiling does not authorize deployment, firmware writes, device-changing service calls or restarts. Reuse authorization already given for this action. Before a live mutation, confirm the target, intended effect, validation and rollback. If authorization/access is absent, report the outstanding live check. Treat `.storage` as read-only diagnostic input; do not edit it to repair a symptom.

First identify the execution context and available access using [context detection and artifact access](reference/access.md). Resolve all resources relative to this loaded skill; neither Claude Code nor Codex consumers need this repository as their working directory. Read [failure patterns/version notes](reference/failure-patterns.md) only for the affected symptom. [Connection setup](../ha-mcp-setup/SKILL.md), [validation](../ha-validate/SKILL.md), [cross-client enforcement proposals](../ha-validate/reference/enforcement.md) and [evaluation records](reference/evaluations.md) are direct companion resources.

## Requirements and completion loop

Use host text/filesystem tools, an existing configured HA MCP/REST connection and a network-capable client. HA CLI requires an existing supported on-host runtime; do not assume it exists on a development computer. Optional SSH requires trusted host keys and a configured SSH server; optional Python alternative installs with `python -m pip install paramiko` in the project environment. SQLite/JSON diagnostics use Python standard-library modules. No package installation is needed for native SSH or ordinary read-only text inspection.

Examples are adaptable diagnostic fragments: substitute confirmed paths, backend, host and entity IDs; preserve read-only database mode, verified SSH trust and live authorization guards. A missing tool/access path is a verification limit, not a passed check.

1. Identify reproducible symptom, changed versions/configuration and authorized scope; detect context before access.
2. Read relevant available state, traces/logs and files via the matching access tier. If evidence is unavailable, return to context/access or report the gap.
3. Test one falsifiable hypothesis at a time using read-only checks; record observed evidence separately from inferred causes. Return to step 2 if evidence contradicts it.
4. Apply the scoped authorized root-cause fix; run [ha-validate](../ha-validate/SKILL.md) and reproduce the symptom within permitted scope. On failure return to step 3, repair and recheck; stop a repeated unchanged failure and report the blocker.
5. Restore only investigation diagnostics, preserve operational logging, and report checks, outstanding live verification and rollback.

- [ ] Confirm context, symptom, version and scope.
- [ ] Gather available evidence; return to access detection for gaps.
- [ ] Test the hypothesis; return to evidence on contradiction.
- [ ] Validate the authorized fix; return to hypothesis on failure.
- [ ] Remove temporary diagnostics and report verification limits.

Diagnose Home Assistant failures using the artifact-specific access hierarchy and evidence below.

## Core Principles

Use a reproducible symptom, changed-version/configuration evidence and one falsifiable hypothesis at a time. Record observed evidence separately from inferred causes. Read relevant available logs early; combine state, traces, version and timestamps. Missing logs do not prove a cause.

### How HA fails

1. **Shared infrastructure can spread failures.** Storage serialization or shared recorder errors may affect unrelated entities. Confirm affected scope from installed-version logs rather than assuming every persistence mechanism failed.

2. Include custom integrations among suspects only when errors or recent changes implicate them.

### Diagnostic methodology

1. **Check the actuator layer first.** For "X is happening but shouldn't be" (or vice versa), check whether commands are actually reaching their target and whether data is actually being written, before analyzing the decision logic that produces those commands.

2. **Check timestamps and freshness.** File modification times, database row counts, and `last_updated` attributes tell you whether a subsystem is actively working or silently stuck.

3. **Trace the data through the full pipeline.** Follow the value, not the code: where does it come from, where is it stored, what reads it back, at which step does it fail? Don't just check start and end — data flows through multiple layers (template → state machine → recorder → database → restore_state → startup) and the break can be at any one of them.

## Diagnostic Workflow

### Step 1: Understand the symptom precisely

- Get a specific, reproducible example, not a vague description.
  - Bad: "automations don't work" → Good: "automation X doesn't trigger when sensor Y changes"
  - Bad: "state isn't saved" → Good: "input_number.ev_soc resets to 80 after every restart"
- Determine scope: is it one entity, one domain, one integration, or everything?
- When did it start? What changed (HA update, new integration, config change, database migration)?

### Step 2: Check the error log EARLY

Read available logs for the affected subsystem and match timestamps to the symptom.

**Fetch the log via the [artifact access hierarchy](reference/access.md#access-hierarchy--route-by-what-you-are-fetching)** — the tier depends on context and on *which* log:
- **AppDaemon / any `/config` file**: read directly off the mounted volume or host when available; that's the top tier, not the API.
- **HA Core log**: not on the mount (2025.11+) — REST `/api/hassio/core/logs?lines=100`, or `ha core logs` over SSH when Core is down.

Use a network-capable tool available in the current host; for local LAN REST, curl is a fallback when browser fetching cannot reach it.

**What to look for in logs:**
- Errors from `homeassistant.helpers.storage` — storage write failures may affect the implicated restore/storage subsystem; verify actual scope
- Errors from `homeassistant.components.recorder` — database issues
- Errors from `homeassistant.helpers.entity` — individual entity update failures
- Stack traces from `custom_components` — investigate only when the traceback or recent change implicates that component
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
- Inspect service schema and traces first; exercise a changing service only within the authorization boundary above.

**File-level checks (when shell/mount access is available):**
The `/config` paths below apply only to a confirmed on-host/container configuration. On a development mount, substitute its confirmed config root.

On applicable HA OS releases Core logs are journal/API-backed; verify installed version and installation type. A mounted config may lack Core logs even while they are available through Supervisor. Use the matching access tier.

```bash
# Is restore_state being actively updated?
ls -la /config/.storage/core.restore_state
# Compare timestamp with installed-version write cadence and logs; staleness alone does not prove failure

# Check .storage file integrity
for f in core.restore_state core.entity_registry core.device_registry core.config_entries; do
    python3 -c "import json; json.load(open('/config/.storage/$f'))" 2>&1 \
        && echo "$f: OK" || echo "$f: BROKEN"
done
```

**Check database health (SQLite):** ([read-only URI documentation](https://docs.python.org/3/library/sqlite3.html#how-to-work-with-sqlite-uris))
Confirm the actual recorder backend/path. Run expensive integrity checks on a consistent SQLite backup for large live databases; do not copy only an active database while omitting WAL state. The example requires a previously confirmed `config_dir`; close the connection in a `finally` block if adapting this into fallible application code.
```python
import sqlite3, time
from pathlib import Path
config_dir = Path(config_dir).resolve()  # previously confirmed configuration directory
conn = sqlite3.connect((config_dir / 'home-assistant_v2.db').as_uri() + '?mode=ro', uri=True)
conn.execute('PRAGMA query_only = ON')
try:
    print('Integrity:', conn.execute('PRAGMA integrity_check').fetchone()[0])
    for table in ['states', 'states_meta', 'events', 'statistics']:
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'{table}: {count:,}')
    recent = conn.execute(
        'SELECT COUNT(*) FROM states WHERE last_updated_ts > ?',
        (time.time() - 3600,)
    ).fetchone()[0]
    print(f'States in last hour: {recent:,}')
finally:
    conn.close()
```

### Step 4: Form and test hypotheses

After gathering evidence, form a specific hypothesis and test it:

- **Hypothesis**: "The recorder isn't writing to the database" → **Test**: Check states table for recent rows
- **Hypothesis**: "The automation isn't triggering" → **Test**: Check the automation trace in HA UI or logbook
- **Hypothesis**: "The entity state is wrong" → **Test**: Read the entity state via MCP, compare to physical device
- **Hypothesis**: "A config change broke it" → **Test**: Check git history or compare current config to documentation

**If you need to instrument or run probe tests to gather evidence:**

- Each debug log line or probe test must have a defined purpose tied to a specific hypothesis. Excessive "just in case" logging hurts performance and drowns out the operational signal the logs are supposed to carry.
- Confirm diagnostic changes are within the already authorized scope; otherwise obtain that scope before adding them.
- After the test, restore the original configuration and remove debug logs — don't leave diagnostic scaffolding in the code.

### Step 5: Fix the root cause, not the symptom

Apply the authorized root-cause fix, retaining a scoped rollback copy; validate using the completion loop. Reuse authorization already given; unresolved scope requires clarification before mutation.

