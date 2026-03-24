---
name: ha-appdaemon
description: AppDaemon development for Home Assistant. Use when writing or modifying AppDaemon Python apps, discussing AppDaemon callbacks, schedulers, state listeners, service calls, or app lifecycle. Also use when the user mentions AppDaemon initialize/terminate, listen_state, run_every, run_in, call_service, or any AppDaemon API usage.
---

# AppDaemon — Non-Obvious Reference

This skill contains ONLY things that differ from generic Python/HA knowledge or are commonly done wrong. Standard AppDaemon docs apply for everything else.

## 1. App Lifecycle

**`initialize()` is SYNCHRONOUS — blocking it freezes ALL of AppDaemon.**
- Long HTTP requests, file I/O, or `time.sleep()` here hangs everything
- Move heavy work to: `self.run_in(self.heavy_callback, 0)`

**Called on:** startup, file changes, config changes, DST transitions, plugin restarts, dependency reloads. Must assume completely fresh start — no state survives between initializations.

**All callbacks from previous initialization are automatically removed** before `initialize()` runs again.

**`terminate()`** runs synchronously before reload. If it errors, auto-reload won't work until file changes again.

## 2. Callback Signatures (Error-Prone)

Each type has a DIFFERENT signature:

| Type | Signature |
|------|-----------|
| State | `cb(self, entity, attribute, old, new, **kwargs)` |
| Scheduler | `cb(self, **kwargs)` |
| Event | `cb(self, event_type, data, **kwargs)` |
| Service | `cb(self, namespace, domain, service, **kwargs)` |

**User kwargs** passed at registration are delivered to callback:
```python
self.listen_state(self.cb, "sensor.x", my_param=42)
# In cb: kwargs["my_param"] == 42
# Or: def cb(self, entity, attribute, old, new, my_param, **kwargs)
```

## 3. Threading Model

- Each app pinned to own thread by default → no concurrent callbacks within same app
- **NEVER use `time.sleep()`** — blocks the worker thread. Use `self.run_in()` instead
- `self.sleep()` is ONLY for async apps — raises exception in sync callbacks
- With `pin_apps: false`, race conditions become possible → use `@ad.app_lock`

## 4. State API

**`get_state(entity_id=None, attribute=None, default=None, copy=True)`**
- No entity_id → returns ALL entities as dict
- Domain only (e.g., `"light"`) → returns all entities in domain
- `attribute="all"` → returns entire state dict including attributes
- **Returns STRINGS** — must cast: `float(self.get_state("sensor.x"))` or use `default`
- Attributes like `brightness` don't exist when light is off → always use `default` parameter

**`set_state(entity_id, state=None, attributes=None, replace=False)`**
- `replace=False` (default): merges with existing attributes
- `replace=True`: replaces entire attributes dict

## 5. `listen_state` Nuances

```python
self.listen_state(callback, entity_id, **kwargs)
```

- `entity_id` can be: string, list of strings, or domain name (e.g., `"light"`)
- `attribute=None` (default): monitors `state` only
- `attribute="all"`: fires on ANY attribute change; old/new are entire state dicts
- `attribute="brightness"`: monitors specific attribute

**`duration` parameter:** State must REMAIN in matched condition for N seconds before callback fires. Callback receives original old/new values, not current. Only reliable with specific entity_ids, not domain-wide.

**`immediate=True`:** Checks current state at registration. If matches, fires immediately (or starts duration timer). `old` will be `None`.

**`oneshot=True`:** Auto-removes after first invocation.

**Lambda filters:**
```python
self.listen_state(self.cb, "sensor.x",
    old=lambda x: x.lower() not in {"unknown", "unavailable"},
    new=lambda x: float(x) > 100)
```

## 6. Scheduler API

All return string handles for cancellation.

**`run_in(callback, delay, **kwargs)`**
- `delay` accepts: int/float (seconds), string (`"SS"`, `"MM:SS"`, `"HH:MM:SS"`), or `timedelta`
- **This is the replacement for `time.sleep()`**

**`run_every(callback, start, interval, **kwargs)`**
- `start` special values:
  - `"now"` (default): first trigger = now + interval
  - `"immediate"`: first trigger = immediately
  - `"now+5"`: first trigger = now + 5 seconds
  - Time string or datetime/time objects
- If `start` is in the past, first trigger is the first calculated interval in the future

**`run_at(callback, start)`** — if time is in the past, fires NEXT DAY.

**`run_daily` / `run_hourly` / `run_minutely`** — same past-time behavior.

**`run_at_sunrise(callback, offset=None)` / `run_at_sunset`**
- `offset` is SECONDS (int), NOT a time string

**Randomization:** All scheduler calls support `random_start` and `random_end` (seconds).

**`cancel_timer(handle)`, `timer_running(handle)`, `reset_timer(handle)`**

## 7. Service Calls

```python
result = self.call_service("domain/service", **data)
```
- Format: `"domain/service"` with SLASH — NOT dot notation
- Always returns result dict
- Uses app's default namespace

**Async callback pattern:**
```python
self.call_service("domain/service", callback=self.handle_result, param=value)
```

**Custom services:**
```python
self.register_service("my_domain/my_service", self.handler, namespace="my_ns")
# handler receives: (namespace, domain, service) as first 3 positional args
```

## 8. Time Utilities

**ALWAYS use AppDaemon time functions** (supports time travel testing):
- `self.get_now()` NOT `datetime.now()`
- `self.time()` NOT `datetime.now().time()`
- `self.date()` NOT `date.today()`
- `self.datetime()` NOT `datetime.now()`

**`now_is_between(start, end)`** — correctly handles midnight crossing.

**`sunrise()` / `sunset()`:**
- Default: returns NEXT occurrence (may be tomorrow!)
- `today=True`: returns today's value even if past
- `days_offset=N`: offset from today (requires `today=True`)

**`parse_time()` formats:** `"HH:MM:SS"`, `"sunrise + 01:00:00"`, `"sunset - 00:30:00"`

## 9. Event API

```python
self.listen_event(callback, event=None, **kwargs)
```
- `event=None` → listens to ALL events (very noisy)
- Extra kwargs act as filters matching event data keys
- Lambda filters supported: `node_id=lambda x: x in ["11", "14"]`

**Built-in events:** `appd_started` (global, once at startup), `app_initialized` / `app_terminated` (admin namespace).

## 10. Entity Attribute Access (Modern)

```python
self.entities.binary_sensor.door.state
self.entities.light.office.attributes.brightness
# Methods: .exists(), .is_state(), .turn_on(), .turn_off(), .toggle()
```

## 11. Async Apps

**All API calls in async context return `Task` objects — MUST `await`:**
```python
handle = await self.run_in(self.cb, 30)   # Correct
handle = self.run_in(self.cb, 30)          # WRONG — returns Task, not handle
```

- Use `self.create_task()` NOT `asyncio.create_task()` (proper cleanup on reload)
- Use `self.run_in_executor()` for blocking I/O
- `self.sleep()` is safe in async apps (unlike `time.sleep()`)

## 12. Configuration & Dependencies

**Arguments:** `self.args["param_name"]` from apps.yaml.

**Dependencies:**
```yaml
my_app:
  dependencies:
    - other_app  # Reloads together, loads after other_app
```

**Priority:** `priority: 10` (lower = loads first, default 50). Dependencies override priority.

**Plugin reload control:**
```yaml
my_app:
  plugin: NONE  # Never reload on plugin restart
```

**Logging:**
- `self.log("message")`, `self.log("msg", level="DEBUG")`
- `self.error("msg")` → error log
- Placeholders: `__function__`, `__module__`, `__line__` auto-expand
