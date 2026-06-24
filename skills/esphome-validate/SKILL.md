---
name: esphome-validate
description: Validation gate for ESPHome device configs (incl. LVGL displays) — the success criteria a config must meet before flashing. Use after editing an ESPHome YAML, when asked to "validate", "compile", or "check" a config, before an OTA/flash, or when running an ESPHome change through a loop. Covers offline config/compile checks and the incremental deploy-and-monitor discipline.
allowed_tools:
  - Bash
  - mcp__home-assistant
---

# ESPHome validation gate

The verifiable stopping condition for an ESPHome change. Most of it runs **offline without the
device** — only flashing needs hardware.

## Two offline stages (no device required)

1. **Config check — fast, always run first:**
   ```bash
   esphome config <file>.yaml
   ```
   Resolves substitutions and packages and validates the schema. Catches: bad keys, undefined
   substitutions, missing `id:`/widget references, wrong component options, malformed LVGL
   widget trees. Seconds, no toolchain.

2. **Compile — full build, catches what config can't:**
   ```bash
   esphome compile <file>.yaml
   ```
   Runs the C++ build. Catches lambda errors, type mismatches, undefined entities referenced in
   lambdas, and out-of-memory/flash-size problems. Minutes; needs the toolchain but **not** the
   board. Produces the firmware binary.

**If `esphome` isn't installed:** `pip install esphome` (or `uv tool install esphome`), or use
the ESPHome dashboard's **Validate** / **Install → Manually** which runs the same two stages.

## Flash + verify (needs the device)

`esphome run <file>.yaml` (USB or OTA) flashes and streams logs. Verify: boots, Wi-Fi + HA API
connect, display renders without glitches, touch/encoder input registers, HA entity bindings
update.

## Incremental-deploy discipline (hard rule)

**One change category per compile-flash cycle** (layout *or* sensor binding *or* boot/memory
*or* cosmetic — not several at once). Some boards expose no serial console, so simultaneous
changes are undiagnosable. Flash, confirm, then make the next change. (Earned the hard way —
see project memory.)

## Diagnosing on-device

Watch OTA logs (`esphome logs <file>.yaml`) and HA state via the HA MCP. For structured
diagnosis of a misbehaving device, use the **ha-troubleshooting** skill.

**Debug-logging discipline:** while diagnosing, raise `logger:` level and add temporary
`lambda`/`on_...` log lines to make behaviour observable. Once the change is confirmed working,
**remove the excessive debug logging**, leaving only `WARN`/`ERROR` for production.

## Success criteria

Done when: `esphome config` passes → `esphome compile` succeeds → (on flash) the device boots,
connects, renders, and the HA bindings update — with only one change in flight and debug logs
stripped back to warn/error.
