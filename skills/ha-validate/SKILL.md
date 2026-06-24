---
name: ha-validate
description: Validation gate for Home Assistant automation projects — the success criteria a change must meet before it is trusted. Use after editing HA automations/scripts/helpers (YAML) or AppDaemon apps (Python), when asked to "validate"/"check" an HA change, or when running one through a loop. Routes by artifact type: offline checks where possible, deploy-and-monitor where not.
allowed_tools:
  - Bash
  - mcp__home-assistant
---

# Home Assistant validation gate

What "validated" means depends on the artifact. Some checks run offline; HA YAML *semantics*
generally don't — they need a running HA, so the gate ends in a deploy-and-monitor loop.

## AppDaemon apps (Python) — strong offline gate

These are plain Python; validate without a live HA:

1. **Compiles:** `python -m py_compile <app>.py` (or `python -m compileall <dir>`).
2. **Lint:** `ruff check <changed .py>` (via `uv run --with ruff ruff …` if ruff isn't installed).
3. **Types:** `mypy <changed .py>` — high signal for AppDaemon's stringly-typed state access.
4. **Unit-test the pure logic** (optimizers, scheduling, allocation, scoring) with mocks — **no
   live HA needed**. Use [`appdaemon-testing`](https://github.com/nickw444/appdaemon-testing)
   (pytest `hass_driver` fixture) or
   [Appdaemon-Test-Framework](https://github.com/HelloThisIsFlo/Appdaemon-Test-Framework)
   (`given_that`/`assert_that`/`time_travel`). Business rules that read like "if X then set Y"
   are exactly what to cover. See **ha-appdaemon** for app structure.

## HA YAML (automations / scripts / helpers) — syntax offline, semantics on HA

- **Offline = syntax only:** parse each file —
  `python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" <file>` (or `yamllint`).
- **Semantic check** needs the full config + the project's integrations:
  `hass --script check_config -c <ha-config-dir>` — only meaningful against a complete HA
  config (mounted or copied), not the repo alone. Skip honestly if unavailable rather than
  pretending it passed.
- **Real validation is dynamic:** deploy → reload the relevant domain (or restart) → monitor
  logs + automation traces → fix → repeat. Use the **ha-troubleshooting** skill and the HA MCP
  (read states, logbook, traces) for the mechanics. See **ha-automations** / **ha-templates**
  for correct syntax that avoids the common failures.

## Debug-logging discipline (during the deploy-and-monitor loop)

While diagnosing, add temporary diagnostic logging — `logger.debug(...)` in AppDaemon,
`system_log.write` / verbose template traces / a debug `input_text` in automations — to make
behaviour observable. **When the change is confirmed working, strip the excessive debug
logging**, leaving only `warning`/`error` level for production.

## Success criteria

Done when, for each touched artifact: AppDaemon Python compiles + lints + types clean and its
logic tests pass; YAML parses and (where checkable) `check_config` passes; and the change has
been observed behaving correctly on HA via logs/traces, with debug logging stripped back to
warn/error. Project-specific rule-reviews (architecture/business-logic checklists) run on top of
this — see the project's own `validate` skill.
